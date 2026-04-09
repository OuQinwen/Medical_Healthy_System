/**
 * user.ts - 用户状态管理
 * 
 * 功能说明：
 * - 管理当前登录用户信息
 * - 提供用户名获取和设置方法
 */

import { ref } from 'vue'

// 用户状态
const currentUser = ref<string>('')
const token = ref<string>('')

// 从 localStorage 加载用户信息
const loadUserFromStorage = () => {
  // 优先使用新的键名
  const savedUser = localStorage.getItem('currentUser')
  const savedToken = localStorage.getItem('token')
  
  // 如果新键名不存在，尝试使用旧的键名
  const oldUser = localStorage.getItem('username')
  const oldToken = localStorage.getItem('access_token')
  
  if (savedUser) {
    currentUser.value = savedUser
  } else if (oldUser) {
    currentUser.value = oldUser
    // 迁移到新的键名
    localStorage.setItem('currentUser', oldUser)
  }
  
  if (savedToken) {
    token.value = savedToken
  } else if (oldToken) {
    token.value = oldToken
    // 迁移到新的键名
    localStorage.setItem('token', oldToken)
  }
  
  console.log('[DEBUG] loadUserFromStorage 执行:')
  console.log('  - currentUser:', currentUser.value)
  console.log('  - token:', token.value ? `已设置 (长度: ${token.value.length})` : '未设置')
}

// 保存用户信息到 localStorage
const saveUserToStorage = (username: string, authToken: string) => {
  currentUser.value = username
  token.value = authToken
  localStorage.setItem('currentUser', username)
  localStorage.setItem('token', authToken)
  console.log('[DEBUG] saveUserToStorage 执行:')
  console.log('  - username:', username)
  console.log('  - token: 已设置 (长度: ${authToken.length})')
}

// 清除用户信息
const clearUser = () => {
  currentUser.value = ''
  token.value = ''
  localStorage.removeItem('currentUser')
  localStorage.removeItem('token')
  console.log('[DEBUG] clearUser 执行')
}

// 初始化时加载用户信息
loadUserFromStorage()

// 初始化时加载用户信息
loadUserFromStorage()

// 创建并导出 store 对象
export const useUserStore = () => {
  return {
    currentUser,
    token,
    saveUserToStorage,
    clearUser
  }
}