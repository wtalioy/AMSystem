import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vite.dev/config/
export default defineConfig({
  plugins: [vue()],
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: `@use "@/assets/styles/variables" as *;` // 全局注入变量
      }
    }
  },
  resolve: {
    alias: {
      '@': '/src' // 确保此配置存在
    }
  }
})
