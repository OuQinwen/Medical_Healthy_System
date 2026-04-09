-- =====================================================
-- 文件上传记录表 (file_uploads)
-- =====================================================
-- 功能：支持每种资料类型上传多份文件
-- 创建时间：2026-04-02
-- =====================================================

CREATE TABLE IF NOT EXISTS file_uploads (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '文件记录ID',
    
    -- 关联患者
    patient_id INT NOT NULL COMMENT '患者ID（关联patients表）',
    
    -- 文件基本信息
    file_name VARCHAR(255) NOT NULL COMMENT '原始文件名',
    file_path VARCHAR(500) NOT NULL COMMENT '文件存储路径',
    file_size BIGINT COMMENT '文件大小（字节）',
    file_type VARCHAR(50) COMMENT '文件类型（image/jpeg, image/png, application/pdf等）',
    file_extension VARCHAR(20) COMMENT '文件扩展名（jpg, png, pdf等）',
    
    -- 资料分类
    data_category ENUM('人口学信息', '既往手术史', '检查结果', '其他') NOT NULL COMMENT '资料分类',
    data_type VARCHAR(100) COMMENT '具体资料类型（如：入院记录、血常规、超声检查等）',
    
    -- OCR处理状态
    ocr_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT 'OCR处理状态',
    ocr_result LONGTEXT COMMENT 'OCR提取结果（JSON格式）',
    ocr_error LONGTEXT COMMENT 'OCR处理错误信息',
    ocr_time DATETIME COMMENT 'OCR处理时间',
    
    -- 数据验证状态
    validation_status ENUM('pending', 'valid', 'invalid', 'needs_review') DEFAULT 'pending' COMMENT '数据验证状态',
    validation_errors LONGTEXT COMMENT '验证错误信息',
    validation_time DATETIME COMMENT '验证时间',
    
    -- 数据入库状态
    import_status ENUM('pending', 'imported', 'failed') DEFAULT 'pending' COMMENT '数据入库状态',
    import_time DATETIME COMMENT '入库时间',
    import_error LONGTEXT COMMENT '入库错误信息',
    
    -- 审核状态
    review_status ENUM('pending', 'approved', 'rejected', 'needs_revision') DEFAULT 'pending' COMMENT '审核状态',
    reviewer_id INT COMMENT '审核人ID',
    review_time DATETIME COMMENT '审核时间',
    review_comment LONGTEXT COMMENT '审核意见',
    
    -- 文件元数据
    file_description LONGTEXT COMMENT '文件描述',
    file_tags VARCHAR(500) COMMENT '文件标签（逗号分隔）',
    upload_source VARCHAR(100) COMMENT '上传来源（web, api, import）',
    
    -- 操作信息
    uploaded_by VARCHAR(100) COMMENT '上传人',
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    
    -- 状态管理
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否有效',
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否删除',
    
    -- 备注
    notes LONGTEXT COMMENT '备注信息',
    
    -- 外键约束
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- 索引
    INDEX idx_patient_id (patient_id),
    INDEX idx_data_category (data_category),
    INDEX idx_data_type (data_type),
    INDEX idx_ocr_status (ocr_status),
    INDEX idx_validation_status (validation_status),
    INDEX idx_import_status (import_status),
    INDEX idx_review_status (review_status),
    INDEX idx_upload_time (upload_time),
    INDEX idx_uploaded_by (uploaded_by),
    INDEX idx_is_active (is_active),
    INDEX idx_is_deleted (is_deleted),
    
    -- 复合索引
    INDEX idx_patient_category (patient_id, data_category),
    INDEX idx_patient_status (patient_id, ocr_status, import_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件上传记录表';

-- 添加表注释
ALTER TABLE file_uploads COMMENT = '文件上传记录表，支持每种资料类型上传多份文件，记录OCR处理、验证、入库和审核状态';