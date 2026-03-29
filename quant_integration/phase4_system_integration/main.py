#!/usr/bin/env python3
"""
统一量化交易分析系统 - 主入口点

功能:
1. 命令行界面 (CLI)
2. 配置文件管理
3. 工作流协调
4. 模块集成
5. 错误处理和日志

设计原则:
- 模块化: 独立组件，易于维护和扩展
- 用户友好: 清晰的CLI，详细的帮助文档
- 生产就绪: 完整的错误处理，日志记录，配置管理
- 可扩展: 易于添加新功能和新模块
"""

import os
import sys
import json
import argparse
import logging
from datetime import datetime
from typing import Optional, List, Dict, Any
import warnings

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class UnifiedTradingSystem:
    """统一量化交易分析系统"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化统一系统
        
        Args:
            config_path: 配置文件路径 (可选)
        """
        self.config_path = config_path
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._setup_modules()
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            'system': {
                'name': 'UnifiedTradingSystem',
                'version': '1.0.0',
                'log_level': 'INFO',
                'log_dir': './logs',
                'cache_dir': './cache',
                'output_dir': './output'
            },
            'data': {
                'default_source': 'local',
                'local_data_dir': './data/example_data',
                'cache_enabled': True,
                'preprocessing_enabled': True
            },
            'analysis': {
                'enable_price_action': True,
                'enable_technical': True,
                'enable_signal': True,
                'result_integration': 'weighted'
            },
            'strategies': {
                'default_strategies': ['MovingAverageAdapter', 'PriceActionSignal'],
                'strategy_config_dir': './config/strategies'
            },
            'backtest': {
                'initial_capital': 1000000,
                'commission_rate': 0.0003,
                'slippage': 0.0001,
                'risk_management': True
            },
            'reporting': {
                'output_dir': './reports',
                'default_format': 'markdown',
                'enable_visualization': True,
                'dashboard_enabled': True
            }
        }
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                
                # 深度合并配置
                import copy
                merged_config = copy.deepcopy(default_config)
                
                def merge_dict(dict1, dict2):
                    for key, value in dict2.items():
                        if key in dict1 and isinstance(dict1[key], dict) and isinstance(value, dict):
                            merge_dict(dict1[key], value)
                        else:
                            dict1[key] = value
                
                merge_dict(merged_config, user_config)
                return merged_config
                
            except Exception as e:
                warnings.warn(f"配置文件加载失败: {e}, 使用默认配置")
                return default_config
        else:
            return default_config
    
    def _setup_logging(self):
        """设置日志系统"""
        log_level = getattr(logging, self.config['system']['log_level'])
        log_dir = self.config['system']['log_dir']
        
        os.makedirs(log_dir, exist_ok=True)
        
        # 配置根日志记录器
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(os.path.join(log_dir, f'system_{datetime.now().strftime("%Y%m%d")}.log')),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger('UnifiedTradingSystem')
        self.logger.info(f"系统初始化完成 - 版本: {self.config['system']['version']}")
    
    def _setup_modules(self):
        """设置系统模块"""
        self.modules = {}
        
        # 延迟导入模块，避免不必要的依赖
        self.modules_available = {
            'data_manager': False,
            'analysis_manager': False,
            'strategy_manager': False,
            'backtest_system': False,
            'reporting_system': False,
            'visualization_system': False
        }
        
        # 检查数据管理器
        try:
            from data.data_manager import UnifiedDataManager
            self.modules['data_manager'] = UnifiedDataManager
            self.modules_available['data_manager'] = True
            self.logger.debug("数据管理器模块可用")
        except ImportError as e:
            self.logger.warning(f"数据管理器模块不可用: {e}")
        
        # 检查分析管理器
        try:
            from analysis.analysis_manager import UnifiedAnalysisManager
            self.modules['analysis_manager'] = UnifiedAnalysisManager
            self.modules_available['analysis_manager'] = True
            self.logger.debug("分析管理器模块可用")
        except ImportError as e:
            self.logger.warning(f"分析管理器模块不可用: {e}")
        
        # 检查策略集成
        try:
            from strategies.strategy_integration import StrategyExecutionPipeline
            self.modules['strategy_pipeline'] = StrategyExecutionPipeline
            self.modules_available['strategy_manager'] = True
            self.logger.debug("策略管道模块可用")
        except ImportError as e:
            self.logger.warning(f"策略管道模块不可用: {e}")
        
        # 检查回测系统
        try:
            from backtest.integrated_backtest_system import IntegratedBacktestSystem
            self.modules['backtest_system'] = IntegratedBacktestSystem
            self.modules_available['backtest_system'] = True
            self.logger.debug("回测系统模块可用")
        except ImportError as e:
            self.logger.warning(f"回测系统模块不可用: {e}")
        
        # 检查报告系统
        try:
            from reporting.report_generator import ReportGenerator
            self.modules['report_generator'] = ReportGenerator
            self.modules_available['reporting_system'] = True
            self.logger.debug("报告生成器模块可用")
        except ImportError as e:
            self.logger.warning(f"报告生成器模块不可用: {e}")
        
        # 检查可视化系统
        try:
            from reporting.visualizer import TradingVisualizer
            self.modules['visualizer'] = TradingVisualizer
            self.modules_available['visualization_system'] = True
            self.logger.debug("可视化系统模块可用")
        except ImportError as e:
            self.logger.warning(f"可视化系统模块不可用: {e}")
        
        # 检查仪表板系统
        try:
            from reporting.dashboard import TradingDashboard
            self.modules['dashboard'] = TradingDashboard
            self.logger.debug("仪表板系统模块可用")
        except ImportError as e:
            self.logger.warning(f"仪表板系统模块不可用: {e}")
    
    def run_data_pipeline(self, 
                         symbols: List[str],
                         start_date: str,
                         end_date: str,
                         data_source: str = 'local',
                         **kwargs) -> Optional[Dict[str, Any]]:
        """
        运行数据管道
        
        Args:
            symbols: 股票/资产代码列表
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
            data_source: 数据源 ('local', 'tushare', 'yfinance')
            **kwargs: 额外参数
            
        Returns:
            数据字典或None
        """
        if not self.modules_available['data_manager']:
            self.logger.error("数据管理器不可用")
            return None
        
        try:
            self.logger.info(f"启动数据管道: {symbols} ({start_date} 至 {end_date})")
            
            # 创建数据管理器
            data_config = self.config['data'].copy()
            if data_source != 'local':
                data_config['default_source'] = data_source
            
            data_manager = self.modules['data_manager'](data_config)
            
            # 获取数据
            all_data = {}
            for symbol in symbols:
                self.logger.info(f"获取数据: {symbol}")
                data = data_manager.get_data(
                    symbol=symbol,
                    start_date=start_date,
                    end_date=end_date,
                    source=data_source,
                    **kwargs
                )
                
                if data is not None:
                    all_data[symbol] = data
                    self.logger.info(f"数据获取成功: {symbol}, 形状: {data.shape}")
                else:
                    self.logger.warning(f"数据获取失败: {symbol}")
            
            return all_data
            
        except Exception as e:
            self.logger.error(f"数据管道执行失败: {e}", exc_info=True)
            return None
    
    def run_analysis_pipeline(self,
                             data: Dict[str, Any],
                             analysis_config: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        运行分析管道
        
        Args:
            data: 输入数据
            analysis_config: 分析配置
            
        Returns:
            分析结果或None
        """
        if not self.modules_available['analysis_manager']:
            self.logger.error("分析管理器不可用")
            return None
        
        try:
            self.logger.info("启动分析管道")
            
            # 合并配置
            config = self.config['analysis'].copy()
            if analysis_config:
                config.update(analysis_config)
            
            # 创建分析管理器
            analysis_manager = self.modules['analysis_manager'](config)
            
            # 执行分析
            results = {}
            for symbol, symbol_data in data.items():
                self.logger.info(f"分析数据: {symbol}")
                
                analysis_result = analysis_manager.analyze(symbol_data)
                
                if analysis_result:
                    results[symbol] = analysis_result
                    self.logger.info(f"分析完成: {symbol}, 信号数: {analysis_result.get('total_signals', 0)}")
                else:
                    self.logger.warning(f"分析失败: {symbol}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"分析管道执行失败: {e}", exc_info=True)
            return None
    
    def run_strategy_pipeline(self,
                             analysis_results: Dict[str, Any],
                             strategy_names: Optional[List[str]] = None,
                             strategy_config: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        运行策略管道
        
        Args:
            analysis_results: 分析结果
            strategy_names: 策略名称列表
            strategy_config: 策略配置
            
        Returns:
            策略执行结果或None
        """
        if not self.modules_available['strategy_manager']:
            self.logger.error("策略管理器不可用")
            return None
        
        try:
            self.logger.info("启动策略管道")
            
            # 合并配置
            config = {
                'data_config': self.config['data'],
                'analysis_config': self.config['analysis'],
                'strategy_config': self.config['strategies']
            }
            
            if strategy_config:
                config.update(strategy_config)
            
            # 创建策略管道
            pipeline = self.modules['strategy_pipeline'](config)
            
            # 如果没有指定策略，使用默认策略
            if not strategy_names:
                strategy_names = self.config['strategies']['default_strategies']
            
            # 执行策略
            results = {}
            for symbol, analysis_data in analysis_results.items():
                self.logger.info(f"执行策略: {symbol}")
                
                strategy_result = pipeline.execute_pipeline(
                    symbols=[symbol],
                    strategy_names=strategy_names,
                    analysis_data=analysis_data
                )
                
                if strategy_result:
                    results[symbol] = strategy_result
                    self.logger.info(f"策略执行完成: {symbol}")
                else:
                    self.logger.warning(f"策略执行失败: {symbol}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"策略管道执行失败: {e}", exc_info=True)
            return None
    
    def run_backtest_pipeline(self,
                             strategy_results: Dict[str, Any],
                             backtest_config: Optional[Dict] = None) -> Optional[Dict[str, Any]]:
        """
        运行回测管道
        
        Args:
            strategy_results: 策略结果
            backtest_config: 回测配置
            
        Returns:
            回测结果或None
        """
        if not self.modules_available['backtest_system']:
            self.logger.error("回测系统不可用")
            return None
        
        try:
            self.logger.info("启动回测管道")
            
            # 合并配置
            config = self.config['backtest'].copy()
            if backtest_config:
                config.update(backtest_config)
            
            # 创建回测系统
            backtest_system = self.modules['backtest_system'](config)
            
            # 执行回测
            results = {}
            for symbol, strategy_data in strategy_results.items():
                self.logger.info(f"回测策略: {symbol}")
                
                if 'signals' in strategy_data and 'price_data' in strategy_data:
                    backtest_result = backtest_system.run_backtest(
                        signals=strategy_data['signals'],
                        price_data=strategy_data['price_data']
                    )
                    
                    if backtest_result:
                        results[symbol] = backtest_result
                        self.logger.info(f"回测完成: {symbol}, 收益率: {backtest_result.get('total_return', 0):.2%}")
                    else:
                        self.logger.warning(f"回测失败: {symbol}")
                else:
                    self.logger.warning(f"回测数据不完整: {symbol}")
            
            return results
            
        except Exception as e:
            self.logger.error(f"回测管道执行失败: {e}", exc_info=True)
            return None
    
    def run_reporting_pipeline(self,
                              results: Dict[str, Any],
                              report_type: str = 'summary',
                              output_dir: Optional[str] = None,
                              **kwargs) -> Optional[Dict[str, str]]:
        """
        运行报告管道
        
        Args:
            results: 分析/回测结果
            report_type: 报告类型 ('summary', 'performance', 'risk', 'full')
            output_dir: 输出目录
            **kwargs: 额外参数
            
        Returns:
            报告文件路径字典或None
        """
        if not self.modules_available['reporting_system']:
            self.logger.error("报告系统不可用")
            return None
        
        try:
            self.logger.info(f"启动报告管道: {report_type}")
            
            # 确定输出目录
            if not output_dir:
                output_dir = self.config['reporting']['output_dir']
            
            # 创建报告生成器
            report_config = self.config['reporting'].copy()
            report_config['output_dir'] = output_dir
            
            report_generator = self.modules['report_generator'](report_config)
            
            # 生成报告
            report_files = {}
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            for symbol, result_data in results.items():
                self.logger.info(f"生成报告: {symbol}")
                
                report_file = report_generator.generate_report(
                    report_type=report_type,
                    data=result_data,
                    title=f"{symbol} {report_type}报告",
                    output_path=os.path.join(output_dir, f'{symbol}_{report_type}_{timestamp}')
                )
                
                if report_file:
                    report_files[symbol] = report_file
                    self.logger.info(f"报告生成成功: {symbol} -> {report_file}")
            
            return report_files
            
        except Exception as e:
            self.logger.error(f"报告管道执行失败: {e}", exc_info=True)
            return None
    
    def run_visualization_pipeline(self,
                                  results: Dict[str, Any],
                                  visualization_type: str = 'dashboard',
                                  output_dir: Optional[str] = None,
                                  **kwargs) -> Optional[Dict[str, str]]:
        """
        运行可视化管道
        
        Args:
            results: 分析/回测结果
            visualization_type: 可视化类型 ('dashboard', 'charts', 'reports')
            output_dir: 输出目录
            **kwargs: 额外参数
            
        Returns:
            可视化文件路径字典或None
        """
        if not self.modules_available['visualization_system']:
            self.logger.error("可视化系统不可用")
            return None
        
        try:
            self.logger.info(f"启动可视化管道: {visualization_type}")
            
            # 确定输出目录
            if not output_dir:
                if visualization_type == 'dashboard':
                    output_dir = './dashboard_output'
                elif visualization_type == 'charts':
                    output_dir = './charts_output'
                else:
                    output_dir = './visualization_output'
            
            # 创建可视化器
            visualizer_config = {
                'output_dir': output_dir,
                'theme': 'light'
            }
            
            visualizer = self.modules['visualizer'](visualizer_config)
            
            # 生成可视化
            visualization_files = {}
            
            for symbol, result_data in results.items():
                self.logger.info(f"生成可视化: {symbol}")
                
                if visualization_type == 'dashboard':
                    # 创建仪表板
                    dashboard_file = visualizer.create_dashboard(
                        analysis_data=result_data,
                        dashboard_type='full',
                        title=f"{symbol} 量化分析仪表板",
                        output_path=os.path.join(output_dir, f'{symbol}_dashboard_{datetime.now().strftime("%Y%m%d_%H%M%S")}.html')
                    )
                    
                    if dashboard_file:
                        visualization_files[symbol] = dashboard_file
                        self.logger.info(f"仪表板生成成功: {symbol} -> {dashboard_file}")
                
                elif visualization_type == 'charts':
                    # 创建图表
                    # 这里可以添加更多图表生成逻辑
                    pass
                
                else:
                    self.logger.warning(f"不支持的可视化类型: {visualization_type}")
            
            return visualization_files
            
        except Exception as e:
            self.logger.error(f"可视化管道执行失败: {e}", exc_info=True)
            return None
    
    def run_full_pipeline(self,
                         symbols: List[str],
                         start_date: str,
                         end_date: str,
                         data_source: str = 'local',
                         strategy_names: Optional[List[str]] = None,
                         generate_reports: bool = True,
                         generate_visualizations: bool = True,
                         **kwargs) -> Dict[str, Any]:
        """
        运行完整管道: 数据 → 分析 → 策略 → 回测 → 报告 → 可视化
        
        Args:
            symbols: 股票/资产代码列表
            start_date: 开始日期
            end_date: 结束日期
            data_source: 数据源
            strategy_names: 策略名称列表
            generate_reports: 是否生成报告
            generate_visualizations: 是否生成可视化
            **kwargs: 额外参数
            
        Returns:
            完整管道结果字典
        """
        self.logger.info("=" * 60)
        self.logger.info("启动完整量化分析管道")
        self.logger.info("=" * 60)
        
        pipeline_results = {
            'metadata': {
                'symbols': symbols,
                'start_date': start_date,
                'end_date': end_date,
                'data_source': data_source,
                'timestamp': datetime.now().isoformat()
            },
            'stages': {}
        }
        
        # 阶段1: 数据获取
        self.logger.info("\n📥 阶段1: 数据获取")
        data_results = self.run_data_pipeline(symbols, start_date, end_date, data_source, **kwargs)
        
        if not data_results:
            self.logger.error("数据获取阶段失败，管道终止")
            return pipeline_results
        
        pipeline_results['stages']['data'] = {
            'status': 'success',
            'symbols_processed': list(data_results.keys())
        }
        
        # 阶段2: 分析
        self.logger.info("\n🔍 阶段2: 数据分析")
        analysis_results = self.run_analysis_pipeline(data_results)
        
        if not analysis_results:
            self.logger.error("数据分析阶段失败，管道终止")
            return pipeline_results
        
        pipeline_results['stages']['analysis'] = {
            'status': 'success',
            'symbols_processed': list(analysis_results.keys())
        }
        
        # 阶段3: 策略执行
        self.logger.info("\n⚙️ 阶段3: 策略执行")
        strategy_results = self.run_strategy_pipeline(analysis_results, strategy_names)
        
        if not strategy_results:
            self.logger.error("策略执行阶段失败，管道终止")
            return pipeline_results
        
        pipeline_results['stages']['strategy'] = {
            'status': 'success',
            'symbols_processed': list(strategy_results.keys()),
            'strategies_used': strategy_names or self.config['strategies']['default_strategies']
        }
        
        # 阶段4: 回测
        self.logger.info("\n📊 阶段4: 回测验证")
        backtest_results = self.run_backtest_pipeline(strategy_results)
        
        if not backtest_results:
            self.logger.error("回测阶段失败，管道终止")
            return pipeline_results
        
        pipeline_results['stages']['backtest'] = {
            'status': 'success',
            'symbols_processed': list(backtest_results.keys())
        }
        
        # 合并所有结果
        all_results = {}
        for symbol in symbols:
            if symbol in backtest_results:
                all_results[symbol] = {
                    'data': data_results.get(symbol),
                    'analysis': analysis_results.get(symbol),
                    'strategy': strategy_results.get(symbol),
                    'backtest': backtest_results.get(symbol)
                }
        
        pipeline_results['results'] = all_results
        
        # 阶段5: 报告生成
        if generate_reports:
            self.logger.info("\n📄 阶段5: 报告生成")
            report_results = self.run_reporting_pipeline(all_results, 'full')
            
            if report_results:
                pipeline_results['stages']['reporting'] = {
                    'status': 'success',
                    'reports_generated': report_results
                }
                self.logger.info(f"报告生成完成: {len(report_results)} 个报告")
            else:
                pipeline_results['stages']['reporting'] = {'status': 'failed'}
                self.logger.warning("报告生成失败")
        
        # 阶段6: 可视化
        if generate_visualizations:
            self.logger.info("\n📈 阶段6: 可视化生成")
            visualization_results = self.run_visualization_pipeline(all_results, 'dashboard')
            
            if visualization_results:
                pipeline_results['stages']['visualization'] = {
                    'status': 'success',
                    'visualizations_generated': visualization_results
                }
                self.logger.info(f"可视化生成完成: {len(visualization_results)} 个可视化")
            else:
                pipeline_results['stages']['visualization'] = {'status': 'failed'}
                self.logger.warning("可视化生成失败")
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("完整管道执行完成")
        self.logger.info("=" * 60)
        
        return pipeline_results
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态"""
        return {
            'system': {
                'name': self.config['system']['name'],
                'version': self.config['system']['version'],
                'config_path': self.config_path,
                'log_level': self.config['system']['log_level']
            },
            'modules': self.modules_available,
            'config_summary': {
                'data_sources': ['local'] + (['tushare'] if 'tushare' in self.config['data'] else []),
                'analysis_modules': [k for k, v in self.config['analysis'].items() if v],
                'default_strategies': self.config['strategies']['default_strategies'],
                'backtest_parameters': {
                    'initial_capital': self.config['backtest']['initial_capital'],
                    'commission_rate': self.config['backtest']['commission_rate']
                }
            }
        }

def main():
    """主函数: 命令行界面"""
    parser = argparse.ArgumentParser(
        description='统一量化交易分析系统',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行完整管道
  python main.py run --symbols TEST001.SZ,TEST002.SZ --start 2024-01-01 --end 2024-12-31
  
  # 只运行数据和分析
  python main.py data --symbol TEST001.SZ --start 2024-01-01 --end 2024-12-31
  
  # 获取系统状态
  python main.py status
  
  # 使用自定义配置
  python main.py run --config my_config.json --symbols TEST001.SZ --start 2024-01-01 --end 2024-12-31
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='命令')
    
    # run命令: 运行完整管道
    run_parser = subparsers.add_parser('run', help='运行完整量化分析管道')
    run_parser.add_argument('--config', type=str, help='配置文件路径')
    run_parser.add_argument('--symbols', type=str, required=True, help='股票代码(逗号分隔)')
    run_parser.add_argument('--start', type=str, required=True, help='开始日期 (YYYY-MM-DD)')
    run_parser.add_argument('--end', type=str, required=True, help='结束日期 (YYYY-MM-DD)')
    run_parser.add_argument('--data-source', type=str, default='local', choices=['local', 'tushare'], help='数据源')
    run_parser.add_argument('--strategies', type=str, help='策略名称(逗号分隔)')
    run_parser.add_argument('--no-reports', action='store_true', help='不生成报告')
    run_parser.add_argument('--no-visualizations', action='store_true', help='不生成可视化')
    run_parser.add_argument('--output-dir', type=str, help='输出目录')
    
    # data命令: 只运行数据管道
    data_parser = subparsers.add_parser('data', help='运行数据管道')
    data_parser.add_argument('--config', type=str, help='配置文件路径')
    data_parser.add_argument('--symbol', type=str, required=True, help='股票代码')
    data_parser.add_argument('--start', type=str, required=True, help='开始日期')
    data_parser.add_argument('--end', type=str, required=True, help='结束日期')
    data_parser.add_argument('--source', type=str, default='local', choices=['local', 'tushare'], help='数据源')
    data_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # analyze命令: 运行分析管道
    analyze_parser = subparsers.add_parser('analyze', help='运行分析管道')
    analyze_parser.add_argument('--config', type=str, help='配置文件路径')
    analyze_parser.add_argument('--data', type=str, required=True, help='数据文件路径')
    analyze_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # backtest命令: 运行回测管道
    backtest_parser = subparsers.add_parser('backtest', help='运行回测管道')
    backtest_parser.add_argument('--config', type=str, help='配置文件路径')
    backtest_parser.add_argument('--signals', type=str, required=True, help='信号文件路径')
    backtest_parser.add_argument('--prices', type=str, required=True, help='价格文件路径')
    backtest_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # report命令: 生成报告
    report_parser = subparsers.add_parser('report', help='生成报告')
    report_parser.add_argument('--config', type=str, help='配置文件路径')
    report_parser.add_argument('--data', type=str, required=True, help='数据文件路径')
    report_parser.add_argument('--type', type=str, default='summary', 
                              choices=['summary', 'performance', 'risk', 'full'], 
                              help='报告类型')
    report_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # visualize命令: 生成可视化
    visualize_parser = subparsers.add_parser('visualize', help='生成可视化')
    visualize_parser.add_argument('--config', type=str, help='配置文件路径')
    visualize_parser.add_argument('--data', type=str, required=True, help='数据文件路径')
    visualize_parser.add_argument('--type', type=str, default='dashboard',
                                 choices=['dashboard', 'charts'],
                                 help='可视化类型')
    visualize_parser.add_argument('--output', type=str, help='输出文件路径')
    
    # status命令: 获取系统状态
    status_parser = subparsers.add_parser('status', help='获取系统状态')
    status_parser.add_argument('--config', type=str, help='配置文件路径')
    
    # config命令: 生成配置模板
    config_parser = subparsers.add_parser('config', help='生成配置模板')
    config_parser.add_argument('--output', type=str, default='config_template.json', help='输出文件路径')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        # 初始化系统
        system = UnifiedTradingSystem(args.config if hasattr(args, 'config') else None)
        
        if args.command == 'run':
            # 解析参数
            symbols = [s.strip() for s in args.symbols.split(',')]
            strategy_names = None
            if args.strategies:
                strategy_names = [s.strip() for s in args.strategies.split(',')]
            
            # 运行完整管道
            results = system.run_full_pipeline(
                symbols=symbols,
                start_date=args.start,
                end_date=args.end,
                data_source=args.data_source,
                strategy_names=strategy_names,
                generate_reports=not args.no_reports,
                generate_visualizations=not args.no_visualizations
            )
            
            # 输出结果摘要
            print("\n" + "=" * 60)
            print("管道执行结果摘要")
            print("=" * 60)
            
            for stage, stage_info in results.get('stages', {}).items():
                status = stage_info.get('status', 'unknown')
                status_icon = "✅" if status == 'success' else "❌" if status == 'failed' else "⚠️"
                print(f"{status_icon} {stage}: {status}")
            
            # 如果有报告，显示路径
            if 'reporting' in results.get('stages', {}) and results['stages']['reporting']['status'] == 'success':
                print("\n📄 生成的报告:")
                for symbol, report_path in results['stages']['reporting']['reports_generated'].items():
                    print(f"  - {symbol}: {report_path}")
            
            # 如果有可视化，显示路径
            if 'visualization' in results.get('stages', {}) and results['stages']['visualization']['status'] == 'success':
                print("\n📈 生成的可视化:")
                for symbol, viz_path in results['stages']['visualization']['visualizations_generated'].items():
                    print(f"  - {symbol}: {viz_path}")
            
            # 保存完整结果
            if args.output_dir:
                output_path = os.path.join(args.output_dir, f'pipeline_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json')
            else:
                output_path = f'pipeline_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2, default=str)
            
            print(f"\n💾 完整结果已保存到: {output_path}")
        
        elif args.command == 'data':
            # 运行数据管道
            data = system.run_data_pipeline(
                symbols=[args.symbol],
                start_date=args.start,
                end_date=args.end,
                data_source=args.source
            )
            
            if data and args.symbol in data:
                df = data[args.symbol]
                print(f"\n📊 数据获取成功: {args.symbol}")
                print(f"   形状: {df.shape}")
                print(f"   日期范围: {df.index.min()} 至 {df.index.max()}")
                print("\n前5行数据:")
                print(df.head())
                
                if args.output:
                    if args.output.endswith('.csv'):
                        df.to_csv(args.output)
                    else:
                        df.to_pickle(args.output)
                    print(f"\n💾 数据已保存到: {args.output}")
        
        elif args.command == 'analyze':
            # 运行分析管道
            # 这里需要加载数据文件
            print("分析功能需要数据文件，请使用完整管道或先运行数据管道")
        
        elif args.command == 'backtest':
            # 运行回测管道
            print("回测功能需要信号和价格数据，请使用完整管道")
        
        elif args.command == 'report':
            # 生成报告
            # 这里需要加载数据文件
            print("报告生成需要分析数据，请使用完整管道或先运行分析管道")
        
        elif args.command == 'visualize':
            # 生成可视化
            # 这里需要加载数据文件
            print("可视化生成需要分析数据，请使用完整管道或先运行分析管道")
        
        elif args.command == 'status':
            # 获取系统状态
            status = system.get_system_status()
            
            print("\n" + "=" * 60)
            print("系统状态")
            print("=" * 60)
            
            print(f"\n📋 系统信息:")
            print(f"  名称: {status['system']['name']}")
            print(f"  版本: {status['system']['version']}")
            print(f"  配置: {status['system']['config_path'] or '默认配置'}")
            print(f"  日志级别: {status['system']['log_level']}")
            
            print(f"\n🧩 模块状态:")
            for module, available in status['modules'].items():
                status_icon = "✅" if available else "❌"
                print(f"  {status_icon} {module}: {'可用' if available else '不可用'}")
            
            print(f"\n⚙️ 配置摘要:")
            print(f"  数据源: {', '.join(status['config_summary']['data_sources'])}")
            print(f"  分析模块: {', '.join(status['config_summary']['analysis_modules'])}")
            print(f"  默认策略: {', '.join(status['config_summary']['default_strategies'])}")
            print(f"  初始资金: {status['config_summary']['backtest_parameters']['initial_capital']:,}")
            print(f"  佣金费率: {status['config_summary']['backtest_parameters']['commission_rate']:.4f}")
        
        elif args.command == 'config':
            # 生成配置模板
            template = {
                'system': {
                    'name': 'MyTradingSystem',
                    'version': '1.0.0',
                    'log_level': 'INFO',
                    'log_dir': './logs',
                    'cache_dir': './cache',
                    'output_dir': './output'
                },
                'data': {
                    'default_source': 'local',
                    'local_data_dir': './data/example_data',
                    'cache_enabled': True,
                    'preprocessing_enabled': True,
                    'tushare': {
                        'token': 'YOUR_TUSHARE_TOKEN',
                        'timeout': 30
                    }
                },
                'analysis': {
                    'enable_price_action': True,
                    'enable_technical': True,
                    'enable_signal': True,
                    'result_integration': 'weighted',
                    'confidence_threshold': 0.6
                },
                'strategies': {
                    'default_strategies': ['MovingAverageAdapter', 'PriceActionSignal'],
                    'strategy_config_dir': './config/strategies',
                    'custom_strategies': []
                },
                'backtest': {
                    'initial_capital': 1000000,
                    'commission_rate': 0.0003,
                    'slippage': 0.0001,
                    'risk_management': True,
                    'stop_loss': 0.05,
                    'take_profit': 0.10
                },
                'reporting': {
                    'output_dir': './reports',
                    'default_format': 'markdown',
                    'enable_visualization': True,
                    'dashboard_enabled': True,
                    'email_report': False
                }
            }
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(template, f, ensure_ascii=False, indent=2)
            
            print(f"✅ 配置模板已生成: {args.output}")
            print("💡 提示: 请根据实际情况修改配置，特别是Tushare token等敏感信息")
    
    except Exception as e:
        print(f"❌ 错误: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()