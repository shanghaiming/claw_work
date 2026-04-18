#!/usr/bin/env python3
"""
QuantTrade 量化交易平台 - CLI工具
统一命令行接口，支持策略管理、回测执行、数据查看和看板启动
"""
import os
import sys
import argparse
import subprocess

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)


def parse_args():
    parser = argparse.ArgumentParser(description='QuantTrade 量化交易平台 CLI')
    subparsers = parser.add_subparsers(dest='command', help='命令')

    # 策略命令
    strategy_parser = subparsers.add_parser('strategy', help='策略管理')
    strategy_subparsers = strategy_parser.add_subparsers(dest='strategy_command')
    strategy_subparsers.add_parser('list', help='列出所有策略').add_argument('--verbose', action='store_true')
    info_parser = strategy_subparsers.add_parser('info', help='查看策略信息')
    info_parser.add_argument('strategy_name', help='策略名称')

    # 回测命令
    bt_parser = subparsers.add_parser('backtest', help='执行策略回测')
    bt_parser.add_argument('--strategy', required=True, help='策略名称')
    bt_parser.add_argument('--symbol', default='000001.SZ', help='股票代码')
    bt_parser.add_argument('--timeframe', default='daily', choices=['daily', 'weekly', '5min', '30min'])
    bt_parser.add_argument('--start-date', default=None, help='开始日期 (YYYYMMDD)')
    bt_parser.add_argument('--end-date', default=None, help='结束日期 (YYYYMMDD)')
    bt_parser.add_argument('--initial-cash', type=float, default=100000, help='初始资金')

    # 数据命令
    data_parser = subparsers.add_parser('data', help='数据管理')
    data_subparsers = data_parser.add_subparsers(dest='data_command')
    data_subparsers.add_parser('info', help='显示数据信息')
    show_parser = data_subparsers.add_parser('show', help='显示股票数据')
    show_parser.add_argument('symbol', help='股票代码')
    show_parser.add_argument('--timeframe', default='daily')
    list_data_parser = data_subparsers.add_parser('list', help='列出所有股票代码')
    list_data_parser.add_argument('--limit', type=int, default=20)

    # 选股命令
    select_parser = subparsers.add_parser('select', help='执行选股')
    select_parser.add_argument('--strategy-id', type=int, default=1, choices=[1, 2, 3, 4, 5])
    select_parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text')
    select_parser.add_argument('--limit', type=int, default=20)

    # 看板命令
    dashboard_parser = subparsers.add_parser('dashboard', help='启动 Django 看板')
    dashboard_parser.add_argument('action', nargs='?', default='start', choices=['start'])
    dashboard_parser.add_argument('--port', type=int, default=8080)
    dashboard_parser.add_argument('--host', default='127.0.0.1')

    return parser.parse_args()


def list_strategies(verbose=False):
    """列出所有策略"""
    import io
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        from core.runner import BacktestRunner
        runner = BacktestRunner()
        strategies = runner.load_all_strategies()
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr

    print(f"策略库 ({len(strategies)} 个)")
    print("=" * 50)
    for i, name in enumerate(sorted(strategies.keys()), 1):
        cls = strategies[name]
        desc = getattr(cls, 'strategy_description', '') or ''
        cat = getattr(cls, 'strategy_category', 'general')
        if verbose:
            print(f"  {i:3d}. {name} ({cls.__name__}) [{cat}]")
            if desc:
                print(f"       {desc}")
        else:
            print(f"  {i:3d}. {name}")
    print("=" * 50)


def run_backtest(args):
    """执行回测"""
    import io
    from core.data_loader import load_stock_data
    from core.runner import BacktestRunner

    print(f"执行回测")
    print(f"  策略: {args.strategy}")
    print(f"  股票: {args.symbol}")
    print(f"  周期: {args.timeframe}")
    print(f"  初始资金: {args.initial_cash:,.0f}")
    print()

    # 加载数据
    data = load_stock_data(
        symbol=args.symbol,
        frequency=args.timeframe,
        start_date=args.start_date,
        end_date=args.end_date
    )
    if data is None or data.empty:
        print(f"数据加载失败: {args.symbol}")
        return
    data['symbol'] = args.symbol
    print(f"数据加载成功: {len(data)} 行")

    # 运行回测
    runner = BacktestRunner()
    results = runner.run(args.strategy, data, {'initial_cash': args.initial_cash})

    if results and 'error' not in results:
        print()
        print("=" * 60)
        print("回测绩效报告")
        print("=" * 60)
        if 'summary' in results:
            s = results['summary']
            print(f"总收益率: {s.get('total_return', 0):.2%}")
            print(f"年化收益率: {s.get('annualized_return', 0):.2%}")
        if 'drawdown' in results:
            print(f"最大回撤: {results['drawdown'].get('max_drawdown', 0):.2%}")
        if 'risk_return' in results:
            rr = results['risk_return']
            print(f"夏普比率: {rr.get('sharpe_ratio', 0):.2f}")
            print(f"索提诺比率: {rr.get('sortino_ratio', 0):.2f}")
        if 'trades' in results:
            t = results['trades']
            print(f"胜率: {t.get('win_rate', 0):.2%}")
            print(f"盈亏比: {t.get('profit_factor', 0):.2f}")
        if 'trades_list' in results:
            print(f"交易笔数: {len(results['trades_list'])}")
        if 'equity_curve' in results:
            ec = results['equity_curve']
            if hasattr(ec, 'iloc'):
                print(f"最终净值: {ec.iloc[-1]:,.2f}")
        print("=" * 60)
    elif results and 'error' in results:
        print(f"回测失败: {results['error']}")
    else:
        print("回测失败")


def show_data_info():
    """显示数据信息"""
    from core.data_loader import list_available_symbols
    print("数据信息")
    print("=" * 50)
    for tf in ['daily', 'weekly', '5min', '30min']:
        try:
            symbols = list_available_symbols(tf)
            print(f"  {tf}: {len(symbols)} 只股票")
        except Exception:
            print(f"  {tf}: 无数据")
    print("=" * 50)


def show_stock_data(args):
    """显示股票数据"""
    from core.data_loader import load_stock_data
    data = load_stock_data(args.symbol, timeframe=args.timeframe)
    if data is not None and not data.empty:
        print(f"数据: {args.symbol} ({args.timeframe}), {len(data)} 行")
        print(data.tail(10).to_string())
    else:
        print(f"数据加载失败: {args.symbol}")


def list_stock_symbols(args):
    """列出所有股票代码"""
    from core.data_loader import list_available_symbols
    symbols = list_available_symbols('daily')
    print(f"可用股票代码 ({len(symbols)} 个)")
    for i, s in enumerate(symbols[:args.limit], 1):
        print(f"  {i:3d}. {s}")
    if len(symbols) > args.limit:
        print(f"  ... 还有 {len(symbols) - args.limit} 个")


def manage_dashboard(args):
    """启动 Django 看板"""
    host = getattr(args, 'host', '127.0.0.1')
    port = getattr(args, 'port', 8080)
    print(f"启动 Django 量化看板: http://{host}:{port}")
    print("按 Ctrl+C 停止")
    print()
    cmd = [sys.executable, 'manage.py', 'runserver', f'{host}:{port}']
    subprocess.run(cmd, cwd=project_root)


def main():
    args = parse_args()
    if not args.command:
        print("请指定命令，使用 --help 查看帮助")
        return

    try:
        if args.command == 'strategy':
            if args.strategy_command == 'list':
                list_strategies(args.verbose)
            elif args.strategy_command == 'info':
                print(f"策略信息: {args.strategy_name}")
        elif args.command == 'backtest':
            run_backtest(args)
        elif args.command == 'data':
            if args.data_command == 'info':
                show_data_info()
            elif args.data_command == 'show':
                show_stock_data(args)
            elif args.data_command == 'list':
                list_stock_symbols(args)
        elif args.command == 'dashboard':
            manage_dashboard(args)
        elif args.command == 'select':
            print("选股功能请使用看板: python cli.py dashboard")
    except KeyboardInterrupt:
        print("\n用户中断")
    except Exception as e:
        print(f"执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
