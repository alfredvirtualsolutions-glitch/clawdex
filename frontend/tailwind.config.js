/** @type {import('tailwindcss').Config} */
// COSMIC-inspired theme (System76 pop-os/cosmic-epoch).
// Accent = COSMIC teal #48B9C7; neutrals from the COSMIC dark/light palettes;
// generous corner radii; Open Sans as the interface font.
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        // Accent — driven by CSS variables so Settings can re-skin it live.
        // Defaults (COSMIC teal) are seeded in index.css and by lib/theme.ts.
        brand: {
          50: 'rgb(var(--brand-50) / <alpha-value>)',
          100: 'rgb(var(--brand-100) / <alpha-value>)',
          200: 'rgb(var(--brand-200) / <alpha-value>)',
          300: 'rgb(var(--brand-300) / <alpha-value>)',
          400: 'rgb(var(--brand-400) / <alpha-value>)',
          500: 'rgb(var(--brand-500) / <alpha-value>)',
          600: 'rgb(var(--brand-600) / <alpha-value>)',
          700: 'rgb(var(--brand-700) / <alpha-value>)',
          800: 'rgb(var(--brand-800) / <alpha-value>)',
          900: 'rgb(var(--brand-900) / <alpha-value>)',
        },
        // Neutrals — remaps `slate-*` to COSMIC greys so existing utilities adopt the theme
        slate: {
          50: '#fafafa', 100: '#f2f2f2', 200: '#e3e3e3', 300: '#cfcfcf',
          400: '#9a9a9a', 500: '#6e6e6e', 600: '#4a4a4a', 700: '#333333',
          800: '#2e2e2e', 900: '#232323', 950: '#1b1b1b',
        },
        // COSMIC extended palette (used for status/semantic accents)
        cosmic: {
          orange: '#ffad00', yellow: '#fedb40', pink: '#f93a83',
          indigo: '#3e88ff', purple: '#cf7dff', teal: '#48b9c7',
          red: '#ffb5b5', green: '#5fce93',
        },
      },
      fontFamily: {
        sans: ['"Open Sans"', 'system-ui', '-apple-system', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['ui-monospace', 'SFMono-Regular', 'Menlo', 'monospace'],
      },
      borderRadius: {
        // Driven by CSS variables so the Settings roundness preset applies live
        lg: 'var(--radius-lg, 0.625rem)',
        xl: 'var(--radius-xl, 0.875rem)',
        '2xl': 'var(--radius-2xl, 1.15rem)',
      },
    },
  },
  plugins: [],
}
