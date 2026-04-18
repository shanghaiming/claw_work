# QuantTrade 量化交易平台

## 📋 项目概述

QuantTrade是一个完整的量化交易平台，包含策略开发、回测系统、选股平台和可视化看板。平台使用统一的策略基类，支持多种数据频率（日线、周线、5分钟、30分钟）。

## 🚀 快速开始

### 环境配置

```bash
# 切换到项目目录
cd /Users/chengming/.openclaw/workspace/quant_trade-main

# 激活虚拟环境
source /Users/chengming/.openclaw/workspace/quant_env/bin/activate

# 安装依赖
pip install pandas numpy matplotlib flask
```

### 平台CLI工具

平台提供了功能强大的命令行工具 `cli.py`：

```bash
# 显示帮助信息
python cli.py --help

# 列出所有可用策略
python cli.py strategy list

# 查看策略详细信息
python cli.py strategy list --verbose

# 查看数据目录信息
python cli.py data info

# 列出日线数据可用股票
python cli.py data list --timeframe daily --limit 20

# 显示股票数据
python cli.py data show --symbol 000001.SZ --timeframe daily --limit 10

# 执行回测（使用真实数据）
python cli.py backtest --strategy simple_ma_strategy --symbol 000001.SZ --timeframe daily

# 使用自定义参数回测
python cli.py backtest --strategy ma_strategy --symbol 000001.SZ --params '{"short_window":5,"long_window":20}'

# 启动看板（Flask Web应用）
python cli.py dashboard start --port 5000
```

### 传统回测工具

```bash
# 列出所有策略
python backtest/main.py --list-strategies

# 运行简单移动平均策略
python backtest/main.py --strategy simple_ma_strategy
```

## 📁 项目结构

```
quant_trade-main/
├── cli.py                      # 🆕 统一命令行工具
├── PLATFORM_GUIDE.md           # 详细平台指南
├── strategies/                 # 策略目录 (159个文件)
│   ├── base_strategy.py       # 策略基类
│   ├── ma_strategy.py        # 移动平均策略
│   ├── simple_ma_strategy.py # 简化移动平均策略
│   └── ...
├── backtest/                  # 回测系统
│   ├── main.py               # 传统回测主程序
│   ├── runner.py             # 策略发现器
│   └── src/backtest/         # 回测引擎核心
├── dashboard/                 # 可视化看板
│   ├── stock_platform_visual_t.py  # Flask看板（推荐）
│   └── quant_dashboard.py    # Dash看板（备选）
├── data/                      # 数据目录
│   ├── daily_data2/          # 日线数据 (5,136个CSV)
│   ├── week_data2/           # 周线数据 (5,136个CSV)
│   ├── 5min/                 # 5分钟数据
│   └── 30min/                # 30分钟数据
└── core/                      # 核心模块
```

## 📊 数据说明

### 数据格式
所有CSV文件包含以下列：
- `ts_code`: 股票代码 (如 000001.SZ)
- `trade_date`: 交易日期 (YYYYMMDD格式)
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价  
- `close`: 收盘价
- `pre_close`: 前收盘价
- `change`: 涨跌额
- `pct_chg`: 涨跌幅
- `vol`: 成交量
- `amount`: 成交额

### 数据路径
- **日线数据**: `data/daily_data2/{股票代码}.csv`
- **周线数据**: `data/week_data2/{股票代码}.csv`
- **5分钟数据**: `data/5min/{股票代码}_analysis.csv`
- **30分钟数据**: `data/30min/{股票代码}_analysis.csv`

### 数据加载示例

```python
import pandas as pd

def load_stock_data(code='000001.SZ', timeframe='daily'):
    """加载股票数据"""
    if timeframe == 'daily':
        filepath = f'data/daily_data2/{code}.csv'
    elif timeframe == 'weekly':
        filepath = f'data/week_data2/{code}.csv'
    
    df = pd.read_csv(filepath)
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.set_index('trade_date', inplace=True)
    return df
```

## 🤖 策略系统

### 策略基类
所有策略继承自 `BaseStrategy`：

```python
from strategies.base_strategy import BaseStrategy

class MyStrategy(BaseStrategy):
    def __init__(self, data, params=None):
        super().__init__(data, params)
        
    def generate_signals(self):
        """返回信号列表，格式统一"""
        signals = []
        # 策略逻辑
        signals.append({
            'timestamp': self.data.index[i],
            'action': 'buy',  # 'buy' 或 'sell'
            'symbol': '000001.SZ',
            'price': 100.0,
            'quantity': 100  # 可选
        })
        return signals
```

### 可用策略
- `MovingAverageStrategy` - 移动平均策略
- `SimpleMovingAverageStrategy` - 简化移动平均策略  
- `TradingViewStrategy` - TradingView风格策略
- `PriceActionStrategy` - 价格行为策略
- `TransformerStrategy` - Transformer深度学习策略

## 🔧 回测系统

### CLI回测示例

```bash
# 使用日线数据回测移动平均策略
python cli.py backtest \
  --strategy ma_strategy \
  --symbol 000001.SZ \
  --timeframe daily \
  --params '{"short_window":5,"long_window":20}' \
  --initial-cash 100000 \
  --plot

# 指定日期范围
python cli.py backtest \
  --strategy simple_ma_strategy \
  --symbol 000001.SZ \
  --start-date 20250101 \
  --end-date 20250630
```

### Python API回测

```python
import pandas as pd
from backtest.src.backtest.engine import BacktestEngine
from strategies.simple_ma_strategy import SimpleMovingAverageStrategy

# 加载数据
data = pd.read_csv('data/daily_data2/000001.SZ.csv')
data['trade_date'] = pd.to_datetime(data['trade_date'], format='%Y%m%d')
data.set_index('trade_date', inplace=True)

# 创建回测引擎
engine = BacktestEngine(data, SimpleMovingAverageStrategy, initial_cash=100000)

# 运行回测
results = engine.run_backtest({'short_window': 3, 'long_window': 5})

# 查看结果
print(f"总收益: {results.get('total_return', 0):.2%}")
print(f"交易次数: {results.get('total_trades', 0)}")
print(f"最大回撤: {results.get('max_drawdown', 0):.2%}")
```

## 📈 可视化看板

### Flask看板（推荐）

```bash
# 启动Flask看板
python cli.py dashboard start

# 或直接运行
python dashboard/stock_platform_visual_t.py

# 访问地址: http://127.0.0.1:5000
```

### 看板功能
1. **股票数据查看** - K线图、技术指标
2. **回测功能** - 策略选择、参数配置、实时回测
3. **选股功能** - 多种选股方法、批量分析
4. **数据分页** - 支持大量数据分页加载

## 🛠️ 开发工具

### 策略检查工具

```bash
# 检查所有策略是否继承BaseStrategy
python check_strategy_inheritance.py

# 修复策略导入问题
python fix_strategy_imports.py

# 严格导入测试
python strict_test.py
```

### 回测集成测试

```bash
# 运行完整集成测试
python backtest_integration_test.py
```

## ⚠️ 故障排除

### 常见问题

1. **策略导入失败**
   ```bash
   python fix_strategy_imports.py
   ```

2. **缺少依赖包**
   ```bash
   pip install pandas numpy talib torch transformers
   ```

3. **数据文件不存在**
   - 检查数据目录路径
   - 确认股票代码格式正确
   - 确保文件扩展名正确 (.csv)

4. **回测无信号**
   - 检查策略参数
   - 验证数据格式
   - 调试策略逻辑

### 环境问题

```bash
# 检查Python版本
python --version

# 检查依赖
pip list | grep -E "pandas|numpy|flask"

# 检查虚拟环境
which python
```

## 📝 开发指南

### 添加新策略
1. 在 `strategies/` 目录创建新文件
2. 继承 `BaseStrategy` 基类
3. 实现 `generate_signals()` 方法
4. 可选：实现 `get_default_params()` 方法

### 扩展CLI功能
1. 修改 `cli.py` 添加新命令
2. 更新参数解析器
3. 实现命令处理函数

### 自定义看板
1. 修改 `dashboard/stock_platform_visual_t.py`
2. 添加新的API端点
3. 更新前端模板

## 🔮 后续计划

1. **实时数据接入** - 集成实时行情
2. **机器学习策略** - 深度学习模型
3. **风险管理系统** - 风控模块
4. **自动调参** - 参数优化
5. **多账户管理** - 多账户回测

## 📞 技术支持

- **平台状态**: ✅ 核心功能可用
- **最后更新**: 2025-04-15
- **版本**: v1.0.0
- **CLI工具**: ✅ 完整命令行支持
- **真实数据**: ✅ 日线、周线数据支持
- **可视化**: ✅ Flask看板

如需技术支持或功能建议，请联系平台开发者。