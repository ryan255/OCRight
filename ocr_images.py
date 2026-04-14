import requests
import base64
import os
import json
import sys

# 设置输出编码为utf-8
sys.stdout.reconfigure(encoding='utf-8')

def encode_image(image_path):
    """将图片编码为base64格式"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def ocr_image(image_path, model, ollama_url="http://localhost:11434"):
    """使用ollama API对图片进行OCR识别"""
    try:
        # 编码图片
        base64_image = encode_image(image_path)
        
        # 构建请求数据
        data = {
            "model": model,
            "prompt": "请详细识别图片中的所有文字，包括标题、正文、注释等所有可见文本，保持原始格式、排版和顺序，不要遗漏任何内容，也不要添加任何解释或额外内容。",
            "images": [base64_image],
            "stream": False
        }
        
        # 打印请求接口
        print(f"请求接口: {ollama_url}/api/generate")
        print(f"使用模型: {model}")
        
        # 发送请求
        headers = {"Content-Type": "application/json"}
        response = requests.post(f'{ollama_url}/api/generate', headers=headers, data=json.dumps(data))
        
        # 处理响应
        response_data = response.json()
        if 'response' in response_data:
            return response_data['response'].strip()
        else:
            return ""
    except Exception as e:
        print(f"OCR识别失败: {e}")
        return ""

def process_images(input_dir, output_file, model, ollama_url="http://localhost:11434"):
    """按顺序处理目录中的所有图片并保存识别结果"""
    # 检查input_dir是否是文件
    if os.path.isfile(input_dir):
        # 处理单个图片文件
        print(f"处理单个图片文件: {input_dir}")
        
        # 检查是否存在现有结果文件
        results = []
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                print(f"发现现有结果文件，已处理 {len(results)} 张图片")
            except Exception as e:
                print(f"读取现有结果文件时出错: {e}")
                print("将从头开始处理图片")
                results = []
        else:
            print("未发现现有结果文件，将从头开始处理图片")
        
        try:
            image_file = os.path.basename(input_dir)
            print(f"\n正在处理图片: {image_file}")
            
            # 进行OCR识别
            text = ocr_image(input_dir, model, ollama_url)
            results.append({
                "image": image_file,
                "text": text
            })
            
            # 保存结果
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"已完成图片的识别")
            print(f"识别结果: {text[:200]}..." if len(text) > 200 else f"识别结果: {text}")
        except Exception as e:
            print(f"处理图片时出错: {e}")
    else:
        # 处理图片目录
        # 获取目录中的所有图片文件并按数字顺序排序
        print(f"正在检查目录: {input_dir}")
        print(f"目录是否存在: {os.path.exists(input_dir)}")
        
        if os.path.exists(input_dir):
            all_files = os.listdir(input_dir)
            print(f"目录中的文件数量: {len(all_files)}")
            
            # 打印前10个文件
            if all_files:
                print(f"前10个文件: {all_files[:10]}")
            
            image_files = []
            for file in all_files:
                # 打印每个文件的扩展名
                ext = os.path.splitext(file)[1].lower()
                print(f"检查文件: {file}, 扩展名: {ext}")
                # 直接使用.endswith方法，不区分大小写
                if file.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.jpx')):
                    image_files.append(file)
            
            # 按数字顺序排序
            def sort_key(filename):
                # 提取文件名中的数字部分
                import re
                match = re.search(r'\d+', filename)
                if match:
                    return int(match.group())
                return 0
            
            image_files.sort(key=sort_key)
            total_images = len(image_files)
            print(f"发现 {total_images} 张图片")
            
            # 打印发现的图片文件
            if image_files:
                print(f"发现的图片文件: {image_files}")
            else:
                # 打印所有文件，看看为什么没有匹配到
                print(f"所有文件: {all_files}")
        else:
            print("目录不存在")
            image_files = []
            total_images = 0
            print(f"发现 {total_images} 张图片")
        
        # 检查是否存在现有结果文件
        results = []
        start_index = 0
        
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r', encoding='utf-8') as f:
                    results = json.load(f)
                
                # 确定已处理的图片数量
                processed_images = [item['image'] for item in results]
                start_index = len(processed_images)
                print(f"发现现有结果文件，已处理 {start_index} 张图片")
                print(f"将从第 {start_index + 1} 张图片开始继续处理")
            except Exception as e:
                print(f"读取现有结果文件时出错: {e}")
                print("将从头开始处理所有图片")
                results = []
                start_index = 0
        else:
            print("未发现现有结果文件，将从头开始处理所有图片")
        
        # 处理剩余的图片
        for i in range(start_index, total_images):
            try:
                image_file = image_files[i]
                image_path = os.path.join(input_dir, image_file)
                print(f"\n正在处理第 {i+1}/{total_images} 张图片: {image_file}")
                
                # 进行OCR识别
                text = ocr_image(image_path, model, ollama_url)
                results.append({
                    "image": image_file,
                    "text": text
                })
                
                # 保存中间结果，防止意外中断
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                
                print(f"已完成第 {i+1} 张图片的识别")
                print(f"当前已处理 {len(results)} 张图片")
                print(f"识别结果: {text[:200]}..." if len(text) > 200 else f"识别结果: {text}")
            except Exception as e:
                print(f"处理第 {i+1} 张图片时出错: {e}")
                continue
    
    print(f"\n处理完成，共处理 {len(results)} 张图片")
    print(f"结果已保存到: {output_file}")
    
    return results

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="使用ollama API对图片进行OCR识别")
    parser.add_argument("--input", "-i", default="output_images", help="输入图片目录，默认: output_images")
    parser.add_argument("--output", "-o", default="ocr_results.json", help="输出结果文件，默认: ocr_results.json")
    parser.add_argument("--model", "-m", default="huihui_ai/qwen3.5-abliterated:2B", help="使用的模型，默认: huihui_ai/qwen3.5-abliterated:2B")
    parser.add_argument("--ollama-url", "-u", default="http://localhost:11434", help="Ollama服务地址，默认: http://localhost:11434")
    
    args = parser.parse_args()
    
    print(f"开始处理图片目录: {args.input}")
    print(f"使用模型: {args.model}")
    print(f"Ollama服务地址: {args.ollama_url}")
    
    results = process_images(args.input, args.output, args.model, args.ollama_url)
    
    print(f"\n处理完成，共处理 {len(results)} 张图片")
    print(f"识别结果已保存到: {args.output}")
