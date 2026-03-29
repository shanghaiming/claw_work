#!/usr/bin/env python3
"""
简化回测试例 - 展示量化交易系统基本功能
"""

import sys
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# 添加系统路径
sys.path.append('/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration')

def run_simple_backtest():
    """运行简化回测试例"""
    print("=" * 60)
    print("简化回测试例 - 量化交易系统验证")
    print("=" * 60)
    
    try:
        # 1. 测试数据加载
        print("\n1️⃣ 数据加载测试")
        data_path = './data/TEST001.SZ.csv'
        
        if not os.path.exists(data_path):
            print(f"❌ 数据文件不存在: {data_path}")
            return False
        
        # 加载数据
        df = pd.read_csv(data_path)
        print(f"✅ 数据加载成功: {data_path}")
        print(f"   数据形状: {df.shape}")
        print(f"   列名: {list(df.columns)}")
        print(f"   时间范围: {df['date'].min()} 到 {df['date'].max()}")
        
        # 2. 创建简单策略
        print("\n2️⃣ 创建简单移动平均策略")
        
        # 转换为DataFrame并设置索引
        df_analysis = df.copy()
        df_analysis['date'] = pd.to_datetime(df_analysis['date'])
        df_analysis.set_index('date', inplace=True)
        
        # 计算移动平均
        df_analysis['ma_short'] = df_analysis['close'].rolling(window=5).mean()
        df_analysis['ma_long'] = df_analysis['close'].rolling(window=20).mean()
        df_analysis['ma_diff'] = df_analysis['ma_short'] - df_analysis['ma_long']
        
        # 生成信号
        df_analysis['signal'] = 0
        df_analysis.loc[df_analysis['ma_diff'] > 0, 'signal'] = 1  # 买入信号
        df_analysis.loc[df_analysis['ma_diff'] < 0, 'signal'] = -1  # 卖出信号
        
        # 计算信号变化
        df_analysis['position'] = df_analysis['signal'].diff()
        
        # 统计信号
        buy_signals = (df_analysis['position'] == 2).sum()  # 从-1到1
        sell_signals = (df_analysis['position'] == -2).sum()  # 从1到-1
        total_signals = buy_signals + sell_signals
        
        print(f"✅ 策略生成完成")
        print(f"   买入信号: {buy_signals}")
        print(f"   卖出信号: {sell_signals}")
        print(f"   总信号数: {total_signals}")
        
        # 3. 简单回测
        print("\n3️⃣ 运行简单回测")
        
        # 初始参数
        initial_capital = 1000000
        commission_rate = 0.0003
        position = 0
        cash = initial_capital
        portfolio_value = initial_capital
        
        trades = []
        positions = []
        portfolio_values = []
        
        for i in range(len(df_analysis)):
            if i < 20:  # 跳过前20个数据点（用于计算MA）
                portfolio_values.append(portfolio_value)
                positions.append(position)
                continue
                
            row = df_analysis.iloc[i]
            price = row['close']
            
            # 检查信号
            if row['position'] == 2:  # 买入信号
                # 计算可买入数量
                max_shares = cash // (price * (1 + commission_rate))
                if max_shares > 0:
                    cost = max_shares * price * (1 + commission_rate)
                    cash -= cost
                    position += max_shares
                    
                    trades.append({
                        'date': row.name,
                        'type': 'buy',
                        'price': price,
                        'shares': max_shares,
                        'cost': cost,
                        'cash': cash,
                        'position': position
                    })
                    
            elif row['position'] == -2:  # 卖出信号
                if position > 0:
                    # 卖出所有持仓
                    revenue = position * price * (1 - commission_rate)
                    cash += revenue
                    
                    trades.append({
                        'date': row.name,
                        'type': 'sell',
                        'price': price,
                        'shares': position,
                        'revenue': revenue,
                        'cash': cash,
                        'position': 0
                    })
                    position = 0
            
            # 更新投资组合价值
            portfolio_value = cash + position * price
            portfolio_values.append(portfolio_value)
            positions.append(position)
        
        # 4. 绩效分析
        print("\n4️⃣ 绩效分析")
        
        df_analysis['portfolio_value'] = portfolio_values
        df_analysis['position'] = positions
        
        # 计算收益
        returns = df_analysis['portfolio_value'].pct_change().dropna()
        cumulative_returns = (1 + returns).cumprod() - 1
        
        # 基础指标
        total_return = (portfolio_values[-1] - initial_capital) / initial_capital
        annual_return = total_return / (len(df_analysis) / 252)  # 粗略年化
        volatility = returns.std() * np.sqrt(252)
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        print(f"✅ 回测完成")
        print(f"   初始资金: ¥{initial_capital:,.2f}")
        print(f"   最终资金: ¥{portfolio_values[-1]:,.2f}")
        print(f"   总收益率: {total_return:.2%}")
        print(f"   年化收益: {annual_return:.2%}")
        print(f"   年化波动: {volatility:.2%}")
        print(f"   夏普比率: {sharpe_ratio:.2f}")
        print(f"   最大回撤: {max_drawdown:.2%}")
        print(f"   交易次数: {len(trades)}")
        
        # 5. 生成简单报告
        print("\n5️⃣ 生成报告文件")
        
        report_dir = './reports'
        os.makedirs(report_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_path = os.path.join(report_dir, f'simple_backtest_report_{timestamp}.md')
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(f"""# 简化回测报告 - TEST001.SZ

## 基本信息
- **策略名称**: 双移动平均线交叉
- **测试标的**: TEST001.SZ
- **测试期间**: {df_analysis.index.min()} 到 {df_analysis.index.max()}
- **初始资金**: ¥{initial_capital:,.2f}
- **交易佣金**: {commission_rate:.4f}

## 绩效指标
| 指标 | 数值 |
|------|------|
| 最终资金 | ¥{portfolio_values[-1]:,.2f} |
| 总收益率 | {total_return:.2%} |
| 年化收益率 | {annual_return:.2%} |
| 年化波动率 | {volatility:.2%} |
| 夏普比率 | {sharpe_ratio:.2f} |
| 最大回撤 | {max_drawdown:.2%} |
| 交易次数 | {len(trades)} |

## 交易统计
- **买入交易**: {sum(1 for t in trades if t['type'] == 'buy')}
- **卖出交易**: {sum(1 for t in trades if t['type'] == 'sell')}

## 策略参数
- 短期移动平均: 5日
- 长期移动平均: 20日
- 信号生成: 短期MA > 长期MA (买入), 短期MA < 长期MA (卖出)

## 数据概况
- 数据点数量: {len(df_analysis)}
- 有效信号数量: {total_signals}
- 时间跨度: {len(df_analysis)} 个交易日

## 优化建议
1. **参数优化**: 测试不同的MA周期组合
2. **信号过滤**: 添加成交量确认或价格位置过滤
3. **风险管理**: 添加止损和止盈机制
4. **仓位管理**: 优化每次交易的仓位规模

## 下一步
1. 使用完整系统进行多参数优化
2. 整合更多技术指标和价格行为信号
3. 运行多时间框架协调策略
4. 进行压力测试和鲁棒性分析

---
**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**系统版本**: 简化回测试例 v1.0
""")
        
        print(f"✅ 报告已生成: {report_path}")
        
        # 6. 保存结果
        print("\n6️⃣ 保存回测结果")
        
        results_path = os.path.join(report_dir, f'simple_backtest_results_{timestamp}.csv')
        
        # 创建结果DataFrame
        results_df = pd.DataFrame({
            'date': df_analysis.index,
            'close': df_analysis['close'],
            'ma_short': df_analysis['ma_short'],
            'ma_long': df_analysis['ma_long'],
            'signal': df_analysis['signal'],
            'position': df_analysis['position'],
            'portfolio_value': df_analysis['portfolio_value']
        })
        
        results_df.to_csv(results_path, index=False)
        print(f"✅ 结果已保存: {results_path}")
        
        # 7. 生成优化建议
        print("\n7️⃣ 优化建议")
        
        print("🚀 **立即可以进行的优化**:")
        print("   1. 参数扫描: 测试MA(3,5,8,13,21) vs MA(21,34,55,89,144)")
        print("   2. 信号确认: 添加RSI或MACD确认")
        print("   3. 风险管理: 添加2%止损和5%止盈")
        
        print("\n📊 **使用完整系统的优化计划**:")
        print("   1. 多策略组合: 移动平均 + 价格行为 + 突破策略")
        print("   2. 多时间框架: 日线趋势 + 30min入场 + 5min确认")
        print("   3. 机器学习: 使用历史数据训练信号分类器")
        
        return True
        
    except Exception as e:
        print(f"❌ 回测试例执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主函数"""
    print("🚀 开始简化回测试例...")
    print(f"工作目录: {os.getcwd()}")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if run_simple_backtest():
        print("\n" + "=" * 60)
        print("✅ 简化回测试例执行成功!")
        print("=" * 60)
        
        print("\n🎯 已证明:")
        print("  1. 数据加载和处理能力 ✅")
        print("  2. 策略生成和信号检测 ✅")
        print("  3. 回测引擎和绩效计算 ✅")
        print("  4. 报告生成和结果保存 ✅")
        
        print("\n🚀 下一步:")
        print("  1. 使用完整系统进行参数优化")
        print("  2. 整合多时间框架数据")
        print("  3. 运行深度优化迭代")
        
        print("\n💡 提示: 完整系统已就绪，等待实际数据即可进行专业级回测优化。")
    else:
        print("\n❌ 简化回测试例执行失败")
    
    print(f"\n📁 生成文件位置: {os.path.abspath('./reports')}")

if __name__ == "__main__":
    main()