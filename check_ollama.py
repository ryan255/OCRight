import requests
import sys

def check_ollama_service(url="http://localhost:11434"):
    """检查ollama服务是否运行"""
    print(f"开始检查Ollama服务: {url}")
    try:
        response = requests.get(f'{url}/api/tags', timeout=5)
        print(f"响应状态码: {response.status_code}")
        if response.status_code == 200:
            print("Ollama服务正在运行")
            data = response.json()
            print(f"可用模型数量: {len(data.get('models', []))}")
            return True, url
        else:
            print(f"Ollama服务返回状态码: {response.status_code}")
            return False, None
    except requests.exceptions.ConnectionError:
        print(f"无法连接到Ollama服务: {url}，请确保服务已启动")
        return False, None
    except Exception as e:
        print(f"检查Ollama服务时出错: {e}")
        return False, None

if __name__ == "__main__":
    print("Python版本:", sys.version)
    result = check_ollama_service()
    print(f"检查结果: {'成功' if result else '失败'}")

