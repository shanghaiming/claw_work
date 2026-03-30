#!/usr/bin/env python3
"""
简化版组合回测系统
使用已验证的3个策略进行组合回测
"""

import pandas as pd
import numpy as np
import talib
import json
from datetime import datetime
import os
import sys

print("=" * 80)
print("📊 简化版组合回测系统")
print("=" * 80)

def load_stock_data(stock_code="000001.SZ"):
    """加载股票数据"""
    data_dir = "quant_trade-main/data/daily_data2"
    file_path = os.path.join(data_dir, f"{stock_code}.csv")
    
    if os.path.exists(file_path):
        print(f"📂 加载数据: {file_path}")
        data = pd.read_csv(file_path)
        # 假设CSV包含列: date, open, high, low, close, volume
        if 'date' in data.columns:
            data['date'] = pd.to_datetime(data['date'])
            data.set_index('date', inplace=True)
        return data
    else:
        print(f"⚠️ 数据文件不存在: {file_path}")
        print("📊 生成模拟数据...")
        return generate_sample_data()

def generate_sample_data():
    """生成样本数据"""
    np.random.seed(42)
    n = 500
    
    dates = pd.date_range(start='2022-01-01', periods=n, freq='D')
    returns = np.random.normal(0.0005, 0.02, n)
    prices = 100 * np.exp(np.cumsum(returns))
    
    data = pd.DataFrame({
        'open': prices * (1 + np.random.normal(0, 0.01, n)),
        'high': prices * (1 + np.abs(np.random.normal(0, 0.015, n))),
        'low': prices * (1 - np.abs(np.random.normal(0, 0.015, n))),
        'close': prices,
        'volume': np.random.randint(10000, 100000, n)
    }, index=dates)
    
    return data

def ma_crossover_strategy(data, fast_period=10, slow_period=30):
    """移动平均交叉策略"""
    close = data['close'].values
    
    # 计算移动平均
    ma_fast = talib.SMA(close, timeperiod=fast_period)
    ma_slow = talib.SMA(close, timeperiod=slow_period)
    
    # 生成信号
    signals = np.zeros_like(close)
    for i in range(1, len(close)):
        if ma_fast[i] > ma_slow[i] and ma_fast[i-1] <= ma_slow[i-1]:
            signals[i] = 1  # 金叉买入
        elif ma_fast[i] < ma_slow[i] and ma_fast[i-1] >= ma_slow[i-1]:
            signals[i] = -1  # 死叉卖出
    
    return signals

def rsi_strategy(data, period=14, oversold=30, overbought=70):
    """RSI超买超卖策略"""
    close = data['close'].values
    
    # 计算RSI
    rsi = talib.RSI(close, timeperiod=period)
    
    # 生成信号
    signals = np.zeros_like(close)
    for i in range(1, len(close)):
        if rsi[i] < oversold and rsi[i-1] >= oversold:
            signals[i] = 1  # 超卖买入
        elif rsi[i] > overbought and rsi[i-1] <= overbought:
            signals[i] = -1  # 超卖卖出
    
    return signals

def macd_strategy(data, fast_period=12, slow_period=26, signal_period=9):
    """MACD交叉策略"""
    close = data['close'].values
    
    # 计算MACD
    macd, signal, hist = talib.MACD(close, 
                                   fastperiod=fast_period,
                                   slowperiod=slow_period,
                                   signalperiod=signal_period)
    
    # 生成信号
    signals = np.zeros_like(close)
    for i in range(1, len(close)):
        if macd[i] > signal[i] and macd[i-1] <= signal[i-1]:
            signals[i] = 1  # MACD金叉买入
        elif macd[i] < signal[i] and macd[i-1] >= signal[i-1]:
            signals[i] = -1  # MACD死叉卖出
    
    return signals

def combine_signals(signals_list, weights=None):
    """组合多个信号"""
    if weights is None:
        weights = [1.0/len(signals_list)] * len(signals_list)
    
    # 加权平均
    weighted_signals = np.zeros_like(signals_list[0])
    for i, signals in enumerate(signals_list):
        weighted_signals += signals * weights[i]
    
    # 转换为离散信号
    combined = np.zeros_like(weighted_signals)
    combined[weighted_signals > 0.5] = 1
    combined[weighted_signals < -0.5] = -1
    
    return combined

def run_backtest(data, signals, initial_capital=1000000.0, commission_rate=0.001):
    """运行回测"""
    capital = initial_capital
    position = 0
    trades = []
    equity_curve = []
    
    close_prices = data['close'].values
    
    for i in range(len(close_prices)):
        price = close_prices[i]
        signal = signals[i]
        
        # 当前权益
        current_equity = capital + position * price
        equity_curve.append(current_equity)
        
        # 执行交易
        if signal == 1 and position <= 0:  # 买入
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
                    'date': data.index[i] if i < len(data.index) else i,
                    'type': 'BUY',
                    'price': price,
                    'shares': buy_shares
                })
        
        elif signal == -1 and position >= 0:  # 卖出
            if position > 0:  # 平多仓
                capital += position * price * (1 - commission_rate)
                trades.append({
                    'date': data.index[i] if i < len(data.index) else i,
                    'type': 'SELL',
                    'price': price,
                    'shares': position
                })
                position = 0
    
    # 最后平仓
    if position != 0:
        last_price = close_prices[-1]
        capital += position * last_price * (1 - commission_rate)
        position = 0
    
    # 计算绩效指标
    equity_curve = np.array(equity_curve)
    if len(equity_curve) > 1:
        returns = np.diff(equity_curve) / equity_curve[:-1]
        
        total_return = (equity_curve[-1] - equity_curve[0]) / equity_curve[0] if equity_curve[0] != 0 else 0
        sharpe_ratio = np.mean(returns) / np.std(returns) * np.sqrt(252) if np.std(returns) != 0 else 0
        
        # 最大回撤
        peak = equity_curve[0]
        max_dd = 0.0
        for value in equity_curve:
            if value > peak:
                peak = value
            dd = (peak - value) / peak if peak != 0 else 0
            if dd > max_dd:
                max_dd = dd
        
        win_rate = len([r for r in returns if r > 0]) / len(returns) if len(returns) > 0 else 0
    else:
        total_return = 0
        sharpe_ratio = 0
        max_dd = 0
        win_rate = 0
    
    return {
        'total_return': total_return,
        'sharpe_ratio': sharpe_ratio,
        'max_drawdown': max_dd,
        'win_rate': win_rate,
        'final_capital': equity_curve[-1] if len(equity_curve) > 0 else initial_capital,
        'trades_count': len(trades),
        'equity_curve': equity_curve.tolist()
    }

def main():
    """主函数"""
    print("📊 加载数据...")
    data = load_stock_data("000001.SZ")
    
    print("🔄 生成策略信号...")
    
    # 生成单个策略信号
    ma_signals = ma_crossover_strategy(data)
    rsi_signals = rsi_strategy(data)
    macd_signals = macd_strategy(data)
    
    print(f"移动平均交叉策略信号统计: 买入 {np.sum(ma_signals == 1)}, 卖出 {np.sum(ma_signals == -1)}")
    print(f"RSI策略信号统计: 买入 {np.sum(rsi_signals == 1)}, 卖出 {np.sum(rsi_signals == -1)}")
    print(f"MACD策略信号统计: 买入 {np.sum(macd_signals == 1)}, 卖出 {np.sum(macd_signals == -1)}")
    
    print("🔄 组合策略信号...")
    
    # 等权重组合
    combined_signals = combine_signals([ma_signals, rsi_signals, macd_signals], 
                                       weights=[0.4, 0.3, 0.3])
    
    print(f"组合策略信号统计: 买入 {np.sum(combined_signals == 1)}, 卖出 {np.sum(combined_signals == -1)}")
    
    print("🚀 运行回测...")
    
    # 回测单个策略
    ma_result = run_backtest(data, ma_signals)
    rsi_result = run_backtest(data, rsi_signals)
    macd_result = run_backtest(data, macd_signals)
    combined_result = run_backtest(data, combined_signals)
    
    print("\n" + "=" * 80)
    print("📊 回测结果")
    print("=" * 80)
    
    results = {
        '移动平均交叉策略': ma_result,
        'RSI策略': rsi_result,
        'MACD策略': macd_result,
        '组合策略(等权重)': combined_result
    }
    
    for name, result in results.items():
        print(f"\n{name}:")
        print(f"  总收益率: {result['total_return']:.2%}")
        print(f"  夏普比率: {result['sharpe_ratio']:.3f}")
        print(f"  最大回撤: {result['max_drawdown']:.2%}")
        print(f"  胜率: {result['win_rate']:.2%}")
        print(f"  交易次数: {result['trades_count']}")
        print(f"  最终资金: {result['final_capital']:,.2f}")
    
    # 确定最佳策略
    best_strategy = max(results.items(), key=lambda x: x[1]['total_return'])
    print(f"\n🏆 最佳策略: {best_strategy[0]} (收益率: {best_strategy[1]['total_return']:.2%})")
    
    # 保存结果
    report = {
        'generated_at': datetime.now().isoformat(),
        'data_points': len(data),
        'results': results,
        'best_strategy': best_strategy[0],
        'best_return': best_strategy[1]['total_return']
    }
    
    with open('simple_combination_backtest_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ 回测完成! 报告已保存: simple_combination_backtest_report.json")
    
    return results

if __name__ == "__main__":
    main()