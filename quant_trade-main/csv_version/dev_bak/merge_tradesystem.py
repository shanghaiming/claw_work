import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from enum import Enum
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional, Any
from datetime import datetime
import json
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')
from pathlib import Path
import os

# ==================== 基础数据结构和枚举定义 ====================

class MarketState(Enum):
    """市场状态枚举"""
    UNKNOWN = "未知"
    CLIMAX = "高潮"
    EXHAUSTION = "疲软"
    BREAKOUT = "突破"
    VACUUM = "真空"
    PULLBACK = "突破回撤"
    RESISTANCE = "反抗"
    # 趋势腿状态
    UP_LEG_1 = "第一条上涨腿"
    UP_LEG_2 = "第二条上涨腿"
    UP_LEG_3 = "第三条上涨腿"
    UP_LEG_PLUS = "上涨腿plus"
    DOWN_LEG_1 = "第一条下跌腿"
    DOWN_LEG_2 = "第二条下跌腿"
    DOWN_LEG_3 = "第三条下跌腿"
    DOWN_LEG_PLUS = "下跌腿plus"
    # 高低点状态
    HIGH_1 = "第一高点"
    HIGH_2 = "第二高点"
    HIGH_PLUS = "高点plus"
    LOW_1 = "第一低点"
    LOW_2 = "第二低点"
    LOW_PLUS = "低点plus"
    # 情绪状态
    CALM = "平静"
    GREED = "贪婪"
    PANIC = "恐慌"
    IGNORANCE = "无明"
    # 仓位状态
    NO_POSITION = "空仓"
    LONG = "多头"
    SHORT = "空头"

@dataclass
class TransitionResult:
    """状态跳转结果"""
    success: bool
    new_state: MarketState
    intermediate_state: Any = None
    reason: str = ""

@dataclass
class IntermediateState:
    """中间状态"""
    from_state: MarketState
    to_state: MarketState
    progress: float  # 0.0 to 1.0
    expected_duration: int  # 预计剩余时间

@dataclass
class KLine:
    """K线数据结构"""
    open: float
    close: float
    high: float
    low: float
    timestamp: datetime = None
    volume: float = 0.0
    
    def __post_init__(self):
        """初始化后确定K线方向"""
        if self.close > self.open:
            self.direction = KLineDirection.BULLISH
        elif self.close < self.open:
            self.direction = KLineDirection.BEARISH
        else:
            self.direction = KLineDirection.DOJI
    
    @property
    def body_length(self) -> float:
        """实体长度"""
        return abs(self.close - self.open)
    
    @property
    def total_length(self) -> float:
        """总长度"""
        return self.high - self.low
    
    @property
    def effective_high(self) -> float:
        """有效最高价（考虑影线阈值）"""
        upper_shadow = self.high - max(self.open, self.close)
        return self.high if upper_shadow > (self.body_length * 0.33) else max(self.open, self.close)
    
    @property
    def effective_low(self) -> float:
        """有效最低价（考虑影线阈值）"""
        lower_shadow = min(self.open, self.close) - self.low
        return self.low if lower_shadow > (self.body_length * 0.33) else min(self.open, self.close)

# ==================== K线关系分析模块 ====================

class KLineRelationship(Enum):
    """K线关系枚举"""
    CONTAINING = 1        # 前一根包含后一根
    CONTAINED = 2         # 前一根被后一根包含
    UPWARD_GAP = 3        # 向上缺口
    DOWNWARD_GAP = 4      # 向下缺口
    OVERLAP = 5           # 重叠
    SEPARATE = 6          # 分离
    NO_RELATIONSHIP = 7   # 无明确关系

class KLineDirection(Enum):
    """K线方向枚举"""
    BULLISH = 1  # 阳线
    BEARISH = 2  # 阴线
    DOJI = 3     # 十字星

class KLineRelationshipAnalyzer:
    """K线关系分析器"""
    
    def __init__(self):
        self.relationship_history = []
    
    def determine_relationship(self, kline1: KLine, kline2: KLine) -> KLineRelationship:
        """确定两根K线的关系"""
        k1_high, k1_low = kline1.effective_high, kline1.effective_low
        k2_high, k2_low = kline2.effective_high, kline2.effective_low
        
        if k2_low >= k1_low and k2_high <= k1_high:
            return KLineRelationship.CONTAINED
        if k1_low >= k2_low and k1_high <= k2_high:
            return KLineRelationship.CONTAINING
        if k2_low > k1_high:
            return KLineRelationship.UPWARD_GAP
        if k2_high < k1_low:
            return KLineRelationship.DOWNWARD_GAP
        if k2_low > k1_high or k2_high < k1_low:
            return KLineRelationship.SEPARATE
        if k2_low < k1_high and k2_high > k1_low:
            return KLineRelationship.OVERLAP
        return KLineRelationship.NO_RELATIONSHIP
    
    def calculate_gap(self, kline1: KLine, kline2: KLine) -> Dict[str, Any]:
        """计算两根K线之间的缺口"""
        upward_gap = max(0, kline2.effective_low - kline1.effective_high)
        downward_gap = max(0, kline1.effective_low - kline2.effective_high)
        
        gap_type = "none"
        if upward_gap > 0:
            gap_type = "upward"
        elif downward_gap > 0:
            gap_type = "downward"
            
        return {
            "type": gap_type, 
            "upward_gap": upward_gap, 
            "downward_gap": downward_gap, 
            "has_gap": gap_type != "none"
        }
    
    def characterize_two_klines(self, kline1: KLine, kline2: KLine) -> Dict[str, Any]:
        """表征两根K线"""
        relationship = self.determine_relationship(kline1, kline2)
        return {
            "relationship": relationship.name,
            "gap_info": self.calculate_gap(kline1, kline2),
            "kline1": {"open": kline1.open, "close": kline1.close, "high": kline1.high, "low": kline1.low},
            "kline2": {"open": kline2.open, "close": kline2.close, "high": kline2.high, "low": kline2.low}
        }
    
    def analyze_window_relationships(self, window: List[KLine]) -> Dict[str, Any]:
        """分析窗口内K线关系模式"""
        relationships = {
            'engulfing_patterns': 0,
            'harami_patterns': 0,
            'gap_patterns': 0,
            'containment_patterns': 0,
            'momentum_continuation': 0,
            'reversal_signals': 0
        }
        
        # 分析相邻K线关系
        for i in range(1, len(window)):
            kline1 = window[i-1]
            kline2 = window[i]
            
            # 使用K线关系判断
            relation = self.determine_relationship(kline1, kline2)
            
            # 统计各种关系模式
            if relation in [KLineRelationship.CONTAINING, KLineRelationship.CONTAINED]:
                relationships['containment_patterns'] += 1
            elif relation in [KLineRelationship.UPWARD_GAP, KLineRelationship.DOWNWARD_GAP]:
                relationships['gap_patterns'] += 1
            
            # 检测吞噬模式
            if (relation == KLineRelationship.CONTAINING and 
                ((kline1.direction == KLineDirection.BEARISH and kline2.direction == KLineDirection.BULLISH) or
                 (kline1.direction == KLineDirection.BULLISH and kline2.direction == KLineDirection.BEARISH))):
                relationships['engulfing_patterns'] += 1
            
            # 检测孕线模式
            if (relation == KLineRelationship.CONTAINED and 
                ((kline1.direction == KLineDirection.BEARISH and kline2.direction == KLineDirection.BULLISH) or
                 (kline1.direction == KLineDirection.BULLISH and kline2.direction == KLineDirection.BEARISH))):
                relationships['harami_patterns'] += 1
        
        # 计算关系强度指标
        total_possible = len(window) - 1
        for key in relationships:
            relationships[key] /= total_possible if total_possible > 0 else 1
        
        return relationships

# ==================== 市场结构分析模块 ====================

class StructuralAnalyzer:
    """市场结构分析器"""
    
    def __init__(self, window_size=20, extreme_lookback=5):
        self.window_size = window_size
        self.extreme_lookback = extreme_lookback
        
        # 数据存储
        self.klines = []
        self.price_extremes = []
        self.volume_extremes = []
        
        # 全局标记
        self.global_marks = {
            'significant_highs': [],
            'significant_lows': [],
            'gaps': [],
            'high_volume_bars': [],
            'key_reversals': []
        }
    
    def _analyze_structure(self, window=None):
        """
        深度分析市场结构
        
        包括:
        1. 趋势腿识别与计数
        2. 高低点序列分析
        3. 市场阶段识别
        4. 结构完整性评估
        """
        if window is None:
            window = self.klines[-self.window_size:] if len(self.klines) >= self.window_size else self.klines
        
        if len(window) < 10:
            return {}
        
        prices = [k.close for k in window]
        highs = [k.high for k in window]
        lows = [k.low for k in window]
        
        # 1. 识别显著高低点
        significant_highs, significant_lows = self._identify_significant_pivots(highs, lows)
        
        # 2. 识别趋势腿
        up_legs, down_legs = self._identify_trend_legs(significant_highs, significant_lows)
        
        # 3. 分析市场阶段
        market_phase = self._analyze_market_phase(up_legs, down_legs)
        
        # 4. 评估结构完整性
        structure_integrity = self._evaluate_structure_integrity(up_legs, down_legs)
        
        # 5. 识别波浪结构
        wave_structure = self._analyze_wave_structure(significant_highs, significant_lows)
        
        return {
            'significant_highs': significant_highs,
            'significant_lows': significant_lows,
            'up_legs': up_legs,
            'down_legs': down_legs,
            'up_leg_count': len(up_legs),
            'down_leg_count': len(down_legs),
            'market_phase': market_phase,
            'structure_integrity': structure_integrity,
            'wave_structure': wave_structure
        }

    def _identify_significant_pivots(self, highs, lows):
        """识别显著高低点"""
        significant_highs = []
        significant_lows = []
        
        # 使用ZigZag算法识别显著高低点
        # 这里简化实现，实际应用中可能需要更复杂的算法
        
        # 识别显著高点
        for i in range(2, len(highs)-2):
            if (highs[i] > highs[i-1] and highs[i] > highs[i-2] and
                highs[i] > highs[i+1] and highs[i] > highs[i+2]):
                significant_highs.append({
                    'index': i,
                    'price': highs[i],
                    'strength': self._calculate_pivot_strength(highs, i, 'high')
                })
        
        # 识别显著低点
        for i in range(2, len(lows)-2):
            if (lows[i] < lows[i-1] and lows[i] < lows[i-2] and
                lows[i] < lows[i+1] and lows[i] < lows[i+2]):
                significant_lows.append({
                    'index': i,
                    'price': lows[i],
                    'strength': self._calculate_pivot_strength(lows, i, 'low')
                })
        
        return significant_highs, significant_lows

    def _calculate_pivot_strength(self, prices, index, pivot_type):
        """计算高低点强度"""
        lookback = min(5, index)
        lookforward = min(5, len(prices) - index - 1)
        
        if pivot_type == 'high':
            # 高点强度 = (当前高点 - 前后平均低点) / 当前高点
            before_avg = np.mean(prices[index-lookback:index]) if lookback > 0 else prices[index]
            after_avg = np.mean(prices[index+1:index+lookforward+1]) if lookforward > 0 else prices[index]
            avg_low = (before_avg + after_avg) / 2
            return (prices[index] - avg_low) / prices[index] if prices[index] > 0 else 0
        else:
            # 低点强度 = (前后平均高点 - 当前低点) / 当前低点
            before_avg = np.mean(prices[index-lookback:index]) if lookback > 0 else prices[index]
            after_avg = np.mean(prices[index+1:index+lookforward+1]) if lookforward > 0 else prices[index]
            avg_high = (before_avg + after_avg) / 2
            return (avg_high - prices[index]) / prices[index] if prices[index] > 0 else 0

    def _identify_trend_legs(self, significant_highs, significant_lows):
        """识别趋势腿"""
        up_legs = []
        down_legs = []
        
        # 确保有足够的高低点
        if len(significant_highs) < 2 or len(significant_lows) < 2:
            return up_legs, down_legs
        
        # 按索引排序
        significant_highs.sort(key=lambda x: x['index'])
        significant_lows.sort(key=lambda x: x['index'])
        
        # 识别上升腿 (低点-高点-更高低点-更高高点)
        for i in range(len(significant_lows)-1):
            low1 = significant_lows[i]
            low2 = significant_lows[i+1]
            
            # 找两个低点之间的高点
            high_between = None
            for high in significant_highs:
                if low1['index'] < high['index'] < low2['index']:
                    if high_between is None or high['price'] > high_between['price']:
                        high_between = high
            
            if high_between and low2['price'] > low1['price']:
                up_legs.append({
                    'start': low1,
                    'peak': high_between,
                    'end': low2,
                    'height': high_between['price'] - low1['price'],
                    'retracement': (high_between['price'] - low2['price']) / (high_between['price'] - low1['price']) if high_between['price'] != low1['price'] else 0
                })
        
        # 识别下降腿 (高点-低点-更低高点-更低低点)
        for i in range(len(significant_highs)-1):
            high1 = significant_highs[i]
            high2 = significant_highs[i+1]
            
            # 找两个高点之间的低点
            low_between = None
            for low in significant_lows:
                if high1['index'] < low['index'] < high2['index']:
                    if low_between is None or low['price'] < low_between['price']:
                        low_between = low
            
            if low_between and high2['price'] < high1['price']:
                down_legs.append({
                    'start': high1,
                    'trough': low_between,
                    'end': high2,
                    'height': high1['price'] - low_between['price'],
                    'retracement': (high2['price'] - low_between['price']) / (high1['price'] - low_between['price']) if high1['price'] != low_between['price'] else 0
                })
        
        return up_legs, down_legs

    def _analyze_market_phase(self, up_legs, down_legs):
        """分析市场阶段"""
        if not up_legs and not down_legs:
            return "consolidation"
        
        # 计算趋势腿的特征
        up_strength = np.mean([leg['height'] for leg in up_legs]) if up_legs else 0
        down_strength = np.mean([leg['height'] for leg in down_legs]) if down_legs else 0
        
        if up_legs and down_legs:
            # 有上升和下降腿，可能是趋势转换或调整
            last_up = up_legs[-1] if up_legs else None
            last_down = down_legs[-1] if down_legs else None
            
            if last_up and last_down:
                if last_up['end']['index'] > last_down['end']['index']:
                    # 最后是上升腿
                    if last_up['height'] > down_strength * 1.5:
                        return "uptrend"
                    else:
                        return "corrective_up"
                else:
                    # 最后是下降腿
                    if last_down['height'] > up_strength * 1.5:
                        return "downtrend"
                    else:
                        return "corrective_down"
        
        elif up_legs:
            # 只有上升腿
            if len(up_legs) >= 2 and up_legs[-1]['height'] > up_legs[-2]['height'] * 0.8:
                return "uptrend"
            else:
                return "corrective_up"
        
        elif down_legs:
            # 只有下降腿
            if len(down_legs) >= 2 and down_legs[-1]['height'] > down_legs[-2]['height'] * 0.8:
                return "downtrend"
            else:
                return "corrective_down"
        
        return "unknown"

    def _evaluate_structure_integrity(self, up_legs, down_legs):
        """评估结构完整性"""
        integrity_score = 0.5  # 初始分数
        
        # 检查上升腿的完整性
        if up_legs:
            # 检查是否有完整的推动-调整结构
            if len(up_legs) >= 3:
                # 检查是否形成高一低一高结构
                if (up_legs[-1]['peak']['price'] > up_legs[-2]['peak']['price'] and
                    up_legs[-1]['start']['price'] > up_legs[-2]['start']['price']):
                    integrity_score += 0.2
            
            # 检查回调幅度
            retracements = [leg['retracement'] for leg in up_legs if leg['retracement'] > 0]
            if retracements:
                avg_retracement = np.mean(retracements)
                # 理想回调幅度在0.382-0.618之间
                if 0.3 < avg_retracement < 0.7:
                    integrity_score += 0.1
        
        # 检查下降腿的完整性
        if down_legs:
            if len(down_legs) >= 3:
                # 检查是否形成低一高一低结构
                if (down_legs[-1]['trough']['price'] < down_legs[-2]['trough']['price'] and
                    down_legs[-1]['start']['price'] < down_legs[-2]['start']['price']):
                    integrity_score += 0.2
            
            # 检查反弹幅度
            retracements = [leg['retracement'] for leg in down_legs if leg['retracement'] > 0]
            if retracements:
                avg_retracement = np.mean(retracements)
                if 0.3 < avg_retracement < 0.7:
                    integrity_score += 0.1
        
        return min(1.0, max(0.0, integrity_score))

    def _analyze_wave_structure(self, significant_highs, significant_lows):
        """分析波浪结构 (简化版)"""
        if len(significant_highs) < 3 or len(significant_lows) < 3:
            return {}
        
        # 按价格排序
        highs_sorted = sorted(significant_highs, key=lambda x: x['price'], reverse=True)
        lows_sorted = sorted(significant_lows, key=lambda x: x['price'])
        
        # 识别可能的波浪顶点和底点
        wave_analysis = {
            'wave_1_high': highs_sorted[0] if len(highs_sorted) > 0 else None,
            'wave_2_low': lows_sorted[0] if len(lows_sorted) > 0 else None,
            'wave_3_high': highs_sorted[1] if len(highs_sorted) > 1 else None,
            'wave_4_low': lows_sorted[1] if len(lows_sorted) > 1 else None,
            'wave_5_high': highs_sorted[2] if len(highs_sorted) > 2 else None,
        }
        
        # 检查波浪关系 (简化版)
        if (wave_analysis['wave_3_high'] and wave_analysis['wave_1_high'] and
            wave_analysis['wave_3_high']['price'] > wave_analysis['wave_1_high']['price']):
            wave_analysis['wave_3_extended'] = True
        
        return wave_analysis

# ==================== 高级成交量分析模块 ====================

class AdvancedVolumeAnalysis:
    """高级成交量模式分析"""
    
    def __init__(self):
        self.volume_patterns = {}
        self.volume_memory = []  # 存储历史成交量模式
        
    def analyze_advanced_volume_patterns(self, window, price_trend, market_structure):
        """
        深度分析成交量模式，结合市场结构和趋势
        
        参数:
        window: K线窗口
        price_trend: 价格趋势
        market_structure: 市场结构分析结果
        
        返回:
        高级成交量模式分析结果
        """
        if len(window) < 10 or not hasattr(window[0], 'volume'):
            return {}
        
        volumes = [k.volume for k in window]
        prices = [k.close for k in window]
        highs = [k.high for k in window]
        lows = [k.low for k in window]
        
        analysis = {}
        
        # 1. 结构特异性成交量模式
        analysis.update(self._analyze_structure_specific_volume(volumes, prices, market_structure))
        
        # 2. 情绪驱动成交量模式
        analysis.update(self._analyze_sentiment_driven_volume(volumes, prices, price_trend))
        
        # 3. 机构行为成交量模式
        analysis.update(self._analyze_institutional_volume(volumes, prices, highs, lows))
        
        # 4. 时间维度成交量模式
        analysis.update(self._analyze_time_based_volume(volumes, window))
        
        # 5. 成交量分布分析
        analysis.update(self._analyze_volume_distribution(volumes, prices))
        
        # 记录当前模式
        current_pattern = self._identify_dominant_volume_pattern(analysis)
        if current_pattern:
            self.volume_memory.append({
                'pattern': current_pattern,
                'timestamp': window[-1].timestamp if hasattr(window[-1], 'timestamp') else len(window),
                'confidence': analysis.get('pattern_confidence', 0.5)
            })
        
        return analysis
    
    def _analyze_structure_specific_volume(self, volumes, prices, market_structure):
        """分析结构特异性成交量模式"""
        patterns = {}
        
        # 根据市场结构识别特定的成交量模式
        market_phase = market_structure.get('market_phase', '')
        leg_count = market_structure.get('up_leg_count', 0) + market_structure.get('down_leg_count', 0)
        
        # 1. 趋势启动成交量模式
        if market_phase in ['uptrend', 'downtrend'] and leg_count <= 1:
            # 趋势启动通常伴随放量突破
            volume_expansion = self._check_volume_expansion(volumes, lookback=5)
            patterns['trend_initiation_volume'] = volume_expansion
            patterns['initiation_strength'] = volume_expansion.get('expansion_strength', 0)
        
        # 2. 趋势延续成交量模式
        elif market_phase in ['uptrend', 'downtrend'] and leg_count > 1:
            # 健康趋势：上涨放量，回调缩量
            if market_phase == 'uptrend':
                up_days = [i for i in range(1, len(prices)) if prices[i] > prices[i-1]]
                down_days = [i for i in range(1, len(prices)) if prices[i] < prices[i-1]]
                
                if up_days and down_days:
                    avg_up_volume = np.mean([volumes[i] for i in up_days])
                    avg_down_volume = np.mean([volumes[i] for i in down_days])
                    patterns['healthy_uptrend_volume'] = avg_up_volume > avg_down_volume * 1.2
            
            elif market_phase == 'downtrend':
                down_days = [i for i in range(1, len(prices)) if prices[i] < prices[i-1]]
                up_days = [i for i in range(1, len(prices)) if prices[i] > prices[i-1]]
                
                if down_days and up_days:
                    avg_down_volume = np.mean([volumes[i] for i in down_days])
                    avg_up_volume = np.mean([volumes[i] for i in up_days])
                    patterns['healthy_downtrend_volume'] = avg_down_volume > avg_up_volume * 1.2
        
        # 3. 趋势衰竭成交量模式
        if leg_count >= 3:
            # 趋势末期通常出现量价背离或异常放量
            recent_volumes = volumes[-5:]
            recent_prices = prices[-5:]
            
            volume_trend = np.polyfit(range(5), recent_volumes, 1)[0] if len(recent_volumes) == 5 else 0
            price_trend = np.polyfit(range(5), recent_prices, 1)[0] if len(recent_prices) == 5 else 0
            
            if (price_trend > 0 and volume_trend < 0) or (price_trend < 0 and volume_trend < 0):
                patterns['exhaustion_divergence'] = True
                patterns['exhaustion_strength'] = abs(volume_trend) * 10
        
        # 4. 盘整结构成交量模式
        if market_phase == 'consolidation':
            # 盘整末期通常出现成交量收缩后突然放大
            volume_contraction = self._check_volume_contraction(volumes, lookback=8)
            if volume_contraction and volumes[-1] > np.mean(volumes[-5:-1]) * 1.5:
                patterns['breakout_imminent'] = True
                patterns['breakout_confidence'] = volumes[-1] / np.mean(volumes[-10:]) if np.mean(volumes[-10:]) > 0 else 1
        
        return patterns
    
    def _analyze_sentiment_driven_volume(self, volumes, prices, price_trend):
        """分析情绪驱动成交量模式"""
        patterns = {}
        
        # 1. 恐慌性抛售模式
        # 特征：放量长阴线，成交量集中在价格低点
        if price_trend == "down" and len(volumes) >= 3:
            recent_volumes = volumes[-3:]
            recent_returns = [(prices[i] - prices[i-1])/prices[i-1] for i in range(-3, 0) if i < 0]
            
            if (recent_volumes[-1] > np.mean(volumes[:-3]) * 2 and 
                min(recent_returns) < -0.03):  # 跌幅超过3%
                patterns['panic_selling'] = True
                patterns['panic_intensity'] = recent_volumes[-1] / np.mean(volumes[:-3]) if np.mean(volumes[:-3]) > 0 else 1
        
        # 2. 贪婪追涨模式
        # 特征：持续放量上涨，成交量逐级放大
        if price_trend == "up" and len(volumes) >= 5:
            volume_growth = np.polyfit(range(5), volumes[-5:], 1)[0] if len(volumes) >= 5 else 0
            price_growth = np.polyfit(range(5), prices[-5:], 1)[0] if len(prices) >= 5 else 0
            
            if volume_growth > 0 and price_growth > 0:
                patterns['greed_chasing'] = True
                patterns['chasing_intensity'] = volume_growth * price_growth * 100
        
        # 3. 犹豫不决模式
        # 特征：成交量低迷且分布均匀，价格波动小
        volume_std = np.std(volumes) / np.mean(volumes) if np.mean(volumes) > 0 else 0
        price_std = np.std(prices) / np.mean(prices) if np.mean(prices) > 0 else 0
        
        if volume_std < 0.3 and price_std < 0.01:
            patterns['indecision'] = True
            patterns['indecision_strength'] = (0.3 - volume_std) * (0.01 - price_std) * 1000
        
        # 4. 确认/否认模式
        # 关键位置成交量确认或否认价格运动
        if len(volumes) >= 2:
            price_change = (prices[-1] - prices[-2]) / prices[-2]
            volume_change = (volumes[-1] - volumes[-2]) / volumes[-2]
            
            if abs(price_change) > 0.01:  # 价格变化超过1%
                if price_change * volume_change > 0:  # 同向变化
                    patterns['volume_confirmation'] = True
                    patterns['confirmation_strength'] = abs(volume_change)
                else:  # 反向变化
                    patterns['volume_denial'] = True
                    patterns['denial_strength'] = abs(volume_change)
        
        return patterns
    
    def _analyze_institutional_volume(self, volumes, prices, highs, lows):
        """分析机构行为成交量模式"""
        patterns = {}
        
        if len(volumes) < 20:
            return patterns
        
        # 1. 吸筹模式 (Accumulation)
        # 特征：价格区间震荡或缓慢下跌，但成交量在低点放大
        low_volume_days = [i for i in range(len(prices)) if prices[i] < np.percentile(prices, 30)]
        if low_volume_days:
            avg_low_volume = np.mean([volumes[i] for i in low_volume_days])
            avg_volume = np.mean(volumes)
            if avg_low_volume > avg_volume * 1.2:
                patterns['accumulation'] = True
                patterns['accumulation_ratio'] = avg_low_volume / avg_volume
        
        # 2. 派发模式 (Distribution)
        # 特征：价格区间震荡或缓慢上涨，但成交量在高点放大
        high_volume_days = [i for i in range(len(prices)) if prices[i] > np.percentile(prices, 70)]
        if high_volume_days:
            avg_high_volume = np.mean([volumes[i] for i in high_volume_days])
            avg_volume = np.mean(volumes)
            if avg_high_volume > avg_volume * 1.2:
                patterns['distribution'] = True
                patterns['distribution_ratio'] = avg_high_volume / avg_volume
        
        # 3. 大宗交易模式
        # 特征：异常大的单根成交量，但价格变化不大
        large_volume_indices = [i for i, vol in enumerate(volumes) if vol > np.mean(volumes) * 3]
        for idx in large_volume_indices:
            if idx < len(prices) - 1:
                price_change = abs(prices[idx] - prices[idx-1]) / prices[idx-1] if idx > 0 else 0
                if price_change < 0.02:  # 价格变化小于2%
                    patterns['block_trading'] = True
                    patterns['block_trading_size'] = volumes[idx] / np.mean(volumes)
                    break
        
        return patterns
    
    def _analyze_time_based_volume(self, volumes, window):
        """分析时间维度成交量模式"""
        patterns = {}
        
        # 1. 日内成交量模式 (如果有时间数据)
        if hasattr(window[0], 'timestamp'):
            # 分析不同时间段的成交量特征
            hour_volumes = {}
            for kline in window:
                if hasattr(kline, 'timestamp'):
                    hour = kline.timestamp.hour
                    hour_volumes.setdefault(hour, []).append(kline.volume)
            
            # 计算各小时平均成交量
            avg_hour_volumes = {hour: np.mean(vols) for hour, vols in hour_volumes.items()}
            if avg_hour_volumes:
                max_hour = max(avg_hour_volumes.items(), key=lambda x: x[1])[0]
                min_hour = min(avg_hour_volumes.items(), key=lambda x: x[1])[0]
                
                patterns['peak_trading_hour'] = max_hour
                patterns['low_trading_hour'] = min_hour
                patterns['hourly_volatility'] = (max(avg_hour_volumes.values()) - min(avg_hour_volumes.values())) / np.mean(list(avg_hour_volumes.values())) if np.mean(list(avg_hour_volumes.values())) > 0 else 0
        
        # 2. 成交量时间序列分析
        if len(volumes) >= 10:
            # 检查成交量的自相关性
            autocorr = self._calculate_volume_autocorrelation(volumes)
            patterns['volume_autocorrelation'] = autocorr
            
            # 成交量周期分析
            periodicity = self._analyze_volume_periodicity(volumes)
            patterns.update(periodicity)
        
        return patterns
    
    def _analyze_volume_distribution(self, volumes, prices):
        """分析成交量分布特征"""
        patterns = {}
        
        if len(volumes) < 10:
            return patterns
        
        # 1. 成交量-价格分布分析
        # 计算不同价格区间的成交量分布
        price_bins = np.linspace(min(prices), max(prices), 5)
        volume_distribution = []
        
        for i in range(len(price_bins)-1):
            bin_volumes = [volumes[j] for j in range(len(prices)) 
                          if price_bins[i] <= prices[j] < price_bins[i+1]]
            if bin_volumes:
                volume_distribution.append(np.mean(bin_volumes))
        
        if volume_distribution:
            # 分析成交量分布的形状
            if volume_distribution[0] > volume_distribution[-1] * 1.5:
                patterns['volume_skew_low'] = True  # 成交量集中在低位
            elif volume_distribution[-1] > volume_distribution[0] * 1.5:
                patterns['volume_skew_high'] = True  # 成交量集中在高位
        
        # 2. 成交量集中度分析
        volume_gini = self._calculate_gini_coefficient(volumes)
        patterns['volume_concentration'] = volume_gini
        
        return patterns
    
    def _identify_dominant_volume_pattern(self, analysis):
        """识别主导成交量模式"""
        if not analysis:
            return None
        
        # 优先识别重要的模式
        important_patterns = [
            'panic_selling', 'greed_chasing', 'accumulation', 'distribution',
            'block_trading', 'exhaustion_divergence', 'breakout_imminent'
        ]
        
        for pattern in important_patterns:
            if analysis.get(pattern, False):
                return pattern
        
        # 其次识别一般模式
        general_patterns = [
            'healthy_uptrend_volume', 'healthy_downtrend_volume',
            'volume_confirmation', 'volume_denial', 'indecision'
        ]
        
        for pattern in general_patterns:
            if analysis.get(pattern, False):
                return pattern
        
        return None
    
    def _check_volume_expansion(self, volumes, lookback=5):
        """检查成交量扩张"""
        if len(volumes) < lookback + 1:
            return {'expansion': False, 'expansion_strength': 0}
        
        current_volume = volumes[-1]
        previous_volumes = volumes[-lookback-1:-1]
        
        if not previous_volumes:
            return {'expansion': False, 'expansion_strength': 0}
        
        avg_previous = np.mean(previous_volumes)
        expansion_ratio = current_volume / avg_previous if avg_previous > 0 else 1
        
        return {
            'expansion': expansion_ratio > 1.5,
            'expansion_strength': expansion_ratio,
            'expansion_ratio': expansion_ratio
        }
    
    def _check_volume_contraction(self, volumes, lookback=8):
        """检查成交量收缩"""
        if len(volumes) < lookback:
            return False
        
        recent_volumes = volumes[-lookback:]
        avg_recent = np.mean(recent_volumes)
        avg_previous = np.mean(volumes[-lookback*2:-lookback]) if len(volumes) >= lookback*2 else avg_recent
        
        return avg_recent < avg_previous * 0.7
    
    def _calculate_volume_autocorrelation(self, volumes, lag=1):
        """计算成交量自相关性"""
        if len(volumes) < lag + 1:
            return 0
        
        return np.corrcoef(volumes[:-lag], volumes[lag:])[0, 1] if not np.isnan(np.corrcoef(volumes[:-lag], volumes[lag:])[0, 1]) else 0
    
    def _analyze_volume_periodicity(self, volumes):
        """分析成交量周期性"""
        # 简化实现：检查成交量是否有明显的周期性模式
        if len(volumes) < 20:
            return {}
        
        # 使用FFT检测周期性
        fft = np.fft.fft(volumes)
        freqs = np.fft.fftfreq(len(volumes))
        
        # 找到主要频率
        idx = np.argmax(np.abs(fft))
        dominant_freq = freqs[idx]
        
        return {
            'dominant_frequency': dominant_freq,
            'has_periodicity': abs(dominant_freq) > 0.1
        }
    
    def _calculate_gini_coefficient(self, values):
        """计算基尼系数（衡量集中度）"""
        if len(values) == 0:
            return 0
        
        values = np.sort(values)
        n = len(values)
        index = np.arange(1, n + 1)
        return (np.sum((2 * index - n - 1) * values)) / (n * np.sum(values))

# ==================== 状态跳转系统 ====================

class StateTransitionSystem:
    """状态跳转系统 with 中间状态"""
    
    def __init__(self):
        self.current_state = MarketState.UNKNOWN
        self.intermediate_state = None
        self.transition_start_time = None
        self.confirmation_signals = []
        self.failed_transitions = []
        
        # 状态跳转配置
        self.transition_config = {
            # 格式: (from_state, to_state): {'confirmation_signals': [], 'timeout': 10, 'failure_signals': []}
        }
        
        self._initialize_transition_config()
    
    def _initialize_transition_config(self):
        """初始化状态跳转配置"""
        # 上涨腿转换配置
        self.transition_config[(MarketState.UP_LEG_1, MarketState.UP_LEG_2)] = {
            'confirmation_signals': ['price_breakout', 'volume_expansion', 'trend_confirmation'],
            'failure_signals': ['price_rejection', 'volume_divergence', 'support_break'],
            'timeout': 15,
            'minimum_retracement': 0.382,
            'maximum_retracement': 0.618
        }
        
        self.transition_config[(MarketState.UP_LEG_2, MarketState.UP_LEG_3)] = {
            'confirmation_signals': ['price_breakout', 'volume_expansion', 'momentum_increase'],
            'failure_signals': ['double_top', 'volume_divergence', 'trend_break'],
            'timeout': 12,
            'minimum_retracement': 0.382,
            'maximum_retracement': 0.618
        }
        
        # 下跌腿转换配置
        self.transition_config[(MarketState.DOWN_LEG_1, MarketState.DOWN_LEG_2)] = {
            'confirmation_signals': ['price_breakdown', 'volume_expansion', 'trend_confirmation'],
            'failure_signals': ['price_rejection', 'volume_divergence', 'resistance_break'],
            'timeout': 15,
            'minimum_retracement': 0.382,
            'maximum_retracement': 0.618
        }
        
        # 趋势转换配置
        self.transition_config[(MarketState.UP_LEG_3, MarketState.DOWN_LEG_1)] = {
            'confirmation_signals': ['trend_reversal', 'volume_spike', 'key_reversal'],
            'failure_signals': ['false_breakout', 'volume_lack', 'support_hold'],
            'timeout': 20,
            'retracement_depth': 0.786  # 深幅回撤
        }
        
        # 盘整突破配置
        self.transition_config[(MarketState.CALM, MarketState.UP_LEG_1)] = {
            'confirmation_signals': ['volume_expansion', 'price_breakout', 'range_expansion'],
            'failure_signals': ['false_breakout', 'volume_lack', 'price_rejection'],
            'timeout': 10,
            'breakout_threshold': 0.02  # 突破幅度阈值
        }
    
    def attempt_state_transition(self, from_state, proposed_state, market_data, analysis_results):
        """
        尝试状态跳转
        
        返回:
        TransitionResult: 跳转结果，可能包含中间状态
        """
        transition_key = (from_state, proposed_state)
        if transition_key not in self.transition_config:
            return TransitionResult(
                success=False,
                new_state=from_state,
                reason="No transition configuration found"
            )
        
        config = self.transition_config[transition_key]
        
        # 检查是否已经在过渡状态中
        if self.intermediate_state and self.intermediate_state['target_state'] == proposed_state:
            # 检查确认信号
            return self._check_confirmation_signals(config, market_data, analysis_results)
        else:
            # 开始新的过渡
            return self._start_new_transition(from_state, proposed_state, config, market_data, analysis_results)
    
    def _start_new_transition(self, from_state, to_state, config, market_data, analysis_results):
        """开始新的状态过渡"""
        # 检查基本过渡条件
        if not self._check_transition_prerequisites(to_state, analysis_results):
            return TransitionResult(
                success=False,
                new_state=from_state,
                reason="Prerequisites not met"
            )
        
        # 进入中间状态
        self.intermediate_state = {
            'from_state': from_state,
            'target_state': to_state,
            'start_kline_count': market_data.get('kline_count', 0),  # 使用K线计数而不是时间戳
            'confirmation_count': 0,
            'failure_count': 0,
            'required_confirmations': len(config['confirmation_signals']) // 2 + 1  # 需要过半确认信号
        }
        
        return TransitionResult(
            success=False,
            new_state=from_state,
            intermediate_state=IntermediateState(
                from_state=from_state,
                to_state=to_state,
                progress=0.0,
                expected_duration=config['timeout']
            ),
            reason="Transition started, awaiting confirmation"
        )
    
    def _check_confirmation_signals(self, config, market_data, analysis_results):
        """检查确认信号"""
        current_signals = self._identify_signals(market_data, analysis_results)
        
        # 统计确认信号和失败信号
        confirmation_count = sum(1 for signal in config['confirmation_signals'] if signal in current_signals)
        failure_count = sum(1 for signal in config['failure_signals'] if signal in current_signals)
        
        # 更新中间状态
        self.intermediate_state['confirmation_count'] = confirmation_count
        self.intermediate_state['failure_count'] = failure_count
        
        # 检查超时 - 使用K线计数而不是时间戳
        current_kline_count = market_data.get('kline_count', 0)
        start_kline_count = self.intermediate_state.get('start_kline_count', 0)
        elapsed_klines = current_kline_count - start_kline_count
        
        if elapsed_klines > config['timeout']:
            return self._handle_transition_timeout()
        
        # 检查是否达到确认条件
        if confirmation_count >= self.intermediate_state['required_confirmations']:
            return self._complete_transition()
        
        # 检查是否失败条件达成
        if failure_count >= 2:  # 至少2个失败信号
            return self._handle_transition_failure()
        
        # 继续等待更多信号
        progress = min(1.0, confirmation_count / self.intermediate_state['required_confirmations'])
        return TransitionResult(
            success=False,
            new_state=self.intermediate_state['from_state'],
            intermediate_state=IntermediateState(
                from_state=self.intermediate_state['from_state'],
                to_state=self.intermediate_state['target_state'],
                progress=progress,
                expected_duration=config['timeout'] - elapsed_klines  # 使用K线计数
            ),
            reason=f"Awaiting confirmation: {confirmation_count}/{self.intermediate_state['required_confirmations']}"
        )

    def _check_transition_prerequisites(self, to_state, analysis_results):
        """检查状态跳转的前提条件"""
        prerequisites = {
            MarketState.UP_LEG_2: lambda: self._check_up_leg_2_prerequisites(analysis_results),
            MarketState.UP_LEG_3: lambda: self._check_up_leg_3_prerequisites(analysis_results),
            MarketState.DOWN_LEG_2: lambda: self._check_down_leg_2_prerequisites(analysis_results),
            MarketState.DOWN_LEG_3: lambda: self._check_down_leg_3_prerequisites(analysis_results),
            MarketState.BREAKOUT: lambda: self._check_breakout_prerequisites(analysis_results),
            MarketState.CLIMAX: lambda: self._check_climax_prerequisites(analysis_results),
        }
        
        check_func = prerequisites.get(to_state, lambda: True)
        return check_func()
    
    def _check_up_leg_2_prerequisites(self, analysis_results):
        """检查UP_LEG_2的前提条件"""
        # 需要完成UP_LEG_1且有一定的回调
        structure = analysis_results.get('structure_analysis', {})
        if structure.get('up_leg_count', 0) != 1:
            return False
        
        # 检查回调幅度是否在合理范围内
        up_legs = structure.get('up_legs', [])
        if not up_legs:
            return False
        
        last_leg = up_legs[-1]
        retracement = last_leg.get('retracement', 1)
        if not (0.382 <= retracement <= 0.618):
            return False
        
        return True
    
    def _complete_transition(self):
        """完成状态跳转"""
        new_state = self.intermediate_state['target_state']
        from_state = self.intermediate_state['from_state']
        
        # 重置中间状态
        self.intermediate_state = None
        self.current_state = new_state
        
        # 记录成功的跳转
        self._record_successful_transition(from_state, new_state)
        
        return TransitionResult(
            success=True,
            new_state=new_state,
            reason="Transition completed successfully"
        )
    
    def _handle_transition_timeout(self):
        """处理跳转超时"""
        from_state = self.intermediate_state['from_state']
        
        # 记录失败的跳转
        self.failed_transitions.append({
            'from': from_state,
            'to': self.intermediate_state['target_state'],
            'reason': 'timeout',
            'timestamp': self.intermediate_state['start_time']
        })
        
        # 重置中间状态，回到原状态
        self.intermediate_state = None
        
        return TransitionResult(
            success=False,
            new_state=from_state,
            reason="Transition timeout"
        )
    
    def _handle_transition_failure(self):
        """处理跳转失败"""
        from_state = self.intermediate_state['from_state']
        
        # 记录失败的跳转
        self.failed_transitions.append({
            'from': from_state,
            'to': self.intermediate_state['target_state'],
            'reason': 'failure_signals',
            'timestamp': self.intermediate_state['start_time']
        })
        
        # 重置中间状态，回到原状态
        self.intermediate_state = None
        
        return TransitionResult(
            success=False,
            new_state=from_state,
            reason="Transition failed due to failure signals"
        )
    
    def _identify_signals(self, market_data, analysis_results):
        """识别当前市场信号"""
        signals = []
        
        # 价格信号
        prices = market_data['prices']
        if len(prices) >= 2:
            price_change = (prices[-1] - prices[-2]) / prices[-2]
            if abs(price_change) > 0.015:  # 1.5%的变化
                signals.append('significant_price_move')
        
        # 成交量信号
        volume_analysis = analysis_results.get('volume_analysis', {})
        if volume_analysis.get('volume_expansion', False):
            signals.append('volume_expansion')
        if volume_analysis.get('volume_contraction', False):
            signals.append('volume_contraction')
        
        # 技术信号
        structure_analysis = analysis_results.get('structure_analysis', {})
        if structure_analysis.get('breakout_detected', False):
            signals.append('price_breakout')
        
        # 模式信号
        pattern_analysis = analysis_results.get('pattern_analysis', {})
        if pattern_analysis.get('key_reversal', False):
            signals.append('key_reversal')
        
        return signals

    def _record_successful_transition(self, from_state, to_state):
        """记录成功的状态跳转"""
        # 这里可以添加成功跳转的记录逻辑
        print(f"成功状态跳转: {from_state.value} -> {to_state.value}")

    def _check_up_leg_3_prerequisites(self, analysis_results):
        """检查UP_LEG_3的前提条件"""
        structure = analysis_results.get('structure_analysis', {})
        return structure.get('up_leg_count', 0) == 2

    def _check_down_leg_2_prerequisites(self, analysis_results):
        """检查DOWN_LEG_2的前提条件"""
        structure = analysis_results.get('structure_analysis', {})
        return structure.get('down_leg_count', 0) == 1

    def _check_down_leg_3_prerequisites(self, analysis_results):
        """检查DOWN_LEG_3的前提条件"""
        structure = analysis_results.get('structure_analysis', {})
        return structure.get('down_leg_count', 0) == 2

    def _check_breakout_prerequisites(self, analysis_results):
        """检查BREAKOUT的前提条件"""
        structure = analysis_results.get('structure_analysis', {})
        return structure.get('market_phase') == 'consolidation'

    def _check_climax_prerequisites(self, analysis_results):
        """检查CLIMAX的前提条件"""
        structure = analysis_results.get('structure_analysis', {})
        return structure.get('up_leg_count', 0) >= 3 or structure.get('down_leg_count', 0) >= 3

# ==================== 整合的交易系统 ====================

class IntegratedTradingSystem:
    """整合的交易系统 - 使用第二版的复杂逻辑"""
    
    def __init__(self, window_size=20, extreme_lookback=5):
        self.window_size = window_size
        self.extreme_lookback = extreme_lookback
        
        # 初始化核心分析器
        self.structural_analyzer = StructuralAnalyzer(window_size, extreme_lookback)
        self.advanced_volume_analyzer = AdvancedVolumeAnalysis()
        self.state_transitioner = StateTransitionSystem()
        self.relationship_analyzer = KLineRelationshipAnalyzer()  # 添加K线关系分析器
        
        # 数据存储
        self.klines = []
        self.analysis_results = []
        self.current_state = MarketState.UNKNOWN
        
        # 状态历史记录
        self.state_history = []
        self.state_transition_probs = {}
    
    def add_kline(self, kline):
        """添加K线数据"""
        self.klines.append(kline)
        
        # 保持窗口大小
        if len(self.klines) > self.window_size:
            self.klines.pop(0)
        
        # 当有足够数据时进行分析
        if len(self.klines) >= self.window_size:
            return self.analyze_current_window()
        return None
 
    def analyze_current_window(self):
        """分析当前窗口"""
        current_window = self.klines[-self.window_size:]
        
        # 1. 结构分析
        structural_analysis = self.structural_analyzer._analyze_structure(current_window)
        
        # 2. 趋势分析
        trend = self._analyze_trend(current_window)
        
        # 3. 高级成交量分析
        volume_analysis = self.advanced_volume_analyzer.analyze_advanced_volume_patterns(
            current_window, trend, structural_analysis
        )
        
        # 4. 情绪分析
        sentiment = self._analyze_sentiment(current_window)
        
        # 5. K线关系分析
        relationship_analysis = self.relationship_analyzer.analyze_window_relationships(current_window)
        
        # 6. 使用第二版的复杂determine_state方法
        new_state = self.determine_state(trend, structural_analysis, sentiment, volume_analysis)
        
        # 7. 尝试状态跳转
        transition_result = self.state_transitioner.attempt_state_transition(
            self.current_state,
            new_state,
            {
                'prices': [k.close for k in current_window],
                'timestamp': current_window[-1].timestamp if hasattr(current_window[-1], 'timestamp') else len(current_window),
                'kline_count': len(self.klines)  # 添加K线计数用于时间计算
            },
            {
                'volume_analysis': volume_analysis,
                'structure_analysis': structural_analysis,
                'relationship_analysis': relationship_analysis
            }
        )
        
        # 8. 更新当前状态
        if transition_result.success:
            self.current_state = transition_result.new_state
        elif transition_result.intermediate_state:
            # 处理中间状态
            self._handle_intermediate_state(transition_result.intermediate_state)
        
        # 9. 记录状态历史
        if self.current_state != new_state:
            self._record_state_transition(self.current_state, new_state)
            self.current_state = new_state
        
        # 10. 使用第二版的复杂get_profit_probability方法
        # 获取完整的上下文信息
        context = self._get_current_context()
        profit_probability = self.get_profit_probability(self.current_state, context)
        
        # 11. 保存分析结果
        result = {
            'timestamp': current_window[-1].timestamp if hasattr(current_window[-1], 'timestamp') else len(current_window),
            'state': self.current_state,
            'profit_probability': profit_probability,
            'trend': trend,
            'structure': structural_analysis,
            'volume': volume_analysis,
            'sentiment': sentiment,
            'relationships': relationship_analysis,  # 添加关系分析结果
            'transition_result': transition_result
        }
        
        self.analysis_results.append(result)
        
        return result

    def _analyze_trend(self, window):
        """分析趋势方向"""
        if len(window) < 5:
            return "sideways"
        
        prices = [k.close for k in window]
        x = np.arange(len(prices))
        
        if np.all(prices == prices[0]):
            return "sideways"
            
        slope, _, r_value, _, _ = linregress(x, prices)
        
        if abs(r_value) < 0.3:
            return "sideways"
        elif slope > 0:
            return "up"
        else:
            return "down"
    
    def _analyze_sentiment(self, window):
        """分析市场情绪"""
        if len(window) < 10:
            return "calm"
        
        recent_prices = [k.close for k in window[-10:]]
        volatility = np.std(recent_prices) / np.mean(recent_prices) if np.mean(recent_prices) > 0 else 0
        
        if hasattr(window[0], 'volume'):
            recent_volumes = [k.volume for k in window[-10:] if hasattr(k, 'volume')]
            if recent_volumes:
                volume_ratio = np.mean(recent_volumes[-5:]) / np.mean(recent_volumes[:-5]) if np.mean(recent_volumes[:-5]) > 0 else 1
            else:
                volume_ratio = 1
        else:
            volume_ratio = 1
        
        if volatility > 0.02 and volume_ratio > 1.5:
            return "greed" if self._analyze_trend(window) == "up" else "panic"
        elif volatility < 0.005:
            return "calm"
        else:
            return "ignorance"
    
    def determine_state(self, trend, structure, sentiment, volume_analysis):
        """
        第二版的复杂determine_state方法
        基于多维分析确定市场状态
        """
        # 获取当前窗口的K线数据
        current_window = self.klines[-self.window_size:] if len(self.klines) >= self.window_size else self.klines
        
        # 1. 趋势强度分析
        trend_strength = self._calculate_trend_strength(current_window)
        
        # 2. 波动性分析
        volatility = self._calculate_volatility(current_window)
        
        # 3. 成交量分析 (如果有)
        volume_analysis = self._analyze_volume(current_window) if hasattr(current_window[0], 'volume') else {}
        
        # 4. 价格位置分析
        price_position = self._analyze_price_position(current_window)
        
        # 5. 模式识别
        patterns = self._identify_patterns(current_window)
        
        # 6. 支撑阻力分析
        support_resistance = self._analyze_support_resistance(current_window)
        
        # 7. 时间周期分析
        time_analysis = self._analyze_time_factors()
        
        # 综合所有因素进行状态判断
        return self._synthesize_state(
            trend=trend,
            trend_strength=trend_strength,
            volatility=volatility,
            volume_analysis=volume_analysis,
            price_position=price_position,
            patterns=patterns,
            support_resistance=support_resistance,
            time_analysis=time_analysis,
            sentiment=sentiment,
            structure=structure
        )
    
    def _synthesize_state(self, **analysis_factors):
        """
        综合所有分析因素确定最终状态
        """
        # 提取分析因素
        trend = analysis_factors['trend']
        trend_strength = analysis_factors['trend_strength']
        volatility = analysis_factors['volatility']
        volume_analysis = analysis_factors['volume_analysis']
        price_position = analysis_factors['price_position']
        patterns = analysis_factors['patterns']
        support_resistance = analysis_factors['support_resistance']
        time_analysis = analysis_factors['time_analysis']
        sentiment = analysis_factors['sentiment']
        structure = analysis_factors['structure']
        
        # 状态判断逻辑
        # 1. 首先判断趋势状态


        if trend == "up":
            # 强势上涨趋势
            if trend_strength > 0.7 and volatility < 0.02:
                if price_position > 0.7:  # 高位
                    if 'exhaustion' in patterns:
                        return MarketState.EXHAUSTION
                    elif sentiment == "greed":
                        return MarketState.CLIMAX
                    else:
                        return MarketState.UP_LEG_PLUS
                else:  # 中低位
                    if 'breakout' in patterns and volume_analysis.get('volume_confirmation', False):
                        return MarketState.BREAKOUT
                    else:
                        # 根据腿的数量确定具体状态
                        leg_count = structure.get('up_leg_count', 0)
                        if leg_count == 0:
                            return MarketState.UP_LEG_1
                        elif leg_count == 1:
                            return MarketState.UP_LEG_2
                        elif leg_count == 2:
                            return MarketState.UP_LEG_3
                        else:
                            return MarketState.UP_LEG_PLUS
            
            # 弱势上涨或震荡上涨
            elif trend_strength > 0.3:
                if price_position > 0.6 and support_resistance.get('near_resistance', False):
                    return MarketState.RESISTANCE
                elif price_position < 0.4 and support_resistance.get('near_support', False):
                    return MarketState.PULLBACK
                else:
                    return MarketState.UP_LEG_2 if structure.get('up_leg_count', 0) >= 1 else MarketState.UP_LEG_1
            
            # 趋势转弱或盘整
            else:
                if sentiment == "calm":
                    return MarketState.CALM
                elif sentiment == "greed":
                    return MarketState.VACUUM
                else:
                    return MarketState.UNKNOWN
        
        elif trend == "down":
            # 强势下跌趋势
            if trend_strength > 0.7 and volatility < 0.02:
                if price_position < 0.3:  # 低位
                    if 'exhaustion' in patterns:
                        return MarketState.EXHAUSTION
                    elif sentiment == "panic":
                        return MarketState.CLIMAX
                    else:
                        return MarketState.DOWN_LEG_PLUS
                else:  # 中高位
                    if 'breakdown' in patterns and volume_analysis.get('volume_confirmation', False):
                        return MarketState.BREAKOUT
                    else:
                        # 根据腿的数量确定具体状态
                        leg_count = structure.get('down_leg_count', 0)
                        if leg_count == 0:
                            return MarketState.DOWN_LEG_1
                        elif leg_count == 1:
                            return MarketState.DOWN_LEG_2
                        elif leg_count == 2:
                            return MarketState.DOWN_LEG_3
                        else:
                            return MarketState.DOWN_LEG_PLUS
            
            # 弱势下跌或震荡下跌
            elif trend_strength > 0.3:
                if price_position < 0.4 and support_resistance.get('near_support', False):
                    return MarketState.RESISTANCE
                elif price_position > 0.6 and support_resistance.get('near_resistance', False):
                    return MarketState.PULLBACK
                else:
                    return MarketState.DOWN_LEG_2 if structure.get('down_leg_count', 0) >= 1 else MarketState.DOWN_LEG_1
            
            # 趋势转弱或盘整
            else:
                if sentiment == "calm":
                    return MarketState.CALM
                elif sentiment == "panic":
                    return MarketState.VACUUM
                else:
                    return MarketState.UNKNOWN
        
        else:  # sideways
            # 高波动性盘整
            if volatility > 0.03:
                if sentiment == "greed":
                    return MarketState.CLIMAX
                elif sentiment == "panic":
                    return MarketState.CLIMAX
                else:
                    return MarketState.VACUUM
            
            # 低波动性盘整
            elif volatility < 0.01:
                if time_analysis.get('extended_consolidation', False):
                    return MarketState.VACUUM
                else:
                    return MarketState.CALM
            
            # 中等波动性盘整
            else:
                if support_resistance.get('near_resistance', False):
                    return MarketState.RESISTANCE
                elif support_resistance.get('near_support', False):
                    return MarketState.RESISTANCE
                else:
                    return MarketState.UNKNOWN

    def _calculate_trend_strength(self, window):
        """计算趋势强度"""
        if len(window) < 5:
            return 0
        
        prices = [k.close for k in window]
        x = np.arange(len(prices))
        
        # 处理常数序列
        if np.all(prices == prices[0]):
            return 0
            
        slope, _, r_value, _, _ = linregress(x, prices)
        return abs(r_value)  # 使用R²的绝对值作为趋势强度
    
    def _calculate_volatility(self, window):
        """计算波动性"""
        if len(window) < 2:
            return 0
        
        price_changes = []
        for i in range(1, len(window)):
            price_change = abs(window[i].close - window[i-1].close) / window[i-1].close
            price_changes.append(price_change)
        
        return np.mean(price_changes) if price_changes else 0
    
    def _analyze_volume(self, window):
        """分析成交量"""
        if len(window) < 5 or not hasattr(window[0], 'volume'):
            return {}
        
        volumes = [k.volume for k in window]
        avg_volume = np.mean(volumes)
        current_volume = volumes[-1]
        
        # 检查成交量确认
        price_trend = self._analyze_trend(window)
        volume_confirmation = (
            (price_trend == "up" and current_volume > avg_volume * 1.2) or
            (price_trend == "down" and current_volume > avg_volume * 1.2)
        )
        
        # 检查成交量背离
        volume_divergence = (
            (price_trend == "up" and current_volume < avg_volume * 0.8) or
            (price_trend == "down" and current_volume < avg_volume * 0.8)
        )
        
        return {
            'volume_confirmation': volume_confirmation,
            'volume_divergence': volume_divergence,
            'volume_ratio': current_volume / avg_volume if avg_volume > 0 else 1
        }
    
    def _analyze_price_position(self, window):
        """分析价格位置"""
        highs = [k.high for k in window]
        lows = [k.low for k in window]
        current_price = window[-1].close
        
        if max(highs) == min(lows):
            return 0.5  # 避免除以零
        
        return (current_price - min(lows)) / (max(highs) - min(lows))
    
    def _identify_patterns(self, window):
        """识别价格模式"""
        patterns = []
        
        # 这里可以添加各种模式识别逻辑
        # 例如: 突破、衰竭、背离、持续等模式
        
        # 简单示例: 检查是否创出新高或新低
        if len(window) >= 5:
            current_high = window[-1].high
            previous_highs = [k.high for k in window[:-1]]
            
            if current_high > max(previous_highs):
                patterns.append('breakout')
            
            current_low = window[-1].low
            previous_lows = [k.low for k in window[:-1]]
            
            if current_low < min(previous_lows):
                patterns.append('breakdown')
        
        return patterns
    
    def _analyze_support_resistance(self, window):
        """分析支撑阻力"""
        # 这里可以添加支撑阻力分析逻辑
        # 例如: 检查是否接近历史支撑阻力位
        
        return {
            'near_support': False,  # 需要实现具体逻辑
            'near_resistance': False,  # 需要实现具体逻辑
            'near_strong_support': False,  # 需要实现具体逻辑
            'near_strong_resistance': False,  # 需要实现具体逻辑
            'broken_support': False,  # 需要实现具体逻辑
            'broken_resistance': False  # 需要实现具体逻辑
        }
    
    def _analyze_time_factors(self):
        """分析时间因素"""
        # 这里可以添加时间因素分析逻辑
        # 例如: 检查是否处于特定交易日、特定时间段等
        
        return {
            'extended_consolidation': False,  # 需要实现具体逻辑
            'high_volatility_period': False  # 需要实现具体逻辑
        }
    
    def _handle_intermediate_state(self, intermediate_state):
        """处理中间状态"""
        print(f"处于中间状态: {intermediate_state.from_state.value} -> {intermediate_state.to_state.value}")
        print(f"进度: {intermediate_state.progress:.2%}, 预计剩余时间: {intermediate_state.expected_duration}")
    
    def _record_state_transition(self, from_state, to_state):
        """记录状态转移"""
        transition_key = f"{from_state.value}->{to_state.value}"
        
        if transition_key not in self.state_transition_probs:
            self.state_transition_probs[transition_key] = {
                'count': 0,
                'profitable': 0,
                'probability': 0
            }
        
        self.state_transition_probs[transition_key]['count'] += 1
        
        # 计算所有转移的概率
        total_transitions = sum([v['count'] for v in self.state_transition_probs.values()])
        for key in self.state_transition_probs:
            self.state_transition_probs[key]['probability'] = (
                self.state_transition_probs[key]['count'] / total_transitions
            )
        
        # 记录状态历史
        self.state_history.append({
            'timestamp': self.klines[-1].timestamp if hasattr(self.klines[-1], 'timestamp') else len(self.klines),
            'state': to_state,
            'price': self.klines[-1].close
        })
    
    def get_trading_signals(self):
        """生成交易信号"""
        if not self.analysis_results:
            return {}
        
        latest_analysis = self.analysis_results[-1]
        state = latest_analysis['state']
        probability = latest_analysis['profit_probability']
        
        signals = {}
        
        if probability > 0.6:
            if state in [MarketState.UP_LEG_1, MarketState.UP_LEG_2, MarketState.BREAKOUT]:
                signals['action'] = 'BUY'
                signals['confidence'] = probability
                signals['reason'] = f"Strong bullish signal in {state.value}"
            
            elif state in [MarketState.DOWN_LEG_1, MarketState.DOWN_LEG_2, MarketState.BREAKOUT]:
                signals['action'] = 'SELL'
                signals['confidence'] = probability
                signals['reason'] = f"Strong bearish signal in {state.value}"
        
        elif probability < 0.4:
            signals['action'] = 'AVOID'
            signals['confidence'] = 1 - probability
            signals['reason'] = f"Low probability environment: {state.value}"
        
        else:
            signals['action'] = 'HOLD'
            signals['confidence'] = 0.5
            signals['reason'] = f"Neutral environment: {state.value}"
        
        return signals

    def get_profit_probability(self, state, context=None):
        """
        第二版的复杂get_profit_probability方法
        计算特定状态下的获利概率
        """
        if context is None:
            context = self._get_current_context()
        
        # 1. 基础概率 (基于历史数据)
        base_prob = self._calculate_base_probability(state)
        
        # 2. 趋势强度调整
        trend_adjustment = self._adjust_for_trend_strength(context['trend_strength'])
        
        # 3. 波动性调整
        volatility_adjustment = self._adjust_for_volatility(context['volatility'])
        
        # 4. 成交量确认调整
        volume_adjustment = self._adjust_for_volume(context['volume_analysis'])
        
        # 5. 价格位置调整
        position_adjustment = self._adjust_for_price_position(context['price_position'])
        
        # 6. 支撑阻力调整
        sr_adjustment = self._adjust_for_support_resistance(context['support_resistance'])
        
        # 7. 时间因素调整
        time_adjustment = self._adjust_for_time_factors(context['time_analysis'])
        
        # 8. 模式识别调整
        pattern_adjustment = self._adjust_for_patterns(context['patterns'])
        
        # 9. 市场情绪调整
        sentiment_adjustment = self._adjust_for_sentiment(context['sentiment'])
        
        # 综合所有调整因素
        adjusted_prob = base_prob * trend_adjustment * volatility_adjustment * volume_adjustment
        adjusted_prob *= position_adjustment * sr_adjustment * time_adjustment * pattern_adjustment * sentiment_adjustment
        
        # 确保概率在合理范围内
        return max(0.0, min(1.0, adjusted_prob))
    
    def _get_current_context(self):
        """获取当前市场上下文信息"""
        current_window = self.klines[-self.window_size:] if len(self.klines) >= self.window_size else self.klines
        
        return {
            'trend': self._analyze_trend(current_window),
            'trend_strength': self._calculate_trend_strength(current_window),
            'volatility': self._calculate_volatility(current_window),
            'volume_analysis': self._analyze_volume(current_window) if hasattr(current_window[0], 'volume') else {},
            'price_position': self._analyze_price_position(current_window),
            'patterns': self._identify_patterns(current_window),
            'support_resistance': self._analyze_support_resistance(current_window),
            'time_analysis': self._analyze_time_factors(),
            'sentiment': self._analyze_sentiment(current_window),
            'structure': self.structural_analyzer._analyze_structure(current_window)
        }
    
    def _calculate_base_probability(self, state):
        """计算基础获利概率 (基于历史数据)"""
        # 获取该状态的所有历史出现次数
        state_occurrences = [s for s in self.state_history if s['state'] == state]
        
        if not state_occurrences:
            # 如果没有历史数据，返回默认概率
            default_probs = {
                MarketState.UP_LEG_1: 0.65,
                MarketState.UP_LEG_2: 0.60,
                MarketState.UP_LEG_3: 0.55,
                MarketState.UP_LEG_PLUS: 0.45,
                MarketState.DOWN_LEG_1: 0.65,
                MarketState.DOWN_LEG_2: 0.60,
                MarketState.DOWN_LEG_3: 0.55,
                MarketState.DOWN_LEG_PLUS: 0.45,
                MarketState.BREAKOUT: 0.70,
                MarketState.CLIMAX: 0.35,
                MarketState.EXHAUSTION: 0.40,
                MarketState.PULLBACK: 0.60,
                MarketState.RESISTANCE: 0.50,
                MarketState.VACUUM: 0.45,
                MarketState.CALM: 0.55,
                MarketState.UNKNOWN: 0.50
            }
            return default_probs.get(state, 0.5)
        
        # 计算该状态下后续价格的盈利情况
        profitable_count = 0
        for occurrence in state_occurrences:
            # 找到状态出现后的K线索引
            occurrence_index = next((i for i, s in enumerate(self.state_history) if s == occurrence), -1)
            
            if occurrence_index == -1 or occurrence_index + 1 >= len(self.klines):
                continue
            
            # 获取状态出现后的价格变化
            entry_price = occurrence['price']
            exit_price = self.klines[occurrence_index + 1].close  # 下一根K线的收盘价
            
            # 根据趋势方向判断是否盈利
            if state.value.startswith("UP") or state in [MarketState.BREAKOUT, MarketState.PULLBACK]:
                profitable = exit_price > entry_price
            elif state.value.startswith("DOWN") or state in [MarketState.BREAKOUT, MarketState.PULLBACK]:
                profitable = exit_price < entry_price
            else:
                # 对于中性状态，使用绝对价格变化
                price_change = abs(exit_price - entry_price) / entry_price
                profitable = price_change > 0.005  # 超过0.5%的变化视为有机会盈利
            
            if profitable:
                profitable_count += 1
        
        return profitable_count / len(state_occurrences)
    
    def _adjust_for_trend_strength(self, trend_strength):
        """根据趋势强度调整概率"""
        # 趋势越强，趋势跟随策略的成功率越高
        if trend_strength > 0.7:
            return 1.2  # 强势趋势，提高概率
        elif trend_strength > 0.4:
            return 1.0  # 中等趋势，不影响概率
        else:
            return 0.8  # 弱势趋势，降低概率
    
    def _adjust_for_volatility(self, volatility):
        """根据波动性调整概率"""
        # 适中的波动性最有利于交易，过高或过低的波动性都会降低成功率
        if 0.01 < volatility < 0.03:
            return 1.1  # 理想波动性范围
        elif volatility < 0.005:
            return 0.7  # 波动性过低，难以获利
        elif volatility > 0.05:
            return 0.6  # 波动性过高，风险增大
        else:
            return 1.0  # 正常波动性
    
    def _adjust_for_volume(self, volume_analysis):
        """根据成交量分析调整概率"""
        if not volume_analysis:
            return 1.0  # 无成交量数据，不影响概率
        
        # 成交量确认趋势时提高概率
        if volume_analysis.get('volume_confirmation', False):
            return 1.15
        # 成交量与价格背离时降低概率
        elif volume_analysis.get('volume_divergence', False):
            return 0.85
        else:
            return 1.0
    
    def _adjust_for_price_position(self, price_position):
        """根据价格位置调整概率"""
        # 极端位置（极高或极低）的获利概率较低
        if price_position > 0.8 or price_position < 0.2:
            return 0.8  # 极端位置，降低概率
        elif 0.4 < price_position < 0.6:
            return 1.1  # 中间位置，提高概率
        else:
            return 1.0  # 正常位置
    
    def _adjust_for_support_resistance(self, support_resistance):
        """根据支撑阻力调整概率"""
        adjustment = 1.0
        
        # 接近强支撑或阻力时降低突破概率
        if support_resistance.get('near_strong_resistance', False):
            adjustment *= 0.7
        if support_resistance.get('near_strong_support', False):
            adjustment *= 0.7
        
        # 刚刚突破支撑或阻力时提高趋势延续概率
        if support_resistance.get('broken_resistance', False):
            adjustment *= 1.2
        if support_resistance.get('broken_support', False):
            adjustment *= 1.2
        
        return adjustment
    
    def _adjust_for_time_factors(self, time_analysis):
        """根据时间因素调整概率"""
        adjustment = 1.0
        
        # 盘整时间过长后突破的概率较高
        if time_analysis.get('extended_consolidation', False):
            adjustment *= 1.15
        
        # 特定时间段的效果调整
        if time_analysis.get('high_volatility_period', False):
            adjustment *= 0.9  # 高波动时段风险较高
        
        return adjustment
    
    def _adjust_for_patterns(self, patterns):
        """根据模式识别调整概率"""
        adjustment = 1.0
        
        # 有利模式提高概率
        favorable_patterns = ['breakout', 'continuation', 'reversal_confirmation']
        for pattern in favorable_patterns:
            if pattern in patterns:
                adjustment *= 1.1
        
        # 不利模式降低概率
        unfavorable_patterns = ['exhaustion', 'divergence', 'reversal_warning']
        for pattern in unfavorable_patterns:
            if pattern in patterns:
                adjustment *= 0.9
        
        return adjustment
    
    def _adjust_for_sentiment(self, sentiment):
        """根据市场情绪调整概率"""
        sentiment_adjustments = {
            "greed": 0.9,      # 贪婪情绪往往预示着反转
            "panic": 0.9,      # 恐慌情绪也可能预示着反转
            "calm": 1.1,       # 平静市场有利于趋势延续
            "ignorance": 1.0   # 不明朗情绪不影响概率
        }
        return sentiment_adjustments.get(sentiment, 1.0)
    
    def plot_analysis(self, lookback=50):
        """绘制分析结果"""
        if len(self.klines) < lookback:
            print("数据不足，无法绘制分析图")
            return
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(15, 10))
        
        # 提取价格数据
        prices = [k.close for k in self.klines[-lookback:]]
        timestamps = [k.timestamp for k in self.klines[-lookback:]] if hasattr(self.klines[0], 'timestamp') else range(len(prices))
        
        # 绘制价格图表
        ax1.plot(timestamps, prices, 'b-', label='Price')
        ax1.set_title('Price Movement')
        ax1.legend()
        ax1.grid(True)
        
        # 绘制状态变化
        if self.analysis_results:
            recent_results = [r for r in self.analysis_results if r['timestamp'] >= (timestamps[0] if hasattr(self.klines[0], 'timestamp') else 0)]
            
            if recent_results:
                state_dates = [r['timestamp'] for r in recent_results]
                state_prices = [next((k.close for k in self.klines if hasattr(k, 'timestamp') and k.timestamp == r['timestamp']), 0) for r in recent_results]
                state_labels = [r['state'].value for r in recent_results]
                
                unique_states = list(set(state_labels))
                color_map = {state: plt.cm.tab10(i) for i, state in enumerate(unique_states)}
                
                for i, (date, price, label) in enumerate(zip(state_dates, state_prices, state_labels)):
                    ax2.scatter(date, price, color=color_map[label], s=50)
                    if i % 5 == 0:
                        ax2.annotate(label, xy=(date, price), xytext=(date, price + 0.3), 
                                    fontsize=8, ha='center')
        
        ax2.set_title('Market State Transitions')
        ax2.grid(True)
        
        plt.tight_layout()
        plt.show()
        
        # 打印当前状态信息
        if self.analysis_results:
            latest = self.analysis_results[-1]
            print(f"当前市场状态: {latest['state'].value}")
            print(f"趋势方向: {latest['trend']}")
            print(f"获利概率: {latest['profit_probability']:.2%}")
            print(f"市场情绪: {latest['sentiment']}")
        
# ==================== 工具函数 ====================

def create_klines_from_df(df):
    """从DataFrame创建K线列表"""
    klines = []
    for idx, row in df.iterrows():
        kline = KLine(
            open=row['open'],
            close=row['close'],
            high=row['high'],
            low=row['low'],
            timestamp=idx if isinstance(idx, datetime) else None,
            volume=row.get('volume', 0.0)
        )
        klines.append(kline)
    return klines

# ==================== 示例使用 ====================

def main():
    """主函数示例"""
    ts_code =  "000001.SZ"
    analysis_dir = os.path.join('E:\stock\csv_version','analysis_results')
    csv_path = Path(analysis_dir) / f"{ts_code}_analysis.csv"
    df = pd.read_csv(csv_path, parse_dates=['trade_date'], index_col="trade_date", nrows=100)
    
    # 创建K线数据
    klines = create_klines_from_df(df)
    
    # 初始化交易系统
    trading_system = IntegratedTradingSystem(window_size=20, extreme_lookback=3)
    
    # 添加K线数据并分析
    for kline in klines:
        result = trading_system.add_kline(kline)
    
    # 生成交易信号
    signals = trading_system.get_trading_signals()
    print("交易信号:", signals)
    
    # 绘制分析结果
    trading_system.plot_analysis(lookback=50)
    
    # 显示最近的分析结果
    if trading_system.analysis_results:
        latest = trading_system.analysis_results[-1]
        print("\n最近分析结果:")
        for key, value in latest.items():
            if key != 'timestamp':
                print(f"{key}: {value}")

if __name__ == "__main__":
    main()