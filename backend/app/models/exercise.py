from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.workout_set import WorkoutSet

class Exercise(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    muscle_group: Optional[str] = None
    equipment: Optional[str] = None

    sets: list["WorkoutSet"] = Relationship(back_populates="exercise")