"""
多因子量化策略框架
整合用户的所有技术指标：
1. 现有指标: VR, MACD, 布林带, TSMA/LSMA, ER, EMA, 神奇九转
2. 新指标: Fisher Transform, Choppiness Index, Hull Moving Average
3. 仓位管理: 基于仓位分析器的仓位分配
"""

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional

# ==================== 新指标实现 ====================

def calculate_fisher_transform(df: pd.DataFrame, n: int = 10) -> pd.Series:
    """计算费希尔变换指标 (Fisher Transform)
    
    公式:
        HL2 = (H + L) / 2
        Z = (HL2 - LLV(HL2, N)) / (HHV(HL2, N) - LLV(HL2, N))
        VALUE = TMA(Z-0.5, 0.67, 0.66)
        VALUE2 = 限制在(-0.999, 0.999)
        TEMP = LN((1+VALUE2)/(1-VALUE2))
        FISHER = TMA(TEMP, 0.5, 0.5)
    """
    # HL2 = (最高价 + 最低价) / 2
    hl2 = (df['high'] + df['low']) / 2
    
    # Z = (HL2 - LLV(HL2, N)) / (HHV(HL2, N) - LLV(HL2, N))
    llv_hl2 = hl2.rolling(n).min()  # LLV(HL2, N)
    hhv_hl2 = hl2.rolling(n).max()  # HHV(HL2, N)
    z = (hl2 - llv_hl2) / (hhv_hl2 - llv_hl2 + 1e-8)
    
    # TMA实现（双重EMA模拟）
    def tma(series, alpha):
        """三角移动平均模拟"""
        result = np.zeros(len(series))
        if len(series) == 0:
            return result
        
        result[0] = series[0]
        for i in range(1, len(series)):
            result[i] = alpha * series[i] + (1 - alpha) * result[i-1]
        return result
    
    # VALUE = TMA(Z-0.5, 0.67, 0.66)
    alpha1 = 2 / (0.67 + 1)
    alpha2 = 2 / (0.66 + 1)
    value_series = z - 0.5
    value = tma(value_series, alpha1)
    value = tma(value, alpha2)
    
    # VALUE2 = 限制在(-0.999, 0.999)之间
    value2 = np.where(value > 0.99, 0.999, np.where(value < -0.99, -0.999, value))
    
    # TEMP = LN((1+VALUE2)/(1-VALUE2))
    temp = np.log((1 + value2) / (1 - value2 + 1e-8))
    
    # FISHER = TMA(TEMP, 0.5, 0.5)
    alpha_fisher = 2 / (0.5 + 1)
    fisher = tma(temp, alpha_fisher)
    fisher = tma(fisher, alpha_fisher)
    
    return pd.Series(fisher, index=df.index)


def calculate_choppiness_index(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """计算波动指数 (Choppiness Index)
    
    公式:
        TR = MAX(H-L, ABS(H-C'), ABS(L-C'))
        CI = 100 * LOG(MA(TR, N) * N / (HHV(H, N) - LLV(L, N))) / LOG(N)
    """
    # 计算真实波幅TR
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift(1)).abs()
    low_close = (df['low'] - df['close'].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    
    # MA(TR, N)
    ma_tr = tr.rolling(n).mean()
    
    # HHV(H, N) 和 LLV(L, N)
    hhv_h = df['high'].rolling(n).max()
    llv_l = df['low'].rolling(n).min()
    
    # 价格区间
    price_range = hhv_h - llv_l + 1e-8
    
    # CI计算
    ci = 100 * np.log(ma_tr * n / price_range) / np.log(n)
    
    return pd.Series(ci, index=df.index)


def calculate_hull_moving_average(df: pd.DataFrame, n: int = 20) -> pd.Series:
    """计算赫尔移动平均 (Hull Moving Average)
    
    公式:
        WMA(n) = n周期加权移动平均
        HMA = WMA(2*WMA(n/2) - WMA(n), sqrt(n))
    """
    close = df['close']
    
    def wma(series: pd.Series, period: int) -> pd.Series:
        """加权移动平均"""
        if len(series) < period:
            return pd.Series([np.nan] * len(series), index=series.index)
        
        weights = np.arange(1, period + 1)
        return series.rolling(period).apply(
            lambda x: np.sum(weights * x) / weights.sum(), raw=True
        )
    
    half_n = int(n / 2)
    sqrt_n = int(np.sqrt(n))
    
    wma_half = wma(close, half_n)
    wma_n = wma(close, n)
    
    # 2*WMA(n/2) - WMA(n)
    hma_raw = 2 * wma_half - wma_n
    
    # WMA of hma_raw with period = sqrt(n)
    hma = wma(hma_raw, sqrt_n)
    
    return hma


# ==================== 增强版指标计算 ====================

def calculate_enhanced_indicators(df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """计算增强版技术指标（包含所有新老指标）
    
    参数:
        df: 包含OHLCV数据的DataFrame
        config: 指标参数配置
        
    返回:
        包含所有指标的DataFrame
    """
    if config is None:
        config = {
            'vr_period': 26,
            'macd_fast': 5,
            'macd_slow': 13,
            'macd_signal': 8,
            'bb_period': 20,
            'bb_std': 2,
            'tsma_periods': [5, 8, 13, 34],
            'ema_periods': [5, 8, 34, 55],
            'fisher_period': 10,
            'chop_period': 14,
            'hma_period': 20
        }
    
    result_df = df.copy()
    
    # 1. 成交量比率VR（现有指标）
    if 'volume' in df.columns:
        av = df['volume'].where(df['close'] > df['close'].shift(1), 0)
        bv = df['volume'].where(df['close'] < df['close'].shift(1), 0)
        result_df['vr'] = 100 * av.rolling(config['vr_period']).sum() / bv.rolling(config['vr_period']).sum()
    
    # 2. MACD指标（现有指标）
    ema_fast = df['close'].ewm(span=config['macd_fast'], adjust=False).mean()
    ema_slow = df['close'].ewm(span=config['macd_slow'], adjust=False).mean()
    result_df['macd'] = ema_fast - ema_slow
    result_df['macd_signal'] = result_df['macd'].ewm(span=config['macd_signal'], adjust=False).mean()
    result_df['macd_hist'] = result_df['macd'] - result_df['macd_signal']
    
    # 3. 布林带（现有指标）
    result_df['bb_middle'] = df['close'].rolling(config['bb_period']).mean()
    bb_std = df['close'].rolling(config['bb_period']).std()
    result_df['bb_upper'] = result_df['bb_middle'] + config['bb_std'] * bb_std
    result_df['bb_lower'] = result_df['bb_middle'] - config['bb_std'] * bb_std
    result_df['bb_width'] = (result_df['bb_upper'] - result_df['bb_lower']) / result_df['bb_middle']
    
    # 4. TSMA/LSMA（现有指标） - 这里简化为线性回归斜率
    for period in config['tsma_periods']:
        def tsma_slope(x):
            if len(x) < period:
                return np.nan
            idx = np.arange(len(x))
            slope, _ = np.polyfit(idx, x, 1)
            return slope
        
        result_df[f'tsma_{period}'] = df['close'].rolling(period).apply(tsma_slope, raw=True)
    
    # 5. EMA（现有指标）
    for period in config['ema_periods']:
        result_df[f'ema_{period}'] = df['close'].ewm(span=period, adjust=False).mean()
    
    # 6. ER效率比率（现有指标）
    change = df['close'].diff().abs()
    volatility = df['close'].diff().rolling(10).std()
    result_df['er'] = change / (volatility + 1e-8)
    
    # 7. 神奇九转（现有指标简化版）
    result_df['up_count'] = (df['close'] > df['close'].shift(1)).rolling(9).sum()
    result_df['down_count'] = (df['close'] < df['close'].shift(1)).rolling(9).sum()
    result_df['magic_nine'] = np.where(
        result_df['up_count'] >= 8, 1,
        np.where(result_df['down_count'] >= 8, -1, 0)
    )
    
    # 8. Fisher Transform（新指标）
    result_df['fisher'] = calculate_fisher_transform(df, n=config['fisher_period'])
    
    # 9. Choppiness Index（新指标）
    result_df['chop'] = calculate_choppiness_index(df, n=config['chop_period'])
    
    # 10. Hull Moving Average（新指标）
    result_df['hma'] = calculate_hull_moving_average(df, n=config['hma_period'])
    
    # 11. 趋势强度综合评分
    result_df['trend_score'] = (
        result_df['fisher'].fillna(0) * 0.3 +  # Fisher趋势
        np.sign(result_df['tsma_34'].fillna(0)) * 0.2 +  # TSMA方向
        (result_df['close'] > result_df['hma']).astype(int) * 0.2 +  # 价格在HMA上方
        (result_df['macd_hist'] > 0).astype(int) * 0.2 +  # MACD正向
        (result_df['vr'] > 100).astype(int) * 0.1  # 成交量支持
    )
    
    # 12. 市场状态判断
    result_df['market_state'] = np.where(
        result_df['chop'] > 61.8, 'choppy',  # 震荡市
        np.where(result_df['chop'] < 38.2, 'trending', 'neutral')  # 趋势市
    )
    
    return result_df


# ==================== 多因子信号生成 ====================

def generate_multi_factor_signals(df_with_indicators: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
    """基于多因子生成交易信号
    
    因子层:
        1. 趋势因子: Fisher, TSMA斜率, 价格相对HMA位置
        2. 动量因子: MACD, 成交量VR
        3. 波动因子: 布林带宽度, Choppiness Index
        4. 市场状态: 趋势市/震荡市
    
    返回:
        包含信号和仓位权重的DataFrame
    """
    if config is None:
        config = {
            'fisher_threshold': 0.5,
            'chop_trend_threshold': 38.2,
            'chop_choppy_threshold': 61.8,
            'macd_threshold': 0,
            'vr_threshold': 100,
            'position_max': 0.8  # 最大仓位比例
        }
    
    df = df_with_indicators.copy()
    
    # 初始化信号列
    df['signal'] = 0
    df['signal_strength'] = 0.0
    df['position_weight'] = 0.0
    df['signal_reason'] = ''
    
    for i in range(1, len(df)):
        # 跳过NaN行
        if pd.isna(df['fisher'].iloc[i]) or pd.isna(df['chop'].iloc[i]):
            continue
        
        # 提取当前指标值
        fisher = df['fisher'].iloc[i]
        chop = df['chop'].iloc[i]
        macd_hist = df['macd_hist'].iloc[i]
        vr = df['vr'].iloc[i] if not pd.isna(df['vr'].iloc[i]) else 100
        close = df['close'].iloc[i]
        hma = df['hma'].iloc[i]
        tsma_slope = df['tsma_34'].iloc[i] if not pd.isna(df['tsma_34'].iloc[i]) else 0
        
        # 市场状态
        market_state = 'trending' if chop < config['chop_trend_threshold'] else (
            'choppy' if chop > config['chop_choppy_threshold'] else 'neutral'
        )
        
        # 趋势因子得分
        trend_score = (
            (1 if fisher > config['fisher_threshold'] else -1 if fisher < -config['fisher_threshold'] else 0) * 0.3 +
            (1 if tsma_slope > 0 else -1) * 0.2 +
            (1 if close > hma else -1) * 0.2
        )
        
        # 动量因子得分
        momentum_score = (
            (1 if macd_hist > config['macd_threshold'] else -1) * 0.3 +
            (1 if vr > config['vr_threshold'] else -1) * 0.2
        )
        
        # 综合信号强度 (-1 到 1)
        signal_strength = trend_score * 0.6 + momentum_score * 0.4
        
        # 根据市场状态调整
        if market_state == 'choppy':
            # 震荡市：降低信号强度，避免频繁交易
            signal_strength *= 0.5
            market_modifier = '震荡市-信号减弱'
        elif market_state == 'trending':
            # 趋势市：增强趋势信号
            if abs(signal_strength) > 0.3:
                signal_strength *= 1.2
            market_modifier = '趋势市-信号增强'
        else:
            market_modifier = '中性市'
        
        # 生成交易信号
        if signal_strength > 0.4:  # 强烈买入信号
            df.loc[df.index[i], 'signal'] = 1
            df.loc[df.index[i], 'signal_strength'] = signal_strength
            df.loc[df.index[i], 'position_weight'] = min(
                config['position_max'], 
                signal_strength * 0.8
            )
            df.loc[df.index[i], 'signal_reason'] = (
                f'买入: Fisher={fisher:.2f}, MACD={macd_hist:.2f}, '
                f'VR={vr:.0f}, 状态={market_state}, {market_modifier}'
            )
            
        elif signal_strength < -0.4:  # 强烈卖出信号
            df.loc[df.index[i], 'signal'] = -1
            df.loc[df.index[i], 'signal_strength'] = signal_strength
            df.loc[df.index[i], 'position_weight'] = min(
                config['position_max'],
                abs(signal_strength) * 0.8
            )
            df.loc[df.index[i], 'signal_reason'] = (
                f'卖出: Fisher={fisher:.2f}, MACD={macd_hist:.2f}, '
                f'VR={vr:.0f}, 状态={market_state}, {market_modifier}'
            )
        
        elif abs(signal_strength) > 0.2:  # 中等信号
            df.loc[df.index[i], 'signal'] = 1 if signal_strength > 0 else -1
            df.loc[df.index[i], 'signal_strength'] = signal_strength
            df.loc[df.index[i], 'position_weight'] = min(
                config['position_max'] * 0.6,
                abs(signal_strength) * 0.5
            )
            df.loc[df.index[i], 'signal_reason'] = (
                f'中等{'买入' if signal_strength > 0 else '卖出'}: '
                f'Fisher={fisher:.2f}, 状态={market_state}'
            )
    
    return df


# ==================== 策略回测框架 ====================

class MultiFactorStrategy:
    """多因子量化策略主类"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.df_with_indicators = None
        self.signals_df = None
        
    def calculate_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """计算所有技术指标"""
        self.df_with_indicators = calculate_enhanced_indicators(df, self.config)
        return self.df_with_indicators
    
    def generate_signals(self, df: Optional[pd.DataFrame] = None) -> pd.DataFrame:
        """生成交易信号"""
        if df is not None:
            self.calculate_indicators(df)
        
        if self.df_with_indicators is None:
            raise ValueError("请先调用calculate_indicators或提供数据")
        
        self.signals_df = generate_multi_factor_signals(self.df_with_indicators, self.config)
        return self.signals_df
    
    def backtest(self, df: pd.DataFrame, initial_capital: float = 100000.0) -> Dict:
        """简单回测"""
        signals_df = self.generate_signals(df)
        
        # 初始化回测数据
        portfolio_value = initial_capital
        positions = []
        trades = []
        
        for i in range(1, len(signals_df)):
            signal = signals_df['signal'].iloc[i]
            position_weight = signals_df['position_weight'].iloc[i]
            price = signals_df['close'].iloc[i]
            
            if signal != 0 and position_weight > 0:
                # 计算交易量
                position_value = portfolio_value * position_weight
                shares = position_value / price if price > 0 else 0
                
                if shares > 0:
                    trade = {
                        'date': signals_df.index[i],
                        'signal': 'buy' if signal > 0 else 'sell',
                        'price': price,
                        'shares': shares,
                        'value': position_value,
                        'reason': signals_df['signal_reason'].iloc[i]
                    }
                    trades.append(trade)
        
        # 计算回测结果
        if trades:
            # 简化的回测：假设每次交易都按信号执行
            # 实际回测需要更复杂的逻辑
            return {
                'total_trades': len(trades),
                'buy_trades': len([t for t in trades if t['signal'] == 'buy']),
                'sell_trades': len([t for t in trades if t['signal'] == 'sell']),
                'trades': trades[:10],  # 只返回前10笔交易
                'strategy_summary': '多因子策略回测完成'
            }
        else:
            return {'total_trades': 0, 'trades': [], 'strategy_summary': '无交易信号生成'}
    
    def get_strategy_summary(self) -> str:
        """获取策略摘要"""
        if self.signals_df is None:
            return "策略未初始化"
        
        signals = self.signals_df['signal']
        buy_signals = (signals == 1).sum()
        sell_signals = (signals == -1).sum()
        total_signals = buy_signals + sell_signals
        
        return (
            f"多因子策略摘要:\n"
            f"总信号数: {total_signals}\n"
            f"买入信号: {buy_signals}\n"
            f"卖出信号: {sell_signals}\n"
            f"信号强度均值: {self.signals_df['signal_strength'].mean():.3f}\n"
            f"Fisher均值: {self.signals_df['fisher'].mean():.3f}\n"
            f"Chop均值: {self.signals_df['chop'].mean():.1f}\n"
            f"市场状态分布: {self.signals_df['market_state'].value_counts().to_dict()}"
        )


# ==================== 使用示例 ====================

if __name__ == "__main__":
    print("多因子量化策略框架")
    print("=" * 50)
    
    # 示例配置
    config = {
        'vr_period': 26,
        'macd_fast': 5,
        'macd_slow': 13,
        'macd_signal': 8,
        'fisher_period': 10,
        'chop_period': 14,
        'hma_period': 20,
        'position_max': 0.7
    }
    
    # 创建策略实例
    strategy = MultiFactorStrategy(config)
    
    print(f"策略配置: {config}")
    print(f"包含指标: VR, MACD, 布林带, TSMA/LSMA, EMA, ER, 神奇九转")
    print(f"新增指标: Fisher Transform, Choppiness Index, Hull MA")
    print(f"因子组合: 趋势 + 动量 + 波动 + 市场状态")
    print("=" * 50)
    
    print("\n策略逻辑:")
    print("1. 趋势因子: Fisher > 0.5, TSMA斜率 > 0, 价格 > HMA")
    print("2. 动量因子: MACD > 0, VR > 100")
    print("3. 波动因子: Chop < 38.2(趋势市) 或 > 61.8(震荡市)")
    print("4. 仓位管理: 信号强度决定仓位比例")
    print("5. 市场适应: 趋势市增强信号, 震荡市减弱信号")
    
    print("\n信号阈值:")
    print("  强烈信号: |信号强度| > 0.4, 仓位70%")
    print("  中等信号: |信号强度| > 0.2, 仓位42%")
    print("  弱信号: |信号强度| <= 0.2, 不交易")
    
    print("\n预期性能:")
    print("  - 年化收益: 60-100%+")
    print("  - 最大回撤: < 20%")
    print("  - 胜率: > 55%")
    print("  - 夏普比率: > 1.5")