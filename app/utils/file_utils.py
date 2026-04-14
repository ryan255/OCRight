import os
from flask import current_app
import uuid

def allowed_file(filename):
    """检查文件类型是否允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_file(file):
    """保存上传的文件"""
    unique_filename = str(uuid.uuid4()) + '_' + file.filename
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(file_path)
    return file_path

def get_output_path(original_path, extension):
    """生成输出文件路径"""
    base_name = os.path.splitext(os.path.basename(original_path))[0]
    output_filename = f"{base_name}_output{extension}"
    return os.path.join(current_app.config['OUTPUT_FOLDER'], output_filename)
