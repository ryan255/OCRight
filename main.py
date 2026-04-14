import os
import sys
import subprocess
import json
import requests

# 设置输出编码为utf-8
sys.stdout.reconfigure(encoding='utf-8')

def get_user_input(prompt):
    """获取用户输入"""
    try:
        return input(prompt).strip()
    except KeyboardInterrupt:
        print("\n操作被用户中断")
        sys.exit(0)

def extract_images_from_pdf(pdf_path, output_dir):
    """从PDF中提取图片"""
    print(f"开始从PDF中提取图片: {pdf_path}")
    
    # 图片保存目录
    image_dir = os.path.join(output_dir, "output_images")
    
    # 调用extract_pdf_images.py脚本，指定输出目录
    result = subprocess.run([
        sys.executable, "extract_pdf_images.py", pdf_path, "--output", image_dir
    ], capture_output=True, text=True, encoding='utf-8')
    
    if result.returncode == 0:
        print(result.stdout)
        print(f"提取完成，图片保存在: {os.path.abspath(image_dir)}")
        return image_dir
    else:
        print(f"提取图片失败: {result.stderr}")
        return None

def check_ollama_service(url="http://localhost:11434"):
    """检查ollama服务是否运行"""
    try:
        response = requests.get(f'{url}/api/tags', timeout=5)
        if response.status_code == 200:
            return True, url
        else:
            return False, None
    except Exception:
        return False, None

def get_ollama_models(ollama_url):
    """获取ollama中的模型列表"""
    try:
        response = requests.get(f'{ollama_url}/api/tags')
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            return [model.get('name') for model in models]
        else:
            return []
    except Exception:
        return []

def perform_ocr(image_input, output_file, model, ollama_url, is_single_image=False):
    """进行OCR识别"""
    print(f"开始进行OCR识别，使用模型: {model}")
    print(f"使用Ollama服务地址: {ollama_url}")
    
    if is_single_image:
        # 处理单个图片文件
        print(f"正在识别图片: {image_input}")
        
        # 调用ocr_images.py脚本处理单个图片
        result = subprocess.run([
            sys.executable, "ocr_images.py",
            "--input", image_input,
            "--output", output_file,
            "--model", model,
            "--ollama-url", ollama_url
        ], text=True, encoding='utf-8')
    else:
        # 处理图片目录
        result = subprocess.run([
            sys.executable, "ocr_images.py",
            "--input", image_input,
            "--output", output_file,
            "--model", model,
            "--ollama-url", ollama_url
        ], text=True, encoding='utf-8')
    
    if result.returncode == 0:
        return True
    else:
        return False

def generate_txt(ocr_results_file, title):
    """生成TXT文件"""
    print(f"开始生成TXT文件")
    
    # 调用generate_txt.py脚本，实时打印输出
    result = subprocess.run([
        sys.executable, "generate_txt.py",
        "--input", ocr_results_file,
        "--title", title
    ], text=True, encoding='utf-8')
    
    if result.returncode == 0:
        # 提取输出中的文件路径
        output_file = os.path.splitext(ocr_results_file)[0] + ".txt"
        print(f"任务完成，输出文件：{os.path.abspath(output_file)}")
        return True
    else:
        return False

def main():
    """主函数"""
    print("========================================")
    print("OCRight - PDF和图片OCR识别工具")
    print("========================================")
    
    # 第一步：获取文件路径
    print("\n第一步：请输入PDF或图片文件路径，或直接拖放文件到对话框")
    file_path = get_user_input("文件路径: ")
    
    if not file_path:
        print("错误：未输入文件路径")
        return
    
    if not os.path.exists(file_path):
        print(f"错误：文件不存在: {file_path}")
        return
    
    # 检查文件类型
    file_ext = os.path.splitext(file_path)[1].lower()
    is_pdf = file_ext == ".pdf"
    is_image = file_ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif"]
    
    if not is_pdf and not is_image:
        print("错误：仅支持PDF和图片文件")
        return
    
    if is_pdf:
        # PDF处理流程
        # 在PDF同级创建输出目录
        pdf_dir = os.path.dirname(file_path)
        pdf_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = os.path.join(pdf_dir, f"{pdf_name}_output")
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"\n输出目录已创建: {os.path.abspath(output_dir)}")
        
        # 提取图片
        image_dir = extract_images_from_pdf(file_path, output_dir)
        if not image_dir:
            return
    else:
        # 图片处理流程
        # 在图片同级创建输出目录
        image_dir = os.path.dirname(file_path)
        image_name = os.path.splitext(os.path.basename(file_path))[0]
        output_dir = os.path.join(image_dir, f"{image_name}_output")
        
        # 确保输出目录存在
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        print(f"\n输出目录已创建: {os.path.abspath(output_dir)}")
        
        # 直接使用输入的图片路径
        image_file = file_path
    
    # 第二步：询问是否需要进行OCR转文字（仅PDF文件需要询问）
    if is_pdf:
        print("\n第二步：是否需要进行OCR转文字")
        print("1. 是 (默认)")
        print("2. 否")
        ocr_choice = get_user_input("请选择 (1/2): ")
        
        # 默认选择是
        if not ocr_choice:
            ocr_choice = "1"
        
        if ocr_choice == "2":
            print("退出对话框")
            return
        
        if ocr_choice != "1":
            print("错误：无效选择")
            return
    else:
        # 图片文件直接进行OCR识别
        print("\n第二步：直接进行OCR识别")
    
    # 询问用户是使用本地ollama还是手动输入ollama地址
    print("\n请选择ollama服务方式:")
    print("1. 使用本地ollama (http://localhost:11434) (默认)")
    print("2. 手动输入ollama地址和端口")
    ollama_choice = get_user_input("请选择 (1/2): ")
    
    # 默认选择使用本地ollama
    if not ollama_choice:
        ollama_choice = "1"
    
    if ollama_choice == "1":
        # 测试本地ollama连接
        print("\n正在测试本地ollama服务...")
        ollama_available, ollama_url = check_ollama_service()
        
        if not ollama_available:
            print("未找到本地ollama服务，请输入ollama地址和端口")
            ollama_url = get_user_input("Ollama地址 (例如: http://localhost:11434): ")
            if not ollama_url:
                print("错误：未输入ollama地址")
                return
            # 测试用户输入的ollama地址
            print(f"\n正在测试ollama服务: {ollama_url}...")
            ollama_available, ollama_url = check_ollama_service(ollama_url)
            if not ollama_available:
                print("无法连接到指定的ollama服务")
                return
    elif ollama_choice == "2":
        # 手动输入ollama地址
        ollama_url = get_user_input("Ollama地址 (例如: http://localhost:11434): ")
        if not ollama_url:
            print("错误：未输入ollama地址")
            return
        # 测试用户输入的ollama地址
        print(f"\n正在测试ollama服务: {ollama_url}...")
        ollama_available, ollama_url = check_ollama_service(ollama_url)
        if not ollama_available:
            print("无法连接到指定的ollama服务")
            return
    else:
        print("错误：无效选择")
        return
    
    # 获取可用模型
    print(f"\n正在获取ollama模型列表...")
    models = get_ollama_models(ollama_url)
    
    if not models:
        print(f"错误：无法获取模型列表，请检查ollama服务是否运行")
        return
    
    # 引导用户选择模型
    print("\n可用模型:")
    for i, model in enumerate(models):
        print(f"{i+1}. {model}" + (" (默认)" if i == 0 else ""))
    
    model_choice = get_user_input("请选择模型编号 (默认 1): ")
    if not model_choice:
        model_choice = "1"
    
    try:
        model_index = int(model_choice) - 1
        if model_index < 0 or model_index >= len(models):
            print("错误：无效的模型编号")
            return
        selected_model = models[model_index]
    except ValueError:
        print("错误：无效的输入")
        return
    
    # 第三步：进行OCR识别
    # OCR结果文件保存在新创建的输出目录中
    ocr_output = os.path.join(output_dir, "ocr_results.json")
    print(f"\n第三步：开始进行OCR识别，使用模型: {selected_model}")
    
    if is_pdf:
        if perform_ocr(image_dir, ocr_output, selected_model, ollama_url, is_single_image=False):
            # 生成TXT文件
            title = os.path.splitext(os.path.basename(file_path))[0]
            generate_txt(ocr_output, title)
    else:
        if perform_ocr(image_file, ocr_output, selected_model, ollama_url, is_single_image=True):
            # 生成TXT文件
            title = os.path.splitext(os.path.basename(file_path))[0]
            generate_txt(ocr_output, title)
    
    # 等待用户按回车键退出
    print("\n请按回车键退出对话框")
    get_user_input("")

if __name__ == "__main__":
    main()
