# 按城市分数据库功能说明

## 概述

本程序支持将不同城市的空气质量数据分开存储到独立的数据库文件中，便于数据管理和查询。

## 功能特性

### 1. 按城市分数据库存储
- 每个城市的数据存储在独立的SQLite数据库文件中
- 数据库文件命名格式：`data/air_quality_{城市名称}.db`
- 城市名称会自动标准化，移除特殊字符并转换为小写

### 2. 向后兼容
- 支持原有的统一数据库存储方式
- 通过配置参数可以切换存储方式

## 配置方法

### 环境变量配置
在 `.env` 文件中设置：

```bash
# 启用按城市分数据库（默认）
AQ_USE_CITY_DB=true

# 禁用按城市分数据库，使用统一数据库
AQ_USE_CITY_DB=false
```

### 命令行参数
```bash
# 启用按城市分数据库
./run.sh --use-city-db --city "北京"

# 禁用按城市分数据库
./run.sh --no-use-city-db --city "北京"
```

## 数据库文件结构

### 按城市分数据库
```
data/
├── air_quality_北京.db
├── air_quality_上海.db
├── air_quality_广州.db
└── ...
```

### 统一数据库
```
air_quality.db  # 包含所有城市的数据
```

## 使用示例

### 1. 为不同城市创建独立数据库
```bash
# 为北京创建独立数据库
./run.sh --mode once --city "北京" --use-city-db

# 为上海创建独立数据库
./run.sh --mode once --city "上海" --use-city-db
```

### 2. 使用统一数据库
```bash
# 所有城市数据存储在同一个文件中
./run.sh --mode once --city "广州" --no-use-city-db
```

### 3. 在监控模式中使用
```bash
# 按城市分数据库的定时监控
./run.sh --mode monitor --city "深圳" --use-city-db --interval 1
```

## 数据库查询

### 查询特定城市的数据
```bash
# 查询北京的数据
sqlite3 data/air_quality_北京.db "SELECT * FROM air_quality ORDER BY timestamp DESC LIMIT 10;"

# 查询上海的数据
sqlite3 data/air_quality_上海.db "SELECT city, aqi, level FROM air_quality WHERE aqi > 100;"
```

### 查询统一数据库中的数据
```bash
# 查询所有城市的数据
sqlite3 air_quality.db "SELECT city, COUNT(*) as count FROM air_quality GROUP BY city;"

# 查询特定时间段的数据
sqlite3 air_quality.db "SELECT * FROM air_quality WHERE timestamp > '2025-12-25' ORDER BY timestamp DESC;"
```

## 优势

### 按城市分数据库的优势：
1. **数据隔离**：不同城市的数据完全独立，避免互相影响
2. **性能提升**：单表数据量减少，查询速度更快
3. **便于维护**：可以针对特定城市进行数据备份、清理等操作
4. **并发友好**：多个进程可以同时访问不同城市的数据库
5. **灵活部署**：可以将不同城市的数据分布到不同的服务器

### 统一数据库的优势：
1. **简单管理**：只需要管理一个数据库文件
2. **跨城市查询**：方便进行城市间的数据对比和分析
3. **存储效率**：避免了数据库文件的重复开销

## 注意事项

1. **切换配置**：从按城市分数据库切换到统一数据库时，原有的分数据库文件不会自动合并
2. **数据迁移**：如需将分数据库的数据合并到统一数据库，需要手动进行数据迁移
3. **磁盘空间**：按城市分数据库可能会占用更多的磁盘空间
4. **城市名称标准化**：城市名称中的特殊字符会被替换为下划线，括号内容会被移除

## 城市名称标准化规则

- 移除括号及其内容：`北京（测试）` → `北京`
- 替换特殊字符为下划线：`New York` → `new_york`
- 转换为小写：`Shanghai` → `shanghai`

例如：
- `北京` → `air_quality_北京.db`
- `Shanghai` → `air_quality_shanghai.db`
- `New York` → `air_quality_new_york.db`
- `成都（四川）` → `air_quality_成都.db`
