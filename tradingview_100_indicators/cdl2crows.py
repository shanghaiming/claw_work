"""
CDL2CROWS - 蜡烛图形态识别指标

基于TA-Lib的CDL2CROWS函数实现
生成时间: 2026-03-30 18:55:49
"""

import numpy as np
import talib

class TV_CDL2CROWS:
    """TradingView风格的CDL2CROWS蜡烛图形态指标"""
    
    def __init__(self):
        """初始化指标"""
        self.name = "CDL2CROWS"
        self.description = "蜡烛图形态识别: CDL2CROWS"
        self.author = "OpenClaw量化系统"
        self.version = "1.0.0"
        
    def calculate(self, open, high, low, close):
        """
        计算CDL2CROWS形态
        
        参数:
            open: 开盘价序列
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
        
        返回:
            result: 形态识别结果 (通常为0, 100, -100)
        """
        try:
            result = talib.CDL2CROWS(open, high, low, close)
            return result
        except Exception as e:
            print(f"计算指标{self.name}时出错: {e}")
            return None
    
    def signal(self, open, high, low, close):
        """
        生成交易信号
        
        参数:
            open: 开盘价序列
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
        
        返回:
            signal: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
        """
        try:
            values = self.calculate(open, high, low, close)
            if values is None:
                return np.zeros_like(close)
            
            # 蜡烛图形态信号: 通常正数表示看涨，负数表示看跌
            signal = np.zeros_like(values)
            
            for i in range(len(values)):
                if values[i] > 0:
                    signal[i] = 1  # 看涨信号
                elif values[i] < 0:
                    signal[i] = -1  # 看跌信号
            
            return signal
        except Exception as e:
            print(f"生成信号时出错: {e}")
            return np.zeros_like(close)
    
    def plot_style(self):
        """返回绘图样式配置"""
        return {
            "name": self.name,
            "type": "histogram",
            "color": "#FF6B6B",
            "linewidth": 1,
            "title": self.name,
            "trackPrice": False
        }

def cdl2crows(open, high, low, close):
    """
    简化的函数接口
    
    参数:
        open: 开盘价序列
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
    
    返回:
        result: 形态识别结果
    """
    indicator = TV_CDL2CROWS()
    return indicator.calculate(open, high, low, close)

if __name__ == "__main__":
    # 测试代码
    np.random.seed(42)
    n = 100
    
    # 生成测试数据
    open = np.random.uniform(95, 105, n)
    high = np.random.uniform(100, 110, n)
    low = np.random.uniform(90, 100, n)
    close = np.random.uniform(95, 105, n)
    
    # 创建指标实例
    indicator = TV_CDL2CROWS()
    
    # 测试计算
    try:
        result = indicator.calculate(open, high, low, close)
        print(f"{indicator.name} 测试完成")
        print(f"结果形状: {result.shape if hasattr(result, 'shape') else len(result)}")
        print(f"前10个值: {result[:10] if hasattr(result, '__len__') else result}")
        
        # 测试信号生成
        signal = indicator.signal(open, high, low, close)
        print(f"信号统计 - 买入: {np.sum(signal == 1)}, 卖出: {np.sum(signal == -1)}, 持有: {np.sum(signal == 0)}")
    except Exception as e:
        print(f"测试失败: {e}")
