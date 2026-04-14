import json
import os
from ebooklib import epub

def generate_epub_from_ocr(ocr_results_file, output_epub, title="PDF OCR结果", author="OCR System"):
    """根据OCR识别结果生成epub电子书"""
    # 读取OCR识别结果
    with open(ocr_results_file, 'r', encoding='utf-8') as f:
        ocr_results = json.load(f)
    
    # 创建epub电子书
    book = epub.EpubBook()
    
    # 设置元数据
    book.set_title(title)
    book.add_author(author)
    book.set_language('zh-CN')
    
    # 创建目录
    book.toc = []
    
    # 为每张图片创建章节
    chapters = []
    for i, result in enumerate(ocr_results):
        image_file = result['image']
        text = result['text']
        
        # 从OCR识别结果中提取章节标题
        # 尝试使用识别文本的第一行作为标题
        lines = text.strip().split('\n')
        if lines:
            # 取第一行作为标题，去除首尾空格
            chapter_title = lines[0].strip()
            # 如果标题太长，截取前30个字符
            if len(chapter_title) > 30:
                chapter_title = chapter_title[:30] + "..."
        else:
            # 如果没有识别到文本，使用默认标题
            chapter_title = f"第 {i+1} 章"
        
        # 创建章节内容
        chapter_content = f"""
        <html>
        <head>
            <title>{chapter_title}</title>
        </head>
        <body>
            <h1>{chapter_title}</h1>
            <div>
                {text.replace('\n', '<br />')}
            </div>
        </body>
        </html>
        """
        
        # 创建章节对象
        chapter = epub.EpubHtml(title=chapter_title, file_name=f'chapter_{i+1}.html', lang='zh-CN')
        chapter.content = chapter_content
        
        # 添加章节到书中
        book.add_item(chapter)
        chapters.append(chapter)
        book.toc.append(chapter)
    
    # 添加导航项
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())
    
    # 设置书的脊柱
    book.spine = ['nav'] + chapters
    
    # 不需要添加图片，只使用OCR识别结果
    
    # 保存epub文件
    epub.write_epub(output_epub, book, {})
    print(f"EPUB电子书已生成: {output_epub}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="根据OCR识别结果生成epub电子书")
    parser.add_argument("--input", "-i", default="ocr_results.json", help="OCR识别结果文件，默认: ocr_results.json")
    parser.add_argument("--output", "-o", default="output.epub", help="输出epub文件，默认: output.epub")
    parser.add_argument("--title", "-t", default="PDF OCR结果", help="电子书标题，默认: PDF OCR结果")
    parser.add_argument("--author", "-a", default="OCR System", help="电子书作者，默认: OCR System")
    
    args = parser.parse_args()
    
    print(f"开始生成EPUB电子书...")
    print(f"输入文件: {args.input}")
    print(f"输出文件: {args.output}")
    print(f"标题: {args.title}")
    print(f"作者: {args.author}")
    
    generate_epub_from_ocr(args.input, args.output, args.title, args.author)
