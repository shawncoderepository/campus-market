/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{vue,js,ts,jsx,tsx}'],
  theme: {
    extend: {
      colors: {
        // 校园二手交易 · 暖橙主色（活泼、亲切，参考闲鱼/转转）
        brand: {
          DEFAULT: '#ff6a00',
          dark: '#e65c00',
          light: '#ff8a3d',
          soft: '#fff1e6',
          gradient: '#ff9a3d',
        },
        cream: '#faf7f2',
        ink: { DEFAULT: '#2b2622', soft: '#8a8078', faint: '#c9c2ba' },
      },
      boxShadow: {
        card: '0 2px 12px rgba(43, 38, 34, 0.06)',
        'card-hover': '0 12px 32px rgba(255, 106, 0, 0.14)',
      },
    },
  },
  plugins: [],
}
