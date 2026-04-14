import os
import json
import subprocess
import sys
import requests
import base64
import fitz
import logging
from PIL import Image
from io import BytesIO
from .file_utils import get_output_path

# 创建日志记录器
logger = logging.getLogger(__name__)

# 导入现有的模块功能
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from ocr_images import process_images
from generate_txt import generate_txt_from_ocr
from generate_epub import generate_epub_from_ocr

def convert_image_to_png(image_path):
    """将图片转换为PNG格式"""
    try:
        # 打开图片
        img = Image.open(image_path)
        
        # 创建一个BytesIO对象
        buffer = BytesIO()
        
        # 将图片保存为PNG格式到buffer
        img.save(buffer, format='PNG')
        
        # 重置buffer的位置到开始
        buffer.seek(0)
        
        # 返回buffer中的数据
        return buffer.getvalue()
    except Exception as e:
        print(f"图片格式转换失败: {e}")
        # 如果转换失败，尝试直接读取原始图片
        try:
            with open(image_path, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"读取原始图片失败: {e}")
            return None

def process_ocr(file_path, model, ollama_url, task_id=None, processing_progress=None):
    """处理OCR任务"""
    logger.info(f"开始处理OCR任务")
    logger.info(f"文件路径: {file_path}")
    logger.info(f"文件是否存在: {os.path.exists(file_path)}")
    logger.info(f"任务ID: {task_id}")
    logger.info(f"模型: {model}")
    logger.info(f"Ollama URL: {ollama_url}")
    
    file_ext = os.path.splitext(file_path)[1].lower()
    logger.info(f"文件扩展名: {file_ext}")
    
    is_pdf = file_ext == ".pdf"
    is_image = file_ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
    
    logger.info(f"是否为PDF: {is_pdf}")
    logger.info(f"是否为图片: {is_image}")
    
    if not is_pdf and not is_image:
        raise Exception("仅支持PDF和图片文件")
    
    # 创建临时输出目录
    temp_output = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'temp_output')
    logger.info(f"临时输出目录: {temp_output}")
    
    # 清理历史临时产物
    if os.path.exists(temp_output):
        logger.info(f"清理历史临时产物: {temp_output}")
        import shutil
        shutil.rmtree(temp_output)
        logger.info(f"历史临时产物清理完成")
    
    # 创建新的临时输出目录
    logger.info(f"创建临时输出目录: {temp_output}")
    os.makedirs(temp_output)
    
    # 直接在这里处理PDF文件，不使用extract_images函数
    try:
        if is_pdf:
            # 提取PDF中的图片
            image_dir = os.path.join(temp_output, 'images')
            logger.info(f"开始提取PDF中的图片到: {image_dir}")
            
            # 更新进度
            if task_id and processing_progress:
                processing_progress[task_id]['progress'] = 15
                processing_progress[task_id]['message'] = '开始提取PDF中的图片...'
            
            # 确保输出目录存在
            if not os.path.exists(image_dir):
                logger.info(f"创建输出目录: {image_dir}")
                os.makedirs(image_dir)
            
            # 打开PDF文件
            logger.info(f"打开PDF文件: {file_path}")
            doc = fitz.open(file_path)
            logger.info(f"PDF文件页数: {len(doc)}")
            
            # 图片计数器
            image_count = 1
            
            # 遍历每一页
            for page_num in range(len(doc)):
                logger.info(f"处理第 {page_num+1} 页")
                page = doc[page_num]
                
                # 获取页面中的图片
                images = page.get_images(full=True)
                logger.info(f"第 {page_num+1} 页有 {len(images)} 张图片")
                
                # 遍历每一张图片
                for img in images:
                    xref = img[0]
                    
                    # 提取图片
                    base_image = doc.extract_image(xref)
                    image_data = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # 生成图片文件名
                    image_filename = f"{image_count}.{image_ext}"
                    image_path = os.path.join(image_dir, image_filename)
                    
                    # 保存图片
                    with open(image_path, "wb") as f:
                        f.write(image_data)
                    
                    logger.info(f"已提取图片: {image_filename}")
                    image_count += 1
            
            doc.close()
            logger.info(f"提取完成，共提取 {image_count-1} 张图片")
            
            # 更新进度
            if task_id and processing_progress:
                processing_progress[task_id]['progress'] = 30
                processing_progress[task_id]['message'] = f'PDF提取完成，共提取 {image_count-1} 张图片，开始OCR识别...'
            
            # 检查图片目录是否存在
            if not os.path.exists(image_dir):
                logger.error(f"图片目录不存在: {image_dir}")
                # 创建一个空的OCR结果
                ocr_output = os.path.join(temp_output, 'ocr_results.json')
                with open(ocr_output, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                logger.info(f"创建空的OCR结果文件: {ocr_output}")
                # 生成TXT文件
                txt_output = get_output_path(file_path, '.txt')
                title = os.path.splitext(os.path.basename(file_path))[0]
                generate_txt_from_ocr(ocr_output, txt_output, title)
                logger.info(f"生成空的TXT文件: {txt_output}")
                # 读取OCR结果
                with open(ocr_output, 'r', encoding='utf-8') as f:
                    ocr_results = json.load(f)
                # 清理临时文件
                if os.path.exists(temp_output):
                    import shutil
                    logger.info(f"清理临时文件: {temp_output}")
                    shutil.rmtree(temp_output)
                    logger.info(f"临时文件清理完成")
                # 返回空结果
                return {
                    'txt_path': txt_output,
                    'ocr_results': ocr_results,
                    'file_name': os.path.basename(file_path)
                }
            
            # 检查目录中是否有图片文件
            image_files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.jpx'))]
            if not image_files:
                logger.error(f"图片目录中没有图片文件: {image_dir}")
                # 创建一个空的OCR结果
                ocr_output = os.path.join(temp_output, 'ocr_results.json')
                with open(ocr_output, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                logger.info(f"创建空的OCR结果文件: {ocr_output}")
                # 生成TXT文件
                txt_output = get_output_path(file_path, '.txt')
                title = os.path.splitext(os.path.basename(file_path))[0]
                generate_txt_from_ocr(ocr_output, txt_output, title)
                logger.info(f"生成空的TXT文件: {txt_output}")
                # 读取OCR结果
                with open(ocr_output, 'r', encoding='utf-8') as f:
                    ocr_results = json.load(f)
                # 清理临时文件
                if os.path.exists(temp_output):
                    import shutil
                    logger.info(f"清理临时文件: {temp_output}")
                    shutil.rmtree(temp_output)
                    logger.info(f"临时文件清理完成")
                # 返回空结果
                return {
                    'txt_path': txt_output,
                    'ocr_results': ocr_results,
                    'file_name': os.path.basename(file_path)
                }
            logger.info(f"图片目录中有 {len(image_files)} 张图片")
            
            # 处理图片目录
            ocr_output = os.path.join(temp_output, 'ocr_results.json')
            logger.info(f"开始处理图片，输出结果到: {ocr_output}")
            
            # 直接在这里处理图片，不使用process_images函数
            logger.info(f"正在处理图片目录: {image_dir}")
            logger.info(f"目录是否存在: {os.path.exists(image_dir)}")
            logger.info(f"目录中的文件数量: {len(image_files)}")
            
            # 打印前10个图片文件
            if image_files:
                logger.info(f"前10个图片文件: {image_files[:10]}")
            
            # 检查是否存在现有结果文件
            results = []
            if os.path.exists(ocr_output):
                try:
                    with open(ocr_output, 'r', encoding='utf-8') as f:
                        results = json.load(f)
                    logger.info(f"发现现有结果文件，已处理 {len(results)} 张图片")
                except Exception as e:
                    logger.error(f"读取现有结果文件时出错: {e}")
                    logger.info("将从头开始处理所有图片")
                    results = []
            else:
                logger.info("未发现现有结果文件，将从头开始处理所有图片")
            
            # 处理所有图片
            logger.info(f"开始处理所有图片，共 {len(image_files)} 张")
            total_images = len(image_files)
            for i, image_file in enumerate(image_files):
                try:
                    # 检查任务是否已停止
                    if task_id and processing_progress and processing_progress[task_id]['status'] == 'stopped':
                        logger.info(f"任务 {task_id} 已停止，退出处理")
                        break
                    
                    # 更新进度
                    if task_id and processing_progress:
                        current_progress = 30 + (i / total_images) * 60
                        processing_progress[task_id]['progress'] = min(current_progress, 90)
                        processing_progress[task_id]['message'] = f'正在处理第 {i+1}/{total_images} 张图片...'
                    
                    image_path = os.path.join(image_dir, image_file)
                    logger.info(f"正在处理第 {i+1}/{len(image_files)} 张图片: {image_file}")
                    logger.info(f"图片路径: {image_path}")
                    logger.info(f"图片是否存在: {os.path.exists(image_path)}")
                    
                    # 检查图片是否存在
                    if not os.path.exists(image_path):
                        logger.error(f"图片不存在: {image_path}")
                        continue
                    
                    # 进行OCR识别
                    logger.info(f"请求接口: {ollama_url}/api/generate")
                    logger.info(f"使用模型: {model}")
                    
                    # 编码图片
                    max_retries = 3
                    retry_delay = 2  # 秒
                    retry_count = 0
                    text = ""
                    success = False
                    
                    while retry_count < max_retries and not success:
                        try:
                            # 将图片转换为PNG格式
                            image_data = convert_image_to_png(image_path)
                            if not image_data:
                                logger.error("图片转换失败，跳过此图片")
                                break
                            
                            base64_image = base64.b64encode(image_data).decode('utf-8')
                            logger.info(f"图片编码完成，大小: {len(base64_image)} 字节")
                            
                            # 构建请求数据
                            data = {
                                "model": model,
                                "prompt": "请详细识别图片中的所有文字，包括标题、正文、注释等所有可见文本，保持原始格式、排版和顺序，不要遗漏任何内容，也不要添加任何解释或额外内容。",
                                "images": [base64_image],
                                "stream": False
                            }
                            logger.info(f"请求数据构建完成")
                            
                            # 发送请求
                            headers = {"Content-Type": "application/json"}
                            response = requests.post(f'{ollama_url}/api/generate', headers=headers, data=json.dumps(data), timeout=60)
                            logger.info(f"请求发送完成，状态码: {response.status_code}")
                            
                            # 处理响应
                            response_data = response.json()
                            logger.info(f"响应处理完成")
                            if 'response' in response_data:
                                text = response_data['response'].strip()
                                logger.info(f"识别结果: {text[:200]}..." if len(text) > 200 else f"识别结果: {text}")
                            else:
                                text = ""
                                logger.info("识别结果为空")
                            
                            success = True
                            logger.info(f"图片处理成功")
                        except Exception as e:
                            retry_count += 1
                            logger.error(f"处理第 {i+1} 张图片时出错 (重试 {retry_count}/{max_retries}): {e}")
                            if retry_count < max_retries:
                                logger.info(f"{retry_delay}秒后重试...")
                                import time
                                time.sleep(retry_delay)
                            else:
                                logger.error(f"已达到最大重试次数，跳过此图片")
                                break
                    
                    results.append({
                        "image": image_file,
                        "text": text
                    })
                    logger.info(f"结果添加到列表")
                    
                    # 保存中间结果，防止意外中断
                    try:
                        with open(ocr_output, 'w', encoding='utf-8') as f:
                            json.dump(results, f, ensure_ascii=False, indent=2)
                        logger.info(f"中间结果保存完成")
                    except Exception as e:
                        logger.error(f"结果保存失败: {e}")
                        continue
                    
                    logger.info(f"已完成第 {i+1} 张图片的识别")
                    logger.info(f"当前已处理 {len(results)} 张图片")
                    
                    # 每次识别完成后休息3秒，避免显卡过热
                    logger.info("识别完成，休息3秒...")
                    import time
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"处理第 {i+1} 张图片时出错: {e}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            logger.info(f"处理完成，共处理 {len(results)} 张图片")
            logger.info(f"结果已保存到: {ocr_output}")
            logger.info(f"图片处理完成")
        else:
            # 处理单个图片
            ocr_output = os.path.join(temp_output, 'ocr_results.json')
            logger.info(f"处理单个图片: {file_path}")
            process_images(file_path, ocr_output, model, ollama_url)
        
        # 生成TXT文件
        txt_output = get_output_path(file_path, '.txt')
        title = os.path.splitext(os.path.basename(file_path))[0]
        logger.info(f"开始生成TXT文件: {txt_output}")
        generate_txt_from_ocr(ocr_output, txt_output, title)
        logger.info(f"TXT文件生成完成")
        
        # 读取OCR结果
        logger.info(f"开始读取OCR结果: {ocr_output}")
        with open(ocr_output, 'r', encoding='utf-8') as f:
            ocr_results = json.load(f)
        logger.info(f"OCR结果读取完成")
        
        # 清理临时文件
        if os.path.exists(temp_output):
            import shutil
            logger.info(f"清理临时文件: {temp_output}")
            shutil.rmtree(temp_output)
            logger.info(f"临时文件清理完成")
        
        return {
            'txt_path': txt_output,
            'ocr_results': ocr_results,
            'file_name': os.path.basename(file_path)
        }
    except Exception as e:
        logger.error(f"OCR处理失败: {e}")
        # 不清理临时文件，便于调试
        logger.info(f"临时文件未清理，路径: {temp_output}")
        raise
