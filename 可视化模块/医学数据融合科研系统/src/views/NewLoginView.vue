<template>
  <div class="login-page">
    <div class="login-bg">
      <div class="bg-orb orb1"></div>
      <div class="bg-orb orb2"></div>
      <div class="bg-orb orb3"></div>
    </div>
    <div class="login-card gradient-border animate-slide-up">
      <div class="login-logo">
        <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
          <rect width="48" height="48" rx="14" fill="url(#lg1)"/>
          <path d="M12 24h6l4-8 6 16 4-10 3 5h7" stroke="white" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/>
          <defs>
            <linearGradient id="lg1" x1="0" y1="0" x2="48" y2="48">
              <stop stop-color="#2563eb"/>
              <stop offset="1" stop-color="#7c3aed"/>
            </linearGradient>
          </defs>
        </svg>
      </div>
      <h1 class="login-title">医学数据融合</h1>
      <p class="login-subtitle">科研管理系统</p>

      <form @submit.prevent="handleLogin" class="login-form">
        <div class="form-group">
          <label class="form-label">用户名</label>
          <div class="input-wrapper">
            <span class="input-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </span>
            <input v-model="username" class="input" type="text" placeholder="请输入用户名" autocomplete="username"/>
          </div>
        </div>
        <div class="form-group">
          <label class="form-label">密码</label>
          <div class="input-wrapper">
            <span class="input-icon">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="3" y="11" width="18" height="11" rx="2" ry="2"/>
                <path d="M7 11V7a5 5 0 0 1 10 0v4"/>
              </svg>
            </span>
            <input v-model="password" class="input" :type="showPwd ? 'text' : 'password'" placeholder="请输入密码" autocomplete="current-password"/>
            <button type="button" class="pwd-toggle" @click="showPwd = !showPwd">
              <svg v-if="!showPwd" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                <circle cx="12" cy="12" r="3"/>
              </svg>
              <svg v-else width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                <line x1="1" y1="1" x2="23" y2="23"/>
              </svg>
            </button>
          </div>
        </div>
        <p v-if="error" class="error-msg">{{ error }}</p>
        <button type="submit" class="btn btn-primary login-btn" :disabled="loading">
          <span v-if="loading" class="animate-spin">⟳</span>
          <span v-else>登 录</span>
        </button>
      </form>

      <div class="login-hint">
        <span>默认账号：</span>
        <code>admin</code>
        <span> / </span>
        <code>admin123</code>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const username = ref('')
const password = ref('')
const showPwd = ref(false)
const loading = ref(false)
const error = ref('')

async function handleLogin() {
  if (!username.value || !password.value) {
    error.value = '请填写用户名和密码'
    return
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await fetch('http://localhost:8000/api/auth/login', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })
    
    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(errorData.detail || '登录失败')
    }
    
    const data = await response.json()
    
    // 更新 auth store，传入完整的登录响应数据
    authStore.login(data)
    
    // 跳转到数据页面
    router.push('/data')
  } catch (err: any) {
    console.error('登录错误:', err)
    error.value = err.message || '登录失败，请检查网络连接'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 20px;
  position: relative;
  overflow: hidden;
}
.login-bg { position: fixed; inset: 0; pointer-events: none; z-index: 0; }
.bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.15;
}
.orb1 { width: 300px; height: 300px; background: #2563eb; top: -100px; left: -100px; }
.orb2 { width: 250px; height: 250px; background: #7c3aed; bottom: -80px; right: -60px; }
.orb3 { width: 200px; height: 200px; background: #06b6d4; top: 50%; left: 50%; transform: translate(-50%,-50%); }

.login-card {
  width: 100%;
  max-width: 380px;
  padding: 36px 32px;
  position: relative;
  z-index: 1;
  text-align: center;
}
.login-logo { margin-bottom: 16px; display: flex; justify-content: center; }
.login-title {
  font-size: 22px;
  font-weight: 700;
  background: var(--gradient-1);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  margin-bottom: 4px;
}
.login-subtitle { color: var(--text-secondary); font-size: 13px; margin-bottom: 32px; }

.login-form { display: flex; flex-direction: column; gap: 16px; }
.form-group { text-align: left; }
.form-label { display: block; font-size: 13px; color: var(--text-secondary); margin-bottom: 6px; font-weight: 500; }
.input-wrapper { position: relative; }
.input-icon {
  position: absolute; left: 12px; top: 50%; transform: translateY(-50%);
  color: var(--text-muted); display: flex; align-items: center;
}
.input-wrapper .input { padding-left: 40px; }
.pwd-toggle {
  position: absolute; right: 12px; top: 50%; transform: translateY(-50%);
  background: none; border: none; cursor: pointer; color: var(--text-muted);
  display: flex; align-items: center; padding: 2px;
}
.pwd-toggle:hover { color: var(--text-secondary); }

.error-msg {
  color: var(--danger);
  font-size: 12px;
  text-align: center;
  padding: 8px;
  background: rgba(239,68,68,0.1);
  border-radius: 6px;
  border: 1px solid rgba(239,68,68,0.2);
}
.login-btn { width: 100%; padding: 14px; font-size: 16px; margin-top: 4px; }
.login-btn:disabled { opacity: 0.7; cursor: not-allowed; transform: none; }

.login-hint {
  margin-top: 20px;
  color: var(--text-muted);
  font-size: 12px;
}
.login-hint code {
  background: rgba(255,255,255,0.08);
  padding: 2px 6px;
  border-radius: 4px;
  color: var(--accent);
  font-family: monospace;
  font-size: 12px;
}
</style>