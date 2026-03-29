#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格行为分析集成 - 将quant_trade-main中的price_action_analysis.py集成到统一策略框架

功能:
1. 导入原始的SignalDefinition和具体信号类
2. 创建适配器将信号定义包装为统一策略
3. 提供预定义的信号策略
4. 支持信号组合和参数配置
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import warnings
warnings.filterwarnings('ignore')

# 添加原始项目路径
original_project_path = "/Users/chengming/downloads/quant_trade-main"
csv_version_path = os.path.join(original_project_path, "csv_version")

# 尝试从原始文件导入
try:
    # 将原始文件目录添加到路径
    sys.path.append(csv_version_path)
    
    # 动态导入 - 避免直接导入可能的问题
    import importlib.util
    
    # 加载原始模块
    spec = importlib.util.spec_from_file_location(
        "price_action_analysis", 
        os.path.join(csv_version_path, "price_action_analysis.py")
    )
    
    if spec and spec.loader:
        price_action_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(price_action_module)
        
        # 提取需要的类
        SignalDefinition = price_action_module.SignalDefinition
        MACDDivergenceSignal = price_action_module.MACDDivergenceSignal
        BreakoutSignal = getattr(price_action_module, 'BreakoutSignal', None)
        SignalAnalysisEngine = getattr(price_action_module, 'SignalAnalysisEngine', None)
        SignalEvaluator = getattr(price_action_module, 'SignalEvaluator', None)
        SignalStatistics = getattr(price_action_module, 'SignalStatistics', None)
        
        PRICE_ACTION_ANALYSIS_AVAILABLE = True
        print("✅ 成功导入price_action_analysis.py模块")
    else:
        raise ImportError("无法加载price_action_analysis模块")
        
except Exception as e:
    print(f"⚠️ 无法导入原始price_action_analysis.py: {e}")
    print("将使用简化实现")
    PRICE_ACTION_ANALYSIS_AVAILABLE = False
    
    # 定义简化版本
    class SignalDefinition:
        def generate_signals(self, df_window):
            return []
        def get_signal_name(self):
            return "SimplifiedSignal"
    
    class MACDDivergenceSignal(SignalDefinition):
        def __init__(self, **kwargs):
            pass
    
    class BreakoutSignal(SignalDefinition):
        def __init__(self, **kwargs):
            pass
    
    SignalAnalysisEngine = None
    SignalEvaluator = None
    SignalStatistics = None

# 导入统一策略框架
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.unified_strategy_base import UnifiedStrategyBase
from adapters.signal_definition_adapter import SignalDefinitionAdapter, MultiSignalDefinitionAdapter


class PriceActionSignalStrategy(UnifiedStrategyBase):
    """
    价格行为信号策略 - 基于SignalDefinition的统一策略实现
    
    提供对price_action_analysis.py中信号定义的直接访问
    """
    
    def __init__(self, 
                 data: pd.DataFrame,
                 params: Dict[str, Any],
                 strategy_name: Optional[str] = None):
        """
        初始化价格行为信号策略
        
        参数:
            data: 交易数据
            params: 策略参数，包含signal_definition配置
            strategy_name: 策略名称
        """
        # 存储信号定义
        self.signal_definition = None
        
        # 调用父类初始化
        super().__init__(data, params, strategy_name)
        
        # 创建信号定义实例
        self._create_signal_definition()
    
    def get_default_params(self) -> Dict[str, Any]:
        """获取默认参数"""
        return {
            'signal_type': 'MACDDivergence',  # MACDDivergence, Breakout, 或 custom
            'signal_params': {},  # 信号特定参数
            'window_size': 100,
            'step': 20,
            'min_window_size': 50,
            'enabled': True,
            'version': '1.0.0',
            'description': '价格行为信号策略'
        }
    
    def _create_signal_definition(self):
        """根据配置创建信号定义实例"""
        signal_type = self.params['signal_type']
        signal_params = self.params['signal_params']
        
        try:
            if signal_type == 'MACDDivergence':
                self.signal_definition = MACDDivergenceSignal(**signal_params)
                print(f"创建MACD背离信号定义: {self.signal_definition.get_signal_name()}")
                
            elif signal_type == 'Breakout' and BreakoutSignal:
                self.signal_definition = BreakoutSignal(**signal_params)
                print(f"创建突破信号定义: {self.signal_definition.get_signal_name()}")
                
            elif signal_type == 'custom':
                # 自定义信号定义
                if 'signal_class' in signal_params:
                    # 动态创建自定义信号类
                    signal_class = signal_params['signal_class']
                    if isinstance(signal_class, type) and issubclass(signal_class, SignalDefinition):
                        custom_params = {k: v for k, v in signal_params.items() if k != 'signal_class'}
                        self.signal_definition = signal_class(**custom_params)
                        print(f"创建自定义信号定义: {self.signal_definition.get_signal_name()}")
                    else:
                        raise ValueError("自定义信号类必须是SignalDefinition的子类")
                else:
                    raise ValueError("自定义信号类型需要提供signal_class参数")
                    
            else:
                raise ValueError(f"不支持的信号类型: {signal_type}")
                
        except Exception as e:
            print(f"创建信号定义失败: {e}")
            print("使用简化信号定义")
            self.signal_definition = SignalDefinition()
    
    def generate_signals(self) -> List[Dict]:
        """生成价格行为信号"""
        if not self.signal_definition:
            print("警告: 没有可用的信号定义")
            return []
        
        print(f"生成价格行为信号: {self.signal_definition.get_signal_name()}")
        
        # 使用SignalDefinitionAdapter处理窗口分割
        adapter = SignalDefinitionAdapter(
            data=self.data,
            params={
                'window_size': self.params['window_size'],
                'step': self.params['step'],
                'min_window_size': self.params['min_window_size']
            },
            signal_definition=self.signal_definition,
            strategy_name=f"{self.strategy_name}_Adapter"
        )
        
        # 生成信号
        signals = adapter.generate_standard_signals()
        
        # 添加信号定义信息
        for signal in signals:
            signal['signal_definition'] = self.signal_definition.get_signal_name()
            signal['signal_type'] = self.params['signal_type']
        
        print(f"生成 {len(signals)} 个价格行为信号")
        return signals
    
    def analyze_signal_performance(self) -> Dict[str, Any]:
        """分析信号性能"""
        signals = self.standard_signals
        
        if not signals:
            return {'error': '没有信号可分析'}
        
        # 按信号类型分组
        signal_types = {}
        for signal in signals:
            sig_type = signal.get('type', 'unknown')
            if sig_type not in signal_types:
                signal_types[sig_type] = []
            signal_types[sig_type].append(signal)
        
        # 计算性能指标
        performance = {
            'total_signals': len(signals),
            'signal_types': len(signal_types),
            'signal_type_distribution': {k: len(v) for k, v in signal_types.items()},
            'avg_confidence': np.mean([s.get('confidence', 0.5) for s in signals]) if signals else 0,
            'signal_definition': self.signal_definition.get_signal_name() if self.signal_definition else 'unknown'
        }
        
        # 添加特定信号类型的分析
        for sig_type, type_signals in signal_types.items():
            if len(type_signals) >= 3:  # 只有足够多的信号才分析
                confidences = [s.get('confidence', 0.5) for s in type_signals]
                performance[f'{sig_type}_count'] = len(type_signals)
                performance[f'{sig_type}_avg_confidence'] = np.mean(confidences)
        
        # 添加到性能指标
        self.performance_metrics.update({
            'price_action_analysis': performance,
            'signal_definition_name': self.signal_definition.get_signal_name() if self.signal_definition else 'unknown'
        })
        
        return performance
    
    def print_signal_analysis(self):
        """打印信号分析"""
        print(f"\n{'='*60}")
        print(f"价格行为信号分析: {self.strategy_name}")
        print(f"{'='*60}")
        
        analysis = self.analyze_signal_performance()
        
        if 'error' in analysis:
            print(f"错误: {analysis['error']}")
            return
        
        print(f"\n📊 信号统计:")
        print(f"  总信号数: {analysis['total_signals']}")
        print(f"  信号类型数: {analysis['signal_types']}")
        print(f"  平均置信度: {analysis['avg_confidence']:.3f}")
        
        print(f"\n📈 信号类型分布:")
        for sig_type, count in analysis['signal_type_distribution'].items():
            percentage = count / analysis['total_signals'] * 100
            print(f"  {sig_type}: {count}个 ({percentage:.1f}%)")
        
        print(f"\n⚙️ 策略配置:")
        print(f"  信号类型: {self.params['signal_type']}")
        print(f"  信号定义: {analysis['signal_definition']}")
        print(f"  窗口大小: {self.params['window_size']}")
        print(f"  步长: {self.params['step']}")
        
        print(f"\n{'='*60}")


class MultiPriceActionStrategy(UnifiedStrategyBase):
    """
    多价格行为策略 - 组合多个信号定义
    
    功能:
    1. 同时运行多个信号定义
    2. 信号合并和冲突解决
    3. 加权信号投票
    """
    
    def __init__(self, 
                 data: pd.DataFrame,
                 params: Dict[str, Any],
                 strategy_name: Optional[str] = None):
        """
        初始化多价格行为策略
        
        参数:
            data: 交易数据
            params: 策略参数，包含signal_definitions配置
            strategy_name: 策略名称
        """
        # 存储信号定义列表
        self.signal_definitions = []
        
        # 调用父类初始化
        super().__init__(data, params, strategy_name)
        
        # 创建信号定义列表
        self._create_signal_definitions()
    
    def get_default_params(self) -> Dict[str, Any]:
        """获取默认参数"""
        return {
            'signal_definitions': [
                {
                    'type': 'MACDDivergence',
                    'params': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}
                }
            ],
            'combination_method': 'voting',  # voting, weighted, sequential
            'weights': None,  # 加权方法的权重
            'window_size': 100,
            'step': 20,
            'min_window_size': 50,
            'enabled': True,
            'version': '1.0.0',
            'description': '多价格行为信号策略'
        }
    
    def _create_signal_definitions(self):
        """根据配置创建信号定义列表"""
        signal_configs = self.params['signal_definitions']
        
        for i, config in enumerate(signal_configs):
            try:
                signal_type = config['type']
                signal_params = config.get('params', {})
                
                if signal_type == 'MACDDivergence':
                    signal_def = MACDDivergenceSignal(**signal_params)
                    self.signal_definitions.append(signal_def)
                    print(f"添加MACD背离信号定义 {i+1}: {signal_def.get_signal_name()}")
                    
                elif signal_type == 'Breakout' and BreakoutSignal:
                    signal_def = BreakoutSignal(**signal_params)
                    self.signal_definitions.append(signal_def)
                    print(f"添加突破信号定义 {i+1}: {signal_def.get_signal_name()}")
                    
                else:
                    print(f"警告: 不支持的信号类型: {signal_type}，跳过")
                    
            except Exception as e:
                print(f"创建信号定义 {i+1} 失败: {e}")
        
        if not self.signal_definitions:
            print("警告: 没有创建任何信号定义")
            self.signal_definitions.append(SignalDefinition())
    
    def generate_signals(self) -> List[Dict]:
        """生成多信号组合"""
        if not self.signal_definitions:
            print("警告: 没有可用的信号定义")
            return []
        
        print(f"生成多价格行为信号 ({len(self.signal_definitions)} 个信号定义)")
        
        # 使用MultiSignalDefinitionAdapter
        adapter = MultiSignalDefinitionAdapter(
            data=self.data,
            params={
                'window_size': self.params['window_size'],
                'step': self.params['step'],
                'min_window_size': self.params['min_window_size']
            },
            signal_definitions=self.signal_definitions,
            strategy_name=f"{self.strategy_name}_MultiAdapter"
        )
        
        # 生成信号
        signals = adapter.generate_standard_signals()
        
        # 应用组合方法
        if self.params['combination_method'] == 'weighted' and self.params['weights']:
            signals = self._apply_weighted_combination(signals)
        elif self.params['combination_method'] == 'sequential':
            signals = self._apply_sequential_combination(signals)
        
        print(f"生成 {len(signals)} 个组合信号")
        return signals
    
    def _apply_weighted_combination(self, signals: List[Dict]) -> List[Dict]:
        """应用加权组合"""
        weights = self.params['weights']
        
        if not weights or len(weights) != len(self.signal_definitions):
            print("警告: 权重配置无效，使用默认投票方法")
            return signals
        
        # 简单的加权实现
        for signal in signals:
            source_idx = signal.get('source_index', 0)
            if source_idx < len(weights):
                weight = weights[source_idx]
                signal['confidence'] = signal.get('confidence', 0.5) * weight
        
        return signals
    
    def _apply_sequential_combination(self, signals: List[Dict]) -> List[Dict]:
        """应用顺序组合（按时间顺序，避免冲突）"""
        if not signals:
            return []
        
        # 按时间排序
        signals.sort(key=lambda x: x.get('timestamp', pd.Timestamp.min))
        
        # 简单的顺序过滤：避免相同时间点的多个信号
        filtered_signals = []
        last_time = None
        
        for signal in signals:
            current_time = signal.get('timestamp')
            
            if last_time is None or current_time != last_time:
                filtered_signals.append(signal)
                last_time = current_time
        
        print(f"顺序组合: {len(signals)} -> {len(filtered_signals)} 个信号")
        return filtered_signals
    
    def print_multi_signal_analysis(self):
        """打印多信号分析"""
        print(f"\n{'='*60}")
        print(f"多价格行为信号分析: {self.strategy_name}")
        print(f"{'='*60}")
        
        signals = self.standard_signals
        
        if not signals:
            print("没有信号可分析")
            return
        
        # 统计信号来源
        source_stats = {}
        for signal in signals:
            source = signal.get('source_adapter', 'unknown')
            if source not in source_stats:
                source_stats[source] = 0
            source_stats[source] += 1
        
        print(f"\n📊 信号统计:")
        print(f"  总信号数: {len(signals)}")
        print(f"  信号来源数: {len(source_stats)}")
        
        print(f"\n📈 信号来源分布:")
        for source, count in source_stats.items():
            percentage = count / len(signals) * 100
            print(f"  {source}: {count}个 ({percentage:.1f}%)")
        
        print(f"\n⚙️ 策略配置:")
        print(f"  信号定义数: {len(self.signal_definitions)}")
        print(f"  组合方法: {self.params['combination_method']}")
        print(f"  窗口大小: {self.params['window_size']}")
        
        # 显示信号定义信息
        print(f"\n🔧 信号定义列表:")
        for i, signal_def in enumerate(self.signal_definitions):
            print(f"  {i+1}. {signal_def.get_signal_name()}")
        
        print(f"\n{'='*60}")


# ========== 预定义策略工厂 ==========

class PriceActionStrategyFactory:
    """
    价格行为策略工厂 - 创建预定义的价格行为策略
    """
    
    @staticmethod
    def create_macd_divergence_strategy(data: pd.DataFrame, 
                                       fast_period: int = 12,
                                       slow_period: int = 26,
                                       signal_period: int = 9,
                                       delay_bars: int = 2,
                                       strategy_name: Optional[str] = None) -> PriceActionSignalStrategy:
        """创建MACD背离策略"""
        strategy_name = strategy_name or f"MACD_Divergence_{fast_period}_{slow_period}"
        
        return PriceActionSignalStrategy(
            data=data,
            params={
                'signal_type': 'MACDDivergence',
                'signal_params': {
                    'fast_period': fast_period,
                    'slow_period': slow_period,
                    'signal_period': signal_period,
                    'delay_bars': delay_bars
                },
                'window_size': 100,
                'step': 20,
                'description': f'MACD背离策略 (快线{fast_period}, 慢线{slow_period}, 信号{signal_period})'
            },
            strategy_name=strategy_name
        )
    
    @staticmethod
    def create_breakout_strategy(data: pd.DataFrame,
                                lookback_period: int = 20,
                                volatility_threshold: float = 1.5,
                                strategy_name: Optional[str] = None) -> Optional[PriceActionSignalStrategy]:
        """创建突破策略"""
        if not BreakoutSignal:
            print("警告: BreakoutSignal不可用")
            return None
        
        strategy_name = strategy_name or f"Breakout_{lookback_period}"
        
        return PriceActionSignalStrategy(
            data=data,
            params={
                'signal_type': 'Breakout',
                'signal_params': {
                    'lookback_period': lookback_period,
                    'volatility_threshold': volatility_threshold
                },
                'window_size': 100,
                'step': 20,
                'description': f'突破策略 (回顾{lookback_period}期, 波动阈值{volatility_threshold})'
            },
            strategy_name=strategy_name
        )
    
    @staticmethod
    def create_composite_strategy(data: pd.DataFrame,
                                 strategy_name: Optional[str] = None) -> MultiPriceActionStrategy:
        """创建复合策略（MACD背离 + 突破）"""
        strategy_name = strategy_name or "PriceAction_Composite"
        
        return MultiPriceActionStrategy(
            data=data,
            params={
                'signal_definitions': [
                    {
                        'type': 'MACDDivergence',
                        'params': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}
                    },
                    {
                        'type': 'Breakout',
                        'params': {'lookback_period': 20, 'volatility_threshold': 1.5}
                    } if BreakoutSignal else {
                        'type': 'MACDDivergence',
                        'params': {'fast_period': 6, 'slow_period': 13, 'signal_period': 5}
                    }
                ],
                'combination_method': 'voting',
                'window_size': 100,
                'step': 20,
                'description': '复合价格行为策略 (MACD背离 + 突破)'
            },
            strategy_name=strategy_name
        )


# ========== 注册函数 ==========

def register_price_action_strategies(manager):
    """
    注册价格行为策略到策略管理器
    
    参数:
        manager: StrategyManager实例
    """
    # 注册基础信号策略
    manager.register_strategy(
        name="PriceActionSignal",
        strategy_class=PriceActionSignalStrategy,
        default_config={
            'signal_type': 'MACDDivergence',
            'signal_params': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9},
            'window_size': 100,
            'step': 20,
            'description': '基础价格行为信号策略'
        },
        description="基于SignalDefinition的价格行为信号策略"
    )
    
    # 注册多信号策略
    manager.register_strategy(
        name="MultiPriceAction",
        strategy_class=MultiPriceActionStrategy,
        default_config={
            'signal_definitions': [
                {'type': 'MACDDivergence', 'params': {'fast_period': 12, 'slow_period': 26, 'signal_period': 9}}
            ],
            'combination_method': 'voting',
            'window_size': 100,
            'step': 20,
            'description': '多价格行为信号策略'
        },
        description="组合多个价格行为信号的策略"
    )
    
    # 注册预定义策略
    print(f"注册了 2 个价格行为策略")
    
    # 显示可用信号类型
    print(f"可用信号类型: MACDDivergence" + (", Breakout" if BreakoutSignal else ""))


# ========== 测试代码 ==========

if __name__ == "__main__":
    print("测试价格行为分析集成...")
    
    # 生成示例数据
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(200).cumsum() + 100,
        'high': np.random.randn(200).cumsum() + 105,
        'low': np.random.randn(200).cumsum() + 95,
        'close': np.random.randn(200).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 200),
        'symbol': 'TEST'
    }, index=dates)
    
    print(f"\n1. 测试MACD背离策略:")
    
    macd_strategy = PriceActionStrategyFactory.create_macd_divergence_strategy(
        data=data,
        fast_period=12,
        slow_period=26,
        signal_period=9,
        strategy_name="MACD_Test"
    )
    
    signals = macd_strategy.generate_standard_signals()
    print(f"生成 {len(signals)} 个MACD背离信号")
    
    macd_strategy.print_summary()
    macd_strategy.print_signal_analysis()
    
    print(f"\n2. 测试多信号策略:")
    
    multi_strategy = PriceActionStrategyFactory.create_composite_strategy(
        data=data,
        strategy_name="Composite_Test"
    )
    
    multi_signals = multi_strategy.generate_standard_signals()
    print(f"生成 {len(multi_signals)} 个复合信号")
    
    multi_strategy.print_multi_signal_analysis()
    
    print(f"\n3. 测试策略管理器集成:")
    
    from managers.strategy_manager import StrategyManager
    
    manager = StrategyManager(
        name="PriceActionTestManager",
        config_dir="./test_pa_configs",
        results_dir="./test_pa_results"
    )
    
    register_price_action_strategies(manager)
    
    # 运行策略
    result = manager.run_strategy(
        strategy_name="PriceActionSignal",
        data=data,
        config={
            'signal_type': 'MACDDivergence',
            'signal_params': {'fast_period': 6, 'slow_period': 13, 'signal_period': 5}
        },
        save_results=True
    )
    
    print(f"\n✅ 价格行为分析集成测试完成")