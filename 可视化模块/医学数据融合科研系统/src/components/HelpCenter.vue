<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="close">
      <div class="modal-card animate-slide-up help-modal">
        <div class="modal-header">
          <h3>帮助中心</h3>
          <button class="btn btn-icon" @click="close">✕</button>
        </div>
        <div class="modal-body">
          <!-- 搜索框 -->
          <div class="help-search">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/>
              <path d="m21 21-4.35-4.35"/>
            </svg>
            <input 
              v-model="searchQuery" 
              type="text" 
              placeholder="搜索问题..." 
              class="help-search-input"
            />
          </div>

          <!-- 快捷入口 -->
          <div class="help-quick-links">
            <div class="help-quick-title">快捷入口</div>
            <div class="help-quick-grid">
              <div class="help-quick-item" @click="expandItem('getting-started')">
                <div class="help-quick-icon">🚀</div>
                <div class="help-quick-text">快速入门</div>
              </div>
              <div class="help-quick-item" @click="expandItem('data-upload')">
                <div class="help-quick-icon">📤</div>
                <div class="help-quick-text">数据上传</div>
              </div>
              <div class="help-quick-item" @click="expandItem('ocr-settings')">
                <div class="help-quick-icon">⚙️</div>
                <div class="help-quick-text">OCR设置</div>
              </div>
              <div class="help-quick-item" @click="expandItem('troubleshooting')">
                <div class="help-quick-icon">🔧</div>
                <div class="help-quick-text">常见问题</div>
              </div>
            </div>
          </div>

          <!-- 帮助内容列表 -->
          <div class="help-content-list">
            <div 
              v-for="(item, index) in filteredItems" 
              :key="index"
              class="help-item"
              :class="{ expanded: expandedIndex === index }"
            >
              <div class="help-item-header" @click="toggleItem(index)">
                <div class="help-item-title">
                  <span class="help-item-icon">{{ item.icon }}</span>
                  <span>{{ item.title }}</span>
                </div>
                <svg 
                  class="help-item-arrow" 
                  :class="{ rotated: expandedIndex === index }"
                  width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"
                >
                  <polyline points="6 9 12 15 18 9"/>
                </svg>
              </div>
              <div v-if="expandedIndex === index" class="help-item-content">
                <div class="help-item-text" v-html="item.content"></div>
              </div>
            </div>
          </div>

          <!-- 联系支持 -->
          <div class="help-contact">
            <div class="help-contact-title">未找到答案？</div>
            <p class="help-contact-desc">如果您的问题没有得到解答，请联系我们的技术支持团队</p>
            <div class="help-contact-actions">
              <button class="btn btn-primary help-contact-btn">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                  <polyline points="22,6 12,13 2,6"/>
                </svg>
                发送邮件
              </button>
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn btn-secondary" @click="close">关闭</button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'

const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

const searchQuery = ref('')
const expandedIndex = ref(-1)

const helpItems = [
  {
    icon: '🚀',
    title: '快速入门',
    content: `
      <p><strong>1. 登录系统</strong><br>使用您的账号和密码登录系统。</p>
      <p><strong>2. 上传数据</strong><br>点击"数据录入"页面，选择要上传的图片文件。</p>
      <p><strong>3. OCR 识别</strong><br>系统会自动识别图片中的文字内容。</p>
      <p><strong>4. 数据确认</strong><br>检查识别结果，如有错误可手动修改。</p>
      <p><strong>5. 保存数据</strong><br>确认无误后点击保存，数据将存储到系统中。</p>
    `
  },
  {
    icon: '📤',
    title: '数据上传',
    content: `
      <p><strong>支持的文件格式：</strong> JPG、PNG、WEBP 等常见图片格式。</p>
      <p><strong>上传步骤：</strong></p>
      <ol style="margin-left: 20px; line-height: 1.8;">
        <li>进入"数据录入"页面</li>
        <li>点击上传区域或拖拽文件</li>
        <li>选择要上传的图片文件</li>
        <li>等待上传完成</li>
        <li>系统自动进行 OCR 识别</li>
      </ol>
      <p><strong>注意事项：</strong>请确保图片清晰度足够，文字内容完整可辨。</p>
    `
  },
  {
    icon: '⚙️',
    title: 'OCR 设置',
    content: `
      <p><strong>云端模型：</strong>使用云端 API 服务，识别准确率高，需要联网。</p>
      <p><strong>本地模型：</strong>使用本地 Ollama 服务，无需联网，但需要提前部署。</p>
      <p><strong>配置步骤：</strong></p>
      <ol style="margin-left: 20px; line-height: 1.8;">
        <li>进入"个人中心"页面</li>
        <li>点击"系统设置"</li>
        <li>选择 AI 模型类型（云端/本地）</li>
        <li>如选择云端，配置 API 密钥</li>
        <li>点击"测试连接"验证配置</li>
        <li>点击"保存设置"完成配置</li>
      </ol>
    `
  },
  {
    icon: '🔧',
    title: '常见问题',
    content: `
      <p><strong>Q: OCR 识别不准确怎么办？</strong><br>A: 请确保上传的图片清晰度足够，文字内容完整。如果仍有问题，可以尝试调整图片角度或重新上传。</p>
      <p><strong>Q: 如何修改密码？</strong><br>A: 进入"个人中心"页面，点击"账户安全"，输入当前密码和新密码即可修改。</p>
      <p><strong>Q: 数据可以导出吗？</strong><br>A: 支持，在数据页面可以选择导出为 Excel 格式。</p>
      <p><strong>Q: 系统支持多用户吗？</strong><br>A: 支持，系统支持医生和管理员角色，可以创建多个用户账号。</p>
    `
  },
  {
    icon: '🔒',
    title: '账户安全',
    content: `
      <p><strong>密码要求：</strong>密码长度至少 6 位，建议包含字母、数字和特殊字符。</p>
      <p><strong>安全建议：</strong></p>
      <ul style="margin-left: 20px; line-height: 1.8;">
        <li>定期修改密码</li>
        <li>不要使用简单密码</li>
        <li>不要与他人共享账号</li>
        <li>退出时记得点击"退出登录"</li>
      </ul>
    `
  },
  {
    icon: '📞',
    title: '技术支持',
    content: `
      <p>如果您在使用过程中遇到任何问题，可以通过以下方式联系我们：</p>
      <p><strong>邮箱：</strong>adminexample@163.com</p>
      <p><strong>工作时间：</strong>周一至周五 9:00-18:00</p>
      <p>我们会在收到您的问题后尽快回复。</p>
    `
  }
]

const filteredItems = computed(() => {
  if (!searchQuery.value) return helpItems
  const query = searchQuery.value.toLowerCase()
  return helpItems.filter(item => 
    item.title.toLowerCase().includes(query) || 
    item.content.toLowerCase().includes(query)
  )
})

function close() {
  emit('close')
}

function toggleItem(index: number) {
  expandedIndex.value = expandedIndex.value === index ? -1 : index
}

function expandItem(itemId: string) {
  const index = helpItems.findIndex(item => {
    if (itemId === 'getting-started') return item.title === '快速入门'
    if (itemId === 'data-upload') return item.title === '数据上传'
    if (itemId === 'ocr-settings') return item.title === 'OCR 设置'
    if (itemId === 'troubleshooting') return item.title === '常见问题'
    return false
  })
  if (index !== -1) {
    expandedIndex.value = index
  }
}
</script>

<style scoped>
.modal-overlay {
  position: fixed !important;
  top: 0 !important;
  left: 0 !important;
  right: 0 !important;
  bottom: 0 !important;
  display: flex !important;
  align-items: flex-end !important;
  justify-content: center !important;
  z-index: 9999 !important;
  background: rgba(0,0,0,0.7) !important;
  backdrop-filter: blur(4px);
}

.modal-card {
  width: 100%;
  max-width: 40vw;
  max-width: min(520px, 40vw);
  background: #1e293b;
  border-radius: 20px 20px 0 0;
  border: 1px solid rgba(99, 179, 237, 0.15);
  max-height: 85vh;
  overflow-y: auto;
  color: #f0f9ff;
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 20px 20px 0;
}

.modal-header h3 {
  font-size: 18px;
  font-weight: 600;
  color: #f0f9ff;
}

.modal-body {
  padding: 16px 20px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.modal-footer {
  display: flex;
  gap: 10px;
  padding: 0 20px 20px;
}

.modal-footer .btn {
  flex: 1;
}

.btn-icon {
  background: transparent;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  padding: 8px;
  border-radius: 8px;
  transition: all 0.2s;
}

.btn-icon:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #f0f9ff;
}

.btn-secondary {
  background: #0f1f35;
  border: 1px solid rgba(99, 179, 237, 0.15);
  color: #94a3b8;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-secondary:hover {
  border-color: rgba(99, 179, 237, 0.4);
  color: #f0f9ff;
}

.btn-primary {
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  border: none;
  color: white;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
}

.help-modal {
  max-width: 520px;
}

.help-search {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 10px;
  margin-bottom: 16px;
}

.help-search svg {
  color: var(--text-muted);
  flex-shrink: 0;
}

.help-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: var(--text-primary);
}

.help-search-input::placeholder {
  color: var(--text-muted);
}

.help-quick-links {
  margin-bottom: 20px;
}

.help-quick-title {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-secondary);
  margin-bottom: 12px;
}

.help-quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.help-quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.help-quick-item:hover {
  border-color: var(--primary);
  background: rgba(37, 99, 235, 0.05);
  transform: translateY(-2px);
}

.help-quick-icon {
  font-size: 24px;
}

.help-quick-text {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-primary);
}

.help-content-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.help-item {
  border: 1px solid var(--border);
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.2s;
}

.help-item.expanded {
  border-color: var(--primary);
}

.help-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.help-item-header:hover {
  background: rgba(255, 255, 255, 0.04);
}

.help-item-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.help-item-icon {
  font-size: 18px;
}

.help-item-arrow {
  color: var(--text-muted);
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.help-item-arrow.rotated {
  transform: rotate(180deg);
}

.help-item-content {
  padding: 0 16px 16px;
  border-top: 1px solid var(--border);
  background: rgba(255, 255, 255, 0.02);
}

.help-item-text {
  padding-top: 14px;
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.help-item-text strong {
  color: var(--text-primary);
  font-weight: 600;
}

.help-item-text p {
  margin-bottom: 10px;
}

.help-item-text p:last-child {
  margin-bottom: 0;
}

.help-contact {
  padding: 16px;
  background: rgba(37, 99, 235, 0.05);
  border: 1px solid rgba(37, 99, 235, 0.1);
  border-radius: 10px;
}

.help-contact-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.help-contact-desc {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.help-contact-actions {
  display: flex;
  gap: 10px;
}

.help-contact-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 13px;
  padding: 10px 16px;
}

.help-search-input {
  flex: 1;
  background: transparent;
  border: none;
  outline: none;
  font-size: 14px;
  color: #f0f9ff;
}

.help-search-input::placeholder {
  color: #64748b;
}

.help-search {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 16px;
  background: #0f1f35;
  border: 1px solid rgba(99, 179, 237, 0.15);
  border-radius: 10px;
  margin-bottom: 16px;
}

.help-search svg {
  color: #64748b;
  flex-shrink: 0;
}

.help-quick-title {
  font-size: 13px;
  font-weight: 600;
  color: #94a3b8;
  margin-bottom: 12px;
}

.help-quick-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
}

.help-quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 16px 8px;
  background: #0f1f35;
  border: 1px solid rgba(99, 179, 237, 0.15);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s;
}

.help-quick-item:hover {
  border-color: #2563eb;
  background: rgba(37, 99, 235, 0.1);
  transform: translateY(-2px);
}

.help-quick-icon {
  font-size: 24px;
}

.help-quick-text {
  font-size: 12px;
  font-weight: 500;
  color: #f0f9ff;
}

.help-content-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.help-item {
  border: 1px solid rgba(99, 179, 237, 0.15);
  border-radius: 10px;
  overflow: hidden;
  transition: all 0.2s;
  background: #0f1f35;
}

.help-item.expanded {
  border-color: #2563eb;
}

.help-item-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.help-item-header:hover {
  background: rgba(255, 255, 255, 0.04);
}

.help-item-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 600;
  color: #f0f9ff;
}

.help-item-icon {
  font-size: 18px;
}

.help-item-arrow {
  color: #64748b;
  transition: transform 0.3s ease;
  flex-shrink: 0;
}

.help-item-arrow.rotated {
  transform: rotate(180deg);
}

.help-item-content {
  padding: 0 16px 16px;
  border-top: 1px solid rgba(99, 179, 237, 0.15);
  background: rgba(255, 255, 255, 0.02);
}

.help-item-text {
  padding-top: 14px;
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.8;
}

.help-item-text strong {
  color: #f0f9ff;
  font-weight: 600;
}

.help-item-text p {
  margin-bottom: 10px;
}

.help-item-text p:last-child {
  margin-bottom: 0;
}

.help-contact {
  padding: 16px;
  background: rgba(37, 99, 235, 0.05);
  border: 1px solid rgba(37, 99, 235, 0.1);
  border-radius: 10px;
}

.help-contact-title {
  font-size: 14px;
  font-weight: 600;
  color: #f0f9ff;
  margin-bottom: 6px;
}

.help-contact-desc {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
}

.help-contact-actions {
  display: flex;
  gap: 10px;
}
</style>