/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./public/index.html", "./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      keyframes: {
        floatA: { to: { transform: "translate(6vmin,4vmin) scale(1.08)" } },
        floatB: { to: { transform: "translate(-5vmin,3vmin) scale(1.05)" } },
        floatC: { to: { transform: "translate(3vmin,-4vmin) scale(1.06)" } },
      },
      animation: {
        floatA: "floatA 12s ease-in-out infinite alternate",
        floatB: "floatB 14s ease-in-out infinite alternate",
        floatC: "floatC 16s ease-in-out infinite alternate",
      },
    },
  },
  plugins: [],
};
