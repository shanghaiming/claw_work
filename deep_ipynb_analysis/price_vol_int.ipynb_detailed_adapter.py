#!/usr/bin/env python3
"""
价量分析策略详细适配器
基于 price_vol_int.ipynb 深度解析生成的策略适配器

分析时间: 2026-03-29 19:42:00
策略类型: 价量分析策略
参数数量: 22
信号条件: 0个买入条件, 0个卖出条件
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class Price_vol_intStrategy:
    """价量分析策略"""
    
    def __init__(self, params: Optional[Dict] = None):
        """初始化策略"""
        self.params = params or {}
        
        # 默认参数（从原始notebook提取）
        self.default_params = {
    "nrows": 100,
    "axis": "x",
    "linewidth": 1,
    "alpha": 0.8,
    "s": 50,
    "y": 0,
    "bins": 20,
    "startangle": 90,
    "rotation": 45,
    "x": 0,
    "ts_code": "603979.SH",
    "index_col": "trade_date",
    "default": "中性",
    "label": "势能动能",
    "color": "black",
    "labelcolor": "brown",
    "loc": "upper right",
    "linestyle": "-",
    "edgecolor": "black",
    "autopct": "%1.1f%%",
    "ha": "center",
    "va": "center"
}
        
        # 合并参数
        for key, value in self.default_params.items():
            if key not in self.params:
                self.params[key] = value
        
        print(f"🔧 初始化 价量分析策略")
        print(f"   参数数量: {len(self.params)}")
        
    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        生成交易信号
        
        基于原始策略逻辑:
        {
    "buy_conditions": [],
    "sell_conditions": [],
    "entry_rules": [
        "axes[1,1].text(0.5, 0.5, '无有效数据', ha='center', va='center',"
    ],
    "exit_rules": [],
    "signal_frequency": 0.19646799116997793
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
                        'source_strategy': 'price_vol_int'
                    })
                # 死叉卖出
                elif prev_short >= prev_long and curr_short < curr_long:
                    signals.append({
                        'timestamp': timestamp,
                        'action': 'sell', 
                        'price': price,
                        'reason': 'ma_death_cross',
                        'confidence': 0.6,
                        'source_strategy': 'price_vol_int'
                    })
        
        print(f"📊 {self.strategy_info['strategy_type']} 生成 {len(signals)} 个信号")
        return signals
    
    def get_strategy_info(self) -> Dict:
        """获取策略信息"""
        return {
            'name': 'price_vol_int',
            'type': '价量分析策略',
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
        strategy = Price_vol_intStrategy()
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
