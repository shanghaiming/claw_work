"""
批量回测TradingView策略 - 第十批 (HAR-RV + Liquidity Trap)
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import io
import contextlib
from core.data_loader import load_stock_data
from core.backtest_engine import BacktestEngine
from strategies.har_rv_sentinel_strategy import HARRVSentinelStrategy
from strategies.liquidity_trap_strategy import LiquidityTrapStrategy

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
    'HARRVSentinel': (HARRVSentinelStrategy, {}),
    'LiquidityTrap': (LiquidityTrapStrategy, {}),
}


def run_batch():
    results = {}
    for strat_name, (strat_class, params) in STRATEGIES.items():
        print(f"\n策略: {strat_name}", flush=True)
        stock_count = 0; profitable = 0; total_return = 0
        for symbol, name in TEST_STOCKS.items():
            try:
                data = load_stock_data(symbol, frequency='daily')
                if data is None or len(data) < 200: continue
                if 'symbol' not in data.columns: data['symbol'] = 'DEFAULT'
                with contextlib.redirect_stdout(io.StringIO()):
                    engine = BacktestEngine(data, strat_class, initial_cash=1e6, commission=0.0003)
                    report = engine.run_backtest(params)
                ret = report['summary']['total_return']
                dd = report['drawdown']['max_drawdown']
                tc = report['summary']['trade_count']
                sh = report['risk_return'].get('sharpe_ratio', 0)
                wr = report['trades'].get('win_rate', 0)
                total_return += ret; stock_count += 1
                if ret > 0: profitable += 1
                print(f"  {name}({symbol}): {ret:+.1f}% DD={dd:.1f}% trades={tc} sharpe={sh:.2f} win={wr:.1%}", flush=True)
            except Exception as e:
                print(f"  {name}({symbol}): ERROR - {str(e)[:80]}", flush=True)
        if stock_count > 0:
            avg = total_return / stock_count
            results[strat_name] = {'avg_return': avg, 'stock_count': stock_count, 'profitable': profitable}
            print(f"  >> {strat_name}: avg={avg:+.1f}% profitable={profitable}/{stock_count}", flush=True)
    return results


if __name__ == '__main__':
    run_batch()
