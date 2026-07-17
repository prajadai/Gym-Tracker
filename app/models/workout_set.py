from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.session import WorkoutSession
    from app.models.exercise import Exercise


class WorkoutSet(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    session_id: int = Field(foreign_key="workoutsession.id", index=True)
    exercise_id: int = Field(foreign_key="exercise.id", index=True)
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = None

    session: "WorkoutSession" = Relationship(back_populates="sets")
    exercise: "Exercise" = Relationship(back_populates="sets")