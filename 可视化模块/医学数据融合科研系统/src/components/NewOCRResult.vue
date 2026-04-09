<template>
  <div class="ocr-result-card gradient-border animate-slide-up">
    <div class="result-header">
      <div class="header-left">
        <div class="result-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </div>
        <div class="header-text">
          <h3 class="result-title">OCR 识别结果</h3>
          <p class="result-subtitle">{{ subtitle }}</p>
        </div>
      </div>
      <div class="header-right">
        <span class="badge" :class="statusBadgeClass">{{ statusText }}</span>
        <button class="btn-icon" @click="toggleExpand" :title="expandInfo ? '收起' : '展开'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 15l-6-6-6 6"/>
          </svg>
        </button>
      </div>
    </div>

    <Transition name="collapse">
      <div v-if="expandInfo" class="result-content">
        <div class="divider"></div>
        
        <!-- 基本信息 -->
        <div class="info-section">
          <div class="section-header">
            <div class="section-icon">📋</div>
            <h4>基本信息</h4>
          </div>
          <div class="info-grid">
            <div v-for="(item, key) in basicInfo" :key="key" class="info-item">
              <span class="info-label">{{ item.label }}</span>
              <span class="info-value">{{ item.value }}</span>
            </div>
          </div>
        </div>

        <!-- 医学数据 -->
        <div v-if="medicalData.length > 0" class="info-section">
          <div class="section-header">
            <div class="section-icon">🏥</div>
            <h4>医学数据</h4>
          </div>
          <div class="medical-grid">
            <div v-for="(item, index) in medicalData" :key="index" class="medical-item">
              <div class="medical-icon">{{ item.icon }}</div>
              <div class="medical-info">
                <span class="medical-label">{{ item.label }}</span>
                <span class="medical-value">{{ item.value }}</span>
              </div>
              <span v-if="item.status" class="badge" :class="item.badgeClass">{{ item.status }}</span>
            </div>
          </div>
        </div>

        <!-- 原始文本 -->
        <div v-if="rawText" class="info-section">
          <div class="section-header">
            <div class="section-icon">📝</div>
            <h4>原始文本</h4>
          </div>
          <div class="raw-text-box">
            <pre class="raw-text-content">{{ rawText }}</pre>
            <button class="btn btn-sm btn-secondary" @click="copyRawText">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9l2-3"/>
              </svg>
              复制
            </button>
          </div>
        </div>

        <!-- 操作按钮 -->
        <div class="action-section">
          <div class="action-row">
            <button class="btn btn-sm" @click="exportResult">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              导出结果
            </button>
            <button class="btn btn-sm btn-secondary" @click="saveToPatient">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/>
                <polyline points="17 21 17 13 12 13 13 17"/>
                <polyline points="7 3 7 8 12 13 17 3"/>
              </svg>
              保存到患者档案
            </button>
            <button class="btn btn-sm btn-secondary" @click="reprocess">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="23 4 23 10 17 10"/>
                <polyline points="1 20 1 8 7 14"/>
                <path d="M20.49 9A9 9 0 0 0 5.64 5.64l1.27 1.27m4.16 4.16l1.27 1.27m1.27-4.16l-4.16-4.16m-1.27 4.16l1.27 1.27"/>
              </svg>
              重新识别
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

interface Props {
  data: any
  status?: 'success' | 'warning' | 'error'
  subtitle?: string
}

const props = withDefaults(defineProps<Props>(), {
  status: 'success',
  subtitle: 'AI智能识别完成'
})

const expandInfo = ref(true)

const statusBadgeClass = computed(() => {
  switch (props.status) {
    case 'success': return 'badge-green'
    case 'warning': return 'badge-yellow'
    case 'error': return 'badge-red'
    default: return 'badge-blue'
  }
})

const statusText = computed(() => {
  switch (props.status) {
    case 'success': return '成功'
    case 'warning': return '警告'
    case 'error': return '失败'
    default: return '处理中'
  }
})

// 提取基本信息
const basicInfo = computed(() => {
  if (!props.data) return []
  
  const info: { label: string; value: string }[] = []
  
  // 患者信息
  if (props.data.patient_name) {
    info.push({ label: '患者姓名', value: props.data.patient_name })
  }
  if (props.data.gender) {
    info.push({ label: '性别', value: props.data.gender })
  }
  if (props.data.age) {
    info.push({ label: '年龄', value: props.data.age })
  }
  if (props.data.patient_id) {
    info.push({ label: '身份证号', value: props.data.patient_id })
  }
  if (props.data.phone) {
    info.push({ label: '联系电话', value: props.data.phone })
  }
  if (props.data.visit_date) {
    info.push({ label: '就诊日期', value: props.data.visit_date })
  }
  if (props.data.doctor) {
    info.push({ label: '主治医师', value: props.data.doctor })
  }
  
  return info
})

// 提取医学数据
const medicalData = computed(() => {
  if (!props.data) return []
  
  const medical: { icon: string; label: string; value: string; status?: string; badgeClass?: string }[] = []
  
  // 诊断信息
  if (props.data.diagnosis) {
    medical.push({
      icon: '🩺',
      label: '诊断结果',
      value: props.data.diagnosis,
      status: '已确认',
      badgeClass: 'badge-green'
    })
  }
  
  // 检查结果
  if (props.data.lab_results) {
    Object.entries(props.data.lab_results).forEach(([key, value]: [string, any]) => {
      medical.push({
        icon: '🔬',
        label: key,
        value: value.value || value,
        status: value.status || '正常',
        badgeClass: value.badgeClass || (value.status === '异常' ? 'badge-red' : 'badge-green')
      })
    })
  }
  
  // 其他医学指标
  if (props.data.vitals) {
    Object.entries(props.data.vitals).forEach(([key, value]: [string, any]) => {
      medical.push({
        icon: '❤️',
        label: key,
        value: value.value || value,
        status: value.status || '正常',
        badgeClass: value.badgeClass || (value.status === '异常' ? 'badge-red' : 'badge-green')
      })
    })
  }
  
  return medical
})

// 原始文本
const rawText = computed(() => {
  return props.data?.raw_text || ''
})

function toggleExpand() {
  expandInfo.value = !expandInfo.value
}

function copyRawText() {
  if (rawText.value) {
    navigator.clipboard.writeText(rawText.value)
    alert('已复制到剪贴板')
  }
}

function exportResult() {
  alert('导出功能开发中')
}

function saveToPatient() {
  alert('保存到患者档案功能开发中')
}

function reprocess() {
  alert('重新识别功能开发中')
}
</script>

<style scoped>
.ocr-result-card {
  padding: 20px;
  margin-bottom: 16px;
  overflow: hidden;
  position: relative;
}

.result-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.result-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: var(--gradient-1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  box-shadow: var(--shadow-sm);
}

.header-text {
  flex: 1;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 2px;
}

.result-subtitle {
  font-size: 12px;
  color: var(--text-secondary);
}

.header-right {
  display: flex;
  align-items: center;
  gap: 8px;
}

.result-content {
  animation: slideDown 0.3s ease;
}

.info-section {
  margin-bottom: 16px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.section-icon {
  font-size: 20px;
}

.section-header h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
  padding: 10px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.2s;
}

.info-item:hover {
  border-color: var(--border-hover);
}

.info-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.info-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.medical-grid {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.medical-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.2s;
}

.medical-item:hover {
  border-color: var(--border-hover);
}

.medical-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.medical-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.medical-label {
  font-size: 11px;
  color: var(--text-secondary);
  font-weight: 500;
}

.medical-value {
  font-size: 13px;
  color: var(--text-primary);
  font-weight: 500;
}

.raw-text-box {
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  position: relative;
}

.raw-text-content {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  color: var(--text-secondary);
  white-space: pre-wrap;
  word-break: break-all;
  margin: 0;
  line-height: 1.5;
}

.action-section {
  margin-top: 16px;
}

.action-row {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.btn-icon {
  padding: 8px;
  border-radius: 8px;
  background: rgba(255,255,255,0.06);
  color: var(--text-secondary);
  border: 1px solid var(--border);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255,255,255,0.1);
  color: var(--text-primary);
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

.animate-slide-up {
  animation: slideUp 0.4s ease forwards;
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
</style>