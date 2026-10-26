// El humor de la oficina: clic izquierdo en un personaje = viene al frente y te cuenta algo (los demás se ríen);
// clic derecho = lo regañas, se asusta y se disculpa. Las bromas del proyecto las genera ADÁN una vez al día;
// estas son las de siempre, por si todavía no han llegado.
import { AGENTS } from './data'
import { useUniverso } from './store'
import { babble, laugh, yelp } from './voice'

const DEFAULT_JOKES: Record<string, string[]> = {
  ceo: ['Si este proyecto despega, el primer viaje de la oficina lo pagas tú, ¿listo?',
    'Yo no duermo, pero sueño con tu punto de equilibrio.',
    'Llevo tres cafés y todavía no me han invitado a la junta de socios.'],
  cfo: ['Con este flujo de caja no alcanza para las galletas… pero para el café sí.',
    'Mi hoja de cálculo tiene más fórmulas que yo amigos.',
    'Cuando cierres la ronda, yo pido aumento en @pples.'],
  cmo: ['Ya tengo el eslogan: «tan bueno que hasta la competencia lo quiere».',
    'Si me das presupuesto, te consigo clientes; si no, te consigo memes.',
    'Mi embudo de ventas está más lleno que la cafetería a las 10.'],
  cto: ['Funciona en mi máquina, que es lo importante.',
    'Le puse inteligencia artificial hasta a la cafetera.',
    'No es un bug, es una funcionalidad sorpresa.'],
  producto: ['Mi MVP favorito: un café que se sirve solo.',
    'Lo que no se valida, no se construye… salvo mi siesta.',
    'Prototipé una excusa para salir temprano. Falta validarla.'],
  legal: ['Antes de reírte, firma aquí, aquí y aquí.',
    'Leí la letra pequeña del menú de la cafetería. Nos deben un pan.',
    'Este chiste está protegido por derechos de autor.'],
  operaciones: ['Organicé tan bien la oficina que perdí mi silla.',
    'Mi proceso favorito: llegar, café, resolver, café.',
    'Tengo un manual para todo, hasta para reírme de tus chistes.'],
  investigador: ['Investigué y el 100 % de los fundadores necesita vacaciones. Fuente: yo.',
    'Encontré un estudio que dice que reírse sube la productividad. Ríete.',
    'Busqué «cómo descansar» en internet. Cero resultados en esta oficina.'],
}

const SCOLDED = [
  '¡Ay! Perdón, perdón, ya me pongo juicioso 😰',
  '¡No me regañe, jefe! Ya lo arreglo…',
  'Uy, ¿fue por lo del café? Prometo que fue el último ☕',
  '¡Me asustó! Ya vuelvo a mi puesto a trabajar 😅',
  'Lo siento, lo siento… ¿me perdona con una galleta?',
  '¡Entendido, entendido! Modo productivo activado 🫡',
]

const LAUGHS = ['jajaja 😂', '¡Jajaja, buenísimo!', 'jeje 😄', '¡No puedo! 🤣', 'jajajaja', '😆']

function pick<T>(list: T[]): T {
  return list[Math.floor(Math.random() * list.length)] as T
}

function jokeFor(agent: string): string {
  const own = useUniverso.getState().jokes.filter((j) => j.agente === agent).map((j) => j.texto)
  const pool = own.length ? [...own, ...own, ...(DEFAULT_JOKES[agent] ?? [])] : (DEFAULT_JOKES[agent] ?? DEFAULT_JOKES.ceo!)
  return pick(pool)
}

// Clic izquierdo: pasa al frente, cuenta la broma con voz y subtítulos, y otros dos o tres se ríen
export function tellJoke(agent: string) {
  const u = useUniverso.getState()
  const a = AGENTS.find((x) => x.id === agent)
  if (!a) return
  const text = jokeFor(agent)
  u.present(agent, 9000)
  u.say(agent, text, 7000)
  u.feel(agent, 'riendo', 7000)
  babble(agent, text)
  u.caption(`${a.name} · ${a.role}`, text, a.color)
  const others = AGENTS.filter((x) => x.id !== agent).sort(() => Math.random() - 0.5).slice(0, 2 + Math.floor(Math.random() * 2))
  others.forEach((o, i) => {
    window.setTimeout(() => {
      useUniverso.getState().feel(o.id, 'riendo', 3500)
      useUniverso.getState().say(o.id, pick(LAUGHS), 3000)
      laugh(o.id)
    }, 2600 + i * 450)
  })
}

// Clic derecho: lo regañas; brinca del susto, tiembla y se disculpa
export function scold(agent: string) {
  const u = useUniverso.getState()
  const a = AGENTS.find((x) => x.id === agent)
  if (!a) return
  const text = pick(SCOLDED)
  u.jolt(agent, 1600)
  u.feel(agent, 'estresado', 4500)
  u.say(agent, text, 4500)
  yelp(agent)
  window.setTimeout(() => babble(agent, text), 450)
  u.caption(`${a.name} · ${a.role}`, text, a.color)
  // Alguien del equipo se burla un poquito
  const witness = pick(AGENTS.filter((x) => x.id !== agent))
  window.setTimeout(() => {
    useUniverso.getState().say(witness.id, pick(['uy, uy, uy 🙊', 'jeje, te pillaron', '😬', 'yo no fui…']), 2800)
    useUniverso.getState().feel(witness.id, 'riendo', 2800)
  }, 1800)
}
