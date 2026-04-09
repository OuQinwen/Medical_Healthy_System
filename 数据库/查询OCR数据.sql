-- =====================================================
-- 查询OCR数据和业务数据的SQL脚本
-- =====================================================

-- 1. 查看患者基本信息
SELECT 
    id,
    patient_id,
    patient_name,
    gender,
    age,
    phone,
    create_time
FROM patients
WHERE patient_name = '王八';

-- 2. 查看文件上传记录（OCR原始数据）
SELECT 
    id AS file_id,
    patient_id,
    file_name,
    file_path,
    file_size,
    file_type,
    data_category,
    data_type,
    ocr_status,
    ocr_result,
    validation_status,
    import_status,
    uploaded_by,
    upload_time,
    ocr_time,
    import_time
FROM file_uploads
WHERE patient_id = 21
ORDER BY upload_time DESC;

-- 3. 查看OCR结果（JSON解析）
SELECT 
    id AS file_id,
    file_name,
    data_category,
    ocr_status,
    JSON_EXTRACT(ocr_result, '$.extracted_data') as extracted_data,
    JSON_EXTRACT(ocr_result, '$.full_data_json') as full_data_json,
    validation_status,
    import_status
FROM file_uploads
WHERE patient_id = 21 
  AND ocr_status = 'completed'
ORDER BY upload_time DESC;

-- 4. 查看检查结果（业务数据）
SELECT 
    lr.id,
    lr.patient_id,
    p.patient_name,
    lr.test_name,
    lr.test_type,
    lr.test_result,
    lr.result_value,
    lr.reference_range,
    lr.unit,
    lr.is_abnormal,
    lr.data_source,
    lr.extraction_time,
    lr.create_time
FROM lab_results lr
JOIN patients p ON lr.patient_id = p.id
WHERE p.patient_name = '王八'
ORDER BY lr.create_time DESC;

-- 5. 查看人口学信息
SELECT 
    dd.id,
    dd.patient_id,
    p.patient_name,
    dd.birth_date,
    dd.ethnicity,
    dd.current_address,
    dd.occupation,
    dd.insurance_type,
    dd.data_source,
    dd.extraction_time
FROM demographic_data dd
JOIN patients p ON dd.patient_id = p.id
WHERE p.patient_name = '王八';

-- 6. 查看手术史
SELECT 
    sh.id,
    sh.patient_id,
    p.patient_name,
    sh.surgery_name,
    sh.surgery_date,
    sh.hospital_name,
    sh.surgeon_name,
    sh.surgery_outcome,
    sh.data_source,
    sh.extraction_time
FROM surgery_history sh
JOIN patients p ON sh.patient_id = p.id
WHERE p.patient_name = '王八';

-- 7. 统计查询
SELECT 
    p.patient_name,
    COUNT(DISTINCT fu.id) as total_files,
    SUM(CASE WHEN fu.ocr_status = 'completed' THEN 1 ELSE 0 END) as ocr_completed,
    SUM(CASE WHEN fu.ocr_status = 'failed' THEN 1 ELSE 0 END) as ocr_failed,
    SUM(CASE WHEN fu.import_status = 'imported' THEN 1 ELSE 0 END) as imported,
    SUM(CASE WHEN fu.import_status = 'failed' THEN 1 ELSE 0 END) as import_failed
FROM patients p
LEFT JOIN file_uploads fu ON p.id = fu.patient_id
WHERE p.patient_name = '王八'
GROUP BY p.id, p.patient_name;

-- 8. 查看完整的处理流程
SELECT 
    fu.id,
    fu.file_name,
    fu.data_category,
    fu.ocr_status,
    fu.validation_status,
    fu.import_status,
    fu.review_status,
    fu.ocr_time,
    fu.import_time,
    CASE 
        WHEN fu.ocr_status = 'pending' THEN '等待OCR处理'
        WHEN fu.ocr_status = 'processing' THEN 'OCR处理中'
        WHEN fu.ocr_status = 'completed' AND fu.import_status = 'pending' THEN 'OCR完成，等待导入'
        WHEN fu.ocr_status = 'completed' AND fu.import_status = 'imported' THEN '处理完成'
        WHEN fu.ocr_status = 'failed' THEN 'OCR失败'
        WHEN fu.import_status = 'failed' THEN '导入失败'
        ELSE '未知状态'
    END as status_description
FROM file_uploads fu
WHERE fu.patient_id = 21
ORDER BY fu.upload_time DESC;

-- 9. 查看OCR处理失败的文件
SELECT 
    id,
    file_name,
    data_category,
    ocr_error,
    upload_time
FROM file_uploads
WHERE patient_id = 21 
  AND ocr_status = 'failed'
ORDER BY upload_time DESC;

-- 10. 查看数据验证失败的文件
SELECT 
    id,
    file_name,
    data_category,
    validation_errors,
    validation_time
FROM file_uploads
WHERE patient_id = 21 
  AND validation_status = 'invalid'
ORDER BY validation_time DESC;