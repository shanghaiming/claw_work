"""
反转系统整合量化分析系统测试
严格按照第18章标准：实际完整测试，非伪代码框架
紧急冲刺最终章：基础测试覆盖核心功能
"""

import unittest
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reversal_system_integration import (
    ReversalSystemIntegration,
    ModuleSignal,
    IntegratedDecision,
    SystemPerformanceReport,
    IntegrationModule,
    SignalStrength,
    DecisionConfidence,
    SystemPerformance,
)


class TestReversalSystemIntegrationInitialization(unittest.TestCase):
    """测试反转系统整合初始化"""
    
    def test_system_initialization(self):
        """测试系统初始化"""
        system = ReversalSystemIntegration(initial_balance=10000.0)
        
        # 检查配置
        self.assertIn("module_weights", system.config)
        self.assertIn("min_confidence_for_action", system.config)
        self.assertIn("conflict_resolution_threshold", system.config)
        self.assertIn("max_position_size", system.config)
        self.assertIn("adaptive_adjustment_enabled", system.config)
        self.assertIn("signal_aggregation_method", system.config)
        
        # 检查模块状态
        self.assertGreater(len(system.module_status), 0)
        for module in IntegrationModule:
            self.assertIn(module, system.module_status)
        
        # 检查数据存储
        self.assertEqual(len(system.module_signals_history), 0)
        self.assertEqual(len(system.decision_history), 0)
        self.assertEqual(len(system.performance_history), 0)
        
        # 检查资金
        self.assertEqual(system.initial_balance, 10000.0)
        self.assertEqual(system.current_balance, 10000.0)
    
    def test_config_values(self):
        """测试配置值有效性"""
        system = ReversalSystemIntegration()
        
        # 检查权重总和（应该接近1.0）
        weights = system.config["module_weights"]
        total_weight = sum(weights.values())
        self.assertGreater(total_weight, 0.95)
        self.assertLess(total_weight, 1.05)
        
        # 检查阈值
        self.assertGreater(system.config["min_confidence_for_action"], 0.0)
        self.assertLess(system.config["min_confidence_for_action"], 1.0)
        
        self.assertGreater(system.config["conflict_resolution_threshold"], 0.0)
        self.assertLess(system.config["conflict_resolution_threshold"], 1.0)
        
        # 检查仓位限制
        self.assertGreater(system.config["max_position_size"], 0.0)
        self.assertLess(system.config["max_position_size"], 0.5)  # 不应超过50%


class TestModuleSignal(unittest.TestCase):
    """测试ModuleSignal数据类"""
    
    def test_signal_creation(self):
        """测试信号创建"""
        signal = ModuleSignal(
            module=IntegrationModule.REVERSAL_BASICS,
            signal_direction="bullish",
            signal_strength=SignalStrength.STRONG,
            confidence_score=0.8,
            module_weight=0.12,
            timestamp=datetime.now(),
            additional_data={"pattern": "test"},
        )
        
        self.assertEqual(signal.module, IntegrationModule.REVERSAL_BASICS)
        self.assertEqual(signal.signal_direction, "bullish")
        self.assertEqual(signal.signal_strength, SignalStrength.STRONG)
        self.assertEqual(signal.confidence_score, 0.8)
        self.assertEqual(signal.module_weight, 0.12)
        self.assertIsInstance(signal.timestamp, datetime)
        self.assertIn("pattern", signal.additional_data)


class TestIntegratedDecision(unittest.TestCase):
    """测试IntegratedDecision数据类"""
    
    def test_decision_creation(self):
        """测试决策创建"""
        # 创建测试信号
        test_signal = ModuleSignal(
            module=IntegrationModule.PATTERN_RECOGNITION,
            signal_direction="bullish",
            signal_strength=SignalStrength.MODERATE,
            confidence_score=0.7,
            module_weight=0.14,
            timestamp=datetime.now(),
        )
        
        decision = IntegratedDecision(
            decision_id="TEST-001",
            overall_direction="bullish",
            overall_confidence=DecisionConfidence.HIGH,
            confidence_score=0.75,
            module_signals=[test_signal],
            weighted_score=0.65,
            risk_assessment={
                "overall_risk": 0.3,
                "confidence_risk": 0.2,
                "conflict_risk": 0.1,
                "module_dispersion_risk": 0.4,
                "market_condition_risk": 0.3,
            },
            recommended_action="建议做多",
            position_size_recommendation=0.05,
            timestamp=datetime.now(),
        )
        
        self.assertEqual(decision.decision_id, "TEST-001")
        self.assertEqual(decision.overall_direction, "bullish")
        self.assertEqual(decision.overall_confidence, DecisionConfidence.HIGH)
        self.assertEqual(decision.confidence_score, 0.75)
        self.assertEqual(len(decision.module_signals), 1)
        self.assertEqual(decision.weighted_score, 0.65)
        self.assertIn("overall_risk", decision.risk_assessment)
        self.assertEqual(decision.recommended_action, "建议做多")
        self.assertEqual(decision.position_size_recommendation, 0.05)
        self.assertIsInstance(decision.timestamp, datetime)


class TestSystemPerformanceReport(unittest.TestCase):
    """测试SystemPerformanceReport数据类"""
    
    def test_report_creation(self):
        """测试报告创建"""
        report = SystemPerformanceReport(
            report_id="REPORT-001",
            generation_date=datetime.now(),
            evaluation_period_days=30,
            module_performance={
                IntegrationModule.REVERSAL_BASICS: {
                    "signal_count": 10,
                    "average_confidence": 0.75,
                    "direction_consistency": 0.8,
                    "contribution_score": 0.7,
                    "performance_score": 0.75,
                }
            },
            overall_performance_score=0.78,
            performance_grade=SystemPerformance.GOOD,
            strengths=["模块集成良好", "信号质量高"],
            weaknesses=["部分模块信号较少"],
            improvement_recommendations=["增加数据收集", "优化算法"],
            risk_adjustments_applied=["高风险下减小仓位"],
            future_optimization_suggestions=["集成机器学习"],
        )
        
        self.assertEqual(report.report_id, "REPORT-001")
        self.assertIsInstance(report.generation_date, datetime)
        self.assertEqual(report.evaluation_period_days, 30)
        self.assertIn(IntegrationModule.REVERSAL_BASICS, report.module_performance)
        self.assertEqual(report.overall_performance_score, 0.78)
        self.assertEqual(report.performance_grade, SystemPerformance.GOOD)
        self.assertEqual(len(report.strengths), 2)
        self.assertEqual(len(report.weaknesses), 1)
        self.assertEqual(len(report.improvement_recommendations), 2)
        self.assertEqual(len(report.risk_adjustments_applied), 1)
        self.assertEqual(len(report.future_optimization_suggestions), 1)


class TestIntegrationMethods(unittest.TestCase):
    """测试集成方法"""
    
    def setUp(self):
        self.system = ReversalSystemIntegration()
    
    def test_integrate_module_signals_empty(self):
        """测试空信号集成"""
        decision = self.system.integrate_module_signals([])
        
        self.assertIsInstance(decision, IntegratedDecision)
        self.assertEqual(decision.overall_direction, "neutral")
        self.assertEqual(decision.overall_confidence, DecisionConfidence.VERY_LOW)
        self.assertEqual(decision.confidence_score, 0.0)
        self.assertEqual(len(decision.module_signals), 0)
    
    def test_integrate_module_signals_single(self):
        """测试单个信号集成"""
        signal = ModuleSignal(
            module=IntegrationModule.REVERSAL_BASICS,
            signal_direction="bullish",
            signal_strength=SignalStrength.STRONG,
            confidence_score=0.8,
            module_weight=0.12,
            timestamp=datetime.now(),
        )
        
        decision = self.system.integrate_module_signals([signal])
        
        self.assertIsInstance(decision, IntegratedDecision)
        self.assertIn(decision.overall_direction, ["bullish", "neutral"])
        self.assertGreaterEqual(decision.confidence_score, 0.0)
        self.assertLessEqual(decision.confidence_score, 1.0)
        self.assertEqual(len(decision.module_signals), 1)
    
    def test_strength_to_score(self):
        """测试强度转分数"""
        system = ReversalSystemIntegration()
        
        scores = {
            SignalStrength.VERY_WEAK: 0.2,
            SignalStrength.WEAK: 0.4,
            SignalStrength.MODERATE: 0.6,
            SignalStrength.STRONG: 0.8,
            SignalStrength.VERY_STRONG: 1.0,
        }
        
        for strength, expected_score in scores.items():
            score = system._strength_to_score(strength)
            self.assertEqual(score, expected_score)
    
    def test_score_to_confidence_level(self):
        """测试分数转置信度等级"""
        system = ReversalSystemIntegration()
        
        test_cases = [
            (0.9, DecisionConfidence.VERY_HIGH),
            (0.7, DecisionConfidence.HIGH),
            (0.5, DecisionConfidence.MEDIUM),
            (0.3, DecisionConfidence.LOW),
            (0.1, DecisionConfidence.VERY_LOW),
        ]
        
        for score, expected_level in test_cases:
            level = system._score_to_confidence_level(score)
            self.assertEqual(level, expected_level)


class TestPerformanceEvaluation(unittest.TestCase):
    """测试性能评估"""
    
    def setUp(self):
        self.system = ReversalSystemIntegration()
    
    def test_evaluate_system_performance_empty(self):
        """测试空历史性能评估"""
        report = self.system.evaluate_system_performance(lookback_days=7)
        
        self.assertIsInstance(report, SystemPerformanceReport)
        self.assertEqual(report.evaluation_period_days, 7)
        self.assertGreater(len(report.module_performance), 0)
        self.assertGreaterEqual(report.overall_performance_score, 0.0)
        self.assertLessEqual(report.overall_performance_score, 1.0)
        self.assertIsInstance(report.performance_grade, SystemPerformance)
        self.assertIsInstance(report.strengths, list)
        self.assertIsInstance(report.weaknesses, list)
        self.assertIsInstance(report.improvement_recommendations, list)


class TestSystemDemonstration(unittest.TestCase):
    """测试系统演示功能"""
    
    def setUp(self):
        self.system = ReversalSystemIntegration()
    
    def test_demonstrate_system(self):
        """测试系统演示"""
        demonstration = self.system.demonstrate_system()
        
        # 检查演示结果结构
        self.assertIsInstance(demonstration, dict)
        self.assertIn("system_name", demonstration)
        self.assertIn("demonstration_time", demonstration)
        self.assertIn("integration_demonstrated", demonstration)
        self.assertIn("decision_generated", demonstration)
        self.assertIn("decision_confidence", demonstration)
        self.assertIn("performance_evaluated", demonstration)
        self.assertIn("overall_performance_score", demonstration)
        self.assertIn("performance_grade", demonstration)
        self.assertIn("final_report_generated", demonstration)
        self.assertIn("completion_status", demonstration)
        self.assertIn("system_status", demonstration)
    
    def test_generate_system_report(self):
        """测试系统报告生成"""
        report = self.system.generate_system_report()
        
        # 检查报告结构
        self.assertIsInstance(report, dict)
        self.assertIn("system_name", report)
        self.assertIn("version", report)
        self.assertIn("generated_at", report)
        self.assertIn("initial_balance", report)
        self.assertIn("current_balance", report)
        self.assertIn("system_config", report)
        self.assertIn("module_status", report)
        self.assertIn("data_summary", report)
        self.assertIn("capabilities", report)
        self.assertIn("performance_metrics", report)
        self.assertIn("recommendations", report)


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    
    # 添加所有测试类
    test_classes = [
        TestReversalSystemIntegrationInitialization,
        TestModuleSignal,
        TestIntegratedDecision,
        TestSystemPerformanceReport,
        TestIntegrationMethods,
        TestPerformanceEvaluation,
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
    print("反转系统整合量化分析系统测试套件")
    print("严格按照第18章标准：实际完整测试")
    print("紧急冲刺最终章：基础测试覆盖核心功能")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ 所有测试通过！系统符合第18章标准。")
    else:
        print("❌ 部分测试失败，请检查系统实现。")
    print("=" * 60)
    
    sys.exit(0 if success else 1)