#!/usr/bin/env python3
"""
动量策略详细适配器
基于 stategy_momentum.ipynb 深度解析生成的策略适配器

分析时间: 2026-03-29 19:42:00
策略类型: 动量策略
参数数量: 63
信号条件: 0个买入条件, 0个卖出条件
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class Stategy_momentumStrategy:
    """动量策略"""
    
    def __init__(self, params: Optional[Dict] = None):
        """初始化策略"""
        self.params = params or {}
        
        # 默认参数（从原始notebook提取）
        self.default_params = {
    "period": 55,
    "window": 20,
    "shadow_ratio": 0.7,
    "min_zone_separation": 0.02,
    "max_zone_width_ratio": 0.1,
    "entity_size_threshold": 0.05,
    "n_clusters": 3,
    "random_state": 0,
    "total_energy": 0,
    "axis": "y",
    "max_workers": 8,
    "days": 400,
    "valid_stock_count": 0,
    "current_index": 0,
    "fontsize": 12,
    "span": 9,
    "ddof": 1,
    "hspace": 0.1,
    "candle_width": 0.8,
    "zorder": 4,
    "alpha": 0.4,
    "width": 0.8,
    "linewidth": 0.7,
    "s": 200,
    "pad": 0.3,
    "rotation": 45,
    "high_col": "high",
    "low_col": "low",
    "close_col": "close",
    "symbol": "未知标的",
    "default": "中性",
    "index_col": "ts_code",
    "by": "count",
    "encoding": "utf_8_sig",
    "channel": "wxpusher",
    "subject": "SuperMind消息提醒",
    "uids": "UID_whd6sWkQtfsrIEFEifgZZWyLufEI",
    "description": "下一只",
    "color": "gray",
    "label": "WR55",
    "linestyle": "--",
    "marker": "*",
    "verticalalignment": "top",
    "boxstyle": "round,pad=0.3",
    "facecolor": "lightblue",
    "fontweight": "bold",
    "loc": "upper left",
    "labelcolor": "purple",
    "adjust": false,
    "overlap_found": true,
    "overlaps": true,
    "parse_dates": true,
    "ascending": false,
    "index": false,
    "email_list": false,
    "topic_ids": false,
    "group_id": false,
    "url": false,
    "payload": false,
    "wait": true,
    "has_regression": false,
    "visible": false,
    "threshold": 0.05
}
        
        # 合并参数
        for key, value in self.default_params.items():
            if key not in self.params:
                self.params[key] = value
        
        print(f"🔧 初始化 动量策略")
        print(f"   参数数量: {len(self.params)}")
        
    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        生成交易信号
        
        基于原始策略逻辑:
        {
    "buy_conditions": [],
    "sell_conditions": [],
    "entry_rules": [
        "class KLineCenterAnalyzer:",
        "centers = sorted([center[0] for center in kmeans.cluster_centers_])",
        "return centers",
        "def find_centers(self, df):",
        "center_lines = self.cluster_prices(all_points, 3)",
        "return center_lines, reversal_points, volume_points",
        "def calculate_center_zones(self, df, center_lines):",
        "center_zones = []",
        "for center_line in center_lines:",
        "if lows[i] <= center_line <= highs[i]:"
    ],
    "exit_rules": [],
    "signal_frequency": 0.1349124613800206
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
                        'source_strategy': 'stategy_momentum'
                    })
                # 死叉卖出
                elif prev_short >= prev_long and curr_short < curr_long:
                    signals.append({
                        'timestamp': timestamp,
                        'action': 'sell', 
                        'price': price,
                        'reason': 'ma_death_cross',
                        'confidence': 0.6,
                        'source_strategy': 'stategy_momentum'
                    })
        
        print(f"📊 {self.strategy_info['strategy_type']} 生成 {len(signals)} 个信号")
        return signals
    
    def get_strategy_info(self) -> Dict:
        """获取策略信息"""
        return {
            'name': 'stategy_momentum',
            'type': '动量策略',
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
        strategy = Stategy_momentumStrategy()
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
