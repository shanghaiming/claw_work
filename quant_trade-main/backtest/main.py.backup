import sys
import os
import json
import argparse
import talib
import glob
import pandas as pd

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations

current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, 'src')
sys.path.append(src_path)

# 导入所有策略类
from strategies.ma_strategy import MovingAverageStrategy
from strategies.tradingview_strategy import TradingViewStrategy
from strategies.price_action_strategy import PriceActionStrategy
from backtest.engine import BacktestEngine
from backtest.performance import PerformanceAnalyzer 
try:
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    plt = None
    MATPLOTLIB_AVAILABLE = False
    print("警告: matplotlib不可用，可视化功能将禁用")
from utils.visualizer import Visualizer
from backtest.optimization import ParameterOptimizer 

# 设置中文字体
if MATPLOTLIB_AVAILABLE:
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 设置默认字体为黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题

# 策略映射字典
STRATEGY_MAP = {
    "MovingAverage": MovingAverageStrategy,
    "TradingView": TradingViewStrategy,
    "PriceAction": PriceActionStrategy
}

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
        default='MovingAverage',
        choices=['MovingAverage', 'TradingView', 'PriceAction'],
        help='选择回测策略（默认: MovingAverage）'
    )
    parser.add_argument(
        '--strategy-params',
        type=str,
        default='{}',
        help='策略参数，JSON格式（例如：\'{"short_window":5, "long_window":20}\')'
    )
    return parser.parse_args()

def load_all_stock_data():
    """直接遍历指定路径下的所有CSV文件并合并"""
    # 使用本地数据路径
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    target_dir = os.path.join(base_dir, "data", "analyzed", "5min")
    
    # 获取所有CSV文件
    file_pattern = os.path.join(target_dir, "*.csv")
    matched_files = glob.glob(file_pattern)
    
    if not matched_files:
        raise FileNotFoundError(f"目录 {target_dir} 下没有找到任何CSV文件")
    
    print(f"找到 {len(matched_files)} 个股票数据文件")
    
    all_data = []
    for file_path in matched_files:
        try:
            # 从文件名提取股票代码
            filename = os.path.basename(file_path)
            file_symbol = filename.replace('.csv', '')
            
            # 读取单个文件
            df_single = pd.read_csv(file_path, parse_dates=['trade_date']).tail(500)
            df_single.set_index('trade_date', inplace=True)
            
            # 检查必要列是否存在
            required_columns = {'open', 'high', 'low', 'close'}
            missing = required_columns - set(df_single.columns)
            if missing:
                print(f"警告: 文件 {filename} 缺少列 {missing}，跳过")
                continue
            
            # 添加股票代码列
            df_single['symbol'] = file_symbol
            all_data.append(df_single)
            
            print(f"成功加载: {filename} -> {file_symbol}, 数据行数: {len(df_single)}")
            
        except Exception as e:
            print(f"警告: 加载文件 {file_path} 失败: {e}")
            continue
    
    if not all_data:
        raise ValueError("所有股票文件加载失败")
    
    # 合并所有数据
    combined_data = pd.concat(all_data, ignore_index=False)
    combined_data = combined_data.sort_index()
    
    # 获取清理后的股票代码列表
    symbols_clean = combined_data['symbol'].unique().tolist()
    
    print(f"合并后总数据行数: {len(combined_data)}")
    print(f"包含股票数量: {len(symbols_clean)}")
    print(f"股票列表: {symbols_clean}")
    
    return combined_data

def main():
    args = parse_args()
    
    # 加载所有股票数据
    print("开始加载所有股票数据...")
    data = load_all_stock_data()
    
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
    strategy_class = STRATEGY_MAP.get(args.strategy)
    if not strategy_class:
        raise ValueError(f"未知策略: {args.strategy}")
    
    # 初始化回测引擎
    engine = BacktestEngine(
        data=data,
        strategy_class=strategy_class
    )

    # 运行回测
    results = engine.run_backtest(strategy_params=strategy_params)
    engine.save_trades(os.path.abspath(os.path.join(os.path.dirname(__file__), "trade_log.csv")))
    
    # 打印完整结果
    print("\n========== 回测结果 ==========")
    print(f"策略: {args.strategy}")
    print(f"参数: {strategy_params}")
    print(f"股票数量: {len(data['symbol'].unique())}")
    print(f"时间范围: {results['summary']['date_range']}")
    print(f"初始资金: {engine.initial_cash:,.2f}")
    print(f"最终净值: {results['equity_curve'].iloc[-1] if hasattr(results['equity_curve'], 'iloc') else results['equity_curve'][-1]:,.2f}")
    print(f"累计收益率: {results['summary']['total_return']:.2%}")
    print(f"年化收益率: {results['summary']['annualized_return']:.2%}")
    print(f"最大回撤: {results['drawdown']['max_drawdown']:.2%}")
    print(f"夏普比率: {results['risk_return']['sharpe_ratio']:.2f}")
    print(f"总交易次数: {results['summary']['trade_count']}次")
    print(f"胜率: {results['trades']['win_rate']:.2%}")
    print(f"盈亏比: {results['trades']['profit_factor']:.2f}:1")
    
    # 显示各股票交易统计
    print(f"\n各股票交易统计:")
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
    
if __name__ == "__main__":
    main()