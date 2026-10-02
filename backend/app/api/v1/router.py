"""API v1 router — aggregates all endpoint modules."""
from fastapi import APIRouter

from app.api.v1 import auth, companies, nivel1, cognitive
from app.hire import api as hire
from app.onboarding import api as onboarding
from app.scoring import api as scoring
from app.twin import api as twin

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(companies.router)
router.include_router(nivel1.router)
router.include_router(cognitive.router)
router.include_router(twin.router)
router.include_router(scoring.router)
router.include_router(onboarding.router)
router.include_router(hire.router)
