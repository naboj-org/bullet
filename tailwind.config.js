const defaultTheme = require('tailwindcss/defaultTheme')

/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './bullet/*/templates/**/*.html',
    './bullet/*/static/**/*.js',
  ],
  theme: {
    extend: {
      aspectRatio: {
        '4/3': '4 / 3',
      },
      colors: {
        primary: "var(--primary)",
        "primary-light": "var(--primary-light)",
        "primary-lighter": "var(--gradient-dark)",
        "primary-dark": "var(--primary-dark)",
      },
      gridTemplateColumns: {
        'registration': 'min-content 3fr 2fr',
        'contestants-edit': 'min-content 3fr 2fr min-content',
      },
      typography: {
        DEFAULT: {
          css: {
            maxWidth: '75ch',
            a: {
              color: 'var(--primary)',
              '&:hover': {
                color: 'var(--primary-dark)',
              },
            },
          },
        },
      }
    },
    fontFamily: {
      sans: ['"Work Sans"', 'sans-serif'],
      mono: defaultTheme.fontFamily.mono,
    },
  },
  variants: {
    extend: {},
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
  ],
}
