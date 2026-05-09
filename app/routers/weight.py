from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.progress import WeightLog

router = APIRouter(prefix="/weight", tags=["weight"])


class WeightIn(BaseModel):
    date: str
    weight_kg: float
    notes: Optional[str] = None


@router.post("")
def add_weight(
    body: WeightIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Check if already logged today
    existing = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id,
        WeightLog.date == body.date,
    ).first()

    if existing:
        # Update instead of block
        existing.weight_kg = body.weight_kg
        existing.notes = body.notes
        db.commit()
        return {"message": "Weight updated", "id": existing.id}

    log = WeightLog(
        user_id   = current_user.id,
        date      = body.date,
        weight_kg = body.weight_kg,
        notes     = body.notes,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return {"message": "Weight logged", "id": log.id}


@router.get("")
def get_weight_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    logs = db.query(WeightLog).filter(
        WeightLog.user_id == current_user.id
    ).order_by(WeightLog.date.asc()).all()

    return [
        {"id": l.id, "date": l.date, "weight_kg": l.weight_kg, "notes": l.notes}
        for l in logs
    ]
