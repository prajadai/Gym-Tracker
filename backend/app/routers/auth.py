from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from app.database import get_session
from app.schemas.user import UserCreate, UserRead
from app.crud import user as user_crud
from app.auth.security import verify_password, create_access_token, hash_password
from pydantic import BaseModel
from app.config import settings
from app.models.user import User

router = APIRouter()


@router.post("/register", response_model=UserRead)
def register(user_in: UserCreate, db: Session = Depends(get_session)):
    existing = user_crud.get_user_by_email(db, user_in.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_crud.create_user(db, user_in)


@router.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = user_crud.get_user_by_email(db, form_data.username)  # OAuth2 form calls it "username"
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

class AdminRegisterRequest(BaseModel):
    email: str
    password: str
    admin_key: str

@router.post("/register-admin", response_model=UserRead)
def register_admin(payload: AdminRegisterRequest, db: Session = Depends(get_session)):
    if payload.admin_key != settings.admin_secret_key:
        raise HTTPException(status_code=403, detail="Invalid admin key")

    existing = db.exec(select(User).where(User.email == payload.email)).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),  # use whatever hashing fn your existing /register uses
        is_admin=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user