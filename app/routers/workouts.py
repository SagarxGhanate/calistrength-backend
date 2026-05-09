from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Any
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.workout import WorkoutSession, SessionExercise
from app.models.progress import DailyLog
import datetime

router = APIRouter(prefix="/workouts", tags=["workouts"])


class SetData(BaseModel):
    set: int
    reps: int


class ExerciseIn(BaseModel):
    exercise_name: str
    category: Optional[str] = None
    sets_data: Optional[List[Any]] = None
    total_reps: Optional[int] = 0


class WorkoutSessionIn(BaseModel):
    date: str
    total_seconds: Optional[int] = 0
    total_reps: Optional[int] = 0
    calories_burned: Optional[float] = 0
    notes: Optional[str] = None
    exercises: Optional[List[ExerciseIn]] = []


@router.post("/session")
def save_workout_session(
    body: WorkoutSessionIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Find or create session for this date
    session = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == current_user.id,
        WorkoutSession.date == body.date,
    ).first()

    if session:
        # Update existing session
        session.total_seconds   = (session.total_seconds or 0) + (body.total_seconds or 0)
        session.total_reps      = (session.total_reps or 0) + (body.total_reps or 0)
        session.calories_burned = (session.calories_burned or 0) + (body.calories_burned or 0)
    else:
        session = WorkoutSession(
            user_id         = current_user.id,
            date            = body.date,
            total_seconds   = body.total_seconds or 0,
            total_reps      = body.total_reps or 0,
            calories_burned = body.calories_burned or 0,
            notes           = body.notes,
        )
        db.add(session)
        db.flush()

    # Save exercises
    for ex in (body.exercises or []):
        existing = db.query(SessionExercise).filter(
            SessionExercise.session_id == session.id,
            SessionExercise.exercise_name == ex.exercise_name,
        ).first()
        if existing:
            existing.total_reps = (existing.total_reps or 0) + (ex.total_reps or 0)
            if ex.sets_data:
                # Append new sets to existing array instead of overwriting
                current_sets = existing.sets_data or []
                existing.sets_data = current_sets + ex.sets_data
                from sqlalchemy.orm.attributes import flag_modified
                flag_modified(existing, "sets_data")
        else:
            db.add(SessionExercise(
                session_id    = session.id,
                exercise_name = ex.exercise_name,
                category      = ex.category,
                sets_data     = ex.sets_data,
                total_reps    = ex.total_reps or 0,
            ))

    # Update daily log
    daily = db.query(DailyLog).filter(
        DailyLog.user_id == current_user.id,
        DailyLog.date == body.date,
    ).first()
    if daily:
        daily.total_reps    = (daily.total_reps or 0) + (body.total_reps or 0)
        daily.total_seconds = (daily.total_seconds or 0) + (body.total_seconds or 0)
    else:
        db.add(DailyLog(
            user_id       = current_user.id,
            date          = body.date,
            total_reps    = body.total_reps or 0,
            total_seconds = body.total_seconds or 0,
        ))

    db.commit()
    return {"message": "Workout session saved", "session_id": session.id}


@router.get("/history")
def get_workout_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    sessions = db.query(WorkoutSession).filter(
        WorkoutSession.user_id == current_user.id
    ).order_by(WorkoutSession.date.asc()).all()

    result = []
    for s in sessions:
        result.append({
            "id": s.id,
            "date": s.date,
            "total_seconds": s.total_seconds,
            "total_reps": s.total_reps,
            "calories_burned": s.calories_burned,
            "exercises": [
                {
                    "exercise_name": e.exercise_name,
                    "category": e.category,
                    "total_reps": e.total_reps,
                    "sets_data": e.sets_data,
                }
                for e in s.exercises
            ],
        })
    return result
