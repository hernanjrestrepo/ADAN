"""Dominios: si están libres (RDAP, el protocolo oficial de los registros, gratis y sin cuenta), precios de
referencia y enlaces para comprar en el registrador que el cliente elija. ADAN no compra ni cobra dominios.
"""
from __future__ import annotations

import asyncio
import re
import unicodedata

import httpx

RDAP = "https://rdap.org/domain/{}"
DNS = "https://dns.google/resolve"
TIMEOUT_S = 8.0

# Primer año en USD, precios públicos de referencia (octubre de 2026). Cambian con frecuencia y con las
# promociones: siempre se confirma en el registrador antes de comprar.
TLDS = {
    ".com": {"usd": (10, 22), "nota": "La más reconocida en el mundo"},
    ".co": {"usd": (12, 35), "nota": "Colombia y startups; corta y conocida"},
    ".com.co": {"usd": (12, 30), "nota": "Señal clara de empresa colombiana"},
    ".net": {"usd": (12, 20), "nota": "Alternativa clásica a .com"},
    ".app": {"usd": (14, 22), "nota": "Para aplicaciones; exige HTTPS"},
    ".io": {"usd": (35, 60), "nota": "Popular en tecnología"},
    ".ai": {"usd": (70, 160), "nota": "Inteligencia artificial; suele venderse por 2 años"},
    ".shop": {"usd": (3, 35), "nota": "Comercio en línea"},
}

REGISTRARS = [
    {"name": "Cloudflare Registrar", "url": "https://domains.cloudflare.com/?domain={domain}",
     "nota": "Precio de costo, sin margen; no vende todas las extensiones (por ejemplo .com.co)."},
    {"name": "Namecheap", "url": "https://www.namecheap.com/domains/registration/results/?domain={domain}",
     "nota": "Precios bajos y privacidad WHOIS gratis."},
    {"name": "GoDaddy", "url": "https://www.godaddy.com/domainsearch/find?domainToCheck={domain}",
     "nota": "Muy conocido; revisa el precio de renovación, suele subir."},
    {"name": "Porkbun", "url": "https://porkbun.com/checkout/search?q={domain}",
     "nota": "Precios bajos y renovaciones estables."},
]


def slugify(name: str) -> str:
    """Nombre → etiqueta de dominio: sin tildes, en minúscula, solo letras, números y guiones."""
    plain = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode().lower()
    slug = re.sub(r"[^a-z0-9]+", "", plain.replace("&", "y"))
    return slug[:63]


async def _status(client: httpx.AsyncClient, domain: str) -> str:
    try:
        r = await client.get(RDAP.format(domain))
    except httpx.HTTPError:
        return "sin_confirmar"
    if r.status_code == 404:
        # Solo es "libre" si lo dice el registro de la extensión (tras la redirección de rdap.org). Un 404 del
        # propio rdap.org significa que esa extensión no tiene RDAP conocido (pasa con .co y .com.co).
        return "disponible" if r.url.host != "rdap.org" else "sin_confirmar"
    if r.status_code == 200:
        return "registrado"
    return "sin_confirmar"


async def _dns_hint(client: httpx.AsyncClient, domain: str) -> str:
    """Para extensiones sin RDAP: si el dominio tiene servidores de nombres está ocupado; si el DNS dice que no
    existe (NXDOMAIN), probablemente está libre (no es confirmación: un dominio puede estar registrado sin DNS)."""
    try:
        r = await client.get(DNS, params={"name": domain, "type": "NS"})
        data = r.json()
    except (httpx.HTTPError, ValueError):
        return "sin_confirmar"
    if data.get("Answer"):
        return "registrado"
    return "probable_libre" if data.get("Status") == 3 else "sin_confirmar"


async def _resolve(client: httpx.AsyncClient, domain: str) -> str:
    status = await _status(client, domain)
    return await _dns_hint(client, domain) if status == "sin_confirmar" else status


async def check(name: str, client: httpx.AsyncClient | None = None) -> dict:
    slug = slugify(name)
    if len(slug) < 2:
        return {"slug": slug, "domains": [], "registrars": []}
    own = client is None
    client = client or httpx.AsyncClient(timeout=TIMEOUT_S, follow_redirects=True,
                                         headers={"Accept": "application/rdap+json"})
    try:
        statuses = await asyncio.gather(*[_resolve(client, slug + tld) for tld in TLDS])
    finally:
        if own:
            await client.aclose()
    domains = [{"domain": slug + tld, "tld": tld, "status": st, "usd_min": info["usd"][0], "usd_max": info["usd"][1],
                "nota": info["nota"]} for (tld, info), st in zip(TLDS.items(), statuses)]
    first = next((d["domain"] for d in domains if d["status"] in ("disponible", "probable_libre")), slug + ".com")
    registrars = [{**r, "url": r["url"].format(domain=first)} for r in REGISTRARS]
    return {"slug": slug, "domains": domains, "registrars": registrars,
            "prices_note": "Precios de referencia del primer año en USD (octubre de 2026). Confírmalos en el registrador: "
                           "cambian con promociones y la renovación suele costar más."}
