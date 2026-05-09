from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Float, Enum, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id              = Column(Integer, primary_key=True, index=True)
    firebase_uid    = Column(String(128), unique=True, index=True, nullable=True)
    # null for Google-only users, required for email/password users
    email           = Column(String(255), unique=True, index=True, nullable=False)
    password_hash   = Column(String(255), nullable=True)   # null for Google login users
    name            = Column(String(100), nullable=False, default="User")
    avatar          = Column(Text, nullable=True)
    bio             = Column(String(300), nullable=True)
    phone           = Column(String(20), nullable=True)
    dob             = Column(String(20), nullable=True)
    role            = Column(Enum("Athlete", "Coach", "Member"), default="Athlete")
    auth_provider   = Column(Enum("email", "google"), nullable=False, default="email")
    is_onboarded    = Column(Boolean, default=False)
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    updated_at      = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    onboarding      = relationship("Onboarding", back_populates="user", uselist=False)
    settings        = relationship("UserSettings", back_populates="user", uselist=False)
    weight_logs     = relationship("WeightLog", back_populates="user")
    workout_sessions = relationship("WorkoutSession", back_populates="user")
    user_skills     = relationship("UserSkill", back_populates="user")
    personal_records = relationship("PersonalRecord", back_populates="user")
    daily_logs      = relationship("DailyLog", back_populates="user")


class Onboarding(Base):
    __tablename__ = "onboarding"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    goal            = Column(String(50), nullable=True)      # e.g. "lose", "gain", "fit"
    experience      = Column(String(50), nullable=True)      # "beginner", "intermediate", "advanced"
    gender          = Column(String(10), nullable=True)
    age             = Column(Integer, nullable=True)
    height_cm       = Column(Float, nullable=True)
    current_weight  = Column(Float, nullable=True)
    target_weight   = Column(Float, nullable=True)
    target_days     = Column(Integer, default=30)
    start_date      = Column(String(20), nullable=True)

    user = relationship("User", back_populates="onboarding")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id              = Column(Integer, primary_key=True, index=True)
    user_id         = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    theme           = Column(String(10), default="dark")
    rest_time       = Column(Integer, default=90)         # seconds
    weekly_target   = Column(Integer, default=4)          # days per week
    injury_filters  = Column(JSON, default=list)          # e.g. ["shoulder", "wrist"]

    user = relationship("User", back_populates="settings")
