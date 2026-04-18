"""
统一策略基类 - 所有策略必须继承此类
信号格式: List[Dict] 每个信号必须包含 {timestamp, action, symbol, price}
"""
from abc import ABC, abstractmethod
import pandas as pd
from typing import Dict, List, Any


class BaseStrategy(ABC):
    """统一策略基类"""

    SIGNAL_ACTIONS = {'buy', 'sell', 'hold'}

    # 看板元数据（子类可覆盖）
    strategy_description: str = ""
    strategy_category: str = "general"  # ma, price_action, momentum, wave, ml, volume, general
    strategy_params_schema: Dict = {}   # 看板动态渲染参数表单用

    def __init__(self, data: pd.DataFrame, params: dict = None):
        self.data = data.copy()
        self.params = {**self.get_default_params(), **(params or {})}
        self.strategy_name = self.__class__.__name__
        self.signals: List[Dict] = []
        self._validate_data()
        self.validate_params()

    @abstractmethod
    def generate_signals(self) -> List[Dict]:
        """生成交易信号，返回信号列表，每个信号必须包含:
        - timestamp: 信号时间
        - action: 'buy'/'sell'/'hold'
        - symbol: 股票代码
        - price: 信号价格
        """
        pass

    def get_default_params(self) -> Dict[str, Any]:
        """子类重写以提供默认参数"""
        return {}

    def validate_params(self):
        """子类重写以添加参数验证，验证失败抛 ValueError"""
        pass

    def _validate_data(self):
        """验证输入数据"""
        required = ['open', 'high', 'low', 'close']
        missing = [c for c in required if c not in self.data.columns]
        if missing:
            raise ValueError(f"数据缺少必需列: {missing}")

        if self.data.empty:
            raise ValueError("数据为空")

        # 自动注入 symbol 列
        if 'symbol' not in self.data.columns:
            self.data['symbol'] = 'DEFAULT'

        if not pd.api.types.is_datetime64_any_dtype(self.data.index):
            try:
                self.data.index = pd.to_datetime(self.data.index)
            except Exception as e:
                raise ValueError(f"无法将索引转换为datetime: {e}")

        if not self.data.index.is_monotonic_increasing:
            self.data = self.data.sort_index()

    def _record_signal(self, timestamp, action, symbol='DEFAULT', price=0.0, **extra):
        """记录交易信号"""
        if action not in self.SIGNAL_ACTIONS:
            raise ValueError(f"无效信号动作: {action}, 允许: {self.SIGNAL_ACTIONS}")
        # 如果没传 symbol，尝试从数据中获取
        if symbol == 'DEFAULT' and 'symbol' in self.data.columns:
            symbol = self.data['symbol'].iloc[0]
        self.signals.append({
            'timestamp': timestamp,
            'action': action,
            'symbol': symbol,
            'price': float(price),
            **extra
        })

    def get_signals_summary(self) -> Dict:
        """返回信号统计摘要"""
        if not self.signals:
            return {"total": 0, "buys": 0, "sells": 0, "holds": 0}
        buys = len([s for s in self.signals if s['action'] == 'buy'])
        sells = len([s for s in self.signals if s['action'] == 'sell'])
        holds = len([s for s in self.signals if s['action'] == 'hold'])
        return {"total": len(self.signals), "buys": buys, "sells": sells, "holds": holds}

    def screen(self) -> Dict:
        """基于最新数据做实时选股判断（非历史统计）

        不调用 generate_signals()（那是回测用的，遍历全历史）。
        只计算必要的技术指标，然后基于最后一根K线做买卖判断。
        子类可覆盖此方法实现自定义选股逻辑。

        Returns:
            Dict with keys: action ('buy'/'sell'/'hold'), reason (str), price (float)
        """
        import numpy as np

        if len(self.data) < 20:
            return {'action': 'hold', 'reason': '数据不足', 'price': float(self.data['close'].iloc[-1])}

        df = self.data
        latest = df.iloc[-1]
        close = latest['close']
        symbol = latest.get('symbol', 'UNKNOWN')
        timestamp = df.index[-1]

        # 计算基础技术指标（仅用于最新判断）
        ma5 = df['close'].rolling(5).mean().iloc[-1]
        ma20 = df['close'].rolling(20).mean().iloc[-1]
        vol_ma5 = df['volume'].rolling(5).mean().iloc[-1] if 'volume' in df.columns else None
        vol = latest.get('volume', 0)

        # 价格变化率
        pct_change = df['close'].pct_change().iloc[-1]

        # RSI(14) 简化计算
        delta = df['close'].diff()
        gain = delta.where(delta > 0, 0).rolling(14).mean().iloc[-1]
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean().iloc[-1]
        rs = gain / (loss + 1e-10)
        rsi = 100 - (100 / (1 + rs))

        # --- 买入条件 ---
        buy_score = 0
        buy_reasons = []
        if ma5 > ma20 and close > ma5:
            buy_score += 1
            buy_reasons.append('均线多头')
        if vol_ma5 and vol > vol_ma5:
            buy_score += 1
            buy_reasons.append('放量')
        if rsi < 70:
            buy_score += 1
            buy_reasons.append('RSI未超买')
        if pct_change > 0:
            buy_score += 1
            buy_reasons.append('收阳')

        # --- 卖出条件 ---
        sell_score = 0
        sell_reasons = []
        if ma5 < ma20 and close < ma5:
            sell_score += 1
            sell_reasons.append('均线空头')
        if vol_ma5 and vol > vol_ma5 and close < latest['open']:
            sell_score += 1
            sell_reasons.append('放量下跌')
        if rsi > 30:
            sell_score += 1
            sell_reasons.append('RSI未超卖')
        if pct_change < 0:
            sell_score += 1
            sell_reasons.append('收阴')

        # 决策
        if buy_score >= 3:
            return {
                'action': 'buy',
                'reason': '+'.join(buy_reasons),
                'price': float(close),
            }
        elif sell_score >= 3:
            return {
                'action': 'sell',
                'reason': '+'.join(sell_reasons),
                'price': float(close),
            }
        else:
            return {
                'action': 'hold',
                'reason': f'buy({buy_score})/sell({sell_score})条件不足',
                'price': float(close),
            }
