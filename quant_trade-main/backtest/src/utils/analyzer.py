from ..backtest.engine import BacktestEngine
from ..strategies import MovingAverageStrategy
from itertools import product
import pandas as pd

def parameter_grid_search(data, strategy_class):
    """遍历参数组合寻找最优策略"""
    short_windows = [5, 10, 20]
    long_windows = [20, 30, 50]
    results = []

    for short, long in product(short_windows, long_windows):
        # 运行回测
        engine = BacktestEngine(data, strategy_class, initial_cash=1e6)
        perf = engine.run_backtest({'short_window': short, 'long_window': long})
        
        # 记录结果
        results.append({
            'short_window': short,
            'long_window': long,
            'sharpe_ratio': perf['sharpe_ratio'],
            'total_return': perf['total_return'],
            'max_drawdown': perf['max_drawdown']
        })
    
    return pd.DataFrame(results)

# 执行优化
df_results = parameter_grid_search(data, MovingAverageStrategy)
print(df_results.sort_values('sharpe_ratio', ascending=False))