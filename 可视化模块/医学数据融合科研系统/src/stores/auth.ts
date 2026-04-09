import { defineStore } from 'pinia'
import { ref } from 'vue'

export interface User {
  id: number
  username: string
  email: string
  real_name?: string
  role: string
  is_active: boolean
  is_verified: boolean
}

export const useAuthStore = defineStore('auth', () => {
  const user = ref<User | null>(null)
  const isLoggedIn = ref(false)

  // 从localStorage加载用户信息
  function loadUser() {
    const savedUser = localStorage.getItem('user')
    const token = localStorage.getItem('access_token')
    if (savedUser && token) {
      try {
        user.value = JSON.parse(savedUser)
        isLoggedIn.value = true
      } catch (e) {
        // 如果解析失败，清除损坏的数据
        localStorage.removeItem('user')
        localStorage.removeItem('isLoggedIn')
      }
    }
  }

  // 登录
  function login(userData: any) {
    // 适配后端返回的用户数据结构
    const userObj: User = {
      id: userData.user?.id || userData.id || 0,
      username: userData.user?.username || userData.username || '',
      email: userData.user?.email || userData.email || '',
      real_name: userData.user?.real_name || userData.real_name,
      role: userData.user?.role || userData.role || 'doctor',
      is_active: userData.user?.is_active ?? userData.is_active ?? true,
      is_verified: userData.user?.is_verified ?? userData.is_verified ?? false
    }
    
    user.value = userObj
    isLoggedIn.value = true
    localStorage.setItem('user', JSON.stringify(userObj))
    localStorage.setItem('isLoggedIn', 'true')
    
    // 保存token
    if (userData.access_token) {
      localStorage.setItem('access_token', userData.access_token)
      localStorage.setItem('token', userData.access_token)
    }
  }

  // 登出
  function logout() {
    user.value = null
    isLoggedIn.value = false
    localStorage.removeItem('user')
    localStorage.removeItem('isLoggedIn')
    localStorage.removeItem('token')
    localStorage.removeItem('access_token')
  }

  // 获取角色显示名称
  function getRoleDisplayName(): string {
    if (!user.value) return ''
    
    const roleMap: Record<string, string> = {
      'admin': '管理员',
      'doctor': '医生'
    }
    
    return roleMap[user.value.role] || user.value.role
  }

  // 检查是否有管理员权限
  function isAdmin(): boolean {
    return user.value?.role === 'admin'
  }

  // 检查是否有医生权限
  function isDoctor(): boolean {
    return user.value?.role === 'doctor' || user.value?.role === 'admin'
  }

  // 初始化时加载用户信息
  loadUser()

  return {
    user,
    isLoggedIn,
    login,
    logout,
    getRoleDisplayName,
    isAdmin,
    isDoctor
  }
})