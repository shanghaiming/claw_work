from strategies.base_strategy import BaseStrategy
import pandas as pd
import numpy as np

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

class MovingAverageStrategy(BaseStrategy):
    def __init__(self, data, params):
        super().__init__(data, params)
        self.short_window = params.get('short_window', 5)
        self.long_window = params.get('long_window', 20)
        
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
        这是策略的核心逻辑，可以替换为任何自定义策略
        
        返回: (score, should_trade)
        - score: 股票评分（越高越好）
        - should_trade: 
            - 如果是选股模式(check_sell=False): True表示可以买入
            - 如果是卖出检查模式(check_sell=True): True表示需要卖出
        """
        # 确保有足够的数据
        if len(symbol_data) < self.long_window:
            return 0, False
        
        # 复制数据避免修改原数据
        data = symbol_data.copy()
        
        # 计算技术指标（避免未来函数）
        data['ma_short'] = data['close'].shift(1).rolling(self.short_window, min_periods=1).mean()
        data['ma_long'] = data['close'].shift(1).rolling(self.long_window, min_periods=1).mean()
        
        # 获取当前时刻的指标
        if len(data) < 2:
            return 0, False
            
        current_ma_short = data['ma_short'].iloc[-1]
        current_ma_long = data['ma_long'].iloc[-1]
        prev_ma_short = data['ma_short'].iloc[-2]
        prev_ma_long = data['ma_long'].iloc[-2]
        
        # 计算金叉死叉
        golden_cross = (current_ma_short > current_ma_long) and (prev_ma_short <= prev_ma_long)
        death_cross = (current_ma_short < current_ma_long) and (prev_ma_short >= prev_ma_long)
        
        # 计算评分（均线差值百分比）
        score = (current_ma_short - current_ma_long) / current_ma_long * 100
        
        if check_sell:
            # 卖出检查模式：出现死叉时卖出
            return score, death_cross
        else:
            # 选股模式：出现金叉时可以考虑买入
            return score, golden_cross