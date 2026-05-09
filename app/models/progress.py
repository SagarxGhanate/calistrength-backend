from sqlalchemy import Column, Integer, String, Float, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class WeightLog(Base):
    __tablename__ = "weight_logs"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date        = Column(String(20), nullable=False)   # "YYYY-MM-DD"
    weight_kg   = Column(Float, nullable=False)
    notes       = Column(String(200), nullable=True)
    logged_at   = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="weight_logs")


class DailyLog(Base):
    """Aggregated daily activity — written after each workout session completes."""
    __tablename__ = "daily_logs"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    date            = Column(String(20), nullable=False)
    total_reps      = Column(Integer, default=0)
    total_seconds   = Column(Integer, default=0)
    calories_burned = Column(Float, default=0)
    notes           = Column(Text, nullable=True)

    user = relationship("User", back_populates="daily_logs")


class PersonalRecord(Base):
    __tablename__ = "personal_records"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    exercise_name   = Column(String(150), nullable=False)
    max_reps        = Column(Integer, nullable=True)
    max_sets        = Column(Integer, nullable=True)
    max_duration_s  = Column(Integer, nullable=True)   # for holds like planche, L-sit
    date_achieved   = Column(String(20), nullable=True)
    notes           = Column(String(200), nullable=True)
    recorded_at     = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="personal_records")
