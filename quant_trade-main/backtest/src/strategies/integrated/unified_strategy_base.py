#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一策略基类 - 扩展原始base_strategy.py，提供更丰富的策略开发接口

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

功能特性:
1. 标准化的策略接口
2. 参数验证和默认值
3. 信号标准化输出
4. 性能指标跟踪
5. 日志和调试支持
6. 向后兼容原始base_strategy.py
"""

from abc import ABC, abstractmethod
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime
import warnings
import json
warnings.filterwarnings('ignore')


class UnifiedStrategyBase(ABC):
    """
    统一策略基类 - 所有策略的基类
    
    设计原则:
    1. 向后兼容: 保持与原始base_strategy.py相同的核心接口
    2. 功能增强: 添加参数验证、信号标准化、性能跟踪
    3. 易于扩展: 清晰的抽象方法和钩子函数
    4. 生产就绪: 完善的错误处理和日志记录
    """
    
    # 标准信号动作类型
    SIGNAL_ACTIONS = ['buy', 'sell', 'hold', 'close', 'adjust']
    
    def __init__(self, 
                 data: pd.DataFrame, 
                 params: Dict[str, Any],
                 strategy_name: Optional[str] = None):
        """
        初始化策略
        
        参数:
            data: 交易数据DataFrame，必须包含OHLC列
            params: 策略参数字典
            strategy_name: 策略名称，如果为None则使用类名
        """
        # 基础属性
        self.data = data.copy()
        self.raw_params = params.copy()
        self.strategy_name = strategy_name or self.__class__.__name__
        
        # 信号存储
        self.signals = []  # 原始信号列表（保持向后兼容）
        self.standard_signals = []  # 标准化信号列表
        self.signal_history = []  # 信号历史记录（用于分析和调试）
        
        # 状态跟踪
        self.initialized = False
        self.execution_start_time = None
        self.execution_end_time = None
        
        # 性能指标
        self.performance_metrics = {}
        self.execution_stats = {
            'signal_count': 0,
            'buy_count': 0,
            'sell_count': 0,
            'execution_time': None
        }
        
        # 验证和初始化
        self._validate_data()
        self._process_params()
        self._initialize_strategy()
        
        print(f"策略 '{self.strategy_name}' 初始化完成")
        print(f"参数: {json.dumps(self.params, indent=2, default=str)}")
    
    def _validate_data(self):
        """验证输入数据的格式和完整性"""
        required_columns = ['open', 'high', 'low', 'close']
        
        # 检查必需列
        missing_cols = [col for col in required_columns if col not in self.data.columns]
        if missing_cols:
            raise ValueError(f"数据缺少必需列: {missing_cols}")
        
        # 检查数据是否为空
        if self.data.empty:
            raise ValueError("数据为空")
        
        # 确保索引是datetime类型
        if not pd.api.types.is_datetime64_any_dtype(self.data.index):
            try:
                self.data.index = pd.to_datetime(self.data.index)
            except Exception as e:
                raise ValueError(f"无法将索引转换为datetime: {e}")
        
        # 检查数据排序
        if not self.data.index.is_monotonic_increasing:
            self.data = self.data.sort_index()
            print("警告: 数据索引未按时间排序，已自动排序")
    
    def _process_params(self):
        """处理策略参数"""
        # 合并默认参数
        default_params = self.get_default_params()
        self.params = {**default_params, **self.raw_params}
        
        # 验证参数
        self._validate_params()
    
    def _validate_params(self):
        """验证策略参数"""
        # 子类可以重写此方法来添加特定的参数验证
        pass
    
    def _initialize_strategy(self):
        """初始化策略特定的设置"""
        # 子类可以重写此方法来进行策略特定的初始化
        self.initialized = True
    
    @abstractmethod
    def generate_signals(self) -> List[Dict]:
        """
        生成交易信号 - 核心策略逻辑
        
        返回:
            信号列表，每个信号至少包含:
            - timestamp: 信号时间
            - action: 信号动作 ('buy'/'sell'等)
            - price: 信号价格
            
        注意: 此方法保持与原始base_strategy.py的向后兼容性
        """
        pass
    
    def generate_standard_signals(self) -> List[Dict]:
        """
        生成标准化信号 - 增强版信号生成
        
        返回:
            标准化信号列表，包含丰富的元数据
        """
        # 开始执行计时
        self.execution_start_time = datetime.now()
        
        try:
            # 调用原始信号生成方法（保持兼容）
            raw_signals = self.generate_signals()
            
            # 转换为标准化信号
            standard_signals = []
            for i, raw_signal in enumerate(raw_signals):
                standard_signal = self._standardize_signal(raw_signal, i)
                standard_signals.append(standard_signal)
            
            # 更新信号存储
            self.signals = raw_signals
            self.standard_signals = standard_signals
            
            # 更新执行统计
            self.execution_end_time = datetime.now()
            execution_time = (self.execution_end_time - self.execution_start_time).total_seconds()
            self.execution_stats.update({
                'signal_count': len(standard_signals),
                'buy_count': len([s for s in standard_signals if s['action'] == 'buy']),
                'sell_count': len([s for s in standard_signals if s['action'] == 'sell']),
                'execution_time': execution_time
            })
            
            # 记录到历史
            self.signal_history.append({
                'execution_time': self.execution_start_time.isoformat(),
                'signal_count': len(standard_signals),
                'signals': standard_signals[:10]  # 只保存前10个信号避免内存问题
            })
            
            return standard_signals
            
        except Exception as e:
            print(f"策略 '{self.strategy_name}' 信号生成失败: {e}")
            raise
    
    def _standardize_signal(self, raw_signal: Dict, signal_index: int) -> Dict:
        """
        将原始信号转换为标准化格式
        
        参数:
            raw_signal: 原始信号字典
            signal_index: 信号索引
            
        返回:
            标准化信号字典
        """
        # 基础标准化
        standardized = {
            'strategy': self.strategy_name,
            'signal_id': f"{self.strategy_name}_{signal_index:04d}",
            'timestamp': raw_signal.get('timestamp'),
            'action': raw_signal.get('action', 'hold'),
            'price': raw_signal.get('price', 0.0),
            'raw_signal': raw_signal,
            'metadata': {
                'generation_time': datetime.now().isoformat(),
                'strategy_params': self.params,
                'signal_index': signal_index
            }
        }
        
        # 提取symbol（如果存在）
        if 'symbol' in raw_signal:
            standardized['symbol'] = raw_signal['symbol']
        elif 'symbol' in self.data.columns and not self.data.empty:
            # 尝试从数据中推断
            standardized['symbol'] = self.data['symbol'].iloc[0] if 'symbol' in self.data.columns else 'UNKNOWN'
        
        # 提取confidence（如果存在）
        if 'confidence' in raw_signal:
            standardized['confidence'] = raw_signal['confidence']
        else:
            standardized['confidence'] = 0.5  # 默认置信度
        
        # 提取signal_type（如果存在）
        if 'type' in raw_signal:
            standardized['signal_type'] = raw_signal['type']
        else:
            standardized['signal_type'] = 'unknown'
        
        # 提取features（如果存在）
        if 'features' in raw_signal:
            standardized['features'] = raw_signal['features']
        else:
            standardized['features'] = {}
        
        # 验证必要字段
        self._validate_standardized_signal(standardized)
        
        return standardized
    
    def _validate_standardized_signal(self, signal: Dict):
        """验证标准化信号的完整性"""
        required_fields = ['timestamp', 'action', 'price']
        missing_fields = [field for field in required_fields if field not in signal]
        
        if missing_fields:
            raise ValueError(f"标准化信号缺少必要字段: {missing_fields}")
        
        # 验证action类型
        if signal['action'] not in self.SIGNAL_ACTIONS:
            warnings.warn(f"非标准信号动作: {signal['action']}, 标准动作: {self.SIGNAL_ACTIONS}")
    
    def get_default_params(self) -> Dict[str, Any]:
        """
        获取策略的默认参数
        
        子类应该重写此方法以提供策略特定的默认参数
        """
        return {
            'enabled': True,
            'version': '1.0.0',
            'description': f'{self.strategy_name} strategy'
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取策略性能指标"""
        metrics = {
            'strategy_name': self.strategy_name,
            'execution_stats': self.execution_stats,
            'signal_summary': {
                'total_signals': len(self.standard_signals),
                'buy_signals': len([s for s in self.standard_signals if s['action'] == 'buy']),
                'sell_signals': len([s for s in self.standard_signals if s['action'] == 'sell']),
                'hold_signals': len([s for s in self.standard_signals if s['action'] == 'hold']),
            },
            'params': self.params,
            'initialized': self.initialized,
        }
        
        # 计算信号时间范围
        if self.standard_signals:
            timestamps = [s['timestamp'] for s in self.standard_signals if s['timestamp']]
            if timestamps:
                metrics['signal_time_range'] = {
                    'start': min(timestamps),
                    'end': max(timestamps)
                }
        
        return metrics
    
    def print_summary(self):
        """打印策略摘要"""
        print(f"\n{'='*60}")
        print(f"策略摘要: {self.strategy_name}")
        print(f"{'='*60}")
        
        metrics = self.get_performance_metrics()
        
        print(f"\n📊 执行统计:")
        print(f"  信号总数: {metrics['execution_stats']['signal_count']}")
        print(f"  买入信号: {metrics['execution_stats']['buy_count']}")
        print(f"  卖出信号: {metrics['execution_stats']['sell_count']}")
        print(f"  执行时间: {metrics['execution_stats']['execution_time']:.3f}秒")
        
        print(f"\n⚙️ 策略参数:")
        for key, value in self.params.items():
            print(f"  {key}: {value}")
        
        print(f"\n📈 信号样本 (前3个):")
        for i, signal in enumerate(self.standard_signals[:3]):
            print(f"  {i+1}. {signal['timestamp']} - {signal['action']} @ {signal.get('price', 'N/A')}")
        
        if len(self.standard_signals) > 3:
            print(f"  ... 还有 {len(self.standard_signals) - 3} 个信号")
        
        print(f"\n{'='*60}")
    
    def save_signals(self, filepath: str, format: str = 'json'):
        """保存信号到文件"""
        if not self.standard_signals:
            print("警告: 没有信号可保存")
            return
        
        try:
            if format == 'json':
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(self.standard_signals, f, indent=2, default=str)
            elif format == 'csv':
                df = pd.DataFrame(self.standard_signals)
                df.to_csv(filepath, index=False)
            else:
                raise ValueError(f"不支持的格式: {format}")
            
            print(f"信号已保存到: {filepath} ({format}格式)")
            
        except Exception as e:
            print(f"保存信号失败: {e}")
    
    def plot_signals(self):
        """绘制信号图表（需要matplotlib）"""
        try:
            import matplotlib.pyplot as plt
            
            if self.data.empty or not self.standard_signals:
                print("没有足够的数据或信号来绘图")
                return
            
            # 简化版绘图
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # 绘制价格
            price_data = self.data['close'].iloc[-100:]  # 最近100个点
            ax.plot(price_data.index, price_data.values, label='Close Price', alpha=0.7)
            
            # 绘制信号
            buy_signals = [s for s in self.standard_signals if s['action'] == 'buy']
            sell_signals = [s for s in self.standard_signals if s['action'] == 'sell']
            
            if buy_signals:
                buy_times = [s['timestamp'] for s in buy_signals]
                buy_prices = [s['price'] for s in buy_signals]
                ax.scatter(buy_times, buy_prices, color='green', marker='^', s=100, label='Buy', zorder=5)
            
            if sell_signals:
                sell_times = [s['timestamp'] for s in sell_signals]
                sell_prices = [s['price'] for s in sell_signals]
                ax.scatter(sell_times, sell_prices, color='red', marker='v', s=100, label='Sell', zorder=5)
            
            ax.set_title(f'Strategy Signals: {self.strategy_name}')
            ax.set_xlabel('Time')
            ax.set_ylabel('Price')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            plt.show()
            
        except ImportError:
            print("绘图需要matplotlib，请安装: pip install matplotlib")
        except Exception as e:
            print(f"绘图失败: {e}")


# ========== 向后兼容包装器 ==========

class BackwardCompatibleStrategy(UnifiedStrategyBase):
    """
    向后兼容包装器 - 将原始base_strategy.py兼容的策略包装为统一接口
    
    使用示例:
        original_strategy = OriginalMovingAverageStrategy(data, params)
        compatible_strategy = BackwardCompatibleStrategy(original_strategy)
        signals = compatible_strategy.generate_standard_signals()
    """
    
    def __init__(self, original_strategy, strategy_name=None):
        """
        初始化兼容包装器
        
        参数:
            original_strategy: 原始策略实例（必须实现generate_signals方法）
            strategy_name: 策略名称
        """
        self.original_strategy = original_strategy
        
        # 调用父类初始化（传递原始策略的数据和参数）
        super().__init__(
            data=original_strategy.data,
            params=original_strategy.params,
            strategy_name=strategy_name or original_strategy.__class__.__name__
        )
    
    def generate_signals(self) -> List[Dict]:
        """调用原始策略的信号生成方法"""
        return self.original_strategy.generate_signals()
    
    def get_default_params(self) -> Dict[str, Any]:
        """获取原始策略的默认参数"""
        # 尝试从原始策略获取默认参数
        if hasattr(self.original_strategy, 'get_default_params'):
            return self.original_strategy.get_default_params()
        return super().get_default_params()


# ========== 简化示例策略 ==========

class ExampleMovingAverageStrategy(UnifiedStrategyBase):
    """示例：移动平均策略的统一定制实现"""
    
    def get_default_params(self) -> Dict[str, Any]:
        """默认参数"""
        return {
            'short_window': 5,
            'long_window': 20,
            'threshold': 0.01,
            'enabled': True,
            'version': '1.0.0',
            'description': '双均线金叉死叉策略'
        }
    
    def generate_signals(self) -> List[Dict]:
        """生成移动平均信号"""
        data = self.data.copy()
        signals = []
        
        # 计算移动平均
        short_ma = data['close'].rolling(window=self.params['short_window']).mean()
        long_ma = data['close'].rolling(window=self.params['long_window']).mean()
        
        # 生成信号
        for i in range(1, len(data)):
            prev_short = short_ma.iloc[i-1]
            prev_long = long_ma.iloc[i-1]
            curr_short = short_ma.iloc[i]
            curr_long = long_ma.iloc[i]
            
            # 金叉买入信号
            if prev_short <= prev_long and curr_short > curr_long:
                signals.append({
                    'timestamp': data.index[i],
                    'action': 'buy',
                    'price': data['close'].iloc[i],
                    'type': 'golden_cross',
                    'confidence': 0.7,
                    'features': {
                        'short_ma': curr_short,
                        'long_ma': curr_long,
                        'difference': curr_short - curr_long
                    }
                })
            
            # 死叉卖出信号
            elif prev_short >= prev_long and curr_short < curr_long:
                signals.append({
                    'timestamp': data.index[i],
                    'action': 'sell',
                    'price': data['close'].iloc[i],
                    'type': 'death_cross',
                    'confidence': 0.7,
                    'features': {
                        'short_ma': curr_short,
                        'long_ma': curr_long,
                        'difference': curr_short - curr_long
                    }
                })
        
        return signals


# ========== 测试代码 ==========

if __name__ == "__main__":
    print("测试统一策略基类...")
    
    # 生成示例数据
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    }, index=dates)
    
    # 测试示例策略
    print("\n1. 测试示例移动平均策略:")
    strategy = ExampleMovingAverageStrategy(
        data=data,
        params={'short_window': 5, 'long_window': 20}
    )
    
    signals = strategy.generate_standard_signals()
    print(f"生成 {len(signals)} 个信号")
    
    strategy.print_summary()
    
    # 测试性能指标
    metrics = strategy.get_performance_metrics()
    print(f"\n2. 性能指标:")
    print(json.dumps(metrics, indent=2, default=str))
    
    print("\n✅ 统一策略基类测试完成")