#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格行为理论与技术分析工具融合引擎
整合AL Brooks价格行为理论与6个技术分析工具
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import linregress
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']
plt.rcParams['axes.unicode_minus'] = False


class PriceActionIntegrationEngine:
    """
    价格行为整合引擎
    融合AL Brooks理论 + 6个技术分析工具
    """
    
    def __init__(self):
        """初始化整合引擎"""
        self.data = None
        self.results = {}
        self.indicators = {}
        
        # 初始化各模块
        self._init_modules()
        
    def _init_modules(self):
        """初始化各分析模块"""
        self.modules = {
            'pivot_detection': PivotDetectionModule(),
            'range_clustering': RangeClusteringModule(),
            'compensated_ma': CompensatedMAModule(),
            'position_energy': PositionEnergyModule(),
            'multi_momentum': MultiMomentumModule(),
            'price_volume': PriceVolumeModule()
        }
        
    def load_data(self, df):
        """加载价格数据"""
        self.data = df.copy()
        # 确保有必要的列
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in self.data.columns:
                raise ValueError(f"缺少必要列: {col}")
        
        print(f"数据加载成功: {len(self.data)} 行, {self.data.index[0]} 到 {self.data.index[-1]}")
        
    def run_analysis(self):
        """运行完整分析"""
        if self.data is None:
            raise ValueError("请先加载数据")
        
        print("=" * 60)
        print("开始价格行为整合分析...")
        print("=" * 60)
        
        # 1. 枢轴点检测（尖峰检测）
        print("1. 运行枢轴点检测...")
        self.results['pivots'] = self.modules['pivot_detection'].analyze(self.data)
        
        # 2. 价格区间聚类
        print("2. 运行价格区间聚类...")
        self.results['ranges'] = self.modules['range_clustering'].analyze(self.data)
        
        # 3. 补偿移动平均线
        print("3. 计算补偿移动平均线...")
        self.results['cma'] = self.modules['compensated_ma'].analyze(self.data)
        
        # 4. 仓位势能分析
        print("4. 计算仓位势能...")
        self.results['energy'] = self.modules['position_energy'].analyze(self.data)
        
        # 5. 多周期动量
        print("5. 分析多周期动量...")
        self.results['momentum'] = self.modules['multi_momentum'].analyze(self.data)
        
        # 6. 价格-成交量互动
        print("6. 分析价格-成交量互动...")
        self.results['price_volume'] = self.modules['price_volume'].analyze(self.data)
        
        # 7. 综合磁力位识别
        print("7. 综合磁力位识别...")
        self.results['magnetic_levels'] = self._identify_magnetic_levels()
        
        print("=" * 60)
        print("分析完成!")
        print("=" * 60)
        
        return self.results
    
    def _identify_magnetic_levels(self):
        """识别综合磁力位"""
        magnetic_levels = {
            'support_levels': [],
            'resistance_levels': [],
            'magnetic_zones': [],
            'strength_scores': {}
        }
        
        # 整合各模块结果识别磁力位
        # 1. 从枢轴点获取关键水平
        if 'pivots' in self.results:
            pivots = self.results['pivots']
            if 'up_peaks' in pivots:
                for peak in pivots['up_peaks']:
                    if 'price' in peak:
                        magnetic_levels['resistance_levels'].append({
                            'price': peak['price'],
                            'source': 'pivot_peak',
                            'strength': 0.7
                        })
            
            if 'down_peaks' in pivots:
                for peak in pivots['down_peaks']:
                    if 'price' in peak:
                        magnetic_levels['support_levels'].append({
                            'price': peak['price'],
                            'source': 'pivot_trough',
                            'strength': 0.7
                        })
        
        # 2. 从价格区间获取支撑阻力
        if 'ranges' in self.results:
            ranges = self.results['ranges']
            if 'support' in ranges and ranges['support'] is not None:
                magnetic_levels['support_levels'].append({
                    'price': ranges['support'],
                    'source': 'range_cluster',
                    'strength': 0.8
                })
            
            if 'resistance' in ranges and ranges['resistance'] is not None:
                magnetic_levels['resistance_levels'].append({
                    'price': ranges['resistance'],
                    'source': 'range_cluster',
                    'strength': 0.8
                })
        
        # 3. 从仓位势能获取中枢区域
        if 'energy' in self.results:
            energy = self.results['energy']
            if 'centers' in energy:
                for center in energy['centers']:
                    magnetic_levels['magnetic_zones'].append({
                        'price': center['price'],
                        'width': center.get('width', 0),
                        'strength': center.get('strength', 0.6),
                        'source': 'position_energy'
                    })
        
        return magnetic_levels
    
    def generate_report(self):
        """生成分析报告"""
        report = {
            'summary': {
                'total_analysis_points': len(self.data),
                'support_levels_count': len(self.results.get('magnetic_levels', {}).get('support_levels', [])),
                'resistance_levels_count': len(self.results.get('magnetic_levels', {}).get('resistance_levels', [])),
                'magnetic_zones_count': len(self.results.get('magnetic_levels', {}).get('magnetic_zones', []))
            },
            'current_market_state': self._assess_market_state(),
            'trading_implications': self._generate_trading_implications(),
            'detailed_results': self.results
        }
        
        return report
    
    def _assess_market_state(self):
        """评估市场状态"""
        # 基于多模块结果评估市场状态
        state = {
            'trend_direction': 'neutral',
            'trend_strength': 0,
            'market_regime': 'range',  # range, trend, reversal
            'volatility_level': 'medium'
        }
        
        # 这里可以添加更复杂的评估逻辑
        return state
    
    def _generate_trading_implications(self):
        """生成交易含义"""
        implications = {
            'key_levels': [],
            'potential_setups': [],
            'risk_warnings': [],
            'monitoring_points': []
        }
        
        # 识别关键水平
        mag_levels = self.results.get('magnetic_levels', {})
        
        for level in mag_levels.get('support_levels', []):
            implications['key_levels'].append({
                'type': 'support',
                'price': level['price'],
                'strength': level['strength'],
                'action': 'watch_for_bounce'
            })
        
        for level in mag_levels.get('resistance_levels', []):
            implications['key_levels'].append({
                'type': 'resistance',
                'price': level['price'],
                'strength': level['strength'],
                'action': 'watch_for_rejection'
            })
        
        return implications
    
    def visualize(self, save_path=None):
        """可视化分析结果"""
        fig, axes = plt.subplots(3, 2, figsize=(16, 12))
        axes = axes.flatten()
        
        # 1. 价格与磁力位
        ax1 = axes[0]
        self._plot_price_with_magnetic_levels(ax1)
        
        # 2. 补偿移动平均线
        ax2 = axes[1]
        self._plot_compensated_ma(ax2)
        
        # 3. 价格区间聚类
        ax3 = axes[2]
        self._plot_range_clusters(ax3)
        
        # 4. 动量分析
        ax4 = axes[3]
        self._plot_momentum(ax4)
        
        # 5. 价格-成交量关系
        ax5 = axes[4]
        self._plot_price_volume(ax5)
        
        # 6. 综合磁力位强度
        ax6 = axes[5]
        self._plot_magnetic_strength(ax6)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"图表已保存到: {save_path}")
        
        plt.show()
    
    def _plot_price_with_magnetic_levels(self, ax):
        """绘制价格与磁力位"""
        if self.data is None:
            return
        
        # 绘制K线（简化版）
        dates = self.data.index
        closes = self.data['close'].values
        
        ax.plot(dates, closes, 'b-', linewidth=1, alpha=0.7, label='收盘价')
        ax.fill_between(dates, self.data['low'], self.data['high'], alpha=0.2, color='gray')
        
        # 绘制磁力位
        mag_levels = self.results.get('magnetic_levels', {})
        
        # 支撑位
        for level in mag_levels.get('support_levels', []):
            price = level['price']
            strength = level.get('strength', 0.5)
            ax.axhline(y=price, color='green', linestyle='--', alpha=strength, 
                      label=f"支撑: {price:.2f}")
        
        # 阻力位
        for level in mag_levels.get('resistance_levels', []):
            price = level['price']
            strength = level.get('strength', 0.5)
            ax.axhline(y=price, color='red', linestyle='--', alpha=strength,
                      label=f"阻力: {price:.2f}")
        
        ax.set_title('价格与磁力位分析')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.legend(loc='best', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def _plot_compensated_ma(self, ax):
        """绘制补偿移动平均线"""
        if 'cma' not in self.results:
            return
        
        # 这里可以添加补偿均线绘图逻辑
        ax.set_title('补偿移动平均线')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.grid(True, alpha=0.3)
        ax.text(0.05, 0.95, '补偿均线模块', transform=ax.transAxes, 
                fontsize=12, verticalalignment='top')
    
    def _plot_range_clusters(self, ax):
        """绘制价格区间聚类"""
        if 'ranges' not in self.results:
            return
        
        ax.set_title('价格区间聚类')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.grid(True, alpha=0.3)
        ax.text(0.05, 0.95, '区间聚类模块', transform=ax.transAxes,
                fontsize=12, verticalalignment='top')
    
    def _plot_momentum(self, ax):
        """绘制动量分析"""
        if 'momentum' not in self.results:
            return
        
        ax.set_title('多周期动量分析')
        ax.set_xlabel('日期')
        ax.set_ylabel('动量强度')
        ax.grid(True, alpha=0.3)
        ax.text(0.05, 0.95, '动量分析模块', transform=ax.transAxes,
                fontsize=12, verticalalignment='top')
    
    def _plot_price_volume(self, ax):
        """绘制价格-成交量关系"""
        if 'price_volume' not in self.results:
            return
        
        ax.set_title('价格-成交量互动分析')
        ax.set_xlabel('日期')
        ax.set_ylabel('成交量/价格')
        ax.grid(True, alpha=0.3)
        ax.text(0.05, 0.95, '价量分析模块', transform=ax.transAxes,
                fontsize=12, verticalalignment='top')
    
    def _plot_magnetic_strength(self, ax):
        """绘制磁力位强度"""
        mag_levels = self.results.get('magnetic_levels', {})
        
        # 收集所有磁力位
        all_levels = []
        for level in mag_levels.get('support_levels', []):
            all_levels.append({
                'price': level['price'],
                'strength': level.get('strength', 0.5),
                'type': 'support'
            })
        
        for level in mag_levels.get('resistance_levels', []):
            all_levels.append({
                'price': level['price'],
                'strength': level.get('strength', 0.5),
                'type': 'resistance'
            })
        
        if not all_levels:
            ax.text(0.5, 0.5, '无磁力位数据', transform=ax.transAxes,
                   ha='center', va='center')
            return
        
        # 按价格排序
        all_levels.sort(key=lambda x: x['price'])
        
        prices = [l['price'] for l in all_levels]
        strengths = [l['strength'] for l in all_levels]
        colors = ['green' if l['type'] == 'support' else 'red' for l in all_levels]
        
        bars = ax.bar(range(len(prices)), strengths, color=colors, alpha=0.7)
        
        # 添加价格标签
        for i, (price, strength) in enumerate(zip(prices, strengths)):
            ax.text(i, strength + 0.02, f'{price:.2f}', ha='center', va='bottom', fontsize=8)
        
        ax.set_title('磁力位强度分析')
        ax.set_xlabel('磁力位索引')
        ax.set_ylabel('强度分数')
        ax.set_ylim(0, 1.1)
        ax.grid(True, alpha=0.3, axis='y')
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.7, label='支撑位'),
            Patch(facecolor='red', alpha=0.7, label='阻力位')
        ]
        ax.legend(handles=legend_elements, loc='upper right')


# ============================================================================
# 各个分析模块（简化版，实际应从原始ipynb导入）
# ============================================================================

class PivotDetectionModule:
    """枢轴点检测模块（基于spike_bake.ipynb）"""
    
    def analyze(self, df):
        """分析枢轴点"""
        close = df['close'].values
        
        # 简化版尖峰检测
        up_peaks, _ = find_peaks(close, prominence=np.std(close)*0.5)
        down_peaks, _ = find_peaks(-close, prominence=np.std(close)*0.5)
        
        # 整理结果
        pivots = {
            'up_peaks': [],
            'down_peaks': [],
            'pivot_bars': []
        }
        
        for idx in up_peaks:
            if idx < len(df):
                pivots['up_peaks'].append({
                    'index': int(idx),
                    'price': close[idx],
                    'date': df.index[idx] if hasattr(df.index, '__getitem__') else None
                })
        
        for idx in down_peaks:
            if idx < len(df):
                pivots['down_peaks'].append({
                    'index': int(idx),
                    'price': close[idx],
                    'date': df.index[idx] if hasattr(df.index, '__getitem__') else None
                })
        
        return pivots


class RangeClusteringModule:
    """价格区间聚类模块（基于cluster.ipynb）"""
    
    def analyze(self, df, window=20, cluster_threshold=1.0):
        """分析价格区间"""
        close = df['close'].values
        
        if len(close) < window:
            return {
                'trend_direction': None,
                'is_range': False,
                'support': None,
                'resistance': None
            }
        
        # 简化版趋势检测
        slopes = []
        for i in range(len(close) - window):
            y = close[i:i+window]
            x = np.arange(len(y))
            slope, _, _, _, _ = linregress(x, y)
            slopes.append(slope)
        
        avg_slope = np.mean(slopes) if slopes else 0
        
        # 识别支撑阻力（简化版）
        support = np.percentile(close, 25)
        resistance = np.percentile(close, 75)
        
        # 判断是否处于区间
        price_range = resistance - support
        avg_price = np.mean(close)
        is_range = price_range < avg_price * 0.05  # 价格波动小于5%
        
        return {
            'trend_direction': 'up' if avg_slope > 0 else 'down' if avg_slope < 0 else 'neutral',
            'trend_strength': abs(avg_slope),
            'is_range': is_range,
            'support': float(support),
            'resistance': float(resistance),
            'range_width': float(price_range)
        }


class CompensatedMAModule:
    """补偿移动平均线模块（基于ma_compensat.ipynb）"""
    
    def analyze(self, df, window=20, beta=0.3, gamma=0.2):
        """计算补偿移动平均线"""
        close = df['close'].values
        
        # 简化版补偿均线
        cma = np.full(len(close), np.nan)
        simple_ma = np.full(len(close), np.nan)
        
        for i in range(window-1, len(close)):
            window_data = close[i-window+1:i+1]
            ma_value = np.mean(window_data)
            simple_ma[i] = ma_value
            
            # 简化补偿逻辑
            if i > window:
                price_change = close[i] - close[i-1]
                trend_factor = 1.0 + gamma * (1 if price_change > 0 else -1)
                compensation = beta * (close[i] - simple_ma[i-1]) * trend_factor
                cma[i] = simple_ma[i] + compensation
            else:
                cma[i] = ma_value
        
        return {
            'simple_ma': simple_ma.tolist(),
            'compensated_ma': cma.tolist(),
            'window': window,
            'beta': beta,
            'gamma': gamma
        }


class PositionEnergyModule:
    """仓位势能模块（基于仓位势能分析.ipynb）"""
    
    def analyze(self, df, min_k_lines=5):
        """分析仓位势能"""
        close = df['close'].values
        
        # 简化版中枢检测
        # 使用K-means聚类识别价格中枢
        from sklearn.cluster import KMeans
        
        # 准备数据
        X = close.reshape(-1, 1)
        
        # 自动确定聚类数量（1-5个）
        n_clusters = min(5, max(2, len(close) // 20))
        
        try:
            kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
            labels = kmeans.fit_predict(X)
            centers = kmeans.cluster_centers_.flatten()
            
            # 计算每个中枢的强度（样本数量）
            strengths = []
            for i in range(n_clusters):
                cluster_points = close[labels == i]
                if len(cluster_points) > 0:
                    center_price = centers[i]
                    cluster_std = np.std(cluster_points)
                    strength = len(cluster_points) / len(close)  # 比例
                    
                    strengths.append({
                        'price': float(center_price),
                        'std': float(cluster_std),
                        'count': int(len(cluster_points)),
                        'strength': float(strength),
                        'min_price': float(np.min(cluster_points)),
                        'max_price': float(np.max(cluster_points))
                    })
            
            # 按强度排序
            strengths.sort(key=lambda x: x['strength'], reverse=True)
            
            return {
                'centers': strengths,
                'n_clusters': n_clusters,
                'total_points': len(close)
            }
            
        except Exception as e:
            return {
                'centers': [],
                'error': str(e),
                'total_points': len(close)
            }


class MultiMomentumModule:
    """多周期动量模块（基于stategy_momentum.ipynb）"""
    
    def analyze(self, df, periods=[5, 8, 13, 21, 34, 55]):
        """分析多周期动量"""
        close = df['close'].values
        
        momentum_results = {}
        
        for period in periods:
            if len(close) >= period:
                # 计算简单动量
                momentum = (close[-1] / close[-period] - 1) * 100
                
                # 计算动量强度（基于波动率调整）
                returns = np.diff(np.log(close[-period:])) if period > 1 else [0]
                vol = np.std(returns) * np.sqrt(252) if len(returns) > 1 else 0.01
                
                momentum_strength = abs(momentum) / (vol * 100) if vol > 0 else 0
                
                momentum_results[f'period_{period}'] = {
                    'momentum': float(momentum),
                    'strength': float(momentum_strength),
                    'volatility': float(vol),
                    'direction': 'bullish' if momentum > 0 else 'bearish'
                }
        
        # 计算综合动量
        if momentum_results:
            avg_momentum = np.mean([v['momentum'] for v in momentum_results.values()])
            avg_strength = np.mean([v['strength'] for v in momentum_results.values()])
            
            momentum_results['composite'] = {
                'avg_momentum': float(avg_momentum),
                'avg_strength': float(avg_strength),
                'momentum_alignment': self._calculate_alignment(momentum_results)
            }
        
        return momentum_results
    
    def _calculate_alignment(self, momentum_results):
        """计算动量一致性"""
        if not momentum_results:
            return 0
        
        directions = []
        for key, value in momentum_results.items():
            if key != 'composite':
                directions.append(1 if value['direction'] == 'bullish' else -1)
        
        if directions:
            alignment = np.mean(directions)
            return float(alignment)
        
        return 0


class PriceVolumeModule:
    """价格-成交量模块（基于price_vol_int.ipynb）"""
    
    def analyze(self, df):
        """分析价格-成交量关系"""
        close = df['close'].values
        volume = df['volume'].values
        
        if len(close) < 2:
            return {}
        
        # 计算基础指标
        price_change = np.diff(close)
        volume_change = np.diff(volume)
        
        # 价格-成交量相关性
        if len(price_change) > 1 and len(volume_change) > 1:
            # 对齐长度
            min_len = min(len(price_change), len(volume_change))
            corr = np.corrcoef(price_change[:min_len], volume_change[:min_len])[0, 1]
        else:
            corr = 0
        
        # 计算成交量确认
        volume_confirmation = self._calculate_volume_confirmation(df)
        
        # 计算价格位置
        recent_high = np.max(close[-20:]) if len(close) >= 20 else np.max(close)
        recent_low = np.min(close[-20:]) if len(close) >= 20 else np.min(close)
        
        if recent_high != recent_low:
            price_position = (close[-1] - recent_low) / (recent_high - recent_low)
        else:
            price_position = 0.5
        
        return {
            'price_volume_correlation': float(corr),
            'volume_confirmation': volume_confirmation,
            'price_position': float(price_position),
            'recent_high': float(recent_high),
            'recent_low': float(recent_low),
            'volume_trend': self._analyze_volume_trend(volume)
        }
    
    def _calculate_volume_confirmation(self, df):
        """计算成交量确认"""
        # 简化版成交量确认逻辑
        close = df['close'].values
        volume = df['volume'].values
        
        if len(close) < 2:
            return {'strength': 0, 'direction': 'neutral'}
        
        # 最近价格变化
        recent_price_change = close[-1] - close[-2] if len(close) >= 2 else 0
        recent_volume_change = volume[-1] - volume[-2] if len(volume) >= 2 else 0
        
        # 判断成交量是否确认价格变化
        if recent_price_change > 0 and recent_volume_change > 0:
            strength = min(1.0, recent_volume_change / np.mean(volume) * 2)
            direction = 'bullish_confirmation'
        elif recent_price_change < 0 and recent_volume_change > 0:
            strength = min(1.0, recent_volume_change / np.mean(volume) * 2)
            direction = 'bearish_confirmation'
        elif recent_price_change > 0 and recent_volume_change < 0:
            strength = 0.3
            direction = 'bullish_divergence'
        elif recent_price_change < 0 and recent_volume_change < 0:
            strength = 0.3
            direction = 'bearish_divergence'
        else:
            strength = 0.1
            direction = 'neutral'
        
        return {'strength': float(strength), 'direction': direction}
    
    def _analyze_volume_trend(self, volume, window=5):
        """分析成交量趋势"""
        if len(volume) < window:
            return {'trend': 'neutral', 'strength': 0}
        
        recent_volume = volume[-window:]
        volume_ma = np.mean(recent_volume)
        avg_volume = np.mean(volume)
        
        if volume_ma > avg_volume * 1.2:
            trend = 'increasing'
            strength = min(1.0, (volume_ma - avg_volume) / avg_volume)
        elif volume_ma < avg_volume * 0.8:
            trend = 'decreasing'
            strength = min(1.0, (avg_volume - volume_ma) / avg_volume)
        else:
            trend = 'stable'
            strength = 0
        
        return {'trend': trend, 'strength': float(strength)}


# ============================================================================
# 主程序
# ============================================================================

def main():
    """主函数"""
    print("价格行为理论与技术分析工具整合系统")
    print("版本: 1.0")
    print("=" * 60)
    
    # 创建引擎
    engine = PriceActionIntegrationEngine()
    
    # 生成示例数据（实际使用时应加载真实数据）
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # 生成模拟价格数据（趋势 + 波动）
    base_price = 100
    trend = np.linspace(0, 20, 100)  # 上升趋势
    noise = np.random.normal(0, 2, 100)
    
    closes = base_price + trend + noise
    opens = closes - np.random.uniform(0.5, 2.0, 100)
    highs = closes + np.random.uniform(0.5, 3.0, 100)
    lows = closes - np.random.uniform(0.5, 3.0, 100)
    volumes = np.random.lognormal(10, 1, 100) * 1000
    
    # 创建DataFrame
    df = pd.DataFrame({
        'open': opens,
        'high': highs,
        'low': lows,
        'close': closes,
        'volume': volumes
    }, index=dates)
    
    # 加载数据
    engine.load_data(df)
    
    # 运行分析
    results = engine.run_analysis()
    
    # 生成报告
    report = engine.generate_report()
    
    # 打印报告摘要
    print("\n" + "=" * 60)
    print("分析报告摘要")
    print("=" * 60)
    print(f"分析数据点: {report['summary']['total_analysis_points']}")
    print(f"识别支撑位: {report['summary']['support_levels_count']}")
    print(f"识别阻力位: {report['summary']['resistance_levels_count']}")
    print(f"识别磁力区: {report['summary']['magnetic_zones_count']}")
    
    print(f"\n市场状态: {report['current_market_state']['trend_direction']}")
    print(f"趋势强度: {report['current_market_state']['trend_strength']:.2f}")
    
    print("\n关键交易水平:")
    for level in report['trading_implications']['key_levels'][:5]:  # 显示前5个
        print(f"  - {level['type']}: {level['price']:.2f} (强度: {level['strength']:.2f})")
    
    # 可视化
    print("\n生成可视化图表...")
    engine.visualize(save_path='price_action_integration.png')
    
    # 保存结果
    import json
    with open('integration_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, default=str, ensure_ascii=False)
    
    print("\n详细结果已保存到: integration_results.json")
    print("图表已保存到: price_action_integration.png")


if __name__ == "__main__":
    main()