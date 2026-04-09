"""
工作流管道模块
协调视觉OCR和LLM提取的完整工作流
"""

from typing import Dict, List, Optional

from .vision_ocr import VisionOCR
from .llm_extractor import LLMExtractor
from .excel_generator import ExcelGenerator
from .config import Config


class OCRPipeline:
    """OCR工作流管道"""
    
    def __init__(self):
        """初始化工作流管道"""
        self.vision_ocr = VisionOCR()
        self.llm_extractor = LLMExtractor()
        self.excel_generator = ExcelGenerator()
        
        # 验证配置
        if not Config.validate():
            print("警告：API密钥未配置，请设置环境变量 QWEN_VISION_API_KEY 和 QWEN_LLM_API_KEY")
    
    def process_image(
        self, 
        image_path: str, 
        extract_fields: Optional[List[str]] = None,
        generate_excel: bool = True,
        model_type: str = "cloud",
        data_type: str = "lab_result"
    ) -> Dict:
        """
        处理医学图片，执行完整的OCR和数据提取工作流
        
        工作流：
        1. 使用视觉模型识别图片，获取全量文本
        2. 使用LLM从全量文本中提取指定字段的数据
        3. 生成全量数据的JSON格式
        4. 生成Excel文件（可选）
        
        Args:
            image_path: 医学图片路径
            extract_fields: 需要提取的字段列表，如果为None则提取所有字段
            generate_excel: 是否生成Excel文件，默认为True
            model_type: 模型类型（cloud/local），默认为 cloud
            data_type: 资料类型，可选值：
                - "demographic": 人口学资料
                - "surgery_history": 手术史
                - "lab_result": 检查结果（默认）
                - "general": 其他文件（通用OCR）
            
        Returns:
            Dict: 处理结果
                - success: 是否成功
                - extracted_data: 提取的字段数据（JSON）
                - full_data_json: 全量数据（JSON）
                - excel_path: Excel文件路径（如果生成）
                - error: 错误信息（如果有）
        """
        print(f"\n开始处理图片: {image_path}")
        print(f"使用的模型类型: {model_type}")
        print(f"资料类型: {data_type}")
        print("-" * 60)
        
        # 步骤1: 视觉OCR识别
        print("[1/3] 正在使用视觉模型识别图片...")
        print("  提示：视觉模型处理图片需要较长时间，请耐心等待（可能需要1-3分钟）")
        # 传递模型类型给 vision_ocr
        ocr_result = self.vision_ocr.extract_text(image_path, model_type)
        
        if not ocr_result.get('success'):
            print(f"  ✗ OCR识别失败: {ocr_result.get('error')}")
            return {
                'success': False,
                'error': f"OCR识别失败: {ocr_result.get('error')}"
            }
        
        full_text = ocr_result['full_text']
        print(f"  ✓ OCR识别成功，共识别 {len(full_text)} 个字符")
        
        # 步骤2: LLM数据提取
        print("[2/3] 正在使用LLM提取结构化数据...")
        print("  提示：LLM分析文本需要一些时间...")
        # 传递模型类型和资料类型给 llm_extractor
        extraction_result = self.llm_extractor.extract_fields(full_text, extract_fields, model_type, data_type)
        
        extracted_data = None
        if extraction_result.get('success'):
            extracted_data = extraction_result['extracted_data']
            print(f"  ✓ 数据提取成功，共提取 {len(extracted_data)} 个字段")
        else:
            print(f"  ✗ 数据提取失败: {extraction_result.get('error')}")
        
        # 步骤3: 生成全量数据JSON和Excel
        print("[3/3] 正在生成全量数据格式...")
        full_data_json = self.excel_generator.generate_full_data_json(full_text)
        excel_path = None
        
        if generate_excel:
            try:
                excel_path = self.excel_generator.generate_excel(full_text)
                print(f"  ✓ Excel文件生成成功: {excel_path}")
            except Exception as e:
                import traceback
                print(f"  ✗ Excel文件生成失败: {str(e)}")
                print(f"  详细错误: {traceback.format_exc()}")
        
        # 返回完整结果
        result = {
            'success': True,
            'extracted_data': extracted_data,
            'full_data_json': full_data_json
        }
        
        if excel_path:
            result['excel_path'] = excel_path
        
        if extraction_result.get('warning'):
            result['warning'] = extraction_result.get('warning')
        
        return result
