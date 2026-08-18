/** @type {import('tailwindcss').Config} */
module.exports = {
  // darkMode/paleta de marca ficam fora de escopo desta fase (CORE-03/Fase
  // 2) — este config é o piso mínimo para provar o pipeline de build.
  content: ["./core/templates/**/*.html"],
  theme: {
    extend: {},
  },
  plugins: [],
};
