<script setup lang="ts">
/**
 * DataInput.vue - 数据输入组件
 * 
 * 功能说明：
 * - 支持文本消息输入和发送
 * - 支持文件上传功能
 * - 自动调整输入框高度
 * - 多行文本支持，超过5行显示滚动条
 * 
 * 特性：
 * - 自适应高度：根据内容自动调整输入框高度
 * - 文件管理：支持文件选择、显示、删除
 * - 快捷键支持：Enter发送，Shift+Enter换行
 * - 文件类型验证：只允许图片、文本、表格文件
 * 
 * 事件：
 * - sendMessage: 发送消息和文件事件
 *   - 参数1: message (string) - 文本消息
 *   - 参数2: files (File[]) - 文件列表
 */

import { ref, watch, nextTick } from 'vue'
import FileSelector from './FileSelector.vue'

// 状态管理
const inputValue = ref('')                    // 输入框内容
const textareaRef = ref<HTMLTextAreaElement>() // 文本域引用
const showFileSelector = ref(false)          // 显示文件选择器
const selectedFiles = ref<File[]>([])        // 已选文件列表

// 定义组件事件
const emit = defineEmits<{
  sendMessage: [message: string, files: File[]]
}>()

// 发送消息函数
const sendMessage = () => {
  if (inputValue.value.trim() || selectedFiles.value.length > 0) {
    emit('sendMessage', inputValue.value, selectedFiles.value)
    selectedFiles.value = []
    inputValue.value = ''
  }
}

// 处理加号按钮点击
const handleAddClick = () => {
  showFileSelector.value = !showFileSelector.value
}

// 处理键盘事件
const handleKeyPress = (e: KeyboardEvent) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    sendMessage()
  }
}

// 处理文件选择事件
const handleFilesSelected = (files: File[]) => {
  selectedFiles.value = [...selectedFiles.value, ...files]
}

// 自动调整输入框高度
const autoResize = () => {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.style.height = 'auto'
    const newHeight = Math.min(textarea.scrollHeight, 120) // 最大高度120px（5行）
    textarea.style.height = newHeight + 'px'
  }
}

// 滚动到底部
const scrollToBottom = () => {
  const textarea = textareaRef.value
  if (textarea) {
    textarea.scrollTop = textarea.scrollHeight
  }
}

// 监听输入变化，自动调整高度
watch(inputValue, () => {
  nextTick(() => {
    autoResize()
    scrollToBottom()
  })
})
</script>

<template>
  <div class="data-input">
    <div class="input-container">
      <textarea
        ref="textareaRef"
        v-model="inputValue"
        class="input-field"
        placeholder="请输入内容..."
        rows="1"
        @keydown="handleKeyPress"
      ></textarea>
      <div class="add-button" @click="handleAddClick">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="add-icon">
          <defs>
            <linearGradient id="addGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
            </linearGradient>
            <filter id="addGlow">
              <feGaussianBlur stdDeviation="2" result="coloredBlur"/>
              <feMerge>
                <feMergeNode in="coloredBlur"/>
                <feMergeNode in="SourceGraphic"/>
              </feMerge>
            </filter>
          </defs>
          <path
            d="M12 5v14M5 12h14"
            stroke="url(#addGradient)"
            stroke-width="2.5"
            stroke-linecap="round"
            fill="none"
            filter="url(#addGlow)"
          />
        </svg>
      </div>
      <div class="send-button" @click="sendMessage">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" class="send-icon">
          <defs>
            <filter id="sendShadow">
              <feDropShadow dx="0" dy="1" stdDeviation="1" flood-color="rgba(0,0,0,0.3)"/>
            </filter>
          </defs>
          <path
            d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"
            fill="#ffffff"
            filter="url(#sendShadow)"
          />
        </svg>
      </div>
    </div>

    <!-- 文件选择器组件 -->
    <FileSelector
      v-if="showFileSelector"
      @files-selected="handleFilesSelected"
      @close="showFileSelector = false"
    />

    <!-- 已选文件列表 -->
    <div v-if="selectedFiles.length > 0" class="selected-files">
      <div class="files-title">已选择 {{ selectedFiles.length }} 个文件：</div>
      <div class="files-list">
        <div v-for="(file, index) in selectedFiles" :key="index" class="file-item">
          <span class="file-name">{{ file.name }}</span>
          <span class="file-size">({{ (file.size / 1024).toFixed(2) }} KB)</span>
          <div class="file-remove" @click="selectedFiles.splice(index, 1)">×</div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
@import '../assets/data-input.css';
</style>