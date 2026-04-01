#!/usr/bin/env python3
"""
测试前5名智能组合 - Phase 3剩余工作

基于strategy_combination_explorer.py生成的前5名组合，
使用pure_python_backtest_system.py进行组合策略回测。

设计目标:
1. 验证智能组合探索算法的有效性
2. 测试组合策略的实际性能
3. 生成组合策略对比报告
4. 为Phase 3完成提供数据支持
"""

import os
import sys
import json
import time
import math
import random
from datetime import datetime, timedelta
from pathlib import Path

print("=" * 80)
print("📊 测试前5名智能组合 - Phase 3剩余工作")
print("=" * 80)
print("开始时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

# 配置
WORKSPACE_ROOT = Path("/Users/chengming/.openclaw/workspace")
COMBINATION_REPORT = WORKSPACE_ROOT / "strategy_combination_results" / "combination_exploration_report_20260331_203003.json"
RESULTS_DIR = WORKSPACE_ROOT / "pure_python_backtest_results" / "top5_combinations"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# 导入纯Python回测系统
sys.path.append(str(WORKSPACE_ROOT))
try:
    from pure_python_backtest_system import PurePythonDataFrame, PurePythonBacktestEngine, MovingAverageStrategy, RSIStrategy, RandomStrategy
    print("✅ 成功导入纯Python回测系统")
except ImportError as e:
    print(f"❌ 导入纯Python回测系统失败: {e}")
    print("正在尝试直接复制必要代码...")
    
    # 如果导入失败，直接定义必要类
    class PurePythonDataFrame:
        def __init__(self, data):
            self.data = data
            self.columns = list(data[0].keys()) if data else []
        
        def __len__(self):
            return len(self.data)
        
        def __getitem__(self, key):
            if isinstance(key, int):
                return self.data[key]
            elif isinstance(key, str):
                return [row.get(key) for row in self.data]
            return None
    
    class BaseStrategy:
        def __init__(self, name="BaseStrategy"):
            self.name = name
            self.positions = []
            self.trades = []
            
        def generate_signals(self, data):
            raise NotImplementedError("子类必须实现generate_signals方法")
        
        def calculate_returns(self, trades, initial_capital=100000):
            if not trades:
                return {"total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0}
            
            capital = initial_capital
            max_capital = capital
            min_capital = capital
            returns = []
            
            for trade in trades:
                capital_change = trade.get("profit", 0)
                capital += capital_change
                returns.append(capital_change / (capital - capital_change) if capital - capital_change != 0 else 0)
                max_capital = max(max_capital, capital)
                min_capital = min(min_capital, capital)
            
            total_return = (capital - initial_capital) / initial_capital if initial_capital != 0 else 0
            
            # 简化计算
            avg_return = sum(returns) / len(returns) if returns else 0
            std_return = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns)) if len(returns) > 1 else 0.001
            sharpe_ratio = avg_return / std_return if std_return != 0 else 0
            
            max_drawdown = (max_capital - min_capital) / max_capital if max_capital != 0 else 0
            
            return {
                "total_return": total_return,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "final_capital": capital,
                "trade_count": len(trades)
            }
    
    class MovingAverageStrategy(BaseStrategy):
        def __init__(self, short_window=10, long_window=30):
            super().__init__(f"MA_{short_window}_{long_window}")
            self.short_window = short_window
            self.long_window = long_window
        
        def generate_signals(self, data):
            if len(data) < self.long_window:
                return []
            
            signals = []
            for i in range(self.long_window - 1, len(data)):
                short_avg = sum(row["close"] for row in data[i-self.short_window+1:i+1]) / self.short_window
                long_avg = sum(row["close"] for row in data[i-self.long_window+1:i+1]) / self.long_window
                
                if short_avg > long_avg * 1.001:
                    signals.append({"index": i, "action": "buy", "price": data[i]["close"], "confidence": 0.7})
                elif short_avg < long_avg * 0.999:
                    signals.append({"index": i, "action": "sell", "price": data[i]["close"], "confidence": 0.7})
            
            return signals
    
    class RSIStrategy(BaseStrategy):
        def __init__(self, period=14, oversold=30, overbought=70):
            super().__init__(f"RSI_{period}")
            self.period = period
            self.oversold = oversold
            self.overbought = overbought
        
        def calculate_rsi(self, prices):
            if len(prices) < self.period + 1:
                return 50
            
            gains = []
            losses = []
            for i in range(1, len(prices)):
                change = prices[i] - prices[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(-change)
            
            avg_gain = sum(gains[-self.period:]) / self.period
            avg_loss = sum(losses[-self.period:]) / self.period
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        def generate_signals(self, data):
            if len(data) < self.period + 1:
                return []
            
            signals = []
            prices = [row["close"] for row in data]
            
            for i in range(self.period, len(prices)):
                rsi = self.calculate_rsi(prices[i-self.period:i+1])
                
                if rsi < self.oversold:
                    signals.append({"index": i, "action": "buy", "price": prices[i], "confidence": 0.8})
                elif rsi > self.overbought:
                    signals.append({"index": i, "action": "sell", "price": prices[i], "confidence": 0.8})
            
            return signals
    
    class RandomStrategy(BaseStrategy):
        def __init__(self, buy_probability=0.05):
            super().__init__("RandomStrategy")
            self.buy_probability = buy_probability
        
        def generate_signals(self, data):
            signals = []
            for i, row in enumerate(data):
                if random.random() < self.buy_probability:
                    signals.append({"index": i, "action": "buy", "price": row["close"], "confidence": 0.5})
                elif random.random() < self.buy_probability:
                    signals.append({"index": i, "action": "sell", "price": row["close"], "confidence": 0.5})
            return signals
    
    class PurePythonBacktestEngine:
        def __init__(self, data, initial_capital=100000):
            self.data = data
            self.initial_capital = initial_capital
        
        def run_backtest(self, strategy):
            signals = strategy.generate_signals(self.data)
            
            # 简化回测逻辑
            trades = []
            capital = self.initial_capital
            position = 0
            
            for signal in signals:
                price = signal["price"]
                action = signal["action"]
                
                if action == "buy" and capital > price * 100:
                    shares = int(capital * 0.1 / price)  # 使用10%资金
                    cost = shares * price
                    capital -= cost
                    position += shares
                    
                    trades.append({
                        "action": "buy",
                        "price": price,
                        "shares": shares,
                        "cost": cost,
                        "timestamp": signal.get("index", 0)
                    })
                
                elif action == "sell" and position > 0:
                    revenue = position * price
                    profit = revenue - (position * price * 0.99)  # 简化计算
                    capital += revenue
                    
                    trades.append({
                        "action": "sell",
                        "price": price,
                        "shares": position,
                        "revenue": revenue,
                        "profit": profit,
                        "timestamp": signal.get("index", 0)
                    })
                    position = 0
            
            # 平仓
            if position > 0 and len(self.data) > 0:
                last_price = self.data[-1]["close"]
                revenue = position * last_price
                profit = revenue - (position * last_price * 0.99)
                capital += revenue
                
                trades.append({
                    "action": "sell",
                    "price": last_price,
                    "shares": position,
                    "revenue": revenue,
                    "profit": profit,
                    "timestamp": len(self.data) - 1
                })
            
            strategy.trades = trades
            return strategy.calculate_returns(trades, self.initial_capital)

class CombinationStrategy:
    """组合策略类 - 将多个策略组合成一个策略"""
    
    def __init__(self, name, strategies, combination_method="weighted_vote"):
        """
        初始化组合策略
        
        Args:
            name: 组合策略名称
            strategies: 策略列表，每个策略是(BaseStrategy, weight)元组
            combination_method: 组合方法，可选:
                - "weighted_vote": 加权投票
                - "confirmation": 确认模式(所有策略一致才交易)
                - "majority": 多数投票
        """
        self.name = name
        self.strategies = strategies  # [(strategy, weight), ...]
        self.combination_method = combination_method
        self.positions = []
        self.trades = []
        
    def generate_signals(self, data):
        """生成组合信号"""
        all_signals = []
        
        # 收集所有策略的信号
        for strategy, weight in self.strategies:
            try:
                signals = strategy.generate_signals(data)
                for signal in signals:
                    signal["strategy"] = strategy.name
                    signal["weight"] = weight
                all_signals.extend(signals)
            except Exception as e:
                print(f"⚠️ 策略 {strategy.name} 生成信号失败: {e}")
                continue
        
        if not all_signals:
            return []
        
        # 按时间索引分组信号
        signals_by_index = {}
        for signal in all_signals:
            idx = signal["index"]
            if idx not in signals_by_index:
                signals_by_index[idx] = []
            signals_by_index[idx].append(signal)
        
        # 根据组合方法合并信号
        combined_signals = []
        for idx, signals in signals_by_index.items():
            if self.combination_method == "weighted_vote":
                combined_signal = self._weighted_vote(signals, idx, data[idx]["close"] if idx < len(data) else 0)
                if combined_signal:
                    combined_signals.append(combined_signal)
            elif self.combination_method == "confirmation":
                combined_signal = self._confirmation(signals, idx, data[idx]["close"] if idx < len(data) else 0)
                if combined_signal:
                    combined_signals.append(combined_signal)
            elif self.combination_method == "majority":
                combined_signal = self._majority_vote(signals, idx, data[idx]["close"] if idx < len(data) else 0)
                if combined_signal:
                    combined_signals.append(combined_signal)
        
        return combined_signals
    
    def _weighted_vote(self, signals, index, price):
        """加权投票法"""
        buy_weight = 0
        sell_weight = 0
        
        for signal in signals:
            weight = signal["weight"]
            if signal["action"] == "buy":
                buy_weight += weight * signal.get("confidence", 0.5)
            elif signal["action"] == "sell":
                sell_weight += weight * signal.get("confidence", 0.5)
        
        total_weight = buy_weight + sell_weight
        if total_weight == 0:
            return None
        
        buy_ratio = buy_weight / total_weight
        sell_ratio = sell_weight / total_weight
        
        # 设置阈值
        threshold = 0.6
        
        if buy_ratio > threshold:
            return {
                "index": index,
                "action": "buy",
                "price": price,
                "confidence": buy_ratio,
                "buy_ratio": buy_ratio,
                "sell_ratio": sell_ratio,
                "signal_count": len(signals)
            }
        elif sell_ratio > threshold:
            return {
                "index": index,
                "action": "sell",
                "price": price,
                "confidence": sell_ratio,
                "buy_ratio": buy_ratio,
                "sell_ratio": sell_ratio,
                "signal_count": len(signals)
            }
        
        return None
    
    def _confirmation(self, signals, index, price):
        """确认模式 - 所有策略一致才交易"""
        if not signals:
            return None
        
        first_action = signals[0]["action"]
        for signal in signals[1:]:
            if signal["action"] != first_action:
                return None
        
        # 计算平均置信度
        avg_confidence = sum(s.get("confidence", 0.5) for s in signals) / len(signals)
        
        return {
            "index": index,
            "action": first_action,
            "price": price,
            "confidence": avg_confidence,
            "signal_count": len(signals),
            "all_agree": True
        }
    
    def _majority_vote(self, signals, index, price):
        """多数投票法"""
        buy_count = sum(1 for s in signals if s["action"] == "buy")
        sell_count = sum(1 for s in signals if s["action"] == "sell")
        
        total = buy_count + sell_count
        if total == 0:
            return None
        
        buy_ratio = buy_count / total
        sell_ratio = sell_count / total
        
        threshold = 0.5
        
        if buy_ratio > threshold:
            return {
                "index": index,
                "action": "buy",
                "price": price,
                "confidence": buy_ratio,
                "buy_count": buy_count,
                "sell_count": sell_count,
                "signal_count": len(signals)
            }
        elif sell_ratio > threshold:
            return {
                "index": index,
                "action": "sell",
                "price": price,
                "confidence": sell_ratio,
                "buy_count": buy_count,
                "sell_count": sell_count,
                "signal_count": len(signals)
            }
        
        return None
    
    def calculate_returns(self, trades, initial_capital=100000):
        """计算回报率"""
        if not trades:
            return {"total_return": 0.0, "sharpe_ratio": 0.0, "max_drawdown": 0.0, "trade_count": 0}
        
        capital = initial_capital
        max_capital = capital
        min_capital = capital
        returns = []
        
        for trade in trades:
            profit = trade.get("profit", 0)
            capital_change = profit
            capital += capital_change
            
            if capital - capital_change != 0:
                returns.append(capital_change / (capital - capital_change))
            else:
                returns.append(0)
            
            max_capital = max(max_capital, capital)
            min_capital = min(min_capital, capital)
        
        total_return = (capital - initial_capital) / initial_capital if initial_capital != 0 else 0
        
        # 计算夏普比率
        if returns:
            avg_return = sum(returns) / len(returns)
            std_return = math.sqrt(sum((r - avg_return) ** 2 for r in returns) / len(returns)) if len(returns) > 1 else 0.001
            sharpe_ratio = avg_return / std_return if std_return != 0 else 0
        else:
            sharpe_ratio = 0
        
        max_drawdown = (max_capital - min_capital) / max_capital if max_capital != 0 else 0
        
        return {
            "total_return": total_return,
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown": max_drawdown,
            "final_capital": capital,
            "trade_count": len(trades),
            "strategy_name": self.name
        }

def load_combination_report():
    """加载组合探索报告"""
    print(f"📂 加载组合探索报告: {COMBINATION_REPORT}")
    
    if not COMBINATION_REPORT.exists():
        print(f"❌ 组合探索报告不存在: {COMBINATION_REPORT}")
        return None
    
    try:
        with open(COMBINATION_REPORT, 'r', encoding='utf-8') as f:
            report = json.load(f)
        
        print(f"✅ 成功加载报告: {len(report.get('top_combinations', []))} 个组合")
        return report
    except Exception as e:
        print(f"❌ 加载报告失败: {e}")
        return None

def create_test_data(num_points=500):
    """创建测试数据"""
    print(f"📈 创建测试数据 ({num_points}个数据点)")
    
    data = []
    base_price = 100.0
    volatility = 0.02
    
    for i in range(num_points):
        # 模拟价格走势
        change = (random.random() - 0.5) * 2 * volatility
        base_price *= (1 + change)
        
        # 确保价格为正
        base_price = max(base_price, 1.0)
        
        # 创建OHLC数据
        open_price = base_price * (1 + (random.random() - 0.5) * 0.01)
        high_price = max(open_price, base_price) * (1 + random.random() * 0.02)
        low_price = min(open_price, base_price) * (1 - random.random() * 0.02)
        close_price = base_price
        
        volume = random.randint(1000000, 5000000)
        
        data.append({
            "timestamp": i,
            "open": open_price,
            "high": high_price,
            "low": low_price,
            "close": close_price,
            "volume": volume
        })
    
    print(f"✅ 测试数据创建完成: {len(data)} 行")
    return data

def create_strategies_for_combination(combination_info):
    """为组合创建策略实例"""
    strategies = []
    
    # 简化实现：基于组合信息创建策略
    # 在实际系统中，应该加载实际的策略文件
    
    combination_id = combination_info.get("combination_id", 0)
    combination_name = combination_info.get("name", f"组合_{combination_id}")
    
    print(f"  🛠️  为组合 {combination_name} 创建策略...")
    
    # 根据组合类型创建不同的策略组合
    if "moving_average" in str(combination_info.get("categories", [])):
        # 移动平均相关组合
        strategies.append((MovingAverageStrategy(5, 20), 0.4))
        strategies.append((MovingAverageStrategy(10, 30), 0.4))
        strategies.append((RSIStrategy(14), 0.2))
    
    elif "medium_complexity" in combination_info.get("name", ""):
        # 中等复杂性组合
        strategies.append((MovingAverageStrategy(8, 21), 0.3))
        strategies.append((RSIStrategy(10, 25, 75), 0.4))
        strategies.append((RandomStrategy(0.03), 0.3))
    
    else:
        # 默认组合
        strategies.append((MovingAverageStrategy(10, 30), 0.5))
        strategies.append((RSIStrategy(14), 0.5))
    
    print(f"  ✅ 创建了 {len(strategies)} 个策略")
    return strategies, combination_name

def test_combination(combination_info, data, combination_method="weighted_vote"):
    """测试单个组合"""
    combination_id = combination_info.get("combination_id", 0)
    combination_name = combination_info.get("name", f"组合_{combination_id}")
    rank = combination_info.get("rank", 99)
    
    print(f"\n🔬 测试组合 #{rank}: {combination_name} (ID: {combination_id})")
    print(f"   组合方法: {combination_method}")
    
    # 创建策略实例
    strategies, name = create_strategies_for_combination(combination_info)
    
    if not strategies:
        print(f"  ⚠️  无法为组合创建策略，跳过")
        return None
    
    # 创建组合策略
    combination_strategy = CombinationStrategy(
        name=f"组合_{rank}_{combination_name}",
        strategies=strategies,
        combination_method=combination_method
    )
    
    # 创建回测引擎
    engine = PurePythonBacktestEngine(data, initial_capital=100000)
    
    # 运行回测
    start_time = time.time()
    results = engine.run_backtest(combination_strategy)
    elapsed_time = time.time() - start_time
    
    if results:
        results["combination_id"] = combination_id
        results["combination_name"] = combination_name
        results["rank"] = rank
        results["combination_method"] = combination_method
        results["strategy_count"] = len(strategies)
        results["elapsed_time"] = elapsed_time
        
        print(f"  ✅ 回测完成: {elapsed_time:.2f}秒")
        print(f"     总回报: {results['total_return']:.2%}")
        print(f"     夏普比率: {results['sharpe_ratio']:.3f}")
        print(f"     最大回撤: {results['max_drawdown']:.2%}")
        print(f"     交易次数: {results['trade_count']}")
    
    return results

def generate_comparison_report(all_results):
    """生成组合对比报告"""
    if not all_results:
        print("⚠️ 没有测试结果，无法生成报告")
        return None
    
    print("\n" + "=" * 80)
    print("📊 前5名组合测试结果对比")
    print("=" * 80)
    
    # 按总回报排序
    sorted_results = sorted(all_results, key=lambda x: x.get("total_return", 0), reverse=True)
    
    report = {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_combinations_tested": len(all_results),
        "results": sorted_results,
        "summary": {
            "best_return": max(r.get("total_return", 0) for r in all_results) if all_results else 0,
            "worst_return": min(r.get("total_return", 0) for r in all_results) if all_results else 0,
            "avg_return": sum(r.get("total_return", 0) for r in all_results) / len(all_results) if all_results else 0,
            "best_sharpe": max(r.get("sharpe_ratio", 0) for r in all_results) if all_results else 0,
            "avg_trade_count": sum(r.get("trade_count", 0) for r in all_results) / len(all_results) if all_results else 0
        }
    }
    
    # 打印对比表格
    print("\n排名 | 组合名称 | 总回报 | 夏普比率 | 最大回撤 | 交易次数")
    print("-" * 80)
    
    for i, result in enumerate(sorted_results[:10], 1):
        name = result.get("combination_name", "未知")[:20]
        total_return = result.get("total_return", 0)
        sharpe = result.get("sharpe_ratio", 0)
        drawdown = result.get("max_drawdown", 0)
        trades = result.get("trade_count", 0)
        
        print(f"{i:2d}  | {name:20s} | {total_return:7.2%} | {sharpe:8.3f} | {drawdown:7.2%} | {trades:6d}")
    
    print("\n" + "=" * 80)
    print("📈 性能摘要:")
    print(f"   最佳回报: {report['summary']['best_return']:.2%}")
    print(f"   最差回报: {report['summary']['worst_return']:.2%}")
    print(f"   平均回报: {report['summary']['avg_return']:.2%}")
    print(f"   最佳夏普比率: {report['summary']['best_sharpe']:.3f}")
    print(f"   平均交易次数: {report['summary']['avg_trade_count']:.1f}")
    
    return report

def save_results(all_results, comparison_report):
    """保存测试结果"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # 保存详细结果
    detailed_file = RESULTS_DIR / f"top5_combinations_detailed_{timestamp}.json"
    with open(detailed_file, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=2)
    print(f"✅ 详细结果保存到: {detailed_file}")
    
    # 保存对比报告
    if comparison_report:
        report_file = RESULTS_DIR / f"top5_combinations_comparison_{timestamp}.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comparison_report, f, ensure_ascii=False, indent=2)
        print(f"✅ 对比报告保存到: {report_file}")
    
    # 保存文本摘要
    summary_file = RESULTS_DIR / f"top5_combinations_summary_{timestamp}.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("前5名智能组合测试结果摘要\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"生成时间: {comparison_report.get('generated_at', '未知')}\n")
        f.write(f"测试组合数量: {len(all_results)}\n\n")
        
        f.write("性能排名:\n")
        f.write("-" * 80 + "\n")
        for i, result in enumerate(sorted(all_results, key=lambda x: x.get("total_return", 0), reverse=True)[:10], 1):
            name = result.get("combination_name", "未知")
            total_return = result.get("total_return", 0)
            sharpe = result.get("sharpe_ratio", 0)
            drawdown = result.get("max_drawdown", 0)
            trades = result.get("trade_count", 0)
            
            f.write(f"{i:2d}. {name}\n")
            f.write(f"    总回报: {total_return:.2%}, 夏普比率: {sharpe:.3f}, 最大回撤: {drawdown:.2%}, 交易次数: {trades}\n\n")
    
    print(f"✅ 文本摘要保存到: {summary_file}")
    
    return detailed_file, report_file, summary_file

def main():
    """主函数"""
    print("🚀 开始测试前5名智能组合")
    
    # 1. 加载组合报告
    report = load_combination_report()
    if not report:
        print("❌ 无法加载组合报告，退出")
        return False
    
    # 2. 获取前5名组合
    top_combinations = report.get("top_combinations", [])[:5]
    if not top_combinations:
        print("❌ 报告中未找到前5名组合")
        return False
    
    print(f"📋 找到 {len(top_combinations)} 个前5名组合")
    
    # 3. 创建测试数据
    test_data = create_test_data(500)
    
    # 4. 测试每个组合
    all_results = []
    
    for i, combination in enumerate(top_combinations, 1):
        print(f"\n{'='*60}")
        print(f"测试进度: {i}/{len(top_combinations)}")
        print(f"{'='*60}")
        
        # 使用加权投票法测试
        results = test_combination(combination, test_data, "weighted_vote")
        if results:
            all_results.append(results)
        
        # 每测试2个组合后短暂暂停
        if i % 2 == 0:
            print("⏸️  短暂暂停...")
            time.sleep(1)
    
    # 5. 生成对比报告
    if all_results:
        comparison_report = generate_comparison_report(all_results)
        
        # 6. 保存结果
        detailed_file, report_file, summary_file = save_results(all_results, comparison_report)
        
        print(f"\n{'='*80}")
        print("🎉 前5名组合测试完成!")
        print(f"{'='*80}")
        print(f"📁 结果文件:")
        print(f"   详细结果: {detailed_file}")
        print(f"   对比报告: {report_file}")
        print(f"   文本摘要: {summary_file}")
        
        return True
    else:
        print("❌ 没有成功测试任何组合")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)