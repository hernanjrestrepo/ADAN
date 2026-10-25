// Logos corporativos en vector: el equipo propone el concepto (estilo, ícono, tipografía y paleta) y aquí se dibuja
// el SVG con íconos de Lucide (licencia ISC) y la tipografía incrustada, para que se vea igual en todas partes.
import {
  Activity, Anchor, Apple, Award, Bike, Book, Brain, Briefcase, Building2, Camera, Car, Cloud, Code, Coffee, Compass,
  Cpu, CreditCard, Crown, Droplet, Dumbbell, Feather, Flame, Gem, Gift, Globe, GraduationCap, Hammer, Handshake, Heart,
  House, Infinity as InfinityIcon, Key, Leaf, Lightbulb, Lock, Map, Mountain, Music, Package, Palette, PawPrint,
  PiggyBank, Plane, Rocket, Scissors, Shield, Ship, Shirt, ShoppingBag, Smile, Sparkles, Sprout, Star, Stethoscope,
  Store, Sun, Target, TrendingUp, Truck, Users, Utensils, Wallet, Wifi, Wind, Wrench, Zap, type IconNode,
} from 'lucide'
import bebas from '@fontsource/bebas-neue/files/bebas-neue-latin-400-normal.woff2?url'
import montserrat from '@fontsource/montserrat/files/montserrat-latin-700-normal.woff2?url'
import nunito from '@fontsource/nunito/files/nunito-latin-700-normal.woff2?url'
import oswald from '@fontsource/oswald/files/oswald-latin-700-normal.woff2?url'
import playfair from '@fontsource/playfair-display/files/playfair-display-latin-700-normal.woff2?url'
import poppins from '@fontsource/poppins/files/poppins-latin-700-normal.woff2?url'
import raleway from '@fontsource/raleway/files/raleway-latin-700-normal.woff2?url'
import spaceGrotesk from '@fontsource/space-grotesk/files/space-grotesk-latin-700-normal.woff2?url'

export interface LogoConcept {
  id: string
  nombre_concepto: string
  estilo: 'icono_texto' | 'monograma' | 'emblema' | 'solo_texto'
  icono: string
  tipografia: string
  primario: string
  acento: string
  fondo: string
  por_que: string
}

const ICONS: Record<string, IconNode> = {
  Activity, Anchor, Apple, Award, Bike, Book, Brain, Briefcase, Building2, Camera, Car, Cloud, Code, Coffee, Compass,
  Cpu, CreditCard, Crown, Droplet, Dumbbell, Feather, Flame, Gem, Gift, Globe, GraduationCap, Hammer, Handshake, Heart,
  House, Infinity: InfinityIcon, Key, Leaf, Lightbulb, Lock, Map, Mountain, Music, Package, Palette, PawPrint,
  PiggyBank, Plane, Rocket, Scissors, Shield, Ship, Shirt, ShoppingBag, Smile, Sparkles, Sprout, Star, Stethoscope,
  Store, Sun, Target, TrendingUp, Truck, Users, Utensils, Wallet, Wifi, Wind, Wrench, Zap,
}

const FONTS: Record<string, string> = {
  Montserrat: montserrat, Poppins: poppins, 'Playfair Display': playfair, 'Bebas Neue': bebas, 'Space Grotesk': spaceGrotesk,
  Nunito: nunito, Raleway: raleway, Oswald: oswald,
}

const fontCache: Record<string, Promise<string>> = {}

// La fuente va dentro del SVG (base64): así el logo se ve igual como imagen, en el navegador y al descargarlo
function fontData(family: string): Promise<string> {
  const url = FONTS[family] ?? FONTS.Montserrat
  fontCache[family] ??= fetch(url as string).then((r) => r.arrayBuffer()).then((buf) => {
    let bin = ''
    const bytes = new Uint8Array(buf)
    for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000))
    return btoa(bin)
  })
  return fontCache[family]
}

function esc(text: string) {
  return text.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;')
}

// Un ícono de Lucide (24×24, trazo) dentro del logo, escalado y coloreado
function icon(name: string, x: number, y: number, size: number, color: string, stroke = 2): string {
  const node = ICONS[name] ?? ICONS.Sparkles ?? []
  const inner = node.map(([tag, attrs]) => `<${tag} ${Object.entries(attrs).map(([k, v]) => `${k}="${esc(String(v))}"`).join(' ')}/>`).join('')
  return `<g transform="translate(${x} ${y}) scale(${size / 24})" fill="none" stroke="${color}" stroke-width="${stroke}" stroke-linecap="round" stroke-linejoin="round">${inner}</g>`
}

function initials(name: string) {
  const words = name.trim().split(/\s+/).filter(Boolean)
  return (words.length > 1 ? (words[0]?.[0] ?? '') + (words[1]?.[0] ?? '') : name.slice(0, 2)).toUpperCase()
}

export async function logoSvg(c: LogoConcept, name: string, slogan = ''): Promise<string> {
  const font = await fontData(c.tipografia)
  const fam = 'LogoFont'
  const style = `<style>@font-face{font-family:'${fam}';src:url(data:font/woff2;base64,${font}) format('woff2');}text{font-family:'${fam}',sans-serif;}</style>`
  const upper = c.tipografia === 'Bebas Neue' || c.tipografia === 'Oswald'
  const label = esc(upper ? name.toUpperCase() : name)
  const fit = (base: number, max: number) => Math.min(base, Math.floor(max / Math.max(1, name.length * 0.58)))
  const sub = slogan ? esc(slogan) : ''
  let body: string
  let w = 640
  let h = 240
  if (c.estilo === 'icono_texto') {
    const fs = fit(78, 400)
    body = `<rect x="24" y="44" width="152" height="152" rx="36" fill="${c.primario}"/>${icon(c.icono, 52, 72, 96, c.fondo, 1.8)}
      <text x="204" y="${sub ? 132 : 146}" font-size="${fs}" font-weight="700" fill="${c.primario}">${label}</text>
      ${sub ? `<text x="206" y="178" font-size="24" fill="${c.acento}">${sub}</text>` : ''}`
  } else if (c.estilo === 'monograma') {
    w = 420
    h = 420
    body = `<circle cx="210" cy="170" r="132" fill="${c.primario}"/><circle cx="210" cy="170" r="132" fill="none" stroke="${c.acento}" stroke-width="10"/>
      <text x="210" y="${170 + 46}" font-size="132" font-weight="700" fill="${c.fondo}" text-anchor="middle">${esc(initials(name))}</text>
      <text x="210" y="356" font-size="${fit(44, 360)}" font-weight="700" fill="${c.primario}" text-anchor="middle">${label}</text>
      ${sub ? `<text x="210" y="396" font-size="20" fill="${c.acento}" text-anchor="middle">${sub}</text>` : ''}`
  } else if (c.estilo === 'emblema') {
    w = 420
    h = 440
    body = `<path d="M210 20 L380 90 V220 C380 320 300 390 210 420 C120 390 40 320 40 220 V90 Z" fill="${c.primario}"/>
      <path d="M210 44 L358 104 V220 C358 306 290 366 210 394 C130 366 62 306 62 220 V104 Z" fill="none" stroke="${c.acento}" stroke-width="6"/>
      ${icon(c.icono, 160, 96, 100, c.fondo, 1.6)}
      <text x="210" y="${sub ? 272 : 290}" font-size="${fit(46, 280)}" font-weight="700" fill="${c.fondo}" text-anchor="middle">${label}</text>
      ${sub ? `<text x="210" y="312" font-size="18" fill="${c.acento}" text-anchor="middle">${sub}</text>` : ''}`
  } else {
    const fs = fit(104, 580)
    body = `<text x="320" y="${sub ? 132 : 146}" font-size="${fs}" font-weight="700" fill="${c.primario}" text-anchor="middle">${label}</text>
      <rect x="250" y="${sub ? 152 : 166}" width="140" height="8" rx="4" fill="${c.acento}"/>
      ${sub ? `<text x="320" y="200" font-size="24" fill="${c.primario}" text-anchor="middle" opacity="0.8">${sub}</text>` : ''}`
  }
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}">${style}<rect width="100%" height="100%" fill="${c.fondo}"/>${body}</svg>`
}

export function svgDataUrl(svg: string): string {
  const bytes = new TextEncoder().encode(svg)
  let bin = ''
  for (let i = 0; i < bytes.length; i += 0x8000) bin += String.fromCharCode(...bytes.subarray(i, i + 0x8000))
  return `data:image/svg+xml;base64,${btoa(bin)}`
}
