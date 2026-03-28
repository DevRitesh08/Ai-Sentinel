/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      colors: {
        // Canvas
        "ats-bg":       "#080E16",
        "ats-surface":  "#0D1520",
        "ats-elevated": "#121E2C",
        "ats-border":   "#182030",
        "ats-hover":    "#1E2D40",
        // Accents
        "ats-teal":     "#01C4A0",
        "ats-blue":     "#4BA8E8",
        "ats-gold":     "#F0B43C",
        "ats-red":      "#F5505A",
        "ats-violet":   "#9B7DE8",
        // Alias (backward compat)
        "ats-mint":     "#01C4A0",
        "ats-caution":  "#F0B43C",
        "ats-danger":   "#F5505A",
        "ats-purple":   "#9B7DE8",
        // Text
        "ats-text":     "#C8D8E8",
        "ats-muted":    "#5A7A90",
        "ats-dim":      "#3D5670",
      },
      fontFamily: {
        sans:  ["Geist", "Inter", "system-ui", "sans-serif"],
        head:  ["Sora", "Geist", "sans-serif"],
        mono:  ["'Geist Mono'", "'JetBrains Mono'", "monospace"],
      },
      animation: {
        "fade-up":     "fadeUp 0.35s ease both",
        "fade-in":     "fadeIn 0.3s ease both",
        "score-in":    "scoreIn 0.6s cubic-bezier(0.34,1.56,0.64,1) both",
        "slide-right": "slideRight 0.25s ease both",
        "slide-up":    "slideUp 0.2s ease both",
        "shimmer":     "shimmer 2s ease infinite",
        "pulse-glow":  "pulseGlow 2s ease-in-out infinite",
        "think-dot":   "thinkDot 1.2s ease-in-out infinite",
        "caret-blink": "caretBlink 0.8s ease infinite",
        "ping":        "ping 1.5s ease infinite",
      },
      boxShadow: {
        "glow-teal":   "0 0 24px rgba(1,196,160,0.2)",
        "glow-blue":   "0 0 24px rgba(14,120,200,0.2)",
        "glow-danger": "0 0 20px rgba(245,80,90,0.2)",
        "card":        "0 4px 24px rgba(0,0,0,0.35)",
      },
      borderRadius: {
        "2xl": "16px",
        "3xl": "22px",
      },
    },
  },
  plugins: [],
};
