import type { Config } from "tailwindcss";

const config: Config = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: "class",
  theme: {
    extend: {
      colors: {
        // Map Tailwind class names to CSS variables defined in globals.css.
        // e.g. bg-background, text-foreground, border-border-subtle
        background: "var(--background)",
        foreground: "var(--foreground)",
        "accent-soft": "var(--accent-soft)",
        "border-subtle": "var(--border-subtle)",
      },
    },
  },
  plugins: [],
};

export default config;
