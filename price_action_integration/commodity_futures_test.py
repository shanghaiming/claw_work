#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
商品期货价格行为整合框架测试
测试优化引擎 + 规则整合器在商品期货市场的应用
"""

import numpy as np
import pandas as pd
import json
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any
import warnings
warnings.filterwarnings('ignore')

# 添加当前目录到路径
sys.path.append('.')

from optimized_integration_engine import OptimizedPriceActionIntegrationEngine
from price_action_rules_integrator import PriceActionRulesIntegrator


def generate_copper_futures_data():
    """
    生成铜期货模拟数据
    铜期货特点：趋势性强，与宏观经济相关，波动适中
    """
    print("生成铜期货模拟数据...")
    
    # 模拟2024年数据
    dates = pd.date_range('2024-01-01', periods=150, freq='D')
    np.random.seed(42)
    
    # 基础价格：60000-70000元/吨区间
    base_price = 65000
    
    # 铜期货价格特征：
    # 1. 长期缓慢上升趋势
    # 2. 季节性不明显
    # 3. 与宏观经济数据相关
    # 4. 偶有大幅波动
    
    # 长期趋势成分
    long_term_trend = np.linspace(0, 5000, 150)  # 5000点上升趋势
    
    # 中期周期成分（3个月周期）
    mid_term_cycle = 2000 * np.sin(np.linspace(0, 4*np.pi, 150))
    
    # 短期波动
    short_term_noise = np.random.normal(0, 800, 150)
    
    # 关键事件冲击（模拟供需冲击）
    event_shocks = np.zeros(150)
    event_positions = [30, 75, 120]  # 假设在第30、75、120天有事件
    for pos in event_positions:
        if pos < len(event_shocks):
            # 事件冲击：±3-5%的价格变动
            event_shocks[pos] = np.random.uniform(0.03, 0.05) * base_price * np.random.choice([-1, 1])
            # 事件后衰减
            for i in range(1, 10):
                if pos + i < len(event_shocks):
                    event_shocks[pos + i] = event_shocks[pos] * np.exp(-0.3 * i)
    
    # 组合价格
    price = base_price + long_term_trend + mid_term_cycle * 0.5 + short_term_noise * 0.8 + event_shocks
    
    # 生成清晰的支撑阻力区域（基于整数关口和技术位）
    key_levels = [62000, 63500, 65000, 66500, 68000, 69500]
    
    for i in range(len(price)):
        # 寻找最近的整数关口
        nearest_level = min(key_levels, key=lambda x: abs(x - price[i]))
        
        # 在整数关口附近添加"磁力"效应
        if abs(price[i] - nearest_level) < 300:  # 300点内
            # 倾向于在整数关口附近震荡
            price[i] = nearest_level + np.random.uniform(-200, 200)
    
    # 生成OHLCV数据
    closes = price
    opens = closes - np.random.uniform(50, 300, 150)
    highs = closes + np.random.uniform(100, 500, 150)
    lows = closes - np.random.uniform(100, 500, 150)
    
    # 成交量：与波动率正相关
    daily_range = highs - lows
    avg_range = np.mean(daily_range)
    volumes = np.random.lognormal(12, 0.6, 150) * 1000 * (1 + daily_range / avg_range * 0.5)
    
    # 在关键事件位置增加成交量
    for pos in event_positions:
        if pos < len(volumes):
            volumes[pos] *= 2.5  # 事件日成交量放大
    
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=dates)
    
    return df, "铜期货 (SHFE铜)"


def generate_crude_oil_futures_data():
    """
    生成原油期货模拟数据
    原油期货特点：高波动，地缘政治敏感，趋势变化快
    """
    print("生成原油期货模拟数据...")
    
    dates = pd.date_range('2024-01-01', periods=150, freq='D')
    np.random.seed(43)
    
    # 基础价格：500-700美元/桶区间
    base_price = 600
    
    # 原油价格特征：
    # 1. 高波动性
    # 2. 地缘政治事件驱动
    # 3. OPEC决策影响
    # 4. 库存数据敏感
    
    # 主要趋势：先上涨后下跌
    trend1 = np.linspace(0, 80, 60)  # 前60天上涨80美元
    trend2 = np.linspace(0, -100, 90)  # 后90天下跌100美元
    main_trend = np.concatenate([trend1, trend2])
    
    # 高波动成分
    high_volatility = np.random.normal(0, 15, 150)  # 15美元标准差
    
    # 地缘政治冲击（更大更频繁）
    geo_shocks = np.zeros(150)
    geo_positions = [20, 45, 80, 110, 135]
    for pos in geo_positions:
        if pos < len(geo_shocks):
            # 地缘政治冲击：±5-10%的价格变动
            shock = np.random.uniform(0.05, 0.10) * base_price * np.random.choice([-1, 1])
            geo_shocks[pos] = shock
            # 冲击后持续影响
            for i in range(1, 15):
                if pos + i < len(geo_shocks):
                    geo_shocks[pos + i] = shock * np.exp(-0.2 * i)
    
    # 组合价格
    price = base_price + main_trend + high_volatility + geo_shocks
    
    # 关键技术位（整数关口）
    key_levels = [550, 575, 600, 625, 650, 675, 700]
    
    for i in range(len(price)):
        nearest_level = min(key_levels, key=lambda x: abs(x - price[i]))
        if abs(price[i] - nearest_level) < 3:  # 3美元内
            price[i] = nearest_level + np.random.uniform(-2, 2)
    
    # 生成OHLCV数据
    closes = price
    opens = closes - np.random.uniform(0.5, 2.0, 150)
    highs = closes + np.random.uniform(1.0, 4.0, 150)
    lows = closes - np.random.uniform(1.0, 4.0, 150)
    
    # 高成交量，与波动正相关
    daily_range = highs - lows
    avg_range = np.mean(daily_range)
    volumes = np.random.lognormal(14, 0.7, 150) * 1000 * (1 + daily_range / avg_range * 0.8)
    
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=dates)
    
    return df, "原油期货 (WTI原油)"


def generate_soybean_futures_data():
    """
    生成大豆期货模拟数据
    大豆期货特点：季节性明显，天气敏感，区间震荡为主
    """
    print("生成大豆期货模拟数据...")
    
    dates = pd.date_range('2024-01-01', periods=150, freq='D')
    np.random.seed(44)
    
    # 基础价格：4000-5000元/吨区间
    base_price = 4500
    
    # 大豆价格特征：
    # 1. 季节性明显（播种、生长、收获期）
    # 2. 天气敏感
    # 3. 区间震荡为主
    
    # 季节性模式：1-3月震荡，4-6月上涨，7-9月震荡，10-12月下跌
    seasonal = np.zeros(150)
    
    # 1-3月：区间震荡
    seasonal[0:90] = 100 * np.sin(np.linspace(0, 6*np.pi, 90))
    
    # 4-6月：种植担忧，价格上涨
    seasonal[90:120] = np.linspace(0, 300, 30)
    
    # 7-9月：天气市，高波动
    seasonal[120:150] = 200 * np.sin(np.linspace(0, 3*np.pi, 30)) + np.random.normal(0, 100, 30)
    
    # 区间震荡成分
    range_cycle = 150 * np.sin(np.linspace(0, 10*np.pi, 150))
    
    # 天气冲击
    weather_shocks = np.zeros(150)
    weather_positions = [95, 110, 130]  # 关键生长阶段
    for pos in weather_positions:
        if pos < len(weather_shocks):
            weather_shocks[pos] = np.random.uniform(0.03, 0.06) * base_price
    
    # 组合价格
    price = base_price + seasonal + range_cycle * 0.5 + weather_shocks
    
    # 关键区间边界
    key_levels = [4300, 4400, 4500, 4600, 4700, 4800]
    
    for i in range(len(price)):
        nearest_level = min(key_levels, key=lambda x: abs(x - price[i]))
        if abs(price[i] - nearest_level) < 20:
            price[i] = nearest_level + np.random.uniform(-15, 15)
    
    # 生成OHLCV数据
    closes = price
    opens = closes - np.random.uniform(10, 50, 150)
    highs = closes + np.random.uniform(20, 80, 150)
    lows = closes - np.random.uniform(20, 80, 150)
    
    # 成交量：季节性变化
    volumes = np.random.lognormal(11, 0.5, 150) * 1000
    # 关键时期成交量放大
    for pos in weather_positions:
        if pos < len(volumes):
            volumes[pos:pos+5] *= 2.0
    
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=dates)
    
    return df, "大豆期货 (DCE大豆)"


def run_commodity_analysis(commodity_name: str, price_data: pd.DataFrame):
    """
    运行商品期货分析
    
    参数:
        commodity_name: 商品名称
        price_data: 价格数据
    """
    print(f"\n{'='*60}")
    print(f"分析 {commodity_name}")
    print(f"{'='*60}")
    
    # 创建引擎实例
    engine = OptimizedPriceActionIntegrationEngine()
    integrator = PriceActionRulesIntegrator()
    
    # 1. 运行优化引擎
    print(f"\n1. 运行优化引擎分析 {commodity_name}...")
    engine.load_data(price_data)
    analysis_results = engine.run_analysis()
    
    # 2. 运行规则整合器
    print(f"2. 运行价格行为规则整合...")
    enhanced_results = integrator.integrate_rules(analysis_results, price_data)
    
    # 3. 生成整合报告
    print(f"3. 生成整合报告...")
    integration_report = integrator.generate_integration_report(enhanced_results)
    
    # 保存结果
    os.makedirs(f"commodity_results/{commodity_name}", exist_ok=True)
    
    with open(f"commodity_results/{commodity_name}/analysis_results.json", "w", encoding="utf-8") as f:
        json.dump(analysis_results, f, indent=2, default=str, ensure_ascii=False)
    
    with open(f"commodity_results/{commodity_name}/enhanced_results.json", "w", encoding="utf-8") as f:
        json.dump(enhanced_results, f, indent=2, default=str, ensure_ascii=False)
    
    with open(f"commodity_results/{commodity_name}/integration_report.json", "w", encoding="utf-8") as f:
        json.dump(integration_report, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"结果已保存到: commodity_results/{commodity_name}/")
    
    return analysis_results, enhanced_results, integration_report


def print_commodity_summary(commodity_name: str, 
                           analysis_results: Dict[str, Any],
                           enhanced_results: Dict[str, Any],
                           integration_report: Dict[str, Any]):
    """
    打印商品期货分析摘要
    """
    print(f"\n{'='*60}")
    print(f"{commodity_name} 分析摘要")
    print(f"{'='*60}")
    
    # 原始分析结果
    market_state = analysis_results.get('market_state', {})
    magnetic_levels = analysis_results.get('magnetic_levels', {})
    
    print(f"\n📊 市场状态:")
    print(f"  市场类型: {market_state.get('market_regime', '未知')}")
    print(f"  趋势方向: {market_state.get('trend_direction', '未知')}")
    print(f"  趋势强度: {market_state.get('trend_strength', '未知')}")
    print(f"  波动率: {market_state.get('volatility_level', '未知')}")
    
    print(f"\n🎯 关键水平识别:")
    print(f"  支撑位: {len(magnetic_levels.get('support_levels', []))} 个")
    print(f"  阻力位: {len(magnetic_levels.get('resistance_levels', []))} 个")
    
    # 规则整合结果
    validated_levels = enhanced_results.get('validated_magnetic_levels', {})
    trend_analysis = enhanced_results.get('trend_analysis', {})
    price_action_signals = enhanced_results.get('price_action_signals', {})
    
    print(f"\n🔍 规则整合验证:")
    print(f"  验证通过支撑位: {len(validated_levels.get('support_levels', []))}")
    print(f"  验证通过阻力位: {len(validated_levels.get('resistance_levels', []))}")
    print(f"  验证通过率: {validated_levels.get('validation_metrics', {}).get('validation_rate', 0):.1%}")
    
    print(f"\n📈 趋势分析:")
    print(f"  趋势方向: {trend_analysis.get('trend_direction', '未知')}")
    print(f"  趋势强度: {trend_analysis.get('trend_strength', '未知')}")
    print(f"  趋势健康度: {trend_analysis.get('trend_health', '未知')}")
    print(f"  趋势置信度: {trend_analysis.get('confidence', 0):.2f}")
    
    print(f"\n🚦 交易信号:")
    entry_signals = price_action_signals.get('entry_signals', [])
    print(f"  入场信号数量: {len(entry_signals)}")
    
    if entry_signals:
        signal_types = {}
        for signal in entry_signals:
            sig_type = signal.get('type', 'unknown')
            signal_types[sig_type] = signal_types.get(sig_type, 0) + 1
        
        print(f"  信号类型分布:")
        for sig_type, count in signal_types.items():
            print(f"    - {sig_type}: {count}个")
    
    # 交易计划
    trading_plans = enhanced_results.get('trading_plans', {})
    plans = trading_plans.get('plans', [])
    
    print(f"\n📝 交易计划:")
    print(f"  创建交易计划: {len(plans)}个")
    
    if plans:
        high_confidence_plans = [p for p in plans if p.get('plan_confidence', 0) >= 0.7]
        print(f"  高置信度计划 (≥0.7): {len(high_confidence_plans)}个")
    
    # 心理纪律检查
    psych_checks = enhanced_results.get('psychological_checks', {})
    warnings = psych_checks.get('warnings', [])
    
    if warnings:
        print(f"\n⚠️  心理纪律警告:")
        for i, warning in enumerate(warnings[:3]):
            print(f"  {i+1}. {warning}")
    
    # 整合报告摘要
    integration_summary = integration_report.get('integration_summary', {})
    print(f"\n✅ 整合报告摘要:")
    print(f"  应用规则类别: {len(integration_summary.get('rules_applied', []))}")
    print(f"  生成信号数量: {integration_summary.get('signals_generated', 0)}")
    print(f"  创建交易计划: {integration_summary.get('trading_plans_created', 0)}")
    
    # 可操作的见解
    print(f"\n💡 可操作的见解:")
    insights = integration_report.get('actionable_insights', [])
    for i, insight in enumerate(insights[:3]):
        insight_type = insight.get('type', 'unknown')
        if insight_type == 'trading_opportunity':
            print(f"  {i+1}. 交易机会: {insight.get('signal_type', '')} @ {insight.get('level_price', 0):.2f}")
        else:
            print(f"  {i+1}. {insight.get('warning', insight.get('recommendation', '未知'))}")


def compare_commodities(commodity_results: Dict[str, Any]):
    """
    比较不同商品期货的分析结果
    """
    print(f"\n{'='*60}")
    print("商品期货对比分析")
    print(f"{'='*60}")
    
    print(f"\n{'商品':<15} {'市场类型':<10} {'趋势':<10} {'强度':<10} {'信号数':<8} {'高置信计划':<12}")
    print("-" * 70)
    
    for commodity_name, results in commodity_results.items():
        enhanced_results = results.get('enhanced_results', {})
        
        market_state = results.get('analysis_results', {}).get('market_state', {})
        market_regime = market_state.get('market_regime', '未知')
        
        trend_analysis = enhanced_results.get('trend_analysis', {})
        trend_direction = trend_analysis.get('trend_direction', '未知')
        trend_strength = trend_analysis.get('trend_strength', '未知')
        
        price_action_signals = enhanced_results.get('price_action_signals', {})
        signal_count = len(price_action_signals.get('entry_signals', []))
        
        trading_plans = enhanced_results.get('trading_plans', {})
        plans = trading_plans.get('plans', [])
        high_conf_plans = len([p for p in plans if p.get('plan_confidence', 0) >= 0.7])
        
        print(f"{commodity_name:<15} {market_regime:<10} {trend_direction:<10} {trend_strength:<10} {signal_count:<8} {high_conf_plans:<12}")
    
    print(f"\n💎 分析结论:")
    
    # 根据市场类型给出建议
    for commodity_name, results in commodity_results.items():
        market_state = results.get('analysis_results', {}).get('market_state', {})
        market_regime = market_state.get('market_regime', '未知')
        trend_direction = results.get('enhanced_results', {}).get('trend_analysis', {}).get('trend_direction', '未知')
        
        if market_regime == 'trend':
            print(f"  • {commodity_name}: 趋势市场，建议趋势跟踪策略")
        elif market_regime == 'range':
            print(f"  • {commodity_name}: 区间市场，建议区间交易策略")
        
        # 交易信号数量建议
        signal_count = len(results.get('enhanced_results', {}).get('price_action_signals', {}).get('entry_signals', []))
        if signal_count > 5:
            print(f"  • {commodity_name}: 交易机会丰富，需精选高质量信号")
        elif signal_count == 0:
            print(f"  • {commodity_name}: 暂无明确交易机会，建议观望")


def main():
    """主函数"""
    print("商品期货价格行为整合框架测试")
    print("测试AL Brooks理论与技术工具在商品期货市场的应用")
    print("=" * 60)
    
    # 生成三种典型商品期货数据
    commodities = {
        "铜期货": generate_copper_futures_data(),
        "原油期货": generate_crude_oil_futures_data(),
        "大豆期货": generate_soybean_futures_data()
    }
    
    # 运行分析
    all_results = {}
    
    for commodity_name, (price_data, description) in commodities.items():
        try:
            print(f"\n📊 开始分析 {commodity_name} ({description})...")
            print(f"数据范围: {price_data.index[0].date()} 到 {price_data.index[-1].date()}")
            print(f"数据行数: {len(price_data)}")
            
            analysis_results, enhanced_results, integration_report = run_commodity_analysis(
                commodity_name, price_data
            )
            
            all_results[commodity_name] = {
                'analysis_results': analysis_results,
                'enhanced_results': enhanced_results,
                'integration_report': integration_report
            }
            
            print_commodity_summary(commodity_name, analysis_results, enhanced_results, integration_report)
            
        except Exception as e:
            print(f"❌ {commodity_name} 分析失败: {e}")
            import traceback
            traceback.print_exc()
    
    # 比较不同商品
    if all_results:
        compare_commodities(all_results)
    
    print(f"\n{'='*60}")
    print("✅ 商品期货分析完成!")
    print("=" * 60)
    print("\n生成的文件:")
    for commodity_name in commodities.keys():
        print(f"  commodity_results/{commodity_name}/")
        print(f"    - analysis_results.json - 原始分析结果")
        print(f"    - enhanced_results.json - 规则整合结果")
        print(f"    - integration_report.json - 整合报告")
    
    print(f"\n🎯 下一步建议:")
    print("  1. 使用真实商品期货数据替换模拟数据")
    print("  2. 调整参数以适应不同商品的波动特性")
    print("  3. 回测框架在历史数据上的表现")
    print("  4. 建立实时监控和信号提醒系统")


if __name__ == "__main__":
    main()