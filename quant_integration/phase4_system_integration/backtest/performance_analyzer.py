#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
绩效分析模块 - 阶段4.4：回测层集成

提供全面的绩效指标计算和分析功能:
1. 基本绩效指标计算
2. 风险调整后收益指标
3. 交易统计分析
4. 基准比较分析
5. 绩效报告生成
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import warnings
import logging
import json

# 尝试导入scipy，如果不可用则使用替代方案
try:
    from scipy import stats
    SCIPY_AVAILABLE = True
except ImportError:
    SCIPY_AVAILABLE = False
    # 创建简单的正态分布分位数函数替代
    import math
    class SimpleStats:
        @staticmethod
        def norm_ppf(p):
            """简单的正态分布分位数函数近似"""
            # 使用近似公式
            if p <= 0 or p >= 1:
                raise ValueError("p must be in (0, 1)")
            
            # Abramowitz and Stegun 近似公式
            t = math.sqrt(-2.0 * math.log(min(p, 1-p)))
            c0 = 2.515517
            c1 = 0.802853
            c2 = 0.010328
            d1 = 1.432788
            d2 = 0.189269
            d3 = 0.001308
            
            numerator = c0 + c1 * t + c2 * t * t
            denominator = 1.0 + d1 * t + d2 * t * t + d3 * t * t * t
            
            z = t - numerator / denominator
            return -z if p < 0.5 else z
    
    # 创建替代的stats模块
    class SimpleStatsModule:
        norm = SimpleStats()
    
    stats = SimpleStatsModule()

warnings.filterwarnings('ignore')


class PerformanceAnalyzer:
    """
    绩效分析器
    提供全面的绩效指标计算和分析
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """初始化绩效分析器
        
        Args:
            risk_free_rate: 无风险利率 (默认: 0.02, 2%)
        """
        self.risk_free_rate = risk_free_rate
        
        # 日志
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"PerformanceAnalyzer_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        logger.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        return logger
    
    def calculate_basic_metrics(self, equity_curve: List[float], 
                              dates: Optional[List] = None) -> Dict[str, Any]:
        """计算基本绩效指标
        
        Args:
            equity_curve: 权益曲线
            dates: 日期列表 (可选)
            
        Returns:
            Dict[str, Any]: 基本绩效指标
        """
        if not equity_curve or len(equity_curve) < 2:
            return {}
        
        equity_array = np.array(equity_curve)
        initial_equity = equity_array[0]
        final_equity = equity_array[-1]
        
        # 总收益率
        total_return = (final_equity - initial_equity) / initial_equity
        
        # 年化收益率
        if dates and len(dates) > 1:
            # 基于日期计算实际年数
            if isinstance(dates[0], (datetime, pd.Timestamp)):
                days = (dates[-1] - dates[0]).days
                years = max(days / 365.25, 0.001)
                annualized_return = (1 + total_return) ** (1 / years) - 1
            else:
                # 假设每天一个数据点
                years = len(equity_array) / 252  # 252个交易日
                annualized_return = (1 + total_return) ** (1 / years) - 1
        else:
            # 默认假设
            years = len(equity_array) / 252
            annualized_return = (1 + total_return) ** (1 / years) - 1
        
        # 计算每日收益率
        daily_returns = self._calculate_daily_returns(equity_array)
        
        # 基本统计
        avg_daily_return = np.mean(daily_returns) if len(daily_returns) > 0 else 0
        std_daily_return = np.std(daily_returns) if len(daily_returns) > 0 else 0
        
        # 最大单日收益和损失
        max_daily_gain = np.max(daily_returns) if len(daily_returns) > 0 else 0
        max_daily_loss = np.min(daily_returns) if len(daily_returns) > 0 else 0
        
        # 正收益天数比例
        positive_days = sum(1 for r in daily_returns if r > 0)
        positive_day_ratio = positive_days / len(daily_returns) if len(daily_returns) > 0 else 0
        
        result = {
            'initial_equity': float(initial_equity),
            'final_equity': float(final_equity),
            'total_return': float(total_return),
            'annualized_return': float(annualized_return),
            'avg_daily_return': float(avg_daily_return),
            'std_daily_return': float(std_daily_return),
            'max_daily_gain': float(max_daily_gain),
            'max_daily_loss': float(max_daily_loss),
            'positive_day_ratio': float(positive_day_ratio),
            'total_days': len(equity_array),
            'positive_days': positive_days,
            'negative_days': len(daily_returns) - positive_days
        }
        
        self.logger.debug(f"基本指标计算: 总收益={total_return:.2%}, 年化={annualized_return:.2%}, "
                         f"波动率={std_daily_return:.4f}, 正收益天数={positive_day_ratio:.2%}")
        
        return result
    
    def _calculate_daily_returns(self, equity_array: np.ndarray) -> np.ndarray:
        """计算每日收益率
        
        Args:
            equity_array: 权益数组
            
        Returns:
            np.ndarray: 每日收益率数组
        """
        if len(equity_array) < 2:
            return np.array([])
        
        returns = np.diff(equity_array) / equity_array[:-1]
        return returns
    
    def calculate_risk_adjusted_metrics(self, equity_curve: List[float], 
                                      dates: Optional[List] = None,
                                      benchmark_returns: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """计算风险调整后收益指标
        
        Args:
            equity_curve: 权益曲线
            dates: 日期列表 (可选)
            benchmark_returns: 基准收益率 (可选)
            
        Returns:
            Dict[str, Any]: 风险调整后指标
        """
        basic_metrics = self.calculate_basic_metrics(equity_curve, dates)
        
        if not equity_curve or len(equity_curve) < 2:
            return {}
        
        equity_array = np.array(equity_curve)
        daily_returns = self._calculate_daily_returns(equity_array)
        
        if len(daily_returns) == 0:
            return {}
        
        avg_return = np.mean(daily_returns)
        std_return = np.std(daily_returns)
        
        # 夏普比率 (年化)
        if std_return > 0:
            daily_risk_free = self.risk_free_rate / 252  # 日化无风险利率
            sharpe_ratio = (avg_return - daily_risk_free) / std_return * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        # 索提诺比率 (只考虑下行风险)
        downside_returns = daily_returns[daily_returns < 0]
        if len(downside_returns) > 0:
            downside_std = np.std(downside_returns)
            if downside_std > 0:
                sortino_ratio = (avg_return - self.risk_free_rate/252) / downside_std * np.sqrt(252)
            else:
                sortino_ratio = 0
        else:
            sortino_ratio = 0
        
        # 卡玛比率 (收益/最大回撤)
        max_drawdown_info = self.calculate_max_drawdown(equity_curve)
        max_drawdown = max_drawdown_info.get('max_drawdown', 0)
        
        if max_drawdown > 0:
            calmar_ratio = basic_metrics.get('annualized_return', 0) / max_drawdown
        else:
            calmar_ratio = 0
        
        # 信息比率 (相对于基准)
        information_ratio = 0
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            # 确保长度匹配
            min_len = min(len(daily_returns), len(benchmark_returns))
            if min_len > 0:
                excess_returns = daily_returns[:min_len] - benchmark_returns[:min_len]
                excess_return_mean = np.mean(excess_returns)
                excess_return_std = np.std(excess_returns)
                
                if excess_return_std > 0:
                    information_ratio = excess_return_mean / excess_return_std * np.sqrt(252)
        
        # 特雷诺比率 (收益/贝塔)
        treynor_ratio = 0
        if benchmark_returns is not None and len(benchmark_returns) > 0:
            min_len = min(len(daily_returns), len(benchmark_returns))
            if min_len > 0:
                # 计算贝塔
                cov_matrix = np.cov(daily_returns[:min_len], benchmark_returns[:min_len])
                if cov_matrix[1, 1] > 0:
                    beta = cov_matrix[0, 1] / cov_matrix[1, 1]
                    if beta > 0:
                        treynor_ratio = (basic_metrics.get('annualized_return', 0) - self.risk_free_rate) / beta
        
        result = {
            'sharpe_ratio': float(sharpe_ratio),
            'sortino_ratio': float(sortino_ratio),
            'calmar_ratio': float(calmar_ratio),
            'information_ratio': float(information_ratio),
            'treynor_ratio': float(treynor_ratio),
            'avg_return': float(avg_return),
            'std_return': float(std_return),
            'downside_std': float(np.std(downside_returns) if len(downside_returns) > 0 else 0)
        }
        
        self.logger.debug(f"风险调整指标: 夏普={sharpe_ratio:.3f}, 索提诺={sortino_ratio:.3f}, "
                         f"卡玛={calmar_ratio:.3f}, 信息比率={information_ratio:.3f}")
        
        return result
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Dict[str, Any]:
        """计算最大回撤
        
        Args:
            equity_curve: 权益曲线
            
        Returns:
            Dict[str, Any]: 最大回撤信息
        """
        if not equity_curve or len(equity_curve) < 2:
            return {
                'max_drawdown': 0,
                'drawdown_start_idx': 0,
                'drawdown_end_idx': 0,
                'drawdown_start_value': 0,
                'drawdown_end_value': 0,
                'recovery_idx': None
            }
        
        equity_array = np.array(equity_curve)
        
        # 计算累积最大值
        cumulative_max = np.maximum.accumulate(equity_array)
        
        # 计算回撤
        drawdowns = (cumulative_max - equity_array) / cumulative_max
        
        # 找到最大回撤
        max_drawdown_idx = np.argmax(drawdowns)
        max_drawdown = drawdowns[max_drawdown_idx] if max_drawdown_idx < len(drawdowns) else 0
        
        # 找到回撤开始点 (累积最大值的位置)
        drawdown_start_idx = np.argmax(equity_array[:max_drawdown_idx+1]) if max_drawdown_idx > 0 else 0
        
        # 找到恢复点 (权益回到或超过回撤开始点)
        recovery_idx = None
        if drawdown_start_idx < len(equity_array):
            recovery_value = equity_array[drawdown_start_idx]
            for i in range(max_drawdown_idx, len(equity_array)):
                if equity_array[i] >= recovery_value:
                    recovery_idx = i
                    break
        
        result = {
            'max_drawdown': float(max_drawdown),
            'drawdown_start_idx': int(drawdown_start_idx),
            'drawdown_end_idx': int(max_drawdown_idx),
            'drawdown_start_value': float(equity_array[drawdown_start_idx]) if drawdown_start_idx < len(equity_array) else 0,
            'drawdown_end_value': float(equity_array[max_drawdown_idx]) if max_drawdown_idx < len(equity_array) else 0,
            'recovery_idx': int(recovery_idx) if recovery_idx is not None else None,
            'recovery_period': int(recovery_idx - max_drawdown_idx) if recovery_idx is not None else None,
            'drawdown_period': int(max_drawdown_idx - drawdown_start_idx) if max_drawdown_idx > drawdown_start_idx else 0
        }
        
        self.logger.debug(f"最大回撤: {max_drawdown:.2%}, 回撤期={result['drawdown_period']}天, "
                         f"恢复期={result['recovery_period']}天")
        
        return result
    
    def calculate_trade_metrics(self, trades: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算交易相关指标
        
        Args:
            trades: 交易记录列表，每个交易包含:
                - action: 'buy' 或 'sell'
                - price: 交易价格
                - quantity: 交易数量
                - date: 交易日期
                - symbol: 标的代码 (可选)
                - pnl: 盈亏金额 (可选)
                
        Returns:
            Dict[str, Any]: 交易指标
        """
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'profit_factor': 0,
                'avg_trade_pnl': 0,
                'total_pnl': 0
            }
        
        # 配对买入和卖出交易
        trade_pairs = self._pair_buy_sell_trades(trades)
        
        total_trades = len(trade_pairs)
        winning_trades = 0
        losing_trades = 0
        total_profit = 0
        total_loss = 0
        win_pnls = []
        loss_pnls = []
        
        for pair in trade_pairs:
            buy_trade = pair.get('buy')
            sell_trade = pair.get('sell')
            
            if buy_trade and sell_trade:
                buy_price = buy_trade.get('price', 0)
                sell_price = sell_trade.get('price', 0)
                quantity = buy_trade.get('quantity', 0)
                
                if quantity > 0 and buy_price > 0:
                    pnl = (sell_price - buy_price) * quantity
                    
                    if pnl > 0:
                        winning_trades += 1
                        total_profit += pnl
                        win_pnls.append(pnl)
                    else:
                        losing_trades += 1
                        total_loss += abs(pnl)
                        loss_pnls.append(pnl)
        
        # 计算指标
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        avg_win = np.mean(win_pnls) if win_pnls else 0
        avg_loss = np.mean(loss_pnls) if loss_pnls else 0
        profit_factor = total_profit / total_loss if total_loss > 0 else (total_profit if total_profit > 0 else 0)
        avg_trade_pnl = (total_profit - total_loss) / total_trades if total_trades > 0 else 0
        total_pnl = total_profit - total_loss
        
        # 平均持仓时间
        avg_holding_period = self._calculate_avg_holding_period(trade_pairs)
        
        # 连续盈利/亏损
        streak_info = self._calculate_streaks(trade_pairs)
        
        result = {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': float(win_rate),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': float(profit_factor),
            'avg_trade_pnl': float(avg_trade_pnl),
            'total_pnl': float(total_pnl),
            'total_profit': float(total_profit),
            'total_loss': float(total_loss),
            'avg_holding_period_days': float(avg_holding_period),
            'max_consecutive_wins': streak_info.get('max_consecutive_wins', 0),
            'max_consecutive_losses': streak_info.get('max_consecutive_losses', 0),
            'current_streak': streak_info.get('current_streak', 0),
            'current_streak_type': streak_info.get('current_streak_type', 'none'),
            'expectancy': self._calculate_expectancy(win_rate, avg_win, avg_loss)
        }
        
        self.logger.debug(f"交易指标: 总交易={total_trades}, 胜率={win_rate:.2%}, "
                         f"盈亏比={profit_factor:.2f}, 平均持仓={avg_holding_period:.1f}天")
        
        return result
    
    def _pair_buy_sell_trades(self, trades: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """配对买入和卖出交易
        
        Args:
            trades: 原始交易记录
            
        Returns:
            List[Dict]: 配对后的交易
        """
        # 按标的代码分组
        symbol_groups = {}
        
        for trade in trades:
            symbol = trade.get('symbol', 'default')
            action = trade.get('action')
            
            if symbol not in symbol_groups:
                symbol_groups[symbol] = {'buys': [], 'sells': []}
            
            if action == 'buy':
                symbol_groups[symbol]['buys'].append(trade)
            elif action == 'sell':
                symbol_groups[symbol]['sells'].append(trade)
        
        # 配对买入和卖出
        trade_pairs = []
        
        for symbol, groups in symbol_groups.items():
            buys = sorted(groups['buys'], key=lambda x: x.get('date', datetime.min))
            sells = sorted(groups['sells'], key=lambda x: x.get('date', datetime.min))
            
            i, j = 0, 0
            while i < len(buys) and j < len(sells):
                buy_trade = buys[i]
                sell_trade = sells[j]
                
                # 检查是否匹配 (简单的先买后卖)
                buy_date = buy_trade.get('date')
                sell_date = sell_trade.get('date')
                
                if buy_date and sell_date and sell_date > buy_date:
                    trade_pairs.append({
                        'symbol': symbol,
                        'buy': buy_trade,
                        'sell': sell_trade,
                        'holding_period': (sell_date - buy_date).days
                    })
                    i += 1
                    j += 1
                else:
                    # 日期不匹配，移动指针
                    if buy_date and sell_date and buy_date > sell_date:
                        j += 1
                    else:
                        i += 1
        
        return trade_pairs
    
    def _calculate_avg_holding_period(self, trade_pairs: List[Dict[str, Any]]) -> float:
        """计算平均持仓时间
        
        Args:
            trade_pairs: 配对后的交易
            
        Returns:
            float: 平均持仓天数
        """
        if not trade_pairs:
            return 0
        
        total_days = 0
        count = 0
        
        for pair in trade_pairs:
            holding_period = pair.get('holding_period')
            if holding_period is not None:
                total_days += holding_period
                count += 1
        
        return total_days / count if count > 0 else 0
    
    def _calculate_streaks(self, trade_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """计算连续盈利/亏损
        
        Args:
            trade_pairs: 配对后的交易
            
        Returns:
            Dict[str, Any]: 连续统计信息
        """
        if not trade_pairs:
            return {
                'max_consecutive_wins': 0,
                'max_consecutive_losses': 0,
                'current_streak': 0,
                'current_streak_type': 'none'
            }
        
        # 提取每笔交易的盈亏
        pnls = []
        for pair in trade_pairs:
            buy_trade = pair.get('buy')
            sell_trade = pair.get('sell')
            
            if buy_trade and sell_trade:
                buy_price = buy_trade.get('price', 0)
                sell_price = sell_trade.get('price', 0)
                quantity = buy_trade.get('quantity', 0)
                
                if quantity > 0 and buy_price > 0:
                    pnl = (sell_price - buy_price) * quantity
                    pnls.append(1 if pnl > 0 else -1)  # 1: 盈利, -1: 亏损
                else:
                    pnls.append(0)
            else:
                pnls.append(0)
        
        # 计算连续统计
        max_consecutive_wins = 0
        max_consecutive_losses = 0
        current_streak = 0
        current_streak_type = 'none'
        
        if pnls:
            current_streak = 1
            current_streak_type = 'win' if pnls[0] > 0 else 'loss' if pnls[0] < 0 else 'none'
            
            for i in range(1, len(pnls)):
                if pnls[i] == pnls[i-1] and pnls[i] != 0:
                    current_streak += 1
                else:
                    # 更新最大连续
                    if pnls[i-1] > 0:
                        max_consecutive_wins = max(max_consecutive_wins, current_streak)
                    elif pnls[i-1] < 0:
                        max_consecutive_losses = max(max_consecutive_losses, current_streak)
                    
                    # 开始新的连续
                    current_streak = 1 if pnls[i] != 0 else 0
                    current_streak_type = 'win' if pnls[i] > 0 else 'loss' if pnls[i] < 0 else 'none'
            
            # 最后一次更新
            if pnls[-1] > 0:
                max_consecutive_wins = max(max_consecutive_wins, current_streak)
            elif pnls[-1] < 0:
                max_consecutive_losses = max(max_consecutive_losses, current_streak)
        
        return {
            'max_consecutive_wins': max_consecutive_wins,
            'max_consecutive_losses': max_consecutive_losses,
            'current_streak': current_streak,
            'current_streak_type': current_streak_type
        }
    
    def _calculate_expectancy(self, win_rate: float, avg_win: float, avg_loss: float) -> float:
        """计算期望值
        
        Args:
            win_rate: 胜率
            avg_win: 平均盈利
            avg_loss: 平均亏损
            
        Returns:
            float: 期望值
        """
        if avg_loss == 0:
            return avg_win * win_rate
        else:
            return (win_rate * avg_win) - ((1 - win_rate) * avg_loss)
    
    def calculate_benchmark_comparison(self, strategy_returns: np.ndarray, 
                                     benchmark_returns: np.ndarray) -> Dict[str, Any]:
        """计算与基准的比较
        
        Args:
            strategy_returns: 策略收益率
            benchmark_returns: 基准收益率
            
        Returns:
            Dict[str, Any]: 基准比较指标
        """
        if len(strategy_returns) == 0 or len(benchmark_returns) == 0:
            return {}
        
        # 确保长度一致
        min_len = min(len(strategy_returns), len(benchmark_returns))
        if min_len == 0:
            return {}
        
        strategy_returns_adj = strategy_returns[:min_len]
        benchmark_returns_adj = benchmark_returns[:min_len]
        
        # 计算超额收益
        excess_returns = strategy_returns_adj - benchmark_returns_adj
        
        # 计算阿尔法、贝塔
        try:
            # 使用线性回归计算贝塔
            if np.std(benchmark_returns_adj) > 0:
                beta = np.cov(strategy_returns_adj, benchmark_returns_adj)[0, 1] / np.var(benchmark_returns_adj)
            else:
                beta = 0
            
            # 计算阿尔法 (年化)
            alpha = np.mean(excess_returns) * 252  # 年化
            
            # 计算R-squared
            correlation = np.corrcoef(strategy_returns_adj, benchmark_returns_adj)[0, 1]
            r_squared = correlation ** 2
            
            # 跟踪误差
            tracking_error = np.std(excess_returns) * np.sqrt(252)
            
            # 信息比率
            information_ratio = np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252) if np.std(excess_returns) > 0 else 0
            
            # 上涨/下跌捕捉率
            up_market_days = benchmark_returns_adj > 0
            down_market_days = benchmark_returns_adj < 0
            
            up_capture = np.mean(strategy_returns_adj[up_market_days]) / np.mean(benchmark_returns_adj[up_market_days]) if np.sum(up_market_days) > 0 and np.mean(benchmark_returns_adj[up_market_days]) != 0 else 0
            down_capture = np.mean(strategy_returns_adj[down_market_days]) / np.mean(benchmark_returns_adj[down_market_days]) if np.sum(down_market_days) > 0 and np.mean(benchmark_returns_adj[down_market_days]) != 0 else 0
            
        except Exception as e:
            self.logger.warning(f"基准比较计算失败: {e}")
            return {}
        
        result = {
            'alpha': float(alpha),
            'beta': float(beta),
            'r_squared': float(r_squared),
            'tracking_error': float(tracking_error),
            'information_ratio': float(information_ratio),
            'up_capture_ratio': float(up_capture),
            'down_capture_ratio': float(down_capture),
            'excess_return_mean': float(np.mean(excess_returns)),
            'excess_return_std': float(np.std(excess_returns)),
            'correlation': float(correlation),
            'outperformance': float(np.sum(excess_returns > 0) / min_len if min_len > 0 else 0)
        }
        
        self.logger.debug(f"基准比较: 阿尔法={alpha:.4f}, 贝塔={beta:.3f}, R²={r_squared:.3f}, "
                         f"信息比率={information_ratio:.3f}, 上涨捕捉={up_capture:.3f}, 下跌捕捉={down_capture:.3f}")
        
        return result
    
    def calculate_monthly_returns(self, equity_curve: List[float], 
                                dates: List) -> Dict[str, Any]:
        """计算月度收益
        
        Args:
            equity_curve: 权益曲线
            dates: 日期列表
            
        Returns:
            Dict[str, Any]: 月度收益统计
        """
        if len(equity_curve) != len(dates) or len(equity_curve) < 2:
            return {}
        
        # 创建DataFrame
        df = pd.DataFrame({
            'equity': equity_curve,
            'date': dates
        })
        
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)
        
        # 按月份重新采样
        monthly_df = df['equity'].resample('M').last()
        
        # 计算月度收益率
        monthly_returns = monthly_df.pct_change().dropna()
        
        # 月度收益统计
        monthly_stats = {
            'monthly_returns': monthly_returns.tolist(),
            'monthly_dates': monthly_returns.index.strftime('%Y-%m').tolist(),
            'best_month': float(monthly_returns.max()) if len(monthly_returns) > 0 else 0,
            'worst_month': float(monthly_returns.min()) if len(monthly_returns) > 0 else 0,
            'avg_monthly_return': float(monthly_returns.mean()) if len(monthly_returns) > 0 else 0,
            'positive_months': int((monthly_returns > 0).sum()) if len(monthly_returns) > 0 else 0,
            'negative_months': int((monthly_returns < 0).sum()) if len(monthly_returns) > 0 else 0,
            'monthly_win_rate': float((monthly_returns > 0).mean()) if len(monthly_returns) > 0 else 0
        }
        
        return monthly_stats
    
    def generate_comprehensive_report(self, equity_curve: List[float], 
                                    trades: List[Dict[str, Any]],
                                    dates: Optional[List] = None,
                                    benchmark_returns: Optional[np.ndarray] = None) -> Dict[str, Any]:
        """生成全面的绩效报告
        
        Args:
            equity_curve: 权益曲线
            trades: 交易记录
            dates: 日期列表 (可选)
            benchmark_returns: 基准收益率 (可选)
            
        Returns:
            Dict[str, Any]: 全面的绩效报告
        """
        self.logger.info("生成全面绩效报告...")
        
        # 计算各类指标
        basic_metrics = self.calculate_basic_metrics(equity_curve, dates)
        risk_adjusted_metrics = self.calculate_risk_adjusted_metrics(equity_curve, dates, benchmark_returns)
        max_drawdown_info = self.calculate_max_drawdown(equity_curve)
        trade_metrics = self.calculate_trade_metrics(trades)
        
        # 计算基准比较 (如果有基准数据)
        benchmark_comparison = {}
        if benchmark_returns is not None and len(equity_curve) > 1:
            daily_returns = self._calculate_daily_returns(np.array(equity_curve))
            if len(daily_returns) > 0:
                benchmark_comparison = self.calculate_benchmark_comparison(daily_returns, benchmark_returns)
        
        # 计算月度收益 (如果有日期数据)
        monthly_stats = {}
        if dates and len(dates) == len(equity_curve):
            monthly_stats = self.calculate_monthly_returns(equity_curve, dates)
        
        # 组合报告
        comprehensive_report = {
            'report_timestamp': datetime.now().isoformat(),
            'period_days': len(equity_curve) if equity_curve else 0,
            'basic_metrics': basic_metrics,
            'risk_adjusted_metrics': risk_adjusted_metrics,
            'max_drawdown': max_drawdown_info,
            'trade_metrics': trade_metrics,
            'benchmark_comparison': benchmark_comparison,
            'monthly_stats': monthly_stats,
            'summary': self._generate_summary(basic_metrics, risk_adjusted_metrics, trade_metrics)
        }
        
        self.logger.info(f"绩效报告生成完成: 总收益={basic_metrics.get('total_return', 0):.2%}, "
                        f"夏普={risk_adjusted_metrics.get('sharpe_ratio', 0):.2f}, "
                        f"胜率={trade_metrics.get('win_rate', 0):.2%}")
        
        return comprehensive_report
    
    def _generate_summary(self, basic_metrics: Dict[str, Any], 
                         risk_adjusted_metrics: Dict[str, Any],
                         trade_metrics: Dict[str, Any]) -> Dict[str, Any]:
        """生成绩效摘要
        
        Args:
            basic_metrics: 基本指标
            risk_adjusted_metrics: 风险调整后指标
            trade_metrics: 交易指标
            
        Returns:
            Dict[str, Any]: 绩效摘要
        """
        # 评估绩效质量
        performance_quality = 'poor'
        
        sharpe_ratio = risk_adjusted_metrics.get('sharpe_ratio', 0)
        total_return = basic_metrics.get('total_return', 0)
        win_rate = trade_metrics.get('win_rate', 0)
        max_drawdown = risk_adjusted_metrics.get('max_drawdown', 1)  # 注意: 这里需要最大回撤数据
        
        # 简单评估逻辑
        if sharpe_ratio > 1.5 and total_return > 0.2 and win_rate > 0.6:
            performance_quality = 'excellent'
        elif sharpe_ratio > 1.0 and total_return > 0.1 and win_rate > 0.5:
            performance_quality = 'good'
        elif sharpe_ratio > 0.5 and total_return > 0:
            performance_quality = 'fair'
        elif total_return > 0:
            performance_quality = 'poor'
        else:
            performance_quality = 'very_poor'
        
        # 生成建议
        recommendations = []
        
        if sharpe_ratio < 0.5:
            recommendations.append("夏普比率较低，建议优化风险调整后收益")
        
        if win_rate < 0.4:
            recommendations.append("胜率较低，建议提高信号质量或优化入场时机")
        
        if trade_metrics.get('profit_factor', 0) < 1.5:
            recommendations.append("盈亏比较低，建议提高平均盈利或降低平均亏损")
        
        if not recommendations:
            recommendations.append("当前策略表现良好，建议继续执行并监控")
        
        summary = {
            'performance_quality': performance_quality,
            'key_strengths': [],
            'key_weaknesses': [],
            'recommendations': recommendations,
            'overall_rating': self._calculate_overall_rating(basic_metrics, risk_adjusted_metrics, trade_metrics)
        }
        
        # 识别关键优势和弱点
        if sharpe_ratio > 1.0:
            summary['key_strengths'].append(f"良好的风险调整后收益 (夏普比率: {sharpe_ratio:.2f})")
        
        if win_rate > 0.6:
            summary['key_strengths'].append(f"较高的胜率 ({win_rate:.2%})")
        
        if total_return > 0.15:
            summary['key_strengths'].append(f"优秀的绝对收益 ({total_return:.2%})")
        
        if sharpe_ratio < 0:
            summary['key_weaknesses'].append("负的夏普比率，风险调整后收益为负")
        
        if total_return < 0:
            summary['key_weaknesses'].append("负的总收益")
        
        if win_rate < 0.3:
            summary['key_weaknesses'].append(f"较低的胜率 ({win_rate:.2%})")
        
        return summary
    
    def _calculate_overall_rating(self, basic_metrics: Dict[str, Any], 
                                risk_adjusted_metrics: Dict[str, Any],
                                trade_metrics: Dict[str, Any]) -> float:
        """计算总体评分 (0-10分)
        
        Args:
            basic_metrics: 基本指标
            risk_adjusted_metrics: 风险调整后指标
            trade_metrics: 交易指标
            
        Returns:
            float: 总体评分
        """
        total_score = 0
        max_score = 0
        
        # 收益评分 (权重: 40%)
        total_return = basic_metrics.get('total_return', 0)
        return_score = min(4.0, max(0, total_return * 10))  # 每10%收益得1分，最多4分
        total_score += return_score
        max_score += 4
        
        # 风险调整后收益评分 (权重: 30%)
        sharpe_ratio = risk_adjusted_metrics.get('sharpe_ratio', 0)
        sharpe_score = min(3.0, max(0, sharpe_ratio))  # 夏普比率直接作为分数，最多3分
        total_score += sharpe_score
        max_score += 3
        
        # 交易质量评分 (权重: 30%)
        win_rate = trade_metrics.get('win_rate', 0)
        profit_factor = trade_metrics.get('profit_factor', 0)
        
        win_rate_score = min(1.5, win_rate * 1.5)  # 胜率评分
        profit_factor_score = min(1.5, (profit_factor - 1) * 0.75)  # 盈亏比评分
        
        trade_score = win_rate_score + profit_factor_score
        total_score += trade_score
        max_score += 3
        
        # 计算最终评分
        if max_score > 0:
            overall_rating = (total_score / max_score) * 10
        else:
            overall_rating = 0
        
        return round(overall_rating, 1)


def demo_performance_analysis():
    """演示绩效分析功能"""
    print("=" * 80)
    print("绩效分析模块演示")
    print("=" * 80)
    
    # 创建绩效分析器
    analyzer = PerformanceAnalyzer(risk_free_rate=0.02)
    
    # 生成示例数据
    np.random.seed(42)
    days = 252  # 一年交易日
    initial_equity = 100000
    
    # 生成随机收益率
    daily_returns = np.random.normal(0.0005, 0.02, days)
    
    # 生成权益曲线
    equity_curve = initial_equity * np.cumprod(1 + daily_returns)
    equity_curve_list = equity_curve.tolist()
    
    # 生成日期
    start_date = datetime(2023, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(days)]
    
    # 生成示例交易
    trades = []
    for i in range(0, days, 20):  # 每20天交易一次
        if i + 10 < days:
            # 买入交易
            trades.append({
                'date': dates[i],
                'symbol': 'TEST001.SZ',
                'action': 'buy',
                'price': equity_curve_list[i] / 1000,  # 简化价格
                'quantity': 100
            })
            
            # 卖出交易
            trades.append({
                'date': dates[i + 10],
                'symbol': 'TEST001.SZ',
                'action': 'sell',
                'price': equity_curve_list[i + 10] / 1000,
                'quantity': 100
            })
    
    # 生成基准收益率
    benchmark_returns = np.random.normal(0.0003, 0.015, days)
    
    print("\n1. 基本绩效指标:")
    basic_metrics = analyzer.calculate_basic_metrics(equity_curve_list, dates)
    print(f"   初始资金: {basic_metrics.get('initial_equity', 0):,.2f}")
    print(f"   最终权益: {basic_metrics.get('final_equity', 0):,.2f}")
    print(f"   总收益率: {basic_metrics.get('total_return', 0):.2%}")
    print(f"   年化收益率: {basic_metrics.get('annualized_return', 0):.2%}")
    print(f"   波动率: {basic_metrics.get('std_daily_return', 0):.4f}")
    
    print("\n2. 风险调整后指标:")
    risk_metrics = analyzer.calculate_risk_adjusted_metrics(equity_curve_list, dates, benchmark_returns)
    print(f"   夏普比率: {risk_metrics.get('sharpe_ratio', 0):.3f}")
    print(f"   索提诺比率: {risk_metrics.get('sortino_ratio', 0):.3f}")
    print(f"   卡玛比率: {risk_metrics.get('calmar_ratio', 0):.3f}")
    print(f"   信息比率: {risk_metrics.get('information_ratio', 0):.3f}")
    
    print("\n3. 最大回撤分析:")
    drawdown_info = analyzer.calculate_max_drawdown(equity_curve_list)
    print(f"   最大回撤: {drawdown_info.get('max_drawdown', 0):.2%}")
    print(f"   回撤期: {drawdown_info.get('drawdown_period', 0)} 天")
    print(f"   恢复期: {drawdown_info.get('recovery_period', 0)} 天")
    
    print("\n4. 交易指标:")
    trade_metrics = analyzer.calculate_trade_metrics(trades)
    print(f"   总交易次数: {trade_metrics.get('total_trades', 0)}")
    print(f"   胜率: {trade_metrics.get('win_rate', 0):.2%}")
    print(f"   盈亏比: {trade_metrics.get('profit_factor', 0):.2f}")
    print(f"   平均盈利: {trade_metrics.get('avg_win', 0):.2f}")
    print(f"   平均亏损: {trade_metrics.get('avg_loss', 0):.2f}")
    print(f"   期望值: {trade_metrics.get('expectancy', 0):.2f}")
    
    print("\n5. 基准比较:")
    daily_returns_array = analyzer._calculate_daily_returns(np.array(equity_curve_list))
    benchmark_comparison = analyzer.calculate_benchmark_comparison(daily_returns_array, benchmark_returns)
    print(f"   阿尔法: {benchmark_comparison.get('alpha', 0):.4f}")
    print(f"   贝塔: {benchmark_comparison.get('beta', 0):.3f}")
    print(f"   R-squared: {benchmark_comparison.get('r_squared', 0):.3f}")
    print(f"   跟踪误差: {benchmark_comparison.get('tracking_error', 0):.4f}")
    
    print("\n6. 全面报告:")
    comprehensive_report = analyzer.generate_comprehensive_report(
        equity_curve_list, trades, dates, benchmark_returns
    )
    
    summary = comprehensive_report.get('summary', {})
    print(f"   绩效质量: {summary.get('performance_quality', 'unknown')}")
    print(f"   总体评分: {summary.get('overall_rating', 0):.1f}/10")
    
    print("\n   建议:")
    for i, rec in enumerate(summary.get('recommendations', []), 1):
        print(f"     {i}. {rec}")
    
    print("\n" + "=" * 80)
    print("演示完成")


if __name__ == "__main__":
    # 运行演示
    demo_performance_analysis()