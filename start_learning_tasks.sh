#!/bin/bash
# 启动学习任务执行脚本
# 自动执行价格行为区间篇学习任务链表

set -e

WORKSPACE="/Users/chengming/.openclaw/workspace"
cd "$WORKSPACE"

echo "========================================"
echo "🚀 启动价格行为学习任务执行系统"
echo "========================================"
echo "工作目录: $WORKSPACE"
echo "当前时间: $(date '+%Y-%m-%d %H:%M:%S %z')"
echo ""

# 检查必要文件
echo "📁 检查必要文件..."
if [ ! -f "task_manager.json" ]; then
    echo "❌ 错误: task_manager.json 不存在"
    exit 1
fi

if [ ! -f "task_executor.py" ]; then
    echo "❌ 错误: task_executor.py 不存在"
    exit 1
fi

if [ ! -f "price_action_ranges_notes.md" ]; then
    echo "⚠️  警告: price_action_ranges_notes.md 不存在，将创建新文件"
    touch "price_action_ranges_notes.md"
fi

if [ ! -d "memory" ]; then
    echo "⚠️  警告: memory/ 目录不存在，将创建"
    mkdir -p "memory"
fi

echo "✅ 所有必要文件检查通过"
echo ""

# 更新任务管理器时间戳
echo "🔄 更新任务管理器状态..."
python3 -c "
import json
import datetime

try:
    with open('task_manager.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    current_time = datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S+08:00')
    data['task_system']['last_updated'] = current_time
    
    # 更新执行引擎状态
    data['execution_engine']['engine_status'] = 'RUNNING'
    data['execution_engine']['next_scheduled_execution'] = 'immediate'
    
    with open('task_manager.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print('✅ 任务管理器状态已更新')
except Exception as e:
    print(f'❌ 更新失败: {e}')
    exit(1)
"

echo ""
echo "🎯 当前学习任务状态:"

# 显示当前任务状态
python3 -c "
import json

try:
    with open('task_manager.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    current_index = data['task_queue']['current_task_index']
    tasks = data['task_queue']['tasks']
    
    if 0 <= current_index < len(tasks):
        task = tasks[current_index]
        print(f'📖 当前章节: 第{task[\"chapter_number\"]}章')
        print(f'🎯 章节标题: {task[\"chapter_title\"]}')
        print(f'🔄 任务状态: {task[\"status\"]}')
        print(f'⏰ 开始时间: {task.get(\"start_time\", \"未开始\")}')
        
        if task['status'] == 'IN_PROGRESS':
            print(f'📝 当前步骤: {task.get(\"current_step\", \"analyze_chapter\")}')
            print(f'⏳ 预计完成: {task.get(\"estimated_completion_time\", \"未设置\")}')
    else:
        print('❌ 当前任务索引无效')
    
    # 显示进度
    completed = len([t for t in tasks if t['status'] == 'COMPLETED'])
    total = len(tasks)
    percentage = (completed / total * 100) if total > 0 else 0
    
    print(f'📊 总体进度: {completed}/{total} 章节 ({percentage:.1f}%)')
    
except Exception as e:
    print(f'❌ 读取状态失败: {e}')
"

echo ""
echo "========================================"
echo "🤖 开始执行学习任务..."
echo "========================================"
echo ""

# 执行任务
echo "执行任务引擎 (最大任务数: 1)..."
python3 task_executor.py --max-tasks 1

echo ""
echo "========================================"
echo "📋 任务执行完成"
echo "========================================"
echo ""

# 显示最终状态
echo "最终状态报告:"
python3 task_executor.py --report

echo ""
echo "🔍 详细状态信息:"
echo "学习笔记文件: price_action_ranges_notes.md"
echo "任务管理器: task_manager.json"
echo "任务执行器: task_executor.py"
echo "状态文件: learning_state.json"
echo ""

# 检查文件大小
echo "📊 文件大小统计:"
if [ -f "price_action_ranges_notes.md" ]; then
    NOTES_SIZE=$(wc -c "price_action_ranges_notes.md" | awk '{print int($1/1024)}')
    echo "学习笔记: ${NOTES_SIZE}KB"
fi

if [ -f "task_manager.json" ]; then
    TM_SIZE=$(wc -c "task_manager.json" | awk '{print int($1/1024)}')
    echo "任务管理器: ${TM_SIZE}KB"
fi

if [ -f "learning_state.json" ]; then
    LS_SIZE=$(wc -c "learning_state.json" | awk '{print int($1/1024)}')
    echo "学习状态: ${LS_SIZE}KB"
fi

echo ""
echo "✅ 学习任务执行系统启动完成"
echo "⏰ 下次检查: 5分钟后 (通过cron任务)"
echo "📅 下次汇报: 明天早上 07:00"
echo ""

exit 0