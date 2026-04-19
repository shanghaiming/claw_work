"""Batch 18: Ensemble strategy test - Regression-Volume Confirmation"""
import sys, os, io, contextlib
sys.path.insert(0, os.path.dirname(__file__))
from core.data_loader import load_stock_data
from core.backtest_engine import BacktestEngine
from strategies.ensemble_regression_volume_strategy import EnsembleRegressionVolumeStrategy

STOCKS = {
    '601318.SH': '中国平安', '600036.SH': '招商银行', '600519.SH': '贵州茅台',
    '000858.SZ': '五粮液', '000333.SZ': '美的集团', '000651.SZ': '格力电器',
    '300750.SZ': '宁德时代', '002415.SZ': '海康威视', '600276.SH': '恒瑞医药',
    '000538.SZ': '云南白药', '002049.SZ': '紫光国微', '603986.SH': '兆易创新',
    '601012.SH': '隆基绿能', '600438.SH': '通威股份', '600309.SH': '万华化学',
    '002493.SZ': '荣盛石化', '002230.SZ': '科大讯飞', '300059.SZ': '东方财富',
    '300454.SZ': '深信服', '688111.SH': '金山办公', '601899.SH': '紫金矿业',
    '600362.SH': '江西铜业', '000002.SZ': '万科A', '600048.SH': '保利发展',
    '688981.SH': '中芯国际', '688012.SH': '中微公司', '601919.SH': '中远海控',
}

print("=" * 70)
print("ENSEMBLE: IRLS(方向) + VDP(确认) + EMA200(过滤) + ATR(止损)")
print("=" * 70)

t = 0; c = 0; p_count = 0
for sym, nm in STOCKS.items():
    try:
        d = load_stock_data(sym, frequency='daily')
        if d is None or len(d) < 200:
            continue
        if 'symbol' not in d.columns:
            d['symbol'] = 'DEFAULT'
        with contextlib.redirect_stdout(io.StringIO()):
            e = BacktestEngine(d, EnsembleRegressionVolumeStrategy, initial_cash=1e6, commission=0.0003)
            r = e.run_backtest({})
        ret = r['summary']['total_return']
        dd = r['drawdown']['max_drawdown']
        tc = r['summary']['trade_count']
        sh = r['risk_return'].get('sharpe_ratio', 0)
        wr = r['trades'].get('win_rate', 0)
        t += ret; c += 1
        if ret > 0:
            p_count += 1
        print(f"  {nm}({sym}): {ret:+.1f}% DD={dd:.1f}% trades={tc} sharpe={sh:.2f} win={wr:.1%}", flush=True)
    except Exception as ex:
        print(f"  {nm}({sym}): ERROR - {str(ex)[:80]}", flush=True)

if c > 0:
    avg = t / c
    print(f"\n{'='*70}")
    print(f"ENSEMBLE RESULT: avg={avg:+.1f}% profitable={p_count}/{c}")
    print(f"Compare: IRLS standalone=+38.1%, VDP standalone=+52.6%")
    print(f"{'='*70}")
