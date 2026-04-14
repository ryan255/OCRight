from flask import Flask, render_template
from flask_cors import CORS
import os
import sys
import logging

# 添加当前目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 获取当前文件所在目录
base_dir = os.path.dirname(os.path.abspath(__file__))

# 创建日志目录
log_dir = os.path.join(base_dir, 'logs')
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'app.log')),
        logging.StreamHandler()
    ]
)

from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# 显式设置模板和静态文件路径
app.template_folder = os.path.join(base_dir, 'app', 'templates')
app.static_folder = os.path.join(base_dir, 'app', 'static')

CORS(app)

# 根路径路由
@app.route('/')
def index():
    return render_template('index.html')

# 导入API路由并注册蓝图
from app.api.routes import api
app.register_blueprint(api)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
