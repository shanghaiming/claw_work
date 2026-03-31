# 整合策略接口文件
# 自动生成于: 2026-03-31 07:55:11

from backtest.src.strategies.base_strategy import BaseStrategy

# 可用策略列表
AVAILABLE_STRATEGIES = {}

# 策略工厂函数
def create_strategy(strategy_name: str, **kwargs):
    """创建策略实例"""
    if strategy_name not in AVAILABLE_STRATEGIES:
        raise ValueError(f"未知策略: {strategy_name}")
    
    strategy_class = AVAILABLE_STRATEGIES[strategy_name]
    return strategy_class(**kwargs)

# 策略加载函数
def load_all_strategies():
    """加载所有策略"""
    return list(AVAILABLE_STRATEGIES.keys())

