import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.workout_set import WorkoutSet


class WorkoutSession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", index=True)
    date: datetime.date = Field(index=True)
    notes: Optional[str] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    user: "User" = Relationship(back_populates="sessions")
    sets: list["WorkoutSet"] = Relationship(back_populates="session")