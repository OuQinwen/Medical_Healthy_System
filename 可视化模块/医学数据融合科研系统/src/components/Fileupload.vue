<template>
  <div class="file-upload" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="handleDrop">
    <div class="upload-zone" :class="{dragging}" @click="triggerInput">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="upload-icon">
        <polyline points="16 16 12 12 8 16"/>
        <line x1="12" y1="12" x2="12" y2="21"/>
        <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
      </svg>
      <p class="upload-text">{{ dragging ? '松开上传文件' : '拖拽文件到此处，或点击选择' }}</p>
      <p class="upload-hint">支持 JPG · PNG · WEBP · PDF · XLSX · TXT</p>
    </div>
    <input ref="inputRef" type="file" multiple accept="image/*,.pdf,.xlsx,.xls,.txt,.csv" class="hidden-input" @change="handleChange"/>

    <div v-if="files.length > 0" class="file-list">
      <div v-for="(file, i) in files" :key="i" class="file-item">
        <div class="file-icon">{{ getFileIcon(file.name) }}</div>
        <div class="file-info">
          <div class="file-name">{{ file.name }}</div>
          <div class="file-size">{{ formatSize(file.size) }}</div>
        </div>
        <button class="file-delete" @click.stop="removeFile(i)">✕</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  (e: 'files-selected', files: File[]): void
  (e: 'files-changed', files: File[]): void
  (e: 'files-cleared'): void
}>()

const inputRef = ref<HTMLInputElement>()
const files = ref<File[]>([])
const dragging = ref(false)

// 清空文件列表
function clearFiles() {
  files.value = []
  // 清空 input 元素的值，确保可以重新选择相同的文件
  if (inputRef.value) {
    inputRef.value.value = ''
  }
  emit('files-cleared')
}

function triggerInput() {
  inputRef.value?.click()
}

function handleChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    addFiles(Array.from(input.files))
    // 清空 input 值，确保可以重新选择相同的文件
    input.value = ''
  }
}

function handleDrop(e: DragEvent) {
  dragging.value = false
  if (e.dataTransfer?.files) {
    addFiles(Array.from(e.dataTransfer.files))
    // 清空 input 值，确保可以重新选择相同的文件
    if (inputRef.value) {
      inputRef.value.value = ''
    }
  }
}

function addFiles(newFiles: File[]) {
  // 只添加新文件，不累积旧文件
  files.value = [...newFiles]
  emit('files-selected', files.value)
  
  // 延迟清空文件列表，避免重复上传
  setTimeout(() => {
    clearFiles()
  }, 1000)
}

function removeFile(index: number) {
  files.value = files.value.filter((_, i) => i !== index)
  emit('files-changed', files.value)
}

function formatSize(bytes: number) {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

function getFileIcon(name: string) {
  const ext = name.split('.').pop()?.toLowerCase()
  if (['jpg', 'jpeg', 'png', 'webp', 'gif'].includes(ext || '')) return '🖼️'
  if (ext === 'pdf') return '📄'
  if (['xlsx', 'xls', 'csv'].includes(ext || '')) return '📊'
  return '📝'
}
</script>

<style scoped>
.upload-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius-md);
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-input);
}
.upload-zone:hover, .upload-zone.dragging {
  border-color: var(--primary-light);
  background: rgba(59,130,246,0.05);
}
.upload-icon { margin: 0 auto 8px; color: var(--text-muted); }
.upload-text { font-size: 13px; color: var(--text-secondary); margin-bottom: 4px; }
.upload-hint { font-size: 11px; color: var(--text-muted); }
.hidden-input { display: none; }

.file-list { margin-top: 10px; display: flex; flex-direction: column; gap: 6px; }
.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
}
.file-icon { font-size: 18px; }
.file-info { flex: 1; min-width: 0; }
.file-name { font-size: 13px; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.file-size { font-size: 11px; color: var(--text-muted); margin-top: 2px; }
.file-delete {
  background: none; border: none; cursor: pointer;
  color: var(--text-muted); font-size: 13px;
  padding: 4px; border-radius: 4px;
  transition: color 0.2s;
}
.file-delete:hover { color: var(--danger); }
</style>
