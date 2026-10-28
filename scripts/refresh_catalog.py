#!/usr/bin/env python3
"""Actualiza los precios de los modelos de OpenRouter en backend/app/ai/catalog.json.

    OPENROUTER_API_KEY=sk-or-... python scripts/refresh_catalog.py

Solo toca el precio (y la fecha) de los modelos que ya están en el catálogo; la calidad asignada no cambia.
Avisa de los modelos que dejaron de existir y de los precios que se movieron más de un 20 %.
"""
import json
import os
import sys
import urllib.request
from datetime import date
from pathlib import Path

CATALOG = Path(__file__).resolve().parent.parent / "backend" / "app" / "ai" / "catalog.json"


def main() -> int:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    req = urllib.request.Request("https://openrouter.ai/api/v1/models", headers={"Authorization": f"Bearer {key}"})
    live = {m["id"]: m["pricing"] for m in json.load(urllib.request.urlopen(req, timeout=60))["data"]}
    data = json.loads(CATALOG.read_text())
    changed = 0
    for m in data["models"]:
        if m["provider"] != "openrouter":
            continue
        pricing = live.get(m["model"])
        if pricing is None:
            print(f"⚠ {m['id']}: ya no está en OpenRouter")
            continue
        new = {"input_per_m": float(pricing["prompt"]) * 1e6, "output_per_m": float(pricing["completion"]) * 1e6}
        if m["modality"] == "image":
            new = {"input_per_m": 0.0, "output_per_m": 0.0, "image_output_per_m": float(pricing["image_output"]) * 1e6}
        for field, value in new.items():
            old = m.get(field, 0.0)
            if old and abs(value - old) / old > 0.2:
                print(f"⚠ {m['id']}: {field} {old:g} → {value:g}")
            if round(value, 4) != round(old, 4):
                changed += 1
            m[field] = round(value, 4)
    data["as_of"] = date.today().isoformat()
    CATALOG.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n")
    print(f"Catálogo al {data['as_of']}: {changed} precios cambiaron")
    return 0


if __name__ == "__main__":
    sys.exit(main())
