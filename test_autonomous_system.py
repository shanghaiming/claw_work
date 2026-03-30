#!/usr/bin/env python3
"""
自主学习和回测循环系统测试脚本
验证系统核心功能
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from autonomous_learning_system import (
    StrategyCondition, 
    TradingStrategy,
    ContentParser,
    BacktestIntegrator,
    LearningCycleController
)

def test_strategy_representation():
    """测试策略表示框架"""
    print("🧪 测试策略表示框架...")
    
    # 创建策略条件
    condition1 = StrategyCondition(
        indicator="RSI",
        condition="<",
        value=30,
        timeframe="1d"
    )
    
    condition2 = StrategyCondition(
        indicator="Price",
        condition="breaks",
        value="support",
        timeframe="1d",
        lookback=2
    )
    
    # 创建交易策略
    strategy = TradingStrategy(
        name="测试策略",
        strategy_type=TradingStrategy.TREND_FOLLOWING,
        description="这是一个测试策略"
    )
    
    strategy.add_entry_condition(condition1)
    strategy.add_exit_condition(condition2)
    
    strategy.set_parameter("rsi_period", 14, 10, 20, 1)
    strategy.set_parameter("stop_loss", 2.0, 1.0, 5.0, 0.5)
    
    strategy.set_risk_management(
        stop_loss_type="fixed",
        stop_loss_value=2.0,
        take_profit_type="rrr",
        take_profit_value=2.0
    )
    
    # 验证策略属性
    assert strategy.name == "测试策略"
    assert strategy.strategy_type == TradingStrategy.TREND_FOLLOWING
    assert len(strategy.entry_conditions) == 1
    assert len(strategy.exit_conditions) == 1
    assert len(strategy.parameters) == 2
    
    # 测试序列化和反序列化
    strategy_dict = strategy.to_dict()
    strategy_from_dict = TradingStrategy.from_dict(strategy_dict)
    
    assert strategy_from_dict.name == strategy.name
    assert strategy_from_dict.strategy_type == strategy.strategy_type
    
    # 测试回测代码生成
    backtest_code = strategy.to_backtest_code()
    assert "策略:" in backtest_code
    assert "Backtrader" in backtest_code or "vectorbt" in backtest_code
    
    print("  ✅ 策略表示框架测试通过")
    return True

def test_content_parser():
    """测试内容解析器"""
    print("🧪 测试内容解析器...")
    
    parser = ContentParser()
    
    # 测试指标描述解析
    indicator_desc = """
    RSI指标，14日周期，超买阈值70，超卖阈值30。
    当RSI低于30时买入，高于70时卖出。
    """
    
    indicator_info = parser.parse_indicator_description(indicator_desc)
    
    assert "name" in indicator_info
    assert "type" in indicator_info
    assert "parameters" in indicator_info
    assert indicator_info["confidence"] > 0
    
    # 测试策略图表解析
    chart_desc = """
    趋势跟踪策略图表。
    当价格突破20日高点时买入。
    当价格跌破10日低点时卖出。
    使用移动平均线确认趋势。
    """
    
    strategy_info = parser.parse_strategy_chart(chart_desc)
    
    assert "strategy_type" in strategy_info
    assert "entry_signals" in strategy_info
    assert "exit_signals" in strategy_info
    assert strategy_info["confidence"] > 0
    
    # 测试策略生成
    strategy = parser.generate_strategy_from_content(
        indicator_desc=indicator_desc,
        chart_desc=chart_desc
    )
    
    assert isinstance(strategy, TradingStrategy)
    assert strategy.name != ""
    assert strategy.strategy_type != ""
    
    print("  ✅ 内容解析器测试通过")
    return True

def test_backtest_integrator():
    """测试回测集成器"""
    print("🧪 测试回测集成器...")
    
    # 创建测试策略
    strategy = TradingStrategy(
        name="回测测试策略",
        strategy_type=TradingStrategy.MEAN_REVERSION
    )
    
    condition = StrategyCondition(
        indicator="RSI",
        condition="<",
        value=30,
        timeframe="1d"
    )
    strategy.add_entry_condition(condition)
    
    condition2 = StrategyCondition(
        indicator="RSI",
        condition=">",
        value=70,
        timeframe="1d"
    )
    strategy.add_exit_condition(condition2)
    
    # 运行回测
    backtester = BacktestIntegrator()
    result = backtester.run_backtest(strategy, initial_capital=100000)
    
    # 验证回测结果
    assert "total_return_percent" in result
    assert "sharpe_ratio" in result
    assert "max_drawdown_percent" in result
    assert "win_rate_percent" in result
    
    # 验证策略绩效已更新
    assert strategy.performance is not None
    assert strategy.performance["total_return_percent"] == result["total_return_percent"]
    
    # 测试报告生成
    report = backtester.generate_report(strategy, result)
    assert strategy.name in report
    assert "回测报告" in report
    assert "绩效摘要" in report
    
    print("  ✅ 回测集成器测试通过")
    return True

def test_learning_cycle():
    """测试学习循环"""
    print("🧪 测试学习循环控制器...")
    
    # 创建输出目录
    output_dir = "./test_cycle_output"
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    
    # 初始化循环控制器
    controller = LearningCycleController(output_dir=output_dir)
    
    # 运行单个循环
    indicator_content = """
    移动平均线交叉策略。
    当5日MA上穿20日MA时买入。
    当5日MA下穿20日MA时卖出。
    参数：快线周期5，慢线周期20。
    """
    
    chart_content = """
    金叉死叉策略图表。
    显示买入和卖出信号点。
    使用日线时间框架。
    """
    
    cycle_result = controller.run_cycle(indicator_content, chart_content)
    
    # 验证循环结果
    assert cycle_result["cycle_number"] == 1
    assert cycle_result["strategies_generated"] > 0
    assert cycle_result["strategies_tested"] > 0
    assert "start_time" in cycle_result
    assert "end_time" in cycle_result
    
    # 验证输出文件
    cycle_file = os.path.join(output_dir, "cycle_001.json")
    assert os.path.exists(cycle_file)
    
    knowledge_file = os.path.join(output_dir, "knowledge_base.json")
    assert os.path.exists(knowledge_file)
    
    # 获取系统摘要
    summary = controller.get_summary()
    assert summary["total_cycles"] == 1
    assert summary["strategies_generated"] > 0
    assert summary["strategies_tested"] > 0
    
    # 清理测试目录
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    
    print("  ✅ 学习循环控制器测试通过")
    return True

def test_full_system():
    """测试完整系统流程"""
    print("🧪 测试完整系统流程...")
    
    # 创建临时输出目录
    output_dir = "./test_full_system_output"
    if os.path.exists(output_dir):
        import shutil
        shutil.rmtree(output_dir)
    
    try:
        # 1. 初始化系统
        controller = LearningCycleController(output_dir=output_dir)
        
        # 2. 运行多个循环
        print("  运行3个学习-回测循环...")
        results = controller.run_multiple_cycles(num_cycles=2)
        
        # 3. 验证结果
        assert len(results) == 2
        assert controller.cycle_count == 2
        
        # 4. 验证最佳策略
        if controller.best_strategies:
            print(f"  找到 {len(controller.best_strategies)} 个最佳策略")
            
            # 检查最佳策略结构
            best = controller.best_strategies[0]
            assert "strategy" in best
            assert "performance" in best
            assert "cycle_number" in best
            
            strategy_data = best["strategy"]
            assert "name" in strategy_data
            assert "strategy_type" in strategy_data
        
        # 5. 验证输出文件
        assert os.path.exists(os.path.join(output_dir, "cycle_001.json"))
        assert os.path.exists(os.path.join(output_dir, "cycle_002.json"))
        assert os.path.exists(os.path.join(output_dir, "knowledge_base.json"))
        
        print("  ✅ 完整系统流程测试通过")
        return True
        
    finally:
        # 清理
        if os.path.exists(output_dir):
            import shutil
            shutil.rmtree(output_dir)

def main():
    """运行所有测试"""
    print("=" * 60)
    print("自主学习和回测循环系统测试")
    print("=" * 60)
    
    tests = [
        test_strategy_representation,
        test_content_parser,
        test_backtest_integrator,
        test_learning_cycle,
        test_full_system
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  ❌ {test_func.__name__} 测试失败: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print(f"✅ 通过: {passed}")
    print(f"❌ 失败: {failed}")
    print(f"📊 总计: {passed + failed}")
    
    if failed == 0:
        print("🎉 所有测试通过!")
    else:
        print("⚠️  有测试失败，请检查")
    
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)