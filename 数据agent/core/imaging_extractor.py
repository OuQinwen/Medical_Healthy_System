"""
影像报告结构化提取器
专门用于处理超声、CT、MRI等影像学检查报告
"""
import re
from typing import Dict, List, Optional, Tuple
import json

class ImagingReportExtractor:
    """影像报告结构化提取器"""
    
    def __init__(self):
        # 影像类型关键词
        self.imaging_type_keywords = {
            '超声': ['超声', 'US', 'ultrasound', '彩超', 'B超'],
            'CT': ['CT', '计算机断层', 'computed tomography'],
            'MRI': ['MRI', '磁共振', 'magnetic resonance'],
            'X光': ['X光', 'X-ray', '放射', 'DR', 'CR'],
            '核医学': ['核医学', 'PET-CT', 'SPECT', '同位素']
        }
        
        # 器官/部位关键词
        self.organ_keywords = [
            '肝', '胆', '胰', '脾', '肾', '膀胱', '前列腺', '子宫', '卵巢',
            '甲状腺', '乳腺', '心脏', '肺', '食管', '胃', '肠', '阑尾',
            '淋巴结', '血管', '神经', '骨骼', '肌肉', '脑', '脊髓',
            '胆囊', '胆管', '胰腺', '肾上腺', '输尿管', '输卵管', '子宫颈'
        ]
        
        # 异常描述关键词
        self.abnormal_keywords = [
            '肿大', '增厚', '狭窄', '扩张', '占位', '包块', '结节',
            '钙化', '积液', '水肿', '梗死', '出血', '血栓', '肿瘤',
            '恶性', '癌', '瘤', '转移', '复发', '残留', '异常',
            '增大', '变形', '破坏', '浸润', '侵犯', '压迫'
        ]
        
        # 影像质量评估
        self.quality_keywords = {
            '优秀': ['优秀', '清晰', '良好'],
            '良好': ['较好', '可以', '基本清晰'],
            '一般': ['一般', '欠清', '部分不清'],
            '差': ['差', '不清', '模糊', '伪影']
        }
    
    def check_ocr_quality(self, raw_text: str) -> Dict:
        """
        检查OCR识别质量
        
        Args:
            raw_text: OCR识别的原始文本
            
        Returns:
            Dict: 包含质量检查结果的字典
        """
        result = {
            'is_good_quality': True,
            'issues': [],
            'warnings': []
        }
        
        # 检查1: 检查是否包含关键字段（放宽条件）
        # 允许各种形式的诊断相关表述
        diagnosis_keywords = [
            '诊断所见', '诊断印象', '检查所见', '检查印象',
            '影像所见', '影像印象', '超声所见', '超声印象',
            'CT所见', 'CT印象', 'MRI所见', 'MRI印象',
            'X线所见', 'X线印象', 'X光所见', 'X光印象',
            '报告描述', '影像描述', '检查描述', '影像结论',
            '报告结论', '检查结论', '诊断结论', '影像意见'
        ]
        has_diagnosis_keywords = any(keyword in raw_text for keyword in diagnosis_keywords)
        
        if not has_diagnosis_keywords:
            # 如果没有标准关键字，检查是否有其他影像相关内容
            has_content = (
                '超声' in raw_text or 'CT' in raw_text or 'MRI' in raw_text or 
                'X线' in raw_text or 'X光' in raw_text or '核医学' in raw_text
            )
            if has_content:
                # 有影像类型但没有标准诊断字段，只给出警告
                result['warnings'].append("OCR文本中不包含标准的'诊断所见'或'诊断印象'关键字")
            else:
                result['is_good_quality'] = False
                result['issues'].append("OCR文本中不包含影像相关内容或诊断信息")
        
        # 检查2: 检查是否有重复内容（大幅放宽阈值）
        check_time_count = raw_text.count('检查时间')
        if check_time_count > 50:  # 从10提高到50
            result['is_good_quality'] = False
            result['issues'].append(f"检测到大量重复内容（'检查时间'出现{check_time_count}次）")
        
        # 检查3: 检查文本长度是否合理
        if len(raw_text) > 5000:
            result['warnings'].append(f"OCR文本过长（{len(raw_text)}字符），可能包含重复或无关内容")
        
        # 检查4: 检查是否包含基本的影像类型信息
        has_imaging_type = any(keyword in raw_text for keywords in self.imaging_type_keywords.values() for keyword in keywords)
        if not has_imaging_type:
            result['warnings'].append("OCR文本中不包含明显的影像类型信息（US、CT、MRI等）")
        
        return result
    
    def extract_imaging_report(self, raw_text: str) -> Dict:
        """
        从原始OCR文本中提取影像报告结构化数据
        
        Args:
            raw_text: OCR识别的原始文本
            
        Returns:
            Dict: 结构化的影像报告数据
        """
        # 清理文本
        cleaned_text = self._clean_text(raw_text)
        
        # 提取各个部分
        result = {
            'imaging_type': self._extract_imaging_type(cleaned_text),
            'exam_category': self._extract_exam_category(cleaned_text),
            'exam_date': self._extract_exam_date(cleaned_text),
            'exam_time': self._extract_exam_time(cleaned_text),
            'hospital_name': self._extract_hospital_name(cleaned_text),
            'department': self._extract_department(cleaned_text),
            'requesting_doctor': self._extract_doctor(cleaned_text, '申请医生'),
            'performing_doctor': self._extract_doctor(cleaned_text, '检查医生'),
            'reporting_doctor': self._extract_doctor(cleaned_text, '报告医生'),
            'reviewing_doctor': self._extract_doctor(cleaned_text, '审核医生'),
            'exam_items': self._extract_exam_items(cleaned_text),
            'findings': self._extract_findings(cleaned_text),
            'impression': self._extract_impression(cleaned_text),
            'limitations': self._extract_limitations(cleaned_text),
            'organ_findings': self._extract_organ_findings(cleaned_text),
            'severity': self._assess_severity(cleaned_text),
            'follow_up_required': self._assess_follow_up(cleaned_text),
            'image_quality': self._assess_image_quality(cleaned_text)
        }
        
        return result
    
    def _clean_text(self, text: str) -> str:
        """清理OCR文本"""
        # 移除多余空格和换行
        text = re.sub(r'\s+', ' ', text)
        # 移除特殊字符
        text = re.sub(r'[^\w\u4e00-\u9fff：：，。、；;！!？?()（）【】\s]', '', text)
        return text.strip()
    
    def _extract_imaging_type(self, text: str) -> str:
        """提取影像类型"""
        for imaging_type, keywords in self.imaging_type_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return imaging_type
        return '其他'
    
    def _extract_exam_category(self, text: str) -> Optional[str]:
        """提取检查分类"""
        # 优先从"检查科室"提取（只取第一个词）
        match = re.search(r'检查科室[：:]\s*(\S+)', text)
        if match:
            return match.group(1).strip()
        
        # 其次从"检查项目"提取
        match = re.search(r'检查项目[：:]\s*(\S+)', text)
        if match:
            project = match.group(1).strip()
            if project and project not in ['', '检查科室', '检查时间']:
                return project
        
        # 根据器官判断
        for organ in ['腹部', '胸部', '头颅', '颈部', '四肢', '骨盆', '心脏', '甲状腺', '乳腺']:
            if organ in text:
                return organ
        
        return None
    
    def _extract_exam_date(self, text: str) -> Optional[str]:
        """提取检查日期"""
        # 查找日期格式：YYYY/M/D 或 YYYY-MM-DD
        date_patterns = [
            r'(\d{4})/(\d{1,2})/(\d{1,2})',
            r'(\d{4})-(\d{1,2})-(\d{1,2})'
        ]
        
        for pattern in date_patterns:
            matches = re.findall(pattern, text)
            if matches:
                # 返回第一个匹配的日期
                year, month, day = matches[0]
                return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        return None
    
    def _extract_exam_time(self, text: str) -> Optional[str]:
        """提取检查时间"""
        # 查找时间格式：HH:MM:SS
        match = re.search(r'检查时间[：:]\s*(\d{1,2}:\d{2}:\d{2})', text)
        if match:
            return match.group(1)
        return None
    
    def _extract_hospital_name(self, text: str) -> Optional[str]:
        """提取医院名称"""
        # 通常在报告顶部或医生信息附近
        hospital_patterns = [
            r'医院[：:]\s*([^；;\n]+)',
            r'就诊医院[：:]\s*([^；;\n]+)'
        ]
        
        for pattern in hospital_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
        
        return None
    
    def _extract_department(self, text: str) -> Optional[str]:
        """提取科室"""
        match = re.search(r'科室[：:]\s*([^；;\n]+)', text)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_doctor(self, text: str, doctor_type: str) -> Optional[str]:
        """提取医生信息"""
        patterns = [
            rf'{doctor_type}[：:]\s*([^；;\n]+)',
            rf'{doctor_type}[：:]\s*([^\s]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                name = match.group(1).strip()
                # 排除明显的非医生姓名
                if len(name) >= 2 and len(name) <= 10:
                    return name
        return None
    
    def _extract_exam_items(self, text: str) -> Optional[str]:
        """提取检查项目"""
        match = re.search(r'检查项目[：:]\s*([^；;\n]+)', text)
        if match:
            return match.group(1).strip()
        return None
    
    def _extract_findings(self, text: str) -> str:
        """提取诊断所见"""
        # 查找"诊断所见："和"诊断印象："之间的内容
        match = re.search(r'诊断所见[：:]\s*(.*?)\s*诊断印象[：:]', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        # 如果没有找到"诊断印象"，则提取"诊断所见："后面的所有内容
        match = re.search(r'诊断所见[：:]\s*(.*)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        
        return ""
    
    def _extract_impression(self, text: str) -> str:
        """提取诊断印象"""
        # 查找"诊断印象："后面的内容
        match = re.search(r'诊断印象[：:]\s*(.*)', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return ""
    
    def _extract_limitations(self, text: str) -> Optional[str]:
        """提取检查限制性说明"""
        # 查找包含"欠清"、"受限"、"遮挡"等关键词的句子
        limitation_keywords = ['欠清', '受限', '遮挡', '显示不全', '部分切面']
        
        for keyword in limitation_keywords:
            # 查找包含关键词的句子
            pattern = rf'[^。；;]*{keyword}[^。；;]*[。；;]?'
            matches = re.findall(pattern, text)
            if matches:
                return '; '.join([m.strip() for m in matches if m.strip()])
        
        return None
    
    def _extract_organ_findings(self, text: str) -> List[Dict]:
        """提取各个器官的检查发现"""
        organ_findings = []
        
        # 从诊断所见中提取器官信息
        findings_section = self._extract_findings(text)
        
        # 按冒号分割，获取各个器官的描述
        organ_descriptions = re.split(r'[：:]\s*', findings_section)
        
        for i, description in enumerate(organ_descriptions):
            if i == 0:
                continue  # 跳过第一个（通常是"诊断所见"标题）
            
            # 提取器官名称
            # 前一个分割点是器官名称
            if i > 1:
                # 获取前面的文本作为器官名称
                prev_text = organ_descriptions[i-1]
                # 提取可能的器官名称
                organ_name = self._extract_organ_name(prev_text)
            else:
                organ_name = ""
            
            if organ_name or description.strip():
                organ_findings.append({
                    'organ_name': organ_name,
                    'findings': description.strip(),
                    'is_abnormal': self._is_abnormal_finding(description)
                })
        
        return organ_findings
    
    def _extract_organ_name(self, text: str) -> str:
        """从文本中提取器官名称"""
        # 查找匹配的器官关键词
        for organ in self.organ_keywords:
            if organ in text:
                return organ
        return ""
    
    def _is_abnormal_finding(self, text: str) -> bool:
        """判断是否为异常发现"""
        for keyword in self.abnormal_keywords:
            if keyword in text:
                return True
        return False
    
    def _assess_severity(self, text: str) -> str:
        """评估严重程度"""
        findings = self._extract_findings(text)
        impression = self._extract_impression(text)
        
        combined_text = findings + " " + impression
        
        # 检查严重程度关键词
        severe_keywords = ['恶性', '癌', '肿瘤', '转移', '破裂', '出血', '梗死', '重度']
        moderate_keywords = ['肿大', '增厚', '狭窄', '扩张', '包块', '中度']
        mild_keywords = ['轻度', '轻微', '少量', '炎症']
        
        for keyword in severe_keywords:
            if keyword in combined_text:
                return '重度'
        
        for keyword in moderate_keywords:
            if keyword in combined_text:
                return '中度'
        
        for keyword in mild_keywords:
            if keyword in combined_text:
                return '轻度'
        
        return '正常'
    
    def _assess_follow_up(self, text: str) -> bool:
        """评估是否需要随访"""
        impression = self._extract_impression(text)
        
        follow_up_keywords = ['随访', '复查', '观察', '定期', '建议', '结合临床']
        
        for keyword in follow_up_keywords:
            if keyword in impression:
                return True
        
        return False
    
    def _assess_image_quality(self, text: str) -> str:
        """评估图像质量"""
        for quality, keywords in self.quality_keywords.items():
            for keyword in keywords:
                if keyword in text:
                    return quality
        return '良好'  # 默认质量
    
    def format_for_database(self, extracted_data: Dict, patient_id: int, file_id: int) -> Dict:
        """
        格式化提取的数据用于数据库插入
        
        Args:
            extracted_data: 提取的结构化数据
            patient_id: 患者ID
            file_id: 文件ID
            
        Returns:
            Dict: 格式化后的数据
        """
        # 辅助函数：限制字符串长度
        def limit_string(value: str, max_length: int) -> str:
            if not value:
                return ''
            if len(value) > max_length:
                return value[:max_length]
            return value
        
        # 辅助函数：限制字符串列表长度
        def limit_string_list(value: str, max_length: int) -> str:
            if not value:
                return ''
            if len(value) > max_length:
                return value[:max_length] + '...'
            return value
        
        return {
            'patient_id': patient_id,
            'imaging_type': extracted_data.get('imaging_type', '其他'),
            'exam_category': limit_string(extracted_data.get('exam_category'), 100),
            'exam_date': extracted_data.get('exam_date'),
            'exam_time': extracted_data.get('exam_time'),
            'hospital_name': limit_string(extracted_data.get('hospital_name'), 200),
            'department': limit_string(extracted_data.get('department'), 100),
            'requesting_doctor': limit_string(extracted_data.get('requesting_doctor'), 50),
            'performing_doctor': limit_string(extracted_data.get('performing_doctor'), 50),
            'reporting_doctor': limit_string(extracted_data.get('reporting_doctor'), 50),
            'reviewing_doctor': limit_string(extracted_data.get('reviewing_doctor'), 50),
            'exam_items': limit_string_list(extracted_data.get('exam_items'), 500),
            'findings': extracted_data.get('findings', ''),
            'impression': extracted_data.get('impression', ''),
            'limitations': limit_string(extracted_data.get('limitations'), 500),
            'severity': extracted_data.get('severity', '正常'),
            'follow_up_required': extracted_data.get('follow_up_required', False),
            'image_quality': extracted_data.get('image_quality', '良好'),
            'data_source': f'file_upload_{file_id}',
            'extraction_time': None  # 将由数据库自动设置
        }
    
    def format_organ_findings_for_database(self, extracted_data: Dict, imaging_report_id: int) -> List[Dict]:
        """
        格式化器官发现数据用于数据库插入
        
        Args:
            extracted_data: 提取的结构化数据
            imaging_report_id: 影像报告ID
            
        Returns:
            List[Dict]: 格式化后的器官发现数据
        """
        organ_findings = []
        
        for organ in extracted_data.get('organ_findings', []):
            organ_findings.append({
                'imaging_report_id': imaging_report_id,
                'organ_name': organ.get('organ_name', ''),
                'organ_findings': organ.get('findings', ''),
                'is_abnormal': organ.get('is_abnormal', False),
                'organ_conclusion': '异常' if organ.get('is_abnormal') else '正常'
            })
        
        return organ_findings