from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.user.schema.users import UserCreate
from app.user.models.users import User
from app.user.services import auth

def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=auth.hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return user