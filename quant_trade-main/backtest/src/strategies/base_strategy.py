from abc import ABC, abstractmethod
import pandas as pd

class BaseStrategy(ABC):
    def __init__(self, data: pd.DataFrame, params: dict):
        self.data = data
        self.params = params
        self.signals = []

    @abstractmethod
    def generate_signals(self):
        """核心逻辑：根据数据和指标生成交易信号"""
        pass

    def _record_signal(self, timestamp, action, price):
        """记录交易信号"""
        self.signals.append({
            'timestamp': timestamp,
            'action': action,  # 'buy'/'sell'/'hold'
            'price': price
        })