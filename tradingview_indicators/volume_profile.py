"""
Volume Profile - 成交量分布图，显示不同价格水平的成交量

来源: TradingView社区
转换时间: 2026-03-29 22:32:49
"""

import numpy as np
import pandas as pd

def volume_profile(high, low, close, volume, price_bins=20):
    """
    成交量分布 (Volume Profile)
    计算每个价格水平的成交量分布
    
    参数:
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
        volume: 成交量序列
        price_bins: 价格区间数量 (默认20)
    
    返回:
        price_levels: 价格水平
        volume_distribution: 成交量分布
        poc_price: 成交量最大处的价格 (Point of Control)
        value_area: 价值区间 (70%成交量集中的价格区间)
    """
    # 确定价格范围
    price_min = np.min(low)
    price_max = np.max(high)
    
    # 创建价格区间
    price_edges = np.linspace(price_min, price_max, price_bins + 1)
    price_centers = (price_edges[:-1] + price_edges[1:]) / 2
    
    # 初始化成交量分布
    volume_dist = np.zeros(price_bins)
    
    # 分配成交量到价格区间
    for i in range(len(close)):
        # 确定价格区间
        price = close[i]
        vol = volume[i]
        
        # 找到对应的价格区间
        bin_idx = np.digitize(price, price_edges) - 1
        bin_idx = max(0, min(bin_idx, price_bins - 1))
        
        volume_dist[bin_idx] += vol
    
    # 计算POC（成交量最大处）
    poc_idx = np.argmax(volume_dist)
    poc_price = price_centers[poc_idx]
    
    # 计算价值区间（70%成交量）
    total_volume = np.sum(volume_dist)
    target_volume = total_volume * 0.7
    
    # 从POC向两边扩展
    sorted_indices = np.argsort(volume_dist)[::-1]
    cumulative_volume = 0
    value_area_indices = []
    
    for idx in sorted_indices:
        cumulative_volume += volume_dist[idx]
        value_area_indices.append(idx)
        
        if cumulative_volume >= target_volume:
            break
    
    # 获取价值区间的价格范围
    value_area_prices = price_centers[value_area_indices]
    value_area = (np.min(value_area_prices), np.max(value_area_prices))
    
    return price_centers, volume_dist, poc_price, value_area

if __name__ == "__main__":
    # 测试代码
    # 测试数据
    np.random.seed(42)
    n = 1000
    close = np.random.uniform(90, 110, n)
    high = close + np.random.uniform(0, 2, n)
    low = close - np.random.uniform(0, 2, n)
    volume = np.random.lognormal(10, 1, n)
    
    # 运行示例
    try:
        # 使用示例
        price_levels, volume_dist, poc, value_area = volume_profile(high, low, close, volume, price_bins=20)
        print(f"Volume Profile 测试完成")
    except Exception as e:
        print(f"测试出错: {e}")