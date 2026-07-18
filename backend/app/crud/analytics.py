from sqlmodel import Session, select
from app.models.workout_set import WorkoutSet
from app.models.session import WorkoutSession
from app.models.exercise import Exercise
from app.schemas.analytics import ExerciseProgressPoint, ExerciseProgressResponse


def get_exercise_progress(db: Session, exercise_id: int, user_id: int) -> ExerciseProgressResponse | None:
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        return None

    statement = (
        select(WorkoutSet, WorkoutSession)
        .join(WorkoutSession, WorkoutSet.session_id == WorkoutSession.id)
        .where(WorkoutSet.exercise_id == exercise_id)
        .where(WorkoutSession.user_id == user_id)
        .order_by(WorkoutSession.date)
    )
    rows = db.exec(statement).all()

    if not rows:
        return ExerciseProgressResponse(
            exercise_id=exercise.id,
            exercise_name=exercise.name,
            history=[],
            personal_best_weight=0.0,
        )

    sessions_map: dict[int, dict] = {}
    for workout_set, workout_session in rows:
        if workout_session.id not in sessions_map:
            sessions_map[workout_session.id] = {
                "session_id": workout_session.id,
                "date": workout_session.date,
                "max_weight": 0.0,
                "total_volume": 0.0,
                "total_sets": 0,
            }
        entry = sessions_map[workout_session.id]
        entry["max_weight"] = max(entry["max_weight"], workout_set.weight)
        entry["total_volume"] += workout_set.weight * workout_set.reps
        entry["total_sets"] += 1

    history = [ExerciseProgressPoint(**data) for data in sessions_map.values()]
    personal_best = max(point.max_weight for point in history)

    return ExerciseProgressResponse(
        exercise_id=exercise.id,
        exercise_name=exercise.name,
        history=history,
        personal_best_weight=personal_best,
    )