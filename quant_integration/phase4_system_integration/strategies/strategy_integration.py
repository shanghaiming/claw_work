#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
策略层集成 - 连接数据层、分析层和策略管理器

功能:
1. 创建完整的策略执行管道
2. 集成phase2_strategy_integration的策略管理器
3. 提供统一的策略执行和工作流管理
4. 支持策略组合和优化
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
import warnings
warnings.filterwarnings('ignore')

# 添加项目路径
sys.path.append('/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration')

# 尝试导入依赖组件
try:
    from data.data_manager import UnifiedDataManager
    DATA_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ 无法导入数据管理器")
    DATA_MANAGER_AVAILABLE = False

try:
    from analysis.analysis_manager import UnifiedAnalysisManager
    ANALYSIS_MANAGER_AVAILABLE = True
except ImportError:
    print("⚠️ 无法导入分析管理器")
    ANALYSIS_MANAGER_AVAILABLE = False

# 导入策略管理器
try:
    sys.path.append('/Users/chengming/.openclaw/workspace/quant_integration/phase2_strategy_integration/managers')
    from strategy_manager import StrategyManager
    STRATEGY_MANAGER_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ 无法导入策略管理器: {e}")
    STRATEGY_MANAGER_AVAILABLE = False


class StrategyExecutionPipeline:
    """策略执行管道 - 连接数据、分析和策略执行"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化策略执行管道
        
        参数:
            config: 管道配置
        """
        # 默认配置
        self.config = config or {
            'data_config': {
                'cache_enabled': True,
                'preprocessing_enabled': False,  # 使用分析层的预处理
                'default_source': 'local'
            },
            'analysis_config': {
                'enable_price_action': True,
                'enable_technical': True,
                'enable_signal': True,
                'result_integration': 'weighted'
            },
            'strategy_config': {
                'name': 'UnifiedPipeline',
                'config_dir': './strategy_configs',
                'results_dir': './strategy_results'
            },
            'execution_mode': 'sequential',  # sequential, parallel, hybrid
            'max_workers': 4,
            'enable_logging': True
        }
        
        # 初始化组件
        self.components = {}
        self._init_components()
        
        print(f"✅ 策略执行管道初始化完成")
        print(f"   可用组件: {list(self.components.keys())}")
    
    def _init_components(self):
        """初始化管道组件"""
        # 数据管理器
        if DATA_MANAGER_AVAILABLE:
            try:
                self.components['data_manager'] = UnifiedDataManager(self.config['data_config'])
                print("✅ 数据管理器初始化成功")
            except Exception as e:
                print(f"⚠️ 数据管理器初始化失败: {e}")
                self.components['data_manager'] = None
        else:
            self.components['data_manager'] = None
        
        # 分析管理器
        if ANALYSIS_MANAGER_AVAILABLE:
            try:
                self.components['analysis_manager'] = UnifiedAnalysisManager(self.config['analysis_config'])
                print("✅ 分析管理器初始化成功")
            except Exception as e:
                print(f"⚠️ 分析管理器初始化失败: {e}")
                self.components['analysis_manager'] = None
        else:
            self.components['analysis_manager'] = None
        
        # 策略管理器
        if STRATEGY_MANAGER_AVAILABLE:
            try:
                strategy_config = self.config['strategy_config']
                self.components['strategy_manager'] = StrategyManager(
                    name=strategy_config['name'],
                    config_dir=strategy_config['config_dir'],
                    results_dir=strategy_config['results_dir']
                )
                print("✅ 策略管理器初始化成功")
                
                # 注册默认策略
                self._register_default_strategies()
            except Exception as e:
                print(f"⚠️ 策略管理器初始化失败: {e}")
                self.components['strategy_manager'] = None
        else:
            self.components['strategy_manager'] = None
    
    def _register_default_strategies(self):
        """注册默认策略"""
        if not self.components.get('strategy_manager'):
            return
        
        try:
            # 导入移动平均策略适配器
            sys.path.append('/Users/chengming/.openclaw/workspace/quant_integration/phase2_strategy_integration/integrations')
            from ma_strategy_adapter import register_ma_strategies
            
            # 注册移动平均策略
            register_ma_strategies(self.components['strategy_manager'])
            print("✅ 移动平均策略注册成功")
        except ImportError as e:
            print(f"⚠️ 移动平均策略注册失败: {e}")
        
        try:
            # 导入价格行为策略
            from price_action_integration import register_price_action_strategies
            register_price_action_strategies(self.components['strategy_manager'])
            print("✅ 价格行为策略注册成功")
        except ImportError as e:
            print(f"⚠️ 价格行为策略注册失败: {e}")
    
    def execute_pipeline(self, 
                        symbols: List[str],
                        start_date: str,
                        end_date: str,
                        strategy_names: Optional[List[str]] = None,
                        **kwargs) -> Dict[str, Any]:
        """
        执行完整策略管道
        
        参数:
            symbols: 交易符号列表
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            strategy_names: 要执行的策略名称列表，如果为None则执行所有注册策略
            **kwargs: 其他参数
        
        返回:
            管道执行结果
        """
        print(f"🚀 开始执行策略管道")
        print(f"   符号: {symbols}")
        print(f"   日期范围: {start_date} 到 {end_date}")
        print(f"   策略: {strategy_names if strategy_names else '所有注册策略'}")
        
        results = {
            'pipeline_start_time': pd.Timestamp.now(),
            'symbols': symbols,
            'date_range': {'start': start_date, 'end': end_date},
            'strategy_names': strategy_names,
            'component_results': {},
            'final_results': {}
        }
        
        # 1. 数据获取阶段
        data_results = self._execute_data_stage(symbols, start_date, end_date, **kwargs)
        results['component_results']['data_stage'] = data_results
        
        if not data_results.get('success', False):
            results['error'] = '数据获取失败'
            return results
        
        # 2. 分析阶段
        analysis_results = self._execute_analysis_stage(data_results['data'], **kwargs)
        results['component_results']['analysis_stage'] = analysis_results
        
        # 3. 策略执行阶段
        strategy_results = self._execute_strategy_stage(
            data_results['data'],
            analysis_results.get('signals', []),
            strategy_names,
            **kwargs
        )
        results['component_results']['strategy_stage'] = strategy_results
        
        # 4. 结果整合阶段
        final_results = self._integrate_results(data_results, analysis_results, strategy_results)
        results['final_results'] = final_results
        
        results['pipeline_end_time'] = pd.Timestamp.now()
        duration = (results['pipeline_end_time'] - results['pipeline_start_time']).total_seconds()
        results['pipeline_duration_seconds'] = duration
        
        print(f"🎯 策略管道执行完成")
        print(f"   总耗时: {duration:.2f} 秒")
        print(f"   数据获取: {data_results.get('data_count', 0)} 个符号")
        print(f"   分析信号: {analysis_results.get('signal_count', 0)} 个")
        print(f"   策略执行: {strategy_results.get('strategy_count', 0)} 个策略")
        
        return results
    
    def _execute_data_stage(self, symbols: List[str], start_date: str, end_date: str, **kwargs) -> Dict[str, Any]:
        """执行数据获取阶段"""
        print(f"\n📥 数据获取阶段...")
        
        if not self.components.get('data_manager'):
            return {'success': False, 'error': '数据管理器不可用'}
        
        try:
            # 获取数据
            data_dict = self.components['data_manager'].get_multiple_symbols(
                symbols=symbols,
                start_date=start_date,
                end_date=end_date,
                **kwargs
            )
            
            success_count = len(data_dict)
            total_count = len(symbols)
            
            print(f"✅ 数据获取完成: {success_count}/{total_count} 个符号成功")
            
            # 准备结果
            result = {
                'success': True,
                'data': data_dict,
                'data_count': success_count,
                'failed_symbols': [s for s in symbols if s not in data_dict],
                'timestamp': pd.Timestamp.now()
            }
            
            # 显示数据统计
            for symbol, data in data_dict.items():
                print(f"   {symbol}: {len(data)} 行, {len(data.columns)} 列")
            
            return result
            
        except Exception as e:
            print(f"❌ 数据获取失败: {e}")
            return {'success': False, 'error': str(e)}
    
    def _execute_analysis_stage(self, data_dict: Dict[str, pd.DataFrame], **kwargs) -> Dict[str, Any]:
        """执行分析阶段"""
        print(f"\n🔍 分析阶段...")
        
        if not self.components.get('analysis_manager'):
            return {'success': False, 'error': '分析管理器不可用', 'signals': []}
        
        all_signals = []
        analysis_results = {}
        
        for symbol, data in data_dict.items():
            print(f"  分析 {symbol}...")
            
            try:
                # 执行多维度分析
                results = self.components['analysis_manager'].analyze(data, **kwargs)
                
                # 收集信号
                consensus_signals = results.get('consensus_signals_list', [])
                for signal in consensus_signals:
                    signal['symbol'] = symbol
                    signal['analysis_timestamp'] = results.get('analysis_timestamp')
                    all_signals.append(signal)
                
                analysis_results[symbol] = {
                    'signal_count': len(consensus_signals),
                    'total_signals': results.get('total_signals', 0),
                    'engine_count': results.get('engine_count', 0)
                }
                
                print(f"    ✅ {symbol}: {len(consensus_signals)} 个共识信号")
                
            except Exception as e:
                print(f"    ❌ {symbol} 分析失败: {e}")
                analysis_results[symbol] = {'error': str(e)}
        
        print(f"✅ 分析阶段完成: 总 {len(all_signals)} 个共识信号")
        
        return {
            'success': True,
            'signals': all_signals,
            'signal_count': len(all_signals),
            'analysis_results': analysis_results,
            'timestamp': pd.Timestamp.now()
        }
    
    def _execute_strategy_stage(self, 
                               data_dict: Dict[str, pd.DataFrame],
                               signals: List[Dict[str, Any]],
                               strategy_names: Optional[List[str]] = None,
                               **kwargs) -> Dict[str, Any]:
        """执行策略阶段"""
        print(f"\n🎯 策略执行阶段...")
        
        if not self.components.get('strategy_manager'):
            return {'success': False, 'error': '策略管理器不可用', 'strategy_results': {}}
        
        strategy_results = {}
        
        # 确定要执行的策略
        if strategy_names is None:
            # 执行所有注册策略
            try:
                # 尝试不同的方法访问策略
                if hasattr(self.components['strategy_manager'], 'strategies'):
                    available_strategies = self.components['strategy_manager'].strategies
                    strategy_names = list(available_strategies.keys())
                elif hasattr(self.components['strategy_manager'], 'get_registered_strategies'):
                    available_strategies = self.components['strategy_manager'].get_registered_strategies()
                    strategy_names = list(available_strategies.keys())
                else:
                    # 默认策略列表
                    strategy_names = ['MovingAverageAdapter', 'PriceActionSignal']
            except:
                strategy_names = ['MovingAverageAdapter', 'PriceActionSignal']
        
        if not strategy_names:
            print("⚠️ 没有可执行的策略")
            return {'success': False, 'error': '没有可执行的策略', 'strategy_results': {}}
        
        print(f"   执行 {len(strategy_names)} 个策略: {strategy_names}")
        
        # 对每个符号执行策略
        for symbol, data in data_dict.items():
            print(f"   {symbol} 策略执行:")
            
            symbol_strategy_results = {}
            
            for strategy_name in strategy_names:
                try:
                    print(f"    执行 {strategy_name}...")
                    
                    # 运行策略
                    result = self.components['strategy_manager'].run_strategy(
                        strategy_name=strategy_name,
                        data=data,
                        save_results=False,  # 管道级别统一保存
                        **kwargs.get('strategy_params', {}).get(strategy_name, {})
                    )
                    
                    symbol_strategy_results[strategy_name] = result
                    print(f"      ✅ {strategy_name}: {result.get('signal_count', 0)} 个信号")
                    
                except Exception as e:
                    print(f"      ❌ {strategy_name} 执行失败: {e}")
                    symbol_strategy_results[strategy_name] = {'error': str(e)}
            
            strategy_results[symbol] = symbol_strategy_results
        
        # 整合策略结果
        integrated_results = self._integrate_strategy_results(strategy_results, signals)
        
        return {
            'success': True,
            'strategy_results': strategy_results,
            'integrated_results': integrated_results,
            'strategy_count': len(strategy_names),
            'symbol_count': len(data_dict),
            'timestamp': pd.Timestamp.now()
        }
    
    def _integrate_strategy_results(self, 
                                   strategy_results: Dict[str, Dict[str, Any]],
                                   analysis_signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """整合策略结果"""
        print(f"\n🔄 整合策略结果...")
        
        integration = {
            'strategy_performance': {},
            'signal_summary': {},
            'recommendations': []
        }
        
        # 按策略汇总性能
        strategy_performance = {}
        
        for symbol, symbol_results in strategy_results.items():
            for strategy_name, result in symbol_results.items():
                if 'error' in result:
                    continue
                
                if strategy_name not in strategy_performance:
                    strategy_performance[strategy_name] = {
                        'signal_counts': [],
                        'execution_times': [],
                        'symbols': []
                    }
                
                strategy_performance[strategy_name]['signal_counts'].append(result.get('signal_count', 0))
                strategy_performance[strategy_name]['execution_times'].append(result.get('execution_time', 0))
                strategy_performance[strategy_name]['symbols'].append(symbol)
        
        # 计算性能指标
        for strategy_name, perf in strategy_performance.items():
            signal_counts = perf['signal_counts']
            exec_times = perf['execution_times']
            
            if signal_counts:
                integration['strategy_performance'][strategy_name] = {
                    'avg_signals': np.mean(signal_counts),
                    'total_signals': sum(signal_counts),
                    'avg_execution_time': np.mean(exec_times) if exec_times else 0,
                    'symbol_count': len(perf['symbols'])
                }
        
        # 信号汇总
        signal_types = {}
        for signal in analysis_signals:
            signal_type = signal.get('type', 'unknown')
            if signal_type not in signal_types:
                signal_types[signal_type] = 0
            signal_types[signal_type] += 1
        
        integration['signal_summary'] = signal_types
        
        # 生成推荐
        if integration['strategy_performance']:
            # 找到信号最多的策略
            best_strategy = max(
                integration['strategy_performance'].items(),
                key=lambda x: x[1].get('avg_signals', 0),
                default=(None, None)
            )
            
            if best_strategy[0]:
                integration['recommendations'].append({
                    'type': 'best_strategy',
                    'strategy': best_strategy[0],
                    'reason': f"平均生成 {best_strategy[1].get('avg_signals', 0):.1f} 个信号",
                    'confidence': 0.7
                })
        
        print(f"✅ 策略结果整合完成")
        print(f"   策略性能评估: {len(integration['strategy_performance'])} 个策略")
        print(f"   信号汇总: {integration['signal_summary']}")
        
        return integration
    
    def _integrate_results(self, 
                          data_results: Dict[str, Any],
                          analysis_results: Dict[str, Any],
                          strategy_results: Dict[str, Any]) -> Dict[str, Any]:
        """整合所有阶段结果"""
        integrated = {
            'summary': {
                'data_symbols': data_results.get('data_count', 0),
                'analysis_signals': analysis_results.get('signal_count', 0),
                'strategy_count': strategy_results.get('strategy_count', 0),
                'successful': all([
                    data_results.get('success', False),
                    analysis_results.get('success', False),
                    strategy_results.get('success', False)
                ])
            },
            'detailed_results': {
                'data': data_results,
                'analysis': analysis_results,
                'strategy': strategy_results
            },
            'timestamp': pd.Timestamp.now()
        }
        
        # 生成执行报告
        integrated['execution_report'] = self._generate_execution_report(integrated)
        
        return integrated
    
    def _generate_execution_report(self, integrated_results: Dict[str, Any]) -> str:
        """生成执行报告"""
        summary = integrated_results['summary']
        
        report_lines = [
            "策略执行管道报告",
            "=" * 60,
            f"执行时间: {integrated_results['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}",
            f"执行状态: {'成功' if summary['successful'] else '失败'}",
            "",
            "执行摘要:",
            f"  • 数据获取: {summary['data_symbols']} 个符号",
            f"  • 分析信号: {summary['analysis_signals']} 个",
            f"  • 策略执行: {summary['strategy_count']} 个策略",
        ]
        
        # 添加策略性能
        strategy_perf = integrated_results.get('detailed_results', {}).get('strategy', {}).get('integrated_results', {}).get('strategy_performance', {})
        if strategy_perf:
            report_lines.append("")
            report_lines.append("策略性能:")
            for strategy, perf in strategy_perf.items():
                report_lines.append(f"  • {strategy}: {perf.get('avg_signals', 0):.1f} 平均信号")
        
        # 添加信号汇总
        signal_summary = integrated_results.get('detailed_results', {}).get('strategy', {}).get('integrated_results', {}).get('signal_summary', {})
        if signal_summary:
            report_lines.append("")
            report_lines.append("信号汇总:")
            for signal_type, count in signal_summary.items():
                report_lines.append(f"  • {signal_type}: {count} 个")
        
        # 添加推荐
        recommendations = integrated_results.get('detailed_results', {}).get('strategy', {}).get('integrated_results', {}).get('recommendations', [])
        if recommendations:
            report_lines.append("")
            report_lines.append("推荐:")
            for rec in recommendations:
                report_lines.append(f"  • {rec.get('strategy', '未知')}: {rec.get('reason', '')}")
        
        return "\n".join(report_lines)
    
    def get_available_strategies(self) -> List[str]:
        """获取可用策略列表"""
        if not self.components.get('strategy_manager'):
            return []
        
        try:
            # 尝试不同的方法访问策略
            if hasattr(self.components['strategy_manager'], 'strategies'):
                strategies = self.components['strategy_manager'].strategies
                return list(strategies.keys())
            elif hasattr(self.components['strategy_manager'], 'get_registered_strategies'):
                strategies = self.components['strategy_manager'].get_registered_strategies()
                return list(strategies.keys())
            else:
                # 默认策略列表
                return ['MovingAverageAdapter', 'PriceActionSignal']
        except:
            return ['MovingAverageAdapter', 'PriceActionSignal']
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """获取管道状态"""
        status = {
            'timestamp': pd.Timestamp.now(),
            'components': {
                'data_manager': DATA_MANAGER_AVAILABLE and bool(self.components.get('data_manager')),
                'analysis_manager': ANALYSIS_MANAGER_AVAILABLE and bool(self.components.get('analysis_manager')),
                'strategy_manager': STRATEGY_MANAGER_AVAILABLE and bool(self.components.get('strategy_manager'))
            },
            'available_strategies': self.get_available_strategies(),
            'config': self.config
        }
        
        return status


# ========== 使用示例 ==========

def example_usage():
    """使用示例"""
    print("="*60)
    print("策略执行管道使用示例")
    print("="*60)
    
    # 创建管道
    print("创建策略执行管道...")
    
    config = {
        'data_config': {
            'cache_enabled': True,
            'preprocessing_enabled': False,
            'default_source': 'local',
            'local_data_dir': '/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration/data/example_data'
        },
        'analysis_config': {
            'enable_price_action': True,
            'enable_technical': True,
            'enable_signal': True,
            'result_integration': 'weighted'
        },
        'strategy_config': {
            'name': 'DemoPipeline',
            'config_dir': './demo_configs',
            'results_dir': './demo_results'
        }
    }
    
    try:
        pipeline = StrategyExecutionPipeline(config)
        print(f"✅ 管道创建成功")
        
        # 显示管道状态
        status = pipeline.get_pipeline_status()
        print(f"   组件状态:")
        for component, available in status['components'].items():
            print(f"     {component}: {'✅ 可用' if available else '❌ 不可用'}")
        
        print(f"   可用策略: {status['available_strategies']}")
        
        # 执行管道
        print(f"\n执行策略管道...")
        
        # 使用示例数据符号
        symbols = ['TEST001.SZ', 'TEST002.SZ'][:1]  # 只测试一个符号节省时间
        
        results = pipeline.execute_pipeline(
            symbols=symbols,
            start_date='20200101',
            end_date='20301231',
            strategy_names=None  # 执行所有可用策略
        )
        
        # 显示结果
        print(f"\n📊 管道执行结果:")
        
        if 'error' in results:
            print(f"❌ 执行失败: {results['error']}")
        else:
            summary = results.get('final_results', {}).get('summary', {})
            print(f"✅ 执行成功")
            print(f"   数据符号: {summary.get('data_symbols', 0)}")
            print(f"   分析信号: {summary.get('analysis_signals', 0)}")
            print(f"   策略数量: {summary.get('strategy_count', 0)}")
            
            # 显示执行报告
            report = results.get('final_results', {}).get('execution_report', '')
            if report:
                print(f"\n📋 执行报告:")
                print(report)
        
        return True
        
    except Exception as e:
        print(f"❌ 管道执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = example_usage()
    
    if success:
        print(f"\n✅ 策略执行管道示例完成")
    else:
        print(f"\n❌ 策略执行管道示例失败")