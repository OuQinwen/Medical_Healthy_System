"""
LLM数据提取模块 - 重构版
支持使用本地LM Studio或硅胶流动云端API从OCR文本中提取结构化数据

架构说明：
- PromptBuilder: 负责构建提取提示词
- ResponseParser: 负责解析LLM响应
- DataValidator: 负责数据验证
- FieldMatcher: 负责字段匹配
- MedicalKnowledge: 医学知识库
"""

import json
import re
import requests
from typing import Dict, List, Optional, Tuple

from .config import Config


class MedicalKnowledge:
    """医学知识库 - 集中管理医学领域知识"""
    
    # 概括性字段展开规则
    FIELD_EXPANSION_RULES = {
        '细胞百分比': '淋巴细胞百分比、中性粒细胞百分比、单核细胞百分比、嗜酸性粒细胞百分比、嗜碱性粒细胞百分比',
        '百分比': '淋巴细胞百分比、中性粒细胞百分比、单核细胞百分比、嗜酸性粒细胞百分比、嗜碱性粒细胞百分比',
        '血常规': '白细胞计数、红细胞计数、血红蛋白、血小板计数、淋巴细胞百分比、中性粒细胞百分比、平均红细胞体积、平均红细胞血红蛋白量、平均红细胞血红蛋白浓度、红细胞分布宽度、红细胞比积',
        '肝功能': '谷丙转氨酶、谷草转氨酶、总胆红素、直接胆红素、间接胆红素、白蛋白、球蛋白、总蛋白、谷氨酰转肽酶、碱性磷酸酶',
        '肾功能': '肌酐、尿素氮、尿酸、胱抑素C、β2微球蛋白、估算肾小球滤过率',
        '血脂': '总胆固醇、甘油三酯、高密度脂蛋白胆固醇、低密度脂蛋白胆固醇、载脂蛋白A1、载脂蛋白B、脂蛋白a',
        '血糖': '空腹血糖、餐后2小时血糖、随机血糖、糖化血红蛋白HbA1c',
        '电解质': '钠、钾、氯、钙、磷、镁、二氧化碳结合力',
        '蛋白': '总蛋白、白蛋白、球蛋白、尿蛋白、血蛋白、血红蛋白、血红蛋白浓度、平均红细胞血红蛋白量、平均红细胞血红蛋白浓度、前白蛋白、微量白蛋白',
        '转氨酶': '谷丙转氨酶、谷草转氨酶、谷丙转氨酶ALT、谷草转氨酶AST、谷氨酰转肽酶GGT',
        '心肌酶': '肌酸激酶、肌酸激酶同工酶、乳酸脱氢酶、肌钙蛋白I、肌钙蛋白T、肌红蛋白',
        '凝血功能': '凝血酶原时间、活化部分凝血活酶时间、纤维蛋白原、凝血酶时间、国际标准化比值INR',
        '甲状腺功能': '促甲状腺激素TSH、游离三碘甲状腺原氨酸FT3、游离甲状腺素FT4、三碘甲状腺原氨酸T3、甲状腺素T4',
        '肿瘤标志物': '癌胚抗原CEA、甲胎蛋白AFP、糖类抗原19-9、糖类抗原125、糖类抗原15-3、前列腺特异性抗原PSA'
    }
    
    # 关键词映射表（用于模糊匹配）
    KEYWORD_MAPPINGS = {
        '蛋白': [
            '总蛋白', '白蛋白', '球蛋白', '前白蛋白', '尿蛋白', '血蛋白',
            '血红蛋白', '血红蛋白浓度', 'HGB', 'Hb',
            '平均红细胞血红蛋白量', 'MCH', '平均红细胞血红蛋白浓度', 'MCHC',
            '微量白蛋白', '尿微量白蛋白', '尿微量白蛋白肌酐比',
            '白蛋白球蛋白比', 'A/G',
            '转铁蛋白', '铁蛋白'
        ],
        '血糖': [
            '空腹血糖', '餐后血糖', '餐后2小时血糖', '随机血糖',
            '糖化血红蛋白', 'HbA1c', '糖化血清蛋白',
            '葡萄糖', 'GLU'
        ],
        '血脂': [
            '总胆固醇', 'TC', '胆固醇', '甘油三酯', 'TG',
            '高密度脂蛋白胆固醇', 'HDL-C', '高密度脂蛋白', '好胆固醇',
            '低密度脂蛋白胆固醇', 'LDL-C', '低密度脂蛋白', '坏胆固醇',
            '载脂蛋白A1', 'ApoA1', '载脂蛋白B', 'ApoB',
            '脂蛋白a', 'Lp(a)', '游离脂肪酸'
        ],
        '转氨酶': [
            '谷丙转氨酶', 'ALT', '丙氨酸转氨酶', 'GPT',
            '谷草转氨酶', 'AST', '天冬氨酸转氨酶', 'GOT',
            '谷氨酰转肽酶', 'GGT', 'γ-谷氨酰转肽酶',
            '碱性磷酸酶', 'ALP', 'AKP'
        ],
        '红细胞': [
            '红细胞计数', 'RBC', '红细胞压积', 'HCT', '红细胞比积',
            '红细胞分布宽度', 'RDW', '红细胞分布宽度CV', '红细胞分布宽度SD',
            '平均红细胞体积', 'MCV',
            '平均红细胞血红蛋白量', 'MCH',
            '平均红细胞血红蛋白浓度', 'MCHC',
            '网织红细胞', '网织红细胞计数', 'RET'
        ],
        '白细胞': [
            '白细胞计数', 'WBC', '白细胞数', '白细胞总数',
            '白细胞分类', '淋巴细胞', 'LYM', '淋巴细胞百分比', 'LYM%',
            '单核细胞', 'MON', '单核细胞百分比', 'MON%',
            '中性粒细胞', 'NEUT', '中性粒细胞百分比', 'NEUT%',
            '嗜酸性粒细胞', 'EOS', '嗜酸性粒细胞百分比', 'EOS%',
            '嗜碱性粒细胞', 'BAS', '嗜碱性粒细胞百分比', 'BAS%',
            '淋巴细胞绝对值', '单核细胞绝对值', '中性粒细胞绝对值',
            '嗜酸性粒细胞绝对值', '嗜碱性粒细胞绝对值'
        ],
        '血小板': [
            '血小板计数', 'PLT', '血小板数',
            '血小板压积', 'PCT', '血小板比积',
            '血小板分布宽度', 'PDW',
            '平均血小板体积', 'MPV',
            '大血小板比率'
        ],
        '肾功能': [
            '肌酐', 'Cr', '血肌酐', '血清肌酐',
            '尿素氮', 'BUN', '尿素',
            '尿酸', 'UA',
            '胱抑素C', 'CysC',
            'β2微球蛋白', 'β2-MG', '微球蛋白',
            '估算肾小球滤过率', 'eGFR'
        ],
        '电解质': [
            '钾', 'K+', '钾离子',
            '钠', 'Na+', '钠离子',
            '氯', 'Cl-', '氯离子',
            '钙', 'Ca', '钙离子', '总钙', '离子钙',
            '磷', 'P', '磷离子',
            '镁', 'Mg', '镁离子',
            '二氧化碳结合力', 'CO2CP'
        ],
        '凝血': [
            '凝血酶原时间', 'PT',
            '活化部分凝血活酶时间', 'APTT',
            '纤维蛋白原', 'FIB',
            '凝血酶时间', 'TT',
            '国际标准化比值', 'INR',
            'D-二聚体', 'D-Dimer'
        ],
        '心肌酶': [
            '肌酸激酶', 'CK', '磷酸肌酸激酶',
            '肌酸激酶同工酶', 'CK-MB',
            '乳酸脱氢酶', 'LDH',
            '肌钙蛋白I', 'cTnI', '肌钙蛋白T', 'cTnT',
            '肌红蛋白', 'MYO'
        ],
        '甲状腺': [
            '促甲状腺激素', 'TSH',
            '游离三碘甲状腺原氨酸', 'FT3', '游离T3',
            '游离甲状腺素', 'FT4', '游离T4',
            '三碘甲状腺原氨酸', 'T3',
            '甲状腺素', 'T4',
            '甲状腺球蛋白', 'TG',
            '甲状腺过氧化物酶抗体', 'TPOAb'
        ],
        '肿瘤': [
            '癌胚抗原', 'CEA',
            '甲胎蛋白', 'AFP',
            '糖类抗原19-9', 'CA19-9',
            '糖类抗原125', 'CA125',
            '糖类抗原15-3', 'CA15-3',
            '前列腺特异性抗原', 'PSA', '总PSA', '游离PSA',
            '神经元特异性烯醇化酶', 'NSE',
            '细胞角蛋白19片段', 'CYFRA21-1'
        ],
        '胆红素': [
            '总胆红素', 'TBIL',
            '直接胆红素', 'DBIL',
            '间接胆红素', 'IBIL'
        ]
    }
    
    # 医学指标的合理范围参考
    MEDICAL_RANGES = {
        # 血常规
        '白细胞计数': (2.0, 30.0),
        '红细胞计数': (2.0, 7.0),
        '血红蛋白': (50, 200),
        '血小板计数': (20, 800),
        # 肝功能
        '谷丙转氨酶': (0, 1000),
        '谷草转氨酶': (0, 1000),
        '总胆红素': (0, 500),
        '总蛋白': (30, 100),
        '白蛋白': (10, 60),
        # 肾功能
        '肌酐': (10, 1000),
        '尿素氮': (1, 30),
        '尿酸': (50, 800),
        # 血脂
        '总胆固醇': (1, 20),
        '甘油三酯': (0.1, 20),
        # 血糖
        '空腹血糖': (1, 30),
        '糖化血红蛋白': (3, 15),
        # 电解质
        '钾': (1, 10),
        '钠': (100, 180),
        '氯': (70, 130),
        '钙': (1, 4),
    }
    
    # 常见缩写映射
    ABBREVIATION_MAP = {
        'ALT': ['谷丙转氨酶', '丙氨酸转氨酶', 'GPT'],
        'AST': ['谷草转氨酶', '天冬氨酸转氨酶', 'GOT'],
        'HGB': ['血红蛋白', 'Hb'],
        'WBC': ['白细胞', '白细胞计数'],
        'RBC': ['红细胞', '红细胞计数'],
        'PLT': ['血小板', '血小板计数'],
        'TC': ['总胆固醇', '胆固醇'],
        'TG': ['甘油三酯'],
        'HDL': ['高密度脂蛋白'],
        'LDL': ['低密度脂蛋白'],
        'CK': ['肌酸激酶', '磷酸肌酸激酶'],
        'LDH': ['乳酸脱氢酶'],
        'TSH': ['促甲状腺激素'],
        'T3': ['三碘甲状腺原氨酸'],
        'T4': ['甲状腺素'],
        'CEA': ['癌胚抗原'],
        'AFP': ['甲胎蛋白'],
        'PSA': ['前列腺特异性抗原']
    }


class FieldMatcher:
    """字段匹配器 - 负责字段名与用户关键词的匹配"""
    
    def __init__(self):
        self.knowledge = MedicalKnowledge()
    
    def is_match(self, field_name: str, user_keyword: str) -> bool:
        """
        检查字段名是否与用户关键词匹配
        
        Args:
            field_name: 字段名
            user_keyword: 用户输入的关键词
            
        Returns:
            bool: 是否匹配
        """
        def normalize(text: str) -> str:
            text = re.sub(r'[\(\)\[\]（）\s]', '', text)
            return text.upper()
        
        field_norm = normalize(field_name)
        keyword_norm = normalize(user_keyword)
        
        # 1. 精确匹配
        if field_norm == keyword_norm:
            return True
        
        # 2. 包含匹配
        if keyword_norm in field_norm or field_norm in keyword_norm:
            return True
        
        # 3. 关键词映射表匹配
        for keyword, related_fields in self.knowledge.KEYWORD_MAPPINGS.items():
            if keyword_norm in keyword or keyword in keyword_norm:
                if field_name in related_fields or keyword in field_name:
                    return True
        
        # 4. 缩写匹配
        if keyword_norm in self.knowledge.ABBREVIATION_MAP:
            for full_name in self.knowledge.ABBREVIATION_MAP[keyword_norm]:
                if normalize(full_name) == field_norm:
                    return True
        
        # 5. 共同子串匹配（至少2个字符）
        min_len = 2
        if len(keyword_norm) >= min_len and len(field_norm) >= min_len:
            for i in range(len(keyword_norm) - min_len + 1):
                if keyword_norm[i:i+min_len] in field_norm:
                    return True
        
        return False
    
    def should_expand_field(self, field: str) -> Optional[str]:
        """
        检查字段是否需要展开，返回展开后的子字段列表
        
        Args:
            field: 字段名
            
        Returns:
            Optional[str]: 需要展开的子字段，不需要展开则返回None
        """
        for key, sub_fields in self.knowledge.FIELD_EXPANSION_RULES.items():
            if key in field or field in key:
                return sub_fields
        return None
    
    def is_fuzzy_keyword(self, field: str) -> bool:
        """检查是否为模糊关键词（短关键词）"""
        return len(field.strip()) <= 4


class DataValidator:
    """数据验证器 - 负责验证医学数据的合理性"""
    
    def __init__(self):
        self.knowledge = MedicalKnowledge()
    
    def validate_value(self, field_name: str, value: str) -> Tuple[bool, str]:
        """
        验证医学数值的合理性
        
        Args:
            field_name: 字段名称
            value: 数值（字符串格式）
            
        Returns:
            tuple: (是否有效, 错误信息)
        """
        # 提取数值部分
        value_match = re.search(r'[-+]?\d*\.?\d+', value)
        if not value_match:
            return False, f"无法提取数值: {value}"
        
        try:
            num_value = float(value_match.group())
        except ValueError:
            return False, f"数值格式错误: {value}"
        
        # 检查负数
        if num_value < 0 and field_name not in ['血糖差值', '血压差值']:
            return False, f"数值不能为负: {num_value}"
        
        # 检查是否过大
        if num_value > 1000000:
            return False, f"数值过大，可能单位错误: {num_value}"
        
        # 检查合理范围
        normalized_field = self._normalize_field_name(field_name)
        if normalized_field in self.knowledge.MEDICAL_RANGES:
            min_val, max_val = self.knowledge.MEDICAL_RANGES[normalized_field]
            if num_value < min_val or num_value > max_val:
                return False, f"数值超出合理范围 [{min_val}, {max_val}]: {num_value}"
        
        return True, ""
    
    def _normalize_field_name(self, field_name: str) -> str:
        """规范化字段名称"""
        field_name = re.sub(r'[（(].*[）)]', '', field_name)
        return field_name.strip()
    
    def clean_value(self, value: str) -> str:
        """清理数值，移除多余的空格和特殊字符"""
        value = ' '.join(value.split())
        return value
    
    def extract_unit(self, value: str) -> str:
        """从值中提取单位"""
        unit_patterns = [
            r'×10\^?\d*/L', r'g/L', r'mmol/L', r'μmol/L', r'U/L',
            r'%', r'fL', r'pg', r'mIU/L', r'umol/L', r'ng/mL', r'μg/L'
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, value)
            if match:
                return match.group()
        
        return ""


class PromptBuilder:
    """提示词构建器 - 负责构建LLM提取提示词"""
    
    def __init__(self):
        self.matcher = FieldMatcher()
        self.knowledge = MedicalKnowledge()
    
    def build_prompt(self, full_text: str, fields: Optional[List[str]] = None, data_type: str = "lab_result") -> str:
        """
        构建提取提示词
        
        Args:
            full_text: OCR识别的全量文本
            fields: 需要提取的字段列表
            data_type: 资料类型，可选值：
                - "demographic": 人口学资料
                - "surgery_history": 手术史
                - "lab_result": 检查结果（默认）
                - "imaging": 影像检查报告（超声、CT、MRI等）
                - "general": 其他文件（通用OCR）
            
        Returns:
            str: 完整的提示词
        """
        if data_type == "demographic":
            return self.build_demographic_prompt(full_text, fields)
        elif data_type == "surgery_history":
            return self.build_surgery_history_prompt(full_text, fields)
        elif data_type == "imaging":
            return self.build_imaging_prompt(full_text, fields)
        elif data_type == "general":
            return self.build_general_ocr_prompt(full_text, fields)
        else:  # lab_result (默认)
            return self.build_lab_result_prompt(full_text, fields)
    
    def _build_field_specific_prompt(self, full_text: str, fields: List[str]) -> str:
        """构建指定字段提取的提示词"""
        fields_str = '、'.join(fields)
        
        # 生成字段展开说明
        expand_instructions = []
        fuzzy_match_notes = []
        
        for field in fields:
            sub_fields = self.matcher.should_expand_field(field)
            if sub_fields:
                expand_instructions.append(
                    f"""
对于"{field}"字段：
- 不要只返回汇总格式
- 必须将每个具体项单独列出，每行一个
- 具体包括：{sub_fields}
- 格式示例：
  {sub_fields.split('、')[0]}：数值
  {sub_fields.split('、')[1]}：数值
"""
                )
            
            if self.matcher.is_fuzzy_keyword(field):
                fuzzy_match_notes.append(
                    f"- 对于\"{field}\"：请提取所有包含该关键词的字段（如相关字段有多个，请全部列出）"
                )
        
        expand_instruction_text = '\n'.join(expand_instructions) if expand_instructions else ""
        fuzzy_match_note_text = '\n'.join(fuzzy_match_notes) if fuzzy_match_notes else ""
        
        prompt = f"""请从以下医学化验单OCR文本中提取指定的数据字段。

【专业医学数据提取任务】
需要提取的字段：{fields_str}

【严格格式要求】：
1. 每个字段必须单独一行，使用冒号(:)或中文冒号(：)分隔字段名和值
2. 格式示例：字段名: 值  或  字段名：值
3. **绝对禁止使用竖线(|)或其他符号作为分隔符**
4. 只返回字段名和结果值，不要包含参考范围和单位在冒号前面
5. 数值必须包含单位（如：g/L, mmol/L, ×10^9/L, U/L, %等）

【精确提取要求】：
1. OCR文本可能是表格格式，使用竖线(|)、制表符或空格分隔各列
2. 表格格式通常是：项目名称 | 结果 | 参考范围 | 单位  或  项目名称  结果  参考范围  单位
3. **必须提取"结果"列的值，而不是"参考范围"或"单位"列**
4. 数值必须包含单位，如果结果包含箭头标记(↑↓←→)，请保留在数值中
5. 对于概括性字段（如细胞百分比、血常规等），必须将每个具体项单独列出
6. **特别注意：如果用户输入的是模糊关键词（如"蛋白"、"血糖"、"转氨酶"），请提取所有包含该关键词的相关字段**
7. **必须跳过表头行**：包含"项目名称"、"结果"、"参考范围"、"单位"、"Test"、"Result"、"Normal"等关键词的行
8. **必须跳过分隔行**：只包含"---"、"|---|---|"、"==="、"==="或空白内容的行
9. **必须跳过格式标记**：以"###"、"**"、"*"等markdown符号开头的表头标记行

{expand_instruction_text}
{fuzzy_match_note_text}

OCR识别的全量文本：
{full_text}

【正确输出示例】：
淋巴细胞百分比：18.8%
中性粒细胞百分比：71.3%
白细胞计数：5.8 ×10^9/L
血红蛋白：120 g/L
谷丙转氨酶(ALT)：25 U/L
总胆固醇：5.2 mmol/L
总蛋白：68 g/L
白蛋白：42 g/L
球蛋白：26 g/L

现在请按上述专业医学数据提取要求，精确提取以下字段：
{fields_str}"""
        
        return prompt
    
    def _build_full_extraction_prompt(self, full_text: str) -> str:
        """构建全量提取的提示词"""
        prompt = f"""请从以下医学化验单OCR文本中提取所有可见的医学检验数据字段，并以专业的易读格式返回。

【专业医学数据提取任务 - 全量提取模式】

【严格格式要求】：
1. 每个字段必须单独一行，使用冒号(:)或中文冒号(：)分隔字段名和值
2. 格式示例：字段名: 值  或  字段名：值
3. **绝对禁止使用竖线(|)或其他符号作为分隔符**
4. 只返回字段名和结果值，不要包含参考范围和单位在冒号前面
5. 数值必须包含单位（如：g/L, mmol/L, ×10^9/L, U/L, %, μmol/L, mIU/L等）

【精确提取要求】：
1. OCR文本可能是表格格式，使用竖线(|)、制表符或空格分隔各列
2. 表格格式通常是：项目名称 | 结果 | 参考范围 | 单位  或  项目名称  结果  参考范围  单位
3. **必须提取"结果"列的值，而不是"参考范围"或"单位"列**
4. 数值必须包含单位，如果结果包含箭头标记(↑↓←→)、异常标记(H/L/N)，请保留在数值中
5. 对于多值字段（如白细胞分类），必须将每个具体项单独列出
6. **必须跳过表头行**：包含"项目名称"、"结果"、"参考范围"、"单位"、"Test"、"Result"、"Normal"等关键词的行
7. **必须跳过分隔行**：只包含"---"、"|---|---|"、"==="、"==="或空白内容的行
8. **必须跳过格式标记**：以"###"、"**"、"*"、"-"等markdown或格式符号开头的表头标记行
9. **必须跳过患者信息**：姓名、性别、年龄、住院号、样本号等非检验数据

【医学检验项目分类参考】：
- 血常规：白细胞(WBC)、红细胞(RBC)、血红蛋白(HGB)、血小板(PLT)及各项参数
- 肝功能：ALT、AST、ALP、GGT、TBIL、DBIL、TP、ALB、GLB等
- 肾功能：Cr、BUN、UA、CysC、β2-MG、eGFR等
- 血脂：TC、TG、HDL-C、LDL-C、ApoA1、ApoB、Lp(a)等
- 血糖：GLU、HbA1c等
- 电解质：K、Na、Cl、Ca、P、Mg等
- 凝血功能：PT、APTT、FIB、TT、INR等
- 心肌酶：CK、CK-MB、LDH、cTnI、cTnT、MYO等
- 甲状腺功能：TSH、FT3、FT4、T3、T4等
- 肿瘤标志物：CEA、AFP、CA19-9、CA125、CA15-3、PSA等

OCR识别的全量文本：
{full_text}

请按上述专业医学数据提取要求，精确提取所有检验数据字段。"""
        
        return prompt
    
    def build_demographic_prompt(self, full_text: str, fields: Optional[List[str]] = None) -> str:
        """
        构建人口学资料提取的专用prompt
        
        Args:
            full_text: OCR识别的全量文本
            fields: 需要提取的字段列表（可选）
            
        Returns:
            str: 人口学资料提取的prompt
        """
        default_fields = [
            "姓名", "性别", "年龄", "出生日期", "身份证号", 
            "联系电话", "手机号", "家庭住址", "民族", "婚姻状况",
            "职业", "工作单位", "联系人", "联系人电话", "医保类型",
            "就诊卡号", "病历号", "住院号"
        ]
        
        target_fields = fields if fields else default_fields
        fields_str = '、'.join(target_fields)
        
        prompt = f"""请从以下患者人口学资料OCR文本中提取指定的数据字段。

【人口学资料提取任务】
需要提取的字段：{fields_str}

【严格格式要求】：
1. 每个字段必须单独一行，使用冒号(:)或中文冒号(：)分隔字段名和值
2. 格式示例：字段名: 值  或  字段名：值
3. **绝对禁止使用竖线(|)或其他符号作为分隔符**
4. 只返回字段名和结果值，不要包含单位

【精确提取要求】：
1. OCR文本可能是表格格式或表单格式
2. 重点提取患者的个人基本信息
3. 对于年龄，请提取数字和单位（如：25岁、25）
4. 对于出生日期，请保持原始格式（如：1998-05-20、1998年5月20日）
5. 对于身份证号，请提取完整的18位号码
6. 对于电话号码，请保留区号和号码
7. 如果某个字段在文本中不存在，请不要返回该字段
8. 注意区分"联系电话"和"手机号"
9. 对于"联系人"，请提取紧急联系人姓名

【字段说明】：
- 姓名：患者的真实姓名
- 性别：男/女
- 年龄：患者年龄，可包含单位
- 出生日期：出生日期，保持原始格式
- 身份证号：18位身份证号码
- 联系电话/手机号：电话号码
- 家庭住址：家庭居住地址
- 民族：民族（如：汉族、回族等）
- 婚姻状况：未婚/已婚/离异/丧偶
- 职业：职业类型
- 工作单位：工作单位名称
- 联系人：紧急联系人姓名
- 联系人电话：紧急联系人电话
- 医保类型：医保类型（如：城镇职工、城乡居民、新农合等）
- 就诊卡号/病历号/住院号：医疗机构分配的编号

OCR识别的全量文本：
{full_text}

【正确输出示例】：
姓名：张三
性别：男
年龄：25岁
出生日期：1998-05-20
身份证号：110101199805201234
联系电话：13800138000
家庭住址：北京市朝阳区XX路XX号
民族：汉族
婚姻状况：未婚
职业：工程师
工作单位：XX科技有限公司
联系人：李四
联系人电话：13900139000
医保类型：城镇职工
病历号：202401001

现在请按上述人口学资料提取要求，精确提取以下字段：
{fields_str}"""
        
        return prompt
    
    def build_surgery_history_prompt(self, full_text: str, fields: Optional[List[str]] = None) -> str:
        """
        构建手术史资料提取的专用prompt
        
        Args:
            full_text: OCR识别的全量文本
            fields: 需要提取的字段列表（可选）
            
        Returns:
            str: 手术史资料提取的prompt
        """
        default_fields = [
            "手术日期", "手术名称", "手术持续时间", "手术开始时间", 
            "手术结束时间", "麻醉方式", "麻醉医师", "主刀医师", 
            "助手医师", "手术方式", "手术部位", "术前诊断", 
            "术后诊断", "手术过程", "术中出血量", "输血情况",
            "手术级别", "手术切口类型", "术后并发症", "手术效果"
        ]
        
        target_fields = fields if fields else default_fields
        fields_str = '、'.join(target_fields)
        
        prompt = f"""请从以下患者手术史资料OCR文本中提取指定的数据字段。

【手术史资料提取任务】
需要提取的字段：{fields_str}

【严格格式要求】：
1. 每个字段必须单独一行，使用冒号(:)或中文冒号(：)分隔字段名和值
2. 格式示例：字段名: 值  或  字段名：值
3. **绝对禁止使用竖线(|)或其他符号作为分隔符**
4. 只返回字段名和结果值，不要包含单位

【精确提取要求】：
1. OCR文本可能是手术记录、病历摘要或表格格式
2. 重点提取手术相关的关键信息
3. 对于手术日期，请保持原始格式（如：2024-03-20、2024年3月20日）
4. 对于手术持续时间，请提取并保持原始格式（如：2小时30分钟、2.5小时、150分钟）
5. 对于手术开始时间和结束时间，请提取具体时间（如：09:00、11:30）
6. 对于手术过程，请简要提取关键步骤，不需要过于详细
7. 对于术中出血量，请提取数值和单位（如：200ml、150毫升）
8. 如果有多次手术记录，请分别提取，使用序号区分（如：手术1、手术2）
9. 如果某个字段在文本中不存在，请不要返回该字段

【字段说明】：
- 手术日期：手术实施的日期
- 手术名称：手术的正式名称
- 手术持续时间：手术从开始到结束的总时长
- 手术开始时间：手术开始的具体时间
- 手术结束时间：手术结束的具体时间
- 麻醉方式：麻醉类型（如：全身麻醉、局部麻醉、椎管内麻醉等）
- 麻醉医师：负责麻醉的医师姓名
- 主刀医师：手术主刀医师姓名
- 助手医师：手术助手医师姓名
- 手术方式：手术的具体方法（如：腹腔镜手术、开腹手术等）
- 手术部位：手术的具体部位
- 术前诊断：手术前的诊断
- 术后诊断：手术后的诊断
- 手术过程：手术的主要过程描述（简要）
- 术中出血量：手术过程中的出血量
- 输血情况：是否输血及输血量
- 手术级别：手术的级别（如：一级、二级、三级、四级）
- 手术切口类型：手术切口类型（如：I类、II类、III类）
- 术后并发症：术后是否出现并发症
- 手术效果：手术效果评价

OCR识别的全量文本：
{full_text}

【正确输出示例】：
手术日期：2024-03-20
手术名称：腹腔镜下阑尾切除术
手术持续时间：1小时20分钟
手术开始时间：09:30
手术结束时间：10:50
麻醉方式：全身麻醉
麻醉医师：王医师
主刀医师：李医师
助手医师：张医师
手术方式：腹腔镜手术
手术部位：右下腹
术前诊断：急性阑尾炎
术后诊断：急性化脓性阑尾炎
手术过程：常规消毒铺巾，腹腔镜探查，发现阑尾充血肿胀，分离阑尾系膜，结扎阑尾根部，切除阑尾，取出标本
术中出血量：50ml
输血情况：未输血
手术级别：二级
手术切口类型：I类
术后并发症：无
手术效果：手术顺利，术后恢复良好

现在请按上述手术史资料提取要求，精确提取以下字段：
{fields_str}"""
        
        return prompt
    
    def build_imaging_prompt(self, full_text: str, fields: Optional[List[str]] = None) -> str:
        """
        构建影像检查报告提取的专用prompt
        
        Args:
            full_text: OCR识别的全量文本
            fields: 需要提取的字段列表（可选）
            
        Returns:
            str: 影像检查报告提取的prompt
        """
        default_fields = [
            # 检查基本信息
            "检查类别", "检查类别名称", "检查项目", "检查日期", "检查时间",
            "申请时间", "报告时间", "申请医生", "报告医生", "检查医生",
            # 检查所见
            "诊断所见", "影像发现", "检查所见",
            # 诊断印象
            "诊断印象", "影像结论", "临床建议",
            # 其他重要信息
            "检查医院", "科室", "检查部位", "检查方法"
        ]
        
        target_fields = fields if fields else default_fields
        fields_str = '、'.join(target_fields)
        
        prompt = f"""请从以下医学影像检查报告OCR文本中提取指定的数据字段。

【影像检查报告提取任务】
需要提取的字段：{fields_str}

【严格格式要求】：
1. 每个字段必须单独一行，使用冒号(:)或中文冒号(：)分隔字段名和值
2. 格式示例：字段名: 值  或  字段名：值
3. **绝对禁止使用竖线(|)或其他符号作为分隔符**
4. 只返回字段名和结果值
5. 对于描述性文本（如诊断所见、诊断印象），保持完整内容

【精确提取要求】：
1. OCR文本可能是超声、CT、MRI、X线等影像检查报告
2. **重点区分"诊断所见"和"诊断印象"**：
   - 诊断所见：详细的影像描述，包含器官形态、回声/密度、血流等信息
   - 诊断印象：最终的诊断结论，通常在报告末尾
3. 对于检查类别，识别影像类型（如：US=超声、CT、MRI、X线=X光）
4. 对于日期时间，保持原始格式（如：2026/3/31 15:49:18）
5. 对于医生信息，区分申请医生、报告医生、检查医生
6. **描述性字段（诊断所见、诊断印象）必须完整提取，不能截断**
7. 如果包含"诊断所见"和"诊断印象"两个标题，请分别提取对应的内容
8. 如果只有"影像结论"，将其作为"诊断印象"提取

【字段说明】：
- 检查类别/检查类别名称：影像检查类型（如：超声、US、CT、MRI、X线、X光）
- 检查项目：具体的检查项目名称（如：腹部超声、胸部CT、钡灌肠造影）
- 检查日期：检查实施日期
- 检查时间：检查实施的具体时间
- 申请时间：检查申请的时间
- 报告时间：报告生成的时间
- 申请医生：开具检查申请的医生
- 报告医生：撰写报告的医生
- 检查医生：执行检查的医生
- 诊断所见/影像发现/检查所见：详细的影像描述内容（完整提取）
- 诊断印象/影像结论/临床建议：最终的诊断结论（完整提取）
- 检查医院：医院名称
- 科室：申请科室
- 检查部位：检查的身体部位
- 检查方法：检查的具体方法（如：经肛门置管造影）

OCR识别的全量文本：
{full_text}

【正确输出示例】：
检查类别：超声
检查类别名称：US
检查项目：腹部超声
检查日期：2026/3/31
检查时间：2026/3/31 15:49:18
申请时间：2026/3/31 15:49:18
报告时间：2026/3/31 16:18:17
申请医生：陈玲婷
报告医生：李婉林
检查医生：李婉林
诊断所见：造瘘袋覆盖，部分切面显示欠清；肠管：大部分肠腔内较多气体及内容物回声，能显示的肠管未见明显扩张，肠壁未见明显增厚，肠蠕动可。阑尾：阑尾区未见明显肿大包块。淋巴结：腹腔内肠系膜区未见明显肿大淋巴结回声。腹水：肝肾隐窝、脾肾之间、肠曲间及膀胱后方未见明显游离无回声区。CDFI：所示切面未见明显异常血流信号。
诊断印象：结肠造瘘术后：可显示腹腔未见明显异常 请结合临床

现在请按上述影像检查报告提取要求，精确提取以下字段：
{fields_str}"""
        
        return prompt
    
    def build_lab_result_prompt(self, full_text: str, fields: Optional[List[str]] = None) -> str:
        """
        构建检查结果（胃肠科检查指标）提取的专用prompt
        
        Args:
            full_text: OCR识别的全量文本
            fields: 需要提取的字段列表（可选）
            
        Returns:
            str: 检查结果提取的prompt
        """
        # 胃肠科常见检查指标
        default_fields = [
            # 血常规
            "白细胞计数", "红细胞计数", "血红蛋白", "血小板计数",
            "中性粒细胞百分比", "淋巴细胞百分比", "单核细胞百分比",
            "嗜酸性粒细胞百分比", "嗜碱性粒细胞百分比",
            # 肝功能
            "谷丙转氨酶", "谷草转氨酶", "谷氨酰转肽酶", "碱性磷酸酶",
            "总胆红素", "直接胆红素", "间接胆红素",
            "总蛋白", "白蛋白", "球蛋白", "白球比",
            # 肾功能
            "肌酐", "尿素氮", "尿酸", "估算肾小球滤过率",
            # 电解质
            "钾", "钠", "氯", "钙", "磷", "镁",
            # 胃肠相关
            "胃蛋白酶原I", "胃蛋白酶原II", "胃蛋白酶原比值",
            "幽门螺杆菌抗体", "胃泌素-17",
            # 凝血功能
            "凝血酶原时间", "活化部分凝血活酶时间", "纤维蛋白原",
            # 肿瘤标志物
            "癌胚抗原", "甲胎蛋白", "糖类抗原19-9", "糖类抗原125",
            # 血脂
            "总胆固醇", "甘油三酯", "高密度脂蛋白胆固醇", "低密度脂蛋白胆固醇",
            # 血糖
            "空腹血糖", "糖化血红蛋白"
        ]
        
        target_fields = fields if fields else default_fields
        fields_str = '、'.join(target_fields)
        
        prompt = f"""请从以下胃肠科检查结果OCR文本中提取指定的检验数据字段。

【胃肠科检查结果提取任务】
需要提取的字段：{fields_str}

【严格格式要求】：
1. 每个字段必须单独一行，使用冒号(:)或中文冒号(：)分隔字段名和值
2. 格式示例：字段名: 值  或  字段名：值
3. **绝对禁止使用竖线(|)或其他符号作为分隔符**
4. 只返回字段名和结果值，不要包含参考范围和单位在冒号前面
5. 数值必须包含单位（如：g/L, mmol/L, ×10^9/L, U/L, %, μmol/L等）

【精确提取要求】：
1. OCR文本通常是表格格式，使用竖线(|)、制表符或空格分隔各列
2. 表格格式通常是：项目名称 | 结果 | 参考范围 | 单位  或  项目名称  结果  参考范围  单位
3. **必须提取"结果"列的值，而不是"参考范围"或"单位"列**
4. 数值必须包含单位，如果结果包含箭头标记(↑↓←→)、异常标记(H/L/N)，请保留在数值中
5. 对于多值字段，必须将每个具体项单独列出
6. **必须跳过表头行**：包含"项目名称"、"结果"、"参考范围"、"单位"、"Test"、"Result"、"Normal"等关键词的行
7. **必须跳过分隔行**：只包含"---"、"|---|---|"、"==="、"==="或空白内容的行
8. **必须跳过格式标记**：以"###"、"**"、"*"等markdown符号开头的表头标记行
9. **必须跳过患者信息**：姓名、性别、年龄、住院号、样本号等非检验数据

【胃肠科重点检查项目】：
- 血常规：白细胞、红细胞、血红蛋白、血小板及其分类
- 肝功能：ALT、AST、GGT、ALP、胆红素、蛋白（评估肝脏功能）
- 肾功能：肌酐、尿素氮、尿酸（评估肾脏功能）
- 电解质：钾、钠、氯、钙、磷、镁（评估电解质平衡）
- 胃肠特异性指标：胃蛋白酶原I/II、幽门螺杆菌抗体、胃泌素-17（评估胃黏膜状态）
- 凝血功能：PT、APTT、FIB（评估凝血功能）
- 肿瘤标志物：CEA、AFP、CA19-9、CA125（筛查消化道肿瘤）
- 血脂：TC、TG、HDL-C、LDL-C（评估脂代谢）
- 血糖：空腹血糖、HbA1c（评估糖代谢）

OCR识别的全量文本：
{full_text}

【正确输出示例】：
白细胞计数：5.8 ×10^9/L
红细胞计数：4.5 ×10^12/L
血红蛋白：135 g/L
血小板计数：210 ×10^9/L
中性粒细胞百分比：65.2%
淋巴细胞百分比：28.5%
谷丙转氨酶：25 U/L
谷草转氨酶：28 U/L
谷氨酰转肽酶：35 U/L
总胆红素：15.2 μmol/L
直接胆红素：4.5 μmol/L
间接胆红素：10.7 μmol/L
总蛋白：72 g/L
白蛋白：45 g/L
球蛋白：27 g/L
白球比：1.67
肌酐：78 μmol/L
尿素氮：5.2 mmol/L
尿酸：320 μmol/L
估算肾小球滤过率：105 ml/min
钾：4.2 mmol/L
钠：140 mmol/L
氯：103 mmol/L
钙：2.35 mmol/L
磷：1.15 mmol/L
胃蛋白酶原I：120 μg/L
胃蛋白酶原II：12 μg/L
胃蛋白酶原比值：10.0
幽门螺杆菌抗体：阳性
胃泌素-17：5.2 pmol/L
凝血酶原时间：12.5 秒
活化部分凝血活酶时间：32.0 秒
纤维蛋白原：3.2 g/L
癌胚抗原：2.5 ng/mL
甲胎蛋白：3.2 ng/mL
糖类抗原19-9：15.8 U/mL
糖类抗原125：18.5 U/mL
总胆固醇：5.2 mmol/L
甘油三酯：1.3 mmol/L
高密度脂蛋白胆固醇：1.4 mmol/L
低密度脂蛋白胆固醇：2.9 mmol/L
空腹血糖：5.1 mmol/L
糖化血红蛋白：5.3%

现在请按上述胃肠科检查结果提取要求，精确提取以下字段：
{fields_str}"""
        
        return prompt
    
    def build_general_ocr_prompt(self, full_text: str, fields: Optional[List[str]] = None) -> str:
        """
        构建通用OCR提取的prompt（用于其他类型文件）
        
        Args:
            full_text: OCR识别的全量文本
            fields: 需要提取的字段列表（可选）
            
        Returns:
            str: 通用OCR提取的prompt
        """
        if fields:
            return self._build_field_specific_prompt(full_text, fields)
        else:
            prompt = f"""请从以下OCR文本中提取所有可见的关键信息，并以结构化格式返回。

【通用OCR文本提取任务】

【严格格式要求】：
1. 每个字段必须单独一行，使用冒号(:)或中文冒号(：)分隔字段名和值
2. 格式示例：字段名: 值  或  字段名：值
3. **绝对禁止使用竖线(|)或其他符号作为分隔符**
4. 只返回字段名和结果值

【精确提取要求】：
1. OCR文本可能包含各种格式（表格、表单、段落等）
2. 提取所有可见的标题、字段名和对应的值
3. 对于日期、时间、数字、金额等关键信息，请准确提取
4. 对于表格数据，请按行提取每列的内容
5. 对于表单数据，请提取字段标签和对应的值
6. 保持原文本的层次结构和逻辑关系
7. 如果文本包含多部分内容，请用空行分隔
8. **必须跳过表头行**：包含"项目名称"、"结果"、"参考范围"、"单位"等关键词的行
9. **必须跳过分隔行**：只包含"---"、"|---|---|"、"==="、"==="或空白内容的行
10. **必须跳过格式标记**：以"###"、"**"、"*"等markdown符号开头的表头标记行

OCR识别的全量文本：
{full_text}

请按上述通用OCR文本提取要求，提取所有可见的关键信息。"""
        
        return prompt


class ResponseParser:
    """响应解析器 - 负责解析LLM的响应"""
    
    def __init__(self):
        self.matcher = FieldMatcher()
        self.validator = DataValidator()
    
    def parse(self, content: str, fields: Optional[List[str]] = None) -> Tuple[Dict[str, str], List[str]]:
        """
        解析LLM响应
        
        Args:
            content: LLM返回的原始内容
            fields: 用户请求的字段列表（用于过滤）
            
        Returns:
            tuple: (提取的数据字典, 验证警告列表)
        """
        extracted_data = {}
        validation_warnings = []
        
        # 去重
        lines = list(dict.fromkeys(content.split('\n')))
        
        for line in lines:
            line = line.strip()
            if not line or line.startswith('```') or line.startswith('#'):
                continue
            
            # 尝试解析
            key, value = self._parse_line(line)
            
            if key and value:
                # 验证字段是否在请求列表中
                if fields and not self._is_field_valid(key, fields):
                    continue
                
                # 数据验证
                is_valid, error_msg = self.validator.validate_value(key, value)
                if not is_valid:
                    validation_warnings.append(f"{key}: {error_msg}")
                
                # 清理值
                cleaned_value = self.validator.clean_value(value)
                
                # 保存数据
                if cleaned_value:
                    if key in extracted_data:
                        if extracted_data[key] != cleaned_value:
                            counter = 1
                            while f"{key}_{counter}" in extracted_data:
                                counter += 1
                            extracted_data[f"{key}_{counter}"] = cleaned_value
                    else:
                        extracted_data[key] = cleaned_value
        
        return extracted_data, validation_warnings
    
    def _parse_line(self, line: str) -> Tuple[Optional[str], Optional[str]]:
        """解析单行数据"""
        # 优先尝试冒号分隔符
        separators = [':', '：']
        for sep in separators:
            pos = line.find(sep)
            if pos > 0:
                key = line[:pos].strip()
                value = line[pos + 1:].strip()
                
                # 清理键
                key = key.replace('**', '').replace('*', '').replace('【', '').replace('】', '')
                key = ' '.join(key.split())
                
                # 清理值
                value = value.replace('**', '').replace('*', '')
                value = ' '.join(value.split())
                
                # 验证有效性
                if key and value and value not in ['|', '：', ':', '-', '—', '']:
                    return key, value
        
        # 尝试竖线分隔符（表格格式）
        if '|' in line:
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 3:
                key = parts[0].replace('**', '').replace('*', '').strip()
                value = parts[1].replace('**', '').replace('*', '').strip()
                
                key = ' '.join(key.split())
                value = ' '.join(value.split())
                
                if key and value and value not in ['|', '：', ':', '-', '—', '']:
                    return key, value
        
        return None, None
    
    def _is_field_valid(self, field_name: str, requested_fields: List[str]) -> bool:
        """验证字段是否在请求列表中"""
        for requested_field in requested_fields:
            if self.matcher.is_match(field_name, requested_field):
                return True
        return False


class LLMExtractor:
    """LLM数据提取器 - 重构版"""
    
    def __init__(self):
        """初始化提取器"""
        self.use_cloud = Config.USE_CLOUD_MODELS
        
        # 本地LM Studio配置
        self.lmstudio_host = Config.LMSTUDIO_HOST
        self.lmstudio_model = Config.LMSTUDIO_MODEL
        self.lmstudio_timeout = Config.LMSTUDIO_TIMEOUT
        
        # 硅胶流动云端API配置
        self.api_key = Config.SILICONFLOW_API_KEY
        self.api_base = Config.SILICONFLOW_API_BASE
        self.model = Config.LLM_MODEL
        self.timeout = Config.LLM_TIMEOUT
        
        # 初始化组件
        self.prompt_builder = PromptBuilder()
        self.response_parser = ResponseParser()
    
    def _call_lmstudio_api(self, messages: list) -> Dict:
        """调用本地LM Studio API"""
        headers = {'Content-Type': 'application/json'}
        
        payload = {
            'model': self.lmstudio_model,
            'messages': messages,
            'temperature': 0.1,
            'stream': False
        }
        
        print(f"  正在发送请求到 LM Studio: {self.lmstudio_host}")
        print(f"  使用模型: {self.lmstudio_model}")
        
        response = requests.post(
            f"{self.lmstudio_host}/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.lmstudio_timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def _call_cloud_api(self, messages: list) -> Dict:
        """调用硅胶流动云端LLM API"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'model': self.model,
            'messages': messages,
            'stream': False,
            'max_tokens': 4096,
            'temperature': 0.1
        }
        
        print(f"  正在发送请求到硅胶流动API: {self.api_base}")
        print(f"  使用模型: {self.model}")
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def extract_fields(
        self, 
        full_text: str, 
        fields: Optional[List[str]] = None,
        model_type: str = None,
        data_type: str = "lab_result"
    ) -> Dict:
        """
        从全量OCR文本中提取指定字段
        
        Args:
            full_text: OCR识别的全量文本
            fields: 需要提取的字段列表，如果为None则提取所有常见字段
            model_type: 模型类型（cloud/local），如果为None则使用配置中的默认模式
            data_type: 资料类型，可选值：
                - "demographic": 人口学资料
                - "surgery_history": 手术史
                - "lab_result": 检查结果（默认）
                - "general": 其他文件（通用OCR）
            
        Returns:
            Dict: 包含提取结果的字典
                - success: 是否成功
                - extracted_data: 提取的数据（键值对）
                - validation_warnings: 验证警告列表
                - error: 错误信息（如果有）
        """
        try:
            # 构建提示词
            prompt = self.prompt_builder.build_prompt(full_text, fields, data_type)
            
            # 构造请求消息
            messages = [{'role': 'user', 'content': prompt}]
            
            # 确定使用哪种API
            if model_type == "local":
                use_cloud = False
            elif model_type == "cloud":
                use_cloud = True
            else:
                use_cloud = self.use_cloud
            
            # 调用API
            if use_cloud:
                print(f"  使用云端硅胶流动API: {self.model}")
                result = self._call_cloud_api(messages)
            else:
                print(f"  使用本地LM Studio模型: {self.lmstudio_model}")
                result = self._call_lmstudio_api(messages)
            
            # 解析响应
            if 'choices' in result and len(result['choices']) > 0:
                content = result['choices'][0]['message']['content'].strip()
            else:
                return {
                    'success': False,
                    'error': 'API返回格式异常'
                }
            
            print(f"  LLM 原始响应:\n{content}\n")
            
            # 解析响应内容
            extracted_data, validation_warnings = self.response_parser.parse(content, fields)
            
            print(f"  共提取到 {len(extracted_data)} 个字段")
            
            # 构建返回结果
            result_dict = {
                'success': True,
                'extracted_data': extracted_data
            }
            
            # 如果有验证警告，添加到结果中
            if validation_warnings:
                result_dict['validation_warnings'] = validation_warnings
                print(f"  ⚠ 共有 {len(validation_warnings)} 个验证警告")
            
            return result_dict
                
        except requests.exceptions.Timeout:
            return {
                'success': False,
                'error': 'API请求超时，请检查服务是否运行'
            }
        except requests.exceptions.ConnectionError:
            return {
                'success': False,
                'error': '无法连接到API服务，请检查服务是否运行'
            }
        except requests.exceptions.RequestException as e:
            error_msg = f'API请求失败: {str(e)}'
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f' - 详情: {error_detail}'
                except:
                    error_msg += f' - 状态码: {e.response.status_code}'
            return {
                'success': False,
                'error': error_msg
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'未知错误: {str(e)}'
            }