#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SignalDefinition适配器 - 将price_action_analysis.py中的SignalDefinition适配到统一策略接口

功能:
1. 将SignalDefinition包装为UnifiedStrategyBase子类
2. 处理窗口分割和信号聚合
3. 转换信号格式为标准格式
4. 支持多个SignalDefinition组合
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# 导入统一策略基类
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.unified_strategy_base import UnifiedStrategyBase


class SignalDefinitionAdapter(UnifiedStrategyBase):
    """
    SignalDefinition适配器 - 将SignalDefinition转换为统一策略接口
    
    设计说明:
    1. SignalDefinition的generate_signals方法接受df_window参数
    2. 我们需要将整个数据分割为重叠窗口
    3. 聚合所有窗口的信号
    4. 转换信号格式为标准格式
    """
    
    def __init__(self, 
                 data: pd.DataFrame,
                 params: Dict[str, Any],
                 signal_definition,
                 strategy_name: Optional[str] = None):
        """
        初始化适配器
        
        参数:
            data: 交易数据
            params: 策略参数
            signal_definition: SignalDefinition实例
            strategy_name: 策略名称
        """
        self.signal_definition = signal_definition
        
        # 调用父类初始化
        super().__init__(data, params, strategy_name)
        
        # SignalDefinition特定参数
        self.window_size = self.params.get('window_size', 100)
        self.step = self.params.get('step', 10)
        self.min_window_size = self.params.get('min_window_size', 50)
        
        # 信号缓存
        self.window_signals = {}  # 窗口编号 -> 信号列表
    
    def get_default_params(self) -> Dict[str, Any]:
        """获取默认参数"""
        return {
            'window_size': 100,
            'step': 10,
            'min_window_size': 50,
            'signal_definition_name': getattr(self.signal_definition, 'get_signal_name', lambda: 'Unknown')(),
            'enabled': True,
            'version': '1.0.0',
            'description': f"SignalDefinition适配器: {getattr(self.signal_definition, 'get_signal_name', lambda: 'Unknown')()}"
        }
    
    def _split_into_windows(self) -> List[Tuple[int, int, pd.DataFrame]]:
        """
        将数据分割为重叠窗口
        
        返回:
            窗口列表，每个元素为(start_idx, end_idx, window_data)
        """
        windows = []
        n = len(self.data)
        
        if n < self.min_window_size:
            print(f"警告: 数据长度({n})小于最小窗口大小({self.min_window_size})")
            return windows
        
        start = 0
        window_count = 0
        
        while start + self.window_size <= n:
            end = start + self.window_size
            window_data = self.data.iloc[start:end].copy()
            
            windows.append((start, end, window_data))
            
            start += self.step
            window_count += 1
        
        print(f"将数据分割为 {window_count} 个窗口 (窗口大小: {self.window_size}, 步长: {self.step})")
        return windows
    
    def _process_window(self, window_idx: int, start: int, end: int, window_data: pd.DataFrame) -> List[Dict]:
        """
        处理单个窗口，生成信号
        
        返回:
            该窗口的信号列表（已转换为标准格式）
        """
        try:
            # 调用SignalDefinition生成信号
            raw_signals = self.signal_definition.generate_signals(window_data)
            
            if not raw_signals:
                return []
            
            # 转换信号格式并调整索引
            converted_signals = []
            for signal in raw_signals:
                # 调整索引为全局索引
                if 'idx' in signal:
                    global_idx = start + signal['idx']
                    signal['global_idx'] = global_idx
                    signal['timestamp'] = self.data.index[global_idx] if global_idx < len(self.data) else None
                elif 'absolute_idx' in signal:
                    # 如果信号包含绝对索引，直接使用
                    pass
                
                # 确保有timestamp
                if 'timestamp' not in signal and 'idx' in signal:
                    idx = signal.get('global_idx', signal.get('idx'))
                    if idx is not None and idx < len(self.data.index):
                        signal['timestamp'] = self.data.index[idx]
                
                # 添加窗口信息
                signal['window_info'] = {
                    'window_idx': window_idx,
                    'window_start': start,
                    'window_end': end - 1,
                    'window_size': self.window_size
                }
                
                # 添加信号定义信息
                signal['signal_definition'] = getattr(self.signal_definition, 'get_signal_name', lambda: 'Unknown')()
                
                converted_signals.append(signal)
            
            return converted_signals
            
        except Exception as e:
            print(f"窗口 {window_idx} ({start}-{end}) 处理失败: {e}")
            return []
    
    def generate_signals(self) -> List[Dict]:
        """
        生成交易信号 - 核心适配逻辑
        
        步骤:
        1. 将数据分割为重叠窗口
        2. 对每个窗口调用SignalDefinition.generate_signals()
        3. 聚合所有窗口的信号
        4. 去重和排序
        """
        print(f"开始生成信号 (适配器: {self.strategy_name})...")
        
        # 分割窗口
        windows = self._split_into_windows()
        if not windows:
            print("警告: 无法分割窗口，数据可能不足")
            return []
        
        # 处理所有窗口
        all_signals = []
        window_count = len(windows)
        
        for window_idx, (start, end, window_data) in enumerate(windows):
            # 显示进度
            if window_idx % 10 == 0 or window_idx == window_count - 1:
                print(f"  处理窗口 {window_idx+1}/{window_count} ({start}-{end})")
            
            # 处理当前窗口
            window_signals = self._process_window(window_idx, start, end, window_data)
            self.window_signals[window_idx] = window_signals
            
            # 添加到总信号列表
            all_signals.extend(window_signals)
        
        print(f"生成 {len(all_signals)} 个原始信号")
        
        # 去重（基于timestamp和类型）
        unique_signals = self._deduplicate_signals(all_signals)
        print(f"去重后剩余 {len(unique_signals)} 个信号")
        
        # 按时间排序
        sorted_signals = sorted(unique_signals, key=lambda x: x.get('timestamp', datetime.min))
        
        # 转换为标准格式（基类会进一步标准化）
        formatted_signals = []
        for signal in sorted_signals:
            formatted = self._format_signal_for_base(signal)
            if formatted:
                formatted_signals.append(formatted)
        
        print(f"最终生成 {len(formatted_signals)} 个格式化信号")
        return formatted_signals
    
    def _deduplicate_signals(self, signals: List[Dict]) -> List[Dict]:
        """去除重复信号"""
        if not signals:
            return []
        
        # 使用(timestamp, signal_type)作为去重键
        seen = set()
        unique_signals = []
        
        for signal in signals:
            timestamp = signal.get('timestamp')
            signal_type = signal.get('type', 'unknown')
            
            if timestamp is None:
                # 如果没有timestamp，无法去重，直接添加
                unique_signals.append(signal)
                continue
            
            key = (timestamp, signal_type)
            if key not in seen:
                seen.add(key)
                unique_signals.append(signal)
        
        return unique_signals
    
    def _format_signal_for_base(self, signal: Dict) -> Dict:
        """
        将SignalDefinition信号格式转换为基类期望的格式
        
        SignalDefinition信号格式:
        {
            'type': 'top_divergence'/'bottom_divergence'/'breakout'等,
            'idx': 信号索引,
            'price': 信号价格,
            'features': {...}  # 特征字典
        }
        
        转换为:
        {
            'timestamp': 信号时间,
            'action': 'buy'/'sell',
            'price': 信号价格,
            'type': 信号类型,
            'features': 特征字典,
            'confidence': 置信度
        }
        """
        # 确定action类型
        signal_type = signal.get('type', 'unknown')
        action = self._map_signal_type_to_action(signal_type)
        
        # 获取timestamp
        timestamp = signal.get('timestamp')
        if timestamp is None and 'idx' in signal:
            idx = signal['idx']
            if idx < len(self.data.index):
                timestamp = self.data.index[idx]
        
        # 获取price
        price = signal.get('price', 0.0)
        if price == 0.0 and timestamp is not None:
            # 尝试从数据中获取价格
            try:
                price = self.data.loc[timestamp, 'close']
            except:
                pass
        
        # 计算置信度
        confidence = self._calculate_confidence(signal)
        
        # 构建格式化信号
        formatted = {
            'timestamp': timestamp,
            'action': action,
            'price': price,
            'type': signal_type,
            'features': signal.get('features', {}),
            'confidence': confidence,
            'original_signal': signal  # 保留原始信号
        }
        
        # 添加额外信息
        if 'symbol' in self.data.columns and not self.data.empty:
            formatted['symbol'] = self.data['symbol'].iloc[0]
        
        # 添加窗口信息
        if 'window_info' in signal:
            formatted['window_info'] = signal['window_info']
        
        return formatted
    
    def _map_signal_type_to_action(self, signal_type: str) -> str:
        """将信号类型映射到交易动作"""
        # 根据常见信号类型映射
        action_map = {
            # 买入信号
            'bottom_divergence': 'buy',
            'breakout_up': 'buy',
            'golden_cross': 'buy',
            'support_bounce': 'buy',
            
            # 卖出信号
            'top_divergence': 'sell',
            'breakout_down': 'sell',
            'death_cross': 'sell',
            'resistance_rejection': 'sell',
            
            # 默认
            'unknown': 'hold'
        }
        
        # 尝试匹配信号类型（包含子字符串）
        for key, action in action_map.items():
            if key in signal_type.lower():
                return action
        
        # 根据信号类型的关键词判断
        if any(word in signal_type.lower() for word in ['bottom', 'up', 'bull', 'buy', 'long']):
            return 'buy'
        elif any(word in signal_type.lower() for word in ['top', 'down', 'bear', 'sell', 'short']):
            return 'sell'
        
        return 'hold'
    
    def _calculate_confidence(self, signal: Dict) -> float:
        """计算信号置信度"""
        confidence = 0.5  # 默认置信度
        
        # 从特征中提取置信度
        features = signal.get('features', {})
        
        # 尝试获取strength特征
        if 'strength' in features:
            strength = features['strength']
            # 归一化到0-1范围
            if isinstance(strength, (int, float)):
                # 假设strength在0-10范围内
                confidence = min(max(strength / 10.0, 0.0), 1.0)
        
        # 尝试从其他特征推断
        elif 'delay_bars' in features:
            # 延迟确认的条数越少，置信度越高
            delay = features['delay_bars']
            if isinstance(delay, (int, float)):
                confidence = max(0.7 - (delay / 20.0), 0.3)
        
        return round(confidence, 2)
    
    def get_window_statistics(self) -> Dict[str, Any]:
        """获取窗口处理统计信息"""
        total_windows = len(self.window_signals)
        windows_with_signals = sum(1 for signals in self.window_signals.values() if signals)
        
        # 统计每个窗口的信号数量
        signal_counts = [len(signals) for signals in self.window_signals.values()]
        
        stats = {
            'total_windows': total_windows,
            'windows_with_signals': windows_with_signals,
            'windows_without_signals': total_windows - windows_with_signals,
            'total_signals': sum(signal_counts),
            'avg_signals_per_window': np.mean(signal_counts) if signal_counts else 0,
            'max_signals_in_window': max(signal_counts) if signal_counts else 0,
            'min_signals_in_window': min(signal_counts) if signal_counts else 0,
            'window_size': self.window_size,
            'step': self.step,
            'signal_definition': getattr(self.signal_definition, 'get_signal_name', lambda: 'Unknown')()
        }
        
        return stats
    
    def print_window_statistics(self):
        """打印窗口处理统计"""
        stats = self.get_window_statistics()
        
        print(f"\n{'='*60}")
        print(f"窗口处理统计: {self.strategy_name}")
        print(f"{'='*60}")
        
        print(f"\n📊 窗口统计:")
        print(f"  总窗口数: {stats['total_windows']}")
        print(f"  有信号的窗口: {stats['windows_with_signals']} ({stats['windows_with_signals']/stats['total_windows']*100:.1f}%)")
        print(f"  无信号的窗口: {stats['windows_without_signals']}")
        
        print(f"\n📈 信号统计:")
        print(f"  总信号数: {stats['total_signals']}")
        print(f"  平均每窗口: {stats['avg_signals_per_window']:.2f}")
        print(f"  最大每窗口: {stats['max_signals_in_window']}")
        print(f"  最小每窗口: {stats['min_signals_in_window']}")
        
        print(f"\n⚙️ 处理参数:")
        print(f"  窗口大小: {stats['window_size']}")
        print(f"  步长: {stats['step']}")
        print(f"  信号定义: {stats['signal_definition']}")
        
        print(f"\n{'='*60}")


# ========== 多信号定义适配器 ==========

class MultiSignalDefinitionAdapter(UnifiedStrategyBase):
    """
    多信号定义适配器 - 组合多个SignalDefinition
    
    功能:
    1. 支持多个SignalDefinition同时运行
    2. 信号合并和冲突解决
    3. 加权信号投票机制
    """
    
    def __init__(self, 
                 data: pd.DataFrame,
                 params: Dict[str, Any],
                 signal_definitions: List,
                 strategy_name: Optional[str] = None):
        """
        初始化多信号适配器
        
        参数:
            data: 交易数据
            params: 策略参数
            signal_definitions: SignalDefinition实例列表
            strategy_name: 策略名称
        """
        self.signal_definitions = signal_definitions
        
        # 调用父类初始化
        super().__init__(data, params, strategy_name)
        
        # 初始化单个适配器
        self.adapters = []
        for i, signal_def in enumerate(signal_definitions):
            adapter_name = f"{strategy_name}_{i}" if strategy_name else f"Adapter_{i}"
            adapter_params = {
                **self.params,
                'signal_definition_name': getattr(signal_def, 'get_signal_name', lambda: f'Signal_{i}')()
            }
            
            adapter = SignalDefinitionAdapter(
                data=data,
                params=adapter_params,
                signal_definition=signal_def,
                strategy_name=adapter_name
            )
            self.adapters.append(adapter)
    
    def generate_signals(self) -> List[Dict]:
        """生成组合信号"""
        all_signals = []
        
        print(f"开始生成组合信号 ({len(self.adapters)} 个信号定义)...")
        
        # 运行所有适配器
        for i, adapter in enumerate(self.adapters):
            print(f"\n运行适配器 {i+1}/{len(self.adapters)}: {adapter.strategy_name}")
            
            try:
                signals = adapter.generate_standard_signals()
                print(f"  生成 {len(signals)} 个信号")
                
                # 标记信号来源
                for signal in signals:
                    signal['source_adapter'] = adapter.strategy_name
                    signal['source_index'] = i
                
                all_signals.extend(signals)
                
            except Exception as e:
                print(f"  适配器 {adapter.strategy_name} 运行失败: {e}")
        
        print(f"\n总计生成 {len(all_signals)} 个原始信号")
        
        # 合并和解决冲突
        merged_signals = self._merge_signals(all_signals)
        print(f"合并后剩余 {len(merged_signals)} 个信号")
        
        return merged_signals
    
    def _merge_signals(self, signals: List[Dict]) -> List[Dict]:
        """合并多个适配器的信号，解决冲突"""
        if not signals:
            return []
        
        # 按时间分组
        time_groups = {}
        for signal in signals:
            timestamp = signal.get('timestamp')
            if timestamp is None:
                continue
            
            # 将时间戳转换为字符串用于分组
            time_key = timestamp.isoformat() if hasattr(timestamp, 'isoformat') else str(timestamp)
            
            if time_key not in time_groups:
                time_groups[time_key] = []
            time_groups[time_key].append(signal)
        
        # 合并每个时间点的信号
        merged = []
        for time_key, group_signals in time_groups.items():
            if len(group_signals) == 1:
                # 只有一个信号，直接使用
                merged.append(group_signals[0])
            else:
                # 多个信号，需要合并
                merged_signal = self._resolve_signal_conflicts(group_signals)
                if merged_signal:
                    merged.append(merged_signal)
        
        # 按时间排序
        return sorted(merged, key=lambda x: x.get('timestamp', datetime.min))
    
    def _resolve_signal_conflicts(self, signals: List[Dict]) -> Dict:
        """解决信号冲突"""
        # 简单的投票机制
        action_votes = {}
        total_confidence = 0
        
        for signal in signals:
            action = signal.get('action', 'hold')
            confidence = signal.get('confidence', 0.5)
            
            if action not in action_votes:
                action_votes[action] = 0
            
            action_votes[action] += confidence
            total_confidence += confidence
        
        if not action_votes:
            return None
        
        # 选择得票最高的动作
        best_action = max(action_votes.items(), key=lambda x: x[1])[0]
        avg_confidence = action_votes[best_action] / total_confidence if total_confidence > 0 else 0.5
        
        # 使用第一个信号作为基础
        base_signal = signals[0].copy()
        
        # 更新动作和置信度
        base_signal['action'] = best_action
        base_signal['confidence'] = avg_confidence
        
        # 添加合并信息
        base_signal['merged_from'] = len(signals)
        base_signal['source_adapters'] = [s.get('source_adapter', 'unknown') for s in signals]
        base_signal['conflict_resolution'] = 'voting'
        
        return base_signal


# ========== 测试代码 ==========

if __name__ == "__main__":
    print("测试SignalDefinition适配器...")
    
    # 生成示例数据
    dates = pd.date_range('2024-01-01', periods=200, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(200).cumsum() + 100,
        'high': np.random.randn(200).cumsum() + 105,
        'low': np.random.randn(200).cumsum() + 95,
        'close': np.random.randn(200).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 200)
    }, index=dates)
    
    # 创建模拟SignalDefinition
    class MockSignalDefinition:
        def __init__(self, name="MockSignal"):
            self.name = name
        
        def get_signal_name(self):
            return self.name
        
        def generate_signals(self, df_window):
            # 生成一些模拟信号
            signals = []
            window_size = len(df_window)
            
            # 在窗口的25%、50%、75%位置生成信号
            for position in [0.25, 0.5, 0.75]:
                idx = int(window_size * position)
                if idx < window_size:
                    signal_type = 'top_divergence' if position < 0.5 else 'bottom_divergence'
                    signals.append({
                        'type': signal_type,
                        'idx': idx,
                        'price': df_window['close'].iloc[idx],
                        'features': {
                            'strength': np.random.uniform(0, 10),
                            'delay_bars': np.random.randint(1, 5)
                        }
                    })
            
            return signals
    
    # 测试单个适配器
    print("\n1. 测试单个SignalDefinition适配器:")
    mock_signal_def = MockSignalDefinition("TestSignal")
    
    adapter = SignalDefinitionAdapter(
        data=data,
        params={'window_size': 50, 'step': 10},
        signal_definition=mock_signal_def,
        strategy_name="TestAdapter"
    )
    
    signals = adapter.generate_standard_signals()
    print(f"生成 {len(signals)} 个标准化信号")
    
    adapter.print_summary()
    adapter.print_window_statistics()
    
    # 测试多信号适配器
    print("\n2. 测试多SignalDefinition适配器:")
    mock_signal_defs = [
        MockSignalDefinition("Signal1"),
        MockSignalDefinition("Signal2")
    ]
    
    multi_adapter = MultiSignalDefinitionAdapter(
        data=data,
        params={'window_size': 50, 'step': 10},
        signal_definitions=mock_signal_defs,
        strategy_name="MultiSignalAdapter"
    )
    
    multi_signals = multi_adapter.generate_standard_signals()
    print(f"生成 {len(multi_signals)} 个组合信号")
    
    multi_adapter.print_summary()
    
    print("\n✅ SignalDefinition适配器测试完成")