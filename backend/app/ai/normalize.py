"""LLM Response Normalization Layer.

ALL LLM responses MUST pass through this layer before any component uses them.
Guarantees a single data contract for the entire application.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


def normalize_string(value: Any, default: str = "") -> str:
    """Convert any value to string. Handles None, dict, list, int, float."""
    if value is None:
        return default
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    if isinstance(value, dict):
        # Extract a meaningful string from dict
        if "description" in value:
            return str(value["description"])
        if "text" in value:
            return str(value["text"])
        if "content" in value:
            return str(value["content"])
        return str(value)
    if isinstance(value, list):
        # Join list items, normalizing each
        return ", ".join(normalize_string(item) for item in value if item is not None)
    return str(value)


def normalize_list(value: Any, default: list | None = None) -> list:
    """Convert any value to a list of strings. Handles None, string, dict, list."""
    if default is None:
        default = []
    if value is None:
        return default
    if isinstance(value, str):
        return [value] if value else default
    if isinstance(value, dict):
        # Extract meaningful list from dict
        if "items" in value:
            return normalize_list(value["items"], default)
        if "values" in value:
            return normalize_list(value["values"], default)
        return [normalize_string(value)] if value else default
    if isinstance(value, list):
        result = []
        for item in value:
            if item is None:
                continue
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict):
                result.append(normalize_string(item))
            elif isinstance(item, (int, float, bool)):
                result.append(str(item))
            else:
                result.append(str(item))
        return result if result else default
    return [str(value)]


def normalize_vote(value: Any, default: str = "ABSTAIN") -> str:
    """Normalize vote to one of: PROCEED, PIVOT, STOP; anything else is ABSTAIN (not counted)."""
    if value is None:
        return default
    if isinstance(value, str):
        v = value.upper().strip()
        if v in ("PROCEED", "PIVOT", "STOP"):
            return v
        return default
    if isinstance(value, dict):
        # Extract vote from dict
        if "vote" in value:
            return normalize_vote(value["vote"], default)
        if "decision" in value:
            return normalize_vote(value["decision"], default)
        return default
    return default


def normalize_confidence(value: Any, default: float = 50.0) -> float:
    """Normalize confidence to a float 0-100."""
    if value is None:
        return default
    if isinstance(value, (int, float)):
        return max(0.0, min(100.0, float(value)))
    if isinstance(value, str):
        try:
            return max(0.0, min(100.0, float(value)))
        except ValueError:
            return default
    if isinstance(value, dict):
        # Extract confidence from dict
        if "confidence" in value:
            return normalize_confidence(value["confidence"], default)
        if "score" in value:
            return normalize_confidence(value["score"], default)
        if "value" in value:
            return normalize_confidence(value["value"], default)
        return default
    return default


def normalize_analysis_response(raw: dict) -> dict:
    """Normalize a complete analysis response from LLM.

    Guarantees the output contract:
    {
        "analysis": str,
        "justification": str,
        "vote": "PROCEED" | "PIVOT" | "STOP" | "ABSTAIN",
        "confidence": float (0-100),
        "key_strengths": list[str],
        "key_concerns": list[str],
        "questions": list[str]
    }
    """
    if raw is None:
        raw = {}

    return {
        "analysis": normalize_string(raw.get("analysis", ""), "Sin análisis"),
        "justification": normalize_string(raw.get("justification", ""), "Sin justificación"),
        "vote": normalize_vote(raw.get("vote")),
        "confidence": normalize_confidence(raw.get("confidence")),
        "key_strengths": normalize_list(raw.get("key_strengths")),
        "key_concerns": normalize_list(raw.get("key_concerns")),
        "questions": normalize_list(raw.get("questions")),
    }
