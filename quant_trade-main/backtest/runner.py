"""
统一回测运行器
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import pandas as pd
import importlib

class BacktestRunner:
    def __init__(self):
        self.strategies = self._discover_strategies()
    
    def _discover_strategies(self):
        """发现所有策略"""
        strategies = {}
        strategies_dir = os.path.join(os.path.dirname(__file__), '..', 'strategies')
        
        if not os.path.exists(strategies_dir):
            return strategies
        
        for filename in os.listdir(strategies_dir):
            if filename.endswith('.py') and filename not in ['__init__.py', 'base_strategy.py']:
                strategy_name = filename[:-3]
                try:
                    module = importlib.import_module(f'strategies.{strategy_name}')
                    # 查找策略类
                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and attr_name not in ['BaseStrategy']:
                            try:
                                from strategies.base_strategy import BaseStrategy
                                if issubclass(attr, BaseStrategy) and attr != BaseStrategy:
                                    strategies[strategy_name] = attr
                                    break
                            except:
                                continue
                except Exception as e:
                    print(f"策略 {strategy_name} 加载失败: {e}")
        
        return strategies
    
    def list_strategies(self):
        """列出所有可用策略"""
        return list(self.strategies.keys())
    
    def run(self, strategy_name, data, params=None):
        """运行策略"""
        if strategy_name not in self.strategies:
            raise ValueError(f"策略不存在: {strategy_name}")
        
        strategy_cls = self.strategies[strategy_name]
        params = params or {}
        strategy = strategy_cls(data, params)
        strategy.generate_signals()
        
        return {
            'strategy_name': strategy_name,
            'signals': strategy.signals,
            'params': params
        }

if __name__ == "__main__":
    runner = BacktestRunner()
    strategies = runner.list_strategies()
    print(f"发现 {len(strategies)} 个策略:")
    for s in strategies:
        print(f"  - {s}")
