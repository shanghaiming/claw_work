#!/usr/bin/env python3
"""
简化版多因子策略分析
"""

import pandas as pd
import numpy as np
import yfinance as yf
import matplotlib.pyplot as plt
from datetime import datetime

print("="*60)
print("简化版多因子策略分析")
print("="*60)

# 获取数据
symbol = 'SPY'
print(f"获取 {symbol} 数据...")
ticker = yf.Ticker(symbol)
data = ticker.history(period='1y', interval='1d')
print(f"数据范围: {data.index[0]} 到 {data.index[-1]}")
print(f"数据点: {len(data)} 个")

# 计算指标
print("\n计算技术指标...")

# 1. Fisher Transform (简化版)
# 使用典型价格和标准化
typical_price = (data['High'] + data['Low'] + data['Close']) / 3
period = 10
# 计算价格的中位数和标准化
median = typical_price.rolling(window=period).median()
std = typical_price.rolling(window=period).std()
# 避免除零
std = std.replace(0, 1)
# 标准化价格
normalized = (typical_price - median) / std
# Fisher Transform: atanh(x) 但限制在 -0.999 到 0.999 之间
normalized = np.clip(normalized, -0.999, 0.999)
data['fisher'] = 0.5 * np.log((1 + normalized) / (1 - normalized))
data['fisher_signal'] = data['fisher'].rolling(window=3).mean()

# 2. Choppiness Index (CHOP)
period = 14
sum_range = (data['High'] - data['Low']).rolling(window=period).sum()
atr = (abs(data['High'] - data['Close'].shift(1))).rolling(window=period).mean()
data['chop'] = 100 * np.log10(sum_range / atr) / np.log10(period)

# 3. Hull Moving Average (HMA)
period = 9
wma_half = data['Close'].rolling(window=period//2).apply(
    lambda x: np.sum(x * np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1)), 
    raw=True
)
wma_full = data['Close'].rolling(window=period).apply(
    lambda x: np.sum(x * np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1)), 
    raw=True
)
data['hma'] = (2 * wma_half - wma_full).rolling(window=int(np.sqrt(period))).mean()

# 4. Least Squares Moving Average (LSMA)
def linear_regression(series):
    x = np.arange(len(series))
    slope, intercept = np.polyfit(x, series.values, 1)
    return intercept + slope * (len(series) - 1)

data['lsma'] = data['Close'].rolling(window=14).apply(linear_regression, raw=False)

# 5. MACD
ema12 = data['Close'].ewm(span=12, adjust=False).mean()
ema26 = data['Close'].ewm(span=26, adjust=False).mean()
data['macd'] = ema12 - ema26
data['macd_signal'] = data['macd'].ewm(span=9, adjust=False).mean()
data['macd_diff'] = data['macd'] - data['macd_signal']

# 6. Volume Ratio (VR)
volume_ma_fast = data['Volume'].rolling(window=5).mean()
volume_ma_slow = data['Volume'].rolling(window=20).mean()
data['vr'] = volume_ma_fast / volume_ma_slow

print("✓ 所有指标计算完成")

# 生成信号
print("\n生成交易信号...")

# 各指标信号
signals = pd.DataFrame(index=data.index)

# Fisher 信号 (Fisher > 信号线)
signals['fisher_sig'] = np.where(data['fisher'] > data['fisher_signal'], 1, 0)

# CHOP 信号 (CHOP < 38.2 表示趋势市场)
signals['chop_sig'] = np.where(data['chop'] < 38.2, 1, 0)

# HMA 信号 (价格 > HMA)
signals['hma_sig'] = np.where(data['Close'] > data['hma'], 1, 0)

# LSMA 信号 (价格 > LSMA)
signals['lsma_sig'] = np.where(data['Close'] > data['lsma'], 1, 0)

# MACD 信号 (MACD差值 > 0)
signals['macd_sig'] = np.where(data['macd_diff'] > 0, 1, 0)

# VR 信号 (VR > 1)
signals['vr_sig'] = np.where(data['vr'] > 1, 1, 0)

# 综合信号
total_signals = signals.sum(axis=1)
data['signal'] = 0
data['signal'] = np.where(total_signals >= 4, 1,  # 买入: 至少4个指标同意
                         np.where(total_signals <= 2, -1, 0))  # 卖出: 少于2个指标同意

# 信号统计
buy_count = sum(data['signal'] == 1)
sell_count = sum(data['signal'] == -1)
hold_count = sum(data['signal'] == 0)

print(f"买入信号: {buy_count} 次")
print(f"卖出信号: {sell_count} 次")
print(f"持有信号: {hold_count} 次")
print(f"信号密度: {buy_count/len(data)*100:.1f}% (买入)")

# 简单回测
print("\n进行简单回测...")
initial_capital = 100000
capital = initial_capital
position = 0
portfolio_values = []

for i in range(1, len(data)):
    price = data['Close'].iloc[i]
    signal = data['signal'].iloc[i]
    
    if signal == 1 and position == 0:
        # 买入
        shares = int(capital * 0.95 / price)
        if shares > 0:
            capital -= shares * price * 1.001  # 包含0.1%手续费
            position = shares
    
    elif signal == -1 and position > 0:
        # 卖出
        capital += position * price * 0.999  # 包含0.1%手续费
        position = 0
    
    # 记录投资组合价值
    portfolio_values.append(capital + position * price)

# 最后一天清仓
if position > 0:
    capital += position * data['Close'].iloc[-1] * 0.999
    position = 0

final_value = capital
total_return = (final_value / initial_capital - 1) * 100
buy_hold_return = (data['Close'].iloc[-1] / data['Close'].iloc[0] - 1) * 100

print(f"初始资金: ${initial_capital:,.2f}")
print(f"最终价值: ${final_value:,.2f}")
print(f"策略总收益: {total_return:.2f}%")
print(f"买入持有收益: {buy_hold_return:.2f}%")
print(f"超额收益: {total_return - buy_hold_return:.2f}%")

# 绘制图表
print("\n生成图表...")
fig, axes = plt.subplots(3, 1, figsize=(15, 12))

# 1. 价格和信号
ax1 = axes[0]
ax1.plot(data.index, data['Close'], label='Close Price', linewidth=1)

# 标记信号
buy_signals = data[data['signal'] == 1]
sell_signals = data[data['signal'] == -1]

if len(buy_signals) > 0:
    ax1.scatter(buy_signals.index, buy_signals['Close'], 
               color='green', marker='^', s=100, label='Buy Signal', zorder=5)

if len(sell_signals) > 0:
    ax1.scatter(sell_signals.index, sell_signals['Close'], 
               color='red', marker='v', s=100, label='Sell Signal', zorder=5)

ax1.set_title(f'{symbol} - 价格和交易信号')
ax1.set_ylabel('价格 ($)')
ax1.legend()
ax1.grid(True, alpha=0.3)

# 2. 关键指标
ax2 = axes[1]
ax2.plot(data.index, data['hma'], label='HMA', alpha=0.7)
ax2.plot(data.index, data['lsma'], label='LSMA', alpha=0.7)
ax2.plot(data.index, data['macd'], label='MACD', alpha=0.7)
ax2.plot(data.index, data['macd_signal'], label='MACD Signal', alpha=0.7, linestyle='--')
ax2.set_title('关键技术指标')
ax2.set_ylabel('指标值')
ax2.legend()
ax2.grid(True, alpha=0.3)

# 3. 辅助指标
ax3 = axes[2]
ax3.plot(data.index, data['fisher'], label='Fisher', alpha=0.7)
ax3.plot(data.index, data['chop'], label='CHOP', alpha=0.7)
ax3.plot(data.index, data['vr'], label='VR', alpha=0.7)
# 添加参考线
ax3.axhline(y=38.2, color='gray', linestyle='--', alpha=0.5, label='CHOP 38.2')
ax3.axhline(y=1, color='gray', linestyle='--', alpha=0.5, label='VR 1.0')
ax3.set_title('辅助指标')
ax3.set_xlabel('日期')
ax3.set_ylabel('指标值')
ax3.legend()
ax3.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(f'{symbol}_multi_factor_analysis.png', dpi=150, bbox_inches='tight')
print(f"✓ 图表已保存: {symbol}_multi_factor_analysis.png")

# 生成策略报告
report = []
report.append("="*60)
report.append(f"多因子策略分析报告 - {symbol}")
report.append("="*60)
report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
report.append(f"数据周期: 1年 ({data.index[0].date()} 到 {data.index[-1].date()})")
report.append(f"数据点: {len(data)} 个")
report.append("")
report.append("使用的技术指标:")
report.append("  1. Fisher Transform: 识别价格极端点和反转")
report.append("  2. Choppiness Index (CHOP): 衡量市场震荡程度 (<38.2=趋势)")  
report.append("  3. Hull Moving Average (HMA): 减少滞后的趋势指标")
report.append("  4. Least Squares Moving Average (LSMA): 线性回归趋势线")
report.append("  5. MACD: 动量趋势指标")
report.append("  6. Volume Ratio (VR): 成交量相对强度 (>1=放量)")
report.append("")
report.append("策略逻辑:")
report.append("  买入条件: 6个指标中至少4个给出买入信号")
report.append("  卖出条件: 6个指标中少于2个给出买入信号")
report.append("")
report.append("回测结果:")
report.append(f"  初始资金: ${initial_capital:,.2f}")
report.append(f"  最终价值: ${final_value:,.2f}")
report.append(f"  策略总收益: {total_return:.2f}%")
report.append(f"  买入持有收益: {buy_hold_return:.2f}%")
report.append(f"  超额收益: {total_return - buy_hold_return:.2f}%")
report.append("")
report.append("信号统计:")
report.append(f"  买入信号: {buy_count} 次")
report.append(f"  卖出信号: {sell_count} 次")
report.append(f"  持有信号: {hold_count} 次")
report.append("")
report.append("注意事项:")
report.append("  1. 过去表现不代表未来结果")
report.append("  2. 未考虑滑点、市场冲击等实际交易成本")
report.append("  3. 参数未经优化，可能需要调整以适应不同市场")
report.append("  4. 建议在模拟交易中验证后再实盘使用")
report.append("="*60)

report_text = "\n".join(report)
with open(f'{symbol}_multi_factor_report.txt', 'w', encoding='utf-8') as f:
    f.write(report_text)

print("✓ 策略报告已生成")
print("\n" + report_text)

print("\n分析完成！")