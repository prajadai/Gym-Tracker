from sqlmodel import Session, select
from app.models.session import WorkoutSession
from app.schemas.session import SessionCreate


def create_session(db: Session, session_in: SessionCreate, user_id: int) -> WorkoutSession:
    workout_session = WorkoutSession.model_validate(session_in, update={"user_id": user_id})
    db.add(workout_session)
    db.commit()
    db.refresh(workout_session)
    return workout_session


def get_session_by_id(db: Session, session_id: int) -> WorkoutSession | None:
    return db.get(WorkoutSession, session_id)


def get_sessions(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> list[WorkoutSession]:
    statement = (
        select(WorkoutSession)
        .where(WorkoutSession.user_id == user_id)
        .offset(skip)
        .limit(limit)
    )
    return db.exec(statement).all()

def get_session_for_user(db: Session, session_id: int, user_id: int) -> WorkoutSession | None:
    workout_session = db.get(WorkoutSession, session_id)
    if workout_session and workout_session.user_id == user_id:
        return workout_session
    return None