"""
Dashboard views for quant trading platform.
"""

import io
import json
import sys

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from . import services


def overview(request):
    """Homepage with summary stats and quick access links."""
    import sys, io
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        strategy_list = services.get_strategy_list()
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

    total = len(strategy_list)
    loaded = len([s for s in strategy_list if s.get('status') == 'loaded'])
    errors = len([s for s in strategy_list if s.get('status') == 'error'])

    # Build available-data summary: stocks grouped by timeframe
    data_summary = {}
    try:
        stock_info = services.get_available_stocks()
        # stock_info is expected to be a dict mapping timeframe -> list of symbols
        if isinstance(stock_info, dict):
            for timeframe, symbols in stock_info.items():
                data_summary[timeframe] = len(symbols) if isinstance(symbols, list) else 0
        elif isinstance(stock_info, list):
            # If a flat list is returned, group under a default key
            data_summary['default'] = len(stock_info)
    except Exception:
        data_summary = {}

    context = {
        'total_strategies': total,
        'loaded_strategies': loaded,
        'error_strategies': errors,
        'data_summary': data_summary,
    }
    return render(request, 'dashboard/overview.html', context)


def strategy_list(request):
    """Display list of all strategies."""
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        strategies = services.get_strategy_list()
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

    stats = {
        'total': len(strategies),
        'loaded': len([s for s in strategies if s.get('status') == 'loaded']),
        'errors': len([s for s in strategies if s.get('status') == 'error']),
        'no_base_strategy': len([s for s in strategies if s.get('status') == 'no_base_strategy']),
    }

    context = {
        'strategies': strategies,
        'stats': stats,
    }
    return render(request, 'dashboard/strategy_list.html', context)


def strategy_detail(request, strategy_name):
    """Display details for a specific strategy."""
    strategy = services.get_strategy_detail(strategy_name)

    if not strategy:
        return render(request, 'dashboard/error.html', {
            'error': f'Strategy "{strategy_name}" not found',
        })

    context = {
        'strategy': strategy,
    }
    return render(request, 'dashboard/strategy_detail.html', context)


def backtest_page(request):
    """Render the backtest form page."""
    strategies = []
    try:
        strategies = services.get_strategy_list()
    except Exception:
        pass

    context = {
        'strategies': strategies,
    }
    return render(request, 'dashboard/backtest.html', context)


@csrf_exempt
@require_http_methods(['POST'])
def run_backtest(request):
    """AJAX endpoint: run a backtest and return JSON results."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON body'}, status=400)

    strategy_name = data.get('strategy_name')
    symbol = data.get('symbol')
    timeframe = data.get('timeframe', 'daily')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    initial_cash = data.get('initial_cash', 1000000)
    params = data.get('params', {})

    # Basic validation
    if not strategy_name:
        return JsonResponse({'error': 'strategy_name is required'}, status=400)
    if not symbol:
        return JsonResponse({'error': 'symbol is required'}, status=400)
    if not start_date or not end_date:
        return JsonResponse({'error': 'start_date and end_date are required'}, status=400)

    try:
        result = services.run_backtest(
            strategy_name=strategy_name,
            symbol=symbol,
            timeframe=timeframe,
            start_date=start_date,
            end_date=end_date,
            initial_cash=initial_cash,
            params=params,
        )
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def stock_selection(request):
    """Stock selection page: all strategies for screening + K-line charts."""
    import sys, io
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        strategies = services.get_strategy_list()
        stocks = services.get_available_stocks('daily')
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

    # Only include strategies that loaded successfully
    loaded_strategies = [s for s in strategies if s.get('status') == 'loaded']

    context = {
        'strategies': loaded_strategies,
        'stocks': stocks,
    }
    return render(request, 'dashboard/stock_selection.html', context)


def api_stock_list(request):
    """Return JSON list of available stocks (for autocomplete)."""
    try:
        stocks = services.get_available_stocks()
        # Normalise to a flat list of symbol strings
        if isinstance(stocks, dict):
            # Flatten dict of {timeframe: [symbols]} into unique sorted list
            symbol_set = set()
            for symbols in stocks.values():
                if isinstance(symbols, list):
                    symbol_set.update(symbols)
            stocks = sorted(symbol_set)
        return JsonResponse({'stocks': stocks})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def api_strategy_list(request):
    """Return JSON list of strategies (for dropdowns)."""
    try:
        strategies = services.get_strategy_list()
        # Return only the fields needed for a dropdown
        strategy_names = [
            {
                'name': s.get('name'),
                'status': s.get('status'),
                'class_name': s.get('class_name'),
            }
            for s in strategies
        ]
        return JsonResponse({'strategies': strategy_names})
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(['POST'])
def api_stock_kline(request):
    """Return OHLCV + indicators for a single stock for K-line charting."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    symbol = data.get('symbol')
    frequency = data.get('frequency', 'daily')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    limit = int(data.get('limit', 200))

    if not symbol:
        return JsonResponse({'error': 'symbol is required'}, status=400)

    result = services.get_stock_kline_data(symbol, frequency, start_date, end_date, limit)
    if 'error' in result:
        return JsonResponse(result, status=404)
    return JsonResponse(result)


@csrf_exempt
@require_http_methods(['POST'])
def api_stock_screen(request):
    """Run a strategy across multiple stocks and return screening results."""
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    strategy_name = data.get('strategy_name')
    symbols = data.get('symbols', [])
    frequency = data.get('frequency', 'daily')
    start_date = data.get('start_date')
    end_date = data.get('end_date')
    params = data.get('params', {})
    cross_screen = data.get('cross_screen', False)

    if not strategy_name:
        return JsonResponse({'error': 'strategy_name is required'}, status=400)
    if not symbols:
        # Default: all available daily stocks
        symbols = services.get_available_stocks(frequency)

    if cross_screen:
        # Cross-screen: scan all stocks with all strategies
        results = services.run_cross_screening(symbols=symbols, frequency=frequency,
                                                start_date=start_date, end_date=end_date)
        return JsonResponse({'results': results})

    results = services.run_stock_screening(
        strategy_name=strategy_name,
        symbols=symbols,
        frequency=frequency,
        start_date=start_date,
        end_date=end_date,
        params=params,
    )
    # Filter out hold signals
    results = [r for r in results if r.get('latest_signal') != 'hold']
    return JsonResponse({'results': results})
