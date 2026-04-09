<template>
  <div>
    <div class="page-topbar">
      <h1>个人中心</h1>
      <button class="btn btn-icon" @click="showSettings = true">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="3"/><path d="M19.07 4.93a10 10 0 0 1 1.2 12.09l-1.42 1.42a2 2 0 0 1-2.83 0l-.7-.7a2 2 0 0 0-2.83 0l-.7.7a2 2 0 0 1-2.83 0L6.54 17A10 10 0 0 1 4.93 4.93"/>
        </svg>
      </button>
    </div>

    <div class="page">
      <!-- User Card -->
      <div class="user-card gradient-border">
        <div class="user-avatar-wrap">
          <div class="user-avatar">{{ authStore.user?.name?.[0]?.toUpperCase() || 'A' }}</div>
          <div class="avatar-ring"></div>
        </div>
        <div class="user-info">
          <h2 class="user-name">{{ authStore.user?.real_name || authStore.user?.username || '用户' }}</h2>
          <span class="badge badge-blue user-role">{{ authStore.getRoleDisplayName() || '医生' }}</span>
          <p class="user-id">ID: MED-{{ authStore.user?.id || '000001' }}</p>
        </div>
      </div>

      <!-- Data Stats -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon-wrapper" style="background: var(--gradient-1)">
            <svg class="stat-icon-svg" width="24" height="24" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="18" r="8" fill="white"/>
              <path d="M12 42 Q12 30 24 30 Q36 30 36 42" stroke="white" stroke-width="3" stroke-linecap="round" fill="none"/>
            </svg>
          </div>
          <div class="stat-value">{{ userStats[0].value }}</div>
          <div class="stat-label">{{ userStats[0].label }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrapper" style="background: var(--gradient-2)">
            <svg class="stat-icon-svg" width="24" height="24" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="16" fill="none" stroke="white" stroke-width="3"/>
              <path d="M16 24 L22 30 L32 18" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-value">{{ userStats[1].value }}</div>
          <div class="stat-label">{{ userStats[1].label }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrapper" style="background: var(--gradient-3)">
            <svg class="stat-icon-svg" width="24" height="24" viewBox="0 0 48 48" fill="none">
              <path d="M4 24 L44 24" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <path d="M24 4 L24 44" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <circle cx="24" cy="24" r="4" fill="white"/>
            </svg>
          </div>
          <div class="stat-value">{{ userStats[2].value }}</div>
          <div class="stat-label">{{ userStats[2].label }}</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrapper" style="background: linear-gradient(135deg, #f59e0b, #d97706)">
            <svg class="stat-icon-svg" width="24" height="24" viewBox="0 0 48 48" fill="none">
              <path d="M8 12 L40 12" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <path d="M8 24 L40 24" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <path d="M8 36 L40 36" stroke="white" stroke-width="3" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-value">{{ userStats[3].value }}</div>
          <div class="stat-label">{{ userStats[3].label }}</div>
        </div>
      </div>

      <!-- Function List -->
      <div class="func-list card">
        <div
          v-for="item in funcItems"
          :key="item.title"
          class="func-item"
          @click="handleFuncClick(item)"
        >
          <div class="func-item-left">
            <div class="func-item-icon" :style="{background: item.color}" v-html="item.icon"></div>
            <div>
              <div class="func-item-title">{{ item.title }}</div>
              <div class="func-item-desc">{{ item.desc }}</div>
            </div>
          </div>
          <div class="func-item-arrow">›</div>
        </div>
      </div>

      <!-- Logout -->
      <button class="btn btn-danger logout-btn" @click="handleLogout">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
          <polyline points="16 17 21 12 16 7"/>
          <line x1="21" y1="12" x2="9" y2="12"/>
        </svg>
        退出登录
      </button>
    </div>

    <!-- Settings Modal -->
    <Teleport to="body">
      <div v-if="showSettings" class="modal-overlay" @click.self="showSettings = false">
        <div class="modal-card animate-slide-up">
          <div class="modal-header">
            <h3>系统设置</h3>
            <button class="btn btn-icon" @click="showSettings = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="settings-section">
              <div class="settings-title">AI 模型选择</div>
              <p class="settings-desc">选择用于 OCR 和数据处理的 AI 模型类型</p>
              
              <div class="model-selector">
                <div 
                  :class="['model-option', { active: selectedModel === 'cloud' }]"
                  @click="selectedModel = 'cloud'"
                >
                  <div class="model-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M18 10h-1.26A8 8 0 1 0 9 20h9a5 5 0 0 0 0-10z"/>
                    </svg>
                  </div>
                  <div class="model-info">
                    <div class="model-name">云端模型</div>
                    <div class="model-desc">使用云端 API 服务，需要联网</div>
                  </div>
                  <div v-if="selectedModel === 'cloud'" class="model-check">✓</div>
                </div>
                
                <div 
                  :class="['model-option', { active: selectedModel === 'local' }]"
                  @click="selectedModel = 'local'"
                >
                  <div class="model-icon">
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                      <line x1="8" y1="21" x2="16" y2="21"/>
                      <line x1="12" y1="17" x2="12" y2="21"/>
                    </svg>
                  </div>
                  <div class="model-info">
                    <div class="model-name">本地模型</div>
                    <div class="model-desc">使用本地 Ollama 服务，无需联网</div>
                  </div>
                  <div v-if="selectedModel === 'local'" class="model-check">✓</div>
                </div>
              </div>
            </div>
            
            <!-- 云端 API 配置区域（仅在选择云端模型时显示） -->
            <div v-if="selectedModel === 'cloud'" class="api-config-section">
              <div class="api-config-header">
                <h4 class="api-config-title">云端 API 配置</h4>
                <p class="api-config-desc">请配置云端模型的 API 密钥</p>
              </div>
              
              <!-- API密钥输入模式选择 -->
              <div class="api-mode-selector">
                <div 
                  :class="['api-mode-option', { active: apiKeyMode === 'unified' }]"
                  @click="apiKeyMode = 'unified'"
                >
                  <div class="api-mode-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M12 2L2 7l10 5 10-5-10-5z"/>
                      <path d="M2 17l10 5 10-5"/>
                      <path d="M2 12l10 5 10-5"/>
                    </svg>
                  </div>
                  <div class="api-mode-info">
                    <div class="api-mode-name">统一密钥</div>
                    <div class="api-mode-desc">一个硅胶流动API密钥用于所有模型</div>
                  </div>
                </div>
                
                <div 
                  :class="['api-mode-option', { active: apiKeyMode === 'separate' }]"
                  @click="apiKeyMode = 'separate'"
                >
                  <div class="api-mode-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                      <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
                      <polyline points="3.27 6.96 12 12.01 20.73 6.96"/>
                      <line x1="12" y1="22.08" x2="12" y2="12"/>
                    </svg>
                  </div>
                  <div class="api-mode-info">
                    <div class="api-mode-name">分别密钥</div>
                    <div class="api-mode-desc">分别为视觉模型和语言模型配置API密钥</div>
                  </div>
                </div>
              </div>
              
              <!-- 统一密钥输入 -->
              <div v-if="apiKeyMode === 'unified'" class="api-input-group">
                <label class="api-label">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 2l-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.778 7.778 5.5 5.5 0 0 1 7.777-7.777zm0 0L15.5 7.5m0 0l3 3L22 7l-3-3m-3.5 3.5L19 4"/>
                  </svg>
                  硅胶流动 API 密钥
                </label>
                <input
                  v-model="apiKey"
                  type="password"
                  placeholder="请输入硅胶流动 API 密钥（sk-...）"
                  class="api-input"
                />
              </div>
              
              <!-- 分别密钥输入 -->
              <div v-if="apiKeyMode === 'separate'" class="api-input-group">
                <label class="api-label">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                  视觉模型 API 密钥
                </label>
                <input
                  v-model="visionApiKey"
                  type="password"
                  placeholder="请输入视觉模型的 API 密钥"
                  class="api-input"
                />
              </div>
              
              <div v-if="apiKeyMode === 'separate'" class="api-input-group">
                <label class="api-label">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2 12s3-7 7-7 7 7-7 7 7-7 7-7-7z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  语言模型 API 密钥
                </label>
                <input
                  v-model="llmApiKey"
                  type="password"
                  placeholder="请输入语言模型的 API 密钥"
                  class="api-input"
                />
              </div>
              
              <!-- 模型名称输入 -->
              <div v-if="selectedModel === 'cloud'" class="api-input-group">
                <label class="api-label">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M2 12s3-7 7-7 7 7-7 7 7-7 7-7-7z"/>
                    <circle cx="12" cy="12" r="3"/>
                  </svg>
                  OCR 视觉模型
                </label>
                <input
                  v-model="visionModel"
                  type="text"
                  placeholder="deepseek-ai/DeepSeek-OCR（推荐）或 Qwen/Qwen2.5-VL-32B-Instruct"
                  class="api-input"
                />
              </div>
              
              <div v-if="selectedModel === 'cloud'" class="api-input-group">
                <label class="api-label">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
                  </svg>
                  语言模型
                </label>
                <input
                  v-model="llmModel"
                  type="text"
                  placeholder="Qwen/Qwen2.5-32B-Instruct"
                  class="api-input"
                />
              </div>
              
              <div v-if="selectedModel === 'cloud'" class="api-config-hint">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <span>API 密钥将保存在服务器端，用于调用云端服务。获取 API 密钥请访问：https://siliconflow.cn/</span>
              </div>
              
              <div v-if="selectedModel === 'cloud'" class="api-status" :class="apiConnected ? 'connected' : 'disconnected'">
                <span>{{ apiConnected ? '✓ 已连接' : '○ 未连接' }}</span>
                <button class="btn btn-sm btn-secondary" @click="testApi">测试连接</button>
              </div>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showSettings = false">取消</button>
            <button class="btn btn-primary" @click="saveSettings">保存设置</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Security Modal - 账户安全 -->
    <Teleport to="body">
      <div v-if="showSecurity" class="modal-overlay" @click.self="showSecurity = false">
        <div class="modal-card animate-slide-up">
          <div class="modal-header">
            <h3>账户安全</h3>
            <button class="btn btn-icon" @click="showSecurity = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="security-info-section">
              <div class="security-info-item">
                <div class="security-info-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2">
                    <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                    <circle cx="12" cy="7" r="4"/>
                  </svg>
                </div>
                <div class="security-info-content">
                  <div class="security-info-title">账号信息</div>
                  <div class="security-info-value">{{ authStore.user?.username || '未设置' }}</div>
                </div>
              </div>
              
              <div class="security-info-item">
                <div class="security-info-icon">
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2">
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                </div>
                <div class="security-info-content">
                  <div class="security-info-title">邮箱</div>
                  <div class="security-info-value">{{ authStore.user?.email || '未设置' }}</div>
                </div>
              </div>
            </div>

            <div class="security-divider"></div>

            <div class="security-section">
              <h4 class="security-section-title">修改密码</h4>
              <p class="security-section-desc">定期修改密码可以保护您的账户安全</p>
              
              <div class="form-group">
                <label class="form-label">当前密码 <span class="required">*</span></label>
                <input
                  v-model="passwordForm.currentPassword"
                  type="password"
                  placeholder="请输入当前密码"
                  class="input"
                />
              </div>
              
              <div class="form-group">
                <label class="form-label">新密码 <span class="required">*</span></label>
                <input
                  v-model="passwordForm.newPassword"
                  type="password"
                  placeholder="请输入新密码（至少6位）"
                  class="input"
                />
              </div>
              
              <div class="form-group">
                <label class="form-label">确认新密码 <span class="required">*</span></label>
                <input
                  v-model="passwordForm.confirmPassword"
                  type="password"
                  placeholder="请再次输入新密码"
                  class="input"
                />
              </div>

              <div class="password-strength" v-if="passwordForm.newPassword">
                <div class="strength-bar">
                  <div 
                    class="strength-fill" 
                    :class="passwordStrength.level"
                    :style="{ width: passwordStrength.width }"
                  ></div>
                </div>
                <div class="strength-text">{{ passwordStrength.text }}</div>
              </div>
            </div>

            <div v-if="passwordError" class="error-message">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#ef4444" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <line x1="12" y1="8" x2="12" y2="12"/>
                <line x1="12" y1="16" x2="12.01" y2="16"/>
              </svg>
              {{ passwordError }}
            </div>

            <div v-if="passwordSuccess" class="success-message">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#10b981" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              {{ passwordSuccess }}
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showSecurity = false">取消</button>
            <button 
              class="btn btn-primary" 
              @click="changePassword"
              :disabled="isChangingPassword"
            >
              {{ isChangingPassword ? '修改中...' : '确认修改' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Help Center Modal -->
    <HelpCenter :visible="showHelp" @close="showHelp = false" />

    <!-- About Us Modal -->
    <AboutUs :visible="showAbout" @close="showAbout = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import HelpCenter from '../components/HelpCenter.vue'
import AboutUs from '../components/AboutUs.vue'

const API_BASE_URL = 'http://localhost:8000'

const router = useRouter()
const authStore = useAuthStore()
const showSettings = ref(false)
const showSecurity = ref(false)
const showHelp = ref(false)
const showAbout = ref(false)
const selectedModel = ref<'cloud' | 'local'>('cloud')
const apiKey = ref('')
const apiEndpoint = ref('https://api.siliconflow.cn/v1')
const apiConnected = ref(false)

// 修改密码相关
const passwordForm = ref({
  currentPassword: '',
  newPassword: '',
  confirmPassword: ''
})
const isChangingPassword = ref(false)
const passwordError = ref('')
const passwordSuccess = ref('')

// API密钥输入模式：unified（统一）或 separate（分别）
const apiKeyMode = ref<'unified' | 'separate'>('unified')

// 分别的API密钥
const visionApiKey = ref('')
const llmApiKey = ref('')

// 模型名称
const visionModel = ref('deepseek-ai/DeepSeek-OCR')
const llmModel = ref('Qwen/Qwen2.5-32B-Instruct')

// 患者数据
const patients = ref<any[]>([])

// 用户统计数据（计算属性）
const userStats = computed(() => {
  const totalPatients = patients.value.length
  const completedPatients = patients.value.filter(p => p.status === '已完成').length
  const completionRate = totalPatients > 0 ? Math.round((completedPatients / totalPatients) * 100) : 0
  
  // 计算本月新增
  const now = new Date()
  const newThisMonth = patients.value.filter(p => {
    const joinDate = new Date(p.joinDate)
    return joinDate.getMonth() === now.getMonth() && joinDate.getFullYear() === now.getFullYear()
  }).length
  
  return [
    { icon: '👥', value: totalPatients.toString(), label: '管理患者' },
    { icon: '✅', value: completedPatients.toString(), label: '已完成' },
    { icon: '📈', value: completionRate.toString() + '%', label: '完成率' },
    { icon: '🆕', value: newThisMonth.toString(), label: '本月新增' },
  ]
})

const funcItems = [
  { 
    icon: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M12 2L3 7V12C3 17.5 6.8 22.7 12 24C17.2 22.7 21 17.5 21 12V7L12 2Z" stroke="white" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
      <rect x="8" y="11" width="8" height="6" rx="1" fill="white" opacity="0.9"/>
      <circle cx="12" cy="14" r="1.5" fill="#2563eb"/>
      <path d="M10 11V9C10 7.9 10.9 7 12 7C13.1 7 14 7.9 14 9V11" stroke="white" stroke-width="1.5" stroke-linecap="round" fill="none"/>
    </svg>`, 
    title: '账户安全', 
    desc: '修改密码、两步验证', 
    color: 'linear-gradient(135deg,#2563eb 0%,#7c3aed 60%,#a855f7 100%)', 
    action: 'security' 
  },
  { 
    icon: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <circle cx="12" cy="12" r="7" stroke="white" stroke-width="1.5" fill="none"/>
      <path d="M12 2v3M12 19v3M2 12h3M19 12h3M4.9 4.9l2.1 2.1M16.9 16.9l2.1 2.1M4.9 19.1l2.1-2.1M16.9 7.1l2.1-2.1" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
      <circle cx="12" cy="12" r="3" stroke="white" stroke-width="1.5" fill="none"/>
      <circle cx="12" cy="12" r="1.5" fill="white"/>
      <rect x="6" y="19" width="12" height="2" rx="1" fill="white" opacity="0.6"/>
      <circle cx="15" cy="20" r="1.5" fill="white"/>
    </svg>`, 
    title: '系统设置', 
    desc: '模型选择、API配置', 
    color: 'linear-gradient(135deg,#06b6d4 0%,#2563eb 50%,#3b82f6 100%)', 
    action: 'settings' 
  },
  { 
    icon: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <path d="M4 4v16h16" stroke="white" stroke-width="1.5" stroke-linecap="round" fill="none"/>
      <path d="M4 8h14" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
      <path d="M4 12h12" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
      <path d="M4 16h10" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.5"/>
      <text x="16" y="18" font-size="10" fill="white" font-weight="bold" text-anchor="middle">?</text>
      <text x="20" y="8" font-size="5" fill="white" opacity="0.6" text-anchor="middle">?</text>
      <path d="M20 4l0.3 0.9 0.9 0.3-0.9 0.3-0.3 0.9-0.3-0.9-0.9-0.3 0.9-0.3Z" fill="white" opacity="0.7"/>
    </svg>`, 
    title: '帮助中心', 
    desc: '使用手册、常见问题', 
    color: 'linear-gradient(135deg,#10b981 0%,#06b6d4 50%,#22d3ee 100%)', 
    action: 'help' 
  },
  { 
    icon: `<svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
      <rect x="3" y="5" width="18" height="14" rx="2" stroke="white" stroke-width="1.5" fill="none"/>
      <rect x="3" y="5" width="18" height="4" rx="2" fill="white" opacity="0.8"/>
      <path d="M6 13h12" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
      <path d="M6 16h8" stroke="white" stroke-width="1.5" stroke-linecap="round" opacity="0.6"/>
      <circle cx="18" cy="12" r="5" fill="white" opacity="0.95"/>
      <text x="18" y="15.5" font-size="6" fill="#f59e0b" font-weight="bold" text-anchor="middle">i</text>
      <path d="M22 2l0.4 1.2 1.2 0.4-1.2 0.4-0.4 1.2-0.4-1.2-1.2-0.4 1.2-0.4Z" fill="white" opacity="0.8"/>
    </svg>`, 
    title: '关于我们', 
    desc: '版本信息、开发团队', 
    color: 'linear-gradient(135deg,#f59e0b 0%,#10b981 50%,#34d399 100%)', 
    action: 'about' 
  },
]

const aiModels = [
  { id: 'cloud', icon: '🤖', name: '云端模型', desc: '使用云端API服务' },
  { id: 'local', icon: '💻', name: '本地模型', desc: '私有化部署' },
]

// 页面加载时加载保存的配置和患者数据
onMounted(() => {
  loadSavedSettings()
  loadPatients()
})

// 从localStorage获取token
const getToken = () => {
  return localStorage.getItem('token') || localStorage.getItem('access_token')
}

// 加载患者数据
async function loadPatients() {
  try {
    const token = getToken()
    if (!token) {
      console.error('未登录或登录已过期')
      return
    }
    
    const response = await fetch(`${API_BASE_URL}/api/patients`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    const result = await response.json()
    
    if (result.success && result.patients) {
      // 转换患者数据
      const convertedPatients = result.patients
        .filter((p: any) => p.patientInfo)
        .map((p: any) => {
          const info = p.patientInfo
          return {
            id: Date.now() + Math.random(),
            name: info.patientName || '未知',
            gender: info.gender === 'male' ? '男' : (info.gender === 'female' ? '女' : '未知'),
            age: parseInt(info.age) || 0,
            phone: info.phone || '',
            diagnosis: info.preliminaryDiagnosis || '未诊断',
            status: info.status || '待处理',
            joinDate: info.createTime ? new Date(info.createTime).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
            contact: info.creator || '',
            note: info.notes || ''
          }
        })
      
      patients.value = convertedPatients
      console.log('加载患者数据成功:', patients.value.length, '个患者')
    }
  } catch (error) {
    console.error('加载患者数据失败:', error)
  }
}



// 加载保存的设置
function loadSavedSettings() {
  // 加载模型选择
  const savedModelPreference = localStorage.getItem('model_preference')
  if (savedModelPreference === 'cloud' || savedModelPreference === 'local') {
    selectedModel.value = savedModelPreference
  }
  
  // 加载API密钥模式
  const savedApiKeyMode = localStorage.getItem('api_key_mode')
  if (savedApiKeyMode === 'unified' || savedApiKeyMode === 'separate') {
    apiKeyMode.value = savedApiKeyMode
  }
  
  // 加载API密钥
  const savedApiKey = localStorage.getItem('siliconflow_api_key')
  if (savedApiKey && apiKeyMode.value === 'unified') {
    apiKey.value = savedApiKey
  }
  
  const savedVisionApiKey = localStorage.getItem('vision_api_key')
  if (savedVisionApiKey && apiKeyMode.value === 'separate') {
    visionApiKey.value = savedVisionApiKey
  }
  
  const savedLlmApiKey = localStorage.getItem('llm_api_key')
  if (savedLlmApiKey && apiKeyMode.value === 'separate') {
    llmApiKey.value = savedLlmApiKey
  }
  
  // 加载模型名称
  const savedVisionModel = localStorage.getItem('vision_model')
  if (savedVisionModel) {
    visionModel.value = savedVisionModel
  }
  
  const savedLlmModel = localStorage.getItem('llm_model')
  if (savedLlmModel) {
    llmModel.value = savedLlmModel
  }
}

function handleFuncClick(item: { action: string, title: string }) {
  if (item.action === 'settings') {
    showSettings.value = true
  } else if (item.action === 'security') {
    showSecurity.value = true
    // 清空之前的表单和消息
    passwordForm.value = {
      currentPassword: '',
      newPassword: '',
      confirmPassword: ''
    }
    passwordError.value = ''
    passwordSuccess.value = ''
  } else if (item.action === 'help') {
    showHelp.value = true
  } else if (item.action === 'about') {
    showAbout.value = true
  }
}

async function testApi() {
  if (!apiKey.value) {
    alert('请先输入API密钥')
    return
  }
  
  apiConnected.value = false
  
  try {
    // 调用后端API测试连接
    const token = localStorage.getItem('token') || localStorage.getItem('access_token')
    
    // 先保存API密钥到后端
    if (token) {
      const saveResponse = await fetch(`${API_BASE_URL}/api/config/siliconflow-api-key`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          api_key: apiKey.value,
          vision_model: 'Qwen/Qwen2.5-VL-7B-Instruct',
          llm_model: 'Qwen/Qwen2.5-32B-Instruct'
        })
      })
      
      if (!saveResponse.ok) {
        throw new Error('保存API密钥失败')
      }
    }
    
    // 测试API连接（使用后端健康检查）
    const healthResponse = await fetch(`${API_BASE_URL}/api/health`, {
      method: 'GET',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {}
    })
    
    if (healthResponse.ok) {
      const healthResult = await healthResponse.json()
      
      // 检查agent服务状态
      if (healthResult.agent_status === 'healthy' || healthResult.agent_status === 'unreachable') {
        // API配置已保存，服务状态正常
        apiConnected.value = true
        alert('API连接测试成功！\n\n✓ API密钥已保存\n✓ 后端服务正常\n✓ Agent服务状态: ' + healthResult.agent_status)
      } else {
        throw new Error('Agent服务异常')
      }
    } else {
      throw new Error('后端服务不可用')
    }
    
  } catch (error) {
    apiConnected.value = false
    console.error('API测试失败:', error)
    alert('API连接测试失败: ' + (error as Error).message)
  }
}

async function saveSettings() {
  try {
    // 保存模型选择
    localStorage.setItem('model_preference', selectedModel.value)
    
    // 保存API密钥模式
    localStorage.setItem('api_key_mode', apiKeyMode.value)
    
    // 如果选择了云端模型，保存API配置
    if (selectedModel.value === 'cloud') {
      // 如果有token，保存到后端
      const token = localStorage.getItem('token') || localStorage.getItem('access_token')
      
      if (token && (apiKey.value || (apiKeyMode.value === 'separate' && (visionApiKey.value || llmApiKey.value)))) {
        try {
          const response = await fetch(`${API_BASE_URL}/api/config/siliconflow-api-key`, {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              api_key: apiKeyMode.value === 'unified' ? apiKey.value : '',
              vision_model: visionModel.value,
              llm_model: llmModel.value
            })
          })
          
          if (response.ok) {
            console.log('API配置已保存到服务器')
          }
        } catch (error) {
          console.warn('保存API配置到服务器失败，但本地已保存:', error)
        }
      }
      
      // 保存到本地
      if (apiKeyMode.value === 'unified') {
        if (apiKey.value) {
          localStorage.setItem('siliconflow_api_key', apiKey.value)
        }
        localStorage.setItem('vision_model', visionModel.value)
        localStorage.setItem('llm_model', llmModel.value)
      } else {
        if (visionApiKey.value) {
          localStorage.setItem('vision_api_key', visionApiKey.value)
        }
        if (llmApiKey.value) {
          localStorage.setItem('llm_api_key', llmApiKey.value)
        }
        localStorage.setItem('vision_model', visionModel.value)
        localStorage.setItem('llm_model', llmModel.value)
      }
    }
    
    showSettings.value = false
    alert('设置已保存')
  } catch (error) {
    console.error('保存设置失败:', error)
    alert('保存设置失败，请重试')
  }
}

// 密码强度计算
const passwordStrength = computed(() => {
  const password = passwordForm.value.newPassword
  if (!password) {
    return { level: '', width: '0%', text: '' }
  }

  let strength = 0
  if (password.length >= 6) strength++
  if (password.length >= 8) strength++
  if (/[A-Z]/.test(password)) strength++
  if (/[0-9]/.test(password)) strength++
  if (/[^A-Za-z0-9]/.test(password)) strength++

  const levels = [
    { level: 'weak', width: '20%', text: '密码强度：弱' },
    { level: 'medium', width: '40%', text: '密码强度：中' },
    { level: 'good', width: '60%', text: '密码强度：良好' },
    { level: 'strong', width: '80%', text: '密码强度：强' },
    { level: 'very-strong', width: '100%', text: '密码强度：很强' }
  ]

  return levels[Math.min(strength, 4)]
})

// 修改密码
async function changePassword() {
  // 清除之前的消息
  passwordError.value = ''
  passwordSuccess.value = ''

  // 表单验证
  if (!passwordForm.value.currentPassword) {
    passwordError.value = '请输入当前密码'
    return
  }

  if (!passwordForm.value.newPassword) {
    passwordError.value = '请输入新密码'
    return
  }

  if (passwordForm.value.newPassword.length < 6) {
    passwordError.value = '新密码长度至少为6位'
    return
  }

  if (passwordForm.value.newPassword !== passwordForm.value.confirmPassword) {
    passwordError.value = '两次输入的新密码不一致'
    return
  }

  if (passwordForm.value.currentPassword === passwordForm.value.newPassword) {
    passwordError.value = '新密码不能与当前密码相同'
    return
  }

  try {
    isChangingPassword.value = true

    // 获取token
    const token = getToken()
    if (!token) {
      passwordError.value = '未登录或登录已过期'
      return
    }

    // 调用后端API修改密码
    const response = await fetch(`${API_BASE_URL}/api/change-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        current_password: passwordForm.value.currentPassword,
        new_password: passwordForm.value.newPassword
      })
    })

    const result = await response.json()

    if (response.ok && result.success) {
      passwordSuccess.value = '密码修改成功！请重新登录'
      
      // 清空表单
      passwordForm.value = {
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      }

      // 延迟关闭模态框并退出登录
      setTimeout(() => {
        showSecurity.value = false
        alert('密码修改成功！请使用新密码重新登录')
        authStore.logout()
        router.push('/login')
      }, 1500)
    } else {
      passwordError.value = result.message || '密码修改失败，请检查当前密码是否正确'
    }
  } catch (error) {
    console.error('修改密码失败:', error)
    passwordError.value = '修改密码失败，请稍后重试'
  } finally {
    isChangingPassword.value = false
  }
}

function handleLogout() {
  if (confirm('确认退出登录？')) {
    authStore.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.user-card {
  padding: 24px;
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 16px;
}
.user-avatar-wrap { position: relative; flex-shrink: 0; }
.user-avatar {
  width: 72px; height: 72px;
  border-radius: 50%;
  background: var(--gradient-1);
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; font-weight: 700; color: white;
}
.avatar-ring {
  position: absolute;
  inset: -3px;
  border-radius: 50%;
  border: 2px solid transparent;
  background: var(--gradient-1) border-box;
  -webkit-mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) padding-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: destination-out;
  mask-composite: exclude;
  animation: spin 4s linear infinite;
}
.user-name { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.user-role { margin-bottom: 6px; display: inline-flex; }
.user-id { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

.stats-row { display: flex; gap: 8px; margin-bottom: 16px; }
.stats-row .stat-card { text-align: center; flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 16px 12px; transition: all 0.3s ease; position: relative; overflow: hidden; }
.stat-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--border-hover); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--gradient-1); opacity: 0; transition: opacity 0.3s ease; }
.stat-card:hover::before { opacity: 1; }
.stat-icon-wrapper { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; box-shadow: var(--shadow-sm); position: relative; overflow: hidden; }
.stat-icon-wrapper::before { content: ''; position: absolute; inset: -50%; background: conic-gradient(from 0deg, transparent, rgba(255,255,255,0.3), transparent); animation: rotate 4s linear infinite; }
.stat-icon-svg { position: relative; z-index: 1; animation: pulse 2s ease infinite; }
.stat-value { font-size: 24px; font-weight: 700; background: var(--gradient-1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; }
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.05); opacity: 0.9; } }

.func-list { padding: 0; overflow: hidden; margin-bottom: 16px; }
.func-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.2s;
  border-bottom: 1px solid var(--border);
}
.func-item:last-child { border-bottom: none; }
.func-item:hover { background: rgba(255,255,255,0.04); }
.func-item-left { display: flex; align-items: center; gap: 12px; }
.func-item-icon { 
  width: 36px; 
  height: 36px; 
  border-radius: 10px; 
  display: flex; 
  align-items: center; 
  justify-content: center; 
  font-size: 18px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}
.func-item-icon svg {
  width: 100%;
  height: 100%;
}
.func-item-title { font-size: 14px; font-weight: 600; color: var(--text-primary); }
.func-item-desc { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }
.func-item-arrow { font-size: 20px; color: var(--text-muted); }

.logout-btn { width: 100%; padding: 14px; font-size: 15px; }
.logout-btn:hover { background: rgba(239,68,68,0.1); }

/* Modal shared */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7); backdrop-filter: blur(4px);
  display: flex; align-items: flex-end; justify-content: center;
  z-index: 1000;
}
.modal-card {
  width: 100%; max-width: 480px;
  background: var(--bg-card);
  border-radius: 20px 20px 0 0;
  border: 1px solid var(--border);
  max-height: 85vh; overflow-y: auto;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 20px 0;
}
.modal-header h3 { font-size: 18px; font-weight: 600; }
.modal-body { padding: 16px 20px; display: flex; flex-direction: column; gap: 16px; }
.modal-footer { display: flex; gap: 10px; padding: 0 20px 20px; }
.modal-footer .btn { flex: 1; }

.settings-title { font-size: 13px; font-weight: 600; color: var(--text-secondary); margin-bottom: 10px; }
.settings-desc { font-size: 12px; color: var(--text-muted); margin-bottom: 12px; }
.model-options { display: flex; flex-direction: column; gap: 8px; }
.model-option {
  display: flex; align-items: center; gap: 12px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}
.model-option.active { border-color: var(--primary); background: rgba(37,99,235,0.1); }
.model-option:hover { border-color: var(--primary); }
.model-icon { font-size: 22px; }
.model-info { flex: 1; }
.model-name { font-size: 14px; font-weight: 600; }
.model-desc { font-size: 12px; color: var(--text-secondary); }
.model-check { color: var(--success); font-weight: bold; }

.api-config-section { margin-top: 16px; }
.api-config-header { margin-bottom: 12px; }
.api-config-title { font-size: 13px; font-weight: 600; }
.api-config-desc { font-size: 12px; color: var(--text-muted); margin-top: 2px; }

.api-mode-selector { display: flex; gap: 8px; margin-bottom: 12px; }
.api-mode-option {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  border: 1px solid var(--border);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.api-mode-option.active { border-color: var(--primary); background: rgba(37,99,235,0.1); }
.api-mode-icon { font-size: 20px; }
.api-mode-info { flex: 1; }
.api-mode-name { font-size: 13px; font-weight: 600; }
.api-mode-desc { font-size: 11px; color: var(--text-secondary); }

.api-input-group { display: flex; flex-direction: column; gap: 4px; margin-bottom: 12px; }
.api-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; display: flex; align-items: center; gap: 6px; }
.api-input { 
  padding: 10px; 
  background: var(--bg-input); 
  border: 1px solid var(--border); 
  border-radius: 6px; 
  font-size: 13px;
  color: var(--text-primary);
  transition: all 0.2s;
}
.api-input:hover { border-color: var(--border-hover); }
.api-input:focus { outline: none; border-color: var(--primary); }

.api-config-hint {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 12px;
  border-radius: 8px;
  background: rgba(245, 158, 11, 0.05);
  border: 1px solid rgba(245, 158, 11, 0.1);
  font-size: 11px;
  color: var(--text-muted);
  margin-top: 8px;
}

.api-status {
  display: flex; align-items: center; justify-content: space-between;
  margin-top: 10px; padding: 8px 12px;
  border-radius: 8px;
  font-size: 13px;
}
.api-status.connected { background: rgba(16,185,129,0.1); color: var(--success); border: 1px solid rgba(16,185,129,0.2); }
.api-status.disconnected { background: rgba(255,255,255,0.04); color: var(--text-muted); border: 1px solid var(--border); }

/* Security Modal Styles */
.security-info-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 20px;
}

.security-info-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 14px;
  background: var(--bg-input);
  border-radius: 10px;
  border: 1px solid var(--border);
}

.security-info-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  background: rgba(37, 99, 235, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.security-info-content {
  flex: 1;
  min-width: 0;
}

.security-info-title {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.security-info-value {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.security-divider {
  height: 1px;
  background: var(--border);
  margin: 20px 0;
}

.security-section {
  margin-bottom: 16px;
}

.security-section-title {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.security-section-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 16px;
}

.security-section .form-group {
  margin-bottom: 14px;
}

.security-section .form-label {
  font-size: 13px;
  color: var(--text-secondary);
  font-weight: 500;
  margin-bottom: 6px;
  display: block;
}

.security-section .input {
  width: 100%;
  padding: 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  font-size: 14px;
  color: var(--text-primary);
  transition: all 0.2s;
}

.security-section .input:hover {
  border-color: var(--border-hover);
}

.security-section .input:focus {
  outline: none;
  border-color: var(--primary);
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
}

.password-strength {
  margin-top: 12px;
}

.strength-bar {
  height: 6px;
  background: var(--bg-input);
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 6px;
}

.strength-fill {
  height: 100%;
  transition: all 0.3s ease;
  border-radius: 3px;
}

.strength-fill.weak {
  background: linear-gradient(90deg, #ef4444, #f97316);
}

.strength-fill.medium {
  background: linear-gradient(90deg, #f97316, #eab308);
}

.strength-fill.good {
  background: linear-gradient(90deg, #eab308, #84cc16);
}

.strength-fill.strong {
  background: linear-gradient(90deg, #84cc16, #22c55e);
}

.strength-fill.very-strong {
  background: linear-gradient(90deg, #22c55e, #10b981);
}

.strength-text {
  font-size: 12px;
  color: var(--text-muted);
}

.error-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(239, 68, 68, 0.1);
  border: 1px solid rgba(239, 68, 68, 0.2);
  border-radius: 8px;
  color: #ef4444;
  font-size: 13px;
  margin-top: 12px;
}

.success-message {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px;
  background: rgba(16, 185, 129, 0.1);
  border: 1px solid rgba(16, 185, 129, 0.2);
  border-radius: 8px;
  color: #10b981;
  font-size: 13px;
  margin-top: 12px;
}
</style>