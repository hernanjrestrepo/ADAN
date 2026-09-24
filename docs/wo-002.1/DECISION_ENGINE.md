# DECISION_ENGINE — Motor de Decisiones de ADÁN

**WO:** WO-002.1  
**Fecha:** 2026-07-24  
**Estado:** Diseño (sin implementar)  
**Prerequisito:** WO-001 cerrada, WO-002 baseline congelado

---

## 1. Visión General

ADÁN toma decisiones constantemente: qué herramienta usar, qué agente invocar, qué información recuperar, cuándo preguntar al usuario. Este documento define cómo se toman esas decisiones.

**Principio:** Toda decisión debe ser justificada, rastreable y, cuando sea apropiada, revisable.

---

## 2. Niveles de Decisión

### 2.1 Jerarquía de Decisiones

```
┌─────────────────────────────────────────────────┐
│  NIVEL 4: DECISIÓN ESTRATÉGICA                   │
│  (Requiere aprobación del usuario)               │
│  Ej: "Cambiar el modelo de negocio"              │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│  NIVEL 3: DECISIÓN TÁCTICA                       │
│  (Requiere revisión del Reviewer)                │
│  Ej: "Invertir $10K en marketing"                │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│  NIVEL 2: DECISIÓN OPERACIONAL                   │
│  (ADÁN decide solo, reporta al usuario)          │
│  Ej: "Usar web_search para encontrar datos"      │
└─────────────────────────────────────────────────┘
                        │
┌─────────────────────────────────────────────────┐
│  NIVEL 1: DECISIÓN AUTÓNOMA                      │
│  (ADÁN decide sin consultar a nadie)             │
│  Ej: "Ordernar resultados por relevancia"        │
└─────────────────────────────────────────────────┘
```

### 2.2 Criterios por Nivel

| Nivel | Impacto | Reversibilidad | Confianza Requerida | Ejemplos |
|---|---|---|---|---|
| Autónoma | Bajo | Alta | > 0.6 | Ordenar datos, formatear respuesta |
| Operacional | Medio | Media | > 0.7 | Seleccionar herramienta, generar documento |
| Táctica | Alto | Baja | > 0.8 | Inversión, cambio de dirección |
| Estratégica | Crítico | Muy baja | > 0.9 | Modelo de negocio, mercado objetivo |

---

## 3. Flujo de Decisión

### 3.1 Diagrama

```
Situación que requiere decisión
       │
       ▼
┌─────────────────┐
│ 1. CLASIFICAR    │  → ¿Qué nivel de decisión es?
│    DECISIÓN      │
└──────────┬──────┘
           │
       ┌───┴───────────────────┐
       │                       │
   Nivel 1-2               Nivel 3-4
   (Autónoma/              (Táctica/
    Operacional)            Estratégica)
       │                       │
       ▼                       ▼
┌─────────────────┐   ┌─────────────────┐
│ 2. RECUPERAR     │   │ 2. RECUPERAR     │
│    CONTEXTO      │   │    CONTEXTO      │
└──────────┬──────┘   └──────────┬──────┘
           │                      │
           ▼                      ▼
┌─────────────────┐   ┌─────────────────┐
│ 3. EVALUAR       │   │ 3. EVALUAR       │
│    OPCIONES      │   │    OPCIONES      │
└──────────┬──────┘   └──────────┬──────┘
           │                      │
           ▼                      ▼
┌─────────────────┐   ┌─────────────────┐
│ 4. SELECCIONAR   │   │ 4. CONSULTAR     │
│    MEJOR OPCIÓN  │   │    REVIEWER      │
└──────────┬──────┘   └──────────┬──────┘
           │                      │
           ▼                      ▼
┌─────────────────┐   ┌─────────────────┐
│ 5. JUSTIFICAR    │   │ 5. JUSTIFICAR    │
│    DECISIÓN      │   │    DECISIÓN      │
└──────────┬──────┘   └──────────┬──────┘
           │                      │
           ▼                      │
┌─────────────────┐               │
│ 6. EJECUTAR      │               │
│                  │               │
└──────────┬──────┘               │
           │                      │
           ▼                      ▼
┌─────────────────┐   ┌─────────────────┐
│ 7. REGISTRAR     │   │ 6. CONSULTAR     │
│    EN EVENTOS    │   │    AL USUARIO    │
└─────────────────┘   └──────────┬──────┘
                                 │
                                 ▼
                          ┌─────────────────┐
                          │ 7. REGISTRAR     │
                          │    EN EVENTOS    │
                          └─────────────────┘
```

### 3.2 Detalle por Paso

#### Paso 1: Clasificar Decisión

```python
class DecisionClassifier:
    def classify(self, situation: str, context: DecisionContext) -> DecisionLevel:
        # 1. Analizar el impacto
        impact = self._assess_impact(situation, context)
        
        # 2. Analizar la reversibilidad
        reversibility = self._assess_reversibility(situation)
        
        # 3. Analizar la confianza disponible
        confidence = self._assess_confidence(situation, context)
        
        # 4. Clasificar
        if impact == "low" and reversibility == "high":
            return DecisionLevel.AUTONOMOUS
        elif impact == "medium" and reversibility == "medium":
            return DecisionLevel.OPERATIONAL
        elif impact == "high" and reversibility == "low":
            return DecisionLevel.TACTICAL
        else:  # impact == "critical" and reversibility == "very_low"
            return DecisionLevel.STRATEGIC
```

**Criterios de clasificación:**

| Factor | Bajo | Medio | Alto | Crítico |
|---|---|---|---|---|
| Impacto financiero | < $100 | $100-$1,000 | $1,000-$10,000 | > $10,000 |
| Impacto en negocio | Sin efecto | Menor | Significativo | Transformador |
| Reversibilidad | Undo inmediato | Undo con esfuerzo | Revertible con coste | Irreversible |
| Conocimiento | Hechos verificados | Inferencia sólida | Inferencia parcial | Especulación |

#### Paso 2: Recuperar Contexto

```python
def recover_context(situation: str, context: DecisionContext) -> DecisionContext:
    # 1. Recuperar del Knowledge Graph
    kg_facts = knowledge_graph.query(situation)
    
    # 2. Recuperar episodios relevantes
    episodes = episodic_memory.search(situation, top_k=5)
    
    # 3. Recuperar decisiones previas similares
    similar_decisions = longterm_memory.search_decisions(situation)
    
    # 4. Recuperar procedimientos aplicables
    procedures = procedural_memory.search(situation)
    
    # 5. Recuperar preferencias del usuario
    preferences = longterm_memory.get_user_preferences()
    
    return DecisionContext(
        facts=kg_facts,
        episodes=episodes,
        similar_decisions=similar_decisions,
        procedures=procedures,
        preferences=preferences
    )
```

#### Paso 3: Evaluar Opciones

```python
def evaluate_options(options: list[Option], context: DecisionContext) -> list[ScoredOption]:
    scored = []
    for option in options:
        score = 0.0
        
        # 1. Alineación con objetivos del proyecto
        goal_alignment = assess_goal_alignment(option, context.goals)
        score += 0.30 * goal_alignment
        
        # 2. Consistencia con hechos conocidos
        fact_consistency = assess_fact_consistency(option, context.facts)
        score += 0.25 * fact_consistency
        
        # 3. Similaridad con decisiones exitosas previas
        precedent_similarity = assess_precedent(option, context.similar_decisions)
        score += 0.20 * precedent_similarity
        
        # 4. Alineación con preferencias del usuario
        preference_alignment = assess_preferences(option, context.preferences)
        score += 0.15 * preference_alignment
        
        # 5. Riesgo estimado
        risk_score = assess_risk(option, context)
        score += 0.10 * (1 - risk_score)
        
        scored.append(ScoredOption(
            option=option,
            score=score,
            justification=build_justification(option, score, context)
        ))
    
    return sorted(scored, key=lambda x: x.score, reverse=True)
```

#### Paso 4: Seleccionar Mejor Opción

```python
def select_best_option(scored_options: list[ScoredOption]) -> Decision:
    best = scored_options[0]
    second = scored_options[1] if len(scored_options) > 1 else None
    
    # Si la mejor opción tiene score muy alto, seleccionar directamente
    if best.score > 0.8:
        return Decision(
            selected=best.option,
            confidence=best.score,
            alternatives=[second.option] if second else [],
            reasoning=best.justification
        )
    
    # Si hay mucha diferencia entre primera y segunda, seleccionar primera
    if second and (best.score - second.score) > 0.2:
        return Decision(
            selected=best.option,
            confidence=best.score,
            alternatives=[second.option],
            reasoning=best.justification
        )
    
    # Si las opciones son cercanas, escalar a nivel superior
    return Decision(
        selected=best.option,
        confidence=best.score,
        alternatives=scored_options[1:3],
        reasoning=best.justification,
        escalate=True,
        escalate_reason="Opciones con scores cercanos, requiere revisión"
    )
```

#### Paso 5: Justificar Decisión

```python
class DecisionJustification:
    decision_id: UUID
    level: DecisionLevel
    selected_option: str
    score: float
    confidence: float
    
    reasoning: str                      # explicación en lenguaje natural
    supporting_facts: list[str]         # hechos que respaldan la decisión
    contradicting_facts: list[str]      # hechos que contradicen (si hay)
    precedent: str | None               # decisión previa similar
    risk_assessment: str                # evaluación de riesgo
    
    alternatives_considered: list[Option]  # otras opciones evaluadas
    why_not_selected: dict[str, str]    # por qué no se seleccionaron
    
    created_by: str                     # agente que tomó la decisión
    reviewed_by: str | None             # agente que revisó (si aplica)
    approved_by: str | None             # usuario que aprobó (si aplica)
```

#### Paso 6: Registrar en Eventos

```python
def record_decision(decision: Decision):
    event_manager.publish(Event(
        type="decision_made",
        payload={
            "decision_id": str(decision.id),
            "level": decision.level.value,
            "selected_option": decision.selected_option,
            "confidence": decision.confidence,
            "reasoning": decision.reasoning,
            "created_by": decision.created_by,
            "timestamp": datetime.now().isoformat()
        }
    ))
```

---

## 4. Cuándo Decide Solo ADÁN

### 4.1 Decisiones Autónomas (Nivel 1)

ADÁN decide sin consultar a nadie cuando:

| Condición | Ejemplo |
|---|---|
| La acción es reversible | Ordenar resultados de búsqueda |
| El impacto es bajo | Formatear una respuesta |
| Hay un procedimiento claro | "Si el usuario pregunta X, hacer Y" |
| La confianza es alta (> 0.9) | Hechos verificados en el knowledge graph |

### 4.2 Decisiones Operacionales (Nivel 2)

ADÁN decide solo pero reporta al usuario:

| Condición | Ejemplo |
|---|---|
| La acción tiene impacto medio | Generar un documento |
| Hay alternativas pero una es claramente mejor | Seleccionar herramienta con score > 0.8 |
| El usuario delegó la decisión | "Tú decides cómo presentarlo" |
| Hay precedente exitoso | "La última vez usamos esta approach" |

---

## 5. Cuándo Consulta Agentes

### 5.1 Board Room (Nivel 3)

El Board Room se invoca cuando:

| Condición | Ejemplo |
|---|---|
| Se necesita análisis multi-perspectiva | Evaluar viabilidad de un mercado |
| Hay desacuerdo entre agentes | CEO dice PROCEED, CTO dice STOP |
| La decisión afecta múltiples áreas | Impacto financiero, técnico y de mercado |
| Se requiere consenso documentado | Decisión que debe ser auditada |

### 5.2 Reviewer (Nivel 3)

El Reviewer se invoca cuando:

| Condición | Ejemplo |
|---|---|
| Inversión > $1,000 | "Invertir $5K en publicidad" |
| Cambio de dirección | "Cambiar de mercado B2B a B2C" |
| Riesgo identificado | "Hay un competidor entrando" |
| Decisión irreversible | "Contratar a alguien" |

### 5.3 Critic (Nivel 2-3)

El Critic se invoca cuando:

| Condición | Ejemplo |
|---|---|
| Se genera una respuesta al usuario | Verificar calidad antes de entregar |
| Hay información no verificada | "¿Es correcto este dato?" |
| Se detecta posible alucinación | El LLM generó un dato falso |
| Se necesita coherencia | "¿Esto es consistente con lo que dijimos antes?" |

---

## 6. Cuándo Consulta al Usuario

### 6.1 Decisiones Estratégicas (Nivel 4)

El usuario se consulta cuando:

| Condición | Ejemplo |
|---|---|
| Impacto > $10,000 | "Invertir $50K en desarrollo" |
| Cambio de modelo de negocio | "De SaaS a consulting" |
| Decisión irreversible | "Cerrar el producto actual" |
| Sin precedente | "Nunca hemos enfrentado algo así" |
| Confianza baja (< 0.5) | "No tengo suficiente información" |
| Conflicto de valores | "¿Priorizamos ganancias o impacto social?" |

### 6.2 Mecanismo de Consulta

```python
class UserConsultation:
    question: str                       # pregunta clara y específica
    context: str                        # contexto para que el usuario entienda
    options: list[UserOption]           # opciones con pros/contras
    recommendation: str | None          # recomendación de ADÁN (si la hay)
    deadline: datetime | None           # cuándo se necesita la respuesta
    
class UserOption:
    label: str                          # "Opción A: Entrar al mercado LATAM"
    description: str                    # descripción detallada
    pros: list[str]                     # ventajas
    cons: list[str]                     # desventajas
    estimated_impact: str               # impacto estimado
    confidence: float                   # confianza de ADÁN en esta opción
```

### 6.3 Ejemplo

```python
consultation = UserConsultation(
    question="¿Deberíamos invertir en publicidad digital o en content marketing?",
    context="Tenemos $5,000 disponibles para marketing este trimestre. Basado en nuestro análisis, el mercado de SaaS en LATAM está creciendo pero la competencia es alta.",
    options=[
        UserOption(
            label="Publicidad digital (Google Ads, Meta)",
            description="Campañas pagadas en plataformas de publicidad",
            pros=["Resultados rápidos", "Targeting preciso", "Escalable"],
            cons=["Costo recurrente", "Dependencia de plataformas", "Ad fatigue"],
            estimated_impact="30-50 leads/mes",
            confidence=0.7
        ),
        UserOption(
            label="Content Marketing (blog, SEO, LinkedIn)",
            description="Crear contenido orgánico y optimizado para búsqueda",
            pros=["Costo bajo a largo plazo", "Autoridad de marca", "Tráfico orgánico"],
            cons=["Resultados lentos (3-6 meses)", "Requiere consistencia", "Competencia alta"],
            estimated_impact="10-20 leads/mes en 6 meses",
            confidence=0.6
        )
    ],
    recommendation="Recomiendo content marketing porque se alinea con nuestro presupuesto limitado y genera tráfico sostenible. La publicidad digital puede complementarse después.",
    deadline=datetime.now() + timedelta(days=3)
)
```

---

## 7. Cómo Justifica una Decisión

### 7.1 Estructura de Justificación

Toda decisión debe incluir:

1. **Qué se decidió:** Acción seleccionada
2. **Por qué:** Razón principal
3. **Basado en:** Hechos y evidencia
4. **Alternativas consideradas:** Qué más se evaluó
5. **Por qué no las otras:** Razón de descarte
6. **Riesgos:** Qué puede salir mal
7. **Confianza:** Qué tan seguro está ADÁN

### 7.2 Ejemplo de Justificación

```
DECISIÓN: Generar diagnóstico de mercado para la empresa X

¿QUÉ SE DECIDIÓ?
Generar un documento de diagnóstico de mercado usando el Board Room (4 agentes) + LLM.

¿POR QUÉ?
El usuario solicitó "analizar mi mercado". El plan requiere:
1. Recuperar contexto del mercado (Memory Manager)
2. Ejecutar Board Room para análisis multi-perspectiva
3. Generar documento consolidado

BASADO EN:
- Hecho: La empresa opera en el mercado de SaaS para PYMEs en LATAM
- Hecho: El mercado tiene CAGR del 15% (fuente: análisis previo)
- Episodio: En la sesión del 2026-07-20, el usuario confirmó que su target son PYMEs de 10-50 empleados

ALTERNATIVAS CONSIDERADAS:
1. Generar diagnóstico solo con LLM (sin Board Room) → Descartado: análisis de una sola perspectiva
2. Usar solo datos del knowledge graph (sin LLM) → Descartado: información insuficiente
3. Consultar fuentes externas (web search) → Considerado como paso adicional

POR QUÉ NO LAS OTRAS:
- Opción 1: Un solo agente no cubre todas las perspectivas (financiera, técnica, de mercado, de valor)
- Opción 2: El knowledge graph tiene información limitada, se necesita análisis cualitativo

RIESGOS:
- El Board Room puede dar resultados genéricos si el contexto es pobre
- Mitigación: Se recuperará contexto detallado antes de invocar el Board Room

CONFIANZA: 0.82 (alta — basado en información verificada + precedente exitoso)
```

---

## 8. Cómo Mide Confianza

### 8.1 Fuentes de Confianza

| Fuente | Peso | Descripción |
|---|---|---|
| Hechos verificados | 0.30 | Información confirmada en el knowledge graph |
| Episodios previos | 0.25 | Experiencia pasada con situaciones similares |
| Consenso de agentes | 0.20 | Si todos los agentes coinciden, más confianza |
| Calidad de información | 0.15 | Qué tan completa y reciente es la información |
| Precedente | 0.10 | Si se ha hecho algo similar antes con éxito |

### 8.2 Cálculo de Confianza

```python
def calculate_confidence(decision: Decision, context: DecisionContext) -> float:
    # 1. Hechos verificados
    verified_facts = len([f for f in context.facts if f.verified])
    total_facts = len(context.facts)
    fact_confidence = verified_facts / max(total_facts, 1)
    
    # 2. Episodios previos
    relevant_episodes = len([e for e in context.episodes if e.relevance_score > 0.5])
    episode_confidence = min(relevant_episodes / 3, 1.0)  # saturar en 3 episodios
    
    # 3. Consenso de agentes (si aplica)
    if decision.agent_votes:
        consensus = calculate_consensus(decision.agent_votes)
        agent_confidence = consensus.score / 100
    else:
        agent_confidence = 0.5  # default sin agentes
    
    # 4. Calidad de información
    info_quality = assess_information_quality(context)
    
    # 5. Precedente
    precedent_score = assess_precedent(decision, context.similar_decisions)
    
    # Score ponderado
    confidence = (
        0.30 * fact_confidence +
        0.25 * episode_confidence +
        0.20 * agent_confidence +
        0.15 * info_quality +
        0.10 * precedent_score
    )
    
    return round(confidence, 2)
```

### 8.3 Niveles de Confianza

| Nivel | Score | Acción |
|---|---|---|
| Muy alta | > 0.9 | Ejecutar directamente |
| Alta | 0.7 - 0.9 | Ejecutar y reportar |
| Media | 0.5 - 0.7 | Ejecutar con monitoreo |
| Baja | 0.3 - 0.5 | Escalar a nivel superior |
| Muy baja | < 0.3 | No ejecutar, solicitar más información |

---

## 9. Cómo Aprende

### 9.1 Ciclo de Aprendizaje

```
Decisión tomada
       │
       ▼
┌─────────────────┐
│ 1. EJECUTAR      │  → La decisión se ejecuta
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 2. OBSERVAR      │  → Se observa el resultado
│    RESULTADO     │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 3. EVALUAR       │  → ¿Fue buena la decisión?
│    CALIDAD       │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 4. ACTUALIZAR    │  → Actualizar memoria y procedimientos
│    MEMORIA       │
└──────────┬──────┘
           │
           ▼
┌─────────────────┐
│ 5. EXTRAER       │  → ¿Qué aprendimos?
│    LECCIÓN       │
└─────────────────┘
```

### 9.2 Evaluación de Calidad

```python
def evaluate_decision_quality(decision: Decision, outcome: DecisionOutcome) -> float:
    # 1. ¿Se logró el objetivo?
    goal_achieved = outcome.goal_achieved  # bool
    
    # 2. ¿El costo fue el esperado?
    cost_accuracy = 1.0 - abs(outcome.actual_cost - decision.estimated_cost) / max(decision.estimated_cost, 1)
    
    # 3. ¿El tiempo fue el esperado?
    time_accuracy = 1.0 - abs(outcome.actual_time - decision.estimated_time) / max(decision.estimated_time, 1)
    
    # 4. ¿Hubo efectos secundarios?
    side_effects = 1.0 - len(outcome.side_effects) * 0.1
    
    # 5. ¿El usuario está satisfecho?
    user_satisfaction = outcome.user_satisfaction  # -1 a +1
    
    # Score ponderado
    quality = (
        0.35 * goal_achieved +
        0.20 * cost_accuracy +
        0.15 * time_accuracy +
        0.15 * side_effects +
        0.15 * (user_satisfaction + 1) / 2  # normalizar a 0-1
    )
    
    return round(quality, 2)
```

### 9.3 Actualización de Memoria

```python
def learn_from_decision(decision: Decision, outcome: DecisionOutcome, quality: float):
    # 1. Actualizar episodio
    episode = EpisodicMemory(
        summary=f"Decisión: {decision.selected_option}",
        context=decision.reasoning,
        outcome=outcome.summary,
        emotional_valence=quality - 0.5,  # positivo si quality > 0.5
        relevance_score=quality  # decisiones de alta calidad son más relevantes
    )
    episodic_memory.store(episode)
    
    # 2. Actualizar procedimiento (si aplica)
    if quality > 0.7:
        # Decisión exitosa → incrementar confianza del procedimiento
        procedure = procedural_memory.find_by_trigger(decision.situation)
        if procedure:
            procedure.success_count += 1
        else:
            # Crear nuevo procedimiento
            procedural_memory.create(
                trigger=decision.situation,
                steps=decision.reasoning_steps,
                confidence=0.5
            )
    elif quality < 0.3:
        # Decisión fallida → decrementar confianza
        procedure = procedural_memory.find_by_trigger(decision.situation)
        if procedure:
            procedure.failure_count += 1
    
    # 3. Extraer lección
    if quality > 0.8 or quality < 0.2:
        lesson = Lesson(
            situation=decision.situation,
            decision=decision.selected_option,
            outcome=outcome.summary,
            quality=quality,
            insight=generate_insight(decision, outcome, quality)
        )
        longterm_memory.add_lesson(lesson)
```

---

## 10. Resumen de Reglas

| Pregunta | Respuesta |
|---|---|
| ¿Cuándo decide solo ADÁN? | Cuando el impacto es bajo y la reversibilidad es alta |
| ¿Cuándo consulta agentes? | Cuando se necesita análisis multi-perspectiva o consenso |
| ¿Cuándo consulta al usuario? | Cuando el impacto es alto, la reversibilidad es baja, o la confianza es baja |
| ¿Cómo justifica? | Con hechos, episodios, alternativas evaluadas y riesgos |
| ¿Cómo mide confianza? | Con score ponderado de fuentes de información |
| ¿Cómo aprende? | Observando resultados, evaluando calidad, actualizando memoria |

---

**Este diseño está CONGELADO.**  
**Las implementaciones futuras deben adherirse a esta especificación.**  
**Los cambios de diseño requieren Work Order específica.**
