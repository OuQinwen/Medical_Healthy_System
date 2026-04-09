"""
main.py - FastAPI 服务器主文件

功能说明：
- 启动 FastAPI 应用
- 注册 API 路由
- 配置 CORS（跨域资源共享）
- 提供服务器健康检查
- 提供用户认证功能

使用方法：
- 直接运行: python main.py
- 或使用 uvicorn: uvicorn main:app --reload

访问地址：
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/api/health
- 登录接口: http://localhost:8000/api/auth/login
"""

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from DataApi import router as data_router
from auth_routes import router as auth_router
from user_auth import get_current_active_user
import uvicorn
import os
import schedule
import threading
import time
from pathlib import Path

# 创建 FastAPI 应用实例
app = FastAPI(
    title="医学数据融合科研系统 API",
    description="后端 API 服务，处理前端上传的文件和文本数据",
    version="1.0.0"
)

# 配置 CORS（允许前端跨域访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应指定具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册数据 API 路由
app.include_router(data_router)

# 注册用户认证 API 路由
app.include_router(auth_router)

# 注册独立的修改密码路由（为了兼容前端调用）
from auth_routes import change_password
app.post("/api/change-password")(change_password)

# 添加静态文件服务
# 挂载 data 目录，允许访问上传的患者文件
# 使用当前脚本所在目录的 data 文件夹
script_dir = os.path.dirname(os.path.abspath(__file__))
data_dir = os.path.join(script_dir, "data")
if os.path.exists(data_dir):
    app.mount("/data", StaticFiles(directory=data_dir), name="data")
    print(f"[INFO] 静态文件服务已启动: /data -> {data_dir}")
else:
    print(f"[WARNING] data 目录不存在: {data_dir}，静态文件服务未启动")


# 添加全局异常处理器
from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse, JSONResponse
import threading
import time
import schedule

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    """
    处理请求验证错误（422）
    """
    print(f"[ERROR] 请求验证失败: {exc}")
    
    # 尝试获取请求体，但如果已经被消耗则跳过
    try:
        body = await request.body()
        print(f"[ERROR] 请求体: {body.decode('utf-8')}")
    except RuntimeError:
        print(f"[ERROR] 请求体已被消耗")
        body = b""
    
    print(f"[ERROR] 错误详情: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={
            "detail": exc.errors(),
            "body": exc.body if exc.body else "请求体已消耗"
        }
    )


# 请求模型
class ApiKeyConfig(BaseModel):
    """API密钥配置模型"""
    api_key: str
    vision_model: str = "Qwen/Qwen2.5-VL-7B-Instruct"
    llm_model: str = "Qwen/Qwen2.5-32B-Instruct"


class VerifyPasswordRequest(BaseModel):
    """密码验证请求模型"""
    password: str


@app.post("/api/config/siliconflow-api-key")
async def save_siliconflow_api_key(
    config: ApiKeyConfig,
    current_user: str = Depends(get_current_active_user)
):
    """
    保存硅胶流动API密钥配置
    
    参数：
    - api_key: API密钥
    - vision_model: 视觉模型（可选，默认Qwen/Qwen2.5-VL-7B-Instruct）
    - llm_model: 语言模型（可选，默认Qwen/Qwen2.5-32B-Instruct）
    
    需要认证
    """
    try:
        # 获取数据agent目录
        agent_dir = Path(__file__).parent.parent / "数据agent"
        env_file = agent_dir / ".env"
        
        # 读取现有配置
        existing_config = {}
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                existing_config = {}
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_config[key.strip()] = value.strip()
        
        # 更新配置
        existing_config['SILICONFLOW_API_KEY'] = config.api_key
        existing_config['VISION_MODEL'] = config.vision_model
        existing_config['LLM_MODEL'] = config.llm_model
        
        # 写入配置文件
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write("# 环境变量配置\n")
            f.write("# 支持本地模型和硅胶流动云端API\n\n")
            
            # 写入本地模型配置
            f.write("# ========== 本地模型配置 ==========\n")
            f.write("OLLAMA_HOST=" + existing_config.get('OLLAMA_HOST', 'http://localhost:11434') + "\n")
            f.write("OLLAMA_VISION_MODEL=" + existing_config.get('OLLAMA_VISION_MODEL', 'qwen2.5vl:7b') + "\n")
            f.write("LMSTUDIO_HOST=" + existing_config.get('LMSTUDIO_HOST', 'http://localhost:1234') + "\n")
            f.write("LMSTUDIO_MODEL=" + existing_config.get('LMSTUDIO_MODEL', 'qwen2.5:32b') + "\n\n")
            
            # 写入云端API配置
            f.write("# ========== 硅胶流动云端API配置 ==========\n")
            f.write("SILICONFLOW_API_KEY=" + existing_config['SILICONFLOW_API_KEY'] + "\n")
            f.write("VISION_MODEL=" + existing_config['VISION_MODEL'] + "\n")
            f.write("LLM_MODEL=" + existing_config['LLM_MODEL'] + "\n")
        
        return {
            "success": True,
            "message": "API密钥配置保存成功",
            "config": {
                "vision_model": config.vision_model,
                "llm_model": config.llm_model
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"保存API密钥失败: {str(e)}"
        )


@app.get("/api/config/siliconflow-api-key")
async def get_siliconflow_api_key_config(current_user: str = Depends(get_current_active_user)):
    """
    获取硅胶流动API密钥配置（返回脱敏信息）
    
    需要认证
    """
    try:
        # 获取数据agent目录
        agent_dir = Path(__file__).parent.parent / "数据agent"
        env_file = agent_dir / ".env"
        
        config = {
            "has_api_key": False,
            "vision_model": "Qwen/Qwen2.5-VL-7B-Instruct",
            "llm_model": "Qwen/Qwen2.5-32B-Instruct"
        }
        
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        if key == 'SILICONFLOW_API_KEY':
                            config['has_api_key'] = bool(value and value != 'your_siliconflow_api_key_here')
                        elif key == 'VISION_MODEL':
                            config['vision_model'] = value
                        elif key == 'LLM_MODEL':
                            config['llm_model'] = value
        
        return config
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"获取API密钥配置失败: {str(e)}"
        )


@app.get("/")
async def root():
    """
    根路径 - 返回服务信息
    """
    return {
        "service": "医学数据融合科研系统 API",
        "status": "running",
        "version": "1.0.0",
        "description": "后端 API 服务，处理前端上传的文件和文本数据，并调用 agent 服务进行 OCR 和数据提取",
        "endpoints": {
            "api_docs": "/docs",
            "health_check": "/api/health",
            "login": "/api/auth/login",
            "user_info": "/api/auth/me",
            "upload_data": "/api/upload",
            "upload_with_fields": "/api/upload-with-fields",
            "send_message": "/api/message",
            "get_agent_outputs": "/api/agent-output-files"
        },
        "agent_service": {
            "url": "http://localhost:8001",
            "description": "OCR 和数据提取服务",
            "api_docs": "http://localhost:8001/docs"
        }
    }


@app.get("/api/health")
async def health_check():
    """
    健康检查接口
    """
    # 检查 agent 服务器状态
    agent_status = "unknown"
    try:
        import requests
        response = requests.get("http://localhost:8001/health", timeout=5)
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
        "timestamp": "2024-01-01T00:00:00Z"
    }


if __name__ == "__main__":
    # 启动时清理旧文件
    def cleanup_on_startup():
        """启动时清理旧文件"""
        try:
            import time
            from datetime import datetime
            
            # 使用当前脚本所在目录的 uploads 文件夹
            script_dir = os.path.dirname(os.path.abspath(__file__))
            UPLOAD_DIR = os.path.join(script_dir, "uploads")
            days_threshold = 3  # 清理3天前的文件
            time_threshold = time.time() - (days_threshold * 24 * 60 * 60)
            
            upload_path = Path(UPLOAD_DIR)
            
            if not upload_path.exists():
                print("[INFO] uploads 文件夹不存在，跳过清理")
                return
            
            deleted_count = 0
            total_size = 0
            
            for file_path in upload_path.iterdir():
                if file_path.is_file():
                    file_mtime = file_path.stat().st_mtime
                    
                    if file_mtime < time_threshold:
                        try:
                            file_size = file_path.stat().st_size
                            total_size += file_size
                            file_path.unlink()
                            deleted_count += 1
                            print(f"[INFO] 已删除旧文件: {file_path.name} ({datetime.fromtimestamp(file_mtime)})")
                        except Exception as e:
                            print(f"[ERROR] 删除文件失败 {file_path.name}: {str(e)}")
            
            if deleted_count > 0:
                print(f"[INFO] 启动清理完成: 删除了 {deleted_count} 个文件，释放空间 {total_size / 1024 / 1024:.2f} MB")
            else:
                print("[INFO] 启动清理完成: 没有需要清理的文件")
                
        except Exception as e:
            print(f"[ERROR] 启动清理出错: {str(e)}")
    
    # 执行启动清理
    print("[INFO] 正在执行启动清理...")
    cleanup_on_startup()
    
    # 定时清理任务
    def cleanup_old_files():
        """定时清理旧文件"""
        import requests
        try:
            # 调用清理接口
            response = requests.post(
                "http://localhost:8000/api/cleanup/uploads",
                data={"days": 3},  # 清理3天前的文件
                timeout=30
            )
            if response.status_code == 200:
                result = response.json()
                print(f"[INFO] 定时清理完成: {result.get('message', '')}")
            else:
                print(f"[ERROR] 定时清理失败: {response.status_code}")
        except Exception as e:
            print(f"[ERROR] 定时清理出错: {str(e)}")
    
    # 设置定时任务（每天凌晨2点执行）
    schedule.every().day.at("02:00").do(cleanup_old_files)
    
    # 启动后台定时任务线程
    def run_schedule():
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次
    
    schedule_thread = threading.Thread(target=run_schedule, daemon=True)
    schedule_thread.start()
    print("[INFO] 定时清理任务已启动，将在每天凌晨2点执行")
    
    # 启动服务器
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True  # 开发模式下启用热重载
    )