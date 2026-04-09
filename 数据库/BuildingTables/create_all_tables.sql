-- =====================================================
-- 医学数据融合科研系统 - 数据库表创建脚本
-- =====================================================
-- 功能：一次性创建所有数据库表
-- 创建时间：2026-03-26
-- 使用方法：mysql -u root -p medical_system < create_all_tables.sql
-- =====================================================

-- 设置字符集
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS medical_research_system 
DEFAULT CHARSET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE medical_research_system;

-- =====================================================
-- 1. 患者基本信息表
-- =====================================================
CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '患者ID',
    patient_id VARCHAR(50) NOT NULL UNIQUE COMMENT '患者唯一标识（证件号等）',
    patient_name VARCHAR(100) NOT NULL COMMENT '患者姓名',
    gender ENUM('male', 'female', 'other') NOT NULL DEFAULT 'male' COMMENT '性别',
    age INT NOT NULL COMMENT '年龄',
    phone VARCHAR(20) NOT NULL COMMENT '联系电话',
    id_number VARCHAR(50) NOT NULL COMMENT '身份证号/护照号',
    preliminary_diagnosis TEXT COMMENT '初步诊断',
    diagnosis_detail TEXT COMMENT '详细诊断信息',
    status ENUM('待处理', '进行中', '已完成', '已关闭') NOT NULL DEFAULT '待处理' COMMENT '患者状态',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    creator VARCHAR(100) COMMENT '创建者',
    notes TEXT COMMENT '备注信息',
    INDEX idx_patient_name (patient_name),
    INDEX idx_phone (phone),
    INDEX idx_id_number (id_number),
    INDEX idx_status (status),
    INDEX idx_create_time (create_time),
    INDEX idx_creator (creator)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='患者基本信息表';

-- =====================================================
-- 2. 人口学信息表
-- =====================================================
CREATE TABLE IF NOT EXISTS demographic_data (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '记录ID',
    patient_id INT NOT NULL COMMENT '患者ID（关联patients表）',
    birth_date DATE COMMENT '出生日期',
    ethnicity VARCHAR(50) COMMENT '民族',
    nationality VARCHAR(50) COMMENT '国籍',
    birth_place VARCHAR(200) COMMENT '出生地',
    current_address VARCHAR(500) COMMENT '现住址',
    residence_type ENUM('城市', '农村', '郊区', '其他') COMMENT '居住类型',
    city VARCHAR(100) COMMENT '所在城市',
    province VARCHAR(100) COMMENT '所在省份',
    education_level ENUM('小学', '初中', '高中', '大专', '本科', '硕士', '博士', '其他') COMMENT '教育程度',
    occupation VARCHAR(100) COMMENT '职业',
    work_unit VARCHAR(200) COMMENT '工作单位',
    marital_status ENUM('未婚', '已婚', '离异', '丧偶', '其他') COMMENT '婚姻状况',
    spouse_name VARCHAR(100) COMMENT '配偶姓名',
    children_count INT DEFAULT 0 COMMENT '子女数量',
    family_size INT DEFAULT 1 COMMENT '家庭人口数',
    insurance_type ENUM('城镇职工医保', '城乡居民医保', '新农合', '商业保险', '自费', '其他') COMMENT '医保类型',
    insurance_number VARCHAR(100) COMMENT '医保卡号',
    annual_income DECIMAL(10,2) COMMENT '年收入（元）',
    economic_status ENUM('贫困', '低收入', '中等收入', '高收入', '富有') COMMENT '经济状况',
    smoking_status ENUM('从不吸烟', '已戒烟', '偶尔吸烟', '经常吸烟') COMMENT '吸烟状况',
    drinking_status ENUM('从不饮酒', '偶尔饮酒', '经常饮酒', '已戒酒') COMMENT '饮酒状况',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    data_source VARCHAR(200) COMMENT '数据来源文件名',
    extraction_time DATETIME COMMENT 'OCR提取时间',
    notes TEXT COMMENT '备注信息',
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_birth_date (birth_date),
    INDEX idx_city (city),
    INDEX idx_province (province),
    INDEX idx_education_level (education_level),
    INDEX idx_create_time (create_time),
    INDEX idx_extraction_time (extraction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='人口学信息表';

-- =====================================================
-- 3. 过往手术史表
-- =====================================================
CREATE TABLE IF NOT EXISTS surgery_history (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '手术记录ID',
    patient_id INT NOT NULL COMMENT '患者ID（关联patients表）',
    surgery_name VARCHAR(200) NOT NULL COMMENT '手术名称',
    surgery_date DATE COMMENT '手术日期',
    hospital_name VARCHAR(200) COMMENT '手术医院',
    department VARCHAR(100) COMMENT '科室',
    surgeon_name VARCHAR(100) COMMENT '主刀医生',
    surgery_type ENUM('急诊手术', '择期手术', '其他') COMMENT '手术类型',
    surgery_grade ENUM('一级', '二级', '三级', '四级') COMMENT '手术等级',
    anesthesia_type VARCHAR(100) COMMENT '麻醉方式',
    surgery_reason TEXT COMMENT '手术原因',
    diagnosis_before_surgery TEXT COMMENT '术前诊断',
    surgery_outcome ENUM('治愈', '好转', '无效', '恶化', '死亡') COMMENT '手术结果',
    complications TEXT COMMENT '术后并发症',
    admission_date DATE COMMENT '入院日期',
    discharge_date DATE COMMENT '出院日期',
    hospitalization_days INT COMMENT '住院天数',
    surgery_cost DECIMAL(12,2) COMMENT '手术费用（元）',
    total_cost DECIMAL(12,2) COMMENT '总费用（元）',
    insurance_reimbursement DECIMAL(12,2) COMMENT '医保报销金额（元）',
    self_payment DECIMAL(12,2) COMMENT '自付金额（元）',
    follow_up_status ENUM('需要随访', '随访完成', '无需随访') COMMENT '随访状态',
    follow_up_date DATE COMMENT '随访日期',
    follow_up_result TEXT COMMENT '随访结果',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    data_source VARCHAR(200) COMMENT '数据来源文件名',
    extraction_time DATETIME COMMENT 'OCR提取时间',
    notes TEXT COMMENT '备注信息',
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_surgery_date (surgery_date),
    INDEX idx_hospital_name (hospital_name),
    INDEX idx_surgery_type (surgery_type),
    INDEX idx_surgery_outcome (surgery_outcome),
    INDEX idx_follow_up_status (follow_up_status),
    INDEX idx_create_time (create_time),
    INDEX idx_extraction_time (extraction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='过往手术史表';

-- =====================================================
-- 4. 检查结果表
-- =====================================================
CREATE TABLE IF NOT EXISTS lab_results (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '检查记录ID',
    patient_id INT NOT NULL COMMENT '患者ID（关联patients表）',
    test_name VARCHAR(200) NOT NULL COMMENT '检查名称',
    test_type ENUM('血液检查', '影像检查', '生化检查', '免疫检查', '病理检查', '其他') COMMENT '检查类型',
    test_date DATE COMMENT '检查日期',
    hospital_name VARCHAR(200) COMMENT '检查医院',
    department VARCHAR(100) COMMENT '科室',
    doctor_name VARCHAR(100) COMMENT '检查医生',
    test_result TEXT COMMENT '检查结果描述',
    result_value VARCHAR(500) COMMENT '检查数值',
    reference_range VARCHAR(500) COMMENT '参考范围',
    unit VARCHAR(50) COMMENT '单位',
    result_status ENUM('正常', '异常', '偏高', '偏低', '临界值') COMMENT '结果状态',
    is_abnormal BOOLEAN DEFAULT FALSE COMMENT '是否异常',
    abnormal_description TEXT COMMENT '异常描述',
    imaging_type ENUM('X光', 'CT', 'MRI', '超声', '其他') COMMENT '影像类型',
    imaging_site VARCHAR(200) COMMENT '检查部位',
    imaging_findings TEXT COMMENT '影像发现',
    imaging_conclusion TEXT COMMENT '影像结论',
    specimen_type VARCHAR(100) COMMENT '标本类型',
    collection_time DATETIME COMMENT '采集时间',
    report_time DATETIME COMMENT '报告时间',
    related_diagnosis TEXT COMMENT '相关诊断',
    clinical_significance TEXT COMMENT '临床意义',
    treatment_suggestion TEXT COMMENT '治疗建议',
    follow_up_required BOOLEAN DEFAULT FALSE COMMENT '是否需要随访',
    follow_up_interval INT COMMENT '随访间隔（天）',
    test_cost DECIMAL(10,2) COMMENT '检查费用（元）',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    data_source VARCHAR(200) COMMENT '数据来源文件名',
    extraction_time DATETIME COMMENT 'OCR提取时间',
    notes TEXT COMMENT '备注信息',
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE ON UPDATE CASCADE,
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

-- =====================================================
-- 5. 系统用户表
-- =====================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '用户ID',
    username VARCHAR(50) NOT NULL UNIQUE COMMENT '用户名',
    email VARCHAR(100) NOT NULL UNIQUE COMMENT '邮箱',
    hashed_password VARCHAR(255) NOT NULL COMMENT '密码哈希',
    full_name VARCHAR(100) COMMENT '全名',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    is_superuser BOOLEAN DEFAULT FALSE COMMENT '是否超级管理员',
    role ENUM('admin', 'doctor', 'researcher', 'viewer') DEFAULT 'viewer' COMMENT '用户角色',
    department VARCHAR(100) COMMENT '所属部门',
    phone VARCHAR(20) COMMENT '联系电话',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    last_login DATETIME COMMENT '最后登录时间',
    INDEX idx_username (username),
    INDEX idx_email (email),
    INDEX idx_role (role),
    INDEX idx_is_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='系统用户表';

-- =====================================================
-- 6. 密码重置令牌表
-- =====================================================
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '令牌ID',
    user_id INT NOT NULL COMMENT '用户ID',
    token VARCHAR(255) NOT NULL UNIQUE COMMENT '重置令牌',
    expires_at DATETIME NOT NULL COMMENT '过期时间',
    used BOOLEAN DEFAULT FALSE COMMENT '是否已使用',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_token (token),
    INDEX idx_expires_at (expires_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='密码重置令牌表';

-- =====================================================
-- 7. 登录日志表
-- =====================================================
CREATE TABLE IF NOT EXISTS login_logs (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '日志ID',
    user_id INT COMMENT '用户ID',
    username VARCHAR(50) COMMENT '用户名',
    login_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '登录时间',
    logout_time DATETIME COMMENT '退出时间',
    ip_address VARCHAR(50) COMMENT 'IP地址',
    user_agent TEXT COMMENT '用户代理',
    login_status ENUM('success', 'failed') DEFAULT 'success' COMMENT '登录状态',
    failure_reason VARCHAR(255) COMMENT '失败原因',
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    INDEX idx_user_id (user_id),
    INDEX idx_login_time (login_time),
    INDEX idx_login_status (login_status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='登录日志表';

-- =====================================================
-- 8. 文件上传记录表
-- =====================================================
CREATE TABLE IF NOT EXISTS file_uploads (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '文件ID',
    patient_id INT COMMENT '患者ID',
    user_id INT COMMENT '上传用户ID',
    file_name VARCHAR(255) NOT NULL COMMENT '文件名',
    file_path VARCHAR(500) COMMENT '文件路径',
    file_size BIGINT COMMENT '文件大小（字节）',
    file_type VARCHAR(50) COMMENT '文件类型',
    is_image BOOLEAN DEFAULT FALSE COMMENT '是否为图片',
    data_category VARCHAR(50) COMMENT '数据分类',
    upload_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '上传时间',
    
    -- OCR处理状态
    ocr_status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending' COMMENT 'OCR状态',
    ocr_result TEXT COMMENT 'OCR结果',
    ocr_error TEXT COMMENT 'OCR错误信息',
    ocr_time DATETIME COMMENT 'OCR处理时间',
    
    -- 数据验证状态
    validation_status ENUM('pending', 'valid', 'invalid') DEFAULT 'pending' COMMENT '验证状态',
    validation_errors TEXT COMMENT '验证错误',
    validation_time DATETIME COMMENT '验证时间',
    
    -- 数据导入状态
    import_status ENUM('pending', 'imported', 'failed') DEFAULT 'pending' COMMENT '导入状态',
    import_error TEXT COMMENT '导入错误',
    import_time DATETIME COMMENT '导入时间',
    
    -- 文件状态
    is_deleted BOOLEAN DEFAULT FALSE COMMENT '是否已删除',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否激活',
    
    notes TEXT COMMENT '备注',
    
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE SET NULL ON UPDATE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL ON UPDATE CASCADE,
    
    INDEX idx_patient_id (patient_id),
    INDEX idx_user_id (user_id),
    INDEX idx_upload_time (upload_time),
    INDEX idx_ocr_status (ocr_status),
    INDEX idx_validation_status (validation_status),
    INDEX idx_import_status (import_status),
    INDEX idx_data_category (data_category)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='文件上传记录表';

-- =====================================================
-- 9. 影像检查报告表
-- =====================================================
CREATE TABLE IF NOT EXISTS imaging_reports (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '影像报告ID',
    patient_id INT NOT NULL COMMENT '患者ID',
    imaging_type ENUM('超声', 'CT', 'MRI', 'X光', '核医学', '其他') NOT NULL COMMENT '影像类型',
    exam_category VARCHAR(100) COMMENT '检查分类',
    exam_date DATE COMMENT '检查日期',
    exam_time DATETIME COMMENT '检查时间',
    hospital_name VARCHAR(200) COMMENT '检查医院',
    department VARCHAR(100) COMMENT '科室',
    requesting_doctor VARCHAR(100) COMMENT '申请医生',
    performing_doctor VARCHAR(100) COMMENT '检查医生',
    reporting_doctor VARCHAR(100) COMMENT '报告医生',
    reviewing_doctor VARCHAR(100) COMMENT '审核医生',
    exam_items TEXT COMMENT '检查项目',
    findings TEXT NOT NULL COMMENT '诊断所见',
    impression TEXT COMMENT '诊断印象',
    limitations TEXT COMMENT '限制性说明',
    technique TEXT COMMENT '检查技术参数',
    contrast_used BOOLEAN DEFAULT FALSE COMMENT '是否使用对比剂',
    contrast_type VARCHAR(50) COMMENT '对比剂类型',
    special_findings TEXT COMMENT '特殊发现',
    normal_findings TEXT COMMENT '正常发现',
    abnormal_findings TEXT COMMENT '异常发现',
    imaging_grade VARCHAR(50) COMMENT '影像分级',
    severity ENUM('正常', '轻度', '中度', '重度') COMMENT '严重程度',
    comparison_with_prior TEXT COMMENT '与既往检查对比',
    prior_exam_date DATE COMMENT '既往检查日期',
    clinical_context TEXT COMMENT '临床背景',
    clinical_correlation TEXT COMMENT '临床相关性',
    follow_up_required BOOLEAN DEFAULT FALSE COMMENT '是否需要随访',
    follow_up_interval INT COMMENT '随访间隔（天）',
    follow_up_recommendation TEXT COMMENT '随访建议',
    image_quality ENUM('优秀', '良好', '一般', '差') COMMENT '图像质量',
    limitations_detail TEXT COMMENT '局限性详细说明',
    report_status ENUM('草稿', '已审核', '已发布') DEFAULT '草稿' COMMENT '报告状态',
    exam_cost DECIMAL(10,2) COMMENT '检查费用（元）',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    update_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    data_source VARCHAR(200) COMMENT '数据来源文件名',
    extraction_time DATETIME COMMENT 'OCR提取时间',
    notes TEXT COMMENT '备注信息',
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_patient_id (patient_id),
    INDEX idx_imaging_type (imaging_type),
    INDEX idx_exam_date (exam_date),
    INDEX idx_exam_category (exam_category),
    INDEX idx_severity (severity),
    INDEX idx_follow_up_required (follow_up_required),
    INDEX idx_report_status (report_status),
    INDEX idx_create_time (create_time),
    INDEX idx_extraction_time (extraction_time)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='影像检查报告表';

-- =====================================================
-- 10. 影像器官发现详情表
-- =====================================================
CREATE TABLE IF NOT EXISTS imaging_organ_findings (
    id INT AUTO_INCREMENT PRIMARY KEY COMMENT '器官发现ID',
    imaging_report_id INT NOT NULL COMMENT '影像报告ID',
    organ_name VARCHAR(100) NOT NULL COMMENT '器官名称',
    organ_region VARCHAR(100) COMMENT '器官部位',
    organ_findings TEXT COMMENT '该器官的检查发现',
    organ_size VARCHAR(100) COMMENT '器官大小描述',
    organ_morphology VARCHAR(100) COMMENT '器官形态描述',
    organ_echo_texture VARCHAR(100) COMMENT '回声/密度描述',
    abnormal_description TEXT COMMENT '异常描述',
    abnormal_location VARCHAR(200) COMMENT '异常位置',
    abnormal_size VARCHAR(100) COMMENT '异常大小',
    abnormal_characteristics TEXT COMMENT '异常特征',
    blood_flow TEXT COMMENT '血流信息',
    vascular_findings TEXT COMMENT '血管发现',
    organ_conclusion VARCHAR(200) COMMENT '该器官的结论',
    create_time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (imaging_report_id) REFERENCES imaging_reports(id) ON DELETE CASCADE ON UPDATE CASCADE,
    INDEX idx_imaging_report_id (imaging_report_id),
    INDEX idx_organ_name (organ_name)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='影像器官发现详情表';

-- =====================================================
-- 创建完成提示
-- =====================================================
SELECT '数据库表创建完成！' AS status;
SELECT COUNT(*) AS table_count FROM information_schema.tables 
WHERE table_schema = 'medical_research_system' 
AND table_name IN ('patients', 'demographic_data', 'surgery_history', 'lab_results', 'users', 'password_reset_tokens', 'login_logs', 'file_uploads', 'imaging_reports', 'imaging_organ_findings');