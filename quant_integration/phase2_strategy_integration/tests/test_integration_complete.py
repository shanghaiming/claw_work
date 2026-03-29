#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
完整集成测试 - 测试整个策略整合框架

测试内容:
1. 统一策略基类功能
2. 策略管理器功能
3. 移动平均策略适配
4. 价格行为策略集成
5. 完整工作流程演示
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入测试组件
from core.unified_strategy_base import UnifiedStrategyBase, ExampleMovingAverageStrategy
from managers.strategy_manager import StrategyManager

# 尝试导入适配器
try:
    from integrations.ma_strategy_adapter import register_ma_strategies
    MA_ADAPTER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 移动平均适配器导入失败: {e}")
    MA_ADAPTER_AVAILABLE = False

try:
    from integrations.price_action_integration import register_price_action_strategies
    PRICE_ACTION_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 价格行为集成导入失败: {e}")
    PRICE_ACTION_AVAILABLE = False


def generate_test_data(symbols=None, periods=200, start_date='2024-01-01'):
    """生成测试数据"""
    if symbols is None:
        symbols = ['TEST1', 'TEST2', 'TEST3']
    
    dates = pd.date_range(start_date, periods=periods, freq='D')
    
    all_data = []
    for symbol in symbols:
        # 为每个股票生成不同的价格走势
        base_price = 100 + np.random.randn() * 10
        
        # 生成价格序列（包含趋势）
        trend = np.linspace(0, 0.5, periods)  # 轻微上升趋势
        noise = np.random.randn(periods) * 0.5
        price = base_price * (1 + trend + noise.cumsum() * 0.01)
        
        data = pd.DataFrame({
            'open': price * (1 + np.random.uniform(-0.01, 0.01, periods)),
            'high': price * (1 + np.random.uniform(0, 0.02, periods)),
            'low': price * (1 + np.random.uniform(-0.02, 0, periods)),
            'close': price,
            'volume': np.random.randint(1000, 10000, periods),
            'symbol': symbol
        }, index=dates)
        
        all_data.append(data)
    
    # 合并所有股票数据
    combined_data = pd.concat(all_data)
    combined_data = combined_data.sort_index()
    
    print(f"生成测试数据: {periods}天 × {len(symbols)}只股票 = {len(combined_data)}行")
    print(f"股票列表: {symbols}")
    print(f"时间范围: {combined_data.index.min()} 到 {combined_data.index.max()}")
    
    return combined_data


def test_unified_base():
    """测试统一策略基类"""
    print("\n" + "="*60)
    print("测试1: 统一策略基类")
    print("="*60)
    
    # 生成测试数据
    data = generate_test_data(symbols=['TEST'], periods=100)
    
    # 测试示例策略
    strategy = ExampleMovingAverageStrategy(
        data=data,
        params={'short_window': 5, 'long_window': 20}
    )
    
    # 生成信号
    signals = strategy.generate_standard_signals()
    
    print(f"策略名称: {strategy.strategy_name}")
    print(f"生成信号: {len(signals)}个")
    print(f"执行时间: {strategy.execution_stats['execution_time']:.3f}秒")
    
    # 打印摘要
    strategy.print_summary()
    
    # 测试信号保存
    test_signal_file = "./test_outputs/test_signals.json"
    os.makedirs(os.path.dirname(test_signal_file), exist_ok=True)
    strategy.save_signals(test_signal_file)
    
    print(f"✅ 统一策略基类测试完成")
    return True


def test_strategy_manager():
    """测试策略管理器"""
    print("\n" + "="*60)
    print("测试2: 策略管理器")
    print("="*60)
    
    # 生成测试数据
    data = generate_test_data(periods=150)
    
    # 创建策略管理器
    manager = StrategyManager(
        name="IntegrationTestManager",
        config_dir="./test_outputs/configs",
        results_dir="./test_outputs/results"
    )
    
    # 注册示例策略
    class TestStrategy1(UnifiedStrategyBase):
        def get_default_params(self):
            return {'param1': 10, 'param2': 20}
        
        def generate_signals(self):
            return [{
                'timestamp': self.data.index[i],
                'action': 'buy',
                'price': self.data['close'].iloc[i],
                'confidence': 0.8
            } for i in range(0, len(self.data), 30)]
    
    class TestStrategy2(UnifiedStrategyBase):
        def get_default_params(self):
            return {'param_a': 5, 'param_b': 15}
        
        def generate_signals(self):
            return [{
                'timestamp': self.data.index[i],
                'action': 'sell',
                'price': self.data['close'].iloc[i],
                'confidence': 0.7
            } for i in range(15, len(self.data), 25)]
    
    manager.register_strategy(
        name="TestStrategy1",
        strategy_class=TestStrategy1,
        default_config={'description': '测试策略1'},
        description="第一个测试策略"
    )
    
    manager.register_strategy(
        name="TestStrategy2", 
        strategy_class=TestStrategy2,
        default_config={'description': '测试策略2'},
        description="第二个测试策略"
    )
    
    # 打印已注册策略
    manager.print_registered_strategies()
    
    # 运行单个策略
    print("\n运行单个策略:")
    result1 = manager.run_strategy(
        strategy_name="TestStrategy1",
        data=data,
        save_results=True
    )
    
    # 批量运行策略
    print("\n批量运行策略:")
    results = manager.run_strategies(
        strategy_names=["TestStrategy1", "TestStrategy2"],
        data=data,
        save_results=True
    )
    
    # 打印执行结果
    manager.print_execution_results()
    
    # 比较策略性能
    print("\n策略性能比较:")
    manager.compare_strategies()
    
    # 生成报告
    report = manager.generate_report(report_format='text')
    print("\n策略执行报告:")
    print(report)
    
    # 保存报告
    report_file = "./test_outputs/integration_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(manager.generate_report(report_format='markdown'))
    
    print(f"\n报告已保存: {report_file}")
    print(f"✅ 策略管理器测试完成")
    return True


def test_ma_strategy_integration():
    """测试移动平均策略集成"""
    if not MA_ADAPTER_AVAILABLE:
        print("⚠️ 移动平均适配器不可用，跳过测试")
        return False
    
    print("\n" + "="*60)
    print("测试3: 移动平均策略集成")
    print("="*60)
    
    # 生成测试数据
    data = generate_test_data(periods=200)
    
    # 创建策略管理器
    manager = StrategyManager(
        name="MATestManager",
        config_dir="./test_outputs/ma_configs",
        results_dir="./test_outputs/ma_results"
    )
    
    # 注册移动平均策略
    register_ma_strategies(manager)
    
    # 运行移动平均策略
    print("\n运行移动平均适配器:")
    result = manager.run_strategy(
        strategy_name="MovingAverageAdapter",
        data=data,
        config={
            'short_window': 10,
            'long_window': 30,
            'threshold': 0.015
        },
        save_results=True
    )
    
    # 打印已注册策略
    manager.print_registered_strategies()
    
    # 生成报告
    report_file = "./test_outputs/ma_integration_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(manager.generate_report(report_format='markdown'))
    
    print(f"\n报告已保存: {report_file}")
    print(f"✅ 移动平均策略集成测试完成")
    return True


def test_price_action_integration():
    """测试价格行为策略集成"""
    if not PRICE_ACTION_AVAILABLE:
        print("⚠️ 价格行为集成不可用，跳过测试")
        return False
    
    print("\n" + "="*60)
    print("测试4: 价格行为策略集成")
    print("="*60)
    
    # 生成测试数据
    data = generate_test_data(periods=200)
    
    # 创建策略管理器
    manager = StrategyManager(
        name="PriceActionTestManager",
        config_dir="./test_outputs/pa_configs",
        results_dir="./test_outputs/pa_results"
    )
    
    # 注册价格行为策略
    register_price_action_strategies(manager)
    
    # 运行价格行为策略
    print("\n运行价格行为策略:")
    result = manager.run_strategy(
        strategy_name="PriceActionSignal",
        data=data,
        config={
            'signal_type': 'MACDDivergence',
            'signal_params': {'fast_period': 6, 'slow_period': 13, 'signal_period': 5},
            'window_size': 80,
            'step': 15
        },
        save_results=True
    )
    
    # 运行多信号策略
    print("\n运行多价格行为策略:")
    result2 = manager.run_strategy(
        strategy_name="MultiPriceAction",
        data=data,
        config={
            'signal_definitions': [
                {'type': 'MACDDivergence', 'params': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}},
                {'type': 'MACDDivergence', 'params': {'fast_period': 6, 'slow_period': 13, 'signal_period': 5}}
            ],
            'combination_method': 'voting'
        },
        save_results=True
    )
    
    # 打印已注册策略
    manager.print_registered_strategies()
    
    # 比较策略性能
    print("\n策略性能比较:")
    manager.compare_strategies()
    
    # 生成报告
    report_file = "./test_outputs/price_action_integration_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(manager.generate_report(report_format='markdown'))
    
    print(f"\n报告已保存: {report_file}")
    print(f"✅ 价格行为策略集成测试完成")
    return True


def test_complete_workflow():
    """测试完整工作流程"""
    print("\n" + "="*60)
    print("测试5: 完整工作流程演示")
    print("="*60)
    
    # 生成测试数据
    data = generate_test_data(periods=250, symbols=['AAPL', 'GOOGL', 'MSFT'])
    
    # 创建综合策略管理器
    manager = StrategyManager(
        name="CompleteWorkflowManager",
        config_dir="./test_outputs/workflow_configs",
        results_dir="./test_outputs/workflow_results"
    )
    
    # 注册所有可用策略
    strategies_registered = 0
    
    # 注册示例策略
    class SimpleTrendStrategy(UnifiedStrategyBase):
        def get_default_params(self):
            return {'trend_window': 50, 'threshold': 0.02}
        
        def generate_signals(self):
            signals = []
            prices = self.data['close']
            
            # 计算趋势
            if len(prices) >= self.params['trend_window']:
                trend = prices.rolling(self.params['trend_window']).mean()
                trend_pct = (prices - trend) / trend
                
                for i in range(self.params['trend_window'], len(prices)):
                    if trend_pct.iloc[i] > self.params['threshold']:
                        signals.append({
                            'timestamp': self.data.index[i],
                            'action': 'buy',
                            'price': prices.iloc[i],
                            'confidence': 0.6,
                            'type': 'trend_following'
                        })
                    elif trend_pct.iloc[i] < -self.params['threshold']:
                        signals.append({
                            'timestamp': self.data.index[i],
                            'action': 'sell',
                            'price': prices.iloc[i],
                            'confidence': 0.6,
                            'type': 'trend_reversal'
                        })
            
            return signals
    
    manager.register_strategy(
        name="SimpleTrend",
        strategy_class=SimpleTrendStrategy,
        default_config={'trend_window': 50, 'threshold': 0.02},
        description="简单趋势跟踪策略"
    )
    strategies_registered += 1
    
    # 注册移动平均策略（如果可用）
    if MA_ADAPTER_AVAILABLE:
        register_ma_strategies(manager)
        strategies_registered += 2  # 适配器 + 包装器
    
    # 注册价格行为策略（如果可用）
    if PRICE_ACTION_AVAILABLE:
        register_price_action_strategies(manager)
        strategies_registered += 2  # 单信号 + 多信号
    
    print(f"总共注册了 {strategies_registered} 个策略")
    
    # 运行所有策略
    print(f"\n运行所有策略 (共 {len(manager.strategies)} 个):")
    all_results = manager.run_all_strategies(
        data=data,
        exclude=[],  # 不排除任何策略
        save_results=True
    )
    
    # 打印执行摘要
    print(f"\n执行完成: {len(all_results)}/{len(manager.strategies)} 个策略成功")
    
    # 生成详细报告
    print(f"\n生成详细报告...")
    detailed_report = manager.generate_report(report_format='markdown')
    
    report_file = "./test_outputs/complete_workflow_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 完整工作流程测试报告\n\n")
        f.write(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**测试数据**: 250天 × 3只股票 = {len(data)}行\n\n")
        f.write(f"**注册策略**: {len(manager.strategies)}个\n\n")
        f.write(f"**成功执行**: {len(all_results)}个\n\n")
        f.write(detailed_report)
    
    # 生成HTML报告
    html_report = manager.generate_report(report_format='html')
    html_file = "./test_outputs/complete_workflow_report.html"
    with open(html_file, 'w', encoding='utf-8') as f:
        f.write(html_report)
    
    print(f"\n报告已保存:")
    print(f"  Markdown: {report_file}")
    print(f"  HTML: {html_file}")
    
    # 打印关键指标
    print(f"\n📊 关键指标:")
    print(f"  测试数据大小: {len(data)} 行")
    print(f"  注册策略数量: {len(manager.strategies)} 个")
    print(f"  成功执行策略: {len(all_results)} 个")
    print(f"  总信号数量: {sum(r.get('signal_count', 0) for r in all_results.values())}")
    
    # 检查是否有错误
    errors = [name for name, result in all_results.items() if 'error' in result]
    if errors:
        print(f"  失败策略: {len(errors)} 个")
        for error_name in errors[:3]:
            print(f"    - {error_name}: {all_results[error_name].get('error')}")
    
    print(f"\n✅ 完整工作流程测试完成")
    return True


def main():
    """运行所有测试"""
    print("="*60)
    print("策略整合框架 - 完整集成测试")
    print("="*60)
    print(f"测试开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 创建测试输出目录
    os.makedirs("./test_outputs", exist_ok=True)
    
    test_results = []
    
    try:
        # 运行测试
        test_results.append(("统一策略基类", test_unified_base()))
        test_results.append(("策略管理器", test_strategy_manager()))
        test_results.append(("移动平均策略集成", test_ma_strategy_integration()))
        test_results.append(("价格行为策略集成", test_price_action_integration()))
        test_results.append(("完整工作流程", test_complete_workflow()))
        
    except Exception as e:
        print(f"\n❌ 测试过程中出现错误: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result:
            print(f"✅ {test_name}: 通过")
            passed += 1
        else:
            print(f"❌ {test_name}: 失败")
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n🎉 所有测试通过! 策略整合框架功能完整")
        
        # 显示下一步建议
        print("\n" + "="*60)
        print("下一步建议")
        print("="*60)
        print("1. 查看测试报告: ./test_outputs/ 目录")
        print("2. 使用策略管理器运行实际策略")
        print("3. 添加自定义策略到集成框架")
        print("4. 将整合框架集成到价格行为分析主系统")
        
    else:
        print(f"\n⚠️ 有 {failed} 个测试失败，请检查问题")
    
    print(f"\n测试结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)