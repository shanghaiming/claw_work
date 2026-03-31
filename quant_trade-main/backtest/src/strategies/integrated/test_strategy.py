"""
多因子策略测试脚本
使用模拟数据进行策略测试和验证
"""

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
sys.path.append('.')

from multi_factor_strategy import MultiFactorStrategy

# ==================== 数据生成函数 ====================

def generate_test_data(n_days: int = 200, seed: int = 42) -> pd.DataFrame:
    """生成测试数据，包含上升趋势、下降趋势和震荡阶段"""
    np.random.seed(seed)
    
    # 生成日期
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    
    # 生成基础价格（带趋势）
    base_price = 100
    trend = np.zeros(n_days)
    
    # 三个阶段：上升趋势 -> 震荡 -> 下降趋势
    trend[0:60] = np.linspace(0, 30, 60)  # 上升趋势
    trend[60:120] = 30 + np.sin(np.linspace(0, 6*np.pi, 60)) * 5  # 震荡
    trend[120:200] = np.linspace(30, -20, 80)  # 下降趋势
    
    # 生成收盘价
    close = base_price + trend + np.random.normal(0, 2, n_days).cumsum()
    
    # 生成高、低、开盘价
    high = close + np.random.uniform(1, 3, n_days)
    low = close - np.random.uniform(1, 3, n_days)
    open_price = close.shift(1) + np.random.normal(0, 1, n_days)
    open_price[0] = close[0] - np.random.uniform(0, 2)
    
    # 生成成交量
    volume = np.random.randint(10000, 100000, n_days)
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume
    }, index=dates)
    
    return df


# ==================== 策略测试 ====================

def test_strategy_implementation():
    """测试策略实现"""
    print("=" * 60)
    print("多因子策略测试")
    print("=" * 60)
    
    # 生成测试数据
    test_df = generate_test_data(n_days=200)
    print(f"测试数据: {len(test_df)}天, 列: {list(test_df.columns)}")
    print(f"价格范围: {test_df['close'].min():.2f} - {test_df['close'].max():.2f}")
    print(f"成交量均值: {test_df['volume'].mean():.0f}")
    
    # 配置策略
    config = {
        'vr_period': 26,
        'macd_fast': 5,
        'macd_slow': 13,
        'macd_signal': 8,
        'bb_period': 20,
        'bb_std': 2,
        'tsma_periods': [5, 8, 13, 34],
        'ema_periods': [5, 8, 34, 55],
        'fisher_period': 10,
        'chop_period': 14,
        'hma_period': 20,
        'fisher_threshold': 0.5,
        'chop_trend_threshold': 38.2,
        'chop_choppy_threshold': 61.8,
        'position_max': 0.7
    }
    
    # 创建策略实例
    strategy = MultiFactorStrategy(config)
    
    print("\n1. 计算技术指标...")
    df_with_indicators = strategy.calculate_indicators(test_df)
    
    # 检查指标计算
    print(f"指标计算完成，新增列数: {len(df_with_indicators.columns) - 5}")
    
    # 显示关键指标
    required_columns = ['fisher', 'chop', 'hma', 'macd', 'vr', 'market_state', 'trend_score']
    missing = [col for col in required_columns if col not in df_with_indicators.columns]
    if missing:
        print(f"警告: 缺失列 {missing}")
    else:
        print("所有关键指标计算成功")
    
    print("\n2. 生成交易信号...")
    signals_df = strategy.generate_signals()
    
    # 分析信号
    buy_signals = (signals_df['signal'] == 1).sum()
    sell_signals = (signals_df['signal'] == -1).sum()
    total_signals = buy_signals + sell_signals
    
    print(f"买入信号数: {buy_signals}")
    print(f"卖出信号数: {sell_signals}")
    print(f"总信号数: {total_signals}")
    
    if total_signals > 0:
        avg_strength = signals_df.loc[signals_df['signal'] != 0, 'signal_strength'].abs().mean()
        avg_position = signals_df.loc[signals_df['signal'] != 0, 'position_weight'].mean()
        print(f"平均信号强度: {avg_strength:.3f}")
        print(f"平均仓位权重: {avg_position:.3f}")
    
    print("\n3. 运行回测...")
    backtest_result = strategy.backtest(test_df, initial_capital=100000)
    
    print(f"总交易数: {backtest_result['total_trades']}")
    if backtest_result['trades']:
        print("\n前5笔交易:")
        for i, trade in enumerate(backtest_result['trades'][:5]):
            print(f"  {i+1}. {trade['date'].strftime('%Y-%m-%d')} {trade['signal']} "
                  f"价格: {trade['price']:.2f} 仓位: {trade['value']:.0f}")
    
    print("\n4. 策略摘要...")
    summary = strategy.get_strategy_summary()
    print(summary)
    
    return df_with_indicators, signals_df


# ==================== 可视化 ====================

def plot_strategy_results(df_with_indicators, signals_df):
    """绘制策略结果"""
    plt.figure(figsize=(15, 12))
    
    # 1. 价格和信号
    plt.subplot(4, 1, 1)
    plt.plot(df_with_indicators.index, df_with_indicators['close'], label='收盘价', linewidth=2)
    plt.plot(df_with_indicators.index, df_with_indicators['hma'], label='Hull MA', linewidth=1.5, alpha=0.7)
    
    # 标记买入信号
    buy_signals = signals_df[signals_df['signal'] == 1]
    if len(buy_signals) > 0:
        plt.scatter(buy_signals.index, buy_signals['close'], 
                   color='green', marker='^', s=100, label='买入信号', zorder=5)
    
    # 标记卖出信号
    sell_signals = signals_df[signals_df['signal'] == -1]
    if len(sell_signals) > 0:
        plt.scatter(sell_signals.index, sell_signals['close'],
                   color='red', marker='v', s=100, label='卖出信号', zorder=5)
    
    plt.title('价格走势与交易信号')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 2. Fisher Transform
    plt.subplot(4, 1, 2)
    plt.plot(df_with_indicators.index, df_with_indicators['fisher'], label='Fisher Transform', linewidth=2)
    plt.axhline(y=0.5, color='green', linestyle='--', alpha=0.5, label='买入阈值')
    plt.axhline(y=-0.5, color='red', linestyle='--', alpha=0.5, label='卖出阈值')
    plt.fill_between(df_with_indicators.index, 0, df_with_indicators['fisher'],
                     where=df_with_indicators['fisher'] > 0.5, color='green', alpha=0.3)
    plt.fill_between(df_with_indicators.index, 0, df_with_indicators['fisher'],
                     where=df_with_indicators['fisher'] < -0.5, color='red', alpha=0.3)
    plt.title('Fisher Transform 指标')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 3. Choppiness Index
    plt.subplot(4, 1, 3)
    plt.plot(df_with_indicators.index, df_with_indicators['chop'], label='Choppiness Index', linewidth=2)
    plt.axhline(y=38.2, color='blue', linestyle='--', alpha=0.5, label='趋势阈值')
    plt.axhline(y=61.8, color='orange', linestyle='--', alpha=0.5, label='震荡阈值')
    plt.fill_between(df_with_indicators.index, 38.2, 61.8, color='yellow', alpha=0.1, label='中性区域')
    plt.fill_between(df_with_indicators.index, 0, 38.2, color='blue', alpha=0.1, label='趋势市')
    plt.fill_between(df_with_indicators.index, 61.8, 100, color='orange', alpha=0.1, label='震荡市')
    plt.title('Choppiness Index 市场状态')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    # 4. 信号强度和仓位
    plt.subplot(4, 1, 4)
    plt.bar(signals_df.index, signals_df['signal_strength'], 
            color=np.where(signals_df['signal_strength'] > 0, 'green', 'red'), alpha=0.6, label='信号强度')
    plt.plot(signals_df.index, signals_df['position_weight'] * 10, 
             color='blue', linewidth=2, label='仓位权重(x10)')
    plt.axhline(y=0, color='black', linewidth=0.5)
    plt.title('信号强度与仓位权重')
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    # 保存图像
    plt.savefig('/Users/chengming/.openclaw/workspace/strategy_results.png', dpi=300, bbox_inches='tight')
    print(f"\n图表已保存到: /Users/chengming/.openclaw/workspace/strategy_results.png")
    
    # 显示图表
    plt.show()


# ==================== 详细分析 ====================

def detailed_analysis(df_with_indicators, signals_df):
    """详细分析策略表现"""
    print("\n" + "=" * 60)
    print("详细策略分析")
    print("=" * 60)
    
    # 1. 指标统计
    print("\n1. 关键指标统计:")
    key_indicators = ['fisher', 'chop', 'hma', 'macd_hist', 'vr']
    for indicator in key_indicators:
        if indicator in df_with_indicators.columns:
            mean_val = df_with_indicators[indicator].mean()
            std_val = df_with_indicators[indicator].std()
            print(f"  {indicator:15} 均值: {mean_val:8.3f}, 标准差: {std_val:8.3f}")
    
    # 2. 市场状态分布
    if 'market_state' in df_with_indicators.columns:
        print(f"\n2. 市场状态分布:")
        state_counts = df_with_indicators['market_state'].value_counts()
        for state, count in state_counts.items():
            percentage = count / len(df_with_indicators) * 100
            print(f"  {state:10} {count:4}天 ({percentage:.1f}%)")
    
    # 3. 信号分析
    print("\n3. 交易信号分析:")
    if 'signal' in signals_df.columns:
        signals = signals_df['signal']
        
        # 信号持续时间分析
        signal_changes = (signals != signals.shift(1))
        signal_periods = []
        current_period = 0
        
        for i in range(1, len(signals)):
            if signal_changes.iloc[i]:
                if current_period > 0:
                    signal_periods.append(current_period)
                current_period = 1
            elif signals.iloc[i] != 0:
                current_period += 1
        
        if current_period > 0:
            signal_periods.append(current_period)
        
        if signal_periods:
            avg_period = np.mean(signal_periods)
            max_period = np.max(signal_periods)
            print(f"  平均持仓天数: {avg_period:.1f}天")
            print(f"  最长持仓天数: {max_period}天")
        
        # 信号强度分布
        if 'signal_strength' in signals_df.columns:
            strong_signals = (signals_df['signal_strength'].abs() > 0.4).sum()
            medium_signals = ((signals_df['signal_strength'].abs() > 0.2) & 
                             (signals_df['signal_strength'].abs() <= 0.4)).sum()
            weak_signals = (signals_df['signal_strength'].abs() <= 0.2).sum()
            
            print(f"  强烈信号: {strong_signals}次")
            print(f"  中等信号: {medium_signals}次")
            print(f"  弱信号: {weak_signals}次")
    
    # 4. 策略性能预估
    print("\n4. 策略性能预估:")
    print("  基于多因子框架，预期性能:")
    print("  - 趋势识别准确率: 通过Fisher+HMA+TSMA多重验证")
    print("  - 市场适应性: 通过Chop指数调整信号强度")
    print("  - 风险控制: 仓位权重与信号强度正相关")
    print("  - 年化收益目标: 60-100%+ (需实际数据验证)")
    print("  - 最大回撤目标: < 20% (通过仓位管理控制)")
    
    # 5. 建议和改进
    print("\n5. 改进建议:")
    print("  a) 参数优化: 对阈值参数进行网格搜索优化")
    print("  b) 止损机制: 添加基于ATR的动态止损")
    print("  c) 因子权重: 使用机器学习优化因子权重")
    print("  d) 市场状态: 添加更多市场状态识别因子")
    print("  e) 回测验证: 使用真实历史数据进行回测")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("多因子量化策略测试开始...")
    
    try:
        # 运行策略测试
        df_with_indicators, signals_df = test_strategy_implementation()
        
        # 详细分析
        detailed_analysis(df_with_indicators, signals_df)
        
        # 尝试绘图
        try:
            plot_strategy_results(df_with_indicators, signals_df)
        except Exception as e:
            print(f"\n绘图错误 (可能缺少GUI环境): {e}")
            print("建议在Jupyter Notebook或支持GUI的环境中运行")
        
        print("\n" + "=" * 60)
        print("策略测试完成!")
        print("=" * 60)
        
        print("\n下一步:")
        print("1. 使用真实股票数据进行测试")
        print("2. 优化策略参数")
        print("3. 添加止损和风险管理")
        print("4. 进行完整的回测验证")
        
        return True
        
    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 测试成功完成!")
    else:
        print("\n❌ 测试失败")