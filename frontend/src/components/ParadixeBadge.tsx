// Marca de Paradixe, fija abajo a la derecha en todas las pantallas; abre su sitio en otra pestaña
export const PARADIXE_URL = 'https://www.paradixe.xyz/es/'

export default function ParadixeBadge() {
  return (
    <a href={PARADIXE_URL} target="_blank" rel="noopener noreferrer" aria-label="Paradixe (abre su sitio web)"
      title="Paradixe" data-testid="paradixe-badge"
      className="fixed bottom-3 right-3 z-40 rounded-lg bg-black/40 px-2.5 py-1.5 opacity-70 backdrop-blur transition hover:opacity-100 focus-visible:opacity-100 focus-visible:outline focus-visible:outline-2 focus-visible:outline-adan-accent">
      <img src="/brand/paradixe-logo.png" alt="Paradixe" width={780} height={143} className="h-4 w-auto sm:h-5" />
    </a>
  )
}
