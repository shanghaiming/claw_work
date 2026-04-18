"""
Dashboard services - Business logic layer for views.

Provides strategy discovery, backtest execution, and data summary functions
using the core/ modules.
"""

import os
import sys
import math
import importlib
import io
import traceback
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, List, Optional, Any

from core.runner import BacktestRunner
from core.data_loader import load_stock_data, list_available_symbols
from core.backtest_engine import BacktestEngine
from core.base_strategy import BaseStrategy

# Project root for resolving paths
PROJECT_ROOT = Path(__file__).resolve().parent.parent


def _discover_strategy_files() -> List[str]:
    """Walk the strategies directory and return strategy filenames (excluding
    __init__.py, base_strategy.py, and utility scripts)."""
    strategies_dir = PROJECT_ROOT / 'strategies'
    if not strategies_dir.exists():
        return []

    exclude_patterns = [
        '__init__', 'base_strategy', 'test_', 'fix_', 'check_', 'analyzer',
        'case_study', 'batch_', 'debug_', 'sample_', 'example_', 'tool_',
        'util_', 'helper_', 'mindgo_api',
        'price_action_talib_backtest_system',
        'price_action_reversals_reversal_',
        'price_action_ranges_market_structure_deep_analyzer',
    ]

    filenames = []
    for f in sorted(strategies_dir.iterdir()):
        if not f.name.endswith('.py'):
            continue
        if any(pat in f.name for pat in exclude_patterns):
            continue
        filenames.append(f.name)
    return filenames


def _load_strategy_module(strategy_name: str):
    """Attempt to import a single strategy module and return the module object
    along with any error string."""
    strategies_dir = PROJECT_ROOT / 'strategies'
    filepath = strategies_dir / f'{strategy_name}.py'
    if not filepath.exists():
        return None, f'File not found: {filepath}'

    module_path = f'strategies.{strategy_name}'
    spec = importlib.util.spec_from_file_location(module_path, str(filepath))
    if spec is None:
        return None, 'Could not create module spec'

    module = importlib.util.module_from_spec(spec)

    # Suppress stdout/stderr while loading (some strategies print on import)
    real_stdout, real_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        spec.loader.exec_module(module)
    except BaseException as exc:
        return None, str(exc)
    finally:
        sys.stdout, sys.stderr = real_stdout, real_stderr

    return module, None


def _find_strategy_class(module) -> Optional[type]:
    """Find the first BaseStrategy subclass defined in *module*."""
    for attr_name in dir(module):
        if attr_name.startswith('_'):
            continue
        try:
            attr = getattr(module, attr_name)
        except Exception:
            continue
        try:
            if isinstance(attr, type) and attr is not BaseStrategy and issubclass(attr, BaseStrategy):
                return attr
        except TypeError:
            continue
    return None


def get_strategy_list() -> List[Dict[str, Any]]:
    """Discover all strategies and return a list of info dicts.

    Each dict contains:
        name, filename, status, class_name, description, category, error

    *status* is one of ``'loaded'``, ``'error'``, or ``'no_base_strategy'``.
    """
    filenames = _discover_strategy_files()
    strategies: List[Dict[str, Any]] = []

    for filename in filenames:
        strategy_name = filename[:-3]  # strip .py
        info: Dict[str, Any] = {
            'name': strategy_name,
            'filename': filename,
            'status': 'no_base_strategy',
            'class_name': None,
            'description': '',
            'category': 'general',
            'error': None,
        }

        module, load_error = _load_strategy_module(strategy_name)
        if load_error is not None:
            info['status'] = 'error'
            info['error'] = load_error
            strategies.append(info)
            continue

        cls = _find_strategy_class(module)
        if cls is None:
            info['status'] = 'no_base_strategy'
            info['error'] = 'No BaseStrategy subclass found'
            strategies.append(info)
            continue

        info['status'] = 'loaded'
        info['class_name'] = cls.__name__
        info['description'] = getattr(cls, 'strategy_description', '') or ''
        info['category'] = getattr(cls, 'strategy_category', 'general') or 'general'
        strategies.append(info)

    return strategies


def get_strategy_detail(strategy_name: str) -> Optional[Dict[str, Any]]:
    """Return detailed information about a single strategy.

    Includes the fields from :func:`get_strategy_list` plus ``default_params``
    and ``params_schema`` extracted from the strategy class.
    """
    module, load_error = _load_strategy_module(strategy_name)
    if load_error is not None:
        return {
            'name': strategy_name,
            'filename': f'{strategy_name}.py',
            'status': 'error',
            'class_name': None,
            'description': '',
            'category': 'general',
            'error': load_error,
            'default_params': {},
            'params_schema': {},
        }

    cls = _find_strategy_class(module)
    if cls is None:
        return {
            'name': strategy_name,
            'filename': f'{strategy_name}.py',
            'status': 'no_base_strategy',
            'class_name': None,
            'description': '',
            'category': 'general',
            'error': 'No BaseStrategy subclass found',
            'default_params': {},
            'params_schema': {},
        }

    # Instantiate a lightweight strategy just to read default params.
    # We need data to __init__, so build a minimal valid DataFrame.
    dummy_data = pd.DataFrame({
        'open': [1.0], 'high': [1.0], 'low': [1.0], 'close': [1.0],
        'volume': [0],
    }, index=pd.date_range('2020-01-01', periods=1))
    dummy_data['symbol'] = 'DUMMY'

    try:
        temp_instance = cls(dummy_data, params={})
        default_params = temp_instance.params
    except Exception:
        # Fallback: call get_default_params on the class directly
        try:
            default_params = cls.get_default_params(cls)
        except Exception:
            default_params = {}

    params_schema = getattr(cls, 'strategy_params_schema', {}) or {}

    return {
        'name': strategy_name,
        'filename': f'{strategy_name}.py',
        'status': 'loaded',
        'class_name': cls.__name__,
        'description': getattr(cls, 'strategy_description', '') or '',
        'category': getattr(cls, 'strategy_category', 'general') or 'general',
        'error': None,
        'default_params': default_params,
        'params_schema': params_schema,
    }


def _to_native(obj):
    """Recursively convert numpy/pandas types to native Python types for
    JSON serialization.  NaN / Infinity are converted to None."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if isinstance(obj, (np.floating,)):
        v = float(obj)
        if math.isnan(v) or math.isinf(v):
            return None
        return v
    if isinstance(obj, (np.integer,)):
        return int(obj)
    if isinstance(obj, (np.bool_,)):
        return bool(obj)
    if isinstance(obj, (np.ndarray,)):
        return _to_native(obj.tolist())
    if isinstance(obj, (pd.Timestamp,)):
        return obj.isoformat()
    if isinstance(obj, (int, bool, str)):
        return obj
    if isinstance(obj, dict):
        return {k: _to_native(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_to_native(v) for v in obj]
    # Fallback: cast to string
    return str(obj)


def run_backtest(
    strategy_name: str,
    symbol: str,
    timeframe: str,
    start_date: str,
    end_date: str,
    initial_cash: float = 100000.0,
    params: Optional[Dict] = None,
) -> Dict[str, Any]:
    """Execute a backtest and return JSON-safe results.

    Steps:
      1. Load price data via ``load_stock_data``
      2. Inject a ``symbol`` column
      3. Run the strategy via ``BacktestEngine``
      4. Serialize results (equity_curve, summary, drawdown, risk_return,
         trades) into plain Python dicts/lists.

    On error, returns ``{'error': <message>}`` so the view can respond
    gracefully.
    """
    try:
        # --- 1. Load data ---
        data = load_stock_data(
            symbol=symbol,
            start_date=start_date,
            end_date=end_date,
            frequency=timeframe,
        )
        if data.empty:
            return {'error': f'No data returned for {symbol} ({timeframe}) between {start_date} and {end_date}'}

        # --- 2. Add symbol column ---
        data['symbol'] = symbol

        # --- 3. Discover and load the strategy class ---
        runner = BacktestRunner()
        strategy_cls = runner.load_strategy(strategy_name)
        if strategy_cls is None:
            return {'error': f'Strategy "{strategy_name}" not found or failed to load'}

        # --- 4. Execute backtest ---
        engine = BacktestEngine(
            data=data,
            strategy_class=strategy_cls,
            initial_cash=float(initial_cash),
        )
        engine_params = params or {}
        results = engine.run_backtest(engine_params)

        if results is None:
            return {'error': 'Backtest engine returned no results'}

        # --- 5. Serialize results ---
        serialized = _serialize_backtest_results(results, initial_cash)
        return serialized

    except FileNotFoundError as exc:
        return {'error': str(exc)}
    except ValueError as exc:
        return {'error': str(exc)}
    except Exception as exc:
        tb = traceback.format_exc()
        return {'error': f'{type(exc).__name__}: {exc}', 'traceback': tb}


def _serialize_backtest_results(results: Dict, initial_cash: float) -> Dict[str, Any]:
    """Convert raw BacktestEngine output into a JSON-safe dict."""

    # -- equity_curve (pd.Series -> list of dicts) --
    equity_curve_series = results.get('equity_curve')
    if isinstance(equity_curve_series, pd.Series):
        equity_curve = [
            {
                'timestamp': _to_native(ts),
                'value': _to_native(val),
            }
            for ts, val in equity_curve_series.items()
        ]
    else:
        equity_curve = []

    # -- summary --
    raw_summary = results.get('summary', {})
    summary = {
        'total_return': _to_native(raw_summary.get('total_return', 0.0)),
        'annualized_return': _to_native(raw_summary.get('annualized_return', 0.0)),
        'trade_count': _to_native(raw_summary.get('trade_count', 0)),
        'final_equity': _to_native(raw_summary.get('final_equity', initial_cash)),
    }

    # -- drawdown --
    raw_drawdown = results.get('drawdown', {})
    drawdown = {
        'max_drawdown': _to_native(raw_drawdown.get('max_drawdown', 0.0)),
    }

    # -- risk_return --
    raw_risk_return = results.get('risk_return', {})
    risk_return = {
        'sharpe_ratio': _to_native(raw_risk_return.get('sharpe_ratio', 0.0)),
        'sortino_ratio': _to_native(raw_risk_return.get('sortino_ratio', 0.0)),
    }

    # -- trades (list of dicts) --
    raw_trades = results.get('trades_list', results.get('trades', []))
    trades = [
        {
            'timestamp': _to_native(t.get('timestamp', '')),
            'action': _to_native(t.get('action', '')),
            'symbol': _to_native(t.get('symbol', '')),
            'price': _to_native(t.get('price', 0.0)),
            'shares': _to_native(t.get('shares', 0)),
            'profit': _to_native(t.get('profit', 0.0)),
        }
        for t in raw_trades
        if isinstance(t, dict)
    ]

    return {
        'equity_curve': equity_curve,
        'summary': summary,
        'drawdown': drawdown,
        'risk_return': risk_return,
        'trades': trades,
    }


def get_available_stocks(frequency: str = 'daily') -> List[str]:
    """Return a sorted list of stock symbols available for the given
    frequency.  Returns an empty list on error instead of raising."""
    try:
        return list_available_symbols(frequency)
    except (ValueError, FileNotFoundError):
        return []


def get_stock_kline_data(symbol: str, frequency: str = 'daily',
                         start_date: str = None, end_date: str = None,
                         limit: int = 200) -> Dict[str, Any]:
    """Load stock OHLCV data and compute technical indicators for charting.

    Returns a dict with ``ohlcv``, ``indicators``, ``latest`` keys.
    """
    try:
        data = load_stock_data(symbol=symbol, start_date=start_date,
                               end_date=end_date, frequency=frequency)
    except Exception as exc:
        return {'error': str(exc)}

    if data.empty:
        return {'error': f'No data for {symbol}'}

    # Limit to most recent N bars
    if len(data) > limit:
        data = data.tail(limit)

    # Compute indicators
    indicators = _compute_chart_indicators(data)

    # Build OHLCV arrays
    dates = [d.strftime('%Y-%m-%d') if hasattr(d, 'strftime') else str(d)
             for d in data.index]
    ohlcv = {
        'dates': dates,
        'open': _to_native(data['open'].values.tolist()),
        'high': _to_native(data['high'].values.tolist()),
        'low': _to_native(data['low'].values.tolist()),
        'close': _to_native(data['close'].values.tolist()),
        'volume': _to_native(data['volume'].values.tolist()) if 'volume' in data.columns else [],
    }

    # Latest values
    latest = {
        'price': _to_native(data['close'].iloc[-1]),
        'change_pct': _to_native(data['pct_change'].iloc[-1]) if 'pct_change' in data.columns else 0,
        'volume': _to_native(data['volume'].iloc[-1]) if 'volume' in data.columns else 0,
    }

    return {
        'symbol': symbol,
        'frequency': frequency,
        'ohlcv': ohlcv,
        'indicators': indicators,
        'latest': latest,
    }


def _compute_chart_indicators(data: pd.DataFrame) -> Dict[str, Any]:
    """Compute MA, RSI, MACD for chart overlay."""
    close = data['close']
    result = {}

    # Moving averages
    for window in [5, 10, 20, 60]:
        ma = close.rolling(window).mean()
        key = f'ma{window}'
        result[key] = _to_native(ma.values.tolist())

    # RSI (14)
    delta = close.diff()
    gain = delta.clip(lower=0).rolling(14).mean()
    loss = (-delta.clip(upper=0)).rolling(14).mean()
    rs = gain / loss.replace(0, np.nan)
    rsi = 100 - (100 / (1 + rs))
    result['rsi'] = _to_native(rsi.values.tolist())
    result['rsi_latest'] = _to_native(rsi.iloc[-1]) if not rsi.empty else None

    # MACD (12, 26, 9)
    ema12 = close.ewm(span=12, adjust=False).mean()
    ema26 = close.ewm(span=26, adjust=False).mean()
    macd_line = ema12 - ema26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    macd_hist = macd_line - signal_line
    result['macd'] = _to_native(macd_line.values.tolist())
    result['macd_signal'] = _to_native(signal_line.values.tolist())
    result['macd_hist'] = _to_native(macd_hist.values.tolist())
    result['macd_latest'] = _to_native(macd_line.iloc[-1]) if not macd_line.empty else None

    # Bollinger Bands (20, 2)
    bb_mid = close.rolling(20).mean()
    bb_std = close.rolling(20).std()
    result['bb_upper'] = _to_native((bb_mid + 2 * bb_std).values.tolist())
    result['bb_mid'] = _to_native(bb_mid.values.tolist())
    result['bb_lower'] = _to_native((bb_mid - 2 * bb_std).values.tolist())

    return result


def run_stock_screening(strategy_name: str, symbols: List[str],
                        frequency: str = 'daily',
                        start_date: str = None, end_date: str = None,
                        params: Optional[Dict] = None) -> List[Dict[str, Any]]:
    """Run a single strategy on multiple stocks for screening.

    Returns list of dicts with symbol, signal_count, buy_count, sell_count,
    latest_signal, latest_price.
    """
    module, load_error = _load_strategy_module(strategy_name)
    if load_error:
        return [{'error': load_error}]

    cls = _find_strategy_class(module)
    if cls is None:
        return [{'error': f'No BaseStrategy subclass in {strategy_name}'}]

    results = []
    for symbol in symbols:
        try:
            data = load_stock_data(symbol=symbol, start_date=start_date,
                                   end_date=end_date, frequency=frequency)
            if data.empty or len(data) < 20:
                continue
            data['symbol'] = symbol

            instance = cls(data, params=params or {})
            signals = instance.generate_signals()

            buy_count = len([s for s in signals if s.get('action') == 'buy'])
            sell_count = len([s for s in signals if s.get('action') == 'sell'])
            latest_signal = signals[-1]['action'] if signals else 'none'
            latest_price = _to_native(data['close'].iloc[-1])

            results.append({
                'symbol': symbol,
                'signal_count': len(signals),
                'buy_count': buy_count,
                'sell_count': sell_count,
                'latest_signal': latest_signal,
                'latest_price': latest_price,
            })
        except Exception:
            continue

    # Sort by buy signals descending
    results.sort(key=lambda x: x.get('buy_count', 0), reverse=True)
    return results


def get_data_summary() -> Dict[str, Any]:
    """Return a summary of available data across all timeframes.

    Returns a dict with a ``timeframes`` key mapping to per-frequency counts
    and a ``total_symbols`` count.
    """
    timeframes = ['daily', 'weekly', '5min', '30min']
    summary: Dict[str, Any] = {'timeframes': {}, 'total_symbols': 0}

    all_symbols = set()
    for tf in timeframes:
        try:
            symbols = list_available_symbols(tf)
            summary['timeframes'][tf] = len(symbols)
            all_symbols.update(symbols)
        except (ValueError, FileNotFoundError):
            summary['timeframes'][tf] = 0

    summary['total_symbols'] = len(all_symbols)
    return summary
