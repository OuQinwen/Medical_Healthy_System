"""
配置模块
管理API密钥、模型配置等参数
支持云端API调用
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


class Config:
    """全局配置类"""
    
    # ========== 云端API配置 ==========
    # API密钥（需要用户配置）
    API_KEY: Optional[str] = os.getenv("API_KEY")
    # API基础地址（需要用户配置）
    API_BASE: str = os.getenv("API_BASE", "")
    # OCR视觉模型配置（需要用户配置）
    VISION_MODEL: str = os.getenv("VISION_MODEL", "")
    # 语言模型配置（需要用户配置）
    LLM_MODEL: str = os.getenv("LLM_MODEL", "")
    # 请求超时配置
    VISION_TIMEOUT: int = 300
    LLM_TIMEOUT: int = 120
    
    # ========== 通用配置 ==========
    # 支持的图片格式
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'}
    # 最大重试次数
    MAX_RETRIES: int = 3
    
    @classmethod
    def validate(cls) -> bool:
        """
        验证配置是否完整
        
        Returns:
            bool: 配置是否有效
        """
        if not cls.API_KEY:
            print("错误：未设置API密钥，请在.env文件中配置API_KEY")
            return False
        if not cls.API_BASE:
            print("错误：未设置API基础地址，请在.env文件中配置API_BASE")
            return False
        if not cls.VISION_MODEL:
            print("错误：未设置视觉模型，请在.env文件中配置VISION_MODEL")
            return False
        if not cls.LLM_MODEL:
            print("错误：未设置语言模型，请在.env文件中配置LLM_MODEL")
            return False
        
        print(f"配置验证通过：API({cls.API_BASE}) + OCR({cls.VISION_MODEL}) + LLM({cls.LLM_MODEL})")
        return True
    
    @classmethod
    def get_image_path(cls, path: str) -> Path:
        """
        获取图片路径并验证
        
        Args:
            path: 图片路径字符串
            
        Returns:
            Path: 图片路径对象
            
        Raises:
            FileNotFoundError: 文件不存在
            ValueError: 文件格式不支持
        """
        img_path = Path(path)
        
        if not img_path.exists():
            raise FileNotFoundError(f"图片文件不存在: {path}")
        
        if img_path.suffix.lower() not in cls.SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"不支持的图片格式: {img_path.suffix}")
        
        return img_path