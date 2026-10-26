"""API v1 router — aggregates all endpoint modules."""
from fastapi import APIRouter

from app.api.v1 import auth, companies, nivel1, cognitive
from app.constitucion import api as constitucion
from app.finanzas import api as finanzas
from app.community import api as comunidad
from app.apples import admin_api as consola
from app.levels import api as niveles
from app.levels import herramientas
from app.empresa import api as empresa
from app.apples import api as apples
from app.hire import api as hire
from app.surveys import api as surveys
from app.onboarding import api as onboarding
from app.scoring import api as scoring
from app.twin import api as twin
from app.visitas import api as visitas
from app.genexis import api as genexis

router = APIRouter(prefix="/api/v1")

router.include_router(auth.router)
router.include_router(companies.router)
router.include_router(nivel1.router)
router.include_router(cognitive.router)
router.include_router(twin.router)
router.include_router(scoring.router)
router.include_router(onboarding.router)
router.include_router(hire.router)
router.include_router(constitucion.router)
router.include_router(surveys.router)
router.include_router(finanzas.router)
router.include_router(comunidad.router)
router.include_router(apples.router)
router.include_router(consola.router)
router.include_router(niveles.router)
router.include_router(empresa.router)
router.include_router(herramientas.router)
router.include_router(visitas.router)
router.include_router(genexis.router)
