from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import Optional

from app.core.deps import get_db, get_current_user
from app.core.firebase import verify_firebase_token
from app.core.security import hash_password, verify_password, create_access_token
from app.models.user import User, UserSettings

router = APIRouter(prefix="/auth", tags=["auth"])


# ── Pydantic Schemas (inline for auth) ────────────────────────────────────────

class FirebaseLoginRequest(BaseModel):
    """Sent from React after Firebase signs the user in (Google or email)."""
    id_token: str   # Firebase ID token from getIdToken()


class EmailSignupRequest(BaseModel):
    name: str
    email: EmailStr
    password: str


class EmailLoginRequest(BaseModel):
    email: EmailStr
    password: str


class OnboardingRequest(BaseModel):
    goal: Optional[str] = None
    experience: Optional[str] = None
    gender: Optional[str] = "male"
    age: Optional[int] = None
    height_cm: Optional[float] = None
    current_weight: Optional[float] = None
    target_weight: Optional[float] = None
    target_days: Optional[int] = 30
    start_date: Optional[str] = None


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: int
    name: str
    email: str
    avatar: Optional[str] = None
    is_onboarded: bool


# ── Helper ─────────────────────────────────────────────────────────────────────

def _build_response(user: User, db: Session) -> AuthResponse:
    """Create JWT and return AuthResponse for any user."""
    token = create_access_token(user.id, user.email)
    return AuthResponse(
        access_token=token,
        user_id=user.id,
        name=user.name,
        email=user.email,
        avatar=user.avatar,
        is_onboarded=user.is_onboarded,
    )


def _ensure_settings(user: User, db: Session):
    """Create default settings row if it doesn't exist yet."""
    if not user.settings:
        db.add(UserSettings(user_id=user.id))
        db.commit()


# ── ROUTE 1: Firebase token login (Google OR Firebase email/password) ──────────

@router.post("/firebase", response_model=AuthResponse)
def firebase_login(body: FirebaseLoginRequest, db: Session = Depends(get_db)):
    """
    React sends the Firebase ID token after any Firebase sign-in.
    We verify it, then find-or-create the user in MySQL.
    Works for both Google and Firebase email/password flows.
    """
    try:
        decoded = verify_firebase_token(body.id_token)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))

    firebase_uid = decoded.get("uid")
    email        = decoded.get("email", "")
    name         = decoded.get("name") or decoded.get("email", "User").split("@")[0]
    avatar       = decoded.get("picture")
    provider     = decoded.get("firebase", {}).get("sign_in_provider", "password")
    auth_provider = "google" if provider == "google.com" else "email"

    # Find existing user by firebase_uid or email
    user = (
        db.query(User).filter(User.firebase_uid == firebase_uid).first()
        or db.query(User).filter(User.email == email).first()
    )

    if user:
        # Update firebase_uid and avatar if missing (e.g. existing email user logs in via Google)
        if not user.firebase_uid:
            user.firebase_uid = firebase_uid
        if avatar and not user.avatar:
            user.avatar = avatar
        db.commit()
        db.refresh(user)
    else:
        # First time — create the user
        user = User(
            firebase_uid=firebase_uid,
            email=email,
            name=name,
            avatar=avatar,
            auth_provider=auth_provider,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        _ensure_settings(user, db)

    return _build_response(user, db)


# ── ROUTE 2: Plain email/password signup (without Firebase for the auth step) ──
# Use this if you want your own DB auth without Firebase for email/password.
# Your React SignupPage can call this directly.

@router.post("/signup", response_model=AuthResponse)
def email_signup(body: EmailSignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email already exists. Please log in.",
        )

    user = User(
        email=body.email,
        password_hash=hash_password(body.password),
        name=body.name,
        auth_provider="email",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    _ensure_settings(user, db)
    return _build_response(user, db)


# ── ROUTE 3: Plain email/password login ────────────────────────────────────────

@router.post("/login", response_model=AuthResponse)
def email_login(body: EmailLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()

    if not user or not user.password_hash:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    return _build_response(user, db)


# ── ROUTE 4: Save onboarding data ──────────────────────────────────────────────

@router.post("/onboarding")
def save_onboarding(
    body: OnboardingRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.models.user import Onboarding
    from app.models.progress import WeightLog
    import datetime

    # Upsert onboarding row
    ob = current_user.onboarding
    if ob:
        ob.goal            = body.goal
        ob.experience      = body.experience
        ob.gender          = body.gender
        ob.age             = body.age
        ob.height_cm       = body.height_cm
        ob.current_weight  = body.current_weight
        ob.target_weight   = body.target_weight
        ob.target_days     = body.target_days
        ob.start_date      = body.start_date or datetime.date.today().isoformat()
    else:
        ob = Onboarding(
            user_id        = current_user.id,
            goal           = body.goal,
            experience     = body.experience,
            gender         = body.gender,
            age            = body.age,
            height_cm      = body.height_cm,
            current_weight = body.current_weight,
            target_weight  = body.target_weight,
            target_days    = body.target_days,
            start_date     = body.start_date or datetime.date.today().isoformat(),
        )
        db.add(ob)

    # Save first weight entry automatically
    if body.current_weight:
        first_log = WeightLog(
            user_id   = current_user.id,
            date      = datetime.date.today().isoformat(),
            weight_kg = body.current_weight,
        )
        db.add(first_log)

    current_user.is_onboarded = True
    db.commit()
    return {"message": "Onboarding complete", "is_onboarded": True}

# ── ROUTE 5: Get current user profile ─────────────────────────────────────────

@router.get("/me")
def get_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    ob = current_user.onboarding
    settings = current_user.settings
    return {
        "access_token":  create_access_token(current_user.id, current_user.email),
        "token_type":    "bearer",
        "user_id":       current_user.id,
        "name":          current_user.name,
        "email":         current_user.email,
        "avatar":        current_user.avatar,
        "bio":           current_user.bio,
        "phone":         current_user.phone,
        "role":          current_user.role,
        "is_onboarded":  current_user.is_onboarded,
        # Onboarding fields (consumed by frontend AppContext)
        "goal":          ob.goal if ob else None,
        "start_date":    ob.start_date if ob else None,
        "target_weight": ob.target_weight if ob else None,
        "experience":    ob.experience if ob else None,
        "gender":        ob.gender if ob else None,
        "age":           ob.age if ob else None,
        "height_cm":     ob.height_cm if ob else None,
        "target_days":   ob.target_days if ob else 30,
        # Settings
        "rest_time":     settings.rest_time if settings else 30,
        "theme":         settings.theme if settings else "dark",
    }


# ── ROUTE 6: Update user settings / profile ───────────────────────────────────

class UpdateSettingsRequest(BaseModel):
    # User profile fields
    name: Optional[str] = None
    avatar: Optional[str] = None
    bio: Optional[str] = None
    phone: Optional[str] = None
    role: Optional[str] = None
    # Onboarding / training fields
    goal: Optional[str] = None
    experience: Optional[str] = None
    gender: Optional[str] = None
    age: Optional[int] = None
    height_cm: Optional[float] = None
    target_weight: Optional[float] = None
    # Settings fields
    rest_time: Optional[int] = None
    theme: Optional[str] = None


@router.put("/settings")
def update_settings(
    body: UpdateSettingsRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Persist settings / profile changes from the Settings page to MySQL."""
    from app.models.user import Onboarding

    # ── Update User table ──────────────────────────────────────────────────
    if body.name is not None:
        current_user.name = body.name
    if body.avatar is not None:
        current_user.avatar = body.avatar
    if body.bio is not None:
        current_user.bio = body.bio
    if body.phone is not None:
        current_user.phone = body.phone
    if body.role is not None and body.role in ("Athlete", "Coach", "Member"):
        current_user.role = body.role

    # ── Update Onboarding table ────────────────────────────────────────────
    ob = current_user.onboarding
    if not ob:
        ob = Onboarding(user_id=current_user.id)
        db.add(ob)
    if body.goal is not None:
        ob.goal = body.goal
    if body.experience is not None:
        ob.experience = body.experience
    if body.gender is not None:
        ob.gender = body.gender
    if body.age is not None:
        ob.age = body.age
    if body.height_cm is not None:
        ob.height_cm = body.height_cm
    if body.target_weight is not None:
        ob.target_weight = body.target_weight

    # ── Update UserSettings table ──────────────────────────────────────────
    _ensure_settings(current_user, db)
    db.refresh(current_user)
    settings = current_user.settings
    if body.rest_time is not None:
        settings.rest_time = body.rest_time
    if body.theme is not None:
        settings.theme = body.theme

    db.commit()
    return {"message": "Settings updated successfully"}


# ── ROUTE 7: Reset app / start new journey ─────────────────────────────────────

class ResetAppRequest(BaseModel):
    carry_over_weight: Optional[float] = None


@router.post("/reset")
def reset_app(
    body: ResetAppRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete all user progress data (workouts, weight, PRs, daily logs, skills)
    but keep the user account and onboarding data intact.
    Optionally seeds a new Day 1 weight entry from the previous journey's
    last recorded weight.
    """
    import datetime
    from app.models.progress import WeightLog, DailyLog, PersonalRecord
    from app.models.workout import WorkoutSession, SessionExercise
    from app.models.skill import UserSkill

    uid = current_user.id

    # Delete session exercises first (FK constraint)
    session_ids = [s.id for s in db.query(WorkoutSession.id).filter(WorkoutSession.user_id == uid).all()]
    if session_ids:
        db.query(SessionExercise).filter(SessionExercise.session_id.in_(session_ids)).delete(synchronize_session=False)

    # Delete main tables
    db.query(WorkoutSession).filter(WorkoutSession.user_id == uid).delete(synchronize_session=False)
    db.query(WeightLog).filter(WeightLog.user_id == uid).delete(synchronize_session=False)
    db.query(PersonalRecord).filter(PersonalRecord.user_id == uid).delete(synchronize_session=False)
    db.query(DailyLog).filter(DailyLog.user_id == uid).delete(synchronize_session=False)
    db.query(UserSkill).filter(UserSkill.user_id == uid).delete(synchronize_session=False)

    # Reset onboarding start_date to today
    ob = current_user.onboarding
    if ob:
        ob.start_date = datetime.date.today().isoformat()

    # Carry over last weight as Day 1 entry
    if body.carry_over_weight and body.carry_over_weight > 0:
        new_log = WeightLog(
            user_id=uid,
            date=datetime.date.today().isoformat(),
            weight_kg=body.carry_over_weight,
        )
        db.add(new_log)

    db.commit()
    return {"message": "App reset successful. New journey started!"}

