"""Los 7 Niveles de ADÁN como guiones de trabajo en la Sala. Metodología híbrida acordada con Hernán (2026-10-25):
Customer Development (Steve Blank y Bob Dorf), The Lean Startup (Eric Ries), Running Lean (Ash Maurya), The Mom Test
(Rob Fitzpatrick), Value Proposition Design y Business Model Generation (Osterwalder y Pigneur), Testing Business
Ideas (Bland y Osterwalder), Disciplined Entrepreneurship (Bill Aulet), Lean Analytics (Croll y Yoskovitz), métricas
AARRR (Dave McClure), Traction (Weinberg y Mares) y Scaling Up (Verne Harnish).

Cada Nivel tiene un objetivo, temas que hay que lograr, entregables, indicadores y el equipo que acompaña. El Board
entra desde el Nivel 3 y La Arena en el 5. Siempre se valida antes de construir (encuesta simulada).
"""
from __future__ import annotations

from app.nivel1.discovery import LEVEL1, Script

LEVEL2 = Script(
    number=2, name="Propuesta de Valor", goal="diseñar una solución que alivie ese dolor mejor que las alternativas",
    topics=(
        ("trabajos", "Trabajos, dolores y ganancias", "el lado del cliente del Lienzo de Propuesta de Valor: qué intenta lograr, qué le duele y qué ganaría"),
        ("solucion", "La solución", "qué hace la solución y cómo alivia cada dolor importante (no funciones sueltas)"),
        ("propuesta", "Propuesta única de valor", "la promesa en una frase clara que un cliente entendería en 5 segundos"),
        ("diferencia", "Frente a las alternativas", "por qué es mejor que lo que el cliente usa hoy y que la competencia"),
        ("precio", "Hipótesis de precio", "cómo y cuánto se cobra (o se gana por comisión), con la lógica detrás"),
        ("adopcion", "Primeros clientes", "quiénes serán los primeros en adoptarla y cómo llegamos a ellos"),
        ("validacion", "Validación de la solución", "encuesta simulada de la solución: cuántos la usarían o comprarían y qué objeciones hay"),
    ),
    method=("Value Proposition Design y Running Lean: encaje problema-solución. Se diseña la solución a partir del "
            "dolor del Nivel 1 y se arma el Lean Canvas. Sin temas legales ni financieros profundos todavía."),
    deliverables=("Lienzo de Propuesta de Valor", "Lean Canvas", "Propuesta única de valor", "Hipótesis de precio"),
    kpis=("% que la usaría o compraría (encuesta simulada)", "Objeciones principales", "Compromisos de primeros clientes"),
    team=("producto", "cmo", "ceo"), dimension="solution",
)

LEVEL3 = Script(
    number=3, name="Modelo de Negocio y Números", goal="que el negocio funcione en el papel: cómo gana dinero y si los números cierran",
    topics=(
        ("ingresos", "Modelo de ingresos", "de dónde sale el dinero y quién paga (Business Model Canvas)"),
        ("mercado", "Tamaño del mercado", "TAM, SAM y SOM calculados de abajo hacia arriba, con fuentes"),
        ("costos", "Estructura de costos", "costos fijos y variables principales"),
        ("unitarios", "Economía unitaria", "precio, margen bruto, CAC estimado, LTV, LTV/CAC y meses para recuperar el CAC"),
        ("caja", "Flujo de caja y equilibrio", "flujo de caja a 24 meses, punto de equilibrio y capital necesario (herramienta Finanzas)"),
        ("organizacion", "Organización híbrida", "organigrama con personas, agentes de IA y servicios de Paradixe (EVA, BPO) que bajan costos, riesgo y CAC"),
        ("legal", "Ruta legal básica", "nombre, país, figura societaria y pasos legales (herramienta Constitución)"),
    ),
    method=("Business Model Generation y Disciplined Entrepreneurship (TAM de abajo hacia arriba, LTV y costo de "
            "adquirir un cliente). Los números se contrastan con referencias del sector; nada se inventa. Al final, "
            "primera sesión del Board."),
    deliverables=("Business Model Canvas", "TAM, SAM y SOM", "Economía unitaria", "Flujo de caja a 24 meses",
                  "Organigrama híbrido con IA y Paradixe", "Ruta legal"),
    kpis=("Margen bruto", "CAC estimado", "LTV", "LTV/CAC (referencia ≥ 3)", "Meses para recuperar el CAC", "Punto de equilibrio"),
    team=("cfo", "legal", "operaciones", "ceo"), dimension="business", board=True,
)

LEVEL4 = Script(
    number=4, name="MVP", goal="construir la versión mínima que entregue el valor y permita aprender",
    topics=(
        ("hipotesis", "Qué aprenderemos", "la hipótesis más riesgosa que el MVP debe probar"),
        ("alcance", "Alcance mínimo", "las 3 a 5 funciones esenciales; todo lo demás queda fuera"),
        ("tipo", "Tipo de MVP", "landing, concierge, prototipo o producto funcional, y por qué"),
        ("medicion", "Medición", "qué se mide desde el primer día (activación, uso, conversión)"),
        ("construccion", "Plan de construcción", "quién lo construye (Genexis o equipo), tiempo y cotización según el trabajo real"),
        ("riesgos", "Riesgos técnicos", "lo que puede fallar y cómo se mitiga"),
        ("exito", "Criterio de éxito", "qué resultado diría que el MVP funcionó"),
    ),
    method=("The Lean Startup (Construir → Medir → Aprender) y Running Lean: el MVP más pequeño que pruebe el "
            "supuesto más riesgoso. El desarrollo listo se cotiza aparte según el trabajo real."),
    deliverables=("Alcance del MVP", "MVP o landing", "Plan de medición", "Cotización del desarrollo"),
    kpis=("Activación", "Tiempo hasta el primer valor", "Costo del MVP"),
    team=("cto", "producto", "ceo"), dimension="product", board=True,
)

LEVEL5 = Script(
    number=5, name="Validación", goal="conseguir evidencia de que el mercado lo quiere y está dispuesto a pagar",
    topics=(
        ("embudo", "Embudo AARRR", "adquisición, activación, retención, referidos e ingresos, con su conversión"),
        ("clientes", "Primeros clientes", "quiénes compraron o usaron y qué dijeron"),
        ("cac", "CAC real", "costo de adquirir un cliente medido con una campaña pequeña (EVA puede bajarlo)"),
        ("retencion", "Retención", "cuántos vuelven o siguen usando"),
        ("encaje", "Encaje producto-mercado", "prueba de Sean Ellis (referencia: 40 % muy decepcionado si desaparece) o señal equivalente"),
        ("aprendizajes", "Pivotar o perseverar", "qué se aprendió y qué se ajusta"),
        ("pitch", "El caso para invertir", "la historia con datos para La Arena"),
    ),
    method=("Lean Analytics y métricas AARRR: la métrica que importa en esta etapa. Se mide con datos reales o, "
            "mientras llegan, con el Simulador de Mercado (marcado como simulado). Board y La Arena."),
    deliverables=("Embudo AARRR medido", "CAC real", "Primeros clientes", "Decisión de pivotar o perseverar", "Pitch"),
    kpis=("Conversión por etapa", "CAC medido", "Retención", "Prueba de Sean Ellis"),
    team=("cmo", "eva", "ceo"), dimension="market", board=True, arena=True,
)

LEVEL6 = Script(
    number=6, name="Lanzamiento y Tracción", goal="crecer con los canales que funcionan",
    topics=(
        ("canales", "Canales (Bullseye)", "los canales con más potencial, probados en pequeño, y el elegido"),
        ("lanzamiento", "Plan de lanzamiento", "qué, cuándo, a quién y con qué mensaje"),
        ("precios", "Precios finales", "precio y paquetes definitivos según lo validado"),
        ("referidos", "Referidos y comunidad", "cómo los clientes traen más clientes"),
        ("operacion", "Operación y entrega", "que se pueda entregar lo que se vende, con calidad"),
        ("metas", "Metas de crecimiento", "metas mensuales de clientes, ingresos y CAC por canal"),
        ("soporte", "Servicio al cliente", "cómo se atiende y se retiene (EVA y el BPO de Paradixe pueden operarlo)"),
    ),
    method="Traction (Bullseye) y Lean Analytics: probar canales en pequeño y escalar el que funcione.",
    deliverables=("Plan Bullseye de canales", "Plan de lanzamiento", "Precios finales", "Mecánica de referidos"),
    kpis=("CAC por canal", "Crecimiento mensual", "Abandono (churn)", "Tasa de referidos", "NPS"),
    team=("cmo", "eva", "operaciones", "ceo"), dimension="market",
)

LEVEL7 = Script(
    number=7, name="Escalamiento", goal="crecer sin romperse",
    topics=(
        ("organizacion", "Organización", "estructura, roles clave y cultura para el siguiente tamaño"),
        ("procesos", "Procesos", "los procesos que deben funcionar sin el fundador"),
        ("automatizacion", "IA y automatización", "qué se automatiza con agentes de IA y servicios de Paradixe para escalar con menos costo"),
        ("capital", "Plan de capital", "cuánto capital, de dónde y para qué"),
        ("indicadores", "Indicadores de gestión", "margen a escala, quema de caja frente a crecimiento, recuperación del CAC"),
        ("riesgos", "Riesgos del crecimiento", "lo que puede romperse al crecer y cómo prevenirlo"),
        ("expansion", "Expansión", "nuevos mercados, segmentos o productos"),
    ),
    method="Scaling Up (gente, estrategia, ejecución y caja). Al final, sesión del Board.",
    deliverables=("Organigrama a escala", "Procesos clave", "Plan de capital", "Tablero de indicadores"),
    kpis=("Margen a escala", "Quema de caja frente a crecimiento", "Recuperación del CAC"),
    team=("operaciones", "cfo", "ceo"), dimension=None, board=True,
)

SCRIPTS = {s.number: s for s in (LEVEL1, LEVEL2, LEVEL3, LEVEL4, LEVEL5, LEVEL6, LEVEL7)}


def script_for(number: int) -> Script:
    return SCRIPTS.get(number, LEVEL1)
