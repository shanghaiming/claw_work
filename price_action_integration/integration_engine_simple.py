#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
价格行为理论与技术分析工具融合引擎（简化版）
移除scipy依赖，使用numpy实现核心功能
"""

import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# 设置中文字体（如果没有matplotlib则不设置）
try:
    import matplotlib.pyplot as plt
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    print("警告: matplotlib不可用，可视化功能将禁用")


class PriceActionIntegrationEngine:
    """
    价格行为整合引擎（简化版）
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
        
        # 去重和合并相近水平
        magnetic_levels = self._merge_similar_levels(magnetic_levels)
        
        return magnetic_levels
    
    def _merge_similar_levels(self, magnetic_levels, threshold=0.01):
        """合并相近的价格水平"""
        # 合并支撑位
        support_levels = magnetic_levels['support_levels']
        if support_levels:
            support_levels.sort(key=lambda x: x['price'])
            merged_supports = []
            
            current_group = []
            for level in support_levels:
                if not current_group:
                    current_group.append(level)
                else:
                    avg_price = np.mean([l['price'] for l in current_group])
                    if abs(level['price'] - avg_price) / avg_price < threshold:
                        current_group.append(level)
                    else:
                        # 合并当前组
                        merged_price = np.mean([l['price'] for l in current_group])
                        merged_strength = np.mean([l['strength'] for l in current_group])
                        merged_sources = list(set([l['source'] for l in current_group]))
                        
                        merged_supports.append({
                            'price': merged_price,
                            'strength': merged_strength,
                            'sources': merged_sources,
                            'count': len(current_group)
                        })
                        current_group = [level]
            
            # 处理最后一组
            if current_group:
                merged_price = np.mean([l['price'] for l in current_group])
                merged_strength = np.mean([l['strength'] for l in current_group])
                merged_sources = list(set([l['source'] for l in current_group]))
                
                merged_supports.append({
                    'price': merged_price,
                    'strength': merged_strength,
                    'sources': merged_sources,
                    'count': len(current_group)
                })
            
            magnetic_levels['support_levels'] = merged_supports
        
        # 合并阻力位（类似逻辑）
        resistance_levels = magnetic_levels['resistance_levels']
        if resistance_levels:
            resistance_levels.sort(key=lambda x: x['price'])
            merged_resistances = []
            
            current_group = []
            for level in resistance_levels:
                if not current_group:
                    current_group.append(level)
                else:
                    avg_price = np.mean([l['price'] for l in current_group])
                    if abs(level['price'] - avg_price) / avg_price < threshold:
                        current_group.append(level)
                    else:
                        merged_price = np.mean([l['price'] for l in current_group])
                        merged_strength = np.mean([l['strength'] for l in current_group])
                        merged_sources = list(set([l['source'] for l in current_group]))
                        
                        merged_resistances.append({
                            'price': merged_price,
                            'strength': merged_strength,
                            'sources': merged_sources,
                            'count': len(current_group)
                        })
                        current_group = [level]
            
            if current_group:
                merged_price = np.mean([l['price'] for l in current_group])
                merged_strength = np.mean([l['strength'] for l in current_group])
                merged_sources = list(set([l['source'] for l in current_group]))
                
                merged_resistances.append({
                    'price': merged_price,
                    'strength': merged_strength,
                    'sources': merged_sources,
                    'count': len(current_group)
                })
            
            magnetic_levels['resistance_levels'] = merged_resistances
        
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
            'detailed_results': {k: v for k, v in self.results.items() if k != 'detailed_data'}
        }
        
        return report
    
    def _assess_market_state(self):
        """评估市场状态"""
        state = {
            'trend_direction': 'neutral',
            'trend_strength': 0,
            'market_regime': 'range',  # range, trend, reversal
            'volatility_level': 'medium'
        }
        
        # 基于动量分析判断趋势
        if 'momentum' in self.results:
            momentum = self.results['momentum']
            if 'composite' in momentum:
                composite = momentum['composite']
                avg_momentum = composite.get('avg_momentum', 0)
                
                if avg_momentum > 1.0:
                    state['trend_direction'] = 'bullish'
                    state['trend_strength'] = min(1.0, avg_momentum / 10.0)
                elif avg_momentum < -1.0:
                    state['trend_direction'] = 'bearish'
                    state['trend_strength'] = min(1.0, abs(avg_momentum) / 10.0)
        
        # 基于价格区间判断市场状态
        if 'ranges' in self.results:
            ranges = self.results['ranges']
            if ranges.get('is_range', False):
                state['market_regime'] = 'range'
            else:
                state['market_regime'] = 'trend'
        
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
                'sources': level.get('sources', ['unknown']),
                'action': 'watch_for_bounce_or_break'
            })
        
        for level in mag_levels.get('resistance_levels', []):
            implications['key_levels'].append({
                'type': 'resistance',
                'price': level['price'],
                'strength': level['strength'],
                'sources': level.get('sources', ['unknown']),
                'action': 'watch_for_rejection_or_breakout'
            })
        
        # 基于市场状态生成潜在交易设置
        market_state = self._assess_market_state()
        
        if market_state['market_regime'] == 'range':
            implications['potential_setups'].append({
                'type': 'range_trading',
                'description': '区间交易：在支撑位买入，阻力位卖出',
                'confidence': 0.7
            })
        elif market_state['market_regime'] == 'trend':
            direction = market_state['trend_direction']
            if direction == 'bullish':
                implications['potential_setups'].append({
                    'type': 'trend_following',
                    'description': '趋势跟踪：逢低买入，跟随趋势',
                    'confidence': 0.6
                })
            elif direction == 'bearish':
                implications['potential_setups'].append({
                    'type': 'trend_following',
                    'description': '趋势跟踪：逢高卖出，跟随下跌趋势',
                    'confidence': 0.6
                })
        
        return implications
    
    def print_report(self):
        """打印分析报告"""
        report = self.generate_report()
        
        print("\n" + "=" * 60)
        print("价格行为整合分析报告")
        print("=" * 60)
        
        # 基本信息
        print(f"\n📊 分析概要")
        print(f"   数据点数: {report['summary']['total_analysis_points']}")
        print(f"   支撑位数量: {report['summary']['support_levels_count']}")
        print(f"   阻力位数量: {report['summary']['resistance_levels_count']}")
        print(f"   磁力区数量: {report['summary']['magnetic_zones_count']}")
        
        # 市场状态
        state = report['current_market_state']
        print(f"\n📈 市场状态")
        print(f"   趋势方向: {state['trend_direction']}")
        print(f"   趋势强度: {state['trend_strength']:.2f}")
        print(f"   市场状态: {state['market_regime']}")
        print(f"   波动水平: {state['volatility_level']}")
        
        # 关键水平
        print(f"\n🎯 关键交易水平")
        key_levels = report['trading_implications']['key_levels']
        if key_levels:
            for level in key_levels[:10]:  # 最多显示10个
                sources = ', '.join(level.get('sources', ['未知']))
                print(f"   {level['type']}: {level['price']:.2f} (强度: {level['strength']:.2f}, 来源: {sources})")
        else:
            print("   未识别到关键水平")
        
        # 潜在交易设置
        print(f"\n💡 潜在交易设置")
        setups = report['trading_implications']['potential_setups']
        if setups:
            for setup in setups:
                print(f"   {setup['type']}: {setup['description']} (置信度: {setup['confidence']:.2f})")
        else:
            print("   未识别到明显交易设置")
        
        # 模块详情
        print(f"\n🔧 各模块分析结果")
        for module_name, module_result in self.results.items():
            if module_name == 'magnetic_levels':
                continue
            
            print(f"   {module_name}: ", end="")
            if isinstance(module_result, dict):
                # 显示关键信息
                if module_name == 'pivots':
                    up_count = len(module_result.get('up_peaks', []))
                    down_count = len(module_result.get('down_peaks', []))
                    print(f"检测到 {up_count} 个上涨尖峰, {down_count} 个下跌尖峰")
                elif module_name == 'ranges':
                    support = module_result.get('support', 'N/A')
                    resistance = module_result.get('resistance', 'N/A')
                    print(f"支撑: {support:.2f}, 阻力: {resistance:.2f}")
                elif module_name == 'momentum':
                    if 'composite' in module_result:
                        comp = module_result['composite']
                        mom = comp.get('avg_momentum', 0)
                        print(f"综合动量: {mom:.2f}%")
                    else:
                        print(f"动量周期数: {len(module_result)}")
                else:
                    print("已完成分析")
            else:
                print("已完成分析")
        
        print("\n" + "=" * 60)
        print("报告生成完成")
        print("=" * 60)
    
    def visualize(self, save_path=None):
        """可视化分析结果（如果matplotlib可用）"""
        if not HAS_MATPLOTLIB:
            print("警告: matplotlib不可用，跳过可视化")
            return
        
        try:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
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
            
            # 4. 磁力位强度
            ax4 = axes[3]
            self._plot_magnetic_strength(ax4)
            
            plt.tight_layout()
            
            if save_path:
                plt.savefig(save_path, dpi=150, bbox_inches='tight')
                print(f"图表已保存到: {save_path}")
            
            plt.show()
        except Exception as e:
            print(f"可视化失败: {e}")
    
    def _plot_price_with_magnetic_levels(self, ax):
        """绘制价格与磁力位"""
        if self.data is None:
            return
        
        # 绘制价格线
        dates = self.data.index
        closes = self.data['close'].values
        
        ax.plot(dates, closes, 'b-', linewidth=1.5, alpha=0.8, label='收盘价')
        
        # 绘制磁力位
        mag_levels = self.results.get('magnetic_levels', {})
        
        # 支撑位
        for level in mag_levels.get('support_levels', []):
            price = level['price']
            strength = level.get('strength', 0.5)
            ax.axhline(y=price, color='green', linestyle='--', alpha=strength, 
                      linewidth=1.5)
        
        # 阻力位
        for level in mag_levels.get('resistance_levels', []):
            price = level['price']
            strength = level.get('strength', 0.5)
            ax.axhline(y=price, color='red', linestyle='--', alpha=strength,
                      linewidth=1.5)
        
        ax.set_title('价格与磁力位分析')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.legend(['收盘价'], loc='best')
        ax.grid(True, alpha=0.3)
    
    def _plot_compensated_ma(self, ax):
        """绘制补偿移动平均线"""
        if 'cma' not in self.results or self.data is None:
            return
        
        dates = self.data.index
        closes = self.data['close'].values
        cma_data = self.results['cma']
        
        if 'compensated_ma' in cma_data:
            cma = cma_data['compensated_ma']
            # 转换为numpy数组并处理NaN
            cma_array = np.array(cma)
            valid_mask = ~np.isnan(cma_array)
            
            if np.any(valid_mask):
                ax.plot(dates[valid_mask], cma_array[valid_mask], 'r-', linewidth=1.5, alpha=0.8, label='补偿均线')
        
        ax.plot(dates, closes, 'b-', linewidth=1, alpha=0.5, label='收盘价')
        ax.set_title('补偿移动平均线')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
    def _plot_range_clusters(self, ax):
        """绘制价格区间聚类"""
        if 'ranges' not in self.results or self.data is None:
            return
        
        dates = self.data.index
        closes = self.data['close'].values
        
        ax.plot(dates, closes, 'b-', linewidth=1, alpha=0.7, label='收盘价')
        
        ranges = self.results['ranges']
        support = ranges.get('support')
        resistance = ranges.get('resistance')
        
        if support is not None:
            ax.axhline(y=support, color='green', linestyle='-', alpha=0.7, linewidth=2, label='支撑')
        
        if resistance is not None:
            ax.axhline(y=resistance, color='red', linestyle='-', alpha=0.7, linewidth=2, label='阻力')
        
        ax.set_title('价格区间聚类分析')
        ax.set_xlabel('日期')
        ax.set_ylabel('价格')
        ax.legend(loc='best')
        ax.grid(True, alpha=0.3)
    
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
            ax.set_title('磁力位强度分析')
            return
        
        # 按价格排序
        all_levels.sort(key=lambda x: x['price'])
        
        prices = [l['price'] for l in all_levels]
        strengths = [l['strength'] for l in all_levels]
        colors = ['green' if l['type'] == 'support' else 'red' for l in all_levels]
        
        x_pos = np.arange(len(prices))
        bars = ax.bar(x_pos, strengths, color=colors, alpha=0.7, width=0.6)
        
        # 添加价格标签
        for i, (price, strength) in enumerate(zip(prices, strengths)):
            ax.text(i, strength + 0.02, f'{price:.2f}', ha='center', va='bottom', fontsize=8)
        
        ax.set_title('磁力位强度分析')
        ax.set_xlabel('磁力位索引')
        ax.set_ylabel('强度分数')
        ax.set_ylim(0, 1.1)
        ax.set_xticks(x_pos)
        ax.set_xticklabels([f'L{i+1}' for i in range(len(prices))])
        ax.grid(True, alpha=0.3, axis='y')
        
        # 添加图例
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='green', alpha=0.7, label='支撑位'),
            Patch(facecolor='red', alpha=0.7, label='阻力位')
        ]
        ax.legend(handles=legend_elements, loc='upper right')


# ============================================================================
# 各个分析模块（简化版，无外部依赖）
# ============================================================================

class PivotDetectionModule:
    """枢轴点检测模块（简化版，不使用scipy）"""
    
    def analyze(self, df, window=5):
        """分析枢轴点"""
        close = df['close'].values
        
        # 简单峰值检测算法
        up_peaks = self._find_local_maxima(close, window)
        down_peaks = self._find_local_minima(close, window)
        
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
                    'price': float(close[idx]),
                    'date': df.index[idx] if hasattr(df.index, '__getitem__') else None
                })
        
        for idx in down_peaks:
            if idx < len(df):
                pivots['down_peaks'].append({
                    'index': int(idx),
                    'price': float(close[idx]),
                    'date': df.index[idx] if hasattr(df.index, '__getitem__') else None
                })
        
        return pivots
    
    def _find_local_maxima(self, values, window=5):
        """查找局部最大值"""
        maxima = []
        n = len(values)
        
        for i in range(window, n - window):
            is_max = True
            # 检查左侧
            for j in range(1, window + 1):
                if values[i] <= values[i - j]:
                    is_max = False
                    break
            
            if not is_max:
                continue
            
            # 检查右侧
            for j in range(1, window + 1):
                if values[i] <= values[i + j]:
                    is_max = False
                    break
            
            if is_max:
                maxima.append(i)
        
        return maxima
    
    def _find_local_minima(self, values, window=5):
        """查找局部最小值"""
        minima = []
        n = len(values)
        
        for i in range(window, n - window):
            is_min = True
            # 检查左侧
            for j in range(1, window + 1):
                if values[i] >= values[i - j]:
                    is_min = False
                    break
            
            if not is_min:
                continue
            
            # 检查右侧
            for j in range(1, window + 1):
                if values[i] >= values[i + j]:
                    is_min = False
                    break
            
            if is_min:
                minima.append(i)
        
        return minima


class RangeClusteringModule:
    """价格区间聚类模块（简化版）"""
    
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
        
        # 使用numpy的polyfit进行趋势检测
        x = np.arange(len(close))
        slope, intercept = np.polyfit(x, close, 1)
        
        # 计算价格分位数作为支撑阻力
        support = np.percentile(close, 30)  # 30%分位数作为支撑
        resistance = np.percentile(close, 70)  # 70%分位数作为阻力
        
        # 判断是否处于区间
        price_range = resistance - support
        avg_price = np.mean(close)
        is_range = price_range < avg_price * 0.1  # 价格波动小于10%
        
        # 趋势强度
        trend_strength = abs(slope) / (np.std(close) + 1e-10)
        
        return {
            'trend_direction': 'up' if slope > 0 else 'down' if slope < 0 else 'neutral',
            'trend_strength': float(trend_strength),
            'is_range': bool(is_range),
            'support': float(support),
            'resistance': float(resistance),
            'range_width': float(price_range),
            'slope': float(slope)
        }


class CompensatedMAModule:
    """补偿移动平均线模块（简化版）"""
    
    def analyze(self, df, window=20, beta=0.3, gamma=0.2):
        """计算补偿移动平均线"""
        close = df['close'].values
        
        # 初始化数组
        cma = np.full(len(close), np.nan)
        simple_ma = np.full(len(close), np.nan)
        
        # 计算简单移动平均
        for i in range(window-1, len(close)):
            window_data = close[i-window+1:i+1]
            simple_ma[i] = np.mean(window_data)
        
        # 计算补偿移动平均
        for i in range(window, len(close)):
            price_change = close[i] - close[i-1]
            
            # 趋势因子
            trend_factor = 1.0
            if i > window:
                recent_trend = np.mean(close[i-5:i]) - np.mean(close[i-10:i-5])
                if recent_trend > 0:
                    trend_factor += gamma
                else:
                    trend_factor -= gamma
            
            # 补偿量
            compensation = beta * (close[i] - simple_ma[i-1]) * trend_factor
            
            # 应用补偿
            cma[i] = simple_ma[i] + compensation
        
        # 填充前window个值
        cma[:window] = simple_ma[:window]
        
        return {
            'simple_ma': simple_ma.tolist(),
            'compensated_ma': cma.tolist(),
            'window': window,
            'beta': beta,
            'gamma': gamma
        }


class PositionEnergyModule:
    """仓位势能模块（简化版，不使用sklearn）"""
    
    def analyze(self, df, n_clusters=3):
        """分析仓位势能"""
        close = df['close'].values
        
        if len(close) < 10:
            return {
                'centers': [],
                'n_clusters': 0,
                'total_points': len(close)
            }
        
        # 简化版聚类：使用价格分位数
        centers = []
        
        # 确定聚类数量
        n_clusters = min(n_clusters, max(2, len(close) // 20))
        
        # 使用分位数作为聚类中心
        percentiles = np.linspace(20, 80, n_clusters)
        
        for i, p in enumerate(percentiles):
            center_price = np.percentile(close, p)
            
            # 计算该中心周围的点
            threshold = np.std(close) * 0.5
            nearby_points = close[(close >= center_price - threshold) & (close <= center_price + threshold)]
            
            if len(nearby_points) > 0:
                # 重新计算中心为附近点的均值
                actual_center = np.mean(nearby_points)
                count = len(nearby_points)
                strength = count / len(close)
                
                centers.append({
                    'price': float(actual_center),
                    'std': float(np.std(nearby_points) if len(nearby_points) > 1 else 0),
                    'count': int(count),
                    'strength': float(strength),
                    'min_price': float(np.min(nearby_points)),
                    'max_price': float(np.max(nearby_points)),
                    'width': float(np.max(nearby_points) - np.min(nearby_points))
                })
        
        # 按强度排序
        centers.sort(key=lambda x: x['strength'], reverse=True)
        
        return {
            'centers': centers,
            'n_clusters': len(centers),
            'total_points': len(close)
        }


class MultiMomentumModule:
    """多周期动量模块（简化版）"""
    
    def analyze(self, df, periods=[5, 8, 13, 21, 34, 55]):
        """分析多周期动量"""
        close = df['close'].values
        
        momentum_results = {}
        
        for period in periods:
            if len(close) >= period:
                # 计算简单动量
                momentum = (close[-1] / close[-period] - 1) * 100
                
                # 计算动量强度
                period_returns = []
                for i in range(1, min(period, len(close))):
                    if close[-i-1] > 0:
                        ret = (close[-i] / close[-i-1] - 1) * 100
                        period_returns.append(ret)
                
                vol = np.std(period_returns) if len(period_returns) > 1 else 1.0
                momentum_strength = abs(momentum) / (vol + 1e-10)
                
                momentum_results[f'period_{period}'] = {
                    'momentum': float(momentum),
                    'strength': float(momentum_strength),
                    'volatility': float(vol),
                    'direction': 'bullish' if momentum > 0 else 'bearish'
                }
        
        # 计算综合动量
        if momentum_results:
            momentums = [v['momentum'] for v in momentum_results.values()]
            strengths = [v['strength'] for v in momentum_results.values()]
            
            avg_momentum = np.mean(momentums)
            avg_strength = np.mean(strengths)
            
            # 计算一致性
            directions = [1 if v['direction'] == 'bullish' else -1 for v in momentum_results.values()]
            alignment = np.mean(directions)
            
            momentum_results['composite'] = {
                'avg_momentum': float(avg_momentum),
                'avg_strength': float(avg_strength),
                'momentum_alignment': float(alignment)
            }
        
        return momentum_results


class PriceVolumeModule:
    """价格-成交量模块（简化版）"""
    
    def analyze(self, df):
        """分析价格-成交量关系"""
        close = df['close'].values
        volume = df['volume'].values
        
        if len(close) < 2:
            return {}
        
        # 价格变化
        price_changes = np.diff(close)
        
        # 成交量变化
        volume_changes = np.diff(volume)
        
        # 价格-成交量相关性
        min_len = min(len(price_changes), len(volume_changes))
        if min_len > 1:
            corr_matrix = np.corrcoef(price_changes[:min_len], volume_changes[:min_len])
            corr = corr_matrix[0, 1] if not np.isnan(corr_matrix[0, 1]) else 0
        else:
            corr = 0
        
        # 成交量确认
        volume_confirmation = self._calculate_volume_confirmation(df)
        
        # 价格位置
        lookback = min(20, len(close))
        recent_high = np.max(close[-lookback:])
        recent_low = np.min(close[-lookback:])
        
        if recent_high != recent_low:
            price_position = (close[-1] - recent_low) / (recent_high - recent_low)
        else:
            price_position = 0.5
        
        # 成交量趋势
        volume_trend = self._analyze_volume_trend(volume)
        
        return {
            'price_volume_correlation': float(corr),
            'volume_confirmation': volume_confirmation,
            'price_position': float(price_position),
            'recent_high': float(recent_high),
            'recent_low': float(recent_low),
            'volume_trend': volume_trend
        }
    
    def _calculate_volume_confirmation(self, df):
        """计算成交量确认"""
        close = df['close'].values
        volume = df['volume'].values
        
        if len(close) < 2:
            return {'strength': 0, 'direction': 'neutral'}
        
        # 最近价格和成交量变化
        recent_price_change = close[-1] - close[-2]
        recent_volume = volume[-1]
        
        # 成交量均值
        avg_volume = np.mean(volume[-10:]) if len(volume) >= 10 else np.mean(volume)
        
        # 判断确认状态
        if recent_price_change > 0 and recent_volume > avg_volume * 1.2:
            strength = min(1.0, recent_volume / avg_volume / 2)
            direction = 'bullish_confirmation'
        elif recent_price_change < 0 and recent_volume > avg_volume * 1.2:
            strength = min(1.0, recent_volume / avg_volume / 2)
            direction = 'bearish_confirmation'
        elif recent_price_change > 0 and recent_volume < avg_volume * 0.8:
            strength = 0.3
            direction = 'bullish_divergence'
        elif recent_price_change < 0 and recent_volume < avg_volume * 0.8:
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
        
        if volume_ma > avg_volume * 1.3:
            trend = 'increasing'
            strength = min(1.0, (volume_ma - avg_volume) / avg_volume)
        elif volume_ma < avg_volume * 0.7:
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
    print("价格行为理论与技术分析工具整合系统（简化版）")
    print("版本: 1.0 - 无外部依赖")
    print("=" * 60)
    
    # 创建引擎
    engine = PriceActionIntegrationEngine()
    
    # 生成示例数据
    print("\n生成示例数据...")
    dates = pd.date_range('2024-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # 生成更有意义的模拟数据：上升趋势 + 波动
    base_price = 100
    trend = np.linspace(0, 25, 100)  # 上升趋势
    cycle = 10 * np.sin(np.linspace(0, 4*np.pi, 100))  # 周期性波动
    noise = np.random.normal(0, 3, 100)  # 随机噪声
    
    closes = base_price + trend + cycle + noise
    opens = closes - np.random.uniform(0.5, 2.0, 100)
    highs = closes + np.random.uniform(0.5, 3.0, 100)
    lows = closes - np.random.uniform(0.5, 3.0, 100)
    volumes = np.random.lognormal(10, 0.8, 100) * 1000
    
    # 添加一些成交量峰值
    peak_indices = [20, 45, 70]
    for idx in peak_indices:
        if idx < len(volumes):
            volumes[idx] *= 3.0
    
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
    
    # 打印报告
    engine.print_report()
    
    # 可视化（如果可用）
    if HAS_MATPLOTLIB:
        print("\n生成可视化图表...")
        engine.visualize(save_path='price_action_integration_simple.png')
    
    # 保存结果
    import json
    with open('integration_results_simple.json', 'w', encoding='utf-8') as f:
        # 简化结果保存，移除大型数组
        simplified_results = {}
        for key, value in results.items():
            if key in ['cma', 'energy', 'momentum', 'price_volume']:
                # 保留这些结果
                simplified_results[key] = value
            elif key == 'pivots':
                # 只保留数量信息
                simplified_results[key] = {
                    'up_peaks_count': len(value.get('up_peaks', [])),
                    'down_peaks_count': len(value.get('down_peaks', [])),
                    'sample_up_peaks': value.get('up_peaks', [])[:3],
                    'sample_down_peaks': value.get('down_peaks', [])[:3]
                }
            elif key == 'ranges':
                simplified_results[key] = value
            elif key == 'magnetic_levels':
                simplified_results[key] = value
        
        json.dump(simplified_results, f, indent=2, default=str, ensure_ascii=False)
    
    print("\n详细结果已保存到: integration_results_simple.json")
    if HAS_MATPLOTLIB:
        print("图表已保存到: price_action_integration_simple.png")
    
    print("\n✅ 整合完成！")


if __name__ == "__main__":
    main()