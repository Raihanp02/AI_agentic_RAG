from fastapi import FastAPI, Depends, HTTPException, status, APIRouter
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from app.user.schema.users import UserCreate, UserOut, validate_user_create
from app.user.schema.tokens import Token
from app.user.models.users import User
from app.user.services import auth
from core.database.session import get_db_fastapi

router = APIRouter()

# ── Register ──────────────────────────────────────────────
@router.post("/auth/register", response_model=UserOut, status_code=201)
def register(user_in: UserCreate = Depends(validate_user_create), db: Session = Depends(get_db_fastapi)):
    return auth.create_user(db, user_in)

# ── Login → returns JWT ───────────────────────────────────
@router.post("/auth/login", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_fastapi)):
    return auth.login(db, form)

# ── Protected Route ───────────────────────────────────────
@router.get("/users/me", response_model=UserOut)
def read_me(current_user: User = Depends(auth.get_current_active_user)):
    return current_user

# ── Admin: list all users (protected) ────────────────────
@router.get("/users", response_model=list[UserOut])
def list_users(
    db: Session = Depends(get_db_fastapi),
    _: User = Depends(auth.get_current_active_user),
):
    return db.query(User).all()