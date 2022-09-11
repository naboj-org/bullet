/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './bullet/**/*.{html,js}',
  ],
  theme: {
    extend: {
      colors: {
        primary: "var(--primary)",
        "primary-light": "var(--primary-light)",
        "primary-lighter": "var(--gradient-dark)",
        "primary-dark": "var(--primary-dark)",
      },
      gridTemplateColumns: {
        'registration': 'min-content 3fr 2fr 2fr',
        'contestants-edit': 'min-content 3fr 2fr 2fr min-content',
      },
      typography: {
        DEFAULT: {
          css: {
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
