/**
 * StudySync AI — design tokens.
 *
 * The palette below is the single source of truth for every surface, border,
 * accent and text color used across the app. Components should always consume
 * these tokens (e.g. `bg-navy`, `text-ivory`, `border-mauve`) instead of
 * hardcoding hex values or stock Tailwind colors.
 *
 *   ink    #00030E  deepest navy      — primary page background
 *   navy   #0B0E1A  secondary navy    — cards and elevated surfaces
 *   plum   #2C1B2F  dark plum         — secondary sections, gradients, dividers
 *   mauve  #5E3A5C  muted purple      — borders, accents, hover states
 *   blush  #B47A9A  dusty rose        — primary accent / highlight
 *   ivory  #F3E9EC  soft off-white    — primary text and important UI
 */
const palette = {
  ink: '#00030E',
  navy: '#0B0E1A',
  plum: '#2C1B2F',
  mauve: '#5E3A5C',
  blush: '#B47A9A',
  ivory: '#F3E9EC',
}

/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: palette,
      boxShadow: {
        'surface': '0 18px 40px -24px rgba(0, 3, 14, 0.9)',
        'accent-sm': '0 0 0 1px rgba(180, 122, 154, 0.35), 0 8px 24px -12px rgba(180, 122, 154, 0.35)',
        'accent-glow': '0 0 24px -6px rgba(180, 122, 154, 0.35)',
      },
      backgroundImage: {
        'page-aurora':
          'radial-gradient(60% 55% at 15% 0%, rgba(94, 58, 92, 0.35) 0%, rgba(0, 3, 14, 0) 70%), radial-gradient(55% 50% at 85% 15%, rgba(44, 27, 47, 0.55) 0%, rgba(0, 3, 14, 0) 75%)',
        'section-fade':
          'linear-gradient(180deg, rgba(0, 3, 14, 0) 0%, rgba(44, 27, 47, 0.35) 50%, rgba(0, 3, 14, 0) 100%)',
        'accent-soft': 'linear-gradient(135deg, rgba(94, 58, 92, 0.9) 0%, rgba(180, 122, 154, 0.9) 100%)',
        'plum-soft': 'linear-gradient(135deg, rgba(44, 27, 47, 0.9) 0%, rgba(94, 58, 92, 0.75) 100%)',
      },
    },
  },
  plugins: [],
}
