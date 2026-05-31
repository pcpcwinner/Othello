#!/usr/bin/env python3
"""
黑白棋 (Othello/Reversi)
玩家 vs AI，支持自定义初始布局、选择先后手
"""
import sys
import os

# 确保能找到同目录模块
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui import OthelloGUI


def main():
    app = OthelloGUI()
    app.run()


if __name__ == '__main__':
    main()
