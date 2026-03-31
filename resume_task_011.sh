#!/bin/bash
# 自动恢复脚本 - task_011

echo "🔧 开始恢复task_011任务..."
cd "$(dirname "$0")"

# 检查必要文件
if [ ! -f "SESSION_RESUME_INSTRUCTIONS.md" ]; then
    echo "❌ 错误: 恢复指令文件不存在"
    exit 1
fi

if [ ! -f "quant_strategy_task_manager.json" ]; then
    echo "❌ 错误: 任务管理器文件不存在"
    exit 1
fi

# 显示恢复指令概要
echo "📋 恢复指令概要:"
head -20 "SESSION_RESUME_INSTRUCTIONS.md"
echo ""

# 检查任务状态
echo "🔍 检查任务状态..."
python3 -c "
import json
import sys
try:
    with open('quant_strategy_task_manager.json', 'r') as f:
        data = json.load(f)
    
    tasks = data.get('current_task_queue', {}).get('tasks', [])
    for task in tasks:
        if task.get('task_id') == 'task_011':
            print(f'任务状态: {task.get("status", "N/A")}')
            print(f'当前阶段: {task.get("current_phase", "N/A")}')
            print(f'创建时间: {task.get("created_at", "N/A")}')
            break
    else:
        print('未找到task_011')
except Exception as e:
    print(f'检查失败: {e}')
"

# 网络测试
echo "🌐 测试网络连接..."
curl -s --head https://www.baidu.com >/dev/null 2>&1
if [ $? -eq 0 ]; then
    echo "✅ 基础网络连接正常"
else
    echo "❌ 基础网络连接失败"
fi

echo ""
echo "🎯 需要执行的操作:"
echo "1. 阅读完整恢复指令: cat SESSION_RESUME_INSTRUCTIONS.md"
echo "2. 创建连续回测优化循环系统"
echo "3. 开始策略回测循环"
echo "4. 每2小时汇报进度"

exit 0
