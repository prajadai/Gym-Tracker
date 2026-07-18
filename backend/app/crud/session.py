from sqlmodel import Session, select
from app.models.session import WorkoutSession
from app.schemas.session import SessionCreate, SessionReadGrouped, ExerciseGroup, SetInGroup


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


def get_session_grouped_by_exercise(db: Session, session_id: int, user_id: int) -> SessionReadGrouped | None:
    workout_session = get_session_for_user(db, session_id, user_id)
    if not workout_session:
        return None

    groups: dict[int, ExerciseGroup] = {}
    for workout_set in workout_session.sets:
        ex_id = workout_set.exercise_id
        if ex_id not in groups:
            groups[ex_id] = ExerciseGroup(
                exercise_id=ex_id,
                exercise_name=workout_set.exercise.name,
                muscle_group=workout_set.exercise.muscle_group,
                sets=[],
            )
        groups[ex_id].sets.append(
            SetInGroup(
                id=workout_set.id,
                set_number=workout_set.set_number,
                weight=workout_set.weight,
                reps=workout_set.reps,
                rpe=workout_set.rpe,
            )
        )

    exercise_list = list(groups.values())

    return SessionReadGrouped(
        id=workout_session.id,
        date=workout_session.date,
        notes=workout_session.notes,
        total_exercises=len(exercise_list),
        total_sets=sum(len(group.sets) for group in exercise_list),
        exercises=exercise_list,
    )