#!/bin/bash
# Build Windows EXE using Wine + PyInstaller
# Run after: brew install --cask wine-stable

set -e

PROJECT_DIR="$(cd "$(dirname "$0")/.." && pwd)"
BUILD_DIR="$PROJECT_DIR/build"
OUTPUT_DIR="$PROJECT_DIR/dist"

echo "=== Othello Windows 打包 ==="

# 1. 安装 Windows Python + PyInstaller
echo "[1/3] 准备 Windows Python 环境..."
WIN_PYTHON="$HOME/.wine/drive_c/Python311/python.exe"
if [ ! -f "$WIN_PYTHON" ]; then
    echo "下载 Python 3.11 for Windows..."
    curl -L -o /tmp/python311.exe "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
    wine /tmp/python311.exe /quiet InstallAllUsers=1 PrependPath=1 TargetDir=C:\\Python311
    echo "下载 PyInstaller..."
    wine "$WIN_PYTHON" -m pip install pyinstaller
fi

# 2. 复制项目文件到 Windows 环境
echo "[2/3] 复制项目文件..."
mkdir -p "$BUILD_DIR"
cp "$PROJECT_DIR"/*.py "$BUILD_DIR/"

# 3. 打包
echo "[3/3] 打包 EXE..."
cd "$BUILD_DIR"
wine "$WIN_PYTHON" -m PyInstaller --onefile --windowed --name Othello main.py
cp dist/Othello.exe "$OUTPUT_DIR/"

echo ""
echo "=== 完成 ==="
echo "EXE 文件: $OUTPUT_DIR/Othello.exe"
echo "文件大小: $(du -h "$OUTPUT_DIR/Othello.exe" | cut -f1)"
