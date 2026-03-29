#!/usr/bin/env python3
"""
统一可视化系统 - 量化交易分析可视化工具

功能:
1. 价格与信号图表
2. 绩效指标可视化
3. 风险分析图表
4. 信号分布可视化
5. 多时间框架对比

设计原则:
- 无外部依赖: 主要使用matplotlib + seaborn (可选)
- 模块化: 独立图表组件，易于组合
- 生产就绪: 错误处理，配置灵活，结果保存
- 用户友好: 简单API，默认配置，详细文档
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
import warnings

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib import ticker
    from matplotlib.patches import Rectangle
    from matplotlib.lines import Line2D
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    warnings.warn("matplotlib not available, visualization disabled")

try:
    import seaborn as sns
    SEABORN_AVAILABLE = True
except ImportError:
    SEABORN_AVAILABLE = False

# 可选依赖: 如果可用则提供高级功能
try:
    from mplfinance.original_flavor import candlestick_ohlc
    CANDLESTICK_AVAILABLE = True
except ImportError:
    CANDLESTICK_AVAILABLE = False

class TradingVisualizer:
    """统一交易可视化系统"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化可视化系统
        
        Args:
            config: 配置字典，包含:
                - output_dir: 输出目录 (默认: './visualization_output')
                - style: matplotlib样式 (默认: 'seaborn' 如果可用)
                - figure_size: 图表尺寸 (默认: (12, 8))
                - dpi: 图像DPI (默认: 100)
                - save_format: 保存格式 (默认: 'png')
                - color_scheme: 颜色方案 (默认: 'trading')
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', './visualization_output')
        self.figure_size = self.config.get('figure_size', (12, 8))
        self.dpi = self.config.get('dpi', 100)
        self.save_format = self.config.get('save_format', 'png')
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置颜色方案
        self._setup_color_scheme()
        
        # 设置matplotlib样式
        self._setup_style()
    
    def _setup_color_scheme(self):
        """设置交易专用的颜色方案"""
        self.colors = {
            # 基础颜色
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'tertiary': '#2ca02c',
            'quaternary': '#d62728',
            
            # 交易专用
            'buy': '#2ca02c',      # 绿色 - 买入
            'sell': '#d62728',     # 红色 - 卖出
            'hold': '#9467bd',     # 紫色 - 持有
            'signal': '#ff7f0e',   # 橙色 - 信号
            
            # 价格
            'price_up': '#2ca02c', # 上涨
            'price_down': '#d62728', # 下跌
            
            # 技术指标
            'ma_short': '#ff7f0e', # 短期均线
            'ma_medium': '#1f77b4', # 中期均线
            'ma_long': '#9467bd',  # 长期均线
            
            # 风险
            'risk_high': '#d62728', # 高风险
            'risk_medium': '#ff7f0e', # 中风险
            'risk_low': '#2ca02c', # 低风险
            
            # 背景
            'background': '#f5f5f5',
            'grid': '#e0e0e0',
            'text': '#333333'
        }
    
    def _setup_style(self):
        """设置matplotlib样式"""
        if not MATPLOTLIB_AVAILABLE:
            return
            
        # 使用seaborn样式如果可用
        if SEABORN_AVAILABLE:
            sns.set_style("whitegrid")
            sns.set_palette("husl")
        else:
            plt.style.use('default')
            
        # 设置中文字体支持 (如果可用)
        try:
            import matplotlib.font_manager as fm
            # 尝试使用系统字体
            plt.rcParams['font.sans-serif'] = ['Arial Unicode MS', 'DejaVu Sans', 'Microsoft YaHei']
            plt.rcParams['axes.unicode_minus'] = False
        except:
            pass
    
    def plot_price_with_signals(self, 
                               price_data: pd.DataFrame,
                               signals: Optional[List[Dict]] = None,
                               indicators: Optional[Dict[str, pd.Series]] = None,
                               title: str = "价格与交易信号",
                               save_path: Optional[str] = None) -> Optional[str]:
        """
        绘制价格图表与交易信号
        
        Args:
            price_data: OHLCV数据DataFrame，需包含'open','high','low','close','volume'
            signals: 信号列表，每个信号包含:
                - timestamp: 时间戳
                - type: 'buy'/'sell'/'hold'
                - price: 价格
                - reason: 信号原因
                - confidence: 置信度 (0-1)
            indicators: 技术指标字典，键为指标名，值为pd.Series
            title: 图表标题
            save_path: 保存路径，如为None则自动生成
            
        Returns:
            保存的文件路径，如不保存则返回None
        """
        if not MATPLOTLIB_AVAILABLE:
            warnings.warn("matplotlib not available, skipping visualization")
            return None
            
        fig, axes = plt.subplots(2, 1, figsize=self.figure_size, 
                                 gridspec_kw={'height_ratios': [3, 1]})
        
        # 主图: 价格和信号
        ax_price = axes[0]
        
        # 准备日期格式
        if 'date' in price_data.columns and pd.api.types.is_datetime64_any_dtype(price_data['date']):
            dates = price_data['date']
        elif pd.api.types.is_datetime64_any_dtype(price_data.index):
            dates = price_data.index
        else:
            # 创建虚拟日期
            dates = pd.date_range(start='2020-01-01', periods=len(price_data), freq='D')
        
        # 绘制价格线
        ax_price.plot(dates, price_data['close'], 
                     color=self.colors['primary'], 
                     linewidth=1.5, 
                     label='收盘价')
        
        # 绘制技术指标
        if indicators:
            for name, values in indicators.items():
                if len(values) == len(price_data):
                    ax_price.plot(dates, values, 
                                 linewidth=1, 
                                 alpha=0.7, 
                                 label=name)
        
        # 绘制交易信号
        if signals:
            buy_signals = [s for s in signals if s.get('type') == 'buy']
            sell_signals = [s for s in signals if s.get('type') == 'sell']
            
            if buy_signals:
                buy_dates = [s['timestamp'] for s in buy_signals]
                buy_prices = [s['price'] for s in buy_signals]
                ax_price.scatter(buy_dates, buy_prices, 
                               color=self.colors['buy'], 
                               s=100, marker='^', 
                               label='买入信号', 
                               zorder=5)
            
            if sell_signals:
                sell_dates = [s['timestamp'] for s in sell_signals]
                sell_prices = [s['price'] for s in sell_signals]
                ax_price.scatter(sell_dates, sell_prices, 
                               color=self.colors['sell'], 
                               s=100, marker='v', 
                               label='卖出信号', 
                               zorder=5)
        
        # 设置主图属性
        ax_price.set_title(title, fontsize=14, fontweight='bold')
        ax_price.set_ylabel('价格', fontsize=12)
        ax_price.legend(loc='upper left')
        ax_price.grid(True, alpha=0.3)
        
        # 格式化x轴日期
        ax_price.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax_price.xaxis.get_majorticklabels(), rotation=45)
        
        # 副图: 成交量
        ax_volume = axes[1]
        
        if 'volume' in price_data.columns:
            # 创建成交量柱状图 (红色下跌，绿色上涨)
            volume_colors = []
            for i in range(len(price_data)):
                if i == 0:
                    volume_colors.append(self.colors['primary'])
                else:
                    if price_data['close'].iloc[i] >= price_data['close'].iloc[i-1]:
                        volume_colors.append(self.colors['price_up'])
                    else:
                        volume_colors.append(self.colors['price_down'])
            
            ax_volume.bar(dates, price_data['volume'], 
                         color=volume_colors, 
                         alpha=0.7, 
                         width=0.8)
        
        ax_volume.set_ylabel('成交量', fontsize=12)
        ax_volume.grid(True, alpha=0.3)
        
        # 格式化副图x轴
        ax_volume.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
        plt.setp(ax_volume.xaxis.get_majorticklabels(), rotation=45)
        
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            full_path = save_path
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            full_path = os.path.join(self.output_dir, f'price_signals_{timestamp}.{self.save_format}')
        
        plt.savefig(full_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return full_path
    
    def plot_performance_metrics(self,
                                performance_data: Dict,
                                benchmark_data: Optional[Dict] = None,
                                title: str = "策略绩效分析",
                                save_path: Optional[str] = None) -> Optional[str]:
        """
        绘制策略绩效指标图表
        
        Args:
            performance_data: 绩效数据字典，包含:
                - returns: 收益率序列
                - cumulative_returns: 累计收益率
                - drawdown: 回撤序列
                - metrics: 绩效指标字典
            benchmark_data: 基准数据 (同上结构)
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            warnings.warn("matplotlib not available, skipping visualization")
            return None
            
        # 创建子图
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 1. 累计收益率
        ax1 = axes[0, 0]
        
        # 策略累计收益率
        if 'cumulative_returns' in performance_data:
            cum_returns = performance_data['cumulative_returns']
            if isinstance(cum_returns, pd.Series):
                dates = cum_returns.index
            else:
                dates = range(len(cum_returns))
            
            ax1.plot(dates, cum_returns, 
                    color=self.colors['primary'], 
                    linewidth=2, 
                    label='策略')
        
        # 基准累计收益率
        if benchmark_data and 'cumulative_returns' in benchmark_data:
            bench_cum_returns = benchmark_data['cumulative_returns']
            if isinstance(bench_cum_returns, pd.Series):
                bench_dates = bench_cum_returns.index
            else:
                bench_dates = range(len(bench_cum_returns))
            
            ax1.plot(bench_dates, bench_cum_returns, 
                    color=self.colors['secondary'], 
                    linewidth=2, 
                    alpha=0.7, 
                    label='基准')
        
        ax1.set_title('累计收益率', fontsize=12, fontweight='bold')
        ax1.set_ylabel('累计收益率 (%)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 收益率分布
        ax2 = axes[0, 1]
        
        if 'returns' in performance_data:
            returns = performance_data['returns']
            # 移除NaN值
            returns_clean = returns[~np.isnan(returns)]
            
            if len(returns_clean) > 0:
                ax2.hist(returns_clean, bins=50, 
                        color=self.colors['primary'], 
                        alpha=0.7, 
                        edgecolor='black')
                
                # 添加统计信息
                mean_return = np.mean(returns_clean)
                std_return = np.std(returns_clean)
                
                ax2.axvline(mean_return, color='red', linestyle='--', linewidth=2, 
                           label=f'均值: {mean_return:.2%}')
                ax2.axvline(mean_return + std_return, color='orange', linestyle=':', linewidth=1)
                ax2.axvline(mean_return - std_return, color='orange', linestyle=':', linewidth=1)
                
                ax2.legend()
        
        ax2.set_title('收益率分布', fontsize=12, fontweight='bold')
        ax2.set_xlabel('收益率')
        ax2.set_ylabel('频次')
        ax2.grid(True, alpha=0.3)
        
        # 3. 回撤分析
        ax3 = axes[1, 0]
        
        if 'drawdown' in performance_data:
            drawdown = performance_data['drawdown']
            if isinstance(drawdown, pd.Series):
                drawdown_dates = drawdown.index
            else:
                drawdown_dates = range(len(drawdown))
            
            # 填充回撤区域
            ax3.fill_between(drawdown_dates, 0, drawdown, 
                            color=self.colors['risk_high'], 
                            alpha=0.5, 
                            label='回撤')
            
            # 标记最大回撤
            if 'metrics' in performance_data and 'max_drawdown' in performance_data['metrics']:
                max_dd = performance_data['metrics']['max_drawdown']
                if 'max_drawdown_period' in performance_data['metrics']:
                    max_dd_period = performance_data['metrics']['max_drawdown_period']
                    if len(max_dd_period) == 2:
                        ax3.axvspan(max_dd_period[0], max_dd_period[1], 
                                   color='red', alpha=0.2, 
                                   label=f'最大回撤: {max_dd:.2%}')
        
        ax3.set_title('回撤分析', fontsize=12, fontweight='bold')
        ax3.set_ylabel('回撤 (%)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # 4. 月度收益率热图
        ax4 = axes[1, 1]
        
        if 'returns' in performance_data and isinstance(performance_data['returns'], pd.Series):
            returns_series = performance_data['returns']
            
            # 转换为DataFrame用于热图
            try:
                returns_df = returns_series.to_frame('returns')
                returns_df['year'] = returns_df.index.year
                returns_df['month'] = returns_df.index.month
                
                # 创建透视表
                monthly_returns = returns_df.pivot_table(
                    values='returns', 
                    index='year', 
                    columns='month', 
                    aggfunc='sum'
                )
                
                # 重命名月份
                month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                              'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
                monthly_returns.columns = month_names[:monthly_returns.shape[1]]
                
                # 创建热图
                im = ax4.imshow(monthly_returns.values * 100, cmap='RdYlGn', aspect='auto')
                
                # 添加文本
                for i in range(monthly_returns.shape[0]):
                    for j in range(monthly_returns.shape[1]):
                        value = monthly_returns.iloc[i, j]
                        if not np.isnan(value):
                            color = 'white' if abs(value) > 0.05 else 'black'
                            ax4.text(j, i, f'{value:.1%}', 
                                    ha='center', va='center', 
                                    color=color, fontsize=8)
                
                # 设置坐标轴
                ax4.set_xticks(range(monthly_returns.shape[1]))
                ax4.set_xticklabels(monthly_returns.columns)
                ax4.set_yticks(range(monthly_returns.shape[0]))
                ax4.set_yticklabels(monthly_returns.index)
                
                # 添加颜色条
                plt.colorbar(im, ax=ax4, label='收益率 (%)')
                
            except Exception as e:
                # 如果热图失败，显示错误信息
                ax4.text(0.5, 0.5, f'热图生成失败:\n{str(e)}', 
                        ha='center', va='center', 
                        transform=ax4.transAxes)
                ax4.set_title('月度收益率热图 (数据不足)', fontsize=12)
        
        ax4.set_title('月度收益率热图', fontsize=12, fontweight='bold')
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            full_path = save_path
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            full_path = os.path.join(self.output_dir, f'performance_{timestamp}.{self.save_format}')
        
        plt.savefig(full_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return full_path
    
    def plot_risk_analysis(self,
                          risk_data: Dict,
                          title: str = "风险分析报告",
                          save_path: Optional[str] = None) -> Optional[str]:
        """
        绘制风险分析图表
        
        Args:
            risk_data: 风险数据字典，包含:
                - var_series: VaR序列
                - cvar_series: CVaR序列
                - risk_metrics: 风险指标字典
                - correlation_matrix: 相关性矩阵
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE:
            warnings.warn("matplotlib not available, skipping visualization")
            return None
            
        # 根据可用数据确定子图数量
        num_plots = 0
        if 'var_series' in risk_data or 'cvar_series' in risk_data:
            num_plots += 1
        if 'correlation_matrix' in risk_data:
            num_plots += 1
        if 'risk_metrics' in risk_data:
            num_plots += 1
        
        if num_plots == 0:
            return None
        
        fig, axes = plt.subplots(1, num_plots, figsize=(5 * num_plots, 5))
        if num_plots == 1:
            axes = [axes]
        
        plot_idx = 0
        
        # 1. VaR/CVaR图表
        if 'var_series' in risk_data or 'cvar_series' in risk_data:
            ax = axes[plot_idx]
            
            # 绘制收益率分布
            if 'returns' in risk_data:
                returns = risk_data['returns']
                returns_clean = returns[~np.isnan(returns)]
                
                if len(returns_clean) > 0:
                    ax.hist(returns_clean, bins=50, 
                           color=self.colors['primary'], 
                           alpha=0.7, 
                           density=True, 
                           edgecolor='black')
            
            # 绘制VaR线
            if 'var_series' in risk_data and 'var_value' in risk_data.get('risk_metrics', {}):
                var_value = risk_data['risk_metrics']['var_value']
                ax.axvline(var_value, color='red', linestyle='--', linewidth=2, 
                          label=f'VaR ({risk_data.get("var_confidence", 95)}%): {var_value:.2%}')
            
            # 绘制CVaR线
            if 'cvar_series' in risk_data and 'cvar_value' in risk_data.get('risk_metrics', {}):
                cvar_value = risk_data['risk_metrics']['cvar_value']
                ax.axvline(cvar_value, color='darkred', linestyle='--', linewidth=2, 
                          label=f'CVaR: {cvar_value:.2%}')
            
            ax.set_title('风险价值 (VaR/CVaR)', fontsize=12, fontweight='bold')
            ax.set_xlabel('收益率')
            ax.set_ylabel('概率密度')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            plot_idx += 1
        
        # 2. 相关性矩阵热图
        if 'correlation_matrix' in risk_data:
            ax = axes[plot_idx] if plot_idx < len(axes) else None
            
            if ax is not None:
                corr_matrix = risk_data['correlation_matrix']
                
                # 创建热图
                if isinstance(corr_matrix, pd.DataFrame):
                    im = ax.imshow(corr_matrix.values, cmap='RdYlBu_r', vmin=-1, vmax=1)
                    
                    # 添加文本
                    for i in range(corr_matrix.shape[0]):
                        for j in range(corr_matrix.shape[1]):
                            value = corr_matrix.iloc[i, j]
                            color = 'white' if abs(value) > 0.5 else 'black'
                            ax.text(j, i, f'{value:.2f}', 
                                   ha='center', va='center', 
                                   color=color, fontsize=8)
                    
                    # 设置坐标轴
                    ax.set_xticks(range(corr_matrix.shape[1]))
                    ax.set_xticklabels(corr_matrix.columns, rotation=45, ha='right')
                    ax.set_yticks(range(corr_matrix.shape[0]))
                    ax.set_yticklabels(corr_matrix.index)
                    
                    # 添加颜色条
                    plt.colorbar(im, ax=ax, label='相关性')
                
                ax.set_title('资产相关性矩阵', fontsize=12, fontweight='bold')
                plot_idx += 1
        
        # 3. 风险指标条形图
        if 'risk_metrics' in risk_data and plot_idx < len(axes):
            ax = axes[plot_idx]
            
            risk_metrics = risk_data['risk_metrics']
            
            # 选择要显示的风险指标
            display_metrics = {
                'volatility': '波动率',
                'sharpe_ratio': '夏普比率',
                'sortino_ratio': '索提诺比率',
                'max_drawdown': '最大回撤',
                'var_value': 'VaR',
                'cvar_value': 'CVaR'
            }
            
            metrics_to_show = {}
            for key, label in display_metrics.items():
                if key in risk_metrics:
                    metrics_to_show[label] = risk_metrics[key]
            
            if metrics_to_show:
                # 创建条形图
                bars = ax.bar(range(len(metrics_to_show)), 
                            list(metrics_to_show.values()), 
                            color=[self.colors['primary']] * len(metrics_to_show))
                
                # 根据值设置颜色
                for i, (label, value) in enumerate(metrics_to_show.items()):
                    if 'drawdown' in label.lower() or 'var' in label.lower() or value < 0:
                        bars[i].set_color(self.colors['risk_high'])
                    elif 'ratio' in label.lower() and value > 1:
                        bars[i].set_color(self.colors['risk_low'])
                    elif 'ratio' in label.lower() and value <= 1:
                        bars[i].set_color(self.colors['risk_medium'])
                
                # 添加数值标签
                for i, (label, value) in enumerate(metrics_to_show.items()):
                    if 'ratio' in label.lower():
                        text = f'{value:.2f}'
                    else:
                        text = f'{value:.2%}' if abs(value) < 1 else f'{value:.2f}'
                    
                    ax.text(i, value, text, 
                           ha='center', va='bottom' if value >= 0 else 'top', 
                           fontsize=9, fontweight='bold')
                
                ax.set_xticks(range(len(metrics_to_show)))
                ax.set_xticklabels(list(metrics_to_show.keys()), rotation=45, ha='right')
                ax.set_title('风险指标概览', fontsize=12, fontweight='bold')
                ax.grid(True, alpha=0.3, axis='y')
                
                plot_idx += 1
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            full_path = save_path
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            full_path = os.path.join(self.output_dir, f'risk_analysis_{timestamp}.{self.save_format}')
        
        plt.savefig(full_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return full_path
    
    def plot_strategy_comparison(self,
                               strategies_data: List[Dict],
                               comparison_metric: str = 'cumulative_returns',
                               title: str = "策略对比分析",
                               save_path: Optional[str] = None) -> Optional[str]:
        """
        绘制多策略对比图表
        
        Args:
            strategies_data: 策略数据列表，每个元素包含:
                - name: 策略名称
                - returns: 收益率序列
                - cumulative_returns: 累计收益率
                - metrics: 绩效指标
            comparison_metric: 对比指标 ('returns', 'cumulative_returns', 'drawdown')
            title: 图表标题
            save_path: 保存路径
            
        Returns:
            保存的文件路径
        """
        if not MATPLOTLIB_AVAILABLE or len(strategies_data) == 0:
            warnings.warn("matplotlib not available or no data, skipping visualization")
            return None
            
        fig, axes = plt.subplots(2, 2, figsize=(14, 10))
        
        # 颜色循环
        colors = plt.cm.tab10(np.linspace(0, 1, len(strategies_data)))
        
        # 1. 累计收益率对比
        ax1 = axes[0, 0]
        
        for i, strategy in enumerate(strategies_data):
            if 'cumulative_returns' in strategy:
                cum_returns = strategy['cumulative_returns']
                if isinstance(cum_returns, pd.Series):
                    dates = cum_returns.index
                else:
                    dates = range(len(cum_returns))
                
                ax1.plot(dates, cum_returns, 
                        color=colors[i], 
                        linewidth=2, 
                        label=strategy.get('name', f'策略{i+1}'))
        
        ax1.set_title('累计收益率对比', fontsize=12, fontweight='bold')
        ax1.set_ylabel('累计收益率 (%)')
        ax1.legend(loc='best')
        ax1.grid(True, alpha=0.3)
        
        # 2. 回撤对比
        ax2 = axes[0, 1]
        
        for i, strategy in enumerate(strategies_data):
            if 'drawdown' in strategy:
                drawdown = strategy['drawdown']
                if isinstance(drawdown, pd.Series):
                    dates = drawdown.index
                else:
                    dates = range(len(drawdown))
                
                ax2.plot(dates, drawdown, 
                        color=colors[i], 
                        linewidth=1.5, 
                        alpha=0.7, 
                        label=strategy.get('name', f'策略{i+1}'))
        
        ax2.set_title('回撤对比', fontsize=12, fontweight='bold')
        ax2.set_ylabel('回撤 (%)')
        ax2.legend(loc='best')
        ax2.grid(True, alpha=0.3)
        
        # 3. 月度收益率对比 (热图风格)
        ax3 = axes[1, 0]
        
        # 准备月度收益率数据
        monthly_data = []
        strategy_names = []
        
        for strategy in strategies_data:
            if 'returns' in strategy and isinstance(strategy['returns'], pd.Series):
                returns_series = strategy['returns']
                strategy_names.append(strategy.get('name', '未知策略'))
                
                # 计算年化收益率
                try:
                    annual_return = (1 + returns_series.mean()) ** 252 - 1
                    monthly_data.append(annual_return)
                except:
                    monthly_data.append(np.nan)
        
        if monthly_data:
            # 创建条形图
            bars = ax3.bar(range(len(monthly_data)), monthly_data, 
                          color=colors[:len(monthly_data)])
            
            # 添加数值标签
            for i, value in enumerate(monthly_data):
                if not np.isnan(value):
                    ax3.text(i, value, f'{value:.2%}', 
                            ha='center', va='bottom' if value >= 0 else 'top', 
                            fontsize=9, fontweight='bold')
            
            ax3.set_xticks(range(len(monthly_data)))
            ax3.set_xticklabels(strategy_names, rotation=45, ha='right')
            ax3.set_title('年化收益率对比', fontsize=12, fontweight='bold')
            ax3.set_ylabel('年化收益率')
            ax3.grid(True, alpha=0.3, axis='y')
        
        # 4. 绩效指标雷达图
        ax4 = axes[1, 1]
        
        # 选择要对比的指标
        comparison_metrics = ['sharpe_ratio', 'sortino_ratio', 'max_drawdown', 'win_rate', 'profit_factor']
        
        # 收集数据
        metric_data = []
        valid_strategies = []
        
        for strategy in strategies_data:
            if 'metrics' in strategy:
                metrics = strategy['metrics']
                valid_metrics = []
                
                for metric_name in comparison_metrics:
                    if metric_name in metrics:
                        value = metrics[metric_name]
                        # 标准化处理
                        if metric_name == 'max_drawdown':
                            # 回撤越小越好，取倒数
                            value = 1 / (abs(value) + 0.01)
                        valid_metrics.append(value)
                
                if len(valid_metrics) == len(comparison_metrics):
                    metric_data.append(valid_metrics)
                    valid_strategies.append(strategy.get('name', '未知策略'))
        
        if len(metric_data) >= 2:
            # 创建雷达图
            angles = np.linspace(0, 2 * np.pi, len(comparison_metrics), endpoint=False).tolist()
            angles += angles[:1]  # 闭合图形
            
            for i, data in enumerate(metric_data):
                # 归一化数据
                data_norm = data / np.max(np.abs(data))
                data_norm = np.concatenate([data_norm, [data_norm[0]]])  # 闭合图形
                
                ax4.plot(angles, data_norm, color=colors[i], linewidth=2, label=valid_strategies[i])
                ax4.fill(angles, data_norm, color=colors[i], alpha=0.1)
            
            # 设置雷达图坐标
            ax4.set_xticks(angles[:-1])
            ax4.set_xticklabels([m.replace('_', ' ').title() for m in comparison_metrics])
            ax4.set_title('绩效指标雷达图', fontsize=12, fontweight='bold')
            ax4.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
            ax4.grid(True)
        else:
            # 如果雷达图数据不足，显示策略数量
            ax4.text(0.5, 0.5, f'共 {len(strategies_data)} 个策略\n进行对比分析', 
                    ha='center', va='center', transform=ax4.transAxes, fontsize=14)
            ax4.set_title('策略对比概览', fontsize=12, fontweight='bold')
            ax4.axis('off')
        
        plt.suptitle(title, fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # 保存或显示
        if save_path:
            full_path = save_path
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            full_path = os.path.join(self.output_dir, f'strategy_comparison_{timestamp}.{self.save_format}')
        
        plt.savefig(full_path, dpi=self.dpi, bbox_inches='tight')
        plt.close()
        
        return full_path
    
    def create_dashboard_report(self,
                               analysis_results: Dict,
                               output_dir: Optional[str] = None,
                               report_name: str = "交易分析仪表板") -> Dict[str, str]:
        """
        创建完整的交易分析仪表板报告
        
        Args:
            analysis_results: 分析结果字典，包含:
                - price_data: 价格数据
                - signals: 交易信号
                - performance: 绩效数据
                - risk: 风险数据
                - strategies: 策略数据列表
            output_dir: 输出目录
            report_name: 报告名称
            
        Returns:
            生成的图表文件路径字典
        """
        if output_dir:
            self.output_dir = output_dir
            os.makedirs(self.output_dir, exist_ok=True)
        
        generated_files = {}
        
        # 1. 价格与信号图表
        if 'price_data' in analysis_results:
            price_data = analysis_results['price_data']
            signals = analysis_results.get('signals', [])
            indicators = analysis_results.get('indicators', {})
            
            price_chart = self.plot_price_with_signals(
                price_data=price_data,
                signals=signals,
                indicators=indicators,
                title=f"{report_name} - 价格与信号"
            )
            
            if price_chart:
                generated_files['price_chart'] = price_chart
        
        # 2. 绩效分析图表
        if 'performance' in analysis_results:
            performance_data = analysis_results['performance']
            benchmark_data = analysis_results.get('benchmark', None)
            
            performance_chart = self.plot_performance_metrics(
                performance_data=performance_data,
                benchmark_data=benchmark_data,
                title=f"{report_name} - 绩效分析"
            )
            
            if performance_chart:
                generated_files['performance_chart'] = performance_chart
        
        # 3. 风险分析图表
        if 'risk' in analysis_results:
            risk_data = analysis_results['risk']
            
            risk_chart = self.plot_risk_analysis(
                risk_data=risk_data,
                title=f"{report_name} - 风险分析"
            )
            
            if risk_chart:
                generated_files['risk_chart'] = risk_chart
        
        # 4. 策略对比图表
        if 'strategies' in analysis_results and len(analysis_results['strategies']) > 1:
            strategies_data = analysis_results['strategies']
            
            comparison_chart = self.plot_strategy_comparison(
                strategies_data=strategies_data,
                title=f"{report_name} - 策略对比"
            )
            
            if comparison_chart:
                generated_files['comparison_chart'] = comparison_chart
        
        # 5. 生成报告摘要HTML
        html_report = self._generate_html_report(generated_files, analysis_results, report_name)
        if html_report:
            generated_files['html_report'] = html_report
        
        return generated_files
    
    def _generate_html_report(self,
                             chart_files: Dict[str, str],
                             analysis_results: Dict,
                             report_name: str) -> Optional[str]:
        """
        生成HTML格式的报告摘要
        
        Args:
            chart_files: 图表文件路径字典
            analysis_results: 分析结果
            report_name: 报告名称
            
        Returns:
            HTML文件路径
        """
        try:
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{report_name}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f8f9fa;
        }}
        .header {{
            background: linear-gradient(135deg, #1f77b4 0%, #2ca02c 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5em;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.9;
        }}
        .section {{
            background: white;
            padding: 25px;
            border-radius: 8px;
            margin-bottom: 25px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }}
        .section h2 {{
            color: #1f77b4;
            border-bottom: 2px solid #e9ecef;
            padding-bottom: 10px;
            margin-top: 0;
        }}
        .chart-container {{
            text-align: center;
            margin: 20px 0;
        }}
        .chart-container img {{
            max-width: 100%;
            height: auto;
            border: 1px solid #dee2e6;
            border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        .metric-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 6px;
            border-left: 4px solid #1f77b4;
        }}
        .metric-card h3 {{
            margin: 0 0 10px;
            color: #495057;
            font-size: 1.1em;
        }}
        .metric-value {{
            font-size: 1.8em;
            font-weight: bold;
            color: #1f77b4;
        }}
        .metric-positive {{ color: #2ca02c; }}
        .metric-negative {{ color: #d62728; }}
        .metric-neutral {{ color: #6c757d; }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #dee2e6;
            color: #6c757d;
            font-size: 0.9em;
        }}
        @media (max-width: 768px) {{
            .header h1 {{ font-size: 2em; }}
            .metrics-grid {{ grid-template-columns: 1fr; }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{report_name}</h1>
        <p>生成时间: {timestamp} | 量化交易分析仪表板</p>
    </div>
"""
            
            # 添加绩效指标部分
            if 'performance' in analysis_results and 'metrics' in analysis_results['performance']:
                metrics = analysis_results['performance']['metrics']
                
                html_content += """
    <div class="section">
        <h2>📊 关键绩效指标</h2>
        <div class="metrics-grid">
"""
                
                metric_display = [
                    ('累计收益率', 'cumulative_return', 'percentage', True),
                    ('年化收益率', 'annual_return', 'percentage', True),
                    ('夏普比率', 'sharpe_ratio', 'number', True),
                    ('最大回撤', 'max_drawdown', 'percentage', False),
                    ('胜率', 'win_rate', 'percentage', True),
                    ('盈亏比', 'profit_factor', 'number', True),
                    ('交易次数', 'total_trades', 'integer', None),
                    ('日均收益', 'avg_daily_return', 'percentage', True)
                ]
                
                for label, key, format_type, is_positive in metric_display:
                    if key in metrics:
                        value = metrics[key]
                        
                        # 格式化值
                        if format_type == 'percentage':
                            display_value = f"{value:.2%}"
                        elif format_type == 'number':
                            display_value = f"{value:.2f}"
                        elif format_type == 'integer':
                            display_value = f"{int(value)}"
                        else:
                            display_value = str(value)
                        
                        # 确定CSS类
                        if is_positive is None:
                            css_class = 'metric-neutral'
                        elif is_positive:
                            css_class = 'metric-positive' if value > 0 else 'metric-negative'
                        else:
                            css_class = 'metric-negative' if value < 0 else 'metric-positive'
                        
                        html_content += f"""
            <div class="metric-card">
                <h3>{label}</h3>
                <div class="metric-value {css_class}">{display_value}</div>
            </div>
"""
                
                html_content += """
        </div>
    </div>
"""
            
            # 添加图表部分
            for chart_type, chart_path in chart_files.items():
                if chart_type != 'html_report':
                    # 获取图表类型的中文名称
                    chart_names = {
                        'price_chart': '价格与信号图表',
                        'performance_chart': '绩效分析图表', 
                        'risk_chart': '风险分析图表',
                        'comparison_chart': '策略对比图表'
                    }
                    
                    chart_name = chart_names.get(chart_type, '分析图表')
                    
                    # 获取相对路径
                    rel_path = os.path.relpath(chart_path, self.output_dir)
                    
                    html_content += f"""
    <div class="section">
        <h2>📈 {chart_name}</h2>
        <div class="chart-container">
            <img src="{rel_path}" alt="{chart_name}">
        </div>
    </div>
"""
            
            # 添加风险指标部分
            if 'risk' in analysis_results and 'risk_metrics' in analysis_results['risk']:
                risk_metrics = analysis_results['risk']['risk_metrics']
                
                html_content += """
    <div class="section">
        <h2>⚠️ 风险指标</h2>
        <div class="metrics-grid">
"""
                
                risk_display = [
                    ('波动率', 'volatility', 'percentage', False),
                    ('VaR (95%)', 'var_value', 'percentage', False),
                    ('CVaR', 'cvar_value', 'percentage', False),
                    ('索提诺比率', 'sortino_ratio', 'number', True)
                ]
                
                for label, key, format_type, is_positive in risk_display:
                    if key in risk_metrics:
                        value = risk_metrics[key]
                        
                        if format_type == 'percentage':
                            display_value = f"{value:.2%}"
                        elif format_type == 'number':
                            display_value = f"{value:.2f}"
                        else:
                            display_value = str(value)
                        
                        css_class = 'metric-positive' if (is_positive and value > 0) else 'metric-negative'
                        
                        html_content += f"""
            <div class="metric-card">
                <h3>{label}</h3>
                <div class="metric-value {css_class}">{display_value}</div>
            </div>
"""
                
                html_content += """
        </div>
    </div>
"""
            
            # 添加信号摘要部分
            if 'signals' in analysis_results and analysis_results['signals']:
                signals = analysis_results['signals']
                buy_signals = [s for s in signals if s.get('type') == 'buy']
                sell_signals = [s for s in signals if s.get('type') == 'sell']
                
                html_content += f"""
    <div class="section">
        <h2>📡 交易信号摘要</h2>
        <div class="metrics-grid">
            <div class="metric-card">
                <h3>买入信号</h3>
                <div class="metric-value metric-positive">{len(buy_signals)} 个</div>
            </div>
            <div class="metric-card">
                <h3>卖出信号</h3>
                <div class="metric-value metric-negative">{len(sell_signals)} 个</div>
            </div>
            <div class="metric-card">
                <h3>总信号数</h3>
                <div class="metric-value metric-neutral">{len(signals)} 个</div>
            </div>
            <div class="metric-card">
                <h3>平均置信度</h3>
                <div class="metric-value metric-neutral">
                    {np.mean([s.get('confidence', 0) for s in signals if 'confidence' in s]):.2%}
                </div>
            </div>
        </div>
    </div>
"""
            
            # 添加结论部分
            html_content += f"""
    <div class="section">
        <h2>📝 分析结论</h2>
        <p>本报告基于量化交易系统分析结果自动生成。报告包含价格分析、绩效评估、风险测量和策略对比等多个维度。</p>
        
        <h3>主要发现:</h3>
        <ul>
            <li><strong>市场分析</strong>: 系统识别了关键价格水平和交易信号</li>
            <li><strong>绩效评估</strong>: 提供了详细的收益率、风险和策略对比分析</li>
            <li><strong>风险管理</strong>: 包含VaR、CVaR等专业风险测量指标</li>
            <li><strong>可视化展示</strong>: 通过图表直观展示分析结果</li>
        </ul>
        
        <h3>使用建议:</h3>
        <ol>
            <li>结合具体市场环境解读分析结果</li>
            <li>关注风险指标，合理控制仓位</li>
            <li>定期更新数据，保持分析时效性</li>
            <li>根据绩效反馈优化策略参数</li>
        </ol>
        
        <p><strong>注意</strong>: 本报告为量化分析结果，不构成投资建议。实际投资需结合个人风险承受能力和市场判断。</p>
    </div>
    
    <div class="footer">
        <p>生成系统: OpenClaw量化交易分析框架 | 版本: 1.0.0</p>
        <p>© 2026 量化分析报告 | 仅用于分析演示</p>
    </div>
</body>
</html>
"""
            
            # 保存HTML文件
            html_path = os.path.join(self.output_dir, f'{report_name.replace(" ", "_")}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return html_path
            
        except Exception as e:
            warnings.warn(f"HTML报告生成失败: {str(e)}")
            return None

# 示例使用代码
if __name__ == "__main__":
    # 创建可视化器
    config = {
        'output_dir': './visualization_output',
        'figure_size': (12, 8),
        'dpi': 100,
        'save_format': 'png'
    }
    
    visualizer = TradingVisualizer(config)
    
    print("✅ 交易可视化系统已初始化")
    print(f"📁 输出目录: {visualizer.output_dir}")
    print(f"🎨 可用颜色方案: {list(visualizer.colors.keys())[:5]}...")
    
    # 示例: 生成示例图表
    print("\n📊 生成示例图表中...")
    
    # 创建示例数据
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    price_data = pd.DataFrame({
        'date': dates,
        'open': np.random.randn(100).cumsum() + 100,
        'high': np.random.randn(100).cumsum() + 102,
        'low': np.random.randn(100).cumsum() + 98,
        'close': np.random.randn(100).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 100)
    })
    
    # 创建示例信号
    signals = []
    for i in range(0, 100, 20):
        signals.append({
            'timestamp': dates[i],
            'type': 'buy' if i % 40 == 0 else 'sell',
            'price': price_data['close'].iloc[i],
            'reason': f'示例信号 {i//20 + 1}',
            'confidence': np.random.uniform(0.6, 0.9)
        })
    
    # 创建示例技术指标
    indicators = {
        'MA20': price_data['close'].rolling(20).mean(),
        'MA50': price_data['close'].rolling(50).mean()
    }
    
    # 生成价格图表
    price_chart = visualizer.plot_price_with_signals(
        price_data=price_data,
        signals=signals,
        indicators=indicators,
        title="示例: 价格与交易信号"
    )
    
    if price_chart:
        print(f"✅ 价格图表已生成: {price_chart}")
    
    # 创建示例绩效数据
    np.random.seed(42)
    returns = np.random.randn(252) * 0.01
    cumulative_returns = (1 + returns).cumprod() - 1
    drawdown = cumulative_returns - cumulative_returns.expanding().max()
    
    performance_data = {
        'returns': pd.Series(returns, index=pd.date_range('2024-01-01', periods=252, freq='B')),
        'cumulative_returns': cumulative_returns,
        'drawdown': drawdown,
        'metrics': {
            'annual_return': 0.156,
            'sharpe_ratio': 1.24,
            'max_drawdown': -0.087,
            'win_rate': 0.58,
            'profit_factor': 1.45
        }
    }
    
    # 生成绩效图表
    performance_chart = visualizer.plot_performance_metrics(
        performance_data=performance_data,
        title="示例: 策略绩效分析"
    )
    
    if performance_chart:
        print(f"✅ 绩效图表已生成: {performance_chart}")
    
    # 创建示例仪表板
    analysis_results = {
        'price_data': price_data,
        'signals': signals,
        'performance': performance_data,
        'risk': {
            'returns': returns,
            'risk_metrics': {
                'volatility': 0.018,
                'var_value': -0.032,
                'cvar_value': -0.045,
                'sortino_ratio': 1.56
            }
        }
    }
    
    dashboard_files = visualizer.create_dashboard_report(
        analysis_results=analysis_results,
        report_name="示例交易分析仪表板"
    )
    
    if dashboard_files:
        print(f"✅ 仪表板报告已生成: {len(dashboard_files)} 个文件")
        for file_type, file_path in dashboard_files.items():
            print(f"   - {file_type}: {file_path}")
    
    print("\n🎉 可视化系统示例完成!")