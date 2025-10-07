import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path' // 1. Импортируем модуль 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  // 2. Добавляем секцию 'resolve' для настройки псевдонимов
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
})