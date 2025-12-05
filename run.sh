#!/bin/bash
# 空气质量监控程序运行脚本

# 激活虚拟环境
source myenv/bin/activate

# 运行程序
python3 main.py "$@"
