#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略管理器 - 统一管理多个策略的注册、配置、执行和比较

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

功能特性:
1. 策略注册和发现
2. 统一配置管理
3. 批量策略执行
4. 性能比较和评估
5. 结果聚合和分析
6. 策略组合和优化
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple, Callable
from datetime import datetime, timedelta
import warnings
import json
import os
import sys
from pathlib import Path
warnings.filterwarnings('ignore')

# 导入统一策略基类
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.unified_strategy_base import UnifiedStrategyBase


class StrategyManager:
    """
    策略管理器 - 统一管理所有策略
    
    设计目标:
    1. 提供统一的策略管理接口
    2. 支持策略的注册、配置和执行
    3. 提供策略性能比较和评估
    4. 支持策略组合和优化
    5. 提供结果可视化和报告
    """
    
    def __init__(self, 
                 name: str = "DefaultStrategyManager",
                 config_dir: Optional[str] = None,
                 results_dir: Optional[str] = None):
        """
        初始化策略管理器
        
        参数:
            name: 管理器名称
            config_dir: 配置文件目录
            results_dir: 结果保存目录
        """
        self.name = name
        self.config_dir = config_dir or "./config"
        self.results_dir = results_dir or "./results"
        
        # 策略注册表
        self.strategies = {}  # name -> strategy_class
        self.strategy_configs = {}  # name -> default_config
        self.strategy_instances = {}  # name -> strategy_instance
        
        # 执行结果缓存
        self.execution_results = {}  # name -> execution_results
        self.comparison_results = {}  # 策略比较结果
        
        # 性能指标
        self.performance_metrics = {}
        
        # 创建目录
        self._create_directories()
        
        print(f"策略管理器 '{self.name}' 初始化完成")
        print(f"配置目录: {self.config_dir}")
        print(f"结果目录: {self.results_dir}")
    
    def _create_directories(self):
        """创建必要的目录结构"""
        directories = [
            self.config_dir,
            self.results_dir,
            os.path.join(self.results_dir, "signals"),
            os.path.join(self.results_dir, "reports"),
            os.path.join(self.results_dir, "comparisons"),
            os.path.join(self.results_dir, "logs")
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
    
    def register_strategy(self, 
                         name: str, 
                         strategy_class: type,
                         default_config: Optional[Dict] = None,
                         description: Optional[str] = None):
        """
        注册策略
        
        参数:
            name: 策略名称（唯一标识）
            strategy_class: 策略类（必须是UnifiedStrategyBase的子类）
            default_config: 默认配置
            description: 策略描述
        """
        # 验证策略类
        if not issubclass(strategy_class, UnifiedStrategyBase):
            raise TypeError(f"策略类必须继承自UnifiedStrategyBase，但收到: {strategy_class}")
        
        # 检查名称是否已存在
        if name in self.strategies:
            print(f"警告: 策略名称 '{name}' 已存在，将被覆盖")
        
        # 注册策略
        self.strategies[name] = strategy_class
        self.strategy_configs[name] = default_config or {}
        
        # 添加描述
        if description:
            self.strategy_configs[name]['description'] = description
        
        print(f"注册策略: {name} ({strategy_class.__name__})")
        
        # 保存默认配置
        self._save_strategy_config(name)
    
    def register_strategies_from_module(self, 
                                       module_path: str,
                                       strategy_names: Optional[List[str]] = None):
        """
        从模块批量注册策略
        
        参数:
            module_path: 模块路径
            strategy_names: 要注册的策略名称列表（如果为None，则注册所有策略类）
        """
        try:
            # 动态导入模块
            import importlib
            module = importlib.import_module(module_path)
            
            # 查找所有策略类
            strategy_classes = []
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # 检查是否是类且是UnifiedStrategyBase的子类
                if (isinstance(attr, type) and 
                    issubclass(attr, UnifiedStrategyBase) and 
                    attr != UnifiedStrategyBase):
                    
                    strategy_classes.append((attr_name, attr))
            
            # 过滤策略
            if strategy_names:
                strategy_classes = [(n, c) for n, c in strategy_classes if n in strategy_names]
            
            # 注册策略
            for strategy_name, strategy_class in strategy_classes:
                self.register_strategy(
                    name=strategy_name,
                    strategy_class=strategy_class,
                    description=f"从模块 {module_path} 自动注册"
                )
            
            print(f"从模块 {module_path} 注册了 {len(strategy_classes)} 个策略")
            
        except Exception as e:
            print(f"从模块注册策略失败: {e}")
    
    def _save_strategy_config(self, strategy_name: str):
        """保存策略配置到文件"""
        if strategy_name not in self.strategy_configs:
            return
        
        config_file = os.path.join(self.config_dir, f"{strategy_name}_config.json")
        
        try:
            with open(config_file, 'w', encoding='utf-8') as f:
                json.dump(self.strategy_configs[strategy_name], f, indent=2, default=str)
            
            print(f"策略配置已保存: {config_file}")
            
        except Exception as e:
            print(f"保存策略配置失败: {e}")
    
    def load_strategy_config(self, strategy_name: str) -> Dict:
        """从文件加载策略配置"""
        config_file = os.path.join(self.config_dir, f"{strategy_name}_config.json")
        
        if not os.path.exists(config_file):
            print(f"配置文件不存在: {config_file}，使用默认配置")
            return self.strategy_configs.get(strategy_name, {})
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            print(f"策略配置已加载: {config_file}")
            return config
            
        except Exception as e:
            print(f"加载策略配置失败: {e}")
            return self.strategy_configs.get(strategy_name, {})
    
    def create_strategy_instance(self,
                                strategy_name: str,
                                data: pd.DataFrame,
                                config: Optional[Dict] = None,
                                instance_name: Optional[str] = None) -> UnifiedStrategyBase:
        """
        创建策略实例
        
        参数:
            strategy_name: 已注册的策略名称
            data: 交易数据
            config: 策略配置（覆盖默认配置）
            instance_name: 实例名称（如果为None，则使用策略名称）
        
        返回:
            策略实例
        """
        # 检查策略是否已注册
        if strategy_name not in self.strategies:
            raise ValueError(f"策略 '{strategy_name}' 未注册")
        
        # 合并配置
        default_config = self.load_strategy_config(strategy_name)
        merged_config = {**default_config, **(config or {})}
        
        # 创建实例名称
        instance_name = instance_name or f"{strategy_name}_instance"
        
        try:
            # 创建策略实例
            strategy_class = self.strategies[strategy_name]
            instance = strategy_class(
                data=data,
                params=merged_config,
                strategy_name=instance_name
            )
            
            # 保存到实例缓存
            self.strategy_instances[instance_name] = instance
            
            print(f"创建策略实例: {instance_name} (基于 {strategy_name})")
            
            return instance
            
        except Exception as e:
            print(f"创建策略实例失败: {e}")
            raise
    
    def run_strategy(self,
                    strategy_name: str,
                    data: pd.DataFrame,
                    config: Optional[Dict] = None,
                    instance_name: Optional[str] = None,
                    save_results: bool = True) -> Dict[str, Any]:
        """
        运行单个策略
        
        参数:
            strategy_name: 策略名称
            data: 交易数据
            config: 策略配置
            instance_name: 实例名称
            save_results: 是否保存结果
        
        返回:
            执行结果字典
        """
        print(f"\n{'='*60}")
        print(f"运行策略: {strategy_name}")
        print(f"{'='*60}")
        
        try:
            # 创建策略实例
            instance = self.create_strategy_instance(
                strategy_name=strategy_name,
                data=data,
                config=config,
                instance_name=instance_name
            )
            
            # 运行策略
            start_time = datetime.now()
            signals = instance.generate_standard_signals()
            end_time = datetime.now()
            
            execution_time = (end_time - start_time).total_seconds()
            
            # 收集结果
            result = {
                'strategy_name': strategy_name,
                'instance_name': instance.strategy_name,
                'execution_time': execution_time,
                'signal_count': len(signals),
                'signals': signals,
                'performance_metrics': instance.get_performance_metrics(),
                'config': instance.params,
                'timestamp': start_time.isoformat()
            }
            
            # 保存结果
            if save_results:
                self._save_execution_result(result)
            
            # 更新缓存
            self.execution_results[instance.strategy_name] = result
            
            # 打印摘要
            print(f"\n✅ 策略执行完成:")
            print(f"  策略: {strategy_name}")
            print(f"  实例: {instance.strategy_name}")
            print(f"  执行时间: {execution_time:.3f}秒")
            print(f"  信号数量: {len(signals)}")
            print(f"  配置参数: {len(instance.params)}个")
            
            # 保存信号到文件
            if save_results and signals:
                signals_file = os.path.join(self.results_dir, "signals", f"{instance.strategy_name}_signals.json")
                instance.save_signals(signals_file, 'json')
            
            return result
            
        except Exception as e:
            print(f"❌ 策略执行失败: {e}")
            import traceback
            traceback.print_exc()
            
            # 返回错误结果
            return {
                'strategy_name': strategy_name,
                'instance_name': instance_name or strategy_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_strategies(self,
                      strategy_names: List[str],
                      data: pd.DataFrame,
                      configs: Optional[Dict[str, Dict]] = None,
                      parallel: bool = False,
                      save_results: bool = True) -> Dict[str, Dict]:
        """
        运行多个策略
        
        参数:
            strategy_names: 策略名称列表
            data: 交易数据
            configs: 策略配置字典（策略名称 -> 配置）
            parallel: 是否并行执行（需要多进程支持）
            save_results: 是否保存结果
        
        返回:
            所有策略的执行结果字典
        """
        print(f"\n{'='*60}")
        print(f"批量运行策略 ({len(strategy_names)} 个策略)")
        print(f"{'='*60}")
        
        results = {}
        configs = configs or {}
        
        if parallel:
            # 并行执行（简化版本）
            print("警告: 并行执行暂未实现，将顺序执行")
            parallel = False
        
        # 顺序执行
        for i, strategy_name in enumerate(strategy_names, 1):
            print(f"\n[{i}/{len(strategy_names)}] 运行策略: {strategy_name}")
            
            # 获取该策略的配置
            strategy_config = configs.get(strategy_name, {})
            
            # 运行策略
            result = self.run_strategy(
                strategy_name=strategy_name,
                data=data,
                config=strategy_config,
                instance_name=f"{strategy_name}_batch_{i}",
                save_results=save_results
            )
            
            results[strategy_name] = result
        
        print(f"\n✅ 批量策略执行完成: {len(results)}/{len(strategy_names)} 个策略成功")
        
        # 比较策略性能
        if len(results) > 1:
            self.compare_strategies(list(results.keys()))
        
        return results
    
    def run_all_strategies(self,
                          data: pd.DataFrame,
                          configs: Optional[Dict[str, Dict]] = None,
                          exclude: Optional[List[str]] = None,
                          **kwargs) -> Dict[str, Dict]:
        """
        运行所有已注册的策略
        
        参数:
            data: 交易数据
            configs: 策略配置字典
            exclude: 要排除的策略名称列表
            **kwargs: 传递给run_strategies的其他参数
        
        返回:
            所有策略的执行结果字典
        """
        # 获取所有策略名称
        all_strategy_names = list(self.strategies.keys())
        
        # 排除指定策略
        if exclude:
            all_strategy_names = [name for name in all_strategy_names if name not in exclude]
        
        print(f"运行所有策略 (共 {len(all_strategy_names)} 个，排除 {len(exclude or [])} 个)")
        
        # 运行策略
        return self.run_strategies(
            strategy_names=all_strategy_names,
            data=data,
            configs=configs,
            **kwargs
        )
    
    def _save_execution_result(self, result: Dict):
        """保存执行结果到文件"""
        instance_name = result.get('instance_name', 'unknown')
        result_file = os.path.join(self.results_dir, "reports", f"{instance_name}_result.json")
        
        try:
            with open(result_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str)
            
            print(f"执行结果已保存: {result_file}")
            
        except Exception as e:
            print(f"保存执行结果失败: {e}")
    
    def compare_strategies(self, strategy_names: Optional[List[str]] = None):
        """
        比较策略性能
        
        参数:
            strategy_names: 要比较的策略名称列表（如果为None，则比较所有有结果的策略）
        """
        # 确定要比较的策略
        if strategy_names is None:
            strategy_names = list(self.execution_results.keys())
        
        if len(strategy_names) < 2:
            print("需要至少2个策略结果进行比较")
            return
        
        print(f"\n{'='*60}")
        print(f"策略性能比较 ({len(strategy_names)} 个策略)")
        print(f"{'='*60}")
        
        comparison_data = []
        
        for strategy_name in strategy_names:
            if strategy_name not in self.execution_results:
                print(f"警告: 策略 '{strategy_name}' 没有执行结果，跳过")
                continue
            
            result = self.execution_results[strategy_name]
            
            # 提取性能指标
            metrics = {
                'strategy': strategy_name,
                'instance': result.get('instance_name', strategy_name),
                'execution_time': result.get('execution_time', 0),
                'signal_count': result.get('signal_count', 0),
                'success': 'error' not in result
            }
            
            # 添加性能指标
            perf_metrics = result.get('performance_metrics', {})
            exec_stats = perf_metrics.get('execution_stats', {})
            
            metrics.update({
                'buy_signals': exec_stats.get('buy_count', 0),
                'sell_signals': exec_stats.get('sell_count', 0),
                'total_signals': exec_stats.get('signal_count', 0)
            })
            
            comparison_data.append(metrics)
        
        if not comparison_data:
            print("没有有效的策略结果可比较")
            return
        
        # 创建比较DataFrame
        df_comparison = pd.DataFrame(comparison_data)
        
        # 计算排名
        if 'execution_time' in df_comparison.columns:
            df_comparison['execution_time_rank'] = df_comparison['execution_time'].rank(ascending=True)
        
        if 'signal_count' in df_comparison.columns:
            df_comparison['signal_count_rank'] = df_comparison['signal_count'].rank(ascending=False)
        
        # 保存比较结果
        comparison_file = os.path.join(self.results_dir, "comparisons", 
                                      f"comparison_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv")
        df_comparison.to_csv(comparison_file, index=False)
        
        # 打印比较结果
        print(f"\n📊 策略性能比较结果:")
        print(df_comparison.to_string(index=False))
        
        print(f"\n🏆 性能最佳策略:")
        
        # 执行时间最快
        if 'execution_time' in df_comparison.columns:
            fastest = df_comparison.loc[df_comparison['execution_time'].idxmin()]
            print(f"  执行最快: {fastest['strategy']} ({fastest['execution_time']:.3f}秒)")
        
        # 信号数量最多
        if 'signal_count' in df_comparison.columns:
            most_signals = df_comparison.loc[df_comparison['signal_count'].idxmax()]
            print(f"  信号最多: {most_signals['strategy']} ({most_signals['signal_count']}个信号)")
        
        # 买入信号最多
        if 'buy_signals' in df_comparison.columns:
            most_buys = df_comparison.loc[df_comparison['buy_signals'].idxmax()]
            print(f"  买入最多: {most_buys['strategy']} ({most_buys['buy_signals']}个买入信号)")
        
        print(f"\n比较结果已保存: {comparison_file}")
        
        # 更新缓存
        self.comparison_results = {
            'timestamp': datetime.now().isoformat(),
            'strategies_compared': len(comparison_data),
            'data': comparison_data,
            'dataframe': df_comparison.to_dict('records')
        }
    
    def generate_report(self, 
                       strategy_names: Optional[List[str]] = None,
                       report_format: str = 'text') -> str:
        """
        生成策略执行报告
        
        参数:
            strategy_names: 策略名称列表
            report_format: 报告格式 ('text', 'markdown', 'html')
        
        返回:
            报告内容
        """
        # 确定要报告的策略
        if strategy_names is None:
            strategy_names = list(self.execution_results.keys())
        
        if not strategy_names:
            return "没有策略执行结果可报告"
        
        # 收集报告数据
        report_data = []
        for name in strategy_names:
            if name in self.execution_results:
                report_data.append(self.execution_results[name])
        
        # 生成报告
        if report_format == 'text':
            return self._generate_text_report(report_data)
        elif report_format == 'markdown':
            return self._generate_markdown_report(report_data)
        elif report_format == 'html':
            return self._generate_html_report(report_data)
        else:
            raise ValueError(f"不支持的报告格式: {report_format}")
    
    def _generate_text_report(self, report_data: List[Dict]) -> str:
        """生成文本报告"""
        lines = []
        
        lines.append("="*60)
        lines.append("策略执行报告")
        lines.append("="*60)
        lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"策略数量: {len(report_data)}")
        lines.append("")
        
        for i, result in enumerate(report_data, 1):
            lines.append(f"{i}. 策略: {result.get('strategy_name', 'Unknown')}")
            lines.append(f"   实例: {result.get('instance_name', 'Unknown')}")
            lines.append(f"   执行时间: {result.get('execution_time', 0):.3f}秒")
            lines.append(f"   信号数量: {result.get('signal_count', 0)}")
            lines.append(f"   状态: {'成功' if 'error' not in result else '失败'}")
            
            if 'error' in result:
                lines.append(f"   错误: {result['error']}")
            
            lines.append("")
        
        # 统计信息
        successful = len([r for r in report_data if 'error' not in r])
        total_signals = sum(r.get('signal_count', 0) for r in report_data)
        total_time = sum(r.get('execution_time', 0) for r in report_data)
        
        lines.append("="*60)
        lines.append("统计摘要")
        lines.append("="*60)
        lines.append(f"成功策略: {successful}/{len(report_data)}")
        lines.append(f"总信号数: {total_signals}")
        lines.append(f"总执行时间: {total_time:.3f}秒")
        lines.append(f"平均每个策略: {total_time/len(report_data):.3f}秒")
        
        return "\n".join(lines)
    
    def _generate_markdown_report(self, report_data: List[Dict]) -> str:
        """生成Markdown报告"""
        # 简化的Markdown报告
        lines = []
        
        lines.append("# 策略执行报告")
        lines.append("")
        lines.append(f"**生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"**策略数量**: {len(report_data)}")
        lines.append("")
        
        lines.append("## 策略执行详情")
        lines.append("")
        
        for i, result in enumerate(report_data, 1):
            status = "✅ 成功" if 'error' not in result else "❌ 失败"
            
            lines.append(f"### {i}. {result.get('strategy_name', 'Unknown')}")
            lines.append("")
            lines.append(f"- **实例**: {result.get('instance_name', 'Unknown')}")
            lines.append(f"- **状态**: {status}")
            lines.append(f"- **执行时间**: {result.get('execution_time', 0):.3f}秒")
            lines.append(f"- **信号数量**: {result.get('signal_count', 0)}")
            
            if 'error' in result:
                lines.append(f"- **错误**: `{result['error']}`")
            
            lines.append("")
        
        # 统计表格
        lines.append("## 性能统计")
        lines.append("")
        
        successful = len([r for r in report_data if 'error' not in r])
        total_signals = sum(r.get('signal_count', 0) for r in report_data)
        total_time = sum(r.get('execution_time', 0) for r in report_data)
        
        lines.append("| 指标 | 值 |")
        lines.append("|------|-----|")
        lines.append(f"| 成功策略 | {successful}/{len(report_data)} |")
        lines.append(f"| 总信号数 | {total_signals} |")
        lines.append(f"| 总执行时间 | {total_time:.3f}秒 |")
        lines.append(f"| 平均执行时间 | {total_time/len(report_data):.3f}秒 |")
        lines.append("")
        
        return "\n".join(lines)
    
    def _generate_html_report(self, report_data: List[Dict]) -> str:
        """生成HTML报告"""
        # 简化的HTML报告
        markdown_report = self._generate_markdown_report(report_data)
        
        # 转换为基本HTML
        import markdown
        html = markdown.markdown(markdown_report)
        
        # 包装完整HTML
        full_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>策略执行报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            {html}
        </body>
        </html>
        """
        
        return full_html
    
    def print_registered_strategies(self):
        """打印已注册的策略"""
        print(f"\n{'='*60}")
        print(f"已注册策略 ({len(self.strategies)} 个)")
        print(f"{'='*60}")
        
        for i, (name, strategy_class) in enumerate(self.strategies.items(), 1):
            config = self.strategy_configs.get(name, {})
            description = config.get('description', '无描述')
            
            print(f"{i}. {name}")
            print(f"   类: {strategy_class.__name__}")
            print(f"   描述: {description}")
            print(f"   默认参数: {len(config)}个")
            
            if i < len(self.strategies):
                print()
    
    def print_execution_results(self):
        """打印执行结果摘要"""
        print(f"\n{'='*60}")
        print(f"执行结果摘要 ({len(self.execution_results)} 个实例)")
        print(f"{'='*60}")
        
        for i, (instance_name, result) in enumerate(self.execution_results.items(), 1):
            strategy_name = result.get('strategy_name', 'Unknown')
            signal_count = result.get('signal_count', 0)
            execution_time = result.get('execution_time', 0)
            status = '成功' if 'error' not in result else '失败'
            
            print(f"{i}. {instance_name} ({strategy_name})")
            print(f"   状态: {status}")
            print(f"   信号: {signal_count}个")
            print(f"   时间: {execution_time:.3f}秒")
            
            if i < len(self.execution_results):
                print()


# ========== 测试代码 ==========

if __name__ == "__main__":
    print("测试策略管理器...")
    
    # 生成示例数据
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    # 创建策略管理器
    manager = StrategyManager(
        name="TestManager",
        config_dir="./test_configs",
        results_dir="./test_results"
    )
    
    # 创建测试策略类
    class TestStrategy1(UnifiedStrategyBase):
        def get_default_params(self):
            return {'window': 10, 'threshold': 0.5}
        
        def generate_signals(self):
            return [{
                'timestamp': self.data.index[i],
                'action': 'buy' if i % 3 == 0 else 'sell',
                'price': self.data['close'].iloc[i],
                'confidence': 0.7
            } for i in range(0, len(self.data), 10)]
    
    class TestStrategy2(UnifiedStrategyBase):
        def get_default_params(self):
            return {'period': 20, 'sensitivity': 1.0}
        
        def generate_signals(self):
            return [{
                'timestamp': self.data.index[i],
                'action': 'buy',
                'price': self.data['close'].iloc[i],
                'confidence': 0.8
            } for i in range(5, len(self.data), 15)]
    
    # 注册策略
    manager.register_strategy(
        name="Strategy1",
        strategy_class=TestStrategy1,
        default_config={'window': 10, 'description': '测试策略1'},
        description="第一个测试策略"
    )
    
    manager.register_strategy(
        name="Strategy2", 
        strategy_class=TestStrategy2,
        default_config={'period': 20, 'description': '测试策略2'},
        description="第二个测试策略"
    )
    
    # 打印已注册策略
    manager.print_registered_strategies()
    
    # 运行单个策略
    print("\n1. 运行单个策略:")
    result1 = manager.run_strategy(
        strategy_name="Strategy1",
        data=data,
        config={'window': 5},  # 覆盖默认配置
        save_results=True
    )
    
    # 运行另一个策略
    result2 = manager.run_strategy(
        strategy_name="Strategy2",
        data=data,
        save_results=True
    )
    
    # 批量运行策略
    print("\n2. 批量运行策略:")
    results = manager.run_strategies(
        strategy_names=["Strategy1", "Strategy2"],
        data=data,
        configs={
            "Strategy1": {'window': 8},
            "Strategy2": {'period': 15}
        },
        save_results=True
    )
    
    # 打印执行结果
    manager.print_execution_results()
    
    # 比较策略性能
    print("\n3. 策略性能比较:")
    manager.compare_strategies()
    
    # 生成报告
    print("\n4. 生成报告:")
    report = manager.generate_report(report_format='text')
    print(report)
    
    # 保存报告
    report_file = "./test_results/test_report.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(manager.generate_report(report_format='markdown'))
    
    print(f"\n报告已保存: {report_file}")
    
    print("\n✅ 策略管理器测试完成")