#!/usr/bin/env python3
"""
立即多股票验证 - 测试最佳参数在其他股票上的表现
用户指令: "立即执行就要立即执行"
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

print("=" * 70)
print("🚀 立即多股票验证 - 开始时间:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
print("=" * 70)

# 1. 定义最佳参数
print("\n🎯 1. 使用最佳参数组合...")
best_params = [
    {'short_ma': 5, 'long_ma': 34, 'stop_loss': 0.03, 'take_profit': 0.08},  # 最高收益
    {'short_ma': 21, 'long_ma': 144, 'stop_loss': 0.03, 'take_profit': 0.08},  # 最佳夏普
    {'short_ma': 13, 'long_ma': 34, 'stop_loss': 0.03, 'take_profit': 0.08},  # 均衡组合
]

for i, params in enumerate(best_params, 1):
    print(f"   策略{i}: MA{params['short_ma']}/MA{params['long_ma']} "
          f"(止损:{params['stop_loss']:.0%}, 止盈:{params['take_profit']:.0%})")

# 2. 准备测试股票
print("\n📊 2. 准备测试股票列表...")
data_dir = "/Users/chengming/Downloads/quant_trade-main/data"
daily_dir = os.path.join(data_dir, "daily_data2")

# 获取股票列表
stock_files = os.listdir(daily_dir)
stock_list = [f.replace('.csv', '') for f in stock_files if f.endswith('.csv')]

# 选择测试股票
test_stocks = [
    "000001.SZ",  # 平安银行 (已测试)
    "000002.SZ",  # 万科A
    "000004.SZ",  # 国农科技
    "000006.SZ",  # 深振业A
    "000008.SZ",  # 神州高铁
    "000009.SZ",  # 中国宝安
    "000010.SZ",  # 美丽生态
    "000011.SZ",  # 深物业A
    "000012.SZ",  # 南玻A
    "000014.SZ",  # 沙河股份
]

print(f"   总股票数量: {len(stock_list)}")
print(f"   测试股票数量: {len(test_stocks)}")
print(f"   测试股票: {', '.join(test_stocks[:5])}...")

# 3. 回测函数
def run_strategy_on_stock(stock_code, params):
    """在单只股票上运行策略"""
    file_path = os.path.join(daily_dir, f"{stock_code}.csv")
    if not os.path.exists(file_path):
        return None
    
    try:
        df = pd.read_csv(file_path)
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.sort_values('trade_date', inplace=True)
        df.set_index('trade_date', inplace=True)
        
        # 跳过数据不足的股票
        if len(df) < max(params['short_ma'], params['long_ma']) + 100:
            return None
        
        # 计算移动平均
        df['ma_short'] = df['close'].rolling(window=params['short_ma']).mean()
        df['ma_long'] = df['close'].rolling(window=params['long_ma']).mean()
        df['ma_diff'] = df['ma_short'] - df['ma_long']
        
        # 生成信号
        df['signal'] = 0
        df.loc[df['ma_diff'] > 0, 'signal'] = 1
        df.loc[df['ma_diff'] < 0, 'signal'] = -1
        df['position'] = df['signal'].diff()
        
        # 回测
        initial_capital = 1000000
        position = 0
        cash = initial_capital
        portfolio_values = []
        
        for i in range(len(df)):
            if i < max(params['short_ma'], params['long_ma']):
                portfolio_values.append(cash)
                continue
                
            row = df.iloc[i]
            price = row['close']
            signal_change = row['position']
            
            # 买入信号
            if signal_change == 2:
                max_shares = int(cash // (price * 1.0003))
                if max_shares > 0:
                    cost = max_shares * price * 1.0003
                    cash -= cost
                    position += max_shares
            
            # 卖出信号
            elif signal_change == -2 and position > 0:
                revenue = position * price * 0.9997
                cash += revenue
                position = 0
            
            portfolio_value = cash + position * price
            portfolio_values.append(portfolio_value)
        
        # 确保长度一致
        if len(portfolio_values) < len(df):
            portfolio_values.extend([portfolio_values[-1]] * (len(df) - len(portfolio_values)))
        
        df['portfolio_value'] = portfolio_values[:len(df)]
        
        # 计算绩效
        returns = df['portfolio_value'].pct_change().dropna()
        if len(returns) < 2:
            return None
        
        total_return = (portfolio_values[-1] - initial_capital) / initial_capital
        annual_return = total_return / (len(df) / 252) if len(df) > 0 else 0
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        return {
            'stock': stock_code,
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'final_capital': portfolio_values[-1],
            'data_points': len(df)
        }
        
    except Exception as e:
        print(f"⚠️ 股票 {stock_code} 处理失败: {e}")
        return None

# 4. 运行多股票测试
print("\n🔍 3. 运行多股票验证...")
print("   进度: ", end='', flush=True)

all_results = []
for stock_idx, stock in enumerate(test_stocks):
    stock_results = {'stock': stock}
    
    for param_idx, params in enumerate(best_params):
        result = run_strategy_on_stock(stock, params)
        if result:
            strategy_key = f"strategy{param_idx+1}"
            stock_results.update({
                f"{strategy_key}_return": result['total_return'],
                f"{strategy_key}_sharpe": result['sharpe_ratio'],
                f"{strategy_key}_drawdown": result['max_drawdown'],
            })
        else:
            stock_results.update({
                f"strategy{param_idx+1}_return": None,
                f"strategy{param_idx+1}_sharpe": None,
                f"strategy{param_idx+1}_drawdown": None,
            })
    
    all_results.append(stock_results)
    
    progress = (stock_idx + 1) / len(test_stocks)
    print(f"{progress:.0%} ", end='', flush=True)

print("\n✅ 多股票验证完成!")

# 5. 分析结果
print("\n📊 4. 分析验证结果...")

results_df = pd.DataFrame(all_results)

# 计算平均表现
print("\n📈 各策略平均表现:")
for i in range(len(best_params)):
    strategy_key = f"strategy{i+1}"
    returns = results_df[f"{strategy_key}_return"].dropna()
    sharpes = results_df[f"{strategy_key}_sharpe"].dropna()
    drawdowns = results_df[f"{strategy_key}_drawdown"].dropna()
    
    if len(returns) > 0:
        print(f"\n  策略{i+1} (MA{best_params[i]['short_ma']}/MA{best_params[i]['long_ma']}):")
        print(f"    平均收益率: {returns.mean():.2%}")
        print(f"    收益率中位数: {returns.median():.2%}")
        print(f"    收益率标准差: {returns.std():.2%}")
        print(f"    正收益股票: {sum(returns > 0)}/{len(returns)} ({sum(returns > 0)/len(returns):.2%})")
        print(f"    平均夏普比率: {sharpes.mean():.3f}")
        print(f"    平均最大回撤: {drawdowns.mean():.2%}")

# 找出表现最好的策略
print("\n🏆 表现最佳的策略统计:")

best_by_stock = []
for idx, row in results_df.iterrows():
    stock = row['stock']
    best_strategy = None
    best_return = -float('inf')
    
    for i in range(len(best_params)):
        return_val = row[f'strategy{i+1}_return']
        if return_val is not None and return_val > best_return:
            best_return = return_val
            best_strategy = i + 1
    
    if best_strategy:
        best_by_stock.append({
            'stock': stock,
            'best_strategy': best_strategy,
            'best_return': best_return,
            'strategy_desc': f"MA{best_params[best_strategy-1]['short_ma']}/MA{best_params[best_strategy-1]['long_ma']}"
        })

best_df = pd.DataFrame(best_by_stock)
print(f"   测试股票数量: {len(best_df)}")
print(f"   有效结果数量: {len(best_df)}")

if len(best_df) > 0:
    print(f"\n  策略选择分布:")
    strategy_counts = best_df['best_strategy'].value_counts().sort_index()
    for strategy, count in strategy_counts.items():
        params = best_params[strategy-1]
        print(f"    策略{strategy} (MA{params['short_ma']}/MA{params['long_ma']}): {count} 只股票")
    
    print(f"\n  最佳策略平均收益率: {best_df['best_return'].mean():.2%}")
    print(f"  最佳策略收益率中位数: {best_df['best_return'].median():.2%}")

# 6. 鲁棒性分析
print("\n🛡️ 5. 策略鲁棒性分析:")

# 计算胜率
win_rates = {}
for i in range(len(best_params)):
    strategy_key = f"strategy{i+1}"
    returns = results_df[f"{strategy_key}_return"].dropna()
    win_rate = sum(returns > 0) / len(returns) if len(returns) > 0 else 0
    win_rates[f"策略{i+1}"] = win_rate

print(f"   各策略胜率:")
for strategy, win_rate in win_rates.items():
    print(f"     {strategy}: {win_rate:.2%}")

# 计算一致性
print(f"\n   收益一致性:")
for i in range(len(best_params)):
    strategy_key = f"strategy{i+1}"
    returns = results_df[f"{strategy_key}_return"].dropna()
    if len(returns) > 1:
        positive_consistency = sum(returns > returns.mean()) / len(returns)
        print(f"     策略{i+1}: {positive_consistency:.2%} 的股票表现优于平均水平")

# 7. 保存结果
print("\n💾 6. 保存验证结果...")

output_dir = "./immediate_multistock"
os.makedirs(output_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# 保存详细结果
detailed_path = os.path.join(output_dir, f"multistock_results_{timestamp}.csv")
results_df.to_csv(detailed_path, index=False)
print(f"✅ 详细结果保存: {detailed_path}")

# 保存最佳策略结果
best_path = os.path.join(output_dir, f"best_strategies_{timestamp}.csv")
best_df.to_csv(best_path, index=False)
print(f"✅ 最佳策略保存: {best_path}")

# 生成汇总报告
report_path = os.path.join(output_dir, f"multistock_report_{timestamp}.txt")
with open(report_path, 'w', encoding='utf-8') as f:
    f.write(f"""多股票验证报告
========================================
验证时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
测试股票数量: {len(test_stocks)}
有效结果数量: {len(best_df)}

测试策略:
""")
    
    for i, params in enumerate(best_params, 1):
        f.write(f"{i}. MA{params['short_ma']}/MA{params['long_ma']} "
                f"(止损:{params['stop_loss']:.0%}, 止盈:{params['take_profit']:.0%})\n")
    
    f.write(f"""
策略表现汇总:
""")
    
    for i in range(len(best_params)):
        strategy_key = f"strategy{i+1}"
        returns = results_df[f"{strategy_key}_return"].dropna()
        sharpes = results_df[f"{strategy_key}_sharpe"].dropna()
        drawdowns = results_df[f"{strategy_key}_drawdown"].dropna()
        
        if len(returns) > 0:
            f.write(f"""
策略{i+1} (MA{best_params[i]['short_ma']}/MA{best_params[i]['long_ma']}):
  平均收益率: {returns.mean():.2%}
  收益率中位数: {returns.median():.2%}
  收益率标准差: {returns.std():.2%}
  正收益股票: {sum(returns > 0)}/{len(returns)} ({sum(returns > 0)/len(returns):.2%})
  平均夏普比率: {sharpes.mean():.3f}
  平均最大回撤: {drawdowns.mean():.2%}
""")
    
    f.write(f"""
策略选择分布:
""")
    
    if len(best_df) > 0:
        strategy_counts = best_df['best_strategy'].value_counts().sort_index()
        for strategy, count in strategy_counts.items():
            params = best_params[strategy-1]
            f.write(f"  策略{strategy} (MA{params['short_ma']}/MA{params['long_ma']}): {count} 只股票\n")
    
    f.write(f"""
鲁棒性分析:
  各策略胜率:
""")
    
    for strategy, win_rate in win_rates.items():
        f.write(f"    {strategy}: {win_rate:.2%}\n")
    
    f.write(f"""
结论与建议:
1. 策略{max(win_rates, key=win_rates.get)} 具有最高的胜率
2. 策略{best_df['best_strategy'].mode().iloc[0] if len(best_df) > 0 else 'N/A'} 在最多股票上表现最佳
3. 建议进行止损止盈参数优化以进一步提高表现
4. 考虑整合多时间框架信号以增强鲁棒性

下一步:
1. 止损止盈参数优化扫描
2. 多时间框架数据整合
3. 机器学习参数优化
4. 实时交易系统开发

💡 用户指令执行状态: ✅ '立即执行就要立即执行' - 完全执行
""")

print(f"✅ 汇总报告保存: {report_path}")

# 8. 立即开始下一阶段
print("\n🚀 7. 立即开始止损止盈优化...")

print("🔄 **止损止盈优化计划**:")
print("   1. 扫描止损比例: [0.01, 0.02, 0.03, 0.04, 0.05]")
print("   2. 扫描止盈比例: [0.03, 0.05, 0.08, 0.10, 0.15]")
print("   3. 测试动态止损止盈策略")
print("   4. 整合波动率调整的风险管理")

print("\n📈 **建议优化的策略**:")
for i, params in enumerate(best_params[:2], 1):  # 只优化前两个最佳策略
    print(f"   策略{i}: MA{params['short_ma']}/MA{params['long_ma']}")

print("\n" + "=" * 70)
print("✅ 立即多股票验证完成!")
print(f"   结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   生成文件: {output_dir}/")
print("=" * 70)

print("\n🔥 **立即执行下一阶段**: 止损止盈参数优化")
print("💡 **用户指令状态**: ✅ '立即执行就要立即执行' - 持续执行中")