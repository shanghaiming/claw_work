"""
Supertrend - 超级趋势指标，结合ATR和价格来识别趋势方向

来源: TradingView社区
转换时间: 2026-03-29 22:32:49
"""

import numpy as np
import pandas as pd

def supertrend(high, low, close, atr_period=10, multiplier=3):
    """
    Supertrend指标实现
    基于: https://www.tradingview.com/script/6MEXgS6m-Supertrend-Indicator/
    
    参数:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        atr_period: ATR周期 (默认10)
        multiplier: 乘数 (默认3)
    
    返回:
        supertrend: Supertrend值
        direction: 方向 (1: 上升, -1: 下降)
    """
    import talib
    
    # 计算ATR
    atr = talib.ATR(high, low, close, timeperiod=atr_period)
    
    # 计算上下轨道
    hl2 = (high + low) / 2
    
    upper_band = hl2 + (multiplier * atr)
    lower_band = hl2 - (multiplier * atr)
    
    # 初始化数组
    supertrend = np.zeros_like(close)
    direction = np.zeros_like(close)
    
    # 计算Supertrend
    for i in range(1, len(close)):
        if close[i] > upper_band[i-1]:
            direction[i] = 1
            supertrend[i] = lower_band[i]
        elif close[i] < lower_band[i-1]:
            direction[i] = -1
            supertrend[i] = upper_band[i]
        else:
            direction[i] = direction[i-1]
            if direction[i] == 1:
                supertrend[i] = max(lower_band[i], supertrend[i-1])
            else:
                supertrend[i] = min(upper_band[i], supertrend[i-1])
    
    return supertrend, direction

if __name__ == "__main__":
    # 测试代码
    # 测试数据
    np.random.seed(42)
    n = 100
    high = np.random.uniform(100, 110, n)
    low = np.random.uniform(90, 100, n)
    close = np.random.uniform(95, 105, n)
    
    # 运行示例
    try:
        # 使用示例
        supertrend_values, direction = supertrend(high, low, close, atr_period=10, multiplier=3)
        print(f"Supertrend 测试完成")
        print(f"Supertrend值前10个: {supertrend_values[:10]}")
        print(f"方向前10个: {direction[:10]}")
    except Exception as e:
        print(f"测试出错: {e}")