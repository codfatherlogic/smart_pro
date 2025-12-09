/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{vue,js,ts,jsx,tsx}",
    "./node_modules/frappe-ui/src/components/**/*.{vue,js}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: "#0089FF",
          50: "#E5F3FF",
          100: "#CCE7FF",
          200: "#99CFFF",
          300: "#66B7FF",
          400: "#339FFF",
          500: "#0089FF",
          600: "#006DCC",
          700: "#005299",
          800: "#003666",
          900: "#001B33",
        },
      },
    },
  },
  plugins: [],
}
