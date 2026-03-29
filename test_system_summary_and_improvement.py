#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
系统总结与未来改进系统测试
第32章：系统总结与未来改进
AL Brooks《价格行为交易之区间篇》

测试标准：按照第18章标准（完整实际代码测试）
1. 学习成果总结测试
2. 技能评估系统测试
3. 改进计划创建测试
4. 未来学习路径测试
5. 系统集成计划测试
6. 系统演示功能测试
"""

import unittest
import tempfile
import os
import json
from datetime import datetime
from system_summary_and_improvement import (
    SystemSummaryAndImprovement,
    LearningOutcome,
    SkillAssessment,
    ImprovementPlan,
    FutureLearningPath,
    SystemIntegrationPlan,
    SkillLevel,
    AssessmentArea,
    ImprovementPriority
)


class TestLearningOutcome(unittest.TestCase):
    """测试学习成果数据结构"""
    
    def test_learning_outcome_creation(self):
        """测试学习成果创建"""
        outcome = LearningOutcome(
            outcome_id="test_outcome_001",
            chapter_number=16,
            chapter_title="测试章节",
            key_concepts=["概念1", "概念2"],
            skills_acquired=["技能1", "技能2"],
            systems_created=["system1.py", "system2.py"],
            confidence_level=0.85,
            mastery_indicator=0.80,
            verification_methods=["测试1", "测试2"],
            application_examples=["应用1", "应用2"]
        )
        
        self.assertEqual(outcome.outcome_id, "test_outcome_001")
        self.assertEqual(outcome.chapter_number, 16)
        self.assertEqual(outcome.chapter_title, "测试章节")
        self.assertEqual(len(outcome.key_concepts), 2)
        self.assertEqual(len(outcome.skills_acquired), 2)
        self.assertEqual(len(outcome.systems_created), 2)
        self.assertEqual(outcome.confidence_level, 0.85)
        self.assertEqual(outcome.mastery_indicator, 0.80)
        self.assertEqual(len(outcome.verification_methods), 2)
        self.assertEqual(len(outcome.application_examples), 2)
    
    def test_learning_outcome_serialization(self):
        """测试学习成果序列化"""
        outcome = LearningOutcome(
            outcome_id="test_outcome_002",
            chapter_number=17,
            chapter_title="序列化测试",
            key_concepts=["概念"],
            skills_acquired=["技能"],
            systems_created=["system.py"],
            confidence_level=0.75,
            mastery_indicator=0.70,
            verification_methods=["测试"],
            application_examples=["应用"]
        )
        
        # 转换为字典
        outcome_dict = outcome.to_dict()
        
        # 验证字典内容
        self.assertEqual(outcome_dict['outcome_id'], "test_outcome_002")
        self.assertEqual(outcome_dict['chapter_number'], 17)
        self.assertEqual(outcome_dict['confidence_level'], 0.75)
        self.assertIn('created_at', outcome_dict)
        
        # 从字典创建
        outcome_from_dict = LearningOutcome.from_dict(outcome_dict)
        
        self.assertEqual(outcome_from_dict.outcome_id, outcome.outcome_id)
        self.assertEqual(outcome_from_dict.chapter_number, outcome.chapter_number)
        self.assertEqual(outcome_from_dict.confidence_level, outcome.confidence_level)


class TestSkillAssessment(unittest.TestCase):
    """测试技能评估数据结构"""
    
    def test_skill_assessment_creation(self):
        """测试技能评估创建"""
        assessment = SkillAssessment(
            area=AssessmentArea.PRICE_ACTION_ANALYSIS,
            current_level=SkillLevel.INTERMEDIATE,
            target_level=SkillLevel.ADVANCED,
            confidence_score=0.85,
            assessment_date=datetime.now(),
            evidence=["证据1", "证据2"],
            strengths=["优势1", "优势2"],
            weaknesses=["弱点1", "弱点2"],
            recommendations=["建议1", "建议2"],
            priority=ImprovementPriority.HIGH
        )
        
        self.assertEqual(assessment.area, AssessmentArea.PRICE_ACTION_ANALYSIS)
        self.assertEqual(assessment.current_level, SkillLevel.INTERMEDIATE)
        self.assertEqual(assessment.target_level, SkillLevel.ADVANCED)
        self.assertEqual(assessment.confidence_score, 0.85)
        self.assertEqual(assessment.priority, ImprovementPriority.HIGH)
        self.assertEqual(len(assessment.evidence), 2)
        self.assertEqual(len(assessment.strengths), 2)
        self.assertEqual(len(assessment.weaknesses), 2)
        self.assertEqual(len(assessment.recommendations), 2)
    
    def test_skill_assessment_serialization(self):
        """测试技能评估序列化"""
        assessment_date = datetime.now()
        
        assessment = SkillAssessment(
            area=AssessmentArea.RISK_MANAGEMENT,
            current_level=SkillLevel.BEGINNER,
            target_level=SkillLevel.INTERMEDIATE,
            confidence_score=0.70,
            assessment_date=assessment_date,
            evidence=["完成风险系统"],
            strengths=["风险计算"],
            weaknesses=["极端风险"],
            recommendations=["学习极端风险"],
            priority=ImprovementPriority.CRITICAL
        )
        
        # 转换为字典
        assessment_dict = assessment.to_dict()
        
        # 验证字典内容
        self.assertEqual(assessment_dict['area'], "risk_management")
        self.assertEqual(assessment_dict['current_level'], "beginner")
        self.assertEqual(assessment_dict['target_level'], "intermediate")
        self.assertEqual(assessment_dict['priority'], "critical")
        self.assertIn('assessment_date', assessment_dict)
        
        # 从字典创建
        assessment_from_dict = SkillAssessment.from_dict(assessment_dict)
        
        self.assertEqual(assessment_from_dict.area, assessment.area)
        self.assertEqual(assessment_from_dict.current_level, assessment.current_level)
        self.assertEqual(assessment_from_dict.target_level, assessment.target_level)
        self.assertEqual(assessment_from_dict.priority, assessment.priority)


class TestSystemSummaryAndImprovement(unittest.TestCase):
    """测试系统总结与改进系统"""
    
    def setUp(self):
        """测试前准备"""
        # 创建临时文件用于存储测试数据
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json')
        self.temp_file.close()
        
        # 创建系统实例
        self.system = SystemSummaryAndImprovement(
            storage_path=self.temp_file.name,
            enable_auto_assessment=True
        )
    
    def tearDown(self):
        """测试后清理"""
        # 删除临时文件
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_system_initialization(self):
        """测试系统初始化"""
        self.assertIsNotNone(self.system.quantum_systems)
        self.assertIsNotNone(self.system.learning_outcomes)
        self.assertIsNotNone(self.system.skill_assessments)
        
        # 验证量子系统信息已加载
        self.assertGreater(len(self.system.quantum_systems), 0)
        self.assertIn('第16章', self.system.quantum_systems)
        self.assertIn('第31章', self.system.quantum_systems)
        
        # 验证学习成果已初始化
        self.assertGreater(len(self.system.learning_outcomes), 0)
        
        # 验证技能评估已初始化
        self.assertGreater(len(self.system.skill_assessments), 0)
        
        # 验证系统统计
        self.assertGreater(self.system.system_statistics['total_chapters_learned'], 0)
        self.assertGreater(self.system.system_statistics['total_systems_created'], 0)
        self.assertGreater(self.system.system_statistics['total_code_size_kb'], 0)
    
    def test_generate_learning_summary(self):
        """测试生成学习总结"""
        summary = self.system.generate_learning_summary()
        
        # 验证总结结构
        self.assertIn('report_id', summary)
        self.assertIn('generated_at', summary)
        self.assertIn('learning_overview', summary)
        self.assertIn('quantum_systems_overview', summary)
        self.assertIn('skill_assessment_summary', summary)
        self.assertIn('key_achievements', summary)
        self.assertIn('knowledge_gaps', summary)
        self.assertIn('recommendations', summary)
        self.assertIn('overall_mastery_level', summary)
        
        # 验证学习概览
        overview = summary['learning_overview']
        self.assertIn('total_chapters', overview)
        self.assertIn('total_systems', overview)
        self.assertIn('total_code_kb', overview)
        self.assertIn('total_tests', overview)
        self.assertIn('learning_duration_days', overview)
        self.assertIn('average_chapters_per_day', overview)
        self.assertIn('completion_percentage', overview)
        
        # 验证量子系统概述
        systems_overview = summary['quantum_systems_overview']
        self.assertIn('total_systems_by_category', systems_overview)
        self.assertIn('systems_by_category', systems_overview)
        self.assertIn('largest_system', systems_overview)
        self.assertIn('most_tested_system', systems_overview)
        
        # 验证关键成就
        self.assertGreater(len(summary['key_achievements']), 0)
        
        # 验证知识差距
        self.assertGreater(len(summary['knowledge_gaps']), 0)
        
        # 验证推荐
        self.assertGreater(len(summary['recommendations']), 0)
        
        # 验证总体掌握水平
        self.assertIsInstance(summary['overall_mastery_level'], float)
        self.assertGreaterEqual(summary['overall_mastery_level'], 0.0)
        self.assertLessEqual(summary['overall_mastery_level'], 1.0)
    
    def test_create_improvement_plan(self):
        """测试创建改进计划"""
        trader_profile = {
            'trader_id': 'test_trader_001',
            'experience_years': 2,
            'current_focus': '技能提升'
        }
        
        result = self.system.create_improvement_plan(trader_profile)
        
        self.assertTrue(result['success'])
        self.assertIn('plan_id', result)
        self.assertIn('focus_areas', result)
        self.assertIn('current_levels', result)
        self.assertIn('target_levels', result)
        self.assertIn('improvement_actions_count', result)
        self.assertIn('estimated_duration_days', result)
        
        plan_id = result['plan_id']
        
        # 验证计划已保存
        self.assertIn(plan_id, self.system.improvement_plans)
        
        plan = self.system.improvement_plans[plan_id]
        self.assertEqual(plan.trader_id, 'test_trader_001')
        self.assertGreater(len(plan.focus_areas), 0)
        self.assertGreater(len(plan.target_skill_levels), 0)
        self.assertGreater(len(plan.improvement_actions), 0)
        self.assertGreater(len(plan.success_criteria), 0)
        self.assertGreater(len(plan.monitoring_metrics), 0)
        self.assertTrue(plan.active)
    
    def test_create_improvement_plan_specific_areas(self):
        """测试创建特定领域的改进计划"""
        trader_profile = {
            'trader_id': 'test_trader_002',
            'experience_years': 1
        }
        
        # 指定关注领域
        focus_areas = [
            AssessmentArea.PRICE_ACTION_ANALYSIS,
            AssessmentArea.RISK_MANAGEMENT
        ]
        
        result = self.system.create_improvement_plan(
            trader_profile=trader_profile,
            focus_areas=focus_areas
        )
        
        self.assertTrue(result['success'])
        
        # 验证计划包含指定领域
        plan_id = result['plan_id']
        plan = self.system.improvement_plans[plan_id]
        
        for area in focus_areas:
            self.assertIn(area, plan.focus_areas)
    
    def test_create_improvement_plan_no_assessments(self):
        """测试没有技能评估时创建改进计划"""
        # 创建一个没有技能评估的系统
        clean_system = SystemSummaryAndImprovement(storage_path=None)
        # 清空技能评估
        clean_system.skill_assessments = {}
        
        trader_profile = {'trader_id': 'test'}
        result = clean_system.create_improvement_plan(trader_profile)
        
        # 应该失败或使用默认领域
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertIn('available_areas', result)
    
    def test_create_future_learning_path(self):
        """测试创建未来学习路径"""
        trader_profile = {
            'trader_id': 'test_trader_003',
            'experience_years': 3,
            'learning_goal': '成为专家'
        }
        
        result = self.system.create_future_learning_path(
            trader_profile,
            target_level=SkillLevel.EXPERT
        )
        
        self.assertTrue(result['success'])
        self.assertIn('path_id', result)
        self.assertIn('current_level', result)
        self.assertIn('target_level', result)
        self.assertIn('learning_stages_count', result)
        self.assertIn('estimated_duration_days', result)
        self.assertIn('milestones_count', result)
        
        path_id = result['path_id']
        
        # 验证路径已保存
        self.assertIn(path_id, self.system.learning_paths)
        
        path = self.system.learning_paths[path_id]
        self.assertEqual(path.trader_id, 'test_trader_003')
        self.assertEqual(path.target_level, SkillLevel.EXPERT)
        self.assertGreater(len(path.learning_stages), 0)
        self.assertGreater(len(path.recommended_resources), 0)
        self.assertGreater(path.estimated_duration_days, 0)
        self.assertGreater(len(path.milestones), 0)
        self.assertGreater(len(path.prerequisites), 0)
    
    def test_create_system_integration_plan(self):
        """测试创建系统集成计划"""
        result = self.system.create_system_integration_plan()
        
        self.assertTrue(result['success'])
        self.assertIn('integration_id', result)
        self.assertIn('systems_count', result)
        self.assertIn('implementation_steps', result)
        self.assertIn('total_duration_days', result)
        
        integration_id = result['integration_id']
        
        # 验证集成计划已保存
        self.assertIn(integration_id, self.system.integration_plans)
        
        integration = self.system.integration_plans[integration_id]
        self.assertGreater(len(integration.systems_to_integrate), 0)
        self.assertIn('approach', integration.integration_architecture)
        self.assertGreater(len(integration.implementation_steps), 0)
        self.assertGreater(len(integration.expected_benefits), 0)
        self.assertGreater(len(integration.risks_and_challenges), 0)
        self.assertIn('total_duration_days', integration.timeline)
    
    def test_system_categorization(self):
        """测试系统分类功能"""
        test_systems = [
            ('趋势通道分析系统', '分析识别类'),
            ('高级风险管理', '风险管理类'),
            ('心理纪律管理', '心理纪律类'),
            ('交易计划制定', '计划评估类'),
            ('交易系统整合', '系统集成类'),
            ('未知系统', '其他类')
        ]
        
        for system_name, expected_category in test_systems:
            category = self.system._categorize_system(system_name)
            self.assertEqual(category, expected_category)
    
    def test_identify_focus_areas(self):
        """测试识别重点关注领域"""
        focus_areas = self.system._identify_focus_areas()
        
        self.assertIsInstance(focus_areas, list)
        
        # 验证返回的是AssessmentArea枚举
        if focus_areas:
            for area in focus_areas:
                self.assertIsInstance(area, AssessmentArea)
    
    def test_create_improvement_actions(self):
        """测试创建改进行动"""
        # 获取一个技能评估
        if self.system.skill_assessments:
            area = list(self.system.skill_assessments.keys())[0]
            assessment = self.system.skill_assessments[area]
            
            # 测试创建行动
            actions = self.system._create_improvement_actions(
                area, assessment, SkillLevel.ADVANCED
            )
            
            self.assertIsInstance(actions, list)
            if actions:
                action = actions[0]
                self.assertIn('action_id', action)
                self.assertIn('area', action)
                self.assertIn('action', action)
                self.assertIn('description', action)
                self.assertIn('duration_days', action)
                self.assertIn('resources', action)
                self.assertIn('success_criteria', action)
    
    def test_create_learning_stages(self):
        """测试创建学习阶段"""
        stages = self.system._create_learning_stages(
            SkillLevel.INTERMEDIATE,
            SkillLevel.EXPERT
        )
        
        self.assertIsInstance(stages, list)
        if stages:
            stage = stages[0]
            self.assertIn('name', stage)
            self.assertIn('description', stage)
            self.assertIn('duration_days', stage)
            self.assertIn('target_level', stage)
            self.assertIn('learning_topics', stage)
    
    def test_recommend_resources(self):
        """测试推荐学习资源"""
        resources = self.system._recommend_resources(SkillLevel.EXPERT)
        
        self.assertIsInstance(resources, list)
        if resources:
            resource = resources[0]
            self.assertIn('type', resource)
            self.assertIn('title', resource)
            self.assertIn('description', resource)
            self.assertIn('level', resource)
    
    def test_create_milestones(self):
        """测试创建里程碑"""
        test_stages = [
            {
                'name': '阶段1',
                'description': '测试阶段1',
                'duration_days': 30,
                'target_level': SkillLevel.INTERMEDIATE,
                'learning_topics': ['主题1', '主题2']
            },
            {
                'name': '阶段2',
                'description': '测试阶段2',
                'duration_days': 45,
                'target_level': SkillLevel.ADVANCED,
                'learning_topics': ['主题3', '主题4']
            }
        ]
        
        milestones = self.system._create_milestones(test_stages)
        
        self.assertIsInstance(milestones, list)
        self.assertEqual(len(milestones), len(test_stages))
        
        if milestones:
            milestone = milestones[0]
            self.assertIn('milestone_id', milestone)
            self.assertIn('name', milestone)
            self.assertIn('description', milestone)
            self.assertIn('target_completion_days', milestone)
            self.assertIn('success_criteria', milestone)
    
    def test_system_persistence(self):
        """测试系统数据持久化"""
        # 在原始系统中创建一些数据
        trader_profile = {'trader_id': 'persistence_test'}
        
        # 创建改进计划
        plan_result = self.system.create_improvement_plan(trader_profile)
        self.assertTrue(plan_result['success'])
        
        # 创建学习路径
        path_result = self.system.create_future_learning_path(trader_profile)
        self.assertTrue(path_result['success'])
        
        # 创建集成计划
        int_result = self.system.create_system_integration_plan()
        self.assertTrue(int_result['success'])
        
        # 保存数据
        if self.system.storage_path:
            self.system._save_data_to_storage()
            
            # 验证文件存在
            self.assertTrue(os.path.exists(self.system.storage_path))
            
            # 创建新系统实例并加载数据
            new_system = SystemSummaryAndImprovement(
                storage_path=self.system.storage_path
            )
            
            # 验证数据已加载
            self.assertGreater(len(new_system.improvement_plans), 0)
            self.assertGreater(len(new_system.learning_paths), 0)
            self.assertGreater(len(new_system.integration_plans), 0)
            
            # 验证计划内容
            for plan_id, plan in new_system.improvement_plans.items():
                self.assertEqual(plan.trader_id, 'persistence_test')
            
            for path_id, path in new_system.learning_paths.items():
                self.assertEqual(path.trader_id, 'persistence_test')
    
    def test_demo_system(self):
        """测试系统演示功能"""
        # 运行演示函数
        results = self.system.demo_system()
        
        # 验证演示结果结构
        self.assertIn('learning_summary', results)
        self.assertIn('improvement_plan', results)
        self.assertIn('future_learning_path', results)
        self.assertIn('system_integration_plan', results)
        
        # 验证学习总结
        if results['learning_summary']:
            summary = results['learning_summary']
            self.assertIn('report_id', summary)
            self.assertIn('total_systems', summary)
            self.assertIn('total_code_kb', summary)
            self.assertIn('overall_mastery', summary)
        
        # 验证改进计划结果
        if results.get('improvement_plan'):
            plan_result = results['improvement_plan']
            self.assertTrue(plan_result['success'])
        
        # 验证学习路径结果
        if results.get('future_learning_path'):
            path_result = results['future_learning_path']
            self.assertTrue(path_result['success'])
        
        # 验证集成计划结果
        if results.get('system_integration_plan'):
            int_result = results['system_integration_plan']
            self.assertTrue(int_result['success'])


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)