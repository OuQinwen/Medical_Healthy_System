-- =====================================================
-- 患者基本信息表 (patients)
-- =====================================================
-- 功能：存储患者的基本信息
-- 创建时间：2026-03-26
-- =====================================================

CREATE TABLE IF NOT EXISTS patients (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '患者ID',
    
    -- 基本信息
    patient_id VARCHAR(50) NOT NULL UNIQUE COMMENT '患者唯一标识（证件号等）',
    patient_name VARCHAR(100) NOT NULL COMMENT '患者姓名',
    gender ENUM('male', 'female', 'other') NOT NULL DEFAULT 'male' COMMENT '性别',
    age INT NOT NULL COMMENT '年龄',
    phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    id_number VARCHAR(50) NOT NULL COMMENT '身份证号/护照号',
    
    -- 诊断信息
    preliminary_diagnosis TEXT COMMENT '初步诊断',
    diagnosis_detail TEXT COMMENT '详细诊断信息',
    
    -- 状态管理
    status ENUM('待处理', '进行中', '已完成', '已关闭') NOT NULL DEFAULT '待处理' COMMENT '患者状态',
    
    -- 时间戳
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    
    -- 创建者信息
    creator VARCHAR(100) COMMENT '创建者',
    
    -- 备注
    notes TEXT COMMENT '备注信息',
    
    -- 索引
    INDEX idx_patient_name (patient_name),
    INDEX idx_phone (phone),
    INDEX idx_id_number (id_number),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time),
    INDEX idx_creator (creator)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='患者基本信息表';

-- 添加表注释
ALTER TABLE patients COMMENT = '患者基本信息表，存储患者的基本人口学信息和诊断信息';