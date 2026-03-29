#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格行为规则整合器
将AL Brooks价格行为理论规则注入技术分析框架

整合的规则来源：
1. 区间篇第16-18章：市场结构识别、趋势通道、多时间框架协调
2. 区间篇第19章：高级入场技术
3. 区间篇第20章：出场策略优化
4. 区间篇第21章：仓位规模调整
5. 区间篇第22章：心理纪律管理
6. 区间篇第23章：交易计划制定
7. 反转篇第2章：反转模式识别
8. 反转篇第3章：反转确认信号
9. 趋势篇：趋势识别、趋势强度评估、趋势健康度分析、趋势延续信号
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class PriceActionRulesIntegrator:
    """
    价格行为规则整合器
    将AL Brooks理论规则注入技术分析结果
    """
    
    def __init__(self):
        """初始化规则整合器"""
        self.rules = self._initialize_rules()
        
    def _initialize_rules(self) -> Dict[str, Any]:
        """初始化价格行为规则库"""
        return {
            # 磁力位验证规则（基于第18章：市场结构识别）
            'magnetic_level_validation': {
                'min_touch_points': 2,  # 最小触及次数
                'timeframe_confirmation': True,  # 需要多时间框架确认
                'volume_confirmation': True,  # 需要成交量确认
                'price_action_confirmation': True,  # 需要价格行为确认
            },
            
            # 入场信号规则（基于第19章：高级入场技术）
            'entry_signals': {
                'pullback_to_support': {
                    'description': '回调至支撑位入场',
                    'required_conditions': [
                        'clear_support_level',
                        'bullish_momentum',
                        'volume_confirmation',
                        'price_action_reversal'
                    ],
                    'confidence_threshold': 0.7
                },
                'breakout_from_resistance': {
                    'description': '突破阻力位入场',
                    'required_conditions': [
                        'clear_resistance_level',
                        'strong_volume',
                        'follow_through',
                        'price_above_resistance'
                    ],
                    'confidence_threshold': 0.75
                },
                'reversal_pattern': {
                    'description': '反转模式入场',
                    'required_conditions': [
                        'identified_pattern',
                        'pattern_confirmation',
                        'volume_confirmation',
                        'key_level_proximity'
                    ],
                    'confidence_threshold': 0.65
                },
                'trend_pullback_entry': {
                    'description': '趋势回调入场',
                    'required_conditions': [
                        'clear_trend_direction',
                        'pullback_to_key_level',
                        'trend_strength_confirmation',
                        'volume_confirmation',
                        'price_action_reversal'
                    ],
                    'confidence_threshold': 0.7
                },
                'trend_breakout_entry': {
                    'description': '趋势突破入场',
                    'required_conditions': [
                        'clear_trend_direction',
                        'breakout_from_consolidation',
                        'strong_volume',
                        'follow_through',
                        'price_above_resistance'  # 对于上升趋势
                    ],
                    'confidence_threshold': 0.75
                }
            },
            
            # 风险管理规则（基于第20章：出场策略优化，第21章：仓位规模调整）
            'risk_management': {
                'stop_loss_placement': {
                    'below_support_for_long': True,
                    'above_resistance_for_short': True,
                    'atr_multiplier': 1.5,  # ATR倍数
                    'key_level_buffer': 0.005,  # 关键水平缓冲（0.5%）
                },
                'position_sizing': {
                    'max_risk_per_trade': 0.02,  # 单笔交易最大风险（2%）
                    'risk_reward_minimum': 1.5,  # 最小风险回报比
                    'volatility_adjustment': True,  # 波动率调整
                },
                'take_profit': {
                    'next_key_level': True,  # 下一关键水平止盈
                    'risk_reward_ratio': True,  # 基于风险回报比止盈
                    'trailing_stop': True,  # 移动止损
                }
            },
            
            # 交易计划规则（基于第23章：交易计划制定）
            'trading_plan': {
                'pre_trade_checklist': [
                    'market_structure_analysis',
                    'key_level_identification',
                    'entry_signal_confirmation',
                    'risk_parameters_calculation',
                    'trade_management_plan'
                ],
                'trade_management': {
                    'scaling_in': False,  # 是否分批入场
                    'scaling_out': True,  # 是否分批出场
                    'breakeven_stop': True,  # 是否设置保本止损
                    'trailing_stop_activation': 1.5  # 移动止损激活条件（风险回报比）
                }
            },
            
            # 趋势分析规则（基于AL Brooks趋势篇）
            'trend_analysis': {
                'trend_identification': {
                    'min_trend_bars': 20,  # 最小趋势条形数
                    'min_slope_threshold': 0.001,  # 最小斜率阈值
                    'higher_highs_lows_required': True,  # 需要更高高点和更高低点（上升趋势）
                    'lower_highs_lows_required': True,  # 需要更低高点和更低低点（下降趋势）
                },
                'trend_strength': {
                    'slope_weight': 0.3,  # 斜率权重
                    'duration_weight': 0.2,  # 持续时间权重
                    'consistency_weight': 0.3,  # 一致性权重
                    'volume_weight': 0.2,  # 成交量权重
                },
                'trend_health': {
                    'pullback_depth_max': 0.382,  # 最大回调深度（斐波那契）
                    'volume_divergence_check': True,  # 成交量背离检查
                    'momentum_divergence_check': True,  # 动量背离检查
                    'trend_line_breaks': 2,  # 趋势线突破次数警告
                },
                'trend_continuation': {
                    'retest_after_breakout': True,  # 突破后回测
                    'pattern_within_trend': True,  # 趋势内形态
                    'volume_confirmation': True,  # 成交量确认
                }
            },
            
            # 心理纪律规则（基于第22章：心理纪律管理）
            'psychological_discipline': {
                'max_consecutive_losses': 3,  # 最大连续亏损次数
                'daily_loss_limit': 0.05,  # 单日最大损失（5%）
                'winning_streak_caution': 5,  # 连胜警戒线
                'emotional_state_monitoring': True  # 情绪状态监控
            }
        }
    
    def integrate_rules(self, analysis_results: Dict[str, Any], price_data: pd.DataFrame) -> Dict[str, Any]:
        """
        整合价格行为规则到分析结果中
        
        参数:
            analysis_results: 优化引擎的分析结果
            price_data: 原始价格数据
            
        返回:
            增强的分析结果，包含价格行为规则验证和信号
        """
        print("=" * 60)
        print("开始价格行为规则整合...")
        print("=" * 60)
        
        enhanced_results = analysis_results.copy()
        
        # 1. 磁力位验证与增强
        print("1. 应用磁力位验证规则...")
        enhanced_results['validated_magnetic_levels'] = self._validate_magnetic_levels(
            analysis_results.get('magnetic_levels', {}),
            price_data
        )
        
        # 2. 趋势分析与增强
        print("2. 趋势分析与增强...")
        enhanced_results['trend_analysis'] = self._analyze_trend_characteristics(
            price_data,
            analysis_results.get('market_state', {}),
            enhanced_results['validated_magnetic_levels']
        )
        
        # 3. 入场信号生成
        print("3. 生成价格行为入场信号...")
        enhanced_results['price_action_signals'] = self._generate_price_action_signals(
            enhanced_results['validated_magnetic_levels'],
            analysis_results.get('market_state', {}),
            analysis_results.get('price_volume', {}),
            price_data,
            enhanced_results['trend_analysis']  # 传递趋势分析结果
        )
        
        # 4. 风险管理参数计算
        print("4. 计算风险管理参数...")
        enhanced_results['risk_parameters'] = self._calculate_risk_parameters(
            enhanced_results['price_action_signals'],
            price_data,
            analysis_results.get('market_state', {})
        )
        
        # 5. 交易计划创建
        print("5. 创建交易计划...")
        enhanced_results['trading_plans'] = self._create_trading_plans(
            enhanced_results['price_action_signals'],
            enhanced_results['risk_parameters'],
            analysis_results.get('market_state', {})
        )
        
        # 6. 心理纪律检查
        print("6. 进行心理纪律检查...")
        enhanced_results['psychological_checks'] = self._perform_psychological_checks(
            enhanced_results['trading_plans'],
            analysis_results.get('market_state', {})
        )
        
        print("=" * 60)
        print("价格行为规则整合完成!")
        print("=" * 60)
        
        return enhanced_results
    
    def _validate_magnetic_levels(self, magnetic_levels: Dict[str, Any], price_data: pd.DataFrame) -> Dict[str, Any]:
        """验证磁力位有效性（基于第18章规则）"""
        validated_levels = {
            'support_levels': [],
            'resistance_levels': [],
            'rejected_levels': [],
            'validation_metrics': {}
        }
        
        # 提取价格数据
        closes = price_data['close'].values
        highs = price_data['high'].values
        lows = price_data['low'].values
        volumes = price_data['volume'].values
        
        # 计算技术指标用于验证
        atr = self._calculate_atr(highs, lows, closes, period=14)
        avg_volume = np.mean(volumes) if len(volumes) > 0 else 1
        
        # 验证支撑位
        for level in magnetic_levels.get('support_levels', []):
            validation_result = self._validate_single_level(level, 'support', closes, highs, lows, volumes, atr, avg_volume)
            
            if validation_result['is_valid']:
                validated_levels['support_levels'].append(validation_result)
            else:
                validated_levels['rejected_levels'].append({
                    'level': level,
                    'reason': validation_result['rejection_reason'],
                    'type': 'support'
                })
        
        # 验证阻力位
        for level in magnetic_levels.get('resistance_levels', []):
            validation_result = self._validate_single_level(level, 'resistance', closes, highs, lows, volumes, atr, avg_volume)
            
            if validation_result['is_valid']:
                validated_levels['resistance_levels'].append(validation_result)
            else:
                validated_levels['rejected_levels'].append({
                    'level': level,
                    'reason': validation_result['rejection_reason'],
                    'type': 'resistance'
                })
        
        # 计算验证指标
        total_levels = len(magnetic_levels.get('support_levels', [])) + len(magnetic_levels.get('resistance_levels', []))
        validated_count = len(validated_levels['support_levels']) + len(validated_levels['resistance_levels'])
        
        validated_levels['validation_metrics'] = {
            'total_levels_analyzed': total_levels,
            'validated_levels': validated_count,
            'validation_rate': validated_count / total_levels if total_levels > 0 else 0,
            'avg_validation_score': self._calculate_avg_validation_score(validated_levels)
        }
        
        return validated_levels
    
    def _validate_single_level(self, level: Dict, level_type: str, 
                               closes: np.ndarray, highs: np.ndarray, lows: np.ndarray,
                               volumes: np.ndarray, atr: np.ndarray, avg_volume: float) -> Dict[str, Any]:
        """验证单个价格水平"""
        price = level.get('price', 0)
        
        # 初始化验证结果
        validation = {
            'original_level': level,
            'price': price,
            'type': level_type,
            'is_valid': False,
            'validation_score': 0.0,
            'validation_details': {},
            'rejection_reason': None
        }
        
        # 计算验证分数（0-100）
        score_components = {}
        
        # 1. 价格触及次数验证
        touch_count, touch_details = self._count_price_touches(price, level_type, closes, highs, lows)
        score_components['touch_count'] = min(10, touch_count) * 10  # 最高100分
        
        # 2. 成交量确认验证
        volume_score = self._validate_volume_confirmation(price, level_type, closes, volumes, avg_volume)
        score_components['volume_confirmation'] = volume_score * 100
        
        # 3. 价格行为确认验证
        price_action_score = self._validate_price_action(price, level_type, closes, highs, lows)
        score_components['price_action'] = price_action_score * 100
        
        # 4. 时间框架一致性验证（简化版）
        timeframe_score = self._validate_timeframe_consistency(price, level_type, closes)
        score_components['timeframe_consistency'] = timeframe_score * 100
        
        # 5. 波动率调整验证
        volatility_score = self._validate_volatility_adjustment(price, atr)
        score_components['volatility_adjustment'] = volatility_score * 100
        
        # 计算综合分数
        weights = {
            'touch_count': 0.25,
            'volume_confirmation': 0.20,
            'price_action': 0.25,
            'timeframe_consistency': 0.15,
            'volatility_adjustment': 0.15
        }
        
        total_score = 0
        for component, weight in weights.items():
            if component in score_components:
                total_score += score_components[component] * weight
        
        validation['validation_score'] = total_score
        validation['validation_details'] = score_components
        validation['validation_details']['touch_details'] = touch_details
        
        # 判断是否有效
        validation_threshold = 60.0  # 60分阈值
        
        if total_score >= validation_threshold:
            validation['is_valid'] = True
        else:
            validation['is_valid'] = False
            validation['rejection_reason'] = f'验证分数不足: {total_score:.1f}/{validation_threshold}'
        
        return validation
    
    def _count_price_touches(self, price: float, level_type: str, 
                            closes: np.ndarray, highs: np.ndarray, lows: np.ndarray,
                            tolerance: float = 0.01) -> Tuple[int, Dict]:
        """计算价格触及关键水平的次数"""
        touches = 0
        touch_details = {
            'exact_touches': 0,
            'near_touches': 0,
            'rejections': 0,
            'penetrations': 0
        }
        
        price_tolerance = price * tolerance
        
        for i in range(len(closes)):
            # 检查是否触及
            if level_type == 'support':
                # 支撑位：价格下跌到该水平附近
                if lows[i] <= price + price_tolerance and lows[i] >= price - price_tolerance:
                    touches += 1
                    
                    # 分类触及类型
                    if abs(lows[i] - price) <= price_tolerance * 0.1:
                        touch_details['exact_touches'] += 1
                    else:
                        touch_details['near_touches'] += 1
                    
                    # 检查是否被拒绝（价格反弹）
                    if i < len(closes) - 1 and closes[i+1] > closes[i]:
                        touch_details['rejections'] += 1
                    elif i < len(closes) - 1 and closes[i+1] < closes[i]:
                        touch_details['penetrations'] += 1
                        
            elif level_type == 'resistance':
                # 阻力位：价格上涨到该水平附近
                if highs[i] >= price - price_tolerance and highs[i] <= price + price_tolerance:
                    touches += 1
                    
                    if abs(highs[i] - price) <= price_tolerance * 0.1:
                        touch_details['exact_touches'] += 1
                    else:
                        touch_details['near_touches'] += 1
                    
                    # 检查是否被拒绝（价格回落）
                    if i < len(closes) - 1 and closes[i+1] < closes[i]:
                        touch_details['rejections'] += 1
                    elif i < len(closes) - 1 and closes[i+1] > closes[i]:
                        touch_details['penetrations'] += 1
        
        return touches, touch_details
    
    def _validate_volume_confirmation(self, price: float, level_type: str,
                                     closes: np.ndarray, volumes: np.ndarray,
                                     avg_volume: float) -> float:
        """验证成交量确认"""
        if len(closes) < 2 or len(volumes) < 2:
            return 0.5
        
        # 查找价格接近该水平的时间点
        tolerance = price * 0.015  # 1.5%容忍度
        touch_indices = []
        
        for i in range(len(closes)):
            if level_type == 'support':
                if closes[i] <= price + tolerance and closes[i] >= price - tolerance:
                    touch_indices.append(i)
            elif level_type == 'resistance':
                if closes[i] >= price - tolerance and closes[i] <= price + tolerance:
                    touch_indices.append(i)
        
        if not touch_indices:
            return 0.3
        
        # 分析触及时的成交量
        volume_scores = []
        
        for idx in touch_indices:
            if idx < len(volumes):
                touch_volume = volumes[idx]
                
                # 成交量相对于平均成交量的比率
                volume_ratio = touch_volume / avg_volume if avg_volume > 0 else 1.0
                
                # 评分逻辑：适度放量最好
                if volume_ratio > 2.0:
                    # 过度放量可能表示 exhaustion
                    score = 0.6
                elif volume_ratio > 1.2:
                    # 健康放量
                    score = 0.9
                elif volume_ratio > 0.8:
                    # 正常成交量
                    score = 0.7
                else:
                    # 缩量，确认不足
                    score = 0.4
                
                volume_scores.append(score)
        
        return np.mean(volume_scores) if volume_scores else 0.5
    
    def _validate_price_action(self, price: float, level_type: str,
                              closes: np.ndarray, highs: np.ndarray, lows: np.ndarray) -> float:
        """验证价格行为确认"""
        if len(closes) < 3:
            return 0.5
        
        # 查找价格接近该水平的时间点
        tolerance = price * 0.02
        confirmation_events = 0
        total_events = 0
        
        for i in range(1, len(closes) - 1):
            if level_type == 'support':
                # 检查是否形成看涨反转模式
                if lows[i] <= price + tolerance:
                    # 检查锤子线、看涨吞没等模式（简化版）
                    is_bullish_reversal = self._check_bullish_reversal(i, closes, highs, lows)
                    if is_bullish_reversal:
                        confirmation_events += 1
                    total_events += 1
                    
            elif level_type == 'resistance':
                # 检查是否形成看跌反转模式
                if highs[i] >= price - tolerance:
                    is_bearish_reversal = self._check_bearish_reversal(i, closes, highs, lows)
                    if is_bearish_reversal:
                        confirmation_events += 1
                    total_events += 1
        
        if total_events == 0:
            return 0.5
        
        return confirmation_events / total_events
    
    def _check_bullish_reversal(self, idx: int, closes: np.ndarray, 
                               highs: np.ndarray, lows: np.ndarray) -> bool:
        """检查看涨反转模式（简化版）"""
        if idx < 2 or idx >= len(closes) - 1:
            return False
        
        # 简化版锤子线检测
        current_body = abs(closes[idx] - closes[idx-1])
        current_range = highs[idx] - lows[idx]
        
        if current_range > 0:
            body_to_range_ratio = current_body / current_range
            
            # 锤子线特征：小实体，长下影线
            if body_to_range_ratio < 0.3 and closes[idx] > closes[idx-1]:
                return True
        
        # 检查看涨吞没
        if closes[idx] > closes[idx-1] and closes[idx-1] < closes[idx-2]:
            # 当前K线收盘高于前一根K线收盘
            return True
        
        return False
    
    def _check_bearish_reversal(self, idx: int, closes: np.ndarray,
                               highs: np.ndarray, lows: np.ndarray) -> bool:
        """检查看跌反转模式（简化版）"""
        if idx < 2 or idx >= len(closes) - 1:
            return False
        
        # 简化版上吊线/射击之星检测
        current_body = abs(closes[idx] - closes[idx-1])
        current_range = highs[idx] - lows[idx]
        
        if current_range > 0:
            body_to_range_ratio = current_body / current_range
            
            # 射击之星特征：小实体，长上影线
            if body_to_range_ratio < 0.3 and closes[idx] < closes[idx-1]:
                return True
        
        # 检查看跌吞没
        if closes[idx] < closes[idx-1] and closes[idx-1] > closes[idx-2]:
            # 当前K线收盘低于前一根K线收盘
            return True
        
        return False
    
    def _validate_timeframe_consistency(self, price: float, level_type: str,
                                       closes: np.ndarray) -> float:
        """验证时间框架一致性（简化版）"""
        if len(closes) < 20:
            return 0.5
        
        # 检查不同时间窗口内该水平的重要性
        windows = [5, 10, 20]
        consistency_scores = []
        
        for window in windows:
            if len(closes) >= window:
                # 检查该水平在窗口内是否显著
                window_closes = closes[-window:]
                window_high = np.max(window_closes)
                window_low = np.min(window_closes)
                window_range = window_high - window_low
                
                if window_range > 0:
                    # 计算价格在窗口范围内的位置
                    price_position = (price - window_low) / window_range
                    
                    # 支撑位应该在底部区域，阻力位应该在顶部区域
                    if level_type == 'support' and price_position < 0.3:
                        consistency_scores.append(0.8)
                    elif level_type == 'resistance' and price_position > 0.7:
                        consistency_scores.append(0.8)
                    else:
                        consistency_scores.append(0.4)
        
        return np.mean(consistency_scores) if consistency_scores else 0.5
    
    def _validate_volatility_adjustment(self, price: float, atr: np.ndarray) -> float:
        """验证波动率调整"""
        if len(atr) == 0:
            return 0.5
        
        recent_atr = atr[-1] if len(atr) > 0 else np.mean(atr) if len(atr) > 0 else price * 0.01
        
        # 检查价格是否在合理的ATR范围内
        # 理想情况下，关键水平应该与最近的波动率相关
        atr_ratio = recent_atr / price if price > 0 else 0.01
        
        # ATR比率在1%-3%之间为最佳
        if 0.01 <= atr_ratio <= 0.03:
            return 0.9
        elif 0.005 <= atr_ratio <= 0.05:
            return 0.7
        else:
            return 0.4
    
    def _calculate_atr(self, highs: np.ndarray, lows: np.ndarray, 
                      closes: np.ndarray, period: int = 14) -> np.ndarray:
        """计算平均真实范围（ATR）"""
        if len(highs) < period or len(lows) < period or len(closes) < period:
            return np.array([])
        
        tr = np.zeros(len(highs))
        tr[0] = highs[0] - lows[0]
        
        for i in range(1, len(highs)):
            hl = highs[i] - lows[i]
            hc = abs(highs[i] - closes[i-1])
            lc = abs(lows[i] - closes[i-1])
            tr[i] = max(hl, hc, lc)
        
        atr = np.zeros(len(tr))
        atr[period-1] = np.mean(tr[:period])
        
        for i in range(period, len(tr)):
            atr[i] = (atr[i-1] * (period - 1) + tr[i]) / period
        
        return atr
    
    def _calculate_avg_validation_score(self, validated_levels: Dict[str, Any]) -> float:
        """计算平均验证分数"""
        all_scores = []
        
        for level in validated_levels.get('support_levels', []):
            all_scores.append(level.get('validation_score', 0))
        
        for level in validated_levels.get('resistance_levels', []):
            all_scores.append(level.get('validation_score', 0))
        
        return np.mean(all_scores) if all_scores else 0.0
    
    def _analyze_trend_characteristics(self, price_data: pd.DataFrame, 
                                      market_state: Dict[str, Any],
                                      validated_levels: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析趋势特征（基于AL Brooks趋势篇）
        
        参数:
            price_data: 价格数据
            market_state: 市场状态
            validated_levels: 验证后的磁力位
            
        返回:
            趋势分析结果
        """
        closes = price_data['close'].values
        highs = price_data['high'].values
        lows = price_data['low'].values
        volumes = price_data['volume'].values if 'volume' in price_data.columns else np.zeros_like(closes)
        
        # 简化版趋势分析
        # 1. 趋势方向判断
        if len(closes) < 20:
            return {
                'trend_direction': 'neutral',
                'trend_strength': 'weak',
                'trend_health': 'unknown',
                'confidence': 0.0
            }
        
        # 计算短期和长期斜率
        short_period = min(20, len(closes))
        long_period = min(50, len(closes))
        
        short_slope = self._calculate_slope(closes[-short_period:])
        long_slope = self._calculate_slope(closes[-long_period:])
        
        # 判断趋势方向
        if long_slope > 0.001 and short_slope > 0:
            trend_direction = 'bullish'
        elif long_slope < -0.001 and short_slope < 0:
            trend_direction = 'bearish'
        else:
            trend_direction = 'neutral'
        
        # 趋势强度评估
        slope_magnitude = abs(long_slope)
        if slope_magnitude > 0.005:
            trend_strength = 'strong'
        elif slope_magnitude > 0.002:
            trend_strength = 'medium'
        else:
            trend_strength = 'weak'
        
        # 趋势健康度评估（简化）
        recent_max = highs[-10:].max() if len(highs) >= 10 else highs.max()
        recent_min = lows[-10:].min() if len(lows) >= 10 else lows.min()
        price_range = recent_max - recent_min
        
        if price_range > 0:
            current_position = (closes[-1] - recent_min) / price_range
            if 0.3 < current_position < 0.7:
                trend_health = 'healthy'
            else:
                trend_health = 'extended'
        else:
            trend_health = 'unknown'
        
        # 趋势置信度
        consistency = 1.0 if np.sign(short_slope) == np.sign(long_slope) else 0.5
        volume_trend = 1.0 if len(volumes) > 10 and volumes[-5:].mean() > volumes[-10:-5].mean() else 0.5
        
        confidence = (consistency + volume_trend) / 2
        
        return {
            'trend_direction': trend_direction,
            'trend_strength': trend_strength,
            'trend_health': trend_health,
            'confidence': confidence,
            'short_slope': short_slope,
            'long_slope': long_slope,
            'price_range': price_range,
            'current_position': current_position if price_range > 0 else 0.5
        }
    
    def _calculate_slope(self, values: np.ndarray) -> float:
        """计算线性回归斜率"""
        if len(values) < 2:
            return 0.0
        x = np.arange(len(values))
        slope, _ = np.polyfit(x, values, 1)
        return slope
    
    def _generate_price_action_signals(self, validated_levels: Dict[str, Any],
                                      market_state: Dict[str, Any],
                                      price_volume_analysis: Dict[str, Any],
                                      price_data: pd.DataFrame,
                                      trend_analysis: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """生成价格行为交易信号（整合趋势分析）"""
        signals = {
            'entry_signals': [],
            'exit_signals': [],
            'monitoring_signals': [],
            'signal_quality_metrics': {}
        }
        
        closes = price_data['close'].values
        current_price = closes[-1] if len(closes) > 0 else 0
        
        # 根据市场状态确定信号生成策略
        market_regime = market_state.get('market_regime', 'unknown')
        trend_direction = market_state.get('trend_direction', 'neutral')
        
        # 整合趋势分析结果（如果提供）
        if trend_analysis is not None:
            # 使用趋势分析增强市场状态
            trend_strength = trend_analysis.get('trend_strength', 'medium')
            trend_health = trend_analysis.get('trend_health', 'healthy')
            # 调整趋势方向置信度
            if trend_strength == 'strong':
                market_regime = 'trend'  # 强制设为趋势市场
                trend_direction = trend_analysis.get('trend_direction', trend_direction)
            elif trend_strength == 'weak' and market_regime == 'trend':
                market_regime = 'range'  # 弱趋势视为区间
            # 记录趋势分析结果
            signals['trend_analysis'] = trend_analysis
        
        # 生成入场信号
        if market_regime == 'range':
            # 区间市场：在边界附近寻找反转信号
            signals['entry_signals'].extend(
                self._generate_range_trading_signals(validated_levels, current_price, price_data)
            )
        elif market_regime == 'trend':
            # 趋势市场：寻找回调入场机会
            signals['entry_signals'].extend(
                self._generate_trend_following_signals(validated_levels, trend_direction, current_price, price_data)
            )
        
        # 生成出场信号
        signals['exit_signals'].extend(
            self._generate_exit_signals(validated_levels, current_price, price_data)
        )
        
        # 生成监控信号
        signals['monitoring_signals'].extend(
            self._generate_monitoring_signals(validated_levels, market_state, current_price)
        )
        
        # 计算信号质量指标
        signals['signal_quality_metrics'] = self._calculate_signal_quality_metrics(signals)
        
        return signals
    
    def _generate_range_trading_signals(self, validated_levels: Dict[str, Any],
                                       current_price: float, price_data: pd.DataFrame) -> List[Dict]:
        """生成区间交易信号"""
        signals = []
        
        closes = price_data['close'].values
        volumes = price_data['volume'].values
        
        # 检查是否接近支撑位
        for support in validated_levels.get('support_levels', []):
            if support.get('is_valid', False):
                support_price = support.get('price', 0)
                price_diff_pct = abs(current_price - support_price) / support_price if support_price > 0 else 0
                
                # 价格接近支撑位（3%以内）
                if price_diff_pct <= 0.03 and current_price >= support_price:
                    # 检查是否出现看涨反转迹象
                    is_bullish_reversal = self._check_recent_bullish_reversal(closes, volumes)
                    
                    signal = {
                        'type': 'range_buy',
                        'level_type': 'support',
                        'level_price': support_price,
                        'current_price': current_price,
                        'distance_pct': price_diff_pct * 100,
                        'signal_strength': max(0.5, 1.0 - price_diff_pct / 0.03),
                        'conditions_met': {
                            'near_support': price_diff_pct <= 0.03,
                            'bullish_reversal': is_bullish_reversal,
                            'volume_confirmation': self._check_volume_confirmation(volumes, 'increase'),
                            'validation_score': support.get('validation_score', 0) / 100
                        },
                        'action': '考虑在支撑位附近买入，等待反转确认',
                        'confidence': min(0.8, support.get('validation_score', 0) / 100 * 0.9)
                    }
                    
                    signals.append(signal)
        
        # 检查是否接近阻力位
        for resistance in validated_levels.get('resistance_levels', []):
            if resistance.get('is_valid', False):
                resistance_price = resistance.get('price', 0)
                price_diff_pct = abs(current_price - resistance_price) / resistance_price if resistance_price > 0 else 0
                
                # 价格接近阻力位（3%以内）
                if price_diff_pct <= 0.03 and current_price <= resistance_price:
                    # 检查是否出现看跌反转迹象
                    is_bearish_reversal = self._check_recent_bearish_reversal(closes, volumes)
                    
                    signal = {
                        'type': 'range_sell',
                        'level_type': 'resistance',
                        'level_price': resistance_price,
                        'current_price': current_price,
                        'distance_pct': price_diff_pct * 100,
                        'signal_strength': max(0.5, 1.0 - price_diff_pct / 0.03),
                        'conditions_met': {
                            'near_resistance': price_diff_pct <= 0.03,
                            'bearish_reversal': is_bearish_reversal,
                            'volume_confirmation': self._check_volume_confirmation(volumes, 'increase'),
                            'validation_score': resistance.get('validation_score', 0) / 100
                        },
                        'action': '考虑在阻力位附近卖出，等待反转确认',
                        'confidence': min(0.8, resistance.get('validation_score', 0) / 100 * 0.9)
                    }
                    
                    signals.append(signal)
        
        return signals
    
    def _generate_trend_following_signals(self, validated_levels: Dict[str, Any],
                                         trend_direction: str, current_price: float,
                                         price_data: pd.DataFrame) -> List[Dict]:
        """生成趋势跟踪信号"""
        signals = []
        
        closes = price_data['close'].values
        volumes = price_data['volume'].values
        
        if trend_direction == 'bullish':
            # 上升趋势：寻找回调至支撑位的买入机会
            for support in validated_levels.get('support_levels', []):
                if support.get('is_valid', False):
                    support_price = support.get('price', 0)
                    price_diff_pct = abs(current_price - support_price) / support_price if support_price > 0 else 0
                    
                    # 价格回调至支撑位附近
                    if price_diff_pct <= 0.02 and current_price >= support_price:
                        # 检查趋势是否仍然健康
                        is_trend_healthy = self._check_trend_health(closes, 'bullish')
                        
                        signal = {
                            'type': 'trend_pullback_buy',
                            'level_type': 'support',
                            'level_price': support_price,
                            'current_price': current_price,
                            'distance_pct': price_diff_pct * 100,
                            'signal_strength': max(0.6, 1.0 - price_diff_pct / 0.02),
                            'conditions_met': {
                                'near_support': price_diff_pct <= 0.02,
                                'trend_healthy': is_trend_healthy,
                                'volume_confirmation': self._check_volume_confirmation(volumes, 'increase_on_rise'),
                                'validation_score': support.get('validation_score', 0) / 100
                            },
                            'action': '趋势回调买入，等待趋势恢复',
                            'confidence': min(0.75, support.get('validation_score', 0) / 100 * 0.85)
                        }
                        
                        signals.append(signal)
                        
        elif trend_direction == 'bearish':
            # 下降趋势：寻找反弹至阻力位的卖出机会
            for resistance in validated_levels.get('resistance_levels', []):
                if resistance.get('is_valid', False):
                    resistance_price = resistance.get('price', 0)
                    price_diff_pct = abs(current_price - resistance_price) / resistance_price if resistance_price > 0 else 0
                    
                    # 价格反弹至阻力位附近
                    if price_diff_pct <= 0.02 and current_price <= resistance_price:
                        is_trend_healthy = self._check_trend_health(closes, 'bearish')
                        
                        signal = {
                            'type': 'trend_rally_sell',
                            'level_type': 'resistance',
                            'level_price': resistance_price,
                            'current_price': current_price,
                            'distance_pct': price_diff_pct * 100,
                            'signal_strength': max(0.6, 1.0 - price_diff_pct / 0.02),
                            'conditions_met': {
                                'near_resistance': price_diff_pct <= 0.02,
                                'trend_healthy': is_trend_healthy,
                                'volume_confirmation': self._check_volume_confirmation(volumes, 'increase_on_fall'),
                                'validation_score': resistance.get('validation_score', 0) / 100
                            },
                            'action': '趋势反弹卖出，等待趋势恢复',
                            'confidence': min(0.75, resistance.get('validation_score', 0) / 100 * 0.85)
                        }
                        
                        signals.append(signal)
        
        return signals
    
    def _generate_exit_signals(self, validated_levels: Dict[str, Any],
                              current_price: float, price_data: pd.DataFrame) -> List[Dict]:
        """生成出场信号"""
        signals = []
        
        closes = price_data['close'].values
        
        # 简化版出场信号：基于关键水平和价格行为
        # 这里可以根据实际持仓情况生成更复杂的出场信号
        
        return signals
    
    def _generate_monitoring_signals(self, validated_levels: Dict[str, Any],
                                    market_state: Dict[str, Any], current_price: float) -> List[Dict]:
        """生成监控信号"""
        signals = []
        
        # 监控关键水平突破
        for resistance in validated_levels.get('resistance_levels', []):
            if resistance.get('is_valid', False):
                resistance_price = resistance.get('price', 0)
                
                # 监控阻力位突破
                if current_price > resistance_price * 1.01:  # 突破1%以上
                    signals.append({
                        'type': 'breakout_monitor',
                        'level_type': 'resistance',
                        'level_price': resistance_price,
                        'current_price': current_price,
                        'breakout_pct': (current_price / resistance_price - 1) * 100,
                        'action': '监控阻力位突破，确认是否有效突破',
                        'importance': 'high'
                    })
        
        for support in validated_levels.get('support_levels', []):
            if support.get('is_valid', False):
                support_price = support.get('price', 0)
                
                # 监控支撑位跌破
                if current_price < support_price * 0.99:  # 跌破1%以上
                    signals.append({
                        'type': 'breakdown_monitor',
                        'level_type': 'support',
                        'level_price': support_price,
                        'current_price': current_price,
                        'breakdown_pct': (1 - current_price / support_price) * 100,
                        'action': '监控支撑位跌破，确认是否有效跌破',
                        'importance': 'high'
                    })
        
        return signals
    
    def _check_recent_bullish_reversal(self, closes: np.ndarray, volumes: np.ndarray) -> bool:
        """检查近期是否出现看涨反转"""
        if len(closes) < 3:
            return False
        
        # 检查最近3根K线
        recent_closes = closes[-3:]
        
        # 简单模式：低点抬高或看涨吞没
        if len(recent_closes) >= 3:
            # 低点抬高
            if recent_closes[2] > recent_closes[1] > recent_closes[0]:
                return True
            
            # 看涨吞没模式（简化）
            if recent_closes[2] > recent_closes[0] and recent_closes[1] < recent_closes[0]:
                return True
        
        return False
    
    def _check_recent_bearish_reversal(self, closes: np.ndarray, volumes: np.ndarray) -> bool:
        """检查近期是否出现看跌反转"""
        if len(closes) < 3:
            return False
        
        # 检查最近3根K线
        recent_closes = closes[-3:]
        
        # 简单模式：高点降低或看跌吞没
        if len(recent_closes) >= 3:
            # 高点降低
            if recent_closes[2] < recent_closes[1] < recent_closes[0]:
                return True
            
            # 看跌吞没模式（简化）
            if recent_closes[2] < recent_closes[0] and recent_closes[1] > recent_closes[0]:
                return True
        
        return False
    
    def _check_volume_confirmation(self, volumes: np.ndarray, confirmation_type: str) -> bool:
        """检查成交量确认"""
        if len(volumes) < 5:
            return False
        
        recent_volumes = volumes[-5:]
        avg_volume = np.mean(volumes[:-5]) if len(volumes) > 5 else np.mean(volumes)
        
        if avg_volume == 0:
            return False
        
        if confirmation_type == 'increase':
            # 成交量增加
            return np.mean(recent_volumes[-2:]) > avg_volume * 1.2
        elif confirmation_type == 'increase_on_rise':
            # 上涨时成交量增加
            return np.mean(recent_volumes[-2:]) > avg_volume * 1.1
        elif confirmation_type == 'increase_on_fall':
            # 下跌时成交量增加
            return np.mean(recent_volumes[-2:]) > avg_volume * 1.1
        
        return False
    
    def _check_trend_health(self, closes: np.ndarray, trend_direction: str) -> bool:
        """检查趋势健康状况"""
        if len(closes) < 10:
            return False
        
        # 计算短期和中期均线
        short_ma = np.mean(closes[-5:]) if len(closes) >= 5 else closes[-1]
        medium_ma = np.mean(closes[-10:]) if len(closes) >= 10 else closes[-1]
        
        if trend_direction == 'bullish':
            # 上升趋势：短期均线在中期均线之上
            return short_ma > medium_ma
        elif trend_direction == 'bearish':
            # 下降趋势：短期均线在中期均线之下
            return short_ma < medium_ma
        
        return False
    
    def _calculate_signal_quality_metrics(self, signals: Dict[str, Any]) -> Dict[str, float]:
        """计算信号质量指标"""
        metrics = {
            'total_signals': 0,
            'avg_confidence': 0.0,
            'avg_signal_strength': 0.0,
            'signal_distribution': {},
            'quality_score': 0.0
        }
        
        all_signals = signals.get('entry_signals', [])
        metrics['total_signals'] = len(all_signals)
        
        if all_signals:
            confidences = [s.get('confidence', 0) for s in all_signals]
            strengths = [s.get('signal_strength', 0) for s in all_signals]
            
            metrics['avg_confidence'] = float(np.mean(confidences))
            metrics['avg_signal_strength'] = float(np.mean(strengths))
            
            # 信号类型分布
            signal_types = {}
            for signal in all_signals:
                sig_type = signal.get('type', 'unknown')
                signal_types[sig_type] = signal_types.get(sig_type, 0) + 1
            
            metrics['signal_distribution'] = signal_types
            
            # 综合质量分数
            metrics['quality_score'] = float(
                metrics['avg_confidence'] * 0.6 + 
                metrics['avg_signal_strength'] * 0.4
            )
        
        return metrics
    
    def _calculate_risk_parameters(self, price_action_signals: Dict[str, Any],
                                  price_data: pd.DataFrame,
                                  market_state: Dict[str, Any]) -> Dict[str, Any]:
        """计算风险管理参数"""
        risk_params = {
            'position_sizing': {},
            'stop_loss_levels': {},
            'take_profit_levels': {},
            'risk_reward_ratios': {},
            'volatility_adjustments': {}
        }
        
        closes = price_data['close'].values
        highs = price_data['high'].values
        lows = price_data['low'].values
        
        current_price = closes[-1] if len(closes) > 0 else 0
        
        # 计算ATR用于波动率调整
        atr = self._calculate_atr(highs, lows, closes, period=14)
        current_atr = atr[-1] if len(atr) > 0 else current_price * 0.02
        
        # 为每个入场信号计算风险参数
        for signal in price_action_signals.get('entry_signals', []):
            signal_type = signal.get('type', '')
            level_price = signal.get('level_price', 0)
            
            if level_price == 0:
                continue
            
            # 止损位计算
            if 'buy' in signal_type:
                # 多头交易：止损在支撑位下方
                stop_loss = level_price * 0.98  # 支撑位下方2%
                stop_loss_atr = current_price - current_atr * 1.5
                stop_loss = min(stop_loss, stop_loss_atr)  # 取更保守的值
                
                # 止盈位计算
                take_profit_1 = level_price * 1.03  # 第一目标：3%
                take_profit_2 = level_price * 1.06  # 第二目标：6%
                
            elif 'sell' in signal_type:
                # 空头交易：止损在阻力位上方
                stop_loss = level_price * 1.02  # 阻力位上方2%
                stop_loss_atr = current_price + current_atr * 1.5
                stop_loss = max(stop_loss, stop_loss_atr)
                
                # 止盈位计算
                take_profit_1 = level_price * 0.97  # 第一目标：-3%
                take_profit_2 = level_price * 0.94  # 第二目标：-6%
            else:
                continue
            
            # 风险回报比计算
            risk_amount = abs(stop_loss - current_price)
            reward_amount_1 = abs(take_profit_1 - current_price)
            reward_amount_2 = abs(take_profit_2 - current_price)
            
            rr_ratio_1 = reward_amount_1 / risk_amount if risk_amount > 0 else 0
            rr_ratio_2 = reward_amount_2 / risk_amount if risk_amount > 0 else 0
            
            # 仓位规模计算（基于2%风险）
            account_size = 100000  # 假设账户规模
            risk_per_trade = account_size * 0.02  # 单笔交易风险2%
            position_size = risk_per_trade / risk_amount if risk_amount > 0 else 0
            
            signal_id = f"{signal_type}_{level_price:.2f}"
            
            risk_params['stop_loss_levels'][signal_id] = float(stop_loss)
            risk_params['take_profit_levels'][signal_id] = {
                'tp1': float(take_profit_1),
                'tp2': float(take_profit_2)
            }
            risk_params['risk_reward_ratios'][signal_id] = {
                'rr1': float(rr_ratio_1),
                'rr2': float(rr_ratio_2)
            }
            risk_params['position_sizing'][signal_id] = {
                'position_size': float(position_size),
                'risk_amount': float(risk_amount),
                'risk_percent': 2.0
            }
        
        # 波动率调整
        risk_params['volatility_adjustments'] = {
            'current_atr': float(current_atr),
            'atr_percent': float(current_atr / current_price * 100) if current_price > 0 else 0,
            'volatility_level': self._classify_volatility(current_atr, current_price)
        }
        
        return risk_params
    
    def _classify_volatility(self, atr: float, price: float) -> str:
        """分类波动率水平"""
        if price == 0:
            return 'unknown'
        
        atr_percent = atr / price * 100
        
        if atr_percent < 1.0:
            return 'low'
        elif atr_percent < 2.5:
            return 'medium'
        elif atr_percent < 5.0:
            return 'high'
        else:
            return 'extreme'
    
    def _create_trading_plans(self, price_action_signals: Dict[str, Any],
                             risk_parameters: Dict[str, Any],
                             market_state: Dict[str, Any]) -> Dict[str, Any]:
        """创建交易计划"""
        trading_plans = {
            'plans': [],
            'plan_summary': {},
            'execution_guidelines': {}
        }
        
        # 为每个高质量信号创建交易计划
        high_quality_signals = []
        for signal in price_action_signals.get('entry_signals', []):
            if signal.get('confidence', 0) >= 0.6:
                high_quality_signals.append(signal)
        
        for signal in high_quality_signals:
            signal_type = signal.get('type', '')
            level_price = signal.get('level_price', 0)
            signal_id = f"{signal_type}_{level_price:.2f}"
            
            # 获取该信号的风险参数
            stop_loss = risk_parameters['stop_loss_levels'].get(signal_id, 0)
            take_profits = risk_parameters['take_profit_levels'].get(signal_id, {})
            rr_ratios = risk_parameters['risk_reward_ratios'].get(signal_id, {})
            position_info = risk_parameters['position_sizing'].get(signal_id, {})
            
            # 创建交易计划
            plan = {
                'signal_id': signal_id,
                'signal_details': signal,
                'entry_conditions': self._define_entry_conditions(signal),
                'entry_execution': self._define_entry_execution(signal),
                'risk_management': {
                    'stop_loss': stop_loss,
                    'take_profits': take_profits,
                    'position_size': position_info.get('position_size', 0),
                    'risk_percent': position_info.get('risk_percent', 2.0)
                },
                'trade_management': self._define_trade_management(signal, stop_loss, take_profits),
                'exit_strategy': self._define_exit_strategy(signal, rr_ratios),
                'monitoring_requirements': self._define_monitoring_requirements(signal),
                'plan_confidence': signal.get('confidence', 0)
            }
            
            trading_plans['plans'].append(plan)
        
        # 计划摘要
        trading_plans['plan_summary'] = {
            'total_plans': len(trading_plans['plans']),
            'avg_confidence': np.mean([p.get('plan_confidence', 0) for p in trading_plans['plans']]) if trading_plans['plans'] else 0,
            'signal_distribution': {},
            'risk_profile': self._assess_risk_profile(trading_plans['plans'])
        }
        
        # 执行指南
        trading_plans['execution_guidelines'] = {
            'pre_trade_checklist': self.rules['trading_plan']['pre_trade_checklist'],
            'order_types': '建议使用限价单在关键水平附近入场',
            'timing': '等待价格行为确认后执行',
            'documentation': '记录交易计划和执行结果'
        }
        
        return trading_plans
    
    def _define_entry_conditions(self, signal: Dict[str, Any]) -> List[str]:
        """定义入场条件"""
        conditions = []
        
        signal_type = signal.get('type', '')
        
        if 'buy' in signal_type:
            conditions.append('价格回调至支撑位附近')
            conditions.append('出现看涨反转价格行为')
            conditions.append('成交量确认反转')
        elif 'sell' in signal_type:
            conditions.append('价格反弹至阻力位附近')
            conditions.append('出现看跌反转价格行为')
            conditions.append('成交量确认反转')
        
        conditions.append('风险回报比不低于1:1.5')
        conditions.append('市场状态支持该交易类型')
        
        return conditions
    
    def _define_entry_execution(self, signal: Dict[str, Any]) -> Dict[str, Any]:
        """定义入场执行"""
        execution = {
            'order_type': 'limit',
            'entry_price': signal.get('level_price', 0) * 0.995 if 'buy' in signal.get('type', '') else signal.get('level_price', 0) * 1.005,
            'validity': 'good_till_cancelled',
            'partial_fill': '允许部分成交',
            'slippage_tolerance': '0.5%'
        }
        
        return execution
    
    def _define_trade_management(self, signal: Dict[str, Any], stop_loss: float, 
                                take_profits: Dict[str, float]) -> Dict[str, Any]:
        """定义交易管理"""
        management = {
            'stop_loss_adjustment': {
                'breakeven': '当价格达到第一目标位时，将止损调整至入场价',
                'trailing_stop': '当价格达到第二目标位时，启动移动止损'
            },
            'position_adjustment': {
                'scaling_in': '不建议加仓',
                'scaling_out': '达到目标位时分批平仓'
            },
            'monitoring_frequency': '每日检查，关键水平附近增加监控频率'
        }
        
        return management
    
    def _define_exit_strategy(self, signal: Dict[str, Any], rr_ratios: Dict[str, float]) -> Dict[str, Any]:
        """定义出场策略"""
        exit_strategy = {
            'primary_exit': '达到第一目标位时平仓1/2',
            'secondary_exit': '达到第二目标位时平仓剩余部分',
            'emergency_exit': '止损触发时立即全部平仓',
            'discretionary_exit': '如果市场状况发生重大变化，考虑提前退出'
        }
        
        return exit_strategy
    
    def _define_monitoring_requirements(self, signal: Dict[str, Any]) -> List[str]:
        """定义监控要求"""
        requirements = [
            '监控关键水平的有效性',
            '监控成交量变化',
            '监控相关市场或板块表现',
            '监控宏观经济新闻事件'
        ]
        
        return requirements
    
    def _assess_risk_profile(self, plans: List[Dict]) -> Dict[str, Any]:
        """评估风险概况"""
        if not plans:
            return {'overall_risk': 'low', 'diversification': 'none'}
        
        # 简单风险评估
        avg_confidence = np.mean([p.get('plan_confidence', 0) for p in plans])
        
        if avg_confidence >= 0.7:
            risk_level = 'low'
        elif avg_confidence >= 0.5:
            risk_level = 'medium'
        else:
            risk_level = 'high'
        
        # 分散度评估
        signal_types = set()
        for plan in plans:
            signal = plan.get('signal_details', {})
            signal_types.add(signal.get('type', ''))
        
        diversification = 'good' if len(signal_types) > 1 else 'poor'
        
        return {
            'overall_risk': risk_level,
            'diversification': diversification,
            'signal_variety': len(signal_types),
            'avg_plan_confidence': avg_confidence
        }
    
    def _perform_psychological_checks(self, trading_plans: Dict[str, Any],
                                     market_state: Dict[str, Any]) -> Dict[str, Any]:
        """进行心理纪律检查"""
        checks = {
            'emotional_state': 'neutral',
            'risk_tolerance_check': 'within_limits',
            'discipline_indicators': [],
            'warnings': [],
            'recommendations': []
        }
        
        # 检查市场状态对心理的影响
        market_regime = market_state.get('market_regime', 'unknown')
        volatility = market_state.get('volatility_level', 'medium')
        
        if volatility == 'high':
            checks['warnings'].append('高波动市场环境，情绪容易波动')
            checks['recommendations'].append('减小仓位规模，增加风险管理')
        
        if market_regime == 'trend':
            checks['emotional_state'] = 'trend_following'
        elif market_regime == 'range':
            checks['emotional_state'] = 'range_trading'
        
        # 纪律指标
        checks['discipline_indicators'].append('有明确的交易计划')
        checks['discipline_indicators'].append('风险管理参数已设定')
        checks['discipline_indicators'].append('入场条件明确')
        
        # 根据规则添加检查
        if len(trading_plans.get('plans', [])) > 3:
            checks['warnings'].append('交易计划过多，可能导致过度交易')
            checks['recommendations'].append('专注于1-2个高质量交易机会')
        
        return checks
    
    def generate_integration_report(self, enhanced_results: Dict[str, Any]) -> Dict[str, Any]:
        """生成整合报告"""
        report = {
            'integration_summary': {
                'rules_applied': list(self.rules.keys()),
                'signals_generated': len(enhanced_results.get('price_action_signals', {}).get('entry_signals', [])),
                'trading_plans_created': len(enhanced_results.get('trading_plans', {}).get('plans', [])),
                'validation_rate': enhanced_results.get('validated_magnetic_levels', {}).get('validation_metrics', {}).get('validation_rate', 0)
            },
            'key_findings': self._extract_key_findings(enhanced_results),
            'actionable_insights': self._extract_actionable_insights(enhanced_results),
            'next_steps': self._recommend_next_steps(enhanced_results)
        }
        
        return report
    
    def _extract_key_findings(self, enhanced_results: Dict[str, Any]) -> List[str]:
        """提取关键发现"""
        findings = []
        
        # 磁力位验证结果
        validation_metrics = enhanced_results.get('validated_magnetic_levels', {}).get('validation_metrics', {})
        validation_rate = validation_metrics.get('validation_rate', 0)
        
        if validation_rate >= 0.7:
            findings.append('磁力位验证通过率较高，关键水平可靠性强')
        elif validation_rate >= 0.5:
            findings.append('磁力位验证通过率中等，需谨慎对待关键水平')
        else:
            findings.append('磁力位验证通过率较低，关键水平需要进一步确认')
        
        # 信号质量
        signal_metrics = enhanced_results.get('price_action_signals', {}).get('signal_quality_metrics', {})
        quality_score = signal_metrics.get('quality_score', 0)
        
        if quality_score >= 0.7:
            findings.append('交易信号质量较高，值得重点关注')
        elif quality_score >= 0.5:
            findings.append('交易信号质量中等，需要选择性执行')
        else:
            findings.append('交易信号质量较低，建议观望')
        
        # 风险概况
        risk_profile = enhanced_results.get('trading_plans', {}).get('plan_summary', {}).get('risk_profile', {})
        overall_risk = risk_profile.get('overall_risk', 'unknown')
        
        findings.append(f'整体风险水平：{overall_risk}')
        
        return findings
    
    def _extract_actionable_insights(self, enhanced_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """提取可操作的见解"""
        insights = []
        
        # 从交易计划中提取
        for plan in enhanced_results.get('trading_plans', {}).get('plans', []):
            signal_details = plan.get('signal_details', {})
            
            insight = {
                'type': 'trading_opportunity',
                'signal_type': signal_details.get('type', ''),
                'level_price': signal_details.get('level_price', 0),
                'confidence': plan.get('plan_confidence', 0),
                'action': plan.get('entry_execution', {}).get('order_type', ''),
                'risk_reward': '查看详细风险参数'
            }
            
            if plan.get('plan_confidence', 0) >= 0.6:
                insights.append(insight)
        
        # 从心理检查中提取
        psych_checks = enhanced_results.get('psychological_checks', {})
        for warning in psych_checks.get('warnings', []):
            insights.append({
                'type': 'psychological_warning',
                'warning': warning,
                'action': '调整交易心态，严格遵守纪律'
            })
        
        for recommendation in psych_checks.get('recommendations', []):
            insights.append({
                'type': 'improvement_recommendation',
                'recommendation': recommendation,
                'action': '考虑实施该建议'
            })
        
        return insights
    
    def _recommend_next_steps(self, enhanced_results: Dict[str, Any]) -> List[str]:
        """推荐下一步行动"""
        next_steps = [
            '根据交易计划执行高质量信号',
            '严格遵循风险管理参数',
            '监控市场状态变化，及时调整策略',
            '记录交易执行结果和教训',
            '定期回顾和优化交易系统'
        ]
        
        # 根据验证率调整建议
        validation_metrics = enhanced_results.get('validated_magnetic_levels', {}).get('validation_metrics', {})
        validation_rate = validation_metrics.get('validation_rate', 0)
        
        if validation_rate < 0.6:
            next_steps.append('考虑增加数据量或调整磁力位识别参数')
        
        # 根据信号质量调整建议
        signal_metrics = enhanced_results.get('price_action_signals', {}).get('signal_quality_metrics', {})
        quality_score = signal_metrics.get('quality_score', 0)
        
        if quality_score < 0.6:
            next_steps.append('等待更高质量的交易信号出现')
        
        return next_steps


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函数"""
    print("价格行为规则整合器")
    print("版本: 1.0 - 整合AL Brooks理论规则")
    print("=" * 60)
    
    # 创建整合器
    integrator = PriceActionRulesIntegrator()
    
    print("\n规则库已初始化:")
    for rule_category, rule_details in integrator.rules.items():
        print(f"  - {rule_category}: {len(rule_details) if isinstance(rule_details, dict) else 1} 条规则")
    
    print("\n✅ 价格行为规则整合器准备就绪")
    print("使用方法:")
    print("  1. 运行优化版整合引擎获取分析结果")
    print("  2. 使用 integrator.integrate_rules(analysis_results, price_data)")
    print("  3. 获取增强的分析结果和交易信号")


if __name__ == "__main__":
    main()