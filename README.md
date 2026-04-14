# OCRight - PDF和图片OCR识别工具

## 软件简介

OCRight是一个功能强大的OCR识别工具，支持从PDF文件中提取图片并进行OCR识别，或将单个图片直接进行OCR识别，最终生成可编辑的文本文件。

## 项目结构

```
OCRight/
├── app/                 # Web应用部分
│   ├── api/             # API路由
│   ├── static/          # 静态文件
│   ├── templates/       # 模板文件
│   └── utils/           # 工具函数
├── cli/                 # 命令行工具部分
│   ├── check_ollama.py  # 检查Ollama服务
│   ├── extract_pdf_images.py  # 提取PDF图片
│   ├── generate_epub.py # 生成EPUB文件
│   ├── generate_txt.py  # 生成TXT文件
│   ├── get_ollama_models.py  # 获取Ollama模型
│   ├── main.py          # 命令行主入口
│   └── ocr_images.py    # 处理图片OCR
├── .gitignore           # Git忽略文件
├── config.py            # 配置文件
├── README.md            # 项目文档
├── requirements.txt     # 依赖项
├── run.py               # Web服务启动文件
└── user_config.json     # 用户配置文件
```

## 功能特点

### 支持多种文件类型
- **PDF文件**：自动提取所有图片并进行OCR识别
- **图片文件**：直接进行OCR识别，无需提取步骤

### 完整的处理流程
- **PDF处理**：提取图片 → 选择Ollama服务 → 选择模型 → OCR识别 → 生成TXT
- **图片处理**：选择Ollama服务 → 选择模型 → OCR识别 → 生成TXT

### 多种使用方式
- **命令行界面**：适合脚本和自动化场景
- **Web界面**：现代化的用户界面，支持Web和移动端适配
- **RESTful API**：支持前后端分离架构

### 交互式命令行界面
- 引导用户输入文件路径
- 支持拖放文件
- 智能默认选项，减少用户输入
- 实时显示处理进度

### 现代化Web界面
- 响应式设计，支持PC和移动设备
- 直观的文件上传和处理流程
- 实时处理状态和进度显示
- 支持直接在浏览器中预览识别结果
- 标签页分离：PDF拆分识别和单图片OCR识别分开操作
- 配置保存：自动保存Ollama服务地址和首选模型
- 智能模型选择：自动选择首选模型，也可手动选择
- 实时状态反馈：详细的错误处理和加载状态
- 停止功能：可随时停止正在进行的OCR任务

### 灵活的Ollama服务选择
- 使用本地Ollama服务（默认）
- 手动输入Ollama服务地址和端口
- 自动测试Ollama服务连接

### 智能输出管理
- 所有输出和中间产物保存在输入文件同级的输出目录
- 目录命名：{文件名}_output
- 支持断点续传，可继续处理未完成的OCR任务
- 按数字顺序处理图片，确保识别结果的顺序与原始PDF一致

## 安装方法

### 从源代码运行

1. 克隆或下载本项目
2. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 方法一：命令行版本

1. 运行命令行工具：
   ```bash
   python cli/main.py
   ```
2. 输入PDF或图片文件路径，或直接拖放文件到命令行窗口
3. 按照提示完成后续操作：
   - **PDF文件**：
     1. 选择是否需要OCR转文字（默认是）
     2. 选择Ollama服务方式（默认使用本地）
     3. 选择模型（默认选择第一个）
   - **图片文件**：
     1. 选择Ollama服务方式（默认使用本地）
     2. 选择模型（默认选择第一个）
4. 等待处理完成，生成的TXT文件会保存在输入文件同级的输出目录中
5. 按回车键退出对话框

### 方法二：Web版本

1. 启动Web服务：
   ```bash
   python run.py
   ```
2. 打开浏览器访问 `http://localhost:5000`
3. 按照Web界面提示操作：
   - **选择功能**：在顶部标签页选择"PDF拆分识别"或"单图片OCR识别"
   - **上传文件**：根据选择的功能，点击或拖放对应的文件到上传区域
   - **OCR设置**：
     1. 输入Ollama服务地址（默认：http://localhost:11434）
     2. 点击"检查服务"按钮验证Ollama服务状态
     3. 选择可用的模型（系统会自动保存您的首选模型）
   - **开始处理**：点击"开始处理"按钮
   - **查看结果**：处理完成后，可以下载TXT和EPUB格式的结果文件，也可以在页面上预览OCR识别结果
   - **新任务**：点击"新任务"按钮开始新的OCR任务
   - **停止任务**：在处理过程中，可以点击"停止处理"按钮中止正在进行的OCR任务

### 方法三：API接口

OCRight提供了RESTful API接口，支持前后端分离架构。

#### 1. 检查Ollama服务状态

```
GET /api/ollama/check?url=http://localhost:11434
```

#### 2. 获取可用模型列表

```
GET /api/ollama/models?url=http://localhost:11434
```

#### 3. 上传文件

```
POST /api/upload
Content-Type: multipart/form-data
```

#### 4. 执行OCR识别

```
POST /api/ocr
Content-Type: application/json

{
  "file_path": "path/to/file",
  "model": "llama3:8b",
  "ollama_url": "http://localhost:11434"
}
```

#### 5. 下载处理结果

```
GET /api/download?file_path=path/to/result
```

#### 6. 获取用户配置

```
GET /api/config/get
```

#### 7. 保存用户配置

```
POST /api/config/save
Content-Type: application/json

{
  "url": "http://localhost:11434",
  "model": "llama3:8b"
}
```

#### 8. 停止OCR任务

```
POST /api/ocr/stop/{task_id}
```

## 示例

### 命令行版本示例

#### 处理PDF文件

```
========================================
OCRight - PDF和图片OCR识别工具
========================================

第一步：请输入PDF或图片文件路径，或直接拖放文件到对话框
文件路径: C:\Documents\example.pdf

输出目录已创建: C:\Documents\example_output
开始从PDF中提取图片: C:\Documents\example.pdf
正在提取第 1 张图片...
正在提取第 2 张图片...
正在提取第 3 张图片...
提取完成，共提取 3 张图片
提取完成，图片保存在: C:\Documents\example_output\output_images

第二步：是否需要进行OCR转文字
1. 是 (默认)
2. 否
请选择 (1/2): 1

请选择ollama服务方式:
1. 使用本地ollama (http://localhost:11434) (默认)
2. 手动输入ollama地址和端口
请选择 (1/2): 1

正在测试本地ollama服务...
开始检查Ollama服务: http://localhost:11434
响应状态码: 200
Ollama服务正在运行
可用模型数量: 3

正在获取ollama模型列表...
发现 3 个可用模型:
1. llama3:8b
   大小: 4.7 GB
   格式: gguf
   系列: llama3

2. mistral:7b
   大小: 4.1 GB
   格式: gguf
   系列: mistral

3. deepseek-r1
   大小: 6.2 GB
   格式: gguf
   系列: deepseek

默认使用第一个模型: llama3:8b

可用模型:
1. llama3:8b (默认)
2. mistral:7b
3. deepseek-r1
请选择模型编号 (默认 1): 1

第三步：开始进行OCR识别，使用模型: llama3:8b
使用Ollama服务地址: http://localhost:11434
开始进行OCR识别，使用模型: llama3:8b
使用Ollama服务地址: http://localhost:11434
发现 3 张图片
未发现现有结果文件，将从头开始处理所有图片

正在处理第 1/3 张图片: 1.jpg
请求接口: http://localhost:11434/api/generate
使用模型: llama3:8b
已完成第 1 张图片的识别
当前已处理 1 张图片
识别结果: 这是第一张图片的内容...

正在处理第 2/3 张图片: 2.jpg
请求接口: http://localhost:11434/api/generate
使用模型: llama3:8b
已完成第 2 张图片的识别
当前已处理 2 张图片
识别结果: 这是第二张图片的内容...

正在处理第 3/3 张图片: 3.jpg
请求接口: http://localhost:11434/api/generate
使用模型: llama3:8b
已完成第 3 张图片的识别
当前已处理 3 张图片
识别结果: 这是第三张图片的内容...

处理完成，共处理 3 张图片
结果已保存到: C:\Documents\example_output\ocr_results.json
开始生成TXT文件
TXT文件已生成: C:\Documents\example_output\ocr_results.txt
任务完成，输出文件：C:\Documents\example_output\ocr_results.txt

请按回车键退出对话框
```

#### 处理图片文件

```
========================================
OCRight - PDF和图片OCR识别工具
========================================

第一步：请输入PDF或图片文件路径，或直接拖放文件到对话框
文件路径: C:\Documents\example.jpg

输出目录已创建: C:\Documents\example_output

第二步：直接进行OCR识别

请选择ollama服务方式:
1. 使用本地ollama (http://localhost:11434) (默认)
2. 手动输入ollama地址和端口
请选择 (1/2): 1

正在测试本地ollama服务...
开始检查Ollama服务: http://localhost:11434
响应状态码: 200
Ollama服务正在运行
可用模型数量: 3

正在获取ollama模型列表...
发现 3 个可用模型:
1. llama3:8b
   大小: 4.7 GB
   格式: gguf
   系列: llama3

2. mistral:7b
   大小: 4.1 GB
   格式: gguf
   系列: mistral

3. deepseek-r1
   大小: 6.2 GB
   格式: gguf
   系列: deepseek

默认使用第一个模型: llama3:8b

可用模型:
1. llama3:8b (默认)
2. mistral:7b
3. deepseek-r1
请选择模型编号 (默认 1): 1

第三步：开始进行OCR识别，使用模型: llama3:8b
使用Ollama服务地址: http://localhost:11434
开始进行OCR识别，使用模型: llama3:8b
使用Ollama服务地址: http://localhost:11434
正在识别图片: C:\Documents\example.jpg
处理单个图片文件: C:\Documents\example.jpg
未发现现有结果文件，将从头开始处理图片

正在处理图片: example.jpg
请求接口: http://localhost:11434/api/generate
使用模型: llama3:8b
已完成图片的识别
识别结果: 这是图片的内容...

处理完成，共处理 1 张图片
结果已保存到: C:\Documents\example_output\ocr_results.json
开始生成TXT文件
TXT文件已生成: C:\Documents\example_output\ocr_results.txt
任务完成，输出文件：C:\Documents\example_output\ocr_results.txt

请按回车键退出对话框
```

### Web版本示例

1. **启动Web服务**：
   ```bash
   python run.py
   ```

2. **访问Web界面**：打开浏览器访问 `http://localhost:5000`

3. **选择功能**：点击顶部标签页选择"PDF拆分识别"或"单图片OCR识别"

4. **上传文件**：点击或拖放文件到上传区域

5. **配置Ollama**：输入服务地址并检查状态，选择模型

6. **开始处理**：点击"开始处理"按钮

7. **查看进度**：实时查看处理进度和状态

8. **下载结果**：处理完成后，下载生成的TXT和EPUB文件

## 技术说明

- **PDF图片提取**：使用PyMuPDF库从PDF中提取所有图片
- **OCR识别**：使用Ollama API对图片进行OCR识别
- **文本生成**：将OCR识别结果汇总成TXT文件
- **断点续传**：支持继续处理未完成的OCR任务
- **跨平台**：支持Windows、macOS和Linux系统
- **图片排序**：按数字顺序处理图片，确保识别结果的顺序与原始PDF一致
- **错误处理**：添加了重试机制，提高OCR识别的成功率
- **GPU保护**：每次识别完成后休息3秒，避免显卡过热

## 注意事项

- 使用前请确保Ollama服务已启动
- 对于大型PDF文件，提取图片和OCR识别可能需要较长时间
- 识别效果取决于使用的模型和图片质量
- 生成的TXT文件会保存在输入文件同级的输出目录中
- Web服务默认运行在 `http://localhost:5000`

## 许可证

本软件采用MIT许可证，详见LICENSE文件。

## 联系我们

如有问题或建议，请通过以下方式联系我们：

- GitHub：https://github.com/ryan255/OCRight

---

**OCRight - 让OCR识别变得简单！**