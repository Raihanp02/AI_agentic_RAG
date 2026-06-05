from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.user.schema.users import UserCreate
from app.user.models.users import User
from app.user.services.password_and_jwt import hash_password

async def create_user(db, user_in: UserCreate) -> User:
    user = User(
        username=user_in.username,
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    return user