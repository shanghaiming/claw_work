#!/usr/bin/env python3
"""
聚类分析策略详细适配器
基于 cluster.ipynb 深度解析生成的策略适配器

分析时间: 2026-03-29 19:42:00
策略类型: 聚类分析策略
参数数量: 29
信号条件: 0个买入条件, 0个卖出条件
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class ClusterStrategy:
    """聚类分析策略"""
    
    def __init__(self, params: Optional[Dict] = None):
        """初始化策略"""
        self.params = params or {}
        
        # 默认参数（从原始notebook提取）
        self.default_params = {
    "window": 5,
    "cluster_threshold": 1.9,
    "min_range_length": 5,
    "order": 5,
    "width": 0.6,
    "width2": 0.05,
    "fontsize": 12,
    "alpha": 0.7,
    "linewidth": 2,
    "nbins": 10,
    "rotation": 45,
    "bar_count": 100,
    "color": "r",
    "fontweight": "bold",
    "linestyle": "--",
    "facecolor": "white",
    "loc": "upper left",
    "prune": "both",
    "ha": "right",
    "description": "Get stock data by code.",
    "default": "300505.SZ",
    "help": "Stock code (default: 300032.SZ)",
    "end_date": "20240112",
    "fre_step": "1d",
    "fq": "pre",
    "pos": false,
    "integer": true,
    "skip_paused": true,
    "threshold": 1.9
}
        
        # 合并参数
        for key, value in self.default_params.items():
            if key not in self.params:
                self.params[key] = value
        
        print(f"🔧 初始化 聚类分析策略")
        print(f"   参数数量: {len(self.params)}")
        
    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        生成交易信号
        
        基于原始策略逻辑:
        {
    "buy_conditions": [],
    "sell_conditions": [],
    "entry_rules": [
        "resistance_centers = cluster.vq.kmeans(resistance.reshape(-1,1), 2)[0]",
        "support_centers = cluster.vq.kmeans(support.reshape(-1,1), 2)[0]",
        "resistance_range = np.abs(resistance_centers[0] - resistance_centers[1])",
        "support_range = np.abs(support_centers[0] - support_centers[1])",
        "support_level = float(min(support_centers))  # 转换为float",
        "resistance_level = float(max(resistance_centers))  # 转换为float",
        "print(\"股价模式分析报告\".center(50))"
    ],
    "exit_rules": [],
    "signal_frequency": 0.10989010989010989
}
        """
        signals = []
        
        # TODO: 实现具体的信号生成逻辑
        # 基于 self.strategy_info['signal_logic'] 中的条件
        
        # 示例实现（需要根据实际策略修改）
        if len(data) > 20:
            # 简单移动平均交叉策略示例
            data = data.copy()
            short_window = self.params.get('window', 5)
            long_window = self.params.get('window', 20) * 2  # 假设长周期是短周期的2倍
            
            data['ma_short'] = data['close'].rolling(window=short_window).mean()
            data['ma_long'] = data['close'].rolling(window=long_window).mean()
            
            for i in range(1, len(data)):
                if pd.isna(data['ma_short'].iloc[i]) or pd.isna(data['ma_long'].iloc[i]):
                    continue
                
                timestamp = data.index[i]
                price = data['close'].iloc[i]
                
                # 金叉买入
                prev_short = data['ma_short'].iloc[i-1]
                prev_long = data['ma_long'].iloc[i-1]
                curr_short = data['ma_short'].iloc[i]
                curr_long = data['ma_long'].iloc[i]
                
                if prev_short <= prev_long and curr_short > curr_long:
                    signals.append({
                        'timestamp': timestamp,
                        'action': 'buy',
                        'price': price,
                        'reason': 'ma_golden_cross',
                        'confidence': 0.6,
                        'source_strategy': 'cluster'
                    })
                # 死叉卖出
                elif prev_short >= prev_long and curr_short < curr_long:
                    signals.append({
                        'timestamp': timestamp,
                        'action': 'sell', 
                        'price': price,
                        'reason': 'ma_death_cross',
                        'confidence': 0.6,
                        'source_strategy': 'cluster'
                    })
        
        print(f"📊 {self.strategy_info['strategy_type']} 生成 {len(signals)} 个信号")
        return signals
    
    def get_strategy_info(self) -> Dict:
        """获取策略信息"""
        return {
            'name': 'cluster',
            'type': '聚类分析策略',
            'parameters': self.params,
            'signal_logic_summary': self.strategy_info['signal_logic'],
            'imports_required': self.strategy_info['imports']
        }

# 测试函数
def test_strategy():
    """测试策略"""
    import os
    
    # 加载测试数据
    data_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/data"
    test_file = os.path.join(data_dir, "daily_data2", "000001.SZ.csv")
    
    if os.path.exists(test_file):
        df = pd.read_csv(test_file)
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.sort_values('trade_date', inplace=True)
        df.set_index('trade_date', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'vol']].iloc[:100]
        
        # 创建策略
        strategy = ClusterStrategy()
        signals = strategy.generate_signals(df)
        
        print(f"\n🧪 策略测试结果:")
        print(f"   数据行数: {len(df)}")
        print(f"   生成信号: {len(signals)}")
        
        if signals:
            buy_signals = [s for s in signals if s['action'] == 'buy']
            sell_signals = [s for s in signals if s['action'] == 'sell']
            print(f"   买入信号: {len(buy_signals)}")
            print(f"   卖出信号: {len(sell_signals)}")
    else:
        print("❌ 测试数据不存在")

if __name__ == "__main__":
    test_strategy()
