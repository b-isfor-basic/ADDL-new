module.exports = {
  content: [
    './templates/**/*.html',
    './node_modules/flowbite/**/*.js'
  ],
  theme: {
    extend: {
      colors: {
        'primary': {
          '50': '#f2f1fe',
          '100': '#ddd9fc',
          '200': '#b5b3f9',
          '300': '#887ef7',
          '400': '#503df5',
          '500': '#2609e1',
          '600': '#2506b2',
          '700': '#180391',
          '800': '#0f016a',
          '900': '#05002e',
        },      
      },
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('flowbite/plugin')
  ],
}
