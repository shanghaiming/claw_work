#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成回测系统 - 阶段4.4：回测层集成

整合以下组件:
1. 统一回测引擎 (backtest_engine.py)
2. 风险管理器 (risk_manager.py)
3. 绩效分析器 (performance_analyzer.py)

提供完整的回测、风险管理和绩效分析功能
"""

import numpy as np
import pandas as pd
import json
import os
import sys
import warnings
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime, timedelta
import logging
from pathlib import Path

# 添加路径以导入本地模块
current_dir = Path(__file__).parent
sys.path.append(str(current_dir))

warnings.filterwarnings('ignore')

# 导入本地模块
try:
    from backtest_engine import UnifiedBacktestEngine, create_demo_backtest_config
    BACKTEST_ENGINE_AVAILABLE = True
except ImportError as e:
    BACKTEST_ENGINE_AVAILABLE = False
    print(f"警告: 回测引擎导入失败: {e}")

try:
    from risk_manager import RiskManager, create_default_risk_config
    RISK_MANAGER_AVAILABLE = True
except ImportError as e:
    RISK_MANAGER_AVAILABLE = False
    print(f"警告: 风险管理器导入失败: {e}")

try:
    from performance_analyzer import PerformanceAnalyzer
    PERFORMANCE_ANALYZER_AVAILABLE = True
except ImportError as e:
    PERFORMANCE_ANALYZER_AVAILABLE = False
    print(f"警告: 绩效分析器导入失败: {e}")


class IntegratedBacktestSystem:
    """
    集成回测系统
    整合回测引擎、风险管理器和绩效分析器
    """
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """初始化集成回测系统
        
        Args:
            config: 系统配置字典，包含:
                - backtest_config: 回测引擎配置
                - risk_config: 风险管理配置
                - performance_config: 绩效分析配置
        """
        self.config = config or {}
        
        # 组件实例
        self.backtest_engine = None
        self.risk_manager = None
        self.performance_analyzer = None
        
        # 日志（必须在初始化组件之前设置）
        self.logger = self._setup_logger()
        
        # 初始化组件
        self._initialize_components()
        
        # 系统状态
        self.system_status = {
            'initialized': False,
            'components_available': {
                'backtest_engine': BACKTEST_ENGINE_AVAILABLE,
                'risk_manager': RISK_MANAGER_AVAILABLE,
                'performance_analyzer': PERFORMANCE_ANALYZER_AVAILABLE
            },
            'last_run': None,
            'total_runs': 0
        }
        
        # 更新初始化状态
        self.system_status['initialized'] = (
            self.backtest_engine is not None or 
            self.risk_manager is not None or 
            self.performance_analyzer is not None
        )
    
    def _setup_logger(self) -> logging.Logger:
        """设置日志记录器"""
        logger = logging.getLogger(f"IntegratedBacktestSystem_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        logger.setLevel(logging.INFO)
        
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        
        logger.addHandler(ch)
        return logger
    
    def _initialize_components(self):
        """初始化所有可用组件"""
        # 初始化回测引擎
        if BACKTEST_ENGINE_AVAILABLE:
            try:
                backtest_config = self.config.get('backtest_config', create_demo_backtest_config())
                self.backtest_engine = UnifiedBacktestEngine(backtest_config)
                self.logger.info("回测引擎初始化成功")
            except Exception as e:
                self.logger.warning(f"回测引擎初始化失败: {e}")
        
        # 初始化风险管理器
        if RISK_MANAGER_AVAILABLE:
            try:
                risk_config = self.config.get('risk_config', create_default_risk_config())
                self.risk_manager = RiskManager(risk_config)
                self.logger.info("风险管理器初始化成功")
            except Exception as e:
                self.logger.warning(f"风险管理器初始化失败: {e}")
        
        # 初始化绩效分析器
        if PERFORMANCE_ANALYZER_AVAILABLE:
            try:
                performance_config = self.config.get('performance_config', {})
                risk_free_rate = performance_config.get('risk_free_rate', 0.02)
                self.performance_analyzer = PerformanceAnalyzer(risk_free_rate)
                self.logger.info("绩效分析器初始化成功")
            except Exception as e:
                self.logger.warning(f"绩效分析器初始化失败: {e}")
    
    def run_complete_backtest(self, strategy_name: str, data: pd.DataFrame,
                            benchmark_data: Optional[pd.DataFrame] = None,
                            **kwargs) -> Dict[str, Any]:
        """运行完整的回测流程
        
        Args:
            strategy_name: 策略名称
            data: 策略数据 (OHLCV格式)
            benchmark_data: 基准数据 (可选)
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 完整的回测结果，包含:
                - backtest_result: 回测结果
                - risk_report: 风险报告
                - performance_report: 绩效报告
                - integrated_report: 综合报告
        """
        self.logger.info(f"开始完整回测流程: {strategy_name}")
        
        # 更新系统状态
        self.system_status['last_run'] = datetime.now()
        self.system_status['total_runs'] += 1
        
        # 结果容器
        results = {
            'strategy_name': strategy_name,
            'timestamp': datetime.now().isoformat(),
            'status': 'started',
            'components_used': [],
            'errors': []
        }
        
        # 1. 运行回测
        backtest_result = None
        if self.backtest_engine is not None:
            try:
                self.logger.info("步骤1: 运行回测引擎...")
                backtest_result = self.backtest_engine.run_backtest(strategy_name, data, **kwargs)
                results['backtest_result'] = backtest_result
                results['components_used'].append('backtest_engine')
                
                if backtest_result.get('status') == 'completed':
                    self.logger.info(f"回测完成: 总收益率={backtest_result['performance_metrics'].get('total_return', 0):.2%}")
                else:
                    self.logger.warning(f"回测失败: {backtest_result.get('error', '未知错误')}")
                    results['errors'].append(f"回测失败: {backtest_result.get('error', '未知错误')}")
                    
            except Exception as e:
                error_msg = f"回测引擎运行失败: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            self.logger.warning("回测引擎不可用，跳过回测步骤")
        
        # 2. 风险分析
        risk_report = None
        if self.risk_manager is not None and backtest_result is not None:
            try:
                self.logger.info("步骤2: 进行风险分析...")
                
                # 准备风险分析数据
                portfolio_state = {
                    'positions': backtest_result.get('positions', {}),
                    'equity_curve': backtest_result.get('equity_curve', []),
                    'account_size': backtest_result.get('performance_metrics', {}).get('initial_capital', 0),
                    'current_date': datetime.now()
                }
                
                # 计算风险报告
                risk_report = self.risk_manager.generate_risk_report(portfolio_state, data)
                results['risk_report'] = risk_report
                results['components_used'].append('risk_manager')
                
                self.logger.info(f"风险分析完成: 风险等级={risk_report.get('risk_level', 'unknown')}, "
                               f"警报数={risk_report.get('total_alerts', 0)}")
                
            except Exception as e:
                error_msg = f"风险分析失败: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            self.logger.warning("风险管理器不可用或回测结果为空，跳过风险分析")
        
        # 3. 绩效分析
        performance_report = None
        if self.performance_analyzer is not None and backtest_result is not None:
            try:
                self.logger.info("步骤3: 进行绩效分析...")
                
                # 准备基准收益率
                benchmark_returns = None
                if benchmark_data is not None and 'close' in benchmark_data.columns:
                    # 计算基准收益率
                    benchmark_prices = benchmark_data['close'].values
                    if len(benchmark_prices) > 1:
                        benchmark_returns = np.diff(benchmark_prices) / benchmark_prices[:-1]
                
                # 计算绩效报告
                equity_curve = backtest_result.get('equity_curve', [])
                trades = backtest_result.get('trades', [])
                dates = backtest_result.get('dates', [])
                
                performance_report = self.performance_analyzer.generate_comprehensive_report(
                    equity_curve, trades, dates, benchmark_returns
                )
                
                results['performance_report'] = performance_report
                results['components_used'].append('performance_analyzer')
                
                summary = performance_report.get('summary', {})
                self.logger.info(f"绩效分析完成: 绩效质量={summary.get('performance_quality', 'unknown')}, "
                               f"总体评分={summary.get('overall_rating', 0):.1f}/10")
                
            except Exception as e:
                error_msg = f"绩效分析失败: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        else:
            self.logger.warning("绩效分析器不可用或回测结果为空，跳过绩效分析")
        
        # 4. 生成综合报告
        integrated_report = None
        if backtest_result is not None:
            try:
                self.logger.info("步骤4: 生成综合报告...")
                integrated_report = self._generate_integrated_report(
                    strategy_name, backtest_result, risk_report, performance_report
                )
                results['integrated_report'] = integrated_report
                
                # 保存报告
                if kwargs.get('save_report', True):
                    self._save_reports(results, **kwargs)
                
            except Exception as e:
                error_msg = f"综合报告生成失败: {e}"
                self.logger.error(error_msg)
                results['errors'].append(error_msg)
        
        # 更新结果状态
        if results['errors']:
            results['status'] = 'completed_with_errors'
            self.logger.warning(f"回测流程完成但有错误: {len(results['errors'])} 个错误")
        else:
            results['status'] = 'completed'
            self.logger.info("回测流程成功完成")
        
        return results
    
    def _generate_integrated_report(self, strategy_name: str, backtest_result: Dict[str, Any],
                                  risk_report: Optional[Dict[str, Any]], 
                                  performance_report: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """生成综合报告
        
        Args:
            strategy_name: 策略名称
            backtest_result: 回测结果
            risk_report: 风险报告
            performance_report: 绩效报告
            
        Returns:
            Dict[str, Any]: 综合报告
        """
        # 提取关键指标
        backtest_metrics = backtest_result.get('performance_metrics', {})
        
        # 基本指标
        total_return = backtest_metrics.get('total_return', 0)
        annualized_return = backtest_metrics.get('annualized_return', 0)
        max_drawdown = backtest_metrics.get('max_drawdown', 0)
        sharpe_ratio = backtest_metrics.get('sharpe_ratio', 0)
        
        # 风险指标
        risk_level = 'unknown'
        risk_alerts = 0
        if risk_report is not None:
            risk_level = risk_report.get('risk_level', 'unknown')
            risk_alerts = risk_report.get('total_alerts', 0)
        
        # 绩效指标
        performance_quality = 'unknown'
        overall_rating = 0
        if performance_report is not None:
            summary = performance_report.get('summary', {})
            performance_quality = summary.get('performance_quality', 'unknown')
            overall_rating = summary.get('overall_rating', 0)
        
        # 生成建议
        recommendations = self._generate_recommendations(
            total_return, sharpe_ratio, max_drawdown, risk_level, performance_quality
        )
        
        # 生成综合评分
        integrated_score = self._calculate_integrated_score(
            total_return, sharpe_ratio, max_drawdown, risk_level, overall_rating
        )
        
        # 综合报告
        integrated_report = {
            'strategy_name': strategy_name,
            'generation_time': datetime.now().isoformat(),
            'key_metrics': {
                'total_return': float(total_return),
                'annualized_return': float(annualized_return),
                'max_drawdown': float(max_drawdown),
                'sharpe_ratio': float(sharpe_ratio),
                'risk_level': risk_level,
                'performance_quality': performance_quality,
                'overall_rating': float(overall_rating)
            },
            'integrated_score': float(integrated_score),
            'recommendations': recommendations,
            'component_reports': {
                'backtest_available': backtest_result is not None,
                'risk_available': risk_report is not None,
                'performance_available': performance_report is not None
            },
            'execution_summary': {
                'total_trades': backtest_metrics.get('total_trades', 0),
                'win_rate': backtest_metrics.get('win_rate', 0),
                'profit_factor': backtest_metrics.get('profit_factor', 0),
                'equity_final': backtest_metrics.get('final_equity', 0),
                'equity_peak': backtest_metrics.get('equity_peak', 0) if 'equity_peak' in backtest_metrics else backtest_metrics.get('final_equity', 0)
            }
        }
        
        self.logger.info(f"综合报告生成: 综合评分={integrated_score:.1f}/10, "
                        f"关键指标: 收益={total_return:.2%}, 夏普={sharpe_ratio:.2f}, "
                        f"回撤={max_drawdown:.2%}")
        
        return integrated_report
    
    def _generate_recommendations(self, total_return: float, sharpe_ratio: float, 
                                max_drawdown: float, risk_level: str, 
                                performance_quality: str) -> List[str]:
        """生成策略建议
        
        Args:
            total_return: 总收益率
            sharpe_ratio: 夏普比率
            max_drawdown: 最大回撤
            risk_level: 风险等级
            performance_quality: 绩效质量
            
        Returns:
            List[str]: 建议列表
        """
        recommendations = []
        
        # 收益相关建议
        if total_return < 0:
            recommendations.append("总收益为负，建议重新评估策略或优化参数")
        elif total_return < 0.05:  # 5%
            recommendations.append("收益较低，建议优化策略以提高收益")
        
        # 风险调整后收益建议
        if sharpe_ratio < 0:
            recommendations.append("夏普比率为负，风险调整后收益不佳")
        elif sharpe_ratio < 0.5:
            recommendations.append("夏普比率较低，建议优化风险收益比")
        
        # 回撤相关建议
        if max_drawdown > 0.2:  # 20%
            recommendations.append("最大回撤较大，建议加强风险管理")
        elif max_drawdown > 0.1:  # 10%
            recommendations.append("回撤适中，建议监控并设置合理的止损")
        
        # 风险等级建议
        if risk_level == 'high':
            recommendations.append("风险等级为'高'，建议减少仓位或暂停交易")
        elif risk_level == 'medium':
            recommendations.append("风险等级为'中'，建议保持谨慎并监控风险")
        
        # 绩效质量建议
        if performance_quality in ['poor', 'very_poor']:
            recommendations.append("绩效质量较差，建议全面优化策略")
        elif performance_quality == 'fair':
            recommendations.append("绩效质量一般，有优化空间")
        
        # 通用建议
        if not recommendations:
            recommendations.append("策略表现良好，建议继续执行并定期监控")
        else:
            recommendations.insert(0, "基于回测结果，以下建议供参考:")
        
        return recommendations
    
    def _calculate_integrated_score(self, total_return: float, sharpe_ratio: float, 
                                  max_drawdown: float, risk_level: str, 
                                  overall_rating: float) -> float:
        """计算综合评分 (0-10分)
        
        Args:
            total_return: 总收益率
            sharpe_ratio: 夏普比率
            max_drawdown: 最大回撤
            risk_level: 风险等级
            overall_rating: 总体评分
            
        Returns:
            float: 综合评分
        """
        # 权重分配
        weights = {
            'return': 0.3,      # 收益权重
            'sharpe': 0.25,     # 风险调整后收益权重
            'drawdown': 0.2,    # 回撤权重
            'risk': 0.15,       # 风险等级权重
            'rating': 0.1       # 总体评分权重
        }
        
        # 收益评分 (0-10)
        return_score = min(10.0, max(0, total_return * 100))  # 每1%收益得1分，最多10分
        
        # 夏普比率评分 (0-10)
        sharpe_score = min(10.0, max(0, sharpe_ratio * 2))  # 夏普比率*2作为分数
        
        # 回撤评分 (0-10，回撤越小分数越高)
        drawdown_score = 0
        if max_drawdown > 0:
            drawdown_score = min(10.0, max(0, (0.3 - max_drawdown) * 50))  # 30%回撤得0分，0%回撤得15分
        else:
            drawdown_score = 10.0
        
        # 风险等级评分 (0-10)
        risk_score_map = {'low': 9.0, 'medium': 6.0, 'high': 3.0, 'unknown': 5.0}
        risk_score = risk_score_map.get(risk_level, 5.0)
        
        # 总体评分 (已归一化到0-10)
        rating_score = min(10.0, max(0, overall_rating))
        
        # 计算加权总分
        integrated_score = (
            return_score * weights['return'] +
            sharpe_score * weights['sharpe'] +
            drawdown_score * weights['drawdown'] +
            risk_score * weights['risk'] +
            rating_score * weights['rating']
        )
        
        return round(integrated_score, 1)
    
    def _save_reports(self, results: Dict[str, Any], **kwargs):
        """保存报告文件
        
        Args:
            results: 回测结果
            **kwargs: 保存参数
        """
        try:
            output_dir = kwargs.get('output_dir', 'backtest_results')
            os.makedirs(output_dir, exist_ok=True)
            
            strategy_name = results.get('strategy_name', 'unknown').replace(' ', '_')
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 保存完整结果
            full_report_file = os.path.join(output_dir, f"full_report_{strategy_name}_{timestamp}.json")
            with open(full_report_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, default=str)
            
            # 保存综合报告
            integrated_report = results.get('integrated_report')
            if integrated_report:
                integrated_file = os.path.join(output_dir, f"integrated_report_{strategy_name}_{timestamp}.json")
                with open(integrated_file, 'w', encoding='utf-8') as f:
                    json.dump(integrated_report, f, indent=2, default=str)
            
            # 生成文本摘要
            summary_file = os.path.join(output_dir, f"summary_{strategy_name}_{timestamp}.txt")
            self._generate_text_summary(results, summary_file)
            
            self.logger.info(f"报告已保存到目录: {output_dir}")
            self.logger.info(f"完整报告: {full_report_file}")
            self.logger.info(f"综合报告: {integrated_file if integrated_report else '未生成'}")
            self.logger.info(f"文本摘要: {summary_file}")
            
        except Exception as e:
            self.logger.error(f"保存报告失败: {e}")
    
    def _generate_text_summary(self, results: Dict[str, Any], output_file: str):
        """生成文本摘要报告
        
        Args:
            results: 回测结果
            output_file: 输出文件路径
        """
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("=" * 80 + "\n")
                f.write(f"回测综合报告摘要\n")
                f.write(f"策略名称: {results.get('strategy_name', '未知策略')}\n")
                f.write(f"生成时间: {results.get('timestamp', datetime.now().isoformat())}\n")
                f.write(f"状态: {results.get('status', 'unknown')}\n")
                f.write("=" * 80 + "\n\n")
                
                # 显示使用的组件
                components_used = results.get('components_used', [])
                f.write("【使用的组件】\n")
                for component in components_used:
                    f.write(f"  ✓ {component}\n")
                f.write("\n")
                
                # 显示错误（如果有）
                errors = results.get('errors', [])
                if errors:
                    f.write("【错误信息】\n")
                    for i, error in enumerate(errors, 1):
                        f.write(f"  {i}. {error}\n")
                    f.write("\n")
                
                # 显示综合报告
                integrated_report = results.get('integrated_report')
                if integrated_report:
                    key_metrics = integrated_report.get('key_metrics', {})
                    
                    f.write("【关键指标】\n")
                    f.write(f"  总收益率: {key_metrics.get('total_return', 0):.2%}\n")
                    f.write(f"  年化收益率: {key_metrics.get('annualized_return', 0):.2%}\n")
                    f.write(f"  最大回撤: {key_metrics.get('max_drawdown', 0):.2%}\n")
                    f.write(f"  夏普比率: {key_metrics.get('sharpe_ratio', 0):.2f}\n")
                    f.write(f"  风险等级: {key_metrics.get('risk_level', 'unknown')}\n")
                    f.write(f"  绩效质量: {key_metrics.get('performance_quality', 'unknown')}\n")
                    f.write(f"  总体评分: {key_metrics.get('overall_rating', 0):.1f}/10\n")
                    f.write(f"  综合评分: {integrated_report.get('integrated_score', 0):.1f}/10\n")
                    f.write("\n")
                    
                    # 显示建议
                    recommendations = integrated_report.get('recommendations', [])
                    if recommendations:
                        f.write("【策略建议】\n")
                        for i, rec in enumerate(recommendations, 1):
                            f.write(f"  {i}. {rec}\n")
                        f.write("\n")
                
                # 显示执行摘要
                execution_summary = results.get('integrated_report', {}).get('execution_summary', {})
                if execution_summary:
                    f.write("【执行摘要】\n")
                    f.write(f"  总交易次数: {execution_summary.get('total_trades', 0)}\n")
                    f.write(f"  胜率: {execution_summary.get('win_rate', 0):.2%}\n")
                    f.write(f"  盈亏比: {execution_summary.get('profit_factor', 0):.2f}\n")
                    f.write(f"  最终权益: {execution_summary.get('equity_final', 0):,.2f}\n")
                    f.write(f"  峰值权益: {execution_summary.get('equity_peak', 0):,.2f}\n")
                    f.write("\n")
                
                f.write("=" * 80 + "\n")
                f.write("报告生成完成\n")
                
        except Exception as e:
            self.logger.error(f"生成文本摘要失败: {e}")
    
    def get_system_status(self) -> Dict[str, Any]:
        """获取系统状态
        
        Returns:
            Dict[str, Any]: 系统状态信息
        """
        return self.system_status
    
    def run_multiple_strategies(self, strategies: List[Dict[str, Any]], 
                              data: pd.DataFrame, 
                              benchmark_data: Optional[pd.DataFrame] = None,
                              **kwargs) -> Dict[str, Any]:
        """运行多个策略的比较回测
        
        Args:
            strategies: 策略列表，每个策略包含:
                - name: 策略名称
                - instance: 策略实例 (可选)
                - type: 策略类型
            data: 回测数据
            benchmark_data: 基准数据 (可选)
            **kwargs: 其他参数
            
        Returns:
            Dict[str, Any]: 多策略比较结果
        """
        self.logger.info(f"开始多策略比较回测，共 {len(strategies)} 个策略")
        
        results = {}
        all_reports = {}
        
        for strategy_info in strategies:
            strategy_name = strategy_info.get('name', f'strategy_{len(results)}')
            
            try:
                self.logger.info(f"运行策略: {strategy_name}")
                
                # 运行完整回测
                result = self.run_complete_backtest(
                    strategy_name, data, benchmark_data, 
                    save_report=False, **kwargs
                )
                
                results[strategy_name] = result
                all_reports[strategy_name] = result.get('integrated_report', {})
                
            except Exception as e:
                self.logger.error(f"策略 '{strategy_name}' 回测失败: {e}")
                results[strategy_name] = {
                    'status': 'failed',
                    'error': str(e)
                }
        
        # 生成比较报告
        comparison_report = self._generate_comparison_report(all_reports)
        
        # 保存比较报告
        if kwargs.get('save_report', True):
            output_dir = kwargs.get('output_dir', 'backtest_results')
            os.makedirs(output_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            comparison_file = os.path.join(output_dir, f"comparison_report_{timestamp}.json")
            
            with open(comparison_file, 'w', encoding='utf-8') as f:
                json.dump(comparison_report, f, indent=2, default=str)
            
            self.logger.info(f"比较报告已保存: {comparison_file}")
        
        return {
            'individual_results': results,
            'comparison_report': comparison_report,
            'total_strategies': len(strategies),
            'successful_strategies': sum(1 for r in results.values() if r.get('status') == 'completed'),
            'timestamp': datetime.now().isoformat()
        }
    
    def _generate_comparison_report(self, all_reports: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
        """生成策略比较报告
        
        Args:
            all_reports: 所有策略的综合报告
            
        Returns:
            Dict[str, Any]: 比较报告
        """
        comparison = {
            'strategies': [],
            'ranking_by_metric': {},
            'best_strategies': {},
            'summary_statistics': {},
            'generation_time': datetime.now().isoformat()
        }
        
        # 收集所有策略的指标
        all_metrics = []
        
        for strategy_name, report in all_reports.items():
            if not report:
                continue
            
            key_metrics = report.get('key_metrics', {})
            integrated_score = report.get('integrated_score', 0)
            
            strategy_data = {
                'name': strategy_name,
                'total_return': key_metrics.get('total_return', 0),
                'annualized_return': key_metrics.get('annualized_return', 0),
                'max_drawdown': key_metrics.get('max_drawdown', 0),
                'sharpe_ratio': key_metrics.get('sharpe_ratio', 0),
                'risk_level': key_metrics.get('risk_level', 'unknown'),
                'performance_quality': key_metrics.get('performance_quality', 'unknown'),
                'overall_rating': key_metrics.get('overall_rating', 0),
                'integrated_score': integrated_score
            }
            
            comparison['strategies'].append(strategy_data)
            all_metrics.append(strategy_data)
        
        if not all_metrics:
            return comparison
        
        # 按不同指标排序
        metrics_to_rank = ['total_return', 'sharpe_ratio', 'integrated_score', 'overall_rating']
        
        for metric in metrics_to_rank:
            sorted_strategies = sorted(all_metrics, key=lambda x: x.get(metric, 0), reverse=True)
            
            ranking = []
            for i, strategy in enumerate(sorted_strategies, 1):
                ranking.append({
                    'rank': i,
                    'strategy': strategy['name'],
                    'value': strategy.get(metric, 0)
                })
            
            comparison['ranking_by_metric'][metric] = ranking
            
            # 记录最佳策略
            if sorted_strategies:
                best_strategy = sorted_strategies[0]
                comparison['best_strategies'][metric] = {
                    'strategy': best_strategy['name'],
                    'value': best_strategy.get(metric, 0)
                }
        
        # 计算摘要统计
        if all_metrics:
            comparison['summary_statistics'] = {
                'avg_total_return': np.mean([m['total_return'] for m in all_metrics]),
                'avg_sharpe_ratio': np.mean([m['sharpe_ratio'] for m in all_metrics]),
                'avg_max_drawdown': np.mean([m['max_drawdown'] for m in all_metrics]),
                'avg_integrated_score': np.mean([m['integrated_score'] for m in all_metrics]),
                'total_strategies': len(all_metrics),
                'best_overall_strategy': max(all_metrics, key=lambda x: x.get('integrated_score', 0))['name']
            }
        
        return comparison


def create_integrated_system_config() -> Dict[str, Any]:
    """创建集成系统配置"""
    return {
        'backtest_config': {
            'initial_capital': 100000.0,
            'commission_rate': 0.001,
            'slippage': 0.001,
            'max_position_pct': 0.1,
            'risk_free_rate': 0.02,
            'data_config': {
                'cache_enabled': True,
                'preprocessing_enabled': False,
                'default_source': 'local',
                'local_data_dir': './data/example_data'
            }
        },
        
        'risk_config': {
            'max_position_risk': 0.02,
            'max_portfolio_risk': 0.1,
            'max_drawdown_limit': 0.2,
            'stop_loss_pct': 0.05,
            'take_profit_pct': 0.1,
            'volatility_window': 20,
            'correlation_window': 60,
            'risk_free_rate': 0.02
        },
        
        'performance_config': {
            'risk_free_rate': 0.02
        }
    }


def demo_integrated_system():
    """演示集成回测系统"""
    print("=" * 80)
    print("集成回测系统演示")
    print("=" * 80)
    
    # 创建集成系统
    config = create_integrated_system_config()
    system = IntegratedBacktestSystem(config)
    
    # 检查系统状态
    status = system.get_system_status()
    print(f"\n系统状态:")
    print(f"  初始化: {'成功' if status['initialized'] else '失败'}")
    print(f"  组件可用性:")
    for component, available in status['components_available'].items():
        print(f"    {component}: {'可用' if available else '不可用'}")
    
    if not status['initialized']:
        print("\n警告: 系统初始化失败，无法运行演示")
        return
    
    # 生成示例数据
    print("\n生成示例数据...")
    np.random.seed(42)
    days = 100
    initial_equity = 100000
    
    # 生成随机收益率
    daily_returns = np.random.normal(0.0005, 0.02, days)
    
    # 生成权益曲线（用于模拟价格）
    price_series = initial_equity * np.cumprod(1 + daily_returns)
    
    # 创建DataFrame
    dates = pd.date_range(start='2023-01-01', periods=days, freq='D')
    data = pd.DataFrame({
        'open': price_series * 0.99,
        'high': price_series * 1.01,
        'low': price_series * 0.98,
        'close': price_series,
        'volume': np.random.randint(100000, 1000000, days)
    }, index=dates)
    
    print(f"数据生成完成: {len(data)} 行，{data.index[0]} 到 {data.index[-1]}")
    
    # 运行单策略回测
    print("\n运行单策略回测演示...")
    try:
        result = system.run_complete_backtest(
            strategy_name="DemoStrategy",
            data=data,
            benchmark_data=data,  # 使用相同数据作为基准
            save_report=True,
            output_dir='demo_results'
        )
        
        if result['status'] == 'completed':
            print(f"回测成功完成!")
            
            integrated_report = result.get('integrated_report', {})
            if integrated_report:
                key_metrics = integrated_report.get('key_metrics', {})
                print(f"\n综合报告:")
                print(f"  总收益率: {key_metrics.get('total_return', 0):.2%}")
                print(f"  最大回撤: {key_metrics.get('max_drawdown', 0):.2%}")
                print(f"  夏普比率: {key_metrics.get('sharpe_ratio', 0):.2f}")
                print(f"  风险等级: {key_metrics.get('risk_level', 'unknown')}")
                print(f"  综合评分: {integrated_report.get('integrated_score', 0):.1f}/10")
                
                # 显示建议
                recommendations = integrated_report.get('recommendations', [])
                if recommendations:
                    print(f"\n策略建议:")
                    for i, rec in enumerate(recommendations, 1):
                        print(f"  {i}. {rec}")
        else:
            print(f"回测失败: {result.get('errors', ['未知错误'])}")
    
    except Exception as e:
        print(f"回测失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 运行多策略比较（如果系统支持）
    print("\n" + "=" * 80)
    print("演示完成")
    
    # 显示下一步操作建议
    print("\n下一步操作建议:")
    print("1. 使用真实数据替换示例数据")
    print("2. 配置自定义策略")
    print("3. 调整风险参数以适应不同市场")
    print("4. 使用多策略比较功能评估不同策略表现")
    print("5. 定期生成风险报告监控策略风险")


if __name__ == "__main__":
    # 运行演示
    demo_integrated_system()