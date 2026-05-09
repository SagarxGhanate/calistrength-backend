from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.core.deps import get_db, get_current_user
from app.models.user import User
from app.models.progress import PersonalRecord

router = APIRouter(prefix="/records", tags=["records"])


class RecordIn(BaseModel):
    exercise_name: str
    max_reps: Optional[int] = None
    max_sets: Optional[int] = None
    date_achieved: Optional[str] = None
    notes: Optional[str] = None


@router.post("")
def save_record(
    body: RecordIn,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    existing = db.query(PersonalRecord).filter(
        PersonalRecord.user_id == current_user.id,
        PersonalRecord.exercise_name == body.exercise_name,
    ).first()

    if existing:
        # Only update if new record is higher
        if (body.max_reps or 0) >= (existing.max_reps or 0):
            existing.max_reps      = body.max_reps
            existing.max_sets      = body.max_sets
            existing.date_achieved = body.date_achieved
            existing.notes         = body.notes
            db.commit()
            return {"message": "PR updated", "id": existing.id}
        return {"message": "Existing PR is higher — no update needed"}

    record = PersonalRecord(
        user_id       = current_user.id,
        exercise_name = body.exercise_name,
        max_reps      = body.max_reps,
        max_sets      = body.max_sets,
        date_achieved = body.date_achieved,
        notes         = body.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {"message": "PR saved", "id": record.id}


@router.get("")
def get_records(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    records = db.query(PersonalRecord).filter(
        PersonalRecord.user_id == current_user.id
    ).all()

    return [
        {
            "id": r.id,
            "exercise_name": r.exercise_name,
            "max_reps": r.max_reps,
            "max_sets": r.max_sets,
            "date_achieved": r.date_achieved,
        }
        for r in records
    ]
