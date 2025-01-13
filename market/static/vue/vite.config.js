import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  base: '/market/static/dist/',  // 修改为正确的基础路径
  css: {
    postcss: {
      plugins: [
        require('autoprefixer')({
          overrideBrowserslist: ['> 1%', 'last 2 versions']
        })
      ]
    }
  },
  build: {
    outDir: '../dist',  // 输出目录
    assetsDir: '',      // 资源目录
    manifest: true,     // 生成manifest.json
    rollupOptions: {
      input: './main.js',
      output: {
        entryFileNames: 'main.js',
        chunkFileNames: '[name].js',
        assetFileNames: '[name].[ext]'
      }
    }
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src')
    }
  }
}) 