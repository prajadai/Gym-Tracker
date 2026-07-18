from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.analytics import ExerciseProgressResponse
from app.crud import analytics as analytics_crud
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/progress/{exercise_id}", response_model=ExerciseProgressResponse)
def get_exercise_progress(
    exercise_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    result = analytics_crud.get_exercise_progress(db, exercise_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return result