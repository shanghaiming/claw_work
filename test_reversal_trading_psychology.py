"""
反转交易心理量化分析系统测试
严格按照第18章标准：实际完整测试，非伪代码框架
紧急冲刺模式：基础测试覆盖核心功能
"""

import unittest
import sys
import os
from datetime import datetime, timedelta

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reversal_trading_psychology import (
    ReversalTradingPsychologySystem,
    PsychologicalAssessment,
    TradingDisciplineRecord,
    EmotionRecord,
    PsychologicalState,
    DisciplineCategory,
    EmotionIntensity,
)


class TestReversalTradingPsychologySystemInitialization(unittest.TestCase):
    """测试反转交易心理系统初始化"""
    
    def test_system_initialization(self):
        """测试系统初始化"""
        system = ReversalTradingPsychologySystem(trader_name="测试交易者")
        
        # 检查配置
        self.assertIn("min_assessment_interval_hours", system.config)
        self.assertIn("max_emotion_records_per_day", system.config)
        self.assertIn("discipline_scoring_weights", system.config)
        self.assertIn("improvement_threshold", system.config)
        
        # 检查数据存储
        self.assertEqual(len(system.psychological_assessments), 0)
        self.assertEqual(len(system.discipline_records), 0)
        self.assertEqual(len(system.emotion_records), 0)
        self.assertEqual(len(system.performance_data), 0)
        
        # 检查心理档案
        self.assertEqual(system.psychological_profile["trader_name"], "测试交易者")
        self.assertEqual(system.psychological_profile["total_trades_assessed"], 0)
    
    def test_config_values(self):
        """测试配置值有效性"""
        system = ReversalTradingPsychologySystem()
        
        # 检查权重总和（应该接近1.0）
        weights = system.config["discipline_scoring_weights"]
        total_weight = sum(weights.values())
        self.assertGreater(total_weight, 0.95)
        self.assertLess(total_weight, 1.05)
        
        # 检查阈值
        self.assertGreater(system.config["improvement_threshold"], 0.0)
        self.assertLess(system.config["improvement_threshold"], 1.0)
        
        self.assertGreater(system.config["high_performance_threshold"], 0.0)
        self.assertLess(system.config["high_performance_threshold"], 1.0)


class TestPsychologicalAssessment(unittest.TestCase):
    """测试PsychologicalAssessment数据类"""
    
    def test_assessment_creation(self):
        """测试评估创建"""
        assessment = PsychologicalAssessment(
            overall_state=PsychologicalState.CALM,
            confidence_score=0.8,
            discipline_score=0.7,
            emotion_stability_score=0.9,
            risk_tolerance=0.6,
            assessment_date=datetime.now(),
            category_scores={DisciplineCategory.RISK_MANAGEMENT: 0.8},
            dominant_emotions=[("calm", EmotionIntensity.LOW)],
            improvement_areas=["保持当前实践"],
        )
        
        self.assertEqual(assessment.overall_state, PsychologicalState.CALM)
        self.assertEqual(assessment.confidence_score, 0.8)
        self.assertEqual(assessment.discipline_score, 0.7)
        self.assertEqual(assessment.emotion_stability_score, 0.9)
        self.assertEqual(assessment.risk_tolerance, 0.6)
        self.assertIsInstance(assessment.assessment_date, datetime)
        self.assertIn(DisciplineCategory.RISK_MANAGEMENT, assessment.category_scores)
        self.assertEqual(len(assessment.dominant_emotions), 1)
        self.assertEqual(len(assessment.improvement_areas), 1)


class TestTradingDisciplineRecord(unittest.TestCase):
    """测试TradingDisciplineRecord数据类"""
    
    def test_record_creation(self):
        """测试记录创建"""
        record = TradingDisciplineRecord(
            trade_id="T001",
            category=DisciplineCategory.RISK_MANAGEMENT,
            action_taken="设置2%止损",
            planned_action="设置2%止损",
            deviation_score=0.0,
            timestamp=datetime.now(),
            notes="完全按计划执行",
        )
        
        self.assertEqual(record.trade_id, "T001")
        self.assertEqual(record.category, DisciplineCategory.RISK_MANAGEMENT)
        self.assertEqual(record.action_taken, "设置2%止损")
        self.assertEqual(record.planned_action, "设置2%止损")
        self.assertEqual(record.deviation_score, 0.0)
        self.assertIsInstance(record.timestamp, datetime)
        self.assertEqual(record.notes, "完全按计划执行")


class TestEmotionRecord(unittest.TestCase):
    """测试EmotionRecord数据类"""
    
    def test_record_creation(self):
        """测试记录创建"""
        record = EmotionRecord(
            emotion_type="自信",
            intensity=EmotionIntensity.MEDIUM,
            trigger_event="成功交易",
            impact_on_trading="positive - 提高了执行效率",
            coping_strategy="保持冷静，按计划执行",
            timestamp=datetime.now(),
            duration_minutes=30,
        )
        
        self.assertEqual(record.emotion_type, "自信")
        self.assertEqual(record.intensity, EmotionIntensity.MEDIUM)
        self.assertEqual(record.trigger_event, "成功交易")
        self.assertEqual(record.impact_on_trading, "positive - 提高了执行效率")
        self.assertEqual(record.coping_strategy, "保持冷静，按计划执行")
        self.assertIsInstance(record.timestamp, datetime)
        self.assertEqual(record.duration_minutes, 30)


class TestAssessmentMethods(unittest.TestCase):
    """测试评估方法"""
    
    def setUp(self):
        self.system = ReversalTradingPsychologySystem()
    
    def test_assess_psychological_state_empty(self):
        """测试空数据评估"""
        assessment = self.system.assess_psychological_state([], [], [])
        
        self.assertIsInstance(assessment, PsychologicalAssessment)
        self.assertIsInstance(assessment.overall_state, PsychologicalState)
        self.assertGreaterEqual(assessment.confidence_score, 0.0)
        self.assertLessEqual(assessment.confidence_score, 1.0)
        self.assertGreaterEqual(assessment.discipline_score, 0.0)
        self.assertLessEqual(assessment.discipline_score, 1.0)
        self.assertGreaterEqual(assessment.emotion_stability_score, 0.0)
        self.assertLessEqual(assessment.emotion_stability_score, 1.0)
    
    def test_calculate_discipline_score_empty(self):
        """测试空纪律数据分数计算"""
        score = self.system._calculate_discipline_score([])
        
        self.assertEqual(score, 0.5)  # 默认中等分数
    
    def test_calculate_emotion_stability_score_empty(self):
        """测试空情绪数据稳定性分数计算"""
        score = self.system._calculate_emotion_stability_score([])
        
        self.assertEqual(score, 0.7)  # 默认较高分数（无情绪记录视为稳定）
    
    def test_calculate_risk_tolerance_empty(self):
        """测试空交易数据风险容忍度计算"""
        score = self.system._calculate_risk_tolerance([])
        
        self.assertEqual(score, 0.5)  # 默认中等风险容忍度


class TestDisciplineManagement(unittest.TestCase):
    """测试纪律管理功能"""
    
    def setUp(self):
        self.system = ReversalTradingPsychologySystem()
    
    def test_record_discipline_violation(self):
        """测试记录纪律违规"""
        record = self.system.record_discipline_violation(
            trade_id="T001",
            category=DisciplineCategory.RISK_MANAGEMENT,
            planned_action="设置2%止损",
            actual_action="设置1.5%止损",
            deviation_score=0.25,
            notes="市场波动小，缩小止损",
        )
        
        self.assertIsInstance(record, TradingDisciplineRecord)
        self.assertEqual(record.trade_id, "T001")
        self.assertEqual(record.category, DisciplineCategory.RISK_MANAGEMENT)
        self.assertEqual(record.planned_action, "设置2%止损")
        self.assertEqual(record.action_taken, "设置1.5%止损")
        self.assertEqual(record.deviation_score, 0.25)
        self.assertEqual(record.notes, "市场波动小，缩小止损")
        
        # 检查是否已保存
        self.assertEqual(len(self.system.discipline_records), 1)
        self.assertEqual(self.system.discipline_records[0].trade_id, "T001")
    
    def test_analyze_discipline_patterns_empty(self):
        """测试空纪律模式分析"""
        analysis = self.system.analyze_discipline_patterns(lookback_days=7)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("analysis_date", analysis)
        self.assertEqual(analysis["total_records"], 0)
        self.assertIn("message", analysis)


class TestEmotionManagement(unittest.TestCase):
    """测试情绪管理功能"""
    
    def setUp(self):
        self.system = ReversalTradingPsychologySystem()
    
    def test_record_emotion(self):
        """测试记录情绪"""
        record = self.system.record_emotion(
            emotion_type="自信",
            intensity=EmotionIntensity.MEDIUM,
            trigger_event="成功交易",
            impact_on_trading="positive - 提高了执行效率",
            coping_strategy="保持冷静，按计划执行",
            duration_minutes=30,
        )
        
        self.assertIsInstance(record, EmotionRecord)
        self.assertEqual(record.emotion_type, "自信")
        self.assertEqual(record.intensity, EmotionIntensity.MEDIUM)
        self.assertEqual(record.trigger_event, "成功交易")
        self.assertEqual(record.impact_on_trading, "positive - 提高了执行效率")
        self.assertEqual(record.coping_strategy, "保持冷静，按计划执行")
        self.assertEqual(record.duration_minutes, 30)
        
        # 检查是否已保存
        self.assertEqual(len(self.system.emotion_records), 1)
        self.assertEqual(self.system.emotion_records[0].emotion_type, "自信")
    
    def test_analyze_emotion_patterns_empty(self):
        """测试空情绪模式分析"""
        analysis = self.system.analyze_emotion_patterns(lookback_days=7)
        
        self.assertIsInstance(analysis, dict)
        self.assertIn("analysis_date", analysis)
        self.assertEqual(analysis["total_records"], 0)
        self.assertIn("message", analysis)


class TestSystemDemonstration(unittest.TestCase):
    """测试系统演示功能"""
    
    def setUp(self):
        self.system = ReversalTradingPsychologySystem()
    
    def test_demonstrate_system(self):
        """测试系统演示"""
        demonstration = self.system.demonstrate_system()
        
        # 检查演示结果结构
        self.assertIsInstance(demonstration, dict)
        self.assertIn("system_name", demonstration)
        self.assertIn("demonstration_time", demonstration)
        self.assertIn("psychological_assessment", demonstration)
        self.assertIn("training_plan_generated", demonstration)
        self.assertIn("discipline_analysis", demonstration)
        self.assertIn("emotion_analysis", demonstration)
        self.assertIn("system_status", demonstration)
    
    def test_generate_system_report(self):
        """测试系统报告生成"""
        report = self.system.generate_system_report()
        
        # 检查报告结构
        self.assertIsInstance(report, dict)
        self.assertIn("system_name", report)
        self.assertIn("version", report)
        self.assertIn("generated_at", report)
        self.assertIn("trader_name", report)
        self.assertIn("system_config", report)
        self.assertIn("data_summary", report)
        self.assertIn("capabilities", report)
        self.assertIn("psychological_profile", report)
        self.assertIn("performance_metrics", report)
        self.assertIn("recommendations", report)


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    
    # 添加所有测试类
    test_classes = [
        TestReversalTradingPsychologySystemInitialization,
        TestPsychologicalAssessment,
        TestTradingDisciplineRecord,
        TestEmotionRecord,
        TestAssessmentMethods,
        TestDisciplineManagement,
        TestEmotionManagement,
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
    print("反转交易心理量化分析系统测试套件")
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