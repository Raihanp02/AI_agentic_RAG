from pydantic import BaseModel, EmailStr
from app.user.models import User
from sqlalchemy.orm import Session
from fastapi import HTTPException, Depends
from core.database.session import get_db_fastapi

class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    email: str
    is_active: bool

    class Config:
        from_attributes = True

def validate_user_create(user_in: UserCreate, db: Session = Depends(get_db_fastapi)):
    if db.query(User).filter(User.username == user_in.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(User).filter(User.email == user_in.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")