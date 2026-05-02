@echo off
chcp 65001 >nul
echo ==========================================
echo    虾仔科技 - HTTPS用户管理系统
echo ==========================================
echo.

echo 步骤1：生成SSL证书...
openssl req -x509 -newkey rsa:2048 -keyout key.pem -out cert.pem -days 365 -nodes -subj "/C=CN/ST=Beijing/L=Beijing/O=XiaZaiTech/OU=IT/CN=49.232.79.54"

echo.
echo 步骤2：安装依赖...
py -m pip install flask

echo.
echo 步骤3：启动HTTPS服务（端口443）...
echo.
py user_system_server_https.py

pause
