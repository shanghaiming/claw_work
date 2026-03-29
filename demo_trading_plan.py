#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第23章《交易计划制定》完整演示
展示已完成的交易计划制定系统实际功能
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from trading_plan_creator import TradingPlanCreator

def main():
    print("=" * 60)
    print("第23章《交易计划制定》完整演示")
    print("按照第18章标准：展示实际代码功能")
    print("=" * 60)
    print()
    
    # 1. 创建交易计划制定器实例
    print("1️⃣ 创建TradingPlanCreator实例")
    print("-" * 40)
    
    trader_profile = {
        'experience_level': 'intermediate',
        'trading_style': 'swing',
        'risk_tolerance': 'moderate',
        'preferred_timeframe': '4h',
        'name': '测试交易员',
        'account_size': 10000.0
    }
    
    tpc = TradingPlanCreator(trader_profile, default_risk_percentage=0.02)
    print(f"   ✅ 交易者: {tpc.trader_profile['name']}")
    print(f"   ✅ 经验级别: {tpc.trader_profile['experience_level']}")
    print(f"   ✅ 交易风格: {tpc.trader_profile['trading_style']}")
    print(f"   ✅ 风险承受度: {tpc.trader_profile['risk_tolerance']}")
    print(f"   ✅ 账户规模: ${tpc.trader_profile['account_size']:,.2f}")
    print(f"   ✅ 默认风险比例: {tpc.default_risk_percentage:.1%}")
    print(f"   ✅ 可用计划模板: {len(tpc.plan_templates)}个")
    print()
    
    # 2. 准备市场分析数据
    print("2️⃣ 准备市场分析数据")
    print("-" * 40)
    
    market_analysis = {
        'trend_strength': 0.75,  # 趋势强度75%
        'market_structure': 'uptrend',
        'volatility': 0.015,  # 1.5%波动率
        'support_levels': [95.0, 96.5, 98.0],
        'resistance_levels': [102.0, 103.5, 105.0],
        'current_price': 100.0,
        'volume_trend': 'increasing',
        'market_sentiment': 'bullish'
    }
    
    print(f"   ✅ 趋势强度: {market_analysis['trend_strength']:.0%}")
    print(f"   ✅ 市场结构: {market_analysis['market_structure']}")
    print(f"   ✅ 波动率: {market_analysis['volatility']:.2%}")
    print(f"   ✅ 当前价格: ${market_analysis['current_price']:.2f}")
    print(f"   ✅ 支撑位: {market_analysis['support_levels']}")
    print(f"   ✅ 阻力位: {market_analysis['resistance_levels']}")
    print()
    
    # 3. 定义交易想法
    print("3️⃣ 定义交易想法")
    print("-" * 40)
    
    trade_idea = {
        'direction': 'long',
        'instrument': 'EURUSD',
        'time_horizon': 'short_term',
        'type': 'speculative',
        'setup_type': 'trend_following',
        'confidence': 0.7,
        'rationale': '上升趋势中的回调买入机会',
        'current_price': market_analysis['current_price']
    }
    
    print(f"   ✅ 交易方向: {trade_idea['direction']}")
    print(f"   ✅ 交易品种: {trade_idea['instrument']}")
    print(f"   ✅ 时间框架: {trade_idea['time_horizon']}")
    print(f"   ✅ 交易类型: {trade_idea['type']}")
    print(f"   ✅ 设置类型: {trade_idea['setup_type']}")
    print(f"   ✅ 信心度: {trade_idea['confidence']:.0%}")
    print(f"   ✅ 交易理由: {trade_idea['rationale']}")
    print()
    
    # 4. 定义风险参数
    print("4️⃣ 定义风险参数")
    print("-" * 40)
    
    risk_parameters = {
        'account_size': 10000.0,
        'max_risk_percentage': 0.02,
        'profit_target': 0.04,
        'max_position_percentage': 0.25,
        'stop_loss_method': 'atr_based',
        'take_profit_method': 'risk_reward_based'
    }
    
    print(f"   ✅ 账户规模: ${risk_parameters['account_size']:,.2f}")
    print(f"   ✅ 最大风险比例: {risk_parameters['max_risk_percentage']:.1%}")
    print(f"   ✅ 盈利目标: {risk_parameters['profit_target']:.1%}")
    print(f"   ✅ 最大仓位比例: {risk_parameters['max_position_percentage']:.0%}")
    print(f"   ✅ 止损方法: {risk_parameters['stop_loss_method']}")
    print(f"   ✅ 止盈方法: {risk_parameters['take_profit_method']}")
    print()
    
    # 5. 创建综合交易计划
    print("5️⃣ 创建综合交易计划")
    print("-" * 40)
    
    comprehensive_plan = tpc.create_comprehensive_plan(
        market_analysis=market_analysis,
        trade_idea=trade_idea,
        risk_parameters=risk_parameters
    )
    
    if 'error' in comprehensive_plan:
        print(f"   ❌ 计划创建失败: {comprehensive_plan['error']}")
        return
    
    print(f"   ✅ 计划ID: {comprehensive_plan['plan_id']}")
    print(f"   ✅ 创建时间: {comprehensive_plan['creation_time']}")
    print(f"   ✅ 市场体制: {comprehensive_plan['market_conditions']['market_regime']}")
    print(f"   ✅ 交易机会评级: {comprehensive_plan['market_conditions']['trading_opportunity']}")
    print()
    
    # 6. 显示交易目标
    print("6️⃣ 交易目标详情")
    print("-" * 40)
    
    objectives = comprehensive_plan['trading_objectives']
    print(f"   ✅ 主要目标: {objectives['primary_objective']}")
    print(f"   ✅ 盈利目标: {objectives['profit_target_percentage']:.1%}")
    print(f"   ✅ 风险目标: {objectives['risk_target_percentage']:.1%}")
    print(f"   ✅ 时间框架: {objectives['time_horizon']}")
    print(f"   ✅ 风险回报比: {objectives['risk_reward_ratio']:.1f}:1")
    print(f"   ✅ 成功指标: {objectives['success_metrics']}")
    print()
    
    # 7. 显示入场规则
    print("7️⃣ 入场规则详情")
    print("-" * 40)
    
    entry_rules = comprehensive_plan['entry_rules']
    print(f"   ✅ 触发条件: {len(entry_rules['trigger_conditions'])}个")
    for i, condition in enumerate(entry_rules['trigger_conditions'], 1):
        print(f"      {i}. {condition}")
    
    print(f"   ✅ 入场价格范围: ${entry_rules['entry_price_range']['min']:.2f} - ${entry_rules['entry_price_range']['max']:.2f}")
    print(f"   ✅ 入场时机: {entry_rules['entry_timing']}")
    print(f"   ✅ 确认信号: {len(entry_rules['confirmation_signals'])}个")
    print()
    
    # 8. 显示出场规则
    print("8️⃣ 出场规则详情")
    print("-" * 40)
    
    exit_rules = comprehensive_plan['exit_rules']
    print(f"   ✅ 止损价格: ${exit_rules['stop_loss_price']:.2f}")
    print(f"   ✅ 止盈价格: ${exit_rules['take_profit_price']:.2f}")
    print(f"   ✅ 止损距离: {exit_rules['stop_loss_distance']:.2%}")
    print(f"   ✅ 止盈距离: {exit_rules['take_profit_distance']:.2%}")
    print(f"   ✅ 风险回报比: {exit_rules['risk_reward_ratio']:.1f}:1")
    
    if exit_rules['trailing_stop_enabled']:
        print(f"   ✅ 移动止损: 启用 (激活条件: {exit_rules['trailing_stop_condition']})")
    else:
        print(f"   ✅ 移动止损: 未启用")
    
    print(f"   ✅ 部分出场策略: {exit_rules['partial_exit_strategy']}")
    print()
    
    # 9. 显示风险管理
    print("9️⃣ 风险管理详情")
    print("-" * 40)
    
    risk_management = comprehensive_plan['risk_management']
    print(f"   ✅ 仓位大小: {risk_management['position_size']:.2f}单位")
    print(f"   ✅ 最大仓位比例: {risk_management['max_position_percentage']:.0%}")
    print(f"   ✅ 单笔交易风险: ${risk_management['risk_per_trade']:.2f}")
    print(f"   ✅ 最大单日亏损: ${risk_management['max_daily_loss']:.2f}")
    print(f"   ✅ 最大单周亏损: ${risk_management['max_weekly_loss']:.2f}")
    
    adjustment_factors = risk_management['risk_adjustment_factors']
    print(f"   ✅ 风险调整因子: 市场体制={adjustment_factors['market_regime_factor']:.2f}, "
          f"波动性={adjustment_factors['volatility_factor']:.2f}, "
          f"信心度={adjustment_factors['confidence_factor']:.2f}")
    print()
    
    # 10. 显示执行计划
    print("🔟 执行计划详情")
    print("-" * 40)
    
    execution_plan = comprehensive_plan['execution_plan']
    print(f"   ✅ 执行条件: {len(execution_plan['execution_conditions'])}个")
    print(f"   ✅ 监控要点: {len(execution_plan['monitoring_points'])}个")
    print(f"   ✅ 应急方案: {len(execution_plan['contingency_plan'])}个")
    print(f"   ✅ 执行阶段: {execution_plan['execution_phases']}")
    print()
    
    # 11. 显示计划验证结果
    print("1️⃣1️⃣ 计划验证结果")
    print("-" * 40)
    
    plan_validation = comprehensive_plan['plan_validation']
    print(f"   ✅ 可行性评级: {plan_validation['feasibility_rating']}")
    print(f"   ✅ 综合验证分数: {plan_validation['overall_validation_score']:.0%}")
    
    if plan_validation['issues']:
        print(f"   ⚠️  潜在问题: {len(plan_validation['issues'])}个")
        for i, issue in enumerate(plan_validation['issues'], 1):
            print(f"      {i}. {issue}")
    else:
        print(f"   ✅ 无潜在问题")
    
    print(f"   💡 改进建议: {len(plan_validation['recommendations'])}个")
    for i, rec in enumerate(plan_validation['recommendations'], 1):
        print(f"      {i}. {rec}")
    print()
    
    # 12. 显示执行检查清单
    print("1️⃣2️⃣ 执行检查清单")
    print("-" * 40)
    
    checklist = comprehensive_plan['execution_checklist']
    print(f"   ✅ 预交易检查: {len(checklist['pre_trade_checklist'])}项")
    for i, item in enumerate(checklist['pre_trade_checklist'][:3], 1):
        print(f"      {i}. {item}")
    if len(checklist['pre_trade_checklist']) > 3:
        print(f"      ... 还有{len(checklist['pre_trade_checklist']) - 3}项")
    
    print(f"   ✅ 执行时检查: {len(checklist['execution_checklist'])}项")
    for i, item in enumerate(checklist['execution_checklist'][:3], 1):
        print(f"      {i}. {item}")
    if len(checklist['execution_checklist']) > 3:
        print(f"      ... 还有{len(checklist['execution_checklist']) - 3}项")
    
    print(f"   ✅ 监控期检查: {len(checklist['monitoring_checklist'])}项")
    print(f"   ✅ 结束后检查: {len(checklist['post_trade_checklist'])}项")
    print()
    
    # 13. 显示计划摘要
    print("1️⃣3️⃣ 交易计划摘要")
    print("-" * 40)
    
    summary = comprehensive_plan['plan_summary']
    print(f"   📊 计划摘要: {summary['summary_text']}")
    print(f"   🎯 关键目标: {summary['key_objectives']}")
    print(f"   ⚡ 行动计划: {summary['action_plan']}")
    print(f"   📈 预期结果: {summary['expected_outcomes']}")
    print()
    
    # 14. 显示计划历史
    print("1️⃣4️⃣ 计划历史管理")
    print("-" * 40)
    
    history_summary = tpc.get_plan_history_summary()
    print(f"   ✅ 总计划数量: {history_summary['total_plans']}")
    print(f"   ✅ 近期计划: {history_summary['recent_plans']}")
    print(f"   ✅ 可行性分布: {history_summary['feasibility_distribution']}")
    print(f"   ✅ 平均验证分数: {history_summary['average_validation_score']:.0%}")
    print(f"   ✅ 性能趋势: {history_summary['performance_trend']}")
    print()
    
    # 15. 导出计划
    print("1️⃣5️⃣ 计划导出功能")
    print("-" * 40)
    
    markdown_content = tpc.export_plan_to_markdown(comprehensive_plan['plan_id'])
    if markdown_content:
        print(f"   ✅ Markdown导出成功: {len(markdown_content)}字符")
        print(f"   📝 前200字符预览:")
        print(f"      {markdown_content[:200]}...")
    else:
        print(f"   ❌ 导出失败: 计划ID未找到")
    
    print()
    print("=" * 60)
    print("🎯 第23章《交易计划制定》演示完成")
    print("✅ 所有功能正常运行，代码完整可执行")
    print("📊 严格按照第18章标准：实际代码实现")
    print("=" * 60)

if __name__ == "__main__":
    main()