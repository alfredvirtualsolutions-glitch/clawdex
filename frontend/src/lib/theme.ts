// Theme engine — COSMIC-style runtime theming.
// Accent + corner-roundness are applied as CSS custom properties on :root, so
// the whole app (Tailwind `brand-*` utilities and `--radius-*`) re-skins live.

export type ThemeMode = 'light' | 'dark'

export interface AccentPreset { key: string; name: string; base: string }
export interface RoundPreset { key: string; name: string; lg: string; xl: string; xl2: string }

// COSMIC accents (from the COSMIC palette: teal is the default)
export const ACCENTS: AccentPreset[] = [
  { key: 'teal', name: 'Teal', base: '#48b9c7' },
  { key: 'indigo', name: 'Indigo', base: '#3e88ff' },
  { key: 'purple', name: 'Purple', base: '#cf7dff' },
  { key: 'pink', name: 'Pink', base: '#f93a83' },
  { key: 'orange', name: 'Orange', base: '#ffad00' },
  { key: 'green', name: 'Green', base: '#34b981' },
]

// COSMIC ships three corner styles: round, slightly-round (default), square
export const ROUNDS: RoundPreset[] = [
  { key: 'round', name: 'Round', lg: '0.875rem', xl: '1.15rem', xl2: '1.5rem' },
  { key: 'default', name: 'Default', lg: '0.625rem', xl: '0.875rem', xl2: '1.15rem' },
  { key: 'square', name: 'Square', lg: '0.25rem', xl: '0.375rem', xl2: '0.5rem' },
]

const DEFAULT_ACCENT = 'teal'
const DEFAULT_ROUND = 'default'

// --- color math: build a 50..900 scale from a base hex -----------------------
function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '')
  return [parseInt(h.slice(0, 2), 16), parseInt(h.slice(2, 4), 16), parseInt(h.slice(4, 6), 16)]
}
function mix([r, g, b]: number[], [r2, g2, b2]: number[], t: number): [number, number, number] {
  return [Math.round(r + (r2 - r) * t), Math.round(g + (g2 - g) * t), Math.round(b + (b2 - b) * t)]
}
const WHITE: [number, number, number] = [255, 255, 255]
const BLACK: [number, number, number] = [0, 0, 0]
const STEPS: Record<number, [boolean, number]> = {
  50: [true, 0.92], 100: [true, 0.82], 200: [true, 0.65], 300: [true, 0.45], 400: [true, 0.22],
  500: [true, 0], 600: [false, 0.14], 700: [false, 0.3], 800: [false, 0.45], 900: [false, 0.58],
}

export function scaleFor(baseHex: string): Record<number, string> {
  const base = hexToRgb(baseHex)
  const out: Record<number, string> = {}
  for (const [k, [toWhite, t]] of Object.entries(STEPS)) {
    const rgb = t === 0 ? base : mix(base, toWhite ? WHITE : BLACK, t)
    out[Number(k)] = rgb.join(' ') // "r g b" for Tailwind rgb(var(--brand-x) / <alpha>)
  }
  return out
}

// --- apply / persist ---------------------------------------------------------
export function applyAccent(key: string) {
  const preset = ACCENTS.find((a) => a.key === key) ?? ACCENTS[0]
  const scale = scaleFor(preset.base)
  const root = document.documentElement
  Object.entries(scale).forEach(([shade, rgb]) => root.style.setProperty(`--brand-${shade}`, rgb))
  localStorage.setItem('vbs-accent', preset.key)
}

export function applyRound(key: string) {
  const preset = ROUNDS.find((r) => r.key === key) ?? ROUNDS[1]
  const root = document.documentElement
  root.style.setProperty('--radius-lg', preset.lg)
  root.style.setProperty('--radius-xl', preset.xl)
  root.style.setProperty('--radius-2xl', preset.xl2)
  localStorage.setItem('vbs-round', preset.key)
}

export function initTheming() {
  applyAccent(localStorage.getItem('vbs-accent') || DEFAULT_ACCENT)
  applyRound(localStorage.getItem('vbs-round') || DEFAULT_ROUND)
}

export function currentAccent() { return localStorage.getItem('vbs-accent') || DEFAULT_ACCENT }
export function currentRound() { return localStorage.getItem('vbs-round') || DEFAULT_ROUND }
