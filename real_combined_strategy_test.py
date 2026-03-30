#!/usr/bin/env python3
"""
实际组合策略测试
将价格行为策略与补偿移动平均策略进行组合测试

测试步骤:
1. 加载真实股票数据
2. 初始化价格行为策略和补偿移动平均策略
3. 使用组合策略框架进行4种模式测试
4. 运行回测比较不同组合模式的性能
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
print("🎯 实际组合策略测试 - 价格行为 + 补偿移动平均")
print("=" * 80)

# 导入组合策略框架
try:
    from combined_strategy_framework import (
        CombinedStrategy, CombinationMode, BaseStrategy,
        TradingSignal, SignalType
    )
    print("✅ 成功导入组合策略框架")
except ImportError as e:
    print(f"❌ 导入组合框架失败: {e}")
    sys.exit(1)

# 数据加载函数
def load_stock_data(stock_code: str = "000001.SZ", 
                   timeframe: str = "daily_data2",
                   limit: Optional[int] = None) -> pd.DataFrame:
    """加载股票数据"""
    data_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/data"
    file_path = os.path.join(data_dir, timeframe, f"{stock_code}.csv")
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    df = pd.read_csv(file_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.sort_values('trade_date', inplace=True)
    df.set_index('trade_date', inplace=True)
    
    # 重命名列
    column_mapping = {
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'vol': 'volume'
    }
    
    result_df = pd.DataFrame()
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            result_df[new_col] = df[old_col]
    
    if limit:
        result_df = result_df.iloc[:limit]
    
    print(f"📊 数据加载: {stock_code}, {len(result_df)} 行")
    print(f"   时间范围: {result_df.index.min()} 到 {result_df.index.max()}")
    
    return result_df

# 简化的价格行为策略（基于之前开发的适配器）
class SimplePriceActionStrategy(BaseStrategy):
    """简化价格行为策略"""
    
    def __init__(self):
        super().__init__("price_action")
        self.params = {
            'window': 20,
            'confidence_threshold': 0.6
        }
        
    def generate_signals(self) -> List[TradingSignal]:
        """生成价格行为信号"""
        if self.data is None:
            return []
        
        print(f"🎯 {self.name} 生成信号...")
        
        signals = []
        data = self.data.copy()
        
        # 简单实现：基于价格突破和移动平均
        if len(data) > 20:
            # 计算移动平均
            data['ma_20'] = data['close'].rolling(window=20).mean()
            data['ma_50'] = data['close'].rolling(window=50).mean()
            
            for i in range(50, len(data)):
                timestamp = data.index[i]
                price = data['close'].iloc[i]
                
                # 价格突破信号
                recent_high = data['high'].iloc[i-20:i].max()
                recent_low = data['low'].iloc[i-20:i].min()
                
                # 价格突破近期高点（买入信号）
                if price > recent_high and data['volume'].iloc[i] > data['volume'].iloc[i-20:i].mean():
                    signals.append(TradingSignal(
                        timestamp=timestamp,
                        signal_type=SignalType.BUY,
                        price=price,
                        confidence=0.7,
                        reason="price_breakout_high",
                        source_strategy=self.name
                    ))
                
                # 价格跌破近期低点（卖出信号）
                elif price < recent_low and data['volume'].iloc[i] > data['volume'].iloc[i-20:i].mean():
                    signals.append(TradingSignal(
                        timestamp=timestamp,
                        signal_type=SignalType.SELL,
                        price=price,
                        confidence=0.7,
                        reason="price_breakout_low",
                        source_strategy=self.name
                    ))
                
                # 移动平均金叉/死叉
                if i > 1:
                    prev_ma20 = data['ma_20'].iloc[i-1]
                    prev_ma50 = data['ma_50'].iloc[i-1]
                    curr_ma20 = data['ma_20'].iloc[i]
                    curr_ma50 = data['ma_50'].iloc[i]
                    
                    if prev_ma20 <= prev_ma50 and curr_ma20 > curr_ma50:
                        signals.append(TradingSignal(
                            timestamp=timestamp,
                            signal_type=SignalType.BUY,
                            price=price,
                            confidence=0.6,
                            reason="ma_golden_cross",
                            source_strategy=self.name
                        ))
                    elif prev_ma20 >= prev_ma50 and curr_ma20 < curr_ma50:
                        signals.append(TradingSignal(
                            timestamp=timestamp,
                            signal_type=SignalType.SELL,
                            price=price,
                            confidence=0.6,
                            reason="ma_death_cross",
                            source_strategy=self.name
                        ))
        
        print(f"   生成 {len(signals)} 个价格行为信号")
        return signals

# 补偿移动平均策略（基于深度解析的适配器）
class CompensatedMAStrategy(BaseStrategy):
    """补偿移动平均策略"""
    
    def __init__(self):
        super().__init__("compensated_ma")
        self.params = {
            'window': 20,
            'beta': 0.3,
            'gamma': 0.2,
            'decay_factor': 0.95
        }
        
    def generate_signals(self) -> List[TradingSignal]:
        """生成补偿移动平均信号"""
        if self.data is None:
            return []
        
        print(f"🎯 {self.name} 生成信号...")
        
        signals = []
        data = self.data.copy()
        
        # 实现补偿移动平均逻辑
        if len(data) > self.params['window']:
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
                
                # 价格与CMA的偏离度
                deviation = abs(price - cma) / cma
                
                # 价格回归CMA信号
                if deviation > 0.05:  # 5%偏离
                    if price > cma:
                        # 价格高于CMA，预期回归（卖出信号）
                        signals.append(TradingSignal(
                            timestamp=timestamp,
                            signal_type=SignalType.SELL,
                            price=price,
                            confidence=0.6,
                            reason="price_above_cma",
                            source_strategy=self.name
                        ))
                    else:
                        # 价格低于CMA，预期回归（买入信号）
                        signals.append(TradingSignal(
                            timestamp=timestamp,
                            signal_type=SignalType.BUY,
                            price=price,
                            confidence=0.6,
                            reason="price_below_cma",
                            source_strategy=self.name
                        ))
        
        print(f"   生成 {len(signals)} 个补偿移动平均信号")
        return signals
    
    def _calculate_cma(self, prices: pd.Series, window: int, beta: float, gamma: float, decay: float) -> pd.Series:
        """计算补偿移动平均"""
        cma = pd.Series(index=prices.index, dtype=float)
        
        for i in range(window, len(prices)):
            window_prices = prices.iloc[i-window:i]
            simple_ma = window_prices.mean()
            
            # 计算补偿因子（基于价格波动）
            volatility = window_prices.std() / window_prices.mean()
            compensation = beta * volatility + gamma * (1 - decay**(i-window))
            
            # 补偿移动平均
            cma.iloc[i] = simple_ma * (1 + compensation)
        
        return cma

# 回测引擎
class BacktestEngine:
    """简单回测引擎"""
    
    def __init__(self, initial_capital: float = 1000000):
        self.initial_capital = initial_capital
        
    def run_backtest(self, data: pd.DataFrame, signals: List[TradingSignal]) -> Dict[str, Any]:
        """运行回测"""
        if not signals:
            return {
                'total_return': 0.0,
                'sharpe_ratio': 0.0,
                'max_drawdown': 0.0,
                'win_rate': 0.0,
                'trades_count': 0
            }
        
        capital = self.initial_capital
        position = 0
        entry_price = 0
        trades = []
        equity_curve = []
        
        # 按时间排序信号
        sorted_signals = sorted(signals, key=lambda x: x.timestamp)
        
        for signal in sorted_signals:
            current_price = signal.price
            equity_curve.append({
                'timestamp': signal.timestamp,
                'capital': capital,
                'position': position,
                'price': current_price
            })
            
            if signal.signal_type == SignalType.BUY and position == 0:
                # 买入
                position = 1
                entry_price = current_price
                trades.append({
                    'timestamp': signal.timestamp,
                    'action': 'buy',
                    'price': entry_price,
                    'reason': signal.reason
                })
                
            elif signal.signal_type == SignalType.SELL and position == 1:
                # 卖出
                position = 0
                exit_price = current_price
                
                # 计算收益
                return_pct = (exit_price - entry_price) / entry_price
                capital *= (1 + return_pct)
                
                trades.append({
                    'timestamp': signal.timestamp,
                    'action': 'sell',
                    'price': exit_price,
                    'return': return_pct,
                    'reason': signal.reason
                })
        
        # 计算绩效指标
        if trades:
            sell_trades = [t for t in trades if t['action'] == 'sell']
            if sell_trades:
                returns = [t['return'] for t in sell_trades]
                total_return = (capital - self.initial_capital) / self.initial_capital
                avg_return = np.mean(returns) if returns else 0
                win_trades = [t for t in sell_trades if t['return'] > 0]
                win_rate = len(win_trades) / len(sell_trades) if sell_trades else 0
                
                # 计算夏普比率（简化）
                sharpe_ratio = avg_return / np.std(returns) if len(returns) > 1 and np.std(returns) > 0 else 0
                
                # 计算最大回撤（简化）
                equity_values = [e['capital'] for e in equity_curve]
                if equity_values:
                    peak = equity_values[0]
                    max_dd = 0
                    for value in equity_values:
                        if value > peak:
                            peak = value
                        dd = (peak - value) / peak
                        if dd > max_dd:
                            max_dd = dd
                else:
                    max_dd = 0
                
                return {
                    'total_return': total_return,
                    'sharpe_ratio': sharpe_ratio,
                    'max_drawdown': max_dd,
                    'win_rate': win_rate,
                    'trades_count': len(sell_trades),
                    'avg_return': avg_return,
                    'final_capital': capital,
                    'trade_details': trades[:10]  # 只返回前10个交易详情
                }
        
        return {
            'total_return': 0.0,
            'sharpe_ratio': 0.0,
            'max_drawdown': 0.0,
            'win_rate': 0.0,
            'trades_count': 0
        }

# 主测试函数
def test_all_combination_modes():
    """测试所有组合模式"""
    print("\n🧪 开始实际组合策略测试...")
    
    # 1. 加载数据
    try:
        df = load_stock_data(stock_code="000001.SZ", timeframe="daily_data2", limit=200)
    except Exception as e:
        print(f"❌ 数据加载失败: {e}")
        return None
    
    # 2. 创建策略实例
    price_action_strategy = SimplePriceActionStrategy()
    compensated_ma_strategy = CompensatedMAStrategy()
    
    # 3. 测试不同组合模式
    combination_modes = [
        (CombinationMode.CONFIRMATION, "确认模式"),
        (CombinationMode.WEIGHTED_VOTE, "加权投票模式"),
        (CombinationMode.HIERARCHICAL_FILTER, "分层过滤模式"),
        (CombinationMode.SIGNAL_ENHANCEMENT, "信号增强模式")
    ]
    
    # 权重配置（加权投票模式使用）
    weights = {
        "price_action": 0.6,
        "compensated_ma": 0.4
    }
    
    results = {}
    backtest_engine = BacktestEngine(initial_capital=1000000)
    
    for mode, mode_name in combination_modes:
        print(f"\n🔧 测试: {mode_name}")
        
        # 创建组合策略
        if mode == CombinationMode.WEIGHTED_VOTE:
            combined = CombinedStrategy(
                strategies=[price_action_strategy, compensated_ma_strategy],
                combination_mode=mode,
                weights=weights
            )
        else:
            combined = CombinedStrategy(
                strategies=[price_action_strategy, compensated_ma_strategy],
                combination_mode=mode
            )
        
        # 初始化策略
        combined.initialize(df)
        
        # 生成组合信号
        signals = combined.generate_combined_signals()
        
        if not signals:
            print(f"   ⚠️ 未生成组合信号")
            results[mode_name] = {
                'signals_count': 0,
                'performance': None
            }
            continue
        
        # 运行回测
        performance = backtest_engine.run_backtest(df, signals)
        
        print(f"   📊 信号数: {len(signals)}")
        print(f"   交易次数: {performance['trades_count']}")
        print(f"   总收益率: {performance['total_return']:.2%}")
        print(f"   胜率: {performance['win_rate']:.2%}")
        print(f"   最大回撤: {performance['max_drawdown']:.2%}")
        
        results[mode_name] = {
            'signals_count': len(signals),
            'performance': performance
        }
    
    return results

# 单策略基准测试
def test_individual_strategies():
    """测试单个策略性能（基准）"""
    print("\n📈 测试单个策略性能（基准）...")
    
    # 加载数据
    df = load_stock_data(stock_code="000001.SZ", timeframe="daily_data2", limit=200)
    
    strategies = [
        ("价格行为策略", SimplePriceActionStrategy()),
        ("补偿移动平均策略", CompensatedMAStrategy())
    ]
    
    results = {}
    backtest_engine = BacktestEngine(initial_capital=1000000)
    
    for strategy_name, strategy in strategies:
        print(f"\n🧪 测试: {strategy_name}")
        
        strategy.initialize(df)
        signals = strategy.generate_signals()
        
        if signals:
            performance = backtest_engine.run_backtest(df, signals)
            
            print(f"   信号数: {len(signals)}")
            print(f"   交易次数: {performance['trades_count']}")
            print(f"   总收益率: {performance['total_return']:.2%}")
            print(f"   胜率: {performance['win_rate']:.2%}")
            
            results[strategy_name] = {
                'signals_count': len(signals),
                'performance': performance
            }
        else:
            print(f"   ⚠️ 未生成信号")
            results[strategy_name] = {
                'signals_count': 0,
                'performance': None
            }
    
    return results

# 结果分析和报告
def analyze_results(individual_results: Dict, combined_results: Dict):
    """分析并生成报告"""
    print("\n" + "=" * 80)
    print("📊 组合策略测试结果分析")
    print("=" * 80)
    
    # 收集所有结果
    all_results = {}
    all_results.update(individual_results)
    all_results.update(combined_results)
    
    # 生成比较表格
    print("\n📈 策略性能比较:")
    print("=" * 60)
    print(f"{'策略名称':<20} {'信号数':<8} {'交易次数':<8} {'总收益率':<10} {'胜率':<8} {'最大回撤':<10}")
    print("-" * 60)
    
    for strategy_name, result in all_results.items():
        perf = result.get('performance')
        if perf:
            print(f"{strategy_name:<20} {result['signals_count']:<8} {perf['trades_count']:<8} "
                  f"{perf['total_return']:>9.2%} {perf['win_rate']:>7.2%} {perf['max_drawdown']:>9.2%}")
        else:
            print(f"{strategy_name:<20} {result['signals_count']:<8} {'N/A':<8} {'N/A':<10} {'N/A':<8} {'N/A':<10}")
    
    # 找出最佳策略
    best_strategy = None
    best_return = -float('inf')
    
    for strategy_name, result in all_results.items():
        perf = result.get('performance')
        if perf and perf['total_return'] > best_return and perf['trades_count'] > 0:
            best_return = perf['total_return']
            best_strategy = strategy_name
    
    if best_strategy:
        print(f"\n🏆 最佳策略: {best_strategy} (收益率: {best_return:.2%})")
    
    # 保存详细结果
    output_data = {
        'analysis_time': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
        'stock_code': '000001.SZ',
        'data_period': '200个交易日',
        'individual_strategies': individual_results,
        'combined_strategies': combined_results,
        'best_strategy': best_strategy if best_strategy else None,
        'best_return': best_return if best_strategy else None
    }
    
    output_path = "/Users/chengming/.openclaw/workspace/combined_strategy_test_results.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 详细结果保存到: {output_path}")
    
    return output_data

# 主函数
def main():
    print("\n" + "=" * 80)
    print("🎯 实际组合策略测试主程序")
    print("=" * 80)
    
    # 测试单个策略（基准）
    individual_results = test_individual_strategies()
    
    # 测试组合策略
    combined_results = test_all_combination_modes()
    
    if combined_results:
        # 分析结果
        final_results = analyze_results(individual_results, combined_results)
        
        print("\n✅ 实际组合策略测试完成!")
        print(f"✅ 单个策略测试: {len(individual_results)} 个")
        print(f"✅ 组合模式测试: {len(combined_results)} 种")
        print(f"✅ 性能比较分析: 完成")
        
        # 输出建议
        best_strategy = final_results.get('best_strategy')
        if best_strategy:
            print(f"\n💡 建议: 考虑使用 {best_strategy} 进行进一步优化和测试")
    else:
        print("\n⚠️ 组合策略测试未完成")
    
    print("\n" + "=" * 80)
    print("🏁 程序结束")

if __name__ == "__main__":
    main()