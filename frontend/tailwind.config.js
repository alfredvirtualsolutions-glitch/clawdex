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
        // Accent — COSMIC teal (darker shades for contrast on light surfaces)
        brand: {
          50: '#e9fafb', 100: '#c9f0f4', 200: '#a3e4ea', 300: '#7ed7df',
          400: '#5fc8d2', 500: '#48b9c7', 600: '#379aa7', 700: '#2c7c87',
          800: '#245f68', 900: '#1f4c53',
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
        // COSMIC leans rounded — bump the default container radius
        lg: '0.625rem', xl: '0.875rem', '2xl': '1.15rem',
      },
    },
  },
  plugins: [],
}
