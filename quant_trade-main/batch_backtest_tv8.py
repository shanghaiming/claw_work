"""
批量回测TradingView策略 - 第八批 (Tier 1 新策略)
基于TV Learning TOP_STRATEGIES_SUMMARY.md中的14个Tier 1策略
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import pandas as pd
import numpy as np
from core.data_loader import load_stock_data
from core.backtest_engine import BacktestEngine

from strategies.smart_liquidity_trend_strategy import SmartLiquidityTrendStrategy
from strategies.institutional_pressure_strategy import InstitutionalPressureStrategy
from strategies.algionics_ribbon_strategy import AlgionicsRibbonStrategy
from strategies.fractal_liquidity_strategy import FractalLiquidityStrategy
from strategies.fib_swing_probability_strategy import FibSwingProbabilityStrategy
from strategies.undercut_rally_strategy import UndercutRallyStrategy
from strategies.metis_ladder_strategy import MetisLadderStrategy
from strategies.nadaraya_watson_strategy import NadarayaWatsonStrategy

TEST_STOCKS = {
    '601318.SH': '中国平安', '600036.SH': '招商银行',
    '600519.SH': '贵州茅台', '000858.SZ': '五粮液',
    '000333.SZ': '美的集团', '000651.SZ': '格力电器',
    '300750.SZ': '宁德时代', '002415.SZ': '海康威视',
    '600276.SH': '恒瑞医药', '000538.SZ': '云南白药',
    '002049.SZ': '紫光国微', '603986.SH': '兆易创新',
    '601012.SH': '隆基绿能', '600438.SH': '通威股份',
    '600309.SH': '万华化学', '002493.SZ': '荣盛石化',
    '002230.SZ': '科大讯飞', '300059.SZ': '东方财富',
    '300454.SZ': '深信服', '688111.SH': '金山办公',
    '601899.SH': '紫金矿业', '600362.SH': '江西铜业',
    '000002.SZ': '万科A', '600048.SH': '保利发展',
    '688981.SH': '中芯国际', '688012.SH': '中微公司',
    '601919.SH': '中远海控',
}

STRATEGIES = {
    'SmartLiquidity': (SmartLiquidityTrendStrategy, {}),
    'InstPressure': (InstitutionalPressureStrategy, {}),
    'AlgionicsRibbon': (AlgionicsRibbonStrategy, {}),
    'FractalLiquidity': (FractalLiquidityStrategy, {}),
    'FibSwingProb': (FibSwingProbabilityStrategy, {}),
    'UndercutRally': (UndercutRallyStrategy, {}),
    'MetisLadder': (MetisLadderStrategy, {}),
    'NadarayaWatson': (NadarayaWatsonStrategy, {}),
}


def run_batch():
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

                if 'symbol' not in data.columns:
                    data['symbol'] = 'DEFAULT'
                engine = BacktestEngine(data, strat_class, initial_cash=1e6, commission=0.0003)
                report = engine.run_backtest(params)

                total_ret = report['summary']['total_return']
                max_dd = report['drawdown']['max_drawdown']
                trade_count = report['summary']['trade_count']
                sharpe = report['risk_return'].get('sharpe_ratio', 0)
                win_rate = report['trades'].get('win_rate', 0)

                stock_results.append({
                    'symbol': symbol, 'name': name,
                    'total_return': total_ret, 'max_drawdown': max_dd,
                    'trade_count': trade_count, 'sharpe': sharpe, 'win_rate': win_rate,
                })

                stock_count += 1
                if total_ret > 0:
                    profitable_count += 1
                total_return += total_ret

                print(f"  {name}({symbol}): {total_ret:+.1f}% DD={max_dd:.1f}% "
                      f"trades={trade_count} sharpe={sharpe:.2f} win={win_rate:.1%}")

            except Exception as e:
                print(f"  {name}({symbol}): ERROR - {str(e)[:80]}")

        if stock_count > 0:
            avg_return = total_return / stock_count
            results[strat_name] = {
                'avg_return': avg_return, 'stock_count': stock_count,
                'profitable': profitable_count, 'profitable_pct': profitable_count / stock_count * 100,
                'details': stock_results,
            }

        print(f"\n{'='*80}")
        print("SUMMARY - Batch 8 (Tier 1 TV Strategies)")
        print(f"{'='*80}")
        print(f"{'Strategy':<25} {'Avg Return':>12} {'Stocks':>8} {'Profitable':>12}")
        print("-" * 60)
        for strat_name, r in sorted(results.items(), key=lambda x: x[1]['avg_return'], reverse=True):
            print(f"{strat_name:<25} {r['avg_return']:>+11.1f}% {r['stock_count']:>8d} "
                  f"{r['profitable']:>5d}/{r['stock_count']:<5d}")

    return results


if __name__ == '__main__':
    run_batch()
