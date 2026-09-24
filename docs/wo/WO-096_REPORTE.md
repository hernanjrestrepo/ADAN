# WO-096 — Consolidación de builds y documentación

**Fecha:** 2026-09-24 · **Ejecutor:** Claude Code · **Autoriza:** Hernán ("haz todo lo que tengas que hacer", 2026-09-24)
**Formato:** EPWO-050 · **Checklist:** EPWO-051
**Estado:** 🟡 **ABIERTA.** Está hecho todo lo que no depende de la laptop. Falta importar Build B, que vive solo en el monorepo local de Hernán (§4).

---

## 1. Fase -1 (AD-GOV-0001, Regla 7)

| Verificación | Resultado |
|---|---|
| Canon | `AD-ROOT-0001`, `AD-GOV-0001`, `AD-DEC-0001` y `AD-DEC-0002` leídos. `main` en `370d7e9` (WO-095 fusionada, hernanjrestrepo/ADAN#2). |
| Reutilización (EPWO-022) | Se compararon archivo por archivo `docs/wo-000/` (Build C) y `adan-platform/docs/blueprint/source/wo-000/` (Build A): **27 idénticos**, **5 solo en Build A** y `kg.json` distinto (el de Build A es un superconjunto). Nada se reescribe: se copia. |
| Alcance congelado | La ficha de WO-096 en `PLAN_WO_ADAN_100.md` §4. |
| Numeración | WO-096 está en el rango asignado WO-095 → 099. |
| Camino crítico | Importar Build B, porque depende de la laptop. El resto no tiene dependencias. |
| Aprobación | Hernán aprobó el plan, 2026-09-24. |

Hallazgo bloqueante **solo para el punto de Build B**. El resto de la WO avanzó.

## 2. Qué se hizo

| Entregable | Resultado |
|---|---|
| Blueprint más nuevo en `docs/wo-000/` | Se copiaron desde Build A: `AD-003` v1.2, `AD-006` v1.2, `AD-FUNC-07` (Scoring), `AD-FUNC-08` (User Journey) y `AD-FUNC-09` (Learning Engine). `kg.json` se reemplazó por la versión de Build A, con las rutas corregidas a `docs/wo-000/`. Build A queda intacto. |
| AD-000 v2.0 | `docs/wo-000/00-fundamentos/AD-000_Paradixe_Ecosystem_Vision_v2.0.md`, según AD-DEC-0002: EVA (antes ARQAI) = ventas y marketing; Genexis interno; Comunidad; agentes por tiempo; finanzas del Nivel 3 con el CFO de ADÁN + CSI; aviso de IA. La v1.0 se conserva. Lista los documentos que quedan desactualizados y la WO que actualiza cada uno. |
| Mapa del blueprint | `docs/wo-000/BLUEPRINT_ADAN_v1.1.md`: parte de la v1.0 de Build A, sin la frase "fuente única de verdad" (Regla 6). Agrega el estado de implementación en Build C y tres hallazgos nuevos: H-6 (solapamiento EVA–ATO), H-7 (ERP y contabilidad sin dueño) y H-8 (concepto duplicado en `kg.json`). |
| Grafo de conocimiento | AD-000 → v2.0. 3 conceptos nuevos: *Agente por tiempo*, *Comunidad* y *Aviso de IA*. 5 relaciones nuevas. Totales: 39 conceptos y 106 relaciones. Todas las rutas del grafo existen en disco (verificado). |
| Mapa de reutilización A → C | `docs/wo/WO-096_MAPA_REUTILIZACION.md`: 20 piezas de Build A con su equivalente en Build C, la decisión (traer, adaptar, referencia o descartar) y la WO que las usa. Encontró que el API del grafo de Build A autentica pero no verifica que el proyecto sea del usuario; solo se trae con esa verificación (WO-097). La sección de Build B queda con los candidatos, pendiente de la importación. |
| `.claude/launch.json` | Apuntaba a rutas de Build B en la laptop (`adan-integration\...`). Ahora usa rutas relativas a este repositorio: backend en `:8020` y frontend en `:5173`. El proxy de Vite toma `ADAN_API_URL`: Docker Compose la fija en `http://backend:8000` y en local vale `http://localhost:8020` por defecto. |
| `ADAN_MASTER_ARCHITECTURE_v1.0.md` | Las reglas 1 ("Single Source of Truth") y 5 ("tiene prioridad") quedan tachadas, con una nota que cita `AD-ROOT-0001 §5`. El texto original se conserva. |
| Canon y README | `AD-ROOT-0001` §5, §6, nota de `launch.json` e historial. El README agrega el mapa del blueprint, AD-000 v2.0, el mapa de reutilización y el arranque sin Docker. |

## 3. Evidencia

| Evidencia | Resultado | Método |
|---|---|---|
| Comparación del blueprint | 27 iguales, 5 solo en A, `kg.json` distinto | `cmp` archivo por archivo |
| `kg.json` de Build A contiene al de Build C | Sí. Solo difiere la fecha de actualización. | Comparación de IDs por sección |
| Rutas del grafo | Todas existen | Script sobre cada `path` |
| Proxy de Vite | Sin `ADAN_API_URL` apunta a `127.0.0.1:8020` | `vite` levantado y petición a `/api` |
| `docker-compose.yml` | YAML válido; el frontend recibe `ADAN_API_URL` | `yaml.safe_load` |
| Sin autodeclaraciones de fuente única | Ningún documento vigente de la raíz la tiene | `grep` |

No se tocó código de backend: la suite de pruebas no cambia (261 passed en WO-095).

## 4. Pendiente: importar Build B (requiere la laptop)

Build B está en la rama `adan/platform-integration` del monorepo `C:\Users\herna\Documents\Paradixe\repos`, carpeta `repos-active/adan`. Ese monorepo tiene datos de contactos de Claro, **así que nunca se sube completo**. Solo se extrae la carpeta de ADÁN, con su historial.

Pasos en PowerShell, uno a la vez:

1. `cd C:\Users\herna\Documents\Paradixe\repos`
2. `git subtree split --prefix=repos-active/adan -b build-b adan/platform-integration`
   Crea la rama `build-b` solo con la historia de esa carpeta.
3. `git log build-b --name-only --format="" | Sort-Object -Unique`
   Lista **todos** los archivos que alguna vez existieron en esa historia. Revisa que no aparezca `.env`, ni archivos de clientes, ni nada de Claro.
4. `git grep -I -n -E "(password|secret|api[_-]?key|token)\s*[:=]" build-b | Select-Object -First 40`
   Busca secretos en la última versión.
5. Si los pasos 3 y 4 salen limpios:
   `git push https://github.com/hernanjrestrepo/ADAN.git build-b:import/build-b`

Con la rama `import/build-b` en GitHub, la sesión la mueve a la carpeta `build-b/` (igual que se hizo con Build A) y la fusiona conservando autores y fechas. Después completa la sección 2 del mapa de reutilización y cierra esta WO.

## 5. Deuda y riesgos

- **H-6, H-7 y H-8** del mapa del blueprint quedan abiertos. H-6 y H-7 los decide Hernán, en WO-100 o en un AD-DEC. H-8 es menor y se corrige en la próxima actualización del grafo.
- **Documentos del blueprint desactualizados por AD-000 v2.0:** AD-001 §1.1, AD-FUNC-01 (Nivel 3), AD-FUNC-03, AD-FUNC-05, AD-FUNC-06 y el índice maestro. Cada uno se versiona en la WO que lo toque (tabla de AD-000 v2.0).
- **`.claude/launch.json`:** usa `python` del PATH. En la laptop hay que activar antes el entorno virtual del backend (`backend\.venv\Scripts\Activate.ps1`).

## 6. Checklist EPWO-051

- [x] Evidencia objetiva ejecutada (§3).
- [x] Pruebas: no aplica cambio de código de backend.
- [x] Documentación y deuda registradas.
- [x] `git status` limpio al hacer el commit.
- [x] Reporte en `docs/wo/`.
- [ ] Build B importado (§4): **pendiente de la laptop**.
- [ ] PR fusionado a `main` con la WO completa. Se fusiona un PR parcial con lo hecho; la WO se cierra en otro PR cuando llegue Build B.
