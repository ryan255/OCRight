import os
import json

# 配置文件路径
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'user_config.json')

def load_config():
    """加载用户配置"""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_config(config):
    """保存用户配置"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def get_ollama_config():
    """获取Ollama配置"""
    config = load_config()
    return {
        'url': config.get('ollama_url', 'http://localhost:11434'),
        'model': config.get('preferred_model', '')
    }

def save_ollama_config(url, model):
    """保存Ollama配置"""
    config = load_config()
    config['ollama_url'] = url
    config['preferred_model'] = model
    return save_config(config)
