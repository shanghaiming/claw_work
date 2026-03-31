#!/usr/bin/env python3
"""
TradingView策略整合系统

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

功能:
1. 将TradingView指标集成到现有策略框架
2. 创建基于TradingView指标的策略
3. 测试整合策略的性能
4. 生成整合报告
5. 优化整合参数
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
import json
import warnings
from datetime import datetime, timedelta
import talib
warnings.filterwarnings('ignore')

print("=" * 80)
print("🔄 TradingView策略整合系统")
print("=" * 80)

# 添加TradingView指标目录
sys.path.append('/Users/chengming/.openclaw/workspace/tradingview_indicators')

class TradingViewStrategyIntegrator:
    """TradingView策略整合器"""
    
    def __init__(self, data: pd.DataFrame):
        """
        初始化整合器
        
        Args:
            data: 包含OHLCV数据的DataFrame
        """
        self.data = data
        self.tradingview_indicators = self._load_tradingview_indicators()
        self.integrated_strategies = {}
        self.performance_results = {}
        
        # 确保数据格式正确
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"数据缺少必要列: {col}")
    
    def _load_tradingview_indicators(self) -> Dict[str, Callable]:
        """加载TradingView指标"""
        indicators = {}
        
        # 尝试导入已转换的指标
        try:
            from tradingview_indicators import supertrend
            indicators['Supertrend'] = supertrend
            print("✅ 已加载: Supertrend")
        except ImportError:
            print("⚠️  Supertrend未找到，使用内置实现")
            indicators['Supertrend'] = self._builtin_supertrend
        
        try:
            from tradingview_indicators import rsi_divergence
            indicators['RSI Divergence'] = rsi_divergence
            print("✅ 已加载: RSI Divergence")
        except ImportError:
            print("⚠️  RSI Divergence未找到，使用内置实现")
            indicators['RSI Divergence'] = self._builtin_rsi_divergence
        
        # 添加更多内置实现
        indicators['Volume Profile'] = self._builtin_volume_profile
        indicators['ATR Trailing Stop'] = self._builtin_atr_trailing_stop
        indicators['Ichimoku Cloud'] = self._builtin_ichimoku
        
        return indicators
    
    def _builtin_supertrend(self, high, low, close, atr_period=10, multiplier=3):
        """内置Supertrend实现"""
        import talib
        
        atr = talib.ATR(high, low, close, timeperiod=atr_period)
        hl2 = (high + low) / 2
        
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        supertrend = np.zeros_like(close)
        direction = np.zeros_like(close)
        
        for i in range(1, len(close)):
            if close[i] > upper_band[i-1]:
                direction[i] = 1
                supertrend[i] = lower_band[i]
            elif close[i] < lower_band[i-1]:
                direction[i] = -1
                supertrend[i] = upper_band[i]
            else:
                direction[i] = direction[i-1]
                if direction[i] == 1:
                    supertrend[i] = max(lower_band[i], supertrend[i-1])
                else:
                    supertrend[i] = min(upper_band[i], supertrend[i-1])
        
        return supertrend, direction
    
    def _builtin_rsi_divergence(self, high, low, close, rsi_period=14, lookback=20):
        """内置RSI背离检测"""
        import talib
        
        rsi = talib.RSI(close, timeperiod=rsi_period)
        
        bullish_divergence = np.zeros_like(close, dtype=bool)
        bearish_divergence = np.zeros_like(close, dtype=bool)
        
        for i in range(lookback, len(close)):
            price_window = close[i-lookback:i+1]
            rsi_window = rsi[i-lookback:i+1]
            
            # 看跌背离检测
            price_high_idx = np.argmax(price_window)
            rsi_low_idx = np.argmin(rsi_window)
            
            if price_high_idx == len(price_window)-1 and rsi_low_idx == len(rsi_window)-1:
                if rsi_window[-1] < rsi_window[-2] and price_window[-1] > price_window[-2]:
                    bearish_divergence[i] = True
            
            # 看涨背离检测
            price_low_idx = np.argmin(price_window)
            rsi_high_idx = np.argmax(rsi_window)
            
            if price_low_idx == len(price_window)-1 and rsi_high_idx == len(rsi_window)-1:
                if rsi_window[-1] > rsi_window[-2] and price_window[-1] < price_window[-2]:
                    bullish_divergence[i] = True
        
        return bullish_divergence, bearish_divergence, rsi
    
    def _builtin_volume_profile(self, high, low, close, volume, price_bins=20):
        """内置成交量分布"""
        price_min = np.min(low)
        price_max = np.max(high)
        
        price_edges = np.linspace(price_min, price_max, price_bins + 1)
        price_centers = (price_edges[:-1] + price_edges[1:]) / 2
        
        volume_dist = np.zeros(price_bins)
        
        for i in range(len(close)):
            price = close[i]
            vol = volume[i]
            
            bin_idx = np.digitize(price, price_edges) - 1
            bin_idx = max(0, min(bin_idx, price_bins - 1))
            
            volume_dist[bin_idx] += vol
        
        poc_idx = np.argmax(volume_dist)
        poc_price = price_centers[poc_idx]
        
        total_volume = np.sum(volume_dist)
        target_volume = total_volume * 0.7
        
        sorted_indices = np.argsort(volume_dist)[::-1]
        cumulative_volume = 0
        value_area_indices = []
        
        for idx in sorted_indices:
            cumulative_volume += volume_dist[idx]
            value_area_indices.append(idx)
            
            if cumulative_volume >= target_volume:
                break
        
        value_area_prices = price_centers[value_area_indices]
        value_area = (np.min(value_area_prices), np.max(value_area_prices))
        
        return price_centers, volume_dist, poc_price, value_area
    
    def _builtin_atr_trailing_stop(self, high, low, close, atr_period=14, multiplier=2):
        """内置ATR移动止损"""
        import talib
        
        atr = talib.ATR(high, low, close, timeperiod=atr_period)
        
        trailing_stop_long = np.zeros_like(close)
        trailing_stop_short = np.zeros_like(close)
        
        for i in range(1, len(close)):
            if i == 1:
                trailing_stop_long[i] = close[i] - (atr[i] * multiplier)
                trailing_stop_short[i] = close[i] + (atr[i] * multiplier)
            else:
                # 多头止损：最高价 - ATR×乘数，且只上移不下移
                current_stop_long = high[i] - (atr[i] * multiplier)
                trailing_stop_long[i] = max(current_stop_long, trailing_stop_long[i-1])
                
                # 空头止损：最低价 + ATR×乘数，且只下移不上移
                current_stop_short = low[i] + (atr[i] * multiplier)
                trailing_stop_short[i] = min(current_stop_short, trailing_stop_short[i-1])
        
        return trailing_stop_long, trailing_stop_short
    
    def _builtin_ichimoku(self, high, low, close, tenkan_period=9, kijun_period=26, senkou_span_b_period=52):
        """内置Ichimoku云"""
        # 转换线
        tenkan_sen = (high.rolling(window=tenkan_period).max() + 
                      low.rolling(window=tenkan_period).min()) / 2
        
        # 基准线
        kijun_sen = (high.rolling(window=kijun_period).max() + 
                     low.rolling(window=kijun_period).min()) / 2
        
        # 先行跨度A
        senkou_span_a = (tenkan_sen + kijun_sen) / 2
        senkou_span_a = senkou_span_a.shift(kijun_period)
        
        # 先行跨度B
        senkou_span_b = (high.rolling(window=senkou_span_b_period).max() + 
                         low.rolling(window=senkou_span_b_period).min()) / 2
        senkou_span_b = senkou_span_b.shift(kijun_period)
        
        # 迟行线
        chikou_span = close.shift(-kijun_period)
        
        return {
            'tenkan_sen': tenkan_sen.values,
            'kijun_sen': kijun_sen.values,
            'senkou_span_a': senkou_span_a.values,
            'senkou_span_b': senkou_span_b.values,
            'chikou_span': chikou_span.values
        }
    
    def create_tradingview_strategy(self, strategy_name: str, 
                                   indicator_configs: List[Dict[str, Any]]) -> Dict[str, Any]:
        """创建基于TradingView指标的策略"""
        
        strategy = {
            'name': strategy_name,
            'created_at': datetime.now().isoformat(),
            'indicators': indicator_configs,
            'signals': None,
            'performance': None,
            'code': self._generate_strategy_code(strategy_name, indicator_configs)
        }
        
        # 计算指标和信号
        signals = self._calculate_strategy_signals(indicator_configs)
        strategy['signals'] = signals
        
        self.integrated_strategies[strategy_name] = strategy
        
        return strategy
    
    def _generate_strategy_code(self, strategy_name: str, 
                               indicator_configs: List[Dict[str, Any]]) -> str:
        """生成策略代码"""
        
        code = f'''class {strategy_name.replace(' ', '_')}Strategy:
    """{strategy_name} - 基于TradingView指标的策略"""
    
    def __init__(self):
        self.name = "{strategy_name}"
        self.indicators = {indicator_configs}
        
    def calculate_signals(self, data):
        """计算交易信号"""
        import numpy as np
        
        signals = np.zeros(len(data))
        
        # 计算各个指标
'''
        
        for i, config in enumerate(indicator_configs):
            indicator_name = config['name']
            params = config.get('parameters', {})
            
            code += f'''        # {indicator_name}
        {indicator_name.lower().replace(' ', '_')}_result = self.calculate_{indicator_name.lower().replace(' ', '_')}(data, {params})
        
'''
        
        code += '''        # 综合信号逻辑
        # 这里需要根据具体策略逻辑组合各个指标
        
        return signals'''
        
        return code
    
    def _calculate_strategy_signals(self, indicator_configs: List[Dict[str, Any]]) -> np.ndarray:
        """计算策略信号"""
        high = self.data['high'].values
        low = self.data['low'].values
        close = self.data['close'].values
        volume = self.data['volume'].values
        
        all_signals = []
        weights = []
        
        for config in indicator_configs:
            indicator_name = config['name']
            params = config.get('parameters', {})
            weight = config.get('weight', 1.0)
            
            if indicator_name in self.tradingview_indicators:
                try:
                    # 调用指标函数
                    indicator_func = self.tradingview_indicators[indicator_name]
                    
                    if indicator_name == 'Supertrend':
                        result, direction = indicator_func(high, low, close, **params)
                        # Supertrend方向作为信号（1: 买入, -1: 卖出）
                        signals = direction
                    
                    elif indicator_name == 'RSI Divergence':
                        bullish, bearish, rsi = indicator_func(high, low, close, **params)
                        # 看涨背离为1，看跌背离为-1
                        signals = np.zeros_like(close)
                        signals[bullish] = 1
                        signals[bearish] = -1
                    
                    elif indicator_name == 'Volume Profile':
                        price_levels, volume_dist, poc, value_area = indicator_func(
                            high, low, close, volume, **params
                        )
                        # 简化信号：价格在价值区间内为0，在上方为-1，在下方为1
                        signals = np.zeros_like(close)
                        for i in range(len(close)):
                            if close[i] > value_area[1]:
                                signals[i] = -1  # 超买
                            elif close[i] < value_area[0]:
                                signals[i] = 1   # 超卖
                    
                    elif indicator_name == 'ATR Trailing Stop':
                        stop_long, stop_short = indicator_func(high, low, close, **params)
                        # 价格高于多头止损为1，低于空头止损为-1
                        signals = np.zeros_like(close)
                        signals[close > stop_long] = 1
                        signals[close < stop_short] = -1
                    
                    elif indicator_name == 'Ichimoku Cloud':
                        ichimoku = indicator_func(high, low, close, **params)
                        tenkan = ichimoku['tenkan_sen']
                        kijun = ichimoku['kijun_sen']
                        # 转换线上穿基准线为1，下穿为-1
                        signals = np.zeros_like(close)
                        for i in range(1, len(close)):
                            if tenkan[i] > kijun[i] and tenkan[i-1] <= kijun[i-1]:
                                signals[i] = 1
                            elif tenkan[i] < kijun[i] and tenkan[i-1] >= kijun[i-1]:
                                signals[i] = -1
                    
                    else:
                        # 通用处理
                        result = indicator_func(high, low, close, **params)
                        if isinstance(result, tuple):
                            signals = result[0]
                        else:
                            signals = result
                    
                    all_signals.append(signals)
                    weights.append(weight)
                    
                except Exception as e:
                    print(f"计算指标 {indicator_name} 时出错: {e}")
        
        if not all_signals:
            return np.zeros(len(close))
        
        # 加权组合信号
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        combined_signals = np.zeros_like(all_signals[0])
        for signal, weight in zip(all_signals, weights):
            combined_signals += signal * weight
        
        # 标准化信号
        combined_signals = np.clip(combined_signals, -1, 1)
        
        return combined_signals
    
    def create_preset_strategies(self) -> Dict[str, Any]:
        """创建预设策略"""
        strategies = {}
        
        # 1. Supertrend趋势跟踪策略
        supertrend_strategy = self.create_tradingview_strategy(
            "Supertrend趋势跟踪",
            [
                {
                    'name': 'Supertrend',
                    'parameters': {'atr_period': 10, 'multiplier': 3},
                    'weight': 1.0,
                    'description': '主要趋势判断'
                },
                {
                    'name': 'ATR Trailing Stop',
                    'parameters': {'atr_period': 14, 'multiplier': 2},
                    'weight': 0.5,
                    'description': '风险管理'
                }
            ]
        )
        strategies['supertrend_trend'] = supertrend_strategy
        
        # 2. RSI背离反转策略
        rsi_divergence_strategy = self.create_tradingview_strategy(
            "RSI背离反转",
            [
                {
                    'name': 'RSI Divergence',
                    'parameters': {'rsi_period': 14, 'lookback': 20},
                    'weight': 1.0,
                    'description': '主要反转信号'
                },
                {
                    'name': 'Volume Profile',
                    'parameters': {'price_bins': 20},
                    'weight': 0.7,
                    'description': '确认关键价位'
                }
            ]
        )
        strategies['rsi_divergence'] = rsi_divergence_strategy
        
        # 3. Ichimoku云策略
        ichimoku_strategy = self.create_tradingview_strategy(
            "Ichimoku云综合",
            [
                {
                    'name': 'Ichimoku Cloud',
                    'parameters': {'tenkan_period': 9, 'kijun_period': 26, 'senkou_span_b_period': 52},
                    'weight': 1.0,
                    'description': '主要分析框架'
                },
                {
                    'name': 'Supertrend',
                    'parameters': {'atr_period': 10, 'multiplier': 2},
                    'weight': 0.6,
                    'description': '趋势确认'
                }
            ]
        )
        strategies['ichimoku_cloud'] = ichimoku_strategy
        
        # 4. 多指标综合策略
        multi_indicator_strategy = self.create_tradingview_strategy(
            "多指标综合",
            [
                {
                    'name': 'Supertrend',
                    'parameters': {'atr_period': 10, 'multiplier': 3},
                    'weight': 0.8,
                    'description': '趋势判断'
                },
                {
                    'name': 'RSI Divergence',
                    'parameters': {'rsi_period': 14, 'lookback': 20},
                    'weight': 0.7,
                    'description': '反转信号'
                },
                {
                    'name': 'Volume Profile',
                    'parameters': {'price_bins': 20},
                    'weight': 0.5,
                    'description': '关键价位'
                },
                {
                    'name': 'ATR Trailing Stop',
                    'parameters': {'atr_period': 14, 'multiplier': 2},
                    'weight': 0.6,
                    'description': '风险管理'
                }
            ]
        )
        strategies['multi_indicator'] = multi_indicator_strategy
        
        return strategies
    
    def backtest_strategy(self, strategy_name: str, signals: np.ndarray,
                         initial_capital: float = 100000) -> Dict[str, float]:
        """回测策略"""
        close_prices = self.data['close'].values
        
        if len(signals) != len(close_prices):
            raise ValueError("信号长度与价格数据长度不一致")
        
        # 简单回测
        position = 0
        capital = initial_capital
        trades = []
        returns = []
        equity_curve = []
        
        for i in range(len(signals)):
            # 记录权益曲线
            if position > 0:
                current_value = capital + position * close_prices[i]
            else:
                current_value = capital
            equity_curve.append(current_value)
            
            # 交易逻辑
            if i == 0:
                continue
            
            # 买入信号
            if signals[i] > 0.5 and position == 0:
                position = capital / close_prices[i]
                capital = 0
                trades.append({
                    'type': 'buy',
                    'price': close_prices[i],
                    'index': i,
                    'signal_strength': signals[i]
                })
            
            # 卖出信号
            elif signals[i] < -0.5 and position > 0:
                capital = position * close_prices[i]
                position = 0
                trades.append({
                    'type': 'sell',
                    'price': close_prices[i],
                    'index': i,
                    'signal_strength': signals[i]
                })
                
                # 计算交易收益
                if len(trades) >= 2 and trades[-2]['type'] == 'buy':
                    buy_price = trades[-2]['price']
                    sell_price = trades[-1]['price']
                    trade_return = (sell_price - buy_price) / buy_price
                    returns.append(trade_return)
        
        # 计算最终价值
        if position > 0:
            final_value = position * close_prices[-1]
        else:
            final_value = capital
        
        # 计算绩效指标
        total_return = (final_value - initial_capital) / initial_capital
        num_trades = len([t for t in trades if t['type'] in ['buy', 'sell']]) // 2
        
        if returns:
            avg_return = np.mean(returns)
            win_rate = len([r for r in returns if r > 0]) / len(returns)
            max_return = np.max(returns) if returns else 0
            min_return = np.min(returns) if returns else 0
            std_return = np.std(returns) if len(returns) > 1 else 0
            
            # 计算夏普比率
            if std_return > 0:
                sharpe_ratio = np.mean(returns) / std_return * np.sqrt(252)
            else:
                sharpe_ratio = 0
            
            # 计算最大回撤
            equity_array = np.array(equity_curve)
            peak = np.maximum.accumulate(equity_array)
            drawdown = (equity_array - peak) / peak
            max_drawdown = np.min(drawdown)
        else:
            avg_return = 0
            win_rate = 0
            max_return = 0
            min_return = 0
            sharpe_ratio = 0
            max_drawdown = 0
        
        performance = {
            'total_return': float(total_return),
            'num_trades': num_trades,
            'avg_return_per_trade': float(avg_return),
            'win_rate': float(win_rate),
            'max_return': float(max_return),
            'min_return': float(min_return),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'final_value': float(final_value),
            'initial_capital': float(initial_capital),
            'total_trades': len(trades)
        }
        
        return performance
    
    def run_all_strategies(self, initial_capital: float = 100000) -> Dict[str, Dict[str, Any]]:
        """运行所有策略"""
        print("\n🧪 运行TradingView策略测试...")
        
        strategies = self.create_preset_strategies()
        results = {}
        
        for strategy_name, strategy in strategies.items():
            print(f"\n🔧 测试策略: {strategy_name}")
            print(f"   使用指标: {', '.join([ind['name'] for ind in strategy['indicators']])}")
            
            try:
                # 获取信号
                signals = strategy['signals']
                
                # 回测
                performance = self.backtest_strategy(strategy_name, signals, initial_capital)
                
                # 更新策略信息
                strategy['performance'] = performance
                results[strategy_name] = strategy
                
                print(f"   绩效:")
                print(f"     总收益率: {performance['total_return']:.2%}")
                print(f"     交易次数: {performance['num_trades']}")
                print(f"     胜率: {performance['win_rate']:.2%}")
                print(f"     夏普比率: {performance['sharpe_ratio']:.2f}")
                print(f"     最大回撤: {performance['max_drawdown']:.2%}")
                
            except Exception as e:
                print(f"   测试策略时出错: {e}")
        
        self.performance_results = results
        return results
    
    def generate_integration_report(self, results: Dict[str, Dict[str, Any]]) -> str:
        """生成整合报告"""
        report = []
        report.append("=" * 80)
        report.append("📊 TradingView策略整合报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"数据长度: {len(self.data)}")
        report.append("=" * 80)
        
        # 汇总所有策略的绩效
        summary_data = []
        
        for strategy_name, strategy in results.items():
            if strategy.get('performance'):
                perf = strategy['performance']
                summary_data.append({
                    '策略名称': strategy_name,
                    '总收益率': f"{perf['total_return']:.2%}",
                    '交易次数': perf['num_trades'],
                    '胜率': f"{perf['win_rate']:.2%}",
                    '夏普比率': f"{perf['sharpe_ratio']:.2f}",
                    '最大回撤': f"{perf['max_drawdown']:.2%}",
                    '使用指标': ', '.join([ind['name'] for ind in strategy['indicators']])
                })
        
        # 按收益率排序
        if summary_data:
            report.append("\n📈 策略绩效排名:")
            sorted_data = sorted(summary_data, 
                               key=lambda x: float(x['总收益率'].strip('%'))/100, 
                               reverse=True)
            
            for i, data in enumerate(sorted_data, 1):
                report.append(f"\n{i}. {data['策略名称']}:")
                report.append(f"   总收益率: {data['总收益率']}")
                report.append(f"   交易次数: {data['交易次数']}")
                report.append(f"   胜率: {data['胜率']}")
                report.append(f"   夏普比率: {data['夏普比率']}")
                report.append(f"   最大回撤: {data['最大回撤']}")
                report.append(f"   使用指标: {data['使用指标']}")
        
        # 最佳策略分析
        if summary_data:
            best_strategy = sorted_data[0]
            report.append("\n🏆 最佳策略分析:")
            report.append(f"策略名称: {best_strategy['策略名称']}")
            report.append(f"关键优势: {self._analyze_strategy_strengths(best_strategy['策略名称'], results)}")
            report.append(f"适用市场: {self._suggest_market_conditions(best_strategy['策略名称'])}")
        
        # 技术实现总结
        report.append("\n🔧 技术实现总结:")
        report.append(f"已整合指标数量: {len(self.tradingview_indicators)}")
        report.append(f"已创建策略数量: {len(results)}")
        report.append(f"指标来源: TradingView社区")
        
        loaded_indicators = list(self.tradingview_indicators.keys())
        report.append(f"已加载指标: {', '.join(loaded_indicators[:5])}{'...' if len(loaded_indicators) > 5 else ''}")
        
        # 建议和改进
        report.append("\n💡 建议和改进方向:")
        report.append("1. 进一步优化策略参数，提高绩效")
        report.append("2. 添加更多TradingView流行指标")
        report.append("3. 实现动态参数优化系统")
        report.append("4. 增加风险管理模块")
        report.append("5. 进行多市场、多品种测试")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def _analyze_strategy_strengths(self, strategy_name: str, 
                                   results: Dict[str, Dict[str, Any]]) -> str:
        """分析策略优势"""
        strengths = {
            'supertrend_trend': '擅长趋势跟踪，适合趋势明显的市场',
            'rsi_divergence': '擅长捕捉反转点，适合震荡和反转市场',
            'ichimoku_cloud': '提供全面的市场分析，适合多种市场条件',
            'multi_indicator': '综合多种指标，平衡性和适应性较好'
        }
        return strengths.get(strategy_name, '综合性强，适应多种市场')
    
    def _suggest_market_conditions(self, strategy_name: str) -> str:
        """建议适用市场条件"""
        conditions = {
            'supertrend_trend': '单边上涨或下跌趋势市场',
            'rsi_divergence': '震荡市场和趋势反转期',
            'ichimoku_cloud': '通用市场，特别适合日线级别交易',
            'multi_indicator': '多种市场条件，综合性较强'
        }
        return conditions.get(strategy_name, '通用市场条件')

def load_sample_data() -> pd.DataFrame:
    """加载示例数据"""
    np.random.seed(42)
    n_points = 1000
    
    dates = pd.date_range(start='2023-01-01', periods=n_points, freq='D')
    
    # 生成更真实的价格序列
    base_price = 100
    trend = np.sin(np.linspace(0, 4*np.pi, n_points)) * 0.2  # 周期性趋势
    noise = np.random.normal(0, 1, n_points) * 0.01  # 1%的日波动
    
    close_prices = base_price * (1 + trend + noise.cumsum() / 100)
    
    # 生成OHLC数据
    data = pd.DataFrame(index=dates)
    data['close'] = close_prices
    
    daily_volatility = np.random.normal(0, 0.015, n_points)
    
    data['open'] = data['close'].shift(1) * (1 + daily_volatility * 0.5)
    data['high'] = data[['open', 'close']].max(axis=1) * (1 + np.abs(daily_volatility) * 0.4)
    data['low'] = data[['open', 'close']].min(axis=1) * (1 - np.abs(daily_volatility) * 0.4)
    data['volume'] = np.random.lognormal(12, 0.8, n_points)
    
    # 处理第一行数据
    data.iloc[0, data.columns.get_loc('open')] = data.iloc[0]['close'] * 0.99
    
    return data

def main():
    """主函数"""
    print("🚀 启动TradingView策略整合系统...")
    
    # 加载数据
    print("\n📊 加载数据...")
    data = load_sample_data()
    print(f"数据形状: {data.shape}")
    print(f"数据时间范围: {data.index[0]} 至 {data.index[-1]}")
    
    # 创建整合器
    integrator = TradingViewStrategyIntegrator(data)
    
    # 运行所有策略
    results = integrator.run_all_strategies(initial_capital=100000)
    
    # 生成报告
    print("\n📝 生成整合报告...")
    report = integrator.generate_integration_report(results)
    
    # 保存报告
    report_file = f"tradingview_integration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存到: {report_file}")
    
    # 保存详细结果到JSON
    json_file = report_file.replace('.txt', '.json')
    detailed_results = {}
    
    for strategy_name, strategy in results.items():
        detailed_results[strategy_name] = {
            'name': strategy['name'],
            'created_at': strategy['created_at'],
            'indicators': strategy['indicators'],
            'performance': strategy.get('performance', {}),
            'code_preview': strategy['code'][:500] + '...' if len(strategy['code']) > 500 else strategy['code']
        }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 详细结果已保存到: {json_file}")
    
    # 保存策略代码文件
    strategies_dir = "tradingview_strategies"
    os.makedirs(strategies_dir, exist_ok=True)
    
    for strategy_name, strategy in results.items():
        code_file = os.path.join(strategies_dir, f"{strategy_name}.py")
        with open(code_file, 'w', encoding='utf-8') as f:
            f.write(strategy['code'])
    
    print(f"✅ 策略代码已保存到: {strategies_dir}/")
    
    print("\n" + "=" * 80)
    print("🎯 TradingView策略整合完成!")
    print("=" * 80)
    print("\n下一步建议:")
    print("1. 使用真实股票数据测试策略")
    print("2. 优化策略参数以提高绩效")
    print("3. 将最佳策略集成到自动化交易系统")
    print("4. 定期更新指标库，添加新策略")

if __name__ == "__main__":
    main()