import pandas as pd
from pathlib import Path
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
import datetime
import numpy as np
from scipy import stats, signal
from scipy import cluster
from scipy.signal import argrelextrema
pd.set_option('future.no_silent_downcasting', True)
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上上一级目录


CONFIG = {
    "PERIODS": [5, 8, 13, 21, 34, 55],  # 需要计算的周期
    "MIN_DATA_DAYS": 55,                # 需要的最少数据天数
    "BATCH_SIZE": 300,                  # 分批处理数量
    "OUTPUT_FILE": "stock_variance_rank.csv"  # 输出文件名
}
def tsma_fast(data, n):
    """极速TSMA实现（参数n为周期数）"""
    data = np.asarray(data)
    length = len(data)
    if n <= 0 or n > length:
        return np.full_like(data, np.nan)
    
    # 生成滑动窗口视图（倒序）
    windows = sliding_window_view(data, n)[:, ::-1]
    m = len(windows)
    
    # 预计算绝对时间索引矩阵
    i_indices = np.arange(n-1, n-1 + m)  # 窗口结束的原始索引
    x = i_indices[:, None] - np.arange(n)
    
    # 批量计算核心项
    y_sum = windows.sum(axis=1)
    x_sum = x.sum(axis=1)
    xx_sum = (x ** 2).sum(axis=1)
    xy_sum = (x * windows).sum(axis=1)
    
    denominator = xx_sum - (x_sum ** 2) / n
    numerator = xy_sum - (y_sum * x_sum) / n
    k = np.divide(numerator, denominator, where=denominator != 0)
    b = (y_sum / n) - k * (x_sum / n)
    
    tsma = k * i_indices + b + k
    
    result = np.full_like(data, np.nan)
    result[n-1 : n-1 + m] = np.where(denominator != 0, tsma, np.nan)
    return result

def detect_single_divergence(df, indicator_col='macd', window_size=30):
    """
    单一指标顶背离检测函数
    参数：
    df - 包含以下列的DataFrame:
         - high: 价格高点
         - close: 收盘价
         - [indicator_col]: 指标列（如macd/vr）
    indicator_col - 要检测的指标列名（默认'macd'）
    window_size - 检测窗口大小（默认14）
    
    返回：
    包含divergence_status列的DataFrame，取值：
    'normal' - 正常状态
    'tbd' - 待确认背离
    'confirmed' - 确认背离
    """
    df = df.copy()
    df['divergence_status'] = 'normal'
    original_index = df.index
    df = df.reset_index(drop=True)
    
    current_status = 'normal'
    reference_high = None
    reference_indicator = None
    
    for i in range(1, len(df)):
        current_high = df.at[i, 'high']
        current_close = df.at[i, 'close']
        current_indicator = df.at[i, indicator_col]
        
        # 状态转移逻辑
        if current_status == 'normal':
            start_idx = max(0, i - window_size)
            window = df.iloc[start_idx:i]
            
            if not window.empty:
                prev_high_idx = window['high'].idxmax()
                prev_high = window.at[prev_high_idx, 'high']
                prev_indicator = window.at[prev_high_idx, indicator_col]
                
                # 价格创新高但指标未新高
                if (current_high > prev_high) and (current_indicator < prev_indicator):
                    current_status = 'tbd'
                    reference_high = prev_high
                    reference_indicator = prev_indicator
        
        elif current_status == 'tbd':
            # 情况1：价格创新高
            if current_high > reference_high:
                if current_indicator >= reference_indicator:
                    current_status = 'normal'
            
            # 情况2：价格下跌
            if current_close < df.at[i-1, 'close']:
                if current_indicator < reference_indicator:
                    current_status = 'confirmed'
                else:
                    current_status = 'normal'
        
        elif current_status == 'confirmed':
            # 清除条件：价格连续2日上涨 或 指标连续2日增加
            clear_cond = False
            if i >= 2:
                price_up = (current_close > df.at[i-1, 'close']) and \
                          (df.at[i-1, 'close'] > df.at[i-2, 'close'])
                indicator_up = (current_indicator > df.at[i-1, indicator_col]) and \
                              (df.at[i-1, indicator_col] > df.at[i-2, indicator_col])
                clear_cond = price_up or indicator_up
            
            if clear_cond:
                current_status = 'normal'
                reference_high = None
                reference_indicator = None
        
        df.at[i, 'divergence_status_' + indicator_col] = current_status
    
    df.index = original_index
    return df

def detect_price_ranges(close_prices, index, window=20, cluster_threshold=1.0, min_range_length=5):
    """
    检测股价区间并识别趋势
    
    参数:
        close_prices: 收盘价序列 (np.array)
        index: 对应的日期索引 (DatetimeIndex)
        window: 趋势检测窗口大小
        cluster_threshold: 聚类边界阈值
        min_range_length: 最小震荡区间长度
        
    返回:
        dict: 包含分析结果
    """
    results = {
        'trend_direction': None, 
        'is_range': False, 
        'support': None, 
        'resistance': None,
        'range_start': None,
        'range_end': None
    }
    
    # 1. 趋势检测（线性回归斜率）
    slopes = []
    for i in range(len(close_prices) - window):
        y = close_prices[i:i+window]
        x = np.arange(len(y))
        slope = stats.linregress(x, y).slope
        slopes.append(slope)
    
    avg_slope = np.mean(slopes)
    
    # 根据斜率判断趋势方向
    if avg_slope > 0.05:
        results['trend_direction'] = '上升趋势'
    elif avg_slope < -0.05:
        results['trend_direction'] = '下降趋势'
    else:
        results['trend_direction'] = '震荡趋势'
    
    # 2. 区间识别（局部极值点）
    max_indices = signal.argrelextrema(close_prices, np.greater, order=5)[0]
    min_indices = signal.argrelextrema(close_prices, np.less, order=5)[0]
    
    resistance = close_prices[max_indices]
    support = close_prices[min_indices]
    
    # 3. 边界聚类分析
    if len(resistance) > 3 and len(support) > 3:
        # 聚类分析找出主要支撑/阻力位
        resistance_centers = cluster.vq.kmeans(resistance.reshape(-1,1), 2)[0]
        support_centers = cluster.vq.kmeans(support.reshape(-1,1), 2)[0]
        
        resistance_range = np.abs(resistance_centers[0] - resistance_centers[1])
        support_range = np.abs(support_centers[0] - support_centers[1])
        
        # 判断是否形成有效区间
        if resistance_range < cluster_threshold and support_range < cluster_threshold:
            support_level = float(min(support_centers))  # 转换为float
            resistance_level = float(max(resistance_centers))  # 转换为float
            
            # 检查区间长度是否足够
            if len(close_prices) >= min_range_length:
                results['is_range'] = True
                results['support'] = support_level
                results['resistance'] = resistance_level
                results['range_start'] = index[0]
                results['range_end'] = index[-1]
    
    return results

def add_price_range_indicators(df, 
                               price_col='close', 
                               window_size=20,
                               cluster_threshold=1.0,
                               min_range_length=10):
    """
    在DataFrame中添加滚动价格区间分析指标
    
    参数:
    df -- 原始DataFrame (需按时间顺序排列，最近的最后)
    price_col -- 价格列名 (默认'close')
    window_size -- 分析窗口大小 (默认20)
    cluster_threshold -- 聚类边界阈值 (默认1.0)
    min_range_length -- 最小震荡区间长度 (默认10)
    
    返回:
    添加了六列新特征的DataFrame:
      'trend_direction' - 趋势方向（上升趋势、下降趋势、震荡趋势）
      'is_range' - 是否形成价格区间
      'support' - 支撑位
      'resistance' - 阻力位
      'range_start' - 区间开始日期
      'range_end' - 区间结束日期
    """
    # 创建新列
    df['trend_direction'] = None
    df['is_range'] = False
    df['support'] = np.nan
    df['resistance'] = np.nan
    df['range_start'] = pd.NaT  # 时间戳类型的NA
    df['range_end'] = pd.NaT
    
    # 滚动计算
    for i in range(window_size, len(df)):
        # 获取当前窗口数据
        window_data = df.iloc[i-window_size:i+1]
        
        # 提取收盘价序列和索引
        close_prices = window_data[price_col].values
        index = window_data.index
        
        # 检测价格区间
        results = detect_price_ranges(
            close_prices,
            index,
            window=window_size,
            cluster_threshold=cluster_threshold,
            min_range_length=min_range_length
        )
        
        # 将结果写入当前行的新列
        df.loc[df.index[i], 'trend_direction'] = results['trend_direction']
        df.loc[df.index[i], 'is_range'] = results['is_range']
        df.loc[df.index[i], 'support'] = results['support']
        df.loc[df.index[i], 'resistance'] = results['resistance']
        df.loc[df.index[i], 'range_start'] = results['range_start']
        df.loc[df.index[i], 'range_end'] = results['range_end']
    
    return df

def detect_ma_trend_change(ma_series, window=None, strictness=3):
    """
    检测均线序列是否出现过极大值（局部峰值），要求峰值大于左右各3个点
    
    参数:
    ma_series -- 均线值序列（Pandas Series），按时间顺序排列（最近的在最后）
    window -- 检测窗口大小（最近的N个数据点，None表示使用全部数据）
    strictness -- 峰值严格程度，即要求大于左右几个点（默认为3）
    
    返回:
    has_extreme -- 布尔值，表示是否出现过极大值
    extreme_indices -- 所有极大值点在原始序列中的索引位置列表
    """
    # 转换为NumPy数组
    ma_values = ma_series.values
    
    # 如果指定了检测窗口，只取最近的数据
    if window is not None and len(ma_values) > window:
        start_idx = len(ma_values) - window
        ma_values = ma_values[-window:]
    else:
        start_idx = 0
    
    # 计算需要的最小数据量
    min_points = 2 * strictness + 1
    
    # 检查数据量是否足够
    if len(ma_values) < min_points:
        return False, []
    
    # 使用argrelextrema查找局部极大值
    # order=strictness表示每个极大值点必须大于左右各strictness个点
    max_indices = argrelextrema(ma_values, np.greater, order=strictness)[0]
    
    # 映射回原始索引
    extreme_indices = [int(idx + start_idx) for idx in max_indices]
    has_extreme = len(extreme_indices) > 0
    
    return has_extreme, extreme_indices
 
def detect_cross_events(df, fast_col='tsma5', slow_col='tsma8', window_size=13):
    """
    检测最近N日(默认13日)内是否发生过快速均线上穿慢速均线后又下穿慢速均线
    
    参数:
    df : DataFrame - 包含均线数据的DataFrame
    fast_col : str - 快速均线列名（默认'tsma5'）
    slow_col : str - 慢速均线列名（默认'tsma8'）
    window_size : int - 检测窗口大小（单位：交易日）
    
    返回:
    int - 最近window_size日内发生金叉后死叉的次数
    """
    # 1. 确保数据足够
    if len(df) < window_size:
        window_size = len(df)
    
    # 2. 提取最近window_size日的数据
    recent_data = df.iloc[-window_size:]
    
    # 3. 识别金叉和死叉
    golden_cross = False
    event_count = 0
    
    # 4. 遍历检测金叉后死叉的事件
    for i in range(1, len(recent_data)):
        # 获取当前和前一日数据
        prev_fast = recent_data[fast_col].iloc[i-1]
        prev_slow = recent_data[slow_col].iloc[i-1]
        curr_fast = recent_data[fast_col].iloc[i]
        curr_slow = recent_data[slow_col].iloc[i]
        
        # 检查金叉：当日快速线 > 慢速线 且 前一日快速线 <= 慢速线
        if curr_fast > curr_slow and prev_fast <= prev_slow:
            golden_cross = True
            golden_index = i
        
        # 检查死叉：当日快速线 < 慢速线 且 前一日快速线 >= 慢速线
        if curr_fast < curr_slow and prev_fast >= prev_slow:
            # 如果之前有金叉且死叉在金叉之后（至少间隔2天）
            if golden_cross and i > golden_index :
                event_count += 1
                # 重置金叉状态
                golden_cross = False
    
    return event_count
 
def calculate_williams_r(data, period=5, high_col='high', low_col='low', close_col='close'):
    """
    计算威廉指标（Williams %R），适配DataFrame输入
    
    参数：
    data : DataFrame
        必须包含最高价、最低价、收盘价列（列名可自定义）
    period : int
        计算周期（默认14）
    high_col, low_col, close_col : str
        指定最高价、最低价、收盘价的列名
    
    返回：
    Series
        Williams %R值，与原始数据索引对齐
    """
    # 确保输入是DataFrame
    if not isinstance(data, pd.DataFrame):
        raise ValueError("输入数据必须是Pandas DataFrame")
    
    # 检查必要的列是否存在
    required_cols = [high_col, low_col, close_col]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise KeyError(f"缺失必要列: {missing_cols}")
    
    # 计算滚动窗口内的最高价和最低价
    highest_high = data[high_col].rolling(window=period, min_periods=period).max()
    lowest_low = data[low_col].rolling(window=period, min_periods=period).min()
    
    # 计算Williams %R
    numerator = highest_high - data[close_col]
    denominator = highest_high - lowest_low
    williams_r1 = (numerator / denominator) * -100
    
    # 处理分母为零的情况（设为NaN）
    williams_r1 = williams_r1.where(denominator != 0, float('nan'))
    williams_r =williams_r1.ewm(span=period, adjust=False).mean()
    
    return williams_r.rename(f'Williams_%R_{period}')    

def add_rolling_indicators(df, 
                           ma_col='close_ma', 
                           ma_col2='close_ma1',
                           ma_windows=[55, 34],  # 改为两个窗口大小
                           strictness=3,
                           fast_col='tsma5',
                           slow_col='tsma8',
                           cross_window=13):
    """
    在DataFrame中添加滚动指标列，支持双窗口均线趋势检测
    
    参数:
    df -- 原始DataFrame (按时间顺序排列，最近的最后)
    ma_col -- 均线列名 (默认'close_ma')
    ma_windows -- 均线趋势检测的双窗口大小列表 (默认[60, 30])
    strictness -- 峰值检测严格度 (默认3)
    fast_col -- 快速均线列名 (默认'tsma5')
    slow_col -- 慢速均线列名 (默认'tsma8')
    cross_window -- 金叉死叉检测窗口大小 (默认13)
    
    返回:
    添加了三列新特征的DataFrame:
      'ma_trend_change_win1' - 第一个窗口内是否出现均线趋势转折
      'ma_trend_change_win2' - 第二个窗口内是否出现均线趋势转折
      'cross_events' - 当前窗口内金叉后死叉的次数
    """
    # 确保有两个窗口大小
    if len(ma_windows) < 2:
        raise ValueError("ma_windows 必须包含至少两个窗口大小")
    
    # 添加两个均线趋势转折列
    df['ma_trend_change_win1'] = False
    df['ma_trend_change_win2'] = False
    
    # 获取最大窗口大小用于边界处理
    max_window = max(ma_windows)
    
    # 第一个窗口的滚动计算
    win1 = ma_windows[0]
    for i in range(win1, len(df)):
        window_data = df.iloc[i-win1:i+1]
        has_extreme, _ = detect_ma_trend_change(
            window_data[ma_col], 
            window=win1,
            strictness=strictness
        )
        df.loc[df.index[i], 'ma_trend_change_win1'] = has_extreme
    
    # 第二个窗口的滚动计算
    win2 = ma_windows[1]
    for i in range(win2, len(df)):
        window_data = df.iloc[i-win2:i+1]
        has_extreme, _ = detect_ma_trend_change(
            window_data[ma_col2], 
            window=win2,
            strictness=strictness
        )
        df.loc[df.index[i], 'ma_trend_change_win2'] = has_extreme
    
    # 添加金叉死叉事件列
    df['cross_events'] = 0
    for i in range(cross_window, len(df)):
        window_data = df.iloc[i-cross_window+1:i+1]
        event_count = detect_cross_events(
            window_data,
            fast_col=fast_col,
            slow_col=slow_col,
            window_size=cross_window
        )
        df.loc[df.index[i], 'cross_events'] = event_count
    
    return df
def detect_pivot_points(df, distance_threshold=7, height_threshold=0.007):
    """检测关键枢轴点（尖峰后的第一根异性K棒），合并相邻且高度相近的峰值"""
    close = df['close'].values
    open_ = df['open'].values
    high = df['high'].values
    low = df['low'].values
    
    # 1. 检测上涨尖峰（局部高点）
    up_peaks = argrelextrema(close, np.greater, order=3)[0]
    
    # 2. 检测下跌极点（局部低点）
    down_peaks = argrelextrema(close, np.less, order=3)[0]
    
    # 3. 合并相邻且高度相近的峰值
    merged_up_peaks = []
    merged_down_peaks = []
    
    # 合并上涨尖峰
    i = 0
    while i < len(up_peaks):
        current_peak = up_peaks[i]
        group = [current_peak]
        j = i + 1
        
        # 寻找相邻的峰值
        while j < len(up_peaks) and (up_peaks[j] - current_peak) <= distance_threshold:
            group.append(up_peaks[j])
            j += 1
        
        # 在组内找到最高点
        highest_idx = group[0]
        for idx in group:
            if high[idx] > high[highest_idx]:
                highest_idx = idx
        
        # 检查高度是否相近
        min_height = min(high[idx] for idx in group)
        max_height = max(high[idx] for idx in group)
        height_diff = (max_height - min_height) / min_height
        
        if height_diff <= height_threshold:
            merged_up_peaks.append(highest_idx)
        else:
            # 高度差异大，保留所有点
            merged_up_peaks.extend(group)
        
        i = j
    
    # 合并下跌极点
    i = 0
    while i < len(down_peaks):
        current_peak = down_peaks[i]
        group = [current_peak]
        j = i + 1
        
        # 寻找相邻的峰值
        while j < len(down_peaks) and (down_peaks[j] - current_peak) <= distance_threshold:
            group.append(down_peaks[j])
            j += 1
        
        # 在组内找到最低点
        lowest_idx = group[0]
        for idx in group:
            if low[idx] < low[lowest_idx]:
                lowest_idx = idx
        
        # 检查高度是否相近
        min_height = min(low[idx] for idx in group)
        max_height = max(low[idx] for idx in group)
        height_diff = (max_height - min_height) / min_height
        
        if height_diff <= height_threshold:
            merged_down_peaks.append(lowest_idx)
        else:
            # 高度差异大，保留所有点
            merged_down_peaks.extend(group)
        
        i = j
    
    # 4. 检测中枢棒（尖峰后第一根反向K棒）
    pivot_bars = []
    
    # 处理上涨尖峰
    for peak_idx in merged_up_peaks:
        # 寻找尖峰后第一根阴棒（收盘<开盘）
        for i in range(peak_idx + 1, min(peak_idx + 10, len(df))):
            if close[i] < open_[i]:  # 阴线
                pivot_bar = {
                    'index': i,
                    'type': 'bearish_pivot',
                    'peak_index': peak_idx,
                    'price': (high[i] + low[i]) / 2,
                    'high': high[i],
                    'low': low[i],
                    'date': df.index[i]
                }
                pivot_bars.append(pivot_bar)
                break
    
    # 处理下跌尖峰
    for trough_idx in merged_down_peaks:
        # 寻找尖峰后第一根阳棒（收盘>开盘）
        for i in range(trough_idx + 1, min(trough_idx + 10, len(df))):
            if close[i] > open_[i]:  # 阳线
                pivot_bar = {
                    'index': i,
                    'type': 'bullish_pivot',
                    'peak_index': trough_idx,
                    'price': (high[i] + low[i]) / 2,
                    'high': high[i],
                    'low': low[i],
                    'date': df.index[i]
                }
                pivot_bars.append(pivot_bar)
                break
    
    # 对枢轴点按索引排序
    pivot_bars.sort(key=lambda x: x['index'])
    
    return merged_up_peaks, merged_down_peaks, pivot_bars

def cluster_pivot_points(pivot_bars, max_distance=5):
    """聚类相邻的BP和AP，识别震荡区间作为中枢"""
    if len(pivot_bars) < 2:
        return [], pivot_bars
    
    # 按索引排序枢轴点
    pivot_bars = sorted(pivot_bars, key=lambda x: x['index'])
    
    # 提取索引用于聚类
    indices = np.array([p['index'] for p in pivot_bars]).reshape(-1,1)
    if len(pivot_bars) < 2:
        return [], pivot_bars
    
    # 按索引排序枢轴点
    pivot_bars = sorted(pivot_bars, key=lambda x: x['index'])
    
    # 提取索引用于聚类
    indices = np.array([p['index'] for p in pivot_bars]).reshape(-1, 1)
    
    # 使用层次聚类
    clusters = cluster.hierarchy.fclusterdata(
        indices, 
        t=max_distance, 
        criterion='distance', 
        metric='euclidean', 
        method='single'
    )
    
    # 组织聚类结果
    clustered_zones = []
    non_clustered = []
    
    for cluster_id in np.unique(clusters):
        cluster_points = [p for i, p in enumerate(pivot_bars) if clusters[i] == cluster_id]
        
        # 如果聚类中只有一个点，则视为非震荡中枢
        if len(cluster_points) == 1:
            non_clustered.append(cluster_points[0])
            continue
        
        # 创建震荡中枢
        start_idx = min(p['index'] for p in cluster_points)
        end_idx = max(p['index'] for p in cluster_points)
        high = max(p['high'] for p in cluster_points)
        low = min(p['low'] for p in cluster_points)
        center = (high + low) / 2
        
        # 确定震荡中枢类型
        bullish_count = sum(1 for p in cluster_points if p['type'] == 'bullish_pivot')
        bearish_count = sum(1 for p in cluster_points if p['type'] == 'bearish_pivot')
        pivot_type = 'bullish' if bullish_count > bearish_count else 'bearish'
        
        clustered_zones.append({
            'start_idx': start_idx,
            'end_idx': end_idx,
            'high': high,
            'low': low,
            'center': center,
            'points': cluster_points,
            'type': pivot_type + '_zone',  # 如 'bullish_zone'
            'index': (start_idx + end_idx) // 2,  # 中枢中心位置
            'price': center,
            'date': cluster_points[len(cluster_points)//2]['date']  # 取中间点的日期
        })
    
    return clustered_zones, non_clustered


def detect_subwaves_by_slope(df, start_idx, end_idx, min_wave_length=2, slope_threshold=0.005, wave_number_start=1):
    """
    改进子波检测：使用更灵敏的极值点检测方法，确保波数连续
    """
    # 检查波段长度
    if end_idx <= start_idx or end_idx - start_idx < min_wave_length * 2:
        direction = 'up' if df['close'].iloc[end_idx] > df['close'].iloc[start_idx] else 'down'
        return [{
            'start': start_idx,
            'end': end_idx,
            'direction': direction,
            'wave_number': wave_number_start
        }]
    
    # 提取波段数据
    segment = df.iloc[start_idx:end_idx+1]
    prices = segment['close'].values
    
    # 1. 确定整体方向
    overall_direction = 1 if prices[-1] > prices[0] else -1
    
    # 2. 寻找波段内的主要转折点（改进的极值点检测）
    peaks = []
    troughs = []
    
    # 使用更灵敏的极值点检测
    for i in range(1, len(prices)-1):
        # 检测局部高点：比前2根和后2根都高
        if i >= 2 and i < len(prices)-2:
            if prices[i] > max(prices[i-2], prices[i-1]) and prices[i] > max(prices[i+1], prices[i+2]):
                peaks.append(i)
        
        # 检测局部低点：比前2根和后2根都低
        if i >= 2 and i < len(prices)-2:
            if prices[i] < min(prices[i-2], prices[i-1]) and prices[i] < min(prices[i+1], prices[i+2]):
                troughs.append(i)
    
    # 3. 添加更严格的转折点筛选
    filtered_points = []
    
    # 确保转折点之间有足够的价格变化
    for point in sorted(peaks + troughs):
        if not filtered_points:
            filtered_points.append(point)
            continue
            
        last_point = filtered_points[-1]
        price_change = abs(prices[point] - prices[last_point]) / prices[last_point]
        
        # 只保留价格变化超过阈值的转折点
        if price_change > slope_threshold:
            filtered_points.append(point)
    
    # 4. 合并起点、终点和过滤后的极值点
    all_points = sorted([0] + filtered_points + [len(prices)-1])
    
    # 5. 创建子波（只保留与整体方向一致的波段）
    subwaves = []
    wave_number = wave_number_start
    
    for i in range(1, len(all_points)):
        start_i = all_points[i-1]
        end_i = all_points[i]
        
        # 确保波段有最小长度
        if end_i - start_i < min_wave_length:
            continue
            
        # 计算波段方向
        start_price = prices[start_i]
        end_price = prices[end_i]
        direction = 'up' if end_price > start_price else 'down'
        
        # 只保留与整体方向一致的波段
        if (overall_direction == 1 and direction == 'up') or (overall_direction == -1 and direction == 'down'):
            # 计算波段斜率
            slope = (end_price - start_price) / (end_i - start_i) if (end_i - start_i) > 0 else 0
            
            # 只保留斜率超过阈值的波段
            if abs(slope) > slope_threshold:
                subwaves.append({
                    'start': start_idx + start_i,
                    'end': start_idx + end_i,
                    'direction': direction,
                    'wave_number': wave_number,
                    'slope': slope
                })
                wave_number += 1
    
    # 6. 如果没有检测到子波，返回整个波段
    if not subwaves:
        direction = 'up' if prices[-1] > prices[0] else 'down'
        return [{
            'start': start_idx,
            'end': end_idx,
            'direction': direction,
            'wave_number': wave_number_start
        }]
    
    return subwaves
    
def create_zone(cluster_points):
    """从一组点创建震荡中枢"""
    # 提取关键信息
    indices = [p['index'] for p in cluster_points]
    prices = [p['price'] for p in cluster_points]
    highs = [p['high'] for p in cluster_points]
    lows = [p['low'] for p in cluster_points]
    
    # 计算区间边界
    start_idx = min(indices)
    end_idx = max(indices)
    high = max(highs)
    low = min(lows)
    center = (high + low) / 2
    
    # 计算价格重心（加权平均）
    weights = np.array([1.0] * len(prices))  # 等权重
    weighted_center = np.average(prices, weights=weights)
    
    # 计算价格变动范围百分比
    price_range_pct = (high - low) / low * 100
    
    # 确定震荡中枢类型
    bullish_count = sum(1 for p in cluster_points if p['type'] == 'bullish_pivot')
    bearish_count = sum(1 for p in cluster_points if p['type'] == 'bearish_pivot')
    pivot_type = 'bullish' if bullish_count > bearish_count else 'bearish'
    
    # 选择代表性日期（中间点）
    mid_index = sorted(indices)[len(indices)//2]
    rep_point = next(p for p in cluster_points if p['index'] == mid_index)
    
    return {
        'start_idx': start_idx,
        'end_idx': end_idx,
        'duration': end_idx - start_idx + 1,
        'high': high,
        'low': low,
        'price_range_pct': price_range_pct,
        'center': center,
        'weighted_center': weighted_center,
        'points': cluster_points,
        'type': pivot_type + '_zone',
        'index': (start_idx + end_idx) // 2,
        'price': weighted_center,
        'date': rep_point['date'],
        'bullish_count': bullish_count,
        'bearish_count': bearish_count
    }

def create_unified_pivots(clustered_zones, non_clustered):
    """创建统一的中枢列表（包括震荡中枢和非震荡中枢）并按时间排序"""
    # 转换非震荡中枢格式
    single_pivots = []
    for pivot in non_clustered:
        single_pivots.append({
            'type': pivot['type'] + '_pivot',
            'index': pivot['index'],
            'price': pivot['price'],
            'date': pivot['date'],
            'is_zone': False
        })
    
    # 转换震荡中枢格式
    zone_pivots = []
    for zone in clustered_zones:
        zone_pivots.append({
            'type': zone['type'],
            'index': zone['index'],
            'price': zone['price'],
            'date': zone['date'],
            'is_zone': True,
            'zone_data': zone  # 保留原始数据用于绘图
        })
    
    # 合并并排序
    all_pivots = single_pivots + zone_pivots
    all_pivots = sorted(all_pivots, key=lambda x: x['index'])
    
    return all_pivots
 
def calculate_wave_structure(pivots, df):
    """为中枢之间的运动分配波数（严格遵循波浪理论）"""
    if len(pivots) < 2:
        return pivots, []
    
    # 初始化波浪计数
    wave_count = 1
    wave_moves = []  # 存储波浪运动的详细信息
    trend_direction = None  # 当前趋势方向
    
    # 第一个中枢没有运动
    pivots[0]['wave'] = 0
    
    # 遍历中枢之间的运动
    for i in range(1, len(pivots)):
        prev_pivot = pivots[i-1]
        curr_pivot = pivots[i]
        
        # 确定运动方向
        if curr_pivot['price'] > prev_pivot['price']:
            move_direction = 'up'
        else:
            move_direction = 'down'
        
        # 确定运动类型
        if i == 1:
            # 第一个运动总是推动波
            move_type = 'impulse'
            wave_count = 1
            trend_direction = move_direction  # 设置趋势方向
        else:
            prev_move = wave_moves[-1]
            
            # 规则1: 连续两个调整波 -> 视为反转
            if prev_move['move_type'] == 'correction' and move_direction == prev_move['direction']:
                move_type = 'impulse'
                wave_count = 1
                trend_direction = move_direction  # 反转趋势
            
            # 规则2: 调整波->推动波->调整波 且价格突破
            elif (
                len(wave_moves) >= 2 and 
                wave_moves[-2]['move_type'] == 'correction' and 
                prev_move['move_type'] == 'impulse'
            ):
                first_correction = wave_moves[-2]  # 第一个调整波
                
                # 在上升趋势中：第二个调整波（下跌）必须创更低低点
                if trend_direction == 'up' and move_direction == 'down':
                    if curr_pivot['price'] < first_correction['end_pivot']['price']:
                        move_type = 'impulse'  # 视为反转
                        wave_count = 1
                        trend_direction = 'down'  # 更新为下跌趋势
                    else:
                        move_type = 'correction'
                
                # 在下跌趋势中：第二个调整波（上涨）必须创更高高点
                elif trend_direction == 'down' and move_direction == 'up':
                    if curr_pivot['price'] > first_correction['end_pivot']['price']:
                        move_type = 'impulse'  # 视为反转
                        wave_count = 1
                        trend_direction = 'up'  # 更新为上升趋势
                    else:
                        move_type = 'correction'
                else:
                    # 其他情况按正常规则处理
                    if move_direction == trend_direction:
                        move_type = 'impulse'
                        wave_count += 1
                    else:
                        move_type = 'correction'
            
            # 正常情况：同方向为推动波，反方向为调整波
            else:
                if move_direction == trend_direction:
                    move_type = 'impulse'
                    wave_count += 1
                else:
                    move_type = 'correction'
        
        # 检测子波
        subwaves = detect_subwaves_by_slope(df, prev_pivot['index'], curr_pivot['index'])
        
        # 记录波浪运动
        move_info = {
            'start_pivot': prev_pivot,
            'end_pivot': curr_pivot,
            'direction': move_direction,
            'wave_number': wave_count if move_type == 'impulse' else 0,
            'move_type': move_type,
            'subwaves': subwaves,
            'trend_direction': trend_direction
        }
        wave_moves.append(move_info)
        
        # 为当前中枢标记波数
        curr_pivot['wave'] = wave_count if move_type == 'impulse' else 0
    
    return pivots, wave_moves


def detect_trend_direction(wave_moves):
    """基于波浪运动识别市场主要趋势方向"""
    if len(wave_moves) == 0:
        return None
    return wave_moves[-1]['trend_direction']

def identify_measurement_moves(wave_moves, df):
    """识别波浪运动的测量目标"""
    measurements = []
    
    for move in wave_moves:
        # 只对推动波进行测量
        if move['move_type'] != 'impulse':
            continue
            
        start_pivot = move['start_pivot']
        end_pivot = move['end_pivot']
        wave_number = move['wave_number']
        direction = move['direction']
        
        # 计算运动距离
        distance = abs(end_pivot['price'] - start_pivot['price'])
        
        # 预测目标位
        if direction == 'up':
            target = end_pivot['price'] + distance
        else:
            target = end_pivot['price'] - distance
        
        # 找到实际突破点
        start_idx = end_pivot['index'] + 1
        if start_idx < len(df):
            # 对于上升趋势，寻找突破高点
            if direction == 'up':
                # 找到从突破点开始的新高
                high_prices = df['high'].iloc[start_idx:]
                if len(high_prices) > 0:
                    # 获取突破点的索引位置
                    breakout_idx = high_prices.idxmax()
                    # 确保是整数索引
                    if isinstance(breakout_idx, pd.Timestamp):
                        # 如果是时间戳，转换为整数位置
                        breakout_idx = df.index.get_loc(breakout_idx)
                    breakout_price = high_prices.max()
                else:
                    breakout_idx = start_idx
                    breakout_price = df['high'].iloc[start_idx]
            # 对于下降趋势，寻找突破低点
            else:
                low_prices = df['low'].iloc[start_idx:]
                if len(low_prices) > 0:
                    breakout_idx = low_prices.idxmin()
                    # 确保是整数索引
                    if isinstance(breakout_idx, pd.Timestamp):
                        # 如果是时间戳，转换为整数位置
                        breakout_idx = df.index.get_loc(breakout_idx)
                    breakout_price = low_prices.min()
                else:
                    breakout_idx = start_idx
                    breakout_price = df['low'].iloc[start_idx]
        else:
            breakout_idx = len(df) - 1
            breakout_price = df['close'].iloc[-1]
        
        measurements.append({
            'start_pivot': start_pivot,
            'end_pivot': end_pivot,
            'distance': distance,
            'direction': direction,
            'target_price': target,
            'breakout_index': breakout_idx,
            'breakout_price': breakout_price,
            'wave_number': wave_number
        })
    
    return measurements

def detect_high_low_points(df, window=5):
    """
    可靠检测高点和低点极点，并在原始DataFrame中标记相关信息
    
    :param df: 包含价格数据的DataFrame（必须有'high'和'low'列）
    :param window: 检测窗口大小（数据点）
    :return: 增强后的DataFrame，包含新列：
        - 'is_high': 是否是高点
        - 'is_low': 是否是低点
        - 'is_extreme_high': 是否是极高点（比相邻高点都高）
        - 'is_extreme_low': 是否是极低点（比相邻低点都低）
        - 'prev_high_index': 前一个高点的索引位置
        - 'prev_low_index': 前一个低点的索引位置
        - 'prev_high_price': 前一个高点的价格
        - 'prev_low_price': 前一个低点的价格
    """
    try:

        # 确保必要的列存在
        if 'high' not in df.columns or 'low' not in df.columns:
            raise ValueError("DataFrame必须包含'high'和'low'列")
        
        # 获取价格序列
        high_prices = df['high'].values
        low_prices = df['low'].values
        
        # 检测高点（局部最大值）
        high_indices = argrelextrema(high_prices, np.greater, order=window)[0]
        # 检测低点（局部最小值）
        low_indices = argrelextrema(low_prices, np.less, order=window)[0]
        
        # 创建标记列
        df = df.copy()
        df['is_high'] = False
        df['is_low'] = False
        df['is_extreme_high'] = False
        df['is_extreme_low'] = False
        
        # 标记高点和低点
        df.loc[df.index[high_indices], 'is_high'] = True
        df.loc[df.index[low_indices], 'is_low'] = True
        
        # 检测极高点
        if len(high_indices) >= 3:
            for i in range(1, len(high_indices) - 1):
                prev_idx = high_indices[i-1]
                current_idx = high_indices[i]
                next_idx = high_indices[i+1]
                
                current_high = high_prices[current_idx]
                prev_high = high_prices[prev_idx]
                next_high = high_prices[next_idx]
                
                if current_high > prev_high and current_high > next_high:
                    df.loc[df.index[current_idx], 'is_extreme_high'] = True
        
        # 检测极低点
        if len(low_indices) >= 3:
            for i in range(1, len(low_indices) - 1):
                prev_idx = low_indices[i-1]
                current_idx = low_indices[i]
                next_idx = low_indices[i+1]
                
                current_low = low_prices[current_idx]
                prev_low = low_prices[prev_idx]
                next_low = low_prices[next_idx]
                
                if current_low < prev_low and current_low < next_low:
                    df.loc[df.index[current_idx], 'is_extreme_low'] = True
        
        # 创建前一个高点和低点的信息列
        df['prev_high_index'] = None
        df['prev_high_price'] = np.nan
        df['prev_low_index'] = None
        df['prev_low_price'] = np.nan
        
        # 初始化前一个高点和低点信息
        prev_high_index = None
        prev_high_price = None
        prev_low_index = None
        prev_low_price = None
        
        # 遍历DataFrame，记录前一个高点和低点信息
        for i, (index, row) in enumerate(df.iterrows()):
            # 记录前一个高点和低点信息
            if prev_high_index is not None:
                df.at[index, 'prev_high_index'] = prev_high_index
                df.at[index, 'prev_high_price'] = prev_high_price
            
            if prev_low_index is not None:
                df.at[index, 'prev_low_index'] = prev_low_index
                df.at[index, 'prev_low_price'] = prev_low_price
            
            # 如果当前点是高点，更新前一个高点信息
            if row['is_high']:
                prev_high_index = index
                prev_high_price = row['high']
            
            # 如果当前点是低点，更新前一个低点信息
            if row['is_low']:
                prev_low_index = index
                prev_low_price = row['low']
        
        return df
    except Exception as e:
        print(f"❌ 文件加载失败: {input_path}")
        print(f"错误详情: {e}")
        return None

def create_new_column(df):
    try:
        # 初始化新列为0
        df = df.copy()  # 创建副本避免修改原始DataFrame
        df['action'] = 0
        
        # 重置索引并保留原始索引
        df = df.reset_index()
        n = len(df)
        
        # 创建影响范围的布尔掩码
        a_mask = np.zeros(n, dtype=bool)
        b_mask = np.zeros(n, dtype=bool)
        
        # 处理高点的影响范围（当前行及上下行）
        for i in range(n):
            if df.loc[i, 'is_high']:  # 直接检查布尔值
                start = max(0, i-1)
                end = min(n, i+2)
                a_mask[start:end] = True
        
        # 处理低点的影响范围（当前行及上下行）
        for i in range(n):
            if df.loc[i, 'is_low']:  # 直接检查布尔值
                start = max(0, i-1)
                end = min(n, i+2)
                b_mask[start:end] = True
        
        # 应用规则（低点优先级高于高点）
        df.loc[a_mask & ~b_mask, 'action'] = 1  # 仅受高点影响
        df.loc[b_mask, 'action'] = 2            # 受低点影响（覆盖高点）
        
        # 恢复原始索引
        if 'index' in df.columns:
            df = df.set_index('index')
            df.index.name = None  # 移除索引名称
        
        return df
    except Exception as e:
        print(f"❌ 创建新列失败: {e}")
        return None



def process_single_stock(ts_code: str = "000001.SZ") -> bool:
    """处理单个 CSV 文件并生成分析结果
    
    Args:
        ts_code (str): 股票 TS 代码（默认: 000001.SZ），自动拼接 ".csv" 后缀
        
    Returns:
        bool: 处理是否成功
    """
    # 固定路径参数（直接修改函数体即可调整）
    output_dir = os.path.join(SCRIPT_DIR, "../data/analyzed/5min")# 输出目录)
    data_dir = os.path.join(SCRIPT_DIR, "../data/raw/5min")    # 数据目录
    
    csv_filename = f"{ts_code}.csv"
    input_path = Path(data_dir) / csv_filename
    output_path = Path(output_dir) / f"{ts_code}_analysis.csv"
    
    required_columns = {
        'ts_code', 'datetime', 'open', 'high', 
        'low', 'close', 'volume', 'amount','name','industry','circ_mv'
    }
    
    try:
        # 解析 trade_date 列并按时间降序排序（最新日期在前）
        df_raw = pd.read_csv(
            input_path,
            parse_dates=['datetime'],

            usecols=lambda x: x in required_columns
        )
        df_raw['datetime'] = pd.to_datetime(df_raw['datetime'], errors='coerce')
        #df_raw = df_raw.sort_values(by='trade_date', ascending=True)  # 反向排序
        
        #print(f"✅ 实际读取的列名: {df_raw.columns.tolist()}")
        
        # 设置 ts_code 为索引并保留原列
        #df = df_raw.set_index('datetime', drop=False)
        df = df_raw.rename(columns={'datetime': 'trade_date', 'vol': 'volume'})        
        df.set_index('trade_date', drop=True)
        # 计算技术指标
        close_prices = df['close'].values
        fast_ema = df['close'].ewm(span=5, adjust=False).mean()
        slow_ema = df['close'].ewm(span=13, adjust=False).mean()
        df['diff'] = fast_ema - slow_ema
        df['dea'] = df['diff'].ewm(span=8, adjust=False).mean()
        df['macd'] = 2 * (df['diff'] - df['dea'])

        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma8'] = df['close'].rolling(window=8).mean()
        df['ma13'] = df['close'].rolling(window=13).mean()
        df['ma21'] = df['close'].rolling(window=21).mean()
        df['ma34'] = df['close'].rolling(window=34).mean()
        df['ma55'] = df['close'].rolling(window=55).mean()
        df['LC'] = df['close'].shift(1)
        df['CLOSE_LC'] = df['close'] - df['LC']
        # 计算VR指标
        av = df['volume'].where(df['close'] > df['LC'], 0)
        bv = df['volume'].where(df['close'] < df['LC'], 0)
        cv = df['volume'].where(df['close'] == df['LC'], 0)
        df['vr'] = (av.rolling(26).sum() + cv.rolling(26).sum()/2) / \
              (bv.rolling(26).sum() + cv.rolling(26).sum()/2 + 1e-7) * 100

    
        #计算tsma
        df['tsma5'] = tsma_fast(df['close'], 5)
        df['tsma8'] = tsma_fast(df['close'], 8)
        df['tsma13'] = tsma_fast(df['close'], 13)
        # 计算ER（效率比率）
        change = df['close'].diff(14).abs()
        volatility = df['close'].diff().abs().rolling(14).sum()
        df['er'] = change / (volatility + 1e-7)
        variances = []
        closes = df['close'].values
        for period in CONFIG["PERIODS"]:
            period_data = closes[-period:]
            variances.append(np.var(period_data, ddof=1)/(closes*closes))  # 样本方差  
        df['var'] = np.mean(variances)  
        
        
        # 计算布林带
        df['sma'] = df['close'].rolling(20).mean()  # 中轨
        df['std'] = df['close'].rolling(20).std()    # 标准差
        df['upper'] = df['sma'] + (df['std'] * 2)              # 上轨
        df['lower'] = df['sma'] - (df['std'] * 2) 
        # 计算连续上涨条件
        df['A1'] = df['close'] > df['close'].shift(4)
        df['NT'] = df['A1'].astype(int).groupby((~df['A1']).cumsum()).cumcount()

        # 计算连续下跌条件
        df['B1'] = df['close'] < df['close'].shift(4)
        df['NT0'] = df['B1'].astype(int).groupby((~df['B1']).cumsum()).cumcount()

        # 初始化标记列
        df['up_mark'] = 0
        df['down_mark'] = 0

        # 获取列索引位置（只需执行一次）
        up_col_idx = df.columns.get_loc('up_mark')
        down_col_idx = df.columns.get_loc('down_mark')

        # 处理上涨标记（使用整数位置）
        # 找到所有九转结构成立的结束位置（整数位置）
        nine_up_indices = np.where(df['NT'] == 9)[0]

        # 标记完整的九转结构
        for pos in nine_up_indices:
            start_pos = max(0, pos - 8)
            # 使用 iloc 位置赋值
            df.iloc[start_pos:pos+1, up_col_idx] = np.arange(1, 10)

        # 处理最后一个K线的未完成结构
        if len(df) > 0 and 5 <= df['NT'].iloc[-1] <= 8:
            nt = df['NT'].iloc[-1]
            start_pos = max(0, len(df) - nt)
            df.iloc[start_pos:, up_col_idx] = np.arange(1, nt + 1)

        # 处理下跌标记（使用整数位置）
        # 找到所有九转结构成立的结束位置（整数位置）
        nine_down_indices = np.where(df['NT0'] == 9)[0]

        # 标记完整的九转结构
        for pos in nine_down_indices:
            start_pos = max(0, pos - 8)
            df.iloc[start_pos:pos+1, down_col_idx] = np.arange(1, 10)

        # 处理最后一个K线的未完成结构
        if len(df) > 0 and 5 <= df['NT0'].iloc[-1] <= 8:
            nt = df['NT0'].iloc[-1]
            start_pos = max(0, len(df) - nt)
            df.iloc[start_pos:, down_col_idx] = np.arange(1, nt + 1)
        df['shadow_ratio'] = (df['high'] - df['close']) / df['open']- df['close']

        df['wr5'] = calculate_williams_r(df, period=5)
        df['wr55'] = calculate_williams_r(df, period=55)
        
        df = add_rolling_indicators(
            df,
            ma_col='ma55',
            ma_col2='ma34',
            ma_windows=[50, 30],  # 双窗口大小
            strictness=3,
            fast_col='tsma5',
            slow_col='tsma8',
            cross_window=13
        )
        df = detect_single_divergence(df, indicator_col='macd')
        df = detect_single_divergence(df, indicator_col='vr')
        df = detect_single_divergence(df, indicator_col='wr5')
        df = add_price_range_indicators(
            df,
            price_col='close',
            window_size=20,
            cluster_threshold=1.0,
            min_range_length=10
        )
        
        # 修改1: 重构wave函数返回单个字典（包含所有需要的信息）
        def wave(df_window):
            up_peaks, down_peaks, pivot_bars = detect_pivot_points(df_window)
            clustered_zones, non_clustered = cluster_pivot_points(pivot_bars)
            all_pivots = create_unified_pivots(clustered_zones, non_clustered)
            all_pivots, wave_moves = calculate_wave_structure(all_pivots, df_window)
            mea = identify_measurement_moves(wave_moves, df_window)
            
            # 获取最后一个波动和测量值（如果存在）
            last_wave = wave_moves[-1] if wave_moves else None
            last_mea = mea[-1] if mea else None
            
            # 构造返回结果（包含所有字段）
            result = {
                'start_type': last_wave['start_pivot']['type'] if last_wave else None,
                'end_type': last_wave['end_pivot']['type'] if last_wave else None,
                'wave_number': last_wave['wave_number'] if last_wave else None,
                'move_type': last_wave['move_type'] if last_wave else None,
                'subwaves': last_wave['subwaves'][0]['wave_number'] if last_wave and last_wave['subwaves'] else None,
                'target': last_mea['target_price'] if last_mea else None
            }
            return result

        # 修改2: 直接计算并赋值到DataFrame（不再使用rolling.apply）
        results = []
        for i in range(49, len(df)):  # 从第50个数据点开始
            window = df.iloc[i-49:i+1]  # 获取50个数据的窗口
            res = wave(window)
            results.append(res)

        # 将结果转换为DataFrame并合并到原始数据
        result_df = pd.DataFrame(results, index=df.index[49:])
        df = df.join(result_df.add_prefix('wave_'))  # 添加前缀避免列名冲突

        # 修改4: 清理列名（移除尾随空格）
        df = df.rename(columns={
            'wave_start_type': 'start_type',
            'wave_end_type': 'end_type',
            'wave_wave_number': 'wave_number',  # 注意原始列名有空格
            'wave_move_type': 'move_type',      # 注意原始列名有空格
            'wave_subwaves': 'subwaves',        # 注意原始列名有空格
            'wave_target': 'target'             # 注意原始列名有空格
        })
        df.set_index('trade_date', inplace=True)  # 设置日期为索引
        df = detect_high_low_points(df, window=5)
        replacement_rules = {
            "ma_trend_change_win1": {True: 1, False: 0},
            "ma_trend_change_win2": {True: 1, False: 0},
            "divergence_status_macd": {"normal": 0, "tbd": 1, "confirmed": 2},
            "divergence_status_vr": {"normal": 0, "tbd": 1, "confirmed": 2},
            "divergence_status_wr5": {"normal": 0, "tbd": 1, "confirmed": 2},
            "divergence_status": {"normal": 0, "tbd": 1, "confirmed": 2},  # 修正了列名拼写错误
            "is_range": {True: 1, False: 0},
            "trend_direction": {"上升趋势": 0, "震荡趋势": 1, "下降趋势": 2},
            "start_type": {"bullish_pivot_pivot": 0, "bearish_pivot_pivot": 1, "bearish_zone": 2, "bullish_zone": 3},
            "end_type": {"bullish_pivot_pivot": 0, "bearish_pivot_pivot": 1, "bearish_zone": 2, "bullish_zone": 3},
            "move_type": {"impulse": 0, "correction": 1},
            "is_high":{True:1, False:0},
            "is_low":{True:1, False:0},
            "is_extreme_high":{True:1, False:0},
            "is_extreme_low":{True:1, False:0},
            
        }
        for column, rules in replacement_rules.items():
            if column in df.columns:
                df[column] = df[column].replace(rules)
            # 注释掉警告，避免大量输出
            else:
                print(f"警告：文件 {filename} 中列 {column} 不存在")
        # 3. 增加action
        
        df = create_new_column(df)
        
        # 4. 删除指定列（如果存在）
        cols_to_drop = ['name', 'industry',  'LC','CLOSE_LC', 'A1', 'B1', 'NT', 'NT0', 'range_start', 'range_end', 'prev_high_index', 'prev_high_price', 'prev_low_index', 'prev_low_price', 'is_high', 'is_low', 'is_extreme_high', 'is_extreme_low']
        df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

        df.to_csv(output_path, index=False)
        print(f"✅ 分析结果已保存: {output_path}")
        return True
    
    except Exception as e:
        print(f"❌ 文件加载失败: {input_path}")
        print(f"错误详情: {e}")
        return None
def main():
    """单文件处理入口"""
    parser = argparse.ArgumentParser(description="处理单个股票数据文件")
    parser.add_argument(
        "-t", "--ts_code", 
        default="000063.SZ",  # 添加默认值
        type=str, 
        help="要处理的 TS 代码（默认: 000001.SZ）"
    )
    args = parser.parse_args()
    
    success = process_single_stock(args.ts_code)
    print(f"\n最终结果: {'✅ 成功' if success else '⚠️ 失败'}")

if __name__ == "__main__":
    main()