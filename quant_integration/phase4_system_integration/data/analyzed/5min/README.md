# 量化交易数据目录

## 目录结构
```
./data/analyzed/5min/
├── 000001.SZ.csv     # 股票数据文件（平安银行）
├── 000002.SZ.csv     # 股票数据文件（万科A）
├── 000063.SZ.csv     # 股票数据文件（中兴通讯）
└── ...
```

## 数据格式要求

每个CSV文件必须包含以下列：

### 必需列
- `trade_date`: 交易日期时间（格式: YYYY-MM-DD HH:MM:SS）
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价

### 可选列
- `volume`: 成交量
- `amount`: 成交额
- 各种技术指标列（如macd, rsi, ma5等）

### 文件命名规则
- 格式: `股票代码.csv`
- 示例: `000001.SZ.csv`, `000002.SZ.csv`

## 获取数据

### 方式1: 使用Tushare等数据API
```python
import tushare as ts

# 设置token
ts.set_token('your_token_here')
pro = ts.pro_api()

# 获取5分钟数据
df = pro.ticks('000001.SZ', start_date='2024-01-01', end_date='2024-01-31')
df.to_csv('000001.SZ.csv', index=False)
```

### 方式2: 使用示例数据
本目录已包含示例数据文件，可用于测试回测系统。

## 配置

在运行回测时，可以通过以下方式指定数据目录：

```bash
# 使用默认目录
python main_fixed.py

# 指定数据目录
python main_fixed.py --data-dir ./your_data_directory

# 指定时间周期
python main_fixed.py --timeframe 5min
```
