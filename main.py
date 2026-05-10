from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.core.config import get_settings
from app.core.deps import get_db
from app.database import Base, engine

# ── Import ALL models so SQLAlchemy knows about them ─────────────────────────
from app.models.user import User, Onboarding, UserSettings
from app.models.workout import WorkoutSession, SessionExercise
from app.models.skill import Skill, UserSkill
from app.models.progress import WeightLog, DailyLog, PersonalRecord

from app.routers import auth, workouts, weight, records, skills
from app.seed import seed_skills

settings = get_settings()

# Create all tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="CaliStrength API",
    description="Backend for CaliStrength — Calisthenics Training & Skill Development App",
    version="1.0.0",
)

# ── CORS ──────────────────────────────────────────────────────────────────────
_cors_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://localhost:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
    "http://127.0.0.1:3000",
]
# Add production frontend URL from .env (e.g. https://calistrength.vercel.app)
if settings.FRONTEND_URL and settings.FRONTEND_URL not in _cors_origins:
    _cors_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(auth.router)
app.include_router(workouts.router)
app.include_router(weight.router)
app.include_router(records.router)
app.include_router(skills.router)


@app.on_event("startup")
def on_startup():
    seed_skills()


@app.get("/")
def health_check(db: Session = Depends(get_db)):
    try:
        db.execute(text("SELECT 1"))
        db_status = "connected"
    except Exception:
        db_status = "disconnected"
    return {"status": "ok", "app": "CaliStrength API", "version": "1.0.0", "database": db_status}
