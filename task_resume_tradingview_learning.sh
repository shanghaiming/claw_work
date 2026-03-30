#!/bin/bash
# TradingView学习项目恢复脚本
# 当会话重启时，运行此脚本恢复学习进度

echo "=== TradingView学习项目恢复 ==="
echo "恢复时间: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo ""

# 检查必要文件
REQUIRED_FILES=(
    "tradingview_learning_task_manager.json"
    "tradingview_learning_notes.md"
    "tradingview_learning_state.json"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ 找到文件: $file"
    else
        echo "⚠️  缺少文件: $file"
    fi
done

echo ""
echo "=== 当前项目状态 ==="

# 读取任务管理器状态
if [ -f "tradingview_learning_task_manager.json" ]; then
    CURRENT_PHASE=$(grep -o '"phase": "[^"]*"' tradingview_learning_task_manager.json | head -1 | cut -d'"' -f4)
    CURRENT_TASK=$(grep -o '"current_task": "[^"]*"' tradingview_learning_task_manager.json | head -1 | cut -d'"' -f4)
    OVERALL_PROGRESS=$(grep -o '"overall_progress": [0-9]*' tradingview_learning_task_manager.json | head -1 | cut -d':' -f2 | tr -d ' ')
    
    echo "当前阶段: $CURRENT_PHASE"
    echo "当前任务: $CURRENT_TASK"
    echo "总体进度: ${OVERALL_PROGRESS}%"
    
    # 显示任务状态
    echo ""
    echo "=== 任务状态 ==="
    
    # 提取已完成任务
    COMPLETED_TASKS=$(grep -o '"completed_tasks": \[[^]]*\]' tradingview_learning_task_manager.json | head -1)
    echo "已完成任务: $COMPLETED_TASKS"
    
    # 提取进行中任务
    ACTIVE_TASKS=$(grep -o '"active_tasks": \[[^]]*\]' tradingview_learning_task_manager.json | head -1)
    echo "进行中任务: $ACTIVE_TASKS"
else
    echo "❌ 任务管理器文件不存在"
fi

echo ""
echo "=== 恢复选项 ==="
echo "1. 继续当前任务"
echo "2. 查看详细状态"
echo "3. 手动调整配置"
echo ""

# Python恢复代码模板
cat > resume_tradingview_learning.py << 'EOF'
#!/usr/bin/env python3
"""
TradingView学习项目Python恢复代码
"""

import json
import os
from datetime import datetime

def load_project_state():
    """加载项目状态"""
    try:
        with open('tradingview_learning_task_manager.json', 'r', encoding='utf-8') as f:
            task_manager = json.load(f)
        
        with open('tradingview_learning_state.json', 'r', encoding='utf-8') as f:
            learning_state = json.load(f)
        
        return task_manager, learning_state
    except FileNotFoundError as e:
        print(f"文件未找到: {e}")
        return None, None

def display_status(task_manager, learning_state):
    """显示当前状态"""
    if task_manager and learning_state:
        print("=== TradingView学习项目状态 ===")
        print(f"项目: {task_manager['project_overview']['project_name']}")
        print(f"用户指令: {task_manager['project_overview']['user_instruction']}")
        print(f"开始时间: {task_manager['project_overview']['start_time']}")
        print(f"目标完成: {task_manager['project_overview']['end_time_goal']}")
        print()
        
        status = task_manager['current_status']
        print(f"当前阶段: {status['phase']}")
        print(f"阶段进度: {status['phase_progress']}%")
        print(f"总体进度: {status['overall_progress']}%")
        print(f"当前任务: {status['current_task']}")
        print(f"最后更新: {status['last_update']}")
        print()
        
        # 显示已完成任务
        if 'completed_tasks' in status and status['completed_tasks']:
            print("已完成任务:")
            for task in status['completed_tasks']:
                print(f"  - {task}")
        
        # 显示进行中任务
        if 'active_tasks' in status and status['active_tasks']:
            print("进行中任务:")
            for task in status['active_tasks']:
                print(f"  - {task}")
        
        print()
        print("=== 学习状态 ===")
        print(f"已用时间: {learning_state.get('elapsed_hours', 'N/A')}小时")
        print(f"剩余时间: {learning_state.get('remaining_hours', 'N/A')}小时")
        
        # 显示下一个里程碑
        if 'next_milestones' in learning_state:
            print("下一个里程碑:")
            for milestone in learning_state['next_milestones']:
                print(f"  - {milestone}")
    else:
        print("无法加载项目状态")

def resume_learning():
    """恢复学习流程"""
    task_manager, learning_state = load_project_state()
    
    if not task_manager or not learning_state:
        print("无法恢复学习，状态文件缺失")
        return
    
    display_status(task_manager, learning_state)
    
    current_phase = task_manager['current_status']['phase']
    current_task = task_manager['current_status']['current_task']
    
    print()
    print(f"=== 恢复执行 ===")
    print(f"将恢复阶段: {current_phase}")
    print(f"将恢复任务: {current_task}")
    print()
    print("恢复选项:")
    print("1. 继续深度学习指标 (task_004)")
    print("2. 继续深度学习策略 (task_005)")
    print("3. 开始Python实现 (task_006)")
    print("4. 自定义恢复路径")
    
    # 这里可以根据当前任务自动继续
    if current_task == "task_004_deep_learn_top_indicators":
        print()
        print("建议: 继续深度学习20个顶级指标")
        print("执行: from tradingview_indicators_deep_learning import continue_indicators_learning")
        print("      continue_indicators_learning()")
    elif current_task == "task_005_deep_learn_top_strategies":
        print()
        print("建议: 继续深度学习32个交易策略")
        print("执行: from tradingview_strategies_deep_learning import continue_strategies_learning")
        print("      continue_strategies_learning()")
    else:
        print()
        print("请根据当前任务选择恢复路径")

if __name__ == "__main__":
    resume_learning()
EOF

echo "Python恢复代码已保存到: resume_tradingview_learning.py"
echo ""
echo "运行以下命令继续学习:"
echo "python3 resume_tradingview_learning.py"
echo ""
echo "或直接查看状态文件:"
echo "cat tradingview_learning_notes.md | tail -20"

# 设置执行权限
chmod +x resume_tradingview_learning.py 2>/dev/null || true

echo ""
echo "=== 恢复完成 ==="
echo "项目已准备就绪，可以继续学习。"