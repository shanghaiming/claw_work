"""
批量回测TradingView策略
在27只多样化股票池上测试5个新TV策略 + 基准(EnhancedFusion)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from core.data_loader import load_stock_data
from core.backtest_engine import BacktestEngine

# 策略导入
from strategies.turtle_trading_strategy import TurtleTradingStrategy
from strategies.squeeze_momentum_strategy import SqueezeMomentumStrategy
from strategies.kauffman_er_gate_strategy import KauffERGateStrategy
from strategies.volatility_regime_strategy import VolatilityRegimeStrategy
from strategies.confluence_matrix_strategy import ConfluenceMatrixStrategy
from strategies.enhanced_fusion_strategy import EnhancedFusionStrategy

# 27只多样化股票池
TEST_STOCKS = {
    # 大盘金融
    '601318.SH': '中国平安', '600036.SH': '招商银行',
    # 大盘消费
    '600519.SH': '贵州茅台', '000858.SZ': '五粮液',
    # 家电
    '000333.SZ': '美的集团', '000651.SZ': '格力电器',
    # 科技成长
    '300750.SZ': '宁德时代', '002415.SZ': '海康威视',
    # 医药
    '600276.SH': '恒瑞医药', '000538.SZ': '云南白药',
    # 半导体
    '002049.SZ': '紫光国微', '603986.SH': '兆易创新',
    # 新能源
    '601012.SH': '隆基绿能', '600438.SH': '通威股份',
    # 化工
    '600309.SH': '万华化学', '002493.SZ': '荣盛石化',
    # 小盘题材
    '002230.SZ': '科大讯飞', '300059.SZ': '东方财富',
    # 小盘软件
    '300454.SZ': '深信服', '688111.SH': '金山办公',
    # 周期有色
    '601899.SH': '紫金矿业', '600362.SH': '江西铜业',
    # 周期地产
    '000002.SZ': '万科A', '600048.SH': '保利发展',
    # 科创板
    '688981.SH': '中芯国际', '688012.SH': '中微公司',
    # 航运
    '601919.SH': '中远海控',
}

STRATEGIES = {
    'TurtleTrading': (TurtleTradingStrategy, {}),
    'SqueezeMomentum': (SqueezeMomentumStrategy, {}),
    'KauffmanERGate': (KauffERGateStrategy, {}),
    'VolatilityRegime': (VolatilityRegimeStrategy, {}),
    'ConfluenceMatrix': (ConfluenceMatrixStrategy, {}),
    'EnhancedFusion': (EnhancedFusionStrategy, {}),  # baseline
}


def run_batch_backtest():
    results = {}

    for strat_name, (strat_class, params) in STRATEGIES.items():
        print(f"\n{'='*80}")
        print(f"策略: {strat_name}")
        print(f"{'='*80}")

        stock_results = []
        stock_count = 0
        profitable_count = 0
        total_return = 0

        for symbol, name in TEST_STOCKS.items():
            try:
                data = load_stock_data(symbol, frequency='daily')
                if data is None or len(data) < 200:
                    print(f"  {name}({symbol}): 数据不足, 跳过")
                    continue

                engine = BacktestEngine(data, strat_class, initial_cash=1e6, commission=0.0003)
                report = engine.run_backtest(params)

                total_ret = report['summary']['total_return']
                max_dd = report['drawdown']['max_drawdown']
                trade_count = report['summary']['trade_count']
                sharpe = report['risk_return'].get('sharpe_ratio', 0)
                win_rate = report['trades'].get('win_rate', 0)

                stock_results.append({
                    'symbol': symbol,
                    'name': name,
                    'total_return': total_ret,
                    'max_drawdown': max_dd,
                    'trade_count': trade_count,
                    'sharpe': sharpe,
                    'win_rate': win_rate,
                })

                stock_count += 1
                if total_ret > 0:
                    profitable_count += 1
                total_return += total_ret

                print(f"  {name}({symbol}): {total_ret:+.1f}% DD={max_dd:.1f}% "
                      f"trades={trade_count} sharpe={sharpe:.2f} win={win_rate:.1%}")

            except Exception as e:
                print(f"  {name}({symbol}): ERROR - {str(e)[:100]}")
                import traceback
                traceback.print_exc()

        if stock_count > 0:
            avg_return = total_return / stock_count
            results[strat_name] = {
                'avg_return': avg_return,
                'stock_count': stock_count,
                'profitable': profitable_count,
                'profitable_pct': profitable_count / stock_count * 100,
                'details': stock_results,
            }
        else:
            results[strat_name] = {
                'avg_return': 0, 'stock_count': 0,
                'profitable': 0, 'profitable_pct': 0,
                'details': [],
            }

    # ===== Print Summary =====
    print(f"\n{'='*80}")
    print("SUMMARY")
    print(f"{'='*80}")
    print(f"{'Strategy':<25} {'Avg Return':>12} {'Stocks':>8} {'Profitable':>12} {'% Profit':>10}")
    print("-" * 70)

    sorted_results = sorted(results.items(), key=lambda x: x[1]['avg_return'], reverse=True)
    for strat_name, r in sorted_results:
        marker = " *** BEST" if r == sorted_results[0][1] else ""
        marker2 = " (baseline)" if strat_name == 'EnhancedFusion' else ""
        print(f"{strat_name:<25} {r['avg_return']:>+11.1f}% {r['stock_count']:>8d} "
              f"{r['profitable']:>5d}/{r['stock_count']:<5d} {r['profitable_pct']:>9.1f}%"
              f"{marker}{marker2}")

    # Per-stock comparison
    print(f"\n{'='*80}")
    print("PER-STOCK COMPARISON (top/bottom)")
    print(f"{'='*80}")

    # Collect all stocks across strategies
    all_stocks = {}
    for strat_name, r in results.items():
        for detail in r['details']:
            sym = detail['symbol']
            if sym not in all_stocks:
                all_stocks[sym] = {}
            all_stocks[sym][strat_name] = detail['total_return']

    # Best stock per strategy
    for strat_name in sorted(results.keys()):
        details = results[strat_name]['details']
        if not details:
            continue
        best = max(details, key=lambda x: x['total_return'])
        worst = min(details, key=lambda x: x['total_return'])
        print(f"{strat_name}: Best={best['name']}({best['total_return']:+.1f}%) "
              f"Worst={worst['name']}({worst['total_return']:+.1f}%)")

    return results


if __name__ == '__main__':
    results = run_batch_backtest()
