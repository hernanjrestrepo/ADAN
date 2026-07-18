# WO-003 Sprint 6 — Pruebas y documentación

**Célula:** A/C · **Fecha:** 2026-07-18

## Resumen ejecutivo

Corpus demo real (`scripts/seed_kg_corpus_demo.py`): 4 hechos de negocio conectados causalmente en el grafo (competidor lanza versión gratuita → clientes cancelan → ventas propone bajar precio → junta aprueba revisar estrategia), indexados con embeddings reales, consultados con la consulta híbrida. Verificación final completa de las tres suites tras cinco sprints de esta WO.

## Archivos creados

`scripts/seed_kg_corpus_demo.py`.

## Evidencias objetivas — el resultado más significativo de la WO

Consulta real contra el corpus demo: **"por qué estamos perdiendo clientes"**

```
[semantico, distancia=0.339] Tres clientes cancelaron su suscripcion mencionando el precio como razon principal
[semantico, distancia=0.447] Un competidor directo lanzo una version gratuita de su producto en marzo
[semantico, distancia=0.489] El equipo de ventas propuso bajar el precio de entrada en un 20%
[grafo,     distancia=0.789] La junta directiva aprobo revisar la estrategia de precios en el proximo trimestre
```

El sistema encuentra correctamente el hecho más relevante por significado (las cancelaciones), y **rescata por el grafo** la decisión de la junta — un hecho que no menciona "clientes" ni "perdiendo" en absoluto, pero que está causalmente conectado. Esto es, literalmente, la razón de ser de la consulta híbrida (Sprint 3) funcionando sobre un caso de negocio realista, no sobre datos sintéticos triviales.

- `ai`: `ruff check .` limpio, **24 passed** en 75s.
- `backend`: `ruff check .` limpio, **11 passed**.
- `frontend`: `npm run lint` / `npm run build` limpios.
- E2E completo contra el stack real en Docker: **4 passed** (smoke, agente de diagnóstico, exploración del KG, ruta privada).

## Tiempo real (Wall Clock)

~20 minutos.

## Estado del Sprint

COMPLETO
