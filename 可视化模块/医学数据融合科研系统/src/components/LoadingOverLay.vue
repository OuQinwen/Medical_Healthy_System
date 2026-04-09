<template>
  <Teleport to="body">
    <Transition name="fade">
      <div v-if="visible" class="loading-overlay">
        <div class="loading-box">
          <div class="loading-rings">
            <div class="ring ring1"></div>
            <div class="ring ring2"></div>
            <div class="ring ring3"></div>
            <div class="ring-center">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83" stroke="url(#lg)" stroke-width="2" stroke-linecap="round"/>
                <defs>
                  <linearGradient id="lg" x1="2" y1="12" x2="22" y2="12">
                    <stop stop-color="#2563eb"/>
                    <stop offset="1" stop-color="#7c3aed"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
          </div>

          <div class="loading-message">{{ message }}</div>
          <div v-if="subMessage" class="loading-sub">{{ subMessage }}</div>

          <div v-if="showProgress" class="loading-progress">
            <div class="progress-bar">
              <div class="progress-fill" :style="{width: progress + '%'}"></div>
            </div>
            <div class="progress-label">{{ progress }}%</div>
          </div>

          <div v-if="steps && steps.length > 0" class="loading-steps">
            <div
              v-for="(step, i) in steps"
              :key="i"
              class="ls-item"
              :class="{done: currentStep > i, active: currentStep === i}"
            >
              <span class="ls-dot">{{ currentStep > i ? '✓' : currentStep === i ? '◉' : '○' }}</span>
              <span>{{ step }}</span>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  visible: boolean
  message?: string
  subMessage?: string
  progress?: number
  showProgress?: boolean
  steps?: string[]
  currentStep?: number
}>(), {
  message: '处理中...',
  progress: 0,
  showProgress: false,
  currentStep: 0,
})
</script>

<style scoped>
.loading-overlay {
  position: fixed; inset: 0;
  background: rgba(10, 15, 30, 0.85);
  backdrop-filter: blur(8px);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999;
}
.loading-box {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-xl);
  padding: 36px 32px;
  text-align: center;
  min-width: 260px;
  max-width: 340px;
}

.loading-rings {
  position: relative;
  width: 80px; height: 80px;
  margin: 0 auto 20px;
}
.ring {
  position: absolute;
  border-radius: 50%;
  border: 2px solid transparent;
}
.ring1 {
  inset: 0;
  border-top-color: #2563eb;
  animation: spin 1.2s linear infinite;
}
.ring2 {
  inset: 8px;
  border-right-color: #7c3aed;
  animation: spin 1.8s linear infinite reverse;
}
.ring3 {
  inset: 16px;
  border-bottom-color: #06b6d4;
  animation: spin 2.4s linear infinite;
}
.ring-center {
  position: absolute;
  inset: 28px;
  display: flex; align-items: center; justify-content: center;
  animation: pulse 2s ease infinite;
}

.loading-message { font-size: 16px; font-weight: 600; color: var(--text-primary); margin-bottom: 4px; }
.loading-sub { font-size: 12px; color: var(--text-secondary); margin-bottom: 16px; }

.loading-progress {
  margin-top: 16px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.progress-label { font-size: 12px; color: var(--text-secondary); white-space: nowrap; }

.loading-steps {
  margin-top: 16px;
  text-align: left;
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.ls-item {
  display: flex; align-items: center; gap: 8px;
  font-size: 13px; color: var(--text-muted);
}
.ls-item.done { color: var(--success); }
.ls-item.active { color: var(--primary-light); font-weight: 500; }
.ls-dot { width: 14px; text-align: center; }

.fade-enter-active, .fade-leave-active { transition: opacity 0.3s; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>
