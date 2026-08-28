"""Authentication endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from ..models.models import Department, User, normalize_name
from ..schemas.schemas import AdminLoginRequest, LoginRequest, RegisterRequest, TokenResponse, UserOut
from ..security.passwords import hash_password, verify_password
from ..security.tokens import create_access_token
from .deps import CurrentUser, DbDep, check_login_rate_limit, reset_login_rate_limit

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbDep, request: Request):
    normalized = normalize_name(payload.full_name)
    if len(normalized.split()) < 2:
        raise HTTPException(400, "Full name must contain at least first and last name.")

    department = db.scalar(select(Department).where(Department.name == payload.department.strip()))
    if department is None:
        raise HTTPException(400, "Invalid department. Select a department from the list.")

    if len(payload.password) < 8:
        raise HTTPException(400, "Password must be at least 8 characters long.")

    if payload.password != payload.confirm_password:
        raise HTTPException(400, "Passwords do not match.")

    existing = db.scalar(select(User).where(User.name_normalized == normalized))
    if existing is not None:
        raise HTTPException(409, "An account with this full name already exists.")

    user = User(
        full_name=normalized,
        name_normalized=normalized,
        department_id=department.id,
        password_hash=hash_password(payload.password),
        role="faculty",
    )
    db.add(user)
    try:
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(409, "An account with this full name already exists.")
    db.refresh(user)

    token = create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=token,
        user=UserOut(id=user.id, full_name=user.full_name, department=department.name, role=user.role),
    )


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: DbDep, request: Request):
    check_login_rate_limit(payload.full_name, request)

    normalized = normalize_name(payload.full_name)
    # Names are globally unique across the platform, so the department is not needed.
    user = db.scalar(select(User).where(User.name_normalized == normalized))

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid full name or password.")

    reset_login_rate_limit(payload.full_name, request)
    token = create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=token,
        user=UserOut(id=user.id, full_name=user.full_name, department=user.department.name, role=user.role),
    )


@router.post("/admin-login", response_model=TokenResponse)
def admin_login(payload: AdminLoginRequest, db: DbDep, request: Request):
    check_login_rate_limit(payload.username, request)

    username = normalize_name(payload.username)
    user = db.scalar(select(User).where(User.full_name == username, User.role == "admin"))

    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(401, "Invalid administrator username or password.")

    reset_login_rate_limit(payload.username, request)
    token = create_access_token(user.id, user.role)
    return TokenResponse(
        access_token=token,
        user=UserOut(id=user.id, full_name=user.full_name, department=user.department.name, role=user.role),
    )


@router.get("/me", response_model=UserOut)
def me(user: CurrentUser):
    return UserOut(
        id=user.id, full_name=user.full_name, department=user.department.name, role=user.role
    )
