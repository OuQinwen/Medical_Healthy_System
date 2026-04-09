<script setup lang="ts">
/**
 * AgentResultDisplay.vue - Agent 结果展示组件（新版 UI 风格）
 * 
 * 功能说明：
 * - 展示全量 Excel 数据下载按钮
 * - 展示按输入字段提取的对应数据
 * - 展示结构化原始全量数据
 * - 使用新版深色主题 UI 风格
 */

import { ref, computed } from 'vue'

interface ExtractedData {
  [key: string]: any
}

interface FileResult {
  filename: string
  success: boolean
  extracted_data?: ExtractedData
  full_data_json?: {
    raw_text: string
    item_count: number
    structured_data: any[]
  }
  excel_filename?: string
  excel_download_url?: string
  error?: string
}

interface AgentResults {
  success: boolean
  message: string
  results: FileResult[]
}

const props = defineProps<{
  agentResults: AgentResults
}>()

// 当前激活的标签页
const activeTab = ref<'extracted' | 'full' | 'download'>('extracted')

// 当前选中的文件结果索引
const selectedFileIndex = ref(0)
const expandResult = ref(true)

// 获取当前选中的文件结果
const currentFileResult = computed(() => {
  if (!props.agentResults || !props.agentResults.results) {
    return null
  }
  return props.agentResults.results[selectedFileIndex.value] || null
})

// 切换文件
const selectFile = (index: number) => {
  selectedFileIndex.value = index
}

// 切换标签页
const switchTab = (tab: 'extracted' | 'full' | 'download') => {
  activeTab.value = tab
}

// 切换结果展开/折叠
const toggleResult = () => {
  expandResult.value = !expandResult.value
}

// 下载 Excel 文件
const downloadExcel = (downloadUrl: string, filename: string) => {
  window.open(`http://localhost:8001${downloadUrl}`, '_blank')
}

// 复制到剪贴板
const copyToClipboard = (text: string) => {
  navigator.clipboard.writeText(text)
  alert('已复制到剪贴板')
}

// 格式化 JSON 数据用于显示
const formatJSON = (data: any) => {
  return JSON.stringify(data, null, 2)
}
</script>

<template>
  <div v-if="agentResults && agentResults.results && agentResults.results.length > 0" class="agent-result-card gradient-border animate-slide-up">
    <div class="result-header">
      <div class="header-left">
        <div class="result-icon">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
        </div>
        <div class="header-text">
          <h3 class="result-title">OCR 处理结果</h3>
          <p class="result-subtitle">{{ agentResults.message || 'AI 智能识别完成' }}</p>
        </div>
      </div>
      <div class="header-right">
        <button class="btn-icon" @click="toggleResult" :title="expandResult ? '收起' : '展开'">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 15l-6-6-6 6"/>
          </svg>
        </button>
      </div>
    </div>

    <Transition name="collapse">
      <div v-if="expandResult" class="result-content">
        <div class="divider"></div>
        
        <!-- 文件选择器（如果有多个文件） -->
        <div v-if="agentResults.results.length > 1" class="file-selector">
          <div class="section-header">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"/>
            </svg>
            <h4>选择文件</h4>
          </div>
          <div class="file-buttons">
            <button
              v-for="(result, index) in agentResults.results"
              :key="index"
              :class="['file-btn', { active: selectedFileIndex === index }]"
              @click="selectFile(index)"
            >
              {{ result.filename }}
            </button>
          </div>
        </div>

        <!-- 当前文件信息 -->
        <div v-if="currentFileResult" class="current-file-info">
          <span class="file-info-label">当前文件：</span>
          <span class="file-info-name">{{ currentFileResult.filename }}</span>
          <span v-if="!currentFileResult.success" class="file-info-error">
            (处理失败: {{ currentFileResult.error }})
          </span>
        </div>

        <!-- 标签页导航 -->
        <div v-if="currentFileResult && currentFileResult.success" class="tab-navigation">
          <button
            :class="['tab-btn', { active: activeTab === 'extracted' }]"
            @click="switchTab('extracted')"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
              <polyline points="14 2 14 8 20 8"/>
              <line x1="16" y1="13" x2="8" y2="13"/>
              <line x1="16" y1="17" x2="8" y2="17"/>
              <polyline points="10 9 9 9 8 9"/>
            </svg>
            提取字段
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'full' }]"
            @click="switchTab('full')"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
            全量数据
          </button>
          <button
            :class="['tab-btn', { active: activeTab === 'download' }]"
            @click="switchTab('download')"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
              <polyline points="7 10 12 15 17 10"/>
              <line x1="12" y1="15" x2="12" y2="3"/>
            </svg>
            Excel 下载
          </button>
        </div>

        <!-- 标签页内容 -->
        <div v-if="currentFileResult && currentFileResult.success" class="tab-content">
          <!-- 提取字段数据 -->
          <div v-if="activeTab === 'extracted'" class="tab-panel">
            <div v-if="currentFileResult.extracted_data && Object.keys(currentFileResult.extracted_data).length > 0" class="extracted-data">
              <div class="section-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <circle cx="12" cy="12" r="10"/>
                  <line x1="12" y1="8" x2="12" y2="12"/>
                  <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <h4>提取的字段数据</h4>
              </div>
              <div class="data-grid">
                <div
                  v-for="(value, key) in currentFileResult.extracted_data"
                  :key="key"
                  class="data-item"
                >
                  <span class="data-key">{{ key }}</span>
                  <span class="data-value">{{ value }}</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-result">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity: 0.3; margin-bottom: 12px;">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                <polyline points="14 2 14 8 20 8"/>
              </svg>
              <p>未提取到字段数据</p>
              <p class="hint">提示：可以指定需要提取的字段</p>
            </div>
          </div>

          <!-- 结构化全量数据 -->
          <div v-if="activeTab === 'full'" class="tab-panel">
            <div v-if="currentFileResult.full_data_json" class="full-data">
              <div class="section-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                  <line x1="8" y1="21" x2="16" y2="21"/>
                  <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                <h4>结构化全量数据</h4>
              </div>
              
              <div class="data-summary">
                <div class="summary-item">
                  <span class="summary-label">原始文本长度：</span>
                  <span class="summary-value">{{ currentFileResult.full_data_json.raw_text?.length || 0 }} 字符</span>
                </div>
                <div class="summary-item">
                  <span class="summary-label">数据项数：</span>
                  <span class="summary-value">{{ currentFileResult.full_data_json.item_count || 0 }} 项</span>
                </div>
              </div>

              <div v-if="currentFileResult.full_data_json.structured_data && currentFileResult.full_data_json.structured_data.length > 0" class="structured-data-list">
                <h5 class="list-title">结构化数据列表：</h5>
                <div
                  v-for="(item, index) in currentFileResult.full_data_json.structured_data"
                  :key="index"
                  class="structured-data-item"
                >
                  <pre class="json-display">{{ formatJSON(item) }}</pre>
                </div>
              </div>

              <div v-if="currentFileResult.full_data_json.raw_text" class="raw-text">
                <div class="raw-text-header">
                  <h5 class="list-title">原始文本：</h5>
                  <button class="btn btn-sm btn-secondary" @click="copyToClipboard(currentFileResult.full_data_json.raw_text)">
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                      <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9l2-3"/>
                    </svg>
                    复制
                  </button>
                </div>
                <div class="raw-text-content">{{ currentFileResult.full_data_json.raw_text }}</div>
              </div>
            </div>
            <div v-else class="empty-result">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity: 0.3; margin-bottom: 12px;">
                <rect x="2" y="3" width="20" height="14" rx="2" ry="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
              <p>未获取到全量数据</p>
            </div>
          </div>

          <!-- Excel 下载 -->
          <div v-if="activeTab === 'download'" class="tab-panel">
            <div v-if="currentFileResult.excel_filename && currentFileResult.excel_download_url" class="download-section">
              <div class="section-header">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                  <polyline points="7 10 12 15 17 10"/>
                  <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                <h4>Excel 文件下载</h4>
              </div>
              <div class="download-card">
                <div class="download-info">
                  <div class="download-icon-wrapper">
                    <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                      <rect x="8" y="8" width="32" height="36" rx="4" fill="none" stroke="#10b981" stroke-width="2"/>
                      <line x1="16" y1="20" x2="32" y2="20" stroke="#10b981" stroke-width="2"/>
                      <line x1="16" y1="28" x2="28" y2="28" stroke="#10b981" stroke-width="2"/>
                      <line x1="16" y1="36" x2="24" y2="36" stroke="#10b981" stroke-width="2"/>
                    </svg>
                  </div>
                  <div class="download-details">
                    <div class="download-filename">{{ currentFileResult.excel_filename }}</div>
                    <div class="download-hint">包含完整的 OCR 提取数据</div>
                  </div>
                </div>
                <button
                  class="btn btn-sm download-btn"
                  @click="downloadExcel(currentFileResult.excel_download_url!, currentFileResult.excel_filename!)"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  下载 Excel
                </button>
              </div>
            </div>
            <div v-else class="empty-result">
              <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="opacity: 0.3; margin-bottom: 12px;">
                <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                <polyline points="7 10 12 15 17 10"/>
                <line x1="12" y1="15" x2="12" y2="3"/>
              </svg>
              <p>未生成 Excel 文件</p>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.agent-result-card {
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

.divider {
  height: 1px;
  background: var(--border);
  margin: 16px 0;
}

/* 文件选择器 */
.file-selector {
  margin-bottom: 16px;
}

.file-buttons {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.file-btn {
  padding: 8px 16px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 20px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 13px;
  font-weight: 500;
}

.file-btn:hover {
  background: rgba(37,99,235,0.1);
  border-color: var(--border-hover);
}

.file-btn.active {
  background: var(--primary);
  border-color: var(--primary);
  color: white;
}

.current-file-info {
  padding: 12px;
  background: var(--bg-input);
  border-radius: 8px;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  margin-bottom: 16px;
}

.file-info-label {
  font-weight: 600;
  color: var(--text-secondary);
}

.file-info-name {
  font-weight: 600;
  color: var(--primary-light);
}

.file-info-error {
  color: var(--danger);
  font-size: 12px;
}

/* 标签页导航 */
.tab-navigation {
  display: flex;
  background: var(--bg-input);
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 16px;
  gap: 4px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.tab-btn:hover {
  background: rgba(255,255,255,0.05);
}

.tab-btn.active {
  background: var(--gradient-1);
  color: white;
  font-weight: 600;
}

.tab-icon {
  font-size: 16px;
}

.tab-content {
  animation: slideDown 0.3s ease;
}

.tab-panel {
  min-height: 200px;
}

.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 16px;
}

.section-header svg {
  width: 20px;
  height: 20px;
  color: var(--primary-light);
  flex-shrink: 0;
}

.section-header h4 {
  font-size: 15px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 提取数据样式 */
.extracted-data {
  animation: fadeIn 0.3s ease;
}

.data-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 12px;
}

.data-item {
  padding: 14px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
  transition: all 0.3s ease;
}

.data-item:hover {
  border-color: var(--border-hover);
  transform: translateY(-2px);
}

.data-key {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-muted);
  text-transform: uppercase;
}

.data-value {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  word-break: break-word;
}

/* 全量数据样式 */
.full-data {
  animation: fadeIn 0.3s ease;
}

.data-summary {
  display: flex;
  gap: 30px;
  margin-bottom: 20px;
  padding: 14px;
  background: var(--bg-input);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.summary-label {
  font-size: 13px;
  color: var(--text-secondary);
}

.summary-value {
  font-size: 16px;
  font-weight: 600;
  color: var(--primary-light);
}

.structured-data-list,
.raw-text {
  margin-top: 20px;
}

.list-title {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.structured-data-item {
  margin-bottom: 12px;
  padding: 14px;
  background: var(--bg-input);
  border-radius: 8px;
  border: 1px solid var(--border);
}

.json-display {
  margin: 0;
  padding: 12px;
  background: var(--bg-card);
  border-radius: 6px;
  font-size: 12px;
  color: var(--text-secondary);
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

.raw-text-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 12px;
}

.raw-text-content {
  padding: 14px;
  background: var(--bg-input);
  border-radius: 8px;
  border: 1px solid var(--border);
  font-size: 13px;
  line-height: 1.6;
  color: var(--text-primary);
  white-space: pre-wrap;
  word-break: break-word;
  max-height: 400px;
  overflow-y: auto;
}

/* 下载样式 */
.download-section {
  animation: fadeIn 0.3s ease;
}

.download-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 24px;
  background: var(--bg-input);
  border-radius: 12px;
  border: 1px solid var(--border);
}

.download-info {
  display: flex;
  align-items: center;
  gap: 16px;
}

.download-icon-wrapper {
  width: 56px;
  height: 56px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(16,185,129,0.15);
  border-radius: 12px;
}

.download-details {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.download-filename {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.download-hint {
  font-size: 12px;
  color: var(--text-secondary);
}

.download-btn {
  background: var(--gradient-3);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 10px 20px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  gap: 6px;
}

.download-btn:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}

/* 空结果样式 */
.empty-result {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.empty-result svg {
  margin: 0 auto 12px;
  display: block;
}

.empty-result p {
  margin: 5px 0;
  font-size: 14px;
}

.empty-result .hint {
  font-size: 12px;
  color: var(--text-muted);
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

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.collapse-enter-active,
.collapse-leave-active {
  transition: all 0.35s ease;
  overflow: hidden;
}

.collapse-enter-from,
.collapse-leave-to {
  max-height: 0;
  opacity: 0;
}

.collapse-enter-to,
.collapse-leave-from {
  max-height: 2000px;
  opacity: 1;
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