"""
Knowledge Quality Engine — Evalúa calidad del conocimiento antes de ingresar a EMS.

Genera un Knowledge Score entre 0-100.
"""

from dataclasses import dataclass, field


@dataclass
class QualityDimension:
    """Dimensión de calidad."""
    name: str
    score: float                         # 0-1
    weight: float
    details: str = ""


@dataclass
class KnowledgeQualityReport:
    """Reporte de calidad del conocimiento."""
    overall_score: float                 # 0-100
    dimensions: list[QualityDimension] = field(default_factory=list)
    passed: bool = False
    issues: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class KnowledgeQualityEngine:
    """
    Evalúa la calidad de la información antes de ingresar a EMS.
    
    Métricas:
    - Source Authority: credibilidad de la fuente
    - Freshness: actualidad de la información
    - Redundancy: duplicados con conocimiento existente
    - Contradictions: contradicciones con conocimiento existente
    - Confidence: confianza general
    - Completeness: completitud de la información
    """

    def __init__(self):
        # Fuentes de alta autoridad
        self._trusted_sources = [
            "wikipedia.org", "gov.co", "banrep.gov.co",
            "dane.gov.co", "procolombia.co",
        ]

    def evaluate(
        self,
        content: str,
        source_url: str = "",
        existing_knowledge: str = "",
        metadata: dict | None = None,
    ) -> KnowledgeQualityReport:
        """Evalúa la calidad del conocimiento."""
        dimensions = []

        # 1. Source Authority (20%)
        authority = self._assess_authority(source_url)
        dimensions.append(QualityDimension(
            name="source_authority",
            score=authority,
            weight=0.20,
            details=f"Fuente: {source_url or 'desconocida'}",
        ))

        # 2. Freshness (15%)
        freshness = self._assess_freshness(metadata or {})
        dimensions.append(QualityDimension(
            name="freshness",
            score=freshness,
            weight=0.15,
            details="Basado en timestamp de adquisición",
        ))

        # 3. Redundancy (15%)
        redundancy = self._assess_redundancy(content, existing_knowledge)
        dimensions.append(QualityDimension(
            name="redundancy",
            score=redundancy,
            weight=0.15,
            details="Duplicados con conocimiento existente",
        ))

        # 4. Contradictions (15%)
        contradictions = self._assess_contradictions(content, existing_knowledge)
        dimensions.append(QualityDimension(
            name="contradictions",
            score=contradictions,
            weight=0.15,
            details="Contradiciones con conocimiento existente",
        ))

        # 5. Confidence (15%)
        confidence = self._assess_confidence(content, metadata or {})
        dimensions.append(QualityDimension(
            name="confidence",
            score=confidence,
            weight=0.15,
            details="Confianza basada en consistencia interna",
        ))

        # 6. Completeness (20%)
        completeness = self._assess_completeness(content)
        dimensions.append(QualityDimension(
            name="completeness",
            score=completeness,
            weight=0.20,
            details="Completitud de la información",
        ))

        # Calcular score general
        overall = sum(d.score * d.weight for d in dimensions) * 100

        # Detectar issues
        issues = []
        recommendations = []
        if authority < 0.5:
            issues.append("Fuente de baja autoridad")
            recommendations.append("Verificar información con fuente adicional")
        if redundancy > 0.7:
            issues.append("Alta redundancia con conocimiento existente")
            recommendations.append("Considerar si el contenido agrega valor nuevo")
        if contradictions < 0.5:
            issues.append("Posibles contradicciones detectadas")
            recommendations.append("Revisar contradicciones antes de almacenar")
        if completeness < 0.3:
            issues.append("Información incompleta")
            recommendations.append("Completar con fuentes adicionales")

        return KnowledgeQualityReport(
            overall_score=round(overall, 1),
            dimensions=dimensions,
            passed=overall >= 40,
            issues=issues,
            recommendations=recommendations,
        )

    def _assess_authority(self, url: str) -> float:
        """Evalúa autoridad de la fuente."""
        if not url:
            return 0.3
        url_lower = url.lower()
        for source in self._trusted_sources:
            if source in url_lower:
                return 0.9
        if ".gov" in url_lower or ".edu" in url_lower:
            return 0.8
        if ".org" in url_lower:
            return 0.6
        return 0.5

    def _assess_freshness(self, metadata: dict) -> float:
        """Evalúa actualidad de la información."""
        # Por defecto, contenido reciente tiene alta frescura
        return 0.8

    def _assess_redundancy(self, content: str, existing: str) -> float:
        """Evalúa redundancia (0=nuevo, 1=completamente duplicado)."""
        if not existing:
            return 0.0
        # Comparación simple por palabras clave
        content_words = set(content.lower().split())
        existing_words = set(existing.lower().split())
        if not content_words:
            return 0.0
        overlap = len(content_words & existing_words) / len(content_words)
        return min(overlap, 1.0)

    def _assess_contradictions(self, content: str, existing: str) -> float:
        """Evalúa contradicciones (0=contradictorio, 1=sin contradicciones)."""
        if not existing:
            return 1.0
        # Detección simple de contradicciones
        contradictory_pairs = [
            ("aumentó", "disminuyó"), ("creció", "cayó"),
            ("aprobó", "rechazó"), ("sí", "no"),
            ("verdadero", "falso"), ("positivo", "negativo"),
        ]
        content_lower = content.lower()
        existing_lower = existing.lower()
        for word1, word2 in contradictory_pairs:
            if (word1 in content_lower and word2 in existing_lower) or \
               (word2 in content_lower and word1 in existing_lower):
                return 0.3
        return 0.9

    def _assess_confidence(self, content: str, metadata: dict) -> float:
        """Evalúa confianza general."""
        score = 0.5
        if len(content) > 200:
            score += 0.2
        if metadata.get("engine") in ["scrapegraph", "firecrawl"]:
            score += 0.1
        if metadata.get("quality_score", 0) > 0.7:
            score += 0.1
        return min(score, 1.0)

    def _assess_completeness(self, content: str) -> float:
        """Evalúa completitud."""
        score = 0.3
        words = len(content.split())
        if words > 50:
            score += 0.2
        if words > 200:
            score += 0.2
        if words > 500:
            score += 0.1
        # Estructura
        if any(c in content for c in ["1.", "2.", "-", "•"]):
            score += 0.1
        return min(score, 1.0)
