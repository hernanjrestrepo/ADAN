/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Design tokens - AD-001 SS14: "confianza calmada, nunca urgencia artificial"
        adan: {
          bg: "#0f1115",
          surface: "#171a21",
          border: "#2a2f3a",
          text: "#e6e8eb",
          muted: "#9aa1ac",
          primary: "#4f7cff",
          success: "#3ecf8e",
          warning: "#f5b942",
        },
      },
    },
  },
  plugins: [],
};
