/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        upm: {
          green: "#009c48", // UPM Brand Green
          dark: "#333333",
          light: "#f4f4f4"
        }
      }
    },
  },
  plugins: [],
}