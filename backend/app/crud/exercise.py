from sqlmodel import Session, select
from app.models.exercise import Exercise
from app.schemas.exercise import ExerciseCreate


def create_exercise(session: Session, exercise_in: ExerciseCreate) -> Exercise:
    exercise = Exercise.model_validate(exercise_in)
    session.add(exercise)
    session.commit()
    session.refresh(exercise)
    return exercise


def get_exercise(session: Session, exercise_id: int) -> Exercise | None:
    return session.get(Exercise, exercise_id)


def get_exercise_by_name(session: Session, name: str) -> Exercise | None:
    return session.exec(select(Exercise).where(Exercise.name == name)).first()


def get_exercises(session: Session, skip: int = 0, limit: int = 100) -> list[Exercise]:
    return session.exec(select(Exercise).offset(skip).limit(limit)).all()