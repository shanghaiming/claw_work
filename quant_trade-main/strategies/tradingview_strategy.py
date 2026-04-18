try:
    from core.base_strategy import BaseStrategy
except ImportError:
    from core.base_strategy import BaseStrategy

import pandas as pd
import numpy as np
try:
    import talib
    _HAS_TALIB = True
except ImportError:
    _HAS_TALIB = False
import sys
import os

# 添加TradingView指标路径
workspace_path = "/Users/chengming/.openclaw/workspace"
sys.path.append(workspace_path)
sys.path.append(os.path.join(workspace_path, "tradingview_indicators"))
sys.path.append(os.path.join(workspace_path, "tradingview_100_indicators"))

class TradingViewStrategy(BaseStrategy):
    def __init__(self, data, params):
        super().__init__(data, params)
        # 默认参数
        self.atr_period = params.get('atr_period', 10)
        self.multiplier = params.get('multiplier', 3)
        self.rsi_period = params.get('rsi_period', 14)
        self.rsi_overbought = params.get('rsi_overbought', 70)
        self.rsi_oversold = params.get('rsi_oversold', 30)
        
    def generate_signals(self):
        """统一的多股票信号生成入口"""
        data = self.data.copy()
        
        # 确保数据有symbol列
        if 'symbol' not in data.columns:
            # 如果没有symbol列，假设是单股票数据，添加默认symbol
            data['symbol'] = 'DEFAULT'
        
        self.signals = []
        current_holding = None  # 当前持有的股票
        
        # 按时间遍历
        unique_times = data.index.unique()
        
        for i, current_time in enumerate(unique_times):
            current_bars = data.loc[current_time]
            
            # 如果只有一只股票，确保格式统一
            if isinstance(current_bars, pd.Series):
                current_bars = pd.DataFrame([current_bars])
            
            # 如果没有持仓，选择最优股票
            if current_holding is None:
                best_stock = self._select_best_stock(current_bars, current_time, data)
                if best_stock:
                    self.signals.append({
                        'timestamp': current_time,
                        'action': 'buy',
                        'symbol': best_stock
                    })
                    current_holding = best_stock
                    print(f"买入 {best_stock}")
            
            # 如果有持仓，检查是否需要卖出
            else:
                should_sell = self._check_sell_signal(current_holding, current_time, data)
                if should_sell:
                    self.signals.append({
                        'timestamp': current_time,
                        'action': 'sell',
                        'symbol': current_holding
                    })
                    print(f"卖出 {current_holding}")
                    current_holding = None
        print(*self.signals, sep='\n')
        return self.signals
    
    def _select_best_stock(self, current_bars, current_time, full_data):
        """
        选择最优股票
        返回评分最高的股票代码，如果没有符合条件的则返回None
        """
        best_score = -float('inf')
        best_stock = None
        
        for _, bar in current_bars.iterrows():
            symbol = bar['symbol']
            
            # 获取该股票的历史数据（当前时间之前）
            symbol_data = full_data[full_data['symbol'] == symbol]
            symbol_data = symbol_data[symbol_data.index <= current_time]
            
            # 计算该股票的评分
            score, should_buy = self._calculate_stock_score(symbol_data, symbol, current_time)
            
            # 更新最优股票
            if should_buy and score > best_score:
                best_score = score
                best_stock = symbol
        
        return best_stock
    
    def _check_sell_signal(self, symbol, current_time, full_data):
        """
        检查持仓股票是否需要卖出
        返回布尔值：True表示需要卖出，False表示继续持有
        """
        # 获取该股票的历史数据（当前时间之前）
        symbol_data = full_data[full_data['symbol'] == symbol]
        symbol_data = symbol_data[symbol_data.index <= current_time]
        
        # 计算该股票的卖出信号
        _, should_sell = self._calculate_stock_score(symbol_data, symbol, current_time, check_sell=True)
        
        return should_sell
    
    def _calculate_stock_score(self, symbol_data, symbol, current_time, check_sell=False):
        """
        计算单只股票的评分和交易信号
        使用TradingView指标组合：Supertrend + RSI
        
        返回: (score, should_trade)
        - score: 股票评分（越高越好）
        - should_trade: 
            - 如果是选股模式(check_sell=False): True表示可以买入
            - 如果是卖出检查模式(check_sell=True): True表示需要卖出
        """
        # 确保有足够的数据
        min_data = max(self.atr_period, self.rsi_period) + 10
        if len(symbol_data) < min_data:
            return 0, False
        
        # 复制数据避免修改原数据
        data = symbol_data.copy()
        
        # 计算TradingView指标
        # 直接使用内置Supertrend实现，避免导入问题
        data['supertrend'], data['supertrend_dir'] = self._builtin_supertrend(
            data['high'], data['low'], data['close']
        )
        
        # 计算RSI
        data['rsi'] = talib.RSI(data['close'], timeperiod=self.rsi_period)
        
        # 获取当前时刻的指标（避免未来函数）
        if len(data) < 2:
            return 0, False
        
        # 使用shift(1)来确保不使用未来数据
        current_supertrend_dir = data['supertrend_dir'].iloc[-1]  # 当前方向
        prev_supertrend_dir = data['supertrend_dir'].iloc[-2] if len(data) >= 2 else current_supertrend_dir
        
        current_rsi = data['rsi'].iloc[-1]
        prev_rsi = data['rsi'].iloc[-2] if len(data) >= 2 else current_rsi
        
        current_price = data['close'].iloc[-1]
        supertrend_value = data['supertrend'].iloc[-1]
        
        # 计算评分（基于多个因素）
        score = 0
        
        # 1. Supertrend方向得分
        if current_supertrend_dir == 1:
            score += 10  # 上升趋势加分
        else:
            score -= 10  # 下降趋势减分
        
        # 2. RSI位置得分
        if current_rsi < self.rsi_oversold:
            score += 15  # 超卖区域，买入机会
        elif current_rsi > self.rsi_overbought:
            score -= 15  # 超买区域，卖出机会
        else:
            # RSI在中间区域，根据趋势方向给予适当分数
            if current_supertrend_dir == 1:
                score += 5
            else:
                score -= 5
        
        # 3. 价格与Supertrend关系得分
        if current_price > supertrend_value:
            score += 5  # 价格在Supertrend之上，看涨
        else:
            score -= 5  # 价格在Supertrend之下，看跌
        
        # 判断交易信号
        if check_sell:
            # 卖出检查模式：Supertrend转为下降趋势或RSI超买时卖出
            should_sell = (prev_supertrend_dir == 1 and current_supertrend_dir == -1) or (current_rsi > self.rsi_overbought)
            return score, should_sell
        else:
            # 选股模式：Supertrend转为上升趋势且RSI不是超买时考虑买入
            should_buy = (prev_supertrend_dir == -1 and current_supertrend_dir == 1) and (current_rsi < self.rsi_overbought)
            return score, should_buy
    
    def _builtin_supertrend(self, high, low, close):
        """内置Supertrend实现（备用）"""
        # 转换为numpy数组
        high_arr = high.values if hasattr(high, 'values') else high
        low_arr = low.values if hasattr(low, 'values') else low
        close_arr = close.values if hasattr(close, 'values') else close
        
        atr = talib.ATR(high_arr, low_arr, close_arr, timeperiod=self.atr_period)
        hl2 = (high_arr + low_arr) / 2
        
        upper_band = hl2 + (self.multiplier * atr)
        lower_band = hl2 - (self.multiplier * atr)
        
        supertrend = np.zeros_like(close_arr)
        direction = np.zeros_like(close_arr)
        
        for i in range(1, len(close_arr)):
            if close_arr[i] > upper_band[i-1]:
                direction[i] = 1
                supertrend[i] = lower_band[i]
            elif close_arr[i] < lower_band[i-1]:
                direction[i] = -1
                supertrend[i] = upper_band[i]
            else:
                direction[i] = direction[i-1]
                if direction[i] == 1:
                    supertrend[i] = max(lower_band[i], supertrend[i-1])
                else:
                    supertrend[i] = min(upper_band[i], supertrend[i-1])
        
        return supertrend, direction