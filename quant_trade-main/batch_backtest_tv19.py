"""Batch 19: Remaining pre-existing strategies - Group A (5 strategies)"""
import sys, os, io, contextlib
sys.path.insert(0, os.path.dirname(__file__))
from core.data_loader import load_stock_data
from core.backtest_engine import BacktestEngine

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

# Strategy imports
try:
    from strategies.adaptive_keltner_strategy import AdaptiveKeltnerStrategy
    _strats = [('AdaptiveKeltner', AdaptiveKeltnerStrategy)]
except Exception as e:
    print(f"AdaptiveKeltner import error: {e}"); _strats = []

try:
    from strategies.advanced_rsi_momentum_strategy import AdvancedRsiMomentumStrategy
    _strats.append(('AdvancedRSIMom', AdvancedRsiMomentumStrategy))
except Exception as e:
    print(f"AdvancedRSIMom import error: {e}")

try:
    from strategies.aegis_hma_sentinel_strategy import AegisHmaSentinelStrategy
    _strats.append(('AegisHMA', AegisHmaSentinelStrategy))
except Exception as e:
    print(f"AegisHMA import error: {e}")

try:
    from strategies.breakout_pullback_strategy import BreakoutPullbackStrategy
    _strats.append(('BreakoutPullback', BreakoutPullbackStrategy))
except Exception as e:
    print(f"BreakoutPullback import error: {e}")

try:
    from strategies.chandelier_exit_strategy import ChandelierExitStrategy
    _strats.append(('ChandelierExit', ChandelierExitStrategy))
except Exception as e:
    print(f"ChandelierExit import error: {e}")

for sn, sc in _strats:
    print(f"\n策略: {sn}", flush=True)
    t=0; c=0; p=0
    for sym, nm in STOCKS.items():
        try:
            d = load_stock_data(sym, frequency='daily')
            if d is None or len(d)<200: continue
            if 'symbol' not in d.columns: d['symbol']='DEFAULT'
            with contextlib.redirect_stdout(io.StringIO()):
                e = BacktestEngine(d, sc, initial_cash=1e6, commission=0.0003)
                r = e.run_backtest({})
            ret=r['summary']['total_return']; dd=r['drawdown']['max_drawdown']
            tc=r['summary']['trade_count']; sh=r['risk_return'].get('sharpe_ratio',0)
            wr=r['trades'].get('win_rate',0)
            t+=ret; c+=1
            if ret>0: p+=1
            print(f"  {nm}({sym}): {ret:+.1f}% DD={dd:.1f}% trades={tc} sharpe={sh:.2f} win={wr:.1%}", flush=True)
        except Exception as ex:
            print(f"  {nm}({sym}): ERROR - {str(ex)[:80]}", flush=True)
    if c>0: print(f"  >> {sn}: avg={t/c:+.1f}% profitable={p}/{c}", flush=True)
