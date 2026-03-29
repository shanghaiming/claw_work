"""
六因子策略测试脚本
测试完整的六因子策略框架
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import sys
import warnings
warnings.filterwarnings('ignore')

sys.path.append('.')
from multi_factor_strategy_v2 import SixFactorStrategy, calculate_all_indicators, generate_six_factor_signals

# ==================== 数据生成函数 ====================

def generate_realistic_test_data(n_days: int = 300, seed: int = 42) -> pd.DataFrame:
    """生成更真实的测试数据，包含多种市场形态"""
    np.random.seed(seed)
    
    # 生成日期
    start_date = datetime(2025, 1, 1)
    dates = [start_date + timedelta(days=i) for i in range(n_days)]
    
    # 基础价格
    base_price = 100
    
    # 创建复杂的市场走势
    trend = np.zeros(n_days)
    noise = np.random.normal(0, 2, n_days).cumsum()
    
    # 5个阶段: 上升趋势 -> 震荡 -> 快速拉升 -> 回调 -> 下降趋势
    # 1. 上升趋势 (0-60天)
    trend[0:60] = np.linspace(0, 25, 60)
    
    # 2. 震荡 (60-120天)
    trend[60:120] = 25 + np.sin(np.linspace(0, 8*np.pi, 60)) * 8
    
    # 3. 快速拉升 (120-180天)
    trend[120:180] = np.linspace(25, 60, 60) + np.random.normal(0, 3, 60)
    
    # 4. 回调 (180-240天)
    trend[180:240] = np.linspace(60, 40, 60) + np.sin(np.linspace(0, 4*np.pi, 60)) * 5
    
    # 5. 下降趋势 (240-300天)
    trend[240:300] = np.linspace(40, 10, 60)
    
    # 生成收盘价
    close = base_price + trend + noise * 0.5
    
    # 生成高、低价（带真实波动）
    volatility = np.abs(close.diff().fillna(0)) * 2 + 1
    high = close + np.random.uniform(0.5, 2.5, n_days) * volatility
    low = close - np.random.uniform(0.5, 2.5, n_days) * volatility
    
    # 确保high > close > low
    high = np.maximum(high, close + 0.01)
    low = np.minimum(low, close - 0.01)
    
    # 生成开盘价
    open_price = close.shift(1) + np.random.normal(0, 1, n_days)
    open_price[0] = close[0] - np.random.uniform(0, 2)
    
    # 生成成交量（与价格波动相关）
    price_change = np.abs(close.diff().fillna(0))
    volume_base = 10000 + price_change * 5000
    volume = volume_base.astype(int) + np.random.randint(-2000, 2000, n_days)
    volume = np.maximum(volume, 5000)
    
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

def test_six_factor_strategy():
    """测试六因子策略"""
    print("=" * 70)
    print("六因子策略测试")
    print("=" * 70)
    
    # 生成测试数据
    test_df = generate_realistic_test_data(n_days=300)
    print(f"测试数据: {len(test_df)}天")
    print(f"价格范围: {test_df['close'].min():.2f} - {test_df['close'].max():.2f}")
    print(f"价格变化: {((test_df['close'].iloc[-1] - test_df['close'].iloc[0]) / test_df['close'].iloc[0] * 100):.1f}%")
    print(f"成交量均值: {test_df['volume'].mean():.0f}")
    
    # 配置策略
    config = {
        'vr_period': 26,
        'macd_fast': 5,
        'macd_slow': 13,
        'macd_signal': 8,
        'fisher_period': 10,
        'chop_period': 14,
        'lsma_period': 20,
        'hma_period': 20,
        'position_max': 0.7
    }
    
    # 创建策略实例
    strategy = SixFactorStrategy(config)
    
    print("\n1. 计算六因子指标...")
    df_with_indicators = strategy.calculate_indicators(test_df)
    
    # 检查指标计算
    required_indicators = ['fisher', 'chop', 'lsma', 'hma', 'macd', 'vr', 'six_factor_score', 'market_state']
    missing = [ind for ind in required_indicators if ind not in df_with_indicators.columns]
    
    if missing:
        print(f"警告: 缺失指标 {missing}")
    else:
        print("✅ 所有六因子指标计算成功")
        
        # 显示指标基本信息
        print(f"\n六因子指标统计:")
        for indicator in required_indicators[:6]:  # 显示前6个主要指标
            if indicator in df_with_indicators.columns:
                mean_val = df_with_indicators[indicator].mean()
                std_val = df_with_indicators[indicator].std()
                non_null = df_with_indicators[indicator].notna().sum()
                print(f"  {indicator:15} 均值: {mean_val:8.3f}, 标准差: {std_val:8.3f}, 有效值: {non_null}")
    
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
        # 信号强度分析
        buy_strength = signals_df.loc[signals_df['signal'] == 1, 'signal_strength'].abs().mean()
        sell_strength = signals_df.loc[signals_df['signal'] == -1, 'signal_strength'].abs().mean()
        avg_position = signals_df.loc[signals_df['signal'] != 0, 'position_weight'].mean()
        
        print(f"平均买入信号强度: {buy_strength:.3f}")
        print(f"平均卖出信号强度: {sell_strength:.3f}")
        print(f"平均仓位权重: {avg_position:.3f}")
        
        # 信号原因分析
        print(f"\n信号原因示例:")
        sample_signals = signals_df[signals_df['signal'] != 0].head(3)
        for idx, row in sample_signals.iterrows():
            print(f"  {idx.strftime('%Y-%m-%d')}: {row['signal_reason']}")
    
    print("\n3. 策略摘要...")
    summary = strategy.get_strategy_summary()
    print(summary)
    
    # 详细分析
    print("\n4. 详细策略分析...")
    
    # 六因子得分分布
    if 'six_factor_score' in df_with_indicators.columns:
        scores = df_with_indicators['six_factor_score'].dropna()
        print(f"六因子得分统计:")
        print(f"  均值: {scores.mean():.3f}, 中位数: {scores.median():.3f}")
        print(f"  标准差: {scores.std():.3f}, 范围: [{scores.min():.3f}, {scores.max():.3f}]")
        
        # 得分分布
        score_bins = [0, 0.3, 0.4, 0.6, 0.7, 1.0]
        score_labels = ['强烈卖出区', '卖出区', '观望区', '买入区', '强烈买入区']
        
        for i in range(len(score_bins)-1):
            low, high = score_bins[i], score_bins[i+1]
            count = ((scores >= low) & (scores < high)).sum()
            percentage = count / len(scores) * 100
            print(f"  {score_labels[i]}: {count}天 ({percentage:.1f}%)")
    
    # 市场状态分析
    if 'market_state' in df_with_indicators.columns:
        state_counts = df_with_indicators['market_state'].value_counts()
        print(f"\n市场状态分布:")
        for state, count in state_counts.items():
            percentage = count / len(df_with_indicators) * 100
            print(f"  {state:8} {count:4}天 ({percentage:.1f}%)")
    
    # 因子相关性分析
    print(f"\n5. 因子相关性分析:")
    factor_columns = ['fisher', 'chop', 'lsma', 'hma', 'macd_hist', 'vr']
    available_factors = [col for col in factor_columns if col in df_with_indicators.columns]
    
    if len(available_factors) >= 2:
        # 计算价格变化
        price_returns = df_with_indicators['close'].pct_change().shift(-1)  # 下一期收益率
        
        # 计算因子与未来收益的相关性
        correlations = {}
        for factor in available_factors:
            factor_series = df_with_indicators[factor]
            # 对齐数据
            aligned_data = pd.concat([factor_series, price_returns], axis=1).dropna()
            if len(aligned_data) > 10:
                corr = aligned_data.iloc[:, 0].corr(aligned_data.iloc[:, 1])
                correlations[factor] = corr
        
        if correlations:
            print(f"因子与下一期收益的相关性:")
            for factor, corr in sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True):
                direction = "正" if corr > 0 else "负"
                print(f"  {factor:12} {corr:.4f} ({direction}相关)")
    
    return df_with_indicators, signals_df


# ==================== 可视化 ====================

def plot_six_factor_strategy(df_with_indicators, signals_df, save_path=None):
    """绘制六因子策略结果"""
    plt.figure(figsize=(16, 14))
    
    # 1. 价格走势和交易信号
    plt.subplot(5, 1, 1)
    plt.plot(df_with_indicators.index, df_with_indicators['close'], 
             label='收盘价', linewidth=2, color='black', alpha=0.8)
    plt.plot(df_with_indicators.index, df_with_indicators['lsma'], 
             label='LSMA', linewidth=1.5, color='orange', alpha=0.7)
    plt.plot(df_with_indicators.index, df_with_indicators['hma'], 
             label='Hull MA', linewidth=1.5, color='blue', alpha=0.7)
    
    # 标记交易信号
    buy_signals = signals_df[signals_df['signal'] == 1]
    sell_signals = signals_df[signals_df['signal'] == -1]
    
    if len(buy_signals) > 0:
        plt.scatter(buy_signals.index, buy_signals['close'], 
                   color='green', marker='^', s=100, label='买入信号', zorder=5, alpha=0.7)
    
    if len(sell_signals) > 0:
        plt.scatter(sell_signals.index, sell_signals['close'],
                   color='red', marker='v', s=100, label='卖出信号', zorder=5, alpha=0.7)
    
    plt.title('价格走势与交易信号 (LSMA橙色, Hull MA蓝色)', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 2. Fisher Transform
    plt.subplot(5, 1, 2)
    fisher = df_with_indicators['fisher'].dropna()
    plt.plot(fisher.index, fisher.values, label='Fisher Transform', linewidth=2, color='purple')
    plt.axhline(y=0.5, color='green', linestyle='--', alpha=0.5, label='买入阈值')
    plt.axhline(y=-0.5, color='red', linestyle='--', alpha=0.5, label='卖出阈值')
    plt.fill_between(fisher.index, 0.5, fisher.values, where=fisher.values > 0.5, 
                     color='green', alpha=0.3, label='强烈买入区')
    plt.fill_between(fisher.index, -0.5, fisher.values, where=fisher.values < -0.5,
                     color='red', alpha=0.3, label='强烈卖出区')
    plt.axhline(y=0, color='gray', linewidth=0.5)
    plt.title('Fisher Transform 指标', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 3. Choppiness Index 和市场状态
    plt.subplot(5, 1, 3)
    chop = df_with_indicators['chop'].dropna()
    plt.plot(chop.index, chop.values, label='Choppiness Index', linewidth=2, color='brown')
    plt.axhline(y=38.2, color='blue', linestyle='--', alpha=0.7, label='趋势阈值')
    plt.axhline(y=61.8, color='orange', linestyle='--', alpha=0.7, label='震荡阈值')
    
    # 填充市场状态区域
    plt.fill_between(chop.index, 0, 38.2, where=chop.values < 38.2, 
                     color='blue', alpha=0.1, label='趋势市')
    plt.fill_between(chop.index, 38.2, 61.8, color='yellow', alpha=0.1, label='中性市')
    plt.fill_between(chop.index, 61.8, 100, where=chop.values > 61.8,
                     color='orange', alpha=0.1, label='震荡市')
    
    plt.title('Choppiness Index 市场状态识别', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 100)
    
    # 4. MACD 和 VR
    plt.subplot(5, 1, 4)
    
    # MACD
    if 'macd_hist' in df_with_indicators.columns:
        macd_hist = df_with_indicators['macd_hist'].dropna()
        colors = ['green' if x > 0 else 'red' for x in macd_hist.values]
        plt.bar(macd_hist.index, macd_hist.values, color=colors, alpha=0.6, label='MACD柱状图')
        plt.axhline(y=0, color='black', linewidth=0.5)
    
    # VR（使用次坐标轴）
    if 'vr' in df_with_indicators.columns:
        ax2 = plt.gca().twinx()
        vr = df_with_indicators['vr'].dropna()
        ax2.plot(vr.index, vr.values, label='VR成交量比率', linewidth=1.5, color='gray', alpha=0.7)
        ax2.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='VR基准')
        ax2.set_ylabel('VR', color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')
    
    plt.title('MACD动量与VR成交量', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    
    # 5. 六因子综合得分和信号强度
    plt.subplot(5, 1, 5)
    
    # 六因子得分
    if 'six_factor_score' in df_with_indicators.columns:
        scores = df_with_indicators['six_factor_score'].dropna()
        plt.plot(scores.index, scores.values, label='六因子综合得分', linewidth=2, color='darkblue', alpha=0.8)
        
        # 阈值线
        plt.axhline(y=0.7, color='darkgreen', linestyle='--', alpha=0.7, label='强烈买入阈值')
        plt.axhline(y=0.6, color='green', linestyle='--', alpha=0.5, label='买入阈值')
        plt.axhline(y=0.4, color='red', linestyle='--', alpha=0.5, label='卖出阈值')
        plt.axhline(y=0.3, color='darkred', linestyle='--', alpha=0.7, label='强烈卖出阈值')
        
        # 填充信号区域
        plt.fill_between(scores.index, 0.7, 1.0, where=scores.values >= 0.7,
                        color='darkgreen', alpha=0.2, label='强烈买入区')
        plt.fill_between(scores.index, 0.6, 0.7, color='green', alpha=0.1, label='买入区')
        plt.fill_between(scores.index, 0.4, 0.6, color='yellow', alpha=0.1, label='观望区')
        plt.fill_between(scores.index, 0.3, 0.4, color='red', alpha=0.1, label='卖出区')
        plt.fill_between(scores.index, 0, 0.3, where=scores.values <= 0.3,
                        color='darkred', alpha=0.2, label='强烈卖出区')
    
    # 信号强度（使用次坐标轴）
    ax2 = plt.gca().twinx()
    if 'signal_strength' in signals_df.columns:
        signal_strength = signals_df['signal_strength'].dropna()
        colors = ['green' if x > 0 else 'red' for x in signal_strength.values]
        ax2.bar(signal_strength.index, signal_strength.values, color=colors, alpha=0.5, width=1, label='信号强度')
        ax2.axhline(y=0, color='black', linewidth=0.5)
        ax2.set_ylabel('信号强度', color='gray')
        ax2.tick_params(axis='y', labelcolor='gray')
    
    plt.title('六因子综合得分与交易信号', fontsize=12)
    plt.legend(loc='upper left')
    plt.grid(True, alpha=0.3)
    plt.ylim(0, 1)
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n图表已保存到: {save_path}")
    
    # 显示图表
    plt.show()


# ==================== 性能评估 ====================

def evaluate_strategy_performance(df_with_indicators, signals_df):
    """评估策略性能"""
    print("\n" + "=" * 70)
    print("策略性能评估")
    print("=" * 70)
    
    # 简化回测：假设每次信号都执行
    signals = signals_df.copy()
    signals['returns'] = df_with_indicators['close'].pct_change().shift(-1)  # 下一期收益率
    
    # 过滤有效信号
    valid_signals = signals[signals['signal'] != 0].copy()
    
    if len(valid_signals) == 0:
        print("无有效交易信号")
        return
    
    # 计算每次交易的收益
    valid_signals['trade_return'] = valid_signals['returns'] * valid_signals['signal']
    valid_signals['position_adjusted_return'] = valid_signals['trade_return'] * valid_signals['position_weight']
    
    # 基本统计
    total_trades = len(valid_signals)
    winning_trades = (valid_signals['trade_return'] > 0).sum()
    losing_trades = (valid_signals['trade_return'] < 0).sum()
    win_rate = winning_trades / total_trades * 100
    
    # 收益统计
    avg_return = valid_signals['trade_return'].mean() * 100
    total_return = valid_signals['trade_return'].sum() * 100
    avg_position_return = valid_signals['position_adjusted_return'].mean() * 100
    total_position_return = valid_signals['position_adjusted_return'].sum() * 100
    
    # 风险统计
    std_return = valid_signals['trade_return'].std() * 100
    max_loss = valid_signals['trade_return'].min() * 100
    max_gain = valid_signals['trade_return'].max() * 100
    
    print(f"交易统计:")
    print(f"  总交易次数: {total_trades}")
    print(f"  盈利交易: {winning_trades} ({win_rate:.1f}%)")
    print(f"  亏损交易: {losing_trades} ({100 - win_rate:.1f}%)")
    
    print(f"\n收益统计 (单次交易):")
    print(f"  平均收益: {avg_return:.2f}%")
    print(f"  总收益: {total_return:.2f}%")
    print(f"  最大单次盈利: {max_gain:.2f}%")
    print(f"  最大单次亏损: {max_loss:.2f}%")
    
    print(f"\n收益统计 (考虑仓位):")
    print(f"  平均仓位调整收益: {avg_position_return:.2f}%")
    print(f"  总仓位调整收益: {total_position_return:.2f}%")
    
    print(f"\n风险统计:")
    print(f"  收益标准差: {std_return:.2f}%")
    
    # 计算夏普比率（简化版）
    if std_return > 0:
        sharpe_ratio = avg_return / std_return * np.sqrt(252)  # 年化夏普
        print(f"  年化夏普比率: {sharpe_ratio:.2f}")
    
    # 连续盈利/亏损分析
    print(f"\n连续交易分析:")
    returns_series = valid_signals['trade_return'].values
    current_streak = 0
    max_win_streak = 0
    max_loss_streak = 0
    
    for ret in returns_series:
        if ret > 0:
            current_streak = max(current_streak, 0) + 1
            max_win_streak = max(max_win_streak, current_streak)
        else:
            current_streak = min(current_streak, 0) - 1
            max_loss_streak = min(max_loss_streak, current_streak)
    
    print(f"  最长连续盈利: {max_win_streak}次")
    print(f"  最长连续亏损: {abs(max_loss_streak)}次")
    
    # 按市场状态分析
    if 'market_state' in df_with_indicators.columns:
        print(f"\n按市场状态分析:")
        valid_signals_with_state = valid_signals.join(df_with_indicators['market_state'])
        
        for state in ['trending', 'neutral', 'choppy']:
            state_trades = valid_signals_with_state[valid_signals_with_state['market_state'] == state]
            if len(state_trades) > 0:
                state_win_rate = (state_trades['trade_return'] > 0).sum() / len(state_trades) * 100
                state_avg_return = state_trades['trade_return'].mean() * 100
                print(f"  {state:8} 交易数: {len(state_trades):3}, 胜率: {state_win_rate:5.1f}%, 平均收益: {state_avg_return:6.2f}%")


# ==================== 主函数 ====================

def main():
    """主函数"""
    print("六因子量化策略测试开始...")
    print("基于用户提供的完整六因子公式:")
    print("1. Fisher Transform")
    print("2. Choppiness Index")
    print("3. LSMA (FORCAST(C, N))")
    print("4. Hull Moving Average")
    print("5. MACD")
    print("6. VR (Volume Ratio)")
    
    try:
        # 运行策略测试
        df_with_indicators, signals_df = test_six_factor_strategy()
        
        # 性能评估
        evaluate_strategy_performance(df_with_indicators, signals_df)
        
        # 尝试绘图
        try:
            plot_six_factor_strategy(
                df_with_indicators, 
                signals_df,
                save_path='/Users/chengming/.openclaw/workspace/six_factor_strategy_results.png'
            )
        except Exception as e:
            print(f"\n绘图错误 (可能缺少GUI环境): {e}")
            print("图表数据已计算完成，可在Jupyter Notebook中查看")
        
        print("\n" + "=" * 70)
        print("🎯 六因子策略测试完成!")
        print("=" * 70)
        
        print("\n📈 策略特点总结:")
        print("  ✅ 完整六因子: Fisher, Chop, LSMA, Hull MA, MACD, VR")
        print("  ✅ 多重验证: 需要多个因子同时确认信号")
        print("  ✅ 市场适应: 自动识别趋势市/震荡市，调整策略")
        print("  ✅ 动态仓位: 信号强度决定仓位大小")
        print("  ✅ 风险控制: 震荡市减少交易，严格止损")
        
        print("\n🚀 下一步建议:")
        print("  1. 使用真实A股/期货数据测试")
        print("  2. 优化各因子权重和阈值参数")
        print("  3. 添加止损和止盈机制")
        print("  4. 进行多品种、多周期回测")
        print("  5. 实盘模拟验证")
        
        return True
        
    except Exception as e:
        print(f"\n测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ 六因子策略测试成功完成!")
    else:
        print("\n❌ 测试失败")