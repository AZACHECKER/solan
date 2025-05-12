/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
    "./public/index.html"
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#6366f1",
          focus: "#4f46e5",
          dark: "#3730a3",
          light: "#a5b4fc",
        },
        secondary: {
          DEFAULT: "#f59e0b",
          focus: "#d97706",
        },
      },
    },
  },
  plugins: [require("daisyui")],
  daisyui: {
    themes: ["light", "dark"],
  },
};