#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一分析管理器 - 整合价格行为分析和技术分析工具

功能:
1. 多维度市场分析 (价格行为、技术指标、市场结构)
2. 信号生成和验证
3. 分析结果整合和优先级排序
4. 与数据管理器和策略管理器集成
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
sys.path.append('/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration')

# 导入数据管理器
try:
    from data.data_manager import UnifiedDataManager
    DATA_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ 无法导入数据管理器")
    DATA_MANAGER_AVAILABLE = False


class AnalysisEngine:
    """分析引擎基类"""
    
    def __init__(self, name: str, description: str = ""):
        self.name = name
        self.description = description
        self.results = {}
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """执行分析"""
        raise NotImplementedError
    
    def get_results(self) -> Dict[str, Any]:
        """获取分析结果"""
        return self.results
    
    def get_supported_indicators(self) -> List[str]:
        """获取支持的指标列表"""
        return []


class PriceActionAnalysisEngine(AnalysisEngine):
    """价格行为分析引擎 - 整合price_action_integration框架"""
    
    def __init__(self):
        super().__init__("PriceAction", "价格行为分析引擎 (基于AL Brooks理论)")
        self._init_components()
    
    def _init_components(self):
        """初始化价格行为分析组件"""
        self.components = {}
        
        # 尝试导入价格行为整合引擎
        try:
            # 添加price_action_integration路径
            pa_path = '/Users/chengming/.openclaw/workspace/price_action_integration'
            sys.path.append(pa_path)
            
            # 尝试导入优化整合引擎
            from optimized_integration_engine import PriceActionIntegrationEngine
            self.components['integration_engine'] = PriceActionIntegrationEngine()
            print("✅ 价格行为整合引擎加载成功")
        except ImportError as e:
            print(f"⚠️ 价格行为整合引擎导入失败: {e}")
            self.components['integration_engine'] = None
        
        # 尝试导入价格行为规则整合器
        try:
            from price_action_rules_integrator import PriceActionRulesIntegrator
            self.components['rules_integrator'] = PriceActionRulesIntegrator()
            print("✅ 价格行为规则整合器加载成功")
        except ImportError as e:
            print(f"⚠️ 价格行为规则整合器导入失败: {e}")
            self.components['rules_integrator'] = None
        
        # 尝试导入枢轴点检测器
        try:
            from detect_pivot_points import PivotPointDetector
            self.components['pivot_detector'] = PivotPointDetector()
            print("✅ 枢轴点检测器加载成功")
        except ImportError:
            print("⚠️ 枢轴点检测器导入失败，使用简化版本")
            self.components['pivot_detector'] = self._create_simple_pivot_detector()
    
    def _create_simple_pivot_detector(self):
        """创建简化版枢轴点检测器"""
        class SimplePivotDetector:
            def detect_pivots(self, df, window=5):
                highs = df['high']
                lows = df['low']
                
                # 简单峰值检测
                high_pivots = (highs == highs.rolling(window=window*2+1, center=True).max())
                low_pivots = (lows == lows.rolling(window=window*2+1, center=True).min())
                
                return {
                    'high_pivots': high_pivots,
                    'low_pivots': low_pivots,
                    'high_indices': np.where(high_pivots)[0],
                    'low_indices': np.where(low_pivots)[0]
                }
        return SimplePivotDetector()
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """执行价格行为分析"""
        print(f"🔍 执行价格行为分析: {len(data)} 行数据")
        
        results = {
            'engine': self.name,
            'timestamp': pd.Timestamp.now(),
            'data_points': len(data),
            'analyses': {}
        }
        
        # 1. 枢轴点分析
        if self.components['pivot_detector']:
            try:
                pivot_results = self.components['pivot_detector'].detect_pivots(data)
                results['analyses']['pivot_points'] = pivot_results
                print(f"✅ 枢轴点分析完成: {len(pivot_results.get('high_indices', []))} 个高点, {len(pivot_results.get('low_indices', []))} 个低点")
            except Exception as e:
                print(f"⚠️ 枢轴点分析失败: {e}")
                results['analyses']['pivot_points'] = {'error': str(e)}
        
        # 2. 价格行为规则分析
        if self.components['rules_integrator']:
            try:
                rule_results = self.components['rules_integrator'].analyze_price_action(data)
                results['analyses']['price_action_rules'] = rule_results
                print(f"✅ 价格行为规则分析完成: {len(rule_results.get('signals', []))} 个信号")
            except Exception as e:
                print(f"⚠️ 价格行为规则分析失败: {e}")
                # 尝试使用简化分析
                rule_results = self._simple_price_action_analysis(data)
                results['analyses']['price_action_rules'] = rule_results
        
        # 3. 整合引擎分析 (如果可用)
        if self.components['integration_engine']:
            try:
                integration_results = self.components['integration_engine'].analyze(data)
                results['analyses']['integration'] = integration_results
                print(f"✅ 整合引擎分析完成")
            except Exception as e:
                print(f"⚠️ 整合引擎分析失败: {e}")
        
        # 4. 生成综合信号
        signals = self._generate_signals(results)
        results['signals'] = signals
        results['signal_count'] = len(signals)
        
        print(f"📊 价格行为分析完成: {len(signals)} 个信号生成")
        self.results = results
        return results
    
    def _simple_price_action_analysis(self, data: pd.DataFrame) -> Dict[str, Any]:
        """简化版价格行为分析"""
        signals = []
        
        # 检查基本价格行为模式
        if len(data) >= 10:
            # 支撑阻力识别
            support_levels = self._identify_support_levels(data)
            resistance_levels = self._identify_resistance_levels(data)
            
            # 趋势分析
            trend = self._analyze_trend(data)
            
            # 生成基本信号
            current_price = data['close'].iloc[-1]
            
            # 接近支撑位买入信号
            for level in support_levels:
                if current_price <= level * 1.01 and current_price >= level * 0.99:
                    signals.append({
                        'type': 'buy',
                        'reason': 'approaching_support',
                        'level': level,
                        'current_price': current_price,
                        'confidence': 0.6
                    })
            
            # 接近阻力位卖出信号
            for level in resistance_levels:
                if current_price >= level * 0.99 and current_price <= level * 1.01:
                    signals.append({
                        'type': 'sell',
                        'reason': 'approaching_resistance',
                        'level': level,
                        'current_price': current_price,
                        'confidence': 0.6
                    })
        
        return {
            'signals': signals,
            'support_levels': support_levels if 'support_levels' in locals() else [],
            'resistance_levels': resistance_levels if 'resistance_levels' in locals() else [],
            'trend': trend if 'trend' in locals() else 'neutral'
        }
    
    def _identify_support_levels(self, data: pd.DataFrame, lookback: int = 20) -> List[float]:
        """识别支撑位"""
        if len(data) < lookback:
            return []
        
        lows = data['low'].tail(lookback)
        # 简单方法: 将近期低点作为支撑位
        support_levels = lows.nsmallest(3).tolist()
        return sorted(set(support_levels))
    
    def _identify_resistance_levels(self, data: pd.DataFrame, lookback: int = 20) -> List[float]:
        """识别阻力位"""
        if len(data) < lookback:
            return []
        
        highs = data['high'].tail(lookback)
        # 简单方法: 将近期高点作为阻力位
        resistance_levels = highs.nlargest(3).tolist()
        return sorted(set(resistance_levels), reverse=True)
    
    def _analyze_trend(self, data: pd.DataFrame) -> str:
        """分析趋势"""
        if len(data) < 10:
            return 'neutral'
        
        prices = data['close']
        
        # 计算短期和长期移动平均
        ma_short = prices.tail(5).mean()
        ma_long = prices.tail(20).mean()
        
        if ma_short > ma_long * 1.01:
            return 'uptrend'
        elif ma_short < ma_long * 0.99:
            return 'downtrend'
        else:
            return 'neutral'
    
    def _generate_signals(self, analysis_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """从分析结果生成信号"""
        signals = []
        
        # 从各个分析组件收集信号
        for analysis_name, results in analysis_results.get('analyses', {}).items():
            if 'signals' in results:
                for signal in results['signals']:
                    signal['source'] = analysis_name
                    signals.append(signal)
        
        # 去重和优先级排序
        unique_signals = self._deduplicate_signals(signals)
        
        return unique_signals
    
    def _deduplicate_signals(self, signals: List[Dict]) -> List[Dict]:
        """信号去重和排序"""
        if not signals:
            return []
        
        # 简单去重: 基于类型和时间
        unique_signals = []
        seen = set()
        
        for signal in signals:
            key = f"{signal.get('type', '')}_{signal.get('reason', '')}_{signal.get('timestamp', '')}"
            if key not in seen:
                seen.add(key)
                unique_signals.append(signal)
        
        # 按置信度排序
        unique_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        return unique_signals


class TechnicalAnalysisEngine(AnalysisEngine):
    """技术分析引擎 - 整合quant_trade-main的技术分析工具"""
    
    def __init__(self):
        super().__init__("Technical", "技术分析引擎 (基于quant_trade-main工具)")
        self._init_components()
    
    def _init_components(self):
        """初始化技术分析组件"""
        self.components = {}
        
        # 尝试导入quant_trade-main的处理模块
        try:
            # 添加quant_trade-main路径
            qt_path = '/Users/chengming/downloads/quant_trade-main/csv_version'
            sys.path.append(qt_path)
            
            # 尝试导入process_single中的函数
            from process_single import calculate_williams_r, calculate_atr, calculate_macd
            self.components['technical_indicators'] = {
                'williams_r': calculate_williams_r,
                'atr': calculate_atr,
                'macd': calculate_macd
            }
            print("✅ 技术指标函数加载成功")
        except ImportError as e:
            print(f"⚠️ 技术指标函数导入失败: {e}")
            self.components['technical_indicators'] = self._create_default_indicators()
    
    def _create_default_indicators(self):
        """创建默认技术指标计算器"""
        def calculate_williams_r(data, period=14):
            """计算威廉指标"""
            high = data['high'].rolling(window=period).max()
            low = data['low'].rolling(window=period).min()
            close = data['close']
            williams_r = -100 * (high - close) / (high - low).replace(0, 1)
            return williams_r
        
        def calculate_atr(data, period=14):
            """计算平均真实范围"""
            high = data['high']
            low = data['low']
            close = data['close']
            
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            return atr
        
        def calculate_macd(data, fast=12, slow=26, signal=9):
            """计算MACD"""
            ema_fast = data['close'].ewm(span=fast, adjust=False).mean()
            ema_slow = data['close'].ewm(span=slow, adjust=False).mean()
            macd_line = ema_fast - ema_slow
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            histogram = macd_line - signal_line
            
            return {
                'macd': macd_line,
                'signal': signal_line,
                'histogram': histogram
            }
        
        return {
            'williams_r': calculate_williams_r,
            'atr': calculate_atr,
            'macd': calculate_macd
        }
    
    def get_supported_indicators(self) -> List[str]:
        """获取支持的技术指标列表"""
        return list(self.components['technical_indicators'].keys())
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """执行技术分析"""
        print(f"🔍 执行技术分析: {len(data)} 行数据")
        
        results = {
            'engine': self.name,
            'timestamp': pd.Timestamp.now(),
            'data_points': len(data),
            'indicators': {},
            'signals': []
        }
        
        # 计算技术指标
        indicators = self.components['technical_indicators']
        
        for indicator_name, indicator_func in indicators.items():
            try:
                if indicator_name == 'macd':
                    macd_result = indicator_func(data)
                    results['indicators']['macd_line'] = macd_result['macd'].iloc[-1] if not macd_result['macd'].empty else 0
                    results['indicators']['macd_signal'] = macd_result['signal'].iloc[-1] if not macd_result['signal'].empty else 0
                    results['indicators']['macd_histogram'] = macd_result['histogram'].iloc[-1] if not macd_result['histogram'].empty else 0
                else:
                    indicator_values = indicator_func(data)
                    if not indicator_values.empty:
                        results['indicators'][indicator_name] = indicator_values.iloc[-1]
                    else:
                        results['indicators'][indicator_name] = 0
                
                print(f"✅ {indicator_name} 计算完成")
            except Exception as e:
                print(f"⚠️ {indicator_name} 计算失败: {e}")
                results['indicators'][indicator_name] = None
        
        # 生成技术信号
        signals = self._generate_technical_signals(data, results['indicators'])
        results['signals'] = signals
        results['signal_count'] = len(signals)
        
        print(f"📊 技术分析完成: {len(signals)} 个信号生成")
        self.results = results
        return results
    
    def _generate_technical_signals(self, data: pd.DataFrame, indicators: Dict[str, Any]) -> List[Dict[str, Any]]:
        """生成技术信号"""
        signals = []
        
        if not indicators:
            return signals
        
        current_price = data['close'].iloc[-1] if not data.empty else 0
        
        # MACD信号
        if 'macd_line' in indicators and 'macd_signal' in indicators:
            macd_line = indicators['macd_line']
            macd_signal = indicators['macd_signal']
            
            if macd_line is not None and macd_signal is not None:
                # 金叉买入信号
                if macd_line > macd_signal and macd_line > 0:
                    signals.append({
                        'type': 'buy',
                        'reason': 'macd_golden_cross',
                        'indicator': 'MACD',
                        'value': macd_line,
                        'signal_value': macd_signal,
                        'confidence': 0.7,
                        'price': current_price
                    })
                # 死叉卖出信号
                elif macd_line < macd_signal and macd_line < 0:
                    signals.append({
                        'type': 'sell',
                        'reason': 'macd_death_cross',
                        'indicator': 'MACD',
                        'value': macd_line,
                        'signal_value': macd_signal,
                        'confidence': 0.7,
                        'price': current_price
                    })
        
        # 威廉指标信号
        if 'williams_r' in indicators and indicators['williams_r'] is not None:
            williams_r = indicators['williams_r']
            
            # 超卖买入信号
            if williams_r < -80:
                signals.append({
                    'type': 'buy',
                    'reason': 'williams_r_oversold',
                    'indicator': 'Williams %R',
                    'value': williams_r,
                    'confidence': 0.6,
                    'price': current_price
                })
            # 超买卖出信号
            elif williams_r > -20:
                signals.append({
                    'type': 'sell',
                    'reason': 'williams_r_overbought',
                    'indicator': 'Williams %R',
                    'value': williams_r,
                    'confidence': 0.6,
                    'price': current_price
                })
        
        return signals


class SignalAnalysisEngine(AnalysisEngine):
    """信号分析引擎 - 基于quant_trade-main的price_action_analysis.py"""
    
    def __init__(self):
        super().__init__("SignalAnalysis", "信号分析引擎 (基于price_action_analysis.py)")
        self._init_components()
    
    def _init_components(self):
        """初始化信号分析组件"""
        self.components = {}
        
        try:
            # 添加quant_trade-main路径
            qt_path = '/Users/chengming/downloads/quant_trade-main/csv_version'
            sys.path.append(qt_path)
            
            # 尝试导入price_action_analysis
            from price_action_analysis import SignalDefinition, MACDDivergenceSignal, SignalAnalysisEngine as OriginalSignalEngine
            
            self.components['signal_definitions'] = {
                'MACDDivergence': MACDDivergenceSignal
            }
            
            # 尝试创建信号分析引擎
            self.components['signal_engine'] = OriginalSignalEngine()
            print("✅ 信号分析引擎加载成功")
        except ImportError as e:
            print(f"⚠️ 信号分析引擎导入失败: {e}")
            self.components['signal_definitions'] = {}
            self.components['signal_engine'] = None
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """执行信号分析"""
        print(f"🔍 执行信号分析: {len(data)} 行数据")
        
        results = {
            'engine': self.name,
            'timestamp': pd.Timestamp.now(),
            'data_points': len(data),
            'signals': []
        }
        
        # 使用信号分析引擎
        if self.components['signal_engine']:
            try:
                signal_results = self.components['signal_engine'].analyze(data)
                results['signals'] = signal_results.get('signals', [])
                results['signal_count'] = len(results['signals'])
                print(f"✅ 信号分析完成: {len(results['signals'])} 个信号")
            except Exception as e:
                print(f"⚠️ 信号分析失败: {e}")
                results['signals'] = self._generate_basic_signals(data)
        else:
            results['signals'] = self._generate_basic_signals(data)
        
        self.results = results
        return results
    
    def _generate_basic_signals(self, data: pd.DataFrame) -> List[Dict[str, Any]]:
        """生成基本信号"""
        signals = []
        
        if len(data) < 20:
            return signals
        
        # 简单的突破信号
        current_close = data['close'].iloc[-1]
        recent_high = data['high'].tail(10).max()
        recent_low = data['low'].tail(10).min()
        
        # 突破近期高点
        if current_close > recent_high:
            signals.append({
                'type': 'buy',
                'reason': 'breakout_high',
                'price': current_close,
                'breakout_level': recent_high,
                'confidence': 0.65
            })
        
        # 突破近期低点
        if current_close < recent_low:
            signals.append({
                'type': 'sell',
                'reason': 'breakout_low',
                'price': current_close,
                'breakout_level': recent_low,
                'confidence': 0.65
            })
        
        return signals


class UnifiedAnalysisManager:
    """
    统一分析管理器 - 主入口点
    
    整合:
    1. 价格行为分析引擎
    2. 技术分析引擎
    3. 信号分析引擎
    4. 多引擎结果整合
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化统一分析管理器
        
        参数:
            config: 配置字典
        """
        # 默认配置
        self.config = config or {
            'enable_price_action': True,
            'enable_technical': True,
            'enable_signal': True,
            'result_integration': 'weighted',  # weighted, voting, priority
            'weights': {
                'price_action': 0.4,
                'technical': 0.3,
                'signal': 0.3
            },
            'confidence_threshold': 0.5,
            'max_signals': 20
        }
        
        # 初始化分析引擎
        self.engines = {}
        self._init_engines()
        
        print(f"✅ 统一分析管理器初始化完成")
        print(f"   启用的引擎: {list(self.engines.keys())}")
    
    def _init_engines(self):
        """初始化分析引擎"""
        if self.config['enable_price_action']:
            try:
                self.engines['price_action'] = PriceActionAnalysisEngine()
            except Exception as e:
                print(f"⚠️ 价格行为引擎初始化失败: {e}")
        
        if self.config['enable_technical']:
            try:
                self.engines['technical'] = TechnicalAnalysisEngine()
            except Exception as e:
                print(f"⚠️ 技术分析引擎初始化失败: {e}")
        
        if self.config['enable_signal']:
            try:
                self.engines['signal'] = SignalAnalysisEngine()
            except Exception as e:
                print(f"⚠️ 信号分析引擎初始化失败: {e}")
        
        if not self.engines:
            print("⚠️ 没有可用的分析引擎")
    
    def analyze(self, data: pd.DataFrame, **kwargs) -> Dict[str, Any]:
        """
        执行多维度分析
        
        参数:
            data: 交易数据
            **kwargs: 其他参数
        
        返回:
            整合的分析结果
        """
        if data.empty:
            print("⚠️ 数据为空，无法分析")
            return {'error': 'empty_data'}
        
        print(f"🔍 开始多维度分析: {len(data)} 行数据, {len(self.engines)} 个引擎")
        
        # 执行各个引擎的分析
        engine_results = {}
        
        for engine_name, engine in self.engines.items():
            print(f"\n运行 {engine_name} 引擎...")
            try:
                results = engine.analyze(data, **kwargs)
                engine_results[engine_name] = results
                print(f"✅ {engine_name}: {results.get('signal_count', 0)} 个信号")
            except Exception as e:
                print(f"❌ {engine_name} 分析失败: {e}")
                engine_results[engine_name] = {'error': str(e)}
        
        # 整合结果
        integrated_results = self._integrate_results(engine_results)
        
        # 生成最终报告
        final_results = self._generate_final_report(integrated_results, engine_results)
        
        print(f"\n🎯 分析完成:")
        print(f"   总信号: {final_results.get('total_signals', 0)}")
        print(f"   引擎数量: {len(engine_results)}")
        print(f"   分析时间: {final_results.get('analysis_duration', 0):.2f} 秒")
        
        return final_results
    
    def _integrate_results(self, engine_results: Dict[str, Dict]) -> Dict[str, Any]:
        """整合各个引擎的结果"""
        integrated = {
            'all_signals': [],
            'engine_stats': {},
            'consensus_signals': []
        }
        
        # 收集所有信号
        all_signals = []
        
        for engine_name, results in engine_results.items():
            if 'error' in results:
                continue
            
            # 统计引擎结果
            signal_count = results.get('signal_count', 0)
            integrated['engine_stats'][engine_name] = {
                'signal_count': signal_count,
                'timestamp': results.get('timestamp', pd.Timestamp.now())
            }
            
            # 收集信号
            engine_signals = results.get('signals', [])
            for signal in engine_signals:
                signal['source_engine'] = engine_name
                all_signals.append(signal)
        
        integrated['all_signals'] = all_signals
        
        # 生成共识信号
        consensus_signals = self._generate_consensus_signals(all_signals)
        integrated['consensus_signals'] = consensus_signals
        
        return integrated
    
    def _generate_consensus_signals(self, all_signals: List[Dict]) -> List[Dict]:
        """生成共识信号 (多个引擎确认的信号)"""
        if not all_signals:
            return []
        
        # 按时间分组信号
        signal_groups = {}
        
        for signal in all_signals:
            # 创建信号键 (类型+原因+时间)
            signal_time = signal.get('timestamp', pd.Timestamp.now())
            time_key = signal_time.strftime('%Y-%m-%d %H:%M')
            signal_key = f"{signal.get('type', '')}_{signal.get('reason', '')}_{time_key}"
            
            if signal_key not in signal_groups:
                signal_groups[signal_key] = {
                    'signals': [],
                    'sources': set(),
                    'type': signal.get('type'),
                    'reason': signal.get('reason'),
                    'timestamp': signal_time
                }
            
            signal_groups[signal_key]['signals'].append(signal)
            signal_groups[signal_key]['sources'].add(signal.get('source_engine', 'unknown'))
        
        # 生成共识信号
        consensus_signals = []
        
        for signal_key, group in signal_groups.items():
            source_count = len(group['sources'])
            
            if source_count >= 2:  # 至少两个引擎确认
                # 计算平均置信度
                confidences = [s.get('confidence', 0) for s in group['signals']]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                # 使用第一个信号的详情
                base_signal = group['signals'][0]
                
                consensus_signal = {
                    'type': group['type'],
                    'reason': group['reason'],
                    'timestamp': group['timestamp'],
                    'confidence': avg_confidence,
                    'source_count': source_count,
                    'sources': list(group['sources']),
                    'price': base_signal.get('price'),
                    'details': base_signal.get('details', {})
                }
                
                # 应用权重
                if self.config['result_integration'] == 'weighted':
                    # 计算加权置信度
                    weighted_confidence = 0
                    for signal in group['signals']:
                        source = signal.get('source_engine', '')
                        weight = self.config['weights'].get(source, 0.3)
                        weighted_confidence += signal.get('confidence', 0) * weight
                    
                    consensus_signal['weighted_confidence'] = weighted_confidence
                    consensus_signal['confidence'] = weighted_confidence  # 使用加权置信度
                
                consensus_signals.append(consensus_signal)
        
        # 按置信度排序
        consensus_signals.sort(key=lambda x: x.get('confidence', 0), reverse=True)
        
        # 限制数量
        max_signals = self.config.get('max_signals', 20)
        consensus_signals = consensus_signals[:max_signals]
        
        return consensus_signals
    
    def _generate_final_report(self, integrated_results: Dict[str, Any], 
                             engine_results: Dict[str, Dict]) -> Dict[str, Any]:
        """生成最终分析报告"""
        final_report = {
            'analysis_timestamp': pd.Timestamp.now(),
            'engine_count': len(engine_results),
            'total_signals': len(integrated_results.get('all_signals', [])),
            'consensus_signals': len(integrated_results.get('consensus_signals', [])),
            'engine_stats': integrated_results.get('engine_stats', {}),
            'consensus_signals_list': integrated_results.get('consensus_signals', []),
            'all_signals_count': len(integrated_results.get('all_signals', []))
        }
        
        # 添加分析摘要
        summary = self._generate_analysis_summary(final_report)
        final_report['summary'] = summary
        
        return final_report
    
    def _generate_analysis_summary(self, final_report: Dict[str, Any]) -> str:
        """生成分析摘要"""
        total_signals = final_report['total_signals']
        consensus_signals = final_report['consensus_signals']
        engine_count = final_report['engine_count']
        
        if total_signals == 0:
            return "❌ 未生成任何交易信号"
        
        consensus_text = f"✅ 生成 {total_signals} 个信号，其中 {consensus_signals} 个获得多个引擎确认"
        
        # 信号类型统计
        signals = final_report.get('consensus_signals_list', [])
        buy_signals = [s for s in signals if s.get('type') == 'buy']
        sell_signals = [s for s in signals if s.get('type') == 'sell']
        
        type_summary = f"买入信号: {len(buy_signals)}，卖出信号: {len(sell_signals)}"
        
        return f"{consensus_text}\n{type_summary}"
    
    def get_available_engines(self) -> List[str]:
        """获取可用的分析引擎"""
        return list(self.engines.keys())
    
    def get_engine(self, engine_name: str) -> Optional[AnalysisEngine]:
        """获取指定的分析引擎"""
        return self.engines.get(engine_name)


# ========== 使用示例 ==========

def example_usage():
    """使用示例"""
    print("="*60)
    print("统一分析管理器使用示例")
    print("="*60)
    
    # 生成示例数据
    print("生成示例数据...")
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 105,
        'low': np.random.randn(100).cumsum() + 95,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100),
        'symbol': 'AAPL'
    }, index=dates)
    
    print(f"示例数据: {len(data)} 行")
    
    # 创建分析管理器
    print("\n创建分析管理器...")
    config = {
        'enable_price_action': True,
        'enable_technical': True,
        'enable_signal': True,
        'result_integration': 'weighted',
        'weights': {
            'price_action': 0.4,
            'technical': 0.3,
            'signal': 0.3
        },
        'confidence_threshold': 0.5
    }
    
    manager = UnifiedAnalysisManager(config)
    
    # 执行分析
    print("\n执行多维度分析...")
    results = manager.analyze(data)
    
    # 显示结果
    print(f"\n📊 分析结果摘要:")
    print(f"   引擎数量: {results.get('engine_count', 0)}")
    print(f"   总信号数: {results.get('total_signals', 0)}")
    print(f"   共识信号: {results.get('consensus_signals', 0)}")
    
    if 'summary' in results:
        print(f"\n📋 分析摘要:")
        print(f"   {results['summary']}")
    
    # 显示共识信号
    consensus_signals = results.get('consensus_signals_list', [])
    if consensus_signals:
        print(f"\n🎯 共识信号 (前5个):")
        for i, signal in enumerate(consensus_signals[:5]):
            print(f"  {i+1}. {signal.get('type', 'unknown')} - {signal.get('reason', 'unknown')}")
            print(f"     置信度: {signal.get('confidence', 0):.2f}, 来源: {signal.get('sources', [])}")
            if 'price' in signal:
                print(f"     价格: {signal.get('price', 0):.2f}")
    else:
        print(f"\n⚠️ 无共识信号")
    
    # 显示引擎统计
    engine_stats = results.get('engine_stats', {})
    if engine_stats:
        print(f"\n⚙️ 引擎统计:")
        for engine_name, stats in engine_stats.items():
            print(f"  {engine_name}: {stats.get('signal_count', 0)} 个信号")
    
    print(f"\n✅ 统一分析管理器示例完成")


if __name__ == "__main__":
    example_usage()