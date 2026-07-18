from typing import Optional
from sqlmodel import SQLModel


class ExerciseCreate(SQLModel):
    name: str
    muscle_group: Optional[str] = None
    equipment: Optional[str] = None


class ExerciseRead(SQLModel):
    id: int
    name: str
    muscle_group: Optional[str] = None
    equipment: Optional[str] = None