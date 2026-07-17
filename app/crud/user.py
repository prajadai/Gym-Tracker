from sqlmodel import Session, select
from app.models.user import User
from app.schemas.user import UserCreate
from app.auth.security import hash_password


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.exec(select(User).where(User.email == email)).first()


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(email=user_in.email, hashed_password=hash_password(user_in.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return user