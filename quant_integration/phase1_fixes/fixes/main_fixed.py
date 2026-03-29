#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复版回测主程序 - 修复quant_trade-main项目的回测系统
主要修复内容:
1. 移除硬编码的Windows路径
2. 使用可配置的数据目录
3. 跨平台兼容性
4. 改进的错误处理和日志
"""

import sys
import os
import json
import argparse
import glob
import pandas as pd

# 可选导入talib
try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False
    print("警告: TA-Lib未安装，部分技术指标功能受限")
    print("安装: pip install TA-Lib 或 conda install -c conda-forge ta-lib")

os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations

current_dir = os.path.dirname(os.path.abspath(__file__))

# 添加原始src路径（保持兼容性）
src_path = os.path.join(current_dir, 'src')
if os.path.exists(src_path):
    sys.path.append(src_path)
else:
    # 如果本地没有src目录，尝试使用原始项目的src
    original_src_path = os.path.join(current_dir, '..', '..', '..', 'downloads', 'quant_trade-main', 'backtest', 'src')
    if os.path.exists(original_src_path):
        sys.path.append(original_src_path)
        print(f"使用原始项目src目录: {original_src_path}")
    else:
        print("警告: 找不到src目录，策略导入可能会失败")

# 导入我们的修复模块
sys.path.append(current_dir)  # 添加当前目录以导入我们的模块
from config_manager import ConfigManager, get_config
from data_adapter import DataAdapter, load_all_stock_data_fixed

# 尝试导入原始策略类（保持兼容性）
try:
    from strategies.ma_strategy import MovingAverageStrategy
    from backtest.engine import BacktestEngine
    from backtest.performance import PerformanceAnalyzer 
    from utils.visualizer import Visualizer
    from backtest.optimization import ParameterOptimizer
    STRATEGY_IMPORT_SUCCESS = True
except ImportError as e:
    print(f"策略导入警告: {e}")
    print("可能原因: src目录不存在或路径不正确")
    print("将尝试使用简化版本运行")
    STRATEGY_IMPORT_SUCCESS = False

# 可选导入matplotlib
try:
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    MATPLOTLIB_AVAILABLE = True
    
    # 设置中文字体
    plt.rcParams['font.sans-serif'] = ['SimHei'] # 设置默认字体为黑体
    plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
    
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("警告: matplotlib未安装，可视化功能受限")
    print("安装: pip install matplotlib")

# 策略映射字典（与原始版本兼容）
STRATEGY_MAP = {
    "MovingAverage": MovingAverageStrategy if STRATEGY_IMPORT_SUCCESS else None
}


def parse_args():
    """解析命令行参数（扩展版本）"""
    # 先获取配置管理器以提供默认值
    config = get_config()
    
    parser = argparse.ArgumentParser(
        description='股票回测系统 - 修复版',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 使用默认配置
  python main_fixed.py
  
  # 指定数据目录
  python main_fixed.py --data-dir ./my_data
  
  # 指定策略参数
  python main_fixed.py --strategy-params '{"short_window":5, "long_window":20}'
  
  # 使用配置文件
  python main_fixed.py --config-file ./config/my_config.yaml
  
环境变量:
  QUANT_DATA_DIR: 数据目录
  QUANT_TIMEFRAME: 时间周期 (5min, 30min等)
  QUANT_INITIAL_CASH: 初始资金
  QUANT_COMMISSION: 佣金率
        """
    )
    
    # 数据相关参数
    parser.add_argument(
        '--data-dir',
        type=str,
        default=config.get_config_value("data.base_dir"),
        help=f'数据基础目录 (默认: {config.get_config_value("data.base_dir")})'
    )
    
    parser.add_argument(
        '--timeframe',
        type=str,
        default=config.get_config_value("data.timeframe"),
        choices=['1min', '5min', '15min', '30min', '60min', 'daily'],
        help=f'数据时间周期 (默认: {config.get_config_value("data.timeframe")})'
    )
    
    # 回测相关参数
    parser.add_argument(
        '--initial-cash',
        type=float,
        default=config.get_config_value("backtest.initial_cash"),
        help=f'初始资金 (默认: {config.get_config_value("backtest.initial_cash"):,.2f})'
    )
    
    parser.add_argument(
        '--commission',
        type=float,
        default=config.get_config_value("backtest.commission"),
        help=f'交易佣金率 (默认: {config.get_config_value("backtest.commission")})'
    )
    
    # 配置文件
    parser.add_argument(
        '--config-file',
        type=str,
        help='配置文件路径 (JSON或YAML)'
    )
    
    # 原始参数（保持兼容性）
    parser.add_argument(
        '--refresh', 
        action='store_true',
        help='全量更新模式：强制重新预处理数据并训练模型（默认加载已有数据及模型）'
    )
    
    parser.add_argument(
        '--strategy',
        type=str,
        default='MovingAverage',
        choices=['MovingAverage'],
        help='选择回测策略（默认: MovingAverage）'
    )
    
    parser.add_argument(
        '--strategy-params',
        type=str,
        default='{}',
        help='策略参数，JSON格式（例如：\'{"short_window":5, "long_window":20}\')'
    )
    
    return parser.parse_args()


def load_all_stock_data_fixed_wrapper(data_dir: str, timeframe: str):
    """
    修复版的load_all_stock_data函数包装器
    
    这是对原始load_all_stock_data函数的直接替换，但使用可配置路径
    """
    print(f"使用修复版数据加载器...")
    print(f"数据目录: {data_dir}")
    print(f"时间周期: {timeframe}")
    
    # 使用我们的数据适配器
    adapter = DataAdapter(data_dir=data_dir, timeframe=timeframe)
    
    # 打印数据摘要
    adapter.print_data_summary()
    
    # 加载数据
    return adapter.load_all_stock_data()


def check_system_requirements():
    """检查系统要求和依赖"""
    print("="*60)
    print("系统检查")
    print("="*60)
    
    issues = []
    
    # 检查Python版本
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        issues.append(f"Python版本过低: {sys.version}，建议使用Python 3.8+")
    
    # 检查必需包
    required_packages = ['pandas', 'numpy']
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            issues.append(f"缺少包: {package}，安装: pip install {package}")
    
    # 检查可选包
    optional_packages = ['talib']
    for package in optional_packages:
        try:
            __import__(package)
        except ImportError:
            print(f"可选包未安装: {package}，部分功能可能受限")
    
    # 检查策略导入
    if not STRATEGY_IMPORT_SUCCESS:
        issues.append("无法导入策略模块，请确保src目录存在且包含必要的策略文件")
    
    if issues:
        print("发现以下问题:")
        for i, issue in enumerate(issues, 1):
            print(f"  {i}. {issue}")
        print("\n建议先解决这些问题再继续。")
        response = input("是否继续? (y/n): ")
        if response.lower() != 'y':
            print("退出程序")
            sys.exit(1)
    else:
        print("✓ 系统检查通过")
    
    print("="*60)


def setup_environment(args):
    """设置运行环境"""
    print("="*60)
    print("环境设置")
    print("="*60)
    
    # 初始化配置（考虑配置文件）
    config = get_config(args.config_file) if args.config_file else get_config()
    
    # 应用命令行参数到配置
    config.set_config_value("data.base_dir", args.data_dir)
    config.set_config_value("data.timeframe", args.timeframe)
    config.set_config_value("backtest.initial_cash", args.initial_cash)
    config.set_config_value("backtest.commission", args.commission)
    
    # 打印最终配置
    config.print_summary()
    
    # 创建必要目录
    data_dir = config.get_data_directory(args.timeframe)
    os.makedirs(data_dir, exist_ok=True)
    
    print("="*60)
    
    return config


def run_backtest_safely(data, args, config):
    """安全运行回测（包含错误处理）"""
    try:
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
        print(f"初始化回测引擎...")
        print(f"策略: {args.strategy}")
        print(f"参数: {strategy_params}")
        
        engine = BacktestEngine(
            data=data,
            strategy_class=strategy_class,
            initial_cash=config.get_config_value("backtest.initial_cash"),
            commission=config.get_config_value("backtest.commission")
        )
        
        # 运行回测
        print("运行回测...")
        results = engine.run_backtest(strategy_params=strategy_params)
        
        # 保存交易日志
        trade_log_path = os.path.join(current_dir, "trade_log.csv")
        engine.save_trades(trade_log_path)
        print(f"交易日志已保存到: {trade_log_path}")
        
        return results, engine
        
    except Exception as e:
        print(f"回测运行失败: {e}")
        import traceback
        traceback.print_exc()
        
        # 提供调试建议
        print("\n调试建议:")
        print("1. 检查数据格式是否正确")
        print("2. 检查策略参数是否合理")
        print("3. 尝试简化策略参数")
        print("4. 检查src目录中的策略实现")
        
        return None, None


def print_backtest_results(results, engine, args):
    """打印回测结果"""
    if not results:
        print("无回测结果可显示")
        return
    
    print("\n" + "="*60)
    print("回测结果")
    print("="*60)
    
    print(f"策略: {args.strategy}")
    print(f"参数: {json.loads(args.strategy_params) if args.strategy_params != '{}' else '默认'}")
    print(f"初始资金: {engine.initial_cash:,.2f}")
    print(f"时间范围: {results['summary']['date_range']}")
    
    # 提取结果字段（处理可能的格式差异）
    equity_curve = results['equity_curve']
    if hasattr(equity_curve, 'iloc'):
        final_equity = equity_curve.iloc[-1]
    else:
        final_equity = equity_curve[-1] if equity_curve else engine.initial_cash
    
    print(f"最终净值: {final_equity:,.2f}")
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
    
    print("="*60)


def visualize_results(results):
    """可视化回测结果"""
    try:
        print("\n生成可视化图表...")
        
        # 确保有回撤数据
        drawdown_series = results.get('drawdown', {}).get('drawdown_series', None)
        
        # 确保equity_curve是正确格式
        equity_curve = results['equity_curve']
        
        Visualizer.plot_equity_curve(equity_curve, drawdown_series, results['trades_list'])
        Visualizer.plot_trade_analysis(results['trades_list'])
        
        print("可视化完成")
        
    except Exception as e:
        print(f"可视化过程中出现错误: {e}")
        print("跳过可视化部分...")


def main():
    """主函数 - 修复版"""
    print("="*60)
    print("量化交易回测系统 - 修复版")
    print("="*60)
    print("修复内容:")
    print("1. ✅ 移除硬编码Windows路径")
    print("2. ✅ 支持可配置数据目录")
    print("3. ✅ 跨平台兼容性")
    print("4. ✅ 改进的错误处理")
    print("="*60)
    
    # 解析参数
    args = parse_args()
    
    # 检查系统要求
    check_system_requirements()
    
    # 设置环境
    config = setup_environment(args)
    
    # 加载数据
    print("\n" + "="*60)
    print("加载数据")
    print("="*60)
    
    try:
        # 使用修复版数据加载器
        data = load_all_stock_data_fixed_wrapper(
            data_dir=config.get_config_value("data.base_dir"),
            timeframe=args.timeframe
        )
        
        # 检查数据是否为空
        if data.empty:
            print("错误: 加载的数据为空")
            print("可能原因:")
            print("1. 数据目录中没有CSV文件")
            print("2. CSV文件格式不正确")
            print("3. 数据目录路径错误")
            return
        
        print(f"数据加载成功: {len(data)} 行")
        print(f"股票列表: {data['symbol'].unique().tolist()}")
        
    except Exception as e:
        print(f"数据加载失败: {e}")
        print("\n解决方法:")
        print("1. 检查数据目录是否存在")
        print("2. 确保CSV文件格式正确")
        print("3. 使用 --data-dir 参数指定正确的数据目录")
        print("4. 查看 data/analyzed/5min/README.md 了解数据格式要求")
        return
    
    # 添加position_state列（与原始代码兼容）
    data['position_state'] = 0
    
    # 运行回测
    print("\n" + "="*60)
    print("运行回测")
    print("="*60)
    
    if not STRATEGY_IMPORT_SUCCESS:
        print("错误: 无法导入策略模块，回测无法进行")
        print("请确保src目录存在且包含必要的策略文件")
        print(f"预期路径: {os.path.join(current_dir, 'src')}")
        return
    
    results, engine = run_backtest_safely(data, args, config)
    
    if results and engine:
        # 打印结果
        print_backtest_results(results, engine, args)
        
        # 可视化结果
        visualize_results(results)
    
    print("\n" + "="*60)
    print("回测完成!")
    print("="*60)
    
    # 提供后续步骤建议
    print("\n后续步骤建议:")
    print("1. 查看 trade_log.csv 获取详细交易记录")
    print("2. 调整策略参数优化性能")
    print("3. 尝试不同的数据时间周期")
    print("4. 添加更多股票数据进行测试")
    
    # 保存配置（便于复现）
    config_save_path = os.path.join(current_dir, "last_run_config.json")
    config.save_config(config_save_path, 'json')
    print(f"配置已保存到: {config_save_path}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n用户中断程序")
    except Exception as e:
        print(f"\n程序运行出错: {e}")
        import traceback
        traceback.print_exc()
        print("\n问题反馈:")
        print("1. 检查数据目录和文件格式")
        print("2. 确认所有依赖包已安装")
        print("3. 查看日志文件获取更多信息")