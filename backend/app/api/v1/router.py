"""API v1 router — aggregates all endpoint modules."""
from fastapi import APIRouter

from app.api.v1 import auth, companies, nivel1, cognitive

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(companies.router)
router.include_router(nivel1.router)
router.include_router(cognitive.router)
