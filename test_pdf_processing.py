import os
import sys
import json
import requests
import base64
import fitz

# 设置输出编码为utf-8
sys.stdout.reconfigure(encoding='utf-8')

def test_pdf_processing():
    """测试PDF处理功能"""
    # 测试PDF文件路径
    pdf_path = r"D:\project\TRAE\OCRight\test.pdf"  # 替换为你的测试PDF文件路径
    
    # 检查PDF文件是否存在
    if not os.path.exists(pdf_path):
        print(f"PDF文件不存在: {pdf_path}")
        return
    
    # 创建临时输出目录
    temp_output = os.path.join(os.path.dirname(__file__), 'temp_test')
    if not os.path.exists(temp_output):
        os.makedirs(temp_output)
    
    try:
        # 提取PDF中的图片
        image_dir = os.path.join(temp_output, 'images')
        if not os.path.exists(image_dir):
            os.makedirs(image_dir)
        
        print(f"开始提取PDF中的图片到: {image_dir}")
        
        # 打开PDF文件
        print(f"打开PDF文件: {pdf_path}")
        doc = fitz.open(pdf_path)
        print(f"PDF文件页数: {len(doc)}")
        
        # 图片计数器
        image_count = 1
        
        # 遍历每一页
        for page_num in range(len(doc)):
            print(f"处理第 {page_num+1} 页")
            page = doc[page_num]
            
            # 获取页面中的图片
            images = page.get_images(full=True)
            print(f"第 {page_num+1} 页有 {len(images)} 张图片")
            
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
                
                print(f"已提取图片: {image_filename}")
                image_count += 1
        
        doc.close()
        print(f"\n提取完成，共提取 {image_count-1} 张图片")
        
        # 检查图片目录是否存在
        if not os.path.exists(image_dir):
            print(f"图片目录不存在: {image_dir}")
            return
        
        # 检查目录中是否有图片文件
        image_files = [f for f in os.listdir(image_dir) if f.endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif', '.jpx'))]
        if not image_files:
            print(f"图片目录中没有图片文件: {image_dir}")
            return
        print(f"图片目录中有 {len(image_files)} 张图片")
        
        # 打印前10个图片文件
        if image_files:
            print(f"前10个图片文件: {image_files[:10]}")
        
        # 处理图片目录
        ocr_output = os.path.join(temp_output, 'ocr_results.json')
        print(f"开始处理图片，输出结果到: {ocr_output}")
        
        # 测试：只处理前2张图片
        print(f"开始处理图片，共 {len(image_files)} 张，仅测试前2张")
        test_images = image_files[:2]
        results = []
        
        for i, image_file in enumerate(test_images):
            try:
                image_path = os.path.join(image_dir, image_file)
                print(f"\n正在处理第 {i+1}/{len(test_images)} 张图片: {image_file}")
                print(f"图片路径: {image_path}")
                print(f"图片是否存在: {os.path.exists(image_path)}")
                
                # 检查图片是否存在
                if not os.path.exists(image_path):
                    print(f"图片不存在: {image_path}")
                    continue
                
                # 模拟OCR识别，不实际调用API
                print(f"模拟OCR识别")
                text = f"这是第 {i+1} 张图片的模拟识别结果"
                
                results.append({
                    "image": image_file,
                    "text": text
                })
                print(f"结果添加到列表")
                
                # 保存中间结果
                with open(ocr_output, 'w', encoding='utf-8') as f:
                    json.dump(results, f, ensure_ascii=False, indent=2)
                print(f"中间结果保存完成")
                
                print(f"已完成第 {i+1} 张图片的识别")
                print(f"当前已处理 {len(results)} 张图片")
                print(f"识别结果: {text}")
            except Exception as e:
                print(f"处理第 {i+1} 张图片时出错: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"\n处理完成，共处理 {len(results)} 张图片")
        print(f"结果已保存到: {ocr_output}")
        
        # 生成TXT文件
        txt_output = os.path.join(temp_output, 'ocr_results.txt')
        print(f"开始生成TXT文件: {txt_output}")
        
        # 读取OCR结果
        with open(ocr_output, 'r', encoding='utf-8') as f:
            ocr_results = json.load(f)
        
        # 生成txt内容
        txt_content = "PDF OCR结果\n\n"
        for i, result in enumerate(ocr_results):
            text = result['text']
            txt_content += f"{text}\n\n"
        
        # 保存txt文件
        with open(txt_output, 'w', encoding='utf-8') as f:
            f.write(txt_content)
        
        print(f"TXT文件生成完成: {txt_output}")
        
        print("\n测试完成！")
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理临时文件
        if os.path.exists(temp_output):
            import shutil
            print(f"清理临时文件: {temp_output}")
            shutil.rmtree(temp_output)
            print(f"临时文件清理完成")

if __name__ == "__main__":
    test_pdf_processing()
