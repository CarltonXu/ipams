import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    proxy: {
      '/api': {
        target: 'http://localhost:5001',
        changeOrigin: true
      },
      // 头像的代理访问
      '/uploads': {
        target: 'http://localhost:5001',
        changeOrigin: true
      }
    },
    port: 3001, // 默认的前端开发端口，确保它没有被占用
    open: true   // 自动打开浏览器
  }
})
