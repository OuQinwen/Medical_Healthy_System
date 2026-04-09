/**
 * router/index.ts - 路由配置文件
 * 
 * 功能说明：
 * - 定义应用的所有路由规则
 * - 支持Vue Router的HTML5 History模式
 * - 配置四大核心功能模块的路由
 * - 添加登录路由和认证守卫
 * 
 * 路由列表：
 * - / - 重定向到 /data
 * - /login - 登录页面
 * - /data - 数据处理页面
 * - /visit - 随访管理页面
 * - /dqm - 数据质量管理页面
 * - /science - 科研分析页面
 * - /mine - 个人中心页面
 */

import { createRouter, createWebHistory } from 'vue-router'
import NewDataView from '../views/NewDataView.vue'
import NewFollowUpView from '../views/NewFollowUpView.vue'
import NewQualityView from '../views/NewQualityView.vue'
import NewResearchView from '../views/NewResearchView.vue'
import NewLoginView from '../views/NewLoginView.vue'
import NewProFileView from '../views/NewProFileView.vue'

// 创建路由实例
const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/data'
    },
    {
      path: '/login',
      name: 'login',
      component: NewLoginView,
      meta: { requiresAuth: false }
    },
    {
      path: '/data',
      name: 'data',
      component: NewDataView,
      meta: { requiresAuth: true }
    },
    {
      path: '/visit',
      name: 'visit',
      component: NewFollowUpView,
      meta: { requiresAuth: true }
    },
    {
      path: '/dqm',
      name: 'dqm',
      component: NewQualityView,
      meta: { requiresAuth: true }
    },
    {
      path: '/science',
      name: 'science',
      component: NewResearchView,
      meta: { requiresAuth: true }
    },
    {
      path: '/mine',
      name: 'mine',
      component: NewProFileView,
      meta: { requiresAuth: true }
    }
  ],
})

// 路由守卫：检查认证状态
router.beforeEach((to, from, next) => {
  // 优先使用新的键名，兼容旧键名
  const token = localStorage.getItem('token') || localStorage.getItem('access_token')
  const requiresAuth = to.meta.requiresAuth

  console.log('[DEBUG] 路由守卫执行:')
  console.log('  - 目标路由:', to.path)
  console.log('  - 需要认证:', requiresAuth)
  console.log('  - Token 存在:', !!token)

  if (requiresAuth && !token) {
    // 需要认证但没有 token，重定向到登录页
    console.log('[DEBUG] 重定向到登录页')
    next('/login')
  } else if (to.path === '/login' && token) {
    // 已登录用户访问登录页，重定向到主页
    console.log('[DEBUG] 已登录，重定向到主页')
    next('/')
  } else {
    // 其他情况正常放行
    console.log('[DEBUG] 正常放行')
    next()
  }
})

export default router