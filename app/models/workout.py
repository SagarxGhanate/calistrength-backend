from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date            = Column(String(20), nullable=False)          # "YYYY-MM-DD"
    total_seconds   = Column(Integer, default=0)
    total_reps      = Column(Integer, default=0)
    calories_burned = Column(Float, default=0)
    notes           = Column(Text, nullable=True)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())

    user      = relationship("User", back_populates="workout_sessions")
    exercises = relationship("SessionExercise", back_populates="session", cascade="all, delete-orphan")


class SessionExercise(Base):
    __tablename__ = "session_exercises"

    id              = Column(Integer, primary_key=True, index=True)
    session_id      = Column(Integer, ForeignKey("workout_sessions.id", ondelete="CASCADE"), index=True)
    exercise_name   = Column(String(150), nullable=False)
    category        = Column(String(50), nullable=True)   # pushup, pullup, squat, etc.
    sets_data       = Column(JSON, nullable=True)          # [{"set": 1, "reps": 12}, ...]
    total_reps      = Column(Integer, default=0)

    session = relationship("WorkoutSession", back_populates="exercises")
