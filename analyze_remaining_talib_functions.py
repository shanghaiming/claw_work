#!/usr/bin/env python3
"""
分析剩余的TA-Lib函数，为扩展100个指标做准备
"""

import json
import os
from typing import List, Dict, Set

def load_talib_functions() -> Dict[str, List[str]]:
    """加载TA-Lib函数分类"""
    with open('talib_comprehensive_report.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    functions_by_category = {}
    for category, info in data['category_details'].items():
        functions = info.get('functions', [])
        functions_by_category[category] = functions
    
    return functions_by_category

def get_existing_indicators() -> Set[str]:
    """获取已存在的指标文件"""
    existing_indicators = set()
    
    if os.path.exists('tradingview_100_indicators'):
        for filename in os.listdir('tradingview_100_indicators'):
            if filename.endswith('.py') and filename != '__init__.py':
                # 去掉.py后缀，获取指标名
                indicator_name = filename[:-3]
                existing_indicators.add(indicator_name)
    
    return existing_indicators

def get_all_talib_functions(functions_by_category: Dict[str, List[str]]) -> Set[str]:
    """获取所有TA-Lib函数"""
    all_functions = set()
    for category, functions in functions_by_category.items():
        for func in functions:
            # 去掉stream_前缀，因为它们是重复的
            if func.startswith('stream_'):
                base_func = func[7:]  # 去掉'stream_'前缀
                all_functions.add(base_func)
            else:
                all_functions.add(func)
    return all_functions

def analyze_remaining_functions():
    """分析剩余函数"""
    print("=" * 80)
    print("🔍 TA-Lib剩余函数分析 - 为扩展100个指标做准备")
    print("=" * 80)
    
    # 加载数据
    functions_by_category = load_talib_functions()
    existing_indicators = get_existing_indicators()
    all_talib_functions = get_all_talib_functions(functions_by_category)
    
    # 计算统计
    total_talib_functions = len(all_talib_functions)
    total_existing = len(existing_indicators)
    
    print(f"\n📊 统计信息:")
    print(f"  TA-Lib总函数数: {total_talib_functions}")
    print(f"  已实现指标数: {total_existing}")
    print(f"  剩余可用函数数: {total_talib_functions - total_existing}")
    
    # 找出剩余函数
    remaining_functions = all_talib_functions - existing_indicators
    
    # 按类别分析剩余函数
    print(f"\n📈 按类别分析剩余函数:")
    
    category_stats = {}
    for category, functions in functions_by_category.items():
        # 转换函数列表为集合（去掉stream_前缀）
        category_funcs = set()
        for func in functions:
            if func.startswith('stream_'):
                base_func = func[7:]
                category_funcs.add(base_func)
            else:
                category_funcs.add(func)
        
        # 计算剩余
        remaining_in_category = category_funcs - existing_indicators
        category_stats[category] = {
            'total': len(category_funcs),
            'remaining': len(remaining_in_category),
            'remaining_list': list(remaining_in_category)
        }
        
        print(f"  {category}:")
        print(f"    总函数数: {len(category_funcs):3d} | 剩余: {len(remaining_in_category):3d} | 剩余比例: {len(remaining_in_category)/len(category_funcs)*100:.1f}%")
    
    # 按剩余数量排序
    sorted_categories = sorted(category_stats.items(), 
                              key=lambda x: x[1]['remaining'], 
                              reverse=True)
    
    print(f"\n🎯 剩余函数最多的类别:")
    for category, stats in sorted_categories[:5]:
        if stats['remaining'] > 0:
            print(f"  {category}: {stats['remaining']} 个剩余函数")
    
    # 选择100个新指标
    print(f"\n📋 选择100个新指标的策略:")
    
    # 优先选择剩余多的类别
    selected_functions = []
    remaining_to_select = 100
    
    for category, stats in sorted_categories:
        if stats['remaining'] > 0 and remaining_to_select > 0:
            # 从这个类别中选择函数
            available = stats['remaining_list'][:min(stats['remaining'], remaining_to_select)]
            selected_functions.extend(available)
            remaining_to_select -= len(available)
            print(f"  {category}: 选择 {len(available)} 个函数")
    
    # 如果需要更多，从其他来源补充
    if remaining_to_select > 0:
        print(f"  ⚠️  TA-Lib剩余函数不足，需要 {remaining_to_select} 个组合/自定义指标")
    
    # 保存分析结果
    analysis_result = {
        'total_talib_functions': total_talib_functions,
        'existing_indicators': total_existing,
        'remaining_functions': len(remaining_functions),
        'category_stats': category_stats,
        'selected_functions': selected_functions[:100],  # 确保不超过100个
        'need_custom_indicators': max(0, 100 - len(selected_functions))
    }
    
    with open('remaining_talib_analysis.json', 'w', encoding='utf-8') as f:
        json.dump(analysis_result, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 分析完成!")
    print(f"  已选择 {len(selected_functions[:100])} 个TA-Lib函数")
    print(f"  需要 {analysis_result['need_custom_indicators']} 个组合/自定义指标")
    print(f"  分析结果已保存: remaining_talib_analysis.json")
    
    return analysis_result

def suggest_composite_indicators():
    """建议组合指标"""
    print(f"\n💡 组合指标建议:")
    
    composite_ideas = [
        {
            'name': '趋势强度组合',
            'description': '多个趋势指标的组合，提高趋势判断准确性',
            'components': ['ADX', 'DMI', 'TRIX', 'MACD'],
            'combination_method': '加权平均'
        },
        {
            'name': '多时间框架RSI',
            'description': '多个时间周期的RSI组合，识别不同时间框架的超买超卖',
            'components': ['RSI_14', 'RSI_28', 'RSI_56'],
            'combination_method': '分层确认'
        },
        {
            'name': '波动率调整动量',
            'description': '动量指标根据波动率调整，适应不同市场环境',
            'components': ['MOM', 'ATR', 'ROC'],
            'combination_method': 'ATR标准化'
        },
        {
            'name': '成交量确认趋势',
            'description': '趋势指标需要成交量确认，提高信号可靠性',
            'components': ['EMA', 'VOLUME', 'OBV'],
            'combination_method': '条件确认'
        },
        {
            'name': '支撑阻力复合指标',
            'description': '多个支撑阻力指标组合，识别关键价格水平',
            'components': ['PIVOT', 'FIBONACCI', 'DEMA', 'SAR'],
            'combination_method': '区域聚合'
        }
    ]
    
    for i, idea in enumerate(composite_ideas, 1):
        print(f"  {i}. {idea['name']}:")
        print(f"     描述: {idea['description']}")
        print(f"     组件: {', '.join(idea['components'])}")
        print(f"     组合方法: {idea['combination_method']}")
    
    return composite_ideas

def suggest_custom_indicators():
    """建议自定义指标"""
    print(f"\n🎨 自定义指标建议 (基于TradingView设计思想):")
    
    custom_ideas = [
        {
            'name': '自适应趋势通道',
            'description': '根据市场波动率动态调整通道宽度',
            'design_philosophy': '自适应设计模式',
            'key_features': ['ATR动态调整', '多时间框架适应', '可视化趋势强度']
        },
        {
            'name': '智能止损系统',
            'description': '结合多个风险管理指标的动态止损',
            'design_philosophy': '风险管理集成模式',
            'key_features': ['波动率适应', '趋势跟随', '多层保护']
        },
        {
            'name': '成交量分布热力图',
            'description': '显示成交量在不同价格区间的分布',
            'design_philosophy': '可视化增强模式',
            'key_features': ['价格维度分布', '时间维度分析', '关键水平识别']
        },
        {
            'name': '多因子评分系统',
            'description': '多个技术指标综合评分，生成买卖信号',
            'design_philosophy': '复合系统模式',
            'key_features': ['多维度评分', '权重可调', '信号确认']
        },
        {
            'name': '市场情绪指标',
            'description': '结合价格、成交量、波动率分析市场情绪',
            'design_philosophy': '市场结构分析模式',
            'key_features': ['情绪量化', '极端预警', '趋势转换识别']
        }
    ]
    
    for i, idea in enumerate(custom_ideas, 1):
        print(f"  {i}. {idea['name']}:")
        print(f"     描述: {idea['description']}")
        print(f"     设计哲学: {idea['design_philosophy']}")
        print(f"     关键特性: {', '.join(idea['key_features'])}")
    
    return custom_ideas

def main():
    """主函数"""
    print("🚀 启动TA-Lib剩余函数分析")
    
    # 分析剩余TA-Lib函数
    analysis = analyze_remaining_functions()
    
    # 建议组合指标
    composite_ideas = suggest_composite_indicators()
    
    # 建议自定义指标
    custom_ideas = suggest_custom_indicators()
    
    # 生成执行计划
    print(f"\n📋 执行计划:")
    
    total_needed = 100
    talib_selected = len(analysis['selected_functions'])
    custom_needed = max(0, total_needed - talib_selected)
    
    print(f"  1. TA-Lib指标: {talib_selected} 个")
    print(f"  2. 组合指标: {min(5, custom_needed//2)} 个")
    print(f"  3. 自定义指标: {max(0, custom_needed - 5)} 个")
    print(f"  总计: {talib_selected + min(5, custom_needed//2) + max(0, custom_needed - 5)} 个")
    
    # 保存完整建议
    recommendations = {
        'talib_functions': analysis['selected_functions'],
        'composite_indicators': composite_ideas,
        'custom_indicators': custom_ideas,
        'implementation_plan': {
            'phase_1': '生成TA-Lib指标代码',
            'phase_2': '实现组合指标框架',
            'phase_3': '开发自定义指标',
            'phase_4': '集成和测试'
        }
    }
    
    with open('indicator_expansion_recommendations.json', 'w', encoding='utf-8') as f:
        json.dump(recommendations, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 分析和建议完成!")
    print(f"  详细建议已保存: indicator_expansion_recommendations.json")
    print(f"\n🎯 下一步: 开始生成新指标代码")

if __name__ == "__main__":
    main()