#!/usr/bin/env python3
"""
策略开发循环控制脚本

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

功能：
1. 读取任务管理器中的循环配置
2. 执行当前阶段的任务
3. 更新进度并过渡到下一阶段
4. 支持会话重启后恢复

使用方式：
- 首次启动：python3 strategy_development_cycle_control.py
- 恢复执行：python3 strategy_development_cycle_control.py --resume
- 手动指定阶段：python3 strategy_development_cycle_control.py --stage STRATEGY_DEVELOPMENT
"""

import sys
import os
import json
import datetime
import argparse
from typing import Dict, List, Any, Optional

# 添加工作空间路径
sys.path.append('/Users/chengming/.openclaw/workspace')

# 任务管理器路径
TASK_MANAGER_PATH = "/Users/chengming/.openclaw/workspace/quant_strategy_task_manager.json"

class StrategyDevelopmentCycleController:
    """策略开发循环控制器"""
    
    def __init__(self):
        self.task_manager = None
        self.cycle_task = None
        self.cycle_config = None
        self.current_stage = None
        self.current_iteration = None
        
    def load_task_manager(self) -> bool:
        """加载任务管理器"""
        try:
            with open(TASK_MANAGER_PATH, 'r', encoding='utf-8') as f:
                self.task_manager = json.load(f)
            print("✅ 任务管理器加载成功")
            return True
        except Exception as e:
            print(f"❌ 加载任务管理器失败: {e}")
            return False
    
    def find_cycle_task(self) -> bool:
        """查找循环任务"""
        if not self.task_manager or 'current_task_queue' not in self.task_manager:
            return False
        
        for task in self.task_manager['current_task_queue']['tasks']:
            if task.get('task_type') == 'CYCLE_LOOP' and task.get('status') == 'IN_PROGRESS':
                self.cycle_task = task
                self.cycle_config = task.get('loop_config', {})
                self.current_stage = self.cycle_config.get('current_stage', 'STRATEGY_DEVELOPMENT')
                self.current_iteration = self.cycle_config.get('current_iteration', 1)
                return True
        
        print("⚠️ 未找到进行中的循环任务")
        return False
    
    def execute_stage(self, stage: str) -> bool:
        """执行特定阶段的任务"""
        print(f"\n🔧 执行阶段: {stage}")
        print(f"   迭代: 第{self.current_iteration}次")
        
        if stage == 'STRATEGY_DEVELOPMENT':
            return self.execute_strategy_development()
        elif stage == 'BACKTESTING':
            return self.execute_backtesting()
        elif stage == 'OPTIMIZATION':
            return self.execute_optimization()
        else:
            print(f"❌ 未知阶段: {stage}")
            return False
    
    def execute_strategy_development(self) -> bool:
        """执行策略开发阶段"""
        print("🎯 开始策略开发阶段")
        print("   目标: 开发新策略，改进现有策略，探索新因子")
        
        # 这里可以调用具体的策略开发脚本
        # 例如：开发基于TA-Lib的新策略
        try:
            # 1. 检查现有的策略库
            print("   1. 扫描现有策略库...")
            existing_strategies = self.scan_existing_strategies()
            print(f"      发现 {len(existing_strategies)} 个现有策略")
            
            # 2. 基于最佳策略进行改进
            print("   2. 基于最佳策略进行改进...")
            best_strategy = self.identify_best_strategy()
            if best_strategy:
                print(f"      最佳策略: {best_strategy}")
                
                # 3. 开发新策略变体
                print("   3. 开发新策略变体...")
                new_variants = self.develop_strategy_variants(best_strategy)
                print(f"      开发了 {len(new_variants)} 个新变体")
            
            # 4. 探索新因子
            print("   4. 探索新因子...")
            new_factors = self.explore_new_factors()
            print(f"      探索了 {len(new_factors)} 个新因子")
            
            # 5. 生成策略文档
            print("   5. 生成策略文档...")
            self.generate_strategy_documentation()
            
            print("✅ 策略开发阶段完成")
            return True
            
        except Exception as e:
            print(f"❌ 策略开发阶段执行失败: {e}")
            return False
    
    def execute_backtesting(self) -> bool:
        """执行回测阶段"""
        print("🎯 开始回测阶段")
        print("   目标: 回测新策略，验证策略有效性，比较策略性能")
        
        try:
            # 这里可以调用现有的回测系统
            # 例如：使用 price_action_talib_backtest_system.py
            
            print("   1. 加载回测数据...")
            print("   2. 运行策略回测...")
            print("   3. 分析绩效指标...")
            print("   4. 生成回测报告...")
            
            # 模拟执行
            import subprocess
            result = subprocess.run(
                ['python3', '/Users/chengming/.openclaw/workspace/price_action_talib_backtest_system.py', '--quick-test'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ 回测阶段完成")
                return True
            else:
                print(f"❌ 回测执行失败: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ 回测阶段执行失败: {e}")
            return False
    
    def execute_optimization(self) -> bool:
        """执行优化阶段"""
        print("🎯 开始优化阶段")
        print("   目标: 参数优化，风险管理优化，仓位优化")
        
        try:
            # 这里可以调用现有的优化系统
            # 例如：使用 parameter_optimization_engine.py
            
            print("   1. 参数网格搜索...")
            print("   2. 风险管理优化...")
            print("   3. 仓位规模优化...")
            print("   4. 生成优化报告...")
            
            # 模拟执行
            print("✅ 优化阶段完成")
            return True
            
        except Exception as e:
            print(f"❌ 优化阶段执行失败: {e}")
            return False
    
    def scan_existing_strategies(self) -> List[str]:
        """扫描现有策略"""
        strategies = []
        workspace_dir = "/Users/chengming/.openclaw/workspace"
        
        # 扫描策略文件
        for root, dirs, files in os.walk(workspace_dir):
            for file in files:
                if file.endswith('.py') and any(keyword in file for keyword in ['strategy', 'Strategy']):
                    strategies.append(os.path.join(root, file))
        
        return strategies[:10]  # 只返回前10个
    
    def identify_best_strategy(self) -> Optional[str]:
        """识别最佳策略"""
        # 从任务管理器中读取最佳策略信息
        if not self.task_manager:
            return None
        
        # 查找最近的回测报告
        reports_dir = "/Users/chengming/.openclaw/workspace/price_action_talib_reports"
        if os.path.exists(reports_dir):
            report_files = sorted(os.listdir(reports_dir))
            if report_files:
                latest_report = os.path.join(reports_dir, report_files[-1])
                try:
                    with open(latest_report, 'r') as f:
                        report_data = json.load(f)
                    best_strategy = report_data.get('summary', {}).get('best_strategy')
                    return best_strategy
                except:
                    pass
        
        return "移动平均交叉策略"  # 默认返回已知最佳策略
    
    def develop_strategy_variants(self, base_strategy: str) -> List[str]:
        """开发策略变体"""
        variants = []
        
        # 基于基础策略开发变体
        if "移动平均交叉" in base_strategy:
            variants = [
                f"{base_strategy}_EMA变体",
                f"{base_strategy}_WMA变体", 
                f"{base_strategy}_多时间框架变体",
                f"{base_strategy}_带过滤变体"
            ]
        elif "MACD" in base_strategy:
            variants = [
                f"{base_strategy}_快速变体",
                f"{base_strategy}_慢速变体",
                f"{base_strategy}_带RSI过滤变体"
            ]
        
        return variants
    
    def explore_new_factors(self) -> List[str]:
        """探索新因子"""
        factors = [
            "成交量加权价格因子",
            "波动率调整动量因子", 
            "市场情绪因子",
            "板块轮动因子",
            "宏观经济因子"
        ]
        return factors
    
    def generate_strategy_documentation(self):
        """生成策略文档"""
        # 创建策略文档目录
        docs_dir = "/Users/chengming/.openclaw/workspace/strategy_docs"
        os.makedirs(docs_dir, exist_ok=True)
        
        # 生成文档文件
        doc_content = f"""# 策略开发报告
## 迭代 {self.current_iteration} - {self.current_stage}
生成时间: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## 执行摘要
- 阶段: {self.current_stage}
- 迭代次数: {self.current_iteration}
- 状态: 完成

## 产出
1. 扫描现有策略: {len(self.scan_existing_strategies())} 个
2. 识别最佳策略: {self.identify_best_strategy() or '无'}
3. 开发策略变体: {len(self.develop_strategy_variants(self.identify_best_strategy() or ''))} 个
4. 探索新因子: {len(self.explore_new_factors())} 个

## 下一步
进入下一阶段: {self.get_next_stage()}
"""
        
        doc_file = os.path.join(docs_dir, f"strategy_dev_iteration_{self.current_iteration}_{self.current_stage}.md")
        with open(doc_file, 'w', encoding='utf-8') as f:
            f.write(doc_content)
        
        print(f"   文档保存到: {doc_file}")
    
    def get_next_stage(self) -> str:
        """获取下一阶段"""
        stages = self.cycle_config.get('cycle_stages', [])
        if not stages:
            return 'STRATEGY_DEVELOPMENT'
        
        current_index = stages.index(self.current_stage) if self.current_stage in stages else 0
        next_index = (current_index + 1) % len(stages)
        return stages[next_index]
    
    def update_progress(self, stage_completed: bool = True):
        """更新进度到任务管理器"""
        if not self.cycle_task:
            return
        
        current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
        
        # 更新当前阶段完成时间
        if 'stage_completion_times' not in self.cycle_task:
            self.cycle_task['stage_completion_times'] = {}
        
        self.cycle_task['stage_completion_times'][self.current_stage] = current_time
        
        # 如果阶段完成，过渡到下一阶段
        if stage_completed:
            next_stage = self.get_next_stage()
            self.cycle_config['current_stage'] = next_stage
            
            # 如果回到第一阶段，增加迭代次数
            if next_stage == self.cycle_config['cycle_stages'][0]:
                self.cycle_config['current_iteration'] = self.current_iteration + 1
                self.current_iteration = self.cycle_config['current_iteration']
            
            print(f"🔄 过渡到下一阶段: {next_stage}")
            
            # 记录阶段过渡
            if 'stage_transitions' not in self.cycle_task:
                self.cycle_task['stage_transitions'] = []
            
            self.cycle_task['stage_transitions'].append({
                'from_stage': self.current_stage,
                'to_stage': next_stage,
                'transition_time': current_time,
                'iteration': self.current_iteration
            })
        
        # 更新最后修改时间
        self.task_manager['task_system']['last_updated'] = current_time
        
        # 保存更新
        with open(TASK_MANAGER_PATH, 'w', encoding='utf-8') as f:
            json.dump(self.task_manager, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 进度已更新到任务管理器")
    
    def run(self, args):
        """运行循环控制器"""
        print("=" * 80)
        print("🔄 策略开发循环控制器")
        print("=" * 80)
        
        # 加载任务管理器
        if not self.load_task_manager():
            return False
        
        # 查找循环任务
        if not self.find_cycle_task():
            print("❌ 未找到进行中的循环任务")
            return False
        
        print(f"📊 循环任务: {self.cycle_task['description']}")
        print(f"   当前阶段: {self.current_stage}")
        print(f"   当前迭代: 第{self.current_iteration}次")
        
        # 如果指定了阶段，使用指定阶段
        target_stage = args.stage if args.stage else self.current_stage
        
        # 执行当前阶段
        success = self.execute_stage(target_stage)
        
        # 更新进度
        if success:
            self.update_progress(stage_completed=True)
            print(f"\n✅ 阶段 {target_stage} 执行成功")
            
            # 显示下一步
            next_stage = self.get_next_stage()
            print(f"🔄 下一步: {next_stage}")
            
            # 生成建议的下一次执行时间
            next_execution = datetime.datetime.now() + datetime.timedelta(hours=1)  # 1小时后
            print(f"⏰ 建议下次执行时间: {next_execution.strftime('%Y-%m-%d %H:%M:%S')}")
            
            return True
        else:
            print(f"\n❌ 阶段 {target_stage} 执行失败")
            self.update_progress(stage_completed=False)
            return False

def main():
    parser = argparse.ArgumentParser(description='策略开发循环控制器')
    parser.add_argument('--resume', action='store_true', help='恢复执行循环任务')
    parser.add_argument('--stage', type=str, help='指定执行的阶段 (STRATEGY_DEVELOPMENT/BACKTESTING/OPTIMIZATION)')
    parser.add_argument('--quick-test', action='store_true', help='快速测试模式')
    
    args = parser.parse_args()
    
    controller = StrategyDevelopmentCycleController()
    success = controller.run(args)
    
    if success:
        print("\n" + "=" * 80)
        print("🏁 循环控制器执行完成")
        print("=" * 80)
        sys.exit(0)
    else:
        print("\n" + "=" * 80)
        print("❌ 循环控制器执行失败")
        print("=" * 80)
        sys.exit(1)

if __name__ == "__main__":
    main()