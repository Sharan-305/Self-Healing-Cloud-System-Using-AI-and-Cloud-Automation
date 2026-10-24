/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        dark: {
          900: '#070C18',
          800: '#0B1222',
          700: '#111C35',
          600: '#182747',
          500: '#233760',
        },
        panel: {
          bg: '#0F182B',
          card: '#142038',
          hover: '#1B2B4A',
          border: '#233659',
          borderSubtle: '#1B2945'
        },
        cloud: {
          cyan: '#06B6D4',
          cyanGlow: 'rgba(6, 182, 212, 0.25)',
          blue: '#3B82F6',
          mint: '#10B981',
          amber: '#F59E0B',
          red: '#EF4444'
        }
      },
      fontFamily: {
        sans: ['Inter', '-apple-system', 'BlinkMacSystemFont', 'Segoe UI', 'Roboto', 'sans-serif'],
        mono: ['JetBrains Mono', 'Fira Code', 'Consolas', 'monospace']
      }
    },
  },
  plugins: [],
}
