#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
环境设置脚本
用于解决Python模块未找到的问题
"""

import subprocess
import sys
import os

def check_python_version():
    """检查Python版本"""
    print(f"当前Python版本: {sys.version}")
    return sys.version_info >= (3, 6)

def check_virtual_env():
    """检查虚拟环境状态"""
    venv_path = "myenv"
    if os.path.exists(venv_path):
        print(f"✓ 虚拟环境目录存在: {venv_path}")
        return True
    else:
        print(f"✗ 虚拟环境目录不存在: {venv_path}")
        return False

def install_requirements():
    """安装requirements.txt中的依赖"""
    print("正在安装项目依赖...")
    
    # 激活虚拟环境并安装依赖
    commands = [
        "source myenv/bin/activate",
        "pip install -r requirements.txt"
    ]
    
    for cmd in commands:
        print(f"执行: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"命令执行失败: {cmd}")
            print(f"错误信息: {result.stderr}")
            return False
        else:
            print(f"✓ 命令执行成功: {cmd}")
    
    return True

def create_run_scripts():
    """创建便捷的运行脚本"""
    
    # 创建运行脚本
    run_script = """#!/bin/bash
# 空气质量监控程序运行脚本

# 激活虚拟环境
source myenv/bin/activate

# 运行程序
python3 main.py "$@"
"""
    
    with open("run.sh", "w", encoding="utf-8") as f:
        f.write(run_script)
    
    # 设置执行权限
    os.chmod("run.sh", 0o755)
    print("✓ 创建运行脚本: run.sh")

def create_activation_script():
    """创建环境激活脚本"""
    
    activate_script = """#!/bin/bash
# 激活虚拟环境脚本

echo "激活虚拟环境..."
source myenv/bin/activate

echo "虚拟环境已激活"
echo "Python路径: $(which python3)"
echo "Pip路径: $(which pip)"
echo ""
echo "现在你可以运行:"
echo "  python3 main.py --help"
echo "  python3 main.py --mode once"
echo "  python3 main.py --mode monitor"
echo ""
echo "或者使用便捷脚本:"
echo "  ./run.sh --mode once"
echo "  ./run.sh --mode monitor"
echo ""
echo "退出虚拟环境: deactivate"
"""
    
    with open("activate_env.sh", "w", encoding="utf-8") as f:
        f.write(activate_script)
    
    # 设置执行权限
    os.chmod("activate_env.sh", 0o755)
    print("✓ 创建激活脚本: activate_env.sh")

def print_solution():
    """打印解决方案说明"""
    solution = """
=== 解决方案说明 ===

问题分析:
1. 项目有虚拟环境目录 myenv/
2. requirements.txt 中列出了所有依赖
3. 但虚拟环境中缺少 pandas 和 requests-cache 模块
4. 直接用 python3 运行时找不到这些模块

解决方案:
1. 确保在虚拟环境中运行程序
2. 安装所有缺失的依赖
3. 使用便捷脚本运行程序

运行方法:
方法1 - 使用激活脚本:
  source activate_env.sh
  
方法2 - 手动激活:
  source myenv/bin/activate
  python3 main.py --mode once
  
方法3 - 使用便捷脚本:
  ./run.sh --mode once
  
方法4 - 一步激活并运行:
  source myenv/bin/activate && python3 main.py "$@"

注意事项:
- 每次新开终端都需要激活虚拟环境
- 可以在 .bashrc 或 .zshrc 中添加别名简化操作
- 确保所有依赖都在虚拟环境中安装

调试命令:
- 检查虚拟环境依赖: source myenv/bin/activate && pip list
- 测试模块导入: source myenv/bin/activate && python3 -c "import pandas, requests_cache; print('OK')"
- 重新安装依赖: source myenv/bin/activate && pip install -r requirements.txt
"""
    print(solution)

def main():
    """主函数"""
    print("=== Python环境问题诊断和解决工具 ===\n")
    
    # 检查Python版本
    if not check_python_version():
        print("✗ Python版本过低，需要3.6+")
        return
    
    # 检查虚拟环境
    if not check_virtual_env():
        print("请先创建虚拟环境")
        return
    
    # 安装依赖
    if not install_requirements():
        print("✗ 依赖安装失败")
        return
    
    # 创建便捷脚本
    create_run_scripts()
    create_activation_script()
    
    print("\n=== 环境设置完成! ===")
    print_solution()

if __name__ == "__main__":
    main()
