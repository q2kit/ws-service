/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["src/**/*.html", "src/**/*.{js,ts}"],
  plugins: [require("daisyui")],
  theme: {
    extend: {
    },
    fontFamily: {
      "noto-jp": ['Noto Sans JP', 'sans-serif']
    },
  },
  daisyui: {
    themes: [
      {
      }
    ],
    base: true,
    styled: true,
    utils: true,
    prefix: "",
    logs: true,
    themeRoot: ":root",
  },
}

