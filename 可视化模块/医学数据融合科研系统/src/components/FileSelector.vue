<script setup lang="ts">
/**
 * FileSelector.vue - 文件选择器组件
 * 
 * 功能说明：
 * - 文件选择和上传功能
 * - 文件类型验证和过滤
 * - 文件选择后立即传递给父组件
 * 
 * 支持的文件类型：
 * - 图片：JPG, PNG, GIF, WebP
 * - 文本：TXT, CSV
 * - 表格：XLS, XLSX
 * 
 * 事件：
 * - filesSelected: 文件选择事件
 *   - 参数: files (File[]) - 选中的文件列表
 * - close: 关闭事件
 */

import { ref } from 'vue'

// 定义组件事件
const emit = defineEmits<{
  filesSelected: [files: File[]]
  close: []
}>()

// 状态管理
const fileInputRef = ref<HTMLInputElement>() // 文件输入框引用

// 触发文件选择
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

// 处理文件选择事件
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const files = target.files
  if (files) {
    // 文件类型验证和过滤
    const validFiles = Array.from(files).filter(file => {
      const validTypes = [
        // 图片类型
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        // 文本类型
        'text/plain', 'text/csv',
        // 表格类型
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/csv'
      ]
      return validTypes.includes(file.type)
    })
    
    emit('filesSelected', validFiles)
  }
  // 清空input以允许重复选择相同文件
  if (target) {
    target.value = ''
  }
}

// 关闭文件选择器
const close = () => {
  emit('close')
}
</script>

<template>
  <div class="file-selector">
    <div class="file-selector-header">
      <span class="file-selector-title">选择文件</span>
      <div class="close-btn" @click="close">×</div>
    </div>
    <div class="file-type-buttons">
      <div class="file-type-btn" @click="triggerFileInput">
        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" width="36" height="36">
          <defs>
            <linearGradient id="uploadGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" style="stop-color:#3b82f6;stop-opacity:1" />
              <stop offset="100%" style="stop-color:#7c3aed;stop-opacity:1" />
            </linearGradient>
          </defs>
          <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M17 8l-5-5-5 5M12 3v12" stroke="url(#uploadGradient)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
        </svg>
        <span>上传文件</span>
      </div>
    </div>
    <div class="file-hint">
      支持格式：图片（JPG, PNG, GIF, WebP）、文本（TXT, CSV）、表格（XLS, XLSX）
    </div>
    <input
      ref="fileInputRef"
      type="file"
      multiple
      accept="image/*,.txt,.csv,.xls,.xlsx"
      @change="handleFileSelect"
      style="display: none"
    />
  </div>
</template>

<style scoped>
@import '../assets/data-input.css';
</style>