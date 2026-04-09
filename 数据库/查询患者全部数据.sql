-- =====================================================
-- 查询患者全部数据的SQL脚本
-- 使用方法：替换患者姓名或ID后执行
-- =====================================================

-- 设置查询参数（修改这里的值）
SET @patient_name = '王八';  -- 患者姓名
SET @patient_id = NULL;       -- 患者ID（如果知道ID，可以在这里设置）

-- 如果设置了patient_id，则使用ID查询，否则使用姓名查询
SELECT @patient_id := COALESCE(@patient_id, (SELECT id FROM patients WHERE patient_name = @patient_name LIMIT 1));

-- =====================================================
-- 1. 患者基本信息
-- =====================================================
SELECT '=== 患者基本信息 ===' as section;
SELECT 
    id AS patient_id,
    patient_id AS patient_code,
    patient_name,
    CASE gender 
        WHEN 'male' THEN '男'
        WHEN 'female' THEN '女'
        ELSE gender
    END AS gender,
    age,
    phone,
    id_number,
    preliminary_diagnosis,
    status,
    create_time,
    creator
FROM patients
WHERE id = @patient_id;

-- =====================================================
-- 2. 文件上传记录（包含OCR原始数据）
-- =====================================================
SELECT '=== 文件上传记录 ===' as section;
SELECT 
    id AS file_id,
    file_name,
    data_category,
    data_type,
    file_size,
    ocr_status,
    validation_status,
    import_status,
    upload_time,
    ocr_time,
    import_time,
    uploaded_by
FROM file_uploads
WHERE patient_id = @patient_id
ORDER BY upload_time DESC;

-- =====================================================
-- 3. OCR提取结果（详细）
-- =====================================================
SELECT '=== OCR提取结果 ===' as section;
SELECT 
    id AS file_id,
    file_name,
    data_category,
    ocr_status,
    JSON_EXTRACT(ocr_result, '$.extracted_data') AS extracted_data,
    JSON_EXTRACT(ocr_result, '$.full_data_json') AS full_data_json,
    upload_time
FROM file_uploads
WHERE patient_id = @patient_id 
  AND ocr_status = 'completed'
ORDER BY upload_time DESC;

-- =====================================================
-- 4. 检查结果数据（lab_results表）
-- =====================================================
SELECT '=== 检查结果数据 ===' as section;
SELECT 
    id,
    test_name,
    test_type,
    test_result,
    result_value,
    reference_range,
    unit,
    is_abnormal,
    data_source,
    extraction_time,
    create_time
FROM lab_results
WHERE patient_id = @patient_id
ORDER BY create_time DESC;

-- =====================================================
-- 5. 人口学信息（demographic_data表）
-- =====================================================
SELECT '=== 人口学信息 ===' as section;
SELECT 
    id,
    birth_date,
    ethnicity,
    current_address,
    occupation,
    insurance_type,
    data_source,
    extraction_time,
    create_time
FROM demographic_data
WHERE patient_id = @patient_id
ORDER BY create_time DESC;

-- =====================================================
-- 6. 手术史（surgery_history表）
-- =====================================================
SELECT '=== 手术史 ===' as section;
SELECT 
    id,
    surgery_name,
    surgery_date,
    hospital_name,
    surgeon_name,
    anesthesia_type,
    surgery_outcome,
    complications,
    data_source,
    extraction_time,
    create_time
FROM surgery_history
WHERE patient_id = @patient_id
ORDER BY create_time DESC;

-- =====================================================
-- 7. 数据统计摘要
-- =====================================================
SELECT '=== 数据统计摘要 ===' as section;
SELECT 
    '文件总数' AS item, 
    COUNT(*) AS count 
FROM file_uploads 
WHERE patient_id = @patient_id

UNION ALL

SELECT 
    'OCR完成' AS item, 
    COUNT(*) AS count 
FROM file_uploads 
WHERE patient_id = @patient_id AND ocr_status = 'completed'

UNION ALL

SELECT 
    'OCR失败' AS item, 
    COUNT(*) AS count 
FROM file_uploads 
WHERE patient_id = @patient_id AND ocr_status = 'failed'

UNION ALL

SELECT 
    '检查结果' AS item, 
    COUNT(*) AS count 
FROM lab_results 
WHERE patient_id = @patient_id

UNION ALL

SELECT 
    '人口学信息' AS item, 
    COUNT(*) AS count 
FROM demographic_data 
WHERE patient_id = @patient_id

UNION ALL

SELECT 
    '手术史' AS item, 
    COUNT(*) AS count 
FROM surgery_history 
WHERE patient_id = @patient_id;

-- =====================================================
-- 8. 按资料分类统计
-- =====================================================
SELECT '=== 按资料分类统计 ===' as section;
SELECT 
    data_category,
    COUNT(*) AS file_count,
    SUM(CASE WHEN ocr_status = 'completed' THEN 1 ELSE 0 END) AS ocr_completed,
    SUM(CASE WHEN ocr_status = 'failed' THEN 1 ELSE 0 END) AS ocr_failed,
    SUM(CASE WHEN import_status = 'imported' THEN 1 ELSE 0 END) AS imported
FROM file_uploads
WHERE patient_id = @patient_id
GROUP BY data_category;

-- =====================================================
-- 快速查询示例（复制使用）
-- =====================================================

-- 方法1：按患者姓名查询
-- SET @patient_name = '患者姓名';
-- SELECT * FROM patients WHERE patient_name = @patient_name;

-- 方法2：按患者ID查询
-- SET @patient_id = 1;
-- SELECT * FROM patients WHERE id = @patient_id;

-- 方法3：查看患者的所有文件
-- SELECT * FROM file_uploads WHERE patient_id = 1;

-- 方法4：查看患者的检查结果
-- SELECT * FROM lab_results WHERE patient_id = 1;

-- 方法5：查看患者的人口学信息
-- SELECT * FROM demographic_data WHERE patient_id = 1;

-- 方法6：查看患者的手术史
-- SELECT * FROM surgery_history WHERE patient_id = 1;