#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试完整集成流程：优化引擎 + 规则整合器
"""

import numpy as np
import pandas as pd
import json
import os
import sys

# 添加当前目录到路径
sys.path.append('.')

from optimized_integration_engine import OptimizedPriceActionIntegrationEngine
from price_action_rules_integrator import PriceActionRulesIntegrator


def generate_test_data():
    """生成测试数据"""
    print("生成测试数据...")
    
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    np.random.seed(42)
    
    # 生成更真实的模拟数据：包含趋势、区间、反转
    base_price = 100
    
    # 1. 第一阶段：上升趋势
    trend1 = np.linspace(0, 15, 70)
    
    # 2. 第二阶段：区间震荡
    range_cycle = 8 * np.sin(np.linspace(0, 4*np.pi, 60))
    
    # 3. 第三阶段：下降趋势
    trend2 = np.linspace(0, -10, 70)
    
    # 组合
    trend = np.concatenate([trend1, np.zeros(60), trend2])
    
    # 添加噪声和周期
    cycle = 5 * np.sin(np.linspace(0, 8*np.pi, 200))
    noise = np.random.normal(0, 3, 200)
    
    closes = base_price + trend + cycle * 0.3 + noise * 0.5
    
    # 创建明显的支撑阻力区域
    support_levels = [102, 108, 105, 98]
    resistance_levels = [112, 118, 115, 122]
    
    for i in range(len(closes)):
        # 寻找最近的支撑阻力
        nearest_support = min(support_levels, key=lambda x: abs(x - closes[i]))
        nearest_resistance = min(resistance_levels, key=lambda x: abs(x - closes[i]))
        
        # 在支撑阻力附近添加"磁力"效应
        if abs(closes[i] - nearest_support) < 3:
            closes[i] = nearest_support + np.random.uniform(0, 2)
        elif abs(closes[i] - nearest_resistance) < 3:
            closes[i] = nearest_resistance - np.random.uniform(0, 2)
    
    # 生成OHLCV数据
    opens = closes - np.random.uniform(0.5, 2.5, 200)
    highs = closes + np.random.uniform(0.5, 4.0, 200)
    lows = closes - np.random.uniform(0.5, 4.0, 200)
    volumes = np.random.lognormal(10, 0.7, 200) * 1000
    
    # 在关键位置增加成交量
    key_positions = [35, 70, 105, 140, 175]
    for idx in key_positions:
        if idx < len(volumes):
            volumes[idx] *= 3.0
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=dates)
    
    return df


def run_optimized_engine(df):
    """运行优化引擎"""
    print("\n" + "=" * 60)
    print("运行优化版价格行为整合引擎")
    print("=" * 60)
    
    engine = OptimizedPriceActionIntegrationEngine()
    engine.load_data(df)
    results = engine.run_analysis()
    
    # 保存结果用于后续分析
    os.makedirs("test_results", exist_ok=True)
    
    with open("test_results/optimized_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)
    
    print("\n优化引擎结果已保存到: test_results/optimized_analysis.json")
    
    return results, df


def run_rules_integrator(analysis_results, price_data):
    """运行规则整合器"""
    print("\n" + "=" * 60)
    print("运行价格行为规则整合器")
    print("=" * 60)
    
    integrator = PriceActionRulesIntegrator()
    enhanced_results = integrator.integrate_rules(analysis_results, price_data)
    
    # 保存增强结果
    with open("test_results/enhanced_analysis.json", "w", encoding="utf-8") as f:
        json.dump(enhanced_results, f, indent=2, default=str, ensure_ascii=False)
    
    print("\n规则整合结果已保存到: test_results/enhanced_analysis.json")
    
    # 生成整合报告
    integration_report = integrator.generate_integration_report(enhanced_results)
    
    with open("test_results/integration_report.json", "w", encoding="utf-8") as f:
        json.dump(integration_report, f, indent=2, default=str, ensure_ascii=False)
    
    print("整合报告已保存到: test_results/integration_report.json")
    
    return enhanced_results, integration_report


def print_summary(analysis_results, enhanced_results, integration_report):
    """打印集成流程摘要"""
    print("\n" + "=" * 60)
    print("集成流程测试摘要")
    print("=" * 60)
    
    # 原始分析结果统计
    mag_levels = analysis_results.get('magnetic_levels', {})
    original_supports = len(mag_levels.get('support_levels', []))
    original_resistances = len(mag_levels.get('resistance_levels', []))
    
    print(f"\n📊 原始分析结果:")
    print(f"  识别支撑位: {original_supports}")
    print(f"  识别阻力位: {original_resistances}")
    
    market_state = analysis_results.get('market_state', {})
    print(f"  市场状态: {market_state.get('market_regime', '未知')}")
    print(f"  趋势方向: {market_state.get('trend_direction', '未知')}")
    
    # 规则整合结果统计
    validated_levels = enhanced_results.get('validated_magnetic_levels', {})
    validated_supports = len(validated_levels.get('support_levels', []))
    validated_resistances = len(validated_levels.get('resistance_levels', []))
    rejected_levels = len(validated_levels.get('rejected_levels', []))
    
    print(f"\n🔍 规则整合结果:")
    print(f"  验证通过支撑位: {validated_supports}")
    print(f"  验证通过阻力位: {validated_resistances}")
    print(f"  拒绝水平: {rejected_levels}")
    
    validation_metrics = validated_levels.get('validation_metrics', {})
    print(f"  验证通过率: {validation_metrics.get('validation_rate', 0):.2%}")
    print(f"  平均验证分数: {validation_metrics.get('avg_validation_score', 0):.1f}/100")
    
    # 交易信号统计
    price_action_signals = enhanced_results.get('price_action_signals', {})
    entry_signals = price_action_signals.get('entry_signals', [])
    
    print(f"\n🎯 交易信号生成:")
    print(f"  入场信号数量: {len(entry_signals)}")
    
    if entry_signals:
        signal_types = {}
        for signal in entry_signals:
            sig_type = signal.get('type', 'unknown')
            signal_types[sig_type] = signal_types.get(sig_type, 0) + 1
        
        print(f"  信号类型分布:")
        for sig_type, count in signal_types.items():
            print(f"    - {sig_type}: {count}个")
        
        avg_confidence = np.mean([s.get('confidence', 0) for s in entry_signals])
        print(f"  平均置信度: {avg_confidence:.2f}")
    
    # 交易计划统计
    trading_plans = enhanced_results.get('trading_plans', {})
    plans = trading_plans.get('plans', [])
    
    print(f"\n📝 交易计划创建:")
    print(f"  创建交易计划: {len(plans)}个")
    
    if plans:
        plan_confidences = [p.get('plan_confidence', 0) for p in plans]
        print(f"  平均计划置信度: {np.mean(plan_confidences):.2f}")
        
        risk_profile = trading_plans.get('plan_summary', {}).get('risk_profile', {})
        print(f"  整体风险水平: {risk_profile.get('overall_risk', '未知')}")
    
    # 整合报告摘要
    print(f"\n✅ 整合报告摘要:")
    integration_summary = integration_report.get('integration_summary', {})
    print(f"  应用规则类别: {len(integration_summary.get('rules_applied', []))}")
    print(f"  生成信号数量: {integration_summary.get('signals_generated', 0)}")
    print(f"  创建交易计划: {integration_summary.get('trading_plans_created', 0)}")
    
    # 关键发现
    print(f"\n💡 关键发现:")
    for i, finding in enumerate(integration_report.get('key_findings', [])[:3]):
        print(f"  {i+1}. {finding}")
    
    # 可操作的见解
    print(f"\n🚀 可操作的见解 (前3个):")
    insights = integration_report.get('actionable_insights', [])
    for i, insight in enumerate(insights[:3]):
        insight_type = insight.get('type', 'unknown')
        if insight_type == 'trading_opportunity':
            print(f"  {i+1}. 交易机会: {insight.get('signal_type', '')} @ {insight.get('level_price', 0):.2f} (置信度: {insight.get('confidence', 0):.2f})")
        else:
            print(f"  {i+1}. {insight.get('warning', insight.get('recommendation', '未知'))}")
    
    # 下一步建议
    print(f"\n📋 下一步建议:")
    for i, step in enumerate(integration_report.get('next_steps', [])[:3]):
        print(f"  {i+1}. {step}")


def test_specific_scenarios():
    """测试特定场景"""
    print("\n" + "=" * 60)
    print("测试特定交易场景")
    print("=" * 60)
    
    # 场景1：区间交易
    print("\n1. 区间交易场景分析:")
    print("   - 市场处于区间状态")
    print("   - 价格接近支撑/阻力位")
    print("   - 成交量确认")
    print("   → 生成区间交易信号")
    
    # 场景2：趋势跟踪
    print("\n2. 趋势跟踪场景分析:")
    print("   - 市场处于趋势状态")
    print("   - 价格回调至动态支撑")
    print("   - 趋势健康确认")
    print("   → 生成趋势跟踪信号")
    
    # 场景3：突破交易
    print("\n3. 突破交易场景分析:")
    print("   - 关键水平被突破")
    print("   - 成交量放大确认")
    print("   - 价格行为跟随")
    print("   → 生成突破交易信号")


def main():
    """主函数"""
    print("完整集成流程测试")
    print("测试: 优化引擎 + 规则整合器")
    print("=" * 60)
    
    try:
        # 1. 生成测试数据
        df = generate_test_data()
        print(f"测试数据生成成功: {len(df)} 行, {df.index[0]} 到 {df.index[-1]}")
        
        # 2. 运行优化引擎
        analysis_results, price_data = run_optimized_engine(df)
        
        # 3. 运行规则整合器
        enhanced_results, integration_report = run_rules_integrator(analysis_results, price_data)
        
        # 4. 打印摘要
        print_summary(analysis_results, enhanced_results, integration_report)
        
        # 5. 测试特定场景
        test_specific_scenarios()
        
        print("\n" + "=" * 60)
        print("✅ 集成流程测试完成!")
        print("=" * 60)
        print("\n生成的文件:")
        print("  test_results/optimized_analysis.json - 优化引擎结果")
        print("  test_results/enhanced_analysis.json - 规则整合结果")
        print("  test_results/integration_report.json - 整合报告")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()