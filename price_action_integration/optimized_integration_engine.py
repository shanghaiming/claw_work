#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
优化版价格行为整合引擎
使用从原始ipynb提取的函数，优化性能和准确性
"""

import numpy as np
import pandas as pd
import warnings
import json
import os
from typing import Dict, List, Any, Optional, Tuple
warnings.filterwarnings('ignore')

# 尝试导入必要的库，提供回退方案
try:
    from scipy.signal import find_peaks
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False
    print("警告: scipy不可用，将使用简化版峰值检测")

try:
    from sklearn.cluster import KMeans
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False
    print("警告: scikit-learn不可用，将使用简化版聚类")

try:
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
except ImportError:
    HAS_MATPLOTLIB = False
    print("警告: matplotlib不可用，可视化功能将禁用")


# ============================================================================
# 模块1: 枢轴点检测模块 (基于spike_bake.ipynb)
# ============================================================================

class PivotDetector:
    """优化版枢轴点检测器"""
    
    @staticmethod
    def detect_pivot_points(df: pd.DataFrame, prominence_factor: float = 0.5) -> Dict[str, Any]:
        """
        检测关键枢轴点
        基于spike_bake.ipynb的detect_pivot_points函数
        
        参数:
            df: 包含OHLCV数据的DataFrame
            prominence_factor: 峰值显著性因子
            
        返回:
            包含枢轴点信息的字典
        """
        close = df['close'].values
        high = df['high'].values
        low = df['low'].values
        open_ = df['open'].values
        
        # 1. 检测上涨尖峰（局部高点）
        if HAS_SCIPY:
            up_peaks = find_peaks(close, prominence=np.std(close) * prominence_factor)[0]
        else:
            # 简化版峰值检测
            up_peaks = PivotDetector._find_local_maxima_simple(close)
        
        # 2. 检测下跌尖峰（局部低点）
        if HAS_SCIPY:
            down_peaks = find_peaks(-close, prominence=np.std(close) * prominence_factor)[0]
        else:
            # 简化版谷值检测
            down_peaks = PivotDetector._find_local_minima_simple(close)
        
        # 3. 检测中枢棒
        pivot_bars = []
        
        # 处理上涨尖峰
        for peak_idx in up_peaks:
            # 寻找尖峰后第一根阴棒（收盘<开盘）
            for i in range(peak_idx + 1, len(df)):
                if close[i] < open_[i]:
                    pivot_bars.append({
                        'index': int(i),
                        'type': 'bearish_pivot',
                        'peak_index': int(peak_idx),
                        'price': float((high[i] + low[i]) / 2),
                        'high': float(high[i]),
                        'low': float(low[i]),
                        'date': df.index[i] if hasattr(df.index, '__getitem__') else None
                    })
                    break
        
        # 处理下跌尖峰
        for trough_idx in down_peaks:
            # 寻找尖峰后第一根阳棒（收盘>开盘）
            for i in range(trough_idx + 1, len(df)):
                if close[i] > open_[i]:
                    pivot_bars.append({
                        'index': int(i),
                        'type': 'bullish_pivot',
                        'peak_index': int(trough_idx),
                        'price': float((high[i] + low[i]) / 2),
                        'high': float(high[i]),
                        'low': float(low[i]),
                        'date': df.index[i] if hasattr(df.index, '__getitem__') else None
                    })
                    break
        
        # 整理结果
        up_peaks_info = []
        for idx in up_peaks:
            up_peaks_info.append({
                'index': int(idx),
                'price': float(close[idx]),
                'high': float(high[idx]),
                'low': float(low[idx]),
                'date': df.index[idx] if hasattr(df.index, '__getitem__') else None
            })
        
        down_peaks_info = []
        for idx in down_peaks:
            down_peaks_info.append({
                'index': int(idx),
                'price': float(close[idx]),
                'high': float(high[idx]),
                'low': float(low[idx]),
                'date': df.index[idx] if hasattr(df.index, '__getitem__') else None
            })
        
        return {
            'up_peaks': up_peaks_info,
            'down_peaks': down_peaks_info,
            'pivot_bars': pivot_bars,
            'up_peaks_indices': up_peaks.tolist() if isinstance(up_peaks, np.ndarray) else up_peaks,
            'down_peaks_indices': down_peaks.tolist() if isinstance(down_peaks, np.ndarray) else down_peaks
        }
    
    @staticmethod
    def _find_local_maxima_simple(values: np.ndarray, window: int = 5) -> List[int]:
        """简化版局部最大值检测"""
        maxima = []
        n = len(values)
        
        for i in range(window, n - window):
            is_max = True
            
            # 检查左侧窗口
            for j in range(1, window + 1):
                if values[i] <= values[i - j]:
                    is_max = False
                    break
            
            if not is_max:
                continue
            
            # 检查右侧窗口
            for j in range(1, window + 1):
                if values[i] <= values[i + j]:
                    is_max = False
                    break
            
            if is_max:
                maxima.append(i)
        
        return maxima
    
    @staticmethod
    def _find_local_minima_simple(values: np.ndarray, window: int = 5) -> List[int]:
        """简化版局部最小值检测"""
        minima = []
        n = len(values)
        
        for i in range(window, n - window):
            is_min = True
            
            # 检查左侧窗口
            for j in range(1, window + 1):
                if values[i] >= values[i - j]:
                    is_min = False
                    break
            
            if not is_min:
                continue
            
            # 检查右侧窗口
            for j in range(1, window + 1):
                if values[i] >= values[i + j]:
                    is_min = False
                    break
            
            if is_min:
                minima.append(i)
        
        return minima
    
    @staticmethod
    def identify_measurement_moves(pivot_bars: List[Dict], df: pd.DataFrame) -> List[Dict]:
        """
        识别测量运动
        基于spike_bake.ipynb的identify_measurement_moves函数
        """
        measurements = []
        
        if len(pivot_bars) < 2:
            return measurements
        
        close = df['close'].values
        
        # 计算中枢间距离
        for i in range(1, len(pivot_bars)):
            prev_pivot = pivot_bars[i-1]
            curr_pivot = pivot_bars[i]
            
            distance = abs(curr_pivot['price'] - prev_pivot['price'])
            
            # 确定突破方向
            if prev_pivot['type'] == 'bearish_pivot':
                direction = 'up' if curr_pivot['price'] > prev_pivot['price'] else 'down'
            else:
                direction = 'up' if curr_pivot['price'] > prev_pivot['price'] else 'down'
            
            # 预测目标位
            if direction == 'up':
                target = curr_pivot['price'] + distance
            else:
                target = curr_pivot['price'] - distance
            
            # 计算测量运动的起点和终点
            start_idx = prev_pivot['index']
            end_idx = curr_pivot['index']
            
            # 计算运动期间的收益率
            if start_idx < end_idx and end_idx < len(close):
                price_change = close[end_idx] / close[start_idx] - 1 if close[start_idx] != 0 else 0
            else:
                price_change = 0
            
            measurements.append({
                'start_index': start_idx,
                'end_index': end_idx,
                'start_price': prev_pivot['price'],
                'end_price': curr_pivot['price'],
                'distance': float(distance),
                'direction': direction,
                'target_price': float(target),
                'price_change_pct': float(price_change * 100)
            })
        
        return measurements


# ============================================================================
# 模块2: 补偿移动平均线模块 (基于ma_compensat.ipynb)
# ============================================================================

class CompensatedMA:
    """优化版补偿移动平均线"""
    
    @staticmethod
    def calculate_compensated_ma(
        close: np.ndarray, 
        window: int = 20, 
        beta: float = 0.3, 
        gamma: float = 0.2, 
        decay_factor: float = 0.95
    ) -> np.ndarray:
        """
        计算补偿移动平均线
        基于ma_compensat.ipynb的calculate_compensated_ma函数
        
        参数:
            close: 收盘价序列
            window: 窗口大小
            beta: 基础补偿系数 (0.2-0.5)
            gamma: 趋势增强系数 (0.1-0.3)
            decay_factor: 补偿衰减因子 (0.9-0.99)
            
        返回:
            补偿均线序列
        """
        cma = np.full(len(close), np.nan)  # 初始化补偿均线数组
        data_queue = []                    # 数据窗口
        current_sum = 0.0                  # 当前窗口和
        prev_mean = 0.0                    # 前一次均线值
        cumulative_compensation = 0.0      # 累积补偿量
        trend_strength = 0.0               # 趋势强度
        
        for i, price in enumerate(close):
            # 维护数据窗口
            data_queue.append(price)
            current_sum += price
            
            if len(data_queue) > window:
                removed = data_queue.pop(0)
                current_sum -= removed
            
            # 计算当前均线值
            if len(data_queue) == window:
                current_mean = current_sum / window
                
                # 计算补偿量
                if i >= window:
                    # 价格偏离度
                    price_deviation = price - prev_mean
                    
                    # 趋势强度计算
                    if i > window:
                        recent_trend = np.mean(close[i-5:i]) - np.mean(close[i-10:i-5])
                        trend_strength = np.tanh(recent_trend / (np.std(close[i-10:i]) + 1e-10))
                    
                    # 计算补偿
                    compensation = beta * price_deviation * (1 + gamma * trend_strength)
                    
                    # 应用衰减因子
                    cumulative_compensation = cumulative_compensation * decay_factor + compensation
                    
                    # 计算最终均线值
                    cma[i] = current_mean + cumulative_compensation
                else:
                    cma[i] = current_mean
                
                prev_mean = current_mean
            elif len(data_queue) < window and i > 0:
                # 窗口未满时的简单处理
                cma[i] = np.mean(data_queue)
        
        return cma


# ============================================================================
# 模块3: 价格区间聚类模块 (基于cluster.ipynb)
# ============================================================================

class RangeCluster:
    """优化版价格区间聚类"""
    
    @staticmethod
    def detect_price_ranges(
        close_prices: np.ndarray,
        index: pd.DatetimeIndex,
        window: int = 20,
        cluster_threshold: float = 1.0,
        min_range_length: int = 5
    ) -> Dict[str, Any]:
        """
        检测股价区间并识别趋势
        基于cluster.ipynb的detect_price_ranges函数
        
        参数:
            close_prices: 收盘价序列
            index: 对应的日期索引
            window: 趋势检测窗口大小
            cluster_threshold: 聚类边界阈值
            min_range_length: 最小震荡区间长度
            
        返回:
            包含分析结果的字典
        """
        results = {
            'trend_direction': None,
            'trend_strength': 0.0,
            'is_range': False,
            'support': None,
            'resistance': None,
            'range_start': None,
            'range_end': None,
            'range_width': 0.0
        }
        
        if len(close_prices) < window:
            return results
        
        # 1. 趋势检测（线性回归斜率）
        slopes = []
        for i in range(len(close_prices) - window):
            y = close_prices[i:i+window]
            x = np.arange(len(y))
            
            # 使用numpy的polyfit进行线性回归
            if len(y) > 1:
                slope = np.polyfit(x, y, 1)[0]
                slopes.append(slope)
        
        if slopes:
            avg_slope = np.mean(slopes)
            results['trend_direction'] = 'up' if avg_slope > 0 else 'down' if avg_slope < 0 else 'neutral'
            results['trend_strength'] = float(abs(avg_slope) / (np.std(close_prices) + 1e-10))
        
        # 2. 区间检测
        # 使用分位数方法识别支撑阻力
        support = np.percentile(close_prices, 30)
        resistance = np.percentile(close_prices, 70)
        
        results['support'] = float(support)
        results['resistance'] = float(resistance)
        results['range_width'] = float(resistance - support)
        
        # 判断是否处于区间状态
        price_range = resistance - support
        avg_price = np.mean(close_prices)
        
        # 区间判断标准：价格波动范围相对较小
        if price_range < avg_price * 0.1:  # 波动小于10%
            results['is_range'] = True
            
            # 寻找区间开始和结束位置
            in_range = False
            range_start = None
            
            for i in range(len(close_prices)):
                if support <= close_prices[i] <= resistance:
                    if not in_range:
                        in_range = True
                        range_start = i
                else:
                    if in_range:
                        range_length = i - range_start
                        if range_length >= min_range_length:
                            results['range_start'] = index[range_start] if range_start < len(index) else None
                            results['range_end'] = index[i-1] if i-1 < len(index) else None
                            break
                        in_range = False
        
        return results


# ============================================================================
# 模块4: 仓位势能分析模块 (基于仓位势能分析.ipynb)
# ============================================================================

class PositionEnergyAnalyzer:
    """优化版仓位势能分析"""
    
    @staticmethod
    def calculate_center_zones(prices: np.ndarray, min_k_lines: int = 5) -> List[Dict]:
        """
        计算中枢区域
        基于仓位势能分析.ipynb的相关函数
        
        参数:
            prices: 价格序列
            min_k_lines: 最小K线数量
            
        返回:
            中枢区域列表
        """
        if len(prices) < min_k_lines:
            return []
        
        # 简化版中枢检测：使用价格密度
        centers = []
        
        # 价格范围分箱
        price_min = np.min(prices)
        price_max = np.max(prices)
        
        if price_max == price_min:
            return []
        
        # 创建价格直方图
        n_bins = min(20, len(prices) // 5)
        hist, bin_edges = np.histogram(prices, bins=n_bins)
        
        # 识别高密度区域
        density_threshold = np.mean(hist) * 1.5
        
        for i in range(len(hist)):
            if hist[i] >= density_threshold:
                # 该分箱是一个潜在的中枢区域
                zone_low = bin_edges[i]
                zone_high = bin_edges[i+1]
                zone_center = (zone_low + zone_high) / 2
                count = hist[i]
                
                # 计算区域内实际价格的统计信息
                zone_prices = prices[(prices >= zone_low) & (prices <= zone_high)]
                
                if len(zone_prices) >= min_k_lines:
                    centers.append({
                        'price': float(zone_center),
                        'low': float(zone_low),
                        'high': float(zone_high),
                        'width': float(zone_high - zone_low),
                        'count': int(count),
                        'strength': float(count / len(prices)),
                        'std': float(np.std(zone_prices) if len(zone_prices) > 1 else 0)
                    })
        
        # 按强度排序
        centers.sort(key=lambda x: x['strength'], reverse=True)
        
        return centers
    
    @staticmethod
    def calculate_energy_components(df: pd.DataFrame) -> Dict[str, float]:
        """
        计算能量分量
        基于仓位势能分析.ipynb的calculate_energy_components函数
        """
        close = df['close'].values
        volume = df['volume'].values
        
        if len(close) < 2:
            return {}
        
        # 价格能量（基于波动率）
        returns = np.diff(np.log(close + 1e-10))
        price_energy = np.std(returns) * 100 if len(returns) > 1 else 0
        
        # 成交量能量
        volume_returns = np.diff(np.log(volume + 1e-10))
        volume_energy = np.std(volume_returns) * 100 if len(volume_returns) > 1 else 0
        
        # 价格-成交量相关性能量
        min_len = min(len(returns), len(volume_returns))
        if min_len > 1:
            corr = np.corrcoef(returns[:min_len], volume_returns[:min_len])[0, 1]
            correlation_energy = abs(corr) * 100
        else:
            correlation_energy = 0
        
        # 趋势能量
        if len(close) >= 10:
            recent_trend = np.mean(close[-5:]) - np.mean(close[-10:-5])
            avg_price = np.mean(close[-10:])
            trend_energy = abs(recent_trend / avg_price) * 100 if avg_price != 0 else 0
        else:
            trend_energy = 0
        
        return {
            'price_energy': float(price_energy),
            'volume_energy': float(volume_energy),
            'correlation_energy': float(correlation_energy),
            'trend_energy': float(trend_energy),
            'total_energy': float(price_energy + volume_energy + correlation_energy + trend_energy)
        }


# ============================================================================
# 模块5: 多周期动量模块 (基于stategy_momentum.ipynb)
# ============================================================================

class MultiMomentumAnalyzer:
    """优化版多周期动量分析"""
    
    @staticmethod
    def calculate_williams_r(
        data: pd.DataFrame,
        period: int = 14,
        high_col: str = 'high',
        low_col: str = 'low',
        close_col: str = 'close'
    ) -> pd.Series:
        """
        计算威廉指标（Williams %R）
        基于stategy_momentum.ipynb的calculate_williams_r函数
        """
        highs = data[high_col]
        lows = data[low_col]
        closes = data[close_col]
        
        williams_r = pd.Series(index=data.index, dtype=float)
        
        for i in range(period - 1, len(data)):
            window_high = highs.iloc[i-period+1:i+1].max()
            window_low = lows.iloc[i-period+1:i+1].min()
            current_close = closes.iloc[i]
            
            if window_high != window_low:
                williams_r.iloc[i] = (window_high - current_close) / (window_high - window_low) * -100
            else:
                williams_r.iloc[i] = 0
        
        return williams_r
    
    @staticmethod
    def analyze_momentum(
        df: pd.DataFrame,
        periods: List[int] = [5, 8, 13, 21, 34, 55]
    ) -> Dict[str, Any]:
        """
        分析多周期动量
        """
        close = df['close'].values
        results = {}
        
        for period in periods:
            if len(close) >= period:
                # 计算简单动量
                momentum = (close[-1] / close[-period] - 1) * 100
                
                # 计算动量强度
                period_returns = []
                for i in range(1, min(period, len(close))):
                    if close[-i-1] > 0:
                        ret = (close[-i] / close[-i-1] - 1) * 100
                        period_returns.append(ret)
                
                vol = np.std(period_returns) if len(period_returns) > 1 else 1.0
                momentum_strength = abs(momentum) / (vol + 1e-10)
                
                results[f'period_{period}'] = {
                    'momentum': float(momentum),
                    'strength': float(momentum_strength),
                    'volatility': float(vol),
                    'direction': 'bullish' if momentum > 0 else 'bearish'
                }
        
        # 计算综合动量
        if results:
            momentums = [v['momentum'] for v in results.values()]
            strengths = [v['strength'] for v in results.values()]
            
            avg_momentum = np.mean(momentums)
            avg_strength = np.mean(strengths)
            
            # 计算一致性
            directions = [1 if v['direction'] == 'bullish' else -1 for v in results.values()]
            alignment = np.mean(directions) if directions else 0
            
            results['composite'] = {
                'avg_momentum': float(avg_momentum),
                'avg_strength': float(avg_strength),
                'momentum_alignment': float(alignment),
                'momentum_consistency': float(1 - np.std(directions) / 2) if len(directions) > 1 else 0.5
            }
        
        return results


# ============================================================================
# 模块6: 价格-成交量互动模块 (基于price_vol_int.ipynb)
# ============================================================================

class PriceVolumeAnalyzer:
    """优化版价格-成交量互动分析"""
    
    @staticmethod
    def calculate_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算技术指标用于势能评估
        基于price_vol_int.ipynb的calculate_technical_indicators函数
        """
        df = df.copy()
        
        # 基础价格变化
        df['price_change'] = df['close'].pct_change()
        df['log_return'] = np.log(df['close'] / df['close'].shift(1))
        
        # K线特征
        df['body_size'] = abs(df['close'] - df['open']) / df['open']
        df['total_range'] = (df['high'] - df['low']) / df['open']
        df['upper_shadow'] = (df['high'] - np.maximum(df['open'], df['close'])) / df['open']
        df['lower_shadow'] = (np.minimum(df['open'], df['close']) - df['low']) / df['open']
        
        # 价格位置特征
        df['price_position'] = (df['close'] - df['low']) / (df['high'] - df['low'])
        
        # 移动平均线
        df['ma5'] = df['close'].rolling(5).mean()
        df['ma20'] = df['close'].rolling(20).mean()
        
        # 成交量移动平均
        df['volume_ma5'] = df['volume'].rolling(5).mean()
        
        # 相对强弱
        df['relative_strength'] = (df['close'] - df['ma20']) / df['ma20']
        
        return df
    
    @staticmethod
    def calculate_potential_energy(df: pd.DataFrame) -> pd.DataFrame:
        """
        计算势能
        基于price_vol_int.ipynb的calculate_potential_energy函数
        """
        df = df.copy()
        
        # 计算基础势能指标
        df['momentum_energy'] = df['log_return'].rolling(5).std() * 100
        df['volatility_energy'] = df['total_range'].rolling(5).mean() * 100
        df['volume_energy'] = (df['volume'] / df['volume_ma5']).rolling(5).mean() * 100
        
        # 综合势能
        df['total_energy'] = (
            df['momentum_energy'].fillna(0) * 0.4 +
            df['volatility_energy'].fillna(0) * 0.3 +
            df['volume_energy'].fillna(0) * 0.3
        )
        
        return df
    
    @staticmethod
    def analyze_price_volume_relationship(df: pd.DataFrame) -> Dict[str, Any]:
        """
        分析价格-成交量关系
        """
        close = df['close'].values
        volume = df['volume'].values
        
        if len(close) < 2:
            return {}
        
        # 价格-成交量相关性
        price_changes = np.diff(close)
        volume_changes = np.diff(volume)
        
        min_len = min(len(price_changes), len(volume_changes))
        if min_len > 1:
            corr = np.corrcoef(price_changes[:min_len], volume_changes[:min_len])[0, 1]
        else:
            corr = 0
        
        # 成交量确认分析
        if len(close) >= 2:
            recent_price_change = close[-1] - close[-2]
            recent_volume = volume[-1]
            avg_volume = np.mean(volume[-10:]) if len(volume) >= 10 else np.mean(volume)
            
            if recent_price_change > 0 and recent_volume > avg_volume * 1.2:
                volume_confirmation = {'strength': min(1.0, recent_volume / avg_volume / 2), 'direction': 'bullish_confirmation'}
            elif recent_price_change < 0 and recent_volume > avg_volume * 1.2:
                volume_confirmation = {'strength': min(1.0, recent_volume / avg_volume / 2), 'direction': 'bearish_confirmation'}
            elif recent_price_change > 0 and recent_volume < avg_volume * 0.8:
                volume_confirmation = {'strength': 0.3, 'direction': 'bullish_divergence'}
            elif recent_price_change < 0 and recent_volume < avg_volume * 0.8:
                volume_confirmation = {'strength': 0.3, 'direction': 'bearish_divergence'}
            else:
                volume_confirmation = {'strength': 0.1, 'direction': 'neutral'}
        else:
            volume_confirmation = {'strength': 0, 'direction': 'neutral'}
        
        # 价格位置
        lookback = min(20, len(close))
        recent_high = np.max(close[-lookback:])
        recent_low = np.min(close[-lookback:])
        
        if recent_high != recent_low:
            price_position = (close[-1] - recent_low) / (recent_high - recent_low)
        else:
            price_position = 0.5
        
        # 成交量趋势
        if len(volume) >= 5:
            recent_volume_ma = np.mean(volume[-5:])
            avg_volume = np.mean(volume)
            
            if recent_volume_ma > avg_volume * 1.3:
                volume_trend = {'trend': 'increasing', 'strength': min(1.0, (recent_volume_ma - avg_volume) / avg_volume)}
            elif recent_volume_ma < avg_volume * 0.7:
                volume_trend = {'trend': 'decreasing', 'strength': min(1.0, (avg_volume - recent_volume_ma) / avg_volume)}
            else:
                volume_trend = {'trend': 'stable', 'strength': 0}
        else:
            volume_trend = {'trend': 'neutral', 'strength': 0}
        
        return {
            'price_volume_correlation': float(corr),
            'volume_confirmation': volume_confirmation,
            'price_position': float(price_position),
            'recent_high': float(recent_high),
            'recent_low': float(recent_low),
            'volume_trend': volume_trend
        }


# ============================================================================
# 主引擎: 优化版价格行为整合引擎
# ============================================================================

class OptimizedPriceActionIntegrationEngine:
    """
    优化版价格行为整合引擎
    使用优化的模块实现更准确的分析
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """初始化引擎"""
        self.data = None
        self.results = {}
        self.config = config or self._default_config()
        
        # 初始化模块
        self.modules = {
            'pivot_detector': PivotDetector(),
            'range_cluster': RangeCluster(),
            'compensated_ma': CompensatedMA(),
            'position_energy': PositionEnergyAnalyzer(),
            'multi_momentum': MultiMomentumAnalyzer(),
            'price_volume': PriceVolumeAnalyzer()
        }
    
    def _default_config(self) -> Dict[str, Any]:
        """默认配置"""
        return {
            'pivot_detection': {
                'prominence_factor': 0.5,
                'window': 5
            },
            'range_clustering': {
                'window': 20,
                'cluster_threshold': 1.0,
                'min_range_length': 5
            },
            'compensated_ma': {
                'window': 20,
                'beta': 0.3,
                'gamma': 0.2,
                'decay_factor': 0.95
            },
            'position_energy': {
                'min_k_lines': 5
            },
            'multi_momentum': {
                'periods': [5, 8, 13, 21, 34, 55]
            }
        }
    
    def load_data(self, df: pd.DataFrame):
        """加载价格数据"""
        self.data = df.copy()
        
        # 验证数据列
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"缺少必要列: {col}")
        
        print(f"数据加载成功: {len(self.data)} 行, {self.data.index[0]} 到 {self.data.index[-1]}")
    
    def run_analysis(self) -> Dict[str, Any]:
        """运行完整分析"""
        if self.data is None:
            raise ValueError("请先加载数据")
        
        print("=" * 60)
        print("开始优化版价格行为整合分析...")
        print("=" * 60)
        
        # 1. 枢轴点检测
        print("1. 运行优化版枢轴点检测...")
        pivot_config = self.config['pivot_detection']
        self.results['pivots'] = PivotDetector.detect_pivot_points(
            self.data, 
            prominence_factor=pivot_config['prominence_factor']
        )
        
        # 2. 价格区间聚类
        print("2. 运行优化版价格区间聚类...")
        range_config = self.config['range_clustering']
        self.results['ranges'] = RangeCluster.detect_price_ranges(
            self.data['close'].values,
            self.data.index,
            window=range_config['window'],
            cluster_threshold=range_config['cluster_threshold'],
            min_range_length=range_config['min_range_length']
        )
        
        # 3. 补偿移动平均线
        print("3. 计算优化版补偿移动平均线...")
        cma_config = self.config['compensated_ma']
        cma_values = CompensatedMA.calculate_compensated_ma(
            self.data['close'].values,
            window=cma_config['window'],
            beta=cma_config['beta'],
            gamma=cma_config['gamma'],
            decay_factor=cma_config['decay_factor']
        )
        self.results['cma'] = {
            'values': cma_values.tolist(),
            'config': cma_config
        }
        
        # 4. 仓位势能分析
        print("4. 计算优化版仓位势能...")
        energy_config = self.config['position_energy']
        centers = PositionEnergyAnalyzer.calculate_center_zones(
            self.data['close'].values,
            min_k_lines=energy_config['min_k_lines']
        )
        energy_components = PositionEnergyAnalyzer.calculate_energy_components(self.data)
        
        self.results['energy'] = {
            'centers': centers,
            'energy_components': energy_components,
            'config': energy_config
        }
        
        # 5. 多周期动量
        print("5. 分析优化版多周期动量...")
        momentum_config = self.config['multi_momentum']
        momentum_results = MultiMomentumAnalyzer.analyze_momentum(
            self.data,
            periods=momentum_config['periods']
        )
        self.results['momentum'] = momentum_results
        
        # 6. 价格-成交量互动
        print("6. 分析优化版价格-成交量互动...")
        # 首先计算技术指标
        df_with_indicators = PriceVolumeAnalyzer.calculate_technical_indicators(self.data)
        df_with_energy = PriceVolumeAnalyzer.calculate_potential_energy(df_with_indicators)
        price_volume_results = PriceVolumeAnalyzer.analyze_price_volume_relationship(self.data)
        
        self.results['price_volume'] = {
            'indicators_dataframe': df_with_indicators.to_dict('records')[:20],  # 只保存前20行
            'energy_dataframe': df_with_energy[['momentum_energy', 'volatility_energy', 'volume_energy', 'total_energy']].to_dict('records')[:20],
            'relationship_analysis': price_volume_results
        }
        
        # 7. 综合磁力位识别
        print("7. 综合磁力位识别与优化...")
        self.results['magnetic_levels'] = self._identify_and_optimize_magnetic_levels()
        
        # 8. 市场状态综合评估
        print("8. 市场状态综合评估...")
        self.results['market_state'] = self._assess_comprehensive_market_state()
        
        print("=" * 60)
        print("优化版分析完成!")
        print("=" * 60)
        
        return self.results
    
    def _identify_and_optimize_magnetic_levels(self) -> Dict[str, Any]:
        """识别并优化磁力位"""
        magnetic_levels = {
            'support_levels': [],
            'resistance_levels': [],
            'magnetic_zones': [],
            'strength_scores': {}
        }
        
        # 1. 从枢轴点获取关键水平
        if 'pivots' in self.results:
            pivots = self.results['pivots']
            
            for peak in pivots.get('up_peaks', []):
                magnetic_levels['resistance_levels'].append({
                    'price': peak['price'],
                    'source': 'pivot_peak',
                    'strength': 0.7,
                    'confidence': 0.8,
                    'data': peak
                })
            
            for trough in pivots.get('down_peaks', []):
                magnetic_levels['support_levels'].append({
                    'price': trough['price'],
                    'source': 'pivot_trough',
                    'strength': 0.7,
                    'confidence': 0.8,
                    'data': trough
                })
        
        # 2. 从价格区间获取支撑阻力
        if 'ranges' in self.results:
            ranges = self.results['ranges']
            
            if ranges.get('support') is not None:
                magnetic_levels['support_levels'].append({
                    'price': ranges['support'],
                    'source': 'range_cluster',
                    'strength': 0.8,
                    'confidence': 0.9 if ranges.get('is_range') else 0.6,
                    'data': ranges
                })
            
            if ranges.get('resistance') is not None:
                magnetic_levels['resistance_levels'].append({
                    'price': ranges['resistance'],
                    'source': 'range_cluster',
                    'strength': 0.8,
                    'confidence': 0.9 if ranges.get('is_range') else 0.6,
                    'data': ranges
                })
        
        # 3. 从仓位势能获取中枢区域
        if 'energy' in self.results:
            energy = self.results['energy']
            
            for center in energy.get('centers', []):
                magnetic_levels['magnetic_zones'].append({
                    'price': center['price'],
                    'low': center.get('low', center['price'] - center.get('width', 0) / 2),
                    'high': center.get('high', center['price'] + center.get('width', 0) / 2),
                    'width': center.get('width', 0),
                    'strength': center.get('strength', 0.6),
                    'confidence': min(1.0, center.get('strength', 0) * 1.5),
                    'source': 'position_energy',
                    'data': center
                })
        
        # 4. 从补偿均线获取动态水平
        if 'cma' in self.results and self.data is not None:
            cma_values = np.array(self.results['cma']['values'])
            valid_cma = cma_values[~np.isnan(cma_values)]
            
            if len(valid_cma) > 0:
                # 最近补偿均线值作为动态支撑/阻力
                recent_cma = valid_cma[-1]
                cma_strength = 0.6
                
                current_price = self.data['close'].iloc[-1]
                
                if current_price > recent_cma:
                    # 均线在价格下方，作为动态支撑
                    magnetic_levels['support_levels'].append({
                        'price': float(recent_cma),
                        'source': 'compensated_ma',
                        'strength': cma_strength,
                        'confidence': 0.7,
                        'dynamic': True,
                        'type': 'dynamic_support'
                    })
                else:
                    # 均线在价格上方，作为动态阻力
                    magnetic_levels['resistance_levels'].append({
                        'price': float(recent_cma),
                        'source': 'compensated_ma',
                        'strength': cma_strength,
                        'confidence': 0.7,
                        'dynamic': True,
                        'type': 'dynamic_resistance'
                    })
        
        # 合并相近水平并计算综合强度
        magnetic_levels = self._merge_and_score_levels(magnetic_levels)
        
        return magnetic_levels
    
    def _merge_and_score_levels(self, magnetic_levels: Dict[str, Any], price_tolerance: float = 0.02) -> Dict[str, Any]:
        """合并相近价格水平并计算综合强度"""
        # 合并支撑位
        if magnetic_levels['support_levels']:
            magnetic_levels['support_levels'] = self._merge_similar_levels(
                magnetic_levels['support_levels'],
                price_tolerance=price_tolerance,
                level_type='support'
            )
        
        # 合并阻力位
        if magnetic_levels['resistance_levels']:
            magnetic_levels['resistance_levels'] = self._merge_similar_levels(
                magnetic_levels['resistance_levels'],
                price_tolerance=price_tolerance,
                level_type='resistance'
            )
        
        # 计算综合强度分数
        all_levels = magnetic_levels['support_levels'] + magnetic_levels['resistance_levels']
        
        for level in all_levels:
            # 基础强度
            base_strength = level.get('strength', 0.5)
            
            # 来源多样性加分
            sources = level.get('sources', [])
            source_bonus = min(0.3, len(sources) * 0.1)
            
            # 置信度加权
            confidence = level.get('confidence', 0.5)
            
            # 动态水平调整
            if level.get('dynamic', False):
                dynamic_bonus = 0.1
            else:
                dynamic_bonus = 0
            
            # 计算综合分数
            composite_score = base_strength * 0.4 + confidence * 0.4 + source_bonus * 0.2 + dynamic_bonus
            level['composite_score'] = min(1.0, composite_score)
        
        return magnetic_levels
    
    def _merge_similar_levels(self, levels: List[Dict], price_tolerance: float = 0.02, level_type: str = 'support') -> List[Dict]:
        """合并相近的价格水平"""
        if not levels:
            return []
        
        # 按价格排序
        levels.sort(key=lambda x: x['price'])
        
        merged_levels = []
        current_group = []
        
        for level in levels:
            if not current_group:
                current_group.append(level)
            else:
                # 计算当前组的平均价格
                group_avg_price = np.mean([l['price'] for l in current_group])
                current_price = level['price']
                
                # 检查是否相近
                price_diff_pct = abs(current_price - group_avg_price) / group_avg_price
                
                if price_diff_pct <= price_tolerance:
                    # 加入当前组
                    current_group.append(level)
                else:
                    # 合并当前组
                    merged_level = self._merge_level_group(current_group, level_type)
                    merged_levels.append(merged_level)
                    current_group = [level]
        
        # 处理最后一组
        if current_group:
            merged_level = self._merge_level_group(current_group, level_type)
            merged_levels.append(merged_level)
        
        # 按综合强度排序
        merged_levels.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
        
        return merged_levels
    
    def _merge_level_group(self, group: List[Dict], level_type: str) -> Dict:
        """合并一组相近的水平"""
        # 计算加权平均价格
        weights = [l.get('strength', 0.5) for l in group]
        total_weight = sum(weights)
        
        if total_weight > 0:
            weighted_prices = sum(l['price'] * w for l, w in zip(group, weights))
            merged_price = weighted_prices / total_weight
        else:
            merged_price = np.mean([l['price'] for l in group])
        
        # 收集所有来源
        all_sources = []
        for level in group:
            sources = level.get('sources', [level.get('source', 'unknown')])
            if isinstance(sources, str):
                all_sources.append(sources)
            else:
                all_sources.extend(sources)
        
        unique_sources = list(set(all_sources))
        
        # 计算平均强度
        avg_strength = np.mean([l.get('strength', 0.5) for l in group])
        
        # 计算平均置信度
        avg_confidence = np.mean([l.get('confidence', 0.5) for l in group])
        
        # 检查是否包含动态水平
        has_dynamic = any(l.get('dynamic', False) for l in group)
        
        return {
            'price': float(merged_price),
            'sources': unique_sources,
            'source_count': len(unique_sources),
            'strength': float(avg_strength),
            'confidence': float(avg_confidence),
            'dynamic': has_dynamic,
            'type': level_type,
            'group_size': len(group),
            'price_std': float(np.std([l['price'] for l in group]) if len(group) > 1 else 0)
        }
    
    def _assess_comprehensive_market_state(self) -> Dict[str, Any]:
        """综合评估市场状态"""
        market_state = {
            'trend_direction': 'neutral',
            'trend_strength': 0.0,
            'market_regime': 'unknown',
            'volatility_level': 'medium',
            'momentum_state': 'neutral',
            'range_quality': 'unknown',
            'risk_level': 'medium'
        }
        
        # 1. 基于动量分析的趋势判断
        if 'momentum' in self.results:
            momentum = self.results['momentum']
            if 'composite' in momentum:
                comp = momentum['composite']
                avg_momentum = comp.get('avg_momentum', 0)
                
                if avg_momentum > 2.0:
                    market_state['trend_direction'] = 'bullish'
                    market_state['trend_strength'] = min(1.0, avg_momentum / 20.0)
                    market_state['momentum_state'] = 'strong_bullish'
                elif avg_momentum > 0.5:
                    market_state['trend_direction'] = 'bullish'
                    market_state['trend_strength'] = min(1.0, avg_momentum / 10.0)
                    market_state['momentum_state'] = 'bullish'
                elif avg_momentum < -2.0:
                    market_state['trend_direction'] = 'bearish'
                    market_state['trend_strength'] = min(1.0, abs(avg_momentum) / 20.0)
                    market_state['momentum_state'] = 'strong_bearish'
                elif avg_momentum < -0.5:
                    market_state['trend_direction'] = 'bearish'
                    market_state['trend_strength'] = min(1.0, abs(avg_momentum) / 10.0)
                    market_state['momentum_state'] = 'bearish'
        
        # 2. 基于价格区间的市场状态判断
        if 'ranges' in self.results:
            ranges = self.results['ranges']
            
            if ranges.get('is_range', False):
                market_state['market_regime'] = 'range'
                
                # 评估区间质量
                range_width = ranges.get('range_width', 0)
                if range_width > 0:
                    avg_price = np.mean(self.data['close'].values) if self.data is not None else 1
                    range_pct = range_width / avg_price
                    
                    if range_pct < 0.05:
                        market_state['range_quality'] = 'tight'
                        market_state['volatility_level'] = 'low'
                    elif range_pct < 0.1:
                        market_state['range_quality'] = 'normal'
                        market_state['volatility_level'] = 'medium'
                    else:
                        market_state['range_quality'] = 'wide'
                        market_state['volatility_level'] = 'high'
            else:
                market_state['market_regime'] = 'trend'
                
                # 趋势强度分类
                trend_strength = market_state['trend_strength']
                if trend_strength > 0.7:
                    market_state['volatility_level'] = 'high'
                elif trend_strength > 0.3:
                    market_state['volatility_level'] = 'medium'
                else:
                    market_state['volatility_level'] = 'low'
        
        # 3. 基于价格-成交量关系的风险评估
        if 'price_volume' in self.results:
            pv = self.results['price_volume']['relationship_analysis']
            volume_confirmation = pv.get('volume_confirmation', {})
            
            if volume_confirmation.get('direction') in ['bullish_confirmation', 'bearish_confirmation']:
                # 成交量确认趋势，风险较低
                market_state['risk_level'] = 'low'
            elif volume_confirmation.get('direction') in ['bullish_divergence', 'bearish_divergence']:
                # 成交量背离，风险较高
                market_state['risk_level'] = 'high'
        
        return market_state
    
    def generate_detailed_report(self) -> Dict[str, Any]:
        """生成详细分析报告"""
        report = {
            'summary': {
                'analysis_timestamp': pd.Timestamp.now().isoformat(),
                'data_points': len(self.data) if self.data is not None else 0,
                'analysis_modules': list(self.modules.keys()),
                'total_magnetic_levels': 0,
                'market_state_summary': {}
            },
            'magnetic_levels_analysis': self.results.get('magnetic_levels', {}),
            'market_state': self.results.get('market_state', {}),
            'module_results': {},
            'trading_implications': self._generate_trading_implications(),
            'recommendations': self._generate_recommendations()
        }
        
        # 统计磁力位数量
        mag_levels = self.results.get('magnetic_levels', {})
        report['summary']['total_magnetic_levels'] = (
            len(mag_levels.get('support_levels', [])) + 
            len(mag_levels.get('resistance_levels', [])) +
            len(mag_levels.get('magnetic_zones', []))
        )
        
        # 市场状态摘要
        market_state = self.results.get('market_state', {})
        report['summary']['market_state_summary'] = {
            'trend': market_state.get('trend_direction', 'unknown'),
            'regime': market_state.get('market_regime', 'unknown'),
            'momentum': market_state.get('momentum_state', 'unknown')
        }
        
        # 模块结果摘要
        for module_name, module_result in self.results.items():
            if module_name in ['magnetic_levels', 'market_state']:
                continue
            
            if isinstance(module_result, dict):
                # 提取关键信息
                if module_name == 'pivots':
                    summary = {
                        'up_peaks': len(module_result.get('up_peaks', [])),
                        'down_peaks': len(module_result.get('down_peaks', [])),
                        'pivot_bars': len(module_result.get('pivot_bars', []))
                    }
                elif module_name == 'ranges':
                    summary = {
                        'trend_direction': module_result.get('trend_direction'),
                        'is_range': module_result.get('is_range'),
                        'support': module_result.get('support'),
                        'resistance': module_result.get('resistance')
                    }
                elif module_name == 'momentum':
                    if 'composite' in module_result:
                        comp = module_result['composite']
                        summary = {
                            'avg_momentum': comp.get('avg_momentum'),
                            'momentum_alignment': comp.get('momentum_alignment'),
                            'direction': 'bullish' if comp.get('avg_momentum', 0) > 0 else 'bearish'
                        }
                    else:
                        summary = {'periods_analyzed': len(module_result)}
                else:
                    summary = {'has_results': True}
            else:
                summary = {'has_results': True}
            
            report['module_results'][module_name] = summary
        
        return report
    
    def _generate_trading_implications(self) -> Dict[str, Any]:
        """生成交易含义"""
        implications = {
            'key_levels': [],
            'potential_setups': [],
            'risk_warnings': [],
            'monitoring_points': [],
            'entry_considerations': [],
            'exit_considerations': []
        }
        
        # 关键水平
        mag_levels = self.results.get('magnetic_levels', {})
        
        for level in mag_levels.get('support_levels', []):
            implications['key_levels'].append({
                'type': 'support',
                'price': level['price'],
                'composite_score': level.get('composite_score', 0.5),
                'sources': level.get('sources', ['unknown']),
                'action': 'watch_for_bounce_or_break',
                'confidence': level.get('confidence', 0.5)
            })
        
        for level in mag_levels.get('resistance_levels', []):
            implications['key_levels'].append({
                'type': 'resistance',
                'price': level['price'],
                'composite_score': level.get('composite_score', 0.5),
                'sources': level.get('sources', ['unknown']),
                'action': 'watch_for_rejection_or_breakout',
                'confidence': level.get('confidence', 0.5)
            })
        
        # 基于市场状态的潜在设置
        market_state = self.results.get('market_state', {})
        regime = market_state.get('market_regime', 'unknown')
        trend_dir = market_state.get('trend_direction', 'neutral')
        
        if regime == 'range':
            implications['potential_setups'].append({
                'type': 'range_trading',
                'description': '区间交易策略：在支撑位附近买入，阻力位附近卖出',
                'confidence': 0.7,
                'risk_level': 'medium',
                'key_considerations': [
                    '等待价格接近区间边界',
                    '使用小止损（区间宽度内）',
                    '区间突破时及时退出'
                ]
            })
        elif regime == 'trend':
            if trend_dir == 'bullish':
                implications['potential_setups'].append({
                    'type': 'trend_following',
                    'description': '上升趋势跟踪：回调至支撑位时买入',
                    'confidence': 0.6,
                    'risk_level': 'medium',
                    'key_considerations': [
                        '等待回调至动态支撑位',
                        '趋势确认后加仓',
                        '使用移动止损跟随趋势'
                    ]
                })
            elif trend_dir == 'bearish':
                implications['potential_setups'].append({
                    'type': 'trend_following',
                    'description': '下降趋势跟踪：反弹至阻力位时卖出',
                    'confidence': 0.6,
                    'risk_level': 'high',
                    'key_considerations': [
                        '等待反弹至动态阻力位',
                        '趋势确认后加仓',
                        '使用移动止损跟随趋势'
                    ]
                })
        
        # 风险警告
        risk_level = market_state.get('risk_level', 'medium')
        if risk_level == 'high':
            implications['risk_warnings'].append({
                'type': 'high_risk',
                'description': '高风险市场环境，建议减小仓位或观望',
                'reason': '成交量背离或高波动性'
            })
        
        # 监控点
        if 'price_volume' in self.results:
            pv = self.results['price_volume']['relationship_analysis']
            volume_confirmation = pv.get('volume_confirmation', {})
            
            if volume_confirmation.get('direction', '').endswith('divergence'):
                implications['monitoring_points'].append({
                    'type': 'volume_divergence',
                    'description': '价格-成交量背离，可能预示反转',
                    'action': '密切关注价格行为确认'
                })
        
        return implications
    
    def _generate_recommendations(self) -> Dict[str, Any]:
        """生成投资建议"""
        recommendations = {
            'overall': 'neutral',
            'position_sizing': 'normal',
            'time_horizon': 'medium_term',
            'specific_actions': [],
            'avoid_actions': []
        }
        
        market_state = self.results.get('market_state', {})
        regime = market_state.get('market_regime', 'unknown')
        trend_dir = market_state.get('trend_direction', 'neutral')
        risk_level = market_state.get('risk_level', 'medium')
        
        # 整体建议
        if regime == 'range' and risk_level == 'low':
            recommendations['overall'] = 'cautiously_positive'
            recommendations['position_sizing'] = 'small_to_normal'
            recommendations['specific_actions'].append('考虑区间交易策略')
            recommendations['specific_actions'].append('在支撑位附近寻找买入机会')
            recommendations['avoid_actions'].append('避免在区间中部开仓')
        
        elif regime == 'trend' and trend_dir == 'bullish' and risk_level != 'high':
            recommendations['overall'] = 'positive'
            recommendations['position_sizing'] = 'normal_to_large'
            recommendations['specific_actions'].append('考虑趋势跟踪策略')
            recommendations['specific_actions'].append('回调至支撑位时买入')
            recommendations['avoid_actions'].append('避免逆势做空')
        
        elif regime == 'trend' and trend_dir == 'bearish':
            recommendations['overall'] = 'negative'
            recommendations['position_sizing'] = 'small'
            recommendations['specific_actions'].append('考虑逢高做空或观望')
            recommendations['avoid_actions'].append('避免抄底买入')
        
        elif risk_level == 'high':
            recommendations['overall'] = 'cautious'
            recommendations['position_sizing'] = 'small'
            recommendations['specific_actions'].append('减小仓位规模')
            recommendations['specific_actions'].append('增加风险管理')
            recommendations['avoid_actions'].append('避免大仓位交易')
        
        return recommendations
    
    def print_report(self):
        """打印分析报告"""
        report = self.generate_detailed_report()
        
        print("\n" + "=" * 60)
        print("优化版价格行为整合分析报告")
        print("=" * 60)
        
        # 基本信息
        print(f"\n📊 分析概要")
        print(f"   分析时间: {report['summary']['analysis_timestamp']}")
        print(f"   数据点数: {report['summary']['data_points']}")
        print(f"   分析模块: {', '.join(report['summary']['analysis_modules'])}")
        print(f"   磁力位总数: {report['summary']['total_magnetic_levels']}")
        
        # 市场状态
        state_summary = report['summary']['market_state_summary']
        print(f"\n📈 市场状态摘要")
        print(f"   趋势方向: {state_summary.get('trend', '未知')}")
        print(f"   市场状态: {state_summary.get('regime', '未知')}")
        print(f"   动量状态: {state_summary.get('momentum', '未知')}")
        
        # 详细市场状态
        market_state = report['market_state']
        print(f"\n🔍 详细市场状态")
        for key, value in market_state.items():
            print(f"   {key}: {value}")
        
        # 关键交易水平
        print(f"\n🎯 关键交易水平 (前10个)")
        key_levels = report['trading_implications']['key_levels']
        if key_levels:
            key_levels.sort(key=lambda x: x.get('composite_score', 0), reverse=True)
            for i, level in enumerate(key_levels[:10]):
                sources = ', '.join(level.get('sources', ['未知']))
                print(f"   {i+1}. {level['type']}: {level['price']:.2f} (分数: {level['composite_score']:.2f}, 来源: {sources})")
        else:
            print("   未识别到关键水平")
        
        # 潜在交易设置
        print(f"\n💡 潜在交易设置")
        setups = report['trading_implications']['potential_setups']
        if setups:
            for setup in setups:
                print(f"   {setup['type']}: {setup['description']} (置信度: {setup['confidence']:.2f}, 风险: {setup['risk_level']})")
        else:
            print("   未识别到明显交易设置")
        
        # 投资建议
        print(f"\n✅ 投资建议")
        rec = report['recommendations']
        print(f"   整体建议: {rec['overall']}")
        print(f"   仓位建议: {rec['position_sizing']}")
        print(f"   时间视野: {rec['time_horizon']}")
        
        if rec['specific_actions']:
            print(f"   建议行动:")
            for action in rec['specific_actions']:
                print(f"     • {action}")
        
        if rec['avoid_actions']:
            print(f"   避免行动:")
            for action in rec['avoid_actions']:
                print(f"     • {action}")
        
        print("\n" + "=" * 60)
        print("报告生成完成")
        print("=" * 60)
    
    def save_results(self, output_dir: str = "results"):
        """保存分析结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存详细报告
        report = self.generate_detailed_report()
        report_path = os.path.join(output_dir, "detailed_report.json")
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"详细报告已保存到: {report_path}")
        
        # 保存原始结果（简化版）
        simplified_results = {}
        for key, value in self.results.items():
            if key in ['cma', 'price_volume']:
                # 这些可能包含大数据，简化保存
                if key == 'cma':
                    simplified_results[key] = {
                        'config': value.get('config', {}),
                        'values_sample': value.get('values', [])[-20:] if value.get('values') else []
                    }
                elif key == 'price_volume':
                    simplified_results[key] = {
                        'relationship_analysis': value.get('relationship_analysis', {}),
                        'has_indicators_data': bool(value.get('indicators_dataframe'))
                    }
            else:
                simplified_results[key] = value
        
        results_path = os.path.join(output_dir, "analysis_results.json")
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump(simplified_results, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"分析结果已保存到: {results_path}")
        
        # 保存交易含义
        implications = report['trading_implications']
        implications_path = os.path.join(output_dir, "trading_implications.json")
        with open(implications_path, 'w', encoding='utf-8') as f:
            json.dump(implications, f, indent=2, default=str, ensure_ascii=False)
        
        print(f"交易含义已保存到: {implications_path}")


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函数"""
    print("优化版价格行为理论与技术分析工具整合系统")
    print("版本: 2.0 - 基于原始算法优化")
    print("=" * 60)
    
    # 创建引擎
    engine = OptimizedPriceActionIntegrationEngine()
    
    # 生成示例数据
    print("\n生成优化示例数据...")
    dates = pd.date_range('2024-01-01', periods=150, freq='D')
    np.random.seed(42)
    
    # 生成更有意义的模拟数据
    base_price = 100
    
    # 1. 主要趋势
    main_trend = np.linspace(0, 30, 150)
    
    # 2. 中期周期
    medium_cycle = 15 * np.sin(np.linspace(0, 3*np.pi, 150))
    
    # 3. 短期波动
    short_noise = np.random.normal(0, 5, 150)
    
    # 4. 支撑阻力区域（模拟磁力位）
    support_zone = 110 + 5 * np.sin(np.linspace(0, 2*np.pi, 150))
    resistance_zone = 130 + 5 * np.sin(np.linspace(0, 2*np.pi, 150))
    
    # 综合价格
    closes = base_price + main_trend + medium_cycle * 0.3 + short_noise * 0.5
    
    # 添加明显的支撑阻力效应
    for i in range(len(closes)):
        if closes[i] < support_zone[i]:
            # 接近支撑区域，有反弹倾向
            closes[i] = support_zone[i] + np.random.uniform(0, 3)
        elif closes[i] > resistance_zone[i]:
            # 接近阻力区域，有回落倾向
            closes[i] = resistance_zone[i] - np.random.uniform(0, 3)
    
    # 生成OHLCV数据
    opens = closes - np.random.uniform(0.5, 2.5, 150)
    highs = closes + np.random.uniform(0.5, 4.0, 150)
    lows = closes - np.random.uniform(0.5, 4.0, 150)
    volumes = np.random.lognormal(10, 0.7, 150) * 1000
    
    # 在关键位置增加成交量
    pivot_indices = [30, 60, 90, 120]
    for idx in pivot_indices:
        if idx < len(volumes):
            volumes[idx] *= 2.5
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=dates)
    
    # 加载数据
    engine.load_data(df)
    
    # 运行分析
    results = engine.run_analysis()
    
    # 打印报告
    engine.print_report()
    
    # 保存结果
    engine.save_results("optimized_results")
    
    # 可视化（如果可用）
    if HAS_MATPLOTLIB:
        print("\n生成可视化图表...")
        # 这里可以添加可视化代码
        print("可视化功能待实现")
    
    print("\n✅ 优化版整合完成！")
    print("结果已保存到 'optimized_results' 目录")


if __name__ == "__main__":
    main()