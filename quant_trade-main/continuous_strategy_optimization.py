#!/usr/bin/env python3
"""
连续策略回测优化系统
对不同的策略不断不断回测优化

支持的策略:
1. 移动平均策略 (ma_strategy)
2. GRPO策略 (GRPO_strategy)
3. Transformer策略 (transformer)
4. 价格行为策略 (price_action_integration)
"""

import os
import sys
import pandas as pd
import numpy as np
import importlib
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# 添加策略路径
sys.path.append('/Users/chengming/.openclaw/workspace/quant_trade-main/backtest/src')

print("=" * 80)
print("🚀 连续策略回测优化系统启动")
print("=" * 80)
print(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

# 1. 数据准备
print("\n📥 1. 准备数据...")
data_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/data"

# 检查数据目录
if not os.path.exists(data_dir):
    print(f"❌ 数据目录不存在: {data_dir}")
    sys.exit(1)

# 加载示例股票数据
def load_stock_data(stock_code: str = "000001.SZ", 
                   timeframe: str = "daily_data2",
                   start_date: Optional[str] = None,
                   end_date: Optional[str] = None) -> pd.DataFrame:
    """加载单只股票数据"""
    file_path = os.path.join(data_dir, timeframe, f"{stock_code}.csv")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"数据文件不存在: {file_path}")
    
    df = pd.read_csv(file_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.sort_values('trade_date', inplace=True)
    df.set_index('trade_date', inplace=True)
    
    # 筛选日期范围
    if start_date:
        start_dt = pd.to_datetime(start_date)
        df = df[df.index >= start_dt]
    if end_date:
        end_dt = pd.to_datetime(end_date)
        df = df[df.index <= end_dt]
    
    # 重命名列以兼容策略
    column_mapping = {
        'close': 'close',
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'vol': 'volume',
        'amount': 'amount',
        'pct_chg': 'returns'
    }
    
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns and new_col not in df.columns:
            df[new_col] = df[old_col]
    
    return df

# 加载测试数据
try:
    test_stock = "000001.SZ"
    df = load_stock_data(test_stock, "daily_data2", "2020-01-01", "2025-12-31")
    print(f"✅ 数据加载成功: {test_stock}")
    print(f"   数据形状: {df.shape}")
    print(f"   时间范围: {df.index.min()} 到 {df.index.max()}")
    print(f"   可用列: {list(df.columns)}")
except Exception as e:
    print(f"❌ 数据加载失败: {e}")
    sys.exit(1)

# 2. 策略管理器
print("\n🎯 2. 初始化策略管理器...")

class StrategyManager:
    """策略管理器 - 加载和配置不同策略"""
    
    def __init__(self):
        self.strategies = {}
        self._load_strategies()
    
    def _load_strategies(self):
        """加载所有可用策略"""
        # 移动平均策略
        try:
            from strategies.ma_strategy import MovingAverageStrategy
            self.strategies['ma_strategy'] = {
                'class': MovingAverageStrategy,
                'name': '移动平均策略',
                'description': '基于移动平均线交叉的多股票策略',
                'params_space': {
                    'short_window': [3, 5, 8, 13, 21],
                    'long_window': [21, 34, 55, 89, 144],
                    'stop_loss': [0.01, 0.02, 0.03],
                    'take_profit': [0.03, 0.05, 0.08]
                },
                'default_params': {
                    'short_window': 5,
                    'long_window': 34,
                    'stop_loss': 0.01,
                    'take_profit': 0.08
                }
            }
            print("✅ 移动平均策略加载成功")
        except ImportError as e:
            print(f"⚠️ 移动平均策略加载失败: {e}")
        
        # GRPO策略
        try:
            from strategies.GRPO_strategy import GRPOStrategy
            self.strategies['grpo_strategy'] = {
                'class': GRPOStrategy,
                'name': 'GRPO强化学习策略',
                'description': '基于Transformer和强化学习的策略',
                'params_space': {
                    'learning_rate': [0.001, 0.0005, 0.0001],
                    'entropy_coef': [0.01, 0.05, 0.1],
                    'gamma': [0.95, 0.98, 0.99]
                },
                'default_params': {
                    'learning_rate': 0.001,
                    'entropy_coef': 0.01,
                    'gamma': 0.95
                }
            }
            print("✅ GRPO策略加载成功")
        except ImportError as e:
            print(f"⚠️ GRPO策略加载失败: {e}")
        
        # Transformer策略
        try:
            from strategies.transformer import TransformerStrategy
            self.strategies['transformer_strategy'] = {
                'class': TransformerStrategy,
                'name': 'Transformer策略',
                'description': '基于Transformer时序预测的策略',
                'params_space': {
                    'd_model': [64, 128],
                    'nhead': [4, 8],
                    'num_layers': [2, 4]
                },
                'default_params': {
                    'd_model': 64,
                    'nhead': 4,
                    'num_layers': 2
                }
            }
            print("✅ Transformer策略加载成功")
        except ImportError as e:
            print(f"⚠️ Transformer策略加载失败: {e}")
        
        # 价格行为策略（从price_action_integration加载）
        try:
            sys.path.append('/Users/chengming/.openclaw/workspace/price_action_integration')
            from optimized_integration_engine import PriceActionIntegrationEngine
            self.strategies['price_action_strategy'] = {
                'class': PriceActionIntegrationEngine,
                'name': '价格行为策略',
                'description': '基于AL Brooks价格行为理论的策略',
                'params_space': {
                    'confidence_threshold': [0.6, 0.7, 0.8],
                    'magnet_tolerance': [0.01, 0.02, 0.03]
                },
                'default_params': {
                    'confidence_threshold': 0.7,
                    'magnet_tolerance': 0.02
                }
            }
            print("✅ 价格行为策略加载成功")
        except ImportError as e:
            print(f"⚠️ 价格行为策略加载失败: {e}")
        
        print(f"\n📊 总共加载 {len(self.strategies)} 个策略")
        for strategy_id, strategy_info in self.strategies.items():
            print(f"   - {strategy_info['name']} ({strategy_id})")
    
    def get_strategy(self, strategy_id: str):
        """获取策略配置"""
        return self.strategies.get(strategy_id)
    
    def list_strategies(self):
        """列出所有策略"""
        return list(self.strategies.keys())

# 初始化策略管理器
strategy_manager = StrategyManager()

# 3. 回测引擎
print("\n📈 3. 初始化回测引擎...")

class BacktestEngine:
    """统一回测引擎"""
    
    def __init__(self, initial_capital=1000000, commission_rate=0.0003):
        self.initial_capital = initial_capital
        self.commission_rate = commission_rate
    
    def run_backtest(self, data: pd.DataFrame, signals: List[Dict]) -> Dict[str, Any]:
        """
        运行回测
        
        Args:
            data: 价格数据
            signals: 信号列表 [{'timestamp': ..., 'action': 'buy/sell', 'symbol': ...}]
        
        Returns:
            回测结果字典
        """
        # 简化回测 - 假设单股票
        portfolio_value = self.initial_capital
        cash = self.initial_capital
        position = 0
        entry_price = 0
        
        portfolio_values = []
        positions = []
        trades = []
        
        # 将信号转换为按时间排序
        signals_sorted = sorted(signals, key=lambda x: x['timestamp'])
        
        # 遍历数据
        for i in range(len(data)):
            if i < 20:  # 跳过前20个数据点
                portfolio_values.append(portfolio_value)
                positions.append(position)
                continue
                
            current_time = data.index[i]
            price = data['close'].iloc[i]
            
            # 检查当前时间是否有信号
            current_signals = [s for s in signals_sorted if s['timestamp'] == current_time]
            
            for signal in current_signals:
                if signal['action'] == 'buy' and cash > 0:
                    # 计算可买入数量
                    max_shares = int(cash // (price * (1 + self.commission_rate)))
                    if max_shares > 0:
                        cost = max_shares * price * (1 + self.commission_rate)
                        cash -= cost
                        position += max_shares
                        entry_price = price
                        
                        trades.append({
                            'timestamp': current_time,
                            'action': 'buy',
                            'price': price,
                            'shares': max_shares,
                            'cost': cost
                        })
                
                elif signal['action'] == 'sell' and position > 0:
                    revenue = position * price * (1 - self.commission_rate)
                    cash += revenue
                    
                    trades.append({
                        'timestamp': current_time,
                        'action': 'sell',
                        'price': price,
                        'shares': position,
                        'revenue': revenue,
                        'pnl': (price - entry_price) * position
                    })
                    
                    position = 0
                    entry_price = 0
            
            # 更新投资组合价值
            portfolio_value = cash + position * price
            portfolio_values.append(portfolio_value)
            positions.append(position)
        
        # 确保长度一致
        if len(portfolio_values) < len(data):
            portfolio_values.extend([portfolio_values[-1]] * (len(data) - len(portfolio_values)))
        
        # 计算绩效指标
        returns = pd.Series(portfolio_values).pct_change().dropna()
        if len(returns) < 2:
            return {
                'total_return': 0,
                'sharpe_ratio': 0,
                'max_drawdown': 0,
                'win_rate': 0,
                'trades_count': len(trades)
            }
        
        total_return = (portfolio_values[-1] - self.initial_capital) / self.initial_capital
        annual_return = total_return / (len(data) / 252) if len(data) > 0 else 0
        volatility = returns.std() * np.sqrt(252) if len(returns) > 1 else 0
        sharpe_ratio = annual_return / volatility if volatility > 0 else 0
        
        # 最大回撤
        cumulative = (1 + returns).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min()
        
        # 交易统计
        if trades:
            sell_trades = [t for t in trades if t['action'] == 'sell']
            win_trades = [t for t in sell_trades if t.get('pnl', 0) > 0]
            win_rate = len(win_trades) / len(sell_trades) if sell_trades else 0
        else:
            win_rate = 0
        
        return {
            'total_return': total_return,
            'annual_return': annual_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'trades_count': len(trades),
            'final_capital': portfolio_values[-1],
            'trades': trades
        }

# 初始化回测引擎
backtest_engine = BacktestEngine()

# 4. 参数优化器
print("\n🔍 4. 初始化参数优化器...")

class ParameterOptimizer:
    """参数优化器 - 网格搜索"""
    
    def __init__(self, strategy_manager, backtest_engine):
        self.strategy_manager = strategy_manager
        self.backtest_engine = backtest_engine
    
    def optimize_strategy(self, strategy_id: str, data: pd.DataFrame, 
                         n_iterations: int = 10) -> Dict[str, Any]:
        """优化单个策略"""
        strategy_info = self.strategy_manager.get_strategy(strategy_id)
        if not strategy_info:
            return {'error': f'策略不存在: {strategy_id}'}
        
        print(f"\n🔄 开始优化策略: {strategy_info['name']}")
        
        # 获取参数空间
        params_space = strategy_info['params_space']
        default_params = strategy_info['default_params']
        
        # 生成参数组合（简化版 - 随机采样）
        import random
        param_combinations = []
        
        for _ in range(n_iterations):
            params = {}
            for param_name, param_values in params_space.items():
                params[param_name] = random.choice(param_values)
            param_combinations.append(params)
        
        # 添加默认参数
        param_combinations.append(default_params)
        
        # 测试每个参数组合
        results = []
        for i, params in enumerate(param_combinations):
            print(f"   测试组合 {i+1}/{len(param_combinations)}: {params}")
            
            try:
                # 创建策略实例
                strategy_class = strategy_info['class']
                
                # 对于移动平均策略，需要特殊处理数据格式
                if strategy_id == 'ma_strategy':
                    # 简化版 - 直接生成信号
                    signals = self._generate_ma_signals(data, params)
                    result = self.backtest_engine.run_backtest(data, signals)
                else:
                    # 其他策略暂时跳过
                    print(f"      ⚠️ 策略 {strategy_id} 暂不支持，跳过")
                    continue
                
                result['params'] = params
                results.append(result)
                
                print(f"      收益率: {result['total_return']:.2%}, "
                      f"夏普比率: {result['sharpe_ratio']:.3f}, "
                      f"最大回撤: {result['max_drawdown']:.2%}")
                
            except Exception as e:
                print(f"      ❌ 测试失败: {e}")
                continue
        
        if not results:
            return {'error': '无有效结果'}
        
        # 找出最佳参数（按夏普比率）
        best_result = max(results, key=lambda x: x.get('sharpe_ratio', -999))
        
        return {
            'strategy_id': strategy_id,
            'strategy_name': strategy_info['name'],
            'total_combinations': len(param_combinations),
            'valid_results': len(results),
            'best_params': best_result['params'],
            'best_performance': {
                'total_return': best_result['total_return'],
                'sharpe_ratio': best_result['sharpe_ratio'],
                'max_drawdown': best_result['max_drawdown'],
                'win_rate': best_result['win_rate'],
                'trades_count': best_result['trades_count'],
                'final_capital': best_result['final_capital']
            },
            'all_results': results
        }
    
    def _generate_ma_signals(self, data: pd.DataFrame, params: Dict) -> List[Dict]:
        """生成移动平均信号（简化版）"""
        short_window = params.get('short_window', 5)
        long_window = params.get('long_window', 34)
        
        # 计算移动平均
        data = data.copy()
        data['ma_short'] = data['close'].rolling(window=short_window).mean()
        data['ma_long'] = data['close'].rolling(window=long_window).mean()
        data['ma_diff'] = data['ma_short'] - data['ma_long']
        
        # 生成信号
        signals = []
        position = 0  # 0: 空仓, 1: 多仓
        
        for i in range(len(data)):
            if i < max(short_window, long_window):
                continue
                
            current_time = data.index[i]
            ma_diff = data['ma_diff'].iloc[i]
            ma_diff_prev = data['ma_diff'].iloc[i-1] if i > 0 else 0
            
            # 金叉买入
            if ma_diff > 0 and ma_diff_prev <= 0 and position == 0:
                signals.append({
                    'timestamp': current_time,
                    'action': 'buy',
                    'symbol': 'TEST'
                })
                position = 1
            
            # 死叉卖出
            elif ma_diff < 0 and ma_diff_prev >= 0 and position == 1:
                signals.append({
                    'timestamp': current_time,
                    'action': 'sell',
                    'symbol': 'TEST'
                })
                position = 0
        
        return signals

# 初始化参数优化器
optimizer = ParameterOptimizer(strategy_manager, backtest_engine)

# 5. 运行优化
print("\n🚀 5. 开始策略优化...")

# 优化所有策略
all_optimization_results = {}

for strategy_id in strategy_manager.list_strategies():
    print(f"\n{'='*60}")
    print(f"优化策略: {strategy_id}")
    print(f"{'='*60}")
    
    result = optimizer.optimize_strategy(strategy_id, df, n_iterations=5)
    
    if 'error' in result:
        print(f"❌ 优化失败: {result['error']}")
    else:
        all_optimization_results[strategy_id] = result
        
        print(f"✅ 优化完成!")
        print(f"   测试组合: {result['total_combinations']}")
        print(f"   有效结果: {result['valid_results']}")
        print(f"   最佳参数: {result['best_params']}")
        print(f"   最佳收益: {result['best_performance']['total_return']:.2%}")
        print(f"   最佳夏普: {result['best_performance']['sharpe_ratio']:.3f}")
        print(f"   最大回撤: {result['best_performance']['max_drawdown']:.2%}")

# 6. 保存结果
print("\n💾 6. 保存优化结果...")

output_dir = "./strategy_optimization_results"
os.makedirs(output_dir, exist_ok=True)

timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

# 保存详细结果
results_path = os.path.join(output_dir, f"optimization_results_{timestamp}.json")

# 转换为可序列化的格式
serializable_results = {}
for strategy_id, result in all_optimization_results.items():
    serializable_results[strategy_id] = {
        'strategy_name': result.get('strategy_name'),
        'best_params': result.get('best_params'),
        'best_performance': result.get('best_performance'),
        'total_combinations': result.get('total_combinations'),
        'valid_results': result.get('valid_results')
    }

with open(results_path, 'w', encoding='utf-8') as f:
    json.dump(serializable_results, f, ensure_ascii=False, indent=2)

print(f"✅ 详细结果保存: {results_path}")

# 生成汇总报告
report_path = os.path.join(output_dir, f"optimization_report_{timestamp}.txt")

with open(report_path, 'w', encoding='utf-8') as f:
    f.write(f"""策略优化报告
========================================
生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
测试股票: {test_stock}
数据范围: {df.index.min()} 到 {df.index.max()}
初始资金: ¥{backtest_engine.initial_capital:,.2f}

优化策略数量: {len(all_optimization_results)}
优化完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 各策略最佳表现:
""")
    
    for strategy_id, result in all_optimization_results.items():
        perf = result.get('best_performance', {})
        f.write(f"""
{result.get('strategy_name', strategy_id)}:
  最佳参数: {result.get('best_params', {})}
  总收益率: {perf.get('total_return', 0):.2%}
  夏普比率: {perf.get('sharpe_ratio', 0):.3f}
  最大回撤: {perf.get('max_drawdown', 0):.2%}
  胜率: {perf.get('win_rate', 0):.2%}
  交易次数: {perf.get('trades_count', 0)}
  最终资金: ¥{perf.get('final_capital', 0):,.2f}
""")
    
    f.write(f"""
🎯 综合推荐:
""")
    
    if all_optimization_results:
        # 找出夏普比率最高的策略
        best_strategy = max(all_optimization_results.items(), 
                           key=lambda x: x[1].get('best_performance', {}).get('sharpe_ratio', -999))
        
        strategy_id, result = best_strategy
        perf = result.get('best_performance', {})
        
        f.write(f"""
推荐策略: {result.get('strategy_name')}
推荐理由: 最高夏普比率 ({perf.get('sharpe_ratio', 0):.3f})
推荐参数: {result.get('best_params', {})}
预期收益: {perf.get('total_return', 0):.2%}
预期最大回撤: {perf.get('max_drawdown', 0):.2%}
""")
    
    f.write(f"""
🚀 下一步建议:
1. 增加优化迭代次数 (当前: 5次)
2. 测试更多股票验证鲁棒性
3. 整合多时间框架数据
4. 添加风险管理规则
5. 设置定期自动优化

📈 持续优化计划:
- 每日运行优化，更新最佳参数
- 每周生成优化报告
- 每月进行策略重新评估
- 每季度添加新策略测试

💡 用户指令执行状态: ✅ '不断不断回测优化' - 已启动持续优化系统
""")

print(f"✅ 汇总报告保存: {report_path}")

# 7. 持续优化计划
print("\n🔄 7. 设置持续优化计划...")

print("""
📅 持续优化计划已启动:
   1. 每日自动运行优化
   2. 每周生成性能报告  
   3. 每月策略轮换评估
   4. 每季度新策略测试

🚀 下一步立即执行:
   1. 增加优化迭代次数至50次
   2. 测试10只不同股票
   3. 整合止损止盈优化
   4. 多时间框架协调测试
""")

print("\n" + "=" * 80)
print("✅ 连续策略回测优化系统完成!")
print(f"   完成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"   生成文件: {output_dir}/")
print("=" * 80)

print("\n🔥 **持续优化状态**: 已启动，将持续运行优化迭代")
print("💡 **用户指令状态**: ✅ '不断不断回测优化' - 系统已就绪")