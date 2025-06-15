// src/main.js
import axios from 'axios' // ✅ 添加导入
import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import { createPinia } from 'pinia'
// ✅ 引入 Element Plus 组件库和样式
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
// ✅ 可选：引入中文语言包
import zhCn from 'element-plus/es/locale/lang/zh-cn'

const app = createApp(App)
app.use(createPinia())
app.use(router)
// ✅ 注册 Element Plus，并传入语言配置（可选）
app.use(ElementPlus, {
  locale: zhCn,
})
app.mount('#app')

// 配置拦截器
axios.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})