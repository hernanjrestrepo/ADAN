"""Archiva (desactiva) un usuario de ADÁN sin borrar sus datos.

El Contrato Base (AD-006 §2) establece que las entidades se archivan, nunca
se eliminan. Un usuario archivado no puede iniciar sesión ni usar tokens
emitidos antes (WO-093).

Uso (desde backend/, con la misma DATABASE_URL que usa la app):
    python -m scripts.archive_user wo090-verify@example.com
    python -m scripts.archive_user wo090-verify@example.com --restore
"""
from __future__ import annotations

import argparse
import sys

from sqlalchemy.orm import Session

from app.core.database import engine, init_db
from app.models.models import EntityStatus, User


def set_status(email: str, status: EntityStatus) -> bool:
    init_db()
    with Session(engine) as db:
        user = db.query(User).filter(User.email == email).first()
        if user is None:
            return False
        user.status = status
        user.version = (user.version or 1) + 1
        db.commit()
        return True


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("email")
    parser.add_argument("--restore", action="store_true", help="reactivar en lugar de archivar")
    args = parser.parse_args(argv)

    status = EntityStatus.ACTIVE if args.restore else EntityStatus.ARCHIVED
    if not set_status(args.email, status):
        print(f"No existe un usuario con email {args.email} (nada que hacer).")
        return 0
    print(f"Usuario {args.email}: {status.value}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
