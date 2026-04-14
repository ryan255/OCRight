from flask import Blueprint, request, jsonify, send_file
import os
import json
import requests
import uuid
import threading
import logging
from app.utils import file_utils, ocr_utils, config_utils

# 创建日志记录器
logger = logging.getLogger(__name__)

api = Blueprint('api', __name__)

@api.route('/api/ollama/check', methods=['GET'])
def check_ollama():
    """检查Ollama服务状态"""
    url = request.args.get('url', 'http://localhost:11434')
    logger.info(f"检查Ollama服务: {url}")
    try:
        response = requests.get(f'{url}/api/tags', timeout=5)
        logger.info(f"Ollama服务响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            models_count = len(data.get('models', []))
            logger.info(f"Ollama服务可用，模型数量: {models_count}")
            return jsonify({
                'status': 'success',
                'message': 'Ollama服务正在运行',
                'models_count': models_count
            })
        else:
            logger.error(f"Ollama服务不可用，状态码: {response.status_code}")
            return jsonify({
                'status': 'error',
                'message': f'Ollama服务返回状态码: {response.status_code}'
            }), 500
    except Exception as e:
        logger.error(f"连接Ollama服务失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'无法连接到Ollama服务: {str(e)}'
        }), 500

@api.route('/api/ollama/models', methods=['GET'])
def get_ollama_models():
    """获取可用的Ollama模型"""
    url = request.args.get('url', 'http://localhost:11434')
    logger.info(f"获取Ollama模型列表: {url}")
    try:
        response = requests.get(f'{url}/api/tags')
        logger.info(f"Ollama模型列表响应状态码: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            model_list = []
            for model in models:
                model_list.append({
                    'name': model.get('name', '未知模型'),
                    'size': model.get('size', '未知大小'),
                    'format': model.get('details', {}).get('format', '未知格式'),
                    'family': model.get('details', {}).get('family', '未知系列')
                })
            logger.info(f"获取到 {len(model_list)} 个Ollama模型")
            return jsonify({
                'status': 'success',
                'models': model_list
            })
        else:
            logger.error(f"获取模型列表失败，状态码: {response.status_code}")
            return jsonify({
                'status': 'error',
                'message': f'获取模型列表失败，状态码: {response.status_code}'
            }), 500
    except Exception as e:
        logger.error(f"获取模型列表时出错: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取模型列表时出错: {str(e)}'
        }), 500

@api.route('/api/upload', methods=['POST'])
def upload_file():
    """上传文件"""
    logger.info("接收到文件上传请求")
    if 'file' not in request.files:
        logger.error("未找到文件")
        return jsonify({
            'status': 'error',
            'message': '未找到文件'
        }), 400
    
    file = request.files['file']
    if file.filename == '':
        logger.error("未选择文件")
        return jsonify({
            'status': 'error',
            'message': '未选择文件'
        }), 400
    
    if not file_utils.allowed_file(file.filename):
        logger.error(f"不支持的文件类型: {file.filename}")
        return jsonify({
            'status': 'error',
            'message': '不支持的文件类型'
        }), 400
    
    try:
        file_path = file_utils.save_file(file)
        logger.info(f"文件上传成功: {file.filename} -> {file_path}")
        return jsonify({
            'status': 'success',
            'file_path': file_path,
            'filename': file.filename
        })
    except Exception as e:
        logger.error(f"文件上传失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'文件上传失败: {str(e)}'
        }), 500

# 全局变量，用于存储处理进度
processing_progress = {}

@api.route('/api/ocr', methods=['POST'])
def perform_ocr():
    """执行OCR识别"""
    logger.info("接收到OCR处理请求")
    
    data = request.json
    logger.info(f"请求数据: {data}")
    
    file_path = data.get('file_path')
    model = data.get('model')
    ollama_url = data.get('ollama_url', 'http://localhost:11434')
    
    logger.info(f"文件路径: {file_path}")
    logger.info(f"模型: {model}")
    logger.info(f"Ollama URL: {ollama_url}")
    
    if not file_path or not model:
        logger.error(f"缺少必要参数: file_path={file_path}, model={model}")
        return jsonify({
            'status': 'error',
            'message': '缺少必要参数'
        }), 400
    
    # 生成任务ID
    task_id = str(uuid.uuid4())
    processing_progress[task_id] = {
        'status': 'processing',
        'progress': 0,
        'message': 'PDF上传成功，开始拆分图片...'
    }
    logger.info(f"生成任务ID: {task_id}")
    
    # 在后台线程中执行OCR处理
    def process_task():
        try:
            # 更新进度
            processing_progress[task_id]['progress'] = 10
            processing_progress[task_id]['message'] = 'PDF上传成功，开始拆分图片...'
            logger.info(f"任务 {task_id}: PDF上传成功，开始拆分图片...")
            
            # 执行OCR处理
            result = ocr_utils.process_ocr(file_path, model, ollama_url, task_id, processing_progress)
            
            # 更新进度
            processing_progress[task_id]['status'] = 'completed'
            processing_progress[task_id]['progress'] = 100
            processing_progress[task_id]['message'] = 'PDF处理完成'
            processing_progress[task_id]['result'] = result
            logger.info(f"任务 {task_id}: PDF处理完成")
        except Exception as e:
            logger.error(f"任务 {task_id}: OCR处理失败: {str(e)}")
            import traceback
            traceback.print_exc()
            processing_progress[task_id]['status'] = 'error'
            processing_progress[task_id]['message'] = f'OCR处理失败: {str(e)}'
    
    # 启动后台线程
    thread = threading.Thread(target=process_task)
    thread.daemon = True
    thread.start()
    logger.info(f"任务 {task_id}: 启动后台处理线程")
    
    # 返回任务ID
    return jsonify({
        'status': 'success',
        'task_id': task_id
    })

@api.route('/api/ocr/progress/<task_id>', methods=['GET'])
def get_ocr_progress(task_id):
    """获取OCR处理进度"""
    logger.info(f"获取任务进度: {task_id}")
    if task_id in processing_progress:
        logger.info(f"任务 {task_id} 进度: {processing_progress[task_id]['progress']}%, 状态: {processing_progress[task_id]['status']}")
        return jsonify({
            'status': 'success',
            'progress': processing_progress[task_id]
        })
    else:
        logger.error(f"任务不存在: {task_id}")
        return jsonify({
            'status': 'error',
            'message': '任务不存在'
        }), 404

@api.route('/api/ocr/stop/<task_id>', methods=['POST'])
def stop_ocr_process(task_id):
    """停止OCR处理任务"""
    logger.info(f"停止任务: {task_id}")
    if task_id in processing_progress:
        processing_progress[task_id]['status'] = 'stopped'
        processing_progress[task_id]['message'] = '任务已停止'
        logger.info(f"任务 {task_id} 已停止")
        return jsonify({
            'status': 'success',
            'message': '任务已停止'
        })
    else:
        logger.error(f"任务不存在: {task_id}")
        return jsonify({
            'status': 'error',
            'message': '任务不存在'
        }), 404

@api.route('/api/download', methods=['GET'])
def download_file():
    """下载处理结果"""
    file_path = request.args.get('file_path')
    logger.info(f"接收到文件下载请求: {file_path}")
    if not file_path:
        logger.error("未指定文件路径")
        return jsonify({
            'status': 'error',
            'message': '未指定文件路径'
        }), 400
    
    if not os.path.exists(file_path):
        logger.error(f"文件不存在: {file_path}")
        return jsonify({
            'status': 'error',
            'message': '文件不存在'
        }), 404
    
    try:
        logger.info(f"开始下载文件: {file_path}")
        return send_file(file_path, as_attachment=True)
    except Exception as e:
        logger.error(f"文件下载失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'文件下载失败: {str(e)}'
        }), 500

@api.route('/api/config/get', methods=['GET'])
def get_config():
    """获取用户配置"""
    logger.info("接收到获取配置请求")
    try:
        config = config_utils.get_ollama_config()
        logger.info(f"获取配置成功: {config}")
        return jsonify({
            'status': 'success',
            'config': config
        })
    except Exception as e:
        logger.error(f"获取配置失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'获取配置失败: {str(e)}'
        }), 500

@api.route('/api/config/save', methods=['POST'])
def save_config():
    """保存用户配置"""
    data = request.json
    logger.info(f"接收到保存配置请求: {data}")
    url = data.get('url')
    model = data.get('model')
    
    if not url:
        logger.error("缺少Ollama服务地址")
        return jsonify({
            'status': 'error',
            'message': '缺少Ollama服务地址'
        }), 400
    
    try:
        success = config_utils.save_ollama_config(url, model)
        if success:
            logger.info(f"配置保存成功: {url}, {model}")
            return jsonify({
                'status': 'success',
                'message': '配置保存成功'
            })
        else:
            logger.error("配置保存失败")
            return jsonify({
                'status': 'error',
                'message': '配置保存失败'
            }), 500
    except Exception as e:
        logger.error(f"保存配置失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'保存配置失败: {str(e)}'
        }), 500
