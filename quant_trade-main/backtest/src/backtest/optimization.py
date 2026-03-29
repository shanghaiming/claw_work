# backtest/optimization.py

import pandas as pd
from backtest.engine import BacktestEngine
class ParameterOptimizer:
    @staticmethod
    def grid_search(strategy_class, data: pd.DataFrame, param_grid: dict, initial_cash: float = 1e6) -> pd.DataFrame:
        results = []
        for short in param_grid.get('short_window', []):
            for long in param_grid.get('long_window', []):
                if short >= long:
                    continue
                
                try:
                    engine = BacktestEngine(data, strategy_class, initial_cash)
                    report = engine.run_backtest({'short_window': short, 'long_window': long})
                    
                    # 防御性获取指标
                    sharpe = report.get('risk_return', {}).get('sharpe_ratio', 0.0)
                    total_return = report.get('summary', {}).get('total_return', 0.0)
                    
                    results.append({
                        'short': short,
                        'long': long,
                        'sharpe_ratio': sharpe,
                        'total_return': total_return
                    })
                except Exception as e:
                    print(f"参数组合 ({short}, {long}) 失败: {e}")
        
        return pd.DataFrame(results)
    
    @staticmethod
    def random_search(
        strategy_class: type,
        data: pd.DataFrame,
        param_distributions: dict,
        n_iter: int = 10,
        initial_cash: float = 1e6
    ) -> pd.DataFrame:
        """随机搜索参数优化"""
        # ... 具体实现 ...

    @staticmethod
    def bayesian_optimization(
        strategy_class: type,
        data: pd.DataFrame,
        param_bounds: dict,
        n_iter: int = 10,
        initial_cash: float = 1e6
    ) -> pd.DataFrame:
        """贝叶斯优化"""
        # ... 具体实现 ...