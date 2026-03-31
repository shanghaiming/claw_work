#!/usr/bin/env python3
"""
指标组合框架系统

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

功能:
1. 提供灵活的指标组合和测试框架
2. 支持多种组合方法（串联、并联、加权等）
3. 自动评估组合性能
4. 生成组合策略报告
5. 优化组合参数
"""

import talib
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable, Union
import json
import warnings
from datetime import datetime, timedelta
import itertools
from dataclasses import dataclass
from enum import Enum
warnings.filterwarnings('ignore')

print("=" * 80)
print("🔄 指标组合框架系统")
print("=" * 80)

class CombinationMethod(Enum):
    """组合方法枚举"""
    SERIES = "series"           # 串联组合：一个指标的输出作为另一个指标的输入
    PARALLEL = "parallel"       # 并联组合：多个指标独立运行，结果综合
    WEIGHTED = "weighted"       # 加权组合：多个指标结果加权平均
    VOTING = "voting"           # 投票组合：多数指标同意则产生信号
    HIERARCHICAL = "hierarchical" # 分层组合：先筛选后确认

@dataclass
class IndicatorConfig:
    """指标配置"""
    name: str
    function: Callable
    parameters: Dict[str, Any]
    weight: float = 1.0
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'name': self.name,
            'parameters': self.parameters,
            'weight': self.weight,
            'enabled': self.enabled
        }

@dataclass
class CombinationResult:
    """组合结果"""
    combination_id: str
    method: CombinationMethod
    indicators: List[IndicatorConfig]
    signals: np.ndarray
    confidence: np.ndarray
    performance: Optional[Dict[str, float]] = None
    metadata: Optional[Dict[str, Any]] = None

class IndicatorCombinationFramework:
    """指标组合框架"""
    
    def __init__(self, data: pd.DataFrame):
        """
        初始化组合框架
        
        Args:
            data: 包含OHLCV数据的DataFrame
        """
        self.data = data
        self.indicators_cache = {}
        self.combinations = {}
        self.performance_metrics = {}
        
        # 确保数据格式正确
        required_columns = ['open', 'high', 'low', 'close', 'volume']
        for col in required_columns:
            if col not in data.columns:
                raise ValueError(f"数据缺少必要列: {col}")
    
    def calculate_indicator(self, config: IndicatorConfig) -> np.ndarray:
        """计算单个指标"""
        cache_key = f"{config.name}_{str(config.parameters)}"
        
        if cache_key in self.indicators_cache:
            return self.indicators_cache[cache_key]
        
        try:
            # 获取指标函数
            indicator_func = getattr(talib, config.name, None)
            if indicator_func is None:
                raise ValueError(f"指标 {config.name} 不存在")
            
            # 根据指标类型准备参数
            result = self._call_indicator(indicator_func, config.parameters)
            
            # 缓存结果
            self.indicators_cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"计算指标 {config.name} 时出错: {e}")
            return np.zeros(len(self.data))
    
    def _call_indicator(self, func: Callable, params: Dict[str, Any]) -> np.ndarray:
        """调用指标函数"""
        # 获取函数签名
        import inspect
        sig = inspect.signature(func)
        
        # 准备参数
        call_args = {}
        
        # 标准OHLC参数
        if 'open' in params:
            call_args['open'] = params['open']
        elif 'open' in sig.parameters:
            call_args['open'] = self.data['open'].values
        
        if 'high' in params:
            call_args['high'] = params['high']
        elif 'high' in sig.parameters:
            call_args['high'] = self.data['high'].values
        
        if 'low' in params:
            call_args['low'] = params['low']
        elif 'low' in sig.parameters:
            call_args['low'] = self.data['low'].values
        
        if 'close' in params:
            call_args['close'] = params['close']
        elif 'close' in sig.parameters:
            call_args['close'] = self.data['close'].values
        
        if 'volume' in params:
            call_args['volume'] = params['volume']
        elif 'volume' in sig.parameters:
            call_args['volume'] = self.data['volume'].values
        
        # 其他参数
        for param_name, param_value in params.items():
            if param_name not in ['open', 'high', 'low', 'close', 'volume']:
                call_args[param_name] = param_value
        
        # 调用函数
        result = func(**call_args)
        
        # 处理多个返回值的情况
        if isinstance(result, tuple):
            # 通常第一个返回值是主要指标值
            return result[0]
        
        return result
    
    def combine_series(self, indicators: List[IndicatorConfig]) -> CombinationResult:
        """串联组合：一个指标的输出作为另一个指标的输入"""
        if len(indicators) < 2:
            raise ValueError("串联组合需要至少2个指标")
        
        signals = None
        current_data = self.data.copy()
        
        for i, indicator in enumerate(indicators):
            if not indicator.enabled:
                continue
            
            # 计算当前指标
            indicator_result = self.calculate_indicator(indicator)
            
            # 如果是第一个指标，直接使用结果
            if signals is None:
                signals = indicator_result
            else:
                # 后续指标基于前一个指标的结果进行调整
                # 这里使用简单的加权平均
                signals = signals * 0.7 + indicator_result * 0.3
            
            # 更新数据用于下一个指标（如果有需要）
            current_data[f'indicator_{i}'] = indicator_result
        
        # 生成最终信号（-1: 卖出, 0: 持有, 1: 买入）
        final_signals = np.zeros_like(signals)
        final_signals[signals > 0.5] = 1  # 买入信号
        final_signals[signals < -0.5] = -1  # 卖出信号
        
        # 置信度（信号强度）
        confidence = np.abs(signals)
        
        return CombinationResult(
            combination_id=f"series_{len(indicators)}",
            method=CombinationMethod.SERIES,
            indicators=indicators,
            signals=final_signals,
            confidence=confidence
        )
    
    def combine_parallel(self, indicators: List[IndicatorConfig]) -> CombinationResult:
        """并联组合：多个指标独立运行，结果综合"""
        if len(indicators) == 0:
            raise ValueError("需要至少1个指标")
        
        all_results = []
        weights = []
        
        for indicator in indicators:
            if not indicator.enabled:
                continue
            
            result = self.calculate_indicator(indicator)
            all_results.append(result)
            weights.append(indicator.weight)
        
        if not all_results:
            raise ValueError("没有启用的指标")
        
        # 归一化权重
        weights = np.array(weights)
        weights = weights / weights.sum()
        
        # 加权平均
        combined = np.zeros_like(all_results[0])
        for result, weight in zip(all_results, weights):
            combined += result * weight
        
        # 生成信号
        signals = np.zeros_like(combined)
        signals[combined > 0.5] = 1
        signals[combined < -0.5] = -1
        
        # 置信度（基于指标一致性）
        if len(all_results) > 1:
            # 计算指标之间的相关性作为置信度
            result_matrix = np.vstack(all_results)
            correlation = np.corrcoef(result_matrix)[0, 1] if len(all_results) > 1 else 1.0
            confidence = np.ones_like(combined) * max(0, correlation)
        else:
            confidence = np.ones_like(combined)
        
        return CombinationResult(
            combination_id=f"parallel_{len(indicators)}",
            method=CombinationMethod.PARALLEL,
            indicators=indicators,
            signals=signals,
            confidence=confidence
        )
    
    def combine_weighted(self, indicators: List[IndicatorConfig]) -> CombinationResult:
        """加权组合：多个指标结果加权平均"""
        return self.combine_parallel(indicators)  # 实现类似
    
    def combine_voting(self, indicators: List[IndicatorConfig], threshold: float = 0.5) -> CombinationResult:
        """投票组合：多数指标同意则产生信号"""
        if len(indicators) == 0:
            raise ValueError("需要至少1个指标")
        
        all_results = []
        
        for indicator in indicators:
            if not indicator.enabled:
                continue
            
            result = self.calculate_indicator(indicator)
            # 转换为-1, 0, 1信号
            signals = np.zeros_like(result)
            signals[result > 0.5] = 1
            signals[result < -0.5] = -1
            all_results.append(signals)
        
        if not all_results:
            raise ValueError("没有启用的指标")
        
        # 投票统计
        vote_matrix = np.vstack(all_results)
        vote_sum = vote_matrix.sum(axis=0)
        
        # 生成最终信号
        signals = np.zeros_like(vote_sum)
        signals[vote_sum > len(indicators) * threshold] = 1  # 多数同意买入
        signals[vote_sum < -len(indicators) * threshold] = -1  # 多数同意卖出
        
        # 置信度（同意比例）
        confidence = np.abs(vote_sum) / len(indicators)
        
        return CombinationResult(
            combination_id=f"voting_{len(indicators)}",
            method=CombinationMethod.VOTING,
            indicators=indicators,
            signals=signals,
            confidence=confidence
        )
    
    def evaluate_performance(self, result: CombinationResult, 
                           initial_capital: float = 100000) -> Dict[str, float]:
        """评估组合性能"""
        signals = result.signals
        close_prices = self.data['close'].values
        
        if len(signals) != len(close_prices):
            raise ValueError("信号长度与价格数据长度不一致")
        
        # 简单回测
        position = 0
        capital = initial_capital
        trades = []
        returns = []
        
        for i in range(1, len(signals)):
            # 买入信号
            if signals[i] == 1 and position == 0:
                position = capital / close_prices[i]
                capital = 0
                trades.append({
                    'type': 'buy',
                    'price': close_prices[i],
                    'index': i
                })
            
            # 卖出信号
            elif signals[i] == -1 and position > 0:
                capital = position * close_prices[i]
                position = 0
                trades.append({
                    'type': 'sell',
                    'price': close_prices[i],
                    'index': i
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
        else:
            avg_return = 0
            win_rate = 0
            max_return = 0
            min_return = 0
        
        # 计算夏普比率（简化）
        if returns and np.std(returns) > 0:
            sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252)
        else:
            sharpe_ratio = 0
        
        performance = {
            'total_return': float(total_return),
            'num_trades': num_trades,
            'avg_return_per_trade': float(avg_return),
            'win_rate': float(win_rate),
            'max_return': float(max_return),
            'min_return': float(min_return),
            'sharpe_ratio': float(sharpe_ratio),
            'final_value': float(final_value),
            'initial_capital': float(initial_capital)
        }
        
        result.performance = performance
        self.performance_metrics[result.combination_id] = performance
        
        return performance
    
    def create_preset_combinations(self) -> Dict[str, List[IndicatorConfig]]:
        """创建预设组合"""
        presets = {}
        
        # 1. 趋势跟踪组合
        trend_configs = [
            IndicatorConfig(
                name='EMA',
                function=talib.EMA,
                parameters={'timeperiod': 20},
                weight=1.0
            ),
            IndicatorConfig(
                name='MACD',
                function=talib.MACD,
                parameters={'fastperiod': 12, 'slowperiod': 26, 'signalperiod': 9},
                weight=0.8
            ),
            IndicatorConfig(
                name='ADX',
                function=talib.ADX,
                parameters={'timeperiod': 14},
                weight=0.6
            )
        ]
        presets['trend_following'] = trend_configs
        
        # 2. 均值回归组合
        mean_reversion_configs = [
            IndicatorConfig(
                name='RSI',
                function=talib.RSI,
                parameters={'timeperiod': 14},
                weight=1.0
            ),
            IndicatorConfig(
                name='STOCH',
                function=talib.STOCH,
                parameters={'fastk_period': 14, 'slowk_period': 3, 'slowd_period': 3},
                weight=0.8
            ),
            IndicatorConfig(
                name='BBANDS',
                function=talib.BBANDS,
                parameters={'timeperiod': 20, 'nbdevup': 2, 'nbdevdn': 2},
                weight=0.7
            )
        ]
        presets['mean_reversion'] = mean_reversion_configs
        
        # 3. 突破策略组合
        breakout_configs = [
            IndicatorConfig(
                name='SAR',
                function=talib.SAR,
                parameters={'acceleration': 0.02, 'maximum': 0.2},
                weight=1.0
            ),
            IndicatorConfig(
                name='ATR',
                function=talib.ATR,
                parameters={'timeperiod': 14},
                weight=0.7
            ),
            IndicatorConfig(
                name='AROON',
                function=talib.AROON,
                parameters={'timeperiod': 25},
                weight=0.6
            )
        ]
        presets['breakout'] = breakout_configs
        
        # 4. 动量策略组合
        momentum_configs = [
            IndicatorConfig(
                name='MOM',
                function=talib.MOM,
                parameters={'timeperiod': 10},
                weight=1.0
            ),
            IndicatorConfig(
                name='ROC',
                function=talib.ROC,
                parameters={'timeperiod': 12},
                weight=0.8
            ),
            IndicatorConfig(
                name='TRIX',
                function=talib.TRIX,
                parameters={'timeperiod': 30},
                weight=0.7
            )
        ]
        presets['momentum'] = momentum_configs
        
        # 5. 波动率策略组合
        volatility_configs = [
            IndicatorConfig(
                name='BBANDS',
                function=talib.BBANDS,
                parameters={'timeperiod': 20, 'nbdevup': 2, 'nbdevdn': 2},
                weight=1.0
            ),
            IndicatorConfig(
                name='ATR',
                function=talib.ATR,
                parameters={'timeperiod': 14},
                weight=0.8
            ),
            IndicatorConfig(
                name='STDDEV',
                function=talib.STDDEV,
                parameters={'timeperiod': 20, 'nbdev': 1},
                weight=0.6
            )
        ]
        presets['volatility'] = volatility_configs
        
        return presets
    
    def run_preset_combinations(self, initial_capital: float = 100000) -> Dict[str, CombinationResult]:
        """运行所有预设组合"""
        presets = self.create_preset_combinations()
        results = {}
        
        for preset_name, indicators in presets.items():
            print(f"\n🔧 运行预设组合: {preset_name}")
            print(f"   使用指标: {', '.join([ind.name for ind in indicators])}")
            
            try:
                # 使用并联组合方法
                result = self.combine_parallel(indicators)
                
                # 评估性能
                performance = self.evaluate_performance(result, initial_capital)
                
                print(f"   绩效:")
                print(f"     总收益率: {performance['total_return']:.2%}")
                print(f"     交易次数: {performance['num_trades']}")
                print(f"     胜率: {performance['win_rate']:.2%}")
                print(f"     夏普比率: {performance['sharpe_ratio']:.2f}")
                
                results[preset_name] = result
                
            except Exception as e:
                print(f"   运行组合时出错: {e}")
        
        return results
    
    def generate_combination_report(self, results: Dict[str, CombinationResult]) -> str:
        """生成组合报告"""
        report = []
        report.append("=" * 80)
        report.append("📊 指标组合测试报告")
        report.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"数据长度: {len(self.data)}")
        report.append("=" * 80)
        
        # 汇总所有组合的绩效
        summary_data = []
        
        for combo_name, result in results.items():
            if result.performance:
                perf = result.performance
                summary_data.append({
                    '组合名称': combo_name,
                    '总收益率': f"{perf['total_return']:.2%}",
                    '交易次数': perf['num_trades'],
                    '胜率': f"{perf['win_rate']:.2%}",
                    '夏普比率': f"{perf['sharpe_ratio']:.2f}",
                    '平均每笔收益': f"{perf['avg_return_per_trade']:.2%}",
                    '使用指标': ', '.join([ind.name for ind in result.indicators if ind.enabled])
                })
        
        # 按收益率排序
        if summary_data:
            report.append("\n📈 组合绩效排名:")
            sorted_data = sorted(summary_data, 
                               key=lambda x: float(x['总收益率'].strip('%'))/100, 
                               reverse=True)
            
            for i, data in enumerate(sorted_data, 1):
                report.append(f"\n{i}. {data['组合名称']}:")
                report.append(f"   总收益率: {data['总收益率']}")
                report.append(f"   交易次数: {data['交易次数']}")
                report.append(f"   胜率: {data['胜率']}")
                report.append(f"   夏普比率: {data['夏普比率']}")
                report.append(f"   使用指标: {data['使用指标']}")
        
        # 最佳组合分析
        if summary_data:
            best_combo = sorted_data[0]
            report.append("\n🏆 最佳组合分析:")
            report.append(f"组合名称: {best_combo['组合名称']}")
            report.append(f"关键优势: {self._analyze_combo_strengths(best_combo['组合名称'], results)}")
            report.append(f"适用市场: {self._suggest_market_conditions(best_combo['组合名称'])}")
        
        # 建议和改进
        report.append("\n💡 建议和改进方向:")
        report.append("1. 对于趋势市场，建议使用趋势跟踪组合")
        report.append("2. 对于震荡市场，建议使用均值回归组合")
        report.append("3. 考虑加入风险管理指标(如ATR)来控制仓位")
        report.append("4. 尝试不同的组合方法(投票、分层等)")
        report.append("5. 进行参数优化以获得更好表现")
        
        report.append("\n" + "=" * 80)
        
        return "\n".join(report)
    
    def _analyze_combo_strengths(self, combo_name: str, results: Dict[str, CombinationResult]) -> str:
        """分析组合优势"""
        strengths = {
            'trend_following': '擅长捕捉和跟随趋势，避免逆势交易',
            'mean_reversion': '擅长在震荡市场中高抛低吸',
            'breakout': '擅长捕捉突破行情，及时入场',
            'momentum': '擅长利用价格动量，快速获利',
            'volatility': '擅长利用波动率变化，适应不同市场'
        }
        return strengths.get(combo_name, '综合性强，适应多种市场')
    
    def _suggest_market_conditions(self, combo_name: str) -> str:
        """建议适用市场条件"""
        conditions = {
            'trend_following': '单边上涨或下跌趋势市场',
            'mean_reversion': '震荡盘整市场',
            'breakout': '突破关键位后的趋势启动期',
            'momentum': '高波动性、有明显趋势的市场',
            'volatility': '波动率变化明显的市场'
        }
        return conditions.get(combo_name, '通用市场条件')

def load_sample_data() -> pd.DataFrame:
    """加载示例数据"""
    # 生成示例数据
    np.random.seed(42)
    n_points = 500
    
    dates = pd.date_range(start='2023-01-01', periods=n_points, freq='D')
    
    # 生成价格序列（带趋势和波动）
    base_price = 100
    trend = np.linspace(0, 0.3, n_points)  # 30%的趋势
    noise = np.random.normal(0, 1, n_points) * 0.02  # 2%的日波动
    
    close_prices = base_price * (1 + trend + noise.cumsum() / 100)
    
    # 生成OHLC数据
    data = pd.DataFrame(index=dates)
    data['close'] = close_prices
    
    # 生成合理的OHLC关系
    daily_volatility = np.random.normal(0, 0.02, n_points)
    
    data['open'] = data['close'].shift(1) * (1 + daily_volatility * 0.5)
    data['high'] = data[['open', 'close']].max(axis=1) * (1 + np.abs(daily_volatility) * 0.3)
    data['low'] = data[['open', 'close']].min(axis=1) * (1 - np.abs(daily_volatility) * 0.3)
    data['volume'] = np.random.lognormal(10, 1, n_points)
    
    # 处理第一行数据
    data.iloc[0, data.columns.get_loc('open')] = data.iloc[0]['close'] * 0.99
    
    return data

def main():
    """主函数"""
    print("🚀 启动指标组合框架系统...")
    
    # 加载数据
    print("\n📊 加载数据...")
    data = load_sample_data()
    print(f"数据形状: {data.shape}")
    print(f"数据时间范围: {data.index[0]} 至 {data.index[-1]}")
    
    # 创建组合框架
    framework = IndicatorCombinationFramework(data)
    
    # 运行预设组合
    print("\n🧪 运行预设组合测试...")
    results = framework.run_preset_combinations(initial_capital=100000)
    
    # 生成报告
    print("\n📝 生成测试报告...")
    report = framework.generate_combination_report(results)
    
    # 保存报告
    report_file = f"indicator_combination_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n✅ 报告已保存到: {report_file}")
    
    # 保存详细结果到JSON
    json_file = report_file.replace('.txt', '.json')
    detailed_results = {}
    
    for combo_name, result in results.items():
        detailed_results[combo_name] = {
            'combination_id': result.combination_id,
            'method': result.method.value,
            'indicators': [ind.to_dict() for ind in result.indicators],
            'performance': result.performance
        }
    
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(detailed_results, f, ensure_ascii=False, indent=2)
    
    print(f"✅ 详细结果已保存到: {json_file}")
    
    print("\n" + "=" * 80)
    print("🎯 指标组合框架测试完成!")
    print("=" * 80)
    print("\n下一步建议:")
    print("1. 使用真实股票数据替换示例数据")
    print("2. 尝试自定义指标组合")
    print("3. 优化组合参数")
    print("4. 将最佳组合集成到交易系统中")

if __name__ == "__main__":
    main()