from flask import Flask, request, jsonify, Response
import requests
import json
import os
from datetime import datetime

app = Flask(__name__)

API_KEYS = {
    "openai": os.environ.get("OPENAI_API_KEY", ""),
    "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
}

PORT = int(os.environ.get("PORT", 8080))

@app.route('/v1/models', methods=['GET', 'POST'])
@app.route('/v1/chat/completions', methods=['GET', 'POST'])
@app.route('/v1/completions', methods=['GET', 'POST'])
@app.route('/v1/embeddings', methods=['GET', 'POST'])
def proxy():
    provider = request.headers.get('X-Provider', 'openai').lower()
    api_key = API_KEYS.get(provider, API_KEYS.get('openai', ''))

    if not api_key:
        return jsonify({
            "error": {
                "message": "API key not configured",
                "type": "invalid_request_error",
                "code": "missing_api_key"
            }
        }), 401

    base_urls = {
        "openai": "https://api.openai.com",
        "anthropic": "https://api.anthropic.com",
        "deepseek": "https://api.deepseek.com",
        "zhipu": "https://open.bigmodel.cn",
    }

    base_url = base_urls.get(provider, base_urls['openai'])
    path = request.path
    target_url = f"{base_url}{path}"

    headers = {k: v for k, v in request.headers if k.lower() not in ['host', 'content-length']}
    headers['Authorization'] = f"Bearer {api_key}"

    try:
        if request.method == 'POST':
            response = requests.post(
                target_url,
                headers=headers,
                data=request.get_data(),
                cookies=request.cookies,
                allow_redirects=False,
                stream=True
            )
        else:
            response = requests.get(
                target_url,
                headers=headers,
                cookies=request.cookies,
                allow_redirects=False
            )

        return Response(
            response.content,
            status=response.status_code,
            headers=dict(response.headers)
        )
    except Exception as e:
        return jsonify({
            "error": {
                "message": str(e),
                "type": "proxy_error"
            }
        }), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "providers": list(API_KEYS.keys())
    })

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "name": "虾仔科技 Token中转服务",
        "version": "1.0.0",
        "endpoints": {
            "chat_completions": "/v1/chat/completions",
            "models": "/v1/models",
            "embeddings": "/v1/embeddings"
        },
        "providers": list(API_KEYS.keys()),
        "usage": "在请求头中添加 X-Provider 指定服务商，如 X-Provider: openai"
    })

if __name__ == '__main__':
    print(f"Token Relay Service starting on port {PORT}")
    print(f"API Keys configured for: {list(API_KEYS.keys())}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
