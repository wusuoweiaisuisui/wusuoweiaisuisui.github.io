# Windows本地使用指南

## 📌 重要提示

**不要使用Linux命令**，Windows有自己的命令！

❌ 错误命令（Linux）：
- `python3`
- `pip3`
- `export`
- `wget`

✅ 正确命令（Windows）：
- `py` 或 `python`
- `py -m pip`
- `$env:` 或 `set`
- `Invoke-WebRequest` 或直接双击批处理文件

---

## 🚀 快速启动（3种方式）

### 方式1：双击批处理文件（最简单）⭐

1. 右键点击 `启动Token中转服务.bat`
2. 选择"编辑"
3. 把里面的API密钥改成您真实的密钥
4. 保存并双击运行

---

### 方式2：PowerShell命令行

```powershell
# 1. 进入目录
cd C:\AIProjects\monitors

# 2. 设置环境变量
$env:OPENAI_API_KEY="您的OpenAI密钥"
$env:ANTHROPIC_API_KEY="您的Anthropic密钥"

# 3. 启动服务
py token_relay_server.py
```

---

### 方式3：CMD命令行

```cmd
# 1. 进入目录
cd C:\AIProjects\monitors

# 2. 设置环境变量
set OPENAI_API_KEY=您的OpenAI密钥
set ANTHROPIC_API_KEY=您的Anthropic密钥

# 3. 启动服务
py token_relay_server.py
```

---

## 🌐 测试服务

服务启动后，打开浏览器访问：

- 首页：http://127.0.0.1:8080/
- 健康检查：http://127.0.0.1:8080/health

---

## 📊 Windows vs Linux命令对照表

| 操作 | Windows (PowerShell) | Linux |
|------|---------------------|-------|
| Python | `py` 或 `python` | `python3` |
| 安装包 | `py -m pip install` | `pip3 install` |
| 设置环境变量 | `$env:KEY="value"` | `export KEY="value"` |
| 下载文件 | `Invoke-WebRequest` 或直接用浏览器 | `wget` |

---

## 🎯 如果要部署到腾讯云服务器

您需要：
1. SSH登录到服务器（这时才是Linux环境）
2. 在服务器上使用Linux命令
3. 参考 `部署指南.md`

---

## 📝 已准备好的文件

- ✅ `token_relay_server.py` - 服务脚本
- ✅ `启动Token中转服务.bat` - 一键启动（Windows）
- ✅ `部署指南.md` - 服务器部署指南
- ✅ `Windows使用指南.md` - 本文件
