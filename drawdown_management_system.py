#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
回撤风险管理量化分析系统
第14章：回撤风险管理
AL Brooks《价格行为交易之区间篇》
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import json

class PriceActionDrawdownManager:
    """价格行为回撤管理"""
    
    def __init__(self, initial_capital: float = 10000.0):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        self.peak_capital = initial_capital
        self.max_drawdown = 0.0
        self.drawdown_history = []
        self.trade_history = []
        
    def calculate_price_action_stop_loss(self, entry_price: float, 
                                        market_structure: Dict,
                                        atr: float,
                                        risk_factor: float = 2.0) -> Dict:
        """
        基于价格行为的止损设置
        
        参数:
            entry_price: 入场价格
            market_structure: 市场结构信息
            atr: 平均真实波幅
            risk_factor: 风险系数
            
        返回:
            止损分析结果
        """
        stop_loss_levels = {}
        
        # 1. 基于ATR的止损
        atr_stop = atr * risk_factor
        stop_loss_levels['atr_stop'] = {
            'level': entry_price - atr_stop if entry_price > market_structure.get('support', 0) else entry_price + atr_stop,
            'distance': atr_stop,
            'type': 'volatility_based'
        }
        
        # 2. 基于支撑/阻力的止损
        if 'support' in market_structure and entry_price > market_structure['support']:
            # 多头交易：止损在支撑下方
            support_stop = market_structure['support'] * 0.995  # 支撑下方0.5%
            stop_loss_levels['support_resistance_stop'] = {
                'level': support_stop,
                'distance': abs(entry_price - support_stop),
                'type': 'structure_based'
            }
        elif 'resistance' in market_structure and entry_price < market_structure['resistance']:
            # 空头交易：止损在阻力上方
            resistance_stop = market_structure['resistance'] * 1.005  # 阻力上方0.5%
            stop_loss_levels['support_resistance_stop'] = {
                'level': resistance_stop,
                'distance': abs(entry_price - resistance_stop),
                'type': 'structure_based'
            }
        
        # 3. 基于最近摆动点的止损
        if 'recent_swing_low' in market_structure:
            swing_stop = market_structure['recent_swing_low'] * 0.99
            stop_loss_levels['swing_stop'] = {
                'level': swing_stop,
                'distance': abs(entry_price - swing_stop),
                'type': 'swing_based'
            }
        
        # 选择最佳止损
        if stop_loss_levels:
            # 优先选择结构止损，其次摆动止损，最后ATR止损
            preferred_types = ['structure_based', 'swing_based', 'volatility_based']
            for stop_type in preferred_types:
                for key, stop_info in stop_loss_levels.items():
                    if stop_info['type'] == stop_type:
                        stop_loss_levels['selected'] = stop_info
                        break
                if 'selected' in stop_loss_levels:
                    break
        
        return stop_loss_levels
    
    def calculate_position_size(self, 
                               entry_price: float, 
                               stop_loss: float, 
                               risk_percentage: float = 0.02,
                               account_risk_adjustment: float = 1.0) -> Dict:
        """
        计算基于风险的仓位大小
        
        参数:
            entry_price: 入场价格
            stop_loss: 止损价格
            risk_percentage: 风险百分比（默认2%）
            account_risk_adjustment: 账户风险调整系数
            
        返回:
            仓位计算详情
        """
        # 当前账户风险调整
        current_risk_percentage = risk_percentage * account_risk_adjustment
        
        # 风险金额
        risk_amount = self.current_capital * current_risk_percentage
        
        # 价格风险
        price_risk = abs(entry_price - stop_loss)
        if price_risk == 0:
            return {'error': '价格风险为零', 'position_size': 0}
        
        # 仓位大小
        position_size = risk_amount / price_risk
        
        # 标准化（外汇市场）
        # 1标准手 = 100,000单位
        standard_lot = 100000
        lots = position_size / standard_lot
        
        return {
            'risk_amount': round(risk_amount, 2),
            'price_risk': round(price_risk, 5),
            'position_size': round(position_size, 2),
            'lots': round(lots, 2),
            'standard_lots': round(lots),  # 整数手数
            'micro_lots': round(lots * 10, 1),  # 微型手
            'risk_percentage_used': round(current_risk_percentage * 100, 2),
            'account_risk_adjustment': account_risk_adjustment
        }
    
    def update_drawdown_metrics(self, current_capital: float) -> Dict:
        """
        更新回撤指标
        
        参数:
            current_capital: 当前资金
            
        返回:
            回撤指标
        """
        self.current_capital = current_capital
        
        # 更新峰值资金
        if current_capital > self.peak_capital:
            self.peak_capital = current_capital
        
        # 计算当前回撤
        if self.peak_capital > 0:
            current_drawdown = (self.peak_capital - current_capital) / self.peak_capital * 100
        else:
            current_drawdown = 0
        
        # 更新最大回撤
        self.max_drawdown = max(self.max_drawdown, current_drawdown)
        
        # 记录历史
        self.drawdown_history.append({
            'timestamp': pd.Timestamp.now(),
            'current_capital': current_capital,
            'peak_capital': self.peak_capital,
            'current_drawdown': current_drawdown,
            'max_drawdown': self.max_drawdown
        })
        
        return {
            'current_capital': round(current_capital, 2),
            'peak_capital': round(self.peak_capital, 2),
            'current_drawdown': round(current_drawdown, 2),
            'max_drawdown': round(self.max_drawdown, 2)
        }
    
    def get_risk_adjustment_factor(self, current_drawdown: float) -> float:
        """
        根据当前回撤获取风险调整系数
        
        参数:
            current_drawdown: 当前回撤百分比
            
        返回:
            风险调整系数
        """
        # 基于回撤的风险调整
        if current_drawdown <= 5:
            return 1.0  # 正常风险
        elif current_drawdown <= 10:
            return 0.7  # 降低30%风险
        elif current_drawdown <= 15:
            return 0.4  # 降低60%风险
        elif current_drawdown <= 20:
            return 0.2  # 降低80%风险
        else:
            return 0.1  # 极低风险
    
    def calculate_risk_reward_ratio(self, 
                                   entry_price: float, 
                                   stop_loss: float, 
                                   take_profit: float) -> Dict:
        """
        计算风险回报比
        
        参数:
            entry_price: 入场价格
            stop_loss: 止损价格
            take_profit: 止盈价格
            
        返回:
            风险回报分析
        """
        risk = abs(entry_price - stop_loss)
        reward = abs(entry_price - take_profit)
        
        if risk == 0:
            return {'error': '风险为零', 'risk_reward_ratio': 0}
        
        risk_reward_ratio = reward / risk
        
        # 评估风险回报比质量
        if risk_reward_ratio >= 3:
            quality = '优秀'
        elif risk_reward_ratio >= 2:
            quality = '良好'
        elif risk_reward_ratio >= 1.5:
            quality = '可接受'
        else:
            quality = '较差'
        
        return {
            'risk': round(risk, 5),
            'reward': round(reward, 5),
            'risk_reward_ratio': round(risk_reward_ratio, 2),
            'quality': quality,
            'required_win_rate': round(1 / (1 + risk_reward_ratio) * 100, 1)
        }
    
    def manage_trade_risk(self, 
                         trade_info: Dict,
                         market_conditions: Dict) -> Dict:
        """
        管理交易风险
        
        参数:
            trade_info: 交易信息
            market_conditions: 市场条件
            
        返回:
            风险管理计划
        """
        # 提取交易信息
        entry_price = trade_info.get('entry_price')
        direction = trade_info.get('direction', 'long')
        market_structure = trade_info.get('market_structure', {})
        atr = market_conditions.get('atr', 0.001)
        
        # 1. 设置止损
        stop_loss_analysis = self.calculate_price_action_stop_loss(
            entry_price, market_structure, atr
        )
        
        if 'selected' not in stop_loss_analysis:
            return {'error': '无法确定止损'}
        
        selected_stop = stop_loss_analysis['selected']
        stop_loss = selected_stop['level']
        
        # 2. 基于回撤调整风险
        drawdown_metrics = self.update_drawdown_metrics(self.current_capital)
        current_drawdown = drawdown_metrics['current_drawdown']
        risk_adjustment = self.get_risk_adjustment_factor(current_drawdown)
        
        # 3. 计算仓位
        position_calculation = self.calculate_position_size(
            entry_price, stop_loss, 
            account_risk_adjustment=risk_adjustment
        )
        
        # 4. 确定止盈（基于风险回报比目标）
        # 目标风险回报比：至少1:2
        target_rr = 2.0
        if direction == 'long':
            take_profit = entry_price + (entry_price - stop_loss) * target_rr
        else:
            take_profit = entry_price - (stop_loss - entry_price) * target_rr
        
        # 5. 风险回报分析
        rr_analysis = self.calculate_risk_reward_ratio(
            entry_price, stop_loss, take_profit
        )
        
        return {
            'trade_id': trade_info.get('id', 'unknown'),
            'entry_price': entry_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'stop_loss_analysis': stop_loss_analysis,
            'position_calculation': position_calculation,
            'risk_reward_analysis': rr_analysis,
            'drawdown_adjustment': {
                'current_drawdown': current_drawdown,
                'risk_adjustment_factor': risk_adjustment,
                'max_drawdown': drawdown_metrics['max_drawdown']
            },
            'market_conditions': {
                'volatility': atr,
                'trend': market_conditions.get('trend', 'neutral'),
                'market_state': market_conditions.get('state', 'normal')
            }
        }

class AdvancedDrawdownAnalyzer:
    """高级回撤分析器"""
    
    def __init__(self):
        self.trade_sequence = []
        self.consecutive_losses = 0
        self.win_streak = 0
        
    def analyze_trade_sequence_risk(self, trade_results: List[Dict]) -> Dict:
        """
        分析交易序列风险
        
        参数:
            trade_results: 交易结果列表
            
        返回:
            序列风险分析
        """
        if not trade_results:
            return {'error': '无交易数据'}
        
        self.trade_sequence = trade_results
        
        # 统计连续亏损
        max_consecutive_losses = 0
        current_streak = 0
        wins = 0
        losses = 0
        
        for trade in trade_results:
            if trade.get('profit', 0) > 0:
                wins += 1
                current_streak = 0
                self.win_streak += 1
                self.consecutive_losses = 0
            else:
                losses += 1
                current_streak += 1
                self.consecutive_losses += 1
                self.win_streak = 0
                max_consecutive_losses = max(max_consecutive_losses, current_streak)
        
        total_trades = len(trade_results)
        win_rate = wins / total_trades * 100 if total_trades > 0 else 0
        
        # 凯利公式计算最优仓位
        avg_win = np.mean([t.get('profit', 0) for t in trade_results if t.get('profit', 0) > 0]) if wins > 0 else 0
        avg_loss = abs(np.mean([t.get('profit', 0) for t in trade_results if t.get('profit', 0) < 0])) if losses > 0 else 0
        
        if avg_loss > 0:
            win_probability = win_rate / 100
            loss_probability = 1 - win_probability
            avg_win_loss_ratio = avg_win / avg_loss
            
            # 凯利公式
            kelly_fraction = win_probability - (loss_probability / avg_win_loss_ratio)
            kelly_fraction = max(0, min(kelly_fraction, 0.5))  # 限制在0-50%
        else:
            kelly_fraction = 0.25  # 默认值
        
        return {
            'total_trades': total_trades,
            'wins': wins,
            'losses': losses,
            'win_rate': round(win_rate, 1),
            'max_consecutive_losses': max_consecutive_losses,
            'current_consecutive_losses': self.consecutive_losses,
            'current_win_streak': self.win_streak,
            'average_win': round(avg_win, 2),
            'average_loss': round(avg_loss, 2),
            'win_loss_ratio': round(avg_win / avg_loss, 2) if avg_loss > 0 else 0,
            'kelly_fraction': round(kelly_fraction, 3),
            'recommended_position_adjustment': min(1.0, 1.0 - (max_consecutive_losses * 0.1))
        }
    
    def calculate_drawdown_recovery(self, 
                                   initial_capital: float,
                                   current_capital: float,
                                   max_drawdown: float,
                                   expected_return: float = 0.1) -> Dict:
        """
        计算回撤恢复
        
        参数:
            initial_capital: 初始资金
            current_capital: 当前资金
            max_drawdown: 最大回撤百分比
            expected_return: 预期月回报率
            
        返回:
            恢复分析
        """
        # 需要恢复的金额
        peak_capital = initial_capital * (1 - max_drawdown / 100)
        recovery_needed = peak_capital - current_capital
        recovery_percentage = recovery_needed / current_capital * 100
        
        # 计算恢复时间（基于预期回报）
        if expected_return > 0:
            months_to_recover = np.log(peak_capital / current_capital) / np.log(1 + expected_return)
            months_to_recover = max(1, months_to_recover)  # 至少1个月
        else:
            months_to_recover = float('inf')
        
        # 建议恢复策略
        if recovery_percentage > 50:
            strategy = '激进恢复：大幅降低风险，专注于高胜率交易'
        elif recovery_percentage > 25:
            strategy = '积极恢复：适度降低风险，优化交易策略'
        elif recovery_percentage > 10:
            strategy = '稳健恢复：微调风险参数，保持一致性'
        else:
            strategy = '正常交易：维持现有策略，关注风险管理'
        
        return {
            'initial_capital': round(initial_capital, 2),
            'current_capital': round(current_capital, 2),
            'peak_capital': round(peak_capital, 2),
            'recovery_needed': round(recovery_needed, 2),
            'recovery_percentage': round(recovery_percentage, 2),
            'max_drawdown': round(max_drawdown, 2),
            'expected_monthly_return': round(expected_return * 100, 1),
            'estimated_months_to_recover': round(months_to_recover, 1),
            'recovery_strategy': strategy,
            'recommended_risk_adjustment': min(1.0, 1.0 - (recovery_percentage / 100 * 0.5))
        }

def main():
    """主函数：演示回撤管理系统"""
    print("=== 价格行为回撤风险管理量化分析系统 ===\n")
    
    # 创建回撤管理器
    manager = PriceActionDrawdownManager(initial_capital=10000)
    
    # 模拟市场条件
    market_conditions = {
        'atr': 0.0012,  # 120点ATR
        'trend': 'bullish',
        'state': 'range_bound',
        'volatility': 'medium'
    }
    
    # 模拟交易
    trade_info = {
        'id': 'TRADE_001',
        'entry_price': 1.1000,
        'direction': 'long',
        'market_structure': {
            'support': 1.0950,
            'resistance': 1.1050,
            'recent_swing_low': 1.0960
        }
    }
    
    print("1. 交易风险管理分析")
    print("-" * 40)
    
    risk_plan = manager.manage_trade_risk(trade_info, market_conditions)
    
    print(f"入场价格: {risk_plan['entry_price']}")
    print(f"止损价格: {risk_plan['stop_loss']:.5f}")
    print(f"止盈价格: {risk_plan['take_profit']:.5f}")
    print(f"仓位大小: {risk_plan['position_calculation']['position_size']:.2f} 单位")
    print(f"手数: {risk_plan['position_calculation']['lots']:.2f} 标准手")
    print(f"风险金额: ${risk_plan['position_calculation']['risk_amount']:.2f}")
    print(f"风险回报比: {risk_plan['risk_reward_analysis']['risk_reward_ratio']:.2f}")
    print(f"质量: {risk_plan['risk_reward_analysis']['quality']}")
    print(f"当前回撤调整系数: {risk_plan['drawdown_adjustment']['risk_adjustment_factor']:.2f}")
    
    print("\n2. 高级回撤分析")
    print("-" * 40)
    
    # 模拟交易序列
    analyzer = AdvancedDrawdownAnalyzer()
    
    # 生成模拟交易结果
    np.random.seed(42)
    n_trades = 50
    trade_results = []
    
    for i in range(n_trades):
        profit = np.random.choice([50, -30, 80, -20, 100, -40, 60, -25], p=[0.3, 0.2, 0.2, 0.1, 0.1, 0.05, 0.03, 0.02])
        trade_results.append({
            'id': f'Trade_{i+1}',
            'profit': profit,
            'risk': 30
        })
    
    sequence_analysis = analyzer.analyze_trade_sequence_risk(trade_results)
    
    print(f"总交易数: {sequence_analysis['total_trades']}")
    print(f"胜率: {sequence_analysis['win_rate']:.1f}%")
    print(f"最大连续亏损: {sequence_analysis['max_consecutive_losses']}")
    print(f"当前连续亏损: {sequence_analysis['current_consecutive_losses']}")
    print(f"平均盈利: ${sequence_analysis['average_win']:.2f}")
    print(f"平均亏损: ${sequence_analysis['average_loss']:.2f}")
    print(f"盈亏比: {sequence_analysis['win_loss_ratio']:.2f}")
    print(f"凯利分数: {sequence_analysis['kelly_fraction']:.3f}")
    print(f"推荐仓位调整: {sequence_analysis['recommended_position_adjustment']:.2f}")
    
    print("\n3. 回撤恢复分析")
    print("-" * 40)
    
    # 模拟回撤场景
    recovery_analysis = analyzer.calculate_drawdown_recovery(
        initial_capital=10000,
        current_capital=8500,
        max_drawdown=15,
        expected_return=0.08
    )
    
    print(f"初始资金: ${recovery_analysis['initial_capital']:.2f}")
    print(f"当前资金: ${recovery_analysis['current_capital']:.2f}")
    print(f"最大回撤: {recovery_analysis['max_drawdown']:.1f}%")
    print(f"需要恢复: ${recovery_analysis['recovery_needed']:.2f} ({recovery_analysis['recovery_percentage']:.1f}%)")
    print(f"预期月回报: {recovery_analysis['expected_monthly_return']:.1f}%")
    print(f"估计恢复时间: {recovery_analysis['estimated_months_to_recover']:.1f} 个月")
    print(f"恢复策略: {recovery_analysis['recovery_strategy']}")
    print(f"推荐风险调整: {recovery_analysis['recommended_risk_adjustment']:.2f}")
    
    print("\n=== 系统演示完成 ===")

if __name__ == "__main__":
    main()