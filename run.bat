@echo off
chcp 65001 >nul
echo 正在启动黑白棋游戏...
python main.py
if %errorlevel% neq 0 (
    echo.
    echo 启动失败！请确保已安装 Python 3。
    echo 下载地址: https://www.python.org/downloads/
    echo 安装时记得勾选 "Add Python to PATH"
    pause
)
