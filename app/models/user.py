import datetime
from typing import Optional, TYPE_CHECKING
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.models.session import WorkoutSession


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(unique=True, index=True)
    hashed_password: str
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)

    sessions: list["WorkoutSession"] = Relationship(back_populates="user")