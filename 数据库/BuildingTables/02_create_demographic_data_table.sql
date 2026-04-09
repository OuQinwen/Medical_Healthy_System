-- =====================================================
-- 人口学信息表 (demographic_data)
-- =====================================================
-- 功能：存储患者的人口学信息
-- 创建时间：2026-03-26
-- =====================================================

CREATE TABLE IF NOT EXISTS demographic_data (
    -- 主键
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    
    -- 关联患者
    patient_id INT NOT NULL COMMENT '患者ID（关联patients表）',
    
    -- 基本信息
    birth_date DATE COMMENT '出生日期',
    ethnicity VARCHAR(50) COMMENT '民族',
    nationality VARCHAR(50) COMMENT '国籍',
    birth_place VARCHAR(200) COMMENT '出生地',
    
    -- 居住信息
    current_address VARCHAR(500) COMMENT '现住址',
    residence_type ENUM('城市', '农村', '郊区', '其他') COMMENT '居住类型',
    city VARCHAR(100) COMMENT '所在城市',
    province VARCHAR(100) COMMENT '所在省份',
    
    -- 教育和职业
    education_level ENUM('小学', '初中', '高中', '大专', '本科', '硕士', '博士', '其他') COMMENT '教育程度',
    occupation VARCHAR(100) COMMENT '职业',
    work_unit VARCHAR(200) COMMENT '工作单位',
    
    -- 家庭信息
    marital_status ENUM('未婚', '已婚', '离异', '丧偶', '其他') COMMENT '婚姻状况',
    spouse_name VARCHAR(100) COMMENT '配偶姓名',
    children_count INT DEFAULT 0 COMMENT '子女数量',
    family_size INT DEFAULT 1 COMMENT '家庭人口数',
    
    -- 医疗保险
    insurance_type ENUM('城镇职工医保', '城乡居民医保', '新农合', '商业保险', '自费', '其他') COMMENT '医保类型',
    insurance_number VARCHAR(100) COMMENT '医保卡号',
    
    -- 经济状况
    annual_income DECIMAL(10,2) COMMENT '年收入（元）',
    economic_status ENUM('贫困', '低收入', '中等收入', '高收入', '富有') COMMENT '经济状况',
    
    -- 生活习惯
    smoking_status ENUM('从不吸烟', '已戒烟', '偶尔吸烟', '经常吸烟') COMMENT '吸烟状况',
    drinking_status ENUM('从不饮酒', '偶尔饮酒', '经常饮酒', '已戒酒') COMMENT '饮酒状况',
    
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
    INDEX idx_birth_date (birth_date),
    INDEX idx_city (city),
    INDEX idx_province (province),
    INDEX idx_education_level (education_level),
    INDEX idx_create_time (create_time),
    INDEX idx_extraction_time (extraction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='人口学信息表';

-- 添加表注释
ALTER TABLE demographic_data COMMENT = '人口学信息表，存储患者详细的人口学信息';