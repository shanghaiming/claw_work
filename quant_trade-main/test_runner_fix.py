#!/usr/bin/env python3
"""
测试修改后的BacktestRunner
"""
import sys
import os

project_root = "/Users/chengming/.openclaw/workspace/quant_trade-main"
sys.path.insert(0, project_root)

print("🔍 测试BacktestRunner修改")
print("=" * 60)

# 测试1: 创建实例但不加载策略
print("\n1. 测试按需加载策略...")
try:
    from backtest.runner import BacktestRunner
    
    # 创建实例时不加载所有策略
    runner = BacktestRunner(load_all=False)
    print(f"   ✅ BacktestRunner实例创建成功")
    print(f"     已加载策略数: {len(runner.strategies)} (应该为0)")
    
    # 加载单个策略
    strategy_cls = runner.load_strategy('ma_strategy')
    if strategy_cls:
        print(f"   ✅ ma_strategy加载成功: {strategy_cls.__name__}")
        print(f"     现在已加载策略数: {len(runner.strategies)} (应该为1)")
    else:
        print(f"   ❌ ma_strategy加载失败")
        
    # 测试另一个策略
    strategy_cls2 = runner.load_strategy('simple_ma_strategy')
    if strategy_cls2:
        print(f"   ✅ simple_ma_strategy加载成功: {strategy_cls2.__name__}")
        print(f"     现在已加载策略数: {len(runner.strategies)} (应该为2)")
    else:
        print(f"   ❌ simple_ma_strategy加载失败")
        
except Exception as e:
    print(f"   ❌ 测试失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 测试有依赖的策略
print("\n2. 测试有依赖的策略...")
try:
    runner2 = BacktestRunner(load_all=False)
    
    # 测试tradingview_strategy (依赖talib)
    strategy_cls = runner2.load_strategy('tradingview_strategy')
    if strategy_cls:
        print(f"   ✅ tradingview_strategy加载成功")
    else:
        print(f"   ❌ tradingview_strategy加载失败 (可能依赖缺失)")
        
    # 测试csv_auto_select (依赖tqdm)
    strategy_cls2 = runner2.load_strategy('csv_auto_select')
    if strategy_cls2:
        print(f"   ✅ csv_auto_select加载成功")
    else:
        print(f"   ❌ csv_auto_select加载失败 (可能依赖缺失)")
        
except Exception as e:
    print(f"   ❌ 测试失败: {e}")

# 测试3: 测试list_strategies方法
print("\n3. 测试list_strategies方法...")
try:
    runner3 = BacktestRunner(load_all=False)
    
    # 先加载一个策略
    runner3.load_strategy('ma_strategy')
    
    # 列出策略
    strategies = runner3.list_strategies()
    print(f"   list_strategies返回: {len(strategies)} 个策略")
    print(f"     策略列表: {strategies[:5]}...")
    
except Exception as e:
    print(f"   ❌ 测试失败: {e}")

# 测试4: 测试load_all_strategies方法
print("\n4. 测试load_all_strategies方法...")
try:
    runner4 = BacktestRunner(load_all=False)
    
    all_strategies = runner4.load_all_strategies()
    print(f"   ✅ load_all_strategies成功")
    print(f"     加载策略数: {len(all_strategies)}")
    
    # 检查一些关键策略
    key_strategies = ['ma_strategy', 'simple_ma_strategy', 'tradingview_strategy', 'csv_auto_select']
    for strategy in key_strategies:
        if strategy in all_strategies:
            print(f"     ✅ {strategy}: 已加载")
        else:
            print(f"     ❌ {strategy}: 未加载")
            
except Exception as e:
    print(f"   ❌ 测试失败: {e}")

print("\n" + "=" * 60)
print("测试完成")