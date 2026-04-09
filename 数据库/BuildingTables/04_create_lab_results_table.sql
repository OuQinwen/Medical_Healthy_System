-- =====================================================
-- 检查结果表 (lab_results)
-- =====================================================
-- 功能：存储患者的检查结果信息
-- 创建时间：2026-03-26
-- =====================================================

CREATE TABLE IF NOT EXISTS lab_results (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '检查记录ID',
    
    -- 关联患者
    patient_id INT NOT NULL COMMENT '患者ID（关联patients表）',
    
    -- 检查基本信息
    test_name VARCHAR(200) NOT NULL COMMENT '检查名称',
    test_type ENUM('血液检查', '影像检查', '生化检查', '免疫检查', '病理检查', '其他') COMMENT '检查类型',
    test_date DATE COMMENT '检查日期',
    
    -- 医院信息
    hospital_name VARCHAR(200) COMMENT '检查医院',
    department VARCHAR(100) COMMENT '科室',
    doctor_name VARCHAR(100) COMMENT '检查医生',
    
    -- 检查结果
    test_result TEXT COMMENT '检查结果描述',
    result_value VARCHAR(500) COMMENT '检查数值',
    reference_range VARCHAR(500) COMMENT '参考范围',
    unit VARCHAR(50) COMMENT '单位',
    
    -- 结果判断
    result_status ENUM('正常', '异常', '偏高', '偏低', '临界值') COMMENT '结果状态',
    is_abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
    abnormal_description TEXT COMMENT '异常描述',
    
    -- 影像检查专用字段
    imaging_type ENUM('X光', 'CT', 'MRI', '超声', '其他') COMMENT '影像类型',
    imaging_site VARCHAR(200) COMMENT '检查部位',
    imaging_findings TEXT COMMENT '影像发现',
    imaging_conclusion TEXT COMMENT '影像结论',
    
    -- 实验室检查专用字段
    specimen_type VARCHAR(100) COMMENT '标本类型',
    collection_time DATETIME COMMENT '采集时间',
    report_time DATETIME COMMENT '报告时间',
    
    -- 疾病诊断
    related_diagnosis TEXT COMMENT '相关诊断',
    clinical_significance TEXT COMMENT '临床意义',
    
    -- 治疗建议
    treatment_suggestion TEXT COMMENT '治疗建议',
    follow_up_required BOOLEAN DEFAULT FALSE COMMENT '是否需要随访',
    follow_up_interval INT COMMENT '随访间隔（天）',
    
    -- 费用信息
    test_cost DECIMAL(10,2) COMMENT '检查费用（元）',
    
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
    INDEX idx_test_name (test_name),
    INDEX idx_test_type (test_type),
    INDEX idx_test_date (test_date),
    INDEX idx_result_status (result_status),
    INDEX idx_is_abnormal (is_abnormal),
    INDEX idx_hospital_name (hospital_name),
    INDEX idx_create_time (create_time),
    INDEX idx_extraction_time (extraction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='检查结果表';

-- 添加表注释
ALTER TABLE lab_results COMMENT = '检查结果表，存储患者的各种检查结果信息';