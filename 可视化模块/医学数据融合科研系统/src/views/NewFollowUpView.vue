<template>
  <div>
    <div class="page-topbar">
      <h1>随访管理</h1>
      <button class="btn btn-primary btn-sm" @click="showAddModal = true">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
          <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
        </svg>
        新增
      </button>
    </div>

    <div class="page">
      <!-- Stats -->
      <div class="stats-row">
        <div class="stat-card">
          <div class="stat-icon-wrapper" style="background: var(--gradient-1)">
            <svg class="stat-icon-svg" width="24" height="24" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="18" r="8" fill="white"/>
              <path d="M12 42 Q12 30 24 30 Q36 30 36 42" stroke="white" stroke-width="3" stroke-linecap="round" fill="none"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.total }}</div>
          <div class="stat-label">总患者</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrapper" style="background: var(--gradient-2)">
            <svg class="stat-icon-svg" width="24" height="24" viewBox="0 0 48 48" fill="none">
              <path d="M8 20 L40 20" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <path d="M8 32 L40 32" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <path d="M8 44 L40 44" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <circle cx="20" cy="20" r="4" fill="white"/>
              <circle cx="24" cy="32" r="4" fill="white"/>
              <circle cx="16" cy="44" r="4" fill="white"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.newMonth }}</div>
          <div class="stat-label">本月新增</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrapper" style="background: var(--gradient-3)">
            <svg class="stat-icon-svg" width="24" height="24" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="16" fill="none" stroke="white" stroke-width="3"/>
              <path d="M16 24 L22 30 L32 18" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.rate }}%</div>
          <div class="stat-label">完成率</div>
        </div>
        <div class="stat-card">
          <div class="stat-icon-wrapper" style="background: linear-gradient(135deg, #f59e0b, #d97706)">
            <svg class="stat-icon-svg" width="24" height="24" viewBox="0 0 48 48" fill="none">
              <circle cx="24" cy="24" r="16" fill="none" stroke="white" stroke-width="3"/>
              <path d="M24 10 L24 20" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <path d="M24 38 L24 28" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <path d="M10 24 L20 24" stroke="white" stroke-width="3" stroke-linecap="round"/>
              <path d="M38 24 L28 24" stroke="white" stroke-width="3" stroke-linecap="round"/>
            </svg>
          </div>
          <div class="stat-value">{{ stats.pending }}</div>
          <div class="stat-label">待处理</div>
        </div>
      </div>

      <!-- Filters -->
      <div class="card filter-card">
        <div class="search-row">
          <div class="search-wrap">
            <svg class="search-icon" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
            </svg>
            <input v-model="searchQuery" class="input search-input" placeholder="搜索姓名/电话/诊断..."/>
          </div>
        </div>
        <div class="filter-row">
          <div class="filter-group">
            <button
              v-for="s in statusFilters" :key="s.val"
              class="filter-pill" :class="{active: statusFilter === s.val}"
              @click="statusFilter = s.val"
            >{{ s.label }}</button>
          </div>
        </div>
        <div class="filter-row">
          <div class="filter-group">
            <button v-for="t in timeFilters" :key="t.val" class="filter-pill" :class="{active: timeFilter === t.val}" @click="timeFilter = t.val">{{ t.label }}</button>
          </div>
          <div class="filter-group">
            <button v-for="g in genderFilters" :key="g.val" class="filter-pill" :class="{active: genderFilter === g.val}" @click="genderFilter = g.val">{{ g.label }}</button>
          </div>
        </div>
      </div>

      <!-- Patient List -->
      <div class="patient-list">
        <!-- Loading State -->
        <div v-if="isPageLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>正在加载患者数据...</p>
        </div>
        
        <!-- Error State -->
        <div v-else-if="error" class="error-state">
          <div class="error-icon">
            <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5">
              <circle cx="12" cy="12" r="10"/>
              <line x1="12" y1="8" x2="12" y2="12"/>
              <line x1="12" y1="16" x2="12.01" y2="16"/>
            </svg>
          </div>
          <p>{{ error }}</p>
          <button class="btn btn-secondary btn-sm" @click="loadPatients">重新加载</button>
        </div>
        
        <!-- Empty State -->
        <div v-else-if="filteredPatients.length === 0" class="empty-state">
          <div style="font-size:48px;margin-bottom:12px">🔍</div>
          <p>没有找到匹配的患者</p>
        </div>
        <div
          v-for="patient in filteredPatients"
          :key="patient.id"
          class="patient-card card animate-slide-up"
        >
          <div class="patient-main" @click="toggleExpand(patient.id)">
            <div class="patient-avatar" :style="{background: patient.gender === '男' ? 'linear-gradient(135deg,#2563eb,#7c3aed)' : 'linear-gradient(135deg,#db2777,#7c3aed)'}">
              {{ patient.name[0] }}
            </div>
            <div class="patient-info">
              <div class="patient-row1">
                <span class="patient-name">{{ patient.name }}</span>
                <span class="badge" :class="statusBadge(patient.status)">{{ patient.status }}</span>
              </div>
              <div class="patient-row2">
                <span>{{ patient.gender }} · {{ patient.age }}岁</span>
                <span>{{ patient.phone }}</span>
              </div>
              <div class="patient-row3">
                <span class="badge badge-blue">{{ patient.diagnosis }}</span>
              </div>
            </div>
            <div class="expand-arrow">{{ expandedId === patient.id ? '▲' : '▼' }}</div>
          </div>

          <!-- Actions -->
          <div class="patient-actions">
            <button class="action-btn action-btn-edit" @click.stop="editPatient(patient)" title="编辑">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1 1 4 4"/>
              </svg>
            </button>
            <button class="action-btn" :class="patient.status === '已完成' ? 'action-btn-secondary' : 'action-btn-primary'" @click.stop="toggleStatus(patient)">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              {{ patient.status === '已完成' ? '重置' : '完成' }}
            </button>
            <button class="action-btn action-btn-delete" @click.stop="deletePatient(patient.id)" title="删除">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <polyline points="3 6 5 6 21 6"/>
                <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11a2 2 0 0 1 2 2"/>
              </svg>
            </button>
          </div>

          <!-- Expanded Detail -->
          <Transition name="collapse">
            <div v-if="expandedId === patient.id" class="patient-detail">
              <div class="divider"></div>
              <div class="detail-grid">
                <div class="detail-item"><span class="detail-key">入组日期</span><span class="detail-val">{{ patient.joinDate }}</span></div>
                <div class="detail-item"><span class="detail-key">联系人</span><span class="detail-val">{{ patient.contact || '未设置' }}</span></div>
              </div>
              
              <!-- 诊断信息 -->
              <div class="detail-section">
                <div class="section-header">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M22 12h-4l-3 9l-9-9"/>
                    <path d="M22 12h-6l-2 3m-2 3h6m-6 0h6"/>
                  </svg>
                  <h4>诊断信息</h4>
                </div>
                <div class="detail-diagnosis">
                  <p class="detail-note">{{ patient.diagnosis || '暂无诊断信息' }}</p>
                </div>
              </div>
              
              <!-- 备注信息 -->
              <div class="detail-section">
                <div class="section-header">
                  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                    <line x1="11" y1="23" x2="17" y2="23"/>
                    <line x1="15" y1="13" x2="19" y2="17"/>
                  </svg>
                  <h4>备注信息</h4>
                </div>
                <p class="detail-note">{{ patient.note || '暂无备注信息' }}</p>
              </div>
              
              <!-- 资料上传 -->
              <div class="detail-upload">
                <div class="section-header">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="17 8 12 23 12 15"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  <h4>资料上传</h4>
                </div>
                <p class="detail-hint">为患者上传不同类型的医学资料</p>
                
                <!-- 四个文件上传分类 -->
                <div class="upload-categories" style="margin-top:12px">
                  <!-- 人口学信息 -->
                  <div class="upload-category" :class="{ 'category-uploaded': patient.uploadedFiles?.人口学信息 }">
                    <div class="category-header">
                      <div class="category-icon-svg icon-demographic">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <circle cx="12" cy="8" r="4" fill="white" opacity="0.9"/>
                          <path d="M4 20c0-4.42 3.58-8 8-8s8 3.58 8 8" stroke="white" stroke-width="2" fill="none" stroke-linecap="round" opacity="0.9"/>
                        </svg>
                      </div>
                      <span class="category-name">人口学信息</span>
                      <span v-if="patient.uploadedFiles?.人口学信息" class="upload-badge">已上传</span>
                    </div>
                    <FileUpload 
                      @files-selected="handleCategoryUpload($event, patient.id, '人口学信息')" 
                      :class="{ 'upload-mini': patient.uploadedFiles?.人口学信息 }"
                      style="margin-top:4px"
                    />
                  </div>
                  
                  <!-- 过往手术史 -->
                  <div class="upload-category" :class="{ 'category-uploaded': patient.uploadedFiles?.过往手术史 }">
                    <div class="category-header">
                      <div class="category-icon-svg icon-surgery">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M4 4h6v6H4z" fill="white" opacity="0.9"/>
                          <path d="M14 14h6v6h-6z" fill="white" opacity="0.9"/>
                          <line x1="10" y1="10" x2="14" y2="14" stroke="white" stroke-width="2" opacity="0.9"/>
                          <circle cx="12" cy="12" r="2" fill="white" opacity="0.9"/>
                        </svg>
                      </div>
                      <span class="category-name">过往手术史</span>
                      <span v-if="patient.uploadedFiles?.过往手术史" class="upload-badge">已上传</span>
                    </div>
                    <FileUpload 
                      @files-selected="handleCategoryUpload($event, patient.id, '过往手术史')" 
                      :class="{ 'upload-mini': patient.uploadedFiles?.过往手术史 }"
                      style="margin-top:4px"
                    />
                  </div>
                  
                  <!-- 检查结果 -->
                  <div class="upload-category" :class="{ 'category-uploaded': patient.uploadedFiles?.检查结果 }">
                    <div class="category-header">
                      <div class="category-icon-svg icon-lab">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M6 4h12v2H6z" fill="white" opacity="0.9"/>
                          <path d="M6 8h12v2H6z" fill="white" opacity="0.9"/>
                          <path d="M6 12h12v2H6z" fill="white" opacity="0.9"/>
                          <path d="M6 16h12v2H6z" fill="white" opacity="0.9"/>
                          <circle cx="16" cy="7" r="2" fill="white" opacity="0.9"/>
                          <circle cx="8" cy="13" r="2" fill="white" opacity="0.9"/>
                        </svg>
                      </div>
                      <span class="category-name">检查结果</span>
                      <span v-if="patient.uploadedFiles?.检查结果" class="upload-badge">已上传</span>
                    </div>
                    <FileUpload 
                      @files-selected="handleCategoryUpload($event, patient.id, '检查结果')" 
                      :class="{ 'upload-mini': patient.uploadedFiles?.检查结果 }"
                      style="margin-top:4px"
                    />
                  </div>
                  
                  <!-- 其他 -->
                  <div class="upload-category" :class="{ 'category-uploaded': patient.uploadedFiles?.其他 }">
                    <div class="category-header">
                      <div class="category-icon-svg icon-other">
                        <svg viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                          <path d="M4 4h16v16H4z" stroke="white" stroke-width="2" fill="none" opacity="0.9"/>
                          <path d="M8 8h2v2H8z" fill="white" opacity="0.9"/>
                          <path d="M14 8h2v2h-2z" fill="white" opacity="0.9"/>
                          <path d="M8 14h2v2H8z" fill="white" opacity="0.9"/>
                          <path d="M14 14h2v2h-2z" fill="white" opacity="0.9"/>
                        </svg>
                      </div>
                      <span class="category-name">其他</span>
                      <span v-if="patient.uploadedFiles?.其他" class="upload-badge">已上传</span>
                    </div>
                    <FileUpload 
                      @files-selected="handleCategoryUpload($event, patient.id, '其他')" 
                      :class="{ 'upload-mini': patient.uploadedFiles?.其他 }"
                      style="margin-top:4px"
                    />
                  </div>
                </div>
              </div>
              
              <!-- 操作按钮 -->
              <div class="detail-actions">
                <button class="btn btn-sm btn-secondary" @click="downloadPatientData(patient)">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                  </svg>
                  导出患者数据
                </button>
              </div>
            </div>
          </Transition>
        </div>
      </div>
    </div>
    
    <!-- OCR结果展示区域 -->
    <div v-if="uploadResult" class="result-section">
      <div class="result-header">
        <span class="result-title">上传结果</span>
        <button class="result-close" @click="uploadResult = null">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <line x1="18" y1="6" x2="6" y2="18"/>
            <line x1="6" y1="6" x2="18" y2="18"/>
          </svg>
        </button>
      </div>
      
      <!-- 始终显示简单的成功消息 -->
      <div class="card result-card">
        <div style="display: flex; align-items: flex-start; gap: 12px;">
          <span class="result-icon" style="font-size: 24px;">
            {{ uploadResult.success ? '✅' : '❌' }}
          </span>
          <div style="flex: 1;">
            <h4 style="margin: 0 0 4px 0; color: var(--text-primary);">
              {{ uploadResult.success ? '上传成功' : '上传失败' }}
            </h4>
            <p style="margin: 0 0 8px 0; color: var(--text-secondary); font-size: 13px;">
              {{ uploadResult.message }}
            </p>
            
            <!-- 显示详细错误信息 -->
            <div v-if="uploadResult.ocr_errors && uploadResult.ocr_errors.length > 0" 
                 style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 10px 12px; border-radius: 4px; margin-bottom: 8px;">
              <div style="font-size: 12px; color: #7f1d1d; font-weight: 600; margin-bottom: 6px;">
                ❌ OCR识别质量问题
              </div>
              <div v-for="(error, index) in uploadResult.ocr_errors" :key="'ocr-error-' + index" 
                   style="font-size: 12px; color: #991b1b; margin: 2px 0;">
                • {{ error }}
              </div>
              <div style="font-size: 11px; color: #6b7280; margin-top: 6px; padding-top: 6px; border-top: 1px solid rgba(239, 68, 68, 0.1);">
                💡 建议：请检查原始图片质量或重新上传
              </div>
            </div>
            
            <!-- 显示验证错误信息 -->
            <div v-if="uploadResult.validation_errors && uploadResult.validation_errors.length > 0" 
                 style="background: rgba(239, 68, 68, 0.1); border-left: 3px solid #ef4444; padding: 10px 12px; border-radius: 4px; margin-bottom: 8px;">
              <div style="font-size: 12px; color: #7f1d1d; font-weight: 600; margin-bottom: 6px;">
                ❌ 数据验证错误
              </div>
              <div v-for="(error, index) in uploadResult.validation_errors" :key="'val-error-' + index" 
                   style="font-size: 12px; color: #991b1b; margin: 2px 0;">
                • {{ error }}
              </div>
            </div>
            
            <!-- 显示警告信息 -->
            <div v-if="uploadResult.ocr_warnings && uploadResult.ocr_warnings.length > 0" 
                 style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 10px 12px; border-radius: 4px; margin-bottom: 8px;">
              <div style="font-size: 12px; color: #78350f; font-weight: 600; margin-bottom: 6px;">
                ⚠️ OCR质量警告
              </div>
              <div v-for="(warning, index) in uploadResult.ocr_warnings" :key="'ocr-warning-' + index" 
                   style="font-size: 12px; color: #92400e; margin: 2px 0;">
                • {{ warning }}
              </div>
            </div>
            
            <div v-if="uploadResult.validation_warnings && uploadResult.validation_warnings.length > 0" 
                 style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 10px 12px; border-radius: 4px; margin-bottom: 8px;">
              <div style="font-size: 12px; color: #78350f; font-weight: 600; margin-bottom: 6px;">
                ⚠️ 数据验证警告
              </div>
              <div v-for="(warning, index) in uploadResult.validation_warnings" :key="'val-warning-' + index" 
                   style="font-size: 12px; color: #92400e; margin: 2px 0;">
                • {{ warning }}
              </div>
            </div>
            
            <!-- 显示成功提示 -->
            <div v-if="uploadResult.import_messages && uploadResult.import_messages.length > 0" 
                 style="background: rgba(16, 185, 129, 0.1); border-left: 3px solid #10b981; padding: 10px 12px; border-radius: 4px; margin-bottom: 8px;">
              <div style="font-size: 12px; color: #065f46; font-weight: 600; margin-bottom: 6px;">
                ✅ 导入结果
              </div>
              <div v-for="(msg, index) in uploadResult.import_messages" :key="'import-msg-' + index" 
                   style="font-size: 12px; color: #064e3b; margin: 2px 0;">
                • {{ msg }}
              </div>
            </div>
            
            <!-- 显示通用警告 -->
            <div v-if="uploadResult.warnings && uploadResult.warnings.length > 0" 
                 style="background: rgba(245, 158, 11, 0.1); border-left: 3px solid #f59e0b; padding: 10px 12px; border-radius: 4px;">
              <div style="font-size: 12px; color: #78350f; font-weight: 600; margin-bottom: 6px;">
                ⚠️ 提示
              </div>
              <div v-for="(warning, index) in uploadResult.warnings" :key="'warning-' + index" 
                   style="font-size: 12px; color: #92400e; margin: 2px 0;">
                • {{ warning }}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 使用 LoadingOverLay 组件显示上传进度 -->
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

    <!-- Add Modal -->
    <Teleport to="body">
      <div v-if="showAddModal" class="modal-overlay" @click.self="showAddModal = false">
        <div class="modal-card animate-slide-up">
          <div class="modal-header">
            <h3>添加患者</h3>
            <button class="btn btn-icon" @click="showAddModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">姓名 <span class="required">*</span></label>
              <input v-model="newPatient.name" class="input" placeholder="患者姓名"/>
            </div>
            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">性别 <span class="required">*</span></label>
                <select v-model="newPatient.gender" class="input">
                  <option>男</option><option>女</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">年龄 <span class="required">*</span></label>
                <input v-model="newPatient.age" class="input" type="number" placeholder="年龄"/>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">电话 <span class="required">*</span></label>
              <input v-model="newPatient.phone" class="input" placeholder="联系电话"/>
            </div>
            <div class="form-group">
              <label class="form-label">证件号码 <span class="required">*</span></label>
              <input v-model="newPatient.idNumber" class="input" placeholder="身份证号/护照号等"/>
            </div>
            <div class="form-group">
              <label class="form-label">诊断</label>
              <input v-model="newPatient.diagnosis" class="input" placeholder="主要诊断"/>
            </div>
            <div class="form-group">
              <label class="form-label">备注</label>
              <textarea v-model="newPatient.note" class="input" placeholder="填写备注信息..." rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showAddModal = false">取消</button>
            <button class="btn btn-primary" @click="addPatient">确认添加</button>
          </div>
        </div>
      </div>
    </Teleport>

    <!-- Edit Modal -->
    <Teleport to="body">
      <div v-if="showEditModal" class="modal-overlay" @click.self="showEditModal = false">
        <div class="modal-card animate-slide-up">
          <div class="modal-header">
            <h3>编辑患者信息</h3>
            <button class="btn btn-icon" @click="showEditModal = false">✕</button>
          </div>
          <div class="modal-body">
            <div class="form-group">
              <label class="form-label">姓名 <span class="required">*</span></label>
              <input v-model="editingPatient.name" class="input" placeholder="患者姓名"/>
            </div>
            <div class="grid-2">
              <div class="form-group">
                <label class="form-label">性别 <span class="required">*</span></label>
                <select v-model="editingPatient.gender" class="input">
                  <option>男</option><option>女</option>
                </select>
              </div>
              <div class="form-group">
                <label class="form-label">年龄 <span class="required">*</span></label>
                <input v-model="editingPatient.age" class="input" type="number" placeholder="年龄"/>
              </div>
            </div>
            <div class="form-group">
              <label class="form-label">电话 <span class="required">*</span></label>
              <input v-model="editingPatient.phone" class="input" placeholder="联系电话"/>
            </div>
            <div class="form-group">
              <label class="form-label">证件号码 <span class="required">*</span></label>
              <input v-model="editingPatient.idNumber" class="input" placeholder="身份证号/护照号等"/>
            </div>
            <div class="form-group">
              <label class="form-label">诊断</label>
              <input v-model="editingPatient.diagnosis" class="input" placeholder="主要诊断"/>
            </div>
            <div class="form-group">
              <label class="form-label">备注</label>
              <textarea v-model="editingPatient.note" class="input" placeholder="填写备注信息..." rows="3"></textarea>
            </div>
          </div>
          <div class="modal-footer">
            <button class="btn btn-secondary" @click="showEditModal = false">取消</button>
            <button class="btn btn-primary" @click="savePatientEdit">保存修改</button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import FileUpload from '../components/Fileupload.vue'
import LoadingOverLay from '../components/LoadingOverLay.vue'
import AgentResultDisplay from '../components/AgentResultDisplay.vue'
import MultiFileUpload from '../components/MultiFileUpload.vue'

const API_BASE_URL = 'http://localhost:8000'

// 从 localStorage 获取 token，与路由守卫保持一致
const getToken = () => {
  return localStorage.getItem('token') || localStorage.getItem('access_token')
}

// 上传状态管理（新增）
const loadingProgress = ref(0)
const loadingMessage = ref('')
const uploadResult = ref<any>(null)
const uploadStatus = ref('')

interface Patient {
  id: number
  name: string
  gender: string
  age: number
  phone: string
  idNumber: string
  diagnosis: string
  status: string
  joinDate: string
  nextVisit: string
  visitCount: number
  contact: string
  note: string
  uploadedFiles: {
    人口学信息: boolean
    过往手术史: boolean
    检查结果: boolean
    其他: boolean
  }
}

const patients = ref<Patient[]>([])
const searchQuery = ref('')
const statusFilter = ref('all')
const timeFilter = ref('all')
const genderFilter = ref('all')
const expandedId = ref<number | null>(null)
const showAddModal = ref(false)
const showEditModal = ref(false)
const newPatient = ref({ name: '', gender: '男', age: '', phone: '', idNumber: '', diagnosis: '', note: '' })
const editingPatient = ref<Patient>({
  id: 0,
  name: '',
  gender: '男',
  age: 0,
  phone: '',
  idNumber: '',
  diagnosis: '',
  status: '待处理',
  joinDate: '',
  nextVisit: '',
  visitCount: 0,
  contact: '',
  note: ''
})
const editingPatientId = ref<number | null>(null)
const isLoading = ref(false) // 用于文件上传加载状态
const isPageLoading = ref(false) // 用于页面数据加载状态
const error = ref('')

const statusFilters = [
  { val: 'all', label: '全部' },
  { val: '待处理', label: '待处理' },
  { val: '已完成', label: '已完成' },
]
const timeFilters = [
  { val: 'all', label: '全部' },
  { val: 'today', label: '今天' },
  { val: 'week', label: '本周' },
  { val: 'month', label: '本月' },
]
const genderFilters = [
  { val: 'all', label: '全部' },
  { val: '男', label: '男' },
  { val: '女', label: '女' },
]

const stats = computed(() => ({
  total: patients.value.length,
  newMonth: patients.value.filter(p => {
    const now = new Date()
    const joinDate = new Date(p.joinDate)
    return joinDate.getMonth() === now.getMonth() && joinDate.getFullYear() === now.getFullYear()
  }).length,
  rate: patients.value.length > 0 ? Math.round(patients.value.filter(p => p.status === '已完成').length / patients.value.length * 100) : 0,
  pending: patients.value.filter(p => p.status === '待处理').length,
}))

const filteredPatients = computed(() => {
  return patients.value.filter(p => {
    const q = searchQuery.value.toLowerCase()
    const matchSearch = !q || p.name.toLowerCase().includes(q) || p.phone.includes(q) || p.diagnosis.toLowerCase().includes(q)
    const matchStatus = statusFilter.value === 'all' || p.status === statusFilter.value
    const matchGender = genderFilter.value === 'all' || p.gender === genderFilter.value
    return matchSearch && matchStatus && matchGender
  })
})

// 从后端加载患者列表
const loadPatients = async () => {
  try {
    isPageLoading.value = true
    error.value = ''
    
    console.log('[DEBUG] 开始加载患者列表')
    
    // 从 localStorage 获取 token，与路由守卫保持一致
    const authToken = getToken()
    
    console.log('[DEBUG] Token 类型:', typeof authToken)
    console.log('[DEBUG] Token 长度:', authToken?.length || 0)
    console.log('[DEBUG] Token 前20字符:', authToken ? authToken.substring(0, 20) : 'None')
    
    if (!authToken || typeof authToken !== 'string') {
      error.value = '未登录或登录已过期，请重新登录'
      console.error('[DEBUG] Token 无效:', authToken)
      console.error('[DEBUG] localStorage 状态:', {
        token: !!localStorage.getItem('token'),
        access_token: !!localStorage.getItem('access_token'),
        currentUser: !!localStorage.getItem('currentUser'),
        user: !!localStorage.getItem('user')
      })
      isPageLoading.value = false
      return
    }
    
    if (authToken.length < 10) {
      error.value = '登录信息无效，请重新登录'
      console.error('[DEBUG] Token 长度过短:', authToken.length)
      isPageLoading.value = false
      return
    }
    
    console.log('[DEBUG] Token 验证通过，开始请求')
    
    const response = await fetch(`${API_BASE_URL}/api/patients`, {
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    })
    
    console.log('[DEBUG] Fetch 请求完成，响应状态:', response.status)
    console.log('[DEBUG] 响应类型:', response.type)
    console.log('[DEBUG] 响应OK:', response.ok)
    
    if (!response.ok) {
      console.error('[DEBUG] HTTP 错误:', response.status, response.statusText)
      throw new Error(`HTTP ${response.status}: ${response.statusText}`)
    }
    
    const result = await response.json()
    
    console.log('[DEBUG] 响应状态:', response.status)
    console.log('[DEBUG] 响应数据:', result)
    console.log('[DEBUG] result.success:', result.success)
    console.log('[DEBUG] result.patients:', result.patients)
    
    if (result.success && result.patients) {
      // 转换为 Patient 格式
      const convertedPatients: Patient[] = result.patients
        .filter((p: any) => p.patientInfo) // 只返回有信息的患者
        .map((p: any, index: number) => {
          const info = p.patientInfo
          const componentTypes = p.componentTypes || []
          
          // 根据 componentTypes 判断文件上传状态
          const uploadedFiles = {
            人口学信息: componentTypes.includes('人口学信息'),
            过往手术史: componentTypes.includes('过往手术史'),
            检查结果: componentTypes.includes('检查结果'),
            其他: componentTypes.includes('其他')
          }
          
          const converted = {
            id: info.id || (index + 1), // 优先使用数据库ID，否则使用索引
            name: info.patientName || '未知',
            gender: info.gender === 'male' ? '男' : (info.gender === 'female' ? '女' : '未知'),
            age: parseInt(info.age) || 0,
            phone: info.phone || '',
            idNumber: info.idNumber || '',
            diagnosis: info.preliminaryDiagnosis || '未诊断',
            status: info.status || '待处理',
            joinDate: info.createTime ? new Date(info.createTime).toISOString().split('T')[0] : new Date().toISOString().split('T')[0],
            nextVisit: '',
            visitCount: p.fileCount || 0, // 使用文件数量作为访问次数
            contact: info.creator || '',
            note: info.notes || '',
            // 根据后端返回的 componentTypes 设置文件上传状态
            uploadedFiles: uploadedFiles
          }
          console.log('[DEBUG] 转换后的患者数据:', converted)
          console.log('[DEBUG] componentTypes:', componentTypes)
          console.log('[DEBUG] uploadedFiles:', uploadedFiles)
          return converted
        })
      
      // 对患者列表进行排序：待处理的患者排在已完成的患者前面
      const pendingPatients = convertedPatients.filter(p => p.status !== '已完成')
      const completedPatients = convertedPatients.filter(p => p.status === '已完成')
      patients.value = [...pendingPatients, ...completedPatients]
      
      console.log('加载患者列表成功:', patients.value.length, '个患者')
      console.log('最终患者数据:', patients.value)
      console.log('统计数据:', {
        total: patients.value.length,
        newMonth: patients.value.filter(p => {
          const now = new Date()
          const joinDate = new Date(p.joinDate)
          return joinDate.getMonth() === now.getMonth() && joinDate.getFullYear() === now.getFullYear()
        }).length,
        rate: patients.value.length > 0 ? Math.round(patients.value.filter(p => p.status === '已完成').length / patients.value.length * 100) : 0,
        pending: patients.value.filter(p => p.status === '待处理').length,
      })
      console.log('患者数据:', patients.value)
    } else {
      console.error('[DEBUG] 加载患者列表失败 - 响应不成功')
      console.error('[DEBUG] result.success:', result.success)
      console.error('[DEBUG] result.message:', result.message)
      console.error('[DEBUG] 完整响应:', result)
      
      if (response.status === 401) {
        error.value = '认证失败，请重新登录'
      } else if (response.status === 403) {
        error.value = '权限不足，无法访问患者数据'
      } else if (response.status === 404) {
        error.value = '患者接口不存在'
      } else {
        error.value = result.message || '加载患者列表失败'
      }
    }
  } catch (err) {
    console.error('[DEBUG] 加载患者列表异常:', err)
    const errorMsg = (err as Error).message
    console.error('[DEBUG] 错误详情:', errorMsg)
    console.error('[DEBUG] 错误堆栈:', (err as Error).stack)
    
    if (errorMsg.includes('fetch') || errorMsg.includes('network') || errorMsg.includes('Failed to fetch')) {
      error.value = '检查网络连接'
    } else if (errorMsg.includes('401') || errorMsg.includes('403')) {
      error.value = '认证失败，请重新登录'
    } else if (errorMsg.includes('404')) {
      error.value = '接口不存在，请联系管理员'
    } else if (errorMsg.includes('500')) {
      error.value = '服务器错误，请稍后重试'
    } else {
      error.value = `加载失败: ${errorMsg}`
    }
  } finally {
    isPageLoading.value = false
  }
}

// 页面加载时获取患者数据
onMounted(() => {
  loadPatients()
})

function statusBadge(status: string) {
  return status === '已完成' ? 'badge-green' : 'badge-yellow'
}

function toggleExpand(id: number) {
  if (expandedId.value === id) {
    // 如果点击的是已展开的卡片，则收起
    expandedId.value = null
  } else {
    // 否则展开该卡片，并收起其他卡片
    expandedId.value = id
    
    // 获取患者信息用于日志
    const patient = patients.value.find(p => p.id === id)
    if (patient) {
      console.log('展开患者:', patient.name)
      console.log('患者上传状态:', patient.uploadedFiles)
      console.log('完整患者数据:', patient)
    }
    
    // TODO: 从后端加载该患者的文件信息
  }
}

async function toggleStatus(patient: Patient) {
  try {
    // 获取token
    const token = getToken()
    if (!token) {
      alert('未登录或登录已过期')
      return
    }
    
    if (patient.status === '已完成') {
      // 从已完成重置为待处理
      patient.status = '待处理'
      console.log('状态变更:', patient.name, '已完成 → 待处理')
      
      // 调用后端API更新状态
      await updatePatientStatus(patient.name, '待处理', token)
    } else {
      // 从待处理设置为已完成
      patient.status = '已完成'
      console.log('状态变更:', patient.name, '待处理 → 已完成')
      
      // 调用后端API更新状态
      await updatePatientStatus(patient.name, '已完成', token)
    }
  } catch (error) {
    console.error('更新状态失败:', error)
    alert('更新状态失败: ' + (error as Error).message)
    // 恢复原状态
    patient.status = patient.status === '已完成' ? '待处理' : '已完成'
  }
}

async function updatePatientStatus(patientName: string, status: string, token: string) {
  try {
    // 直接从本地患者列表中获取患者信息
    const patient = patients.value.find(p => p.name === patientName)
    if (!patient) {
      alert('患者信息不存在')
      return
    }

    // 构建更新数据，使用本地患者信息
    const updatedData = {
      patientName: patient.name,
      patientId: patient.name, // 使用患者姓名作为ID
      gender: patient.gender === '男' ? 'male' : 'female',
      age: String(patient.age),
      phone: patient.phone,
      idNumber: patient.idNumber || '',
      preliminaryDiagnosis: patient.diagnosis || '',
      createTime: patient.joinDate || new Date().toISOString(),
      creator: 'current_user', // 临时值，后端会处理
      notes: patient.note || '',
      status: status
    }

    // 调用更新API
    const updateResponse = await fetch(`${API_BASE_URL}/api/patient/${encodeURIComponent(patientName)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify(updatedData)
    })

    const updateResult = await updateResponse.json()

    if (updateResult.success) {
      console.log('状态更新成功:', patientName, status)
    } else {
      throw new Error(updateResult.message || '更新状态失败')
    }
  } catch (error) {
    throw error
  }
}

async function deletePatient(id: number) {
  const patient = patients.value.find(p => p.id === id)
  if (!patient) return
  
  if (confirm(`确认删除患者"${patient.name}"？\n姓名: ${patient.name}\n电话: ${patient.phone}\n\n此操作不可恢复！`)) {
    try {
      // 获取token
      const token = getToken()
      if (!token) {
        alert('未登录或登录已过期')
        return
      }
      
      // 调用后端API删除患者
      const deleteResponse = await fetch(`${API_BASE_URL}/api/patient/${encodeURIComponent(patient.name)}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      })
      
      const deleteResult = await deleteResponse.json()
      
      if (deleteResult.success) {
        // 从本地列表中删除
        patients.value = patients.value.filter(p => p.id !== id)
        console.log('删除患者成功:', patient.name)
        alert('患者删除成功')
      } else {
        alert('删除患者失败: ' + (deleteResult.message || '未知错误'))
      }
    } catch (error) {
      console.error('删除患者异常:', error)
      alert('删除患者失败: ' + (error as Error).message)
    }
  }
}

function editPatient(patient: Patient) {
  // 填充编辑表单数据
  editingPatient.value = {
    id: patient.id,
    name: patient.name,
    gender: patient.gender,
    age: patient.age,
    phone: patient.phone,
    idNumber: patient.idNumber || '',
    diagnosis: patient.diagnosis,
    status: patient.status,
    joinDate: patient.joinDate,
    nextVisit: patient.nextVisit,
    visitCount: patient.visitCount,
    contact: patient.contact,
    note: patient.note
  }
  editingPatientId.value = patient.id
  showEditModal.value = true
}

// 导出患者数据
async function downloadPatientData(patient: Patient) {
  console.log('导出患者数据:', patient.name, 'ID:', patient.id)
  
  try {
    const authToken = getToken()
    
    if (!authToken) {
      alert('未登录或登录已过期，请重新登录')
      return
    }
    
    // 调用后端API导出CSV
    const response = await fetch(`${API_BASE_URL}/api/patient/${patient.id}/export-csv`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${authToken}`
      }
    })
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({ detail: response.statusText }))
      throw new Error(errorData.detail || `导出失败: ${response.statusText}`)
    }
    
    // 获取文件名（从响应头中提取）
    const contentDisposition = response.headers.get('Content-Disposition')
    let filename = `${patient.name}_全部数据_${new Date().toISOString().split('T')[0]}.csv`
    
    if (contentDisposition) {
      const filenameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (filenameMatch && filenameMatch[1]) {
        filename = filenameMatch[1].replace(/['"]/g, '')
      }
    }
    
    // 下载文件
    const blob = await response.blob()
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    console.log('患者数据已导出:', filename)
    alert(`成功导出患者数据：${filename}`)
    
  } catch (error: any) {
    console.error('导出患者数据失败:', error)
    alert(`导出患者数据失败：${error.message || '未知错误'}`)
  }
}

async function addPatient() {
  // 必填项验证
  if (!newPatient.value.name || !newPatient.value.name.trim()) {
    alert('请填写患者姓名')
    return
  }
  if (newPatient.value.age === '' || newPatient.value.age === null || newPatient.value.age === undefined) {
    alert('请填写年龄')
    return
  }
  if (!newPatient.value.phone || !newPatient.value.phone.trim()) {
    alert('请填写联系电话')
    return
  }
  if (!newPatient.value.idNumber || !newPatient.value.idNumber.trim()) {
    alert('请填写证件号码')
    return
  }
  
  try {
    // 从token获取当前用户信息
    const token = getToken()
    let creator = '未知用户'
    
    if (token) {
      try {
        // 简单的JWT解码（仅用于获取用户名，不验证签名）
        const parts = token.split('.')
        if (parts.length >= 2 && parts[1]) {
          const payload = JSON.parse(atob(parts[1]))
          creator = payload.sub || '未知用户'
        }
      } catch (e) {
        console.error('解析token失败:', e)
      }
    }
    
    // 获取当前时间戳
    const createTime = new Date().toISOString()
    
    // 调用后端API创建患者
    const response = await fetch(`${API_BASE_URL}/api/patient`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        patientName: newPatient.value.name,
        patientId: newPatient.value.idNumber || '',
        gender: newPatient.value.gender === '男' ? 'male' : 'female',
        age: String(newPatient.value.age || '0'),
        phone: newPatient.value.phone || '',
        idNumber: newPatient.value.idNumber || '',
        preliminaryDiagnosis: newPatient.value.diagnosis || '',
        createTime: createTime,
        creator: creator,
        notes: newPatient.value.note || '',
        status: '待处理'
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      // 添加到本地列表
      patients.value.unshift({
        id: Date.now(),
        name: newPatient.value.name,
        gender: newPatient.value.gender,
        age: Number(newPatient.value.age || 0) || 0,
        phone: newPatient.value.phone || '',
        idNumber: newPatient.value.idNumber || '',
        diagnosis: newPatient.value.diagnosis || '',
        status: '待处理',
        joinDate: (createTime.split('T')[0] as string) || (new Date().toISOString().split('T')[0] as string),
        nextVisit: '',
        visitCount: 0,
        contact: creator,
        note: newPatient.value.note || '',
        // 初始化文件上传状态
        uploadedFiles: {
          人口学信息: false,
          过往手术史: false,
          检查结果: false,
          其他: false
        }
      })
      
      // 重置表单
      newPatient.value = { name: '', gender: '男', age: '', phone: '', idNumber: '', diagnosis: '', note: '' }
      showAddModal.value = false
      
      console.log('患者创建成功:', result)
    } else {
      alert('创建患者失败: ' + (result.message || '未知错误'))
    }
  } catch (err) {
    console.error('创建患者异常:', err)
    alert('创建患者失败: ' + (err as Error).message)
  }
}

function handlePatientFiles(files: File[], patientId: number) {
  console.log('Files for patient', patientId, files)
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

async function handleCategoryUpload(files: File[], patientId: number, category: string) {
  try {
    // 获取患者信息
    const patient = patients.value.find(p => p.id === patientId)
    if (!patient) {
      alert('患者信息不存在')
      return
    }

    // 获取token
    const token = getToken()
    if (!token) {
      alert('未登录或登录已过期')
      return
    }

    console.log(`开始上传 ${category} 文件，患者: ${patient.name}`, files)
    
    // 开始加载状态
    isLoading.value = true
    uploadStatus.value = '正在上传文件...'
    uploadResult.value = null
    
    // 检查是否有文件
    if (!files || files.length === 0) {
      isLoading.value = false
      uploadStatus.value = '❌ 请选择要上传的文件'
      alert('请选择要上传的文件')
      return
    }
    
    // 启动进度模拟
    const progressInterval = startProgressSimulation()

    // 使用新的多文件上传接口
    const formData = new FormData()
    formData.append('patient_id', patientId.toString())
    formData.append('data_category', category)
    formData.append('model_type', 'cloud')  // 使用云端模型
    
    // 从localStorage读取用户设置的模型
    const userVisionModel = localStorage.getItem('vision_model') || ''
    const userLlmModel = localStorage.getItem('llm_model') || ''
    
    if (userVisionModel) {
      formData.append('vision_model', userVisionModel)
      console.log(`使用用户设置的视觉模型: ${userVisionModel}`)
    }
    
    if (userLlmModel) {
      formData.append('llm_model', userLlmModel)
      console.log(`使用用户设置的语言模型: ${userLlmModel}`)
    }
    
    // 添加所有文件
    files.forEach(file => {
      console.log(`添加文件到FormData: ${file.name}, size: ${file.size}, type: ${file.type}`)
      formData.append('files', file)
    })

    console.log(`准备发送请求: patient_id=${patientId}, category=${category}, files数量=${files.length}`)

    const response = await fetch(`${API_BASE_URL}/api/multi-file-upload`, {
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

    console.log(`[DEBUG] 服务器响应:`, result)

    if (result.success) {
      loadingMessage.value = '上传完成，正在处理OCR...'
      
      // 立即更新本地患者的文件上传状态
      if (!patient.uploadedFiles) {
        patient.uploadedFiles = {
          人口学信息: false,
          过往手术史: false,
          检查结果: false,
          其他: false
        }
      }
      
      // 更新对应类别的上传状态
      if (category === '人口学信息') {
        patient.uploadedFiles.人口学信息 = true
      } else if (category === '过往手术史') {
        patient.uploadedFiles.过往手术史 = true
      } else if (category === '检查结果') {
        patient.uploadedFiles.检查结果 = true
      } else if (category === '其他') {
        patient.uploadedFiles.其他 = true
      }
      
      console.log(`[DEBUG] 更新患者 ${patient.name} 的上传状态:`, patient.uploadedFiles)
      
      // 使用 nextTick 确保 UI 立即更新
      await nextTick()
      
      setTimeout(async () => {
        isLoading.value = false
        
        // 检查上传结果
        const uploadedCount = result.uploaded_files?.length || 0
        const processingCount = result.uploaded_files?.filter((f: any) => f.is_image).length || 0
        
        if (processingCount > 0) {
          uploadStatus.value = `✅ 成功上传 ${uploadedCount} 个文件，${processingCount} 个文件正在进行OCR处理...`
        } else {
          uploadStatus.value = `✅ 成功上传 ${uploadedCount} 个文件`
        }
        
        // 构建结果信息
        uploadResult.value = {
          success: true,
          message: result.message,
          patient_id: patientId,
          patient_name: patient.name,
          data_category: category,
          uploaded_files: result.uploaded_files || [],
          total_files: uploadedCount,
          processing_files: processingCount
        }
        
        // 5秒后刷新文件列表（OCR可能已经完成）
        setTimeout(() => {
          loadPatients() // 刷新患者列表
          
          // 如果有图片文件，轮询获取文件状态和错误信息
          if (processingCount > 0) {
            const imageFileIds = result.uploaded_files
              .filter((f: any) => f.is_image)
              .map((f: any) => f.file_id)
            
            // 轮询获取文件状态（持续30秒，每3秒一次）
            const pollFileStatus = async (attempts = 0) => {
              console.log(`[DEBUG] 开始轮询文件状态，第 ${attempts + 1} 次`)
              
              if (attempts >= 10) {
                console.log(`[DEBUG] 轮询达到最大次数，停止轮询`)
                return // 最多轮询10次（30秒）
              }
              
              try {
                let hasErrors = false
                let allCompleted = true
                
                for (const fileId of imageFileIds) {
                  const statusResponse = await fetch(`${API_BASE_URL}/api/files/${fileId}/status`, {
                    headers: { 'Authorization': `Bearer ${getToken()}` }
                  })
                  
                  if (statusResponse.ok) {
                    const statusData = await statusResponse.json()
                    console.log(`[DEBUG] 文件 ${fileId} 状态:`, statusData)
                    
                    // 检查是否有错误
                    if (statusData.ocr_error || statusData.import_error) {
                      console.log(`[DEBUG] 文件 ${fileId} 处理失败:`, statusData)
                      hasErrors = true
                      
                      // 更新上传结果显示错误信息
                      uploadResult.value = {
                        ...uploadResult.value,
                        success: false,
                        message: "文件处理失败",
                        ocr_errors: statusData.errors || [],
                        ocr_warnings: statusData.suggestions || [],
                        validation_errors: statusData.import_error ? [statusData.import_error] : [],
                        import_messages: []
                      }
                    } else if (statusData.ocr_status === 'completed' && statusData.import_status === 'imported') {
                      console.log(`[DEBUG] 文件 ${fileId} 处理成功`)
                      
                      // 文件处理成功，更新上传结果显示成功信息
                      uploadResult.value = {
                        ...uploadResult.value,
                        success: true,
                        message: "文件上传并处理成功",
                        import_messages: uploadResult.value.import_messages || []
                      }
                      uploadResult.value.import_messages.push("OCR识别成功，数据已导入数据库")
                    } else {
                      // 文件还在处理中
                      allCompleted = false
                      console.log(`[DEBUG] 文件 ${fileId} 还在处理中，状态: ocr_status=${statusData.ocr_status}, import_status=${statusData.import_status}`)
                    }
                  }
                }
                
                // 如果所有文件都处理完成或有错误，停止轮询
                if (hasErrors || allCompleted) {
                  console.log(`[DEBUG] 所有文件处理完成或发现错误，停止轮询`)
                  return
                }
                
                // 继续轮询
                setTimeout(() => pollFileStatus(attempts + 1), 3000)
              } catch (error) {
                console.error('获取文件状态失败:', error)
              }
            }
            
            // 启动轮询
            console.log(`[DEBUG] 启动文件状态轮询，文件ID列表:`, imageFileIds)
            pollFileStatus()
          }
        }, 5000)
        
      }, 1000)
    } else {
      isLoading.value = false
      uploadStatus.value = '❌ 上传失败'
      uploadResult.value = {
        success: false,
        message: result.message || '上传失败',
        error: result
      }
      alert('上传失败: ' + (result.message || '未知错误'))
    }
  } catch (error) {
    console.error('上传失败:', error)
    isLoading.value = false
    uploadStatus.value = '❌ 上传失败'
    uploadResult.value = {
      success: false,
      message: '上传失败',
      error: error
    }
    alert('上传失败: ' + error)
  }
}

async function savePatientEdit() {
  if (!editingPatientId.value) return
  
  // 必填项验证
  if (!editingPatient.value.name || !editingPatient.value.name.trim()) {
    alert('请填写患者姓名')
    return
  }
  if (!editingPatient.value.age || editingPatient.value.age <= 0) {
    alert('请填写有效的年龄')
    return
  }
  if (!editingPatient.value.phone || !editingPatient.value.phone.trim()) {
    alert('请填写联系电话')
    return
  }
  if (!editingPatient.value.idNumber || !editingPatient.value.idNumber.trim()) {
    alert('请填写证件号码')
    return
  }
  
  try {
    // 查找并更新患者信息
    const index = patients.value.findIndex(p => p.id === editingPatientId.value)
    if (index === -1) {
      alert('患者信息不存在')
      return
    }
    
    const existingPatient = patients.value[index]
    if (!existingPatient) {
      alert('患者信息不存在')
      return
    }
    
    // 获取token
    const token = getToken()
    if (!token) {
      alert('未登录或登录已过期')
      return
    }
    
    // 调用后端API更新患者信息
    const response = await fetch(`${API_BASE_URL}/api/patient/${encodeURIComponent(existingPatient.name)}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        patientName: editingPatient.value.name,
        patientId: editingPatient.value.idNumber || '',
        gender: editingPatient.value.gender === '男' ? 'male' : 'female',
        age: String(editingPatient.value.age),
        phone: editingPatient.value.phone || '',
        idNumber: editingPatient.value.idNumber || '',
        preliminaryDiagnosis: editingPatient.value.diagnosis || '',
        createTime: existingPatient.joinDate ? new Date(existingPatient.joinDate).toISOString() : new Date().toISOString(),
        creator: existingPatient.contact || '',
        notes: editingPatient.value.note || ''
      })
    })
    
    const result = await response.json()
    
    if (result.success) {
      // 更新本地列表
      patients.value[index] = {
        id: existingPatient.id,
        name: editingPatient.value.name,
        gender: editingPatient.value.gender,
        age: editingPatient.value.age,
        phone: editingPatient.value.phone,
        idNumber: editingPatient.value.idNumber,
        diagnosis: editingPatient.value.diagnosis,
        note: editingPatient.value.note,
        status: existingPatient.status,
        joinDate: existingPatient.joinDate,
        nextVisit: existingPatient.nextVisit,
        visitCount: existingPatient.visitCount,
        contact: existingPatient.contact
      }
      
      console.log('患者信息已更新:', patients.value[index].name)
      alert('患者信息更新成功！')
      
      // 重新加载患者列表以确保数据同步
      await loadPatients()
      
      // 关闭编辑模态框
      showEditModal.value = false
      editingPatientId.value = null
    } else {
      alert('更新患者信息失败: ' + (result.message || '未知错误'))
    }
  } catch (error) {
    console.error('更新患者信息异常:', error)
    alert('更新患者信息失败: ' + (error as Error).message)
  }
}
</script>

<style scoped>
.stats-row { display: flex; gap: 8px; margin-bottom: 16px; }
.stats-row .stat-card { text-align: center; flex: 1; background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius-md); padding: 16px 12px; transition: all 0.3s ease; position: relative; overflow: hidden; }
.stat-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-md); border-color: var(--border-hover); }
.stat-card::before { content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px; background: var(--gradient-1); opacity: 0; transition: opacity 0.3s ease; }
.stat-card:hover::before { opacity: 1; }
.stat-icon-wrapper { width: 42px; height: 42px; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin: 0 auto 10px; box-shadow: var(--shadow-sm); position: relative; overflow: hidden; }
.stat-icon-wrapper::before { content: ''; position: absolute; inset: -50%; background: conic-gradient(from 0deg, transparent, rgba(255,255,255,0.3), transparent); animation: rotate 4s linear infinite; }
.stat-icon-svg { position: relative; z-index: 1; animation: pulse 2s ease infinite; }
.stat-value { font-size: 24px; font-weight: 700; background: var(--gradient-1); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; margin-bottom: 4px; }
.stat-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; }
@keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
@keyframes pulse { 0%, 100% { transform: scale(1); opacity: 1; } 50% { transform: scale(1.05); opacity: 0.9; } }

.filter-card { margin-bottom: 16px; }
.search-row { margin-bottom: 10px; }
.search-wrap { position: relative; }
.search-icon { position: absolute; left: 12px; top: 50%; transform: translateY(-50%); color: var(--text-muted); }
.search-input { padding-left: 36px; }
.filter-row { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-top: 8px; flex-wrap: wrap; }

.patient-list { display: flex; flex-direction: column; gap: 12px; }

.loading-state, .error-state {
  text-align: center;
  padding: 40px 20px;
  color: var(--text-muted);
}

.error-icon {
  width: 80px;
  height: 80px;
  margin: 0 auto 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(249, 115, 22, 0.1));
  border-radius: 50%;
  color: #ef4444;
  animation: shake 0.5s ease-in-out;
}

@keyframes shake {
  0%, 100% { transform: translateX(0); }
  10%, 30%, 50%, 70%, 90% { transform: translateX(-3px); }
  20%, 40%, 60%, 80% { transform: translateX(3px); }
}

.loading-spinner {
  width: 40px;
  height: 40px;
  margin: 0 auto 16px;
  border: 3px solid rgba(255,255,255,0.1);
  border-top: 3px solid var(--primary-light);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state { text-align: center; padding: 40px 20px; color: var(--text-muted); }

.patient-card { 
  padding: 16px; 
  background: var(--bg-card2);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.patient-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
  border-color: var(--border-hover);
}

.patient-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: var(--gradient-1);
  opacity: 0;
  transition: opacity 0.3s ease;
}

.patient-card:hover::before {
  opacity: 1;
}
.patient-main { display: flex; align-items: flex-start; gap: 12px; cursor: pointer; }
.patient-avatar {
  width: 42px; height: 42px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 18px; font-weight: 700; color: white;
  flex-shrink: 0;
}
.patient-info { flex: 1; min-width: 0; }
.patient-row1 { display: flex; align-items: center; gap: 8px; margin-bottom: 3px; }
.patient-name { font-size: 15px; font-weight: 600; color: var(--text-primary); }
.patient-row2 { display: flex; align-items: center; gap: 10px; font-size: 12px; color: var(--text-secondary); margin-bottom: 5px; }
.expand-arrow { color: var(--text-muted); font-size: 11px; flex-shrink: 0; }

/* 分隔线 */
.divider { height: 1px; background: var(--border); margin: 16px 0; }

/* 操作按钮样式 */
.patient-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid var(--border);
}

.action-btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
  padding: 8px 14px;
  border-radius: 8px;
  border: none;
  cursor: pointer;
  font-size: 13px;
  font-weight: 500;
  transition: all 0.2s ease;
  font-family: inherit;
}

.action-btn:hover {
  transform: translateY(-1px);
}

.action-btn:active {
  transform: scale(0.97);
}

.action-btn-edit {
  background: var(--bg-input);
  color: var(--primary-light);
  border: 1px solid var(--border);
}

.action-btn-edit:hover {
  background: rgba(37,99,235,0.1);
  border-color: var(--primary-light);
}

.action-btn-primary {
  background: var(--gradient-1);
  color: white;
  box-shadow: 0 2px 8px rgba(37,99,235,0.3);
}

.action-btn-primary:hover {
  background: var(--gradient-1);
  box-shadow: 0 4px 12px rgba(37,99,235,0.4);
}

.action-btn-secondary {
  background: var(--bg-input);
  color: var(--text-secondary);
  border: 1px solid var(--border);
}

.action-btn-secondary:hover {
  background: rgba(255,255,255,0.05);
  border-color: var(--border-hover);
}

.action-btn-delete {
  background: rgba(239,68,68,0.1);
  color: var(--danger);
  border: 1px solid rgba(239,68,68,0.2);
}

.action-btn-delete:hover {
  background: rgba(239,68,68,0.2);
  border-color: var(--danger);
}

.detail-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-bottom: 16px; }
.detail-item { display: flex; flex-direction: column; gap: 2px; }
.detail-key { font-size: 11px; color: var(--text-muted); font-weight: 500; }
.detail-val { font-size: 13px; color: var(--text-primary); font-weight: 500; }
.detail-section { margin-bottom: 16px; }
.detail-note { font-size: 13px; color: var(--text-secondary); margin-top: 4px; line-height: 1.5; }
.detail-upload { margin-top: 8px; }

.upload-categories {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  margin-top: 12px;
}

.upload-category {
  background: var(--bg-input);
  border: 1px solid var(--border);
  border-radius: 8px;
  padding: 12px;
  transition: all 0.2s ease;
}

.upload-category:hover {
  border-color: var(--primary-light);
  box-shadow: 0 2px 8px rgba(37, 99, 235, 0.1);
}

/* 已上传状态的样式 */
.upload-category.category-uploaded {
  background: rgba(34, 197, 94, 0.05);
  border-color: rgba(34, 197, 94, 0.3);
}

.upload-category.category-uploaded:hover {
  border-color: rgba(34, 197, 94, 0.5);
  box-shadow: 0 2px 8px rgba(34, 197, 94, 0.15);
}

.category-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
  position: relative;
}

.category-icon-svg {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.category-icon-svg svg {
  width: 20px;
  height: 20px;
}

/* 人口学信息图标 - 蓝色渐变 */
.icon-demographic {
  background: linear-gradient(135deg, #3b82f6, #2563eb);
  box-shadow: 0 4px 20px rgba(37, 99, 235, 0.4);
}

/* 过往手术史图标 - 紫色渐变 */
.icon-surgery {
  background: linear-gradient(135deg, #7c3aed, #6d28d9);
  box-shadow: 0 4px 20px rgba(124, 58, 237, 0.4);
}

/* 检查结果图标 - 青色渐变 */
.icon-lab {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
  box-shadow: 0 4px 20px rgba(6, 182, 212, 0.4);
}

/* 其他图标 - 绿色渐变 */
.icon-other {
  background: linear-gradient(135deg, #10b981, #059669);
  box-shadow: 0 4px 20px rgba(16, 185, 129, 0.4);
}

.category-name {
  font-size: 13px;
  font-weight: 600;
  color: var(--text-primary);
  flex: 1;
}

/* 已上传标记 */
.upload-badge {
  font-size: 11px;
  font-weight: 500;
  color: #16a34a;
  background: rgba(34, 197, 94, 0.15);
  padding: 2px 8px;
  border-radius: 10px;
  border: 1px solid rgba(34, 197, 94, 0.25);
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: scale(0.9);
  }
  to {
    opacity: 1;
    transform: scale(1);
  }
}

/* 已上传后的缩小展示 */
.upload-mini {
  transform: scale(0.9);
  opacity: 0.7;
  transition: all 0.2s ease;
}

.upload-mini:hover {
  transform: scale(1);
  opacity: 1;
}
.detail-hint { font-size: 12px; color: var(--text-muted); margin-top: 4px; }

.detail-diagnosis {
  padding: 12px;
  background: var(--bg-input);
  border-radius: 8px;
  border: 1px solid var(--border);
  border-left: 3px solid var(--primary-light);
}

.detail-actions {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border);
}

/* Modal */
.modal-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,0.7);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: flex-end;
  justify-content: center;
  z-index: 1000;
  padding: 0;
}
.modal-card {
  width: 100%; max-width: 480px;
  background: var(--bg-card);
  border-radius: 20px 20px 0 0;
  border: 1px solid var(--border);
  padding: 0;
  max-height: 85vh;
  overflow-y: auto;
}
.modal-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 20px 20px 0;
}
.modal-header h3 { font-size: 18px; font-weight: 600; }
.modal-body { padding: 16px 20px; display: flex; flex-direction: column; gap: 12px; }
.modal-footer { display: flex; gap: 10px; padding: 0 20px 20px; }
.modal-footer .btn { flex: 1; }
.form-group { display: flex; flex-direction: column; gap: 4px; }
.form-label { font-size: 12px; color: var(--text-secondary); font-weight: 500; }
.required { color: #ef4444; margin-left: 2px; }
.section-header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 12px;
}

.section-header svg {
  width: 18px;
  height: 18px;
  color: var(--primary-light);
  flex-shrink: 0;
}

.section-header h4 {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

/* 过渡动画 */
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

.animate-slide-up {
  animation: slideUp 0.4s ease forwards;
}

/* 结果展示区域 */
.result-section {
  position: fixed;
  bottom: 80px; /* 避开底部导航栏 */
  left: 50%;
  transform: translateX(-50%);
  width: 100%;
  max-width: 480px; /* 与底部导航栏相同的最大宽度 */
  max-height: 60vh;
  overflow-y: auto;
  background: var(--bg);
  border-radius: 12px;
  border: 1px solid var(--border);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  margin: 0;
  padding: 20px;
  animation: slideUp 0.3s ease;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .result-section {
    width: 90%;
    bottom: 70px;
    max-height: 70vh;
    padding: 15px;
  }
}

@media (max-width: 480px) {
  .result-section {
    width: 95%;
    bottom: 70px; /* 与底部导航栏保持适当距离 */
    max-height: 75vh;
    padding: 12px;
  }
}

.result-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 12px;
}

.result-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.result-close {
  background: var(--bg-secondary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.result-close:hover {
  background: var(--bg);
  color: var(--text-primary);
  border-color: var(--border);
}

.result-card {
  max-width: 600px;
  margin: 0;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border: 1px solid var(--border);
}

.result-icon {
  font-size: 32px;
  flex-shrink: 0;
}
</style>
