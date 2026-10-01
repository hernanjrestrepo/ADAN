"""Auth endpoints — register, login, me."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.auth import (
    create_access_token, get_current_user, hash_password, verify_password,
)
from app.core.database import get_db
from app.core.security import limit_auth_attempts
from app.models.models import EntityStatus, User, UserRole
from app.schemas.schemas import (
    TokenResponse, UserLogin, UserRegister, UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Hash fijo para gastar el mismo tiempo cuando el email no existe y no
# revelar por latencia qué cuentas están registradas.
_DUMMY_HASH = hash_password("timing-equalizer")


@router.post(
    "/register", response_model=TokenResponse, status_code=201,
    dependencies=[Depends(limit_auth_attempts)],
)
def register(body: UserRegister, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(
        email=body.email,
        name=body.name,
        hashed_password=hash_password(body.password),
        role=UserRole.PRIMARY_USER,
        created_by=None,
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.post("/login", response_model=TokenResponse, dependencies=[Depends(limit_auth_attempts)])
def login(body: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    password_ok = verify_password(body.password, user.hashed_password if user else _DUMMY_HASH)
    if not user or not password_ok or user.status != EntityStatus.ACTIVE:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_access_token(user.id, user.email)
    return TokenResponse(
        access_token=token,
        user=UserResponse.model_validate(user),
    )


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
