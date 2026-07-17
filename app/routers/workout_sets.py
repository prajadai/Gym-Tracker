from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.workout_set import WorkoutSetCreate, WorkoutSetRead
from app.crud import workout_set as workout_set_crud
from app.crud import session as session_crud
from app.auth.dependencies import get_current_user
from app.models.user import User

router = APIRouter()


@router.post("/{session_id}", response_model=WorkoutSetRead)
def create_workout_set(
    session_id: int,
    set_in: WorkoutSetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    workout_session = session_crud.get_session_for_user(db, session_id, current_user.id)
    if not workout_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return workout_set_crud.create_workout_set(db, set_in, session_id)


@router.get("/{session_id}", response_model=list[WorkoutSetRead])
def list_workout_sets(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    workout_session = session_crud.get_session_for_user(db, session_id, current_user.id)
    if not workout_session:
        raise HTTPException(status_code=404, detail="Session not found")
    return workout_set_crud.get_sets_for_session(db, session_id)