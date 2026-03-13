/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // Core brand
        "ats-bg":       "#0B0F14",
        "ats-surface":  "#111820",
        "ats-elevated": "#182030",
        "ats-border":   "#1E2A3A",
        "ats-hover":    "#243040",

        // Trust palette
        "ats-mint":     "#01E6A8",
        "ats-blue":     "#0EA5FF",
        "ats-caution":  "#F5C156",
        "ats-danger":   "#FF6B6B",
        "ats-purple":   "#A78BFA",

        // Text
        "ats-text":     "#E2E8F0",
        "ats-muted":    "#64748B",
        "ats-dim":      "#475569",
      },
      fontFamily: {
        sans:  ["Inter", "system-ui", "sans-serif"],
        head:  ["Poppins", "Inter", "sans-serif"],
        mono:  ["'JetBrains Mono'", "monospace"],
      },
      animation: {
        "fade-up":     "fadeUp 0.35s ease both",
        "fade-in":     "fadeIn 0.3s ease both",
        "score-in":    "scoreIn 0.7s cubic-bezier(0.34, 1.56, 0.64, 1) both",
        "pulse-dot":   "pulseDot 2s ease-in-out infinite",
        "shimmer":     "shimmer 1.8s ease infinite",
        "slide-right": "slideRight 0.25s ease both",
        "slide-up":    "slideUp 0.2s ease both",
        "glow":        "glow 2s ease-in-out infinite alternate",
      },
      keyframes: {
        fadeUp: {
          "0%":   { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        fadeIn: {
          "0%":   { opacity: "0" },
          "100%": { opacity: "1" },
        },
        scoreIn: {
          "0%":   { transform: "scale(0.5)", opacity: "0" },
          "100%": { transform: "scale(1)",   opacity: "1" },
        },
        pulseDot: {
          "0%, 100%": { opacity: "1",   transform: "scale(1)" },
          "50%":      { opacity: "0.4", transform: "scale(0.8)" },
        },
        shimmer: {
          "0%":   { backgroundPosition: "-200% 0" },
          "100%": { backgroundPosition: "200% 0" },
        },
        slideRight: {
          "0%":   { opacity: "0", transform: "translateX(16px)" },
          "100%": { opacity: "1", transform: "translateX(0)" },
        },
        slideUp: {
          "0%":   { opacity: "0", transform: "translateY(6px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        glow: {
          "0%":   { boxShadow: "0 0 12px rgba(1,230,168,0.15)" },
          "100%": { boxShadow: "0 0 24px rgba(1,230,168,0.3)" },
        },
      },
      boxShadow: {
        "glow-mint":   "0 0 20px rgba(1,230,168,0.15)",
        "glow-blue":   "0 0 20px rgba(14,165,255,0.15)",
        "glow-danger": "0 0 20px rgba(255,107,107,0.15)",
      },
      borderRadius: {
        "2xl": "1rem",
        "3xl": "1.25rem",
      },
    },
  },
  plugins: [],
}
