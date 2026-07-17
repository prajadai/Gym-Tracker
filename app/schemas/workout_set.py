from typing import Optional
from sqlmodel import SQLModel


class WorkoutSetCreate(SQLModel):
    exercise_id: int
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = None


class WorkoutSetRead(SQLModel):
    id: int
    exercise_id: int
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = None