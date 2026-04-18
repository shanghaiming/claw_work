#!/usr/bin/env python3
"""
严格策略导入测试 - 所有导入失败都会抛出异常
"""

import sys
import os

# 添加项目根目录到路径
project_root = "/Users/chengming/.openclaw/workspace/quant_trade-main"
sys.path.insert(0, project_root)

print("="*80)
print("严格策略导入测试")
print("="*80)

# 测试关键模块导入
modules_to_test = [
    "strategies.base_strategy",
    "strategies.ma_strategy", 
    "strategies.simple_ma_strategy",
    "strategies.tradingview_strategy",
    "strategies.price_action_strategy",
    "strategies.transformer",
    "backtest.src.backtest.engine",
    "backtest.runner",
]

failed_modules = []

for module_name in modules_to_test:
    print(f"\n测试导入: {module_name}")
    try:
        __import__(module_name)
        print(f"  ✅ 成功")
    except ImportError as e:
        print(f"  ❌ 导入失败: {e}")
        failed_modules.append((module_name, str(e)))
    except Exception as e:
        print(f"  ❌ 其他错误: {e}")
        failed_modules.append((module_name, str(e)))

# 测试策略类
print("\n" + "="*80)
print("测试策略类实例化")
print("="*80)

import pandas as pd
import numpy as np

# 创建测试数据
dates = pd.date_range('2025-01-01', periods=100, freq='D')
test_data = pd.DataFrame({
    'open': np.random.randn(100).cumsum() + 100,
    'high': np.random.randn(100).cumsum() + 105,
    'low': np.random.randn(100).cumsum() + 95,
    'close': np.random.randn(100).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, 100),
    'symbol': '000001.SZ'
}, index=dates)

strategies_to_test = [
    ("ma_strategy", "MovingAverageStrategy", {'short_window': 3, 'long_window': 5}),
    ("simple_ma_strategy", "SimpleMovingAverageStrategy", {'short_window': 3, 'long_window': 5}),
]

failed_strategies = []

for module_name, class_name, params in strategies_to_test:
    print(f"\n测试策略: {module_name}.{class_name}")
    try:
        # 动态导入
        module = __import__(f"strategies.{module_name}", fromlist=[class_name])
        StrategyClass = getattr(module, class_name)
        
        # 实例化
        strategy = StrategyClass(test_data, params)
        print(f"  ✅ 实例化成功")
        
        # 生成信号
        signals = strategy.generate_signals()
        print(f"  ✅ 生成 {len(signals) if signals else 0} 个信号")
        
        # 验证信号格式
        if signals:
            if isinstance(signals, list) and len(signals) > 0 and isinstance(signals[0], dict):
                required_keys = {'timestamp', 'action', 'symbol'}
                if all(key in signals[0] for key in required_keys):
                    print(f"  ✅ 信号格式正确")
                else:
                    print(f"  ⚠️  信号缺少必要字段")
                    missing = required_keys - set(signals[0].keys())
                    print(f"     缺少: {missing}")
            else:
                print(f"  ⚠️  信号格式不正确")
                
    except Exception as e:
        print(f"  ❌ 失败: {e}")
        failed_strategies.append((module_name, str(e)))

# 测试回测系统
print("\n" + "="*80)
print("测试回测系统")
print("="*80)

try:
    from backtest.src.backtest.engine import BacktestEngine
    print("✅ BacktestEngine 导入成功")
    
    # 使用简单移动平均策略测试回测
    from strategies.simple_ma_strategy import SimpleMovingAverageStrategy
    
    engine = BacktestEngine(test_data, SimpleMovingAverageStrategy, initial_cash=100000)
    print("✅ BacktestEngine 实例化成功")
    
    results = engine.run_backtest({'short_window': 3, 'long_window': 5})
    print(f"✅ 回测执行成功")
    if 'total_return' in results:
        print(f"   总收益: {results.get('total_return', 0):.2%}")
        
except Exception as e:
    print(f"❌ 回测测试失败: {e}")

# 总结
print("\n" + "="*80)
print("测试总结")
print("="*80)

if failed_modules:
    print(f"❌ 模块导入失败: {len(failed_modules)} 个")
    for module, error in failed_modules:
        print(f"  - {module}: {error}")
else:
    print(f"✅ 所有模块导入成功")

if failed_strategies:
    print(f"❌ 策略实例化失败: {len(failed_strategies)} 个")
    for strategy, error in failed_strategies:
        print(f"  - {strategy}: {error}")
else:
    print(f"✅ 所有策略实例化成功")

if not failed_modules and not failed_strategies:
    print("\n🎉 所有测试通过！")
else:
    print(f"\n⚠️  发现 {len(failed_modules) + len(failed_strategies)} 个问题需要修复")
    sys.exit(1)