module.exports = {
  content: [
    './**/*.{html,js}',
  ],
  theme: {
    extend: {
      colors: {
        primary: "var(--primary)",
        "primary-lighter": "var(--gradient-dark)",
      },
      gridTemplateColumns: {
        'registration': 'min-content 3fr 2fr 2fr',
        'participants-edit': 'min-content 3fr 2fr 2fr min-content',
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
