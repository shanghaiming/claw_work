#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
风险管理模块 - 阶段4.4：回测层集成

提供全面的风险管理功能:
1. 仓位风险管理
2. 组合风险管理
3. 止损和止盈策略
4. 风险指标监控
5. 风险报告生成
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import warnings
import logging

warnings.filterwarnings('ignore')


class RiskManager:
    """
    风险管理器
    提供全面的风险管理功能
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化风险管理器
        
        Args:
            config: 风险配置字典，包含:
                - max_position_risk: 单笔交易最大风险比例 (默认: 0.02, 2%)
                - max_portfolio_risk: 投资组合最大风险比例 (默认: 0.1, 10%)
                - max_drawdown_limit: 最大回撤限制 (默认: 0.2, 20%)
                - stop_loss_pct: 止损百分比 (默认: 0.05, 5%)
                - take_profit_pct: 止盈百分比 (默认: 0.1, 10%)
                - volatility_window: 波动率计算窗口 (默认: 20)
                - correlation_window: 相关性计算窗口 (默认: 60)
                - risk_free_rate: 无风险利率 (默认: 0.02)
        """
        self.config = config or {}
        
        # 风险参数
        self.max_position_risk = self.config.get('max_position_risk', 0.02)  # 2%
        self.max_portfolio_risk = self.config.get('max_portfolio_risk', 0.1)  # 10%
        self.max_drawdown_limit = self.config.get('max_drawdown_limit', 0.2)  # 20%
        self.stop_loss_pct = self.config.get('stop_loss_pct', 0.05)  # 5%
        self.take_profit_pct = self.config.get('take_profit_pct', 0.1)  # 10%
        self.volatility_window = self.config.get('volatility_window', 20)
        self.correlation_window = self.config.get('correlation_window', 60)
        self.risk_free_rate = self.config.get('risk_free_rate', 0.02)
        
        # 风险状态
        self.current_risk_level = 'low'  # low, medium, high
        self.risk_alerts = []
        self.risk_history = []
        
        # 日志
        self.logger = self._setup_logger()
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"RiskManager_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        logger.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        return logger
    
    def calculate_position_size(self, entry_price: float, stop_loss_price: float, 
                              account_size: float, risk_per_trade: Optional[float] = None) -> Tuple[int, float]:
        """计算基于风险的仓位大小
        
        Args:
            entry_price: 入场价格
            stop_loss_price: 止损价格
            account_size: 账户总资金
            risk_per_trade: 单笔交易风险比例 (默认使用max_position_risk)
            
        Returns:
            Tuple[int, float]: (股份数量, 实际风险金额)
        """
        if risk_per_trade is None:
            risk_per_trade = self.max_position_risk
        
        # 计算每股风险
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk <= 0 or entry_price <= 0:
            self.logger.warning("无效的价格参数，无法计算仓位")
            return 0, 0
        
        # 计算风险金额
        risk_amount = account_size * risk_per_trade
        
        # 计算股份数量
        shares = int(risk_amount / price_risk)
        
        # 确保仓位大小合理
        min_shares = 1
        max_shares_by_capital = int(account_size * 0.1 / entry_price)  # 最多10%资金
        
        shares = max(min_shares, min(shares, max_shares_by_capital))
        
        actual_risk = shares * price_risk
        
        self.logger.debug(f"仓位计算: 入场价={entry_price:.2f}, 止损价={stop_loss_price:.2f}, "
                         f"股份={shares}, 实际风险={actual_risk:.2f} ({actual_risk/account_size:.2%})")
        
        return shares, actual_risk
    
    def calculate_stop_loss(self, entry_price: float, position_type: str = 'long', 
                          volatility: Optional[float] = None) -> float:
        """计算动态止损价格
        
        Args:
            entry_price: 入场价格
            position_type: 仓位类型 ('long' 或 'short')
            volatility: 波动率 (可选，用于动态止损)
            
        Returns:
            float: 止损价格
        """
        if volatility is not None:
            # 基于波动率的动态止损
            dynamic_stop_pct = min(self.stop_loss_pct, volatility * 1.5)
        else:
            dynamic_stop_pct = self.stop_loss_pct
        
        if position_type == 'long':
            stop_loss = entry_price * (1 - dynamic_stop_pct)
        elif position_type == 'short':
            stop_loss = entry_price * (1 + dynamic_stop_pct)
        else:
            stop_loss = entry_price * (1 - dynamic_stop_pct)
        
        volatility_str = f"{volatility:.4f}" if volatility is not None else 'N/A'
        self.logger.debug(f"止损计算: 入场价={entry_price:.2f}, 类型={position_type}, "
                         f"波动率={volatility_str}, 止损={stop_loss:.2f}")
        
        return stop_loss
    
    def calculate_take_profit(self, entry_price: float, position_type: str = 'long',
                            risk_reward_ratio: float = 2.0) -> float:
        """计算止盈价格
        
        Args:
            entry_price: 入场价格
            position_type: 仓位类型 ('long' 或 'short')
            risk_reward_ratio: 风险回报比 (默认: 2.0)
            
        Returns:
            float: 止盈价格
        """
        # 基于风险回报比计算止盈
        risk_amount = entry_price * self.stop_loss_pct
        reward_amount = risk_amount * risk_reward_ratio
        
        if position_type == 'long':
            take_profit = entry_price + reward_amount
        elif position_type == 'short':
            take_profit = entry_price - reward_amount
        else:
            take_profit = entry_price + reward_amount
        
        # 同时考虑固定止盈百分比
        fixed_take_profit = entry_price * (1 + self.take_profit_pct) if position_type == 'long' else entry_price * (1 - self.take_profit_pct)
        
        # 取更保守的值
        if position_type == 'long':
            take_profit = min(take_profit, fixed_take_profit)
        else:
            take_profit = max(take_profit, fixed_take_profit)
        
        self.logger.debug(f"止盈计算: 入场价={entry_price:.2f}, 类型={position_type}, "
                         f"风险回报比={risk_reward_ratio}, 止盈={take_profit:.2f}")
        
        return take_profit
    
    def calculate_portfolio_risk(self, positions: Dict[str, Dict[str, Any]], 
                               historical_returns: pd.DataFrame) -> Dict[str, Any]:
        """计算投资组合风险
        
        Args:
            positions: 持仓字典，格式: {symbol: {'shares': x, 'entry_price': y, 'current_price': z}}
            historical_returns: 历史收益率DataFrame，index为日期，columns为标的代码
            
        Returns:
            Dict[str, Any]: 组合风险指标
        """
        if not positions or historical_returns.empty:
            return {
                'portfolio_value': 0,
                'portfolio_risk': 0,
                'component_risks': {},
                'status': 'no_positions'
            }
        
        # 计算组合价值
        portfolio_value = 0
        position_values = {}
        
        for symbol, position_info in positions.items():
            shares = position_info.get('shares', 0)
            current_price = position_info.get('current_price', 0)
            position_value = shares * current_price
            position_values[symbol] = position_value
            portfolio_value += position_value
        
        if portfolio_value <= 0:
            return {
                'portfolio_value': 0,
                'portfolio_risk': 0,
                'component_risks': {},
                'status': 'zero_value'
            }
        
        # 计算权重
        weights = {symbol: value / portfolio_value for symbol, value in position_values.items()}
        
        # 计算组合风险 (简化版本)
        portfolio_risk = 0
        component_risks = {}
        
        for symbol, weight in weights.items():
            if symbol in historical_returns.columns:
                # 计算单个标的的波动率
                returns = historical_returns[symbol].dropna()
                if len(returns) >= self.volatility_window:
                    volatility = returns.tail(self.volatility_window).std()
                    component_risk = weight * volatility
                    portfolio_risk += component_risk
                    
                    component_risks[symbol] = {
                        'weight': weight,
                        'volatility': volatility,
                        'component_risk': component_risk
                    }
        
        # 检查是否超过最大组合风险限制
        risk_exceeded = portfolio_risk > self.max_portfolio_risk
        
        # 计算风险等级
        if portfolio_risk < self.max_portfolio_risk * 0.5:
            risk_level = 'low'
        elif portfolio_risk < self.max_portfolio_risk * 0.8:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        result = {
            'portfolio_value': portfolio_value,
            'portfolio_risk': portfolio_risk,
            'portfolio_risk_pct': portfolio_risk,
            'risk_level': risk_level,
            'risk_exceeded': risk_exceeded,
            'component_risks': component_risks,
            'weights': weights,
            'status': 'calculated'
        }
        
        self.logger.info(f"组合风险计算: 价值={portfolio_value:.2f}, 风险={portfolio_risk:.4f}, "
                        f"等级={risk_level}, 超限={risk_exceeded}")
        
        return result
    
    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95, 
                     method: str = 'historical') -> float:
        """计算在险价值 (Value at Risk)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平 (默认: 0.95)
            method: 计算方法 ('historical', 'parametric', 'monte_carlo')
            
        Returns:
            float: 在险价值 (负数表示损失)
        """
        if returns.empty:
            return 0
        
        if method == 'historical':
            # 历史模拟法
            var = -np.percentile(returns, (1 - confidence_level) * 100)
        elif method == 'parametric':
            # 参数法 (正态分布假设)
            mean = returns.mean()
            std = returns.std()
            from scipy.stats import norm
            z_score = norm.ppf(1 - confidence_level)
            var = -(mean + z_score * std)
        else:
            # 默认使用历史模拟法
            var = -np.percentile(returns, (1 - confidence_level) * 100)
        
        self.logger.debug(f"VaR计算: 置信水平={confidence_level}, 方法={method}, VaR={var:.4f}")
        
        return var
    
    def calculate_cvar(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """计算条件在险价值 (Conditional VaR, Expected Shortfall)
        
        Args:
            returns: 收益率序列
            confidence_level: 置信水平 (默认: 0.95)
            
        Returns:
            float: 条件在险价值
        """
        if returns.empty:
            return 0
        
        # 计算VaR
        var = self.calculate_var(returns, confidence_level, 'historical')
        
        # 计算超过VaR的损失平均值
        losses_beyond_var = returns[returns < -var]
        
        if len(losses_beyond_var) > 0:
            cvar = -losses_beyond_var.mean()
        else:
            cvar = var * 1.5  # 保守估计
        
        self.logger.debug(f"CVaR计算: 置信水平={confidence_level}, VaR={var:.4f}, CVaR={cvar:.4f}")
        
        return cvar
    
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
                'drawdown_start': None,
                'drawdown_end': None,
                'recovery_period': None
            }
        
        equity_array = np.array(equity_curve)
        
        # 计算回撤
        peak = equity_array[0]
        max_drawdown = 0
        drawdown_start_idx = 0
        drawdown_end_idx = 0
        current_drawdown_start = 0
        
        for i, equity in enumerate(equity_array):
            if equity > peak:
                peak = equity
                current_drawdown_start = i
            else:
                drawdown = (peak - equity) / peak
                if drawdown > max_drawdown:
                    max_drawdown = drawdown
                    drawdown_start_idx = current_drawdown_start
                    drawdown_end_idx = i
        
        # 计算恢复期
        recovery_period = None
        if drawdown_end_idx > drawdown_start_idx:
            # 寻找回撤恢复的时间点
            recovery_value = equity_array[drawdown_start_idx]
            for i in range(drawdown_end_idx, len(equity_array)):
                if equity_array[i] >= recovery_value:
                    recovery_period = i - drawdown_end_idx
                    break
        
        result = {
            'max_drawdown': max_drawdown,
            'drawdown_start_idx': drawdown_start_idx,
            'drawdown_end_idx': drawdown_end_idx,
            'recovery_period': recovery_period,
            'exceeded_limit': max_drawdown > self.max_drawdown_limit
        }
        
        self.logger.debug(f"最大回撤计算: 回撤={max_drawdown:.2%}, "
                         f"超限={result['exceeded_limit']}, 恢复期={recovery_period}")
        
        return result
    
    def check_position_risk(self, position_info: Dict[str, Any], 
                          account_size: float) -> Dict[str, Any]:
        """检查单笔交易风险
        
        Args:
            position_info: 持仓信息，包含:
                - symbol: 标的代码
                - shares: 股份数量
                - entry_price: 入场价格
                - current_price: 当前价格
                - stop_loss: 止损价格
            account_size: 账户总资金
            
        Returns:
            Dict[str, Any]: 风险检查结果
        """
        symbol = position_info.get('symbol', 'unknown')
        shares = position_info.get('shares', 0)
        entry_price = position_info.get('entry_price', 0)
        current_price = position_info.get('current_price', entry_price)
        stop_loss = position_info.get('stop_loss')
        
        if stop_loss is None:
            stop_loss = self.calculate_stop_loss(entry_price, 'long')
        
        # 计算当前盈亏
        current_pnl = (current_price - entry_price) * shares
        current_pnl_pct = (current_price - entry_price) / entry_price if entry_price > 0 else 0
        
        # 计算潜在损失
        potential_loss = abs(entry_price - stop_loss) * shares if entry_price > 0 and stop_loss > 0 else 0
        potential_loss_pct = potential_loss / account_size if account_size > 0 else 0
        
        # 检查是否超过风险限制
        risk_exceeded = potential_loss_pct > self.max_position_risk
        
        # 检查是否需要止损
        stop_loss_triggered = current_price <= stop_loss if entry_price > stop_loss else current_price >= stop_loss
        
        # 检查是否需要止盈
        take_profit = self.calculate_take_profit(entry_price, 'long')
        take_profit_triggered = current_price >= take_profit
        
        result = {
            'symbol': symbol,
            'current_pnl': current_pnl,
            'current_pnl_pct': current_pnl_pct,
            'potential_loss': potential_loss,
            'potential_loss_pct': potential_loss_pct,
            'risk_exceeded': risk_exceeded,
            'stop_loss_price': stop_loss,
            'stop_loss_triggered': stop_loss_triggered,
            'take_profit_price': take_profit,
            'take_profit_triggered': take_profit_triggered,
            'recommendation': 'hold'  # hold, reduce, exit
        }
        
        # 生成建议
        if stop_loss_triggered:
            result['recommendation'] = 'exit'
            result['reason'] = '止损触发'
        elif take_profit_triggered:
            result['recommendation'] = 'reduce'
            result['reason'] = '止盈触发'
        elif risk_exceeded:
            result['recommendation'] = 'reduce'
            result['reason'] = '风险超限'
        elif current_pnl_pct < -0.03:  # 亏损3%以上
            result['recommendation'] = 'monitor'
            result['reason'] = '亏损扩大'
        
        self.logger.debug(f"持仓风险检查: {symbol}, 盈亏={current_pnl:.2f}({current_pnl_pct:.2%}), "
                         f"潜在损失={potential_loss_pct:.2%}, 建议={result['recommendation']}")
        
        return result
    
    def generate_risk_report(self, portfolio_state: Dict[str, Any], 
                           historical_data: pd.DataFrame) -> Dict[str, Any]:
        """生成全面的风险报告
        
        Args:
            portfolio_state: 投资组合状态，包含:
                - positions: 持仓信息
                - equity_curve: 权益曲线
                - account_size: 账户资金
                - current_date: 当前日期
            historical_data: 历史数据，用于计算风险指标
            
        Returns:
            Dict[str, Any]: 风险报告
        """
        positions = portfolio_state.get('positions', {})
        equity_curve = portfolio_state.get('equity_curve', [])
        account_size = portfolio_state.get('account_size', 0)
        
        # 计算各项风险指标
        portfolio_risk = self.calculate_portfolio_risk(positions, historical_data)
        
        # 计算最大回撤
        max_drawdown_info = self.calculate_max_drawdown(equity_curve)
        
        # 计算在险价值 (如果需要历史收益率)
        var = 0
        cvar = 0
        if not historical_data.empty and 'returns' in historical_data.columns:
            returns = historical_data['returns'].dropna()
            if len(returns) > 0:
                var = self.calculate_var(returns, confidence_level=0.95)
                cvar = self.calculate_cvar(returns, confidence_level=0.95)
        
        # 检查单个持仓风险
        position_risks = {}
        for symbol, position_info in positions.items():
            position_risks[symbol] = self.check_position_risk(position_info, account_size)
        
        # 生成风险警报
        risk_alerts = []
        
        if portfolio_risk.get('risk_exceeded', False):
            risk_alerts.append({
                'level': 'high',
                'type': 'portfolio_risk',
                'message': f'投资组合风险超过限制: {portfolio_risk.get("portfolio_risk_pct", 0):.2%} > {self.max_portfolio_risk:.2%}',
                'recommendation': '减少仓位'
            })
        
        if max_drawdown_info.get('exceeded_limit', False):
            risk_alerts.append({
                'level': 'high',
                'type': 'max_drawdown',
                'message': f'最大回撤超过限制: {max_drawdown_info.get("max_drawdown", 0):.2%} > {self.max_drawdown_limit:.2%}',
                'recommendation': '暂停新交易'
            })
        
        # 检查是否有止损触发
        for symbol, risk_info in position_risks.items():
            if risk_info.get('stop_loss_triggered', False):
                risk_alerts.append({
                    'level': 'medium',
                    'type': 'stop_loss',
                    'symbol': symbol,
                    'message': f'{symbol} 触发止损: 当前价={risk_info.get("current_price", 0):.2f}, 止损价={risk_info.get("stop_loss_price", 0):.2f}',
                    'recommendation': '立即平仓'
                })
        
        # 生成报告
        report = {
            'report_date': portfolio_state.get('current_date', datetime.now()),
            'account_size': account_size,
            'portfolio_risk': portfolio_risk,
            'max_drawdown': max_drawdown_info,
            'value_at_risk': {
                'var_95': var,
                'cvar_95': cvar
            },
            'position_risks': position_risks,
            'risk_alerts': risk_alerts,
            'risk_level': portfolio_risk.get('risk_level', 'low'),
            'total_alerts': len(risk_alerts),
            'high_risk_alerts': sum(1 for alert in risk_alerts if alert.get('level') == 'high'),
            'recommendations': self._generate_recommendations(portfolio_risk, max_drawdown_info, position_risks)
        }
        
        # 记录风险历史
        self.risk_history.append({
            'timestamp': datetime.now(),
            'report': report
        })
        
        self.logger.info(f"风险报告生成: 风险等级={report['risk_level']}, "
                        f"警报数={report['total_alerts']}(高:{report['high_risk_alerts']})")
        
        return report
    
    def _generate_recommendations(self, portfolio_risk: Dict[str, Any], 
                                max_drawdown_info: Dict[str, Any], 
                                position_risks: Dict[str, Dict[str, Any]]) -> List[str]:
        """生成风险建议
        
        Args:
            portfolio_risk: 投资组合风险信息
            max_drawdown_info: 最大回撤信息
            position_risks: 持仓风险信息
            
        Returns:
            List[str]: 风险建议列表
        """
        recommendations = []
        
        # 投资组合风险建议
        if portfolio_risk.get('risk_exceeded', False):
            recommendations.append(f"投资组合风险过高 ({portfolio_risk.get('portfolio_risk_pct', 0):.2%})，建议减少总体仓位")
        
        if portfolio_risk.get('risk_level') == 'high':
            recommendations.append("投资组合风险等级为'高'，建议暂停新交易并评估现有持仓")
        
        # 最大回撤建议
        if max_drawdown_info.get('exceeded_limit', False):
            recommendations.append(f"最大回撤超过限制 ({max_drawdown_info.get('max_drawdown', 0):.2%})，建议暂停交易直到回撤恢复")
        
        # 单个持仓建议
        exit_positions = []
        reduce_positions = []
        
        for symbol, risk_info in position_risks.items():
            recommendation = risk_info.get('recommendation', 'hold')
            
            if recommendation == 'exit':
                exit_positions.append(symbol)
            elif recommendation == 'reduce':
                reduce_positions.append(symbol)
        
        if exit_positions:
            recommendations.append(f"以下持仓建议立即平仓: {', '.join(exit_positions)}")
        
        if reduce_positions:
            recommendations.append(f"以下持仓建议减少仓位: {', '.join(reduce_positions)}")
        
        # 通用建议
        if not recommendations:
            recommendations.append("当前风险水平正常，可继续执行交易策略")
        
        return recommendations
    
    def monitor_risk_continuously(self, portfolio_state: Dict[str, Any], 
                                market_data: pd.DataFrame, 
                                check_interval: int = 1) -> Dict[str, Any]:
        """持续监控风险
        
        Args:
            portfolio_state: 投资组合状态
            market_data: 市场数据
            check_interval: 检查间隔 (交易日)
            
        Returns:
            Dict[str, Any]: 监控结果
        """
        # 生成当前风险报告
        current_report = self.generate_risk_report(portfolio_state, market_data)
        
        # 检查是否有高风险警报
        high_risk_alerts = [alert for alert in current_report['risk_alerts'] 
                           if alert.get('level') == 'high']
        
        # 生成监控结果
        monitoring_result = {
            'timestamp': datetime.now(),
            'risk_report': current_report,
            'high_risk_alerts': high_risk_alerts,
            'requires_action': len(high_risk_alerts) > 0,
            'action_recommendations': current_report.get('recommendations', []),
            'monitoring_status': 'active'
        }
        
        # 如果有高风险警报，记录并可能触发自动动作
        if monitoring_result['requires_action']:
            self.logger.warning(f"检测到高风险警报: {len(high_risk_alerts)} 个高风险问题")
            
            # 这里可以添加自动风险控制动作
            # 例如: 自动平仓、减少仓位等
        
        return monitoring_result


def create_default_risk_config() -> Dict[str, Any]:
    """创建默认风险配置"""
    return {
        'max_position_risk': 0.02,      # 2%
        'max_portfolio_risk': 0.1,      # 10%
        'max_drawdown_limit': 0.2,      # 20%
        'stop_loss_pct': 0.05,          # 5%
        'take_profit_pct': 0.1,         # 10%
        'volatility_window': 20,
        'correlation_window': 60,
        'risk_free_rate': 0.02
    }


def demo_risk_management():
    """演示风险管理功能"""
    print("=" * 80)
    print("风险管理模块演示")
    print("=" * 80)
    
    # 创建风险管理器
    config = create_default_risk_config()
    risk_manager = RiskManager(config)
    
    # 演示仓位大小计算
    print("\n1. 仓位大小计算演示:")
    entry_price = 100.0
    stop_loss = 95.0
    account_size = 100000.0
    
    shares, actual_risk = risk_manager.calculate_position_size(
        entry_price, stop_loss, account_size
    )
    
    print(f"  入场价: {entry_price:.2f}")
    print(f"  止损价: {stop_loss:.2f}")
    print(f"  账户资金: {account_size:.2f}")
    print(f"  建议仓位: {shares} 股")
    print(f"  实际风险: {actual_risk:.2f} ({actual_risk/account_size:.2%})")
    
    # 演示止损止盈计算
    print("\n2. 止损止盈计算演示:")
    stop_loss_price = risk_manager.calculate_stop_loss(entry_price, 'long')
    take_profit_price = risk_manager.calculate_take_profit(entry_price, 'long')
    
    print(f"  动态止损: {stop_loss_price:.2f} ({abs(entry_price-stop_loss_price)/entry_price:.2%})")
    print(f"  止盈价格: {take_profit_price:.2f} ({abs(take_profit_price-entry_price)/entry_price:.2%})")
    print(f"  风险回报比: {abs(take_profit_price-entry_price)/abs(entry_price-stop_loss_price):.2f}")
    
    # 演示持仓风险检查
    print("\n3. 持仓风险检查演示:")
    position_info = {
        'symbol': 'TEST001.SZ',
        'shares': 100,
        'entry_price': 100.0,
        'current_price': 102.0,
        'stop_loss': 95.0
    }
    
    risk_check = risk_manager.check_position_risk(position_info, account_size)
    
    print(f"  标的: {risk_check['symbol']}")
    print(f"  当前盈亏: {risk_check['current_pnl']:.2f} ({risk_check['current_pnl_pct']:.2%})")
    print(f"  潜在损失: {risk_check['potential_loss']:.2f} ({risk_check['potential_loss_pct']:.2%})")
    print(f"  风险超限: {risk_check['risk_exceeded']}")
    print(f"  止损触发: {risk_check['stop_loss_triggered']}")
    print(f"  止盈触发: {risk_check['take_profit_triggered']}")
    print(f"  建议: {risk_check['recommendation']} ({risk_check.get('reason', 'N/A')})")
    
    # 演示最大回撤计算
    print("\n4. 最大回撤计算演示:")
    
    # 生成示例权益曲线
    np.random.seed(42)
    days = 100
    base_equity = 100000
    random_returns = np.random.normal(0.0005, 0.02, days)
    equity_curve = base_equity * np.cumprod(1 + random_returns)
    
    drawdown_info = risk_manager.calculate_max_drawdown(equity_curve.tolist())
    
    print(f"  最大回撤: {drawdown_info['max_drawdown']:.2%}")
    print(f"  回撤超限: {drawdown_info['exceeded_limit']}")
    print(f"  恢复期: {drawdown_info['recovery_period']} 天")
    
    print("\n" + "=" * 80)
    print("演示完成")


if __name__ == "__main__":
    # 运行演示
    demo_risk_management()