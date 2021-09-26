module.exports = {
  purge: [
    './**/*.html',
    './**/*.js',
  ],
  darkMode: false, // or 'media' or 'class'
  theme: {
    extend: {
      colors: {
        primary: "var(--primary)",
        "primary-lighter": "var(--gradient-dark)",
      },
    },
    fontFamily: {
      sans: ['"Work Sans"', 'sans-serif'],
    },
  },
  variants: {
    extend: {},
  },
  plugins: [],
}
