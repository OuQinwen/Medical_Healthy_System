-- =====================================================
-- 影像检查报告表 (imaging_reports)
-- =====================================================
-- 功能：存储患者的影像检查报告信息（超声、CT、MRI等）
-- 创建时间：2026-04-09
-- =====================================================

CREATE TABLE IF NOT EXISTS imaging_reports (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '影像报告ID',
    
    -- 关联患者
    patient_id INT NOT NULL COMMENT '患者ID（关联patients表）',
    
    -- 影像基本信息
    imaging_type ENUM('超声', 'CT', 'MRI', 'X光', '核医学', '其他') NOT NULL COMMENT '影像类型',
    exam_category VARCHAR(100) COMMENT '检查分类（如：腹部超声、胸部CT等）',
    exam_date DATE COMMENT '检查日期',
    exam_time DATETIME COMMENT '检查时间',
    
    -- 医院信息
    hospital_name VARCHAR(200) COMMENT '检查医院',
    department VARCHAR(100) COMMENT '科室',
    requesting_doctor VARCHAR(100) COMMENT '申请医生',
    performing_doctor VARCHAR(100) COMMENT '检查医生',
    reporting_doctor VARCHAR(100) COMMENT '报告医生',
    reviewing_doctor VARCHAR(100) COMMENT '审核医生',
    
    -- 检查项目
    exam_items TEXT COMMENT '检查项目描述',
    
    -- 诊断所见（核心内容）
    findings TEXT NOT NULL COMMENT '诊断所见（影像描述）',
    
    -- 诊断印象
    impression TEXT COMMENT '诊断印象（结论）',
    
    -- 限制性说明
    limitations TEXT COMMENT '检查限制性说明（如：部分切面显示不清等）',
    
    -- 影像技术参数
    technique TEXT COMMENT '检查技术参数',
    contrast_used BOOLEAN DEFAULT FALSE COMMENT '是否使用对比剂',
    contrast_type VARCHAR(50) COMMENT '对比剂类型',
    
    -- 特殊发现
    special_findings TEXT COMMENT '特殊发现',
    normal_findings TEXT COMMENT '正常发现',
    abnormal_findings TEXT COMMENT '异常发现',
    
    -- 分级评估
    imaging_grade VARCHAR(50) COMMENT '影像分级',
    severity ENUM('正常', '轻度', '中度', '重度') COMMENT '严重程度',
    
    -- 比较影像
    comparison_with_prior TEXT COMMENT '与既往检查对比',
    prior_exam_date DATE COMMENT '既往检查日期',
    
    -- 临床相关性
    clinical_context TEXT COMMENT '临床背景',
    clinical_correlation TEXT COMMENT '临床相关性',
    
    -- 随访建议
    follow_up_required BOOLEAN DEFAULT FALSE COMMENT '是否需要随访',
    follow_up_interval INT COMMENT '随访间隔（天）',
    follow_up_recommendation TEXT COMMENT '随访建议',
    
    -- 质量控制
    image_quality ENUM('优秀', '良好', '一般', '差') COMMENT '图像质量',
    limitations_detail TEXT COMMENT '局限性详细说明',
    
    -- 报告状态
    report_status ENUM('草稿', '已审核', '已发布') DEFAULT '草稿' COMMENT '报告状态',
    
    -- 费用信息
    exam_cost DECIMAL(10,2) COMMENT '检查费用（元）',
    
    -- 时间戳
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 数据来源
    data_source VARCHAR(200) COMMENT '数据来源文件名',
    extraction_time DATETIME COMMENT 'OCR提取时间',
    
    -- 备注
    notes TEXT COMMENT '备注信息',
    
    -- 外键约束
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- 索引
    INDEX idx_patient_id (patient_id),
    INDEX idx_imaging_type (imaging_type),
    INDEX idx_exam_date (exam_date),
    INDEX idx_exam_category (exam_category),
    INDEX idx_severity (severity),
    INDEX idx_follow_up_required (follow_up_required),
    INDEX idx_report_status (report_status),
    INDEX idx_create_time (create_time),
    INDEX idx_extraction_time (extraction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='影像检查报告表，存储超声、CT、MRI等影像学检查报告';

-- 添加表注释
ALTER TABLE imaging_reports COMMENT = '影像检查报告表，存储超声、CT、MRI等影像学检查报告的详细描述和结论';

-- 创建影像器官/部位详情表（可选，用于更详细的记录）
CREATE TABLE IF NOT EXISTS imaging_organ_findings (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '器官发现ID',
    
    -- 关联影像报告
    imaging_report_id INT NOT NULL COMMENT '影像报告ID',
    
    -- 器官/部位信息
    organ_name VARCHAR(100) NOT NULL COMMENT '器官名称（如：肝脏、胆囊、肾脏等）',
    organ_region VARCHAR(100) COMMENT '器官部位（如：左叶、右叶等）',
    
    -- 检查发现
    organ_findings TEXT COMMENT '该器官的检查发现',
    organ_size VARCHAR(100) COMMENT '器官大小描述',
    organ_morphology VARCHAR(100) COMMENT '器官形态描述',
    organ_echo_texture VARCHAR(100) COMMENT '回声/密度描述',
    
    -- 异常描述
    abnormal_description TEXT COMMENT '异常描述',
    abnormal_location VARCHAR(200) COMMENT '异常位置',
    abnormal_size VARCHAR(100) COMMENT '异常大小',
    abnormal_characteristics TEXT COMMENT '异常特征',
    
    -- 血流信息
    blood_flow TEXT COMMENT '血流信息',
    vascular_findings TEXT COMMENT '血管发现',
    
    -- 结论
    organ_conclusion VARCHAR(200) COMMENT '该器官的结论',
    
    -- 时间戳
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    
    -- 外键约束
    FOREIGN KEY (imaging_report_id) REFERENCES imaging_reports(id) ON DELETE CASCADE ON UPDATE CASCADE,
    
    -- 索引
    INDEX idx_imaging_report_id (imaging_report_id),
    INDEX idx_organ_name (organ_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='影像器官发现详情表，记录每个器官的详细检查发现';

-- 添加表注释
ALTER TABLE imaging_organ_findings COMMENT = '影像器官发现详情表，记录影像检查中各个器官的详细发现和描述';