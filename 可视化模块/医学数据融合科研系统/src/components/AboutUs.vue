<template>
  <Teleport to="body">
    <div v-if="visible" class="modal-overlay" @click.self="close">
      <div class="modal-card animate-slide-up about-modal">
        <div class="modal-header">
          <h3>关于我们</h3>
          <button class="btn btn-icon" @click="close">✕</button>
        </div>
        <div class="modal-body">
          <!-- Logo 和版本信息 -->
          <div class="about-logo-section">
            <div class="about-logo-icon">
              <svg width="48" height="48" viewBox="0 0 48 48" fill="none">
                <circle cx="24" cy="24" r="20" fill="url(#logo-gradient)"/>
                <path d="M16 24h16" stroke="white" stroke-width="3" stroke-linecap="round"/>
                <path d="M24 16v16" stroke="white" stroke-width="3" stroke-linecap="round"/>
                <circle cx="24" cy="24" r="6" fill="none" stroke="white" stroke-width="2"/>
                <defs>
                  <linearGradient id="logo-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#2563eb"/>
                    <stop offset="100%" style="stop-color:#7c3aed"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div class="about-app-name">医学数据融合科研系统</div>
            <div class="about-version">版本 1.0.0</div>
          </div>

          <!-- 产品介绍 -->
          <div class="about-section">
            <div class="about-section-title">产品介绍</div>
            <p class="about-section-text">
              医学数据融合科研系统是一款专为医学研究人员设计的智能化数据处理平台。
              系统集成了先进的 OCR 技术、AI 数据提取和分析功能，帮助科研人员高效处理医学数据，
              提升科研工作效率。
            </p>
          </div>

          <!-- 核心功能 -->
          <div class="about-section">
            <div class="about-section-title">核心功能</div>
            <div class="about-features">
              <div class="about-feature-item">
                <div class="about-feature-icon">📷</div>
                <div class="about-feature-text">智能图像识别</div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon">🤖</div>
                <div class="about-feature-text">AI 数据提取</div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon">📊</div>
                <div class="about-feature-text">数据可视化</div>
              </div>
              <div class="about-feature-item">
                <div class="about-feature-icon">🔒</div>
                <div class="about-feature-text">安全加密存储</div>
              </div>
            </div>
          </div>

          <!-- 技术栈 -->
          <div class="about-section">
            <div class="about-section-title">技术栈</div>
            <div class="about-tech-stack">
              <span class="tech-tag">Vue 3</span>
              <span class="tech-tag">TypeScript</span>
              <span class="tech-tag">Python</span>
              <span class="tech-tag">FastAPI</span>
              <span class="tech-tag">OCR</span>
              <span class="tech-tag">AI/LLM</span>
            </div>
          </div>

          <!-- 开发团队 -->
          <div class="about-section">
            <div class="about-section-title">开发团队</div>
            <p class="about-section-text">
              本系统由专业的信息化团队开发，致力于为医学科研提供高质量的技术解决方案。
            </p>
          </div>

          <!-- 版权信息 -->
          <div class="about-footer">
            <div class="about-footer-text">© 2026 医学数据融合科研系统. 保留所有权利。</div>
            <div class="about-footer-links">
              <a href="#" class="about-footer-link">隐私政策</a>
              <span class="about-footer-divider">|</span>
              <a href="#" class="about-footer-link">服务条款</a>
              <span class="about-footer-divider">|</span>
              <a href="#" class="about-footer-link">开源许可</a>
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
const props = defineProps<{
  visible: boolean
}>()

const emit = defineEmits<{
  close: []
}>()

function close() {
  emit('close')
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
  max-width: 480px;
  background: #1e293b;
  border-radius: 20px 20px 0 0;
  border: 1px solid rgba(99, 179, 237, 0.15);
  max-height: 85vh;
  overflow-y: auto;
  color: #f0f9ff;
  max-width: min(480px, 40vw);
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

.about-modal {
  max-width: 480px;
}

.about-logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(124, 58, 237, 0.1));
  border-radius: 12px;
  margin-bottom: 20px;
}

.about-logo-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
}

.about-app-name {
  font-size: 18px;
  font-weight: 700;
  color: var(--text-primary);
}

.about-version {
  font-size: 13px;
  color: var(--text-muted);
  background: var(--bg-input);
  padding: 4px 12px;
  border-radius: 12px;
}

.about-section {
  margin-bottom: 20px;
}

.about-section-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 10px;
  padding-left: 12px;
  border-left: 3px solid var(--primary);
}

.about-section-text {
  font-size: 13px;
  color: var(--text-secondary);
  line-height: 1.8;
}

.about-features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.about-feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
}

.about-feature-icon {
  font-size: 20px;
}

.about-feature-text {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
}

.about-tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-tag {
  display: inline-block;
  padding: 6px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.tech-tag:hover {
  border-color: var(--primary);
  color: var(--primary);
}

.about-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid var(--border);
  text-align: center;
}

.about-footer-text {
  font-size: 12px;
  color: var(--text-muted);
  margin-bottom: 12px;
}

.about-footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.about-footer-link {
  font-size: 12px;
  color: var(--text-secondary);
  text-decoration: none;
  transition: color 0.2s;
}

.about-footer-link:hover {
  color: var(--primary);
}

.about-footer-divider {
  color: rgba(99, 179, 237, 0.15);
}

.about-logo-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 24px;
  background: linear-gradient(135deg, rgba(37, 99, 235, 0.1), rgba(124, 58, 237, 0.1));
  border-radius: 12px;
  margin-bottom: 20px;
}

.about-logo-icon {
  width: 72px;
  height: 72px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #2563eb, #7c3aed);
  border-radius: 16px;
  box-shadow: 0 8px 20px rgba(37, 99, 235, 0.3);
}

.about-app-name {
  font-size: 18px;
  font-weight: 700;
  color: #f0f9ff;
}

.about-version {
  font-size: 13px;
  color: #64748b;
  background: #0f1f35;
  padding: 4px 12px;
  border-radius: 12px;
}

.about-section {
  margin-bottom: 20px;
}

.about-section-title {
  font-size: 14px;
  font-weight: 600;
  color: #f0f9ff;
  margin-bottom: 10px;
  padding-left: 12px;
  border-left: 3px solid #2563eb;
}

.about-section-text {
  font-size: 13px;
  color: #94a3b8;
  line-height: 1.8;
}

.about-features {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 10px;
}

.about-feature-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px;
  background: #0f1f35;
  border: 1px solid rgba(99, 179, 237, 0.15);
  border-radius: 8px;
}

.about-feature-icon {
  font-size: 20px;
}

.about-feature-text {
  font-size: 13px;
  font-weight: 500;
  color: #f0f9ff;
}

.about-tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-tag {
  display: inline-block;
  padding: 6px 12px;
  background: #0f1f35;
  border: 1px solid rgba(99, 179, 237, 0.15);
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  color: #94a3b8;
  transition: all 0.2s;
}

.tech-tag:hover {
  border-color: #2563eb;
  color: #f0f9ff;
}

.about-footer {
  margin-top: 24px;
  padding-top: 20px;
  border-top: 1px solid rgba(99, 179, 237, 0.15);
  text-align: center;
}

.about-footer-text {
  font-size: 12px;
  color: #64748b;
  margin-bottom: 12px;
}

.about-footer-links {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}

.about-footer-link {
  font-size: 12px;
  color: #94a3b8;
  text-decoration: none;
  transition: color 0.2s;
}

.about-footer-link:hover {
  color: #2563eb;
}
</style>