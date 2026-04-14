import requests

def get_ollama_models(ollama_url="http://localhost:11434"):
    """获取ollama中的模型列表"""
    try:
        response = requests.get(f'{ollama_url}/api/tags')
        if response.status_code == 200:
            data = response.json()
            models = data.get('models', [])
            print(f"发现 {len(models)} 个可用模型:")
            
            model_names = []
            for i, model in enumerate(models):
                model_name = model.get('name', '未知模型')
                model_names.append(model_name)
                model_size = model.get('size', '未知大小')
                model_details = model.get('details', {})
                model_format = model_details.get('format', '未知格式')
                model_family = model_details.get('family', '未知系列')
                
                print(f"{i+1}. {model_name}")
                print(f"   大小: {model_size}")
                print(f"   格式: {model_format}")
                print(f"   系列: {model_family}")
                print()
            
            if model_names:
                print(f"默认使用第一个模型: {model_names[0]}")
                return model_names
            else:
                print("没有可用模型")
                return None
        else:
            print(f"获取模型列表失败，状态码: {response.status_code}")
            return None
    except Exception as e:
        print(f"获取模型列表时出错: {e}")
        return None

if __name__ == "__main__":
    get_ollama_models()
