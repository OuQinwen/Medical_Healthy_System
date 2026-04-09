"""
视觉OCR模块
支持使用Ollama本地视觉模型或硅胶流动云端API识别医学化验单图片
"""

import base64
from typing import Dict
import requests

from .config import Config


class VisionOCR:
    """视觉OCR识别器"""
    
    def __init__(self):
        """初始化OCR识别器"""
        self.use_cloud = Config.USE_CLOUD_MODELS
        
        # 本地Ollama配置
        self.ollama_host = Config.OLLAMA_HOST
        self.ollama_model = Config.OLLAMA_VISION_MODEL
        self.ollama_timeout = Config.OLLAMA_TIMEOUT
        
        # 硅胶流动云端API配置
        self.api_key = Config.SILICONFLOW_API_KEY
        self.api_base = Config.SILICONFLOW_API_BASE
        self.model = Config.VISION_MODEL
        self.timeout = Config.VISION_TIMEOUT
    
    def encode_image(self, image_path: str) -> str:
        """
        将图片编码为base64格式
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            str: base64编码的图片字符串
        """
        import os
        
        # 检查文件是否存在
        if not os.path.exists(image_path):
            raise FileNotFoundError(f'图片文件不存在: {image_path}')
        
        # 检查文件大小
        file_size = os.path.getsize(image_path)
        if file_size == 0:
            raise ValueError(f'图片文件为空: {image_path}')
        
        print(f"  读取图片文件: {image_path} (大小: {file_size} 字节)")
        
        try:
            with open(image_path, 'rb') as f:
                image_data = f.read()
                print(f"  读取到 {len(image_data)} 字节数据")
                
                # 使用标准 base64 编码，确保无换行
                base64_str = base64.b64encode(image_data).decode('utf-8')
                # 移除所有可能的空白字符
                result = base64_str.strip()
                
                print(f"  Base64 编码完成，长度: {len(result)} 字符")
                return result
        except Exception as e:
            raise RuntimeError(f'读取图片文件失败: {str(e)}')
    
    def _call_ollama_api(self, image_path: str) -> Dict:
        """
        调用本地Ollama视觉API
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Dict: API响应结果
        """
        headers = {
            'Content-Type': 'application/json'
        }
        
        # 编码图片 - Ollama 需要纯 base64 字符串
        base64_image = self.encode_image(image_path)
        
        # 简单验证：检查是否为空
        if not base64_image or len(base64_image) < 100:
            raise ValueError(f'Base64 编码异常，长度过短: {len(base64_image)}')
        
        prompt = f'请识别这张医学化验单的所有文字内容。按行输出，保持表格结构。'
        
        payload = {
            'model': self.ollama_model,
            'messages': [
                {
                    'role': 'user',
                    'content': prompt,
                    'images': [base64_image]
                }
            ],
            'stream': False,
            'options': {
                'num_predict': 4096,
                'temperature': 0.3
            }
        }
        
        print(f"  正在发送请求到 Ollama: {self.ollama_host}")
        print(f"  使用模型: {self.ollama_model}")
        print(f"  图片 base64 长度: {len(base64_image)} 字符")
        
        response = requests.post(
            f"{self.ollama_host}/api/chat",
            headers=headers,
            json=payload,
            timeout=self.ollama_timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def _call_cloud_api(self, image_path: str) -> Dict:
        """
        调用硅胶流动云端视觉API
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            Dict: API响应结果
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # 编码图片
        base64_image = self.encode_image(image_path)
        
        payload = {
            'model': self.model,
            'messages': [{
                'role': 'user',
                'content': [
                    {
                        'type': 'image_url',
                        'image_url': {
                            'url': f'data:image/jpeg;base64,{base64_image}'
                        }
                    },
                    {
                        'type': 'text',
                        'text': '请识别这张医学化验单的所有文字内容。按行输出，保持表格结构。'
                    }
                ]
            }],
            'stream': False,
            'max_tokens': 4096,
            'temperature': 0.3
        }
        
        print(f"  正在发送请求到硅胶流动API: {self.api_base}")
        print(f"  使用模型: {self.model}")
        print(f"  图片 base64 长度: {len(base64_image)} 字符")
        
        response = requests.post(
            f"{self.api_base}/chat/completions",
            headers=headers,
            json=payload,
            timeout=self.timeout
        )
        
        response.raise_for_status()
        return response.json()
    
    def extract_text(self, image_path: str, model_type: str = None) -> Dict:
        """
        从医学图片中提取全量文本信息
        
        Args:
            image_path: 医学化验单图片路径
            model_type: 模型类型（cloud/local），如果为None则使用配置中的默认模式
        
        Returns:
            Dict: 包含提取结果的字典
                - success: 是否成功
                - full_text: 提取的全量文本
                - error: 错误信息（如果有）
        """
        try:
            # 验证图片路径
            Config.get_image_path(image_path)
            
            # 确定使用哪种API
            if model_type == "local":
                use_cloud = False
            elif model_type == "cloud":
                use_cloud = True
            else:
                use_cloud = self.use_cloud
            
            # 根据模型类型选择 API
            if use_cloud:
                print(f"  使用云端硅胶流动API: {self.model}")
                result = self._call_cloud_api(image_path)
                # 云API格式: choices[0].message.content
                if 'choices' in result and len(result['choices']) > 0:
                    full_text = result['choices'][0]['message']['content']
                    return {
                        'success': True,
                        'full_text': full_text
                    }
                else:
                    return {
                        'success': False,
                        'error': '云端API返回格式异常'
                    }
            else:
                print(f"  使用本地Ollama模型: {self.ollama_model}")
                result = self._call_ollama_api(image_path)
                # Ollama格式: message.content
                if 'message' in result and 'content' in result['message']:
                    full_text = result['message']['content']
                    return {
                        'success': True,
                        'full_text': full_text
                    }
                else:
                    return {
                        'success': False,
                        'error': 'Ollama返回格式异常'
                    }
                
        except FileNotFoundError as e:
            return {
                'success': False,
                'error': f'文件错误: {str(e)}'
            }
        except ValueError as e:
            return {
                'success': False,
                'error': f'格式错误: {str(e)}'
            }
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