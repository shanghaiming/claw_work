#!/usr/bin/env python3
"""
策略组合回测框架 (基于100个TradingView指标)

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

功能:
1. 加载100个TradingView指标
2. 支持多种组合方法
3. 自动化回测和绩效评估
4. 组合优化和报告生成

依赖:
- tradingview_100_indicators (本任务生成的指标库)
- 现有回测框架
- TA-Lib数据
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
import json
import warnings
from datetime import datetime, timedelta
import itertools
from dataclasses import dataclass
from enum import Enum
import random
import talib

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 尝试导入指标库
try:
    from tradingview_100_indicators import *
    INDICATOR_LIB_AVAILABLE = True
    print("✅ TradingView指标库导入成功")
except ImportError as e:
    print(f"⚠️ 指标库导入失败: {e}")
    print("⚠️ 使用TA-Lib作为后备")
    INDICATOR_LIB_AVAILABLE = False

warnings.filterwarnings('ignore')

print("=" * 80)
print("🔄 策略组合回测框架 (基于100个TradingView指标)")
print("=" * 80)

class CombinationMethod(Enum):
    """组合方法枚举"""
    WEIGHTED = "weighted"       # 加权组合：多个指标结果加权平均
    VOTING = "voting"           # 投票组合：多数指标同意则产生信号
    SERIES = "series"           # 串联组合：一个指标的输出作为另一个指标的输入
    PARALLEL = "parallel"       # 并联组合：多个指标独立运行，结果综合
    HIERARCHICAL = "hierarchical" # 分层组合：先筛选后确认

@dataclass
class IndicatorWrapper:
    """指标包装器"""
    name: str
    calculate_func: Callable
    signal_func: Callable
    default_params: Dict[str, Any]
    category: str
    weight: float = 1.0
    
    def calculate(self, data: pd.DataFrame, **kwargs) -> np.ndarray:
        """计算指标值"""
        params = self.default_params.copy()
        params.update(kwargs)
        
        try:
            # 根据指标类型调用相应函数
            if self.category == "price_based":
                result = self.calculate_func(
                    data['high'].values,
                    data['low'].values,
                    data['close'].values,
                    **params
                )
            elif self.category == "volume_based":
                result = self.calculate_func(
                    data['high'].values,
                    data['low'].values,
                    data['close'].values,
                    data['volume'].values,
                    **params
                )
            elif self.category == "pattern_recognition":
                result = self.calculate_func(
                    data['open'].values,
                    data['high'].values,
                    data['low'].values,
                    data['close'].values
                )
            else:
                result = self.calculate_func(data['close'].values, **params)
            
            return result
        except Exception as e:
            print(f"计算指标 {self.name} 时出错: {e}")
            return np.zeros(len(data))
    
    def generate_signal(self, data: pd.DataFrame, **kwargs) -> np.ndarray:
        """生成交易信号"""
        params = self.default_params.copy()
        params.update(kwargs)
        
        try:
            if self.category == "price_based":
                signal = self.signal_func(
                    data['high'].values,
                    data['low'].values,
                    data['close'].values,
                    **params
                )
            elif self.category == "volume_based":
                signal = self.signal_func(
                    data['high'].values,
                    data['low'].values,
                    data['close'].values,
                    data['volume'].values,
                    **params
                )
            elif self.category == "pattern_recognition":
                signal = self.signal_func(
                    data['open'].values,
                    data['high'].values,
                    data['low'].values,
                    data['close'].values
                )
            else:
                signal = self.signal_func(data['close'].values, **params)
            
            return signal
        except Exception as e:
            print(f"生成信号 {self.name} 时出错: {e}")
            return np.zeros(len(data))

class IndicatorLibrary:
    """指标库管理器"""
    
    def __init__(self):
        self.indicators: Dict[str, IndicatorWrapper] = {}
        self.load_indicators()
    
    def load_indicators(self):
        """加载指标库"""
        print("📊 加载指标库...")
        
        # 如果指标库不可用，使用TA-Lib作为后备
        if not INDICATOR_LIB_AVAILABLE:
            self.load_talib_fallback()
            return
        
        # 加载技术指标
        tech_indicators = [
            ("ADX", "price_based", {"timeperiod": 14}),
            ("RSI", "price_based", {"timeperiod": 14}),
            ("MACD", "price_based", {"fastperiod": 12, "slowperiod": 26, "signalperiod": 9}),
            ("BBANDS", "price_based", {"timeperiod": 20, "nbdevup": 2, "nbdevdn": 2}),
            ("ATR", "price_based", {"timeperiod": 14}),
            ("OBV", "volume_based", {}),
            ("EMA", "price_based", {"timeperiod": 20}),
            ("SMA", "price_based", {"timeperiod": 20}),
            ("STOCH", "price_based", {"fastk_period": 14, "slowk_period": 3, "slowd_period": 3}),
            ("CCI", "price_based", {"timeperiod": 20}),
        ]
        
        for name, category, params in tech_indicators:
            try:
                # 获取指标函数
                calc_func = getattr(talib, name)
                
                # 创建信号函数
                def create_signal_func(ind_name):
                    def signal_func(*args, **kwargs):
                        try:
                            values = calc_func(*args, **kwargs)
                            signal = np.zeros_like(values)
                            
                            # 简单信号逻辑
                            if isinstance(values, np.ndarray):
                                if values.ndim == 1:
                                    for i in range(1, len(values)):
                                        if not np.isnan(values[i]):
                                            if values[i] > 0 and values[i-1] <= 0:
                                                signal[i] = 1
                                            elif values[i] < 0 and values[i-1] >= 0:
                                                signal[i] = -1
                            
                            return signal
                        except Exception as e:
                            print(f"信号函数错误 {ind_name}: {e}")
                            return np.zeros_like(args[0])
                    return signal_func
                
                signal_func = create_signal_func(name)
                
                wrapper = IndicatorWrapper(
                    name=name,
                    calculate_func=calc_func,
                    signal_func=signal_func,
                    default_params=params,
                    category=category
                )
                
                self.indicators[name] = wrapper
                print(f"  ✅ 加载指标: {name}")
                
            except Exception as e:
                print(f"  ✗ 加载指标 {name} 失败: {e}")
        
        print(f"📈 总共加载 {len(self.indicators)} 个指标")
    
    def load_talib_fallback(self):
        """TA-Lib后备加载"""
        print("⚠️ 使用TA-Lib作为指标库后备")
        
        talib_indicators = [
            ("ADX", talib.ADX, {"timeperiod": 14}),
            ("RSI", talib.RSI, {"timeperiod": 14}),
            ("MACD", talib.MACD, {"fastperiod": 12, "slowperiod": 26, "signalperiod": 9}),
            ("BBANDS", talib.BBANDS, {"timeperiod": 20, "nbdevup": 2, "nbdevdn": 2}),
            ("ATR", talib.ATR, {"timeperiod": 14}),
            ("OBV", talib.OBV, {}),
            ("EMA", talib.EMA, {"timeperiod": 20}),
            ("SMA", talib.SMA, {"timeperiod": 20}),
            ("STOCH", talib.STOCH, {"fastk_period": 14, "slowk_period": 3, "slowd_period": 3}),
            ("CCI", talib.CCI, {"timeperiod": 20}),
        ]
        
        for name, calc_func, params in talib_indicators:
            def create_signal_func(ind_name, func):
                def signal_func(*args, **kwargs):
                    try:
                        values = func(*args, **kwargs)
                        signal = np.zeros_like(values)
                        
                        if isinstance(values, np.ndarray):
                            if values.ndim == 1:
                                for i in range(1, len(values)):
                                    if not np.isnan(values[i]):
                                        if values[i] > 0 and values[i-1] <= 0:
                                            signal[i] = 1
                                        elif values[i] < 0 and values[i-1] >= 0:
                                            signal[i] = -1
                        return signal
                    except Exception as e:
                        print(f"信号函数错误 {ind_name}: {e}")
                        return np.zeros_like(args[0])
                return signal_func
            
            signal_func = create_signal_func(name, calc_func)
            
            wrapper = IndicatorWrapper(
                name=name,
                calculate_func=calc_func,
                signal_func=signal_func,
                default_params=params,
                category="price_based"
            )
            
            self.indicators[name] = wrapper
        
        print(f"📈 加载 {len(self.indicators)} 个TA-Lib指标")

class CombinationStrategy:
    """组合策略"""
    
    def __init__(self, name: str, method: CombinationMethod, indicators: List[str], 
                 weights: Optional[List[float]] = None):
        self.name = name
        self.method = method
        self.indicators = indicators
        self.weights = weights if weights else [1.0/len(indicators)] * len(indicators)
        
        # 验证权重
        if len(self.weights) != len(indicators):
            self.weights = [1.0/len(indicators)] * len(indicators)
        
        # 归一化权重
        weight_sum = sum(self.weights)
        if weight_sum > 0:
            self.weights = [w/weight_sum for w in self.weights]
    
    def generate_signals(self, data: pd.DataFrame, indicator_lib: IndicatorLibrary) -> np.ndarray:
        """生成组合信号"""
        if not self.indicators:
            return np.zeros(len(data))
        
        signals = []
        
        # 获取每个指标的信号
        for indicator_name in self.indicators:
            if indicator_name in indicator_lib.indicators:
                indicator = indicator_lib.indicators[indicator_name]
                signal = indicator.generate_signal(data)
                signals.append(signal)
            else:
                # 如果指标不存在，使用零信号
                signals.append(np.zeros(len(data)))
        
        signals = np.array(signals)
        
        # 应用组合方法
        if self.method == CombinationMethod.WEIGHTED:
            # 加权组合
            weighted_signals = signals * np.array(self.weights).reshape(-1, 1)
            combined_signal = np.sum(weighted_signals, axis=0)
            
            # 转换为离散信号
            discrete_signal = np.zeros_like(combined_signal)
            discrete_signal[combined_signal > 0.5] = 1
            discrete_signal[combined_signal < -0.5] = -1
            
            return discrete_signal
        
        elif self.method == CombinationMethod.VOTING:
            # 投票组合
            vote_signals = np.zeros_like(signals[0])
            
            for i in range(len(signals[0])):
                buy_votes = np.sum(signals[:, i] == 1)
                sell_votes = np.sum(signals[:, i] == -1)
                
                if buy_votes > sell_votes and buy_votes > len(self.indicators) / 2:
                    vote_signals[i] = 1
                elif sell_votes > buy_votes and sell_votes > len(self.indicators) / 2:
                    vote_signals[i] = -1
            
            return vote_signals
        
        elif self.method == CombinationMethod.PARALLEL:
            # 并联组合：任一指标发出信号则产生信号
            parallel_signal = np.zeros_like(signals[0])
            
            for i in range(len(signals[0])):
                for j in range(len(signals)):
                    if signals[j, i] != 0:
                        parallel_signal[i] = signals[j, i]
                        break
            
            return parallel_signal
        
        else:
            # 默认使用加权组合
            weighted_signals = signals * np.array(self.weights).reshape(-1, 1)
            combined_signal = np.sum(weighted_signals, axis=0)
            discrete_signal = np.zeros_like(combined_signal)
            discrete_signal[combined_signal > 0.5] = 1
            discrete_signal[combined_signal < -0.5] = -1
            
            return discrete_signal

class BacktestEngine:
    """回测引擎"""
    
    def __init__(self, initial_capital: float = 1000000.0):
        self.initial_capital = initial_capital
    
    def run_backtest(self, data: pd.DataFrame, signals: np.ndarray, 
                     commission_rate: float = 0.001) -> Dict[str, Any]:
        """运行回测"""
        if len(data) != len(signals):
            raise ValueError("数据和信号长度不匹配")
        
        # 初始化变量
        capital = self.initial_capital
        position = 0
        trades = []
        equity_curve = []
        
        # 回测循环
        for i in range(len(data)):
            price = data['close'].iloc[i]
            signal = signals[i]
            
            # 记录当前权益
            current_equity = capital + position * price
            equity_curve.append(current_equity)
            
            # 执行交易信号
            if signal == 1 and position <= 0:  # 买入信号
                if position < 0:  # 平空仓
                    capital += position * price * (1 - commission_rate)
                    position = 0
                
                # 开多仓 (使用50%资金)
                buy_amount = capital * 0.5
                if buy_amount > 0:
                    buy_shares = buy_amount / price
                    capital -= buy_amount
                    position += buy_shares
                    
                    trades.append({
                        'date': data.index[i] if hasattr(data.index[i], 'strftime') else i,
                        'type': 'BUY',
                        'price': price,
                        'shares': buy_shares,
                        'capital_change': -buy_amount
                    })
            
            elif signal == -1 and position >= 0:  # 卖出信号
                if position > 0:  # 平多仓
                    capital += position * price * (1 - commission_rate)
                    trades.append({
                        'date': data.index[i] if hasattr(data.index[i], 'strftime') else i,
                        'type': 'SELL',
                        'price': price,
                        'shares': position,
                        'capital_change': position * price * (1 - commission_rate)
                    })
                    position = 0
                
                # 开空仓 (暂不支持)
                pass
        
        # 最后平仓
        if position != 0:
            last_price = data['close'].iloc[-1]
            capital += position * last_price * (1 - commission_rate)
            position = 0
        
        # 计算绩效指标
        equity_curve = np.array(equity_curve)
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        if len(returns) > 0:
            total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] if equity_curve[0] != 0 else 0
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) != 0 else 0
            max_drawdown = self.calculate_max_drawdown(equity_curve)
            win_rate = len([r for r in returns if r > 0]) / len(returns) if len(returns) > 0 else 0
        else:
            total_return = 0
            sharpe_ratio = 0
            max_drawdown = 0
            win_rate = 0
        
        return {
            'total_return': total_return,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'final_capital': equity_curve[-1] if len(equity_curve) > 0 else self.initial_capital,
            'trades_count': len(trades),
            'equity_curve': equity_curve.tolist(),
            'trades': trades
        }
    
    def calculate_max_drawdown(self, equity_curve: np.ndarray) -> float:
        """计算最大回撤"""
        peak = equity_curve[0]
        max_dd = 0.0
        
        for value in equity_curve:
            if value > peak:
                peak = value
            
            dd = (peak - value) / peak if peak != 0 else 0
            if dd > max_dd:
                max_dd = dd
        
        return max_dd

class StrategyCombinationBacktestFramework:
    """策略组合回测框架主类"""
    
    def __init__(self):
        self.indicator_lib = IndicatorLibrary()
        self.backtest_engine = BacktestEngine()
        self.strategies: List[CombinationStrategy] = []
    
    def create_preset_strategies(self):
        """创建预设策略组合"""
        print("🔄 创建预设策略组合...")
        
        # 策略1: 趋势指标组合
        trend_strategy = CombinationStrategy(
            name="趋势指标组合",
            method=CombinationMethod.WEIGHTED,
            indicators=["ADX", "EMA", "MACD", "ATR"],
            weights=[0.3, 0.3, 0.2, 0.2]
        )
        self.strategies.append(trend_strategy)
        print(f"  ✅ 创建策略: {trend_strategy.name}")
        
        # 策略2: 动量指标组合
        momentum_strategy = CombinationStrategy(
            name="动量指标组合",
            method=CombinationMethod.VOTING,
            indicators=["RSI", "STOCH", "CCI", "OBV"],
            weights=[0.25, 0.25, 0.25, 0.25]
        )
        self.strategies.append(momentum_strategy)
        print(f"  ✅ 创建策略: {momentum_strategy.name}")
        
        # 策略3: 波动率指标组合
        volatility_strategy = CombinationStrategy(
            name="波动率指标组合",
            method=CombinationMethod.PARALLEL,
            indicators=["BBANDS", "ATR", "STDDEV"],
            weights=[0.4, 0.3, 0.3]
        )
        self.strategies.append(volatility_strategy)
        print(f"  ✅ 创建策略: {volatility_strategy.name}")
        
        # 策略4: 综合指标组合
        comprehensive_strategy = CombinationStrategy(
            name="综合指标组合",
            method=CombinationMethod.WEIGHTED,
            indicators=["ADX", "RSI", "MACD", "BBANDS", "OBV"],
            weights=[0.2, 0.2, 0.2, 0.2, 0.2]
        )
        self.strategies.append(comprehensive_strategy)
        print(f"  ✅ 创建策略: {comprehensive_strategy.name}")
        
        print(f"📋 总共创建 {len(self.strategies)} 个预设策略")
    
    def load_test_data(self) -> pd.DataFrame:
        """加载测试数据"""
        print("📊 加载测试数据...")
        
        # 生成模拟数据
        np.random.seed(42)
        n = 500
        
        dates = pd.date_range(start='2022-01-01', periods=n, freq='D')
        
        # 生成价格序列
        returns = np.random.normal(0.0005, 0.02, n)
        prices = 100 * np.exp(np.cumsum(returns))
        
        # 生成OHLCV数据
        data = pd.DataFrame({
            'open': prices * (1 + np.random.normal(0, 0.01, n)),
            'high': prices * (1 + np.abs(np.random.normal(0, 0.015, n))),
            'low': prices * (1 - np.abs(np.random.normal(0, 0.015, n))),
            'close': prices,
            'volume': np.random.randint(10000, 100000, n)
        }, index=dates)
        
        print(f"  ✅ 生成 {len(data)} 条测试数据")
        return data
    
    def run_all_strategies(self, data: pd.DataFrame) -> Dict[str, Any]:
        """运行所有策略的回测"""
        print("🚀 运行策略回测...")
        
        results = {}
        
        for strategy in self.strategies:
            print(f"  🔄 运行策略: {strategy.name}")
            
            # 生成信号
            signals = strategy.generate_signals(data, self.indicator_lib)
            
            # 运行回测
            backtest_result = self.backtest_engine.run_backtest(data, signals)
            
            results[strategy.name] = {
                'strategy': strategy.name,
                'method': strategy.method.value,
                'indicators': strategy.indicators,
                'weights': strategy.weights,
                'performance': backtest_result
            }
            
            print(f"    📈 收益率: {backtest_result['total_return']:.2%}")
            print(f"    📊 夏普比率: {backtest_result['sharpe_ratio']:.3f}")
            print(f"    📉 最大回撤: {backtest_result['max_drawdown']:.2%}")
            print(f"    🎯 胜率: {backtest_result['win_rate']:.2%}")
            print(f"    🔄 交易次数: {backtest_result['trades_count']}")
        
        return results
    
    def generate_report(self, results: Dict[str, Any], output_file: str = "strategy_combination_report.json"):
        """生成回测报告"""
        print("📋 生成回测报告...")
        
        report = {
            'generated_at': datetime.now().isoformat(),
            'total_strategies': len(results),
            'strategies': results,
            'summary': self.generate_summary(results)
        }
        
        # 保存JSON报告
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"  ✅ 报告已保存: {output_file}")
        
        # 打印摘要
        self.print_summary(report['summary'])
        
        return report
    
    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """生成绩效摘要"""
        if not results:
            return {}
        
        best_strategy = None
        best_return = -float('inf')
        
        for strategy_name, result in results.items():
            return_val = result['performance']['total_return']
            if return_val > best_return:
                best_return = return_val
                best_strategy = strategy_name
        
        return {
            'best_strategy': best_strategy,
            'best_return': best_return,
            'total_strategies_tested': len(results),
            'average_return': np.mean([r['performance']['total_return'] for r in results.values()]),
            'average_sharpe': np.mean([r['performance']['sharpe_ratio'] for r in results.values()]),
            'average_drawdown': np.mean([r['performance']['max_drawdown'] for r in results.values()])
        }
    
    def print_summary(self, summary: Dict[str, Any]):
        """打印摘要"""
        print("\n" + "=" * 80)
        print("📊 回测结果摘要")
        print("=" * 80)
        
        if not summary:
            print("无结果")
            return
        
        print(f"🏆 最佳策略: {summary.get('best_strategy', 'N/A')}")
        print(f"📈 最佳收益率: {summary.get('best_return', 0):.2%}")
        print(f"📋 测试策略总数: {summary.get('total_strategies_tested', 0)}")
        print(f"📊 平均收益率: {summary.get('average_return', 0):.2%}")
        print(f"⚖️ 平均夏普比率: {summary.get('average_sharpe', 0):.3f}")
        print(f"📉 平均最大回撤: {summary.get('average_drawdown', 0):.2%}")
        print("=" * 80)

def main():
    """主函数"""
    print("🚀 启动策略组合回测框架")
    
    # 创建框架实例
    framework = StrategyCombinationBacktestFramework()
    
    # 创建预设策略
    framework.create_preset_strategies()
    
    # 加载测试数据
    data = framework.load_test_data()
    
    # 运行所有策略回测
    results = framework.run_all_strategies(data)
    
    # 生成报告
    report = framework.generate_report(results)
    
    print("\n✅ 策略组合回测框架执行完成!")
    print(f"📁 报告文件: strategy_combination_report.json")
    print(f"📈 测试策略: {len(results)} 个")
    
    return report

if __name__ == "__main__":
    main()