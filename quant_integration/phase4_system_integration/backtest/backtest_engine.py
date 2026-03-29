#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一回测引擎 - 阶段4.4：回测层集成

集成组件:
1. phase1_fixes的修复回测系统 (数据加载和兼容性)
2. price_action_integration的回测系统 (持仓管理和绩效计算)
3. phase2_strategy_integration的策略管理器 (策略执行框架)

设计目标:
1. 统一接口，支持多种策略类型
2. 完整的绩效指标计算
3. 风险管理功能
4. 灵活的回测配置
5. 详细的报告输出
"""

import numpy as np
import pandas as pd
import json
import os
import sys
import warnings
from typing import Dict, List, Any, Optional, Tuple, Union, Callable
from datetime import datetime, timedelta
import logging
from pathlib import Path

# 添加路径以导入现有组件
workspace_root = Path("/Users/chengming/.openclaw/workspace")
sys.path.append(str(workspace_root / "quant_integration/phase4_system_integration"))
sys.path.append(str(workspace_root / "quant_integration/phase2_strategy_integration"))
sys.path.append(str(workspace_root / "price_action_integration"))

warnings.filterwarnings('ignore')

# 尝试导入价格行为回测系统
try:
    from backtest_system import BacktestSystem as PriceActionBacktestSystem
    PRICE_ACTION_BACKTEST_AVAILABLE = True
except ImportError:
    PRICE_ACTION_BACKTEST_AVAILABLE = False
    print("警告: 价格行为回测系统不可用，部分功能受限")

# 尝试导入策略管理器
try:
    from managers.strategy_manager import StrategyManager
    STRATEGY_MANAGER_AVAILABLE = True
except ImportError:
    STRATEGY_MANAGER_AVAILABLE = False
    print("警告: 策略管理器不可用，部分功能受限")

# 尝试导入统一数据管理器
try:
    from data.data_manager import UnifiedDataManager
    DATA_MANAGER_AVAILABLE = True
except ImportError:
    DATA_MANAGER_AVAILABLE = False
    print("警告: 统一数据管理器不可用，需要手动提供数据")


class UnifiedBacktestEngine:
    """
    统一回测引擎
    整合多个回测系统，提供统一的接口和功能
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化统一回测引擎
        
        Args:
            config: 回测配置字典，包含:
                - initial_capital: 初始资金 (默认: 100000)
                - commission_rate: 交易佣金率 (默认: 0.001)
                - slippage: 滑点率 (默认: 0.001)
                - max_position_pct: 最大仓位比例 (默认: 0.1)
                - risk_free_rate: 无风险利率 (默认: 0.02)
                - benchmark_symbol: 基准指数代码 (可选)
                - data_config: 数据管理器配置 (可选)
                - strategy_config: 策略配置 (可选)
        """
        self.config = config or {}
        
        # 回测参数
        self.initial_capital = self.config.get('initial_capital', 100000.0)
        self.capital = self.initial_capital
        self.commission_rate = self.config.get('commission_rate', 0.001)  # 0.1%
        self.slippage = self.config.get('slippage', 0.001)  # 0.1%
        self.max_position_pct = self.config.get('max_position_pct', 0.1)  # 10%
        self.risk_free_rate = self.config.get('risk_free_rate', 0.02)  # 2%
        self.benchmark_symbol = self.config.get('benchmark_symbol')
        
        # 回测状态
        self.current_date = None
        self.positions = {}  # 当前持仓 {symbol: shares}
        self.trades = []     # 已完成的交易
        self.equity_curve = []  # 每日权益曲线
        self.daily_returns = []  # 每日收益率
        self.dates = []          # 日期列表
        
        # 组件实例
        self.price_action_backtest = None
        self.strategy_manager = None
        self.data_manager = None
        
        # 日志（必须在初始化组件之前设置）
        self.logger = self._setup_logger()
        
        # 初始化组件
        self._initialize_components()
        
        # 性能指标
        self.performance_metrics = {}
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"UnifiedBacktestEngine_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        logger.setLevel(logging.INFO)
        
        # 创建控制台处理器
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        return logger
    
    def _initialize_components(self):
        """初始化所有可用组件"""
        # 初始化价格行为回测系统
        if PRICE_ACTION_BACKTEST_AVAILABLE:
            try:
                self.price_action_backtest = PriceActionBacktestSystem(
                    initial_capital=self.initial_capital
                )
                self.logger.info("价格行为回测系统初始化成功")
            except Exception as e:
                self.logger.warning(f"价格行为回测系统初始化失败: {e}")
        
        # 初始化策略管理器
        if STRATEGY_MANAGER_AVAILABLE:
            try:
                strategy_config = self.config.get('strategy_config', {})
                self.strategy_manager = StrategyManager(
                    name=strategy_config.get('name', 'UnifiedBacktestManager')
                )
                self.logger.info("策略管理器初始化成功")
            except Exception as e:
                self.logger.warning(f"策略管理器初始化失败: {e}")
        
        # 初始化数据管理器
        if DATA_MANAGER_AVAILABLE:
            try:
                data_config = self.config.get('data_config', {})
                self.data_manager = UnifiedDataManager(data_config)
                self.logger.info("数据管理器初始化成功")
            except Exception as e:
                self.logger.warning(f"数据管理器初始化失败: {e}")
    
    def register_strategy(self, strategy_name: str, strategy_instance: Any, 
                         strategy_type: str = 'custom') -> bool:
        """注册策略到回测引擎
        
        Args:
            strategy_name: 策略名称
            strategy_instance: 策略实例
            strategy_type: 策略类型 ('custom', 'price_action', 'ma')
            
        Returns:
            bool: 是否注册成功
        """
        if self.strategy_manager is None:
            self.logger.error("策略管理器未初始化，无法注册策略")
            return False
        
        try:
            # 根据策略类型进行适配
            if strategy_type == 'custom':
                # 自定义策略，需要实现generate_signals方法
                self.strategy_manager.register_strategy(strategy_name, strategy_instance)
            elif strategy_type == 'price_action':
                # 价格行为策略
                self.strategy_manager.register_strategy(
                    f"PriceAction_{strategy_name}", 
                    strategy_instance
                )
            elif strategy_type == 'ma':
                # 移动平均策略
                self.strategy_manager.register_strategy(
                    f"MA_{strategy_name}", 
                    strategy_instance
                )
            else:
                self.logger.warning(f"未知策略类型: {strategy_type}")
                self.strategy_manager.register_strategy(strategy_name, strategy_instance)
            
            self.logger.info(f"策略 '{strategy_name}' ({strategy_type}) 注册成功")
            return True
            
        except Exception as e:
            self.logger.error(f"策略注册失败: {e}")
            return False
    
    def load_data(self, symbol: str, start_date: str, end_date: str, 
                 source: str = 'local', **kwargs) -> Optional[pd.DataFrame]:
        """加载回测数据
        
        Args:
            symbol: 股票代码
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            source: 数据源 ('local', 'tushare', 'custom')
            **kwargs: 其他数据源参数
            
        Returns:
            pd.DataFrame: OHLCV数据，包含columns: ['open', 'high', 'low', 'close', 'volume']
            如果加载失败返回None
        """
        if self.data_manager is not None:
            try:
                data = self.data_manager.get_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    source=source,
                    **kwargs
                )
                if data is not None and not data.empty:
                    self.logger.info(f"数据加载成功: {symbol} ({start_date} 到 {end_date}), 共 {len(data)} 行")
                    return data
            except Exception as e:
                self.logger.error(f"数据管理器加载数据失败: {e}")
        
        # 回退方案：从本地文件加载
        try:
            # 尝试从示例数据目录加载
            example_dir = workspace_root / "quant_integration/phase4_system_integration/data/example_data"
            csv_file = example_dir / f"{symbol}.csv"
            
            if csv_file.exists():
                data = pd.read_csv(csv_file)
                # 确保日期格式
                if 'date' in data.columns:
                    data['date'] = pd.to_datetime(data['date'])
                    data.set_index('date', inplace=True)
                elif 'trade_date' in data.columns:
                    data['trade_date'] = pd.to_datetime(data['trade_date'])
                    data.set_index('trade_date', inplace=True)
                
                # 过滤日期范围
                mask = (data.index >= pd.Timestamp(start_date)) & (data.index <= pd.Timestamp(end_date))
                data = data[mask]
                
                if not data.empty:
                    self.logger.info(f"从本地文件加载数据成功: {symbol}")
                    return data
        except Exception as e:
            self.logger.error(f"本地文件加载失败: {e}")
        
        self.logger.error(f"无法加载数据: {symbol}")
        return None
    
    def run_backtest(self, strategy_name: str, data: pd.DataFrame, 
                    **kwargs) -> Dict[str, Any]:
        """运行回测
        
        Args:
            strategy_name: 策略名称
            data: OHLCV数据
            **kwargs: 回测参数
            
        Returns:
            Dict[str, Any]: 回测结果，包含:
                - trades: 交易记录
                - equity_curve: 权益曲线
                - performance_metrics: 性能指标
                - positions: 最终持仓
        """
        self.logger.info(f"开始回测: {strategy_name}")
        
        # 重置回测状态
        self._reset_backtest_state()
        
        if data is None or data.empty:
            self.logger.error("回测数据为空")
            return self._create_empty_result()
        
        # 确保数据按日期排序
        data = data.sort_index()
        
        # 提取日期索引
        dates = data.index.tolist()
        self.dates = dates
        
        if not dates:
            self.logger.error("没有有效的日期数据")
            return self._create_empty_result()
        
        # 初始化权益曲线
        self.equity_curve = [self.capital]
        
        # 遍历每个交易日
        for i, current_date in enumerate(dates):
            self.current_date = current_date
            
            # 获取当前价格数据
            current_data = data.iloc[i] if i < len(data) else None
            
            if current_data is None:
                continue
            
            # 获取策略信号（根据策略类型）
            signals = self._get_strategy_signals(strategy_name, data, i, **kwargs)
            
            # 执行交易
            self._execute_trades(signals, current_data)
            
            # 更新持仓价值
            self._update_portfolio_value(current_data)
            
            # 记录权益
            self.equity_curve.append(self.capital)
        
        # 计算性能指标
        self._calculate_performance_metrics(data)
        
        # 生成回测结果
        result = self._generate_backtest_result(strategy_name)
        
        self.logger.info(f"回测完成: {strategy_name}, 总收益率: {self.performance_metrics.get('total_return', 0):.2%}")
        
        return result
    
    def _reset_backtest_state(self):
        """重置回测状态"""
        self.capital = self.initial_capital
        self.positions = {}
        self.trades = []
        self.equity_curve = []
        self.daily_returns = []
        self.dates = []
        self.current_date = None
        self.performance_metrics = {}
    
    def _create_empty_result(self) -> Dict[str, Any]:
        """创建空的回测结果"""
        return {
            'trades': [],
            'equity_curve': [],
            'performance_metrics': {},
            'positions': {},
            'strategy_name': 'unknown',
            'status': 'failed',
            'error': 'No data available'
        }
    
    def _get_strategy_signals(self, strategy_name: str, data: pd.DataFrame, 
                             current_idx: int, **kwargs) -> List[Dict[str, Any]]:
        """获取策略信号
        
        Args:
            strategy_name: 策略名称
            data: 完整数据
            current_idx: 当前数据索引
            **kwargs: 策略参数
            
        Returns:
            List[Dict]: 信号列表，每个信号包含:
                - symbol: 股票代码
                - action: 动作 ('buy', 'sell', 'hold')
                - price: 价格
                - quantity: 数量（可选）
                - confidence: 置信度（可选）
        """
        signals = []
        
        # 方法1: 使用策略管理器
        if self.strategy_manager is not None:
            try:
                # 获取历史数据（到当前日期）
                historical_data = data.iloc[:current_idx + 1] if current_idx > 0 else data.iloc[:1]
                
                # 运行策略
                strategy_result = self.strategy_manager.run_strategy(
                    strategy_name, 
                    historical_data
                )
                
                if strategy_result and 'signals' in strategy_result:
                    signals.extend(strategy_result['signals'])
            except Exception as e:
                self.logger.warning(f"策略管理器获取信号失败: {e}")
        
        # 方法2: 价格行为策略
        if not signals and self.price_action_backtest is not None:
            try:
                # 这里可以集成价格行为信号
                # 暂时返回空列表，后续可以扩展
                pass
            except Exception as e:
                self.logger.warning(f"价格行为策略获取信号失败: {e}")
        
        # 方法3: 简单移动平均策略（演示）
        if not signals and current_idx >= 20:  # 确保有足够的数据
            try:
                # 简单双均线策略演示
                close_prices = data['close'].iloc[:current_idx + 1].values
                
                if len(close_prices) >= 20:
                    ma5 = np.mean(close_prices[-5:])
                    ma20 = np.mean(close_prices[-20:])
                    
                    if ma5 > ma20 * 1.02:  # 短期均线上穿长期均线2%
                        signals.append({
                            'symbol': 'default',
                            'action': 'buy',
                            'price': close_prices[-1],
                            'quantity': int(self.capital * 0.1 / close_prices[-1]),  # 10%仓位
                            'confidence': 0.7
                        })
                    elif ma5 < ma20 * 0.98:  # 短期均线下穿长期均线2%
                        signals.append({
                            'symbol': 'default',
                            'action': 'sell',
                            'price': close_prices[-1],
                            'quantity': 'all',  # 卖出全部
                            'confidence': 0.7
                        })
            except Exception as e:
                self.logger.warning(f"简单移动平均策略失败: {e}")
        
        return signals
    
    def _execute_trades(self, signals: List[Dict[str, Any]], current_data: pd.Series):
        """执行交易
        
        Args:
            signals: 信号列表
            current_data: 当前价格数据
        """
        if not signals:
            return
        
        current_price = current_data['close'] if 'close' in current_data else 0
        
        for signal in signals:
            try:
                symbol = signal.get('symbol', 'default')
                action = signal.get('action', 'hold')
                price = signal.get('price', current_price)
                quantity = signal.get('quantity', 0)
                confidence = signal.get('confidence', 0.5)
                
                # 如果置信度太低，跳过
                if confidence < 0.3:
                    continue
                
                if action == 'buy' and price > 0:
                    # 计算可买数量
                    if isinstance(quantity, str) and quantity == 'all':
                        # 使用全部可用资金
                        max_shares = int(self.capital / (price * (1 + self.commission_rate + self.slippage)))
                        quantity = min(max_shares, int(self.capital * self.max_position_pct / price))
                    
                    # 计算总成本（含佣金和滑点）
                    total_cost = quantity * price * (1 + self.commission_rate + self.slippage)
                    
                    if total_cost <= self.capital and quantity > 0:
                        # 执行买入
                        self.capital -= total_cost
                        current_shares = self.positions.get(symbol, 0)
                        self.positions[symbol] = current_shares + quantity
                        
                        # 记录交易
                        self.trades.append({
                            'date': self.current_date,
                            'symbol': symbol,
                            'action': 'buy',
                            'price': price,
                            'quantity': quantity,
                            'cost': total_cost,
                            'capital_after': self.capital,
                            'signal_confidence': confidence
                        })
                        
                        self.logger.debug(f"买入: {symbol} {quantity}股 @ {price:.2f}, 成本: {total_cost:.2f}")
                
                elif action == 'sell' and symbol in self.positions:
                    current_shares = self.positions[symbol]
                    
                    if isinstance(quantity, str) and quantity == 'all':
                        quantity = current_shares
                    
                    if quantity > 0 and quantity <= current_shares:
                        # 计算总收入（扣除佣金和滑点）
                        total_revenue = quantity * price * (1 - self.commission_rate - self.slippage)
                        
                        # 执行卖出
                        self.capital += total_revenue
                        self.positions[symbol] = current_shares - quantity
                        
                        if self.positions[symbol] == 0:
                            del self.positions[symbol]
                        
                        # 记录交易
                        self.trades.append({
                            'date': self.current_date,
                            'symbol': symbol,
                            'action': 'sell',
                            'price': price,
                            'quantity': quantity,
                            'revenue': total_revenue,
                            'capital_after': self.capital,
                            'signal_confidence': confidence
                        })
                        
                        self.logger.debug(f"卖出: {symbol} {quantity}股 @ {price:.2f}, 收入: {total_revenue:.2f}")
            
            except Exception as e:
                self.logger.error(f"执行交易失败: {e}, 信号: {signal}")
    
    def _update_portfolio_value(self, current_data: pd.Series):
        """更新投资组合价值
        
        Args:
            current_data: 当前价格数据
        """
        # 当前仅支持单标的，可扩展为多标的
        portfolio_value = self.capital
        
        # 添加持仓价值
        for symbol, shares in self.positions.items():
            # 使用当前价格估算持仓价值
            price = current_data['close'] if 'close' in current_data else 0
            portfolio_value += shares * price
        
        # 记录每日收益率
        if self.equity_curve:
            prev_equity = self.equity_curve[-1]
            if prev_equity > 0:
                daily_return = (portfolio_value - prev_equity) / prev_equity
                self.daily_returns.append(daily_return)
    
    def _calculate_performance_metrics(self, data: pd.DataFrame):
        """计算性能指标
        
        Args:
            data: 原始数据，用于计算基准收益率
        """
        if not self.equity_curve or len(self.equity_curve) < 2:
            return
        
        # 提取权益曲线（去除第一个初始值）
        equity_array = np.array(self.equity_curve[1:])
        
        # 基本指标
        final_equity = equity_array[-1] if len(equity_array) > 0 else self.initial_capital
        total_return = (final_equity - self.initial_capital) / self.initial_capital
        
        # 年化收益率
        if self.dates and len(self.dates) > 1:
            days = (self.dates[-1] - self.dates[0]).days
            years = max(days / 365.25, 0.001)  # 避免除以零
            annualized_return = (1 + total_return) ** (1 / years) - 1 if years > 0 else 0
        else:
            annualized_return = 0
        
        # 最大回撤
        peak = equity_array[0]
        max_drawdown = 0
        drawdown_start = None
        drawdown_end = None
        
        for i, equity in enumerate(equity_array):
            if equity > peak:
                peak = equity
            else:
                drawdown = (peak - equity) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    drawdown_start = self.dates[i-1] if i > 0 else None
                    drawdown_end = self.dates[i] if i < len(self.dates) else None
        
        # 夏普比率
        if self.daily_returns:
            returns_array = np.array(self.daily_returns)
            avg_return = np.mean(returns_array)
            std_return = np.std(returns_array)
            
            if std_return > 0:
                sharpe_ratio = (avg_return - self.risk_free_rate / 252) / std_return * np.sqrt(252)
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0
        
        # 交易统计
        total_trades = len(self.trades)
        winning_trades = 0
        total_pnl = 0
        
        for trade in self.trades:
            if 'revenue' in trade and 'cost' in trade.get('previous_trade', {}):
                # 计算单笔交易盈亏（简化）
                pnl = trade.get('revenue', 0) - trade.get('previous_trade', {}).get('cost', 0)
                total_pnl += pnl
                if pnl > 0:
                    winning_trades += 1
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 保存性能指标
        self.performance_metrics = {
            'initial_capital': self.initial_capital,
            'final_equity': final_equity,
            'total_return': total_return,
            'annualized_return': annualized_return,
            'max_drawdown': max_drawdown,
            'drawdown_start': drawdown_start,
            'drawdown_end': drawdown_end,
            'sharpe_ratio': sharpe_ratio,
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'win_rate': win_rate,
            'total_pnl': total_pnl,
            'avg_trade_pnl': total_pnl / total_trades if total_trades > 0 else 0,
            'equity_curve': equity_array.tolist(),
            'daily_returns': self.daily_returns
        }
    
    def _generate_backtest_result(self, strategy_name: str) -> Dict[str, Any]:
        """生成回测结果
        
        Args:
            strategy_name: 策略名称
            
        Returns:
            Dict[str, Any]: 完整的回测结果
        """
        return {
            'strategy_name': strategy_name,
            'config': self.config,
            'trades': self.trades,
            'positions': self.positions,
            'equity_curve': self.equity_curve,
            'performance_metrics': self.performance_metrics,
            'dates': self.dates,
            'status': 'completed',
            'timestamp': datetime.now().isoformat()
        }
    
    def generate_report(self, result: Dict[str, Any], 
                       output_dir: Optional[str] = None) -> str:
        """生成回测报告
        
        Args:
            result: 回测结果
            output_dir: 输出目录（可选）
            
        Returns:
            str: 报告文件路径
        """
        if output_dir is None:
            output_dir = workspace_root / "quant_integration/phase4_system_integration/demo_results"
            os.makedirs(output_dir, exist_ok=True)
        
        # 生成报告文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        strategy_name = result.get('strategy_name', 'unknown').replace(' ', '_')
        report_file = Path(output_dir) / f"backtest_report_{strategy_name}_{timestamp}.json"
        
        # 保存JSON报告
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, default=str)
        
        # 生成文本摘要
        summary_file = Path(output_dir) / f"backtest_summary_{strategy_name}_{timestamp}.txt"
        self._generate_text_summary(result, summary_file)
        
        self.logger.info(f"回测报告已生成: {report_file}")
        self.logger.info(f"回测摘要已生成: {summary_file}")
        
        return str(report_file)
    
    def _generate_text_summary(self, result: Dict[str, Any], output_file: Path):
        """生成文本摘要报告
        
        Args:
            result: 回测结果
            output_file: 输出文件路径
        """
        metrics = result.get('performance_metrics', {})
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(f"回测报告 - {result.get('strategy_name', '未知策略')}\n")
            f.write(f"生成时间: {result.get('timestamp', datetime.now().isoformat())}\n")
            f.write("=" * 80 + "\n\n")
            
            f.write("【基本统计】\n")
            f.write(f"初始资金: {metrics.get('initial_capital', 0):,.2f}\n")
            f.write(f"最终权益: {metrics.get('final_equity', 0):,.2f}\n")
            f.write(f"总收益率: {metrics.get('total_return', 0):.2%}\n")
            f.write(f"年化收益率: {metrics.get('annualized_return', 0):.2%}\n\n")
            
            f.write("【风险指标】\n")
            f.write(f"最大回撤: {metrics.get('max_drawdown', 0):.2%}\n")
            f.write(f"回撤期间: {metrics.get('drawdown_start', 'N/A')} 到 {metrics.get('drawdown_end', 'N/A')}\n")
            f.write(f"夏普比率: {metrics.get('sharpe_ratio', 0):.2f}\n\n")
            
            f.write("【交易统计】\n")
            f.write(f"总交易次数: {metrics.get('total_trades', 0)}\n")
            f.write(f"盈利交易次数: {metrics.get('winning_trades', 0)}\n")
            f.write(f"胜率: {metrics.get('win_rate', 0):.2%}\n")
            f.write(f"总盈亏: {metrics.get('total_pnl', 0):,.2f}\n")
            f.write(f"平均每笔盈亏: {metrics.get('avg_trade_pnl', 0):,.2f}\n\n")
            
            f.write("【持仓情况】\n")
            positions = result.get('positions', {})
            if positions:
                for symbol, shares in positions.items():
                    f.write(f"  {symbol}: {shares} 股\n")
            else:
                f.write("  无持仓\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("交易记录（最近10笔）:\n")
            trades = result.get('trades', [])
            for trade in trades[-10:]:
                f.write(f"  {trade.get('date')} - {trade.get('symbol')} - {trade.get('action')} "
                       f"{trade.get('quantity')}股 @ {trade.get('price', 0):.2f}\n")
            
            f.write("\n" + "=" * 80 + "\n")
            f.write("报告生成完成\n")
    
    def run_comparative_backtest(self, strategies: List[Dict[str, Any]], 
                               data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """运行多个策略的比较回测
        
        Args:
            strategies: 策略列表，每个策略包含:
                - name: 策略名称
                - instance: 策略实例（可选）
                - type: 策略类型
            data: 回测数据
            **kwargs: 回测参数
            
        Returns:
            Dict[str, Any]: 比较回测结果，包含每个策略的结果
        """
        self.logger.info(f"开始比较回测，共 {len(strategies)} 个策略")
        
        results = {}
        
        for strategy_info in strategies:
            strategy_name = strategy_info.get('name', f'strategy_{len(results)}')
            strategy_instance = strategy_info.get('instance')
            strategy_type = strategy_info.get('type', 'custom')
            
            # 注册策略
            if strategy_instance is not None:
                self.register_strategy(strategy_name, strategy_instance, strategy_type)
            
            # 运行回测
            try:
                result = self.run_backtest(strategy_name, data, **kwargs)
                results[strategy_name] = result
                
                # 生成报告
                output_dir = kwargs.get('output_dir')
                self.generate_report(result, output_dir)
                
            except Exception as e:
                self.logger.error(f"策略 '{strategy_name}' 回测失败: {e}")
                results[strategy_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        # 生成比较报告
        comparison_report = self._generate_comparison_report(results)
        
        return {
            'individual_results': results,
            'comparison_report': comparison_report,
            'total_strategies': len(strategies),
            'successful_strategies': sum(1 for r in results.values() if r.get('status') == 'completed')
        }
    
    def _generate_comparison_report(self, results: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """生成策略比较报告
        
        Args:
            results: 各个策略的回测结果
            
        Returns:
            Dict[str, Any]: 比较报告
        """
        comparison = {
            'strategies': [],
            'best_by_metric': {},
            'summary_statistics': {}
        }
        
        # 收集所有策略的指标
        all_metrics = []
        
        for strategy_name, result in results.items():
            if result.get('status') != 'completed':
                continue
            
            metrics = result.get('performance_metrics', {})
            
            strategy_data = {
                'name': strategy_name,
                'total_return': metrics.get('total_return', 0),
                'annualized_return': metrics.get('annualized_return', 0),
                'max_drawdown': metrics.get('max_drawdown', 0),
                'sharpe_ratio': metrics.get('sharpe_ratio', 0),
                'win_rate': metrics.get('win_rate', 0),
                'total_trades': metrics.get('total_trades', 0)
            }
            
            comparison['strategies'].append(strategy_data)
            all_metrics.append(strategy_data)
        
        if not all_metrics:
            return comparison
        
        # 找出每个指标的最佳策略
        metrics_to_compare = ['total_return', 'annualized_return', 'sharpe_ratio', 'win_rate']
        
        for metric in metrics_to_compare:
            if all_metrics:
                best_strategy = max(all_metrics, key=lambda x: x.get(metric, 0))
                comparison['best_by_metric'][metric] = {
                    'strategy': best_strategy['name'],
                    'value': best_strategy[metric]
                }
        
        # 计算摘要统计
        if all_metrics:
            comparison['summary_statistics'] = {
                'avg_total_return': np.mean([m['total_return'] for m in all_metrics]),
                'avg_sharpe_ratio': np.mean([m['sharpe_ratio'] for m in all_metrics]),
                'avg_max_drawdown': np.mean([m['max_drawdown'] for m in all_metrics]),
                'total_strategies': len(all_metrics)
            }
        
        return comparison


def create_demo_backtest_config() -> Dict[str, Any]:
    """创建演示回测配置"""
    return {
        'initial_capital': 100000.0,
        'commission_rate': 0.001,  # 0.1%
        'slippage': 0.001,         # 0.1%
        'max_position_pct': 0.1,   # 10%
        'risk_free_rate': 0.02,    # 2%
        
        'data_config': {
            'cache_enabled': True,
            'preprocessing_enabled': False,
            'default_source': 'local',
            'local_data_dir': './data/example_data'
        },
        
        'strategy_config': {
            'name': 'DemoBacktest',
            'auto_register_strategies': True
        }
    }


def run_demo_backtest():
    """运行演示回测"""
    print("=" * 80)
    print("统一回测引擎演示")
    print("=" * 80)
    
    # 创建回测引擎
    config = create_demo_backtest_config()
    engine = UnifiedBacktestEngine(config)
    
    # 加载示例数据
    data_dir = workspace_root / "quant_integration/phase4_system_integration/data/example_data"
    
    # 查找示例数据文件
    csv_files = list(data_dir.glob("*.csv"))
    
    if not csv_files:
        print("错误: 未找到示例数据文件")
        print("请先运行 example_data_generator.py 生成示例数据")
        return
    
    # 使用第一个CSV文件
    data_file = csv_files[0]
    print(f"使用示例数据: {data_file.name}")
    
    try:
        data = pd.read_csv(data_file)
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            data.set_index('date', inplace=True)
        
        # 运行简单策略回测
        print("\n运行简单移动平均策略回测...")
        result = engine.run_backtest("SimpleMA", data)
        
        if result.get('status') == 'completed':
            print(f"回测成功! 总收益率: {result['performance_metrics'].get('total_return', 0):.2%}")
            
            # 生成报告
            report_file = engine.generate_report(result)
            print(f"报告已保存: {report_file}")
            
            # 显示摘要
            print("\n回测摘要:")
            print(f"初始资金: {result['performance_metrics'].get('initial_capital', 0):,.2f}")
            print(f"最终权益: {result['performance_metrics'].get('final_equity', 0):,.2f}")
            print(f"最大回撤: {result['performance_metrics'].get('max_drawdown', 0):.2%}")
            print(f"夏普比率: {result['performance_metrics'].get('sharpe_ratio', 0):.2f}")
            print(f"总交易次数: {result['performance_metrics'].get('total_trades', 0)}")
        else:
            print(f"回测失败: {result.get('error', '未知错误')}")
    
    except Exception as e:
        print(f"演示回测失败: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("演示完成")


if __name__ == "__main__":
    # 运行演示
    run_demo_backtest()