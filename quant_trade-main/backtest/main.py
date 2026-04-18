import sys
import os
import json
import argparse
import talib
import glob
import pandas as pd
import numpy as np

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

# 导入回测引擎和性能分析器
from backtest.src.backtest.engine import BacktestEngine
from backtest.src.backtest.performance import PerformanceAnalyzer
try:
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    MATPLOTLIB_AVAILABLE = False
    print("警告: matplotlib不可用，可视化功能将禁用")
from backtest.src.utils.visualizer import Visualizer
from backtest.src.backtest.optimization import ParameterOptimizer

# 设置中文字体
if MATPLOTLIB_AVAILABLE:
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 设置默认字体为黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 导入策略发现器
sys.path.append(os.path.join(current_dir, '..'))
from .runner import BacktestRunner

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='股票回测系统')
    parser.add_argument(
        '--refresh', 
        action='store_true',
        help='全量更新模式：强制重新预处理数据并训练模型（默认加载已有数据及模型）'
    )
    parser.add_argument(
        '--strategy',
        type=str,
        default='simple_ma_strategy',
        help='选择回测策略（默认: simple_ma_strategy），使用--list-strategies查看所有可用策略'
    )
    parser.add_argument(
        '--strategy-params',
        type=str,
        default='{}',
        help='策略参数，JSON格式（例如：\'{"short_window":5, "long_window":20}\'）'
    )
    parser.add_argument(
        '--list-strategies',
        action='store_true',
        help='列出所有可用策略并退出'
    )
    parser.add_argument(
        '--symbol',
        type=str,
        default=None,
        help='股票代码（例如：000001.SZ），如果未指定则使用所有股票'
    )
    parser.add_argument(
        '--timeframe',
        type=str,
        choices=['daily', 'weekly', '5min', '30min'],
        default='daily',
        help='数据时间频率（默认: daily）'
    )
    parser.add_argument(
        '--start-date',
        type=str,
        help='开始日期（格式: YYYYMMDD）'
    )
    parser.add_argument(
        '--end-date',
        type=str,
        help='结束日期（格式: YYYYMMDD）'
    )
    parser.add_argument(
        '--limit-stocks',
        type=int,
        default=None,
        help='限制股票数量（用于测试）'
    )
    parser.add_argument(
        '--initial-cash',
        type=float,
        default=100000,
        help='初始资金（默认: 100000）'
    )
    return parser.parse_args()

def load_stock_data(symbol='000001.SZ', timeframe='daily', start_date=None, end_date=None):
    """加载指定股票的完整数据"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 根据时间频率确定文件路径
    if timeframe == 'daily':
        file_path = os.path.join(base_dir, "data", "daily_data2", f"{symbol}.csv")
    elif timeframe == 'weekly':
        file_path = os.path.join(base_dir, "data", "week_data2", f"{symbol}.csv")
    elif timeframe == '5min':
        file_path = os.path.join(base_dir, "data", "5min", f"{symbol}_analysis.csv")
    elif timeframe == '30min':
        file_path = os.path.join(base_dir, "data", "30min", f"{symbol}_analysis.csv")
    else:
        raise ValueError(f"不支持的时间频率: {timeframe}")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    print(f"加载数据: {symbol} ({timeframe})")
    print(f"文件: {file_path}")
    
    # 读取数据
    df = pd.read_csv(file_path)
    
    # 转换日期列
    if 'trade_date' in df.columns:
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.set_index('trade_date', inplace=True)
        df.sort_index(inplace=True)
    
    # 过滤日期范围
    if start_date:
        start_dt = pd.to_datetime(start_date, format='%Y%m%d')
        df = df[df.index >= start_dt]
    
    if end_date:
        end_dt = pd.to_datetime(end_date, format='%Y%m%d')
        df = df[df.index <= end_dt]
    
    # 添加symbol列
    df['symbol'] = symbol
    
    print(f"数据行数: {len(df)}")
    print(f"日期范围: {df.index.min()} 到 {df.index.max()}")
    
    return df

def load_all_stock_data(timeframe='daily', limit=None):
    """直接遍历指定路径下的所有CSV文件并合并"""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # 根据时间频率确定目录
    if timeframe == 'daily':
        target_dir = os.path.join(base_dir, "data", "daily_data2")
        file_pattern = os.path.join(target_dir, "*.csv")
    elif timeframe == 'weekly':
        target_dir = os.path.join(base_dir, "data", "week_data2")
        file_pattern = os.path.join(target_dir, "*.csv")
    elif timeframe == '5min':
        target_dir = os.path.join(base_dir, "data", "5min")
        file_pattern = os.path.join(target_dir, "*_analysis.csv")
    elif timeframe == '30min':
        target_dir = os.path.join(base_dir, "data", "30min")
        file_pattern = os.path.join(target_dir, "*_analysis.csv")
    else:
        raise ValueError(f"不支持的时间频率: {timeframe}")
    
    # 获取所有CSV文件
    matched_files = glob.glob(file_pattern)
    
    if not matched_files:
        raise FileNotFoundError(f"目录 {target_dir} 下没有找到任何CSV文件")
    
    print(f"找到 {len(matched_files)} 个{timeframe}数据文件")
    
    all_data = []
    files_processed = 0
    
    for file_path in matched_files:
        if limit and files_processed >= limit:
            break
            
        try:
            # 从文件名提取股票代码
            filename = os.path.basename(file_path)
            if timeframe in ['daily', 'weekly']:
                file_symbol = filename.replace('.csv', '')
            else:  # 5min, 30min
                file_symbol = filename.replace('_analysis.csv', '')
            
            # 读取单个文件
            df_single = pd.read_csv(file_path)
            
            # 转换日期列
            if 'trade_date' in df_single.columns:
                df_single['trade_date'] = pd.to_datetime(df_single['trade_date'], format='%Y%m%d')
                df_single.set_index('trade_date', inplace=True)
                df_single.sort_index(inplace=True)
            
            # 检查必要列是否存在
            required_columns = {'open', 'high', 'low', 'close'}
            missing = required_columns - set(df_single.columns)
            if missing:
                print(f"警告: 文件 {filename} 缺少列 {missing}，跳过")
                continue
            
            # 添加股票代码列
            df_single['symbol'] = file_symbol
            all_data.append(df_single)
            files_processed += 1
            
            if files_processed <= 5:  # 只显示前5个文件的信息
                print(f"成功加载: {filename} -> {file_symbol}, 数据行数: {len(df_single)}")
            
        except Exception as e:
            print(f"警告: 加载文件 {file_path} 失败: {e}")
            continue
    
    if not all_data:
        raise ValueError(f"所有{timeframe}数据文件加载失败")
    
    # 合并所有数据
    combined_data = pd.concat(all_data, ignore_index=False)
    combined_data = combined_data.sort_index()
    
    # 获取清理后的股票代码列表
    symbols_clean = combined_data['symbol'].unique().tolist()
    
    print(f"\n合并后总数据行数: {len(combined_data)}")
    print(f"包含股票数量: {len(symbols_clean)}")
    if len(symbols_clean) <= 10:
        print(f"股票列表: {symbols_clean}")
    else:
        print(f"股票列表 (前10个): {symbols_clean[:10]} ...")
    
    return combined_data
def get_strategy_class(strategy_name):
    """根据策略名称获取策略类"""
    runner = BacktestRunner()
    strategies = runner.strategies
    if strategy_name not in strategies:
        # 尝试查找大小写不匹配
        for key in strategies.keys():
            if key.lower() == strategy_name.lower():
                return strategies[key]
        raise ValueError(f"策略 '{strategy_name}' 不存在。可用策略: {list(strategies.keys())}")
    return strategies[strategy_name]

def main():
    args = parse_args()
    
    # 列出所有策略
    if args.list_strategies:
        runner = BacktestRunner()
        strategies = runner.list_strategies()
        print(f"发现 {len(strategies)} 个策略:")
        for s in strategies:
            print(f"  - {s}")
        return
    
    print(f"🚀 开始回测: {args.strategy} ({args.timeframe}数据)")
    print("=" * 60)
    
    # 加载股票数据
    if args.symbol:
        # 加载单个股票数据
        print(f"📊 加载单股票数据: {args.symbol}")
        data = load_stock_data(
            symbol=args.symbol,
            timeframe=args.timeframe,
            start_date=args.start_date,
            end_date=args.end_date
        )
    else:
        # 加载所有股票数据
        print(f"📊 加载所有{args.timeframe}数据")
        data = load_all_stock_data(
            timeframe=args.timeframe,
            limit=args.limit_stocks
        )
    
    # 如果您只想回测单只股票，可以在这里手动筛选
    # 例如：data = data[data['symbol'] == '000063.SZ']
    
    data['position_state'] = 0

    # 解析策略参数
    try:
        strategy_params = json.loads(args.strategy_params)
    except json.JSONDecodeError:
        print(f"警告：无法解析策略参数 '{args.strategy_params}'，使用默认参数")
        strategy_params = {}
    
    # 获取策略类
    strategy_class = get_strategy_class(args.strategy)
    
    # 初始化回测引擎
    print(f"\n🔧 初始化回测引擎")
    print(f"   策略: {args.strategy}")
    print(f"   参数: {strategy_params}")
    print(f"   初始资金: {args.initial_cash:,.2f}")
    
    engine = BacktestEngine(
        data=data,
        strategy_class=strategy_class,
        initial_cash=args.initial_cash
    )

    # 运行回测
    print("\n🔄 运行回测中...")
    results = engine.run_backtest(strategy_params=strategy_params)
    engine.save_trades(os.path.abspath(os.path.join(os.path.dirname(__file__), "trade_log.csv")))
    
    # 打印完整结果
    print("\n" + "=" * 60)
    print("📊 回测结果")
    print("=" * 60)
    print(f"策略: {args.strategy}")
    print(f"参数: {strategy_params}")
    print(f"时间频率: {args.timeframe}")
    print(f"股票数量: {len(data['symbol'].unique())}")
    
    if 'summary' in results and 'date_range' in results['summary']:
        print(f"时间范围: {results['summary']['date_range']}")
    
    print(f"初始资金: {args.initial_cash:,.2f}")
    
    if 'equity_curve' in results:
        if hasattr(results['equity_curve'], 'iloc'):
            final_equity = results['equity_curve'].iloc[-1]
        elif isinstance(results['equity_curve'], (list, np.ndarray)) and len(results['equity_curve']) > 0:
            final_equity = results['equity_curve'][-1]
        else:
            final_equity = args.initial_cash
        
        print(f"最终净值: {final_equity:,.2f}")
        total_return = (final_equity - args.initial_cash) / args.initial_cash
        print(f"累计收益率: {total_return:.2%}")
    
    if 'summary' in results:
        summary = results['summary']
        if 'total_return' in summary:
            print(f"累计收益率: {summary['total_return']:.2%}")
        if 'annualized_return' in summary:
            print(f"年化收益率: {summary['annualized_return']:.2%}")
        if 'trade_count' in summary:
            print(f"总交易次数: {summary['trade_count']}次")
    
    if 'drawdown' in results and 'max_drawdown' in results['drawdown']:
        print(f"最大回撤: {results['drawdown']['max_drawdown']:.2%}")
    
    if 'risk_return' in results and 'sharpe_ratio' in results['risk_return']:
        print(f"夏普比率: {results['risk_return']['sharpe_ratio']:.2f}")
    
    if 'trades' in results:
        trades = results['trades']
        if 'win_rate' in trades:
            print(f"胜率: {trades['win_rate']:.2%}")
        if 'profit_factor' in trades:
            print(f"盈亏比: {trades['profit_factor']:.2f}:1")
    
    # 显示各股票交易统计
    if 'trades_list' in results:
        print(f"\n📈 各股票交易统计:")
        symbol_trades = {}
        for trade in results['trades_list']:
            symbol = trade.get('symbol', 'unknown')
            if symbol not in symbol_trades:
                symbol_trades[symbol] = []
            symbol_trades[symbol].append(trade)
        
        for symbol, trades in symbol_trades.items():
            profitable_trades = [t for t in trades if t.get('profit', 0) > 0]
            win_rate = len(profitable_trades) / len(trades) if trades else 0
            total_profit = sum(t.get('profit', 0) for t in trades)
            print(f"  {symbol}: {len(trades)}次交易, 胜率{win_rate:.2%}, 总收益{total_profit:.2f}")
    
    # 可视化结果 - 添加错误处理
    if MATPLOTLIB_AVAILABLE:
        try:
            # 确保有回撤数据
            drawdown_series = results.get('drawdown', {}).get('drawdown_series', None)
            
            # 确保equity_curve是正确格式
            equity_curve = results['equity_curve']
            if isinstance(equity_curve, pd.Series):
                # 如果是Series，确保索引是时间类型
                if not isinstance(equity_curve.index, pd.DatetimeIndex):
                    # 尝试转换索引
                    try:
                        equity_curve.index = pd.to_datetime(equity_curve.index)
                    except:
                        # 如果转换失败，使用默认索引
                        pass
            
            Visualizer.plot_equity_curve(equity_curve, drawdown_series, results['trades_list'])
            Visualizer.plot_trade_analysis(results['trades_list'])
        except Exception as e:
            print(f"可视化过程中出现错误: {e}")
            print("跳过可视化部分...")
    else:
        print("matplotlib不可用，跳过可视化部分")
    
    print("\n✅ 回测完成")

def run_backtest(strategy_name, symbol='000001.SZ', timeframe='daily', initial_cash=100000, verbose=False):
    """程序化回测接口"""
    import sys
    # 保存原始sys.argv
    original_argv = sys.argv.copy()
    try:
        # 构建命令行参数
        args = ['--strategy', strategy_name, '--symbol', symbol, '--timeframe', timeframe, '--initial-cash', str(initial_cash)]
        if verbose:
            args.append('--verbose')
        sys.argv = ['main.py'] + args
        
        # 执行main函数
        main()
        return True
    except Exception as e:
        print(f"回测执行异常: {e}")
        return False
    finally:
        # 恢复sys.argv
        sys.argv = original_argv


if __name__ == "__main__":
    main()