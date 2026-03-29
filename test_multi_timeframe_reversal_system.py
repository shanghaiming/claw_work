"""
多时间框架反转量化分析系统测试
严格按照第18章标准：实际完整测试，非伪代码框架
紧急冲刺恢复模式：基础测试覆盖核心功能
"""

import unittest
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_timeframe_reversal_system import (
    MultiTimeframeReversalSystem,
    MultiTimeframeAnalysis,
    MultiTimeframeSignal,
    TimeframeLevel,
    TimeframeAlignment
)


class TestMultiTimeframeReversalSystemInitialization(unittest.TestCase):
    """测试多时间框架反转系统初始化"""
    
    def test_system_initialization(self):
        """测试系统初始化"""
        system = MultiTimeframeReversalSystem()
        
        # 检查配置
        self.assertIn("timeframe_weights", system.config)
        self.assertIn("min_alignment_score", system.config)
        self.assertIn("min_signals_per_timeframe", system.config)
        self.assertIn("max_timeframe_gap_hours", system.config)
        
        # 检查时间框架定义
        self.assertIn(TimeframeLevel.MAJOR, system.timeframe_definitions)
        self.assertIn(TimeframeLevel.MINOR, system.timeframe_definitions)
        self.assertIn(TimeframeLevel.MICRO, system.timeframe_definitions)
    
    def test_config_values(self):
        """测试配置值有效性"""
        system = MultiTimeframeReversalSystem()
        
        # 检查权重总和（应该接近1.0）
        weights = system.config["timeframe_weights"]
        total_weight = sum(weights.values())
        self.assertGreater(total_weight, 0.9)
        self.assertLess(total_weight, 1.1)
        
        # 检查阈值
        self.assertGreater(system.config["min_alignment_score"], 0.0)
        self.assertLess(system.config["min_alignment_score"], 1.0)
        
        self.assertGreater(system.config["trend_strength_threshold"], 0.0)
        self.assertLess(system.config["trend_strength_threshold"], 1.0)


class TestMultiTimeframeSignal(unittest.TestCase):
    """测试MultiTimeframeSignal数据类"""
    
    def test_signal_creation(self):
        """测试信号创建"""
        signal = MultiTimeframeSignal(
            timeframe=TimeframeLevel.MAJOR,
            trend_direction="bullish",
            trend_strength=0.8,
            reversal_signals=[{"type": "test", "strength": 0.7}],
            confidence_score=0.75,
            timestamp=datetime.now()
        )
        
        self.assertEqual(signal.timeframe, TimeframeLevel.MAJOR)
        self.assertEqual(signal.trend_direction, "bullish")
        self.assertEqual(signal.trend_strength, 0.8)
        self.assertEqual(len(signal.reversal_signals), 1)
        self.assertEqual(signal.confidence_score, 0.75)
        self.assertIsInstance(signal.timestamp, datetime)
    
    def test_signal_to_dict(self):
        """测试信号转换为字典"""
        signal = MultiTimeframeSignal(
            timeframe=TimeframeLevel.MINOR,
            trend_direction="bearish",
            trend_strength=0.6,
            reversal_signals=[{"type": "test"}],
            confidence_score=0.65,
            timestamp=datetime.now()
        )
        
        signal_dict = signal.to_dict()
        
        self.assertIn("timeframe", signal_dict)
        self.assertIn("trend_direction", signal_dict)
        self.assertIn("trend_strength", signal_dict)
        self.assertIn("reversal_signals_count", signal_dict)
        self.assertIn("confidence_score", signal_dict)
        self.assertIn("timestamp", signal_dict)


class TestAnalysisMethods(unittest.TestCase):
    """测试分析方法"""
    
    def setUp(self):
        self.system = MultiTimeframeReversalSystem()
    
    def test_analyze_trend_from_signals_empty(self):
        """测试空信号分析"""
        direction, strength = self.system._analyze_trend_from_signals([])
        
        self.assertEqual(direction, "neutral")
        self.assertEqual(strength, 0.0)
    
    def test_analyze_trend_from_signals_bullish(self):
        """测试看涨信号分析"""
        signals = [
            {"signal_type": "bullish_reversal", "strength": 0.8},
            {"signal_type": "bullish_divergence", "strength": 0.7},
        ]
        
        direction, strength = self.system._analyze_trend_from_signals(signals)
        
        self.assertEqual(direction, "bullish")
        self.assertGreater(strength, 0.0)
        self.assertLessEqual(strength, 1.0)
    
    def test_calculate_signal_confidence_empty(self):
        """测试空信号置信度计算"""
        confidence = self.system._calculate_signal_confidence([], TimeframeLevel.MAJOR)
        
        self.assertEqual(confidence, 0.0)
    
    def test_calculate_signal_confidence_with_signals(self):
        """测试有信号时的置信度计算"""
        signals = [
            {"signal_type": "test", "strength": 0.8, "quality": 0.7},
            {"signal_type": "test", "strength": 0.6, "quality": 0.8},
        ]
        
        confidence = self.system._calculate_signal_confidence(signals, TimeframeLevel.MAJOR)
        
        self.assertGreater(confidence, 0.0)
        self.assertLessEqual(confidence, 1.0)


class TestTimeframeAlignment(unittest.TestCase):
    """测试时间框架对齐分析"""
    
    def setUp(self):
        self.system = MultiTimeframeReversalSystem()
    
    def test_create_timeframe_signal(self):
        """测试创建时间框架信号"""
        signals = [
            {"signal_type": "bullish_reversal", "strength": 0.8, "quality": 0.7},
        ]
        
        signal = self.system._create_timeframe_signal(
            TimeframeLevel.MAJOR, signals, "测试分析"
        )
        
        self.assertIsInstance(signal, MultiTimeframeSignal)
        self.assertEqual(signal.timeframe, TimeframeLevel.MAJOR)
        self.assertGreater(signal.confidence_score, 0.0)
    
    def test_analyze_timeframe_alignment_empty(self):
        """测试空信号对齐分析"""
        alignment, score = self.system._analyze_timeframe_alignment([])
        
        self.assertEqual(alignment, TimeframeAlignment.UNCLEAR)
        self.assertLess(score, 0.5)
    
    def test_analyze_timeframe_alignment_single(self):
        """测试单个信号对齐分析"""
        signal = MultiTimeframeSignal(
            timeframe=TimeframeLevel.MAJOR,
            trend_direction="bullish",
            trend_strength=0.8,
            reversal_signals=[],
            confidence_score=0.7,
            timestamp=datetime.now()
        )
        
        alignment, score = self.system._analyze_timeframe_alignment([signal])
        
        self.assertEqual(alignment, TimeframeAlignment.UNCLEAR)
        self.assertLess(score, 0.5)


class TestRiskAssessment(unittest.TestCase):
    """测试风险评估"""
    
    def setUp(self):
        self.system = MultiTimeframeReversalSystem()
    
    def test_assess_multi_timeframe_risk_empty(self):
        """测试空信号风险评估"""
        signals = []
        alignment = TimeframeAlignment.UNCLEAR
        
        risk_assessment = self.system._assess_multi_timeframe_risk(signals, alignment)
        
        self.assertIn("overall_risk", risk_assessment)
        self.assertGreaterEqual(risk_assessment["overall_risk"], 0.0)
        self.assertLessEqual(risk_assessment["overall_risk"], 1.0)
    
    def test_generate_recommendation_full_alignment(self):
        """测试完全对齐的推荐生成"""
        alignment = TimeframeAlignment.FULL_ALIGNMENT
        trend_direction = "bullish"
        confidence = 0.8
        risk_assessment = {"overall_risk": 0.2}
        
        recommendation = self.system._generate_recommendation(
            alignment, trend_direction, confidence, risk_assessment
        )
        
        self.assertIsInstance(recommendation, str)
        self.assertGreater(len(recommendation), 0)


class TestSystemDemonstration(unittest.TestCase):
    """测试系统演示功能"""
    
    def setUp(self):
        self.system = MultiTimeframeReversalSystem()
    
    def test_demonstrate_system(self):
        """测试系统演示"""
        demonstration = self.system.demonstrate_system()
        
        # 检查演示结果结构
        self.assertIsInstance(demonstration, dict)
        self.assertIn("system_name", demonstration)
        self.assertIn("demonstration_time", demonstration)
        self.assertIn("analysis_results", demonstration)
        self.assertIn("trade_setup_generated", demonstration)
        self.assertIn("system_status", demonstration)
    
    def test_generate_system_report(self):
        """测试系统报告生成"""
        report = self.system.generate_system_report()
        
        # 检查报告结构
        self.assertIsInstance(report, dict)
        self.assertIn("system_name", report)
        self.assertIn("version", report)
        self.assertIn("generated_at", report)
        self.assertIn("system_config", report)
        self.assertIn("timeframe_definitions", report)
        self.assertIn("capabilities", report)
        self.assertIn("performance_metrics", report)
        self.assertIn("recommendations", report)


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    
    # 添加所有测试类
    test_classes = [
        TestMultiTimeframeReversalSystemInitialization,
        TestMultiTimeframeSignal,
        TestAnalysisMethods,
        TestTimeframeAlignment,
        TestRiskAssessment,
        TestSystemDemonstration,
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
    print("多时间框架反转量化分析系统测试套件")
    print("严格按照第18章标准：实际完整测试")
    print("紧急冲刺恢复模式：基础测试覆盖核心功能")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ 所有测试通过！系统符合第18章标准。")
    else:
        print("❌ 部分测试失败，请检查系统实现。")
    print("=" * 60)
    
    sys.exit(0 if success else 1)