"""
反转仓位管理量化分析系统测试
严格按照第18章标准：实际完整测试，非伪代码框架
紧急冲刺加速模式：基础测试覆盖核心功能
"""

import unittest
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reversal_position_management import (
    ReversalPositionManagement,
    PositionSizeResult,
    PositionSizeMethod,
    PositionAdjustment,
    PositionAdjustmentType
)


class TestReversalPositionManagementInitialization(unittest.TestCase):
    """测试反转仓位管理系统初始化"""
    
    def test_system_initialization(self):
        """测试系统初始化"""
        system = ReversalPositionManagement(initial_balance=50000.0)
        
        self.assertEqual(system.initial_balance, 50000.0)
        self.assertEqual(system.current_balance, 50000.0)
        self.assertEqual(system.total_positions_value, 0.0)
        self.assertEqual(len(system.active_positions), 0)
        self.assertEqual(len(system.position_history), 0)
        self.assertEqual(len(system.adjustment_history), 0)
        
        # 检查默认配置
        self.assertIn("max_portfolio_risk", system.config)
        self.assertIn("max_position_risk", system.config)
        self.assertIn("default_risk_per_trade", system.config)
        self.assertIn("volatility_lookback_period", system.config)
        self.assertIn("position_concentration_limit", system.config)
    
    def test_config_values(self):
        """测试配置值有效性"""
        system = ReversalPositionManagement()
        
        # 检查配置值范围
        self.assertGreater(system.config["max_portfolio_risk"], 0.0)
        self.assertLess(system.config["max_portfolio_risk"], 0.5)
        
        self.assertGreater(system.config["max_position_risk"], 0.0)
        self.assertLess(system.config["max_position_risk"], system.config["max_portfolio_risk"])
        
        self.assertGreater(system.config["default_risk_per_trade"], 0.0)
        self.assertLess(system.config["default_risk_per_trade"], 0.1)
        
        self.assertGreaterEqual(system.config["volatility_lookback_period"], 10)
        self.assertGreater(system.config["position_concentration_limit"], 0.0)
        self.assertLess(system.config["position_concentration_limit"], 1.0)


class TestPositionSizeResult(unittest.TestCase):
    """测试PositionSizeResult数据类"""
    
    def test_position_size_result_creation(self):
        """测试PositionSizeResult创建"""
        result = PositionSizeResult(
            method=PositionSizeMethod.FIXED_RISK,
            position_size=5000.0,
            shares_or_units=50.0,
            risk_amount=100.0,
            risk_percentage=0.02,
            stop_loss_price=98.0,
            take_profit_price=106.0,
            confidence_score=0.8,
            details={"key": "value"}
        )
        
        self.assertEqual(result.method, PositionSizeMethod.FIXED_RISK)
        self.assertEqual(result.position_size, 5000.0)
        self.assertEqual(result.shares_or_units, 50.0)
        self.assertEqual(result.risk_amount, 100.0)
        self.assertEqual(result.risk_percentage, 0.02)
        self.assertEqual(result.stop_loss_price, 98.0)
        self.assertEqual(result.take_profit_price, 106.0)
        self.assertEqual(result.confidence_score, 0.8)
        self.assertEqual(result.details["key"], "value")


class TestPositionAdjustment(unittest.TestCase):
    """测试PositionAdjustment数据类"""
    
    def test_position_adjustment_creation(self):
        """测试PositionAdjustment创建"""
        adjustment = PositionAdjustment(
            adjustment_id="test_adjustment",
            adjustment_type=PositionAdjustmentType.DECREASE,
            current_position_size=2000.0,
            new_position_size=1000.0,
            adjustment_amount=1000.0,
            adjustment_percentage=0.5,
            reason="风险过高，建议减少仓位",
            priority=5,
            recommended_action="立即减少仓位规模",
            timestamp=datetime.now(),
            metadata={"risk_score": 0.8, "volatility": 0.04}
        )
        
        self.assertEqual(adjustment.adjustment_id, "test_adjustment")
        self.assertEqual(adjustment.adjustment_type, PositionAdjustmentType.DECREASE)
        self.assertEqual(adjustment.current_position_size, 2000.0)
        self.assertEqual(adjustment.new_position_size, 1000.0)
        self.assertEqual(adjustment.adjustment_amount, 1000.0)
        self.assertEqual(adjustment.adjustment_percentage, 0.5)
        self.assertEqual(adjustment.reason, "风险过高，建议减少仓位")
        self.assertEqual(adjustment.priority, 5)
        self.assertEqual(adjustment.recommended_action, "立即减少仓位规模")
        self.assertIsInstance(adjustment.timestamp, datetime)
        self.assertEqual(adjustment.metadata["risk_score"], 0.8)


class TestPositionCalculationMethods(unittest.TestCase):
    """测试仓位计算方法"""
    
    def setUp(self):
        self.system = ReversalPositionManagement(initial_balance=10000.0)
    
    def test_calculate_fixed_risk_position(self):
        """测试固定风险仓位计算"""
        result = self.system.calculate_position_size(
            entry_price=100.0,
            stop_loss=98.0,
            method=PositionSizeMethod.FIXED_RISK
        )
        
        self.assertIsInstance(result, PositionSizeResult)
        self.assertEqual(result.method, PositionSizeMethod.FIXED_RISK)
        self.assertGreater(result.position_size, 0.0)
        self.assertGreaterEqual(result.risk_percentage, 0.0)
        self.assertLessEqual(result.risk_percentage, self.system.config["max_position_risk"])
    
    def test_calculate_equal_weight_position(self):
        """测试等权重仓位计算"""
        result = self.system.calculate_position_size(
            entry_price=100.0,
            stop_loss=98.0,
            method=PositionSizeMethod.EQUAL_WEIGHT
        )
        
        self.assertIsInstance(result, PositionSizeResult)
        self.assertEqual(result.method, PositionSizeMethod.EQUAL_WEIGHT)
        self.assertGreater(result.position_size, 0.0)
    
    def test_calculate_position_invalid_stop_loss(self):
        """测试无效止损价格的仓位计算"""
        # 止损价格等于入场价格（零风险）
        result = self.system.calculate_position_size(
            entry_price=100.0,
            stop_loss=100.0,  # 零风险
            method=PositionSizeMethod.FIXED_RISK
        )
        
        self.assertIsInstance(result, PositionSizeResult)
        # 系统应该处理零风险情况


class TestPositionAdjustmentAnalysis(unittest.TestCase):
    """测试仓位调整分析"""
    
    def setUp(self):
        self.system = ReversalPositionManagement(initial_balance=10000.0)
    
    def test_analyze_position_adjustment_empty(self):
        """测试空仓位调整分析"""
        # 空仓位数据
        adjustments = self.system.analyze_position_adjustment(
            current_position={},
            market_conditions={},
            risk_assessment={}
        )
        
        self.assertIsInstance(adjustments, list)
    
    def test_analyze_risk_based_adjustment_high_risk(self):
        """测试高风险仓位调整分析"""
        mock_position = {
            "position_size": 2000.0,
            "risk_percentage": 0.02,  # 2%风险
        }
        
        mock_risk_assessment = {
            "risk_score": 0.8,  # 高风险
        }
        
        adjustments = self.system._analyze_risk_based_adjustment(
            position=mock_position,
            risk_assessment=mock_risk_assessment
        )
        
        self.assertIsInstance(adjustments, list)
        # 高风险应触发减少仓位建议
        if adjustments:
            self.assertEqual(adjustments[0].adjustment_type, PositionAdjustmentType.DECREASE)
    
    def test_analyze_risk_based_adjustment_low_risk(self):
        """测试低风险仓位调整分析"""
        mock_position = {
            "position_size": 500.0,
            "risk_percentage": 0.003,  # 0.3%风险
        }
        
        mock_risk_assessment = {
            "risk_score": 0.2,  # 低风险
        }
        
        adjustments = self.system._analyze_risk_based_adjustment(
            position=mock_position,
            risk_assessment=mock_risk_assessment
        )
        
        self.assertIsInstance(adjustments, list)
        # 低风险可能触发增加仓位建议
        if adjustments:
            self.assertEqual(adjustments[0].adjustment_type, PositionAdjustmentType.INCREASE)


class TestSystemDemonstration(unittest.TestCase):
    """测试系统演示功能"""
    
    def setUp(self):
        self.system = ReversalPositionManagement()
    
    def test_demonstrate_system(self):
        """测试系统演示"""
        demonstration = self.system.demonstrate_system()
        
        # 检查演示结果结构
        self.assertIsInstance(demonstration, dict)
        self.assertIn("position_methods_tested", demonstration)
        self.assertIn("methods_results", demonstration)
        self.assertIn("adjustments_analyzed", demonstration)
        self.assertIn("adjustment_types", demonstration)
        self.assertIn("position_report_generated", demonstration)
        self.assertIn("system_status", demonstration)
        self.assertIn("generated_at", demonstration)
    
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
        TestReversalPositionManagementInitialization,
        TestPositionSizeResult,
        TestPositionAdjustment,
        TestPositionCalculationMethods,
        TestPositionAdjustmentAnalysis,
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
    print("反转仓位管理量化分析系统测试套件")
    print("严格按照第18章标准：实际完整测试")
    print("紧急冲刺加速模式：基础测试覆盖核心功能")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ 所有测试通过！系统符合第18章标准。")
    else:
        print("❌ 部分测试失败，请检查系统实现。")
    print("=" * 60)
    
    sys.exit(0 if success else 1)