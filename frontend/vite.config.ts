import { defineConfig, loadEnv } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

export default defineConfig(({ mode }) => {
  // 加载环境变量
  const env = loadEnv(mode, process.cwd())
  
  return {
    plugins: [vue()],
    server: {
      proxy: {
        '/api': {
          target: env.VITE_API_BASE_URL,
          changeOrigin: true
        },
        // 头像的代理访问
        '/uploads': {
          target: env.VITE_UPLOAD_BASE_URL,
          changeOrigin: true
        }
      },
      host: true,
      port: parseInt(env.VITE_SERVER_PORT || '3001'),
      open: true   // 自动打开浏览器
    },
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  }
})
