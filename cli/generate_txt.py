import json
import os
import sys

# 设置输出编码为utf-8
sys.stdout.reconfigure(encoding='utf-8')

def generate_txt_from_ocr(ocr_results_file, output_txt, title="PDF OCR结果"):
    """根据OCR识别结果生成txt文件"""
    # 读取OCR识别结果
    with open(ocr_results_file, 'r', encoding='utf-8') as f:
        ocr_results = json.load(f)
    
    # 生成txt内容
    txt_content = f"{title}\n\n"
    
    for i, result in enumerate(ocr_results):
        text = result['text']
        # 直接拼接文本内容，不添加标题和分隔符
        txt_content += f"{text}\n\n"
    
    # 保存txt文件
    with open(output_txt, 'w', encoding='utf-8') as f:
        f.write(txt_content)
    
    print(f"TXT文件已生成: {output_txt}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="根据OCR识别结果生成txt文件")
    parser.add_argument("--input", "-i", default="ocr_results.json", help="OCR识别结果文件，默认: ocr_results.json")
    parser.add_argument("--output", "-o", default="output.txt", help="输出txt文件，默认: output.txt")
    parser.add_argument("--title", "-t", default="PDF OCR结果", help="文件标题，默认: PDF OCR结果")
    
    args = parser.parse_args()
    
    # 如果未指定输出文件名，自动使用输入文件的文件名（去掉.json后缀）加上.txt，并保存在同一目录
    if args.output == "output.txt":
        import os
        input_dir = os.path.dirname(args.input)
        base_name = os.path.splitext(os.path.basename(args.input))[0]
        args.output = os.path.join(input_dir, f"{base_name}.txt")
    
    print(f"开始生成TXT文件...")
    print(f"输入文件: {args.input}")
    print(f"输出文件: {args.output}")
    print(f"标题: {args.title}")
    
    generate_txt_from_ocr(args.input, args.output, args.title)
