import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./app/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./lib/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          50: "#eef6ff",
          100: "#d9eaff",
          200: "#b7d4ff",
          300: "#85b6ff",
          400: "#4d8eff",
          500: "#2768ff",
          600: "#1248e6",
          700: "#0d39b4",
          800: "#0e328f",
          900: "#0f2d72",
        },
        ink: {
          950: "#04060d",
          900: "#0a0e1a",
          850: "#0f1422",
          800: "#161b2c",
        },
      },
      fontFamily: {
        sans: ["ui-sans-serif", "system-ui", "Segoe UI", "Roboto", "sans-serif"],
        mono: ["ui-monospace", "SFMono-Regular", "Menlo", "monospace"],
      },
      backgroundImage: {
        "glass-1":
          "linear-gradient(135deg, rgba(59,130,246,0.12) 0%, rgba(15,23,42,0.55) 60%)",
        "glass-2":
          "linear-gradient(135deg, rgba(168,85,247,0.10) 0%, rgba(15,23,42,0.55) 60%)",
        "glass-3":
          "linear-gradient(135deg, rgba(34,197,94,0.10) 0%, rgba(15,23,42,0.55) 60%)",
        "glass-4":
          "linear-gradient(135deg, rgba(244,63,94,0.10) 0%, rgba(15,23,42,0.55) 60%)",
        "glass-5":
          "linear-gradient(135deg, rgba(251,191,36,0.10) 0%, rgba(15,23,42,0.55) 60%)",
        "aurora":
          "radial-gradient(60% 50% at 50% 0%, rgba(59,130,246,0.18) 0%, rgba(2,6,23,0) 60%), radial-gradient(45% 35% at 90% 20%, rgba(168,85,247,0.12) 0%, rgba(2,6,23,0) 65%), radial-gradient(40% 30% at 10% 30%, rgba(34,197,94,0.08) 0%, rgba(2,6,23,0) 65%)",
      },
      boxShadow: {
        glass:
          "0 1px 0 0 rgba(255,255,255,0.04) inset, 0 0 0 1px rgba(148,163,184,0.10), 0 20px 40px -24px rgba(0,0,0,0.5)",
        "glow-brand":
          "0 0 0 1px rgba(59,130,246,0.35), 0 0 30px -6px rgba(59,130,246,0.45)",
      },
      keyframes: {
        pulseDot: {
          "0%, 100%": { opacity: "1" },
          "50%": { opacity: "0.35" },
        },
      },
      animation: {
        pulseDot: "pulseDot 1.6s ease-in-out infinite",
      },
    },
  },
  plugins: [],
};

export default config;
