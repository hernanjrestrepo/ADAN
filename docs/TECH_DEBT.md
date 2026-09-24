# TECH_DEBT — Deuda Técnica ADÁN Nivel 1

**Fecha de Registro:** 2026-07-24  
**WO de Origen:** WO-001 (Cerrada)  
**Estado:** Documentado — No corregido (regla WO-002)

---

## Reglas

- **No corregir nada.** Solo documentar.
- Cada punto incluye: descripción, impacto, prioridad, complejidad, recomendación.
- Las correcciones deberán pasar por una Work Order específica.

---

## TD-001: Streaming de Respuestas (SSE Parcial)

**Descripción:**  
El endpoint `/nivel1/{id}/chat-stream` está parcialmente implementado. El streaming SSE funciona para el chat básico pero no está integrado con el Board Room ni con la generación de diagnósticos.

**Impacto:**  
Los usuarios experimentan esperas largas sin feedback visual durante operaciones pesadas (Board Room ~23s, Diagnóstico ~15s). Experiencia de usuario degradada.

**Prioridad:** ALTA  
**Complejidad:** MEDIA  

**Recomendación:**  
Implementar SSE completo para Board Room y Diagnóstico. Usar el patrón ya existente en chat-stream como base. Considerar streaming de progreso (agente por agente en Board Room).

---

## TD-002: Memoria entre Sesiones

**Descripción:**  
El sistema no preserva contexto entre sesiones de chat. Cada nueva conversación comienza sin memoria de interacciones anteriores del usuario con la empresa. Solo hay un resumen básico por conversación.

**Impacto:**  
El usuario debe re-explicar contexto en cada sesión. La experiencia no es continua como la de un "ejecutivo que nunca pierde contexto" (promesa del producto).

**Prioridad:** ALTA  
**Complejidad:** ALTA  

**Recomendación:**  
Implementar un sistema de memoria persistente que:
1. Resuma conversaciones anteriores y los incluya en el system prompt
2. Mantenga un "estado mental" de la empresa actualizado
3. Use el Gemelo Digital como fuente de verdad para contexto

---

## TD-003: Rate Limiting

**Descripción:**  
No existe rate limiting en ningún endpoint de la API. Cualquier cliente puede hacer llamadas ilimitadas.

**Impacto:**  
Vulnerabilidad a abuso, DoS accidental, consumo descontrolado de recursos de Ollama (CPU).

**Prioridad:** MEDIA  
**Complejidad:** BAJA  

**Recomendación:**  
Implementar rate limiting con `slowapi` o similar. Límites sugeridos:
- Auth endpoints: 10 req/min por IP
- Chat: 30 req/min por usuario
- Board Room: 5 req/min por usuario (costoso en CPU)
- Otros: 60 req/min por usuario

---

## TD-004: Alembic Migrations

**Descripción:**  
El schema de la BD se crea con `Base.metadata.create_all()` al inicio de la aplicación. No hay sistema de migraciones.

**Impacto:**  
Imposible evolucionar el schema de la BD de forma segura. Cualquier cambio de modelo requiere borrado y recreación de la BD (pérdida de datos).

**Prioridad:** MEDIA  
**Complejidad:** MEDIA  

**Recomendación:**  
1. Instalar Alembic
2. Generar migración inicial del estado actual
3. Configurar para que las migraciones se ejecuten automáticamente al arrancar
4. Cambiar `create_all()` por `alembic upgrade head`

---

## TD-005: Logging Estructurado

**Descripción:**  
Existe un formatter JSON en `core/logging.py` pero no está integrado con los logs de la aplicación. Los logs actuales van a stdout sin estructura.

**Impacto:**  
Difícil depurar en producción. Imposible filtrar o buscar logs por campos específicos (userId, requestId, etc.).

**Prioridad:** MEDIA  
**Complejidad:** BAJA  

**Recomendación:**  
1. Integrar el formatter JSON existente con uvicorn
2. Agregar request_id middleware para trazabilidad
3. Agregar userId a los logs de endpoints autenticados
4. Configurar nivel de log por variable de entorno

---

## TD-006: Tests de Integración

**Descripción:**  
Los tests actuales son unitarios y de componente. No hay tests end-to-end que validen el flujo completo: registro → crear empresa → chat → board room → diagnóstico → gate review.

**Impacto:**  
No se detectan roturas en el flujo completo hasta que un usuario lo prueba manualmente.

**Prioridad:** MEDIA  
**Complejidad:** MEDIA  

**Recomendación:**  
Crear tests de integración que:
1. Ejecuten el flujo completo del Nivel 1
2. Validen transiciones de estado
3. Verifiquen que el Gemelo Digital persiste correctamente
4. Se ejecuten con `pytest` pero contra una BD real (no in-memory)

---

## TD-007: Multi-Stage Docker Builds

**Descripción:**  
Los Dockerfiles actuales son de etapa única. Las imágenes incluyen herramientas de build que no son necesarias en runtime.

**Impacto:**  
Imágenes Docker más grandes de lo necesario. Mayor tiempo de build y pull.

**Prioridad:** BAJA  
**Complejidad:** BAJA  

**Recomendación:**  
Convertir a multi-stage builds:
- Backend: stage de build con pip install, stage final solo con runtime
- Frontend: stage de build con npm run build, stage final con nginx para archivos estáticos (o mantener Vite dev para desarrollo)

---

## TD-008: GPU Support para Ollama

**Descripción:**  
Ollama ejecuta en CPU only. No hay configuración para GPU en docker-compose.yml.

**Impacto:**  
Tiempos de respuesta 5-10x más lentos que con GPU. Board Room toma 23s en CPU vs ~3-5s con GPU.

**Prioridad:** BAJA (depende de infraestructura)  
**Complejidad:** MEDIA  

**Recomendación:**  
1. Agregar profile `gpu` en docker-compose.yml
2. Configurar `deploy.resources.reservations.devices` para NVIDIA
3. Documentar requisitos de GPU (CUDA, driver version)
4. Mantener fallback a CPU cuando GPU no esté disponible

---

## TD-009: Validación de Input

**Descripción:**  
La validación de input es básica (Pydantic schemas). No hay validación de:
- Longitud máxima de mensajes
- Caracteres especiales en campos de texto
- Validación de email más allá del formato
- Sanitización de contenido para XSS

**Impacto:**  
Riesgo de inyección de prompts, mensajes extremadamente largos que consumen recursos, XSS en el frontend.

**Prioridad:** MEDIA  
**Complejidad:** BAJA  

**Recomendación:**  
1. Agregar validación de longitud en schemas Pydantic
2. Sanitizar contenido de chat antes de enviarlo al LLM
3. Usar DOMPurify en el frontend para renders de markdown
4. Agregar validación de email con library dedicada

---

## TD-010: Backup de Base de Datos

**Descripción:**  
No hay estrategia de backup automática para la BD SQLite.

**Impacto:**  
Pérdida total de datos en caso de corrupción del archivo o eliminación accidental.

**Prioridad:** MEDIA  
**Complejidad:** BAJA  

**Recomendación:**  
1. Script de backup que copie `adan.db` a volumen separado
2. Cron job diario via Docker
3. Retención de 7 días
4. Considerar migración a PostgreSQL para production

---

## TD-011: Health Check Frontend

**Descripción:**  
Solo Ollama tiene healthcheck configurado en docker-compose.yml. Frontend y Backend no tienen healthcheck.

**Impacto:**  
Docker no puede detectar si el frontend o backend están caídos. El dependiente puede estar esperando un servicio muerto.

**Prioridad:** BAJA  
**Complejidad:** BAJA  

**Recomendación:**  
1. Backend: agregar healthcheck con curl a `/health`
2. Frontend: agregar healthcheck con curl a `/` o un endpoint dedicado
3. Configurar `depends_on` con `condition: service_healthy`

---

## TD-012: CORS en Producción

**Descripción:**  
CORS está configurado para múltiples orígenes de desarrollo (`localhost:5173`, `localhost:3000`). No hay configuración separada para producción.

**Impacto:**  
En producción, CORS podría estar demasiado abierto o no funcionar correctamente.

**Prioridad:** BAJA  
**Complejidad:** BAJA  

**Recomendación:**  
1. Usar variable de entorno `CORS_ORIGINS` para configurar por ambiente
2. En producción, solo permitir el dominio real
3. Documentar configuración de CORS para deployment

---

## TD-013: Observabilidad

**Descripción:**  
No hay métricas, tracing, ni monitoreo integrado. No se puede saber:
- Cuántas llamadas a LLM se hacen
- Tiempo promedio de respuesta por endpoint
- Tasa de error
- Uso de recursos

**Impacto:**  
Imposible detectar problemas de performance o errores en producción sin logs manuales.

**Prioridad:** BAJA  
**Complejidad:** MEDIA  

**Recomendación:**  
1. Agregar métricas con Prometheus o similar
2. Integrar OpenTelemetry para tracing
3. Dashboard de monitoreo con Grafana
4. Alertas para errores y latencia alta

---

## TD-014: CI/CD Pipeline

**Descripción:**  
No hay pipeline de integración continua ni despliegue automático.

**Impacto:**  
Los tests se ejecutan manualmente. No hay garantía de que el código funcione antes de deploy.

**Prioridad:** BAJA  
**Complejidad:** MEDIA  

**Recomendación:**  
1. GitHub Actions o similar
2. Ejecutar tests en cada PR
3. Build de Docker images
4. Deploy automático a staging
5. Deploy manual a producción

---

## Resumen

| Prioridad | Cantidad | Items |
|---|---|---|
| ALTA | 2 | TD-001, TD-002 |
| MEDIA | 7 | TD-003, TD-004, TD-005, TD-006, TD-009, TD-010, TD-011 |
| BAJA | 5 | TD-007, TD-008, TD-012, TD-013, TD-014 |

**Total:** 14 items de deuda técnica

---

**Este documento está CONGELADO.**  
**Las correcciones deben pasar por una Work Order específica.**  
**No se corregirá nada sin autorización expresa.**
