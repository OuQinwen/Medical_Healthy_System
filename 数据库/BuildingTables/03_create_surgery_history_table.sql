-- =====================================================
-- 过往手术史表 (surgery_history)
-- =====================================================
-- 功能：存储患者的过往手术史信息
-- 创建时间：2026-03-26
-- =====================================================

CREATE TABLE IF NOT EXISTS surgery_history (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '手术记录ID',
    
    -- 关联患者
    patient_id INT NOT NULL COMMENT '患者ID（关联patients表）',
    
    -- 手术基本信息
    surgery_name VARCHAR(200) NOT NULL COMMENT '手术名称',
    surgery_date DATE COMMENT '手术日期',
    hospital_name VARCHAR(200) COMMENT '手术医院',
    department VARCHAR(100) COMMENT '科室',
    surgeon_name VARCHAR(100) COMMENT '主刀医生',
    
    -- 手术类型和等级
    surgery_type ENUM('急诊手术', '择期手术', '其他') COMMENT '手术类型',
    surgery_grade ENUM('一级', '二级', '三级', '四级') COMMENT '手术等级',
    anesthesia_type VARCHAR(100) COMMENT '麻醉方式',
    
    -- 手术原因
    surgery_reason TEXT COMMENT '手术原因',
    diagnosis_before_surgery TEXT COMMENT '术前诊断',
    
    -- 手术结果
    surgery_outcome ENUM('治愈', '好转', '无效', '恶化', '死亡') COMMENT '手术结果',
    complications TEXT COMMENT '术后并发症',
    
    -- 住院信息
    admission_date DATE COMMENT '入院日期',
    discharge_date DATE COMMENT '出院日期',
    hospitalization_days INT COMMENT '住院天数',
    
    -- 费用信息
    surgery_cost DECIMAL(12,2) COMMENT '手术费用（元）',
    total_cost DECIMAL(12,2) COMMENT '总费用（元）',
    
    -- 医保报销
    insurance_reimbursement DECIMAL(12,2) COMMENT '医保报销金额（元）',
    self_payment DECIMAL(12,2) COMMENT '自付金额（元）',
    
    -- 随访信息
    follow_up_status ENUM('需要随访', '随访完成', '无需随访') COMMENT '随访状态',
    follow_up_date DATE COMMENT '随访日期',
    follow_up_result TEXT COMMENT '随访结果',
    
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
    INDEX idx_surgery_date (surgery_date),
    INDEX idx_hospital_name (hospital_name),
    INDEX idx_surgery_type (surgery_type),
    INDEX idx_surgery_outcome (surgery_outcome),
    INDEX idx_follow_up_status (follow_up_status),
    INDEX idx_create_time (create_time),
    INDEX idx_extraction_time (extraction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='过往手术史表';

-- 添加表注释
ALTER TABLE surgery_history COMMENT = '过往手术史表，存储患者的手术历史记录';