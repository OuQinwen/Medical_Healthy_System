"""
数据验证和转换模块

根据不同资料类型进行数据校验和标准化转换
"""

import re
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime


class DataValidator:
    """数据验证器基类"""
    
    @staticmethod
    def validate_name(value: str) -> Tuple[bool, str]:
        """验证姓名"""
        if not value or not value.strip():
            return False, "姓名不能为空"
        if len(value.strip()) < 2 or len(value.strip()) > 50:
            return False, "姓名长度应在2-50个字符之间"
        return True, ""
    
    @staticmethod
    def validate_gender(value: str) -> Tuple[bool, str]:
        """验证性别"""
        value = value.strip()
        if value in ["男", "女", "male", "female"]:
            return True, ""
        return False, "性别必须是'男'或'女'"
    
    @staticmethod
    def validate_age(value: str) -> Tuple[bool, str, Optional[int]]:
        """验证年龄"""
        # 提取数字
        match = re.search(r'\d+', value)
        if not match:
            return False, "年龄格式错误", None
        
        age = int(match.group())
        
        if age < 0 or age > 150:
            return False, "年龄必须在0-150之间", None
        
        return True, "", age
    
    @staticmethod
    def validate_phone(value: str) -> Tuple[bool, str]:
        """验证电话号码"""
        value = value.strip()
        # 移除所有非数字字符
        phone = re.sub(r'[^\d]', '', value)
        
        if len(phone) == 11 and phone.startswith('1'):
            return True, ""
        
        if len(phone) >= 7 and len(phone) <= 12:
            return True, ""
        
        return False, "电话号码格式错误"
    
    @staticmethod
    def validate_id_number(value: str) -> Tuple[bool, str]:
        """验证身份证号"""
        value = value.strip()
        # 简单验证：18位数字
        if len(value) == 18 and re.match(r'^\d{17}[\dXx]$', value):
            return True, ""
        return False, "身份证号格式错误（应为18位）"
    
    @staticmethod
    def validate_date(value: str) -> Tuple[bool, str, Optional[str]]:
        """验证日期格式"""
        value = value.strip()
        
        # 尝试多种日期格式
        date_formats = [
            "%Y-%m-%d",
            "%Y年%m月%d日",
            "%Y/%m/%d",
            "%Y.%m.%d"
        ]
        
        for fmt in date_formats:
            try:
                date_obj = datetime.strptime(value, fmt)
                # 统一转换为 YYYY-MM-DD 格式
                return True, "", date_obj.strftime("%Y-%m-%d")
            except ValueError:
                continue
        
        return False, "日期格式错误（应为YYYY-MM-DD或YYYY年MM月DD日）", None


class DemographicValidator(DataValidator):
    """人口学资料验证器"""
    
    REQUIRED_FIELDS = ["姓名", "性别", "年龄"]
    OPTIONAL_FIELDS = ["出生日期", "身份证号", "联系电话", "手机号", "家庭住址", "民族", "婚姻状况", "职业", "工作单位", "联系人", "联系人电话", "医保类型", "就诊卡号", "病历号", "住院号"]
    
    def validate(self, data: Dict[str, str]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """
        验证人口学数据
        
        Args:
            data: 提取的数据字典
        
        Returns:
            tuple: (是否有效, 错误列表, 标准化后的数据)
        """
        errors = []
        standardized = {}
        
        # 验证必填字段
        for field in self.REQUIRED_FIELDS:
            if field not in data or not data[field].strip():
                errors.append(f"缺少必填字段: {field}")
            else:
                # 根据字段类型进行验证
                if field == "姓名":
                    is_valid, error = self.validate_name(data[field])
                    if not is_valid:
                        errors.append(f"{field}: {error}")
                    else:
                        standardized["patient_name"] = data[field].strip()
                
                elif field == "性别":
                    is_valid, error = self.validate_gender(data[field])
                    if not is_valid:
                        errors.append(f"{field}: {error}")
                    else:
                        gender = data[field].strip()
                        # 标准化
                        if gender in ["male", "男"]:
                            standardized["gender"] = "male"
                        else:
                            standardized["gender"] = "female"
                
                elif field == "年龄":
                    is_valid, error, age = self.validate_age(data[field])
                    if not is_valid:
                        errors.append(f"{field}: {error}")
                    else:
                        standardized["age"] = age
        
        # 验证可选字段
        optional_mapping = {
            "出生日期": ("birth_date", self.validate_date),
            "身份证号": ("id_number", self.validate_id_number),
            "联系电话": ("phone", self.validate_phone),
            "手机号": ("phone", self.validate_phone),
            "家庭住址": ("address", lambda x: (True, "")),
            "民族": ("ethnicity", lambda x: (True, "")),
            "婚姻状况": ("marital_status", lambda x: (True, "")),
            "职业": ("occupation", lambda x: (True, "")),
            "工作单位": ("workplace", lambda x: (True, "")),
            "联系人": ("emergency_contact", lambda x: (True, "")),
            "联系人电话": ("emergency_phone", self.validate_phone),
            "医保类型": ("insurance_type", lambda x: (True, "")),
            "就诊卡号": ("card_number", lambda x: (True, "")),
            "病历号": ("medical_record_number", lambda x: (True, "")),
            "住院号": ("admission_number", lambda x: (True, ""))
        }
        
        for field, (std_field, validator) in optional_mapping.items():
            if field in data and data[field].strip():
                is_valid, error = validator(data[field])
                if not is_valid:
                    errors.append(f"{field}: {error}")
                else:
                    if isinstance(validator, type(DemographicValidator.validate_date)):
                        # validate_date 返回三个值
                        is_valid, error, std_value = validator(data[field])
                        if is_valid:
                            standardized[std_field] = std_value
                    else:
                        standardized[std_field] = data[field].strip()
        
        return len(errors) == 0, errors, standardized


class SurgeryHistoryValidator(DataValidator):
    """手术史验证器"""
    
    REQUIRED_FIELDS = ["手术日期", "手术名称"]
    OPTIONAL_FIELDS = ["手术持续时间", "手术开始时间", "手术结束时间", "麻醉方式", "麻醉医师", "主刀医师", "助手医师", "手术方式", "手术部位", "术前诊断", "术后诊断", "手术过程", "术中出血量", "输血情况", "手术级别", "手术切口类型", "术后并发症", "手术效果"]
    
    def validate(self, data: Dict[str, str]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """验证手术史数据"""
        errors = []
        standardized = {}
        
        # 验证必填字段
        for field in self.REQUIRED_FIELDS:
            if field not in data or not data[field].strip():
                errors.append(f"缺少必填字段: {field}")
            else:
                if field == "手术日期":
                    is_valid, error, std_date = self.validate_date(data[field])
                    if not is_valid:
                        errors.append(f"{field}: {error}")
                    else:
                        standardized["surgery_date"] = std_date
                elif field == "手术名称":
                    standardized["surgery_name"] = data[field].strip()
        
        # 验证可选字段
        optional_mapping = {
            "手术持续时间": ("duration", lambda x: (True, "")),
            "手术开始时间": ("start_time", lambda x: (True, "")),
            "手术结束时间": ("end_time", lambda x: (True, "")),
            "麻醉方式": ("anesthesia_type", lambda x: (True, "")),
            "麻醉医师": ("anesthesiologist", lambda x: (True, "")),
            "主刀医师": ("surgeon", lambda x: (True, "")),
            "助手医师": ("assistant", lambda x: (True, "")),
            "手术方式": ("surgery_method", lambda x: (True, "")),
            "手术部位": ("surgery_site", lambda x: (True, "")),
            "术前诊断": ("preoperative_diagnosis", lambda x: (True, "")),
            "术后诊断": ("postoperative_diagnosis", lambda x: (True, "")),
            "手术过程": ("surgery_process", lambda x: (True, "")),
            "术中出血量": ("blood_loss", lambda x: (True, "")),
            "输血情况": ("transfusion", lambda x: (True, "")),
            "手术级别": ("surgery_grade", lambda x: (True, "")),
            "手术切口类型": ("incision_type", lambda x: (True, "")),
            "术后并发症": ("complications", lambda x: (True, "")),
            "手术效果": ("surgery_outcome", lambda x: (True, ""))
        }
        
        for field, (std_field, validator) in optional_mapping.items():
            if field in data and data[field].strip():
                standardized[std_field] = data[field].strip()
        
        return len(errors) == 0, errors, standardized


class LabResultValidator(DataValidator):
    """检查结果验证器"""
    
    def validate(self, data: Dict[str, str]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """验证检查结果数据"""
        errors = []
        standardized = {}
        
        # 检查结果可能有多个字段，但都不是必填的
        # 只需要验证值的格式是否合理
        for key, value in data.items():
            if not value or not value.strip():
                continue
            
            # 提取数值和单位
            match = re.search(r'([-+]?\d*\.?\d+)\s*([a-zA-Zμ°%×/^]+)?', value)
            if match:
                num_value = match.group(1)
                unit = match.group(2) or ""
                
                try:
                    float(num_value)
                    standardized[key] = {
                        "value": num_value,
                        "unit": unit,
                        "original": value.strip()
                    }
                except ValueError:
                    errors.append(f"{key}: 数值格式错误")
            else:
                # 可能是定性结果（如"阳性"、"阴性"）
                standardized[key] = {
                    "value": value.strip(),
                    "unit": "",
                    "original": value.strip()
                }
        
        return len(errors) == 0, errors, standardized


class GeneralValidator(DataValidator):
    """通用验证器"""
    
    def validate(self, data: Dict[str, str]) -> Tuple[bool, List[str], Dict[str, Any]]:
        """验证通用数据"""
        # 通用验证只做基本检查，不做严格验证
        standardized = {}
        for key, value in data.items():
            if value and value.strip():
                standardized[key] = value.strip()
        
        return True, [], standardized


def get_validator(data_type: str) -> DataValidator:
    """根据资料类型获取对应的验证器"""
    validators = {
        "demographic": DemographicValidator(),
        "surgery_history": SurgeryHistoryValidator(),
        "lab_result": LabResultValidator(),
        "general": GeneralValidator()
    }
    
    return validators.get(data_type, GeneralValidator())