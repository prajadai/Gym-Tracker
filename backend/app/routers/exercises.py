from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from app.database import get_session
from app.schemas.exercise import ExerciseCreate, ExerciseRead
from app.crud import exercise as exercise_crud

router = APIRouter()


@router.post("/", response_model=ExerciseRead)
def create_exercise(exercise_in: ExerciseCreate, session: Session = Depends(get_session)):
    existing = exercise_crud.get_exercise_by_name(session, exercise_in.name)
    if existing:
        raise HTTPException(status_code=400, detail="Exercise name already exists")
    return exercise_crud.create_exercise(session, exercise_in)


@router.get("/", response_model=list[ExerciseRead])
def list_exercises(skip: int = 0, limit: int = 100, session: Session = Depends(get_session)):
    return exercise_crud.get_exercises(session, skip, limit)


@router.get("/{exercise_id}", response_model=ExerciseRead)
def read_exercise(exercise_id: int, session: Session = Depends(get_session)):
    exercise = exercise_crud.get_exercise(session, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")
    return exercise