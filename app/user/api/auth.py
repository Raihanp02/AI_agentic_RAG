from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import timedelta

from app.user.schema.users import UserCreate, UserOut, validate_user_create
from app.user.schema.tokens import Token
from app.user.models.users import User
from app.user.services import auth
from app.user.services.user import create_user
from core.database.session import get_db_fastapi

router = APIRouter()

# ── Register ──────────────────────────────────────────────
@router.post("/auth/register", response_model=UserOut, status_code=201)
async def register(user_in: UserCreate = Depends(validate_user_create), db: AsyncSession = Depends(get_db_fastapi)):
    return await create_user(db, user_in)

# ── Login → returns JWT ───────────────────────────────────
@router.post("/auth/login", response_model=Token)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db_fastapi)):
    return await auth.login(db, form)

# ── Protected Route ───────────────────────────────────────
@router.get("/users/me", response_model=UserOut)
def read_me(current_user: User = Depends(auth.get_current_active_user)):
    return current_user

# ── Admin: list all users (protected) ────────────────────
@router.get("/users", response_model=list[UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db_fastapi),
    _: User = Depends(auth.get_current_active_user),
):
    result = await db.execute(select(User))
    return result.scalars().all()