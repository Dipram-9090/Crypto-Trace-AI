/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: ["class"],
  content: [
    "./src/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        border: "hsl(217.2 32.6% 17.5%)",
        background: "hsl(222.2 84% 4.9%)",
        foreground: "hsl(210 40% 98%)",
        primary: {
          DEFAULT: "hsl(187 100% 50%)", // Neon Cyan
          foreground: "hsl(222.2 47.4% 11.2%)",
        },
        destructive: {
          DEFAULT: "hsl(0 100% 50%)", // Neon Crimson
          foreground: "hsl(210 40% 98%)",
        },
        card: {
          DEFAULT: "hsl(222.2 84% 6.9%)",
          foreground: "hsl(210 40% 98%)",
        },
        cyber: {
          glow: "#00f0ff",
          danger: "#ff003c",
          warning: "#ffe600",
          success: "#00ff66",
          dark: "#0b0e14",
          panel: "#121824"
        }
      }
    },
  },
  plugins: [],
}
