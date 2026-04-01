#!/usr/bin/env python3
"""
策略基类 - 定义统一策略接口
扩展simple_backtest.py的简单策略为完整可扩展框架
"""

import pandas as pd
import numpy as np
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


class StrategyBase(ABC):
    """
    量化策略基类
    所有策略必须继承此类并实现核心方法
    """
    
    def __init__(self, name: str, params: Optional[Dict[str, Any]] = None):
        """
        初始化策略
        
        Args:
            name: 策略名称
            params: 策略参数字典
        """
        self.name = name
        self.params = params or {}
        self.data = None
        self.position = 0  # 当前持仓
        self.signals = []  # 信号历史
        self.initialized = False
        
        logger.info(f"策略初始化: {name}, 参数: {params}")
    
    def initialize(self, initial_capital: float = 1000000):
        """
        策略初始化，设置初始状态
        
        Args:
            initial_capital: 初始资金
        """
        self.initial_capital = initial_capital
        self.cash = initial_capital
        self.portfolio_value = initial_capital
        self.trades = []
        self.positions_history = []
        self.portfolio_history = []
        self.initialized = True
        
        logger.info(f"策略{self.name}初始化完成，初始资金: {initial_capital}")
    
    @abstractmethod
    def on_data(self, data: pd.DataFrame) -> None:
        """
        处理市场数据
        子类必须实现此方法
        
        Args:
            data: 市场数据DataFrame，包含OHLCV等字段
        """
        pass
    
    @abstractmethod
    def generate_signal(self) -> Dict[str, Any]:
        """
        生成交易信号
        子类必须实现此方法
        
        Returns:
            信号字典，包含signal_type, confidence, price等字段
        """
        pass
    
    def execute_trade(self, signal: Dict[str, Any], price: float, commission_rate: float = 0.0003) -> Dict[str, Any]:
        """
        执行交易
        
        Args:
            signal: 交易信号
            price: 当前价格
            commission_rate: 佣金率
            
        Returns:
            交易记录
        """
        signal_type = signal.get('signal_type', 'hold')
        confidence = signal.get('confidence', 0.5)
        
        trade_record = {
            'timestamp': pd.Timestamp.now(),
            'signal_type': signal_type,
            'confidence': confidence,
            'price': price,
            'position_before': self.position,
            'cash_before': self.cash,
            'portfolio_before': self.portfolio_value
        }
        
        if signal_type == 'buy' and self.position == 0:
            # 买入逻辑
            max_shares = self.cash // (price * (1 + commission_rate))
            if max_shares > 0:
                cost = max_shares * price * (1 + commission_rate)
                self.cash -= cost
                self.position = max_shares
                
                trade_record.update({
                    'action': 'buy',
                    'shares': max_shares,
                    'cost': cost,
                    'commission': max_shares * price * commission_rate,
                    'position_after': self.position,
                    'cash_after': self.cash
                })
                
                logger.info(f"买入: {max_shares}股 @ ¥{price:.2f}, 成本: ¥{cost:.2f}")
                
        elif signal_type == 'sell' and self.position > 0:
            # 卖出逻辑
            revenue = self.position * price * (1 - commission_rate)
            self.cash += revenue
            
            trade_record.update({
                'action': 'sell',
                'shares': self.position,
                'revenue': revenue,
                'commission': self.position * price * commission_rate,
                'position_after': 0,
                'cash_after': self.cash
            })
            
            logger.info(f"卖出: {self.position}股 @ ¥{price:.2f}, 收入: ¥{revenue:.2f}")
            self.position = 0
            
        else:
            # 持有或无操作
            trade_record['action'] = 'hold'
            
        # 更新投资组合价值
        self.portfolio_value = self.cash + self.position * price
        trade_record['portfolio_after'] = self.portfolio_value
        
        if trade_record.get('action') in ['buy', 'sell']:
            self.trades.append(trade_record)
            
        return trade_record
    
    def update_portfolio(self, price: float) -> None:
        """
        更新投资组合价值
        
        Args:
            price: 当前价格
        """
        self.portfolio_value = self.cash + self.position * price
        self.positions_history.append(self.position)
        self.portfolio_history.append(self.portfolio_value)
    
    def get_params(self) -> Dict[str, Any]:
        """
        获取策略参数
        
        Returns:
            策略参数字典
        """
        return self.params.copy()
    
    def set_params(self, params: Dict[str, Any]) -> None:
        """
        设置策略参数
        
        Args:
            params: 新参数字典
        """
        self.params.update(params)
        logger.info(f"策略{self.name}参数更新: {params}")
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """
        获取策略性能指标
        
        Returns:
            性能指标字典
        """
        if not self.portfolio_history:
            return {}
        
        returns = pd.Series(self.portfolio_history).pct_change().dropna()
        
        if len(returns) == 0:
            return {}
        
        # 基础指标
        total_return = (self.portfolio_history[-1] - self.initial_capital) / self.initial_capital
        cumulative_returns = (1 + returns).cumprod() - 1
        
        # 年化指标（假设252个交易日）
        annual_return = total_return / (len(returns) / 252) if len(returns) > 0 else 0
        volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
        
        # 交易统计
        trades_df = pd.DataFrame(self.trades) if self.trades else pd.DataFrame()
        if not trades_df.empty and 'action' in trades_df.columns:
            buy_trades = len(trades_df[trades_df['action'] == 'buy'])
            sell_trades = len(trades_df[trades_df['action'] == 'sell'])
            total_trades = buy_trades + sell_trades
        else:
            buy_trades = sell_trades = total_trades = 0
        
        metrics = {
            'strategy_name': self.name,
            'initial_capital': self.initial_capital,
            'final_portfolio': self.portfolio_history[-1] if self.portfolio_history else self.initial_capital,
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'total_trades': total_trades,
            'buy_trades': buy_trades,
            'sell_trades': sell_trades,
            'current_position': self.position,
            'current_cash': self.cash,
            'current_portfolio': self.portfolio_value
        }
        
        return metrics
    
    def __str__(self):
        """策略字符串表示"""
        metrics = self.get_performance_metrics()
        if not metrics:
            return f"Strategy: {self.name} (未初始化)"
        
        return f"""
策略: {self.name}
初始资金: ¥{metrics['initial_capital']:,.2f}
最终资产: ¥{metrics['final_portfolio']:,.2f}
总收益率: {metrics['total_return']:.2%}
年化收益: {metrics['annual_return']:.2%}
夏普比率: {metrics['sharpe_ratio']:.2f}
最大回撤: {metrics['max_drawdown']:.2%}
交易次数: {metrics['total_trades']} (买入: {metrics['buy_trades']}, 卖出: {metrics['sell_trades']})
当前持仓: {metrics['current_position']}股
当前现金: ¥{metrics['current_cash']:,.2f}
当前资产: ¥{metrics['current_portfolio']:,.2f}
"""


class MovingAverageStrategy(StrategyBase):
    """
    移动平均策略示例 - 基于simple_backtest.py的实现
    """
    
    def __init__(self, short_window: int = 5, long_window: int = 20, **kwargs):
        """
        初始化移动平均策略
        
        Args:
            short_window: 短期移动平均窗口
            long_window: 长期移动平均窗口
            **kwargs: 其他策略参数
        """
        params = {
            'short_window': short_window,
            'long_window': long_window,
            **kwargs
        }
        super().__init__(name=f"MA({short_window},{long_window})", params=params)
        
        self.short_window = short_window
        self.long_window = long_window
        self.data_processed = None
        
    def on_data(self, data: pd.DataFrame) -> None:
        """
        处理市场数据，计算移动平均
        
        Args:
            data: 市场数据DataFrame
        """
        self.data = data.copy()
        
        # 确保有日期索引
        if 'date' in self.data.columns:
            self.data['date'] = pd.to_datetime(self.data['date'])
            self.data.set_index('date', inplace=True)
        
        # 计算移动平均
        self.data['ma_short'] = self.data['close'].rolling(window=self.short_window).mean()
        self.data['ma_long'] = self.data['close'].rolling(window=self.long_window).mean()
        self.data['ma_diff'] = self.data['ma_short'] - self.data['ma_long']
        
        # 生成原始信号（1:买入, -1:卖出, 0:持有）
        self.data['raw_signal'] = 0
        self.data.loc[self.data['ma_diff'] > 0, 'raw_signal'] = 1
        self.data.loc[self.data['ma_diff'] < 0, 'raw_signal'] = -1
        
        # 计算信号变化（用于检测信号切换点）
        self.data['signal_change'] = self.data['raw_signal'].diff()
        
        self.data_processed = self.data
        
    def generate_signal(self) -> Dict[str, Any]:
        """
        生成交易信号
        
        Returns:
            交易信号字典
        """
        if self.data_processed is None or len(self.data_processed) == 0:
            return {'signal_type': 'hold', 'confidence': 0.0, 'reason': '数据未准备好'}
        
        # 获取最新数据
        latest = self.data_processed.iloc[-1]
        
        # 检查是否有足够的计算数据
        if pd.isna(latest['ma_short']) or pd.isna(latest['ma_long']):
            return {'signal_type': 'hold', 'confidence': 0.0, 'reason': '数据不足'}
        
        current_price = latest['close']
        
        # 基于信号变化生成交易信号
        signal_change = latest.get('signal_change', 0)
        
        if signal_change == 2:  # 从-1变为1，金叉买入信号
            signal_type = 'buy'
            confidence = min(abs(latest['ma_diff']) / current_price * 10, 0.9)
            reason = f"MA金叉: 短期MA({self.short_window})上穿长期MA({self.long_window})，差值: {latest['ma_diff']:.2f}"
            
        elif signal_change == -2:  # 从1变为-1，死叉卖出信号
            signal_type = 'sell'
            confidence = min(abs(latest['ma_diff']) / current_price * 10, 0.9)
            reason = f"MA死叉: 短期MA({self.short_window})下穿长期MA({self.long_window})，差值: {latest['ma_diff']:.2f}"
            
        else:
            signal_type = 'hold'
            confidence = 0.3
            reason = f"MA趋势延续: 短期MA({self.short_window})={latest['ma_short']:.2f}, 长期MA({self.long_window})={latest['ma_long']:.2f}"
        
        signal = {
            'signal_type': signal_type,
            'confidence': confidence,
            'price': current_price,
            'ma_short': latest['ma_short'],
            'ma_long': latest['ma_long'],
            'ma_diff': latest['ma_diff'],
            'reason': reason,
            'timestamp': latest.name if hasattr(latest, 'name') else pd.Timestamp.now()
        }
        
        self.signals.append(signal)
        return signal


def create_strategy(strategy_type: str, **params) -> StrategyBase:
    """
    策略工厂函数 - 创建策略实例
    
    Args:
        strategy_type: 策略类型
        **params: 策略参数
        
    Returns:
        策略实例
    """
    strategy_registry = {
        'moving_average': MovingAverageStrategy,
        'ma': MovingAverageStrategy,
    }
    
    if strategy_type not in strategy_registry:
        raise ValueError(f"未知策略类型: {strategy_type}，可用类型: {list(strategy_registry.keys())}")
    
    strategy_class = strategy_registry[strategy_type]
    return strategy_class(**params)


if __name__ == "__main__":
    """策略基类测试"""
    import sys
    import os
    
    # 添加路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 测试策略基类
    print("测试策略基类...")
    
    # 创建测试数据
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    test_data = pd.DataFrame({
        'date': dates,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(10000, 100000, 100)
    })
    
    # 创建策略实例
    strategy = MovingAverageStrategy(short_window=5, long_window=20)
    strategy.initialize(initial_capital=1000000)
    strategy.on_data(test_data)
    
    # 测试信号生成
    signal = strategy.generate_signal()
    print(f"生成的信号: {signal}")
    
    # 测试性能指标
    metrics = strategy.get_performance_metrics()
    print(f"性能指标: {metrics}")
    
    print("策略基类测试完成!")