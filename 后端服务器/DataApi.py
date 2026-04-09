"""
DataApi.py - 数据处理 API 模块

功能说明：
- 接收前端 DataView.vue 组件上传的文件
- 接收文本消息输入
- 支持多种文件格式（图片、文本、表格文件）
- 调用 agent 服务器进行 OCR 和数据提取
- 根据资料类型进行数据校验和标准化
- 将提取的结构化数据导入到数据库

依赖：FastAPI, python-multipart, requests
"""
from user_auth import get_current_active_user, User
from data_import import DataImportService, PatientData, Patient, DemographicData, SurgeryHistory, LabResults
from sqlalchemy import create_engine, text
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import os
import requests
from datetime import datetime
import json
import re
from data_validator import get_validator

# 辅助函数：判断是否为影像报告
def _is_imaging_report(full_data_json: dict) -> bool:
    """
    判断OCR结果是否为影像检查报告
    
    Args:
        full_data_json: 完整的OCR数据
        
    Returns:
        bool: 是否为影像报告
    """
    if not full_data_json:
        return False
    
    # 处理两种可能的数据结构
    data_content = None
    if 'full_data_json' in full_data_json:
        data_content = full_data_json['full_data_json']
    else:
        data_content = full_data_json
    
    if not data_content:
        return False
    
    # 获取原始文本
    raw_text = data_content.get('raw_text', '')
    
    # 影像报告的特征（强特征）
    strong_imaging_keywords = [
        '诊断所见', '诊断印象', 'CDFI', '无回声区', '回声', '包块', '占位', 
        '增厚', '肿大', '结节', '钙化', '积液', '造影', '钡灌肠'
    ]
    
    # 影像类型关键词（中等特征）
    imaging_type_keywords = [
        '超声', 'US', 'CT', 'MRI', 'X光', 'X线', '影像', '彩超', 'B超',
        '核医学', 'PET-CT', 'SPECT'
    ]
    
    # 器官/部位关键词（弱特征）
    organ_keywords = [
        '肝脏', '胆囊', '胰腺', '脾脏', '肾脏', '膀胱', '前列腺', '甲状腺',
        '乳腺', '心脏', '肺部', '腹部', '胸部', '头颅', '颈部', '四肢'
    ]
    
    # 实验室检验的特征
    lab_keywords = [
        '项目名称', '检验结果', '参考范围', '单位', 'Test', 'Result', 'Normal',
        '检验项目', '化验单', '血常规', '肝功能', '肾功能', '血脂'
    ]
    
    # 统计关键词出现次数
    strong_count = sum(1 for keyword in strong_imaging_keywords if keyword in raw_text)
    type_count = sum(1 for keyword in imaging_type_keywords if keyword in raw_text)
    organ_count = sum(1 for keyword in organ_keywords if keyword in raw_text)
    lab_count = sum(1 for keyword in lab_keywords if keyword in raw_text)
    
    # 检查items中的数据
    items = data_content.get('items', [])
    has_numerical_results = False
    has_long_text_results = False
    has_diagnostic_items = False
    
    for item in items:
        result = item.get('结果', '')
        project_name = item.get('项目名称', '')
        original_data = item.get('原始数据', '')
        
        # 检查是否有诊断相关字段
        if '诊断' in project_name or '诊断' in original_data:
            has_diagnostic_items = True
        
        # 检查是否有数值结果
        if any(char.isdigit() for char in result):
            has_numerical_results = True
        
        # 检查是否有长文本结果（超过30个字符且包含汉字）
        if len(result) > 30 and any('\u4e00' <= char <= '\u9fff' for char in result):
            has_long_text_results = True
    
    # 计算综合得分
    imaging_score = (
        strong_count * 3 +      # 强特征权重高
        type_count * 2 +        # 影像类型权重中等
        organ_count * 1 +       # 器官关键词权重低
        (2 if has_diagnostic_items else 0) +  # 有诊断字段加分
        (2 if has_long_text_results else 0)  # 有长文本加分
    )
    
    lab_score = (
        lab_count * 2 +         # 实验室关键词权重
        (1 if has_numerical_results else 0)  # 有数值结果加分
    )
    
    # 调试信息
    print(f"[AUTO分流] 影像报告判断:")
    print(f"  强特征关键词: {strong_count} 个")
    print(f"  影像类型关键词: {type_count} 个")
    print(f"  器官关键词: {organ_count} 个")
    print(f"  实验室关键词: {lab_count} 个")
    print(f"  有诊断字段: {has_diagnostic_items}")
    print(f"  有长文本结果: {has_long_text_results}")
    print(f"  有数值结果: {has_numerical_results}")
    print(f"  影像得分: {imaging_score}")
    print(f"  实验室得分: {lab_score}")
    
    # 判断逻辑（优先级从高到低）
    # 1. 有"诊断所见"或"诊断印象" → 影像报告
    if '诊断所见' in raw_text or '诊断印象' in raw_text:
        print(f"  结果: 影像报告（有诊断所见/诊断印象）")
        return True
    
    # 2. 有"检查类别名称"且值为US/CT/MRI等 → 影像报告
    match = re.search(r'检查类别名称[：:]\s*(US|CT|MRI|X线|X光|超声)', raw_text)
    if match:
        print(f"  结果: 影像报告（检查类别为{match.group(1)}）")
        return True
    
    # 3. 影像得分明显高于实验室得分 → 影像报告
    if imaging_score >= 3 and imaging_score > lab_score:
        print(f"  结果: 影像报告（影像得分{imaging_score} > 实验室得分{lab_score}）")
        return True
    
    # 4. 有诊断字段且有长文本结果 → 影像报告
    if has_diagnostic_items and has_long_text_results:
        print(f"  结果: 影像报告（有诊断字段和长文本）")
        return True
    
    # 5. 实验室得分明显高于影像得分 → 实验室检验
    if lab_score >= 3 and lab_score > imaging_score:
        print(f"  结果: 实验室检验（实验室得分{lab_score} > 影像得分{imaging_score}）")
        return False
    
    # 6. 默认情况：有影像类型关键词 → 影像报告
    if type_count >= 1:
        print(f"  结果: 影像报告（有影像类型关键词）")
        return True
    
    print(f"  结果: 实验室检验（默认）")
    return False

# 创建路由
router = APIRouter(prefix="/api", tags=["data"])

# 获取当前脚本所在目录
script_dir = os.path.dirname(os.path.abspath(__file__))

# 上传文件保存目录（使用当前脚本所在目录）
UPLOAD_DIR = os.path.join(script_dir, "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 患者数据保存目录（使用当前脚本所在目录）
DATA_DIR = os.path.join(script_dir, "data")
os.makedirs(DATA_DIR, exist_ok=True)

# 数据库引擎
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:610610@localhost:3306/medical_research_system")
engine = create_engine(DATABASE_URL)

# 基本信息表和人口学表的字段冲突映射
# 这些字段在两个表中都存在，需要特殊处理
CONFLICT_FIELDS_MAPPING = {
    'name': 'patient_name',           # 患者姓名
    'gender': 'gender',               # 性别
    'age': 'age',                     # 年龄
    'phone': 'phone',                 # 电话
    'id_number': 'id_number',         # 证件号
    'birth_date': 'birth_date',       # 出生日期（与年龄相关）
    'address': 'address',             # 地址信息
}

# 基本信息表的字段（创建患者时必填）
PATIENT_BASIC_FIELDS = [
    'patientName', 'patientId', 'gender', 'age', 'phone', 'idNumber'
]

# 人口学表的字段（详细补充信息）
DEMOGRAPHIC_FIELDS = [
    'birth_date', 'ethnicity', 'nationality', 'birth_place',
    'current_address', 'residence_type', 'city', 'province',
    'education_level', 'occupation', 'work_unit',
    'marital_status', 'spouse_name', 'children_count', 'family_size',
    'insurance_type', 'insurance_number', 'annual_income', 'economic_status',
    'smoking_status', 'drinking_status'
]


def _handle_field_conflicts(extracted_data: Dict, patient_info: Dict) -> Dict:
    """
    处理基本信息表和人口学表之间的字段冲突
    
    Args:
        extracted_data: OCR提取的数据
        patient_info: 患者基本信息
    
    Returns:
        Dict: 处理后的数据，移除冲突字段
    """
    # 冲突字段：这些字段在基本信息表中已经存在，不应该在人口学表中重复
    conflict_fields = ['name', '姓名', 'patientName', 'gender', '性别', 'age', '年龄', 
                      'phone', '电话', 'phoneNumber', 'id_number', '身份证号', '证件号']
    
    # 移除冲突字段
    cleaned_data = {}
    for key, value in extracted_data.items():
        # 检查是否是冲突字段
        is_conflict = False
        for conflict_field in conflict_fields:
            if conflict_field.lower() in key.lower() or key.lower() in conflict_field.lower():
                is_conflict = True
                print(f"[INFO] 检测到冲突字段: {key} = {value}, 该字段已存在于基本信息表，跳过")
                break
        
        if not is_conflict:
            cleaned_data[key] = value
    
    return cleaned_data


def _update_patient_info_if_needed(extracted_data: Dict, patient_name: str):
    """
    更新患者基本信息到数据库
    
    参数：
    - extracted_data: OCR提取的数据
    - patient_name: 患者姓名
    """
    try:
        # 需要更新的字段映射
        field_mapping = {
            'age': 'age',
            'phone': 'phone',
            'preliminary_diagnosis': 'preliminary_diagnosis',
            'notes': 'notes'
        }
        
        # 构建更新语句
        update_fields = []
        update_values = {"patient_name": patient_name}
        
        for extract_field, db_field in field_mapping.items():
            if extract_field in extracted_data and extracted_data[extract_field]:
                update_fields.append(f"{db_field} = :{db_field}")
                update_values[db_field] = extracted_data[extract_field]
        
        if update_fields:
            with engine.connect() as connection:
                update_query = text(f"""
                    UPDATE patients 
                    SET {', '.join(update_fields)}, update_time = NOW()
                    WHERE patient_name = :patient_name
                """)
                connection.execute(update_query, update_values)
                connection.commit()
                print(f"[INFO] 已更新患者基本信息: {patient_name}")
        
    except Exception as e:
        print(f"[ERROR] 更新患者信息失败: {str(e)}")


def _map_component_to_data_type(component_name: str) -> str:
    """
    将前端组件名称映射到agent的data_type
    
    Args:
        component_name: 前端传来的组件名称（如：人口学信息、过往手术史、检查结果、其他）
    
    Returns:
        str: 对应的data_type
    """
    mapping = {
        "人口学信息": "demographic",
        "人口学": "demographic",
        "过往手术史": "surgery_history",
        "手术史": "surgery_history",
        "检查结果": "lab_result",
        "影像检查": "imaging",
        "影像": "imaging",
        "其他": "general"
    }
    
    # 如果完全匹配
    if component_name in mapping:
        return mapping[component_name]
    
    # 优先检查是否包含"影像"
    if "影像" in component_name:
        return "imaging"
    
    # 模糊匹配
    for key, value in mapping.items():
        if key in component_name or component_name in key:
            return value
    
    # 默认返回通用类型
    return "general"


async def _call_agent_with_file(file_path: str, filename: str, data_type: str, user_vision_model: str = "", user_llm_model: str = "") -> Dict:
    """
    调用agent服务处理单个文件
    
    Args:
        file_path: 文件路径
        filename: 文件名
        data_type: 资料类型
        user_vision_model: 用户指定的视觉模型
        user_llm_model: 用户指定的语言模型
    
    Returns:
        Dict: agent处理结果
    """
    try:
        # 优先使用用户指定的模型，如果没有则读取配置文件
        vision_model = user_vision_model if user_vision_model else None
        llm_model = user_llm_model if user_llm_model else None
        model_type = "cloud"
        
        # 如果用户没有指定模型，从配置文件读取
        if not vision_model or not llm_model:
            try:
                agent_dir = Path(__file__).parent.parent / "数据agent"
                env_file = agent_dir / ".env"
                if env_file.exists():
                    with open(env_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            line = line.strip()
                            if line and not line.startswith('#') and '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                value = value.strip()
                                if key == 'VISION_MODEL' and not vision_model:
                                    vision_model = value
                                elif key == 'LLM_MODEL' and not llm_model:
                                    llm_model = value
                print(f"[DEBUG] 使用云端模型 - 视觉: {vision_model}, 语言: {llm_model}")
            except Exception as e:
                print(f"[WARNING] 读取模型配置失败: {str(e)}")
        
        # 读取文件内容
        with open(file_path, 'rb') as f:
            file_content = f.read()
        
        # 构建请求数据
        files_data = [("files", (filename, file_content, "image/jpeg"))]
        
        data = {
            "generate_excel": "true",
            "model_type": model_type,
            "data_type": data_type
        }
        
        if vision_model:
            data["vision_model"] = vision_model
        if llm_model:
            data["llm_model"] = llm_model
        
        # 调用agent服务器的批量处理接口
        print(f"[INFO] 调用agent处理文件: {filename}, data_type: {data_type}")
        response = requests.post(
            f"{AGENT_BASE_URL}/api/batch-process",
            files=files_data,
            data=data,
            timeout=300  # 5分钟超时
        )
        
        response.raise_for_status()
        result = response.json()
        
        # 提取第一个文件的结果
        if result.get("success") and result.get("results"):
            first_result = result["results"][0]
            if first_result.get("success"):
                return {
                    "success": True,
                    "extracted_data": first_result.get("extracted_data", {}),
                    "full_data_json": first_result.get("full_data_json", {})
                }
            else:
                return {
                    "success": False,
                    "error": first_result.get("error", "未知错误")
                }
        else:
            return {
                "success": False,
                "error": result.get("message", "agent处理失败")
            }
            
    except requests.exceptions.Timeout:
        return {
            "success": False,
            "error": "图片识别服务响应超时"
        }
    except requests.exceptions.ConnectionError:
        return {
            "success": False,
            "error": "无法连接到图片识别服务"
        }
    except Exception as e:
        return {
            "success": False,
            "error": f"调用agent失败: {str(e)}"
        }


# 请求模型
class PatientDataRequest(BaseModel):
    """患者数据模型（API请求）"""
    patientName: str
    patientId: str
    gender: str
    age: str
    phone: str
    idNumber: str = ""
    preliminaryDiagnosis: str = ""
    createTime: str
    creator: str
    notes: str = ""
    status: str = "待处理"

# Agent 服务器配置
AGENT_BASE_URL = "http://localhost:8001"


async def call_agent_process(file_paths: List[str], filenames: List[str], content_types: List[str], fields: Optional[str] = None, model_type: str = "cloud", vision_model: Optional[str] = None, llm_model: Optional[str] = None):
    """
    调用 agent 服务器处理图片
    
    Args:
        file_paths: 图片文件路径列表
        filenames: 原始文件名列表
        content_types: 文件内容类型列表
        fields: 可选的提取字段（逗号分隔）
        model_type: 模型类型（cloud/local），默认为 cloud
        vision_model: 视觉模型名称（可选）
        llm_model: 语言模型名称（可选）
    
    Returns:
        agent 服务器的处理结果
    """
    try:
        # 准备表单数据 - 从文件路径读取
        files_data = []
        for file_path, filename, content_type in zip(file_paths, filenames, content_types):
            with open(file_path, 'rb') as f:
                files_data.append(("files", (filename, f.read(), content_type)))
        
        data = {}
        if fields:
            data["fields"] = fields
        data["generate_excel"] = "true"
        data["model_type"] = model_type  # 传递模型类型到 agent
        
        # 如果提供了具体的模型名称，也传递过去
        if vision_model:
            data["vision_model"] = vision_model
        if llm_model:
            data["llm_model"] = llm_model
        
        # 调用 agent 服务器的批量处理接口
        response = requests.post(
            f"{AGENT_BASE_URL}/api/batch-process",
            files=files_data,
            data=data,
            timeout=300  # 5分钟超时，因为OCR处理较慢
        )
        
        response.raise_for_status()
        return response.json()
        
    except requests.exceptions.RequestException as e:
        # 将技术错误转换为用户友好的自然语言
        error_str = str(e)
        
        # 连接超时
        if "timeout" in error_str.lower() or "timed out" in error_str.lower():
            return {
                "success": False,
                "error": "图片识别服务响应超时，可能是网络连接不稳定或服务器负载较高，请稍后重试"
            }
        
        # 连接被拒绝
        elif "connection refused" in error_str.lower():
            return {
                "success": False,
                "error": "图片识别服务暂时无法连接，请联系管理员检查服务是否正常运行"
            }
        
        # 无法连接
        elif "connection error" in error_str.lower():
            return {
                "success": False,
                "error": "无法连接到图片识别服务，请检查网络连接是否正常"
            }
        
        # HTTP 错误
        elif hasattr(e, 'response') and e.response is not None:
            status_code = e.response.status_code
            if status_code == 404:
                return {
                    "success": False,
                    "error": "图片识别服务暂时不可用，请联系管理员"
                }
            elif status_code == 500:
                return {
                    "success": False,
                    "error": "图片识别服务内部出现错误，请联系管理员"
                }
            else:
                return {
                    "success": False,
                    "error": f"图片识别服务返回错误，状态码: {status_code}"
                }
        
        # 其他错误
        else:
            return {
                "success": False,
                "error": "图片识别服务处理失败，请稍后重试或联系管理员"
            }


@router.post("/upload")
async def upload_data(
    files: Optional[List[UploadFile]] = File(None),
    message: str = Form(""),
    model_type: str = Form("cloud"),  # 添加模型类型参数，默认为 cloud
    current_user: User = Depends(get_current_active_user)  # 添加这行
):
    """
    接收前端上传的文件和文本消息
    
    如果上传的是图片文件，会自动调用 agent 服务器进行 OCR 和数据提取
    
    参数：
    - files: 可选的文件列表（支持多个文件）
    - message: 文本消息内容
    - model_type: 模型类型（cloud/local），默认为 cloud
    
    返回：
    - JSON 格式的响应，包含处理结果
    """
    try:
        result = {
            "success": True,
            "message": message,
            "uploaded_files": [],
            "agent_results": None,
            "timestamp": datetime.now().isoformat()
        }

        # 处理上传的文件
        image_file_paths = []
        image_filenames = []
        image_content_types = []
        
        if files:
            for file in files:
                # 创建唯一的文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, filename)

                # 保存文件
                with open(file_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)

                # 记录文件信息
                file_info = {
                    "filename": file.filename,
                    "content_type": file.content_type,
                    "size": len(content),
                    "saved_path": file_path,
                    "is_image": file.content_type in ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"]
                }
                result["uploaded_files"].append(file_info)
                
                # 如果是图片文件，记录路径和文件信息
                if file_info["is_image"]:
                    image_file_paths.append(file_path)
                    image_filenames.append(file.filename)
                    image_content_types.append(file.content_type)

        # 如果有图片文件，调用 agent 服务器处理
        if image_file_paths:
            print(f"检测到 {len(image_file_paths)} 个图片文件，正在调用 agent 服务器进行 OCR 处理...")
            print(f"使用的模型类型: {model_type}")
            
            # 读取用户配置的模型名称（如果使用云端模型）
            vision_model = None
            llm_model = None
            if model_type == "cloud":
                try:
                    agent_dir = Path(__file__).parent.parent / "数据agent"
                    env_file = agent_dir / ".env"
                    if env_file.exists():
                        with open(env_file, 'r', encoding='utf-8') as f:
                            for line in f:
                                line = line.strip()
                                if line and not line.startswith('#') and '=' in line:
                                    key, value = line.split('=', 1)
                                    key = key.strip()
                                    value = value.strip()
                                    if key == 'VISION_MODEL':
                                        vision_model = value
                                    elif key == 'LLM_MODEL':
                                        llm_model = value
                    print(f"使用云端模型 - 视觉: {vision_model}, 语言: {llm_model}")
                except Exception as e:
                    print(f"读取模型配置失败: {str(e)}")
            
            # 如果用户输入了消息，将其作为提取字段
            extract_fields = None
            if message and message.strip():
                # 将用户输入的消息分割为字段列表（支持逗号、顿号、空格分隔）
                import re
                # 使用正则表达式分割常见的分隔符
                fields_list = re.split(r'[,，、\s]+', message.strip())
                # 过滤空字符串
                extract_fields = [f for f in fields_list if f.strip()]
                if extract_fields:
                    print(f"用户指定的提取字段: {extract_fields}")
            
            # 调用 agent 处理，传递模型类型和具体模型名称
            agent_result = await call_agent_process(image_file_paths, image_filenames, image_content_types, extract_fields, model_type, vision_model, llm_model)
            result["agent_results"] = agent_result
            
            # 如果 agent 处理失败，记录错误信息
            if not agent_result.get("success"):
                error_msg = agent_result.get("error", "未知错误")
                print(f"警告: agent 处理失败 - {error_msg}")
                # 使用用户友好的提示信息
                result["agent_warning"] = "抱歉，图片识别功能暂时无法使用，文件已成功保存，您可以稍后重试或手动输入数据"
                # 将错误信息也添加到 message 字段，方便前端显示
                if not message:
                    result["message"] = "文件已保存，但图片识别暂时失败，请稍后重试"
                else:
                    result["message"] = f"{message}（注意：图片识别暂时失败，文件已保存）"

        # 如果有文件或消息，返回处理结果
        if result["uploaded_files"] or message:
            return JSONResponse(content=result)
        else:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "未提供任何数据（文件或消息）"
                },
                status_code=400
            )
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"处理失败: {str(e)}"
            },
            status_code=500
        )


@router.post("/upload-with-fields")
async def upload_with_fields(
    files: List[UploadFile] = File(...),
    message: str = Form(""),
    fields: str = Form(""),
    current_user: User = Depends(get_current_active_user)  # 添加这行
):
    """
    上传文件并指定需要提取的字段（适用于图片OCR）
    
    参数：
    - files: 文件列表（必填）
    - message: 文本消息内容
    - fields: 需要提取的字段，多个字段用逗号分隔（例如：姓名,性别,年龄）
    
    返回：
    - JSON 格式的响应，包含处理结果
    """
    try:
        result = {
            "success": True,
            "message": message,
            "uploaded_files": [],
            "agent_results": None,
            "timestamp": datetime.now().isoformat()
        }

        # 处理上传的文件
        image_files = []
        for file in files:
            # 创建唯一的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(UPLOAD_DIR, filename)

            # 保存文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)

            # 记录文件信息
            file_info = {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content),
                "saved_path": file_path,
                "is_image": file.content_type in ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"]
            }
            result["uploaded_files"].append(file_info)
            
            # 如果是图片文件，加入待处理列表
            if file_info["is_image"]:
                image_files.append(file)

        # 如果有图片文件，调用 agent 服务器处理
        if image_files:
            print(f"检测到 {len(image_files)} 个图片文件，正在调用 agent 服务器进行 OCR 处理...")
            print(f"指定提取字段: {fields if fields else '全量提取'}")
            agent_result = await call_agent_process(image_files, fields if fields else None)
            result["agent_results"] = agent_result

        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"处理失败: {str(e)}"
            },
            status_code=500
        )


@router.post("/message")
async def receive_message(message: str = Form(...)):
    """
    单独接收文本消息（不包含文件）
    
    参数：
    - message: 文本消息内容（必填）
    
    返回：
    - JSON 格式的响应，确认消息已接收
    """
    try:
        return JSONResponse(content={
            "success": True,
            "message": message,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"接收消息失败: {str(e)}"
            },
            status_code=500
        )


@router.get("/agent-output-files")
async def get_agent_output_files(current_user: User = Depends(get_current_active_user)): # 添加这行
    """
    获取 agent 服务器生成的所有输出文件
    
    返回：
    - agent 服务器的输出文件列表
    """
    try:
        response = requests.get(f"{AGENT_BASE_URL}/api/output-files", timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"获取 agent 输出文件失败: {str(e)}"
            },
            status_code=500
        )


@router.get("/health")
async def health_check():
    """
    健康检查接口
    """
    # 检查 agent 服务器状态
    agent_status = "unknown"
    try:
        response = requests.get(f"{AGENT_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            agent_status = "healthy"
        else:
            agent_status = "unhealthy"
    except:
        agent_status = "unreachable"
    
    return {
        "status": "healthy",
        "service": "Data API",
        "agent_status": agent_status,
        "timestamp": datetime.now().isoformat()
    }


@router.post("/patient")
async def create_patient(
    patient_data: PatientDataRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    创建患者记录并保存患者数据（同时保存到数据库和文件系统）
    
    参数：
    - patient_data: 患者数据对象
    
    返回：
    - 创建结果
    """
    try:
        print(f"[DEBUG] create_patient 被调用")
        print(f"[DEBUG] 当前用户: {current_user.username}")
        print(f"[DEBUG] 患者数据: {patient_data}")
        
        # 1. 保存到数据库
        service = DataImportService()
        
        # 准备患者基本信息（使用正确的字段名和数据类型）
        # 注意：这里导入的是 data_import.py 中的 PatientData，使用蛇形命名
        patient_basic_info = {
            "patient_id": patient_data.patientId or patient_data.idNumber,
            "patient_name": patient_data.patientName,
            "gender": patient_data.gender,
            "age": int(patient_data.age) if patient_data.age else 0,
            "phone": patient_data.phone,
            "id_number": patient_data.idNumber,
            "preliminary_diagnosis": patient_data.preliminaryDiagnosis,
            "status": patient_data.status or '待处理',
            "creator": current_user.username,
            "notes": patient_data.notes
        }
        
        # 创建或更新患者记录到数据库
        # 直接使用字典参数，而不是先转换为 PatientData 对象
        patient_obj = service.get_or_create_patient(
            patient_basic_info,
            current_user.username
        )
        
        print(f"[DEBUG] 数据库保存成功: 患者ID={patient_obj.id}")
        
        # 2. 同时保存到文件系统（作为备份）
        user_dir = os.path.join(DATA_DIR, current_user.username)
        print(f"[DEBUG] 创建用户目录: {user_dir}")
        os.makedirs(user_dir, exist_ok=True)
        
        patient_dir = os.path.join(user_dir, patient_data.patientName)
        print(f"[DEBUG] 创建患者目录: {patient_dir}")
        os.makedirs(patient_dir, exist_ok=True)
        
        # 保存患者数据到 JSON 文件
        patient_file = os.path.join(patient_dir, "patient_info.json")
        print(f"[DEBUG] 保存患者信息文件: {patient_file}")
        with open(patient_file, 'w', encoding='utf-8') as f:
            json.dump(patient_data.dict(), f, ensure_ascii=False, indent=2)
        
        print(f"[DEBUG] 患者记录创建成功")
        
        return JSONResponse(content={
            "success": True,
            "message": "患者记录创建成功",
            "patient_id": patient_obj.id,
            "patient_path": patient_dir,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        print(f"[ERROR] 创建患者记录失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"创建患者记录失败: {str(e)}"
            },
            status_code=500
        )


@router.post("/patient/{patient_name}/upload")
async def upload_patient_file(
    patient_name: str,
    component_name: str = Form(...),
    files: List[UploadFile] = File(...),
    enable_ocr: bool = Form(True),
    current_user: User = Depends(get_current_active_user)
):
    """
    上传患者资料文件
    
    参数：
    - patient_name: 患者姓名
    - component_name: 组件名称（资料类型）
    - files: 文件列表
    - enable_ocr: 是否启用OCR提取（默认True）
    
    返回：
    - 上传结果
    
    注意：每个患者每个资料类型只保留最新的一份文件，上传新文件时会自动删除旧文件
    """
    try:
        # 从数据库获取患者信息
        with engine.connect() as connection:
            patient_query = text("""
                SELECT id, patient_name, gender, age, phone, id_number, 
                       preliminary_diagnosis, status, creator
                FROM patients 
                WHERE patient_name = :patient_name
                AND (creator = :username OR :is_admin)
            """)
            
            patient_db = connection.execute(patient_query, {
                "patient_name": patient_name,
                "username": current_user.username,
                "is_admin": 1 if current_user.role == 'admin' else 0
            }).fetchone()
            
            if not patient_db:
                return JSONResponse(content={
                    "success": False,
                    "message": "患者不存在或无权访问"
                }, status_code=404)
            
            patient_db_id = patient_db[0]
            patient_db_name = patient_db[1]
            
        # 构建目标目录：/data/{username}/{patient_name}/{component_name}/
        target_dir = os.path.join(DATA_DIR, current_user.username, patient_name, component_name)
        os.makedirs(target_dir, exist_ok=True)
        
        # 删除该目录下的所有旧文件（只保留最新的一份）
        deleted_count = 0
        if os.path.exists(target_dir):
            for filename in os.listdir(target_dir):
                file_path = os.path.join(target_dir, filename)
                if os.path.isfile(file_path):
                    try:
                        os.remove(file_path)
                        deleted_count += 1
                        print(f"[INFO] 删除旧文件: {filename}")
                    except Exception as e:
                        print(f"[WARNING] 删除旧文件失败 {filename}: {str(e)}")
            
            if deleted_count > 0:
                print(f"[INFO] 已删除 {deleted_count} 个旧文件，准备上传新文件")
        else:
            print(f"[INFO] 目标目录不存在，创建新目录: {target_dir}")
        
        uploaded_files = []
        ocr_results = []
        
        # 保存每个文件（只保存最新的一个文件）
        for file in files:
            # 创建唯一的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"{timestamp}_{file.filename}"
            file_path = os.path.join(target_dir, filename)
            
            # 保存文件
            with open(file_path, "wb") as buffer:
                content = await file.read()
                buffer.write(content)
            
            uploaded_files.append({
                "filename": file.filename,
                "saved_name": filename,
                "content_type": file.content_type,
                "size": len(content),
                "path": file_path
            })
            
            # 如果启用OCR且是图片文件，调用agent进行OCR提取
            if enable_ocr and file.content_type in ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"]:
                print(f"[INFO] 检测到图片文件，开始OCR提取: {file.filename}")
                
                # 根据资料类型映射到data_type
                data_type = _map_component_to_data_type(component_name)
                
                # 调用agent进行OCR处理
                ocr_result = await _call_agent_with_file(
                    file_path, 
                    file.filename, 
                    data_type
                )
                
                if ocr_result.get("success"):
                    extracted_data = ocr_result.get("extracted_data", {})
                    
                    print(f"[DEBUG] 原始OCR提取数据: {extracted_data}")
                    
                    # 如果是人口学信息，处理字段冲突
                    if component_name in ["人口学信息", "人口学"]:
                        print(f"[INFO] 检测到人口学信息上传，开始处理字段冲突")
                        
                        # 1. 检查并更新患者基本信息表中的字段
                        _update_patient_info_if_needed(extracted_data, patient_name)
                        
                        # 2. 移除冲突字段，只保留人口学表特有的字段
                        cleaned_data = _handle_field_conflicts(extracted_data, {})
                        print(f"[DEBUG] 清理后的数据: {cleaned_data}")
                        
                        # 使用清理后的数据进行后续处理
                        extracted_data = cleaned_data
                    
                    # 根据资料类型进行数据校验
                    validator = get_validator(data_type)
                    is_valid, errors, standardized_data = validator.validate(extracted_data)
                    
                    ocr_results.append({
                        "filename": file.filename,
                        "ocr_success": True,
                        "extracted_data": extracted_data,
                        "standardized_data": standardized_data,
                        "data_type": data_type,
                        "validation": {
                            "is_valid": is_valid,
                            "errors": errors
                        },
                        "note": "冲突字段已移除，详细信息已更新到患者基本信息表" if component_name in ["人口学信息", "人口学"] else ""
                    })
                    print(f"[INFO] OCR提取成功: {file.filename}, 校验: {'通过' if is_valid else '失败'}")
                    if errors:
                        print(f"[WARNING] 数据校验错误: {errors}")
                else:
                    ocr_results.append({
                        "filename": file.filename,
                        "ocr_success": False,
                        "error": ocr_result.get("error", "未知错误")
                    })
                    print(f"[WARNING] OCR提取失败: {file.filename} - {ocr_result.get('error')}")
        
        return JSONResponse(content={
            "success": True,
            "message": f"成功更新 {component_name} 资料，已删除旧文件",
            "uploaded_files": uploaded_files,
            "ocr_results": ocr_results,
            "target_dir": target_dir,
            "timestamp": datetime.now().isoformat(),
            "note": "每个患者每个资料类型只保留最新的一份文件",
            "data_conflict_handling": "已自动处理基本信息表和人口学表之间的字段冲突"
        })
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"上传文件失败: {str(e)}"
            },
            status_code=500
        )


@router.get("/patients")
async def get_patients(current_user: User = Depends(get_current_active_user)):
    """
    获取当前用户的所有患者列表（从数据库查询）
    
    返回：
    - 患者列表，每个患者包含基本信息和文件统计
    """
    try:
        from data_import import Patient, DemographicData, SurgeryHistory, LabResults
        
        # 从数据库查询患者列表
        patients = []
        
        with engine.connect() as connection:
            # 根据用户角色构建查询条件
            if current_user.role == 'admin':
                # 管理员可以看到所有患者
                query = text("""
                    SELECT id, patient_id, patient_name, gender, age, phone, id_number,
                           preliminary_diagnosis, status, create_time, creator, notes
                    FROM patients
                    ORDER BY create_time DESC
                """)
                result = connection.execute(query)
            else:
                # 普通用户只能看到自己创建的患者
                query = text("""
                    SELECT id, patient_id, patient_name, gender, age, phone, id_number,
                           preliminary_diagnosis, status, create_time, creator, notes
                    FROM patients
                    WHERE creator = :username
                    ORDER BY create_time DESC
                """)
                result = connection.execute(query, {"username": current_user.username})
            
            for row in result:
                patient_id = row[0]
                
                # 查询患者的人口学信息
                demographic_query = text("SELECT id FROM demographic_data WHERE patient_id = :patient_id")
                has_demographic = connection.execute(demographic_query, {"patient_id": patient_id}).fetchone() is not None
                
                # 查询患者的手术史
                surgery_query = text("SELECT COUNT(*) FROM surgery_history WHERE patient_id = :patient_id")
                surgery_count = connection.execute(surgery_query, {"patient_id": patient_id}).fetchone()[0]
                
                # 查询患者的检查结果（包括实验室检查和影像检查）
                lab_query = text("SELECT COUNT(*) FROM lab_results WHERE patient_id = :patient_id")
                lab_count = connection.execute(lab_query, {"patient_id": patient_id}).fetchone()[0]
                
                # 查询患者的影像报告
                imaging_query = text("SELECT COUNT(*) FROM imaging_reports WHERE patient_id = :patient_id")
                imaging_count = connection.execute(imaging_query, {"patient_id": patient_id}).fetchone()[0]
                
                # 构建组件类型列表
                component_types = []
                if has_demographic:
                    component_types.append("人口学信息")
                if surgery_count > 0:
                    component_types.append("过往手术史")
                if lab_count > 0 or imaging_count > 0:
                    component_types.append("检查结果")
                
                # 计算文件总数（手术史+检查结果+影像报告）
                file_count = surgery_count + lab_count + imaging_count
                
                # 构建患者信息
                patient_info = {
                    "id": patient_id,  # 添加数据库ID
                    "patientName": row[2],
                    "patientId": row[1],
                    "gender": row[3],
                    "age": row[4],
                    "phone": row[5],
                    "idNumber": row[6],
                    "preliminaryDiagnosis": row[7],
                    "status": row[8],
                    "createTime": row[9].isoformat() if row[9] else None,
                    "creator": row[10],
                    "notes": row[11]
                }
                
                # 计算文件总数（手术史+检查结果）
                file_count = surgery_count + lab_count
                
                patients.append({
                    "patientName": row[2],
                    "patientInfo": patient_info,
                    "componentTypes": component_types,
                    "fileCount": file_count
                })
        
        return JSONResponse(content={
            "success": True,
            "patients": patients
        })
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"获取患者列表失败: {str(e)}"
            },
            status_code=500
        )


@router.get("/patient/{patient_name}/files")
async def get_patient_files(
    patient_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    
    获取指定患者的所有文件
    
    参数：
    - patient_name: 患者姓名
    
    返回：
    - 文件列表，按组件类型分组（每个资料类型最多返回一份文件）
    
    """
    try:
        # 构建患者目录
        patient_dir = os.path.join(DATA_DIR, current_user.username, patient_name)
        
        if not os.path.exists(patient_dir):
            return JSONResponse(
                content={
                    "success": False,
                    "message": "患者不存在"
                },
                status_code=404
            )
        
        # 读取患者信息
        patient_info = None
        patient_info_file = os.path.join(patient_dir, "patient_info.json")
        if os.path.exists(patient_info_file):
            with open(patient_info_file, 'r', encoding='utf-8') as f:
                patient_info = json.load(f)
        
        # 收集所有文件
        files_by_component = {}
        
        if os.path.exists(patient_dir):
            for item in os.listdir(patient_dir):
                item_path = os.path.join(patient_dir, item)
                
                # 跳过患者信息文件
                if item == "patient_info.json":
                    continue
                
                # 如果是目录，收集其中的文件
                if os.path.isdir(item_path):
                    files = []
                    for filename in os.listdir(item_path):
                        file_path = os.path.join(item_path, filename)
                        if os.path.isfile(file_path):
                            files.append({
                                "filename": filename,
                                "path": file_path,
                                "size": os.path.getsize(file_path),
                                "uploadTime": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            })
                    
                    if files:
                        files_by_component[item] = files
        
        return JSONResponse(content={
            "success": True,
            "patientInfo": patient_info,
            "filesByComponent": files_by_component
        })
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"获取患者文件失败: {str(e)}"
            },
            status_code=500
        )


@router.delete("/patient/{patient_name}")
async def delete_patient_record(
    patient_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    删除患者记录（同时删除数据库记录和文件系统）
    
    参数：
    - patient_name: 患者姓名
    
    返回：
    - 删除结果
    """
    try:
        print(f"[DEBUG] 尝试删除患者记录: {patient_name}")
        
        # 1. 首先从数据库查找患者
        with engine.connect() as connection:
            patient_query = text("""
                SELECT id, patient_name, creator
                FROM patients 
                WHERE patient_name = :patient_name
                AND (creator = :username OR :is_admin)
            """)
            
            patient_db = connection.execute(patient_query, {
                "patient_name": patient_name,
                "username": current_user.username,
                "is_admin": 1 if current_user.role == 'admin' else 0
            }).fetchone()
            
            if not patient_db:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "患者不存在或无权访问"
                    },
                    status_code=404
                )
            
            patient_db_id = patient_db[0]
            print(f"[DEBUG] 找到数据库记录: ID={patient_db_id}")
            
            # 2. 删除关联的数据库记录（级联删除）
            connection.execute(text("DELETE FROM lab_results WHERE patient_id = :patient_id"), {"patient_id": patient_db_id})
            connection.execute(text("DELETE FROM surgery_history WHERE patient_id = :patient_id"), {"patient_id": patient_db_id})
            connection.execute(text("DELETE FROM demographic_data WHERE patient_id = :patient_id"), {"patient_id": patient_db_id})
            
            # 删除患者基本信息
            connection.execute(text("DELETE FROM patients WHERE id = :patient_id"), {"patient_id": patient_db_id})
            connection.commit()
            print(f"[DEBUG] 数据库记录已删除")
        
        # 3. 删除文件系统中的患者目录（如果存在）
        patient_dir = os.path.join(DATA_DIR, current_user.username, patient_name)
        
        if os.path.exists(patient_dir):
            print(f"[DEBUG] 删除文件系统目录: {patient_dir}")
            
            # 递归删除患者目录下的所有文件和子目录
            for root, dirs, files in os.walk(patient_dir, topdown=False):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        os.remove(file_path)
                        print(f"[DEBUG] 已删除文件: {file_path}")
                    except Exception as e:
                        print(f"[ERROR] 删除文件失败 {file_path}: {str(e)}")
                
                for dir in dirs:
                    dir_path = os.path.join(root, dir)
                    try:
                        os.rmdir(dir_path)
                        print(f"[DEBUG] 已删除目录: {dir_path}")
                    except Exception as e:
                        print(f"[ERROR] 删除目录失败 {dir_path}: {str(e)}")
            
            # 删除患者根目录
            try:
                os.rmdir(patient_dir)
                print(f"[DEBUG] 已删除患者根目录: {patient_dir}")
            except Exception as e:
                print(f"[ERROR] 删除根目录失败: {str(e)}")
        
        return JSONResponse(content={
            "success": True,
            "message": "患者记录已删除",
            "deleted_id": patient_db_id
        })
    except Exception as e:
        print(f"[ERROR] 删除患者记录失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"删除患者记录失败: {str(e)}"
            },
            status_code=500
        )


@router.put("/patient/{patient_name}")
async def update_patient(
    patient_name: str,
    patient_data: PatientDataRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    更新患者记录（同时更新数据库和文件系统）
    
    参数：
    - patient_name: 原患者姓名（用于查找）
    - patient_data: 更新后的患者数据对象
    
    返回：
    - 更新结果
    """
    try:
        print(f"[DEBUG] update_patient 被调用")
        print(f"[DEBUG] 原患者姓名: {patient_name}")
        print(f"[DEBUG] 更新后数据: {patient_data}")
        
        # 1. 首先从数据库查找患者并更新记录（在同一个连接中完成）
        service = DataImportService()
        with engine.connect() as connection:
            patient_query = text("""
                SELECT id, patient_id, patient_name, gender, age, phone, id_number, 
                       preliminary_diagnosis, status, creator
                FROM patients 
                WHERE patient_name = :patient_name
                AND (creator = :username OR :is_admin)
            """)
            
            patient_db = connection.execute(patient_query, {
                "patient_name": patient_name,
                "username": current_user.username,
                "is_admin": 1 if current_user.role == 'admin' else 0
            }).fetchone()
            
            if not patient_db:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": "患者不存在或无权访问"
                    },
                    status_code=404
                )
            
            patient_db_id = patient_db[0]
            print(f"[DEBUG] 找到数据库记录: ID={patient_db_id}")
            
            # 2. 更新数据库记录（在同一个连接中）
            update_query = text("""
                UPDATE patients 
                SET patient_id = :patient_id,
                    patient_name = :patient_name,
                    gender = :gender,
                    age = :age,
                    phone = :phone,
                    id_number = :id_number,
                    preliminary_diagnosis = :preliminary_diagnosis,
                    status = :status,
                    notes = :notes,
                    update_time = NOW()
                WHERE id = :db_patient_id
            """)
            
            connection.execute(update_query, {
                "db_patient_id": patient_db_id,
                "patient_id": patient_db[1],
                "patient_name": patient_data.patientName,
                "gender": patient_data.gender,
                "age": patient_data.age,
                "phone": patient_data.phone,
                "id_number": patient_data.idNumber,
                "preliminary_diagnosis": patient_data.preliminaryDiagnosis,
                "status": patient_data.status or '待处理',
                "notes": patient_data.notes
            })
            connection.commit()
            print(f"[DEBUG] 数据库更新成功")
            
            # 3. 同步更新文件系统（如果存在）
            # 构建原患者目录路径
            original_patient_dir = os.path.join(DATA_DIR, current_user.username, patient_name)
            
            # 检查原患者目录是否存在
            if os.path.exists(original_patient_dir):
                # 如果患者姓名发生变化，需要重命名目录
                new_patient_name = patient_data.patientName
                if new_patient_name != patient_name:
                    new_patient_dir = os.path.join(DATA_DIR, current_user.username, new_patient_name)
                    
                    # 检查新名称是否已存在
                    if os.path.exists(new_patient_dir):
                        return JSONResponse(
                            content={
                                "success": False,
                                "message": f"患者名称 '{new_patient_name}' 已存在"
                            },
                            status_code=400
                        )
                    
                    # 重命名目录
                    os.rename(original_patient_dir, new_patient_dir)
                    print(f"[DEBUG] 患者目录已重命名: {patient_name} -> {new_patient_name}")
                    
                    # 更新患者目录路径
                    patient_dir = new_patient_dir
                else:
                    patient_dir = original_patient_dir
                
                # 更新患者信息文件
                patient_file = os.path.join(patient_dir, "patient_info.json")
                print(f"[DEBUG] 更新患者信息文件: {patient_file}")
                
                with open(patient_file, 'w', encoding='utf-8') as f:
                    json.dump(patient_data.dict(), f, ensure_ascii=False, indent=2)
                
                print(f"[DEBUG] 文件系统更新成功")
            
            return JSONResponse(content={
                "success": True,
                "message": "患者信息更新成功",
                "patient_id": patient_db_id
            })
            
    except Exception as e:
        print(f"[ERROR] 更新患者记录失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"更新患者记录失败: {str(e)}"
            },
            status_code=500
        )


@router.delete("/patient/{patient_name}/file")
async def delete_patient_file(
    patient_name: str,
    component_name: str = Form(...),
    filename: str = Form(...),
    current_user: User = Depends(get_current_active_user)
):
    """
    删除患者文件
    
    参数：
    - patient_name: 患者姓名
    - component_name: 组件名称（资料类型）
    - filename: 文件名
    
    返回：
    - 删除结果
    """
    try:
        # 构建文件路径
        file_path = os.path.join(DATA_DIR, current_user.username, patient_name, component_name, filename)
        
        print(f"[DEBUG] 尝试删除文件: {file_path}")
        
        # 检查文件是否存在
        if not os.path.exists(file_path):
            return JSONResponse(
                content={
                    "success": False,
                    "message": "文件不存在"
                },
                status_code=404
            )
        
        # 检查是否为文件（不是目录）
        if not os.path.isfile(file_path):
            return JSONResponse(
                content={
                    "success": False,
                    "message": "目标不是文件"
                },
                status_code=400
            )
        
        # 删除文件
        os.remove(file_path)
        
        print(f"[DEBUG] 文件删除成功: {file_path}")
        
        return JSONResponse(content={
            "success": True,
            "message": "文件删除成功",
            "deleted_file": filename
        })
    except Exception as e:
        print(f"[ERROR] 删除文件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"删除文件失败: {str(e)}"
            },
            status_code=500
        )


@router.post("/cleanup/uploads")
async def cleanup_old_files(
    days: int = Form(7),  # 默认清理7天前的文件
    current_user: User = Depends(get_current_active_user)
):
    """
    清理 uploads 文件夹中的旧文件
    
    参数：
    - days: 清理多少天前的文件（默认7天）
    
    返回：
    - 清理结果
    """
    try:
        import time
        from pathlib import Path
        
        # 计算时间阈值（秒）
        time_threshold = time.time() - (days * 24 * 60 * 60)
        
        # 获取 uploads 文件夹中的所有文件
        upload_path = Path(UPLOAD_DIR)
        
        if not upload_path.exists():
            return JSONResponse(content={
                "success": True,
                "message": "uploads 文件夹不存在",
                "deleted_count": 0
            })
        
        deleted_files = []
        deleted_count = 0
        
        # 遍历所有文件
        for file_path in upload_path.iterdir():
            if file_path.is_file():
                # 检查文件修改时间
                file_mtime = file_path.stat().st_mtime
                
                # 如果文件超过指定天数，则删除
                if file_mtime < time_threshold:
                    try:
                        file_path.unlink()
                        deleted_files.append({
                            "filename": file_path.name,
                            "size": file_path.stat().st_size,
                            "modified_time": datetime.fromtimestamp(file_mtime).isoformat()
                        })
                        deleted_count += 1
                        print(f"[INFO] 已删除旧文件: {file_path.name}")
                    except Exception as e:
                        print(f"[ERROR] 删除文件失败 {file_path.name}: {str(e)}")
        
        return JSONResponse(content={
            "success": True,
            "message": f"成功清理 {deleted_count} 个文件",
            "deleted_count": deleted_count,
            "deleted_files": deleted_files,
            "cleanup_threshold_days": days
        })
    except Exception as e:
        print(f"[ERROR] 清理文件失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"清理文件失败: {str(e)}"
            },
            status_code=500
        )


@router.get("/patient/{patient_name}/complete-info")
async def get_patient_complete_info(
    patient_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取患者的完整信息，包括基本信息和各类资料
    
    参数：
    - patient_name: 患者姓名
    
    返回：
    - 患者完整信息，包括基本信息、人口学信息、手术史、检查结果等
    """
    try:
        # 构建患者目录
        patient_dir = os.path.join(DATA_DIR, current_user.username, patient_name)
        
        if not os.path.exists(patient_dir):
            return JSONResponse(
                content={
                    "success": False,
                    "message": "患者不存在"
                },
                status_code=404
            )
        
        # 读取患者基本信息
        patient_info = None
        patient_info_file = os.path.join(patient_dir, "patient_info.json")
        if os.path.exists(patient_info_file):
            with open(patient_info_file, 'r', encoding='utf-8') as f:
                patient_info = json.load(f)
        
        # 收集各类资料信息
        component_types = []
        component_data = {}
        
        if os.path.exists(patient_dir):
            for item in os.listdir(patient_dir):
                item_path = os.path.join(patient_dir, item)
                
                # 跳过患者信息文件
                if item == "patient_info.json":
                    continue
                
                # 如果是目录，收集其中的文件信息
                if os.path.isdir(item_path):
                    component_types.append(item)
                    
                    files = []
                    for filename in os.listdir(item_path):
                        file_path = os.path.join(item_path, filename)
                        if os.path.isfile(file_path):
                            files.append({
                                "filename": filename,
                                "path": file_path,
                                "size": os.path.getsize(file_path),
                                "upload_time": datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
                            })
                    
                    component_data[item] = {
                        "file_count": len(files),
                        "latest_file": files[-1] if files else None,
                        "all_files": files
                    }
        
        return JSONResponse(content={
            "success": True,
            "patient_info": patient_info,
            "component_types": component_types,
            "component_data": component_data,
            "data_structure": {
                "basic_info": "患者基本信息表（patients）",
                "demographic": "人口学信息表（demographic_data）",
                "surgery_history": "过往手术史表（surgery_history）",
                "lab_results": "检查结果表（lab_results）"
            },
            "field_conflict_handling": "已自动处理基本信息表和人口学表之间的字段冲突"
        })
    except Exception as e:
        print(f"[ERROR] 获取患者完整信息失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"获取患者完整信息失败: {str(e)}"
            },
            status_code=500
        )
        return JSONResponse(
            content={
                "success": False,
                "message": f"清理文件失败: {str(e)}"
            },
            status_code=500
        )


# ==================== 数据入库API ====================

@router.post("/import-extracted-data")
async def import_extracted_data(
    patient_name: str = Form(...),
    data_type: str = Form(...),
    extracted_data: str = Form(...),
    patient_basic_info: str = Form("{}"),
    data_source: str = Form(None),
    current_user: User = Depends(get_current_active_user)
):
    """
    导入OCR提取的结构化数据到数据库
    
    参数：
    - patient_name: 患者姓名
    - data_type: 数据类型（人口学信息、过往手术史、检查结果、其他）
    - extracted_data: JSON格式的提取数据
    - patient_basic_info: JSON格式的患者基本信息
    - data_source: 数据来源文件名
    
    返回：
    - 导入结果
    """
    try:
        import json
        
        # 解析JSON数据
        extracted_dict = json.loads(extracted_data)
        patient_info_dict = json.loads(patient_basic_info)
        
        print(f"[DEBUG] 开始导入数据")
        print(f"[DEBUG] 患者姓名: {patient_name}")
        print(f"[DEBUG] 数据类型: {data_type}")
        print(f"[DEBUG] 提取数据: {extracted_dict}")
        print(f"[DEBUG] 患者基本信息: {patient_info_dict}")
        
        # 创建数据导入服务
        service = DataImportService()
        
        # 准备患者基本信息
        patient_data = PatientData(
            patient_name=patient_name,
            gender=patient_info_dict.get('gender', 'male'),
            age=patient_info_dict.get('age', 0),
            phone=patient_info_dict.get('phone', ''),
            id_number=patient_info_dict.get('id_number', ''),
            preliminary_diagnosis=patient_info_dict.get('preliminary_diagnosis'),
            creator=current_user.username
        )
        
        # 获取或创建患者
        patient = service.get_or_create_patient(patient_data, current_user.username)
        
        # 检查提取的数据是否为空
        is_data_empty = not extracted_dict or all(v is None or v == "" for v in extracted_dict.values())
        
        if is_data_empty:
            # 数据为空，返回提示信息
            return JSONResponse(content={
                "success": False,
                "message": "未提取到有效数据，请检查图片质量或重新上传",
                "patient_id": patient.id,
                "patient_name": patient.patient_name,
                "data_type": data_type,
                "data_source": data_source,
                "extracted_fields": [],
                "warning": "OCR未识别到任何字段",
                "import_time": datetime.now().isoformat()
            })
        
        # 导入对应类型的数据
        result = service.import_data_by_type(
            patient.id, data_type, extracted_dict, data_source
        )
        
        if result:
            return JSONResponse(content={
                "success": True,
                "message": f"成功导入{data_type}",
                "patient_id": patient.id,
                "patient_name": patient.patient_name,
                "data_type": data_type,
                "result_id": result.id,
                "extracted_fields": list(extracted_dict.keys()),
                "import_time": datetime.now().isoformat()
            })
        else:
            # result为None说明数据为空或无效
            return JSONResponse(content={
                "success": False,
                "message": "未提取到有效数据，请检查图片质量或重新上传",
                "patient_id": patient.id,
                "patient_name": patient.patient_name,
                "data_type": data_type,
                "data_source": data_source,
                "extracted_fields": list(extracted_dict.keys()) if extracted_dict else [],
                "warning": "数据验证失败，跳过导入",
                "import_time": datetime.now().isoformat()
            })
            
    except json.JSONDecodeError as e:
        return JSONResponse(content={
            "success": False,
            "message": f"JSON解析错误: {str(e)}"
        }, status_code=400)
    except Exception as e:
        print(f"[ERROR] 导入数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={
            "success": False,
            "message": f"导入数据失败: {str(e)}"
        }, status_code=500)


@router.get("/patient/{patient_name}/database-records")
async def get_patient_database_records(
    patient_name: str,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取患者的数据库记录
    
    参数：
    - patient_name: 患者姓名
    
    返回：
    - 患者在数据库中的所有记录
    """
    try:
        from sqlalchemy import or_
        
        service = DataImportService()
        
        # 查找患者
        patient = service.db.query(service.db.query(Patient).filter(
            Patient.patient_name == patient_name
        ).first())
        
        if not patient:
            return JSONResponse(content={
                "success": False,
                "message": "患者不存在"
            }, status_code=404)
        
        # 获取患者的人口学信息
        demographic = service.db.query(DemographicData).filter(
            DemographicData.patient_id == patient.id
        ).first()
        
        # 获取患者的手术史
        surgeries = service.db.query(SurgeryHistory).filter(
            SurgeryHistory.patient_id == patient.id
        ).all()
        
        # 获取患者的检查结果
        lab_results = service.db.query(LabResults).filter(
            LabResults.patient_id == patient.id
        ).all()
        
        # 构建返回数据
        result = {
            "success": True,
            "patient": {
                "id": patient.id,
                "patient_name": patient.patient_name,
                "gender": patient.gender,
                "age": patient.age,
                "phone": patient.phone,
                "preliminary_diagnosis": patient.preliminary_diagnosis,
                "status": patient.status,
                "create_time": patient.create_time.isoformat() if patient.create_time else None
            },
            "demographic_data": {
                "id": demographic.id,
                "birth_date": demographic.birth_date.isoformat() if demographic.birth_date else None,
                "education_level": demographic.education_level,
                "occupation": demographic.occupation,
                "marital_status": demographic.marital_status,
                "city": demographic.city,
                "province": demographic.province
            } if demographic else None,
            "surgery_history": [
                {
                    "id": s.id,
                    "surgery_name": s.surgery_name,
                    "surgery_date": s.surgery_date.isoformat() if s.surgery_date else None,
                    "hospital_name": s.hospital_name,
                    "surgery_outcome": s.surgery_outcome
                }
                for s in surgeries
            ],
            "lab_results": [
                {
                    "id": l.id,
                    "test_name": l.test_name,
                    "test_type": l.test_type,
                    "test_date": l.test_date.isoformat() if l.test_date else None,
                    "result_status": l.result_status,
                    "is_abnormal": l.is_abnormal
                }
                for l in lab_results
            ]
        }
        
        return JSONResponse(content=result)
        
    except Exception as e:
        print(f"[ERROR] 获取患者数据库记录失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(content={
            "success": False,
            "message": f"获取数据失败: {str(e)}"
        }, status_code=500)


# =====================================================
# 多文件上传API - 支持每种资料类型上传多份文件
# =====================================================

class MultiFileUploadRequest(BaseModel):
    """多文件上传请求模型"""
    patient_id: int
    data_category: str  # 人口学信息、既往手术史、检查结果、其他
    data_type: str = ""  # 具体资料类型（如：入院记录、血常规、超声检查等）
    file_description: str = ""
    file_tags: str = ""


@router.post("/multi-file-upload")
async def multi_file_upload(
    patient_id: int = Form(...),
    data_category: str = Form(...),
    data_type: str = Form(""),
    file_description: str = Form(""),
    file_tags: str = Form(""),
    files: List[UploadFile] = File(default=[]),  # 改为可选，避免验证错误
    model_type: str = Form("cloud"),
    vision_model: str = Form(""),
    llm_model: str = Form(""),
    current_user: User = Depends(get_current_active_user)
):
    """
    多文件上传接口 - 支持每种资料类型上传多份文件
    
    参数：
    - patient_id: 患者ID
    - data_category: 资料分类（人口学信息、既往手术史、检查结果、其他）
    - data_type: 具体资料类型（如：入院记录、血常规、超声检查等）
    - file_description: 文件描述
    - file_tags: 文件标签（逗号分隔）
    - files: 文件列表（支持多个文件）
    - model_type: 模型类型（cloud/local），默认为 cloud
    - vision_model: 视觉模型名称（可选，用于云端API）
    - llm_model: 语言模型名称（可选，用于云端API）
    
    返回：
    - 上传的文件列表及其处理状态
    """
    try:
        # 验证资料分类
        valid_categories = ['人口学信息', '既往手术史', '检查结果', '其他']
        if data_category not in valid_categories:
            return JSONResponse(
                content={
                    "success": False,
                    "message": f"无效的资料分类，必须是: {', '.join(valid_categories)}"
                },
                status_code=400
            )
        
        # 验证文件是否存在
        if not files or len(files) == 0:
            return JSONResponse(
                content={
                    "success": False,
                    "message": "未上传任何文件，请选择至少一个文件"
                },
                status_code=400
            )
        
        # 验证患者是否存在
        with engine.connect() as connection:
            patient_check = connection.execute(
                text("SELECT id, patient_name FROM patients WHERE id = :patient_id"),
                {"patient_id": patient_id}
            ).fetchone()
            
            if not patient_check:
                return JSONResponse(
                    content={
                        "success": False,
                        "message": f"患者ID {patient_id} 不存在"
                    },
                    status_code=404
                )
        
        # 准备返回结果
        result = {
            "success": True,
            "patient_id": patient_id,
            "data_category": data_category,
            "uploaded_files": [],
            "timestamp": datetime.now().isoformat()
        }
        
        # 处理每个上传的文件
        for file in files:
            try:
                # 创建唯一的文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                safe_filename = f"{timestamp}_{file.filename}"
                file_path = os.path.join(UPLOAD_DIR, safe_filename)
                
                # 保存文件
                content = await file.read()
                with open(file_path, "wb") as buffer:
                    buffer.write(content)
                
                # 获取文件信息
                file_size = len(content)
                file_type = file.content_type
                file_extension = os.path.splitext(file.filename)[1].lower().lstrip('.')
                
                # 如果未指定data_type，根据文件名推断
                if not data_type:
                    data_type = _infer_data_type_from_filename(file.filename, data_category)
                
                # 插入文件记录到数据库
                with engine.connect() as connection:
                    insert_query = text("""
                        INSERT INTO file_uploads (
                            patient_id, file_name, file_path, file_size, file_type, file_extension,
                            data_category, data_type, ocr_status, validation_status, import_status,
                            file_description, file_tags, upload_source, uploaded_by, upload_time
                        ) VALUES (
                            :patient_id, :file_name, :file_path, :file_size, :file_type, :file_extension,
                            :data_category, :data_type, 'pending', 'pending', 'pending',
                            :file_description, :file_tags, 'web', :uploaded_by, NOW()
                        )
                    """)
                    
                    connection.execute(insert_query, {
                        "patient_id": patient_id,
                        "file_name": file.filename,
                        "file_path": file_path,
                        "file_size": file_size,
                        "file_type": file_type,
                        "file_extension": file_extension,
                        "data_category": data_category,
                        "data_type": data_type,
                        "file_description": file_description,
                        "file_tags": file_tags,
                        "uploaded_by": current_user.username
                    })
                    connection.commit()
                    
                    # 获取插入的文件ID
                    file_id = connection.execute(
                        text("SELECT LAST_INSERT_ID()")
                    ).scalar()
                
                # 记录文件信息
                file_info = {
                    "file_id": file_id,
                    "original_filename": file.filename,
                    "saved_filename": safe_filename,
                    "file_path": file_path,
                    "file_size": file_size,
                    "file_type": file_type,
                    "data_category": data_category,
                    "data_type": data_type,
                    "ocr_status": "pending",
                    "is_image": file_type in ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"]
                }
                result["uploaded_files"].append(file_info)
                
            except Exception as e:
                print(f"[ERROR] 处理文件 {file.filename} 失败: {str(e)}")
                result["uploaded_files"].append({
                    "original_filename": file.filename,
                    "error": str(e)
                })
        
        # 异步处理图片文件的OCR
        image_files = [f for f in result["uploaded_files"] if f.get("is_image") and "error" not in f]
        if image_files:
            # 在后台线程中处理OCR
            import threading
            ocr_thread = threading.Thread(
                target=_process_ocr_background,
                args=(image_files, model_type, current_user.username, vision_model, llm_model)
            )
            ocr_thread.daemon = True
            ocr_thread.start()
            
            result["message"] = f"成功上传 {len(result['uploaded_files'])} 个文件，其中 {len(image_files)} 个图片文件正在进行OCR处理。"
        
        # 添加详细的提示和错误信息
        if len(image_files) > 0:
            result["message"] += " OCR处理可能需要1-3分钟时间，请耐心等待。"
            result["warnings"] = [
                "OCR处理需要一定时间，请耐心等待",
                "如果图片质量不佳或文字不清晰，OCR识别可能会失败",
                "建议：使用清晰、对比度良好的图片以提高识别准确率"
            ]
            result["ocr_errors"] = [
                "如果出现以下情况，OCR识别可能会失败：",
                "  • 图片模糊不清，文字难以辨认",
                "  • 图片有反光或阴影，影响文字识别",
                "  • 图片中包含大量重复内容（如检查时间重复出现多次）",
                "  • 图片中缺少关键的诊断信息（如诊断所见、诊断印象等）",
                "  • 图片质量较差，分辨率过低"
            ]
            result["ocr_warnings"] = [
                "建议：上传清晰、高分辨率的图片",
                "建议：确保图片包含完整的诊断信息",
                "建议：避免上传包含大量无关内容的图片"
            ]
        else:
            result["message"] += " 没有需要OCR处理的图片文件。"
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"[ERROR] 多文件上传失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return JSONResponse(
            content={
                "success": False,
                "message": f"上传失败: {str(e)}"
            },
            status_code=500
        )


def _infer_data_type_from_filename(filename: str, category: str) -> str:
    """
    根据文件名推断资料类型
    
    Args:
        filename: 文件名
        category: 资料分类
    
    Returns:
        str: 推断的资料类型
    """
    filename_lower = filename.lower()
    
    if category == "人口学信息":
        if "入院" in filename_lower:
            return "入院记录"
        elif "出院" in filename_lower:
            return "出院记录"
        elif "病历" in filename_lower:
            return "病历"
        else:
            return "人口学资料"
    
    elif category == "检查结果":
        if "血" in filename_lower or "检验" in filename_lower:
            return "血液检查"
        elif "超声" in filename_lower or "b超" in filename_lower:
            return "超声检查"
        elif "x线" in filename_lower or "xray" in filename_lower:
            return "X线检查"
        elif "ct" in filename_lower:
            return "CT检查"
        elif "mri" in filename_lower or "核磁" in filename_lower:
            return "MRI检查"
        else:
            return "检查结果"
    
    elif category == "既往手术史":
        if "手术" in filename_lower:
            return "手术记录"
        else:
            return "手术史"
    
    else:
        return "其他"


def _process_ocr_background(image_files: list, model_type: str, username: str, vision_model: str = "", llm_model: str = ""):
    """
    后台处理OCR任务
    
    Args:
        image_files: 图片文件列表
        model_type: 模型类型
        username: 用户名
        vision_model: 视觉模型名称
        llm_model: 语言模型名称
    """
    import time
    import json
    import asyncio
    
    for file_info in image_files:
        file_id = file_info["file_id"]
        file_path = file_info["file_path"]
        original_filename = file_info["original_filename"]
        data_category = file_info["data_category"]
        
        try:
            print(f"[OCR] 开始处理文件: {original_filename} (ID: {file_id})")
            
            # 更新OCR状态为处理中
            with engine.connect() as connection:
                connection.execute(
                    text("UPDATE file_uploads SET ocr_status = 'processing' WHERE id = :file_id"),
                    {"file_id": file_id}
                )
                connection.commit()
            
            # 在后台线程中调用异步函数
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                agent_result = loop.run_until_complete(
                    _call_agent_with_file(
                        file_path, 
                        original_filename, 
                        _map_component_to_data_type(data_category),
                        vision_model,
                        llm_model
                    )
                )
            finally:
                loop.close()
            
            if agent_result.get("success"):
                # 更新OCR结果
                extracted_data = agent_result.get("extracted_data", {})
                full_data_json = agent_result.get("full_data_json", {})
                
                with engine.connect() as connection:
                    connection.execute(
                        text("""
                            UPDATE file_uploads 
                            SET ocr_status = 'completed', 
                                ocr_result = :ocr_result,
                                ocr_time = NOW()
                            WHERE id = :file_id
                        """),
                        {
                            "file_id": file_id,
                            "ocr_result": json.dumps({
                                "extracted_data": extracted_data,
                                "full_data_json": full_data_json
                            }, ensure_ascii=False)
                        }
                    )
                    connection.commit()
                
                print(f"[OCR] 文件处理成功: {original_filename}")
                
                # 验证和导入数据，并收集提示信息
                messages = _validate_and_import_data(file_id, extracted_data, data_category, username, full_data_json)
                
                # 注意：消息不存储到数据库，仅用于前端显示
            else:
                # OCR处理失败
                error_msg = agent_result.get("error", "未知错误")
                
                with engine.connect() as connection:
                    connection.execute(
                        text("""
                            UPDATE file_uploads 
                            SET ocr_status = 'failed', 
                                ocr_error = :error
                            WHERE id = :file_id
                        """),
                        {
                            "file_id": file_id,
                            "error": error_msg
                        }
                    )
                    connection.commit()
                
                print(f"[OCR] 文件处理失败: {original_filename} - {error_msg}")
                
        except Exception as e:
            print(f"[ERROR] OCR处理异常: {original_filename} - {str(e)}")
            import traceback
            traceback.print_exc()
            
            # 更新状态为失败
            with engine.connect() as connection:
                connection.execute(
                    text("""
                        UPDATE file_uploads 
                        SET ocr_status = 'failed', 
                            ocr_error = :error
                        WHERE id = :file_id
                    """),
                    {
                        "file_id": file_id,
                        "error": str(e)
                    }
                )
                connection.commit()


def _validate_and_import_data(file_id: int, extracted_data: dict, data_category: str, username: str, full_data_json: dict = None) -> dict:
    """
    验证并导入数据到相应的数据表
    
    Returns:
        dict: 包含收集到的提示信息
        {
            "ocr_quality_issues": [],  # OCR质量问题
            "ocr_quality_warnings": [],  # OCR质量警告
            "validation_errors": [],  # 验证错误
            "validation_warnings": [],  # 验证警告
            "import_messages": []  # 导入消息
        }
    
    Args:
        file_id: 文件ID
        extracted_data: OCR提取的数据
        data_category: 资料分类
        username: 用户名
    """
    import json
    
    # 初始化消息收集变量
    messages = {
        "ocr_quality_issues": [],
        "ocr_quality_warnings": [],
        "validation_errors": [],
        "validation_warnings": [],
        "import_messages": []
    }
    
    # 更新验证状态
    with engine.connect() as connection:
        connection.execute(
            text("UPDATE file_uploads SET validation_status = 'pending' WHERE id = :file_id"),
            {"file_id": file_id}
        )
        connection.commit()
    
    # 获取patient_id
    with engine.connect() as connection:
        patient_id = connection.execute(
            text("SELECT patient_id FROM file_uploads WHERE id = :file_id"),
            {"file_id": file_id}
        ).scalar()
    
    # 根据资料类型进行不同的验证和导入
    validator = get_validator(data_category)
    validation_result = validator.validate(extracted_data)
    
    # 处理验证结果 - 返回格式是 Tuple[bool, List[str], Dict[str, Any]]
    is_valid = validation_result[0]  # 第一个元素是bool
    errors = validation_result[1]      # 第二个元素是错误列表
    standardized_data = validation_result[2]  # 第三个元素是标准化数据
    
    print(f"[DEBUG] 验证结果: is_valid={is_valid}, errors={errors}")
    print(f"[DEBUG] 标准化数据类型: {type(standardized_data)}")
    print(f"[DEBUG] 标准化数据内容: {json.dumps(standardized_data, ensure_ascii=False)[:300]}")
    
    if is_valid:
        # 验证通过，导入数据
        try:
            # 将标准化数据转换为导入格式
            # standardized_data的格式是: {"field_name": {"value": "...", "unit": "...", "original": "..."}}
            # 需要转换为: {"field_name": "..."}
            import_data = {}
            for key, value_obj in standardized_data.items():
                if isinstance(value_obj, dict) and "value" in value_obj:
                    import_data[key] = value_obj["value"]
                else:
                    import_data[key] = value_obj
            
            # 如果转换后数据为空，使用原始数据
            if not import_data and extracted_data:
                import_data = extracted_data
                print(f"[DEBUG] 使用原始数据，因为转换后数据为空")
            
            # 如果数据仍然为空，尝试从full_data_json提取
            if not import_data and full_data_json and "structured_data" in full_data_json:
                structured_data = full_data_json["structured_data"]
                if isinstance(structured_data, list) and len(structured_data) > 0:
                    print(f"[DEBUG] 从full_data_json提取结构化数据，共{len(structured_data)}项")
                    
                    # 定义需要过滤的元数据字段
                    metadata_fields = {
                        "申请医生", "审核医生", "检查医生", "报告医生", "主治医生", "执行医生",
                        "申请时间", "检查时间", "报告时间", "采集时间", "检验时间",
                        "检查类别名称", "报告类型", "标本类型", "样本类型",
                        "检查科室", "送检科室", "检验科室",
                        "申请单号", "报告单号", "检验单号", "样本编号",
                        "患者姓名", "性别", "年龄", "床号", "住院号", "门诊号",
                        "临床诊断", "送检目的", "备注信息", "备注",
                        "送检单位", "检验单位", "医院名称", "检查者名称"
                    }
                    
                    # 过滤掉元数据字段
                    filtered_data = []
                    filtered_count = 0
                    for item in structured_data:
                        project_name = item.get("项目名称", "").strip()
                        # 检查是否为元数据字段
                        if project_name in metadata_fields or \
                           any(field in project_name for field in ["医生", "时间", "类型", "编号", "单号", "科室", "姓名", "性别", "年龄", "床号", "诊断", "目的", "备注", "单位"]):
                            filtered_count += 1
                            continue
                        filtered_data.append(item)
                    
                    print(f"[DEBUG] 过滤了 {filtered_count} 个元数据字段，剩余 {len(filtered_data)} 个有效项目")
                    
                    # 对于检查结果，将过滤后的结构化数据转换为检查项目列表
                    import_data = {"items": filtered_data}
            
            # 如果数据仍然为空，设置默认值
            if not import_data:
                print(f"[WARNING] 数据为空，设置默认值")
                if data_category == "检查结果":
                    import_data = {
                        "test_name": "未命名检查",
                        "test_type": "其他",
                        "test_result": "无数据"
                    }
                elif data_category == "人口学信息":
                    import_data = {
                        "备注": "无数据"
                    }
                elif data_category == "既往手术史":
                    import_data = {
                        "surgery_name": "未命名手术",
                        "surgery_outcome": "未知"
                    }
            
            print(f"[DEBUG] 最终导入数据: {json.dumps(import_data, ensure_ascii=False)[:300]}")
            
            # 使用转换后的数据进行导入
            if data_category == "人口学信息":
                _import_demographic_data(patient_id, import_data, file_id)
            elif data_category == "检查结果":
                # 判断是否为影像报告
                is_imaging_report = _is_imaging_report(full_data_json)
                
                if is_imaging_report:
                    print(f"[INFO] 检测到影像报告，使用影像报告处理逻辑")
                    _import_imaging_report(patient_id, import_data, file_id, full_data_json)
                else:
                    print(f"[INFO] 检测到实验室检验报告，使用检验报告处理逻辑")
                    _import_lab_results(patient_id, import_data, file_id, full_data_json)
            elif data_category == "既往手术史":
                _import_surgery_history(patient_id, import_data, file_id)
            
            # 更新状态
            with engine.connect() as connection:
                connection.execute(
                    text("""
                        UPDATE file_uploads 
                        SET validation_status = 'valid', 
                            import_status = 'imported',
                            validation_time = NOW(),
                            import_time = NOW()
                        WHERE id = :file_id
                    """),
                    {"file_id": file_id}
                )
                connection.commit()
            
            print(f"[IMPORT] 数据导入成功: file_id={file_id}, category={data_category}")
            messages["import_messages"].append(f"数据导入成功，资料类型：{data_category}")
            
        except Exception as e:
            error_msg = str(e)
            messages["import_messages"].append(f"数据导入失败：{error_msg}")
            
            # 检查是否是OCR质量检查失败
            is_ocr_quality_error = "OCR识别质量" in error_msg or "OCR文本中不包含" in error_msg
            
            # 导入失败
            with engine.connect() as connection:
                if is_ocr_quality_error:
                    # OCR质量检查失败，设置ocr_error
                    connection.execute(
                        text("""
                            UPDATE file_uploads 
                            SET validation_status = 'valid',
                                ocr_status = 'failed',
                                ocr_error = :error,
                                validation_time = NOW()
                            WHERE id = :file_id
                        """),
                        {
                            "file_id": file_id,
                            "error": error_msg
                        }
                    )
                else:
                    # 其他导入失败，设置import_error
                    connection.execute(
                        text("""
                            UPDATE file_uploads 
                            SET validation_status = 'valid',
                                import_status = 'failed',
                                import_error = :error,
                                validation_time = NOW()
                        """),
                        {
                            "file_id": file_id,
                            "error": error_msg
                        }
                    )
                connection.commit()
            
            print(f"[ERROR] 数据导入失败: {error_msg}")
    else:
        # 验证失败
        with engine.connect() as connection:
            connection.execute(
                text("""
                    UPDATE file_uploads 
                    SET validation_status = 'invalid',
                        validation_errors = :errors,
                        validation_time = NOW()
                    WHERE id = :file_id
                """),
                {
                    "file_id": file_id,
                    "errors": json.dumps(errors, ensure_ascii=False)
                }
            )
            connection.commit()
        
        print(f"[VALIDATION] 数据验证失败: {errors}")
        messages["validation_errors"].extend(errors)
    
    # 返回收集到的所有消息
    return messages


def _import_demographic_data(patient_id: int, data: dict, file_id: int):
    """导入人口学数据"""
    with engine.connect() as connection:
        # 检查是否已有记录
        existing = connection.execute(
            text("SELECT id FROM demographic_data WHERE patient_id = :patient_id"),
            {"patient_id": patient_id}
        ).fetchone()
        
        # 处理冲突字段
        cleaned_data = _handle_field_conflicts(data, {})
        
        # 构建插入/更新语句
        if existing:
            # 更新现有记录
            update_fields = []
            update_values = {"patient_id": patient_id}
            
            for key, value in cleaned_data.items():
                if key in DEMOGRAPHIC_FIELDS:
                    update_fields.append(f"{key} = :{key}")
                    update_values[key] = value
            
            if update_fields:
                update_values["data_source"] = f"file_upload_{file_id}"
                update_fields.append("data_source = :data_source")
                
                connection.execute(
                    text(f"""
                        UPDATE demographic_data 
                        SET {', '.join(update_fields)}, update_time = NOW()
                        WHERE patient_id = :patient_id
                    """),
                    update_values
                )
        else:
            # 插入新记录
            insert_fields = ["patient_id", "data_source"]
            insert_values = {"patient_id": patient_id, "data_source": f"file_upload_{file_id}"}
            
            for key, value in cleaned_data.items():
                if key in DEMOGRAPHIC_FIELDS:
                    insert_fields.append(key)
                    insert_values[key] = value
            
            connection.execute(
                text(f"""
                    INSERT INTO demographic_data ({', '.join(insert_fields)})
                    VALUES (:{', :'.join(insert_fields)})
                """),
                insert_values
            )
        
        connection.commit()


def _import_lab_results(patient_id: int, data: dict, file_id: int, full_data_json: dict = None):
    """导入检查结果数据"""
    import json
    
    try:
        with engine.connect() as connection:
            # 打印数据结构用于调试
            print(f"[DEBUG] 导入检查结果数据 - file_id: {file_id}")
            print(f"[DEBUG] 数据类型: {type(data)}")
            print(f"[DEBUG] 数据内容: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
            
            # 检查data是否为字典
            if not isinstance(data, dict):
                print(f"[ERROR] 数据格式错误，期望dict，得到: {type(data)}")
                return
            
            # 检查是否有items字段
            if "items" in data and isinstance(data["items"], list):
                # 多个检查项目
                print(f"[DEBUG] 检测到 {len(data['items'])} 个检查项目")
                
                # 定义无效的项目名称（列头等）
                invalid_project_names = {
                    '项目名称', '项目编码', '结果', '单位', '参考值范围', '提示',
                    'test_name', 'test_type', 'test_date', 'hospital_name', 'department',
                    'doctor_name', 'imaging_type', 'imaging_site', 'imaging_findings',
                    'imaging_conclusion', 'specimen_type', 'collection_time', 'report_time',
                    'related_diagnosis', 'clinical_significance', 'treatment_suggestion',
                    '日期', '阳性', '阴性', '阳性（+）', '阴性（-）'
                }
                
                # 定义需要过滤的元数据字段（这些不是检查项目）
                metadata_fields = {
                    "申请医生", "审核医生", "检查医生", "报告医生", "主治医生",
                    "申请时间", "检查时间", "报告时间", "采集时间", "检验时间",
                    "检查类别名称", "报告类型", "标本类型", "样本类型",
                    "检查科室", "送检科室", "检验科室",
                    "申请单号", "报告单号", "检验单号", "样本编号",
                    "患者姓名", "性别", "年龄", "床号", "住院号", "门诊号",
                    "临床诊断", "送检目的", "备注信息", "备注",
                    "送检单位", "检验单位", "医院名称"
                }
                
                valid_items = []
                filtered_count = 0
                duplicate_count = 0
                
                print(f"[DEDUPLICATE] ========== 开始重复数据检测 ==========")
                
                for i, item in enumerate(data["items"]):
                    project_name = item.get("项目名称") or item.get("项目名称 ") or ""
                    project_name_stripped = project_name.strip()
                    
                    # 批量过滤元数据字段
                    if project_name_stripped in metadata_fields or \
                       any(field in project_name_stripped for field in ["医生", "时间", "类型", "编号", "单号", "科室", "姓名", "性别", "年龄", "床号", "诊断", "目的", "备注", "单位"]):
                        filtered_count += 1
                        continue
                    
                    # 跳过无效项目（列头、单位等）
                    if project_name in invalid_project_names:
                        print(f"[DEBUG] 跳过无效项目: {project_name}")
                        continue
                    
                    # 只处理包含实际检验数据的项目
                    if item.get("结果") and item.get("结果") not in invalid_project_names:
                        print(f"[DEBUG] 处理第 {i+1} 个项目: {project_name}")
                        
                        # 检查是否存在重复数据
                        test_date = item.get("检验日期") or item.get("检验日期 ")
                        if test_date:
                            try:
                                # 删除同一天、同一患者、同一检验项目的旧数据
                                delete_query = text("""
                                    DELETE FROM lab_results 
                                    WHERE patient_id = :patient_id 
                                    AND test_name = :test_name 
                                    AND test_date = :test_date
                                """)
                                result = connection.execute(delete_query, {
                                    "patient_id": patient_id,
                                    "test_name": project_name_stripped,
                                    "test_date": test_date
                                })
                                deleted_count = result.rowcount
                                if deleted_count > 0:
                                    duplicate_count += deleted_count
                                    print(f"[DEDUPLICATE] 删除了 {deleted_count} 条重复记录（患者ID={patient_id}, 检验项目={project_name_stripped}, 检验日期={test_date}）")
                            except Exception as e:
                                print(f"[ERROR] 删除重复数据失败: {str(e)}")
                        
                        # 插入新数据
                        _insert_single_lab_result(connection, patient_id, item, file_id)
                        valid_items.append(project_name)
                
                print(f"[INFO] 过滤了 {filtered_count} 个元数据字段")
                print(f"[DEDUPLICATE] 删除了 {duplicate_count} 条重复记录")
                print(f"[INFO] 成功导入检查结果数据，有效项目: {len(valid_items)}个")
                
                connection.commit()
                
            else:
                # 单个检查结果
                print(f"[DEBUG] 处理单个检查项目")
                
                # 检查是否存在重复数据
                if isinstance(data, dict):
                    project_name = data.get("项目名称") or data.get("项目名称 ") or ""
                    test_date = data.get("检验日期") or data.get("检验日期 ")
                    if project_name and test_date:
                        try:
                            # 删除同一天、同一患者、同一检验项目的旧数据
                            delete_query = text("""
                                DELETE FROM lab_results 
                                WHERE patient_id = :patient_id 
                                AND test_name = :test_name 
                                AND test_date = :test_date
                            """)
                            result = connection.execute(delete_query, {
                                "patient_id": patient_id,
                                "test_name": project_name.strip(),
                                "test_date": test_date
                            })
                            deleted_count = result.rowcount
                            if deleted_count > 0:
                                print(f"[DEDUPLICATE] 删除了 {deleted_count} 条重复记录（患者ID={patient_id}, 检验项目={project_name.strip()}, 检验日期={test_date}）")
                        except Exception as e:
                            print(f"[ERROR] 删除重复数据失败: {str(e)}")
                
                _insert_single_lab_result(connection, patient_id, data, file_id)
                connection.commit()
                print(f"[INFO] 成功导入检查结果数据")
            
    except Exception as e:
        print(f"[ERROR] 导入检查结果数据失败: {str(e)}")
        print(f"[ERROR] 数据类型: {type(data)}")
        print(f"[ERROR] 数据内容: {str(data)[:500]}")
        import traceback
        traceback.print_exc()
        raise


def _insert_single_lab_result(connection, patient_id: int, data: dict, file_id: int):
    """插入单条检查结果"""
    # 处理structured_data格式（来自full_data_json）
    # 支持多种字段名变体
    project_name = data.get("项目名称") or data.get("项目名称 ") or data.get("test_name") or data.get("test_name ")
    raw_result = data.get("结果") or data.get("结果 ") or data.get("test_result") or data.get("test_result ")
    reference_range = data.get("参考范围") or data.get("参考范围 ") or data.get("reference_range") or data.get("reference_range ")
    unit = data.get("单位") or data.get("单位 ") or data.get("unit") or data.get("unit ")
    test_date = data.get("检验日期") or data.get("检验日期 ") or data.get("test_date") or data.get("test_date ")
    
    # 检查是否需要转换structured_data格式
    needs_conversion = project_name and not (data.get("test_name") or data.get("test_result") or data.get("result_value"))
    
    # 定义需要过滤的元数据字段（这些不是检查项目，不应该插入数据库）
    metadata_fields = {
        "申请医生", "审核医生", "检查医生", "报告医生", "主治医生",
        "申请时间", "检查时间", "报告时间", "采集时间", "检验时间",
        "检查类别名称", "报告类型", "标本类型", "样本类型",
        "检查科室", "送检科室", "检验科室",
        "申请单号", "报告单号", "检验单号", "样本编号",
        "患者姓名", "性别", "年龄", "床号", "住院号", "门诊号",
        "临床诊断", "送检目的", "备注信息", "备注",
        "送检单位", "检验单位", "医院名称"
    }
    
    # 过滤元数据字段
    if needs_conversion and project_name:
        project_name_stripped = project_name.strip()
        # 检查是否为元数据字段
        if project_name_stripped in metadata_fields or \
           any(field in project_name_stripped for field in ["医生", "时间", "类型", "编号", "单号", "科室", "姓名", "性别", "年龄", "床号", "诊断", "目的", "备注", "单位"]):
            print(f"[DEBUG] 过滤元数据字段: {project_name_stripped}")
            return  # 跳过这个字段，不插入数据库
    
    if needs_conversion:
        # 这是structured_data格式，需要转换
        print(f"[DEBUG] 检测到structured_data格式，需要转换")
        print(f"[DEBUG] 原始数据: project_name={project_name}, raw_result={raw_result}, reference_range={reference_range}, unit={unit}")
        
        # 根据项目名称判断数据类型
        test_type = "其他"
        test_result = ""
        
        if "血型" in project_name or "ABO" in project_name or "Rh" in project_name:
            # 血型检测
            print(f"[DEBUG] 识别为血型检测")
            test_type = "血液检查"
            test_result = raw_result if raw_result else ""
# 乙肝检测
        elif "乙肝" in project_name or "HBs" in project_name or "HBe" in project_name or "HBc" in project_name:
            # 乙肝检测 - 改为免疫检查
            print(f"[DEBUG] 识别为乙肝检测，映射为免疫检查")
            test_type = "免疫检查"
            # 使用原始结果作为检测结果
            test_result = raw_result if raw_result else ""
        # 血常规
        elif "白细胞" in project_name or "红细胞" in project_name or "血红蛋白" in project_name or "血小板" in project_name or \
             "中性粒细胞" in project_name or "淋巴细胞" in project_name or "单核细胞" in project_name or \
             "嗜酸性" in project_name or "嗜碱性" in project_name:
            print(f"[DEBUG] 识别为血常规")
            test_type = "血液检查"
            test_result = raw_result if raw_result else ""
        # 肝功能
        elif "谷丙转氨酶" in project_name or "谷草转氨酶" in project_name or "ALT" in project_name or "AST" in project_name or \
             "谷氨酰转肽酶" in project_name or "碱性磷酸酶" in project_name or "总胆红素" in project_name or \
             "直接胆红素" in project_name or "间接胆红素" in project_name or "总蛋白" in project_name or \
             "白蛋白" in project_name or "球蛋白" in project_name:
            print(f"[DEBUG] 识别为肝功能")
            test_type = "生化检查"
            test_result = raw_result if raw_result else ""
        # 肾功能
        elif "肌酐" in project_name or "尿素氮" in project_name or "尿酸" in project_name or "estimated" in project_name or \
             "肾小球滤过率" in project_name or "GFR" in project_name:
            print(f"[DEBUG] 识别为肾功能")
            test_type = "生化检查"
            test_result = raw_result if raw_result else ""
        # 血脂
        elif "总胆固醇" in project_name or "甘油三酯" in project_name or "高密度" in project_name or \
             "低密度" in project_name or "血脂" in project_name or "HDL" in project_name or "LDL" in project_name:
            print(f"[DEBUG] 识别为血脂")
            test_type = "生化检查"
            test_result = raw_result if raw_result else ""
        # 血糖
        elif "血糖" in project_name or "空腹血糖" in project_name or "糖化血红蛋白" in project_name or "HbA1c" in project_name:
            print(f"[DEBUG] 识别为血糖")
            test_type = "生化检查"
            test_result = raw_result if raw_result else ""
        # 凝血功能
        elif "凝血" in project_name or "血小板" in project_name or "纤维蛋白原" in project_name or \
             "凝血酶原时间" in project_name or "活化部分" in project_name or "APTT" in project_name:
            print(f"[DEBUG] 识别为凝血功能")
            test_type = "血液检查"
            test_result = raw_result if raw_result else ""
        # 肿瘤标志物
        elif "癌胚" in project_name or "甲胎" in project_name or "CA" in project_name or "肿瘤" in project_name or \
             "CEA" in project_name or "AFP" in project_name or "CA19" in project_name or "CA125" in project_name:
            print(f"[DEBUG] 识别为肿瘤标志物")
            test_type = "免疫检查"
            test_result = raw_result if raw_result else ""
        # 电解质
        elif "钾" in project_name or "钠" in project_name or "氯" in project_name or "钙" in project_name or \
             "磷" in project_name or "镁" in project_name or "电解质" in project_name:
            print(f"[DEBUG] 识别为电解质")
            test_type = "生化检查"
            test_result = raw_result if raw_result else ""
        else:
            # 其他检验
            print(f"[DEBUG] 识别为其他检验: {project_name}")
            test_type = "其他"
            test_result = raw_result if raw_result else ""
        
        converted_data = {
            "test_name": project_name.strip() if project_name else "未知检查",
            "test_result": test_result.strip() if test_result else "",
            "result_value": test_result.strip() if test_result else (raw_result.strip() if raw_result else ""),
            "reference_range": reference_range.strip() if reference_range else "",
            "unit": unit.strip() if unit else "",
            "test_type": test_type,
            "is_abnormal": "阳性" in str(test_result) if test_result else False
        }
        
        # 添加 test_date 字段
        if test_date and test_date.strip():
            converted_data["test_date"] = test_date.strip()
        print(f"[DEBUG] 转换structured_data: {converted_data}")
        print(f"[DEBUG] 最终test_result: {converted_data['test_result']}")
        data = converted_data
    else:
        print(f"[DEBUG] 数据已是正确格式，无需转换")
    
    # 映射字段
    field_mapping = {
        "test_name": "test_name",
        "test_type": "test_type",
        "test_date": "test_date",
        "hospital_name": "hospital_name",
        "department": "department",
        "doctor_name": "doctor_name",
        "test_result": "test_result",
        "result_value": "result_value",
        "reference_range": "reference_range",
        "unit": "unit",
        "result_status": "result_status",
        "is_abnormal": "is_abnormal",
        "abnormal_description": "abnormal_description",
        "imaging_type": "imaging_type",
        "imaging_site": "imaging_site",
        "imaging_findings": "imaging_findings",
        "imaging_conclusion": "imaging_conclusion",
        "specimen_type": "specimen_type",
        "collection_time": "collection_time",
        "report_time": "report_time",
        "related_diagnosis": "related_diagnosis",
        "clinical_significance": "clinical_significance",
        "treatment_suggestion": "treatment_suggestion"
    }
    
    insert_fields = ["patient_id", "data_source"]
    insert_values = {
        "patient_id": patient_id,
        "data_source": f"file_upload_{file_id}"
    }
    
    for data_key, db_field in field_mapping.items():
        if data_key in data and data[data_key]:
            insert_fields.append(db_field)
            insert_values[db_field] = data[data_key]
    
    # 确保test_name字段存在（必需字段）
    if "test_name" not in insert_values:
        print(f"[ERROR] test_name字段缺失，当前数据: {data}")
        print(f"[ERROR] insert_fields: {insert_fields}")
        print(f"[ERROR] insert_values: {insert_values}")
        # 使用默认值
        insert_fields.append("test_name")
        insert_values["test_name"] = data.get("项目名称", "未知检查") if "项目名称" in data else "未知检查"
    
    # 设置异常标志
    if "is_abnormal" not in insert_values:
        insert_values["is_abnormal"] = data.get("is_abnormal", False)
    
    print(f"[DEBUG] 最终插入字段: {insert_fields}")
    print(f"[DEBUG] 最终插入值: {insert_values}")
    
    connection.execute(
        text(f"""
            INSERT INTO lab_results ({', '.join(insert_fields)})
            VALUES (:{', :'.join(insert_fields)})
        """),
        insert_values
    )


def _import_surgery_history(patient_id: int, data: dict, file_id: int):
    """导入手术历史数据"""
    with engine.connect() as connection:
        # 映射字段
        field_mapping = {
            "surgery_name": "surgery_name",
            "surgery_date": "surgery_date",
            "hospital_name": "hospital_name",
            "department": "department",
            "surgeon_name": "surgeon_name",
            "surgery_type": "surgery_type",
            "surgery_grade": "surgery_grade",
            "anesthesia_type": "anesthesia_type",
            "surgery_reason": "surgery_reason",
            "diagnosis_before_surgery": "diagnosis_before_surgery",
            "surgery_outcome": "surgery_outcome",
            "complications": "complications",
            "admission_date": "admission_date",
            "discharge_date": "discharge_date",
            "hospitalization_days": "hospitalization_days",
            "surgery_cost": "surgery_cost",
            "total_cost": "total_cost",
            "insurance_reimbursement": "insurance_reimbursement",
            "self_payment": "self_payment",
            "follow_up_status": "follow_up_status",
            "follow_up_date": "follow_up_date",
            "follow_up_result": "follow_up_result"
        }
        
        insert_fields = ["patient_id", "data_source"]
        insert_values = {
            "patient_id": patient_id,
            "data_source": f"file_upload_{file_id}"
        }
        
        for data_key, db_field in field_mapping.items():
            if data_key in data and data[data_key]:
                insert_fields.append(db_field)
                insert_values[db_field] = data[data_key]
        
        connection.execute(
            text(f"""
                INSERT INTO surgery_history ({', '.join(insert_fields)})
                VALUES (:{', :'.join(insert_fields)})
            """),
            insert_values
        )
        
        connection.commit()


def _import_imaging_report(patient_id: int, data: dict, file_id: int, full_data_json: dict = None):
    """
    导入影像检查报告数据
    
    Args:
        patient_id: 患者ID
        data: OCR提取的数据
        file_id: 文件ID
        full_data_json: 完整的OCR数据
    """
    try:
        # 导入影像报告提取器
        import sys
        import os
        sys.path.append(os.path.join(os.path.dirname(__file__), '..', '数据agent'))
        from core.imaging_extractor import ImagingReportExtractor
        
        print(f"[DEBUG] 开始导入影像报告数据 - file_id: {file_id}")
        
        # 获取原始文本（处理两种可能的数据结构）
        raw_text = ""
        if full_data_json:
            # 情况1: full_data_json 包含 'full_data_json' 键（嵌套结构）
            if 'full_data_json' in full_data_json:
                raw_text = full_data_json['full_data_json'].get('raw_text', '')
            # 情况2: full_data_json 直接包含 'raw_text' 键（平铺结构）
            elif 'raw_text' in full_data_json:
                raw_text = full_data_json.get('raw_text', '')
        
        # 如果 full_data_json 中没有 raw_text，才尝试从 items 中提取
        if not raw_text and 'items' in data and data['items']:
            print(f"[DEBUG] 从 items 中提取文本（不推荐）")
            for item in data['items']:
                raw_text += f"{item.get('项目名称', '')} {item.get('结果', '')} {item.get('原始数据', '')}\n"
        
        print(f"[DEBUG] 原始文本长度: {len(raw_text)}")
        
        # 提取结构化数据
        extractor = ImagingReportExtractor()
        extracted_data = extractor.extract_imaging_report(raw_text)
        
        print(f"[DEBUG] 提取的影像类型: {extracted_data.get('imaging_type')}")
        print(f"[DEBUG] 诊断所见长度: {len(extracted_data.get('findings', ''))}")
        print(f"[DEBUG] 诊断印象长度: {len(extracted_data.get('impression', ''))}")
        
        # OCR质量检查
        print(f"[OCR_QUALITY] ========== 开始OCR质量检查 ==========")
        quality_check = extractor.check_ocr_quality(raw_text)
        
        if not quality_check['is_good_quality']:
            print(f"[OCR_QUALITY] ❌ OCR识别质量检查失败")
            for issue in quality_check['issues']:
                print(f"  - {issue}")
            print(f"[OCR_QUALITY] 建议：请检查原始图片质量或重新上传")
            
            # 如果OCR质量严重问题，阻止导入
            if quality_check['issues']:
                error_msg = f"OCR识别质量严重问题：{'; '.join(quality_check['issues'])}"
                print(f"[ERROR] {error_msg}")
                raise Exception(error_msg)
        
        for warning in quality_check['warnings']:
            print(f"[OCR_QUALITY] ⚠️  {warning}")
        
        # 数据验证和错误诊断
        print(f"[VALIDATION] ========== 开始影像报告数据验证 ==========")
        validation_errors = []
        validation_warnings = []
        
        # 1. 检查必填字段
        required_fields = {
            'patient_id': patient_id,
            'imaging_type': extracted_data.get('imaging_type'),
            'findings': extracted_data.get('findings', '')
        }
        
        for field_name, field_value in required_fields.items():
            if not field_value or (isinstance(field_value, str) and not field_value.strip()):
                validation_errors.append(f"【严重错误】必填字段 '{field_name}' 为空")
        
        # 2. 检查影像类型
        imaging_type = extracted_data.get('imaging_type', '')
        valid_imaging_types = ['超声', 'CT', 'MRI', 'X光', '核医学', '其他']
        if imaging_type not in valid_imaging_types:
            validation_errors.append(f"【错误】影像类型 '{imaging_type}' 无效，有效值为：{', '.join(valid_imaging_types)}")
        
        # 3. 检查诊断所见和诊断印象（核心内容）
        findings = extracted_data.get('findings', '')
        impression = extracted_data.get('impression', '')
        
        # 诊断所见是核心内容，必须有一定长度
        if len(findings) < 10:
            validation_errors.append(f"【严重错误】诊断所见内容过短（{len(findings)}字符），数据不完整，无法导入")
        
        if len(findings) > 5000:
            validation_warnings.append(f"【警告】诊断所见内容过长（{len(findings)}字符），可能包含无关信息")
        
        # 诊断印象是核心内容，不能为空
        if not impression or not impression.strip():
            validation_errors.append("【严重错误】诊断印象为空，缺少核心诊断结论，无法导入")
        
        # 4. 检查日期字段
        exam_date = extracted_data.get('exam_date')
        exam_time = extracted_data.get('exam_time')
        
        if exam_date and exam_time:
            try:
                from datetime import datetime
                if isinstance(exam_date, str):
                    # 尝试解析日期字符串
                    datetime.strptime(exam_date, '%Y-%m-%d')
                if isinstance(exam_time, str):
                    # 尝试解析时间字符串
                    datetime.strptime(exam_time, '%H:%M:%S')
            except ValueError as e:
                validation_errors.append(f"【错误】日期时间格式不正确：{str(e)}")
        
        # 5. 检查医生信息
        doctor_fields = {
            '申请医生': extracted_data.get('requesting_doctor'),
            '检查医生': extracted_data.get('performing_doctor'),
            '报告医生': extracted_data.get('reporting_doctor')
        }
        
        missing_doctors = [name for name, value in doctor_fields.items() if not value]
        if missing_doctors:
            validation_warnings.append(f"【警告】缺少医生信息：{', '.join(missing_doctors)}")
        
        # 6. 检查严重程度
        severity = extracted_data.get('severity')
        valid_severities = ['正常', '轻度', '中度', '重度']
        if severity and severity not in valid_severities:
            validation_warnings.append(f"【警告】严重程度 '{severity}' 不是标准值")
        
        # 7. 检查器官发现
        organ_findings = extracted_data.get('organ_findings', [])
        if not organ_findings and not findings:
            validation_errors.append("【严重错误】诊断所见和器官发现均为空，无法导入")
        
        if organ_findings and len(organ_findings) > 20:
            validation_warnings.append(f"【警告】器官发现数量过多（{len(organ_findings)}个），可能包含重复或无关项")
        
        # 8. 检查数据完整性
        if not extracted_data.get('hospital_name'):
            validation_warnings.append("【警告】缺少医院名称")
        
        if not extracted_data.get('department'):
            validation_warnings.append("【警告】缺少科室信息")
        
        # 9. 逻辑一致性检查
        if severity == '正常' and '异常' in findings:
            validation_warnings.append("【警告】严重程度为'正常'，但诊断所见中包含'异常'描述，请检查")
        
        if extracted_data.get('follow_up_required') and not extracted_data.get('follow_up_recommendation'):
            validation_warnings.append("【警告】标记需要随访，但未提供随访建议")
        
        # 输出验证结果
        if validation_errors:
            print(f"[VALIDATION] ❌ 发现 {len(validation_errors)} 个严重错误：")
            for error in validation_errors:
                print(f"  - {error}")
        
        if validation_warnings:
            print(f"[VALIDATION] ⚠️  发现 {len(validation_warnings)} 个警告：")
            for warning in validation_warnings:
                print(f"  - {warning}")
        
        if not validation_errors and not validation_warnings:
            print(f"[VALIDATION] ✅ 数据验证通过，未发现问题")
        
        print(f"[VALIDATION] ========== 验证结束 ==========")
        
        # 如果有严重错误，阻止导入
        if validation_errors:
            print(f"[ERROR] 发现 {len(validation_errors)} 个严重错误，阻止导入到数据库")
            for error in validation_errors:
                print(f"  - {error}")
            # 抛出异常阻止导入
            raise ValueError(f"数据验证失败，发现 {len(validation_errors)} 个严重错误：{'; '.join(validation_errors)}")
        
        # 格式化为数据库格式
        db_data = extractor.format_for_database(extracted_data, patient_id, file_id)
        
        with engine.connect() as connection:
            # 插入影像报告主记录
            query = text("""
                INSERT INTO imaging_reports (
                    patient_id, imaging_type, exam_category, exam_date, exam_time,
                    hospital_name, department, requesting_doctor, performing_doctor,
                    reporting_doctor, reviewing_doctor, exam_items, findings, impression,
                    limitations, severity, follow_up_required, image_quality,
                    data_source, extraction_time
                ) VALUES (
                    :patient_id, :imaging_type, :exam_category, :exam_date, :exam_time,
                    :hospital_name, :department, :requesting_doctor, :performing_doctor,
                    :reporting_doctor, :reviewing_doctor, :exam_items, :findings, :impression,
                    :limitations, :severity, :follow_up_required, :image_quality,
                    :data_source, NOW()
                )
            """)
            
            result = connection.execute(query, db_data)
            imaging_report_id = result.lastrowid
            connection.commit()
            
            print(f"[INFO] 影像报告导入成功 - ID: {imaging_report_id}, 类型: {extracted_data.get('imaging_type')}")
            
            # 插入器官发现详情（如果有）
            organ_findings = extractor.format_organ_findings_for_database(extracted_data, imaging_report_id)
            if organ_findings:
                for organ in organ_findings:
                    if organ.get('organ_name'):  # 只插入有器官名称的记录
                        organ_query = text("""
                            INSERT INTO imaging_organ_findings (
                                imaging_report_id, organ_name, organ_findings,
                                organ_conclusion
                            ) VALUES (
                                :imaging_report_id, :organ_name, :organ_findings,
                                :organ_conclusion
                            )
                        """)
                        connection.execute(organ_query, organ)
                
                connection.commit()
                print(f"[INFO] 器官发现导入成功 - {len(organ_findings)} 条记录")
    
    except Exception as e:
        print(f"[ERROR] 导入影像报告数据失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise


@router.get("/patient/{patient_id}/files")
async def get_patient_files(
    patient_id: int,
    data_category: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取患者的所有上传文件
    
    参数：
    - patient_id: 患者ID
    - data_category: 可选的资料分类筛选
    
    返回：
    - 文件列表
    """
    try:
        with engine.connect() as connection:
            query = text("""
                SELECT * FROM file_uploads 
                WHERE patient_id = :patient_id AND is_deleted = FALSE
            """)
            params = {"patient_id": patient_id}
            
            if data_category:
                query = text("""
                    SELECT * FROM file_uploads 
                    WHERE patient_id = :patient_id AND data_category = :data_category AND is_deleted = FALSE
                """)
                params["data_category"] = data_category
            
            result = connection.execute(query, params)
            files = [dict(row) for row in result]
        
        return JSONResponse(content={
            "success": True,
            "patient_id": patient_id,
            "files": files,
            "total": len(files)
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"获取文件列表失败: {str(e)}"
            },
            status_code=500
        )


@router.delete("/file/{file_id}")
async def delete_file(
    file_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    删除上传的文件（软删除）
    
    参数：
    - file_id: 文件ID
    
    返回：
    - 删除结果
    """
    try:
        with engine.connect() as connection:
            # 软删除
            connection.execute(
                text("""
                    UPDATE file_uploads 
                    SET is_deleted = TRUE, is_active = FALSE 
                    WHERE id = :file_id
                """),
                {"file_id": file_id}
            )
            connection.commit()
        
        return JSONResponse(content={
            "success": True,
            "message": "文件已删除"
        })
        
    except Exception as e:
        return JSONResponse(
            content={
                "success": False,
                "message": f"删除文件失败: {str(e)}"
            },
            status_code=500
        )


@router.get("/patient/{patient_id}/export-csv")
async def export_patient_csv(
    patient_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    导出患者全部数据为CSV格式
    
    参数：
    - patient_id: 患者ID
    
    返回：
    - CSV文件，包含患者的所有数据（基本信息、人口学信息、手术史、检查结果）
    """
    try:
        import io
        import csv
        from fastapi.responses import StreamingResponse
        from datetime import datetime
        
        # 查询患者基本信息
        with engine.connect() as connection:
            # 获取患者基本信息
            patient_query = text("""
                SELECT id, patient_id, patient_name, gender, age, phone, id_number,
                       preliminary_diagnosis, status, create_time, creator, notes
                FROM patients
                WHERE id = :patient_id
            """)
            patient_result = connection.execute(patient_query, {"patient_id": patient_id}).fetchone()
            
            if not patient_result:
                raise HTTPException(
                    status_code=404,
                    detail=f"患者ID {patient_id} 不存在"
                )
            
            # 获取人口学信息
            demographic_query = text("""
                SELECT birth_date, ethnicity, nationality, birth_place,
                       current_address, residence_type, city, province,
                       education_level, occupation, work_unit,
                       marital_status, spouse_name, children_count, family_size,
                       insurance_type, insurance_number, annual_income, economic_status,
                       smoking_status, drinking_status
                FROM demographic_data
                WHERE patient_id = :patient_id
                LIMIT 1
            """)
            demographic_result = connection.execute(demographic_query, {"patient_id": patient_id}).fetchone()
            
            # 获取手术史
            surgery_query = text("""
                SELECT surgery_name, surgery_date, hospital_name, department, surgeon_name,
                       surgery_type, surgery_grade, anesthesia_type, surgery_reason,
                       diagnosis_before_surgery, surgery_outcome, complications,
                       admission_date, discharge_date, hospitalization_days,
                       surgery_cost, total_cost, insurance_reimbursement, self_payment
                FROM surgery_history
                WHERE patient_id = :patient_id
                ORDER BY surgery_date DESC
            """)
            surgery_results = connection.execute(surgery_query, {"patient_id": patient_id}).fetchall()
            
            # 获取检查结果
            lab_query = text("""
                SELECT test_name, test_type, test_date, hospital_name, department, doctor_name,
                       test_result, result_value, reference_range, unit, result_status, is_abnormal,
                       imaging_type, imaging_site, imaging_findings, imaging_conclusion,
                       specimen_type, collection_time, report_time,
                       related_diagnosis, clinical_significance, treatment_suggestion
                FROM lab_results
                WHERE patient_id = :patient_id
                ORDER BY test_date DESC
            """)
            lab_results = connection.execute(lab_query, {"patient_id": patient_id}).fetchall()
            
            # 获取影像报告
            imaging_query = text("""
                SELECT imaging_type, exam_category, exam_date, exam_time, hospital_name, department,
                       requesting_doctor, performing_doctor, reporting_doctor, reviewing_doctor,
                       findings, impression, limitations, severity, follow_up_required, image_quality
                FROM imaging_reports
                WHERE patient_id = :patient_id
                ORDER BY exam_date DESC
            """)
            imaging_results = connection.execute(imaging_query, {"patient_id": patient_id}).fetchall()
        
        # 创建CSV内容
        output = io.StringIO()
        writer = csv.writer(output)
        
        # 写入UTF-8 BOM，确保Excel能正确显示中文
        output.write('\ufeff')
        
        # ============= 患者基本信息 =============
        writer.writerow(['=== 患者基本信息 ==='])
        writer.writerow([])
        writer.writerow(['字段', '值'])
        
        patient_data = {
            '患者ID': patient_result[0],
            '患者编号': patient_result[1],
            '患者姓名': patient_result[2],
            '性别': '男' if patient_result[3] == 'male' else ('女' if patient_result[3] == 'female' else patient_result[3]),
            '年龄': patient_result[4],
            '电话': patient_result[5],
            '身份证号': patient_result[6],
            '初步诊断': patient_result[7],
            '状态': patient_result[8],
            '创建时间': patient_result[9].strftime('%Y-%m-%d %H:%M:%S') if patient_result[9] else '',
            '创建人': patient_result[10],
            '备注': patient_result[11] or ''
        }
        
        for key, value in patient_data.items():
            writer.writerow([key, value])
        
        writer.writerow([])
        
        # ============= 人口学信息 =============
        writer.writerow(['=== 人口学信息 ==='])
        writer.writerow([])
        writer.writerow(['字段', '值'])
        
        if demographic_result:
            demographic_data = {
                '出生日期': demographic_result[0].strftime('%Y-%m-%d') if demographic_result[0] else '',
                '民族': demographic_result[1] or '',
                '国籍': demographic_result[2] or '',
                '出生地': demographic_result[3] or '',
                '现住址': demographic_result[4] or '',
                '居住类型': demographic_result[5] or '',
                '所在城市': demographic_result[6] or '',
                '所在省份': demographic_result[7] or '',
                '教育程度': demographic_result[8] or '',
                '职业': demographic_result[9] or '',
                '工作单位': demographic_result[10] or '',
                '婚姻状况': demographic_result[11] or '',
                '配偶姓名': demographic_result[12] or '',
                '子女数量': demographic_result[13] or 0,
                '家庭人口数': demographic_result[14] or 1,
                '医保类型': demographic_result[15] or '',
                '医保卡号': demographic_result[16] or '',
                '年收入': demographic_result[17] or '',
                '经济状况': demographic_result[18] or '',
                '吸烟状况': demographic_result[19] or '',
                '饮酒状况': demographic_result[20] or ''
            }
            
            for key, value in demographic_data.items():
                writer.writerow([key, value])
        else:
            writer.writerow(['无人口学信息'])
        
        writer.writerow([])
        
        # ============= 手术史 =============
        writer.writerow(['=== 手术史 ==='])
        writer.writerow([])
        
        if surgery_results:
            # 写入表头
            writer.writerow([
                '手术名称', '手术日期', '手术医院', '科室', '主刀医生',
                '手术类型', '手术等级', '麻醉方式', '手术原因',
                '术前诊断', '手术结果', '术后并发症',
                '入院日期', '出院日期', '住院天数',
                '手术费用(元)', '总费用(元)', '医保报销(元)', '自付金额(元)'
            ])
            
            # 写入数据
            for row in surgery_results:
                writer.writerow([
                    row[0] or '',  # 手术名称
                    row[1].strftime('%Y-%m-%d') if row[1] else '',  # 手术日期
                    row[2] or '',  # 手术医院
                    row[3] or '',  # 科室
                    row[4] or '',  # 主刀医生
                    row[5] or '',  # 手术类型
                    row[6] or '',  # 手术等级
                    row[7] or '',  # 麻醉方式
                    row[8] or '',  # 手术原因
                    row[9] or '',  # 术前诊断
                    row[10] or '',  # 手术结果
                    row[11] or '',  # 术后并发症
                    row[12].strftime('%Y-%m-%d') if row[12] else '',  # 入院日期
                    row[13].strftime('%Y-%m-%d') if row[13] else '',  # 出院日期
                    row[14] or 0,  # 住院天数
                    row[15] or '',  # 手术费用
                    row[16] or '',  # 总费用
                    row[17] or '',  # 医保报销
                    row[18] or ''   # 自付金额
                ])
        else:
            writer.writerow(['无手术史记录'])
        
        writer.writerow([])
        
        # ============= 检查结果 =============
        writer.writerow(['=== 检查结果 ==='])
        writer.writerow([])
        
        if lab_results:
            # 写入表头
            writer.writerow([
                '检查名称', '检查类型', '检查日期', '检查医院', '科室', '检查医生',
                '检查结果', '检查数值', '参考范围', '单位', '结果状态', '是否异常', '影像类型', '检查部位', '影像发现', '影像结论',
                '标本类型', '采集时间', '报告时间',
                '相关诊断', '临床意义', '治疗建议'
            ])
            
            # 写入数据
            for row in lab_results:
                writer.writerow([
                    row[0] or '',  # 检查名称
                    row[1] or '',  # 检查类型
                    row[2].strftime('%Y-%m-%d') if row[2] else '',  # 检查日期
                    row[3] or '',  # 检查医院
                    row[4] or '',  # 科室
                    row[5] or '',  # 检查医生
                    row[6] or '',  # 检查结果
                    row[7] or '',  # 检查数值
                    row[8] or '',  # 参考范围
                    row[9] or '',  # 单位
                    row[10] or '',  # 结果状态
                    '是' if row[11] else '否',  # 是否异常
                    row[12] or '',  # 影像类型
                    row[13] or '',  # 检查部位
                    row[14] or '',  # 影像发现
                    row[15] or '',  # 影像结论
                    row[16] or '',  # 标本类型
                    row[17].strftime('%Y-%m-%d %H:%M:%S') if row[17] else '',  # 采集时间
                    row[18].strftime('%Y-%m-%d %H:%M:%S') if row[18] else '',  # 报告时间
                    row[19] or '',  # 相关诊断
                    row[20] or '',  # 临床意义
                    row[21] or ''   # 治疗建议
                ])
        else:
            writer.writerow(['无检查结果记录'])
        
        writer.writerow([])
        
        # ============= 影像报告 =============
        writer.writerow(['=== 影像报告 ==='])
        writer.writerow([])
        
        if imaging_results:
                    # 写入表头
                    writer.writerow([
                        '影像类型', '检查分类', '检查日期', '检查时间', '医院', '科室',
                        '申请医生', '检查医生', '报告医生', '审核医生',
                        '诊断所见', '诊断印象', '限制性说明', '严重程度', '是否需要随访', '图像质量'
                    ])
                    
                    # 写入数据
                    for row in imaging_results:
                        writer.writerow([
                            row[0] or '',  # 影像类型
                            row[1] or '',  # 检查分类
                            row[2].strftime('%Y-%m-%d') if row[2] else '',  # 检查日期
                            row[3].strftime('%H:%M:%S') if row[3] else '',  # 检查时间
                            row[4] or '',  # 医院
                            row[5] or '',  # 科室
                            row[6] or '',  # 申请医生
                            row[7] or '',  # 检查医生
                            row[8] or '',  # 报告医生
                            row[9] or '',  # 审核医生
                            row[10] or '',  # 诊断所见
                            row[11] or '',  # 诊断印象
                            row[12] or '',  # 限制性说明
                            row[13] or '',  # 严重程度
                            '是' if row[14] else '否',  # 是否需要随访
                            row[15] or ''   # 图像质量
                        ])
        else:
            writer.writerow(['无影像报告记录'])        
        # 生成文件名（使用ASCII字符避免编码问题）
        patient_id = patient_result[0]
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        ascii_filename = f"patient_{patient_id}_data_{timestamp}.csv"
        
        # 返回CSV文件
        output.seek(0)
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8-sig')),
            media_type='text/csv; charset=utf-8-sig',
            headers={
                'Content-Disposition': f'attachment; filename="{ascii_filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"导出患者数据失败: {str(e)}"
        )


@router.get("/files/{file_id}/status")
async def get_file_status(
    file_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    获取文件的处理状态和错误信息
    
    参数：
    - file_id: 文件ID
    
    返回：
    - 文件的处理状态、OCR结果和错误信息
    """
    try:
        with engine.connect() as connection:
            # 查询文件信息
            file_query = text("""
                SELECT id, file_name, ocr_status, ocr_error, import_status, import_error,
                       validation_status, data_category, upload_time
                FROM file_uploads
                WHERE id = :file_id
            """)
            file_result = connection.execute(file_query, {"file_id": file_id}).fetchone()
            
            if not file_result:
                raise HTTPException(
                    status_code=404,
                    detail=f"文件ID {file_id} 不存在"
                )
            
            # 构建响应
            result = {
                "success": True,
                "file_id": file_id,
                "file_name": file_result[1],
                "ocr_status": file_result[2],
                "import_status": file_result[4],
                "validation_status": file_result[6],
                "data_category": file_result[7],
                "upload_time": file_result[8].isoformat() if file_result[8] else None
            }
            
            # 添加OCR错误信息
            if file_result[3]:
                result["ocr_error"] = file_result[3]
            
            # 添加导入错误信息
            if file_result[5]:
                result["import_error"] = file_result[5]
            
            # 添加具体的错误原因和改进建议
            if file_result[3]:  # OCR错误
                result["errors"] = [
                    "OCR识别失败，可能的原因：",
                    "  • 图片质量不佳，文字不清晰",
                    "  • 图片包含大量重复内容",
                    "  • 缺少关键的诊断信息",
                    "  • 图片格式不支持或损坏"
                ]
                result["suggestions"] = [
                    "建议：检查原始图片质量",
                    "建议：确保图片包含完整的诊断信息",
                    "建议：使用清晰、高分辨率的图片",
                    "建议：避免上传包含大量无关内容的图片"
                ]
            
            # 如果有导入错误，添加错误详情
            if file_result[5]:  # 导入错误
                if not result.get("errors"):
                    result["errors"] = []
                result["errors"].append(f"数据导入失败：{file_result[5]}")
                
                if not result.get("suggestions"):
                    result["suggestions"] = []
                result["suggestions"].append("建议：检查图片内容是否包含有效的医疗数据")
            
            return result
            
    except HTTPException:
        raise
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=500,
            detail=f"获取文件状态失败: {str(e)}"
        )