/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: '#ff6b35',
        secondary: '#f7931e', 
        accent: '#ffcc02',
        dark: '#1a1a2e',
        'dark-light': '#16213e',
        'game-blue': '#0f3460',
        'game-purple': '#533483'
      },
      fontFamily: {
        'pixel': ['"Press Start 2P"', 'cursive'],
        'gaming': ['Orbitron', 'sans-serif']
      }
    },
  },
  plugins: [],
}
