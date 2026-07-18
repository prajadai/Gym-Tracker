import datetime
from typing import Optional
from sqlmodel import SQLModel


class SessionCreate(SQLModel):
    date: datetime.date
    notes: Optional[str] = None


class SessionRead(SQLModel):
    id: int
    date: datetime.date
    notes: Optional[str] = None


class SetInGroup(SQLModel):
    id: int
    set_number: int
    weight: float
    reps: int
    rpe: Optional[float] = None


class ExerciseGroup(SQLModel):
    exercise_id: int
    exercise_name: str
    muscle_group: Optional[str] = None
    sets: list[SetInGroup]


class SessionReadGrouped(SessionRead):
    exercises: list[ExerciseGroup] = []

class SessionReadGrouped(SessionRead):
    total_exercises: int
    total_sets: int
    exercises: list[ExerciseGroup] = []