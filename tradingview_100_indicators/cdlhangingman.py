"""
TV_CDLHANGINGMAN - TradingView风格的CDLHANGINGMAN指标

基于TA-Lib的CDLHANGINGMAN函数实现
生成时间: 2026-03-30 18:53:47
"""

import numpy as np
import pandas as pd
import talib

class TV_CDLHANGINGMAN:
    """TradingView风格的CDLHANGINGMAN指标"""
    
    def __init__(self):
        """初始化指标"""
        self.name = "CDLHANGINGMAN"
        self.description = "基于TA-Lib CDLHANGINGMAN函数的TradingView风格实现"
        self.author = "OpenClaw量化系统"
        self.version = "1.0.0"
        
    def calculate(self, open, high, low, close):
        """
        计算CDLHANGINGMAN指标
        
        参数:
        open: open序列
        high: high序列
        low: low序列
        close: close序列

        返回:
            result: 指标结果
        """
        try:
            result = talib.CDLHANGINGMAN(open, high, low, close)
            return result
        except Exception as e:
            print(f"计算指标{self.name}时出错: {e}")
            return None
    
    def signal(self, open, high, low, close, threshold=0):
        """
        生成交易信号
        
        参数:
        open: open序列
        high: high序列
        low: low序列
        close: close序列

            threshold: 信号阈值
        
        返回:
            signal: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
        """
        try:
            values = self.calculate(open, high, low, close)
            if values is None:
                return np.zeros_like(open)
            
            # 默认信号生成逻辑（可根据指标类型定制）
            signal = np.zeros_like(values)
            
            # 简单阈值信号
            if len(values.shape) == 1:  # 一维数组
                for i in range(1, len(values)):
                    if values[i] > threshold and values[i-1] <= threshold:
                        signal[i] = 1  # 买入
                    elif values[i] < -threshold and values[i-1] >= -threshold:
                        signal[i] = -1  # 卖出
            else:
                # 多维数组，取第一列
                if values.shape[1] > 0:
                    col_values = values[:, 0]
                    for i in range(1, len(col_values)):
                        if col_values[i] > threshold and col_values[i-1] <= threshold:
                            signal[i] = 1
                        elif col_values[i] < -threshold and col_values[i-1] >= -threshold:
                            signal[i] = -1
            
            return signal
        except Exception as e:
            print(f"生成信号时出错: {e}")
            return np.zeros_like(open)
    
    def plot_style(self):
        """返回绘图样式配置"""
        return {
            "name": self.name,
            "type": "line",
            "color": "#2962FF",
            "linewidth": 1,
            "title": self.name,
            "trackPrice": True
        }

def cdlhangingman(open, high, low, close):
    """
    简化的函数接口
    
    参数:
        open: open序列
        high: high序列
        low: low序列
        close: close序列

    返回:
        result: 指标结果
    """
    indicator = TV_CDLHANGINGMAN()
    return indicator.calculate(open, high, low, close)

if __name__ == "__main__":
    # 测试代码
    np.random.seed(42)
    n = 100
    
    # 生成测试数据
    high = np.random.uniform(100, 110, n)
    low = np.random.uniform(90, 100, n)
    close = np.random.uniform(95, 105, n)
    
    # 创建指标实例
    indicator = TV_CDLHANGINGMAN()
    
    # 测试计算
    try:
        result = indicator.calculate(open, high, low, close)
        print(f"{indicator.name} 测试完成")
        print(f"结果形状: {result.shape if hasattr(result, 'shape') else len(result)}")
        print(f"前10个值: {result[:10] if hasattr(result, '__len__') else result}")
        
        # 测试信号生成
        signal = indicator.signal(open, high, low, close, threshold=0)
        print(f"信号统计 - 买入: {np.sum(signal == 1)}, 卖出: {np.sum(signal == -1)}, 持有: {np.sum(signal == 0)}")
    except Exception as e:
        print(f"测试失败: {e}")
