/** @type {import('tailwindcss').Config} */

// ARQUIVO DO NÚCLEO — não edite. Os VALORES vivem em
// core/static/src/input.css; este arquivo só aponta para eles via
// var(--cor-*). Cores próprias do seu domínio vão em
// core/static/src/dominio.css. Chega verbatim ao sistema gerado: nenhuma
// interpolação, nenhuma derivação em JS — a cor institucional entra só pela
// variável de ambiente correspondente no .env (core/tema.py resolve em
// runtime).
module.exports = {
  darkMode: ["selector", '[data-tema="escuro"]'],
  content: ["./core/templates/**/*.html", "./apps/**/*.html"],
  safelist: [
    "results",
    "module",
    "form-row",
    "btn",
    "btn--primaria",
    "btn--secundaria",
    "btn--neutro",
    "btn--destrutiva",
  ],
  theme: {
    extend: {
      colors: {
        page: "var(--cor-page)",
        surface: "var(--cor-surface)",
        "surface-2": "var(--cor-surface-2)",
        "surface-3": "var(--cor-surface-3)",
        ink: "var(--cor-ink)",
        "ink-2": "var(--cor-ink-2)",
        muted: "var(--cor-muted)",
        grid: "var(--cor-grid)",
        baseline: "var(--cor-baseline)",
        destructive: "var(--cor-destructive)",
        "danger-tint": "var(--cor-danger-tint)",
        "warn-bg": "var(--cor-warn-bg)",
        "warn-tx": "var(--cor-warn-tx)",
        secundaria: "var(--cor-secundaria)",
        brand: "var(--cor-brand)",
        "brand-hover": "var(--cor-brand-hover)",
        "brand-ink": "var(--cor-brand-ink)",
        "brand-tint": "var(--cor-brand-tint)",
        "seq-600": "var(--cor-seq-600)",
        "seq-450": "var(--cor-seq-450)",
        "seq-300": "var(--cor-seq-300)",
      },
      borderRadius: {
        DEFAULT: "2px",
        sm: "2px",
        md: "2px",
        lg: "2px",
        xl: "2px",
        "2xl": "2px",
      },
      fontSize: {
        xs: ["11px", { lineHeight: "1.4" }],
        sm: ["12px", { lineHeight: "1.4" }],
        base: ["13px", { lineHeight: "1.5" }],
        md: ["14px", { lineHeight: "1.5" }],
        lg: ["16px", { lineHeight: "1.4" }],
        xl: ["20px", { lineHeight: "1.3" }],
      },
      fontFamily: {
        sans: ["system-ui", "-apple-system", '"Segoe UI"', "sans-serif"],
      },
    },
  },
  plugins: [],
};
