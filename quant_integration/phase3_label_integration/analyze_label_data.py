#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析Label Studio标注数据
提取模式类型分布，分析标注特征，为策略整合提供洞察
"""

import json
import os
import glob
from collections import Counter, defaultdict
import pandas as pd
from typing import Dict, List, Any, Tuple
import re

class LabelDataAnalyzer:
    """Label Studio标注数据分析器"""
    
    def __init__(self, data_dir: str):
        """初始化分析器
        
        Args:
            data_dir: Label Studio导出数据目录路径
        """
        self.data_dir = data_dir
        self.all_data = []
        self.annotations = []
        self.pattern_stats = Counter()
        self.stock_stats = Counter()
        self.date_pattern = re.compile(r'(\d{8})_(\d{8})')
        self.stock_pattern = re.compile(r'([0-9]{6})\.(SZ|SH)')
        
    def load_all_data(self) -> List[Dict[str, Any]]:
        """加载所有JSON标注数据
        
        Returns:
            List[Dict]: 所有标注数据
        """
        json_files = glob.glob(os.path.join(self.data_dir, "*.json"))
        print(f"找到 {len(json_files)} 个JSON文件")
        
        all_data = []
        for json_file in json_files:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    all_data.extend(data)
            except Exception as e:
                print(f"加载文件 {json_file} 失败: {e}")
        
        self.all_data = all_data
        print(f"加载了 {len(all_data)} 个标注任务")
        return all_data
    
    def extract_annotations(self) -> List[Dict[str, Any]]:
        """提取所有标注信息
        
        Returns:
            List[Dict]: 标注信息列表
        """
        annotations = []
        
        for task in self.all_data:
            task_id = task.get('id')
            file_upload = task.get('file_upload', '')
            
            # 从文件名提取信息
            stock_code, start_date, end_date = self._extract_file_info(file_upload)
            
            for annotation in task.get('annotations', []):
                result = annotation.get('result', [])
                if not result:
                    continue
                
                for item in result:
                    if item.get('type') == 'choices':
                        choices = item.get('value', {}).get('choices', [])
                        if choices:
                            for choice in choices:
                                annotations.append({
                                    'task_id': task_id,
                                    'file_name': file_upload,
                                    'stock_code': stock_code,
                                    'start_date': start_date,
                                    'end_date': end_date,
                                    'pattern_type': choice,
                                    'annotation_id': annotation.get('id'),
                                    'completed_by': annotation.get('completed_by'),
                                    'created_at': annotation.get('created_at'),
                                    'ground_truth': annotation.get('ground_truth', False),
                                    'score': item.get('score')  # 预测置信度
                                })
        
        self.annotations = annotations
        print(f"提取了 {len(annotations)} 个模式标注")
        return annotations
    
    def _extract_file_info(self, file_name: str) -> Tuple[str, str, str]:
        """从文件名提取股票代码和日期范围
        
        Args:
            file_name: 文件名，如 "000063.SZ_analysis_20220104_20220106.png"
            
        Returns:
            Tuple: (股票代码, 开始日期, 结束日期)
        """
        stock_code = '未知'
        start_date = '未知'
        end_date = '未知'
        
        # 提取股票代码
        stock_match = self.stock_pattern.search(file_name)
        if stock_match:
            stock_code = f"{stock_match.group(1)}.{stock_match.group(2)}"
        
        # 提取日期范围
        date_match = self.date_pattern.search(file_name)
        if date_match:
            start_date = date_match.group(1)
            end_date = date_match.group(2)
        
        return stock_code, start_date, end_date
    
    def analyze_pattern_distribution(self) -> Dict[str, Any]:
        """分析模式类型分布
        
        Returns:
            Dict: 模式分布统计
        """
        if not self.annotations:
            self.extract_annotations()
        
        # 统计模式类型
        pattern_counter = Counter()
        for ann in self.annotations:
            pattern_counter[ann['pattern_type']] += 1
        
        self.pattern_stats = pattern_counter
        
        # 计算百分比
        total = sum(pattern_counter.values())
        pattern_percent = {k: v/total*100 for k, v in pattern_counter.items()}
        
        # 按股票统计
        stock_counter = Counter()
        for ann in self.annotations:
            stock_counter[ann['stock_code']] += 1
        
        self.stock_stats = stock_counter
        
        return {
            'total_annotations': total,
            'pattern_distribution': dict(pattern_counter),
            'pattern_percentage': pattern_percent,
            'stock_distribution': dict(stock_counter),
            'unique_patterns': len(pattern_counter),
            'unique_stocks': len(stock_counter)
        }
    
    def analyze_pattern_combinations(self) -> Dict[str, Any]:
        """分析模式组合
        
        Returns:
            Dict: 模式组合统计
        """
        if not self.all_data:
            self.load_all_data()
        
        pattern_combinations = []
        single_patterns = []
        multi_patterns = []
        
        for task in self.all_data:
            task_patterns = set()
            for annotation in task.get('annotations', []):
                for item in annotation.get('result', []):
                    if item.get('type') == 'choices':
                        choices = item.get('value', {}).get('choices', [])
                        task_patterns.update(choices)
            
            if task_patterns:
                pattern_list = sorted(list(task_patterns))
                pattern_combinations.append(tuple(pattern_list))
                
                if len(task_patterns) == 1:
                    single_patterns.append(pattern_list[0])
                else:
                    multi_patterns.append(pattern_list)
        
        # 统计组合频率
        combo_counter = Counter(pattern_combinations)
        
        return {
            'total_tasks': len(pattern_combinations),
            'single_pattern_tasks': len(single_patterns),
            'multi_pattern_tasks': len(multi_patterns),
            'single_pattern_ratio': len(single_patterns)/len(pattern_combinations)*100 if pattern_combinations else 0,
            'top_combinations': dict(combo_counter.most_common(10)),
            'unique_combinations': len(combo_counter)
        }
    
    def analyze_temporal_patterns(self) -> Dict[str, Any]:
        """分析时间模式
        
        Returns:
            Dict: 时间模式统计
        """
        if not self.annotations:
            self.extract_annotations()
        
        # 按日期范围统计
        date_stats = defaultdict(list)
        for ann in self.annotations:
            if ann['start_date'] != '未知' and ann['end_date'] != '未知':
                key = f"{ann['start_date']}-{ann['end_date']}"
                date_stats[key].append(ann['pattern_type'])
        
        # 按年份统计
        year_stats = Counter()
        for ann in self.annotations:
            if ann['start_date'] != '未知':
                year = ann['start_date'][:4]
                year_stats[year] += 1
        
        return {
            'date_ranges_covered': len(date_stats),
            'year_distribution': dict(year_stats),
            'samples_per_date_range': {k: len(v) for k, v in list(date_stats.items())[:10]}
        }
    
    def analyze_prediction_quality(self) -> Dict[str, Any]:
        """分析预测质量
        
        Returns:
            Dict: 预测质量统计
        """
        if not self.annotations:
            self.extract_annotations()
        
        manual_annotations = []
        predicted_annotations = []
        
        for ann in self.annotations:
            if ann.get('score') is not None:
                predicted_annotations.append(ann)
            else:
                manual_annotations.append(ann)
        
        # 统计预测模式分布
        manual_patterns = Counter([a['pattern_type'] for a in manual_annotations])
        predicted_patterns = Counter([a['pattern_type'] for a in predicted_annotations])
        
        # 计算预测置信度统计
        scores = [a.get('score', 0) for a in predicted_annotations if a.get('score') is not None]
        
        return {
            'total_manual': len(manual_annotations),
            'total_predicted': len(predicted_annotations),
            'manual_ratio': len(manual_annotations)/len(self.annotations)*100 if self.annotations else 0,
            'predicted_ratio': len(predicted_annotations)/len(self.annotations)*100 if self.annotations else 0,
            'manual_pattern_dist': dict(manual_patterns),
            'predicted_pattern_dist': dict(predicted_patterns),
            'avg_prediction_score': sum(scores)/len(scores) if scores else 0,
            'min_prediction_score': min(scores) if scores else 0,
            'max_prediction_score': max(scores) if scores else 0
        }
    
    def generate_insights_for_strategy(self) -> Dict[str, Any]:
        """生成策略洞察
        
        Returns:
            Dict: 策略洞察和建议
        """
        # 分析所有数据
        pattern_stats = self.analyze_pattern_distribution()
        combo_stats = self.analyze_pattern_combinations()
        temporal_stats = self.analyze_temporal_patterns()
        quality_stats = self.analyze_prediction_quality()
        
        # 提取关键洞察
        pattern_dist = pattern_stats['pattern_distribution']
        
        # 识别主要趋势模式
        trend_patterns = {'上升趋势', '下降趋势', '区间震荡'}
        trend_count = sum(v for k, v in pattern_dist.items() if k in trend_patterns)
        
        # 识别主要形态模式
        formation_patterns = {'W底形态', 'M顶形态', '头肩顶', '头肩底'}
        formation_count = sum(v for k, v in pattern_dist.items() if k in formation_patterns)
        
        # 识别阶段模式
        phase_patterns = {'中阴阶段'}
        phase_count = sum(v for k, v in pattern_dist.items() if k in phase_patterns)
        
        insights = {
            # 基础统计
            'total_annotations': pattern_stats['total_annotations'],
            'unique_patterns': pattern_stats['unique_patterns'],
            'unique_stocks': pattern_stats['unique_stocks'],
            
            # 模式分类
            'trend_patterns_count': trend_count,
            'trend_patterns_ratio': trend_count/pattern_stats['total_annotations']*100,
            'formation_patterns_count': formation_count,
            'formation_patterns_ratio': formation_count/pattern_stats['total_annotations']*100,
            'phase_patterns_count': phase_count,
            'phase_patterns_ratio': phase_count/pattern_stats['total_annotations']*100,
            
            # 组合洞察
            'multi_pattern_ratio': combo_stats['multi_pattern_ratio'],
            'common_combinations': combo_stats['top_combinations'],
            
            # 质量洞察
            'prediction_quality': quality_stats['avg_prediction_score'],
            'human_annotation_ratio': quality_stats['manual_ratio'],
            
            # 时间洞察
            'temporal_coverage': temporal_stats['date_ranges_covered'],
            'year_distribution': temporal_stats['year_distribution']
        }
        
        # 生成策略建议
        suggestions = []
        
        # 基于趋势模式
        if trend_count > 0:
            suggestions.append("标注数据包含大量趋势模式，可用于训练趋势识别模型")
            suggestions.append("上升趋势和下降趋势标注可用于验证移动平均策略信号")
        
        # 基于形态模式
        if formation_count > 0:
            suggestions.append("W底/M顶/头肩顶等形态标注可用于增强价格行为模式识别")
            suggestions.append("形态标注数据可作为模式识别策略的ground truth")
        
        # 基于多模式组合
        if combo_stats['multi_pattern_ratio'] > 20:
            suggestions.append("多模式组合常见，建议开发复合模式识别策略")
            suggestions.append("可分析模式组合与后续价格走势的关系")
        
        # 基于预测质量
        if quality_stats['avg_prediction_score'] > 0.7:
            suggestions.append("预测模型质量较高，可考虑集成到实时分析中")
        else:
            suggestions.append("预测模型质量一般，建议优先使用人工标注数据")
        
        insights['strategy_suggestions'] = suggestions
        
        return insights
    
    def create_summary_report(self) -> str:
        """创建分析摘要报告
        
        Returns:
            str: 报告文本
        """
        pattern_stats = self.analyze_pattern_distribution()
        insights = self.generate_insights_for_strategy()
        
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("Label Studio标注数据分析报告")
        report_lines.append("=" * 80)
        report_lines.append("")
        
        report_lines.append("【基础统计】")
        report_lines.append(f"  总标注数: {pattern_stats['total_annotations']}")
        report_lines.append(f"  唯一模式类型: {pattern_stats['unique_patterns']}")
        report_lines.append(f"  涉及股票数量: {pattern_stats['unique_stocks']}")
        report_lines.append("")
        
        report_lines.append("【模式类型分布】")
        for pattern, count in pattern_stats['pattern_distribution'].items():
            percentage = pattern_stats['pattern_percentage'][pattern]
            report_lines.append(f"  {pattern}: {count} ({percentage:.1f}%)")
        report_lines.append("")
        
        report_lines.append("【股票分布】")
        for stock, count in list(pattern_stats['stock_distribution'].items())[:5]:
            report_lines.append(f"  {stock}: {count}")
        if len(pattern_stats['stock_distribution']) > 5:
            report_lines.append(f"  ... 等 {len(pattern_stats['stock_distribution'])} 只股票")
        report_lines.append("")
        
        report_lines.append("【策略洞察】")
        report_lines.append(f"  趋势模式占比: {insights['trend_patterns_ratio']:.1f}%")
        report_lines.append(f"  形态模式占比: {insights['formation_patterns_ratio']:.1f}%")
        report_lines.append(f"  多模式组合占比: {insights.get('multi_pattern_ratio', 0):.1f}%")
        report_lines.append(f"  人工标注比例: {insights.get('human_annotation_ratio', 0):.1f}%")
        report_lines.append("")
        
        report_lines.append("【策略建议】")
        for i, suggestion in enumerate(insights.get('strategy_suggestions', []), 1):
            report_lines.append(f"  {i}. {suggestion}")
        
        report_lines.append("")
        report_lines.append("=" * 80)
        report_lines.append("报告生成完成")
        
        return "\n".join(report_lines)
    
    def save_analysis_results(self, output_dir: str):
        """保存分析结果
        
        Args:
            output_dir: 输出目录
        """
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存详细统计数据
        pattern_stats = self.analyze_pattern_distribution()
        insights = self.generate_insights_for_strategy()
        
        # 保存JSON格式数据
        results = {
            'pattern_statistics': pattern_stats,
            'strategy_insights': insights,
            'annotations_sample': self.annotations[:10] if self.annotations else []
        }
        
        output_file = os.path.join(output_dir, 'label_analysis_results.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"详细分析结果已保存: {output_file}")
        
        # 保存文本报告
        report = self.create_summary_report()
        report_file = os.path.join(output_dir, 'label_analysis_report.txt')
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"文本报告已保存: {report_file}")
        
        # 保存为CSV格式用于进一步分析
        if self.annotations:
            df = pd.DataFrame(self.annotations)
            csv_file = os.path.join(output_dir, 'annotations_data.csv')
            df.to_csv(csv_file, index=False, encoding='utf-8-sig')
            print(f"标注数据CSV已保存: {csv_file}")


def main():
    """主函数"""
    # 设置数据目录
    data_dir = "/Users/chengming/Downloads/quant_trade-main/lable_ana/dataset/export"
    
    if not os.path.exists(data_dir):
        print(f"数据目录不存在: {data_dir}")
        return
    
    # 创建分析器
    analyzer = LabelDataAnalyzer(data_dir)
    
    print("开始分析Label Studio标注数据...")
    print("=" * 80)
    
    # 加载数据
    analyzer.load_all_data()
    
    # 提取标注
    analyzer.extract_annotations()
    
    # 生成报告
    report = analyzer.create_summary_report()
    print(report)
    
    # 保存结果
    output_dir = "/Users/chengming/.openclaw/workspace/quant_integration/phase3_label_integration/results"
    analyzer.save_analysis_results(output_dir)
    
    print("\n分析完成!")


if __name__ == "__main__":
    main()