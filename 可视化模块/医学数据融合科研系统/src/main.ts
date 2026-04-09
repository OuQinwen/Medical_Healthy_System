/**
 * 医学智能数据融合科研系统 - 主入口文件
 * 
 * 项目概述：
 * - 这是一个基于Vue 3 + TypeScript的医学数据融合科研系统
 * - 主要功能包括数据处理、随访管理、数据质量管理和科研分析
 * - 采用现代化前端技术栈，支持响应式布局和模块化开发
 * 
 * 技术栈：
 * - Vue 3: 渐进式JavaScript框架
 * - TypeScript: 类型安全的JavaScript超集
 * - Vue Router: 官方路由管理器
 * - Pinia: Vue官方状态管理库
 * - Vite: 新一代前端构建工具
 */

import { createApp } from 'vue'
import { createPinia } from 'pinia'

import App from './App.vue'
import router from './router'
import './assets/main.css'  // 导入全局样式
import './Newstyle.css'     // 导入新UI样式

// 创建Vue应用实例
const app = createApp(App)

// 注册全局插件
app.use(createPinia())  // 状态管理
app.use(router)        // 路由管理

// 挂载应用到DOM
app.mount('#app')
