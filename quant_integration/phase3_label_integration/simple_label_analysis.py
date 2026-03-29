#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单Label Studio标注数据分析
快速提取模式分布，为策略整合提供洞察
"""

import json
import os
import glob
from collections import Counter
import re

def analyze_label_data(data_dir):
    """分析标注数据"""
    json_files = glob.glob(os.path.join(data_dir, "*.json"))
    print(f"找到 {len(json_files)} 个JSON文件")
    
    pattern_counter = Counter()
    stock_counter = Counter()
    total_annotations = 0
    processed_files = 0
    
    for json_file in json_files:
        # 跳过info文件
        if 'info.json' in json_file:
            continue
            
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                if not content:
                    continue
                    
                # 尝试解析为JSON
                data = json.loads(content)
                
                # 检查是否为列表
                if isinstance(data, list):
                    for task in data:
                        if isinstance(task, dict):
                            file_upload = task.get('file_upload', '')
                            stock_code = extract_stock_code(file_upload)
                            
                            for annotation in task.get('annotations', []):
                                for item in annotation.get('result', []):
                                    if item.get('type') == 'choices':
                                        choices = item.get('value', {}).get('choices', [])
                                        for choice in choices:
                                            pattern_counter[choice] += 1
                                            stock_counter[stock_code] += 1
                                            total_annotations += 1
                    
                    processed_files += 1
                    
        except json.JSONDecodeError as e:
            print(f"JSON解析错误 {json_file}: {e}")
            continue
        except Exception as e:
            print(f"处理文件 {json_file} 错误: {e}")
            continue
    
    print(f"\n处理了 {processed_files} 个标注文件")
    print(f"总标注数: {total_annotations}")
    
    return pattern_counter, stock_counter, total_annotations

def extract_stock_code(file_name):
    """提取股票代码"""
    pattern = re.compile(r'([0-9]{6})\.(SZ|SH)')
    match = pattern.search(file_name)
    if match:
        return f"{match.group(1)}.{match.group(2)}"
    return "未知"

def generate_strategy_insights(pattern_counter, stock_counter):
    """生成策略洞察"""
    total_patterns = sum(pattern_counter.values())
    
    # 分类模式
    trend_patterns = {'上升趋势', '下降趋势', '区间震荡'}
    formation_patterns = {'W底形态', 'M顶形态', '头肩顶', '头肩底'}
    phase_patterns = {'中阴阶段'}
    
    trend_count = sum(count for pattern, count in pattern_counter.items() if pattern in trend_patterns)
    formation_count = sum(count for pattern, count in pattern_counter.items() if pattern in formation_patterns)
    phase_count = sum(count for pattern, count in pattern_counter.items() if pattern in phase_patterns)
    
    # 计算比例
    trend_ratio = trend_count / total_patterns * 100 if total_patterns > 0 else 0
    formation_ratio = formation_count / total_patterns * 100 if total_patterns > 0 else 0
    phase_ratio = phase_count / total_patterns * 100 if total_patterns > 0 else 0
    
    insights = {
        'total_annotations': total_patterns,
        'unique_patterns': len(pattern_counter),
        'unique_stocks': len(stock_counter),
        'trend_patterns': trend_count,
        'trend_ratio': trend_ratio,
        'formation_patterns': formation_count,
        'formation_ratio': formation_ratio,
        'phase_patterns': phase_count,
        'phase_ratio': phase_ratio,
        'top_patterns': dict(pattern_counter.most_common(10)),
        'top_stocks': dict(stock_counter.most_common(5))
    }
    
    return insights

def create_integration_plan(insights):
    """创建标注数据整合计划"""
    plans = []
    
    # 1. 数据验证
    plans.append("1. 数据验证与清洗")
    plans.append("   - 验证标注数据质量，筛选高质量人工标注")
    plans.append("   - 建立标注数据与原始K线数据的映射关系")
    plans.append("   - 创建标注数据集，包含股票、时间范围、模式类型")
    
    # 2. 模式识别增强
    plans.append("\n2. 模式识别增强")
    plans.append("   - 使用标注数据训练/验证模式识别模型")
    plans.append("   - 集成标注模式到现有价格行为分析框架")
    plans.append("   - 建立标注置信度与策略信号权重的关联")
    
    # 3. 策略优化
    plans.append("\n3. 策略优化")
    plans.append("   - 分析不同模式标注后的价格走势规律")
    plans.append("   - 优化现有策略的入场和出场条件")
    plans.append("   - 开发基于标注模式的复合策略")
    
    # 4. 实时应用
    plans.append("\n4. 实时应用")
    plans.append("   - 将标注模型集成到实时分析系统")
    plans.append("   - 建立标注反馈循环，持续优化模型")
    plans.append("   - 开发标注驱动的信号预警系统")
    
    return plans

def main():
    """主函数"""
    data_dir = "/Users/chengming/Downloads/quant_trade-main/lable_ana/dataset/export"
    
    if not os.path.exists(data_dir):
        print(f"数据目录不存在: {data_dir}")
        return
    
    print("=" * 80)
    print("Label Studio标注数据分析")
    print("=" * 80)
    
    # 分析数据
    pattern_counter, stock_counter, total = analyze_label_data(data_dir)
    
    if total == 0:
        print("未找到有效标注数据")
        return
    
    # 生成洞察
    insights = generate_strategy_insights(pattern_counter, stock_counter)
    
    print("\n" + "=" * 80)
    print("分析结果摘要")
    print("=" * 80)
    
    print(f"\n【基础统计】")
    print(f"  总标注数: {insights['total_annotations']}")
    print(f"  唯一模式类型: {insights['unique_patterns']}")
    print(f"  涉及股票数量: {insights['unique_stocks']}")
    
    print(f"\n【模式分类】")
    print(f"  趋势模式: {insights['trend_patterns']} ({insights['trend_ratio']:.1f}%)")
    print(f"  形态模式: {insights['formation_patterns']} ({insights['formation_ratio']:.1f}%)")
    print(f"  阶段模式: {insights['phase_patterns']} ({insights['phase_ratio']:.1f}%)")
    
    print(f"\n【主要模式类型】")
    for pattern, count in insights['top_patterns'].items():
        percentage = count / insights['total_annotations'] * 100
        print(f"  {pattern}: {count} ({percentage:.1f}%)")
    
    print(f"\n【主要股票】")
    for stock, count in insights['top_stocks'].items():
        print(f"  {stock}: {count}")
    
    # 生成整合计划
    plans = create_integration_plan(insights)
    
    print("\n" + "=" * 80)
    print("标注数据整合计划")
    print("=" * 80)
    
    for plan in plans:
        print(plan)
    
    # 保存结果
    output_dir = "/Users/chengming/.openclaw/workspace/quant_integration/phase3_label_integration/results"
    os.makedirs(output_dir, exist_ok=True)
    
    # 保存统计结果
    results = {
        'insights': insights,
        'pattern_distribution': dict(pattern_counter),
        'stock_distribution': dict(stock_counter)
    }
    
    output_file = os.path.join(output_dir, 'simple_analysis_results.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\n分析结果已保存: {output_file}")
    print("\n" + "=" * 80)
    print("分析完成")

if __name__ == "__main__":
    main()