# 空气质量自动化监控程序（增强版）

一个基于WAQI API的空气质量数据自动监控和存储程序，提供增强的错误处理和数据验证功能。

## 功能特性

- 🌟 **实时监控**: 自动获取WAQI API空气质量数据
- 📊 **数据存储**: 将数据存储到SQLite数据库
- 🔄 **多种运行模式**: 支持测试、定时监控和单次收集模式
- ⚙️ **灵活配置**: 支持配置文件和环境变量配置
- 📝 **增强日志**: 完善的日志记录和错误处理机制
- 🛡️ **数据验证**: 完整的数据验证和类型检查
- 🔄 **重试机制**: 自动重试失败的操作
- 📈 **统计功能**: 提供数据库操作统计信息
- 🎭 **模拟数据**: 支持模拟数据用于测试和演示

## 技术栈

- **语言**: Python 3.x
- **数据库**: SQLite
- **API**: WAQI (World Air Quality Index) API
- **依赖库**: requests, schedule, python-dotenv

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

创建 `.env` 文件：
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑 .env 文件，填入你的WAQI API密钥
vim .env
```

在 `.env` 文件中添加：
```bash
AQ_API_KEY=your_waqi_api_key
AQ_CITY=北京
AQ_DB_PATH=air_quality.db
AQ_INTERVAL=1
AQ_LOG_LEVEL=INFO
```

### 3. 获取WAQI API密钥

1. 访问 [WAQI API](https://api.waqi.info/)
2. 注册账户并获取免费API密钥
3. 免费额度：每日1000次请求

### 4. 运行程序

#### 测试模式（默认）
```bash
python main.py --mode test
```

#### 定时监控模式
```bash
python main.py --mode monitor
```

#### 单次收集数据
```bash
python main.py --mode once --city 上海
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--city` | 监控的城市名称 | 北京 |
| `--api-key` | WAQI API密钥 | 无 |
| `--db-path` | 数据库文件路径 | air_quality.db |
| `--interval` | 监控间隔（小时） | 1 |
| `--mode` | 运行模式 | test |
| `test` | 测试模式（运行3次收集操作） | - |
| `monitor` | 定时监控模式 | - |
| `once` | 单次收集模式 | - |

## 环境变量

程序支持通过环境变量进行配置：

```bash
# API配置
export AQ_API_KEY=your_waqi_api_key

# 数据库配置
export AQ_DB_PATH=air_quality.db

# 监控配置
export AQ_CITY=深圳
export AQ_INTERVAL=2

# 日志配置
export AQ_LOG_LEVEL=INFO
```

## 数据库结构

`air_quality` 表结构：

```sql
CREATE TABLE air_quality (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    city TEXT NOT NULL,
    aqi INTEGER,
    pm25 REAL,
    pm10 REAL,
    co REAL,
    no2 REAL,
    o3 REAL,
    so2 REAL,
    level TEXT,
    source TEXT DEFAULT 'waqi',
    raw_data TEXT
);
```

## 增强功能

### 1. 数据验证
- 完整性检查：验证必填字段
- 类型检查：确保数据类型正确
- 等级验证：验证空气质量等级有效性
- 长度限制：防止数据过长导致数据库问题

### 2. 错误处理
- 异常捕获：处理API请求、数据库操作等异常
- 错误重试：自动重试失败的操作
- 详细日志：记录完整的错误信息和堆栈跟踪
- 数据验证异常：专门处理数据验证错误

### 3. 数据库操作统计
- 记录总尝试次数
- 统计成功和失败插入数量
- 跟踪验证错误
- 记录最后错误信息和时间

### 4. 模拟数据支持
当未设置API密钥时，程序会自动生成模拟数据用于测试和演示：

```python
# 模拟数据示例
{
    "city": "北京",
    "aqi": 88,
    "pm25": 35.5,
    "pm10": 67.2,
    "co": 1.2,
    "no2": 45.8,
    "o3": 78.3,
    "so2": 12.5,
    "level": "良",
    "raw_data": {"mock": True, "generated_at": "2025-11-06T11:19:01"}
}
```

## 使用示例

### 示例1: 测试模式验证功能
```bash
python main.py --mode test --city 广州
```

输出示例：
```
=== 测试模式：验证改进的错误处理机制 ===
使用配置: 城市=广州, 数据库=air_quality.db

--- 测试轮次 1 ---
2025-11-06 11:19:01 - INFO - 开始收集 广州 的空气质量数据...
2025-11-06 11:19:01 - INFO - 正在请求WAQI API: https://api.waqi.info/feed/广州/
2025-11-06 11:19:01 - INFO - 数据解析成功 - Guangzhou: AQI 63 (良)
2025-11-06 11:19:01 - INFO - 数据保存成功 - Guangzhou: AQI 63 (良) [尝试 1]
收集结果: 成功

=== 数据库操作统计 ===
总尝试次数: 1
成功插入: 1
失败插入: 0
验证错误: 0
成功率: 1/1 (100.0%)
```

### 示例2: 监控成都空气质量
```bash
python main.py --mode monitor --city 成都 --interval 2
```

### 示例3: 一次性收集北京数据
```bash
python main.py --mode once --city 北京
```

### 示例4: 使用自定义配置
```bash
python main.py \
    --mode monitor \
    --city 深圳 \
    --db-path /data/air_quality.db \
    --interval 1
```

## API支持

### WAQI (World Air Quality Index)
- **API文档**: [https://aqicn.org/api/](https://aqicn.org/api/)
- **支持数据**: AQI, PM2.5, PM10, CO, NO2, O3, SO2
- **免费额度**: 每日1000次请求
- **特点**: 全球覆盖，数据质量高

### 直接SQL查询
```sql
-- 查看最近24小时数据
SELECT * FROM air_quality 
WHERE timestamp >= datetime('now', '-24 hours')
ORDER BY timestamp DESC;

-- 计算平均AQI
SELECT AVG(aqi) as avg_aqi, city 
FROM air_quality 
WHERE date(timestamp) = date('now')
GROUP BY city;

-- 空气质量等级分布
SELECT level, COUNT(*) as count
FROM air_quality 
WHERE timestamp >= datetime('now', '-7 days')
GROUP BY level;
```

## 日志和监控

程序会生成详细的日志文件 `air_quality_enhanced.log`，记录：
- 数据获取状态
- 数据库操作结果
- 错误和异常信息
- 程序运行状态
- 验证和重试操作

## 故障排除

### 常见问题

1. **API请求失败**
   - 检查API密钥是否正确
   - 确认网络连接正常
   - 查看API服务状态
   - 检查城市名称是否有效

2. **数据库错误**
   - 检查数据库文件权限
   - 确认磁盘空间充足
   - 验证数据格式正确性

3. **数据验证失败**
   - 检查API返回数据格式
   - 确认所有必需字段存在
   - 验证数据类型正确

### 调试模式

程序提供详细的调试信息：
```bash
# 启用调试日志
python main.py --log-level DEBUG
```

## 性能特点

- **内存优化**: 使用上下文管理器管理数据库连接
- **错误恢复**: 自动重试机制，提高数据收集成功率
- **资源管理**: 合理的超时设置和连接管理
- **数据完整性**: 完整的验证和错误处理

## 扩展功能

### 添加新API支持
1. 在 `fetch_data_from_api` 方法中添加新的API逻辑
2. 在 `parse_waqi_response` 方法中添加相应的数据解析
3. 更新API配置和错误处理

### 数据库增强
- 添加数据压缩
- 实现数据清理机制
- 支持数据导出功能

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request！

## 更新日志

### v2.0.0 (增强版)
- 添加完整的数据验证机制
- 实现增强的错误处理
- 增加数据库操作统计
- 支持模拟数据生成
- 改进日志记录机制
- 添加重试机制
