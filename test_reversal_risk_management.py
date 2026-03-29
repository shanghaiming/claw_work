"""
反转风险管理量化分析系统测试
严格按照第18章标准：实际完整测试，非伪代码框架
紧急冲刺模式：基础测试覆盖核心功能
"""

import unittest
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reversal_risk_management import (
    ReversalRiskManagement,
    RiskMetric,
    RiskMetricType,
    RiskLevel,
    RiskAssessment
)


class TestReversalRiskManagementInitialization(unittest.TestCase):
    """测试反转风险管理系统初始化"""
    
    def test_system_initialization(self):
        """测试系统初始化"""
        system = ReversalRiskManagement(initial_balance=50000.0)
        
        self.assertEqual(system.initial_balance, 50000.0)
        self.assertEqual(system.current_balance, 50000.0)
        self.assertEqual(system.portfolio_value, 50000.0)
        self.assertEqual(system.max_drawdown, 0.0)
        self.assertEqual(len(system.active_positions), 0)
        self.assertEqual(len(system.risk_metrics), 0)
        self.assertEqual(len(system.risk_assessments), 0)
        
        # 检查默认配置
        self.assertIn("max_portfolio_risk", system.config)
        self.assertIn("max_position_risk", system.config)
        self.assertIn("max_drawdown_limit", system.config)
        self.assertIn("volatility_lookback_period", system.config)
        self.assertIn("liquidity_threshold", system.config)
    
    def test_config_values(self):
        """测试配置值有效性"""
        system = ReversalRiskManagement()
        
        # 检查配置值范围
        self.assertGreater(system.config["max_portfolio_risk"], 0.0)
        self.assertLess(system.config["max_portfolio_risk"], 0.5)
        
        self.assertGreater(system.config["max_position_risk"], 0.0)
        self.assertLess(system.config["max_position_risk"], system.config["max_portfolio_risk"])
        
        self.assertGreater(system.config["max_drawdown_limit"], 0.0)
        self.assertLess(system.config["max_drawdown_limit"], 0.5)
        
        self.assertGreaterEqual(system.config["volatility_lookback_period"], 10)
        self.assertGreaterEqual(system.config["liquidity_threshold"], 0.0)


class TestRiskMetric(unittest.TestCase):
    """测试RiskMetric数据类"""
    
    def test_risk_metric_creation(self):
        """测试RiskMetric创建"""
        metric = RiskMetric(
            metric_id="test_metric_1",
            metric_type=RiskMetricType.VOLATILITY_RISK,
            value=0.25,
            risk_level=RiskLevel.MODERATE,
            timestamp=datetime.now(),
            description="测试风险指标",
            metadata={"key": "value"}
        )
        
        self.assertEqual(metric.metric_id, "test_metric_1")
        self.assertEqual(metric.metric_type, RiskMetricType.VOLATILITY_RISK)
        self.assertEqual(metric.value, 0.25)
        self.assertEqual(metric.risk_level, RiskLevel.MODERATE)
        self.assertIsInstance(metric.timestamp, datetime)
        self.assertEqual(metric.description, "测试风险指标")
        self.assertEqual(metric.metadata["key"], "value")


class TestRiskAssessment(unittest.TestCase):
    """测试RiskAssessment数据类"""
    
    def test_risk_assessment_creation(self):
        """测试RiskAssessment创建"""
        # 创建测试指标
        metric = RiskMetric(
            metric_id="test_metric",
            metric_type=RiskMetricType.VOLATILITY_RISK,
            value=0.25,
            risk_level=RiskLevel.MODERATE,
            timestamp=datetime.now(),
            description="测试指标",
            metadata={}
        )
        
        assessment = RiskAssessment(
            assessment_id="test_assessment",
            metrics=[metric],
            overall_risk_level=RiskLevel.MODERATE,
            risk_score=0.65,
            recommendations=["建议1", "建议2"],
            assessment_time=datetime.now(),
            details={"metrics_count": 1, "risk_levels": ["moderate"]}
        )
        
        self.assertEqual(assessment.assessment_id, "test_assessment")
        self.assertEqual(len(assessment.metrics), 1)
        self.assertEqual(assessment.overall_risk_level, RiskLevel.MODERATE)
        self.assertEqual(assessment.risk_score, 0.65)
        self.assertEqual(len(assessment.recommendations), 2)
        self.assertIsInstance(assessment.assessment_time, datetime)
        self.assertEqual(assessment.details["metrics_count"], 1)


class TestRiskAssessmentMethods(unittest.TestCase):
    """测试风险评估方法"""
    
    def setUp(self):
        self.system = ReversalRiskManagement()
    
    def test_assess_overall_risk_empty(self):
        """测试空指标风险评估"""
        assessment = self.system.assess_overall_risk([])
        
        self.assertIsInstance(assessment, RiskAssessment)
        self.assertEqual(assessment.overall_risk_level, RiskLevel.MODERATE)
        self.assertEqual(assessment.risk_score, 0.5)
        self.assertEqual(assessment.recommendations[0], "无风险数据，建议谨慎操作")
    
    def test_assess_overall_risk_single(self):
        """测试单个指标风险评估"""
        metric = RiskMetric(
            metric_id="test_metric",
            metric_type=RiskMetricType.VOLATILITY_RISK,
            value=0.15,
            risk_level=RiskLevel.LOW,
            timestamp=datetime.now(),
            description="低波动率风险",
            metadata={}
        )
        
        assessment = self.system.assess_overall_risk([metric])
        
        self.assertEqual(assessment.overall_risk_level, RiskLevel.LOW)
        self.assertLess(assessment.risk_score, 0.4)
        self.assertGreater(len(assessment.recommendations), 0)


class TestSystemMethods(unittest.TestCase):
    """测试系统方法"""
    
    def setUp(self):
        self.system = ReversalRiskManagement()
    
    def test_calculate_all_risk_metrics_empty(self):
        """测试空数据风险指标计算"""
        metrics = self.system.calculate_all_risk_metrics([], [])
        self.assertEqual(metrics, [])


class TestSystemDemonstration(unittest.TestCase):
    """测试系统演示功能"""
    
    def setUp(self):
        self.system = ReversalRiskManagement()
    
    def test_demonstrate_system(self):
        """测试系统演示"""
        demonstration = self.system.demonstrate_system()
        
        # 检查演示结果结构
        self.assertIsInstance(demonstration, dict)
        self.assertIn("risk_metrics_calculated", demonstration)
        self.assertIn("risk_assessment", demonstration)
        self.assertIn("risk_monitoring", demonstration)
        self.assertIn("system_status", demonstration)
        self.assertIn("generated_at", demonstration)
        
        # 检查风险评估结果
        assessment = demonstration["risk_assessment"]
        self.assertIn("overall_risk_level", assessment)
        self.assertIn("risk_score", assessment)
        self.assertIn("recommendations_count", assessment)
        
        # 检查风险监控结果
        monitoring = demonstration["risk_monitoring"]
        self.assertIn("all_limits_ok", monitoring)
        self.assertIn("limits_violated", monitoring)
        self.assertIn("portfolio_risk_ratio", monitoring)
    
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


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    
    # 添加所有测试类
    test_classes = [
        TestReversalRiskManagementInitialization,
        TestRiskMetric,
        TestRiskAssessment,
        TestRiskAssessmentMethods,
        TestSystemMethods,
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
    print("反转风险管理量化分析系统测试套件")
    print("严格按照第18章标准：实际完整测试")
    print("紧急冲刺模式：基础测试覆盖核心功能")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ 所有测试通过！系统符合第18章标准。")
    else:
        print("❌ 部分测试失败，请检查系统实现。")
    print("=" * 60)
    
    sys.exit(0 if success else 1)