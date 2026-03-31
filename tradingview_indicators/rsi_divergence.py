"""
RSI Divergence - RSI背离检测，识别潜在的反转点

来源: TradingView社区
转换时间: 2026-03-29 22:32:49
"""

import numpy as np
import pandas as pd

def rsi_divergence(high, low, close, rsi_period=14, lookback=20):
    """
    RSI背离检测
    识别价格与RSI之间的背离
    
    参数:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        rsi_period: RSI周期 (默认14)
        lookback: 回顾周期 (默认20)
    
    返回:
        bullish_divergence: 看涨背离信号 (True/False)
        bearish_divergence: 看跌背离信号 (True/False)
        rsi_values: RSI值
    """
    import talib
    
    # 计算RSI
    rsi = talib.RSI(close, timeperiod=rsi_period)
    
    # 初始化信号数组
    bullish_divergence = np.zeros_like(close, dtype=bool)
    bearish_divergence = np.zeros_like(close, dtype=bool)
    
    # 检测背离
    for i in range(lookback, len(close)):
        # 查找价格和RSI的极值点
        price_window = close[i-lookback:i+1]
        rsi_window = rsi[i-lookback:i+1]
        
        # 寻找价格高点但RSI低点（看跌背离）
        price_high_idx = np.argmax(price_window)
        rsi_low_idx = np.argmin(rsi_window)
        
        if price_high_idx > 0 and price_high_idx < len(price_window)-1:
            if rsi_low_idx > 0 and rsi_low_idx < len(rsi_window)-1:
                # 价格创新高但RSI未创新高
                if price_high_idx == len(price_window)-1 and rsi_low_idx == len(rsi_window)-1:
                    if rsi_window[-1] < rsi_window[-2] and price_window[-1] > price_window[-2]:
                        bearish_divergence[i] = True
        
        # 寻找价格低点但RSI高点（看涨背离）
        price_low_idx = np.argmin(price_window)
        rsi_high_idx = np.argmax(rsi_window)
        
        if price_low_idx > 0 and price_low_idx < len(price_window)-1:
            if rsi_high_idx > 0 and rsi_high_idx < len(rsi_window)-1:
                # 价格创新低但RSI未创新低
                if price_low_idx == len(price_window)-1 and rsi_high_idx == len(rsi_window)-1:
                    if rsi_window[-1] > rsi_window[-2] and price_window[-1] < price_window[-2]:
                        bullish_divergence[i] = True
    
    return bullish_divergence, bearish_divergence, rsi

if __name__ == "__main__":
    # 测试代码
    # 测试数据
    np.random.seed(42)
    n = 100
    close = np.cumsum(np.random.randn(n)) + 100
    high = close + np.random.uniform(0, 2, n)
    low = close - np.random.uniform(0, 2, n)
    
    # 运行示例
    try:
        # 使用示例
        bullish, bearish, rsi_values = rsi_divergence(high, low, close, rsi_period=14, lookback=20)
        print(f"RSI Divergence 测试完成")
    except Exception as e:
        print(f"测试出错: {e}")