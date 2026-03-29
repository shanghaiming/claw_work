#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略整合框架使用示例

展示如何:
1. 使用策略管理器注册和运行策略
2. 集成移动平均策略
3. 集成价格行为策略
4. 比较策略性能
5. 生成报告
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入策略管理器
from managers.strategy_manager import StrategyManager

# 尝试导入策略适配器
try:
    from integrations.ma_strategy_adapter import register_ma_strategies
    MA_ADAPTER_AVAILABLE = True
except ImportError:
    MA_ADAPTER_AVAILABLE = False
    print("⚠️ 移动平均适配器不可用")

try:
    from integrations.price_action_integration import register_price_action_strategies
    PRICE_ACTION_AVAILABLE = True
except ImportError:
    PRICE_ACTION_AVAILABLE = False
    print("⚠️ 价格行为集成不可用")


def generate_sample_data():
    """生成示例数据"""
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    
    data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'symbol': 'AAPL'
    }, index=dates)
    
    print(f"生成示例数据: {len(data)} 行")
    print(f"时间范围: {data.index.min()} 到 {data.index.max()}")
    
    return data


def example_1_basic_usage():
    """示例1: 基本使用"""
    print("\n" + "="*60)
    print("示例1: 基本使用 - 创建和运行简单策略")
    print("="*60)
    
    # 生成数据
    data = generate_sample_data()
    
    # 创建策略管理器
    manager = StrategyManager(
        name="BasicExampleManager",
        config_dir="./examples/configs",
        results_dir="./examples/results"
    )
    
    # 定义简单策略
    from core.unified_strategy_base import UnifiedStrategyBase
    
    class SimpleBuyHoldStrategy(UnifiedStrategyBase):
        def get_default_params(self):
            return {'hold_period': 10, 'initial_buy': True}
        
        def generate_signals(self):
            signals = []
            
            # 初始买入
            if self.params['initial_buy']:
                signals.append({
                    'timestamp': self.data.index[0],
                    'action': 'buy',
                    'price': self.data['close'].iloc[0],
                    'confidence': 0.8,
                    'type': 'initial_buy'
                })
            
            # 定期调整
            hold_period = self.params['hold_period']
            for i in range(hold_period, len(self.data), hold_period):
                if i < len(self.data):
                    signals.append({
                        'timestamp': self.data.index[i],
                        'action': 'adjust',
                        'price': self.data['close'].iloc[i],
                        'confidence': 0.6,
                        'type': 'periodic_adjustment'
                    })
            
            return signals
    
    # 注册策略
    manager.register_strategy(
        name="SimpleBuyHold",
        strategy_class=SimpleBuyHoldStrategy,
        default_config={'hold_period': 10, 'description': '简单买入持有策略'},
        description="简单的买入持有策略示例"
    )
    
    # 运行策略
    result = manager.run_strategy(
        strategy_name="SimpleBuyHold",
        data=data,
        save_results=True
    )
    
    print(f"\n✅ 策略执行完成:")
    print(f"  策略: SimpleBuyHold")
    print(f"  信号数量: {result.get('signal_count', 0)}")
    print(f"  执行时间: {result.get('execution_time', 0):.3f}秒")
    
    # 生成报告
    report = manager.generate_report(report_format='text')
    print(f"\n📊 执行报告:")
    print(report)
    
    return True


def example_2_ma_strategy_integration():
    """示例2: 移动平均策略集成"""
    if not MA_ADAPTER_AVAILABLE:
        print("\n⚠️ 移动平均适配器不可用，跳过示例2")
        return False
    
    print("\n" + "="*60)
    print("示例2: 移动平均策略集成")
    print("="*60)
    
    # 生成数据
    data = generate_sample_data()
    
    # 创建策略管理器
    manager = StrategyManager(
        name="MAExampleManager",
        config_dir="./examples/ma_configs",
        results_dir="./examples/ma_results"
    )
    
    # 注册移动平均策略
    register_ma_strategies(manager)
    
    print("\n已注册策略:")
    manager.print_registered_strategies()
    
    # 运行移动平均策略（不同参数）
    results = {}
    
    print("\n📈 测试不同参数的移动平均策略:")
    
    # 测试1: 快速均线
    result1 = manager.run_strategy(
        strategy_name="MovingAverageAdapter",
        data=data,
        config={
            'short_window': 5,
            'long_window': 20,
            'threshold': 0.01
        },
        instance_name="MA_Fast"
    )
    results['MA_Fast'] = result1
    
    # 测试2: 慢速均线
    result2 = manager.run_strategy(
        strategy_name="MovingAverageAdapter",
        data=data,
        config={
            'short_window': 10,
            'long_window': 30,
            'threshold': 0.015
        },
        instance_name="MA_Slow"
    )
    results['MA_Slow'] = result2
    
    # 比较性能
    print("\n📊 策略性能比较:")
    manager.compare_strategies(['MA_Fast', 'MA_Slow'])
    
    # 显示结果摘要
    print("\n📈 结果摘要:")
    for name, result in results.items():
        print(f"  {name}: {result.get('signal_count', 0)}信号, "
              f"{result.get('execution_time', 0):.3f}秒")
    
    return True


def example_3_price_action_integration():
    """示例3: 价格行为策略集成"""
    if not PRICE_ACTION_AVAILABLE:
        print("\n⚠️ 价格行为集成不可用，跳过示例3")
        return False
    
    print("\n" + "="*60)
    print("示例3: 价格行为策略集成")
    print("="*60)
    
    # 生成数据
    data = generate_sample_data()
    
    # 创建策略管理器
    manager = StrategyManager(
        name="PriceActionExampleManager",
        config_dir="./examples/pa_configs",
        results_dir="./examples/pa_results"
    )
    
    # 注册价格行为策略
    register_price_action_strategies(manager)
    
    print("\n已注册策略:")
    manager.print_registered_strategies()
    
    # 运行价格行为策略
    print("\n📈 运行价格行为策略:")
    
    result = manager.run_strategy(
        strategy_name="PriceActionSignal",
        data=data,
        config={
            'signal_type': 'MACDDivergence',
            'signal_params': {
                'fast_period': 12,
                'slow_period': 26,
                'signal_period': 9,
                'delay_bars': 2
            },
            'window_size': 80,
            'step': 15
        },
        instance_name="MACD_Divergence"
    )
    
    print(f"\n✅ MACD背离策略执行完成:")
    print(f"  信号数量: {result.get('signal_count', 0)}")
    print(f"  执行时间: {result.get('execution_time', 0):.3f}秒")
    
    # 运行多信号策略
    print("\n📈 运行多信号策略:")
    
    result2 = manager.run_strategy(
        strategy_name="MultiPriceAction",
        data=data,
        config={
            'signal_definitions': [
                {
                    'type': 'MACDDivergence',
                    'params': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}
                },
                {
                    'type': 'MACDDivergence',
                    'params': {'fast_period': 6, 'slow_period': 13, 'signal_period': 5}
                }
            ],
            'combination_method': 'voting',
            'window_size': 80,
            'step': 15
        },
        instance_name="Multi_MACD"
    )
    
    print(f"\n✅ 多MACD策略执行完成:")
    print(f"  信号数量: {result2.get('signal_count', 0)}")
    print(f"  执行时间: {result2.get('execution_time', 0):.3f}秒")
    
    return True


def example_4_complete_workflow():
    """示例4: 完整工作流程"""
    print("\n" + "="*60)
    print("示例4: 完整工作流程 - 集成所有策略")
    print("="*60)
    
    # 生成更多数据
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(200).cumsum() + 100,
        'high': np.random.randn(200).cumsum() + 105,
        'low': np.random.randn(200).cumsum() + 95,
        'close': np.random.randn(200).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 200),
        'symbol': 'AAPL'
    }, index=dates)
    
    print(f"生成工作流数据: {len(data)} 行")
    
    # 创建综合策略管理器
    manager = StrategyManager(
        name="CompleteWorkflowManager",
        config_dir="./examples/workflow_configs",
        results_dir="./examples/workflow_results"
    )
    
    # 注册所有可用策略
    strategies_count = 0
    
    # 注册简单策略
    from core.unified_strategy_base import UnifiedStrategyBase
    
    class MomentumStrategy(UnifiedStrategyBase):
        def get_default_params(self):
            return {'momentum_period': 20, 'threshold': 0.05}
        
        def generate_signals(self):
            signals = []
            prices = self.data['close']
            
            if len(prices) >= self.params['momentum_period']:
                momentum = prices.pct_change(self.params['momentum_period'])
                
                for i in range(self.params['momentum_period'], len(prices)):
                    mom = momentum.iloc[i]
                    
                    if mom > self.params['threshold']:
                        signals.append({
                            'timestamp': self.data.index[i],
                            'action': 'buy',
                            'price': prices.iloc[i],
                            'confidence': 0.7,
                            'type': 'momentum_buy'
                        })
                    elif mom < -self.params['threshold']:
                        signals.append({
                            'timestamp': self.data.index[i],
                            'action': 'sell',
                            'price': prices.iloc[i],
                            'confidence': 0.7,
                            'type': 'momentum_sell'
                        })
            
            return signals
    
    manager.register_strategy(
        name="Momentum",
        strategy_class=MomentumStrategy,
        default_config={'momentum_period': 20, 'threshold': 0.05},
        description="动量策略"
    )
    strategies_count += 1
    
    # 注册移动平均策略
    if MA_ADAPTER_AVAILABLE:
        register_ma_strategies(manager)
        strategies_count += 2
    
    # 注册价格行为策略
    if PRICE_ACTION_AVAILABLE:
        register_price_action_strategies(manager)
        strategies_count += 2
    
    print(f"\n总共注册了 {strategies_count} 个策略")
    
    # 运行所有策略
    print(f"\n🚀 运行所有策略...")
    all_results = manager.run_all_strategies(
        data=data,
        exclude=[],
        save_results=True
    )
    
    # 生成综合报告
    print(f"\n📊 生成综合报告...")
    
    # Markdown报告
    md_report = manager.generate_report(report_format='markdown')
    md_file = "./examples/complete_workflow_report.md"
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write("# 完整工作流程测试报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**测试数据**: {len(data)} 行\n\n")
        f.write(f"**注册策略**: {len(manager.strategies)} 个\n\n")
        f.write(f"**成功执行**: {len(all_results)} 个\n\n")
        f.write("## 详细结果\n\n")
        f.write(md_report)
    
    # 文本摘要
    print(f"\n📈 工作流执行摘要:")
    print(f"  测试数据: {len(data)} 行")
    print(f"  注册策略: {len(manager.strategies)} 个")
    print(f"  成功执行: {len(all_results)} 个")
    
    successful = [name for name, result in all_results.items() if 'error' not in result]
    total_signals = sum(result.get('signal_count', 0) for result in all_results.values())
    
    print(f"  总信号数: {total_signals}")
    print(f"  平均每策略: {total_signals/len(successful) if successful else 0:.1f} 信号")
    
    # 显示最佳策略
    if successful:
        best_strategy = max(
            [(name, result.get('signal_count', 0)) for name, result in all_results.items() 
             if name in successful],
            key=lambda x: x[1],
            default=(None, 0)
        )
        
        if best_strategy[0]:
            print(f"  信号最多: {best_strategy[0]} ({best_strategy[1]} 信号)")
    
    print(f"\n📄 报告文件: {md_file}")
    
    return True


def main():
    """运行所有示例"""
    print("="*60)
    print("策略整合框架使用示例")
    print("="*60)
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 创建示例目录
    os.makedirs("./examples", exist_ok=True)
    
    # 运行示例
    examples = [
        ("基本使用", example_1_basic_usage),
        ("移动平均策略集成", example_2_ma_strategy_integration),
        ("价格行为策略集成", example_3_price_action_integration),
        ("完整工作流程", example_4_complete_workflow)
    ]
    
    results = []
    
    for name, example_func in examples:
        try:
            print(f"\n▶️ 运行示例: {name}")
            success = example_func()
            results.append((name, success))
            
            if success:
                print(f"✅ 示例 '{name}' 完成")
            else:
                print(f"⚠️ 示例 '{name}' 跳过或失败")
                
        except Exception as e:
            print(f"❌ 示例 '{name}' 出错: {e}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("示例运行结果汇总")
    print("="*60)
    
    successful = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "✅ 完成" if success else "❌ 失败/跳过"
        print(f"  {name}: {status}")
    
    print(f"\n总计: {successful}/{total} 个示例成功")
    
    # 使用说明
    print("\n" + "="*60)
    print("快速开始指南")
    print("="*60)
    
    print("""
1. 导入策略管理器:
   from managers.strategy_manager import StrategyManager

2. 创建数据:
   data = pd.DataFrame({...})  # 包含OHLC列

3. 创建管理器:
   manager = StrategyManager(name="MyManager")

4. 注册策略:
   manager.register_strategy(name="MyStrategy", strategy_class=MyStrategyClass)

5. 运行策略:
   result = manager.run_strategy("MyStrategy", data=data)

6. 生成报告:
   report = manager.generate_report()

更详细的使用方法请参考:
  - usage_example.py (本文件)
  - tests/test_integration_complete.py (完整测试)
  - 各模块的文档字符串
""")
    
    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return successful > 0


if __name__ == "__main__":
    success = main()
    
    if success:
        print("\n🎉 示例运行成功！策略整合框架已准备就绪。")
        print("下一步: 将框架集成到您的量化交易系统中。")
    else:
        print("\n⚠️ 部分示例运行失败，请检查配置和依赖。")
    
    sys.exit(0 if success else 1)