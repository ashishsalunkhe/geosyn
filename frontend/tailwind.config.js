/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        background: "var(--background)",
        foreground: "var(--foreground)",
        primary: {
          DEFAULT: "var(--primary)",
          dark: "var(--primary-dark)",
        },
        secondary: "var(--secondary)",
        border: "var(--border)",
        hazard: "var(--hazard)",
        success: "var(--success)",
        error: "var(--error)",
        info: "var(--info)",
        "text-muted": "var(--text-muted)",
        "panel-bg": "var(--panel-bg)",
        surface: "rgba(255, 255, 255, 0.03)",
        glass: "rgba(255, 255, 255, 0.05)",
      },
      fontFamily: {
        tactical: ["Inter", "monospace"],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
      }
    },
  },
  plugins: [],
}
