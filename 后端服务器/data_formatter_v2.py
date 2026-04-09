"""
数据格式化处理模块 V2.0 - 基于实际测试文件重新设计

功能：
- 格式化OCR提取的JSON数据
- 标准化字段名称和数值格式
- 处理特殊格式的医疗数据
- 支持多种资料类型的差异化处理

改进点：
1. 基于实际测试文件优化格式化规则
2. 增强数值提取和单位处理
3. 支持JSON数组和对象的灵活处理
4. 优化异常标记识别
5. 增强医学单位标准化
"""

import json
import re
from typing import Dict, List, Any, Optional, Union
from datetime import datetime


class MedicalDataFormatterV2:
    """医学数据格式化器 V2.0"""
    
    # 医学单位标准化映射
    UNIT_STANDARDIZATION = {
        # 温度
        '℃': '°C',
        '摄氏度': '°C',
        # 体重
        'Kg': 'kg',
        '公斤': 'kg',
        '千克': 'kg',
        # 长度
        'cm': 'cm',
        '毫米': 'mm',
        '公分': 'cm',
        # 频率
        '次/分': '次/min',
        '次/分钟': '次/min',
        # 压力
        'mmHg': 'mmHg',
        '毫米汞柱': 'mmHg',
        # 浓度
        'IU/mL': 'IU/mL',
        'mIU/mL': 'mIU/mL',
        'COI': 'COI',
        # 血细胞
        '×10^9/L': '×10^9/L',
        'g/L': 'g/L',
        'mmol/L': 'mmol/L',
        'μmol/L': 'μmol/L',
        'U/L': 'U/L',
        '%': '%'
    }
    
    # 检验结果标准化映射
    RESULT_STANDARDIZATION = {
        # 定性结果
        '阳性(+)': '阳性',
        '阳性': '阳性',
        '阴性': '阴性',
        '(-)': '阴性',
        '(+)': '阳性',
        # 血型
        '"B"型': 'B型',
        '"A"型': 'A型',
        '"AB"型': 'AB型',
        '"O"型': 'O型',
        # 数值标记
        '<': '<',
        '>': '>',
        '≤': '≤',
        '≥': '≥'
    }
    
    def __init__(self):
        """初始化格式化器"""
        self.formatted_data = {}
    
    def format_data(self, raw_data: Union[Dict, List], data_category: str) -> Dict[str, Any]:
        """
        格式化原始OCR数据
        
        Args:
            raw_data: OCR提取的原始数据（JSON对象或数组）
            data_category: 资料分类（人口学信息、检查结果、既往手术史、其他）
        
        Returns:
            Dict: 格式化后的数据
        """
        try:
            # 解析JSON字符串（如果需要）
            if isinstance(raw_data, str):
                raw_data = json.loads(raw_data)
            
            # 根据资料类型选择格式化策略
            if data_category == "人口学信息":
                return self._format_demographic_data(raw_data)
            elif data_category == "检查结果":
                return self._format_lab_results(raw_data)
            elif data_category == "既往手术史":
                return self._format_surgery_history(raw_data)
            else:
                return self._format_general_data(raw_data)
                
        except Exception as e:
            print(f"[ERROR] 数据格式化失败: {str(e)}")
            return {
                "success": False,
                "error": f"数据格式化失败: {str(e)}",
                "raw_data": raw_data
            }
    
    def _format_demographic_data(self, raw_data: Union[Dict, List]) -> Dict[str, Any]:
        """
        格式化人口学数据
        
        处理：入院记录、病历首页等
        
        优化点：
        - 处理生命体征数值
        - 标准化体重单位
        - 提取体格检查关键信息
        """
        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else {}
        
        formatted = {
            "data_type": "demographic",
            "items": []
        }
        
        # 基本信息
        basic_info = {}
        for key in ["姓名", "性别", "年龄", "出生日期", "身份证号", "科室", "床号", "病案号", "住院号"]:
            if key in raw_data:
                value = raw_data[key]
                # 特殊处理
                if key == "年龄" and value and isinstance(value, str):
                    # 提取年龄数字，去除单位
                    age_match = re.search(r'(\d+)', value)
                    if age_match:
                        basic_info[f"{key}_数值"] = int(age_match.group(1))
                basic_info[key] = value
        
        # 生命体征
        vital_signs = {}
        for key in ["体温", "脉搏", "呼吸", "体重", "血压"]:
            if key in raw_data:
                value = raw_data[key]
                if value:
                    vital_signs[key] = self._format_vital_sign(key, value)
        
        # 体格检查
        physical_exam = {}
        for key in ["神志", "精神状态", "营养状况", "发育状况", "前囟状态", "心尖搏动位置"]:
            if key in raw_data and raw_data[key]:
                physical_exam[key] = raw_data[key]
        
        # 家族史
        family_history = {}
        for key in ["母亲健康状况", "是否近亲结婚", "家族遗传史", "母妊娠史"]:
            if key in raw_data and raw_data[key]:
                family_history[key] = raw_data[key]
        
        # 联系信息
        contact_info = {}
        for key in ["联系电话", "家庭住址", "民族", "婚姻状况", "职业", "工作单位"]:
            if key in raw_data and raw_data[key]:
                contact_info[key] = raw_data[key]
        
        # 构建结果
        if basic_info:
            formatted["basic_info"] = basic_info
        if vital_signs:
            formatted["vital_signs"] = vital_signs
        if physical_exam:
            formatted["physical_exam"] = physical_exam
        if family_history:
            formatted["family_history"] = family_history
        if contact_info:
            formatted["contact_info"] = contact_info
        
        # 添加时间戳
        formatted["formatted_time"] = datetime.now().isoformat()
        
        return formatted
    
    def _format_vital_sign(self, sign_type: str, value: str) -> Dict[str, Any]:
        """
        格式化生命体征数据
        
        Args:
            sign_type: 生命体征类型（体温、脉搏、呼吸、体重、血压）
            value: 原始值
        
        Returns:
            Dict: 格式化后的生命体征数据
        """
        result = {"raw_value": value}
        
        if sign_type == "体温":
            # 提取数值和单位
            match = re.search(r'([\d.]+)\s*([°℃C]?)', value)
            if match:
                result["value"] = float(match.group(1))
                result["unit"] = "°C"
        
        elif sign_type in ["脉搏", "呼吸"]:
            # 提取数值和单位
            match = re.search(r'(\d+)\s*(次/分|次/min|bpm)', value)
            if match:
                result["value"] = int(match.group(1))
                result["unit"] = "次/min"
        
        elif sign_type == "体重":
            # 提取数值和单位
            match = re.search(r'([\d.]+)\s*(kg|Kg|公斤|千克)', value)
            if match:
                result["value"] = float(match.group(1))
                result["unit"] = "kg"
        
        elif sign_type == "血压":
            # 提取收缩压和舒张压
            match = re.search(r'(\d+)/(\d+)\s*(mmHg)?', value)
            if match:
                result["systolic"] = int(match.group(1))
                result["diastolic"] = int(match.group(2))
                result["unit"] = "mmHg"
        
        return result
    
    def _format_lab_results(self, raw_data: Union[Dict, List]) -> Dict[str, Any]:
        """
        格式化检查结果数据
        
        处理：检验报告、影像报告等
        
        优化点：
        - 支持多检验项目数组
        - 标准化检验结果格式
        - 识别异常标记
        - 处理特殊数值格式（如[<0.05]阴性）
        """
        formatted = {
            "data_type": "lab_result",
            "items": []
        }
        
        # 处理数组格式（多个检验项目）
        if isinstance(raw_data, list):
            for item in raw_data:
                formatted_item = self._format_single_lab_item(item)
                if formatted_item:
                    formatted["items"].append(formatted_item)
        else:
            # 处理单个检验项目
            formatted_item = self._format_single_lab_item(raw_data)
            if formatted_item:
                formatted["items"].append(formatted_item)
        
        # 如果是影像检查，添加特殊处理
        if any("检查类别" in str(item) for item in formatted["items"]):
            formatted["is_imaging"] = True
            formatted = self._enhance_imaging_data(formatted)
        
        # 添加时间戳
        formatted["formatted_time"] = datetime.now().isoformat()
        
        return formatted
    
    def _format_single_lab_item(self, item: Dict) -> Optional[Dict]:
        """
        格式化单个检验项目
        
        Args:
            item: 单个检验项目的原始数据
        
        Returns:
            Dict: 格式化后的检验项目
        """
        if not item:
            return None
        
        formatted = {}
        
        # 基本字段
        for key in ["检验项目", "项目编码", "检验类型", "检验日期"]:
            if key in item and item[key]:
                formatted[key] = item[key]
        
        # 处理检验结果
        if "检验结果" in item:
            result_value = item["检验结果"]
            formatted["raw_result"] = result_value
            
            # 解析结果值和定性判断
            parsed = self._parse_lab_result(result_value)
            formatted.update(parsed)
        
        # 处理单位
        if "单位" in item and item["单位"]:
            formatted["unit"] = self._standardize_unit(item["单位"])
        
        # 处理参考范围
        if "参考范围" in item and item["参考范围"]:
            formatted["reference_range"] = item["参考范围"]
        
        # 处理异常标记
        if "异常标记" in item and item["异常标记"]:
            formatted["is_abnormal"] = True
            formatted["abnormal_marker"] = item["异常标记"]
        elif "结果判断" in item:
            result_judgment = item["结果判断"]
            if result_judgment and "阳性" in str(result_judgment):
                # 需要结合参考范围判断是否异常
                formatted["is_positive"] = True
            elif result_judgment:
                formatted["result_judgment"] = result_judgment
        
        return formatted
    
    def _parse_lab_result(self, result: str) -> Dict[str, Any]:
        """
        解析检验结果
        
        处理格式：
        - "[<0.05]阴性" - 数值+定性
        - ">1000.00" - 纯数值
        - "B型" - 定性结果
        - "<0.10 阴性" - 数值+定性
        
        Args:
            result: 检验结果字符串
        
        Returns:
            Dict: 解析后的结果
        """
        parsed = {}
        
        # 检查是否包含方括号格式
        bracket_match = re.search(r'\[([^\]]+)\]\s*([阳性阴性]+)?', result)
        if bracket_match:
            # 提取数值部分
            numeric_part = bracket_match.group(1)
            parsed["result_value"] = numeric_part
            
            # 提取定性判断
            qualitative = bracket_match.group(2)
            if qualitative:
                parsed["result_qualitative"] = self._standardize_result(qualitative)
        else:
            # 处理其他格式
            # 检查是否包含空格分隔的数值和定性结果
            space_match = re.match(r'([\d.<>]+)\s+([阳性阴性]+)', result)
            if space_match:
                parsed["result_value"] = space_match.group(1)
                parsed["result_qualitative"] = self._standardize_result(space_match.group(2))
            else:
                # 纯定性结果或纯数值
                if any(c in result for c in ['阳', '阴', '+', '-']):
                    parsed["result_qualitative"] = self._standardize_result(result)
                else:
                    parsed["result_value"] = result
        
        # 标准化定性结果
        if "result_qualitative" in parsed:
            parsed["result_qualitative"] = self._standardize_result(parsed["result_qualitative"])
        
        return parsed
    
    def _standardize_result(self, result: str) -> str:
        """
        标准化检验结果
        
        Args:
            result: 原始结果
        
        Returns:
            str: 标准化后的结果
        """
        result = result.strip()
        
        # 去除引号
        result = result.replace('"', '').replace("'", "")
        
        # 标准化映射
        for old, new in self.RESULT_STANDARDIZATION.items():
            if old in result:
                result = result.replace(old, new)
        
        return result
    
    def _standardize_unit(self, unit: str) -> str:
        """
        标准化单位
        
        Args:
            unit: 原始单位
        
        Returns:
            str: 标准化后的单位
        """
        unit = unit.strip()
        
        # 标准化映射
        for old, new in self.UNIT_STANDARDIZATION.items():
            if old in unit:
                unit = unit.replace(old, new)
        
        return unit
    
    def _enhance_imaging_data(self, formatted: Dict) -> Dict:
        """
        增强影像检查数据
        
        处理：超声、X线、CT、MRI等影像报告
        
        优化点：
        - 提取影像所见和诊断印象
        - 解析解剖测量值
        - 识别检查技术参数
        """
        imaging_data = {}
        
        # 遍历所有项目，提取影像相关信息
        for item in formatted.get("items", []):
            # 检查基本信息
            for key in ["检查类别", "检查子类", "检查项目", "检查部位", "检查方法"]:
                if key in item and key not in imaging_data:
                    imaging_data[key] = item[key]
            
            # 检查所见
            if "诊断所见" in item:
                imaging_data["findings"] = item["诊断所见"]
            elif "影像发现" in item:
                imaging_data["findings"] = item["影像发现"]
            
            # 诊断印象
            if "诊断印象" in item:
                imaging_data["impression"] = item["诊断印象"]
            elif "影像结论" in item:
                imaging_data["impression"] = item["影像结论"]
            
            # 人员信息
            for key in ["申请医生", "报告医生", "审核医生"]:
                if key in item and key not in imaging_data:
                    imaging_data[key] = item[key]
            
            # 时间信息
            for key in ["检查时间", "报告时间", "申请时间"]:
                if key in item and item[key]:
                    imaging_data[key] = item[key]
        
        # 提取解剖测量值
        if "findings" in imaging_data:
            measurements = self._extract_anatomical_measurements(imaging_data["findings"])
            if measurements:
                imaging_data["measurements"] = measurements
        
        formatted["imaging_data"] = imaging_data
        
        return formatted
    
    def _extract_anatomical_measurements(self, findings: str) -> Dict[str, str]:
        """
        从影像所见中提取解剖测量值
        
        Args:
            findings: 影像所见文本
        
        Returns:
            Dict: 测量值字典
        """
        measurements = {}
        
        # 常见测量模式
        patterns = [
            r'(\w+[\u4e00-\u9fa5]*)距离\s*([：:]\s*)?([\d.]+)\s*(cm|mm)',
            r'([\d.]+)\s*(cm|mm)\s*([距离长度宽度高度直径厚度])',
            r'([\d.]+)\s*×\s*([\d.]+)\s*(cm|mm)',
        ]
        
        for pattern in patterns:
            matches = re.finditer(pattern, findings)
            for match in matches:
                if len(match.groups()) == 3:
                    key, value, unit = match.groups()
                    measurements[key] = f"{value}{unit}"
                elif len(match.groups()) == 4:
                    key, sep, value, unit = match.groups()
                    measurements[key] = f"{value}{unit}"
        
        return measurements
    
    def _format_surgery_history(self, raw_data: Union[Dict, List]) -> Dict[str, Any]:
        """
        格式化手术史数据
        
        处理：手术记录、麻醉记录等
        """
        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else {}
        
        formatted = {
            "data_type": "surgery_history",
            "items": []
        }
        
        # 手术基本信息
        surgery_info = {}
        for key in ["手术日期", "手术名称", "手术方式", "手术部位", "麻醉方式"]:
            if key in raw_data and raw_data[key]:
                surgery_info[key] = raw_data[key]
        
        # 人员信息
        personnel = {}
        for key in ["主刀医师", "助手医师", "麻醉医师"]:
            if key in raw_data and raw_data[key]:
                personnel[key] = raw_data[key]
        
        # 诊断信息
        diagnosis = {}
        for key in ["术前诊断", "术后诊断"]:
            if key in raw_data and raw_data[key]:
                diagnosis[key] = raw_data[key]
        
        # 手术过程和结果
        procedure = {}
        for key in ["手术过程", "术中出血量", "输血情况", "手术并发症", "手术结果"]:
            if key in raw_data and raw_data[key]:
                procedure[key] = raw_data[key]
        
        # 构建结果
        if surgery_info:
            formatted["surgery_info"] = surgery_info
        if personnel:
            formatted["personnel"] = personnel
        if diagnosis:
            formatted["diagnosis"] = diagnosis
        if procedure:
            formatted["procedure"] = procedure
        
        formatted["formatted_time"] = datetime.now().isoformat()
        
        return formatted
    
    def _format_general_data(self, raw_data: Union[Dict, List]) -> Dict[str, Any]:
        """
        格式化通用数据
        
        处理：其他类型的医疗文档
        """
        if isinstance(raw_data, list):
            raw_data = raw_data[0] if raw_data else {}
        
        formatted = {
            "data_type": "general",
            "items": [],
            "raw_data": raw_data
        }
        
        # 直接返回原始数据，添加时间戳
        formatted["formatted_time"] = datetime.now().isoformat()
        
        return formatted


# 便捷函数
def format_medical_data(raw_data: Union[Dict, List], data_category: str) -> Dict[str, Any]:
    """
    格式化医学数据的便捷函数
    
    Args:
        raw_data: OCR提取的原始数据
        data_category: 资料分类
    
    Returns:
        Dict: 格式化后的数据
    """
    formatter = MedicalDataFormatterV2()
    return formatter.format_data(raw_data, data_category)


# 测试代码
if __name__ == "__main__":
    # 测试人口学数据格式化
    test_demographic = {
        "姓名": "陈宏赫",
        "性别": "男",
        "年龄": "新生儿",
        "科室": "新生儿外科病房",
        "床号": "9",
        "病案号": "E0089181",
        "住院号": "R516707",
        "体温": "36.6℃",
        "脉搏": "130次/分",
        "呼吸": "30次/分",
        "体重": "14Kg",
        "血压": "80/52mmHg"
    }
    
    result = format_medical_data(test_demographic, "人口学信息")
    print("人口学数据格式化结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # 测试检验结果格式化
    test_lab_result = [
        {
            "检验项目": "乙肝表面抗原",
            "项目编码": "HBsAg",
            "检验结果": "[<0.05]阴性",
            "单位": "IU/mL",
            "参考范围": "<0.05",
            "结果判断": "阴性"
        },
        {
            "检验项目": "乙肝表面抗体",
            "项目编码": "HBsAb",
            "检验结果": "[>1000.00]阳性",
            "单位": "mIU/mL",
            "参考范围": "<10.00",
            "结果判断": "阳性",
            "异常标记": "红色加粗"
        }
    ]
    
    result = format_medical_data(test_lab_result, "检查结果")
    print("\n检验结果格式化结果:")
    print(json.dumps(result, ensure_ascii=False, indent=2))
