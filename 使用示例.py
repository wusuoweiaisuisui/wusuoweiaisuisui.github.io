#!/usr/bin/env python3
"""
Token中转服务使用示例
"""

import requests

# ======================================
# 配置
# ======================================

# 服务地址（本地测试用这个）
BASE_URL = "http://127.0.0.1:8080"

# 如果部署到服务器了，改成：
# BASE_URL = "http://49.232.79.54:8080"

# ======================================
# 示例1：健康检查
# ======================================
print("=" * 50)
print("示例1：健康检查")
print("=" * 50)
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"状态码: {response.status_code}")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

print("\n" + "=" * 50)
print("示例2：获取服务信息")
print("=" * 50)
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"响应: {response.json()}")
except Exception as e:
    print(f"错误: {e}")

# ======================================
# 示例3：OpenAI格式的Chat请求（需要配置真实API密钥）
# ======================================
print("\n" + "=" * 50)
print("示例3：Chat请求示例（需要真实API密钥）")
print("=" * 50)
print("""
使用说明：
1. 先设置环境变量 OPENAI_API_KEY 和 ANTHROPIC_API_KEY
2. 然后启动服务
3. 再运行这个示例

请求格式：
{
    "model": "gpt-3.5-turbo",
    "messages": [
        {"role": "user", "content": "你好"}
    ]
}

请求头需要添加：
X-Provider: openai  (或 anthropic, deepseek, zhipu)
""")

# ======================================
# 模拟请求示例（不实际发送）
# ======================================
print("\n" + "=" * 50)
print("Python代码示例")
print("=" * 50)
print("""
import requests

# 配置
BASE_URL = "http://127.0.0.1:8080"

# 方式1：OpenAI
response = requests.post(
    f"{BASE_URL}/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "X-Provider": "openai"  # 指定服务商
    },
    json={
        "model": "gpt-3.5-turbo",
        "messages": [
            {"role": "user", "content": "你好，请介绍一下自己"}
        ]
    }
)
print(response.json())

# 方式2：Anthropic
response = requests.post(
    f"{BASE_URL}/v1/chat/completions",
    headers={
        "Content-Type": "application/json",
        "X-Provider": "anthropic"
    },
    json={
        "model": "claude-3-sonnet-20240229",
        "messages": [
            {"role": "user", "content": "你好"}
        ]
    }
)
print(response.json())
""")

# ======================================
# cURL 命令示例
# ======================================
print("\n" + "=" * 50)
print("cURL命令示例")
print("=" * 50)
print("""
# OpenAI
curl http://127.0.0.1:8080/v1/chat/completions \\
  -H "Content-Type: application/json" \\
  -H "X-Provider: openai" \\
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "你好"}]
  }'

# Anthropic
curl http://127.0.0.1:8080/v1/chat/completions \\
  -H "Content-Type": application/json" \\
  -H "X-Provider: anthropic" \\
  -d '{
    "model": "claude-3-sonnet-20240229",
    "messages": [{"role": "user", "content": "你好"}]
  }'
""")
