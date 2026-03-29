import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib import font_manager

class Visualizer:
    @staticmethod
    def plot_equity_curve(equity_curve, drawdown_series, trades_list):
        """绘制资金曲线和回撤 - 修复版本"""
        # 确保equity_curve是Series
        if not isinstance(equity_curve, pd.Series):
            print("警告: equity_curve 不是 pandas Series，尝试转换")
            if hasattr(equity_curve, 'values'):
                equity_curve = pd.Series(equity_curve.values, index=range(len(equity_curve)))
            else:
                equity_curve = pd.Series(equity_curve)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), sharex=True)
        
        # 绘制资金曲线
        ax1.plot(equity_curve.index, equity_curve.values, linewidth=2, label='Equity Curve', color='blue')
        ax1.set_ylabel('Portfolio Value')
        ax1.set_title('Portfolio Equity Curve')
        ax1.grid(True, alpha=0.3)
        ax1.legend()
        
        # 绘制交易信号
        if trades_list:
            Visualizer._plot_trade_signals_safe(ax1, equity_curve, trades_list)
        
        # 绘制回撤
        if drawdown_series is not None:
            if not isinstance(drawdown_series, pd.Series):
                # 如果drawdown_series不是Series，尝试创建
                if hasattr(drawdown_series, '__len__') and len(drawdown_series) == len(equity_curve):
                    drawdown_series = pd.Series(drawdown_series, index=equity_curve.index)
                else:
                    print("警告: drawdown_series 格式不正确，跳过绘制")
            else:
                ax2.fill_between(drawdown_series.index, drawdown_series.values, 0, alpha=0.3, color='red', label='Drawdown')
                ax2.set_ylabel('Drawdown (%)')
                ax2.set_xlabel('Date')
                ax2.set_title('Portfolio Drawdown')
                ax2.grid(True, alpha=0.3)
                ax2.legend()
        
        plt.tight_layout()
        plt.show()

    @staticmethod
    def _plot_trade_signals_safe(ax, equity_curve, trades_list):
        """安全地绘制交易信号 - 修复版本"""
        if not trades_list:
            return
            
        # 将交易列表转换为DataFrame
        df_trades = pd.DataFrame(trades_list)
        
        # 确保时间戳类型正确
        df_trades['timestamp'] = pd.to_datetime(df_trades['timestamp'])
        
        # 分离买入和卖出信号
        buys = df_trades[df_trades['action'].isin(['buy', 'cover_short'])]
        sells = df_trades[df_trades['action'].isin(['sell', 'short'])]
        
        # 为买入信号找到对应的equity值
        buy_x = []
        buy_y = []
        
        for _, trade in buys.iterrows():
            timestamp = trade['timestamp']
            # 找到最接近的时间点
            if isinstance(equity_curve.index, pd.DatetimeIndex):
                # 对于时间序列，找到最接近的时间点
                time_diff = abs(equity_curve.index - timestamp)
                if len(time_diff) > 0:
                    closest_idx = time_diff.argmin()
                    closest_time = equity_curve.index[closest_idx]
                    buy_x.append(closest_time)
                    buy_y.append(equity_curve.iloc[closest_idx])
        
        # 为卖出信号找到对应的equity值
        sell_x = []
        sell_y = []
        
        for _, trade in sells.iterrows():
            timestamp = trade['timestamp']
            # 找到最接近的时间点
            if isinstance(equity_curve.index, pd.DatetimeIndex):
                time_diff = abs(equity_curve.index - timestamp)
                if len(time_diff) > 0:
                    closest_idx = time_diff.argmin()
                    closest_time = equity_curve.index[closest_idx]
                    sell_x.append(closest_time)
                    sell_y.append(equity_curve.iloc[closest_idx])
        
        # 绘制信号点
        if buy_x and buy_y and len(buy_x) == len(buy_y):
            ax.scatter(buy_x, buy_y, color='green', marker='^', label='Buy/Cover', s=100, zorder=5)
        if sell_x and sell_y and len(sell_x) == len(sell_y):
            ax.scatter(sell_x, sell_y, color='red', marker='v', label='Sell/Short', s=100, zorder=5)
        
        if buy_x or sell_x:
            ax.legend()

    @staticmethod
    def plot_trade_analysis(trades_list):
        """绘制交易分析"""
        if not trades_list:
            print("无交易数据可分析")
            return
            
        df_trades = pd.DataFrame(trades_list)
        
        # 确保有时间戳列
        if 'timestamp' not in df_trades.columns:
            print("警告: 交易数据缺少时间戳，无法绘制时间序列图")
            return
        
        df_trades['timestamp'] = pd.to_datetime(df_trades['timestamp'])
        df_trades = df_trades.sort_values('timestamp')
        
        # 计算每笔交易的盈亏
        profitable_trades = df_trades[df_trades['profit'] > 0]
        losing_trades = df_trades[df_trades['profit'] < 0]
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # 盈亏分布
        if len(df_trades) > 0:
            axes[0, 0].hist(df_trades['profit'], bins=30, alpha=0.7, color='skyblue')
            axes[0, 0].axvline(0, color='red', linestyle='--', linewidth=1)
            axes[0, 0].set_title('Profit Distribution')
            axes[0, 0].set_xlabel('Profit')
            axes[0, 0].set_ylabel('Frequency')
        
        # 胜率饼图
        win_rate = len(profitable_trades) / len(df_trades) if len(df_trades) > 0 else 0
        labels = ['Winning Trades', 'Losing Trades']
        sizes = [len(profitable_trades), len(losing_trades)]
        colors = ['lightgreen', 'lightcoral']
        
        if sum(sizes) > 0:
            axes[0, 1].pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            axes[0, 1].set_title(f'Win Rate: {win_rate:.1%}')
        
        # 累计盈亏曲线
        if len(df_trades) > 0:
            df_trades['cumulative_profit'] = df_trades['profit'].cumsum()
            axes[1, 0].plot(df_trades['timestamp'], df_trades['cumulative_profit'], linewidth=2, color='blue')
            axes[1, 0].set_title('Cumulative Profit')
            axes[1, 0].set_xlabel('Date')
            axes[1, 0].set_ylabel('Cumulative Profit')
            axes[1, 0].grid(True, alpha=0.3)
        
        # 单笔盈亏分布
        if len(profitable_trades) > 0 or len(losing_trades) > 0:
            bp_data = []
            labels = []
            if len(profitable_trades) > 0:
                bp_data.append(profitable_trades['profit'].values)
                labels.append('Profitable')
            if len(losing_trades) > 0:
                bp_data.append(losing_trades['profit'].values)
                labels.append('Losing')
            
            axes[1, 1].boxplot(bp_data, labels=labels)
            axes[1, 1].set_title('Profit/Loss by Trade Type')
            axes[1, 1].set_ylabel('Profit')
        
        plt.tight_layout()
        plt.show()