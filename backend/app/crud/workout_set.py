from sqlmodel import Session, select
from app.models.workout_set import WorkoutSet
from app.schemas.workout_set import WorkoutSetCreate


def create_workout_set(db: Session, set_in: WorkoutSetCreate, session_id: int) -> WorkoutSet:
    workout_set = WorkoutSet.model_validate(set_in, update={"session_id": session_id})
    db.add(workout_set)
    db.commit()
    db.refresh(workout_set)
    return workout_set


def get_sets_for_session(db: Session, session_id: int) -> list[WorkoutSet]:
    statement = select(WorkoutSet).where(WorkoutSet.session_id == session_id)
    return db.exec(statement).all()