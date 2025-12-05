#!/bin/bash
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
