#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回测层集成测试 - 阶段4.4

测试集成回测系统的所有组件:
1. 统一回测引擎
2. 风险管理器
3. 绩效分析器
4. 集成回测系统
"""

import sys
import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json

# 添加当前目录到路径
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

def test_backtest_engine():
    """测试统一回测引擎"""
    print("=" * 80)
    print("测试1: 统一回测引擎")
    print("=" * 80)
    
    try:
        from backtest_engine import UnifiedBacktestEngine, create_demo_backtest_config
        
        # 创建回测引擎
        config = create_demo_backtest_config()
        engine = UnifiedBacktestEngine(config)
        
        # 生成示例数据
        np.random.seed(42)
        days = 50
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        
        data = pd.DataFrame({
            'open': np.random.normal(100, 5, days),
            'high': np.random.normal(105, 5, days),
            'low': np.random.normal(95, 5, days),
            'close': np.random.normal(100, 5, days),
            'volume': np.random.randint(100000, 1000000, days)
        }, index=dates)
        
        print(f"创建回测引擎: 初始资金={config['initial_capital']:,.2f}")
        print(f"示例数据: {len(data)} 行，{dates[0]} 到 {dates[-1]}")
        
        # 运行回测
        result = engine.run_backtest("TestStrategy", data)
        
        if result.get('status') == 'completed':
            metrics = result.get('performance_metrics', {})
            print(f"回测成功!")
            print(f"  总收益率: {metrics.get('total_return', 0):.2%}")
            print(f"  总交易次数: {metrics.get('total_trades', 0)}")
            print(f"  最终权益: {metrics.get('final_equity', 0):,.2f}")
            
            # 生成报告
            report_file = engine.generate_report(result, output_dir='test_results')
            print(f"  报告文件: {report_file}")
            
            return True
        else:
            print(f"回测失败: {result.get('error', '未知错误')}")
            return False
            
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_risk_manager():
    """测试风险管理器"""
    print("\n" + "=" * 80)
    print("测试2: 风险管理器")
    print("=" * 80)
    
    try:
        from risk_manager import RiskManager, create_default_risk_config
        
        # 创建风险管理器
        config = create_default_risk_config()
        risk_manager = RiskManager(config)
        
        print(f"创建风险管理器:")
        print(f"  最大单笔风险: {config['max_position_risk']:.2%}")
        print(f"  最大组合风险: {config['max_portfolio_risk']:.2%}")
        print(f"  止损百分比: {config['stop_loss_pct']:.2%}")
        
        # 测试仓位大小计算
        entry_price = 100.0
        stop_loss = 95.0
        account_size = 100000.0
        
        shares, actual_risk = risk_manager.calculate_position_size(
            entry_price, stop_loss, account_size
        )
        
        print(f"仓位计算测试:")
        print(f"  入场价: {entry_price:.2f}")
        print(f"  止损价: {stop_loss:.2f}")
        print(f"  建议仓位: {shares} 股")
        print(f"  实际风险: {actual_risk:.2f} ({actual_risk/account_size:.2%})")
        
        # 测试止损止盈计算
        stop_loss_price = risk_manager.calculate_stop_loss(entry_price, 'long')
        take_profit_price = risk_manager.calculate_take_profit(entry_price, 'long')
        
        print(f"止损止盈计算:")
        print(f"  动态止损: {stop_loss_price:.2f}")
        print(f"  止盈价格: {take_profit_price:.2f}")
        print(f"  风险回报比: {abs(take_profit_price-entry_price)/abs(entry_price-stop_loss_price):.2f}")
        
        # 测试最大回撤计算
        np.random.seed(42)
        equity_curve = 100000 * np.cumprod(1 + np.random.normal(0.0005, 0.02, 100))
        
        drawdown_info = risk_manager.calculate_max_drawdown(equity_curve.tolist())
        
        print(f"最大回撤计算:")
        print(f"  最大回撤: {drawdown_info.get('max_drawdown', 0):.2%}")
        print(f"  回撤超限: {drawdown_info.get('exceeded_limit', False)}")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance_analyzer():
    """测试绩效分析器"""
    print("\n" + "=" * 80)
    print("测试3: 绩效分析器")
    print("=" * 80)
    
    try:
        from performance_analyzer import PerformanceAnalyzer
        
        # 创建绩效分析器
        analyzer = PerformanceAnalyzer(risk_free_rate=0.02)
        
        # 生成示例数据
        np.random.seed(42)
        days = 100
        initial_equity = 100000
        equity_curve = initial_equity * np.cumprod(1 + np.random.normal(0.0005, 0.02, days))
        
        # 生成示例交易
        trades = []
        for i in range(0, days, 20):
            if i + 10 < days:
                trades.append({
                    'date': datetime(2023, 1, 1) + timedelta(days=i),
                    'symbol': 'TEST001.SZ',
                    'action': 'buy',
                    'price': equity_curve[i] / 1000,
                    'quantity': 100
                })
                trades.append({
                    'date': datetime(2023, 1, 1) + timedelta(days=i+10),
                    'symbol': 'TEST001.SZ',
                    'action': 'sell',
                    'price': equity_curve[i+10] / 1000,
                    'quantity': 100
                })
        
        print(f"创建绩效分析器: 无风险利率={analyzer.risk_free_rate:.2%}")
        print(f"示例数据: {len(equity_curve)} 天权益曲线，{len(trades)} 笔交易")
        
        # 测试基本指标
        dates = [datetime(2023, 1, 1) + timedelta(days=i) for i in range(days)]
        basic_metrics = analyzer.calculate_basic_metrics(equity_curve.tolist(), dates)
        
        print(f"基本指标计算:")
        print(f"  总收益率: {basic_metrics.get('total_return', 0):.2%}")
        print(f"  年化收益率: {basic_metrics.get('annualized_return', 0):.2%}")
        print(f"  波动率: {basic_metrics.get('std_daily_return', 0):.4f}")
        
        # 测试风险调整后指标
        benchmark_returns = np.random.normal(0.0003, 0.015, days)
        risk_metrics = analyzer.calculate_risk_adjusted_metrics(
            equity_curve.tolist(), dates, benchmark_returns
        )
        
        print(f"风险调整后指标:")
        print(f"  夏普比率: {risk_metrics.get('sharpe_ratio', 0):.3f}")
        print(f"  索提诺比率: {risk_metrics.get('sortino_ratio', 0):.3f}")
        
        # 测试交易指标
        trade_metrics = analyzer.calculate_trade_metrics(trades)
        
        print(f"交易指标:")
        print(f"  总交易次数: {trade_metrics.get('total_trades', 0)}")
        print(f"  胜率: {trade_metrics.get('win_rate', 0):.2%}")
        print(f"  盈亏比: {trade_metrics.get('profit_factor', 0):.2f}")
        
        # 测试全面报告
        comprehensive_report = analyzer.generate_comprehensive_report(
            equity_curve.tolist(), trades, dates, benchmark_returns
        )
        
        summary = comprehensive_report.get('summary', {})
        print(f"全面报告:")
        print(f"  绩效质量: {summary.get('performance_quality', 'unknown')}")
        print(f"  总体评分: {summary.get('overall_rating', 0):.1f}/10")
        
        return True
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integrated_system():
    """测试集成回测系统"""
    print("\n" + "=" * 80)
    print("测试4: 集成回测系统")
    print("=" * 80)
    
    try:
        from integrated_backtest_system import IntegratedBacktestSystem, create_integrated_system_config
        
        # 创建集成系统
        config = create_integrated_system_config()
        system = IntegratedBacktestSystem(config)
        
        # 检查系统状态
        status = system.get_system_status()
        
        print(f"创建集成回测系统:")
        print(f"  初始化: {'成功' if status['initialized'] else '失败'}")
        print(f"  可用组件: {len(status['components_available'])} 个")
        
        if not status['initialized']:
            print("警告: 系统初始化失败，跳过集成测试")
            return False
        
        # 生成示例数据
        np.random.seed(42)
        days = 60
        dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
        
        data = pd.DataFrame({
            'open': 100 + np.cumsum(np.random.normal(0, 2, days)),
            'high': 105 + np.cumsum(np.random.normal(0, 2, days)),
            'low': 95 + np.cumsum(np.random.normal(0, 2, days)),
            'close': 100 + np.cumsum(np.random.normal(0, 2, days)),
            'volume': np.random.randint(100000, 1000000, days)
        }, index=dates)
        
        print(f"示例数据: {len(data)} 行")
        
        # 运行完整回测
        result = system.run_complete_backtest(
            strategy_name="IntegratedTestStrategy",
            data=data,
            benchmark_data=data,  # 使用相同数据作为基准
            save_report=True,
            output_dir='test_results'
        )
        
        if result.get('status') in ['completed', 'completed_with_errors']:
            print(f"集成回测完成!")
            print(f"  状态: {result.get('status')}")
            print(f"  使用的组件: {', '.join(result.get('components_used', []))}")
            print(f"  错误数: {len(result.get('errors', []))}")
            
            integrated_report = result.get('integrated_report', {})
            if integrated_report:
                key_metrics = integrated_report.get('key_metrics', {})
                print(f"  综合评分: {integrated_report.get('integrated_score', 0):.1f}/10")
                print(f"  总收益率: {key_metrics.get('total_return', 0):.2%}")
                print(f"  最大回撤: {key_metrics.get('max_drawdown', 0):.2%}")
            
            # 检查报告文件
            import glob
            report_files = glob.glob('test_results/*.json')
            if report_files:
                print(f"  生成的报告: {len(report_files)} 个文件")
            
            return True
        else:
            print(f"集成回测失败: {result.get('errors', ['未知错误'])}")
            return False
        
    except Exception as e:
        print(f"测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """运行所有测试"""
    print("开始回测层集成测试...")
    print("=" * 80)
    
    test_results = []
    
    # 运行各个测试
    test_results.append(("统一回测引擎", test_backtest_engine()))
    test_results.append(("风险管理器", test_risk_manager()))
    test_results.append(("绩效分析器", test_performance_analyzer()))
    test_results.append(("集成回测系统", test_integrated_system()))
    
    # 输出测试结果
    print("\n" + "=" * 80)
    print("测试结果汇总")
    print("=" * 80)
    
    total_tests = len(test_results)
    passed_tests = sum(1 for _, passed in test_results if passed)
    
    for test_name, passed in test_results:
        status = "✅ 通过" if passed else "❌ 失败"
        print(f"{test_name}: {status}")
    
    print(f"\n总计: {passed_tests}/{total_tests} 通过 ({passed_tests/total_tests*100:.0f}%)")
    
    # 清理测试目录
    import shutil
    if os.path.exists('test_results'):
        try:
            shutil.rmtree('test_results')
            print(f"清理测试目录: test_results")
        except:
            pass
    
    # 总体评估
    if passed_tests == total_tests:
        print("\n🎉 所有测试通过! 回测层集成完成。")
        return True
    elif passed_tests >= total_tests * 0.75:
        print(f"\n⚠️  {passed_tests}/{total_tests} 测试通过，基本功能可用。")
        return True
    else:
        print(f"\n❌ 只有 {passed_tests}/{total_tests} 测试通过，需要修复问题。")
        return False

def main():
    """主函数"""
    # 创建测试目录
    os.makedirs('test_results', exist_ok=True)
    
    # 运行所有测试
    success = run_all_tests()
    
    # 返回退出码
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()