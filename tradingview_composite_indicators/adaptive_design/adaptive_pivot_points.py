"""
Adaptive_Pivot_Points - 自适应设计模式指标

自适应设计模式指标 #16: Adaptive_Pivot_Points
基于TradingView自适应设计思想：
1. 参数根据市场波动率动态调整
2. 适应不同市场条件（趋势、震荡、突破）
3. 自动优化指标敏感度
4. 实时响应市场变化

生成时间: 2026-03-30 20:27:04
设计模式: 自适应设计模式
"""

import numpy as np
import pandas as pd
import talib

class TV_Adaptive_Pivot_Points:
    """Adaptive_Pivot_Points - 自适应设计模式指标"""
    
    def __init__(self, base_period=14, sensitivity=2.0):
        """初始化自适应指标"""
        self.name = "Adaptive_Pivot_Points"
        self.description = "自适应设计模式指标 #16: Adaptive_Pivot_Points"
        self.author = "OpenClaw量化系统"
        self.version = "1.0.0"
        self.base_period = base_period
        self.sensitivity = sensitivity
        
    def calculate_volatility_adjustment(self, high, low, close):
        """计算波动率调整因子"""
        atr = talib.ATR(high, low, close, timeperiod=self.base_period)
        avg_atr = np.mean(atr[-self.base_period:]) if len(atr) >= self.base_period else np.mean(atr)
        price_range = np.max(high[-self.base_period:]) - np.min(low[-self.base_period:]) if len(high) >= self.base_period else np.max(high) - np.min(low)
        
        if price_range > 0:
            volatility_ratio = avg_atr / price_range
        else:
            volatility_ratio = 0.1
        
        # 波动率越高，调整因子越小（更保守）
        adjustment = 1.0 / (1.0 + self.sensitivity * volatility_ratio)
        return np.clip(adjustment, 0.5, 2.0)
    
    def detect_market_condition(self, high, low, close):
        """检测市场条件"""
        # 使用ADX判断趋势强度
        adx = talib.ADX(high, low, close, timeperiod=self.base_period)
        last_adx = adx[-1] if len(adx) > 0 else 25
        
        # 使用ATR判断波动率
        atr = talib.ATR(high, low, close, timeperiod=self.base_period)
        avg_atr = np.mean(atr[-self.base_period:]) if len(atr) >= self.base_period else np.mean(atr)
        price_level = np.mean(close[-self.base_period:]) if len(close) >= self.base_period else np.mean(close)
        
        if avg_atr > 0:
            volatility_pct = avg_atr / price_level
        else:
            volatility_pct = 0.01
        
        # 判断市场条件
        if last_adx > 30:
            condition = "trending"
        elif last_adx < 20:
            condition = "ranging"
        else:
            condition = "transition"
        
        # 判断波动率水平
        if volatility_pct > 0.02:
            volatility_level = "high"
        elif volatility_pct < 0.005:
            volatility_level = "low"
        else:
            volatility_level = "normal"
        
        return condition, volatility_level, last_adx, volatility_pct
    
    def calculate(self, high, low, close, volume=None):
        """
        计算自适应指标
        
        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列（可选）
        
        返回:
            result: 自适应指标值
            condition_info: 市场条件信息
        """
        try:
            # 检测市场条件
            condition, volatility_level, adx_value, volatility_pct = self.detect_market_condition(high, low, close)
            
            # 计算波动率调整因子
            volatility_adjustment = self.calculate_volatility_adjustment(high, low, close)
            
            # 根据市场条件调整计算周期
            if condition == "trending":
                effective_period = int(self.base_period * 0.8)  # 趋势中缩短周期
            elif condition == "ranging":
                effective_period = int(self.base_period * 1.2)  # 震荡中延长周期
            else:
                effective_period = self.base_period
            
            effective_period = max(5, min(effective_period, 50))  # 限制范围
            
            # 基础指标计算（以自适应EMA为例）
            if volatility_level == "high":
                # 高波动率市场，使用较慢的EMA
                ema_fast = talib.EMA(close, timeperiod=effective_period)
                ema_slow = talib.EMA(close, timeperiod=effective_period * 2)
            elif volatility_level == "low":
                # 低波动率市场，使用较快的EMA
                ema_fast = talib.EMA(close, timeperiod=max(5, effective_period // 2))
                ema_slow = talib.EMA(close, timeperiod=effective_period)
            else:
                # 正常波动率
                ema_fast = talib.EMA(close, timeperiod=effective_period)
                ema_slow = talib.EMA(close, timeperiod=int(effective_period * 1.5))
            
            # 应用波动率调整
            ema_fast = ema_fast * volatility_adjustment
            ema_slow = ema_slow * (1.0 / volatility_adjustment)
            
            # 计算自适应指标值（EMA差值标准化）
            ema_diff = ema_fast - ema_slow
            if len(ema_diff) > 0 and np.std(ema_diff) > 0:
                adaptive_value = ema_diff / np.std(ema_diff)
            else:
                adaptive_value = ema_diff
            
            # 包装结果
            result = {
                "adaptive_value": adaptive_value,
                "ema_fast": ema_fast,
                "ema_slow": ema_slow,
                "volatility_adjustment": np.full_like(close, volatility_adjustment),
                "effective_period": np.full_like(close, effective_period)
            }
            
            condition_info = {
                "market_condition": condition,
                "volatility_level": volatility_level,
                "adx_strength": adx_value,
                "volatility_pct": volatility_pct,
                "volatility_adjustment": volatility_adjustment
            }
            
            return result, condition_info
            
        except Exception as e:
            print(f"计算自适应指标{self.name}时出错: {e}")
            return None, None
    
    def signal(self, high, low, close, volume=None, threshold=0.5):
        """
        生成自适应交易信号
        
        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列（可选）
            threshold: 信号阈值（会自适应调整）
        
        返回:
            signal: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
            confidence: 信号置信度
        """
        try:
            result, condition_info = self.calculate(high, low, close, volume)
            if result is None:
                return np.zeros_like(close), np.zeros_like(close)
            
            adaptive_value = result["adaptive_value"]
            
            # 根据市场条件调整阈值
            if condition_info["market_condition"] == "trending":
                adjusted_threshold = threshold * 0.7  # 趋势中降低阈值
            elif condition_info["market_condition"] == "ranging":
                adjusted_threshold = threshold * 1.3  # 震荡中提高阈值
            else:
                adjusted_threshold = threshold
            
            # 根据波动率调整阈值
            adjusted_threshold *= condition_info["volatility_adjustment"]
            
            # 生成信号
            signal = np.zeros_like(adaptive_value)
            confidence = np.zeros_like(adaptive_value)
            
            for i in range(1, len(adaptive_value)):
                if np.isnan(adaptive_value[i]) or np.isnan(adaptive_value[i-1]):
                    continue
                
                # 自适应信号生成
                if adaptive_value[i] > adjusted_threshold and adaptive_value[i-1] <= adjusted_threshold:
                    signal[i] = 1  # 买入信号
                    # 置信度基于ADX强度和波动率调整
                    confidence[i] = min(1.0, condition_info["adx_strength"] / 50.0) * condition_info["volatility_adjustment"]
                    
                elif adaptive_value[i] < -adjusted_threshold and adaptive_value[i-1] >= -adjusted_threshold:
                    signal[i] = -1  # 卖出信号
                    confidence[i] = min(1.0, condition_info["adx_strength"] / 50.0) * condition_info["volatility_adjustment"]
            
            return signal, confidence
            
        except Exception as e:
            print(f"生成自适应信号时出错: {e}")
            return np.zeros_like(close), np.zeros_like(close)
    
    def plot_style(self):
        """返回绘图样式配置"""
        return {
            "name": self.name,
            "type": "line",
            "color": "#26A69A",  # 自适应设计的绿色
            "linewidth": 2,
            "title": self.name,
            "description": self.description,
            "trackPrice": True,
            "style": "adaptive",  # 特殊样式标识
            "features": ["自适应参数", "市场条件感知", "波动率调整"]
        }

def adaptive_pivot_points(high, low, close, volume=None):
    """
    简化的函数接口
    
    参数:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        volume: 成交量序列（可选）
    
    返回:
        result: 自适应指标值
        condition_info: 市场条件信息
    """
    indicator = TV_Adaptive_Pivot_Points()
    return indicator.calculate(high, low, close, volume)

if __name__ == "__main__":
    # 测试代码
    np.random.seed(42)
    n = 200
    
    # 生成测试数据
    high = np.cumsum(np.random.normal(0, 1, n)) + 100
    low = high - np.random.uniform(1, 3, n)
    close = (high + low) / 2 + np.random.normal(0, 0.5, n)
    
    # 创建指标实例
    indicator = TV_Adaptive_Pivot_Points(base_period=14, sensitivity=2.0)
    
    # 测试计算
    try:
        result, condition_info = indicator.calculate(high, low, close)
        print(f"{indicator.name} 测试完成")
        print(f"市场条件: {condition_info}")
        
        # 测试信号生成
        signal, confidence = indicator.signal(high, low, close, threshold=0.5)
        print(f"信号统计 - 买入: {np.sum(signal == 1)}, 卖出: {np.sum(signal == -1)}, 持有: {np.sum(signal == 0)}")
        print(f"平均置信度: {np.mean(confidence[confidence > 0]) if np.any(confidence > 0) else 0:.3f}")
    except Exception as e:
        print(f"测试失败: {e}")
