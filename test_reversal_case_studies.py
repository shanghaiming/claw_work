"""
反转实战案例量化分析系统测试
严格按照第18章标准：实际完整测试，非伪代码框架
紧急冲刺最终阶段：基础测试覆盖核心功能
"""

import unittest
import sys
import os
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from reversal_case_studies import (
    ReversalCaseStudiesSystem,
    ReversalCase,
    CaseMatchResult,
    CaseCategory,
    MarketCondition,
    CaseOutcome,
)


class TestReversalCaseStudiesSystemInitialization(unittest.TestCase):
    """测试反转案例系统初始化"""
    
    def test_system_initialization_internal(self):
        """测试内部数据源系统初始化"""
        system = ReversalCaseStudiesSystem(data_source="internal")
        
        # 检查配置
        self.assertIn("min_similarity_score", system.config)
        self.assertIn("max_cases_to_return", system.config)
        self.assertIn("pattern_weight", system.config)
        self.assertIn("market_condition_weight", system.config)
        self.assertIn("timeframe_weight", system.config)
        
        # 检查数据库是否初始化
        self.assertIsInstance(system.case_database, list)
        self.assertGreater(len(system.case_database), 0)
    
    def test_system_initialization_external(self):
        """测试外部数据源系统初始化"""
        system = ReversalCaseStudiesSystem(data_source="external")
        
        # 检查配置
        self.assertIn("min_similarity_score", system.config)
        self.assertIn("max_cases_to_return", system.config)
        
        # 外部数据源可能没有初始化内置数据库
        self.assertIsInstance(system.case_database, list)
    
    def test_config_values(self):
        """测试配置值有效性"""
        system = ReversalCaseStudiesSystem()
        
        # 检查权重总和（应该接近1.0）
        pattern_weight = system.config["pattern_weight"]
        market_weight = system.config["market_condition_weight"]
        timeframe_weight = system.config["timeframe_weight"]
        
        total_weight = pattern_weight + market_weight + timeframe_weight
        self.assertGreater(total_weight, 0.95)
        self.assertLess(total_weight, 1.05)
        
        # 检查阈值
        self.assertGreater(system.config["min_similarity_score"], 0.0)
        self.assertLess(system.config["min_similarity_score"], 1.0)


class TestReversalCase(unittest.TestCase):
    """测试ReversalCase数据类"""
    
    def test_case_creation(self):
        """测试案例创建"""
        case = ReversalCase(
            case_id="TEST-001",
            case_name="测试案例",
            category=CaseCategory.DOUBLE_TOP_BOTTOM,
            market_condition=MarketCondition.TRENDING,
            timeframe="日线",
            symbol="TEST",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 31),
            pattern_formation_days=20,
            price_move_percentage=10.5,
            volume_change_percentage=25.3,
            outcome=CaseOutcome.SUCCESSFUL_REVERSAL,
            key_lessons=["测试教训1", "测试教训2"],
            success_factors=["成功因素1"],
            failure_reasons=[],
            entry_price=100.0,
            exit_price=110.5,
            profit_loss_percentage=10.5,
            risk_reward_ratio=2.5,
            confidence_score=0.85,
            notes="测试备注",
        )
        
        self.assertEqual(case.case_id, "TEST-001")
        self.assertEqual(case.case_name, "测试案例")
        self.assertEqual(case.category, CaseCategory.DOUBLE_TOP_BOTTOM)
        self.assertEqual(case.market_condition, MarketCondition.TRENDING)
        self.assertEqual(case.timeframe, "日线")
        self.assertEqual(case.symbol, "TEST")
        self.assertEqual(case.pattern_formation_days, 20)
        self.assertEqual(case.price_move_percentage, 10.5)
        self.assertEqual(case.volume_change_percentage, 25.3)
        self.assertEqual(case.outcome, CaseOutcome.SUCCESSFUL_REVERSAL)
        self.assertEqual(len(case.key_lessons), 2)
        self.assertEqual(len(case.success_factors), 1)
        self.assertEqual(len(case.failure_reasons), 0)
        self.assertEqual(case.entry_price, 100.0)
        self.assertEqual(case.exit_price, 110.5)
        self.assertEqual(case.profit_loss_percentage, 10.5)
        self.assertEqual(case.risk_reward_ratio, 2.5)
        self.assertEqual(case.confidence_score, 0.85)
        self.assertEqual(case.notes, "测试备注")


class TestCaseMatchResult(unittest.TestCase):
    """测试CaseMatchResult数据类"""
    
    def setUp(self):
        # 创建测试案例
        self.test_case = ReversalCase(
            case_id="TEST-001",
            case_name="测试案例",
            category=CaseCategory.DOUBLE_TOP_BOTTOM,
            market_condition=MarketCondition.TRENDING,
            timeframe="日线",
            symbol="TEST",
            start_date=datetime(2023, 1, 1),
            end_date=datetime(2023, 1, 31),
            pattern_formation_days=20,
            price_move_percentage=10.5,
            volume_change_percentage=25.3,
            outcome=CaseOutcome.SUCCESSFUL_REVERSAL,
            key_lessons=["测试教训"],
            success_factors=["成功因素"],
            failure_reasons=[],
            entry_price=100.0,
            exit_price=110.5,
            profit_loss_percentage=10.5,
            risk_reward_ratio=2.5,
            confidence_score=0.85,
        )
    
    def test_match_result_creation(self):
        """测试匹配结果创建"""
        match_result = CaseMatchResult(
            current_situation_id="SIT-001",
            matched_case=self.test_case,
            similarity_score=0.75,
            matching_factors=["模式相似", "市场条件匹配"],
            mismatching_factors=["时间框架不同"],
            predicted_outcome=CaseOutcome.SUCCESSFUL_REVERSAL,
            predicted_confidence=0.8,
            recommended_actions=["考虑入场", "应用风险管理"],
            risk_warnings=["历史表现不代表未来"],
            match_timestamp=datetime.now(),
        )
        
        self.assertEqual(match_result.current_situation_id, "SIT-001")
        self.assertEqual(match_result.matched_case.case_id, "TEST-001")
        self.assertEqual(match_result.similarity_score, 0.75)
        self.assertEqual(len(match_result.matching_factors), 2)
        self.assertEqual(len(match_result.mismatching_factors), 1)
        self.assertEqual(match_result.predicted_outcome, CaseOutcome.SUCCESSFUL_REVERSAL)
        self.assertEqual(match_result.predicted_confidence, 0.8)
        self.assertEqual(len(match_result.recommended_actions), 2)
        self.assertEqual(len(match_result.risk_warnings), 1)
        self.assertIsInstance(match_result.match_timestamp, datetime)


class TestDatabaseManagement(unittest.TestCase):
    """测试数据库管理功能"""
    
    def setUp(self):
        self.system = ReversalCaseStudiesSystem(data_source="internal")
    
    def test_add_case(self):
        """测试添加案例"""
        initial_count = len(self.system.case_database)
        
        new_case = ReversalCase(
            case_id="NEW-001",
            case_name="新案例",
            category=CaseCategory.HEAD_SHOULDERS,
            market_condition=MarketCondition.RANGING,
            timeframe="4小时",
            symbol="NEW",
            start_date=datetime.now(),
            end_date=datetime.now(),
            pattern_formation_days=15,
            price_move_percentage=8.5,
            volume_change_percentage=30.0,
            outcome=CaseOutcome.SUCCESSFUL_REVERSAL,
            key_lessons=["新教训"],
            success_factors=["新因素"],
            failure_reasons=[],
            entry_price=50.0,
            exit_price=54.25,
            profit_loss_percentage=8.5,
            risk_reward_ratio=2.2,
            confidence_score=0.78,
        )
        
        result = self.system.add_case(new_case)
        
        self.assertTrue(result)
        self.assertEqual(len(self.system.case_database), initial_count + 1)
    
    def test_add_duplicate_case(self):
        """测试添加重复案例"""
        # 获取现有案例ID
        existing_id = self.system.case_database[0].case_id
        
        duplicate_case = ReversalCase(
            case_id=existing_id,
            case_name="重复案例",
            category=CaseCategory.DOUBLE_TOP_BOTTOM,
            market_condition=MarketCondition.TRENDING,
            timeframe="日线",
            symbol="DUP",
            start_date=datetime.now(),
            end_date=datetime.now(),
            pattern_formation_days=10,
            price_move_percentage=5.0,
            volume_change_percentage=20.0,
            outcome=CaseOutcome.SUCCESSFUL_REVERSAL,
            key_lessons=[],
            success_factors=[],
            failure_reasons=[],
            entry_price=100.0,
            exit_price=105.0,
            profit_loss_percentage=5.0,
            risk_reward_ratio=1.5,
            confidence_score=0.7,
        )
        
        result = self.system.add_case(duplicate_case)
        
        self.assertFalse(result)
    
    def test_search_cases_empty(self):
        """测试空数据库搜索"""
        empty_system = ReversalCaseStudiesSystem(data_source="external")
        results = empty_system.search_cases()
        
        self.assertEqual(len(results), 0)
    
    def test_search_cases_by_category(self):
        """测试按类别搜索案例"""
        results = self.system.search_cases(category=CaseCategory.DOUBLE_TOP_BOTTOM)
        
        self.assertIsInstance(results, list)
        if results:
            for case in results:
                self.assertEqual(case.category, CaseCategory.DOUBLE_TOP_BOTTOM)


class TestStatisticsMethods(unittest.TestCase):
    """测试统计方法"""
    
    def setUp(self):
        self.system = ReversalCaseStudiesSystem(data_source="internal")
    
    def test_get_case_statistics_non_empty(self):
        """测试非空数据库统计"""
        stats = self.system.get_case_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertIn("total_cases", stats)
        self.assertIn("category_distribution", stats)
        self.assertIn("outcome_distribution", stats)
        self.assertIn("performance_metrics", stats)
        self.assertIn("database_health", stats)
        
        self.assertGreater(stats["total_cases"], 0)
    
    def test_get_case_statistics_empty(self):
        """测试空数据库统计"""
        empty_system = ReversalCaseStudiesSystem(data_source="external")
        stats = empty_system.get_case_statistics()
        
        self.assertIsInstance(stats, dict)
        self.assertEqual(stats["total_cases"], 0)
        self.assertIn("message", stats)


class TestSystemDemonstration(unittest.TestCase):
    """测试系统演示功能"""
    
    def setUp(self):
        self.system = ReversalCaseStudiesSystem(data_source="internal")
    
    def test_demonstrate_system(self):
        """测试系统演示"""
        demonstration = self.system.demonstrate_system()
        
        # 检查演示结果结构
        self.assertIsInstance(demonstration, dict)
        self.assertIn("system_name", demonstration)
        self.assertIn("demonstration_time", demonstration)
        self.assertIn("case_database_stats", demonstration)
        self.assertIn("example_cases_found", demonstration)
        self.assertIn("matched_cases_found", demonstration)
        self.assertIn("quality_evaluations_performed", demonstration)
        self.assertIn("system_status", demonstration)
    
    def test_generate_system_report(self):
        """测试系统报告生成"""
        report = self.system.generate_system_report()
        
        # 检查报告结构
        self.assertIsInstance(report, dict)
        self.assertIn("system_name", report)
        self.assertIn("version", report)
        self.assertIn("generated_at", report)
        self.assertIn("data_source", report)
        self.assertIn("system_config", report)
        self.assertIn("database_summary", report)
        self.assertIn("capabilities", report)
        self.assertIn("performance_metrics", report)
        self.assertIn("recommendations", report)


def run_all_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    
    # 添加所有测试类
    test_classes = [
        TestReversalCaseStudiesSystemInitialization,
        TestReversalCase,
        TestCaseMatchResult,
        TestDatabaseManagement,
        TestStatisticsMethods,
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
    print("反转实战案例量化分析系统测试套件")
    print("严格按照第18章标准：实际完整测试")
    print("紧急冲刺最终阶段：基础测试覆盖核心功能")
    print("=" * 60)
    
    success = run_all_tests()
    
    print("=" * 60)
    if success:
        print("✅ 所有测试通过！系统符合第18章标准。")
    else:
        print("❌ 部分测试失败，请检查系统实现。")
    print("=" * 60)
    
    sys.exit(0 if success else 1)