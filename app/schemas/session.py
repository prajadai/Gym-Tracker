import datetime
from typing import Optional
from sqlmodel import SQLModel
from app.schemas.workout_set import WorkoutSetRead

class SessionCreate(SQLModel):
    date: datetime.date
    notes: Optional[str] = None


class SessionRead(SQLModel):
    id: int
    date: datetime.date
    notes: Optional[str] = None


class SessionReadWithSets(SessionRead):
    sets: list[WorkoutSetRead] = []