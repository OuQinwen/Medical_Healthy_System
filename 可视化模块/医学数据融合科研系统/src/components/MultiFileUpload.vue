<template>
  <div class="multi-file-upload">
    <!-- 上传区域 -->
    <div class="upload-zone" :class="{dragging}" @dragover.prevent="dragging = true" @dragleave.prevent="dragging = false" @drop.prevent="handleDrop" @click="triggerInput">
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" class="upload-icon">
        <polyline points="16 16 12 12 8 16"/>
        <line x1="12" y1="12" x2="12" y2="21"/>
        <path d="M20.39 18.39A5 5 0 0 0 18 9h-1.26A8 8 0 1 0 3 16.3"/>
      </svg>
      <p class="upload-text">{{ dragging ? '松开上传文件' : '拖拽文件到此处，或点击选择' }}</p>
      <p class="upload-hint">支持 JPG · PNG · WEBP · PDF · XLSX · TXT | 支持多文件上传</p>
    </div>
    <input ref="inputRef" type="file" multiple accept="image/*,.pdf,.xlsx,.xls,.txt,.csv" class="hidden-input" @change="handleChange"/>

    <!-- 待上传文件列表 -->
    <div v-if="pendingFiles.length > 0" class="file-list-section">
      <div class="file-list-header">
        <span class="file-list-title">待上传文件 ({{ pendingFiles.length }})</span>
        <button class="btn-clear" @click="clearPendingFiles">清空</button>
      </div>
      <div class="file-list">
        <div v-for="(file, i) in pendingFiles" :key="i" class="file-item pending">
          <div class="file-icon">{{ getFileIcon(file.name) }}</div>
          <div class="file-info">
            <div class="file-name">{{ file.name }}</div>
            <div class="file-meta">
              <span class="file-size">{{ formatSize(file.size) }}</span>
              <span class="file-status" :class="{ uploading: file.uploading }">
                {{ file.uploading ? '上传中...' : '待上传' }}
              </span>
            </div>
          </div>
          <button class="file-delete" @click.stop="removePendingFile(i)" :disabled="file.uploading">✕</button>
        </div>
      </div>
      <button class="btn-upload" @click="uploadFiles" :disabled="uploading">
        {{ uploading ? '上传中...' : `开始上传 (${pendingFiles.length})` }}
      </button>
    </div>

    <!-- 已上传文件列表 -->
    <div v-if="uploadedFiles.length > 0" class="file-list-section uploaded">
      <div class="file-list-header">
        <span class="file-list-title">已上传文件 ({{ uploadedFiles.length }})</span>
      </div>
      <div class="file-list">
        <div v-for="(file, i) in uploadedFiles" :key="file.file_id" class="file-item uploaded">
          <div class="file-icon">{{ getFileIcon(file.file_name) }}</div>
          <div class="file-info">
            <div class="file-name">{{ file.file_name }}</div>
            <div class="file-meta">
              <span class="file-size">{{ formatSize(file.file_size) }}</span>
              <span class="file-type">{{ file.data_type || file.data_category }}</span>
              <span class="file-ocr-status" :class="file.ocr_status">
                {{ getOcrStatusText(file.ocr_status) }}
              </span>
            </div>
          </div>
          <button class="file-delete" @click="deleteFile(file.file_id)" :disabled="file.ocr_status === 'processing'">删除</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'

interface PendingFile {
  name: string
  size: number
  file: File
  uploading?: boolean
}

interface UploadedFile {
  file_id: number
  file_name: string
  file_size: number
  file_type: string
  data_category: string
  data_type: string
  ocr_status: 'pending' | 'processing' | 'completed' | 'failed'
  upload_time: string
}

const props = defineProps<{
  patientId: number
  dataCategory: string
  uploadedFiles?: UploadedFile[]
}>()

const emit = defineEmits<{
  (e: 'upload-complete', result: any): void
  (e: 'upload-error', error: any): void
  (e: 'file-deleted', fileId: number): void
}>()

const inputRef = ref<HTMLInputElement>()
const pendingFiles = ref<PendingFile[]>([])
const uploadedFiles = ref<UploadedFile[]>(props.uploadedFiles || [])
const dragging = ref(false)
const uploading = ref(false)

function triggerInput() {
  inputRef.value?.click()
}

function handleChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    addFiles(Array.from(input.files))
  }
}

function handleDrop(e: DragEvent) {
  dragging.value = false
  if (e.dataTransfer?.files) {
    addFiles(Array.from(e.dataTransfer.files))
  }
}

function addFiles(newFiles: File[]) {
  const filesToAdd = newFiles.map(file => ({
    name: file.name,
    size: file.size,
    file: file,
    uploading: false
  }))
  pendingFiles.value = [...pendingFiles.value, ...filesToAdd]
}

function removePendingFile(index: number) {
  pendingFiles.value = pendingFiles.value.filter((_, i) => i !== index)
}

function clearPendingFiles() {
  pendingFiles.value = []
}

async function uploadFiles() {
  if (pendingFiles.value.length === 0 || uploading.value) return

  uploading.value = true

  try {
    const formData = new FormData()
    formData.append('patient_id', props.patientId.toString())
    formData.append('data_category', props.dataCategory)

    // 添加所有文件
    pendingFiles.value.forEach(f => {
      f.uploading = true
      formData.append('files', f.file)
    })

    const response = await fetch('http://localhost:8000/api/multi-file-upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      },
      body: formData
    })

    const result = await response.json()

    if (result.success) {
      // 将成功上传的文件移到已上传列表
      result.uploaded_files.forEach((file: any) => {
        if (!file.error) {
          uploadedFiles.value.push({
            file_id: file.file_id,
            file_name: file.original_filename,
            file_size: file.file_size,
            file_type: file.file_type,
            data_category: file.data_category,
            data_type: file.data_type,
            ocr_status: file.ocr_status,
            upload_time: new Date().toISOString()
          })
        }
      })

      // 清空待上传列表
      pendingFiles.value = []

      emit('upload-complete', result)
    } else {
      emit('upload-error', result)
    }
  } catch (error) {
    console.error('上传失败:', error)
    pendingFiles.value.forEach(f => f.uploading = false)
    emit('upload-error', error)
  } finally {
    uploading.value = false
  }
}

async function deleteFile(fileId: number) {
  try {
    const response = await fetch(`http://localhost:8000/api/file/${fileId}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${localStorage.getItem('token')}`
      }
    })

    const result = await response.json()

    if (result.success) {
      uploadedFiles.value = uploadedFiles.value.filter(f => f.file_id !== fileId)
      emit('file-deleted', fileId)
    }
  } catch (error) {
    console.error('删除文件失败:', error)
  }
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

function getOcrStatusText(status: string) {
  const statusMap: Record<string, string> = {
    'pending': '待处理',
    'processing': '处理中',
    'completed': '已完成',
    'failed': '失败'
  }
  return statusMap[status] || status
}

// 暴露方法供父组件调用
defineExpose({
  refreshUploadedFiles: async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/patient/${props.patientId}/files?data_category=${props.dataCategory}`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      })
      const result = await response.json()
      if (result.success) {
        uploadedFiles.value = result.files
      }
    } catch (error) {
      console.error('刷新文件列表失败:', error)
    }
  }
})
</script>

<style scoped>
.multi-file-upload {
  width: 100%;
}

.upload-zone {
  border: 2px dashed var(--border);
  border-radius: var(--radius-md);
  padding: 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s;
  background: var(--bg-input);
  margin-bottom: 16px;
}

.upload-zone:hover,
.upload-zone.dragging {
  border-color: var(--primary-light);
  background: rgba(59,130,246,0.05);
}

.upload-icon {
  margin: 0 auto 8px;
  color: var(--text-muted);
}

.upload-text {
  font-size: 13px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 11px;
  color: var(--text-muted);
}

.hidden-input {
  display: none;
}

.file-list-section {
  margin-bottom: 16px;
}

.file-list-section.uploaded {
  border-top: 1px solid var(--border);
  padding-top: 16px;
}

.file-list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.file-list-title {
  font-size: 12px;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-clear {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 11px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
}

.btn-clear:hover {
  background: var(--bg-hover);
  color: var(--danger);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  transition: all 0.2s;
}

.file-item.pending {
  border-left: 3px solid var(--warning);
}

.file-item.uploaded {
  border-left: 3px solid var(--success);
}

.file-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
  min-width: 0;
}

.file-name {
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  margin-bottom: 2px;
}

.file-meta {
  display: flex;
  gap: 8px;
  font-size: 11px;
  color: var(--text-muted);
}

.file-size {
  flex-shrink: 0;
}

.file-type {
  flex-shrink: 0;
  color: var(--text-secondary);
}

.file-status {
  flex-shrink: 0;
}

.file-status.uploading {
  color: var(--primary);
  animation: pulse 1.5s infinite;
}

.file-ocr-status {
  flex-shrink: 0;
  font-weight: 500;
}

.file-ocr-status.pending {
  color: var(--text-muted);
}

.file-ocr-status.processing {
  color: var(--primary);
  animation: pulse 1.5s infinite;
}

.file-ocr-status.completed {
  color: var(--success);
}

.file-ocr-status.failed {
  color: var(--danger);
}

@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.5; }
}

.file-delete {
  background: none;
  border: none;
  cursor: pointer;
  color: var(--text-muted);
  font-size: 13px;
  padding: 6px;
  border-radius: 4px;
  transition: all 0.2s;
  flex-shrink: 0;
}

.file-delete:hover:not(:disabled) {
  color: var(--danger);
  background: rgba(239, 68, 68, 0.1);
}

.file-delete:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-upload {
  width: 100%;
  padding: 10px 16px;
  background: var(--primary);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 13px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  margin-top: 12px;
}

.btn-upload:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-upload:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>