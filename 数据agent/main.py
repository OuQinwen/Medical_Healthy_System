"""
医学数据融合科研系统 - OCR Agent 服务
功能：通过视觉模型识别医学化验单图片，使用LLM提取结构化数据
工作流：图片输入 -> 视觉模型识别 -> LLM数据提取 -> 返回全量数据和指定数据
支持单张图片处理和多张图片批量处理

启动方式：
    python main.py
    或
    uvicorn main:app --host 0.0.0.0 --port 8001 --reload
"""

import sys
from pathlib import Path
from typing import List, Optional
import os
import shutil
from datetime import datetime

# 添加项目根目录到路径
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel

from core.pipeline import OCRPipeline
from core.config import Config

# 创建FastAPI应用
app = FastAPI(
    title="医学OCR信息提取Agent",
    description="基于视觉模型和LLM的医学化验单信息提取服务",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化OCR管道
pipeline = OCRPipeline()

# 文件保存目录
UPLOAD_DIR = ROOT_DIR / "temp_uploads"
OUTPUT_DIR = ROOT_DIR / "output"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)


class ExtractFieldsRequest(BaseModel):
    """提取字段请求模型"""
    fields: Optional[List[str]] = None
    generate_excel: bool = True


@app.get("/")
async def root():
    """根路径 - 返回服务信息"""
    return {
        "service": "医学OCR信息提取Agent",
        "status": "running",
        "version": "1.0.0",
        "model_config": {
            "use_local_models": Config.USE_LOCAL_MODELS,
            "vision_model": Config.OLLAMA_VISION_MODEL if Config.USE_LOCAL_MODELS else Config.VISION_MODEL,
            "llm_model": Config.LMSTUDIO_MODEL if Config.USE_LOCAL_MODELS else Config.LLM_MODEL
        },
        "endpoints": {
            "api_docs": "/docs",
            "health_check": "/health",
            "process_image": "/api/process",
            "batch_process": "/api/batch-process",
            "download_excel": "/api/download/{filename}"
        }
    }


@app.get("/health")
async def health_check():
    """健康检查接口"""
    return {
        "status": "healthy",
        "service": "OCR Agent",
        "timestamp": datetime.now().isoformat()
    }


@app.post("/api/process")
async def process_single_image(
    file: UploadFile = File(...),
    fields: Optional[str] = Form(None),
    generate_excel: bool = Form(True),
    model_type: str = Form("cloud"),
    data_type: str = Form("lab_result")  # 添加资料类型参数，默认为 lab_result
):
    """
    处理单张医学图片
    
    参数：
    - file: 图片文件（必填）
    - fields: 需要提取的字段列表，逗号分隔（可选）
    - generate_excel: 是否生成Excel文件（默认True）
    - model_type: 模型类型（cloud/local），默认为 cloud
    - data_type: 资料类型（可选），可选值：
        - "demographic": 人口学资料
        - "surgery_history": 手术史
        - "lab_result": 检查结果（默认）
        - "general": 其他文件（通用OCR）
    """
    try:
        # 验证文件类型
        if file.content_type not in ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"]:
            raise HTTPException(status_code=400, detail="不支持的文件类型，仅支持图片格式")
        
        # 保存上传的文件
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        file_extension = Path(file.filename).suffix
        temp_filename = f"temp_{timestamp}{file_extension}"
        temp_path = UPLOAD_DIR / temp_filename
        
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # 解析提取字段
        extract_fields = None
        if fields:
            extract_fields = [f.strip() for f in fields.split(",")]
        
        # 执行OCR处理，传递模型类型和资料类型
        result = pipeline.process_image(str(temp_path), extract_fields, generate_excel, model_type, data_type)
        
        # 清理临时文件
        try:
            os.remove(temp_path)
        except:
            pass
        
        # 返回结果
        if result.get("success"):
            response_data = {
                "success": True,
                "message": "图片处理成功",
                "extracted_data": result.get("extracted_data"),
                "full_data_json": result.get("full_data_json"),
                "timestamp": datetime.now().isoformat()
            }
            
            # 如果生成了Excel文件，添加下载信息
            if result.get("excel_path"):
                excel_filename = Path(result["excel_path"]).name
                response_data["excel_filename"] = excel_filename
                response_data["excel_download_url"] = f"/api/download/{excel_filename}"
            
            return JSONResponse(content=response_data)
        else:
            raise HTTPException(status_code=500, detail=result.get("error", "处理失败"))
            
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理失败: {str(e)}")


@app.post("/api/batch-process")
async def batch_process_images(
    files: List[UploadFile] = File(...),
    fields: Optional[str] = Form(None),
    generate_excel: bool = Form(True),
    model_type: str = Form("cloud"),  # 添加模型类型参数，默认为 cloud
    vision_model: Optional[str] = Form(None),  # 添加视觉模型参数
    llm_model: Optional[str] = Form(None),  # 添加语言模型参数
    data_type: str = Form("lab_result")  # 添加资料类型参数，默认为 lab_result
):
    """
    批量处理多张医学图片
    
    参数：
    - files: 图片文件列表（必填，至少1个）
    - fields: 需要提取的字段列表，逗号分隔（可选）
    - generate_excel: 是否生成Excel文件（默认True）
    - model_type: 模型类型（cloud/local），默认为 cloud
    - vision_model: 视觉模型名称（可选，用于云端API）
    - llm_model: 语言模型名称（可选，用于云端API）
    - data_type: 资料类型（可选），可选值：
        - "demographic": 人口学资料
        - "surgery_history": 手术史
        - "lab_result": 检查结果（默认）
        - "general": 其他文件（通用OCR）
    """
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="至少需要上传一个文件")
    
    if len(files) > 10:
        raise HTTPException(status_code=400, detail="批量处理最多支持10个文件")
    
    try:
        # 解析提取字段
        extract_fields = None
        if fields:
            extract_fields = [f.strip() for f in fields.split(",")]
        
        results = []
        success_count = 0
        error_count = 0
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for idx, file in enumerate(files):
            try:
                # 验证文件类型
                if file.content_type not in ["image/jpeg", "image/png", "image/bmp", "image/tiff", "image/webp"]:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": "不支持的文件类型"
                    })
                    error_count += 1
                    continue
                
                # 保存上传的文件
                file_extension = Path(file.filename).suffix
                temp_filename = f"temp_{timestamp}_{idx}{file_extension}"
                temp_path = UPLOAD_DIR / temp_filename
                
                with open(temp_path, "wb") as buffer:
                    content = await file.read()
                    buffer.write(content)
                
                # 如果提供了模型名称，动态更新配置
                if vision_model or llm_model:
                    from core.config import Config
                    from dotenv import load_dotenv
                    
                    # 重新加载环境变量
                    load_dotenv()
                    
                    if vision_model:
                        Config.VISION_MODEL = vision_model
                        print(f"  使用视觉模型: {vision_model}")
                    if llm_model:
                        Config.LLM_MODEL = llm_model
                        print(f"  使用语言模型: {llm_model}")
                    
                    # 重新初始化pipeline以使用新配置
                    from core.pipeline import OCRPipeline
                    global pipeline
                    pipeline = OCRPipeline()
                
                # 执行OCR处理，传递模型类型和资料类型
                result = pipeline.process_image(str(temp_path), extract_fields, generate_excel, model_type, data_type)
                
                # 清理临时文件
                try:
                    os.remove(temp_path)
                except:
                    pass
                
                if result.get("success"):
                    file_result = {
                        "filename": file.filename,
                        "success": True,
                        "extracted_data": result.get("extracted_data"),
                        "full_data_json": result.get("full_data_json")
                    }
                    
                    if result.get("excel_path"):
                        excel_filename = Path(result["excel_path"]).name
                        file_result["excel_filename"] = excel_filename
                        file_result["excel_download_url"] = f"/api/download/{excel_filename}"
                    
                    results.append(file_result)
                    success_count += 1
                else:
                    results.append({
                        "filename": file.filename,
                        "success": False,
                        "error": result.get("error", "处理失败")
                    })
                    error_count += 1
                    
            except Exception as e:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": str(e)
                })
                error_count += 1
        
        return JSONResponse(content={
            "success": True,
            "message": f"批量处理完成，成功 {success_count} 个，失败 {error_count} 个",
            "total_files": len(files),
            "success_count": success_count,
            "error_count": error_count,
            "results": results,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量处理失败: {str(e)}")


@app.get("/api/download/{filename}")
async def download_excel(filename: str):
    """
    下载生成的Excel文件
    
    参数：
    - filename: Excel文件名
    """
    try:
        file_path = OUTPUT_DIR / filename
        
        if not file_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=str(file_path),
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@app.get("/api/output-files")
async def list_output_files():
    """列出所有输出的Excel文件"""
    try:
        files = []
        for file_path in OUTPUT_DIR.glob("*.xlsx"):
            files.append({
                "filename": file_path.name,
                "size": file_path.stat().st_size,
                "created_time": datetime.fromtimestamp(file_path.stat().st_ctime).isoformat(),
                "download_url": f"/api/download/{file_path.name}"
            })
        
        return JSONResponse(content={
            "success": True,
            "files": sorted(files, key=lambda x: x["created_time"], reverse=True)
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取文件列表失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    print("=" * 60)
    print("医学OCR信息提取Agent服务")
    print("=" * 60)
    print(f"服务地址: http://localhost:8001")
    print(f"API文档: http://localhost:8001/docs")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=False
    )