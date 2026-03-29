"""
反转交易基础量化分析系统测试
严格按照第18章标准：实际完整测试，非伪代码框架

测试覆盖：
1. 系统初始化
2. 信号检测功能
3. 交易设置生成
4. 风险管理和绩效评估
5. 系统演示功能
"""

import unittest
import sys
import os
from datetime import datetime, timedelta
import numpy as np

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reversal_trading_basics import (
    ReversalTradingBasics,
    PriceBar,
    ReversalSignal,
    ReversalSignalType,
    ReversalConfidence,
    ReversalTradeSetup
)


class TestPriceBar(unittest.TestCase):
    """测试PriceBar数据类"""
    
    def test_price_bar_creation(self):
        """测试PriceBar创建"""
        bar = PriceBar(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=10000.0
        )
        
        self.assertEqual(bar.open, 100.0)
        self.assertEqual(bar.high, 105.0)
        self.assertEqual(bar.low, 95.0)
        self.assertEqual(bar.close, 102.0)
        self.assertEqual(bar.volume, 10000.0)
    
    def test_price_bar_properties(self):
        """测试PriceBar计算属性"""
        bar = PriceBar(
            timestamp=datetime.now(),
            open=100.0,
            high=105.0,
            low=95.0,
            close=102.0,
            volume=10000.0
        )
        
        # 测试实体大小
        self.assertEqual(bar.body, 2.0)  # |102 - 100| = 2
        
        # 测试价格范围
        self.assertEqual(bar.range, 10.0)  # 105 - 95 = 10
        
        # 测试阴阳线
        self.assertTrue(bar.is_bullish)  # 102 > 100
        self.assertFalse(bar.is_bearish)
        
        # 测试阴线
        bearish_bar = PriceBar(
            timestamp=datetime.now(),
            open=102.0,
            high=105.0,
            low=95.0,
            close=100.0,
            volume=10000.0
        )
        self.assertFalse(bearish_bar.is_bullish)
        self.assertTrue(bearish_bar.is_bearish)


class TestReversalTradingBasicsInitialization(unittest.TestCase):
    """测试反转交易系统初始化"""
    
    def test_system_initialization(self):
        """测试系统初始化"""
        system = ReversalTradingBasics(initial_balance=50000.0)
        
        self.assertEqual(system.initial_balance, 50000.0)
        self.assertEqual(system.current_balance, 50000.0)
        self.assertEqual(len(system.signals_detected), 0)
        self.assertEqual(len(system.trade_setups), 0)
        self.assertEqual(len(system.trade_history), 0)
        
        # 检查默认配置
        self.assertIn("min_confidence_score", system.config)
        self.assertIn("min_signals_for_confirmation", system.config)
        self.assertIn("default_risk_per_trade", system.config)
        self.assertIn("min_risk_reward_ratio", system.config)
        self.assertIn("max_position_size_percent", system.config)
    
    def test_config_values(self):
        """测试配置值有效性"""
        system = ReversalTradingBasics()
        
        # 检查配置值范围
        self.assertGreaterEqual(system.config["min_confidence_score"], 0.0)
        self.assertLessEqual(system.config["min_confidence_score"], 1.0)
        
        self.assertGreaterEqual(system.config["min_signals_for_confirmation"], 1)
        
        self.assertGreater(system.config["default_risk_per_trade"], 0.0)
        self.assertLess(system.config["default_risk_per_trade"], 0.5)  # 应小于50%
        
        self.assertGreaterEqual(system.config["min_risk_reward_ratio"], 1.0)
        
        self.assertGreater(system.config["max_position_size_percent"], 0.0)
        self.assertLess(system.config["max_position_size_percent"], 1.0)


class TestSignalDetection(unittest.TestCase):
    """测试信号检测功能"""
    
    def setUp(self):
        """测试前准备"""
        self.system = ReversalTradingBasics()
        self.mock_bars = self._create_mock_price_bars(50)
    
    def _create_mock_price_bars(self, n_bars: int) -> list:
        """创建模拟价格柱"""
        bars = []
        current_time = datetime.now()
        base_price = 100.0
        
        for i in range(n_bars):
            # 随机价格变动
            random_change = np.random.normal(0.001, 0.02)
            price = base_price * (1 + random_change)
            
            # 生成OHLC
            open_price = price
            close_price = price * (1 + np.random.normal(0, 0.01))
            high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.005)))
            low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.005)))
            
            # 确保高低价正确
            high_price = max(open_price, close_price, high_price)
            low_price = min(open_price, close_price, low_price)
            
            # 成交量
            volume = np.random.uniform(1000, 10000)
            
            bar = PriceBar(
                timestamp=current_time,
                open=open_price,
                high=high_price,
                low=low_price,
                close=close_price,
                volume=volume
            )
            bars.append(bar)
            
            # 更新时间
            current_time = current_time.replace(second=current_time.second + 60)
            base_price = close_price
        
        return bars
    
    def test_detect_price_extreme(self):
        """测试价格极端检测"""
        signals = self.system.detect_price_extreme(self.mock_bars, lookback_period=10)
        
        # 信号应为列表
        self.assertIsInstance(signals, list)
        
        # 检查信号结构
        if signals:
            signal = signals[0]
            self.assertIsInstance(signal, ReversalSignal)
            self.assertEqual(signal.signal_type, ReversalSignalType.PRICE_EXTREME)
            self.assertIsInstance(signal.timestamp, datetime)
            self.assertIsInstance(signal.price_level, float)
            self.assertIsInstance(signal.confidence_score, float)
            self.assertGreaterEqual(signal.confidence_score, 0.0)
            self.assertLessEqual(signal.confidence_score, 1.0)
    
    def test_detect_momentum_divergence(self):
        """测试动量背离检测"""
        signals = self.system.detect_momentum_divergence(self.mock_bars, rsi_period=14)
        
        self.assertIsInstance(signals, list)
        
        if signals:
            signal = signals[0]
            self.assertEqual(signal.signal_type, ReversalSignalType.MOMENTUM_DIVERGENCE)
    
    def test_detect_volume_spike(self):
        """测试成交量放大检测"""
        # 修改一个柱的成交量使其异常高
        if len(self.mock_bars) > 10:
            self.mock_bars[10].volume = 50000.0  # 设置异常高成交量
        
        signals = self.system.detect_volume_spike(self.mock_bars, volume_multiplier=2.0)
        
        self.assertIsInstance(signals, list)
        
        if signals:
            signal = signals[0]
            self.assertEqual(signal.signal_type, ReversalSignalType.VOLUME_SPIKE)
    
    def test_detect_price_patterns(self):
        """测试价格模式检测"""
        signals = self.system.detect_price_patterns(self.mock_bars)
        
        self.assertIsInstance(signals, list)
        
        if signals:
            signal = signals[0]
            self.assertEqual(signal.signal_type, ReversalSignalType.PRICE_PATTERN)


class TestSignalConfirmation(unittest.TestCase):
    """测试信号确认功能"""
    
    def setUp(self):
        self.system = ReversalTradingBasics()
    
    def test_confirm_reversal_signals_empty(self):
        """测试空信号列表确认"""
        confidences = self.system.confirm_reversal_signals([])
        self.assertEqual(confidences, [])
    
    def test_confirm_reversal_signals_single(self):
        """测试单个信号确认"""
        signal = ReversalSignal(
            signal_id="test_signal_1",
            signal_type=ReversalSignalType.PRICE_EXTREME,
            timestamp=datetime.now(),
            price_level=100.0,
            confidence_score=0.8,
            description="测试信号",
            metadata={}
        )
        
        confidences = self.system.confirm_reversal_signals([signal])
        self.assertEqual(len(confidences), 1)
        self.assertEqual(confidences[0], ReversalConfidence.LOW)
    
    def test_confirm_reversal_signals_multiple(self):
        """测试多个信号确认"""
        signals = []
        for i in range(3):
            signal = ReversalSignal(
                signal_id=f"test_signal_{i}",
                signal_type=ReversalSignalType.PRICE_EXTREME,
                timestamp=datetime.now() + timedelta(minutes=i),
                price_level=100.0 + i,
                confidence_score=0.7 + i * 0.1,
                description=f"测试信号{i}",
                metadata={}
            )
            signals.append(signal)
        
        confidences = self.system.confirm_reversal_signals(signals)
        self.assertEqual(len(confidences), 1)  # 应该在一个时间窗口内
        self.assertEqual(confidences[0], ReversalConfidence.HIGH)  # 3个信号


class TestTradeSetupGeneration(unittest.TestCase):
    """测试交易设置生成"""
    
    def setUp(self):
        self.system = ReversalTradingBasics(initial_balance=10000.0)
        self.mock_bars = self._create_mock_price_bars(30)
    
    def _create_mock_price_bars(self, n_bars: int) -> list:
        """创建模拟价格柱"""
        bars = []
        current_time = datetime.now()
        base_price = 100.0
        
        for i in range(n_bars):
            bar = PriceBar(
                timestamp=current_time,
                open=base_price,
                high=base_price * 1.02,
                low=base_price * 0.98,
                close=base_price * 1.01,
                volume=10000.0
            )
            bars.append(bar)
            current_time = current_time.replace(second=current_time.second + 60)
            base_price *= 1.001  # 轻微上涨
        
        return bars
    
    def test_generate_trade_setup_insufficient_signals(self):
        """测试信号不足时交易设置生成"""
        # 单个信号不足
        signal = ReversalSignal(
            signal_id="test_signal",
            signal_type=ReversalSignalType.PRICE_EXTREME,
            timestamp=datetime.now(),
            price_level=100.0,
            confidence_score=0.9,
            description="测试信号",
            metadata={}
        )
        
        setup = self.system.generate_trade_setup([signal], self.mock_bars)
        self.assertIsNone(setup)  # 应返回None
    
    def test_generate_trade_setup_sufficient_signals(self):
        """测试信号充足时交易设置生成"""
        signals = []
        for i in range(3):
            signal = ReversalSignal(
                signal_id=f"test_signal_{i}",
                signal_type=ReversalSignalType.PRICE_EXTREME,
                timestamp=datetime.now() + timedelta(minutes=i),
                price_level=100.0 + i,
                confidence_score=0.8,
                description=f"测试信号{i}",
                metadata={"type": "resistance" if i % 2 == 0 else "support"}
            )
            signals.append(signal)
        
        setup = self.system.generate_trade_setup(signals, self.mock_bars)
        
        # 应有交易设置生成
        self.assertIsNotNone(setup)
        self.assertIsInstance(setup, ReversalTradeSetup)
        
        # 检查设置属性
        self.assertIsInstance(setup.setup_id, str)
        self.assertEqual(len(setup.signals), 3)
        self.assertIsInstance(setup.entry_price, float)
        self.assertIsInstance(setup.stop_loss, float)
        self.assertIsInstance(setup.take_profit, float)
        self.assertIsInstance(setup.risk_reward_ratio, float)
        self.assertIsInstance(setup.position_size, float)
        self.assertIsInstance(setup.confidence, ReversalConfidence)
        self.assertIsInstance(setup.setup_time, datetime)
        self.assertIsInstance(setup.notes, str)
        
        # 检查风险回报比
        self.assertGreaterEqual(setup.risk_reward_ratio, 0.0)
        
        # 检查仓位大小合理性
        self.assertGreaterEqual(setup.position_size, 0.0)
        self.assertLessEqual(setup.position_size, self.system.current_balance * 0.1)  # 不超过10%
    
    def test_generate_trade_setup_low_confidence(self):
        """测试低置信度信号交易设置生成"""
        signals = []
        for i in range(3):
            signal = ReversalSignal(
                signal_id=f"test_signal_{i}",
                signal_type=ReversalSignalType.PRICE_EXTREME,
                timestamp=datetime.now() + timedelta(minutes=i),
                price_level=100.0 + i,
                confidence_score=0.3,  # 低置信度
                description=f"测试信号{i}",
                metadata={}
            )
            signals.append(signal)
        
        setup = self.system.generate_trade_setup(signals, self.mock_bars)
        # 可能为None，因为平均置信度低于阈值
        if setup is not None:
            self.assertIsInstance(setup, ReversalTradeSetup)


class TestRiskManagement(unittest.TestCase):
    """测试风险管理功能"""
    
    def setUp(self):
        self.system = ReversalTradingBasics()
    
    def test_calculate_risk_reward_ratio(self):
        """测试风险回报比计算"""
        # 正常情况
        rr = self.system.calculate_risk_reward_ratio(
            entry=100.0,
            stop_loss=98.0,
            take_profit=106.0
        )
        self.assertAlmostEqual(rr, 3.0)  # (106-100)/(100-98) = 6/2 = 3
        
        # 零风险情况
        rr_zero_risk = self.system.calculate_risk_reward_ratio(
            entry=100.0,
            stop_loss=100.0,
            take_profit=106.0
        )
        self.assertEqual(rr_zero_risk, 0.0)
        
        # 做空情况
        rr_short = self.system.calculate_risk_reward_ratio(
            entry=100.0,
            stop_loss=102.0,
            take_profit=94.0
        )
        self.assertAlmostEqual(rr_short, 3.0)  # (100-94)/(102-100) = 6/2 = 3
    
    def test_evaluate_setup_quality(self):
        """测试交易设置质量评估"""
        # 创建测试信号
        signals = []
        for i in range(3):
            signal = ReversalSignal(
                signal_id=f"test_signal_{i}",
                signal_type=ReversalSignalType.PRICE_EXTREME,
                timestamp=datetime.now() + timedelta(minutes=i),
                price_level=100.0 + i,
                confidence_score=0.8,
                description=f"测试信号{i}",
                metadata={}
            )
            signals.append(signal)
        
        # 创建交易设置
        setup = ReversalTradeSetup(
            setup_id="test_setup",
            signals=signals,
            entry_price=100.0,
            stop_loss=98.0,
            take_profit=106.0,
            risk_reward_ratio=3.0,
            position_size=1000.0,
            confidence=ReversalConfidence.HIGH,
            setup_time=datetime.now(),
            notes="测试设置"
        )
        
        # 评估质量
        evaluation = self.system.evaluate_setup_quality(setup)
        
        # 检查评估结果
        self.assertIsInstance(evaluation, dict)
        self.assertIn("setup_id", evaluation)
        self.assertIn("signal_count", evaluation)
        self.assertIn("avg_signal_confidence", evaluation)
        self.assertIn("risk_reward_ratio", evaluation)
        self.assertIn("position_size_percent", evaluation)
        self.assertIn("confidence_level", evaluation)
        self.assertIn("quality_score", evaluation)
        self.assertIn("recommendation", evaluation)
        
        # 检查数值范围
        self.assertGreaterEqual(evaluation["quality_score"], 0.0)
        self.assertLessEqual(evaluation["quality_score"], 100.0)
        self.assertIsInstance(evaluation["recommendation"], str)
        
        # 检查计算
        self.assertEqual(evaluation["signal_count"], 3)
        self.assertAlmostEqual(evaluation["avg_signal_confidence"], 0.8)
        self.assertEqual(evaluation["risk_reward_ratio"], 3.0)


class TestTradeExecution(unittest.TestCase):
    """测试交易执行功能"""
    
    def setUp(self):
        self.system = ReversalTradingBasics(initial_balance=10000.0)
    
    def test_execute_trade(self):
        """测试交易执行"""
        # 创建交易设置
        setup = ReversalTradeSetup(
            setup_id="test_setup",
            signals=[],
            entry_price=100.0,
            stop_loss=98.0,
            take_profit=106.0,
            risk_reward_ratio=3.0,
            position_size=1000.0,
            confidence=ReversalConfidence.HIGH,
            setup_time=datetime.now(),
            notes="测试设置"
        )
        
        # 执行交易
        trade_result = self.system.execute_trade(setup)
        
        # 检查交易结果
        self.assertIsInstance(trade_result, dict)
        self.assertIn("trade_id", trade_result)
        self.assertIn("setup_id", trade_result)
        self.assertIn("entry_price", trade_result)
        self.assertIn("stop_loss", trade_result)
        self.assertIn("take_profit", trade_result)
        self.assertIn("position_size", trade_result)
        self.assertIn("direction", trade_result)
        self.assertIn("execution_time", trade_result)
        self.assertIn("status", trade_result)
        self.assertIn("profit_loss", trade_result)
        self.assertIn("profit_loss_percent", trade_result)
        
        # 检查值
        self.assertEqual(trade_result["setup_id"], "test_setup")
        self.assertEqual(trade_result["entry_price"], 100.0)
        self.assertEqual(trade_result["position_size"], 1000.0)
        self.assertEqual(trade_result["status"], "executed")
        
        # 检查交易历史
        self.assertEqual(len(self.system.trade_history), 1)
        self.assertEqual(self.system.trade_history[0]["trade_id"], trade_result["trade_id"])


class TestSystemDemonstration(unittest.TestCase):
    """测试系统演示功能"""
    
    def setUp(self):
        self.system = ReversalTradingBasics()
    
    def test_demonstrate_system(self):
        """测试系统演示"""
        demonstration = self.system.demonstrate_system()
        
        # 检查演示结果结构
        self.assertIsInstance(demonstration, dict)
        self.assertIn("mock_data_points", demonstration)
        self.assertIn("signals_detected", demonstration)
        self.assertIn("confidence_levels", demonstration)
        self.assertIn("trade_setup_generated", demonstration)
        self.assertIn("setup_evaluation", demonstration)
        self.assertIn("system_status", demonstration)
        
        # 检查信号检测结果
        signals_detected = demonstration["signals_detected"]
        self.assertIsInstance(signals_detected, dict)
        self.assertIn("price_extreme", signals_detected)
        self.assertIn("momentum_divergence", signals_detected)
        self.assertIn("volume_spike", signals_detected)
        self.assertIn("price_patterns", signals_detected)
        self.assertIn("total", signals_detected)
        
        # 检查置信度等级
        self.assertIsInstance(demonstration["confidence_levels"], list)
        
        # 如果生成了交易设置，检查评估结果
        if demonstration["trade_setup_generated"]:
            evaluation = demonstration["setup_evaluation"]
            self.assertIsInstance(evaluation, dict)
            self.assertIn("quality_score", evaluation)
            self.assertIn("recommendation", evaluation)
    
    def test_generate_system_report(self):
        """测试系统报告生成"""
        report = self.system.generate_system_report()
        
        # 检查报告结构
        self.assertIsInstance(report, dict)
        self.assertIn("system_name", report)
        self.assertIn("version", report)
        self.assertIn("generated_at", report)
        self.assertIn("system_config", report)
        self.assertIn("performance_metrics", report)
        self.assertIn("recent_activity", report)
        self.assertIn("system_status", report)
        self.assertIn("recommendations", report)
        
        # 检查性能指标
        metrics = report["performance_metrics"]
        self.assertIn("signals_detected_total", metrics)
        self.assertIn("trade_setups_generated", metrics)
        self.assertIn("trades_executed", metrics)
        self.assertIn("current_balance", metrics)
        self.assertIn("balance_change_percent", metrics)
        
        # 检查最近活动
        activity = report["recent_activity"]
        self.assertIn("last_signals", activity)
        self.assertIn("last_setups", activity)
        self.assertIn("last_trades", activity)
        
        # 检查推荐
        self.assertIsInstance(report["recommendations"], list)
        self.assertGreater(len(report["recommendations"]), 0)


class TestSystemIntegration(unittest.TestCase):
    """测试系统集成功能"""
    
    def test_full_system_workflow(self):
        """测试完整系统工作流"""
        # 创建系统
        system = ReversalTradingBasics(initial_balance=50000.0)
        
        # 创建模拟数据
        mock_bars = []
        current_time = datetime.now()
        base_price = 100.0
        
        for i in range(100):
            bar = PriceBar(
                timestamp=current_time,
                open=base_price,
                high=base_price * 1.02,
                low=base_price * 0.98,
                close=base_price * 1.01,
                volume=10000.0
            )
            mock_bars.append(bar)
            current_time = current_time.replace(second=current_time.second + 60)
            base_price *= 1.001
        
        # 检测信号
        extreme_signals = system.detect_price_extreme(mock_bars)
        divergence_signals = system.detect_momentum_divergence(mock_bars)
        
        all_signals = extreme_signals + divergence_signals
        
        # 确认信号
        confidences = system.confirm_reversal_signals(all_signals)
        
        # 如果有足够信号，生成交易设置
        if len(all_signals) >= system.config["min_signals_for_confirmation"]:
            setup = system.generate_trade_setup(all_signals[:3], mock_bars)
            
            if setup:
                # 评估设置质量
                evaluation = system.evaluate_setup_quality(setup)
                
                # 执行交易
                trade_result = system.execute_trade(setup)
                
                # 验证交易执行
                self.assertIsInstance(trade_result, dict)
                self.assertEqual(trade_result["status"], "executed")
                
                # 验证交易历史更新
                self.assertEqual(len(system.trade_history), 1)
        
        # 生成系统报告
        report = system.generate_system_report()
        
        # 验证报告
        self.assertEqual(report["system_status"], "active")
        self.assertIsInstance(report["performance_metrics"], dict)


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    
    # 添加所有测试类
    test_classes = [
        TestPriceBar,
        TestReversalTradingBasicsInitialization,
        TestSignalDetection,
        TestSignalConfirmation,
        TestTradeSetupGeneration,
        TestRiskManagement,
        TestTradeExecution,
        TestSystemDemonstration,
        TestSystemIntegration,
    ]
    
    suites = []
    for test_class in test_classes:
        suite = loader.loadTestsFromTestCase(test_class)
        suites.append(suite)
    
    all_tests = unittest.TestSuite(suites)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(all_tests)
    
    # 返回测试结果
    return result.wasSuccessful()


if __name__ == "__main__":
    print("=" * 60)
    print("反转交易基础量化分析系统测试套件")
    print("严格按照第18章标准：实际完整测试")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ 所有测试通过！系统符合第18章标准。")
    else:
        print("❌ 部分测试失败，请检查系统实现。")
    print("=" * 60)
    
    sys.exit(0 if success else 1)