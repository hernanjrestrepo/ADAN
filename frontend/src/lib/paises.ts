// Nombre en español de un país por su código ISO (el que pone Cloudflare en cada visita)
const COUNTRY_NAMES = new Intl.DisplayNames(['es'], { type: 'region' })

export function countryName(iso: string): string {
  try {
    return COUNTRY_NAMES.of(iso) ?? iso
  } catch {
    return iso
  }
}
