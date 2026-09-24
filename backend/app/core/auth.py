"""Autenticación: JWT en cookie httpOnly (navegador) o en `Authorization: Bearer` (API).

WO-097:
- La interfaz web usa la cookie `adan_session` (httpOnly, SameSite=Lax, Secure en
  producción): el token ya no vive en `localStorage`, donde un XSS podía leerlo (S15).
- Con la cookie, toda petición que modifica datos debe traer `X-Requested-With: adan`.
  Un sitio ajeno no puede agregar esa cabecera sin pasar por CORS (anti-CSRF).
- Cada token lleva la `token_version` del usuario: cerrar sesión la incrementa y
  revoca todos los tokens emitidos antes.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, Request, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.models.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer(auto_error=False)

SESSION_COOKIE = "adan_session"
CSRF_HEADER = "X-Requested-With"
CSRF_VALUE = "adan"
SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user: User) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user.id,
        "email": user.email,
        "ver": user.token_version or 0,
        "iat": now,
        "exp": now + timedelta(minutes=settings.JWT_EXPIRATION_MINUTES),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def set_session_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        SESSION_COOKIE, token,
        max_age=settings.JWT_EXPIRATION_MINUTES * 60,
        httponly=True,
        samesite="lax",
        secure=settings.ADAN_ENV == "production",
        path="/",
    )


def clear_session_cookie(response: Response) -> None:
    response.delete_cookie(SESSION_COOKIE, path="/", httponly=True, samesite="lax",
                           secure=settings.ADAN_ENV == "production")


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    if credentials:
        token = credentials.credentials
    else:
        token = request.cookies.get(SESSION_COOKIE)
        if token and request.method not in SAFE_METHODS and request.headers.get(CSRF_HEADER) != CSRF_VALUE:
            raise HTTPException(status_code=403, detail="Falta la cabecera X-Requested-With")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated",
                            headers={"WWW-Authenticate": "Bearer"})

    payload = decode_token(token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    if payload.get("ver", 0) != (user.token_version or 0):
        raise HTTPException(status_code=401, detail="La sesión fue cerrada")
    return user
