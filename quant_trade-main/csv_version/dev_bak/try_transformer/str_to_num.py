import pandas as pd
import os
from scipy.signal import argrelextrema
# 定义替换规则（保持不变）
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

# 设置目录路径
input_dir = r"E:\stock\csv_version\analysis_results"
output_dir = r"E:\stock\csv_version\out_analysis_results"

# 确保输出目录存在
os.makedirs(output_dir, exist_ok=True)

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
    df['prev_high_index'] = np.nan
    df['prev_high_price'] = np.nan
    df['prev_low_index'] = np.nan
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

import pandas as pd
import numpy as np

def create_new_column(df):
    # 初始化新列为0
    df['action'] = 0
    
    # 创建影响范围的布尔掩码
    n = len(df)
    a_mask = np.zeros(n, dtype=bool)
    b_mask = np.zeros(n, dtype=bool)
    
    # 处理a列=1的影响范围（当前行及上下行）
    for i in range(n):
        if df.loc[i, 'is_high'] == 1:
            a_mask[max(0, i-1):min(n, i+2)] = True
    
    # 处理b列=1的影响范围（当前行及上下行）
    for i in range(n):
        if df.loc[i, 'is_low'] == 1:
            b_mask[max(0, i-1):min(n, i+2)] = True
    
    # 应用规则（b列优先级高于a列）
    df.loc[a_mask & ~b_mask, 'action'] = 1  # 仅受a影响
    df.loc[b_mask, 'action'] = 2          # 受b影响（覆盖a）
    
    return df


# 遍历输入目录中的所有CSV文件
for filename in os.listdir(input_dir):
    if filename.endswith("_analysis.csv"):
        tscode = filename.split('_')[0]  # 从文件名提取股票代码
        
        # 1. 读取CSV文件
        file_path = os.path.join(input_dir, filename)
        df = pd.read_csv(file_path)
        df = df.reset_index(drop=True)
        df = detect_high_low_points(df, window=5)
        # 2. 应用替换规则
        for column, rules in replacement_rules.items():
            if column in df.columns:
                df[column] = df[column].replace(rules)
            # 注释掉警告，避免大量输出
            # else:
            #     print(f"警告：文件 {filename} 中列 {column} 不存在")
        # 3. 增加action
        df = create_new_column(df)
        # 4. 删除指定列（如果存在）
        cols_to_drop = ['range_start', 'range_end', 'prev_high_index', 'prev_high_price', 'prev_low_index', 'prev_low_price', 'future_5d_return', 'is_high', 'is_low', 'is_extreme_high', 'is_extreme_low']
        df = df.drop(columns=[col for col in cols_to_drop if col in df.columns], errors='ignore')
        
        # 5. 保存结果
        out_path = os.path.join(output_dir, f"{tscode}_analysis.csv")
        df.to_csv(out_path, index=False)
        print(f"处理完成: {filename} -> 保存至 {out_path}")

print("所有文件处理完成！")