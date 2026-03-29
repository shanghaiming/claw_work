#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格行为整合框架回测系统
测试优化引擎 + 规则整合器的交易性能
"""

import numpy as np
import pandas as pd
import json
import os
import sys
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# 添加当前目录到路径
sys.path.append('.')

from optimized_integration_engine import OptimizedPriceActionIntegrationEngine
from price_action_rules_integrator import PriceActionRulesIntegrator


class BacktestSystem:
    """
    回测系统
    评估价格行为整合框架的交易性能
    """
    
    def __init__(self, initial_capital: float = 100000.0):
        """初始化回测系统"""
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions = []  # 当前持仓
        self.trades = []     # 已完成交易
        self.equity_curve = []  # 权益曲线
        self.daily_pnl = []     # 每日盈亏
        
        # 交易参数
        self.commission_rate = 0.001  # 交易佣金率（0.1%）
        self.slippage = 0.001         # 滑点（0.1%）
        self.max_position_pct = 0.1   # 最大仓位比例（10%）
        
        # 性能指标
        self.performance_metrics = {}
        
        # 引擎实例
        self.engine = None
        self.integrator = None
    
    def prepare_engines(self):
        """准备分析引擎"""
        self.engine = OptimizedPriceActionIntegrationEngine()
        self.integrator = PriceActionRulesIntegrator()
    
    def run_backtest(self, price_data: pd.DataFrame, 
                    lookback_days: int = 100,
                    step_days: int = 5) -> Dict[str, Any]:
        """
        运行回测
        
        参数:
            price_data: 完整价格数据
            lookback_days: 分析回溯天数
            step_days: 步进天数
            
        返回:
            回测结果
        """
        print("=" * 60)
        print("开始回测价格行为整合框架")
        print("=" * 60)
        
        # 重置状态
        self._reset_state()
        
        # 准备引擎
        self.prepare_engines()
        
        # 获取日期索引
        dates = price_data.index
        start_idx = lookback_days
        
        total_steps = len(range(start_idx, len(dates), step_days))
        current_step = 0
        
        print(f"回测参数:")
        print(f"  初始资金: ${self.initial_capital:,.2f}")
        print(f"  数据范围: {dates[0].date()} 到 {dates[-1].date()}")
        print(f"  回溯天数: {lookback_days}")
        print(f"  步进天数: {step_days}")
        print(f"  总步数: {total_steps}")
        print()
        
        # 主回测循环
        for i in range(start_idx, len(dates), step_days):
            current_step += 1
            current_date = dates[i]
            
            # 提取回溯数据
            lookback_data = price_data.iloc[max(0, i-lookback_days):i+1].copy()
            
            if len(lookback_data) < 50:  # 最少需要50个数据点
                continue
            
            # 更新进度
            if current_step % 20 == 0 or current_step == total_steps:
                progress = current_step / total_steps * 100
                print(f"进度: {current_step}/{total_steps} ({progress:.1f}%) - {current_date.date()}")
            
            # 1. 运行分析引擎
            try:
                self.engine.load_data(lookback_data)
                analysis_results = self.engine.run_analysis()
            except Exception as e:
                print(f"分析引擎错误 ({current_date.date()}): {e}")
                continue
            
            # 2. 运行规则整合器
            try:
                enhanced_results = self.integrator.integrate_rules(analysis_results, lookback_data)
            except Exception as e:
                print(f"规则整合器错误 ({current_date.date()}): {e}")
                continue
            
            # 3. 生成交易决策
            trading_decisions = self._generate_trading_decisions(
                enhanced_results, 
                lookback_data,
                current_date
            )
            
            # 4. 执行交易
            self._execute_trades(trading_decisions, lookback_data, current_date)
            
            # 5. 更新持仓市值
            self._update_positions(lookback_data, current_date)
            
            # 6. 记录权益曲线
            self._record_equity(current_date)
        
        # 计算性能指标
        self._calculate_performance_metrics(price_data)
        
        # 生成回测报告
        report = self._generate_backtest_report()
        
        print("\n" + "=" * 60)
        print("回测完成!")
        print("=" * 60)
        
        return report
    
    def _reset_state(self):
        """重置回测状态"""
        self.capital = self.initial_capital
        self.positions = []
        self.trades = []
        self.equity_curve = []
        self.daily_pnl = []
        self.performance_metrics = {}
    
    def _generate_trading_decisions(self, enhanced_results: Dict[str, Any],
                                   price_data: pd.DataFrame,
                                   current_date: datetime) -> List[Dict[str, Any]]:
        """
        生成交易决策
        """
        decisions = []
        
        # 获取当前价格
        current_price = price_data['close'].iloc[-1] if len(price_data) > 0 else 0
        
        # 1. 检查是否有需要平仓的持仓
        for position in self.positions:
            exit_decision = self._check_exit_conditions(position, enhanced_results, current_price, current_date)
            if exit_decision:
                decisions.append(exit_decision)
        
        # 2. 检查是否有新入场信号
        entry_signals = enhanced_results.get('price_action_signals', {}).get('entry_signals', [])
        
        for signal in entry_signals:
            # 过滤低质量信号
            if signal.get('confidence', 0) < 0.6:
                continue
            
            # 检查是否已经有类似持仓
            if self._has_similar_position(signal):
                continue
            
            # 生成入场决策
            entry_decision = self._create_entry_decision(signal, enhanced_results, current_price, current_date)
            if entry_decision:
                decisions.append(entry_decision)
        
        return decisions
    
    def _check_exit_conditions(self, position: Dict[str, Any],
                              enhanced_results: Dict[str, Any],
                              current_price: float,
                              current_date: datetime) -> Optional[Dict[str, Any]]:
        """
        检查出场条件
        """
        position_type = position.get('type', '')  # 'long' or 'short'
        entry_price = position.get('entry_price', 0)
        stop_loss = position.get('stop_loss', 0)
        take_profit = position.get('take_profit', 0)
        position_size = position.get('size', 0)
        
        if position_size == 0:
            return None
        
        # 1. 止损检查
        if position_type == 'long' and current_price <= stop_loss:
            return {
                'action': 'exit',
                'position_id': position.get('id'),
                'reason': 'stop_loss',
                'price': current_price,
                'date': current_date
            }
        elif position_type == 'short' and current_price >= stop_loss:
            return {
                'action': 'exit',
                'position_id': position.get('id'),
                'reason': 'stop_loss',
                'price': current_price,
                'date': current_date
            }
        
        # 2. 止盈检查
        if position_type == 'long' and current_price >= take_profit:
            return {
                'action': 'exit',
                'position_id': position.get('id'),
                'reason': 'take_profit',
                'price': current_price,
                'date': current_date
            }
        elif position_type == 'short' and current_price <= take_profit:
            return {
                'action': 'exit',
                'position_id': position.get('id'),
                'reason': 'take_profit',
                'price': current_price,
                'date': current_date
            }
        
        # 3. 基于规则整合器的出场信号
        exit_signals = enhanced_results.get('price_action_signals', {}).get('exit_signals', [])
        for signal in exit_signals:
            # 简化版：如果信号与持仓方向相反，考虑出场
            signal_type = signal.get('type', '')
            if (position_type == 'long' and 'sell' in signal_type) or \
               (position_type == 'short' and 'buy' in signal_type):
                return {
                    'action': 'exit',
                    'position_id': position.get('id'),
                    'reason': 'signal_based_exit',
                    'price': current_price,
                    'date': current_date
                }
        
        return None
    
    def _has_similar_position(self, signal: Dict[str, Any]) -> bool:
        """
        检查是否有类似持仓
        """
        signal_type = signal.get('type', '')
        level_price = signal.get('level_price', 0)
        
        for position in self.positions:
            position_type = position.get('type', '')
            entry_price = position.get('entry_price', 0)
            
            # 如果持仓方向相同且入场价相近，认为是类似持仓
            if ('buy' in signal_type and position_type == 'long') or \
               ('sell' in signal_type and position_type == 'short'):
                price_diff_pct = abs(entry_price - level_price) / level_price
                if price_diff_pct < 0.03:  # 价格相差小于3%
                    return True
        
        return False
    
    def _create_entry_decision(self, signal: Dict[str, Any],
                              enhanced_results: Dict[str, Any],
                              current_price: float,
                              current_date: datetime) -> Optional[Dict[str, Any]]:
        """
        创建入场决策
        """
        signal_type = signal.get('type', '')
        level_price = signal.get('level_price', 0)
        confidence = signal.get('confidence', 0)
        
        # 确定交易方向
        if 'buy' in signal_type:
            position_type = 'long'
            entry_price = level_price * 0.995  # 在支撑位下方0.5%入场
        elif 'sell' in signal_type:
            position_type = 'short'
            entry_price = level_price * 1.005  # 在阻力位上方0.5%入场
        else:
            return None
        
        # 获取风险参数
        risk_params = enhanced_results.get('risk_parameters', {})
        signal_id = f"{signal_type}_{level_price:.2f}"
        
        stop_loss = risk_params.get('stop_loss_levels', {}).get(signal_id, 0)
        take_profits = risk_params.get('take_profit_levels', {}).get(signal_id, {})
        position_info = risk_params.get('position_sizing', {}).get(signal_id, {})
        
        # 使用第一目标位作为止盈
        take_profit = take_profits.get('tp1', entry_price * (1.03 if position_type == 'long' else 0.97))
        
        # 计算仓位规模
        position_size = self._calculate_position_size(
            entry_price, stop_loss, position_type, confidence
        )
        
        if position_size == 0:
            return None
        
        return {
            'action': 'enter',
            'type': position_type,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'size': position_size,
            'confidence': confidence,
            'signal': signal,
            'date': current_date
        }
    
    def _calculate_position_size(self, entry_price: float, stop_loss: float,
                                position_type: str, confidence: float) -> float:
        """
        计算仓位规模
        """
        # 计算风险金额（单笔交易最大风险2%）
        max_risk_amount = self.capital * 0.02
        
        # 计算每单位风险
        if position_type == 'long':
            risk_per_unit = entry_price - stop_loss
        else:  # short
            risk_per_unit = stop_loss - entry_price
        
        if risk_per_unit <= 0:
            return 0
        
        # 基础仓位
        base_position = max_risk_amount / risk_per_unit
        
        # 根据置信度调整
        adjusted_position = base_position * confidence
        
        # 根据最大仓位比例限制
        max_position_value = self.capital * self.max_position_pct
        max_position_units = max_position_value / entry_price
        
        final_position = min(adjusted_position, max_position_units)
        
        # 取整
        return round(final_position)
    
    def _execute_trades(self, decisions: List[Dict[str, Any]],
                       price_data: pd.DataFrame,
                       current_date: datetime):
        """
        执行交易
        """
        for decision in decisions:
            if decision['action'] == 'enter':
                self._execute_entry(decision, price_data, current_date)
            elif decision['action'] == 'exit':
                self._execute_exit(decision, price_data, current_date)
    
    def _execute_entry(self, decision: Dict[str, Any],
                      price_data: pd.DataFrame,
                      current_date: datetime):
        """
        执行入场
        """
        position_type = decision['type']
        entry_price = decision['entry_price']
        stop_loss = decision['stop_loss']
        take_profit = decision['take_profit']
        size = decision['size']
        
        # 计算交易成本
        trade_value = entry_price * size
        commission = trade_value * self.commission_rate
        slippage_cost = trade_value * self.slippage
        
        # 检查资金是否足够
        if position_type == 'long':
            total_cost = trade_value + commission + slippage_cost
            if total_cost > self.capital:
                # 资金不足，减小仓位
                size = int(self.capital / (entry_price * (1 + self.commission_rate + self.slippage)))
                if size == 0:
                    return
                trade_value = entry_price * size
                commission = trade_value * self.commission_rate
                slippage_cost = trade_value * self.slippage
                total_cost = trade_value + commission + slippage_cost
        
        # 更新资金
        if position_type == 'long':
            self.capital -= total_cost
        else:  # short (简化处理，不考虑保证金)
            # 空头交易需要保证金，这里简化处理
            margin_required = trade_value * 0.5  # 50%保证金
            if margin_required > self.capital:
                return
            self.capital -= commission + slippage_cost  # 只扣除费用
        
        # 创建持仓
        position_id = f"pos_{len(self.positions)}_{current_date.strftime('%Y%m%d')}"
        
        position = {
            'id': position_id,
            'type': position_type,
            'entry_date': current_date,
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'size': size,
            'commission': commission,
            'slippage': slippage_cost,
            'signal': decision.get('signal', {})
        }
        
        self.positions.append(position)
        
        # 记录交易
        trade = {
            'type': 'entry',
            'position_id': position_id,
            'date': current_date,
            'price': entry_price,
            'size': size,
            'direction': position_type,
            'commission': commission,
            'slippage': slippage_cost,
            'signal_confidence': decision.get('confidence', 0)
        }
        
        self.trades.append(trade)
    
    def _execute_exit(self, decision: Dict[str, Any],
                     price_data: pd.DataFrame,
                     current_date: datetime):
        """
        执行出场
        """
        position_id = decision['position_id']
        exit_price = decision['price']
        exit_reason = decision['reason']
        
        # 查找持仓
        position_idx = -1
        position = None
        for i, pos in enumerate(self.positions):
            if pos['id'] == position_id:
                position_idx = i
                position = pos
                break
        
        if position is None:
            return
        
        # 计算盈亏
        entry_price = position['entry_price']
        size = position['size']
        position_type = position['type']
        
        if position_type == 'long':
            pnl = (exit_price - entry_price) * size
        else:  # short
            pnl = (entry_price - exit_price) * size
        
        # 扣除交易成本
        trade_value = exit_price * size
        commission = trade_value * self.commission_rate
        slippage_cost = trade_value * self.slippage
        
        net_pnl = pnl - commission - slippage_cost
        
        # 更新资金
        if position_type == 'long':
            # 多头平仓：收回市值并加上盈亏
            self.capital += trade_value + net_pnl
        else:
            # 空头平仓：收回保证金并加上盈亏
            self.capital += net_pnl + (trade_value * 0.5)  # 简化处理
        
        # 记录交易
        trade = {
            'type': 'exit',
            'position_id': position_id,
            'date': current_date,
            'price': exit_price,
            'size': size,
            'direction': position_type,
            'pnl': pnl,
            'net_pnl': net_pnl,
            'commission': commission,
            'slippage': slippage_cost,
            'exit_reason': exit_reason,
            'holding_days': (current_date - position['entry_date']).days
        }
        
        self.trades.append(trade)
        
        # 移除持仓
        if position_idx >= 0:
            del self.positions[position_idx]
    
    def _update_positions(self, price_data: pd.DataFrame, current_date: datetime):
        """更新持仓市值（用于计算权益曲线）"""
        # 这个简化版本中，我们已经在执行交易时更新了资金
        # 这里可以添加更复杂的持仓市值计算
        pass
    
    def _record_equity(self, current_date: datetime):
        """记录权益曲线"""
        # 计算总权益：现金 + 持仓市值
        total_equity = self.capital
        
        # 这里可以添加持仓市值计算
        # 简化版：只记录现金
        self.equity_curve.append({
            'date': current_date,
            'equity': total_equity,
            'capital': self.capital,
            'positions': len(self.positions)
        })
        
        # 计算每日盈亏
        if len(self.equity_curve) > 1:
            prev_equity = self.equity_curve[-2]['equity']
            daily_pnl = total_equity - prev_equity
            daily_return = daily_pnl / prev_equity if prev_equity > 0 else 0
        else:
            daily_pnl = 0
            daily_return = 0
        
        self.daily_pnl.append({
            'date': current_date,
            'pnl': daily_pnl,
            'return': daily_return
        })
    
    def _calculate_performance_metrics(self, price_data: pd.DataFrame):
        """计算性能指标"""
        if not self.equity_curve:
            return
        
        # 提取权益数据
        equity_dates = [e['date'] for e in self.equity_curve]
        equity_values = [e['equity'] for e in self.equity_curve]
        
        # 计算收益
        returns = []
        for i in range(1, len(equity_values)):
            if equity_values[i-1] > 0:
                ret = (equity_values[i] - equity_values[i-1]) / equity_values[i-1]
                returns.append(ret)
        
        if not returns:
            return
        
        # 基本指标
        total_return = (equity_values[-1] - self.initial_capital) / self.initial_capital
        annual_return = total_return / (len(equity_values) / 252) if len(equity_values) > 252 else total_return
        
        # 风险指标
        volatility = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 回撤
        running_max = np.maximum.accumulate(equity_values)
        drawdowns = (equity_values - running_max) / running_max
        max_drawdown = np.min(drawdowns) if len(drawdowns) > 0 else 0
        
        # 交易统计
        total_trades = len([t for t in self.trades if t['type'] == 'exit'])
        winning_trades = len([t for t in self.trades if t['type'] == 'exit' and t.get('net_pnl', 0) > 0])
        losing_trades = total_trades - winning_trades
        
        win_rate = winning_trades / total_trades if total_trades > 0 else 0
        
        # 平均盈亏
        winning_pnls = [t.get('net_pnl', 0) for t in self.trades if t['type'] == 'exit' and t.get('net_pnl', 0) > 0]
        losing_pnls = [t.get('net_pnl', 0) for t in self.trades if t['type'] == 'exit' and t.get('net_pnl', 0) < 0]
        
        avg_win = np.mean(winning_pnls) if winning_pnls else 0
        avg_loss = np.mean(losing_pnls) if losing_pnls else 0
        profit_factor = abs(sum(winning_pnls) / sum(losing_pnls)) if sum(losing_pnls) != 0 else float('inf')
        
        # 持仓统计
        holding_periods = [t.get('holding_days', 0) for t in self.trades if t['type'] == 'exit']
        avg_holding_period = np.mean(holding_periods) if holding_periods else 0
        
        self.performance_metrics = {
            'initial_capital': self.initial_capital,
            'final_capital': equity_values[-1],
            'total_return': float(total_return),
            'annual_return': float(annual_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': float(win_rate),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': float(profit_factor),
            'avg_holding_period': float(avg_holding_period),
            'total_commission': sum(t.get('commission', 0) for t in self.trades),
            'total_slippage': sum(t.get('slippage', 0) for t in self.trades)
        }
    
    def _generate_backtest_report(self) -> Dict[str, Any]:
        """生成回测报告"""
        report = {
            'summary': {
                'backtest_period': {
                    'start': self.equity_curve[0]['date'] if self.equity_curve else None,
                    'end': self.equity_curve[-1]['date'] if self.equity_curve else None,
                    'days': len(self.equity_curve)
                },
                'performance_summary': self.performance_metrics
            },
            'equity_curve': self.equity_curve[-100:] if len(self.equity_curve) > 100 else self.equity_curve,  # 只保存最后100个点
            'trades': self.trades[-50:] if len(self.trades) > 50 else self.trades,  # 只保存最后50笔交易
            'analysis': {
                'performance_interpretation': self._interpret_performance(),
                'strengths': self._identify_strengths(),
                'weaknesses': self._identify_weaknesses(),
                'improvement_suggestions': self._suggest_improvements()
            }
        }
        
        return report
    
    def _interpret_performance(self) -> List[str]:
        """解释性能指标"""
        interpretations = []
        
        metrics = self.performance_metrics
        
        # 总收益解释
        total_return = metrics.get('total_return', 0)
        if total_return > 0.2:
            interpretations.append(f"优秀的总收益: {total_return:.1%}，显著超越市场平均")
        elif total_return > 0:
            interpretations.append(f"正的总收益: {total_return:.1%}，但仍有提升空间")
        else:
            interpretations.append(f"负的总收益: {total_return:.1%}，需要优化策略")
        
        # 夏普比率解释
        sharpe = metrics.get('sharpe_ratio', 0)
        if sharpe > 1.5:
            interpretations.append(f"优秀的风险调整收益: 夏普比率 {sharpe:.2f}")
        elif sharpe > 0.5:
            interpretations.append(f"可接受的风险调整收益: 夏普比率 {sharpe:.2f}")
        else:
            interpretations.append(f"较差的风险调整收益: 夏普比率 {sharpe:.2f}")
        
        # 胜率解释
        win_rate = metrics.get('win_rate', 0)
        if win_rate > 0.6:
            interpretations.append(f"高胜率: {win_rate:.1%}，交易一致性较好")
        elif win_rate > 0.4:
            interpretations.append(f"中等胜率: {win_rate:.1%}，需要提高信号质量")
        else:
            interpretations.append(f"低胜率: {win_rate:.1%}，需要重新评估入场策略")
        
        # 最大回撤解释
        max_dd = metrics.get('max_drawdown', 0)
        if abs(max_dd) < 0.1:
            interpretations.append(f"优秀的风险控制: 最大回撤仅 {abs(max_dd):.1%}")
        elif abs(max_dd) < 0.2:
            interpretations.append(f"可接受的风险控制: 最大回撤 {abs(max_dd):.1%}")
        else:
            interpretations.append(f"风险控制需要加强: 最大回撤达 {abs(max_dd):.1%}")
        
        return interpretations
    
    def _identify_strengths(self) -> List[str]:
        """识别优势"""
        strengths = []
        metrics = self.performance_metrics
        
        # 基于绩效指标识别优势
        if metrics.get('win_rate', 0) > 0.55:
            strengths.append("高胜率策略，交易一致性较好")
        
        if metrics.get('profit_factor', 0) > 1.5:
            strengths.append("盈亏比较高，盈利交易显著超过亏损交易")
        
        if abs(metrics.get('max_drawdown', 0)) < 0.15:
            strengths.append("优秀的风险控制，回撤较小")
        
        if metrics.get('total_trades', 0) > 20:
            strengths.append("充分的交易样本，结果具有统计意义")
        
        return strengths
    
    def _identify_weaknesses(self) -> List[str]:
        """识别弱点"""
        weaknesses = []
        metrics = self.performance_metrics
        
        # 基于绩效指标识别弱点
        if metrics.get('total_return', 0) < 0:
            weaknesses.append("总收益为负，策略需要根本性改进")
        
        if metrics.get('sharpe_ratio', 0) < 0.5:
            weaknesses.append("风险调整收益较差，单位风险收益低")
        
        if metrics.get('win_rate', 0) < 0.4 and metrics.get('total_trades', 0) > 10:
            weaknesses.append("胜率过低，入场信号质量有待提高")
        
        if metrics.get('avg_holding_period', 0) < 1:
            weaknesses.append("持仓时间过短，可能过度交易")
        
        return weaknesses
    
    def _suggest_improvements(self) -> List[str]:
        """提出改进建议"""
        suggestions = []
        metrics = self.performance_metrics
        
        # 基于弱点提出改进建议
        if metrics.get('total_return', 0) < 0:
            suggestions.append("优化入场信号筛选条件，提高信号质量")
            suggestions.append("调整风险管理参数，减少亏损交易的影响")
        
        if metrics.get('sharpe_ratio', 0) < 0.5:
            suggestions.append("降低策略波动性，增加过滤条件减少虚假信号")
            suggestions.append("优化仓位管理，根据市场波动调整仓位规模")
        
        if metrics.get('win_rate', 0) < 0.4:
            suggestions.append("增加信号确认条件，避免过早入场")
            suggestions.append("结合更多技术指标或价格行为模式进行确认")
        
        if metrics.get('max_drawdown', 0) < -0.2:
            suggestions.append("设置更严格的止损规则，控制单笔损失")
            suggestions.append("在市场不利时减小仓位或暂停交易")
        
        # 通用建议
        suggestions.append("定期回顾和优化策略参数")
        suggestions.append("在不同市场环境下测试策略适应性")
        suggestions.append("考虑加入资金管理规则，如根据权益曲线调整风险")
        
        return suggestions


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函数"""
    print("价格行为整合框架回测系统")
    print("版本: 1.0")
    print("=" * 60)
    
    # 生成测试数据
    print("\n生成回测数据...")
    dates = pd.date_range('2023-01-01', periods=500, freq='D')
    np.random.seed(42)
    
    # 生成更复杂的模拟数据，包含不同市场状态
    base_price = 100
    
    # 分段生成不同市场状态
    segments = [
        ('trend_up', 100, 0.0005),    # 上升趋势
        ('range', 50, 0),             # 区间震荡
        ('trend_down', 100, -0.0004), # 下降趋势
        ('volatile', 150, 0.0001),    # 高波动
        ('trend_up', 100, 0.0003)     # 再次上升
    ]
    
    closes = []
    current_price = base_price
    
    for segment_name, length, trend_strength in segments:
        for i in range(length):
            # 趋势成分
            trend = trend_strength * i
            
            # 波动成分
            if segment_name == 'volatile':
                volatility = 0.02
            else:
                volatility = 0.01
            
            noise = np.random.normal(0, volatility)
            
            # 周期成分（仅区间阶段明显）
            if segment_name == 'range':
                cycle = 0.02 * np.sin(2 * np.pi * i / 20)
            else:
                cycle = 0
            
            price_change = trend + cycle + noise
            current_price *= (1 + price_change)
            closes.append(current_price)
    
    # 生成OHLCV数据
    closes = np.array(closes)
    opens = closes - np.random.uniform(0.5, 2.0, len(closes))
    highs = closes + np.random.uniform(0.5, 3.0, len(closes))
    lows = closes - np.random.uniform(0.5, 3.0, len(closes))
    volumes = np.random.lognormal(10, 0.8, len(closes)) * 1000
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=dates[:len(closes)])
    
    print(f"回测数据生成成功: {len(df)} 行, {df.index[0].date()} 到 {df.index[-1].date()}")
    
    # 创建回测系统
    backtester = BacktestSystem(initial_capital=100000.0)
    
    # 运行回测
    report = backtester.run_backtest(
        price_data=df,
        lookback_days=100,
        step_days=3
    )
    
    # 保存报告
    os.makedirs("backtest_results", exist_ok=True)
    
    with open("backtest_results/backtest_report.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, default=str, ensure_ascii=False)
    
    print(f"\n回测报告已保存到: backtest_results/backtest_report.json")
    
    # 打印关键指标
    print("\n" + "=" * 60)
    print("回测关键指标")
    print("=" * 60)
    
    metrics = report['summary']['performance_summary']
    
    print(f"初始资金: ${metrics['initial_capital']:,.2f}")
    print(f"最终资金: ${metrics['final_capital']:,.2f}")
    print(f"总收益率: {metrics['total_return']:.2%}")
    print(f"年化收益率: {metrics['annual_return']:.2%}")
    print(f"波动率: {metrics['volatility']:.2%}")
    print(f"夏普比率: {metrics['sharpe_ratio']:.2f}")
    print(f"最大回撤: {metrics['max_drawdown']:.2%}")
    print(f"总交易次数: {metrics['total_trades']}")
    print(f"胜率: {metrics['win_rate']:.2%}")
    print(f"平均盈利: ${metrics['avg_win']:.2f}")
    print(f"平均亏损: ${metrics['avg_loss']:.2f}")
    print(f"盈亏比: {metrics['profit_factor']:.2f}")
    
    # 打印分析
    print("\n" + "=" * 60)
    print("性能分析")
    print("=" * 60)
    
    for interpretation in report['analysis']['performance_interpretation']:
        print(f"• {interpretation}")
    
    print("\n优势:")
    for strength in report['analysis']['strengths']:
        print(f"• {strength}")
    
    print("\n弱点:")
    for weakness in report['analysis']['weaknesses']:
        print(f"• {weakness}")
    
    print("\n改进建议:")
    for suggestion in report['analysis']['improvement_suggestions']:
        print(f"• {suggestion}")
    
    print("\n" + "=" * 60)
    print("✅ 回测完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()