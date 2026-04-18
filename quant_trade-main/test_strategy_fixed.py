import sys
import os
import importlib

# 添加当前目录到路径
sys.path.insert(0, '/Users/chengming/.openclaw/workspace/quant_trade-main')

print("开始测试策略导入...")

# 测试 discover_strategies 函数
try:
    import strategies
    print("✅ strategies 模块导入成功")
    
    # 启用策略发现
    os.environ['ENABLE_STRATEGY_DISCOVERY'] = '1'
    
    # 重新导入以触发策略发现
    import importlib
    importlib.reload(strategies)
    
    print(f"\n发现 {len(strategies.available_strategies)} 个可用策略:")
    for name in strategies.available_strategies:
        print(f"  - {name}")
        
except Exception as e:
    print(f"❌ 策略发现失败: {e}")

# 测试回测接口
print("\n" + "="*50)
print("测试回测接口...")
print("="*50)

# 创建测试数据
import pandas as pd
import numpy as np

# 创建模拟数据
dates = pd.date_range('2025-01-01', periods=100, freq='D')
test_data = pd.DataFrame({
    'open': np.random.randn(100).cumsum() + 100,
    'high': np.random.randn(100).cumsum() + 105,
    'low': np.random.randn(100).cumsum() + 95,
    'close': np.random.randn(100).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, 100),
    'symbol': '000001.SZ'
}, index=dates)

# 测试具体策略
test_cases = [
    ('ma_strategy', {'short_window': 3, 'long_window': 5}),
    ('price_action_strategy', {}),
    ('tradingview_strategy', {'atr_period': 10, 'multiplier': 3}),
    ('transformer', {}),
    ('simple_ma_strategy', {'short_window': 3, 'long_window': 5})
]

for strategy_name, params in test_cases:
    print(f"\n测试策略: {strategy_name}")
    try:
        # 获取策略类
        if strategy_name in strategies.available_strategies:
            StrategyClass = strategies.available_strategies[strategy_name]
        else:
            print(f"  ❌ 策略未发现: {strategy_name}")
            continue
            
        # 实例化策略
        strategy = StrategyClass(test_data, params)
        
        # 生成信号
        signals = strategy.generate_signals()
        
        if signals:
            print(f"  ✅ 信号生成成功，数量: {len(signals)}")
            # 检查信号格式
            if isinstance(signals, list):
                if len(signals) > 0 and isinstance(signals[0], dict):
                    print(f"  ✅ 信号格式正确 (List[Dict])")
                    # 显示前几个信号
                    for i, signal in enumerate(signals[:3]):
                        print(f"    信号{i+1}: {signal}")
                else:
                    print(f"  ⚠️  信号格式不是List[Dict]")
            else:
                print(f"  ⚠️  信号格式不是列表")
        else:
            print(f"  ⚠️  未生成信号")
            
    except Exception as e:
        print(f"  ❌ 测试失败: {e}")

print("\n" + "="*50)
print("策略导入测试完成")
print("="*50)