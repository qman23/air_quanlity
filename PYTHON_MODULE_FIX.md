# Python模块未找到问题解决方案

## 问题描述
每次用 `python3` 启动程序都会报模块未找到的错误，原因是之前依赖装在虚拟环境中，而直接使用系统Python运行程序时无法找到这些模块。

## 问题分析

### 发现的问题：
1. ✅ 项目有虚拟环境目录 `myenv/`
2. ✅ `requirements.txt` 中列出了所有必要依赖
3. ❌ 虚拟环境中缺少 `pandas` 和 `requests-cache` 模块
4. ❌ 直接用 `python3` 运行时找不到这些模块

### 根本原因：
- 程序需要的某些模块（如 `pandas`, `requests-cache`）虽然在 `requirements.txt` 中列出，但没有在虚拟环境中安装
- 直接使用系统的 `python3` 运行程序，而不是虚拟环境中的Python

## 解决方案

### 🔧 已执行的修复步骤：

1. **安装缺失的依赖到虚拟环境**
   ```bash
   source myenv/bin/activate
   pip install pandas requests-cache
   ```

2. **安装完整的requirements.txt依赖**
   ```bash
   source myenv/bin/activate
   pip install -r requirements.txt
   ```

3. **创建便捷运行脚本**
   - `run.sh`: 一键运行程序（自动激活虚拟环境）
   - `activate_env.sh`: 激活虚拟环境脚本

### 📝 现在可用的运行方法：

#### 方法1：使用便捷脚本（推荐）
```bash
# 单次运行
./run.sh --mode once

# 定时监控
./run.sh --mode monitor

# 测试模式
./run.sh --mode test

# 查看帮助
./run.sh --help
```

#### 方法2：手动激活虚拟环境
```bash
# 激活虚拟环境
source myenv/bin/activate

# 运行程序
python3 main.py --mode once

# 退出虚拟环境
deactivate
```

#### 方法3：使用激活脚本
```bash
# 运行激活脚本（会显示详细说明）
source activate_env.sh
```

#### 方法4：一步激活并运行
```bash
source myenv/bin/activate && python3 main.py --mode once
```

## 验证结果

### ✅ 测试通过：
- 使用 `./run.sh --mode once` 成功运行程序
- 程序正常获取空气质量数据并保存到数据库
- 所有依赖模块都可以正常导入

### 📊 运行结果示例：
```
2025-12-04 11:52:25,316 - INFO - 开始收集 chengdu 的空气质量数据...
2025-12-04 11:52:26,976 - INFO - 数据解析成功 - Chengdu (成都): AQI 80 (良)
2025-12-04 11:52:27,003 - INFO - 数据保存成功 - Chengdu (成都): AQI 80 (良) [尝试 1]
数据收集成功

=== 数据库操作统计 ===
总尝试次数: 1
成功插入: 1
失败插入: 0
验证错误: 0
成功率: 1/1 (100.0%)
========================
```

## 注意事项

### ⚠️ 重要提醒：
1. **每次新开终端都需要激活虚拟环境**
2. **建议使用 `./run.sh` 脚本运行程序**（自动处理环境问题）
3. **确保所有依赖都在虚拟环境中安装**

### 🔍 调试命令：
```bash
# 检查虚拟环境中的已安装包
source myenv/bin/activate && pip list

# 测试模块导入
source myenv/bin/activate && python3 -c "import pandas, requests_cache; print('OK')"

# 重新安装所有依赖
source myenv/bin/activate && pip install -r requirements.txt

# 检查Python路径
source myenv/bin/activate && which python3
```

### 🚀 长期解决方案：
可以在 `.zshrc` 或 `.bashrc` 中添加别名简化操作：

```bash
# 添加到 ~/.zshrc 或 ~/.bashrc
alias air-quality='cd /Users/lizhiwei/workspace/test/air_quanlity && ./run.sh'
alias activate-air='cd /Users/lizhiwei/workspace/test/air_quanlity && source myenv/bin/activate'
```

然后重新加载配置：
```bash
source ~/.zshrc  # 或 source ~/.bashrc
```

之后就可以直接使用：
```bash
air-quality --mode once
activate-air
```

## 文件说明

### 📁 新增的文件：
- `setup_environment.py`: 环境问题诊断和修复脚本
- `run.sh`: 便捷运行脚本
- `activate_env.sh`: 虚拟环境激活脚本
- `PYTHON_MODULE_FIX.md`: 本解决方案文档

### 📁 现有文件：
- `myenv/`: Python虚拟环境目录
- `requirements.txt`: 项目依赖列表
- `main.py`: 主程序文件
- `analyze_api.py`: API分析工具

## 总结

✅ **问题已完全解决**：
- 所有缺失的依赖已安装到虚拟环境
- 创建了便捷的运行脚本
- 提供了多种运行方式
- 程序可以正常运行并获取数据

🎯 **最佳实践**：
- 使用 `./run.sh` 运行程序
- 在虚拟环境中安装所有依赖
- 定期更新依赖包

现在您可以正常使用空气质量监控程序，不再会遇到模块未找到的问题！
