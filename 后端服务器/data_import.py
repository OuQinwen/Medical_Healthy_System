"""
data_import.py - 数据入库模块

功能说明：
- 将OCR提取的结构化数据导入到数据库
- 支持四种数据类型：患者基本信息、人口学信息、手术史、检查结果
- 处理字段映射和数据转换
- 支持数据更新和新增

依赖：SQLAlchemy, Pydantic
"""

from sqlalchemy import create_engine, text, Column, Integer, String, Date, DateTime, Text, Boolean, Enum, DECIMAL, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel, Field, validator
from datetime import datetime, date
from typing import Optional, List, Dict, Any
from decimal import Decimal
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 数据库配置
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:610610@localhost:3306/medical_research_system")

# 创建数据库引擎
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# ==================== 数据库模型 ====================

class Patient(Base):
    """患者基本信息表模型"""
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(String(50), unique=True, nullable=False)
    patient_name = Column(String(100), nullable=False)
    gender = Column(Enum('male', 'female', 'other'), nullable=False, default='male')
    age = Column(Integer, nullable=False)
    phone = Column(String(20), nullable=False)
    id_number = Column(String(50), nullable=False)
    preliminary_diagnosis = Column(Text)
    diagnosis_detail = Column(Text)
    status = Column(Enum('待处理', '进行中', '已完成', '已关闭'), nullable=False, default='待处理')
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    creator = Column(String(100))
    notes = Column(Text)


class DemographicData(Base):
    """人口学信息表模型"""
    __tablename__ = "demographic_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    birth_date = Column(Date)
    ethnicity = Column(String(50))
    nationality = Column(String(50))
    birth_place = Column(String(200))
    current_address = Column(String(500))
    residence_type = Column(Enum('城市', '农村', '郊区', '其他'))
    city = Column(String(100))
    province = Column(String(100))
    education_level = Column(Enum('小学', '初中', '高中', '大专', '本科', '硕士', '博士', '其他'))
    occupation = Column(String(100))
    work_unit = Column(String(200))
    marital_status = Column(Enum('未婚', '已婚', '离异', '丧偶', '其他'))
    spouse_name = Column(String(100))
    children_count = Column(Integer, default=0)
    family_size = Column(Integer, default=1)
    insurance_type = Column(Enum('城镇职工医保', '城乡居民医保', '新农合', '商业保险', '自费', '其他'))
    insurance_number = Column(String(100))
    annual_income = Column(DECIMAL(10, 2))
    economic_status = Column(Enum('贫困', '低收入', '中等收入', '高收入', '富有'))
    smoking_status = Column(Enum('从不吸烟', '已戒烟', '偶尔吸烟', '经常吸烟'))
    drinking_status = Column(Enum('从不饮酒', '偶尔饮酒', '经常饮酒', '已戒酒'))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    data_source = Column(String(200))
    extraction_time = Column(DateTime)
    notes = Column(Text)


class SurgeryHistory(Base):
    """过往手术史表模型"""
    __tablename__ = "surgery_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    surgery_name = Column(String(200), nullable=False)
    surgery_date = Column(Date)
    hospital_name = Column(String(200))
    department = Column(String(100))
    surgeon_name = Column(String(100))
    surgery_type = Column(Enum('急诊手术', '择期手术', '其他'))
    surgery_grade = Column(Enum('一级', '二级', '三级', '四级'))
    anesthesia_type = Column(String(100))
    surgery_reason = Column(Text)
    diagnosis_before_surgery = Column(Text)
    surgery_outcome = Column(Enum('治愈', '好转', '无效', '恶化', '死亡'))
    complications = Column(Text)
    admission_date = Column(Date)
    discharge_date = Column(Date)
    hospitalization_days = Column(Integer)
    surgery_cost = Column(DECIMAL(12, 2))
    total_cost = Column(DECIMAL(12, 2))
    insurance_reimbursement = Column(DECIMAL(12, 2))
    self_payment = Column(DECIMAL(12, 2))
    follow_up_status = Column(Enum('需要随访', '随访完成', '无需随访'))
    follow_up_date = Column(Date)
    follow_up_result = Column(Text)
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    data_source = Column(String(200))
    extraction_time = Column(DateTime)
    notes = Column(Text)


class LabResults(Base):
    """检查结果表模型"""
    __tablename__ = "lab_results"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    patient_id = Column(Integer, ForeignKey('patients.id', ondelete='CASCADE'), nullable=False)
    test_name = Column(String(200), nullable=False)
    test_type = Column(Enum('血液检查', '影像检查', '生化检查', '免疫检查', '病理检查', '其他'))
    test_date = Column(Date)
    hospital_name = Column(String(200))
    department = Column(String(100))
    doctor_name = Column(String(100))
    test_result = Column(Text)
    result_value = Column(String(500))
    reference_range = Column(String(500))
    unit = Column(String(50))
    result_status = Column(Enum('正常', '异常', '偏高', '偏低', '临界值'))
    is_abnormal = Column(Boolean, default=False)
    abnormal_description = Column(Text)
    imaging_type = Column(Enum('X光', 'CT', 'MRI', '超声', '其他'))
    imaging_site = Column(String(200))
    imaging_findings = Column(Text)
    imaging_conclusion = Column(Text)
    specimen_type = Column(String(100))
    collection_time = Column(DateTime)
    report_time = Column(DateTime)
    related_diagnosis = Column(Text)
    clinical_significance = Column(Text)
    treatment_suggestion = Column(Text)
    follow_up_required = Column(Boolean, default=False)
    follow_up_interval = Column(Integer)
    test_cost = Column(DECIMAL(10, 2))
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    data_source = Column(String(200))
    extraction_time = Column(DateTime)
    notes = Column(Text)


# ==================== Pydantic 模型 ====================

class PatientData(BaseModel):
    """患者基本信息数据模型"""
    patient_id: Optional[str] = None
    patient_name: str
    gender: str = 'male'
    age: int
    phone: str
    id_number: str
    preliminary_diagnosis: Optional[str] = None
    diagnosis_detail: Optional[str] = None
    status: str = '待处理'
    creator: Optional[str] = None
    notes: Optional[str] = None
    
    @validator('gender')
    def validate_gender(cls, v):
        gender_map = {
            '男': 'male',
            '女': 'female',
            '其他': 'other',
            'male': 'male',
            'female': 'female',
            'other': 'other'
        }
        return gender_map.get(v, 'male')
    
    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['待处理', '进行中', '已完成', '已关闭']
        return v if v in valid_statuses else '待处理'


class DemographicDataModel(BaseModel):
    """人口学信息数据模型"""
    birth_date: Optional[str] = None
    ethnicity: Optional[str] = None
    nationality: Optional[str] = None
    birth_place: Optional[str] = None
    current_address: Optional[str] = None
    residence_type: Optional[str] = None
    city: Optional[str] = None
    province: Optional[str] = None
    education_level: Optional[str] = None
    occupation: Optional[str] = None
    work_unit: Optional[str] = None
    marital_status: Optional[str] = None
    spouse_name: Optional[str] = None
    children_count: Optional[int] = 0
    family_size: Optional[int] = 1
    insurance_type: Optional[str] = None
    insurance_number: Optional[str] = None
    annual_income: Optional[Decimal] = None
    economic_status: Optional[str] = None
    smoking_status: Optional[str] = None
    drinking_status: Optional[str] = None
    data_source: Optional[str] = None
    extraction_time: Optional[datetime] = None
    notes: Optional[str] = None


class SurgeryDataModel(BaseModel):
    """手术史数据模型"""
    surgery_name: str
    surgery_date: Optional[str] = None
    hospital_name: Optional[str] = None
    department: Optional[str] = None
    surgeon_name: Optional[str] = None
    surgery_type: Optional[str] = None
    surgery_grade: Optional[str] = None
    anesthesia_type: Optional[str] = None
    surgery_reason: Optional[str] = None
    diagnosis_before_surgery: Optional[str] = None
    surgery_outcome: Optional[str] = None
    complications: Optional[str] = None
    admission_date: Optional[str] = None
    discharge_date: Optional[str] = None
    hospitalization_days: Optional[int] = None
    surgery_cost: Optional[Decimal] = None
    total_cost: Optional[Decimal] = None
    insurance_reimbursement: Optional[Decimal] = None
    self_payment: Optional[Decimal] = None
    follow_up_status: Optional[str] = None
    follow_up_date: Optional[str] = None
    follow_up_result: Optional[str] = None
    data_source: Optional[str] = None
    extraction_time: Optional[datetime] = None
    notes: Optional[str] = None


class LabResultDataModel(BaseModel):
    """检查结果数据模型"""
    test_name: str
    test_type: Optional[str] = None
    test_date: Optional[str] = None
    hospital_name: Optional[str] = None
    department: Optional[str] = None
    doctor_name: Optional[str] = None
    test_result: Optional[str] = None
    result_value: Optional[str] = None
    reference_range: Optional[str] = None
    unit: Optional[str] = None
    result_status: Optional[str] = None
    is_abnormal: Optional[bool] = False
    abnormal_description: Optional[str] = None
    imaging_type: Optional[str] = None
    imaging_site: Optional[str] = None
    imaging_findings: Optional[str] = None
    imaging_conclusion: Optional[str] = None
    specimen_type: Optional[str] = None
    collection_time: Optional[datetime] = None
    report_time: Optional[datetime] = None
    related_diagnosis: Optional[str] = None
    clinical_significance: Optional[str] = None
    treatment_suggestion: Optional[str] = None
    follow_up_required: Optional[bool] = False
    follow_up_interval: Optional[int] = None
    test_cost: Optional[Decimal] = None
    data_source: Optional[str] = None
    extraction_time: Optional[datetime] = None
    notes: Optional[str] = None


# ==================== 数据入库服务 ====================

class DataImportService:
    """数据入库服务类"""
    
    def __init__(self):
        self.db = SessionLocal()
    
    def __del__(self):
        if hasattr(self, 'db'):
            self.db.close()
    
    def get_or_create_patient(self, patient_data, creator: str) -> Patient:
        """
        获取或创建患者记录
        
        Args:
            patient_data: 患者数据（可以是PatientData对象或字典）
            creator: 创建者用户名
        
        Returns:
            Patient对象
        """
        # 如果是字典，转换为PatientData对象
        if isinstance(patient_data, dict):
            patient_data = PatientData(**patient_data)
        
        # 根据身份证号查找患者
        patient = self.db.query(Patient).filter(
            Patient.id_number == patient_data.id_number
        ).first()
        
        if patient:
            # 更新患者信息
            for field, value in patient_data.dict(exclude_unset=True).items():
                if field != 'id' and hasattr(patient, field):
                    setattr(patient, field, value)
            patient.update_time = datetime.now()
            self.db.commit()
            self.db.refresh(patient)
            print(f"[INFO] 更新患者信息: {patient.patient_name}")
        else:
            # 创建新患者
            patient_dict = patient_data.dict(exclude_unset=True)
            patient_dict['creator'] = creator
            patient_dict['patient_id'] = patient_data.id_number or f"PAT{datetime.now().strftime('%Y%m%d%H%M%S')}"
            patient = Patient(**patient_dict)
            self.db.add(patient)
            self.db.commit()
            self.db.refresh(patient)
            print(f"[INFO] 创建新患者: {patient.patient_name}")
        
        return patient
    
    def import_demographic_data(self, patient_id: int, demographic_data: Dict[str, Any], 
                                data_source: str = None) -> DemographicData:
        """
        导入人口学信息
        
        Args:
            patient_id: 患者ID
            demographic_data: 人口学数据字典
            data_source: 数据来源文件名
        
        Returns:
            DemographicData对象
        """
        # 检查是否已存在该患者的人口学信息
        existing = self.db.query(DemographicData).filter(
            DemographicData.patient_id == patient_id
        ).first()
        
        # 准备数据
        data_dict = demographic_data.copy()
        data_dict['patient_id'] = patient_id
        data_dict['data_source'] = data_source
        data_dict['extraction_time'] = datetime.now()
        
        # 检查是否有有效数据
        has_data = any([
            data_dict.get('birth_date'),
            data_dict.get('ethnicity'),
            data_dict.get('nationality'),
            data_dict.get('current_address'),
            data_dict.get('education_level'),
            data_dict.get('occupation')
        ])
        
        if not has_data:
            print(f"[WARNING] 人口学数据为空，跳过导入: {data_source}")
            return None
        
        if existing:
            # 更新现有记录
            for field, value in data_dict.items():
                if value is not None and hasattr(existing, field):
                    setattr(existing, field, value)
            existing.update_time = datetime.now()
            self.db.commit()
            self.db.refresh(existing)
            print(f"[INFO] 更新人口学信息: patient_id={patient_id}")
            return existing
        else:
            # 创建新记录
            demographic = DemographicData(**data_dict)
            self.db.add(demographic)
            self.db.commit()
            self.db.refresh(demographic)
            print(f"[INFO] 创建人口学信息: patient_id={patient_id}")
            return demographic
    
    def import_surgery_history(self, patient_id: int, surgery_data: Dict[str, Any], 
                              data_source: str = None) -> SurgeryHistory:
        """
        导入手术史
        
        Args:
            patient_id: 患者ID
            surgery_data: 手术史数据字典
            data_source: 数据来源文件名
        
        Returns:
            SurgeryHistory对象
        """
        # 准备数据
        data_dict = surgery_data.copy()
        data_dict['patient_id'] = patient_id
        data_dict['data_source'] = data_source
        data_dict['extraction_time'] = datetime.now()
        
        # 设置surgery_name的默认值
        if not data_dict.get('surgery_name'):
            data_dict['surgery_name'] = '未命名手术'
            print(f"[WARNING] surgery_name为空，使用默认值: {data_source}")
        
        # 检查是否有有效数据
        has_data = any([
            data_dict.get('surgery_date'),
            data_dict.get('diagnosis_before_surgery'),
            data_dict.get('surgery_outcome')
        ])
        
        if not has_data:
            print(f"[WARNING] 手术史数据为空，跳过导入: {data_source}")
            return None
        
        # 创建新的手术记录
        surgery = SurgeryHistory(**data_dict)
        self.db.add(surgery)
        self.db.commit()
        self.db.refresh(surgery)
        print(f"[INFO] 创建手术史记录: patient_id={patient_id}, surgery_name={surgery_data.get('surgery_name', '未命名手术')}")
        return surgery
    
    def import_lab_results(self, patient_id: int, lab_data: Dict[str, Any], 
                           data_source: str = None) -> LabResults:
        """
        导入检查结果
        
        Args:
            patient_id: 患者ID
            lab_data: 检查结果数据字典
            data_source: 数据来源文件名
        
        Returns:
            LabResults对象
        """
        # 准备数据
        data_dict = lab_data.copy()
        data_dict['patient_id'] = patient_id
        data_dict['data_source'] = data_source
        data_dict['extraction_time'] = datetime.now()
        
        # 设置test_name的默认值，避免NOT NULL约束错误
        if not data_dict.get('test_name'):
            data_dict['test_name'] = '未命名检查'
            print(f"[WARNING] test_name为空，使用默认值: {data_source}")
        
        # 检查是否有有效数据
        has_data = any([
            data_dict.get('test_result'),
            data_dict.get('result_value'),
            data_dict.get('imaging_findings'),
            data_dict.get('imaging_conclusion')
        ])
        
        if not has_data:
            print(f"[WARNING] 检查结果数据为空，跳过导入: {data_source}")
            return None
        
        # 创建新的检查结果记录
        lab_result = LabResults(**data_dict)
        self.db.add(lab_result)
        self.db.commit()
        self.db.refresh(lab_result)
        print(f"[INFO] 创建检查结果记录: patient_id={patient_id}, test_name={lab_data.get('test_name', '未命名检查')}")
        return lab_result
    
    def import_data_by_type(self, patient_id: int, data_type: str, 
                            extracted_data: Dict[str, Any], data_source: str = None):
        """
        根据数据类型导入数据
        
        Args:
            patient_id: 患者ID
            data_type: 数据类型（患者基本信息、人口学信息、手术史、检查结果、其他）
            extracted_data: 提取的数据
            data_source: 数据来源文件名
        
        Returns:
            导入的结果对象
        """
        try:
            if data_type in ['人口学信息', '人口学']:
                return self.import_demographic_data(patient_id, extracted_data, data_source)
            elif data_type in ['过往手术史', '手术史']:
                return self.import_surgery_history(patient_id, extracted_data, data_source)
            elif data_type in ['检查结果', '化验结果', '实验室检查']:
                return self.import_lab_results(patient_id, extracted_data, data_source)
            else:
                print(f"[WARNING] 未知的数据类型: {data_type}")
                return None
        except Exception as e:
            print(f"[ERROR] 导入数据失败: {str(e)}")
            self.db.rollback()
            raise


# ==================== 便捷函数 ====================

def import_extracted_data(patient_name: str, patient_data: PatientData, 
                          data_type: str, extracted_data: Dict[str, Any], 
                          data_source: str = None, creator: str = 'system'):
    """
    导入提取的数据（便捷函数）
    
    Args:
        patient_name: 患者姓名
        patient_data: 患者基本信息
        data_type: 数据类型
        extracted_data: 提取的数据
        data_source: 数据来源文件名
        creator: 创建者
    
    Returns:
        导入结果字典
    """
    service = DataImportService()
    
    try:
        # 获取或创建患者
        patient = service.get_or_create_patient(patient_data, creator)
        
        # 导入对应类型的数据
        result = service.import_data_by_type(
            patient.id, data_type, extracted_data, data_source
        )
        
        return {
            'success': True,
            'patient_id': patient.id,
            'patient_name': patient.patient_name,
            'data_type': data_type,
            'result_id': result.id if result else None,
            'message': f"成功导入{data_type}"
        }
    except Exception as e:
        return {
            'success': False,
            'error': str(e),
            'message': f"导入失败: {str(e)}"
        }


if __name__ == "__main__":
    # 测试代码
    print("=== 数据入库模块测试 ===")
    
    # 测试患者基本信息导入
    patient_data = PatientData(
        patient_name="测试患者",
        gender="男",
        age=35,
        phone="13800138000",
        id_number="110101199001011234",
        preliminary_diagnosis="高血压",
        creator="test_user"
    )
    
    result = import_extracted_data(
        patient_name="测试患者",
        patient_data=patient_data,
        data_type="人口学信息",
        extracted_data={
            "birth_date": "1990-01-01",
            "education_level": "本科",
            "occupation": "工程师",
            "marital_status": "已婚"
        },
        data_source="test_ocr.jpg",
        creator="test_user"
    )
    
    print(f"导入结果: {result}")