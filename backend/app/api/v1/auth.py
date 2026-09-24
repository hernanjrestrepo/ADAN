"""Auth endpoints — register, login, logout, me."""
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session

from app.core.auth import (
    clear_session_cookie, create_access_token, get_current_user, hash_password,
    set_session_cookie, verify_password,
)
from app.core.config import settings
from app.core.database import get_db
from app.core.ratelimit import client_ip, limiter, too_many
from app.models.models import User, UserRole
from app.schemas.schemas import (
    TokenResponse, UserLogin, UserRegister, UserResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])

LOGIN_WINDOW_SECONDS = 15 * 60


def _issue_session(user: User, response: Response) -> TokenResponse:
    token = create_access_token(user)
    set_session_cookie(response, token)
    return TokenResponse(access_token=token, user=UserResponse.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=201)
def register(body: UserRegister, request: Request, response: Response, db: Session = Depends(get_db)):
    wait = limiter.hit(f"register:{client_ip(request)}", settings.REGISTER_PER_IP_PER_HOUR, 3600)
    if wait:
        raise too_many(wait, "Demasiados registros desde esta dirección; intenta más tarde", scope="register")

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
    return _issue_session(user, response)


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin, request: Request, response: Response, db: Session = Depends(get_db)):
    # Se cuenta por IP y correo: frena la fuerza bruta sin dejar que un tercero bloquee la cuenta
    # desde cualquier dirección
    key = f"login:{client_ip(request)}:{body.email.lower()}"
    wait = limiter.blocked_for(key, settings.LOGIN_MAX_FAILURES, LOGIN_WINDOW_SECONDS)
    if wait:
        raise too_many(wait, "Demasiados intentos fallidos; intenta más tarde", scope="login")

    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        limiter.hit(key, settings.LOGIN_MAX_FAILURES, LOGIN_WINDOW_SECONDS)
        raise HTTPException(status_code=401, detail="Invalid credentials")

    limiter.reset(key)
    return _issue_session(user, response)


@router.post("/logout", status_code=204)
def logout(response: Response, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Cierra la sesión en todos los dispositivos: revoca los tokens emitidos hasta ahora."""
    current_user.token_version = (current_user.token_version or 0) + 1
    db.commit()
    clear_session_cookie(response)
    response.status_code = 204
    return response


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return UserResponse.model_validate(current_user)
