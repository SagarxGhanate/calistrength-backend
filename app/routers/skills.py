from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import datetime
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.skill import Skill, UserSkill

router = APIRouter(prefix="/skills", tags=["skills"])


@router.get("")
def get_all_skills(db: Session = Depends(get_db)):
    skills = db.query(Skill).all()
    return [
        {
            "id": s.id,
            "skill_key": s.skill_key,
            "name": s.name,
            "category": s.category,
            "freq": s.freq,
            "img_path": s.img_path,
            "requirements": s.requirements,
            "badge": s.badge,
        }
        for s in skills
    ]


@router.get("/user")
def get_user_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_skills = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id
    ).all()

    ongoing  = []
    mastered = []

    for us in user_skills:
        s = us.skill
        entry = {
            "id": s.id,
            "skill_key": s.skill_key,
            "name": s.name,
            "category": s.category,
            "freq": s.freq,
            "img_path": s.img_path,
            "requirements": s.requirements,
            "started_at": us.started_at.isoformat() if us.started_at else None,
        }
        if us.status == "mastered":
            entry["mastered_at"] = us.mastered_at.isoformat() if us.mastered_at else None
            mastered.append(entry)
        else:
            ongoing.append(entry)

    return {"ongoing": ongoing, "mastered": mastered}


class SkillAction(BaseModel):
    skill_key: str


@router.post("/start")
def start_skill(
    body: SkillAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = db.query(Skill).filter(Skill.skill_key == body.skill_key).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    existing = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill.id,
    ).first()

    if existing:
        return {"message": "Already tracking this skill"}

    db.add(UserSkill(
        user_id  = current_user.id,
        skill_id = skill.id,
        status   = "ongoing",
    ))
    db.commit()
    return {"message": "Skill started"}


@router.post("/master")
def master_skill(
    body: SkillAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = db.query(Skill).filter(Skill.skill_key == body.skill_key).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    us = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill.id,
    ).first()

    if us:
        us.status      = "mastered"
        us.mastered_at = datetime.datetime.utcnow()
    else:
        db.add(UserSkill(
            user_id     = current_user.id,
            skill_id    = skill.id,
            status      = "mastered",
            mastered_at = datetime.datetime.utcnow(),
        ))
    db.commit()
    return {"message": "Skill mastered"}


@router.delete("/remove")
def remove_skill(
    body: SkillAction,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = db.query(Skill).filter(Skill.skill_key == body.skill_key).first()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    us = db.query(UserSkill).filter(
        UserSkill.user_id == current_user.id,
        UserSkill.skill_id == skill.id,
    ).first()

    if us:
        db.delete(us)
        db.commit()
    return {"message": "Skill removed"}
