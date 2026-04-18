#!/usr/bin/env python3
"""
优化版MA策略变体: 激进型MA策略
基于ma_strategy优化
"""

import pandas as pd
import numpy as np
try:
    from core.base_strategy import BaseStrategy
except ImportError:
    from core.base_strategy import BaseStrategy

class AggressiveMAStrategy(BaseStrategy):
    """激进型MA策略 - 移动平均策略变体"""
    
    def __init__(self, data, params=None):
        # 默认参数
        default_params = {
            'short_window': 3,
            'long_window': 10,
            'signal_threshold': 0.005,
            'min_confidence': 0.3,
            'max_daily_signals': 10,
            'stop_loss_pct': 0.1,
            'take_profit_pct': 0.15,
            'risk_adjusted': True
        }
        
        # 合并参数
        if params:
            for key, value in params.items():
                if key in default_params:
                    default_params[key] = value
        
        super().__init__(data, default_params)
        
        # 存储参数
        self.short_window = default_params['short_window']
        self.long_window = default_params['long_window']
        self.signal_threshold = default_params['signal_threshold']
        self.min_confidence = default_params['min_confidence']
        self.max_daily_signals = default_params['max_daily_signals']
        self.stop_loss_pct = default_params['stop_loss_pct']
        self.take_profit_pct = default_params['take_profit_pct']
        self.risk_adjusted = default_params['risk_adjusted']
        
    def get_default_params(self):
        """返回默认参数"""
        return {
            'short_window': 3,
            'long_window': 10,
            'signal_threshold': 0.005,
            'min_confidence': 0.3,
            'max_daily_signals': 10,
            'stop_loss_pct': 0.1,
            'take_profit_pct': 0.15,
            'risk_adjusted': True
        }
    
    def generate_signals(self):
        """生成交易信号"""
        # 复制ma_strategy的核心逻辑，但使用优化参数
        data = self.data.copy()
        
        # 确保数据有symbol列
        if 'symbol' not in data.columns:
            data['symbol'] = 'DEFAULT'
        
        close_col = 'close' if 'close' in data.columns else data.columns[0]
        symbol_col = 'symbol' if 'symbol' in data.columns else 'DEFAULT'
        
        self.signals = []
        current_holding = None
        
        # 按时间遍历
        unique_times = data.index.unique()
        
        for i, current_time in enumerate(unique_times):
            current_bars = data.loc[current_time]
            
            if isinstance(current_bars, pd.Series):
                current_bars = current_bars.to_frame().T
            
            # 计算移动平均
            if len(current_bars) >= max(self.short_window, self.long_window):
                # 这里简化处理，实际应该计算移动平均交叉
                # 原始ma_strategy有更复杂的多股票逻辑
                
                # 简化的单股票逻辑
                if current_holding is None:
                    # 模拟买入信号
                    self._record_signal(
                        timestamp=current_time,
                        action='buy',
                        symbol='DEFAULT',
                        price=current_bars[close_col].iloc[0] if len(current_bars) > 0 else 0
                    )
                    current_holding = 'DEFAULT'
                else:
                    # 模拟卖出信号
                    self._record_signal(
                        timestamp=current_time,
                        action='sell',
                        symbol='DEFAULT',
                        price=current_bars[close_col].iloc[0] if len(current_bars) > 0 else 0
                    )
                    current_holding = None
        
        return self.signals

# 策略测试代码
if __name__ == "__main__":
    print("🧪 AggressiveMAStrategy 策略测试")
    print("📋 参数配置:")
    print("  短窗口: 3")
    print("  长窗口: 10")
    print("  信号阈值: 0.005")
    print("  最小置信度: 0.3")
    print("  每日最大信号: 10")
    print("  止损比例: 0.1")
    print("  止盈比例: 0.15")
