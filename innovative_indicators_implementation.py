#!/usr/bin/env python3
"""
创新指标实现 - 体现TradingView社区设计思想

实现4个代表性的TradingView社区指标，并通过代码架构体现其设计思想：
1. Supertrend - 自适应趋势跟踪设计
2. Volume Profile - 成交量分析设计  
3. ATR Trailing Stop - 风险管理设计
4. RSI Divergence - 传统指标创新设计

每个指标实现都包含：
1. 完整的功能实现
2. 设计思想注释
3. 架构特点说明
4. 交易哲学体现
"""

import numpy as np
import pandas as pd
import talib
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum

print("=" * 80)
print("🎨 创新指标实现 - 体现TradingView社区设计思想")
print("=" * 80)

class DesignPhilosophy(Enum):
    """设计哲学"""
    TREND_FOLLOWING = "趋势跟踪"
    RISK_MANAGEMENT = "风险管理"
    VOLUME_ANALYSIS = "成交量分析"
    MEAN_REVERSION = "均值回归"
    ADAPTIVE_DESIGN = "自适应设计"
    VISUALIZATION = "可视化设计"
    COMPOSITE_SYSTEM = "复合系统"

@dataclass
class IndicatorDesign:
    """指标设计说明"""
    philosophy: DesignPhilosophy
    key_features: List[str]
    innovation_points: List[str]
    trading_insights: List[str]
    implementation_notes: List[str]

class SupertrendIndicator:
    """
    Supertrend指标实现 - 体现自适应趋势跟踪设计思想
    
    设计思想:
    1. 自适应设计: 根据市场波动率(ATR)动态调整趋势线
    2. 趋势可视化: 明确的多空颜色标识，直观展示趋势方向
    3. 风险管理集成: 内置止损逻辑，趋势反转时自动切换
    4. 简单实用: 复杂算法，简单信号
    
    交易哲学: "让趋势可视化，让止损自动化"
    """
    
    def __init__(self, atr_period: int = 10, multiplier: float = 3.0):
        """
        初始化Supertrend指标
        
        参数设计思想:
        - atr_period: 波动率观察周期，体现自适应设计的参数可调性
        - multiplier: 趋势灵敏度，体现用户自定义的灵活性
        """
        self.atr_period = atr_period
        self.multiplier = multiplier
        self.design = IndicatorDesign(
            philosophy=DesignPhilosophy.ADAPTIVE_DESIGN,
            key_features=[
                "基于ATR的自适应轨道宽度",
                "动态趋势方向识别",
                "内置止损止盈逻辑",
                "直观的多空颜色标识"
            ],
            innovation_points=[
                "将波动率分析与趋势跟踪结合",
                "可视化趋势强度和方向",
                "集成风险管理功能到趋势指标中"
            ],
            trading_insights=[
                "趋势跟踪应该在波动率适应的轨道内进行",
                "止损应该随着趋势发展而移动",
                "明确的视觉信号减少主观判断"
            ],
            implementation_notes=[
                "使用ATR作为波动率基准，确保适应不同市场条件",
                "上下轨道的动态计算体现自适应设计思想",
                "趋势方向的连续跟踪体现趋势跟踪哲学"
            ]
        )
    
    def calculate(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        计算Supertrend指标
        
        算法设计思想:
        1. 使用ATR衡量市场波动率，体现自适应设计
        2. 根据波动率动态计算上下轨道，体现风险管理
        3. 跟踪价格与轨道的关系确定趋势方向，体现趋势跟踪
        """
        # 计算ATR - 波动率基准
        atr = talib.ATR(high, low, close, timeperiod=self.atr_period)
        
        # 计算基础线 - HL2 (最高最低平均)
        hl2 = (high + low) / 2
        
        # 计算上下轨道 - 体现自适应设计
        upper_band = hl2 + (self.multiplier * atr)
        lower_band = hl2 - (self.multiplier * atr)
        
        # 初始化数组
        supertrend = np.zeros_like(close)
        direction = np.zeros_like(close)  # 1: 上升趋势, -1: 下降趋势
        
        # 核心算法 - 体现趋势跟踪和风险管理集成
        for i in range(1, len(close)):
            if close[i] > upper_band[i-1]:
                # 价格突破上轨，转为上升趋势 - 体现突破交易思想
                direction[i] = 1
                supertrend[i] = lower_band[i]  # 止损设在下降轨
            elif close[i] < lower_band[i-1]:
                # 价格突破下轨，转为下降趋势
                direction[i] = -1
                supertrend[i] = upper_band[i]  # 止损设在上升轨
            else:
                # 趋势延续 - 体现趋势持续性思想
                direction[i] = direction[i-1]
                if direction[i] == 1:
                    # 上升趋势中，止损线上移但不下降 - 体现让利润奔跑
                    supertrend[i] = max(lower_band[i], supertrend[i-1])
                else:
                    # 下降趋势中，止损线下移但不上升
                    supertrend[i] = min(upper_band[i], supertrend[i-1])
        
        return supertrend, direction
    
    def generate_signals(self, supertrend: np.ndarray, direction: np.ndarray) -> np.ndarray:
        """
        生成交易信号
        
        信号设计思想:
        1. 趋势方向变化时产生信号，减少频繁交易
        2. 明确的买卖点，避免模糊判断
        3. 集成风险管理，信号包含止损信息
        """
        signals = np.zeros_like(supertrend)
        
        for i in range(1, len(direction)):
            if direction[i] == 1 and direction[i-1] == -1:
                # 从下降趋势转为上升趋势 - 买入信号
                signals[i] = 1
            elif direction[i] == -1 and direction[i-1] == 1:
                # 从上升趋势转为下降趋势 - 卖出信号
                signals[i] = -1
        
        return signals
    
    def plot_config(self) -> Dict[str, Any]:
        """可视化配置 - 体现可视化设计思想"""
        return {
            'name': 'Supertrend',
            'type': 'line',
            'colors': {
                'uptrend': '#26A69A',  # 绿色代表上升趋势
                'downtrend': '#EF5350'  # 红色代表下降趋势
            },
            'line_width': 2,
            'title': 'Supertrend - 自适应趋势跟踪',
            'description': '基于ATR的自适应趋势指标，集成风险管理'
        }

class VolumeProfileIndicator:
    """
    Volume Profile指标实现 - 体现成交量分析设计思想
    
    设计思想:
    1. 三维分析: 价格 × 时间 × 成交量
    2. 市场结构: 识别关键价格水平和支撑阻力
    3. 行为分析: 反映机构和大资金行为
    4. 价值区域: 识别高成交量价格区域
    
    交易哲学: "价格需要成交量确认，关键价位有成交量聚集"
    """
    
    def __init__(self, price_bins: int = 24, lookback_period: int = 20):
        """
        初始化Volume Profile指标
        
        参数设计思想:
        - price_bins: 价格区间数量，体现分析的粒度
        - lookback_period: 观察周期，体现时间维度分析
        """
        self.price_bins = price_bins
        self.lookback_period = lookback_period
        self.design = IndicatorDesign(
            philosophy=DesignPhilosophy.VOLUME_ANALYSIS,
            key_features=[
                "价格维度的成交量分布",
                "关键价格水平识别",
                "市场结构分析",
                "价值区域定位"
            ],
            innovation_points=[
                "将成交量分析从时间维度扩展到价格维度",
                "识别支撑阻力的成交量证据",
                "分析机构资金的行为模式"
            ],
            trading_insights=[
                "高成交量价格区域有更强支撑阻力",
                "价格突破需要成交量确认",
                "市场结构决定价格行为"
            ],
            implementation_notes=[
                "价格分箱处理体现结构化分析思想",
                "成交量累积计算反映资金聚集",
                "百分比分析提供标准化视角"
            ]
        )
    
    def calculate(self, high: np.ndarray, low: np.ndarray, close: np.ndarray, 
                  volume: np.ndarray) -> Dict[str, Any]:
        """
        计算Volume Profile
        
        算法设计思想:
        1. 价格分箱: 将价格范围分成多个区间，体现结构化分析
        2. 成交量分配: 将成交量分配到对应价格区间，体现三维分析
        3. 累积统计: 计算每个价格区间的累计成交量，体现资金聚集
        """
        if len(close) < self.lookback_period:
            raise ValueError(f"数据长度不足，至少需要 {self.lookback_period} 个数据点")
        
        # 使用最近lookback_period个数据
        recent_high = high[-self.lookback_period:]
        recent_low = low[-self.lookback_period:]
        recent_close = close[-self.lookback_period:]
        recent_volume = volume[-self.lookback_period:]
        
        # 确定价格范围 - 体现市场结构分析
        price_min = np.min(recent_low)
        price_max = np.max(recent_high)
        price_range = price_max - price_min
        
        if price_range == 0:
            # 价格没有波动的情况
            return {
                'price_levels': [price_min],
                'volume_profile': [np.sum(recent_volume)],
                'percentages': [100.0]
            }
        
        # 创建价格区间 - 体现结构化设计
        bin_width = price_range / self.price_bins
        price_levels = [price_min + i * bin_width for i in range(self.price_bins + 1)]
        
        # 初始化成交量分布数组
        volume_profile = np.zeros(self.price_bins)
        
        # 分配成交量到价格区间 - 核心算法体现成交量分析思想
        for i in range(len(recent_close)):
            price = recent_close[i]
            vol = recent_volume[i]
            
            # 确定价格所在的区间
            if price <= price_min:
                bin_idx = 0
            elif price >= price_max:
                bin_idx = self.price_bins - 1
            else:
                bin_idx = int((price - price_min) / bin_width)
                bin_idx = min(bin_idx, self.price_bins - 1)
            
            volume_profile[bin_idx] += vol
        
        # 计算百分比 - 体现标准化分析
        total_volume = np.sum(volume_profile)
        if total_volume > 0:
            percentages = (volume_profile / total_volume) * 100
        else:
            percentages = np.zeros_like(volume_profile)
        
        # 识别关键水平 - 体现市场结构识别
        peak_indices = np.argsort(volume_profile)[-3:]  # 前3个高成交量区间
        key_levels = [price_levels[i] for i in peak_indices]
        
        # 计算价值区域 (VA) - 体现价值区域概念
        # 价值区域 = 成交量最高的70%价格区间
        sorted_indices = np.argsort(volume_profile)[::-1]
        cumulative_percentage = 0
        value_area_indices = []
        
        for idx in sorted_indices:
            cumulative_percentage += percentages[idx]
            value_area_indices.append(idx)
            if cumulative_percentage >= 70:
                break
        
        value_area_prices = [price_levels[i] for i in sorted(value_area_indices)]
        value_area_low = min(value_area_prices)
        value_area_high = max(value_area_prices)
        
        return {
            'price_levels': price_levels,
            'volume_profile': volume_profile.tolist(),
            'percentages': percentages.tolist(),
            'key_levels': key_levels,
            'value_area': {
                'low': value_area_low,
                'high': value_area_high,
                'indices': value_area_indices
            },
            'total_volume': total_volume,
            'price_range': {
                'min': price_min,
                'max': price_max,
                'range': price_range
            }
        }
    
    def analyze_structure(self, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析市场结构 - 体现市场结构分析思想
        """
        price_levels = profile_data['price_levels']
        volume_profile = profile_data['volume_profile']
        
        # 识别支撑阻力 - 高成交量价格水平
        support_levels = []
        resistance_levels = []
        
        for i in range(1, len(volume_profile) - 1):
            if volume_profile[i] > volume_profile[i-1] and volume_profile[i] > volume_profile[i+1]:
                # 局部峰值，可能是关键水平
                if i < len(volume_profile) / 2:
                    # 下半部分可能是支撑
                    support_levels.append({
                        'price': price_levels[i],
                        'volume': volume_profile[i],
                        'strength': volume_profile[i] / np.max(volume_profile)
                    })
                else:
                    # 上半部分可能是阻力
                    resistance_levels.append({
                        'price': price_levels[i],
                        'volume': volume_profile[i],
                        'strength': volume_profile[i] / np.max(volume_profile)
                    })
        
        # 按强度排序
        support_levels.sort(key=lambda x: x['strength'], reverse=True)
        resistance_levels.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'supports': support_levels[:3],  # 前3个最强支撑
            'resistances': resistance_levels[:3],  # 前3个最强阻力
            'balance_area': profile_data['value_area'],
            'market_condition': self.assess_market_condition(profile_data)
        }
    
    def assess_market_condition(self, profile_data: Dict[str, Any]) -> str:
        """评估市场状况"""
        value_area = profile_data['value_area']
        price_range = profile_data['price_range']
        
        va_width = value_area['high'] - value_area['low']
        range_ratio = va_width / price_range['range'] if price_range['range'] > 0 else 0
        
        if range_ratio < 0.3:
            return "趋势市场"  # 价值区域狭窄，趋势性强
        elif range_ratio < 0.6:
            return "平衡市场"  # 价值区域适中，市场平衡
        else:
            return "震荡市场"  # 价值区域宽广，市场震荡

class ATRTrailingStopIndicator:
    """
    ATR Trailing Stop指标实现 - 体现风险管理设计思想
    
    设计思想:
    1. 波动率适应: 止损基于市场波动率(ATR)动态调整
    2. 趋势保护: 止损随趋势发展而移动，保护利润
    3. 自动化管理: 减少主观判断，系统化风险管理
    4. 动态调整: 不同市场条件自动适应
    
    交易哲学: "风险管理应该适应市场波动"
    """
    
    def __init__(self, atr_period: int = 14, multiplier: float = 3.0):
        self.atr_period = atr_period
        self.multiplier = multiplier
        self.design = IndicatorDesign(
            philosophy=DesignPhilosophy.RISK_MANAGEMENT,
            key_features=[
                "基于ATR的动态止损",
                "趋势适应的止损移动",
                "自动化风险管理",
                "波动率敏感的参数设计"
            ],
            innovation_points=[
                "将波动率分析应用于风险管理",
                "动态止损替代固定止损",
                "集成趋势跟踪与风险管理"
            ],
            trading_insights=[
                "止损应该反映市场波动性",
                "盈利仓位需要保护但也要允许发展",
                "风险管理应该是系统化的而非主观的"
            ],
            implementation_notes=[
                "ATR作为波动率基准确保适应性",
                "止损只向有利方向移动体现趋势保护",
                "多空分别计算体现全面风险管理"
            ]
        )
    
    def calculate(self, high: np.ndarray, low: np.ndarray, close: np.ndarray) -> Dict[str, np.ndarray]:
        """
        计算ATR Trailing Stop
        
        算法设计思想:
        1. 使用ATR作为波动率基准，确保止损适应市场
        2. 止损只向有利方向移动，保护利润同时允许趋势发展
        3. 多空分别计算，全面管理风险
        """
        # 计算ATR - 波动率基准
        atr = talib.ATR(high, low, close, timeperiod=self.atr_period)
        
        # 初始化止损数组
        long_stop = np.zeros_like(close)
        short_stop = np.zeros_like(close)
        
        # 初始止损
        long_stop[0] = close[0] - (atr[0] * self.multiplier)
        short_stop[0] = close[0] + (atr[0] * self.multiplier)
        
        # 动态计算止损 - 核心算法体现风险管理思想
        for i in range(1, len(close)):
            # 多头止损: 价格最高点 - ATR×乘数，且只上移不下移
            potential_long_stop = np.max(high[:i+1]) - (atr[i] * self.multiplier)
            long_stop[i] = max(potential_long_stop, long_stop[i-1])
            
            # 空头止损: 价格最低点 + ATR×乘数，且只下移不上移
            potential_short_stop = np.min(low[:i+1]) + (atr[i] * self.multiplier)
            short_stop[i] = min(potential_short_stop, short_stop[i-1])
        
        # 生成信号
        signals = np.zeros_like(close)
        position = 0  # 0: 无仓位, 1: 多头, -1: 空头
        
        for i in range(1, len(close)):
            if position == 0:
                # 无仓位，寻找入场机会
                if close[i] > short_stop[i]:
                    signals[i] = 1  # 突破空头止损，做多
                    position = 1
                elif close[i] < long_stop[i]:
                    signals[i] = -1  # 跌破多头止损，做空
                    position = -1
            elif position == 1:
                # 多头仓位，检查止损
                if close[i] < long_stop[i]:
                    signals[i] = -1  # 跌破止损，平多翻空
                    position = -1
            else:  # position == -1
                # 空头仓位，检查止损
                if close[i] > short_stop[i]:
                    signals[i] = 1  # 突破止损，平空翻多
                    position = 1
        
        return {
            'long_stop': long_stop,
            'short_stop': short_stop,
            'signals': signals,
            'atr': atr
        }
    
    def risk_metrics(self, stops: Dict[str, np.ndarray], close: np.ndarray) -> Dict[str, float]:
        """
        计算风险指标 - 体现风险管理的量化分析
        """
        long_stop = stops['long_stop']
        short_stop = stops['short_stop']
        
        # 计算平均止损距离
        long_distances = close - long_stop
        short_distances = short_stop - close
        
        valid_long = long_distances[long_distances > 0]
        valid_short = short_distances[short_distances > 0]
        
        avg_long_distance = np.mean(valid_long) if len(valid_long) > 0 else 0
        avg_short_distance = np.mean(valid_short) if len(valid_short) > 0 else 0
        
        # 计算止损触发频率
        signals = stops['signals']
        stop_hits = np.sum(np.abs(signals) > 0)
        stop_frequency = stop_hits / len(signals) if len(signals) > 0 else 0
        
        return {
            'avg_long_stop_distance': avg_long_distance,
            'avg_short_stop_distance': avg_short_distance,
            'stop_hit_frequency': stop_frequency,
            'avg_atr': np.mean(stops['atr'][stops['atr'] > 0]) if np.any(stops['atr'] > 0) else 0,
            'risk_per_trade': np.mean([avg_long_distance, avg_short_distance]) if avg_long_distance > 0 and avg_short_distance > 0 else max(avg_long_distance, avg_short_distance)
        }

def main():
    """主函数 - 演示指标实现和设计思想"""
    print("🚀 启动创新指标实现演示")
    
    # 生成测试数据
    np.random.seed(42)
    n = 100
    dates = pd.date_range(start='2023-01-01', periods=n, freq='D')
    
    returns = np.random.normal(0.0005, 0.02, n)
    prices = 100 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices * (1 + np.random.normal(0, 0.01, n)),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.015, n))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.015, n))),
        'close': prices,
        'volume': np.random.randint(10000, 100000, n)
    }, index=dates)
    
    high = data['high'].values
    low = data['low'].values
    close = data['close'].values
    volume = data['volume'].values
    
    print(f"\n📊 测试数据: {n} 个数据点")
    
    # 1. Supertrend演示
    print("\n" + "=" * 60)
    print("1. Supertrend - 自适应趋势跟踪设计")
    print("=" * 60)
    
    supertrend_indicator = SupertrendIndicator(atr_period=10, multiplier=3.0)
    print(f"设计哲学: {supertrend_indicator.design.philosophy.value}")
    print(f"关键特性: {', '.join(supertrend_indicator.design.key_features[:3])}...")
    
    supertrend, direction = supertrend_indicator.calculate(high, low, close)
    signals = supertrend_indicator.generate_signals(supertrend, direction)
    
    print(f"趋势方向统计: 上升 {np.sum(direction == 1)}, 下降 {np.sum(direction == -1)}")
    print(f"交易信号: 买入 {np.sum(signals == 1)}, 卖出 {np.sum(signals == -1)}")
    
    # 2. Volume Profile演示
    print("\n" + "=" * 60)
    print("2. Volume Profile - 成交量分析设计")
    print("=" * 60)
    
    volume_profile_indicator = VolumeProfileIndicator(price_bins=24, lookback_period=20)
    print(f"设计哲学: {volume_profile_indicator.design.philosophy.value}")
    print(f"关键特性: {', '.join(volume_profile_indicator.design.key_features[:3])}...")
    
    profile_data = volume_profile_indicator.calculate(high, low, close, volume)
    structure_analysis = volume_profile_indicator.analyze_structure(profile_data)
    
    print(f"价格范围: {profile_data['price_range']['min']:.2f} - {profile_data['price_range']['max']:.2f}")
    print(f"价值区域: {profile_data['value_area']['low']:.2f} - {profile_data['value_area']['high']:.2f}")
    print(f"市场状况: {structure_analysis['market_condition']}")
    
    # 3. ATR Trailing Stop演示
    print("\n" + "=" * 60)
    print("3. ATR Trailing Stop - 风险管理设计")
    print("=" * 60)
    
    atr_stop_indicator = ATRTrailingStopIndicator(atr_period=14, multiplier=3.0)
    print(f"设计哲学: {atr_stop_indicator.design.philosophy.value}")
    print(f"关键特性: {', '.join(atr_stop_indicator.design.key_features[:3])}...")
    
    stops_data = atr_stop_indicator.calculate(high, low, close)
    risk_metrics = atr_stop_indicator.risk_metrics(stops_data, close)
    
    print(f"多头止损平均距离: {risk_metrics['avg_long_stop_distance']:.4f}")
    print(f"空头止损平均距离: {risk_metrics['avg_short_stop_distance']:.4f}")
    print(f"止损触发频率: {risk_metrics['stop_hit_frequency']:.2%}")
    print(f"每笔交易风险: {risk_metrics['risk_per_trade']:.4f}")
    
    print("\n" + "=" * 60)
    print("✅ 创新指标实现演示完成")
    print("=" * 60)
    
    print("\n🎯 设计思想总结:")
    print("1. Supertrend: 自适应设计 + 趋势可视化 + 风险管理集成")
    print("2. Volume Profile: 三维分析 + 市场结构识别 + 行为分析")
    print("3. ATR Trailing Stop: 波动率适应 + 趋势保护 + 自动化管理")
    
    print("\n💡 核心启示:")
    print("- 指标设计应该体现明确的交易哲学")
    print("- 技术创新应该服务于实际交易需求")
    print("- 风险管理应该内置到指标设计中")
    print("- 用户体验和可视化是重要设计考虑")
    
    return {
        'supertrend': (supertrend, direction, signals),
        'volume_profile': profile_data,
        'atr_trailing_stop': stops_data,
        'risk_metrics': risk_metrics
    }

if __name__ == "__main__":
    results = main()