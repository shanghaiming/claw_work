"""
简单看板
"""
import json

class SimpleDashboard:
    def __init__(self, results_dir="backtest/results"):
        self.results_dir = results_dir
    
    def show_strategy_results(self, result_file):
        """显示策略结果"""
        try:
            with open(f"{self.results_dir}/{result_file}", 'r') as f:
                results = json.load(f)
            
            print("=" * 50)
            print(f"策略: {results.get('strategy_name', '未知')}")
            print(f"信号数量: {len(results.get('signals', []))}")
            
            signals = results.get('signals', [])
            if signals:
                buy_count = len([s for s in signals if s.get('action') == 'buy'])
                sell_count = len([s for s in signals if s.get('action') == 'sell'])
                print(f"买入信号: {buy_count}, 卖出信号: {sell_count}")
            
            params = results.get('params', {})
            if params:
                print("参数:")
                for k, v in params.items():
                    print(f"  {k}: {v}")
            
            print("=" * 50)
            
        except Exception as e:
            print(f"加载结果失败: {e}")
