import fitz
import os
import argparse


def extract_images(pdf_path, output_dir):
    """提取PDF中的所有图片并按顺序编码保存"""
    # 如果未指定输出目录，使用PDF文件所在目录
    if not output_dir:
        pdf_dir = os.path.dirname(pdf_path)
        output_dir = os.path.join(pdf_dir, "output_images")
    
    # 确保输出目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 打开PDF文件
    doc = fitz.open(pdf_path)
    
    # 图片计数器
    image_count = 1
    
    # 遍历每一页
    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # 获取页面中的图片
        images = page.get_images(full=True)
        
        # 遍历每一张图片
        for img in images:
            xref = img[0]
            
            # 提取图片
            base_image = doc.extract_image(xref)
            image_data = base_image["image"]
            image_ext = base_image["ext"]
            
            # 生成图片文件名
            image_filename = f"{image_count}.{image_ext}"
            image_path = os.path.join(output_dir, image_filename)
            
            # 保存图片
            with open(image_path, "wb") as f:
                f.write(image_data)
            
            print(f"已提取图片: {image_filename}")
            image_count += 1
    
    doc.close()
    print(f"\n提取完成，共提取 {image_count-1} 张图片")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="提取PDF中的所有图片并按顺序编码")
    parser.add_argument("pdf_path", help="PDF文件路径")
    parser.add_argument("--output", "-o", default="output_images", help="输出目录，默认: output_images")
    
    args = parser.parse_args()
    
    extract_images(args.pdf_path, args.output)
