from sqlalchemy import Column, Integer, String, DateTime, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base


class Skill(Base):
    """Master list of all 27 calisthenics skills — seeded once at startup."""
    __tablename__ = "skills"

    id              = Column(Integer, primary_key=True, index=True)
    skill_key       = Column(String(50), unique=True, nullable=False)  # e.g. "muscle-ups"
    name            = Column(String(100), nullable=False)
    category        = Column(Enum("beginner", "intermediate", "advanced", "elite"), nullable=False)
    freq            = Column(String(50), nullable=True)   # "3x per week"
    img_path        = Column(String(255), nullable=True)
    requirements    = Column(JSON, nullable=True)          # ["Dead Hang — 1 min", ...]
    badge           = Column(String(20), nullable=True)    # "HOT", etc.

    user_skills = relationship("UserSkill", back_populates="skill")


class UserSkill(Base):
    """Which skills a user is currently working on or has mastered."""
    __tablename__ = "user_skills"

    id          = Column(Integer, primary_key=True, index=True)
    user_id     = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True)
    skill_id    = Column(Integer, ForeignKey("skills.id", ondelete="CASCADE"), index=True)
    status      = Column(Enum("ongoing", "mastered"), nullable=False, default="ongoing")
    started_at  = Column(DateTime(timezone=True), server_default=func.now())
    mastered_at = Column(DateTime(timezone=True), nullable=True)

    user  = relationship("User", back_populates="user_skills")
    skill = relationship("Skill", back_populates="user_skills")
