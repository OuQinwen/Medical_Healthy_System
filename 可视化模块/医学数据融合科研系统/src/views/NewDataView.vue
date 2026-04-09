<template>
  <div>
    <div class="page-topbar">
      <h1>数据处理</h1>
      <button class="btn btn-icon" title="帮助">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </button>
    </div>

    <div class="page">
      <!-- OCR Scanner Header -->
      <div class="scanner-header gradient-border">
        <div class="scanner-content">
          <div class="scanner-icon-wrap">
            <svg class="scanner-svg" width="48" height="48" viewBox="0 0 48 48" fill="none">
              <rect x="4" y="4" width="12" height="4" rx="1" fill="#3b82f6"/>
              <rect x="4" y="4" width="4" height="12" rx="1" fill="#3b82f6"/>
              <rect x="32" y="4" width="12" height="4" rx="1" fill="#3b82f6"/>
              <rect x="40" y="4" width="4" height="12" rx="1" fill="#3b82f6"/>
              <rect x="4" y="40" width="12" height="4" rx="1" fill="#7c3aed"/>
              <rect x="4" y="32" width="4" height="12" rx="1" fill="#7c3aed"/>
              <rect x="32" y="40" width="12" height="4" rx="1" fill="#7c3aed"/>
              <rect x="40" y="32" width="4" height="12" rx="1" fill="#7c3aed"/>
            </svg>
            <div class="scan-line"></div>
          </div>
          <div>
            <h3>OCR 智能识别</h3>
            <p>上传医学影像或文档，AI自动提取结构化数据</p>
          </div>
        </div>
      </div>

      <!-- Function Cards -->
      <div class="func-grid">
        <div class="func-card gradient-border" :class="{active: activeFunc === 'ocr'}" @click="activeFunc = 'ocr'">
          <div class="func-icon icon-ocr">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <!-- 文档 -->
              <rect x="3" y="3" width="14" height="18" rx="1.5" stroke="white" stroke-width="1.5" fill="none"/>
              <!-- 文档上的三条文字线 -->
              <path d="M6 8h8" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M6 12h8" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M6 16h5" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <!-- 放大镜 -->
              <circle cx="17" cy="17" r="4.5" stroke="white" stroke-width="1.5" fill="none"/>
              <path d="M20.5 20.5L23 23" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="func-info">
            <h4>OCR识别</h4>
            <p>图像文字提取</p>
          </div>
          <div v-if="activeFunc==='ocr'" class="func-check">✓</div>
        </div>
        <div class="func-card gradient-border" :class="{active: activeFunc === 'clean'}" @click="activeFunc = 'clean'">
          <div class="func-icon icon-clean">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <!-- 刷子柄 -->
              <path d="M6 4L10 16" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <!-- 刷子头 -->
              <path d="M3 16L10 14L17 16L14 18L6 18Z" stroke="white" stroke-width="1.5" fill="none" stroke-linejoin="round"/>
              <!-- 刷子毛 -->
              <path d="M4 18v3" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M7 18v3" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M10 18v3" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M13 18v2" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <!-- 散落的灰尘颗粒 -->
              <circle cx="18" cy="5" r="1" fill="white"/>
              <circle cx="20" cy="8" r="1.5" fill="white"/>
              <circle cx="19" cy="12" r="1" fill="white"/>
              <circle cx="22" cy="6" r="1" fill="white"/>
              <circle cx="17" cy="9" r="0.75" fill="white"/>
              <circle cx="21" cy="10" r="0.75" fill="white"/>
            </svg>
          </div>
          <div class="func-info">
            <h4>数据清洗</h4>
            <p>质控规范化</p>
          </div>
          <div v-if="activeFunc==='clean'" class="func-check">✓</div>
        </div>
      </div>

      <!-- Input Area -->
      <div class="card input-section">
        <div class="section-header">
          <div class="section-icon icon-text">
            <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
              <!-- 输入框 -->
              <rect x="2" y="5" width="20" height="14" rx="2" stroke="white" stroke-width="1.5" fill="none"/>
              <!-- 文字行 -->
              <path d="M6 9h8" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M6 12h6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <path d="M6 15h10" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
              <!-- 光标 -->
              <path d="M18 9v6" stroke="white" stroke-width="1.5" stroke-linecap="round"/>
            </svg>
          </div>
          <h2>文本输入</h2>
        </div>
        
        <!-- 使用DataInput组件，与原DataView保持一致 -->
        <DataInput @sendMessage="handleMessage" />

        <!-- 上传状态显示 -->
        <div v-if="uploadStatus" class="card-status" :class="uploadStatus.includes('成功') ? 'success' : uploadStatus.includes('失败') || uploadStatus.includes('错误') ? 'error' : 'loading'">
          {{ uploadStatus }}
        </div>
      </div>
      
      <!-- OCR结果可展开/折叠区域 -->
      <div v-if="uploadResult" class="result-section">
        <!-- 优先使用 AgentResultDisplay 展示 agent 结果 -->
        <AgentResultDisplay 
          v-if="uploadResult.agent_results"
          :agent-results="uploadResult.agent_results"
        />
        <!-- 如果没有 agent_results，使用原有的 NewOCRResult -->
        <NewOCRResult 
          v-else
          :data="uploadResult" 
          :status="uploadStatus.includes('成功') ? 'success' : uploadStatus.includes('失败') || uploadStatus.includes('错误') ? 'error' : 'warning'"
          :subtitle="uploadResult.message || 'OCR处理完成'"
        />
      </div>
    </div>
    
    <!-- 使用新版UI的LoadingOverLay组件 -->
    <LoadingOverLay
      :visible="isLoading"
      :message="loadingMessage"
      :sub-message="'AI 模型处理需要一些时间，请耐心等待...'"
      :progress="loadingProgress"
      :show-progress="true"
      :steps="[
        '正在上传您的文件...',
        '文件上传完成',
        '正在智能识别图片内容...',
        '正在提取关键信息...',
        '正在整理数据格式...',
        '即将完成...'
      ]"
      :current-step="Math.floor(loadingProgress / 20)"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import DataInput from '../components/DataInput.vue'
import NewOCRResult from '../components/NewOCRResult.vue'
import LoadingOverLay from '../components/LoadingOverLay.vue'
import AgentResultDisplay from '../components/AgentResultDisplay.vue'

const API_BASE_URL = 'http://localhost:8000'

const uploadStatus = ref('')
const uploadResult = ref<any>(null)
const isLoading = ref(false)
const loadingProgress = ref(0)
const loadingMessage = ref('')
const showResult = ref(true) // 控制结果显示的展开/折叠

// 模型类型状态（从 localStorage 加载）
const modelType = ref<'cloud' | 'local'>('cloud')

// 从 localStorage 加载模型选择状态
const loadModelPreference = () => {
  const modelPreference = localStorage.getItem('model_preference')
  if (modelPreference === 'cloud' || modelPreference === 'local') {
    modelType.value = modelPreference
  }
}

// 从 localStorage 获取 token，与路由守卫保持一致
const getToken = () => {
  return localStorage.getItem('token') || localStorage.getItem('access_token')
}

// 页面加载时加载模型选择
loadModelPreference()

// 切换结果显示的展开/折叠
const toggleResult = () => {
  showResult.value = !showResult.value
}

// 模拟加载进度
const startProgressSimulation = () => {
  loadingProgress.value = 0
  loadingMessage.value = '正在上传您的文件...'
  
  const messages = [
    '正在上传您的文件...',
    '文件上传完成',
    '正在智能识别图片内容...',
    '正在提取关键信息...',
    '正在整理数据格式...',
    '即将完成...'
  ]
  
  let step = 0
  const interval = setInterval(() => {
    if (step < messages.length) {
      loadingMessage.value = messages[step]
      loadingProgress.value = Math.min((step + 1) * 15, 95)
      step++
    } else {
      clearInterval(interval)
    }
  }, 2000)
  
  return interval
}

// 处理消息发送（与原DataView完全相同）
const handleMessage = async (message: string, files: File[]) => {
  isLoading.value = true
  uploadStatus.value = ''
  uploadResult.value = null

  // 启动进度模拟
  const progressInterval = startProgressSimulation()

  try {
    // 构建 FormData
    const formData = new FormData()
    
    // 添加消息
    if (message.trim()) {
      formData.append('message', message)
    }
    
    // 添加文件
    if (files.length > 0) {
      files.forEach((file) => {
        formData.append('files', file)
      })
    }
    
    // 添加模型类型
    formData.append('model_type', modelType.value)

    // 发送到后端 API
    const token = getToken()
    const response = await fetch(`${API_BASE_URL}/api/upload`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    })

    const result = await response.json()

    // 清除进度模拟
    clearInterval(progressInterval)
    loadingProgress.value = 100

    if (response.ok && result.success) {
      loadingMessage.value = '处理完成！'
      setTimeout(() => {
        isLoading.value = false
        // 检查是否有 agent 警告信息
        if (result.agent_warning) {
          uploadStatus.value = '⚠️ ' + result.agent_warning
        } else {
          uploadStatus.value = '✅ 上传成功！'
        }
        uploadResult.value = result
        console.log('上传成功:', result)
        if (result.agent_warning) {
          console.warn('Agent 警告:', result.agent_warning)
        }
      }, 500)
    } else {
      loadingMessage.value = '处理失败'
      setTimeout(() => {
        isLoading.value = false
        // 使用更友好的错误提示
        const errorMsg = result.message || '未知错误'
        if (errorMsg.includes('网络') || errorMsg.includes('连接')) {
          uploadStatus.value = '❌ 网络连接失败，请检查网络后重试'
        } else if (errorMsg.includes('超时')) {
          uploadStatus.value = '❌ 处理超时，请稍后重试'
        } else if (errorMsg.includes('认证') || errorMsg.includes('登录')) {
          uploadStatus.value = '❌ 登录已过期，请重新登录'
        } else {
          uploadStatus.value = '❌ 处理失败，请稍后重试'
        }
        console.error('上传失败:', result)
      }, 500)
    }
  } catch (error) {
    clearInterval(progressInterval)
    loadingMessage.value = '网络错误'
    setTimeout(() => {
      isLoading.value = false
      // 使用更友好的错误提示
      const errorMsg = (error as Error).message
      if (errorMsg.includes('fetch') || errorMsg.includes('network')) {
        uploadStatus.value = '❌ 网络连接失败，请检查网络后重试'
      } else if (errorMsg.includes('timeout')) {
        uploadStatus.value = '❌ 请求超时，请稍后重试'
      } else {
        uploadStatus.value = '❌ 系统繁忙，请稍后重试'
      }
      console.error('请求失败:', error)
    }, 500)
  }
}
</script>

<style scoped>
.scanner-header {
  padding: 20px;
  margin-bottom: 16px;
  overflow: hidden;
  position: relative;
}
.scanner-content { display: flex; align-items: center; gap: 16px; }
.scanner-icon-wrap { position: relative; width: 48px; height: 48px; flex-shrink: 0; }
.scanner-svg { animation: pulse 2s ease infinite; }
.scan-line {
  position: absolute;
  left: 0; right: 0;
  height: 2px;
  background: linear-gradient(90deg, transparent, #3b82f6, transparent);
  top: 0;
  animation: scanLine 2s ease-in-out infinite;
}
@keyframes scanLine {
  0%, 100% { top: 0; opacity: 0; }
  10%, 90% { opacity: 1; }
  50% { top: 46px; }
}
.scanner-content h3 { font-size: 16px; font-weight: 600; color: var(--text-primary); }
.scanner-content p { font-size: 12px; color: var(--text-secondary); margin-top: 2px; }

.func-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 12px; margin-bottom: 16px; }
.func-card {
  padding: 14px;
  display: flex;
  align-items: center;
  gap: 10px;
  cursor: pointer;
  transition: all 0.2s;
  border-radius: var(--radius-md);
}
.func-card:hover { transform: translateY(-2px); }
.func-card.active { background: rgba(37,99,235,0.15); }
.func-icon { width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center; justify-content: center; }

/* 图标样式 */
.icon-ocr {
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 60%, #a855f7 100%);
  box-shadow: 0 4px 20px rgba(59, 130, 246, 0.4);
}

.icon-clean {
  background: linear-gradient(135deg, #06b6d4 0%, #2563eb 50%, #1e40af 100%);
  box-shadow: 0 4px 20px rgba(6, 182, 212, 0.4);
}

.icon-text {
  background: linear-gradient(135deg, #3b82f6 0%, #7c3aed 100%);
  box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
}
.func-info h4 { font-size: 13px; font-weight: 600; color: var(--text-primary); }
.func-info p { font-size: 11px; color: var(--text-secondary); }
.func-check { margin-left: auto; color: var(--success); font-weight: bold; }

.text-area { resize: vertical; min-height: 100px; }
.action-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 10px;
  margin-top: 12px;
}

.loading-steps { margin-bottom: 16px; }
.steps-header {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}
.steps-list { margin-top: 12px; display: flex; flex-direction: column; gap: 8px; }
.step-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  color: var(--text-muted);
  transition: color 0.3s;
}
.step-item.done { color: var(--success); }
.step-item.active { color: var(--primary-light); font-weight: 500; }
.step-dot { font-size: 14px; width: 16px; text-align: center; }

.result-header { display: flex; align-items: center; justify-content: space-between; cursor: pointer; }
.result-meta { display: flex; align-items: center; gap: 8px; }
.expand-icon { color: var(--text-muted); font-size: 12px; }
.result-fields { display: flex; flex-direction: column; gap: 8px; }
.result-field {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: var(--bg-input);
  border-radius: 6px;
  font-size: 13px;
}
.field-key { color: var(--text-secondary); }
.field-val { color: var(--text-primary); font-weight: 500; }

/* 结果区域 */
.card-result-wrapper {
  margin-top: 16px;
  border: 1px solid var(--border);
  border-radius: 12px;
  overflow: hidden;
}

.result-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px;
  background: linear-gradient(135deg, var(--bg-card), var(--bg));
  cursor: pointer;
  transition: all 0.3s ease;
  user-select: none;
}

.result-toggle:hover {
  background: linear-gradient(135deg, rgba(37,99,235,0.1), var(--bg-card));
}

.result-toggle-left {
  flex: 1;
}

.result-toggle-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.result-toggle-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
}

.result-toggle-icon {
  width: 32px;
  height: 32px;
  background: var(--bg);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--primary-light);
  transition: transform 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.result-toggle-icon.expanded {
  transform: rotate(180deg);
}

.result-content {
  padding: 16px;
  background: var(--bg);
  border-top: 1px solid var(--border);
  animation: slideDown 0.3s ease;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.card-result {
  padding: 16px;
  background-color: var(--bg-input);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.card-result .result-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
  color: var(--text-primary);
}

.card-result .result-message {
  margin-bottom: 12px;
  padding: 8px;
  background-color: var(--bg-card);
  border-radius: 6px;
  border-left: 4px solid var(--primary-light);
  font-size: 14px;
}

.card-result .result-files {
  margin-bottom: 12px;
}

.card-result .file-result-item {
  padding: 6px 10px;
  margin: 4px 0;
  background-color: var(--bg-card);
  border-radius: 4px;
  border: 1px solid var(--border);
  font-size: 13px;
}

.card-result .result-time {
  color: var(--text-muted);
  font-size: 11px;
  margin-top: 8px;
}

@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>