"""
Pattern_Trend_Volume_Trinity - 复合系统模式指标

复合系统模式指标 #7: Pattern_Trend_Volume_Trinity
基于TradingView复合系统设计思想：
1. 整合多个基础指标 (ULTOSC, OBV, AROON)
2. 使用科学组合方法（加权、投票、分层）
3. 提供综合市场视角
4. 提高信号可靠性和稳定性

生成时间: 2026-03-30 20:27:04
设计模式: 复合系统模式
组合方法: 加权综合评分
"""

import numpy as np
import pandas as pd
import talib

class TV_Pattern_Trend_Volume_Trinity:
    """Pattern_Trend_Volume_Trinity - 复合系统模式指标"""
    
    def __init__(self):
        """初始化复合系统指标"""
        self.name = "Pattern_Trend_Volume_Trinity"
        self.description = "复合系统模式指标 #7: Pattern_Trend_Volume_Trinity"
        self.author = "OpenClaw量化系统"
        self.version = "1.0.0"
        self.base_indicators = ['ULTOSC', 'OBV', 'AROON']
        
        # 默认权重（可根据回测优化）
        self.weights = {
            "ULTOSC": 0.4,
            "OBV": 0.4,
            "AROON": 0.19,
        }
        
    def calculate_individual_indicators(self, high, low, close, volume=None):
        """计算各个基础指标"""
        results = {}
        
        try:
            # ULTOSC指标
            try:
                # 尝试计算指标
                indicator_value = talib.ULTOSC(close)
                if indicator_value is not None:
                    # 简单标准化
                    if len(indicator_value) > 0 and np.std(indicator_value) > 0:
                        results["ULTOSC"] = (indicator_value - np.mean(indicator_value)) / np.std(indicator_value)
                    else:
                        results["ULTOSC"] = indicator_value
            except:
                results["ULTOSC"] = np.zeros_like(close)
            
            # OBV指标
            try:
                # 尝试计算指标
                indicator_value = talib.OBV(close)
                if indicator_value is not None:
                    # 简单标准化
                    if len(indicator_value) > 0 and np.std(indicator_value) > 0:
                        results["OBV"] = (indicator_value - np.mean(indicator_value)) / np.std(indicator_value)
                    else:
                        results["OBV"] = indicator_value
            except:
                results["OBV"] = np.zeros_like(close)
            
            # AROON指标
            try:
                # 尝试计算指标
                indicator_value = talib.AROON(close)
                if indicator_value is not None:
                    # 简单标准化
                    if len(indicator_value) > 0 and np.std(indicator_value) > 0:
                        results["AROON"] = (indicator_value - np.mean(indicator_value)) / np.std(indicator_value)
                    else:
                        results["AROON"] = indicator_value
            except:
                results["AROON"] = np.zeros_like(close)
            
            return results
            
        except Exception as e:
            print(f"计算基础指标时出错: {e}")
            return {}
    
    def calculate_composite_score(self, individual_results):
        """计算复合系统评分"""
        composite_score = np.zeros_like(next(iter(individual_results.values())) if individual_results else np.array([]))
        
        for indicator, values in individual_results.items():
            if indicator in self.weights and len(values) == len(composite_score):
                weight = self.weights[indicator]
                composite_score += values * weight
        
        return composite_score
    
    def calculate(self, high, low, close, volume=None):
        """
        计算复合系统指标
        
        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列（可选）
        
        返回:
            composite_score: 复合系统评分
            individual_scores: 各个基础指标分数
            system_health: 系统健康度指标
        """
        try:
            # 计算各个基础指标
            individual_results = self.calculate_individual_indicators(high, low, close, volume)
            
            if not individual_results:
                return None, None, None
            
            # 计算复合评分
            composite_score = self.calculate_composite_score(individual_results)
            
            # 计算系统健康度（各指标一致性）
            if len(individual_results) > 1:
                # 计算指标间的相关性
                indicator_values = list(individual_results.values())
                if len(indicator_values[0]) > 10:
                    # 计算最近10个点的平均相关性
                    recent_values = [values[-10:] for values in indicator_values]
                    correlations = []
                    for i in range(len(recent_values)):
                        for j in range(i+1, len(recent_values)):
                            if len(recent_values[i]) == len(recent_values[j]):
                                corr = np.corrcoef(recent_values[i], recent_values[j])[0, 1]
                                if not np.isnan(corr):
                                    correlations.append(abs(corr))
                    
                    if correlations:
                        system_health = np.mean(correlations)
                    else:
                        system_health = 0.5
                else:
                    system_health = 0.5
            else:
                system_health = 1.0  # 只有一个指标，健康度最高
            
            # 包装结果
            result = {
                "composite_score": composite_score,
                "individual_scores": individual_results,
                "system_health": np.full_like(composite_score, system_health),
                "weights": self.weights
            }
            
            return result
            
        except Exception as e:
            print(f"计算复合系统指标{self.name}时出错: {e}")
            return None
    
    def signal(self, high, low, close, volume=None, threshold=0.3):
        """
        生成复合系统交易信号
        
        参数:
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
            volume: 成交量序列（可选）
            threshold: 信号阈值
        
        返回:
            signal: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
            signal_strength: 信号强度
        """
        try:
            result = self.calculate(high, low, close, volume)
            if result is None:
                return np.zeros_like(close), np.zeros_like(close)
            
            composite_score = result["composite_score"]
            system_health = result["system_health"][0] if len(result["system_health"]) > 0 else 0.5
            
            # 根据系统健康度调整阈值
            adjusted_threshold = threshold * (2.0 - system_health)  # 健康度越低，阈值越高
            
            signal = np.zeros_like(composite_score)
            signal_strength = np.zeros_like(composite_score)
            
            for i in range(1, len(composite_score)):
                if np.isnan(composite_score[i]) or np.isnan(composite_score[i-1]):
                    continue
                
                # 复合系统信号生成
                if composite_score[i] > adjusted_threshold and composite_score[i-1] <= adjusted_threshold:
                    signal[i] = 1  # 买入信号
                    signal_strength[i] = min(1.0, composite_score[i] * system_health)
                    
                elif composite_score[i] < -adjusted_threshold and composite_score[i-1] >= -adjusted_threshold:
                    signal[i] = -1  # 卖出信号
                    signal_strength[i] = min(1.0, abs(composite_score[i]) * system_health)
            
            return signal, signal_strength
            
        except Exception as e:
            print(f"生成复合系统信号时出错: {e}")
            return np.zeros_like(close), np.zeros_like(close)
    
    def plot_style(self):
        """返回绘图样式配置"""
        return {
            "name": self.name,
            "type": "line",
            "color": "#5C6BC0",  # 复合系统的紫色
            "linewidth": 2,
            "title": self.name,
            "description": self.description,
            "trackPrice": False,
            "style": "composite",  # 特殊样式标识
            "components": ['ULTOSC', 'OBV', 'AROON'],
            "weights": self.weights
        }

def pattern_trend_volume_trinity(high, low, close, volume=None):
    """
    简化的函数接口
    
    参数:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        volume: 成交量序列（可选）
    
    返回:
        composite_score: 复合系统评分
        individual_scores: 各个基础指标分数
        system_health: 系统健康度指标
    """
    indicator = TV_Pattern_Trend_Volume_Trinity()
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
    indicator = TV_Pattern_Trend_Volume_Trinity()
    
    # 测试计算
    try:
        result = indicator.calculate(high, low, close)
        print(f"{indicator.name} 测试完成")
        print(f"基础指标: {list(result['individual_scores'].keys()) if result else []}")
        print(f"权重配置: {indicator.weights}")
        print(f"系统健康度: {result['system_health'][0] if result and len(result['system_health']) > 0 else 0:.3f}")
        
        # 测试信号生成
        signal, signal_strength = indicator.signal(high, low, close, threshold=0.3)
        print(f"信号统计 - 买入: {np.sum(signal == 1)}, 卖出: {np.sum(signal == -1)}, 持有: {np.sum(signal == 0)}")
        print(f"平均信号强度: {np.mean(signal_strength[signal_strength > 0]) if np.any(signal_strength > 0) else 0:.3f}")
    except Exception as e:
        print(f"测试失败: {e}")
