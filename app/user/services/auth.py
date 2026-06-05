from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.user.models import User
from jose import JWTError, jwt

from app.user.services.password_and_jwt import create_access_token, verify_password
from core.database.session import get_db_fastapi
from app.user.schema.tokens import TokenData
from core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/login")

# --- User Auth ---
async def authenticate_user(db, username: str, password: str):
    user = await db.execute(select(User).filter(User.username == username))
    user = user.scalars().first()
    if not user or not verify_password(password, user.hashed_password):
        return None
    return user

# --- Dependency: Get Current User from Token ---
async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db_fastapi)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = await db.execute(select(User).filter(User.username == token_data.username))
    user = user.scalars().first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def login(db, form: OAuth2PasswordRequestForm) -> dict:
    user = await authenticate_user(db, form.username, form.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": token, "token_type": "bearer"}