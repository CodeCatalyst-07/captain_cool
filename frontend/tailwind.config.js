/** @type {import('tailwindcss').Config} */
export default {
  content: [
    './index.html',
    './src/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        pitch: {
          950: '#020b14',
          900: '#030d1a',
          800: '#051328',
          700: '#071a35',
          600: '#0a2240',
        },
        gold: {
          300: '#fde68a',
          400: '#fcd34d',
          500: '#f59e0b',
          600: '#d97706',
        },
        cricket: {
          green: '#00a651',
          'green-dark': '#007a3d',
          'green-light': '#4ade80',
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        display: ['Outfit', 'Inter', 'sans-serif'],
      },
      animation: {
        'fade-slide-up': 'fadeSlideUp 0.6s ease forwards',
        'spin-slow': 'spin 2s linear infinite',
        'pulse-gold': 'pulseGold 2s ease-in-out infinite',
        'shimmer': 'shimmer 2s linear infinite',
      },
      keyframes: {
        fadeSlideUp: {
          '0%': { opacity: '0', transform: 'translateY(32px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        pulseGold: {
          '0%, 100%': { boxShadow: '0 0 0 0 rgba(245, 158, 11, 0.4)' },
          '50%': { boxShadow: '0 0 0 12px rgba(245, 158, 11, 0)' },
        },
        shimmer: {
          '0%': { backgroundPosition: '-200% 0' },
          '100%': { backgroundPosition: '200% 0' },
        },
      },
      backgroundImage: {
        'pitch-gradient': 'linear-gradient(135deg, #020b14 0%, #051328 40%, #071a35 100%)',
        'gold-gradient': 'linear-gradient(135deg, #f59e0b 0%, #fcd34d 50%, #d97706 100%)',
        'green-gradient': 'linear-gradient(135deg, #007a3d 0%, #00a651 100%)',
      },
    },
  },
  plugins: [],
}
