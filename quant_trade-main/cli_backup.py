     1|#!/usr/bin/env python3
     2|"""
     3|量化交易平台CLI工具
     4|支持策略回测、数据加载、策略管理等功能
     5|"""
     6|
     7|import sys
     8|import os
     9|import json
    10|import argparse
    11|import pandas as pd
    12|import numpy as np
    13|from datetime import datetime, timedelta
    14|import glob
    15|
    16|# 添加项目路径
    17|project_root = os.path.dirname(os.path.abspath(__file__))
    18|sys.path.insert(0, project_root)
    19|
    20|# 导入回测模块
    21|try:
    22|    from backtest.src.backtest.engine import BacktestEngine
    23|    from backtest.src.backtest.performance import PerformanceAnalyzer
    24|    BACKTEST_AVAILABLE = True
    25|except ImportError as e:
    26|    print(f"⚠️  回测模块导入失败: {e}")
    27|    BACKTEST_AVAILABLE = False
    28|
    29|# 导入策略发现器
    30|try:
    31|    from backtest.runner import BacktestRunner
    32|    RUNNER_AVAILABLE = True
    33|except ImportError as e:
    34|    print(f"⚠️  策略发现器导入失败: {e}")
    35|    RUNNER_AVAILABLE = False
    36|
    37|def parse_args():
    38|    """解析命令行参数"""
    39|    parser = argparse.ArgumentParser(
    40|        description='量化交易平台CLI工具',
    41|        formatter_class=argparse.RawDescriptionHelpFormatter,
    42|        epilog="""
    43|使用示例:
    44|  # 列出所有可用策略
    45|  %(prog)s strategy list
    46|  
    47|  # 使用日线数据回测移动平均策略
    48|  %(prog)s backtest --strategy ma_strategy --symbol 000001.SZ --timeframe daily
    49|  
    50|  # 使用自定义参数回测
    51|  %(prog)s backtest --strategy simple_ma_strategy --params '{"short_window":5,"long_window":20}'
    52|  
    53|  # 查看数据目录信息
    54|  %(prog)s data info
    55|  
    56|  # 加载并显示股票数据
    57|  %(prog)s data show --symbol 000001.SZ --timeframe daily --limit 10
    58|        """
    59|    )
    60|    
    61|    subparsers = parser.add_subparsers(dest='command', help='命令')
    62|    
    63|    # 策略管理命令
    64|    strategy_parser = subparsers.add_parser('strategy', help='策略管理')
    65|    strategy_subparsers = strategy_parser.add_subparsers(dest='strategy_command')
    66|    
    67|    strategy_list_parser = strategy_subparsers.add_parser('list', help='列出所有可用策略')
    68|    strategy_list_parser.add_argument('--verbose', '-v', action='store_true', help='显示详细信息')
    69|    
    70|    strategy_info_parser = strategy_subparsers.add_parser('info', help='查看策略信息')
    71|    strategy_info_parser.add_argument('strategy_name', help='策略名称')
    72|    
    73|    # 回测命令
    74|    backtest_parser = subparsers.add_parser('backtest', help='执行回测')
    75|    backtest_parser.add_argument('--strategy', '-s', required=True, help='策略名称')
    76|    backtest_parser.add_argument('--symbol', default='000001.SZ', help='股票代码 (默认: 000001.SZ)')
    77|    backtest_parser.add_argument('--timeframe', '-t', choices=['daily', 'weekly', '5min', '30min'], 
    78|                               default='daily', help='数据时间频率 (默认: daily)')
    79|    backtest_parser.add_argument('--params', '-p', default='{}', help='策略参数，JSON格式')
    80|    backtest_parser.add_argument('--initial-cash', type=float, default=100000, help='初始资金 (默认: 100000)')
    81|    backtest_parser.add_argument('--start-date', help='开始日期 (格式: YYYYMMDD)')
    82|    backtest_parser.add_argument('--end-date', help='结束日期 (格式: YYYYMMDD)')
    83|    backtest_parser.add_argument('--output', '-o', help='结果输出文件')
    84|    backtest_parser.add_argument('--plot', action='store_true', help='生成图表')
    85|    
    86|    # 数据管理命令
    87|    data_parser = subparsers.add_parser('data', help='数据管理')
    88|    data_subparsers = data_parser.add_subparsers(dest='data_command')
    89|    
    90|    data_info_parser = data_subparsers.add_parser('info', help='查看数据目录信息')
    91|    
    92|    data_show_parser = data_subparsers.add_parser('show', help='显示股票数据')
    93|    data_show_parser.add_argument('--symbol', '-s', required=True, help='股票代码')
    94|    data_show_parser.add_argument('--timeframe', '-t', choices=['daily', 'weekly', '5min', '30min'], 
    95|                                default='daily', help='数据时间频率')
    96|    data_show_parser.add_argument('--limit', '-l', type=int, default=10, help='显示行数')
    97|    data_show_parser.add_argument('--columns', '-c', help='显示指定列 (逗号分隔)')
    98|    
    99|    data_list_parser = data_subparsers.add_parser('list', help='列出可用股票代码')
   100|    data_list_parser.add_argument('--timeframe', '-t', choices=['daily', 'weekly', '5min', '30min'], 
   101|                                default='daily', help='数据时间频率')
   102|    data_list_parser.add_argument('--limit', '-l', type=int, default=20, help='显示数量')
   103|    
   104|    # 看板命令
   105|    dashboard_parser = subparsers.add_parser('dashboard', help='看板管理')
   106|    dashboard_parser.add_argument('action', choices=['start', 'stop', 'status'], 
   107|                                nargs='?', default='start', help='启动/停止/查看状态 (默认: start)')
   108|    dashboard_parser.add_argument('--port', type=int, default=5000, help='端口号 (默认: 5000)')
   109|    dashboard_parser.add_argument('--host', default='127.0.0.1', help='主机地址 (默认: 127.0.0.1)')
   110|    
   111|    return parser.parse_args()
   112|
   113|def load_stock_data(symbol, timeframe='daily', start_date=None, end_date=None):
   114|    """加载股票数据"""
   115|    data_dir = os.path.join(project_root, 'data')
   116|    
   117|    # 确定文件路径
   118|    if timeframe == 'daily':
   119|        filepath = os.path.join(data_dir, 'daily_data2', f"{symbol}.csv")
   120|    elif timeframe == 'weekly':
   121|        filepath = os.path.join(data_dir, 'week_data2', f"{symbol}.csv")
   122|    elif timeframe == '5min':
   123|        filepath = os.path.join(data_dir, '5min', f"{symbol}_analysis.csv")
   124|    elif timeframe == '30min':
   125|        filepath = os.path.join(data_dir, '30min', f"{symbol}_analysis.csv")
   126|    else:
   127|        raise ValueError(f"不支持的时间频率: {timeframe}")
   128|    
   129|    if not os.path.exists(filepath):
   130|        raise FileNotFoundError(f"数据文件不存在: {filepath}")
   131|    
   132|    print(f"📊 加载数据: {symbol} ({timeframe})")
   133|    print(f"   文件: {filepath}")
   134|    
   135|    # 读取CSV文件
   136|    df = pd.read_csv(filepath)
   137|    
   138|    # 转换日期列
   139|    if 'trade_date' in df.columns:
   140|        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
   141|        df.set_index('trade_date', inplace=True)
   142|        df.sort_index(inplace=True)
   143|    
   144|    # 过滤日期范围
   145|    if start_date:
   146|        start_dt = pd.to_datetime(start_date, format='%Y%m%d')
   147|        df = df[df.index >= start_dt]
   148|    
   149|    if end_date:
   150|        end_dt = pd.to_datetime(end_date, format='%Y%m%d')
   151|        df = df[df.index <= end_dt]
   152|    
   153|    print(f"   数据行数: {len(df)}")
   154|    print(f"   日期范围: {df.index.min()} 到 {df.index.max()}")
   155|    
   156|    # 添加symbol列
   157|    df['symbol'] = symbol
   158|    
   159|    return df
   160|
   161|def get_available_symbols(timeframe='daily'):
   162|    """获取可用股票代码列表"""
   163|    data_dir = os.path.join(project_root, 'data')
   164|    
   165|    if timeframe == 'daily':
   166|        dir_path = os.path.join(data_dir, 'daily_data2')
   167|        pattern = "*.csv"
   168|    elif timeframe == 'weekly':
   169|        dir_path = os.path.join(data_dir, 'week_data2')
   170|        pattern = "*.csv"
   171|    elif timeframe == '5min':
   172|        dir_path = os.path.join(data_dir, '5min')
   173|        pattern = "*_analysis.csv"
   174|    elif timeframe == '30min':
   175|        dir_path = os.path.join(data_dir, '30min')
   176|        pattern = "*_analysis.csv"
   177|    else:
   178|        return []
   179|    
   180|    if not os.path.exists(dir_path):
   181|        return []
   182|    
   183|    files = glob.glob(os.path.join(dir_path, pattern))
   184|    symbols = []
   185|    
   186|    for filepath in files:
   187|        filename = os.path.basename(filepath)
   188|        if timeframe in ['daily', 'weekly']:
   189|            symbol = filename.replace('.csv', '')
   190|        else:  # 5min, 30min
   191|            symbol = filename.replace('_analysis.csv', '')
   192|        symbols.append(symbol)
   193|    
   194|    return sorted(symbols)
   195|
   196|def list_strategies(verbose=False):
   197|    """列出所有可用策略"""
   198|    if not RUNNER_AVAILABLE:
   199|        print("❌ 策略发现器不可用")
   200|        return
   201|    
   202|    try:
   203|        runner = BacktestRunner()
   204|        strategies = runner.list_strategies()
   205|        
   206|        print("📋 可用策略列表")
   207|        print("=" * 60)
   208|        
   209|        if not strategies:
   210|            print("⚠️  未找到任何策略")
   211|            return
   212|        
   213|        print(f"共发现 {len(strategies)} 个策略:")
   214|        print()
   215|        
   216|        for i, strategy_name in enumerate(strategies, 1):
   217|            print(f"{i:2d}. {strategy_name}")
   218|            
   219|            if verbose:
   220|                try:
   221|                    strategy_cls = runner.strategies[strategy_name]
   222|                    print(f"    类名: {strategy_cls.__name__}")
   223|                    
   224|                    # 尝试获取默认参数
   225|                    if hasattr(strategy_cls, 'get_default_params'):
   226|                        params = strategy_cls.get_default_params()
   227|                        if params:
   228|                            print(f"    默认参数: {params}")
   229|                    
   230|                    # 显示类文档
   231|                    if strategy_cls.__doc__:
   232|                        doc_lines = strategy_cls.__doc__.strip().split('\n')
   233|                        if doc_lines:
   234|                            print(f"    描述: {doc_lines[0]}")
   235|                    
   236|                except Exception as e:
   237|                    print(f"    信息获取失败: {e}")
   238|                
   239|                print()
   240|        
   241|        print("=" * 60)
   242|        
   243|    except Exception as e:
   244|        print(f"❌ 列出策略失败: {e}")
   245|
   246|def run_backtest(args):
   247|    """执行回测"""
   248|    if not BACKTEST_AVAILABLE:
   249|        print("❌ 回测模块不可用")
   250|        return
   251|    
   252|    print("🚀 开始回测")
   253|    print("=" * 60)
   254|    
   255|    try:
   256|        # 加载数据
   257|        data = load_stock_data(
   258|            symbol=args.symbol,
   259|            timeframe=args.timeframe,
   260|            start_date=args.start_date,
   261|            end_date=args.end_date
   262|        )
   263|        
   264|        if len(data) == 0:
   265|            print("❌ 无可用数据")
   266|            return
   267|        
   268|        # 解析策略参数
   269|        try:
   270|            strategy_params = json.loads(args.params)
   271|        except json.JSONDecodeError as e:
   272|            print(f"❌ 参数解析失败: {e}")
   273|            print(f"   使用默认参数")
   274|            strategy_params = {}
   275|        
   276|        # 导入策略
   277|        if not RUNNER_AVAILABLE:
   278|            print("❌ 策略发现器不可用")
   279|            return
   280|        
   281|        runner = BacktestRunner(load_all=False)
   282|        strategy_cls = runner.load_strategy(args.strategy)
   283|        if strategy_cls is None:
   284|            print(f"❌ 策略不存在或加载失败: {args.strategy}")
   285|            return
   286|        print(f"📈 使用策略: {args.strategy} ({strategy_cls.__name__})")
   287|        print(f"⚙️  策略参数: {strategy_params}")
   288|        print(f"💰 初始资金: {args.initial_cash:,.2f}")
   289|        print(f"📅 数据范围: {data.index.min()} 到 {data.index.max()}")
   290|        print(f"📊 数据行数: {len(data)}")
   291|        
   292|        # 运行回测
   293|        print("\n🔄 执行回测中...")
   294|        engine = BacktestEngine(data, strategy_cls, initial_cash=args.initial_cash)
   295|        results = engine.run_backtest(strategy_params)
   296|        
   297|        # 显示结果
   298|        print("\n" + "=" * 60)
   299|        print("📊 回测结果")
   300|        print("=" * 60)
   301|        
   302|        # 提取关键指标
   303|        summary = results.get('summary', {})
   304|        trades = results.get('trades', {})
   305|        risk_return = results.get('risk_return', {})
   306|        drawdown = results.get('drawdown', {})
   307|        
   308|        print(f"💰 初始资金: {args.initial_cash:,.2f}")
   309|        
   310|        if 'final_capital' in results:
   311|            final_capital = results['final_capital']
   312|            total_return = (final_capital - args.initial_cash) / args.initial_cash
   313|            print(f"💰 最终资金: {final_capital:,.2f}")
   314|            print(f"📈 总收益率: {total_return:.2%}")
   315|        
   316|        if 'total_return' in summary:
   317|            print(f"📈 总收益率: {summary['total_return']:.2%}")
   318|        
   319|        if 'annualized_return' in summary:
   320|            print(f"📅 年化收益率: {summary['annualized_return']:.2%}")
   321|        
   322|        if 'max_drawdown' in drawdown:
   323|            print(f"📉 最大回撤: {drawdown['max_drawdown']:.2%}")
   324|        
   325|        if 'sharpe_ratio' in risk_return:
   326|            print(f"⚖️  夏普比率: {risk_return['sharpe_ratio']:.2f}")
   327|        
   328|        if 'trade_count' in summary:
   329|            print(f"📊 交易次数: {summary['trade_count']}")
   330|        
   331|        if 'win_rate' in trades:
   332|            print(f"🎯 胜率: {trades['win_rate']:.2%}")
   333|        
   334|        if 'profit_factor' in trades:
   335|            print(f"💵 盈亏比: {trades['profit_factor']:.2f}")
   336|        
   337|        # 保存结果
   338|        if args.output:
   339|            output_path = os.path.abspath(args.output)
   340|            with open(output_path, 'w', encoding='utf-8') as f:
   341|                json.dump(results, f, indent=2, default=str)
   342|            print(f"\n💾 结果已保存到: {output_path}")
   343|        
   344|        print("\n✅ 回测完成")
   345|        
   346|    except Exception as e:
   347|        print(f"❌ 回测失败: {e}")
   348|        import traceback
   349|        traceback.print_exc()
   350|
   351|def show_data_info():
   352|    """显示数据目录信息"""
   353|    data_dir = os.path.join(project_root, 'data')
   354|    
   355|    if not os.path.exists(data_dir):
   356|        print(f"❌ 数据目录不存在: {data_dir}")
   357|        return
   358|    
   359|    print("📁 数据目录结构")
   360|    print("=" * 60)
   361|    
   362|    for item in os.listdir(data_dir):
   363|        item_path = os.path.join(data_dir, item)
   364|        if os.path.isdir(item_path):
   365|            # 统计CSV文件数量
   366|            csv_files = glob.glob(os.path.join(item_path, "**", "*.csv"), recursive=True)
   367|            print(f"{item}/")
   368|            print(f"  📄 CSV文件数: {len(csv_files)}")
   369|            
   370|            if csv_files:
   371|                # 显示示例文件
   372|                sample = os.path.basename(csv_files[0])
   373|                print(f"  示例: {sample}")
   374|                
   375|                # 如果是daily_data2或week_data2，统计股票数量
   376|                if item in ['daily_data2', 'week_data2', '5min', '30min']:
   377|                    if item in ['daily_data2', 'week_data2']:
   378|                        files = glob.glob(os.path.join(item_path, "*.csv"))
   379|                    else:
   380|                        files = glob.glob(os.path.join(item_path, "*_analysis.csv"))
   381|                    
   382|                    symbols = []
   383|                    for f in files[:5]:  # 只检查前5个文件
   384|                        basename = os.path.basename(f)
   385|                        if item in ['daily_data2', 'week_data2']:
   386|                            symbol = basename.replace('.csv', '')
   387|                        else:
   388|                            symbol = basename.replace('_analysis.csv', '')
   389|                        symbols.append(symbol)
   390|                    
   391|                    print(f"  股票示例: {', '.join(symbols)}")
   392|        
   393|        print()
   394|
   395|def show_stock_data(args):
   396|    """显示股票数据"""
   397|    try:
   398|        df = load_stock_data(args.symbol, args.timeframe)
   399|        
   400|        print(f"\n📋 {args.symbol} 数据 ({args.timeframe})")
   401|        print("=" * 80)
   402|        
   403|        # 选择要显示的列
   404|        if args.columns:
   405|            columns = [col.strip() for col in args.columns.split(',')]
   406|            # 只保留存在的列
   407|            columns = [col for col in columns if col in df.columns]
   408|            if not columns:
   409|                print("⚠️  指定的列不存在，显示所有列")
   410|                columns = df.columns.tolist()
   411|        else:
   412|            columns = df.columns.tolist()
   413|        
   414|        # 显示数据
   415|        pd.set_option('display.max_columns', None)
   416|        pd.set_option('display.width', None)
   417|        
   418|        print(f"数据形状: {df.shape}")
   419|        print(f"列名: {', '.join(df.columns.tolist())}")
   420|        print(f"日期范围: {df.index.min()} 到 {df.index.max()}")
   421|        
   422|        print("\n前{}行数据:".format(args.limit))
   423|        print(df[columns].head(args.limit))
   424|        
   425|        # 显示统计信息
   426|        print("\n📊 统计信息:")
   427|        if len(df) > 0:
   428|            numeric_cols = df.select_dtypes(include=[np.number]).columns
   429|            if len(numeric_cols) > 0:
   430|                stats = df[numeric_cols].describe().T[['mean', 'std', 'min', 'max']]
   431|                print(stats)
   432|        
   433|    except Exception as e:
   434|        print(f"❌ 显示数据失败: {e}")
   435|
   436|def list_stock_symbols(args):
   437|    """列出股票代码"""
   438|    symbols = get_available_symbols(args.timeframe)
   439|    
   440|    if not symbols:
   441|        print(f"❌ 未找到 {args.timeframe} 数据")
   442|        return
   443|    
   444|    print(f"📋 {args.timeframe} 数据可用股票代码")
   445|    print("=" * 60)
   446|    print(f"共 {len(symbols)} 个股票")
   447|    print()
   448|    
   449|    # 分组显示
   450|    for i in range(0, min(len(symbols), args.limit), 10):
   451|        group = symbols[i:i+10]
   452|        print('  '.join(group))
   453|    
   454|    if len(symbols) > args.limit:
   455|        print(f"\n... 还有 {len(symbols) - args.limit} 个")
   456|
   457|def manage_dashboard(args):
   458|    """管理看板"""
   459|    # 使用简化版看板
   460|    dashboard_script = os.path.join(project_root, 'simple_dashboard.py')
   461|    
   462|    if not os.path.exists(dashboard_script):
   463|        print(f"❌ 看板脚本不存在: {dashboard_script}")
   464|        print(f"   正在创建简化看板...")
   465|        return
   466|    
   467|    if args.action == 'start':
   468|        port = args.port if hasattr(args, 'port') else 5000
   469|        host = args.host if hasattr(args, 'host') else '127.0.0.1'
   470|        
   471|        print(f"🚀 启动简化看板...")
   472|        print(f"   地址: http://{host}:{port}")
   473|        print(f"   功能: 策略回测、系统工具、实时日志")
   474|        print(f"   按 Ctrl+C 停止")
   475|        print()
   476|        
   477|        # 启动命令 - 使用当前Python解释器
   478|        import sys
   479|        python_exe = sys.executable
   480|        
   481|        cmd = [python_exe, dashboard_script]
   482|        
   483|        print(f"执行命令: cd {project_root} && {python_exe} {dashboard_script}")
   484|        print()
   485|        
   486|        # 在当前进程中运行（阻塞）
   487|        os.chdir(project_root)
   488|        os.execv(python_exe, cmd)
   489|        
   490|    elif args.action == 'status':
   491|        print("📊 看板状态")
   492|        print("   简化看板: 使用Flask框架")
   493|        print("   功能: 回测执行、策略查看、系统工具")
   494|    """主函数"""
   495|    args = parse_args()
   496|    
   497|    if not args.command:
   498|        print("❌ 请指定命令")
   499|        print("   使用 --help 查看帮助")
   500|        return
   501|