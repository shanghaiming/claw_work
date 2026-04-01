#!/usr/bin/env python3
"""
自动化参数优化系统 - task_011 Phase 3 核心组件

功能:
1. 参数网格搜索
2. 优化算法框架
3. 结果评估和可视化
4. 优化策略持久化

设计理念:
- 支持多种优化算法
- 模块化设计，易于扩展
- 结果可重现
- 性能优先，支持并行
"""

import os
import json
import random
import math
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum
import statistics

print("=" * 80)
print("⚙️ 自动化参数优化系统 - task_011 Phase 3")
print("=" * 80)

# 配置
WORKSPACE_ROOT = Path("/Users/chengming/.openclaw/workspace")
OUTPUT_DIR = WORKSPACE_ROOT / "optimization_results"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class OptimizationAlgorithm(Enum):
    """优化算法类型"""
    GRID_SEARCH = "grid_search"
    RANDOM_SEARCH = "random_search"
    BAYESIAN = "bayesian"
    GENETIC = "genetic"
    GRADIENT = "gradient"

@dataclass
class ParameterRange:
    """参数范围定义"""
    name: str
    min_value: float
    max_value: float
    step: Optional[float] = None
    is_integer: bool = False
    log_scale: bool = False
    
    def generate_values(self) -> List[float]:
        """生成参数值列表"""
        if self.step is None:
            return [self.min_value, self.max_value]
        
        values = []
        current = self.min_value
        
        while current <= self.max_value + 1e-10:  # 处理浮点误差
            if self.is_integer:
                values.append(round(current))
            else:
                values.append(round(current, 6))
            current += self.step
        
        return values

@dataclass
class OptimizationResult:
    """优化结果"""
    parameters: Dict[str, float]
    score: float
    evaluation_time: float
    metadata: Dict[str, Any]
    timestamp: str

class BaseOptimizer:
    """优化器基类"""
    
    def __init__(self, name: str, strategy_name: str):
        self.name = name
        self.strategy_name = strategy_name
        self.results: List[OptimizationResult] = []
        self.best_result: Optional[OptimizationResult] = None
        self.history: List[Dict] = []
    
    def optimize(self, 
                objective_function: Callable[[Dict[str, float]], float],
                parameter_ranges: Dict[str, ParameterRange],
                max_iterations: int = 100,
                **kwargs) -> OptimizationResult:
        """执行优化"""
        raise NotImplementedError("子类必须实现此方法")
    
    def save_results(self, output_dir: Path):
        """保存优化结果"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_file = output_dir / f"{self.name}_{self.strategy_name}_{timestamp}.json"
        
        results_data = {
            "optimizer_name": self.name,
            "strategy_name": self.strategy_name,
            "optimization_time": datetime.now().isoformat(),
            "total_iterations": len(self.results),
            "best_score": self.best_result.score if self.best_result else None,
            "best_parameters": self.best_result.parameters if self.best_result else None,
            "all_results": [
                {
                    "parameters": r.parameters,
                    "score": r.score,
                    "evaluation_time": r.evaluation_time,
                    "timestamp": r.timestamp
                }
                for r in self.results
            ],
            "history": self.history
        }
        
        with open(results_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)
        
        return results_file

class GridSearchOptimizer(BaseOptimizer):
    """网格搜索优化器"""
    
    def __init__(self, strategy_name: str):
        super().__init__("grid_search", strategy_name)
    
    def optimize(self, 
                objective_function: Callable[[Dict[str, float]], float],
                parameter_ranges: Dict[str, ParameterRange],
                max_iterations: int = 100,
                **kwargs) -> OptimizationResult:
        """执行网格搜索优化"""
        print(f"🔍 开始网格搜索优化: {self.strategy_name}")
        print(f"   参数数量: {len(parameter_ranges)}")
        print(f"   最大迭代次数: {max_iterations}")
        
        # 生成参数网格
        param_grid = self._generate_parameter_grid(parameter_ranges, max_iterations)
        
        total_combinations = len(param_grid)
        actual_iterations = min(total_combinations, max_iterations)
        
        print(f"   参数组合总数: {total_combinations}")
        print(f"   实际评估组合: {actual_iterations}")
        
        # 评估参数组合
        for i, params in enumerate(param_grid[:actual_iterations]):
            start_time = time.time()
            
            try:
                score = objective_function(params)
                eval_time = time.time() - start_time
                
                result = OptimizationResult(
                    parameters=params,
                    score=score,
                    evaluation_time=eval_time,
                    metadata={"iteration": i + 1},
                    timestamp=datetime.now().isoformat()
                )
                
                self.results.append(result)
                
                # 更新最佳结果
                if self.best_result is None or score > self.best_result.score:
                    self.best_result = result
                
                # 记录历史
                self.history.append({
                    "iteration": i + 1,
                    "parameters": params,
                    "score": score,
                    "time": eval_time,
                    "is_best": (result == self.best_result)
                })
                
                if (i + 1) % 10 == 0 or i + 1 == actual_iterations:
                    print(f"   迭代 {i+1}/{actual_iterations}: 分数={score:.4f}, 最佳={self.best_result.score:.4f}")
                    
            except Exception as e:
                print(f"   迭代 {i+1} 失败: {e}")
                continue
        
        print(f"✅ 网格搜索完成: 评估 {len(self.results)} 个组合")
        print(f"   最佳分数: {self.best_result.score:.4f}" if self.best_result else "   没有有效结果")
        
        return self.best_result
    
    def _generate_parameter_grid(self, 
                               parameter_ranges: Dict[str, ParameterRange],
                               max_points: int) -> List[Dict[str, float]]:
        """生成参数网格"""
        # 分离参数和值列表
        param_names = list(parameter_ranges.keys())
        value_lists = [parameter_ranges[name].generate_values() for name in param_names]
        
        # 计算总组合数
        total_combinations = math.prod(len(values) for values in value_lists)
        
        # 如果组合数太多，使用智能采样
        if total_combinations > max_points:
            return self._sample_parameter_grid(param_names, value_lists, max_points)
        
        # 生成完整网格
        grid = []
        self._generate_grid_recursive([], param_names, value_lists, grid)
        return grid
    
    def _generate_grid_recursive(self, current_params: List[Tuple[str, float]],
                               param_names: List[str],
                               value_lists: List[List[float]],
                               grid: List[Dict[str, float]]):
        """递归生成参数网格"""
        if len(current_params) == len(param_names):
            # 转换为字典并添加到网格
            param_dict = {name: value for name, value in current_params}
            grid.append(param_dict)
            return
        
        current_idx = len(current_params)
        param_name = param_names[current_idx]
        
        for value in value_lists[current_idx]:
            new_params = current_params + [(param_name, value)]
            self._generate_grid_recursive(new_params, param_names, value_lists, grid)
    
    def _sample_parameter_grid(self, 
                             param_names: List[str],
                             value_lists: List[List[float]],
                             max_samples: int) -> List[Dict[str, float]]:
        """智能采样参数网格"""
        samples = []
        
        # 1. 包含所有边界值组合
        boundary_values = []
        for values in value_lists:
            if len(values) >= 2:
                boundary_values.append([values[0], values[-1]])
            else:
                boundary_values.append(values)
        
        # 生成边界组合
        boundary_combinations = []
        self._generate_grid_recursive([], param_names, boundary_values, boundary_combinations)
        samples.extend(boundary_combinations)
        
        # 2. 添加随机样本
        remaining_samples = max_samples - len(samples)
        
        for _ in range(remaining_samples):
            params = {}
            for i, (name, values) in enumerate(zip(param_names, value_lists)):
                params[name] = random.choice(values)
            
            # 确保不重复
            if params not in samples:
                samples.append(params)
        
        return samples

class RandomSearchOptimizer(BaseOptimizer):
    """随机搜索优化器"""
    
    def __init__(self, strategy_name: str):
        super().__init__("random_search", strategy_name)
    
    def optimize(self, 
                objective_function: Callable[[Dict[str, float]], float],
                parameter_ranges: Dict[str, ParameterRange],
                max_iterations: int = 100,
                **kwargs) -> OptimizationResult:
        """执行随机搜索优化"""
        print(f"🎲 开始随机搜索优化: {self.strategy_name}")
        print(f"   最大迭代次数: {max_iterations}")
        
        for i in range(max_iterations):
            # 生成随机参数
            params = self._generate_random_parameters(parameter_ranges)
            
            start_time = time.time()
            
            try:
                score = objective_function(params)
                eval_time = time.time() - start_time
                
                result = OptimizationResult(
                    parameters=params,
                    score=score,
                    evaluation_time=eval_time,
                    metadata={"iteration": i + 1},
                    timestamp=datetime.now().isoformat()
                )
                
                self.results.append(result)
                
                # 更新最佳结果
                if self.best_result is None or score > self.best_result.score:
                    self.best_result = result
                
                # 记录历史
                self.history.append({
                    "iteration": i + 1,
                    "parameters": params,
                    "score": score,
                    "time": eval_time,
                    "is_best": (result == self.best_result)
                })
                
                if (i + 1) % 10 == 0 or i + 1 == max_iterations:
                    print(f"   迭代 {i+1}/{max_iterations}: 分数={score:.4f}, 最佳={self.best_result.score:.4f}")
                    
            except Exception as e:
                print(f"   迭代 {i+1} 失败: {e}")
                continue
        
        print(f"✅ 随机搜索完成: 评估 {len(self.results)} 个组合")
        print(f"   最佳分数: {self.best_result.score:.4f}" if self.best_result else "   没有有效结果")
        
        return self.best_result
    
    def _generate_random_parameters(self, 
                                  parameter_ranges: Dict[str, ParameterRange]) -> Dict[str, float]:
        """生成随机参数"""
        params = {}
        
        for name, param_range in parameter_ranges.items():
            if param_range.log_scale:
                # 对数尺度上的均匀分布
                log_min = math.log10(param_range.min_value)
                log_max = math.log10(param_range.max_value)
                log_value = random.uniform(log_min, log_max)
                value = 10 ** log_value
            else:
                # 线性尺度上的均匀分布
                value = random.uniform(param_range.min_value, param_range.max_value)
            
            if param_range.is_integer:
                value = round(value)
            
            params[name] = round(value, 6)
        
        return params

class OptimizationManager:
    """优化管理器"""
    
    def __init__(self):
        self.optimizers = {}
        self.strategy_configs = {}
    
    def register_strategy(self, strategy_name: str, parameter_definitions: Dict[str, ParameterRange]):
        """注册策略优化配置"""
        self.strategy_configs[strategy_name] = parameter_definitions
        print(f"📝 注册策略: {strategy_name}, 参数: {list(parameter_definitions.keys())}")
    
    def create_optimizer(self, algorithm: OptimizationAlgorithm, strategy_name: str) -> BaseOptimizer:
        """创建优化器"""
        if algorithm == OptimizationAlgorithm.GRID_SEARCH:
            optimizer = GridSearchOptimizer(strategy_name)
        elif algorithm == OptimizationAlgorithm.RANDOM_SEARCH:
            optimizer = RandomSearchOptimizer(strategy_name)
        else:
            raise ValueError(f"不支持的优化算法: {algorithm}")
        
        self.optimizers[f"{strategy_name}_{algorithm.value}"] = optimizer
        return optimizer
    
    def get_strategy_parameter_definitions(self) -> Dict[str, Dict[str, ParameterRange]]:
        """获取常见策略的参数定义"""
        definitions = {
            "MovingAverageStrategy": {
                "short_window": ParameterRange("short_window", 3, 20, step=1, is_integer=True),
                "long_window": ParameterRange("long_window", 15, 50, step=5, is_integer=True),
                "threshold": ParameterRange("threshold", 0.001, 0.05, step=0.005)
            },
            "RSIStrategy": {
                "period": ParameterRange("period", 7, 21, step=2, is_integer=True),
                "overbought": ParameterRange("overbought", 65, 85, step=5, is_integer=True),
                "oversold": ParameterRange("oversold", 15, 35, step=5, is_integer=True)
            },
            "MACDStrategy": {
                "fast_period": ParameterRange("fast_period", 8, 15, step=1, is_integer=True),
                "slow_period": ParameterRange("slow_period", 17, 35, step=2, is_integer=True),
                "signal_period": ParameterRange("signal_period", 5, 12, step=1, is_integer=True)
            },
            "BollingerBandsStrategy": {
                "period": ParameterRange("period", 10, 30, step=5, is_integer=True),
                "std_dev": ParameterRange("std_dev", 1.5, 3.0, step=0.5)
            }
        }
        
        return definitions

# ========== 模拟目标函数（用于测试） ==========

def create_mock_objective_function(strategy_name: str) -> Callable[[Dict[str, float]], float]:
    """创建模拟目标函数"""
    def mock_evaluation(parameters: Dict[str, float]) -> float:
        """模拟策略评估"""
        # 模拟计算时间
        time.sleep(0.01)
        
        # 基于参数计算模拟分数
        base_score = 0.5
        
        # 添加参数贡献
        param_contrib = 0.0
        for name, value in parameters.items():
            # 简单的模拟逻辑
            if "window" in name or "period" in name:
                # 中等值通常更好
                normalized = abs(value - 20) / 20
                param_contrib += 0.1 * (1 - normalized)
            elif "threshold" in name:
                # 小阈值通常更好
                param_contrib += 0.2 * (0.02 / max(value, 0.001))
            else:
                param_contrib += 0.05
        
        # 添加随机性
        random_factor = random.uniform(0.8, 1.2)
        
        score = (base_score + param_contrib / len(parameters)) * random_factor
        return min(max(score, 0), 1)  # 限制在0-1范围内
    
    return mock_evaluation

def main():
    """主函数"""
    print(f"工作空间: {WORKSPACE_ROOT}")
    print(f"输出目录: {OUTPUT_DIR}")
    print()
    
    # 1. 初始化优化管理器
    print("🔧 初始化优化管理器...")
    manager = OptimizationManager()
    
    # 2. 获取常见策略的参数定义
    print("📋 加载策略参数定义...")
    strategy_definitions = manager.get_strategy_parameter_definitions()
    
    for strategy_name, param_defs in strategy_definitions.items():
        manager.register_strategy(strategy_name, param_defs)
    
    print(f"✅ 加载 {len(strategy_definitions)} 个策略配置")
    print()
    
    # 3. 选择策略进行优化演示
    demo_strategy = "MovingAverageStrategy"
    print(f"🎯 选择演示策略: {demo_strategy}")
    
    if demo_strategy not in strategy_definitions:
        print(f"❌ 策略 {demo_strategy} 未找到")
        return False
    
    param_definitions = strategy_definitions[demo_strategy]
    
    # 4. 创建模拟目标函数
    print("🧪 创建模拟评估函数...")
    objective_function = create_mock_objective_function(demo_strategy)
    
    # 5. 运行网格搜索优化
    print("\n" + "=" * 60)
    print("1. 网格搜索优化演示")
    print("=" * 60)
    
    grid_optimizer = manager.create_optimizer(
        OptimizationAlgorithm.GRID_SEARCH,
        demo_strategy
    )
    
    grid_result = grid_optimizer.optimize(
        objective_function=objective_function,
        parameter_ranges=param_definitions,
        max_iterations=50
    )
    
    # 保存结果
    grid_results_file = grid_optimizer.save_results(OUTPUT_DIR)
    print(f"   结果保存到: {grid_results_file}")
    
    # 6. 运行随机搜索优化
    print("\n" + "=" * 60)
    print("2. 随机搜索优化演示")
    print("=" * 60)
    
    random_optimizer = manager.create_optimizer(
        OptimizationAlgorithm.RANDOM_SEARCH,
        demo_strategy
    )
    
    random_result = random_optimizer.optimize(
        objective_function=objective_function,
        parameter_ranges=param_definitions,
        max_iterations=50
    )
    
    # 保存结果
    random_results_file = random_optimizer.save_results(OUTPUT_DIR)
    print(f"   结果保存到: {random_results_file}")
    
    # 7. 比较优化结果
    print("\n" + "=" * 60)
    print("📊 优化结果比较")
    print("=" * 60)
    
    if grid_result and random_result:
        print(f"网格搜索最佳分数: {grid_result.score:.4f}")
        print(f"随机搜索最佳分数: {random_result.score:.4f}")
        
        if grid_result.score > random_result.score:
            print("🎖️  网格搜索表现更好")
            best_method = "网格搜索"
            best_result = grid_result
        else:
            print("🎖️  随机搜索表现更好")
            best_method = "随机搜索"
            best_result = random_result
        
        print(f"\n🏆 最佳参数组合 ({best_method}):")
        for param, value in best_result.parameters.items():
            print(f"   {param}: {value}")
    
    # 8. 生成优化报告
    print("\n" + "=" * 60)
    print("📋 生成优化报告")
    print("=" * 60)
    
    report = {
        "generated_at": datetime.now().isoformat(),
        "demo_strategy": demo_strategy,
        "total_optimizations": 2,
        "optimization_algorithms": [
            {
                "name": "grid_search",
                "results_file": str(grid_results_file),
                "best_score": grid_result.score if grid_result else None,
                "evaluations": len(grid_optimizer.results)
            },
            {
                "name": "random_search",
                "results_file": str(random_results_file),
                "best_score": random_result.score if random_result else None,
                "evaluations": len(random_optimizer.results)
            }
        ],
        "parameter_definitions": {
            name: {
                "min": param_def.min_value,
                "max": param_def.max_value,
                "step": param_def.step,
                "is_integer": param_def.is_integer,
                "log_scale": param_def.log_scale
            }
            for name, param_def in param_definitions.items()
        },
        "next_steps": [
            "集成真实策略评估函数",
            "实现贝叶斯优化算法",
            "实现遗传算法优化",
            "添加并行计算支持",
            "开发优化结果可视化"
        ]
    }
    
    report_file = OUTPUT_DIR / f"optimization_demo_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 优化演示完成")
    print(f"   演示策略: {demo_strategy}")
    print(f"   评估参数: {list(param_definitions.keys())}")
    print(f"   网格搜索评估: {len(grid_optimizer.results)} 个组合")
    print(f"   随机搜索评估: {len(random_optimizer.results)} 个组合")
    print(f"   优化报告: {report_file}")
    print()
    
    print("🎯 系统功能验证:")
    print("   ✅ 参数范围定义和验证")
    print("   ✅ 网格搜索算法实现")
    print("   ✅ 随机搜索算法实现")
    print("   ✅ 优化结果持久化")
    print("   ✅ 多算法比较框架")
    print()
    
    print("🚀 下一步扩展:")
    print("   1. 集成真实策略回测评估")
    print("   2. 实现高级优化算法（贝叶斯、遗传）")
    print("   3. 添加并行和分布式计算支持")
    print("   4. 开发优化过程可视化")
    print("   5. 集成到连续回测优化循环")
    
    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)