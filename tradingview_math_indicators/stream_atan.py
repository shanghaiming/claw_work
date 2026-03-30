"""
TV_stream_ATAN - TradingView风格的stream_ATAN数学变换指标

反正切函数，计算实数的反正切值 (流式版本，支持实时更新)
基于TA-Lib的stream_ATAN函数实现
生成时间: 2026-03-30 20:23:09
"""

import numpy as np
import pandas as pd
import talib

class TV_stream_ATAN:
    """TradingView风格的stream_ATAN数学变换指标"""
    
    def __init__(self):
        """初始化指标"""
        self.name = "stream_ATAN"
        self.description = "反正切函数，计算实数的反正切值 (流式版本，支持实时更新)"
        self.author = "OpenClaw量化系统"
        self.version = "1.0.0"
        
    def calculate(self, real):
        """
        计算stream_ATAN指标
        
        参数:
            real: 输入序列
        
        返回:
            result: 数学变换结果
        """
        try:
            result = talib.stream_ATAN(real)
            return result
        except Exception as e:
            print(f"计算指标{self.name}时出错: {e}")
            return None
    
    def signal(self, real, threshold=0.5):
        """
        生成交易信号（基于数学变换的极端值）
        
        参数:
            real: 输入序列
            threshold: 信号阈值
        
        返回:
            signal: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
        """
        try:
            values = self.calculate(real)
            if values is None:
                return np.zeros_like(real)
            
            # 数学变换信号的生成逻辑
            signal = np.zeros_like(values)
            
            # 根据函数类型生成不同的信号
            if "ATAN" in ["ACOS", "ASIN"]:
                # 反三角函数，值域在特定范围内
                for i in range(1, len(values)):
                    if values[i] > threshold and values[i-1] <= threshold:
                        signal[i] = -1  # 值过高，卖出信号
                    elif values[i] < -threshold and values[i-1] >= -threshold:
                        signal[i] = 1   # 值过低，买入信号
                        
            elif "ATAN" in ["CEIL", "FLOOR"]:
                # 取整函数，检测整数关口突破
                for i in range(1, len(values)):
                    if abs(values[i] - values[i-1]) >= 0.9:  # 接近整数变化
                        if values[i] > values[i-1]:
                            signal[i] = 1   # 向上突破整数关口
                        else:
                            signal[i] = -1  # 向下跌破整数关口
                            
            elif "ATAN" in ["EXP", "LN", "LOG10"]:
                # 指数和对数函数，检测增长率变化
                for i in range(2, len(values)):
                    if values[i-1] != 0:
                        growth = values[i] / values[i-1]
                        if growth > 1 + threshold:
                            signal[i] = 1   # 快速增长
                        elif growth < 1 - threshold:
                            signal[i] = -1  # 快速下降
                            
            elif "ATAN" in ["SIN", "COS", "TAN", "SINH", "COSH", "TANH"]:
                # 三角函数，检测周期性变化
                for i in range(1, len(values)):
                    if values[i] > threshold and values[i-1] <= threshold:
                        signal[i] = -1  # 达到峰值
                    elif values[i] < -threshold and values[i-1] >= -threshold:
                        signal[i] = 1   # 达到谷值
                        
            elif "ATAN" == "SQRT":
                # 平方根函数，检测平方根增长率
                for i in range(2, len(values)):
                    if values[i-1] > 0:
                        growth = values[i] / values[i-1]
                        if growth > 1 + threshold/2:
                            signal[i] = 1   # 快速增长
                        elif growth < 1 - threshold/2:
                            signal[i] = -1  # 快速下降
            
            return signal
        except Exception as e:
            print(f"生成信号时出错: {e}")
            return np.zeros_like(real)
    
    def plot_style(self):
        """返回绘图样式配置"""
        # 根据函数类型选择颜色
        color_map = {
            "ACOS": "#FF6B6B",
            "ASIN": "#4ECDC4", 
            "ATAN": "#45B7D1",
            "CEIL": "#96CEB4",
            "COS": "#FECA57",
            "COSH": "#FF9FF3",
            "EXP": "#54A0FF",
            "FLOOR": "#5F27CD",
            "LN": "#00D2D3",
            "LOG10": "#FF9F43",
            "SIN": "#EE5A24",
            "SINH": "#C4E538",
            "SQRT": "#12CBC4",
            "TAN": "#FDA7DF",
            "TANH": "#ED4C67"
        }
        
        color = color_map.get("ATAN", "#2962FF")
        
        return {
            "name": self.name,
            "type": "line",
            "color": color,
            "linewidth": 1,
            "title": self.name,
            "trackPrice": False,
            "description": self.description
        }

def stream_atan(real):
    """
    简化的函数接口
    
    参数:
        real: 输入序列
    
    返回:
        result: 数学变换结果
    """
    indicator = TV_stream_ATAN()
    return indicator.calculate(real)

if __name__ == "__main__":
    # 测试代码
    np.random.seed(42)
    n = 100
    
    # 生成测试数据
    real = np.random.uniform(-0.9, 0.9, n)  # 对于三角函数，保持在定义域内
    
    # 特殊处理某些函数
    if "ATAN" in ["SQRT", "LN", "LOG10"]:
        real = np.random.uniform(0.1, 10, n)  # 正数
    elif "ATAN" in ["ACOS", "ASIN"]:
        real = np.random.uniform(-0.9, 0.9, n)  # 保持在[-1, 1]范围内
    
    # 创建指标实例
    indicator = TV_stream_ATAN()
    
    # 测试计算
    try:
        result = indicator.calculate(real)
        print(f"{indicator.name} 测试完成")
        print(f"结果形状: {result.shape if hasattr(result, 'shape') else len(result)}")
        print(f"前10个值: {result[:10] if hasattr(result, '__len__') else result}")
        
        # 测试信号生成
        signal = indicator.signal(real, threshold=0.5)
        print(f"信号统计 - 买入: {np.sum(signal == 1)}, 卖出: {np.sum(signal == -1)}, 持有: {np.sum(signal == 0)}")
    except Exception as e:
        print(f"测试失败: {e}")
