#!/usr/bin/env python3
"""
回测引擎 - 扩展simple_backtest.py的回测功能
支持批量策略回测、绩效分析和报告生成
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any, Union, Tuple
import logging
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

from ..core.strategy_base import StrategyBase
from ..data.data_loader import DataLoader

logger = logging.getLogger(__name__)


class BacktestEngine:
    """
    回测引擎 - 执行策略回测和绩效分析
    """
    
    def __init__(self, initial_capital: float = 1000000, 
                 commission_rate: float = 0.0003,
                 slippage: float = 0.0,
                 data_loader: Optional[DataLoader] = None):
        """
        初始化回测引擎
        
        Args:
            initial_capital: 初始资金
            commission_rate: 交易佣金率
            slippage: 滑点率
            data_loader: 数据加载器实例
        """
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
        self.slippage = slippage
        
        # 数据加载器
        if data_loader is None:
            self.data_loader = DataLoader()
        else:
            self.data_loader = data_loader
        
        # 回测结果存储
        self.results = {}
        self.strategies = {}
        self.current_strategy = None
        
        logger.info(f"回测引擎初始化: 初始资金={initial_capital}, 佣金={commission_rate}, 滑点={slippage}")
    
    def run_single_backtest(self, strategy: StrategyBase, 
                           data: pd.DataFrame,
                           stock_code: str = "UNKNOWN",
                           strategy_name: Optional[str] = None) -> Dict[str, Any]:
        """
        运行单个策略回测
        
        Args:
            strategy: 策略实例
            data: 回测数据
            stock_code: 股票代码
            strategy_name: 策略名称（如未提供则使用策略自带的名称）
            
        Returns:
            回测结果字典
        """
        if strategy_name is None:
            strategy_name = strategy.name
        
        logger.info(f"开始回测: {strategy_name} @ {stock_code}")
        
        try:
            # 初始化策略
            strategy.initialize(self.initial_capital)
            
            # 准备数据
            if isinstance(data, pd.DataFrame) and not data.empty:
                processed_data = self.data_loader.preprocess_data(data)
            else:
                logger.error(f"回测数据无效: {stock_code}")
                return self._create_error_result(strategy_name, stock_code, "无效数据")
            
            # 策略处理数据
            strategy.on_data(processed_data)
            
            # 回测循环
            trades = []
            portfolio_values = []
            positions_history = []
            signals_history = []
            
            for i in range(len(processed_data)):
                if i < max(strategy.params.get('short_window', 20), 
                          strategy.params.get('long_window', 20), 
                          20):  # 确保有足够数据计算指标
                    # 更新投资组合价值
                    current_price = processed_data.iloc[i]['close']
                    strategy.update_portfolio(current_price)
                    portfolio_values.append(strategy.portfolio_value)
                    positions_history.append(strategy.position)
                    signals_history.append({'signal_type': 'hold', 'confidence': 0.0})
                    continue
                
                # 生成信号
                signal = strategy.generate_signal()
                signals_history.append(signal)
                
                # 执行交易
                current_price = processed_data.iloc[i]['close']
                trade = strategy.execute_trade(signal, current_price, self.commission_rate)
                
                if trade.get('action') in ['buy', 'sell']:
                    trades.append(trade)
                
                # 更新投资组合
                strategy.update_portfolio(current_price)
                portfolio_values.append(strategy.portfolio_value)
                positions_history.append(strategy.position)
            
            # 计算绩效指标
            performance = self._calculate_performance_metrics(
                strategy, portfolio_values, trades, processed_data
            )
            
            # 构建结果
            result = {
                'strategy_name': strategy_name,
                'stock_code': stock_code,
                'initial_capital': self.initial_capital,
                'final_portfolio': strategy.portfolio_value,
                'performance': performance,
                'trades': trades,
                'total_trades': len(trades),
                'portfolio_values': portfolio_values,
                'positions_history': positions_history,
                'signals_history': signals_history,
                'data_points': len(processed_data),
                'date_range': {
                    'start': processed_data.index[0].strftime('%Y-%m-%d'),
                    'end': processed_data.index[-1].strftime('%Y-%m-%d'),
                    'days': (processed_data.index[-1] - processed_data.index[0]).days
                },
                'backtest_time': datetime.now().isoformat(),
                'status': 'success'
            }
            
            # 缓存结果
            result_key = f"{strategy_name}_{stock_code}"
            self.results[result_key] = result
            self.strategies[result_key] = strategy
            
            logger.info(f"回测完成: {strategy_name} @ {stock_code}, "
                       f"总收益: {performance['total_return']:.2%}, "
                       f"夏普: {performance['sharpe_ratio']:.2f}, "
                       f"交易: {len(trades)}")
            
            return result
            
        except Exception as e:
            logger.error(f"回测失败 {strategy_name} @ {stock_code}: {e}", exc_info=True)
            return self._create_error_result(strategy_name, stock_code, str(e))
    
    def run_batch_backtest(self, strategies: List[StrategyBase],
                          stock_data: Dict[str, pd.DataFrame],
                          strategy_names: Optional[List[str]] = None) -> Dict[str, Dict[str, Any]]:
        """
        运行批量策略回测
        
        Args:
            strategies: 策略实例列表
            stock_data: 股票数据字典，键为股票代码，值为DataFrame
            strategy_names: 策略名称列表
            
        Returns:
            回测结果字典，键为"策略名_股票代码"
        """
        if strategy_names is None:
            strategy_names = [s.name for s in strategies]
        
        if len(strategies) != len(strategy_names):
            raise ValueError("策略实例和策略名称数量不匹配")
        
        all_results = {}
        total_combinations = len(strategies) * len(stock_data)
        completed = 0
        
        logger.info(f"开始批量回测: {len(strategies)}个策略 × {len(stock_data)}只股票 = {total_combinations}个组合")
        
        for strategy, strategy_name in zip(strategies, strategy_names):
            for stock_code, data in stock_data.items():
                try:
                    result = self.run_single_backtest(strategy, data, stock_code, strategy_name)
                    result_key = f"{strategy_name}_{stock_code}"
                    all_results[result_key] = result
                    completed += 1
                    
                    # 进度报告
                    if completed % 5 == 0 or completed == total_combinations:
                        logger.info(f"批量回测进度: {completed}/{total_combinations} "
                                  f"({completed/total_combinations*100:.1f}%)")
                        
                except Exception as e:
                    logger.error(f"批量回测失败 {strategy_name} @ {stock_code}: {e}")
                    result_key = f"{strategy_name}_{stock_code}"
                    all_results[result_key] = self._create_error_result(strategy_name, stock_code, str(e))
                    completed += 1
        
        logger.info(f"批量回测完成: {completed}/{total_combinations} 个组合")
        return all_results
    
    def _calculate_performance_metrics(self, strategy: StrategyBase,
                                     portfolio_values: List[float],
                                     trades: List[Dict[str, Any]],
                                     data: pd.DataFrame) -> Dict[str, Any]:
        """
        计算绩效指标
        
        Args:
            strategy: 策略实例
            portfolio_values: 投资组合价值历史
            trades: 交易记录
            data: 原始数据
            
        Returns:
            绩效指标字典
        """
        if len(portfolio_values) < 2:
            return {}
        
        returns = pd.Series(portfolio_values).pct_change().dropna()
        
        if len(returns) == 0:
            return {}
        
        # 基础收益指标
        total_return = (portfolio_values[-1] - self.initial_capital) / self.initial_capital
        
        # 年化指标（假设252个交易日）
        days = len(returns)
        annual_return = (1 + total_return) ** (252 / days) - 1 if days > 0 else 0
        
        # 波动率和夏普比率
        volatility = returns.std() * np.sqrt(252) if len(returns) > 0 else 0
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() if len(drawdown) > 0 else 0
        
        # Calmar比率
        calmar_ratio = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        
        # Sortino比率（只考虑下行风险）
        downside_returns = returns[returns < 0]
        downside_std = downside_returns.std() * np.sqrt(252) if len(downside_returns) > 0 else 0
        sortino_ratio = annual_return / downside_std if downside_std > 0 else 0
        
        # 交易统计
        trades_df = pd.DataFrame(trades) if trades else pd.DataFrame()
        if not trades_df.empty and 'action' in trades_df.columns:
            buy_trades = len(trades_df[trades_df['action'] == 'buy'])
            sell_trades = len(trades_df[trades_df['action'] == 'sell'])
            total_trades = buy_trades + sell_trades
            
            # 盈利交易统计
            if 'profit' in trades_df.columns:
                winning_trades = len(trades_df[trades_df['profit'] > 0])
                losing_trades = len(trades_df[trades_df['profit'] <= 0])
                win_rate = winning_trades / total_trades if total_trades > 0 else 0
                
                avg_win = trades_df[trades_df['profit'] > 0]['profit'].mean() if winning_trades > 0 else 0
                avg_loss = trades_df[trades_df['profit'] <= 0]['profit'].mean() if losing_trades > 0 else 0
                profit_factor = abs(avg_win * winning_trades / (avg_loss * losing_trades)) if losing_trades > 0 and avg_loss != 0 else 0
            else:
                winning_trades = losing_trades = win_rate = avg_win = avg_loss = profit_factor = 0
        else:
            buy_trades = sell_trades = total_trades = 0
            winning_trades = losing_trades = win_rate = avg_win = avg_loss = profit_factor = 0
        
        # 持仓时间统计
        if trades and 'timestamp' in trades[0]:
            try:
                trade_times = [pd.Timestamp(t['timestamp']) for t in trades if 'timestamp' in t]
                if len(trade_times) >= 2:
                    holding_periods = [(trade_times[i+1] - trade_times[i]).days 
                                      for i in range(0, len(trade_times)-1, 2)]
                    avg_holding_days = np.mean(holding_periods) if holding_periods else 0
                else:
                    avg_holding_days = 0
            except:
                avg_holding_days = 0
        else:
            avg_holding_days = 0
        
        # 与基准比较（假设基准为买入持有策略）
        if 'close' in data.columns and len(data) > 0:
            initial_price = data['close'].iloc[0]
            final_price = data['close'].iloc[-1]
            buy_hold_return = (final_price - initial_price) / initial_price
            excess_return = total_return - buy_hold_return
            alpha = excess_return  # 简化alpha计算
            beta = 1.0  # 简化beta计算
        else:
            buy_hold_return = excess_return = alpha = beta = 0
        
        metrics = {
            'total_return': float(total_return),
            'annual_return': float(annual_return),
            'volatility': float(volatility),
            'sharpe_ratio': float(sharpe_ratio),
            'max_drawdown': float(max_drawdown),
            'calmar_ratio': float(calmar_ratio),
            'sortino_ratio': float(sortino_ratio),
            'total_trades': int(total_trades),
            'buy_trades': int(buy_trades),
            'sell_trades': int(sell_trades),
            'winning_trades': int(winning_trades),
            'losing_trades': int(losing_trades),
            'win_rate': float(win_rate),
            'avg_win': float(avg_win),
            'avg_loss': float(avg_loss),
            'profit_factor': float(profit_factor),
            'avg_holding_days': float(avg_holding_days),
            'buy_hold_return': float(buy_hold_return),
            'excess_return': float(excess_return),
            'alpha': float(alpha),
            'beta': float(beta),
            'initial_capital': float(self.initial_capital),
            'final_portfolio': float(portfolio_values[-1]) if portfolio_values else float(self.initial_capital)
        }
        
        return metrics
    
    def _create_error_result(self, strategy_name: str, stock_code: str, 
                           error_msg: str) -> Dict[str, Any]:
        """创建错误结果"""
        return {
            'strategy_name': strategy_name,
            'stock_code': stock_code,
            'initial_capital': self.initial_capital,
            'final_portfolio': self.initial_capital,
            'performance': {
                'total_return': 0.0,
                'error': error_msg
            },
            'trades': [],
            'total_trades': 0,
            'portfolio_values': [self.initial_capital],
            'positions_history': [0],
            'signals_history': [],
            'data_points': 0,
            'date_range': {'start': None, 'end': None, 'days': 0},
            'backtest_time': datetime.now().isoformat(),
            'status': 'error',
            'error_message': error_msg
        }
    
    def generate_report(self, result: Dict[str, Any], 
                       output_dir: str = "./reports") -> Dict[str, str]:
        """
        生成回测报告
        
        Args:
            result: 回测结果
            output_dir: 输出目录
            
        Returns:
            报告文件路径字典
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            strategy_name = result['strategy_name']
            stock_code = result['stock_code']
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            
            # 1. 生成Markdown报告
            md_report = self._generate_markdown_report(result)
            md_filename = f"{strategy_name}_{stock_code}_{timestamp}.md"
            md_path = os.path.join(output_dir, md_filename)
            
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write(md_report)
            
            # 2. 生成JSON结果文件
            json_filename = f"{strategy_name}_{stock_code}_{timestamp}.json"
            json_path = os.path.join(output_dir, json_filename)
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2, default=str, ensure_ascii=False)
            
            # 3. 生成CSV交易记录
            if result['trades']:
                trades_df = pd.DataFrame(result['trades'])
                csv_filename = f"{strategy_name}_{stock_code}_{timestamp}_trades.csv"
                csv_path = os.path.join(output_dir, csv_filename)
                trades_df.to_csv(csv_path, index=False, encoding='utf-8')
            else:
                csv_path = None
            
            # 4. 生成投资组合价值CSV
            portfolio_df = pd.DataFrame({
                'portfolio_value': result['portfolio_values'],
                'position': result['positions_history']
            })
            portfolio_filename = f"{strategy_name}_{stock_code}_{timestamp}_portfolio.csv"
            portfolio_path = os.path.join(output_dir, portfolio_filename)
            portfolio_df.to_csv(portfolio_path, index=False)
            
            logger.info(f"报告生成完成: {strategy_name} @ {stock_code}")
            
            return {
                'markdown_report': md_path,
                'json_results': json_path,
                'trades_csv': csv_path,
                'portfolio_csv': portfolio_path
            }
            
        except Exception as e:
            logger.error(f"报告生成失败: {e}")
            return {}
    
    def _generate_markdown_report(self, result: Dict[str, Any]) -> str:
        """生成Markdown格式报告"""
        strategy_name = result['strategy_name']
        stock_code = result['stock_code']
        performance = result['performance']
        status = result.get('status', 'unknown')
        
        if status == 'error':
            error_msg = result.get('error_message', '未知错误')
            return f"""# 回测报告 - {strategy_name} @ {stock_code}

## 状态: ❌ 失败

### 错误信息
{error_msg}

### 基本信息
- **策略名称**: {strategy_name}
- **股票代码**: {stock_code}
- **回测时间**: {result.get('backtest_time', '未知')}
- **数据点数**: {result.get('data_points', 0)}
- **状态**: 失败

---
**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        # 成功回测的报告
        date_range = result.get('date_range', {})
        start_date = date_range.get('start', '未知')
        end_date = date_range.get('end', '未知')
        days = date_range.get('days', 0)
        
        # 格式化数字
        def fmt_pct(x):
            return f"{x:.2%}" if isinstance(x, (int, float)) else str(x)
        
        def fmt_num(x):
            if isinstance(x, (int, float)):
                if abs(x) >= 1e6:
                    return f"¥{x/1e6:.2f}M"
                elif abs(x) >= 1e3:
                    return f"¥{x/1e3:.1f}K"
                else:
                    return f"¥{x:.2f}"
            return str(x)
        
        report = f"""# 回测报告 - {strategy_name} @ {stock_code}

## 基本信息
| 项目 | 数值 |
|------|------|
| 策略名称 | {strategy_name} |
| 股票代码 | {stock_code} |
| 测试期间 | {start_date} 到 {end_date} ({days}天) |
| 初始资金 | {fmt_num(performance.get('initial_capital', 0))} |
| 最终资产 | {fmt_num(performance.get('final_portfolio', 0))} |
| 数据点数 | {result.get('data_points', 0)} |
| 回测时间 | {result.get('backtest_time', '未知')} |

## 绩效指标

### 收益指标
| 指标 | 数值 |
|------|------|
| 总收益率 | {fmt_pct(performance.get('total_return', 0))} |
| 年化收益率 | {fmt_pct(performance.get('annual_return', 0))} |
| 买入持有收益率 | {fmt_pct(performance.get('buy_hold_return', 0))} |
| 超额收益 | {fmt_pct(performance.get('excess_return', 0))} |
| Alpha | {fmt_pct(performance.get('alpha', 0))} |
| Beta | {performance.get('beta', 0):.2f} |

### 风险指标
| 指标 | 数值 |
|------|------|
| 年化波动率 | {fmt_pct(performance.get('volatility', 0))} |
| 最大回撤 | {fmt_pct(performance.get('max_drawdown', 0))} |
| 夏普比率 | {performance.get('sharpe_ratio', 0):.2f} |
| 索提诺比率 | {performance.get('sortino_ratio', 0):.2f} |
| Calmar比率 | {performance.get('calmar_ratio', 0):.2f} |

### 交易统计
| 指标 | 数值 |
|------|------|
| 总交易次数 | {performance.get('total_trades', 0)} |
| 买入交易 | {performance.get('buy_trades', 0)} |
| 卖出交易 | {performance.get('sell_trades', 0)} |
| 盈利交易 | {performance.get('winning_trades', 0)} |
| 亏损交易 | {performance.get('losing_trades', 0)} |
| 胜率 | {fmt_pct(performance.get('win_rate', 0))} |
| 平均盈利 | {fmt_num(performance.get('avg_win', 0))} |
| 平均亏损 | {fmt_num(performance.get('avg_loss', 0))} |
| 盈亏比 | {performance.get('profit_factor', 0):.2f} |
| 平均持仓天数 | {performance.get('avg_holding_days', 0):.1f}天 |

## 交易记录
总计 {performance.get('total_trades', 0)} 笔交易。

"""
        
        # 添加交易详情（前10笔）
        if result.get('trades') and len(result['trades']) > 0:
            report += "### 最近10笔交易\n"
            report += "| 时间 | 操作 | 价格 | 数量 | 金额 | 持仓后 | 现金后 |\n"
            report += "|------|------|------|------|------|--------|--------|\n"
            
            for i, trade in enumerate(result['trades'][-10:]):
                timestamp = trade.get('timestamp', '未知')
                action = trade.get('action', '未知')
                price = fmt_num(trade.get('price', 0))
                shares = trade.get('shares', 0)
                
                if action == 'buy':
                    amount = fmt_num(trade.get('cost', 0))
                elif action == 'sell':
                    amount = fmt_num(trade.get('revenue', 0))
                else:
                    amount = '0'
                
                position_after = trade.get('position_after', 0)
                cash_after = fmt_num(trade.get('cash_after', 0))
                
                report += f"| {timestamp} | {action} | {price} | {shares} | {amount} | {position_after} | {cash_after} |\n"
        
        # 添加总结和建议
        total_return = performance.get('total_return', 0)
        sharpe_ratio = performance.get('sharpe_ratio', 0)
        max_drawdown = performance.get('max_drawdown', 0)
        
        report += f"""
## 绩效总结

### 总体评价
"""
        
        if total_return > 0.2 and sharpe_ratio > 1.0 and max_drawdown > -0.1:
            report += "**优秀策略** - 高收益、高夏普比率、低回撤，建议实盘部署。\n"
        elif total_return > 0.1 and sharpe_ratio > 0.5:
            report += "**良好策略** - 收益和风险平衡较好，建议参数优化后部署。\n"
        elif total_return > 0:
            report += "**可行策略** - 有正收益但需要进一步优化风险管理。\n"
        else:
            report += "**需优化策略** - 收益为负或风险过高，需要重新设计。\n"
        
        report += f"""
### 关键优势
1. 总收益率: {fmt_pct(total_return)}
2. 夏普比率: {sharpe_ratio:.2f} (大于1为优秀)
3. 最大回撤: {fmt_pct(max_drawdown)} (小于-20%需关注)

### 改进建议
1. **参数优化**: 测试不同参数组合以提高收益
2. **风险管理**: 添加止损止盈机制控制回撤
3. **信号过滤**: 添加成交量或动量确认提高胜率
4. **仓位管理**: 优化仓位规模适应市场波动

## 下一步
1. 运行参数优化寻找最佳参数
2. 进行多股票验证测试稳健性
3. 整合到实盘交易系统
4. 持续监控和优化

---
**报告生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**回测引擎版本**: v1.0 (基于simple_backtest.py扩展)
**数据来源**: quant_trade-main数据系统
"""

        return report
    
    def compare_strategies(self, results_dict: Dict[str, Dict[str, Any]]) -> pd.DataFrame:
        """
        比较多个策略绩效
        
        Args:
            results_dict: 回测结果字典，键为策略标识
            
        Returns:
            比较DataFrame
        """
        comparison_data = []
        
        for key, result in results_dict.items():
            if result.get('status') != 'success':
                continue
            
            perf = result['performance']
            comparison_data.append({
                'strategy': result['strategy_name'],
                'stock': result['stock_code'],
                'total_return': perf.get('total_return', 0),
                'annual_return': perf.get('annual_return', 0),
                'sharpe_ratio': perf.get('sharpe_ratio', 0),
                'max_drawdown': perf.get('max_drawdown', 0),
                'win_rate': perf.get('win_rate', 0),
                'total_trades': perf.get('total_trades', 0),
                'final_portfolio': perf.get('final_portfolio', 0)
            })
        
        if not comparison_data:
            return pd.DataFrame()
        
        df = pd.DataFrame(comparison_data)
        
        # 排序（按夏普比率降序）
        if 'sharpe_ratio' in df.columns:
            df = df.sort_values('sharpe_ratio', ascending=False)
        
        return df


if __name__ == "__main__":
    """回测引擎测试"""
    import sys
    import os
    
    # 添加路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 测试回测引擎
    print("测试回测引擎...")
    
    # 创建数据加载器
    loader = DataLoader()
    
    # 创建测试数据
    test_data = loader._create_test_data("TEST001.SZ", "daily", days=100)
    
    # 创建策略
    from core.strategy_base import MovingAverageStrategy
    strategy = MovingAverageStrategy(short_window=5, long_window=20)
    
    # 创建回测引擎
    engine = BacktestEngine(initial_capital=1000000)
    
    # 运行回测
    result = engine.run_single_backtest(strategy, test_data, "TEST001.SZ")
    
    # 打印结果
    print(f"回测状态: {result.get('status')}")
    print(f"策略: {result.get('strategy_name')}")
    print(f"股票: {result.get('stock_code')}")
    
    perf = result.get('performance', {})
    print(f"总收益率: {perf.get('total_return', 0):.2%}")
    print(f"夏普比率: {perf.get('sharpe_ratio', 0):.2f}")
    print(f"最大回撤: {perf.get('max_drawdown', 0):.2%}")
    print(f"交易次数: {perf.get('total_trades', 0)}")
    
    # 生成报告
    reports = engine.generate_report(result, output_dir="./test_reports")
    print(f"报告生成: {reports}")
    
    print("回测引擎测试完成!")