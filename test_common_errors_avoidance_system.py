#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
常见错误与避免系统测试
第31章：常见错误与避免
AL Brooks《价格行为交易之区间篇》

测试标准：按照第18章标准（完整实际代码测试）
1. 错误定义和分类测试
2. 错误检测引擎测试
3. 错误记录和统计测试
4. 纠正措施测试
5. 预防计划测试
6. 学习系统测试
"""

import unittest
import tempfile
import os
import json
from datetime import datetime, timedelta
from common_errors_avoidance_system import (
    CommonErrorsAvoidanceSystem,
    TradingError,
    ErrorOccurrence,
    ErrorPreventionPlan,
    ErrorCategory,
    ErrorSeverity,
    ErrorFrequency
)


class TestTradingError(unittest.TestCase):
    """测试交易错误数据结构"""
    
    def test_trading_error_creation(self):
        """测试交易错误创建"""
        error = TradingError(
            error_id="test_001",
            error_name="测试错误",
            category=ErrorCategory.PSYCHOLOGICAL,
            severity=ErrorSeverity.MEDIUM,
            frequency=ErrorFrequency.OCCASIONAL,
            description="测试错误描述",
            root_cause="测试根本原因",
            typical_symptoms=["症状1", "症状2"],
            common_triggers=["触发1", "触发2"],
            prevention_strategies=["预防1", "预防2"],
            correction_actions=["纠正1", "纠正2"],
            learning_questions=["问题1", "问题2"],
            detection_rules=[{"condition": "test > 1", "severity": "medium"}],
            risk_score=50.0,
            impact_score=60.0,
            difficulty_to_fix=0.5,
            related_errors=["rel_001"],
            tags=["test", "error"],
            examples=[{"description": "测试案例", "lesson": "测试教训"}]
        )
        
        self.assertEqual(error.error_id, "test_001")
        self.assertEqual(error.error_name, "测试错误")
        self.assertEqual(error.category, ErrorCategory.PSYCHOLOGICAL)
        self.assertEqual(error.severity, ErrorSeverity.MEDIUM)
        self.assertEqual(error.frequency, ErrorFrequency.OCCASIONAL)
        self.assertEqual(error.risk_score, 50.0)
        self.assertEqual(error.impact_score, 60.0)
        self.assertEqual(error.difficulty_to_fix, 0.5)
        self.assertEqual(len(error.typical_symptoms), 2)
        self.assertEqual(len(error.prevention_strategies), 2)
        self.assertEqual(len(error.correction_actions), 2)
    
    def test_trading_error_serialization(self):
        """测试交易错误序列化和反序列化"""
        error = TradingError(
            error_id="test_002",
            error_name="序列化测试",
            category=ErrorCategory.RISK_MANAGEMENT,
            severity=ErrorSeverity.HIGH,
            frequency=ErrorFrequency.FREQUENT,
            description="测试描述",
            root_cause="测试原因",
            typical_symptoms=["症状"],
            common_triggers=["触发"],
            prevention_strategies=["预防"],
            correction_actions=["纠正"],
            learning_questions=["问题"],
            detection_rules=[{"condition": "rule", "severity": "high"}],
            risk_score=75.0,
            impact_score=80.0,
            difficulty_to_fix=0.6,
            related_errors=[],
            tags=["serialization"],
            examples=[]
        )
        
        # 转换为字典
        error_dict = error.to_dict()
        
        # 验证字典内容
        self.assertEqual(error_dict['error_id'], "test_002")
        self.assertEqual(error_dict['category'], "risk_management")
        self.assertEqual(error_dict['severity'], "high")
        self.assertEqual(error_dict['frequency'], "frequent")
        self.assertIn('created_at', error_dict)
        self.assertIn('updated_at', error_dict)
        
        # 从字典创建
        error_from_dict = TradingError.from_dict(error_dict)
        
        self.assertEqual(error_from_dict.error_id, error.error_id)
        self.assertEqual(error_from_dict.error_name, error.error_name)
        self.assertEqual(error_from_dict.category, error.category)
        self.assertEqual(error_from_dict.severity, error.severity)
        self.assertEqual(error_from_dict.frequency, error.frequency)
        self.assertEqual(error_from_dict.risk_score, error.risk_score)


class TestErrorOccurrence(unittest.TestCase):
    """测试错误发生记录"""
    
    def test_error_occurrence_creation(self):
        """测试错误发生记录创建"""
        timestamp = datetime.now()
        
        occurrence = ErrorOccurrence(
            occurrence_id="occ_001",
            error_id="psych_001",
            timestamp=timestamp,
            context={"market": "bullish", "confidence": 0.9},
            detected_by=["rule_001", "monitor_001"],
            severity_at_occurrence=ErrorSeverity.HIGH,
            impact_assessment={"financial": 0.7, "psychological": 0.8},
            correction_applied=["减仓", "暂停交易"],
            learning_extracted=["学习点1", "学习点2"],
            prevented_future=True,
            recurrence_count=2,
            notes="测试备注"
        )
        
        self.assertEqual(occurrence.occurrence_id, "occ_001")
        self.assertEqual(occurrence.error_id, "psych_001")
        self.assertEqual(occurrence.timestamp, timestamp)
        self.assertEqual(occurrence.severity_at_occurrence, ErrorSeverity.HIGH)
        self.assertEqual(len(occurrence.detected_by), 2)
        self.assertEqual(len(occurrence.correction_applied), 2)
        self.assertEqual(len(occurrence.learning_extracted), 2)
        self.assertTrue(occurrence.prevented_future)
        self.assertEqual(occurrence.recurrence_count, 2)
        self.assertEqual(occurrence.notes, "测试备注")
    
    def test_error_occurrence_serialization(self):
        """测试错误发生记录序列化"""
        timestamp = datetime.now()
        
        occurrence = ErrorOccurrence(
            occurrence_id="occ_002",
            error_id="disc_001",
            timestamp=timestamp,
            context={"stop_loss": "not_set"},
            detected_by=["critical_monitor"],
            severity_at_occurrence=ErrorSeverity.CRITICAL,
            impact_assessment={"financial": 0.9},
            correction_applied=["设置止损"],
            learning_extracted=["必须设止损"],
            resolved_at=timestamp + timedelta(hours=1)
        )
        
        # 转换为字典
        occurrence_dict = occurrence.to_dict()
        
        # 验证字典内容
        self.assertEqual(occurrence_dict['occurrence_id'], "occ_002")
        self.assertEqual(occurrence_dict['error_id'], "disc_001")
        self.assertEqual(occurrence_dict['severity_at_occurrence'], "critical")
        self.assertIn('timestamp', occurrence_dict)
        self.assertIn('resolved_at', occurrence_dict)
        
        # 从字典创建
        occurrence_from_dict = ErrorOccurrence.from_dict(occurrence_dict)
        
        self.assertEqual(occurrence_from_dict.occurrence_id, occurrence.occurrence_id)
        self.assertEqual(occurrence_from_dict.error_id, occurrence.error_id)
        self.assertEqual(occurrence_from_dict.severity_at_occurrence, occurrence.severity_at_occurrence)
        self.assertIsNotNone(occurrence_from_dict.resolved_at)


class TestCommonErrorsAvoidanceSystem(unittest.TestCase):
    """测试常见错误避免系统"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时文件用于存储测试数据
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        # 创建系统实例
        self.system = CommonErrorsAvoidanceSystem(
            storage_path=self.temp_file.name,
            enable_realtime_detection=True,
            enable_learning_feedback=True
        )
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_system_initialization(self):
        """测试系统初始化"""
        self.assertIsNotNone(self.system.error_knowledge_base)
        self.assertIsNotNone(self.system.detection_rules)
        self.assertIsNotNone(self.system.detection_patterns)
        self.assertIsNotNone(self.system.realtime_monitors)
        
        # 验证默认错误库已初始化
        self.assertGreater(len(self.system.error_knowledge_base), 0)
        self.assertIn('psych_001', self.system.error_knowledge_base)  # 过度自信
        self.assertIn('disc_001', self.system.error_knowledge_base)   # 不设止损
        self.assertIn('risk_001', self.system.error_knowledge_base)   # 仓位过大
        
        # 验证统计信息
        self.assertGreater(self.system.system_statistics['total_errors_defined'], 0)
    
    def test_error_detection_basic(self):
        """测试基本错误检测"""
        # 创建测试上下文
        trading_context = {
            'confidence_level': 0.9,  # 过度自信
            'risk_taking_increased': True,
            'trades_today': 12,       # 过度交易
            'daily_trade_limit': 5,
            'stop_loss_not_set': False
        }
        
        # 检测错误
        detected_errors = self.system.detect_errors(trading_context)
        
        # 应该检测到至少过度自信错误
        self.assertGreater(len(detected_errors), 0)
        
        # 验证检测结果格式
        for error in detected_errors:
            self.assertIn('error_id', error)
            self.assertIn('error_name', error)
            self.assertIn('severity', error)
            self.assertIn('detected_by', error)
            self.assertIn('recommended_actions', error)
            self.assertIn('prevention_strategies', error)
        
        # 检查具体错误
        error_ids = [e['error_id'] for e in detected_errors]
        
        # 过度自信应该被检测到
        if 'confidence_level' in trading_context and trading_context['confidence_level'] > 0.8:
            self.assertIn('psych_001', error_ids)
        
        # 过度交易应该被检测到
        if trading_context.get('trades_today', 0) > trading_context.get('daily_trade_limit', 5):
            self.assertIn('disc_002', error_ids)
    
    def test_error_detection_psychological(self):
        """测试心理错误检测"""
        trading_context = {
            'confidence_level': 0.85,      # 过度自信阈值
            'fear_level': 0.7,             # 恐惧交易阈值
            'missed_opportunities': 3,     # 错过机会
            'emotional_entry': True,       # 情绪化入场
            'market_condition': 'volatile'
        }
        
        detected_errors = self.system.detect_errors(trading_context)
        
        # 应该检测到心理错误
        psychological_errors = [e for e in detected_errors 
                               if self.system.error_knowledge_base[e['error_id']].category == ErrorCategory.PSYCHOLOGICAL]
        
        self.assertGreater(len(psychological_errors), 0)
    
    def test_error_detection_risk_management(self):
        """测试风险管理错误检测"""
        trading_context = {
            'position_size': 2.5,          # 仓位过大
            'max_position_size': 1.0,
            'risk_per_trade_percent': 3.0, # 风险超过2%
            'risk_reward_ratio': 0.8,      # 不合理风险回报比
            'required_win_rate': 75        # 要求过高胜率
        }
        
        detected_errors = self.system.detect_errors(trading_context)
        
        # 应该检测到风险管理错误
        risk_errors = [e for e in detected_errors 
                      if self.system.error_knowledge_base[e['error_id']].category == ErrorCategory.RISK_MANAGEMENT]
        
        self.assertGreater(len(risk_errors), 0)
    
    def test_error_detection_discipline(self):
        """测试纪律错误检测"""
        trading_context = {
            'stop_loss_not_set': True,     # 不设止损
            'trades_today': 8,             # 过度交易
            'daily_trade_limit': 5,
            'rule_violations_per_day': 4,  # 规则违反
            'plan_adherence_percent': 60   # 计划遵守率低
        }
        
        detected_errors = self.system.detect_errors(trading_context)
        
        # 应该检测到纪律错误
        discipline_errors = [e for e in detected_errors 
                           if self.system.error_knowledge_base[e['error_id']].category == ErrorCategory.DISCIPLINE]
        
        self.assertGreater(len(discipline_errors), 0)
        
        # 不设止损应该是严重错误
        critical_errors = [e for e in discipline_errors if e.get('severity') == 'critical']
        self.assertGreater(len(critical_errors), 0)
    
    def test_record_error_occurrence(self):
        """测试记录错误发生"""
        context = {
            'confidence_level': 0.9,
            'position_size': 2.0,
            'market': 'bullish',
            'emotional_state': 'excited'
        }
        
        result = self.system.record_error_occurrence(
            error_id='psych_001',  # 过度自信
            context=context,
            severity=ErrorSeverity.HIGH,
            notes="测试记录过度自信错误"
        )
        
        self.assertTrue(result['success'])
        self.assertIn('occurrence_id', result)
        self.assertEqual(result['error_name'], '过度自信')
        self.assertEqual(result['severity'], 'high')
        self.assertGreater(len(result['prevention_suggestions']), 0)
        self.assertGreater(len(result['correction_suggestions']), 0)
        
        # 验证记录已保存
        occurrence_id = result['occurrence_id']
        self.assertIn(occurrence_id, self.system.error_occurrences)
        
        occurrence = self.system.error_occurrences[occurrence_id]
        self.assertEqual(occurrence.error_id, 'psych_001')
        self.assertEqual(occurrence.severity_at_occurrence, ErrorSeverity.HIGH)
        self.assertEqual(occurrence.notes, "测试记录过度自信错误")
        
        # 验证统计已更新
        self.assertGreater(self.system.system_statistics['total_occurrences'], 0)
        self.assertIn('psych_001', self.system.error_statistics)
        self.assertGreater(self.system.error_statistics['psych_001']['occurrence_count'], 0)
    
    def test_record_invalid_error(self):
        """测试记录无效错误ID"""
        result = self.system.record_error_occurrence(
            error_id='invalid_error_id',
            context={},
            notes="测试无效错误"
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('valid_error_ids', result)
        self.assertIsInstance(result['valid_error_ids'], list)
        self.assertGreater(len(result['valid_error_ids']), 0)
    
    def test_apply_correction(self):
        """测试应用纠正措施"""
        # 先记录一个错误
        context = {'position_size': 3.0, 'max_allowed': 1.0}
        record_result = self.system.record_error_occurrence(
            error_id='risk_001',  # 仓位过大
            context=context,
            notes="测试仓位过大错误"
        )
        
        self.assertTrue(record_result['success'])
        occurrence_id = record_result['occurrence_id']
        
        # 应用纠正措施
        correction_actions = [
            "立即减仓至1.0",
            "重新评估风险承受能力",
            "暂停新交易1天"
        ]
        
        correction_result = self.system.apply_correction(
            occurrence_id=occurrence_id,
            correction_actions=correction_actions
        )
        
        self.assertTrue(correction_result['success'])
        self.assertEqual(correction_result['occurrence_id'], occurrence_id)
        self.assertEqual(correction_result['correction_applied'], correction_actions)
        self.assertGreater(len(correction_result['learning_points']), 0)
        self.assertIn('resolved_at', correction_result)
        
        # 验证发生记录已更新
        occurrence = self.system.error_occurrences[occurrence_id]
        self.assertEqual(occurrence.correction_applied, correction_actions)
        self.assertIsNotNone(occurrence.resolved_at)
        self.assertGreater(len(occurrence.learning_extracted), 0)
        
        # 验证统计已更新
        self.assertGreater(self.system.system_statistics['corrected_errors'], 0)
        self.assertGreater(self.system.error_statistics['risk_001']['correction_count'], 0)
    
    def test_apply_correction_invalid_occurrence(self):
        """测试应用纠正措施到无效发生记录"""
        result = self.system.apply_correction(
            occurrence_id='invalid_occ_id',
            correction_actions=["测试纠正"]
        )
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_create_prevention_plan(self):
        """测试创建错误预防计划"""
        trader_profile = {
            'trader_id': 'test_trader_001',
            'experience_years': 2,
            'weak_areas': ['discipline', 'risk_management'],
            'strong_areas': ['technical_analysis'],
            'success_criteria': '减少关键错误发生率50%'
        }
        
        # 创建预防计划
        plan_result = self.system.create_prevention_plan(trader_profile)
        
        self.assertTrue(plan_result['success'])
        self.assertIn('plan_id', plan_result)
        self.assertIn('focus_errors', plan_result)
        self.assertIn('error_names', plan_result)
        self.assertIn('prevention_strategies_count', plan_result)
        self.assertIn('implementation_steps', plan_result)
        self.assertIn('estimated_duration_days', plan_result)
        
        plan_id = plan_result['plan_id']
        
        # 验证计划已保存
        self.assertIn(plan_id, self.system.prevention_plans)
        
        plan = self.system.prevention_plans[plan_id]
        self.assertEqual(plan.trader_id, 'test_trader_001')
        self.assertGreater(len(plan.focus_errors), 0)
        self.assertGreater(len(plan.prevention_strategies), 0)
        self.assertEqual(len(plan.implementation_steps), 3)
        self.assertEqual(len(plan.monitoring_metrics), 3)
        self.assertEqual(len(plan.success_criteria), 4)
        self.assertTrue(plan.active)
    
    def test_create_prevention_plan_specific_errors(self):
        """测试创建特定错误的预防计划"""
        trader_profile = {
            'trader_id': 'test_trader_002',
            'experience_years': 1
        }
        
        # 指定重点关注错误
        focus_error_ids = ['psych_001', 'disc_001', 'risk_001']
        
        plan_result = self.system.create_prevention_plan(
            trader_profile=trader_profile,
            focus_error_ids=focus_error_ids
        )
        
        self.assertTrue(plan_result['success'])
        self.assertIn('plan_id', plan_result)
        
        # 验证关注错误
        plan_id = plan_result['plan_id']
        plan = self.system.prevention_plans[plan_id]
        
        # 计划应该包含指定的错误（如果有效）
        valid_error_ids = [eid for eid in focus_error_ids if eid in self.system.error_knowledge_base]
        
        for error_id in valid_error_ids:
            self.assertIn(error_id, plan.focus_errors)
    
    def test_create_prevention_plan_invalid_errors(self):
        """测试创建包含无效错误的预防计划"""
        trader_profile = {'trader_id': 'test'}
        
        # 包含无效错误ID
        focus_error_ids = ['psych_001', 'invalid_error_001', 'another_invalid']
        
        plan_result = self.system.create_prevention_plan(
            trader_profile=trader_profile,
            focus_error_ids=focus_error_ids
        )
        
        # 应该成功，但忽略无效错误
        self.assertTrue(plan_result['success'])
        
        plan_id = plan_result['plan_id']
        plan = self.system.prevention_plans[plan_id]
        
        # 应该只包含有效错误
        self.assertIn('psych_001', plan.focus_errors)
        self.assertNotIn('invalid_error_001', plan.focus_errors)
        self.assertNotIn('another_invalid', plan.focus_errors)
    
    def test_get_error_analysis_general(self):
        """测试获取一般错误分析"""
        analysis = self.system.get_error_analysis()
        
        self.assertIn('timestamp', analysis)
        self.assertIn('system_statistics', analysis)
        self.assertIn('total_errors_defined', analysis)
        self.assertIn('total_occurrences', analysis)
        self.assertIn('error_categories', analysis)
        self.assertIn('severity_distribution', analysis)
        self.assertIn('top_errors_by_frequency', analysis)
        self.assertIn('top_errors_by_severity', analysis)
        self.assertIn('improvement_opportunities', analysis)
        self.assertIn('recommendations', analysis)
        
        # 验证数据结构
        self.assertIsInstance(analysis['error_categories'], dict)
        self.assertIsInstance(analysis['severity_distribution'], dict)
        self.assertIsInstance(analysis['top_errors_by_frequency'], list)
        self.assertIsInstance(analysis['top_errors_by_severity'], list)
        
        # 应该包含默认错误
        self.assertGreater(analysis['total_errors_defined'], 0)
    
    def test_get_error_analysis_specific(self):
        """测试获取特定错误分析"""
        # 先记录一些错误发生
        context = {'test': True}
        self.system.record_error_occurrence('psych_001', context, notes="测试")
        self.system.record_error_occurrence('disc_001', context, notes="测试")
        
        # 获取特定错误分析
        analysis = self.system.get_error_analysis(error_id='psych_001')
        
        self.assertIn('timestamp', analysis)
        self.assertIn('system_statistics', analysis)
        self.assertIn('specific_error_analysis', analysis)
        
        specific = analysis['specific_error_analysis']
        self.assertIn('error_details', specific)
        self.assertIn('statistics', specific)
        self.assertIn('prevention_strategies', specific)
        self.assertIn('correction_actions', specific)
        self.assertIn('learning_questions', specific)
        self.assertIn('recent_occurrences', specific)
        
        # 验证错误详情
        details = specific['error_details']
        self.assertEqual(details['error_id'], 'psych_001')
        self.assertEqual(details['error_name'], '过度自信')
        self.assertEqual(details['category'], 'psychological')
        self.assertEqual(details['severity'], 'high')
    
    def test_get_error_analysis_invalid_error(self):
        """测试获取无效错误的分析"""
        analysis = self.system.get_error_analysis(error_id='invalid_error_id')
        
        self.assertFalse(analysis['success'])
        self.assertIn('error', analysis)
        self.assertIn('available_error_ids', analysis)
        self.assertIsInstance(analysis['available_error_ids'], list)
        self.assertGreater(len(analysis['available_error_ids']), 0)
    
    def test_generate_learning_report(self):
        """测试生成学习报告"""
        # 先记录一些错误发生
        context = {'learning_test': True}
        
        # 记录几个错误
        for i in range(5):
            error_id = 'psych_001' if i % 2 == 0 else 'disc_001'
            self.system.record_error_occurrence(
                error_id=error_id,
                context=context,
                notes=f"学习测试{i}"
            )
        
        # 应用一些纠正措施
        for occ_id in list(self.system.error_occurrences.keys())[:3]:
            self.system.apply_correction(
                occurrence_id=occ_id,
                correction_actions=["测试纠正"]
            )
        
        # 生成学习报告
        report = self.system.generate_learning_report(days_back=7, min_occurrences=1)
        
        self.assertIn('report_id', report)
        self.assertIn('period', report)
        self.assertIn('summary', report)
        self.assertIn('key_learnings', report)
        self.assertIn('patterns_identified', report)
        self.assertIn('action_items', report)
        self.assertIn('next_steps', report)
        
        # 验证报告内容
        summary = report['summary']
        self.assertGreater(summary['total_occurrences'], 0)
        self.assertGreater(summary['unique_errors'], 0)
        self.assertGreater(summary['corrected_errors'], 0)
        self.assertIn('correction_rate', summary)
        self.assertIn('prevention_rate', summary)
        
        # 验证学习点
        self.assertGreater(len(report['key_learnings']), 0)
        
        # 验证行动项
        self.assertIsInstance(report['action_items'], list)
        self.assertIsInstance(report['next_steps'], list)
    
    def test_generate_learning_report_no_data(self):
        """测试没有数据时生成学习报告"""
        # 使用全新的系统（没有发生记录）
        clean_system = CommonErrorsAvoidanceSystem(storage_path=None)
        
        report = clean_system.generate_learning_report(days_back=30)
        
        self.assertFalse(report['success'])
        self.assertIn('error', report)
        self.assertIn('days_back', report)
    
    def test_system_persistence(self):
        """测试系统数据持久化"""
        # 在原始系统中记录一些数据
        context = {'persistence_test': True}
        
        record_result = self.system.record_error_occurrence(
            error_id='psych_001',
            context=context,
            notes="持久化测试"
        )
        
        self.assertTrue(record_result['success'])
        
        # 创建预防计划
        plan_result = self.system.create_prevention_plan(
            trader_profile={'trader_id': 'persistence_trader'}
        )
        
        self.assertTrue(plan_result['success'])
        
        # 保存数据
        if self.system.storage_path:
            # 系统应该已自动保存，但我们可以强制检查
            self.system._save_data_to_storage()
            
            # 验证文件存在
            self.assertTrue(os.path.exists(self.system.storage_path))
            
            # 创建新系统实例并加载数据
            new_system = CommonErrorsAvoidanceSystem(
                storage_path=self.system.storage_path,
                enable_realtime_detection=True
            )
            
            # 验证数据已加载
            self.assertGreater(len(new_system.error_occurrences), 0)
            self.assertGreater(len(new_system.prevention_plans), 0)
            
            # 验证发生记录
            for occ_id, occurrence in new_system.error_occurrences.items():
                self.assertEqual(occurrence.error_id, 'psych_001')
                self.assertIn('persistence_test', occurrence.context)
            
            # 验证预防计划
            for plan_id, plan in new_system.prevention_plans.items():
                self.assertEqual(plan.trader_id, 'persistence_trader')
                self.assertGreater(len(plan.focus_errors), 0)
    
    def test_monitor_functions(self):
        """测试监控函数"""
        # 测试心理错误监控
        psych_context = {
            'confidence_level': 0.85,
            'fear_level': 0.7,
            'missed_opportunities': 3
        }
        
        psych_results = self.system._monitor_psychological_errors(psych_context)
        self.assertIsInstance(psych_results, list)
        
        # 测试风险管理监控
        risk_context = {
            'position_size': 2.5,
            'max_position_size': 1.0,
            'risk_per_trade_percent': 3.0
        }
        
        risk_results = self.system._monitor_risk_management_errors(risk_context)
        self.assertIsInstance(risk_results, list)
        
        # 测试执行错误监控
        exec_context = {
            'chasing_entry': True,
            'early_exit_ratio': 0.6
        }
        
        exec_results = self.system._monitor_execution_errors(exec_context)
        self.assertIsInstance(exec_results, list)
        
        # 测试纪律错误监控
        disc_context = {
            'stop_loss_not_set': True,
            'trades_today': 8,
            'daily_trade_limit': 5
        }
        
        disc_results = self.system._monitor_discipline_errors(disc_context)
        self.assertIsInstance(disc_results, list)
    
    def test_error_impact_assessment(self):
        """测试错误影响评估"""
        error = self.system.error_knowledge_base['psych_001']  # 过度自信
        
        context = {
            'financial_impact_factor': 0.8,
            'psychological_impact_factor': 0.7,
            'time_impact_factor': 0.5
        }
        
        impact = self.system._assess_impact(error, context)
        
        self.assertIn('financial_impact', impact)
        self.assertIn('psychological_impact', impact)
        self.assertIn('time_impact', impact)
        self.assertIn('learning_opportunity', impact)
        self.assertIn('overall_score', impact)
        
        # 验证分数在合理范围内
        for key in ['financial_impact', 'psychological_impact', 'time_impact', 'learning_opportunity', 'overall_score']:
            self.assertGreaterEqual(impact[key], 0.0)
            self.assertLessEqual(impact[key], 1.0)
    
    def test_error_statistics_update(self):
        """测试错误统计更新"""
        # 初始统计
        initial_stats = self.system.error_statistics.get('psych_001', {}).copy()
        initial_occurrence_count = initial_stats.get('occurrence_count', 0)
        
        # 记录错误
        context = {'test': True}
        result = self.system.record_error_occurrence('psych_001', context, notes="统计测试")
        
        self.assertTrue(result['success'])
        
        # 验证统计已更新
        updated_stats = self.system.error_statistics.get('psych_001', {})
        self.assertEqual(updated_stats.get('occurrence_count', 0), initial_occurrence_count + 1)
        
        # 验证平均严重程度
        self.assertIn('average_severity', updated_stats)
        self.assertGreater(updated_stats['average_severity'], 0)
        
        # 验证最后发生时间
        self.assertIsNotNone(updated_stats.get('last_occurrence'))
        
        # 验证系统统计
        self.assertGreater(self.system.system_statistics['total_occurrences'], 0)
    
    def test_extract_learning_points(self):
        """测试提取学习点"""
        # 创建发生记录
        occurrence = ErrorOccurrence(
            occurrence_id="test_occ",
            error_id="psych_001",
            timestamp=datetime.now(),
            context={'market_condition': 'volatile', 'emotional_state': 'excited'},
            detected_by=['test_rule'],
            severity_at_occurrence=ErrorSeverity.HIGH,
            impact_assessment={},
            correction_applied=[],
            learning_extracted=[],
            notes="测试提取学习点"
        )
        
        learning_points = self.system._extract_learning_points(occurrence)
        
        self.assertIsInstance(learning_points, list)
        self.assertGreater(len(learning_points), 0)
        
        # 验证学习点内容
        for point in learning_points:
            self.assertIsInstance(point, str)
            self.assertGreater(len(point), 0)
        
        # 应该包含特定上下文的学习点
        context_points = [p for p in learning_points if 'volatile' in p or 'excited' in p]
        self.assertGreater(len(context_points), 0)


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)