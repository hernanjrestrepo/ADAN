# ADAN

Sistema operativo empresarial de Paradixe: agentes especializados (Board de 7 roles), memoria empresarial (EMS), ejecución de herramientas (TEF), gestión operativa (OOS), adquisición de conocimiento (DKA), voz y omnicanal, sobre modelos locales vía Ollama.

Este repositorio reúne en un solo lugar todo el código de ADAN que existía por separado.

## Qué hay en este repositorio

| Ubicación | Qué es | Estado | Origen |
|---|---|---|---|
| Raíz: `backend/`, `frontend/`, `docs/`, `scripts/`, `docker-compose.yml` | **Build C**, "Vertical Nivel 1". FastAPI + SQLite + React (JSX) + Ollama. | **Línea oficial** (`AD-DEC-0001 §5.1`) | Carpeta `repos-active/adan` de la laptop. No tenía historial de git; su primer commit es `abc6b6c`. |
| `adan-platform/` | **Build A**. Monorepo FastAPI + PostgreSQL/pgvector + React/TypeScript, WO-000 → WO-003. | Archivo histórico, sin más desarrollo (`AD-DEC-0001 §5.2`) | Repo local sin remote. Sus 25 commits se conservan. |
| `autonomous/` | Prototipo de 2024: Lambda que crea clones de sí misma, código autogenerado y despliegue con CodePipeline/CodeBuild. | Histórico | `hernanjrestrepo/adan_autonomous`. Sus 14 commits se conservan (último original: `2fab0bc`). |

**Build B** (rama `adan/platform-integration` del monorepo compartido `Paradixe/repos`, WO-000 → WO-012, tag `v1.0.0`) no está aquí: sigue viviendo en ese monorepo como referencia técnica (`AD-DEC-0001 §5.3`).

`hernanjrestrepo/ADAN-BACK` estaba vacío (sin commits), así que no aportó contenido.

Los historiales importados se reescribieron para vivir bajo su carpeta, con autores y fechas intactos: `git log -- adan-platform/` y `git log -- autonomous/`.

## Por dónde empezar

1. `AD-ROOT-0001_Canon_del_Proyecto.md`: repositorio, rama, arquitectura y numeración oficiales. Leer antes de escribir código.
2. `AD-DEC-0001_Historia_Oficial_de_ADAN.md`: por qué existen tres builds y cuál es la oficial.
3. `AD-GOV-0001_Reglas_de_Desarrollo.md`: reglas de proceso.
4. `REPORTE_CONSOLIDACION_WO090.md`: estado de Build C al 2026-07-31 (WO-090 abierta).
5. `docs/auditoria/AUDITORIA_ADAN_2026-09.md`: auditoría completa del código, avance (~22 %), bugs y brechas frente al blueprint.
6. `docs/auditoria/PLAN_WO_ADAN_100.md`: plan de Work Orders propuesto para llegar al 100 %.

Este repositorio y su rama `main` son los oficiales desde el 2026-09-24 (`AD-ROOT-0001 §1-2`).

## Arranque rápido (Build C)

```bash
export JWT_SECRET=<un-secreto-propio>   # obligatorio fuera de desarrollo
docker compose up --build
```

- API: http://localhost:8050 (`/health`, `/docs`)
- Web: http://localhost:5174
- Ollama: http://localhost:11434. El modelo por defecto es `qwen2.5:0.5b` (`DEFAULT_MODEL`) y lo descarga el servicio `model-pull`.

Pruebas del backend:

```bash
cd backend
pip install -r requirements.txt pytest pytest-asyncio pytest-cov aiohttp
pytest
```

`tests/test_stress.py` necesita el backend levantado en `localhost:8050`.

## Despliegue de `autonomous/`

Si se conecta un proyecto de CodeBuild a este repositorio, configura la ruta del buildspec como `autonomous/buildspec.yml`. CodeBuild ejecuta los comandos desde la raíz del repo, por eso las pruebas se invocan con `pytest autonomous/tests/`.
