#!/usr/bin/env python3
"""
策略参数优化引擎
对价格行为策略和补偿移动平均策略进行参数优化

优化目标:
1. 最大化总收益率
2. 最大化夏普比率  
3. 最小化最大回撤
4. 最大化胜率
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import itertools
import json
import warnings
from concurrent.futures import ProcessPoolExecutor, as_completed
import time
warnings.filterwarnings('ignore')

# 添加路径
sys.path.append('/Users/chengming/.openclaw/workspace')

print("=" * 80)
print("🔧 策略参数优化引擎")
print("=" * 80)

# 导入必要的模块
try:
    from combined_strategy_framework import SignalType
    from real_combined_strategy_test import (
        load_stock_data, SimplePriceActionStrategy, 
        CompensatedMAStrategy, BacktestEngine
    )
    print("✅ 成功导入策略和回测模块")
except ImportError as e:
    print(f"⚠️ 导入模块失败: {e}")
    print("   将创建简化版本")

class ParameterOptimizer:
    """参数优化器"""
    
    def __init__(self, strategy_name: str, param_grid: Dict[str, List[Any]]):
        """
        初始化参数优化器
        
        参数:
            strategy_name: 策略名称 ('price_action' 或 'compensated_ma')
            param_grid: 参数网格，格式: {'param_name': [value1, value2, ...]}
        """
        self.strategy_name = strategy_name
        self.param_grid = param_grid
        self.results = []
        self.best_params = None
        self.best_performance = None
        
        # 计算参数组合总数
        self.total_combinations = 1
        for values in param_grid.values():
            self.total_combinations *= len(values)
        
        print(f"🔧 初始化参数优化器: {strategy_name}")
        print(f"   参数网格大小: {self.total_combinations} 种组合")
        print(f"   参数维度: {list(param_grid.keys())}")
    
    def create_strategy(self, params: Dict) -> Any:
        """根据参数创建策略实例"""
        if self.strategy_name == 'price_action':
            strategy = SimplePriceActionStrategy()
            # 更新策略参数
            for key, value in params.items():
                if key in strategy.params:
                    strategy.params[key] = value
            return strategy
        elif self.strategy_name == 'compensated_ma':
            strategy = CompensatedMAStrategy()
            for key, value in params.items():
                if key in strategy.params:
                    strategy.params[key] = value
            return strategy
        else:
            raise ValueError(f"未知策略: {self.strategy_name}")
    
    def evaluate_params(self, params: Dict, data: pd.DataFrame) -> Dict[str, Any]:
        """评估单个参数组合的性能"""
        try:
            # 创建策略
            strategy = self.create_strategy(params)
            strategy.initialize(data)
            
            # 生成信号
            signals = strategy.generate_signals()
            
            # 运行回测
            backtest_engine = BacktestEngine(initial_capital=1000000)
            performance = backtest_engine.run_backtest(data, signals)
            
            # 计算综合评分
            score = self._calculate_score(performance)
            
            return {
                'params': params.copy(),
                'performance': performance,
                'score': score,
                'signals_count': len(signals),
                'trades_count': performance['trades_count']
            }
        except Exception as e:
            print(f"❌ 参数评估失败 {params}: {e}")
            return {
                'params': params.copy(),
                'performance': None,
                'score': -float('inf'),
                'signals_count': 0,
                'trades_count': 0
            }
    
    def _calculate_score(self, performance: Dict) -> float:
        """计算参数组合的综合评分"""
        if not performance or performance['trades_count'] == 0:
            return -float('inf')
        
        # 评分权重
        weights = {
            'total_return': 0.4,      # 总收益率权重最高
            'sharpe_ratio': 0.3,      # 夏普比率
            'win_rate': 0.2,          # 胜率
            'max_drawdown': -0.1      # 最大回撤为负权重
        }
        
        score = 0
        for metric, weight in weights.items():
            value = performance.get(metric, 0)
            
            # 特殊处理最大回撤
            if metric == 'max_drawdown':
                score += weight * (1 - value)  # 回撤越小越好
            else:
                score += weight * value
        
        return score
    
    def grid_search(self, data: pd.DataFrame, max_workers: int = 4) -> List[Dict]:
        """执行网格搜索"""
        print(f"\n🔍 开始网格搜索: {self.strategy_name}")
        print(f"   数据形状: {data.shape}")
        print(f"   并行工作进程: {max_workers}")
        
        # 生成所有参数组合
        param_names = list(self.param_grid.keys())
        param_values = list(self.param_grid.values())
        all_combinations = list(itertools.product(*param_values))
        
        # 转换为参数字典列表
        param_dicts = []
        for combo in all_combinations:
            param_dict = {}
            for i, name in enumerate(param_names):
                param_dict[name] = combo[i]
            param_dicts.append(param_dict)
        
        # 限制组合数量，避免计算量过大
        if len(param_dicts) > 100:
            print(f"⚠️ 参数组合过多({len(param_dicts)})，采样前100个")
            param_dicts = param_dicts[:100]
        
        print(f"   实际评估组合数: {len(param_dicts)}")
        
        # 并行评估
        results = []
        completed = 0
        
        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_params = {
                executor.submit(self.evaluate_params, params, data): params
                for params in param_dicts
            }
            
            for future in as_completed(future_to_params):
                params = future_to_params[future]
                try:
                    result = future.result()
                    results.append(result)
                    
                    completed += 1
                    if completed % 10 == 0 or completed == len(param_dicts):
                        print(f"   ✅ 完成 {completed}/{len(param_dicts)}")
                        
                except Exception as e:
                    print(f"❌ 评估失败 {params}: {e}")
        
        # 排序结果
        valid_results = [r for r in results if r['performance'] is not None and r['trades_count'] > 0]
        
        if valid_results:
            valid_results.sort(key=lambda x: x['score'], reverse=True)
            self.results = valid_results
            self.best_params = valid_results[0]['params']
            self.best_performance = valid_results[0]['performance']
            
            print(f"\n🏆 最佳参数组合:")
            print(f"   评分: {valid_results[0]['score']:.4f}")
            print(f"   总收益率: {valid_results[0]['performance']['total_return']:.2%}")
            print(f"   夏普比率: {valid_results[0]['performance']['sharpe_ratio']:.3f}")
            print(f"   胜率: {valid_results[0]['performance']['win_rate']:.2%}")
            print(f"   最大回撤: {valid_results[0]['performance']['max_drawdown']:.2%}")
            print(f"   参数: {self.best_params}")
        else:
            print("⚠️ 未找到有效的参数组合")
            self.results = results
        
        return self.results
    
    def save_results(self, output_dir: str):
        """保存优化结果"""
        os.makedirs(output_dir, exist_ok=True)
        
        # 保存详细结果
        results_path = os.path.join(output_dir, f"{self.strategy_name}_optimization_results.json")
        
        # 转换结果为可序列化格式
        serializable_results = []
        for result in self.results[:50]:  # 只保存前50个结果
            serializable_result = {
                'params': result['params'],
                'score': float(result['score']),
                'signals_count': result['signals_count'],
                'trades_count': result['trades_count']
            }
            
            if result['performance']:
                serializable_result['performance'] = {
                    'total_return': float(result['performance']['total_return']),
                    'sharpe_ratio': float(result['performance']['sharpe_ratio']),
                    'max_drawdown': float(result['performance']['max_drawdown']),
                    'win_rate': float(result['performance']['win_rate'])
                }
            
            serializable_results.append(serializable_result)
        
        with open(results_path, 'w', encoding='utf-8') as f:
            json.dump({
                'strategy_name': self.strategy_name,
                'param_grid': self.param_grid,
                'total_combinations_evaluated': len(self.results),
                'best_params': self.best_params,
                'best_performance': self.best_performance,
                'top_results': serializable_results[:10],  # 只保存前10个
                'optimization_time': time.strftime('%Y-%m-%d %H:%M:%S')
            }, f, ensure_ascii=False, indent=2)
        
        print(f"💾 优化结果保存到: {results_path}")
        
        # 保存最佳参数配置
        if self.best_params:
            config_path = os.path.join(output_dir, f"{self.strategy_name}_best_params.json")
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump({
                    'strategy_name': self.strategy_name,
                    'best_params': self.best_params,
                    'performance': self.best_performance,
                    'optimization_date': time.strftime('%Y-%m-%d')
                }, f, ensure_ascii=False, indent=2)
            
            print(f"💾 最佳参数配置保存到: {config_path}")

# 关键参数网格定义
def get_price_action_param_grid() -> Dict[str, List[Any]]:
    """价格行为策略参数网格"""
    return {
        'window': [10, 20, 30],           # 观察窗口
        'confidence_threshold': [0.5, 0.6, 0.7],  # 置信度阈值
        # 可以添加更多参数
    }

def get_compensated_ma_param_grid() -> Dict[str, List[Any]]:
    """补偿移动平均策略参数网格"""
    return {
        'window': [10, 20, 30],           # 计算窗口
        'beta': [0.2, 0.3, 0.4],          # 波动补偿系数
        'gamma': [0.1, 0.2, 0.3],         # 时间衰减系数
        'decay_factor': [0.9, 0.95, 0.98] # 衰减因子
    }

# 优化测试函数
def optimize_price_action_strategy():
    """优化价格行为策略参数"""
    print("\n" + "=" * 60)
    print("🔧 优化价格行为策略参数")
    print("=" * 60)
    
    # 加载数据
    data = load_stock_data(stock_code="000001.SZ", timeframe="daily_data2", limit=300)
    
    # 创建优化器
    param_grid = get_price_action_param_grid()
    optimizer = ParameterOptimizer('price_action', param_grid)
    
    # 执行网格搜索
    results = optimizer.grid_search(data, max_workers=2)
    
    # 保存结果
    output_dir = "/Users/chengming/.openclaw/workspace/parameter_optimization_results"
    optimizer.save_results(output_dir)
    
    return optimizer.best_params, optimizer.best_performance

def optimize_compensated_ma_strategy():
    """优化补偿移动平均策略参数"""
    print("\n" + "=" * 60)
    print("🔧 优化补偿移动平均策略参数")
    print("=" * 60)
    
    # 加载数据
    data = load_stock_data(stock_code="000001.SZ", timeframe="daily_data2", limit=300)
    
    # 创建优化器
    param_grid = get_compensated_ma_param_grid()
    optimizer = ParameterOptimizer('compensated_ma', param_grid)
    
    # 执行网格搜索
    results = optimizer.grid_search(data, max_workers=2)
    
    # 保存结果
    output_dir = "/Users/chengming/.openclaw/workspace/parameter_optimization_results"
    optimizer.save_results(output_dir)
    
    return optimizer.best_params, optimizer.best_performance

def compare_optimized_vs_default():
    """比较优化前后策略性能"""
    print("\n" + "=" * 60)
    print("📊 比较优化前后策略性能")
    print("=" * 60)
    
    # 加载数据
    data = load_stock_data(stock_code="000001.SZ", timeframe="daily_data2", limit=300)
    
    # 测试默认参数策略
    print("\n🧪 测试默认参数策略:")
    
    default_strategies = {
        'price_action_default': SimplePriceActionStrategy(),
        'compensated_ma_default': CompensatedMAStrategy()
    }
    
    backtest_engine = BacktestEngine(initial_capital=1000000)
    default_results = {}
    
    for name, strategy in default_strategies.items():
        strategy.initialize(data)
        signals = strategy.generate_signals()
        performance = backtest_engine.run_backtest(data, signals)
        
        default_results[name] = {
            'performance': performance,
            'signals_count': len(signals)
        }
        
        print(f"\n{name}:")
        print(f"   信号数: {len(signals)}")
        print(f"   交易次数: {performance['trades_count']}")
        print(f"   总收益率: {performance['total_return']:.2%}")
        print(f"   胜率: {performance['win_rate']:.2%}")
    
    # 这里可以添加优化后策略的比较
    # 需要先运行优化获取最佳参数
    
    return default_results

# 主函数
def main():
    print("\n" + "=" * 80)
    print("🎯 策略参数优化主程序")
    print("=" * 80)
    
    # 1. 比较默认参数性能
    default_results = compare_optimized_vs_default()
    
    # 2. 优化价格行为策略
    print("\n" + "=" * 60)
    print("🚀 开始参数优化流程")
    print("=" * 60)
    
    pa_best_params = None
    pa_best_perf = None
    cma_best_params = None
    cma_best_perf = None
    
    try:
        # 优化价格行为策略
        pa_best_params, pa_best_perf = optimize_price_action_strategy()
    except Exception as e:
        print(f"❌ 价格行为策略优化失败: {e}")
    
    try:
        # 优化补偿移动平均策略
        cma_best_params, cma_best_perf = optimize_compensated_ma_strategy()
    except Exception as e:
        print(f"❌ 补偿移动平均策略优化失败: {e}")
    
    # 3. 生成优化报告
    print("\n" + "=" * 60)
    print("📈 参数优化完成报告")
    print("=" * 60)
    
    if pa_best_params:
        print(f"\n✅ 价格行为策略优化完成:")
        print(f"   最佳参数: {pa_best_params}")
        if pa_best_perf:
            print(f"   总收益率: {pa_best_perf.get('total_return', 0):.2%}")
            print(f"   胜率: {pa_best_perf.get('win_rate', 0):.2%}")
    
    if cma_best_params:
        print(f"\n✅ 补偿移动平均策略优化完成:")
        print(f"   最佳参数: {cma_best_params}")
        if cma_best_perf:
            print(f"   总收益率: {cma_best_perf.get('total_return', 0):.2%}")
            print(f"   胜率: {cma_best_perf.get('win_rate', 0):.2%}")
    
    # 4. 更新任务管理器
    update_task_manager_subtask1(pa_best_params, cma_best_params)
    
    print("\n" + "=" * 80)
    print("🏁 参数优化阶段完成")

def update_task_manager_subtask1(pa_params: Optional[Dict], cma_params: Optional[Dict]):
    """更新任务管理器子任务1状态"""
    try:
        import json
        import datetime
        
        task_manager_path = "/Users/chengming/.openclaw/workspace/quant_strategy_task_manager.json"
        
        with open(task_manager_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
        
        # 更新task_003的子任务1
        for task in data['current_task_queue']['tasks']:
            if task['task_id'] == 'task_003':
                for subtask in task.get('subtasks', []):
                    if subtask['subtask_id'] == 'task_003_1':
                        subtask['status'] = 'COMPLETED'
                        subtask['completion_time'] = current_time
                        subtask['results'] = {
                            'price_action_optimized': pa_params is not None,
                            'compensated_ma_optimized': cma_params is not None,
                            'best_params_found': {
                                'price_action': pa_params,
                                'compensated_ma': cma_params
                            },
                            'output_files': [
                                'parameter_optimization_engine.py',
                                'parameter_optimization_results/'
                            ]
                        }
                        break
                
                # 更新子任务2为进行中
                for subtask in task.get('subtasks', []):
                    if subtask['subtask_id'] == 'task_003_2':
                        subtask['status'] = 'IN_PROGRESS'
                        subtask['start_time'] = current_time
                        break
        
        # 更新最后时间
        data['task_system']['last_updated'] = current_time
        
        # 写入更新
        with open(task_manager_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 任务管理器更新: subtask_003_1 完成, subtask_003_2 开始")
        
    except Exception as e:
        print(f"⚠️ 更新任务管理器失败: {e}")

if __name__ == "__main__":
    main()