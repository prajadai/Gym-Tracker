from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.session import SessionCreate, SessionRead, SessionReadGrouped
from app.crud import session as session_crud
from app.auth.dependencies import get_current_user
from app.models.user import User


router = APIRouter()


@router.post("/", response_model=SessionRead)
def create_workout_session(
    session_in: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    return session_crud.create_session(db, session_in, current_user.id)


@router.get("/", response_model=list[SessionRead])
def list_workout_sessions(
    current_user: User = Depends(get_current_user),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_session),
):
    return session_crud.get_sessions(db, current_user.id, skip, limit)


@router.get("/{session_id}", response_model=SessionReadGrouped)
def read_workout_session(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session),
):
    result = session_crud.get_session_grouped_by_exercise(db, session_id, current_user.id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result