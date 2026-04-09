-- =====================================================
-- 查询和删除影像报告数据的SQL脚本
-- =====================================================

-- 1. 查看所有影像报告
SELECT 
    ir.id,
    ir.patient_id,
    p.patient_name,
    ir.imaging_type,
    ir.exam_category,
    ir.exam_date,
    ir.hospital_name,
    ir.findings,
    ir.impression,
    ir.severity,
    ir.data_source,
    ir.create_time
FROM imaging_reports ir
LEFT JOIN patients p ON ir.patient_id = p.id
ORDER BY ir.create_time DESC;

-- 2. 查看所有器官发现
SELECT 
    iof.id,
    iof.imaging_report_id,
    ir.imaging_type,
    ir.patient_id,
    iof.organ_name,
    iof.organ_findings,
    iof.organ_conclusion,
    iof.create_time
FROM imaging_organ_findings iof
LEFT JOIN imaging_reports ir ON iof.imaging_report_id = ir.id
ORDER BY iof.create_time DESC;

-- 3. 统计每个患者的影像报告数量
SELECT 
    p.patient_name,
    p.id as patient_id,
    COUNT(ir.id) as report_count
FROM patients p
LEFT JOIN imaging_reports ir ON p.id = ir.patient_id
GROUP BY p.id, p.patient_name
ORDER BY report_count DESC;

-- 4. 删除所有影像报告（包括关联的器官发现）
-- 注意：由于有外键约束 ON DELETE CASCADE，删除影像报告会自动删除关联的器官发现
DELETE FROM imaging_reports;

-- 5. 删除特定患者的影像报告
-- DELETE FROM imaging_reports WHERE patient_id = 21;

-- 6. 删除特定ID的影像报告
-- DELETE FROM imaging_reports WHERE id = 1;

-- 7. 查看删除后的结果
SELECT COUNT(*) as remaining_reports FROM imaging_reports;
SELECT COUNT(*) as remaining_organ_findings FROM imaging_organ_findings;