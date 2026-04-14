"""
策略分析工具
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any

class StrategyAnalyzer:
    """策略分析器"""
    
    def __init__(self):
        self.strategies = {}
    
    def analyze_strategy_performance(self, signals: List[Dict], prices: pd.DataFrame) -> Dict:
        """分析策略性能"""
        if not signals:
            return {"error": "无信号数据"}
        
        # 计算基本指标
        buy_signals = [s for s in signals if s.get('action') == 'buy']
        sell_signals = [s for s in signals if s.get('action') == 'sell']
        
        return {
            "total_signals": len(signals),
            "buy_signals": len(buy_signals),
            "sell_signals": len(sell_signals),
            "buy_ratio": len(buy_signals) / len(signals) if signals else 0
        }
    
    def compare_strategies(self, strategy_results: Dict[str, Dict]) -> pd.DataFrame:
        """比较多个策略"""
        comparison_data = []
        
        for strategy_name, results in strategy_results.items():
            comparison_data.append({
                "strategy": strategy_name,
                "total_signals": results.get("total_signals", 0),
                "buy_signals": results.get("buy_signals", 0),
                "sell_signals": results.get("sell_signals", 0),
                "buy_ratio": results.get("buy_ratio", 0)
            })
        
        return pd.DataFrame(comparison_data)

