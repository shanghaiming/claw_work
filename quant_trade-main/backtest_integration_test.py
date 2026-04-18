#!/usr/bin/env python3
"""
回测系统集成测试
测试：策略加载、回测执行、结果分析
"""

import sys
import os
import pandas as pd
import numpy as np

project_root = "/Users/chengming/.openclaw/workspace/quant_trade-main"
sys.path.insert(0, project_root)

print("="*80)
print("回测系统集成测试")
print("="*80)

# 1. 测试数据加载
print("\n1. 测试数据加载...")
data_dir = os.path.join(project_root, "data")
if os.path.exists(data_dir):
    print(f"✅ 数据目录存在: {data_dir}")
    
    # 检查数据文件
    import glob
    csv_files = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
    print(f"  发现 {len(csv_files)} 个CSV文件")
    
    if csv_files:
        # 尝试加载一个文件
        sample_file = csv_files[0]
        print(f"  示例文件: {os.path.relpath(sample_file, data_dir)}")
        try:
            df = pd.read_csv(sample_file)
            print(f"  ✅ 文件加载成功: {len(df)} 行, {len(df.columns)} 列")
            print(f"     列名: {list(df.columns)}")
            
            # 检查必要列
            required_cols = {'open', 'high', 'low', 'close'}
            available_cols = set(df.columns)
            missing = required_cols - available_cols
            if missing:
                print(f"  ⚠️  缺少必要列: {missing}")
            else:
                print(f"  ✅ 包含所有必要价格列")
                
        except Exception as e:
            print(f"  ❌ 文件加载失败: {e}")
    else:
        print(f"  ⚠️  未找到CSV文件")
else:
    print(f"❌ 数据目录不存在: {data_dir}")
    # 创建测试数据
    print("  创建模拟数据用于测试...")
    dates = pd.date_range('2025-01-01', periods=100, freq='D')
    test_data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'symbol': '000001.SZ'
    }, index=dates)

# 2. 测试策略加载
print("\n2. 测试策略加载...")

strategies_to_test = [
    ("ma_strategy", "MovingAverageStrategy"),
    ("simple_ma_strategy", "SimpleMovingAverageStrategy"),
    ("tradingview_strategy", "TradingViewStrategy"),
    ("price_action_strategy", "PriceActionStrategy"),
    ("transformer", "TransformerStrategy"),
]

loaded_strategies = []

for module_name, class_name in strategies_to_test:
    try:
        module = __import__(f"strategies.{module_name}", fromlist=[class_name])
        StrategyClass = getattr(module, class_name)
        loaded_strategies.append((module_name, class_name, StrategyClass))
        print(f"  ✅ {module_name}.{class_name}")
    except Exception as e:
        print(f"  ❌ {module_name}.{class_name}: {e}")

if not loaded_strategies:
    print("❌ 没有策略加载成功，测试终止")
    sys.exit(1)

# 3. 测试回测引擎
print("\n3. 测试回测引擎...")

try:
    from backtest.src.backtest.engine import BacktestEngine
    print("✅ BacktestEngine 导入成功")
    
    # 创建测试数据
    dates = pd.date_range('2025-01-01', periods=200, freq='D')
    test_data = pd.DataFrame({
        'open': np.random.randn(200).cumsum() + 100,
        'high': np.random.randn(200).cumsum() + 105,
        'low': np.random.randn(200).cumsum() + 95,
        'close': np.random.randn(200).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 200),
        'symbol': '000001.SZ'
    }, index=dates)
    
    print(f"  测试数据: {len(test_data)} 行")
    
    # 测试每个策略
    test_results = []
    
    for module_name, class_name, StrategyClass in loaded_strategies[:2]:  # 只测试前两个
        print(f"\n  --- 测试策略: {class_name} ---")
        
        try:
            # 创建回测引擎
            engine = BacktestEngine(test_data, StrategyClass, initial_cash=100000)
            
            # 策略参数
            if class_name == "MovingAverageStrategy":
                params = {'short_window': 5, 'long_window': 20}
            elif class_name == "SimpleMovingAverageStrategy":
                params = {'short_window': 3, 'long_window': 5}
            elif class_name == "TradingViewStrategy":
                params = {'atr_period': 14, 'multiplier': 3}
            elif class_name == "PriceActionStrategy":
                params = {}
            elif class_name == "TransformerStrategy":
                params = {}
            else:
                params = {}
            
            # 运行回测
            results = engine.run_backtest(params)
            
            if results:
                print(f"    ✅ 回测成功")
                print(f"      交易数: {results.get('total_trades', 0)}")
                print(f"      总收益: {results.get('total_return', 0):.2%}")
                print(f"      夏普比率: {results.get('sharpe_ratio', 0):.2f}")
                
                test_results.append({
                    'strategy': class_name,
                    'success': True,
                    'trades': results.get('total_trades', 0),
                    'return': results.get('total_return', 0),
                    'sharpe': results.get('sharpe_ratio', 0)
                })
            else:
                print(f"    ⚠️  回测无结果")
                test_results.append({
                    'strategy': class_name,
                    'success': False,
                    'error': '无结果'
                })
                
        except Exception as e:
            print(f"    ❌ 回测失败: {e}")
            test_results.append({
                'strategy': class_name,
                'success': False,
                'error': str(e)
            })
    
    # 总结回测结果
    print("\n  --- 回测结果汇总 ---")
    successful = sum(1 for r in test_results if r['success'])
    print(f"    成功: {successful}/{len(test_results)}")
    
    for result in test_results:
        if result['success']:
            print(f"    {result['strategy']}: {result['trades']}笔交易, 收益{result['return']:.2%}, 夏普{result['sharpe']:.2f}")
        else:
            print(f"    {result['strategy']}: 失败 - {result['error']}")
            
except Exception as e:
    print(f"❌ 回测引擎测试失败: {e}")
    import traceback
    traceback.print_exc()

# 4. 测试 backtest/main.py 命令行接口
print("\n4. 测试命令行接口...")

main_script = os.path.join(project_root, "backtest", "main.py")
if os.path.exists(main_script):
    print(f"✅ main.py 存在: {main_script}")
    
    # 测试 --list-strategies
    import subprocess
    commands = [
        ["--list-strategies"],
        ["--help"],
    ]
    
    for cmd_args in commands:
        cmd = ["/Users/chengming/.openclaw/workspace/quant_env/bin/python", 
               main_script] + cmd_args
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, 
                                  cwd=project_root, timeout=30)
            
            print(f"\n  命令: {' '.join(cmd_args)}")
            if result.returncode == 0:
                print(f"    ✅ 执行成功")
                # 显示部分输出
                output_lines = result.stdout.strip().split('\n')
                for line in output_lines[:5]:
                    if line.strip():
                        print(f"      {line}")
                if len(output_lines) > 5:
                    print(f"      ... (还有{len(output_lines)-5}行)")
            else:
                print(f"    ❌ 执行失败 (退出码: {result.returncode})")
                if result.stderr:
                    print(f"      错误: {result.stderr[:200]}")
                    
        except subprocess.TimeoutExpired:
            print(f"    ⚠️  命令超时")
        except Exception as e:
            print(f"    ❌ 执行异常: {e}")
else:
    print(f"❌ main.py 不存在")

# 5. 测试回测结果分析
print("\n5. 测试回测结果分析...")

try:
    from backtest.src.backtest.performance import PerformanceAnalyzer
    print("✅ PerformanceAnalyzer 导入成功")
    
    # 创建示例回测结果
    example_results = {
        'initial_capital': 100000,
        'final_capital': 110000,
        'total_return': 0.10,
        'annual_return': 0.15,
        'sharpe_ratio': 1.2,
        'max_drawdown': -0.08,
        'total_trades': 25,
        'win_rate': 0.60,
        'profit_factor': 1.8,
        'trades': [
            {'entry_time': '2025-01-01', 'exit_time': '2025-01-10', 'pnl': 500},
            {'entry_time': '2025-01-15', 'exit_time': '2025-01-20', 'pnl': -200},
        ]
    }
    
    analyzer = PerformanceAnalyzer(example_results)
    print(f"  ✅ 分析器实例化成功")
    
    # 测试分析方法
    stats = analyzer.get_summary_statistics()
    print(f"  ✅ 获取统计摘要: {len(stats)} 项指标")
    
    # 显示关键指标
    key_metrics = ['total_return', 'sharpe_ratio', 'max_drawdown', 'win_rate']
    for metric in key_metrics:
        if metric in stats:
            value = stats[metric]
            if isinstance(value, float):
                if 'return' in metric or 'rate' in metric:
                    print(f"     {metric}: {value:.2%}")
                else:
                    print(f"     {metric}: {value:.2f}")
            else:
                print(f"     {metric}: {value}")
                
except Exception as e:
    print(f"❌ 回测结果分析测试失败: {e}")

print("\n" + "="*80)
print("回测系统集成测试完成")
print("="*80)