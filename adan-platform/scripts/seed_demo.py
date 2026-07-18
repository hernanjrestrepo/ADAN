"""Seed demo data - one Empresa end-to-end through the core entity graph.
Run: cd backend && .venv/Scripts/python.exe ../scripts/seed_demo.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.auth.jwt import hash_password
from app.db import SessionLocal
from app.models import Empresa, Nivel, Proyecto, Usuario, Workspace


def seed() -> None:
    db = SessionLocal()
    try:
        existing = db.query(Usuario).filter(Usuario.email == "demo@adan-demo.io").first()
        if existing:
            print("Demo data already seeded, skipping.")
            return

        usuario = Usuario(
            email="demo@adan-demo.io",
            hashed_password=hash_password("demo1234"),
            display_name="Demo Responsable",
        )
        db.add(usuario)
        db.flush()

        empresa = Empresa(razon_social="Paradixe Demo S.A.S.", jurisdiccion="Colombia")
        db.add(empresa)
        db.flush()

        proyecto = Proyecto(empresa_id=empresa.id, usuario_principal_id=usuario.id)
        db.add(proyecto)
        db.flush()

        workspace = Workspace(proyecto_id=proyecto.id)
        db.add(workspace)

        nivel_1 = Nivel(proyecto_id=proyecto.id, numero=1, nombre="El Dolor")
        db.add(nivel_1)

        db.commit()
        print(f"Seeded: Usuario={usuario.id}, Empresa={empresa.id}, Proyecto={proyecto.id}")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
