"""Cifrado de secretos en reposo (credenciales de conectores, WO-097).

Usa ENCRYPTION_KEY (Fernet). Fuera de producción, sin clave, la deriva de JWT_SECRET:
si ese secreto es aleatorio por proceso, las credenciales guardadas dejan de poder
leerse al reiniciar y hay que volver a conectar. En producción ENCRYPTION_KEY es obligatoria.
"""
from __future__ import annotations

import base64
import hashlib
import json

from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings


def _fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY
    if not key:
        key = base64.urlsafe_b64encode(hashlib.sha256(settings.JWT_SECRET.encode()).digest()).decode()
    return Fernet(key)


def encrypt_json(data: dict) -> str:
    return _fernet().encrypt(json.dumps(data).encode()).decode()


def decrypt_json(token: str) -> dict:
    """Devuelve el diccionario cifrado; ValueError si la clave cambió o el dato se alteró."""
    try:
        return json.loads(_fernet().decrypt(token.encode()))
    except InvalidToken as exc:
        raise ValueError("No se pudieron descifrar las credenciales (¿cambió ENCRYPTION_KEY?)") from exc
