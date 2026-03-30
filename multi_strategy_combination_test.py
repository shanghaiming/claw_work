#!/usr/bin/env python3
"""
多策略组合测试
从20个已解析策略中选择多种策略进行组合测试

测试策略组合:
1. 补偿移动平均策略 (优化后) - 趋势跟踪
2. 聚类分析策略 - 模式识别  
3. 动量策略 - 动量因子
4. 价量分析策略 - 价量关系
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import json
import warnings
warnings.filterwarnings('ignore')

# 添加路径
sys.path.append('/Users/chengming/.openclaw/workspace')

print("=" * 80)
print("🎯 多策略组合测试")
print("=" * 80)

# 导入必要模块
try:
    from combined_strategy_framework import (
        CombinedStrategy, CombinationMode, BaseStrategy,
        TradingSignal, SignalType
    )
    from real_combined_strategy_test import load_stock_data, BacktestEngine
    print("✅ 成功导入组合框架和回测模块")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 策略工厂 - 创建不同类型策略
class StrategyFactory:
    """策略工厂"""
    
    @staticmethod
    def create_strategy(strategy_type: str, optimized_params: Optional[Dict] = None) -> BaseStrategy:
        """创建策略实例"""
        if strategy_type == 'compensated_ma':
            return StrategyFactory._create_compensated_ma_strategy(optimized_params)
        elif strategy_type == 'cluster':
            return StrategyFactory._create_cluster_strategy(optimized_params)
        elif strategy_type == 'momentum':
            return StrategyFactory._create_momentum_strategy(optimized_params)
        elif strategy_type == 'price_volume':
            return StrategyFactory._create_price_volume_strategy(optimized_params)
        elif strategy_type == 'price_action':
            return StrategyFactory._create_price_action_strategy(optimized_params)
        else:
            raise ValueError(f"未知策略类型: {strategy_type}")
    
    @staticmethod
    def _create_compensated_ma_strategy(params: Optional[Dict] = None) -> BaseStrategy:
        """创建补偿移动平均策略"""
        class CompensatedMAStrategy(BaseStrategy):
            def __init__(self):
                super().__init__("compensated_ma_optimized")
                # 使用优化后的参数
                self.params = params or {
                    'window': 30,
                    'beta': 0.2,
                    'gamma': 0.1,
                    'decay_factor': 0.95
                }
                
            def generate_signals(self) -> List[TradingSignal]:
                if self.data is None:
                    return []
                
                print(f"🎯 {self.name} 生成信号...")
                
                signals = []
                data = self.data.copy()
                
                window = self.params['window']
                beta = self.params['beta']
                gamma = self.params['gamma']
                decay = self.params['decay_factor']
                
                # 计算补偿移动平均
                data['cma'] = self._calculate_cma(data['close'], window, beta, gamma, decay)
                
                for i in range(window, len(data)):
                    if pd.isna(data['cma'].iloc[i]):
                        continue
                        
                    timestamp = data.index[i]
                    price = data['close'].iloc[i]
                    cma = data['cma'].iloc[i]
                    
                    # 改进的信号逻辑
                    deviation = (price - cma) / cma
                    
                    # 价格显著低于CMA且开始回升（买入信号）
                    if deviation < -0.03 and i > 1:
                        prev_deviation = (data['close'].iloc[i-1] - data['cma'].iloc[i-1]) / data['cma'].iloc[i-1]
                        if deviation > prev_deviation:  # 偏离度在改善
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.BUY,
                                price=price,
                                confidence=0.7,
                                reason="price_recovering_from_below_cma",
                                source_strategy=self.name
                            ))
                    
                    # 价格显著高于CMA且开始回落（卖出信号）
                    elif deviation > 0.03 and i > 1:
                        prev_deviation = (data['close'].iloc[i-1] - data['cma'].iloc[i-1]) / data['cma'].iloc[i-1]
                        if deviation < prev_deviation:  # 偏离度在恶化
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.SELL,
                                price=price,
                                confidence=0.7,
                                reason="price_declining_from_above_cma",
                                source_strategy=self.name
                            ))
                
                print(f"   ✅ 生成 {len(signals)} 个信号")
                return signals
            
            def _calculate_cma(self, prices: pd.Series, window: int, beta: float, gamma: float, decay: float) -> pd.Series:
                """计算补偿移动平均"""
                cma = pd.Series(index=prices.index, dtype=float)
                
                for i in range(window, len(prices)):
                    window_prices = prices.iloc[i-window:i]
                    simple_ma = window_prices.mean()
                    
                    # 计算补偿因子
                    volatility = window_prices.std() / window_prices.mean()
                    compensation = beta * volatility + gamma * (1 - decay**(i-window))
                    
                    cma.iloc[i] = simple_ma * (1 + compensation)
                
                return cma
        
        return CompensatedMAStrategy()
    
    @staticmethod
    def _create_cluster_strategy(params: Optional[Dict] = None) -> BaseStrategy:
        """创建聚类分析策略"""
        class ClusterStrategy(BaseStrategy):
            def __init__(self):
                super().__init__("cluster_analysis")
                self.params = params or {
                    'window': 20,
                    'n_clusters': 3,
                    'threshold': 0.02
                }
                
            def generate_signals(self) -> List[TradingSignal]:
                if self.data is None:
                    return []
                
                print(f"🎯 {self.name} 生成信号...")
                
                signals = []
                data = self.data.copy()
                window = self.params['window']
                
                if len(data) > window * 2:
                    # 简化的聚类逻辑：价格在区间内震荡
                    for i in range(window, len(data)):
                        timestamp = data.index[i]
                        price = data['close'].iloc[i]
                        
                        # 计算近期价格区间
                        recent_prices = data['close'].iloc[i-window:i]
                        price_range = recent_prices.max() - recent_prices.min()
                        range_mid = (recent_prices.max() + recent_prices.min()) / 2
                        
                        # 价格接近区间顶部（卖出信号）
                        if abs(price - recent_prices.max()) / price_range < 0.1:
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.SELL,
                                price=price,
                                confidence=0.6,
                                reason="price_near_range_top",
                                source_strategy=self.name
                            ))
                        
                        # 价格接近区间底部（买入信号）
                        elif abs(price - recent_prices.min()) / price_range < 0.1:
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.BUY,
                                price=price,
                                confidence=0.6,
                                reason="price_near_range_bottom",
                                source_strategy=self.name
                            ))
                
                print(f"   ✅ 生成 {len(signals)} 个信号")
                return signals
        
        return ClusterStrategy()
    
    @staticmethod
    def _create_momentum_strategy(params: Optional[Dict] = None) -> BaseStrategy:
        """创建动量策略"""
        class MomentumStrategy(BaseStrategy):
            def __init__(self):
                super().__init__("momentum")
                self.params = params or {
                    'short_window': 5,
                    'long_window': 20,
                    'momentum_threshold': 0.02
                }
                
            def generate_signals(self) -> List[TradingSignal]:
                if self.data is None:
                    return []
                
                print(f"🎯 {self.name} 生成信号...")
                
                signals = []
                data = self.data.copy()
                short_window = self.params['short_window']
                long_window = self.params['long_window']
                
                if len(data) > long_window:
                    # 计算动量
                    data['momentum_short'] = data['close'].pct_change(periods=short_window)
                    data['momentum_long'] = data['close'].pct_change(periods=long_window)
                    
                    for i in range(long_window, len(data)):
                        if pd.isna(data['momentum_short'].iloc[i]) or pd.isna(data['momentum_long'].iloc[i]):
                            continue
                        
                        timestamp = data.index[i]
                        price = data['close'].iloc[i]
                        
                        short_momentum = data['momentum_short'].iloc[i]
                        long_momentum = data['momentum_long'].iloc[i]
                        
                        # 短期动量强劲且超过长期动量（买入）
                        if short_momentum > self.params['momentum_threshold'] and short_momentum > long_momentum:
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.BUY,
                                price=price,
                                confidence=0.65,
                                reason="strong_short_term_momentum",
                                source_strategy=self.name
                            ))
                        
                        # 短期动量负向且弱于长期动量（卖出）
                        elif short_momentum < -self.params['momentum_threshold'] and short_momentum < long_momentum:
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.SELL,
                                price=price,
                                confidence=0.65,
                                reason="weak_short_term_momentum",
                                source_strategy=self.name
                            ))
                
                print(f"   ✅ 生成 {len(signals)} 个信号")
                return signals
        
        return MomentumStrategy()
    
    @staticmethod
    def _create_price_volume_strategy(params: Optional[Dict] = None) -> BaseStrategy:
        """创建价量分析策略"""
        class PriceVolumeStrategy(BaseStrategy):
            def __init__(self):
                super().__init__("price_volume")
                self.params = params or {
                    'volume_window': 20,
                    'price_volume_threshold': 1.5
                }
                
            def generate_signals(self) -> List[TradingSignal]:
                if self.data is None or 'volume' not in self.data.columns:
                    return []
                
                print(f"🎯 {self.name} 生成信号...")
                
                signals = []
                data = self.data.copy()
                window = self.params['volume_window']
                
                if len(data) > window:
                    # 计算成交量均值和价格变化
                    data['volume_ma'] = data['volume'].rolling(window=window).mean()
                    data['price_change'] = data['close'].pct_change()
                    
                    for i in range(window, len(data)):
                        if pd.isna(data['volume_ma'].iloc[i]):
                            continue
                        
                        timestamp = data.index[i]
                        price = data['close'].iloc[i]
                        current_volume = data['volume'].iloc[i]
                        avg_volume = data['volume_ma'].iloc[i]
                        price_change = data['price_change'].iloc[i]
                        
                        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1
                        
                        # 放量上涨（买入信号）
                        if volume_ratio > self.params['price_volume_threshold'] and price_change > 0:
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.BUY,
                                price=price,
                                confidence=0.7,
                                reason="high_volume_price_increase",
                                source_strategy=self.name
                            ))
                        
                        # 放量下跌（卖出信号）
                        elif volume_ratio > self.params['price_volume_threshold'] and price_change < 0:
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.SELL,
                                price=price,
                                confidence=0.7,
                                reason="high_volume_price_decrease",
                                source_strategy=self.name
                            ))
                
                print(f"   ✅ 生成 {len(signals)} 个信号")
                return signals
        
        return PriceVolumeStrategy()
    
    @staticmethod
    def _create_price_action_strategy(params: Optional[Dict] = None) -> BaseStrategy:
        """创建价格行为策略"""
        class PriceActionStrategy(BaseStrategy):
            def __init__(self):
                super().__init__("price_action")
                self.params = params or {
                    'window': 20,
                    'breakout_threshold': 0.02
                }
                
            def generate_signals(self) -> List[TradingSignal]:
                if self.data is None:
                    return []
                
                print(f"🎯 {self.name} 生成信号...")
                
                signals = []
                data = self.data.copy()
                window = self.params['window']
                
                if len(data) > window:
                    for i in range(window, len(data)):
                        timestamp = data.index[i]
                        price = data['close'].iloc[i]
                        
                        # 近期价格区间
                        recent_high = data['high'].iloc[i-window:i].max()
                        recent_low = data['low'].iloc[i-window:i].min()
                        
                        # 突破近期高点（买入）
                        if price > recent_high * (1 + self.params['breakout_threshold']):
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.BUY,
                                price=price,
                                confidence=0.7,
                                reason="breakout_above_resistance",
                                source_strategy=self.name
                            ))
                        
                        # 跌破近期低点（卖出）
                        elif price < recent_low * (1 - self.params['breakout_threshold']):
                            signals.append(TradingSignal(
                                timestamp=timestamp,
                                signal_type=SignalType.SELL,
                                price=price,
                                confidence=0.7,
                                reason="breakdown_below_support",
                                source_strategy=self.name
                            ))
                
                print(f"   ✅ 生成 {len(signals)} 个信号")
                return signals
        
        return PriceActionStrategy()

# 策略组合测试
class MultiStrategyCombinationTester:
    """多策略组合测试器"""
    
    def __init__(self):
        self.strategy_factory = StrategyFactory()
        self.results = {}
        
    def test_strategy_combination(self, 
                                 strategy_types: List[str],
                                 combination_mode: CombinationMode,
                                 data: pd.DataFrame,
                                 weights: Optional[Dict[str, float]] = None) -> Dict[str, Any]:
        """测试策略组合"""
        print(f"\n🔧 测试策略组合: {strategy_types}")
        print(f"   组合模式: {combination_mode.value}")
        
        # 创建策略实例
        strategies = []
        for strategy_type in strategy_types:
            strategy = self.strategy_factory.create_strategy(strategy_type)
            strategies.append(strategy)
        
        # 创建组合策略
        if weights and combination_mode == CombinationMode.WEIGHTED_VOTE:
            combined = CombinedStrategy(
                strategies=strategies,
                combination_mode=combination_mode,
                weights=weights
            )
        else:
            combined = CombinedStrategy(
                strategies=strategies,
                combination_mode=combination_mode
            )
        
        # 初始化并生成信号
        combined.initialize(data)
        signals = combined.generate_combined_signals()
        
        if not signals:
            print("   ⚠️ 未生成组合信号")
            return {
                'strategy_types': strategy_types,
                'combination_mode': combination_mode.value,
                'signals_count': 0,
                'performance': None
            }
        
        # 运行回测
        backtest_engine = BacktestEngine(initial_capital=1000000)
        performance = backtest_engine.run_backtest(data, signals)
        
        print(f"   📊 信号数: {len(signals)}")
        print(f"   交易次数: {performance['trades_count']}")
        print(f"   总收益率: {performance['total_return']:.2%}")
        print(f"   胜率: {performance['win_rate']:.2%}")
        print(f"   最大回撤: {performance['max_drawdown']:.2%}")
        
        return {
            'strategy_types': strategy_types,
            'combination_mode': combination_mode.value,
            'signals_count': len(signals),
            'performance': performance
        }
    
    def run_comprehensive_test(self, data: pd.DataFrame):
        """运行全面的策略组合测试"""
        print("\n" + "=" * 60)
        print("🧪 开始全面的策略组合测试")
        print("=" * 60)
        
        # 定义测试组合
        test_combinations = [
            # 单策略
            (['compensated_ma'], CombinationMode.CONFIRMATION, None, "单策略-补偿移动平均"),
            
            # 双策略组合
            (['compensated_ma', 'cluster'], CombinationMode.CONFIRMATION, None, "双策略-补偿MA+聚类"),
            (['compensated_ma', 'momentum'], CombinationMode.WEIGHTED_VOTE, 
             {'compensated_ma_optimized': 0.6, 'momentum': 0.4}, "双策略-补偿MA+动量(加权)"),
            (['compensated_ma', 'price_volume'], CombinationMode.HIERARCHICAL_FILTER, None, "双策略-补偿MA+价量(分层)"),
            
            # 三策略组合
            (['compensated_ma', 'cluster', 'momentum'], CombinationMode.WEIGHTED_VOTE,
             {'compensated_ma_optimized': 0.4, 'cluster_analysis': 0.3, 'momentum': 0.3}, "三策略-补偿MA+聚类+动量"),
            (['compensated_ma', 'price_action', 'price_volume'], CombinationMode.CONFIRMATION, None, "三策略-补偿MA+价格行为+价量"),
            
            # 四策略组合
            (['compensated_ma', 'cluster', 'momentum', 'price_volume'], CombinationMode.WEIGHTED_VOTE,
             {'compensated_ma_optimized': 0.3, 'cluster_analysis': 0.25, 'momentum': 0.25, 'price_volume': 0.2}, "四策略-全组合")
        ]
        
        # 运行所有测试
        for strategy_types, combination_mode, weights, test_name in test_combinations:
            print(f"\n🔬 测试: {test_name}")
            
            result = self.test_strategy_combination(
                strategy_types=strategy_types,
                combination_mode=combination_mode,
                data=data,
                weights=weights
            )
            
            self.results[test_name] = result
        
        return self.results
    
    def analyze_results(self):
        """分析测试结果"""
        print("\n" + "=" * 60)
        print("📊 策略组合测试结果分析")
        print("=" * 60)
        
        # 收集有效结果
        valid_results = {}
        for test_name, result in self.results.items():
            if result['performance'] and result['performance']['trades_count'] > 0:
                valid_results[test_name] = result
        
        if not valid_results:
            print("⚠️ 没有有效的测试结果")
            return None
        
        # 生成比较表格
        print("\n📈 策略组合性能排名:")
        print("=" * 80)
        print(f"{'测试名称':<30} {'策略数量':<10} {'信号数':<8} {'交易次数':<8} {'总收益率':<12} {'胜率':<8} {'最大回撤':<10}")
        print("-" * 80)
        
        sorted_results = sorted(
            valid_results.items(),
            key=lambda x: x[1]['performance']['total_return'],
            reverse=True
        )
        
        for test_name, result in sorted_results:
            perf = result['performance']
            print(f"{test_name:<30} {len(result['strategy_types']):<10} "
                  f"{result['signals_count']:<8} {perf['trades_count']:<8} "
                  f"{perf['total_return']:>11.2%} {perf['win_rate']:>7.2%} {perf['max_drawdown']:>9.2%}")
        
        # 找出最佳组合
        best_test_name, best_result = sorted_results[0]
        best_perf = best_result['performance']
        
        print(f"\n🏆 最佳策略组合: {best_test_name}")
        print(f"   总收益率: {best_perf['total_return']:.2%}")
        print(f"   胜率: {best_perf['win_rate']:.2%}")
        print(f"   最大回撤: {best_perf['max_drawdown']:.2%}")
        print(f"   策略组合: {best_result['strategy_types']}")
        print(f"   组合模式: {best_result['combination_mode']}")
        
        # 保存详细结果
        output_data = {
            'analysis_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': len(self.results),
            'valid_tests': len(valid_results),
            'best_combination': {
                'name': best_test_name,
                'strategy_types': best_result['strategy_types'],
                'combination_mode': best_result['combination_mode'],
                'performance': best_perf
            },
            'all_results': self.results
        }
        
        output_path = "/Users/chengming/.openclaw/workspace/multi_strategy_combination_results.json"
        
        # 转换为可序列化格式
        serializable_results = {}
        for test_name, result in self.results.items():
            serializable_results[test_name] = {
                'strategy_types': result['strategy_types'],
                'combination_mode': result['combination_mode'],
                'signals_count': result['signals_count']
            }
            
            if result['performance']:
                serializable_results[test_name]['performance'] = {
                    'total_return': float(result['performance']['total_return']),
                    'sharpe_ratio': float(result['performance']['sharpe_ratio']),
                    'max_drawdown': float(result['performance']['max_drawdown']),
                    'win_rate': float(result['performance']['win_rate']),
                    'trades_count': result['performance']['trades_count']
                }
        
        output_data['all_results'] = serializable_results
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 详细结果保存到: {output_path}")
        
        return output_data

# 主函数
def main():
    print("\n" + "=" * 80)
    print("🎯 多策略组合测试主程序")
    print("=" * 80)
    
    # 加载数据
    print("\n📊 加载测试数据...")
    try:
        data = load_stock_data(stock_code="000001.SZ", timeframe="daily_data2", limit=300)
        print(f"✅ 数据加载成功: {len(data)} 行")
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return
    
    # 创建测试器
    tester = MultiStrategyCombinationTester()
    
    # 运行全面测试
    results = tester.run_comprehensive_test(data)
    
    # 分析结果
    if results:
        analysis = tester.analyze_results()
        
        if analysis:
            print("\n✅ 多策略组合测试完成!")
            print(f"✅ 测试组合数: {analysis['total_tests']}")
            print(f"✅ 有效结果数: {analysis['valid_tests']}")
            print(f"✅ 最佳组合: {analysis['best_combination']['name']}")
            
            # 更新任务管理器
            update_task_manager_subtask2(analysis)
    
    print("\n" + "=" * 80)
    print("🏁 多策略组合测试完成")

def update_task_manager_subtask2(analysis: Dict):
    """更新任务管理器子任务2状态"""
    try:
        import json
        import datetime
        
        task_manager_path = "/Users/chengming/.openclaw/workspace/quant_strategy_task_manager.json"
        
        with open(task_manager_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
        
        # 更新task_003的子任务2
        for task in data['current_task_queue']['tasks']:
            if task['task_id'] == 'task_003':
                for subtask in task.get('subtasks', []):
                    if subtask['subtask_id'] == 'task_003_2':
                        subtask['status'] = 'COMPLETED'
                        subtask['completion_time'] = current_time
                        subtask['results'] = {
                            'total_combinations_tested': analysis.get('total_tests', 0),
                            'valid_combinations': analysis.get('valid_tests', 0),
                            'best_combination': analysis.get('best_combination', {}),
                            'output_files': [
                                'multi_strategy_combination_test.py',
                                'multi_strategy_combination_results.json'
                            ]
                        }
                        break
                
                # 更新子任务3为进行中
                for subtask in task.get('subtasks', []):
                    if subtask['subtask_id'] == 'task_003_3':
                        subtask['status'] = 'IN_PROGRESS'
                        subtask['start_time'] = current_time
                        break
        
        # 更新最后时间
        data['task_system']['last_updated'] = current_time
        
        # 写入更新
        with open(task_manager_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 任务管理器更新: subtask_003_2 完成, subtask_003_3 开始")
        
    except Exception as e:
        print(f"⚠️ 更新任务管理器失败: {e}")

if __name__ == "__main__":
    main()