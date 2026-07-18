import datetime
from sqlmodel import SQLModel


class ExerciseProgressPoint(SQLModel):
    session_id: int
    date: datetime.date
    max_weight: float
    total_volume: float   # sum of (weight * reps) across all sets that day
    total_sets: int


class ExerciseProgressResponse(SQLModel):
    exercise_id: int
    exercise_name: str
    history: list[ExerciseProgressPoint]
    personal_best_weight: float