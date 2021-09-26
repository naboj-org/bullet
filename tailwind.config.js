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
      gridTemplateColumns: {
        'registration': 'min-content 3fr 3fr 2fr 2fr',
      }
    },
    fontFamily: {
      sans: ['"Work Sans"', 'sans-serif'],
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
  ],
}
