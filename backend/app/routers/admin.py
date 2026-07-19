from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.database import get_session
from app.auth.dependencies import get_current_admin
from app.models.user import User
from app.models.session import WorkoutSession
from app.models.workout_set import WorkoutSet
from app.models.exercise import Exercise
from app.schemas.user import AdminUserRead

router = APIRouter()


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # manually cascade: delete sets -> sessions -> user (no ON DELETE CASCADE set up)
    sessions = db.exec(select(WorkoutSession).where(WorkoutSession.user_id == user_id)).all()
    for s in sessions:
        sets = db.exec(select(WorkoutSet).where(WorkoutSet.session_id == s.id)).all()
        for st in sets:
            db.delete(st)
        db.delete(s)

    db.delete(user)
    db.commit()
    return {"detail": f"User {user_id} and all associated data deleted"}


@router.delete("/sessions/{session_id}")
def delete_session(
    session_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    session_obj = db.get(WorkoutSession, session_id)
    if not session_obj:
        raise HTTPException(status_code=404, detail="Session not found")

    sets = db.exec(select(WorkoutSet).where(WorkoutSet.session_id == session_id)).all()
    for st in sets:
        db.delete(st)

    db.delete(session_obj)
    db.commit()
    return {"detail": f"Session {session_id} deleted"}


@router.delete("/exercises/{exercise_id}")
def delete_exercise(
    exercise_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    exercise = db.get(Exercise, exercise_id)
    if not exercise:
        raise HTTPException(status_code=404, detail="Exercise not found")

    in_use = db.exec(select(WorkoutSet).where(WorkoutSet.exercise_id == exercise_id)).first()
    if in_use:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete exercise: it has workout sets referencing it",
        )

    db.delete(exercise)
    db.commit()
    return {"detail": f"Exercise {exercise_id} deleted"}


@router.get("/users", response_model=list[AdminUserRead])
def list_all_users(
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    return db.exec(select(User)).all()

@router.delete("/workout-sets/{set_id}")
def delete_workout_set(
    set_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_session),
):
    workout_set = db.get(WorkoutSet, set_id)
    if not workout_set:
        raise HTTPException(status_code=404, detail="Workout set not found")

    db.delete(workout_set)
    db.commit()
    return {"detail": f"Workout set {set_id} deleted"}