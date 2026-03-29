#!/bin/bash
# 量化交易策略开发任务恢复脚本
# 新会话启动时自动恢复量化策略开发任务

echo "🔍 恢复量化交易策略开发任务..."
echo "=========================================="

# 检查任务管理器文件是否存在
TASK_MANAGER="/Users/chengming/.openclaw/workspace/quant_strategy_task_manager.json"

if [ ! -f "$TASK_MANAGER" ]; then
    echo "❌ 任务管理器文件不存在: $TASK_MANAGER"
    echo "   请先创建任务管理器文件"
    exit 1
fi

echo "✅ 找到任务管理器文件"

# 读取项目信息
PROJECT_NAME=$(grep -A 2 '"name"' "$TASK_MANAGER" | grep '"量化交易策略' | cut -d'"' -f4)
CREATED_AT=$(grep '"created_at"' "$TASK_MANAGER" | head -1 | cut -d'"' -f4)
LAST_UPDATED=$(grep '"last_updated"' "$TASK_MANAGER" | head -1 | cut -d'"' -f4)

echo "📋 项目: $PROJECT_NAME"
echo "📅 创建时间: $CREATED_AT"
echo "🔄 最后更新: $LAST_UPDATED"

# 检查当前任务队列
echo ""
echo "📊 当前任务状态:"
echo "----------------"

# 提取当前任务
CURRENT_TASK_ID=$(grep -A 2 '"current_task_id"' "$TASK_MANAGER" | grep '"task_001"' | cut -d'"' -f4 2>/dev/null || echo "task_001")

if [ -n "$CURRENT_TASK_ID" ]; then
    echo "🎯 当前任务ID: $CURRENT_TASK_ID"
    
    # 提取任务详情
    TASK_DESC=$(grep -A 10 "\"$CURRENT_TASK_ID\"" "$TASK_MANAGER" | grep '"description"' | head -1 | cut -d'"' -f4)
    TASK_PRIORITY=$(grep -A 10 "\"$CURRENT_TASK_ID\"" "$TASK_MANAGER" | grep '"priority"' | head -1 | cut -d'"' -f4)
    TASK_STATUS=$(grep -A 10 "\"$CURRENT_TASK_ID\"" "$TASK_MANAGER" | grep '"status"' | head -1 | cut -d'"' -f4)
    
    echo "📝 任务描述: $TASK_DESC"
    echo "⚡ 优先级: $TASK_PRIORITY"
    echo "📈 状态: $TASK_STATUS"
else
    echo "⚠️ 无法确定当前任务"
fi

# 检查已完成工作
echo ""
echo "✅ 已完成工作摘要:"
echo "------------------"

COMPLETED_COUNT=$(grep -c '"status": "COMPLETED"' "$TASK_MANAGER")
echo "   已完成任务: $COMPLETED_COUNT 个"

# 检查发现的策略
STRATEGY_COUNT=$(grep '"total_strategies_found"' "$TASK_MANAGER" | head -1 | cut -d':' -f2 | tr -d ', ')
echo "   发现策略: $STRATEGY_COUNT 个"

# 检查回测结果
BACKTEST_COUNT=$(grep '"total_backtests_completed"' "$TASK_MANAGER" | head -1 | cut -d':' -f2 | tr -d ', ')
echo "   完成回测: $BACKTEST_COUNT 个"

# 生成恢复指令
echo ""
echo "🚀 恢复执行指令:"
echo "----------------"

if [ "$CURRENT_TASK_ID" = "task_001" ]; then
    echo "📋 立即执行: 深度分析价格行为策略"
    echo ""
    echo "执行步骤:"
    echo "1. 检查 price_action_integration/ 目录下的策略文件"
    echo "2. 解析策略逻辑和接口"
    echo "3. 创建适配器使其兼容回测框架"
    echo "4. 运行初步回测试验"
    echo ""
    echo "📁 相关文件:"
    echo "   - /Users/chengming/.openclaw/workspace/price_action_integration/"
    echo "   - /Users/chengming/.openclaw/workspace/quant_strategy_task_manager.json"
elif [ "$CURRENT_TASK_ID" = "task_002" ]; then
    echo "📋 立即执行: 解析IPython Notebook复杂策略"
    echo ""
    echo "执行步骤:"
    echo "1. 创建Notebook解析工具"
    echo "2. 批量解析所有ipynb文件"
    echo "3. 提取策略逻辑和参数"
    echo "4. 分类和归档策略"
    echo ""
    echo "📁 相关文件:"
    echo "   - /Users/chengming/.openclaw/workspace/quant_trade-main/csv_version/*.ipynb"
fi

# 检查依赖问题
echo ""
echo "⚠️ 已知问题:"
echo "-----------"

if grep -q "DEPENDENCY_ISSUE" "$TASK_MANAGER"; then
    echo "   • GRPO/Transformer策略需要torch库"
    echo "     修复命令: pip install torch"
fi

if grep -q "IMPORT_ISSUE" "$TASK_MANAGER"; then
    echo "   • 价格行为策略导入问题"
    echo "     需要确认正确的类名和导入方式"
fi

# 生成Python恢复代码
echo ""
echo "🐍 Python恢复代码模板:"
echo "---------------------"
cat << 'PYTHON_TEMPLATE'
import json
import os

# 加载任务管理器
task_manager_path = "/Users/chengming/.openclaw/workspace/quant_strategy_task_manager.json"
with open(task_manager_path, 'r', encoding='utf-8') as f:
    task_manager = json.load(f)

print(f"恢复量化交易策略开发任务: {task_manager['task_system']['name']}")
print(f"当前阶段: {task_manager['current_task_queue']['current_phase']}")
print(f"当前任务: {task_manager['current_task_queue']['tasks'][0]['description']}")

# 根据当前任务执行相应操作
current_task_id = task_manager['execution_engine']['current_task_id']
if current_task_id == 'task_001':
    print("执行任务: 深度分析价格行为策略")
    # 添加价格行为策略分析代码
elif current_task_id == 'task_002':
    print("执行任务: 解析IPython Notebook复杂策略")
    # 添加Notebook解析代码

# 更新最后更新时间
task_manager['task_system']['last_updated'] = "当前时间ISO格式"
with open(task_manager_path, 'w', encoding='utf-8') as f:
    json.dump(task_manager, f, ensure_ascii=False, indent=2)
PYTHON_TEMPLATE

echo ""
echo "=========================================="
echo "✅ 任务恢复准备完成"
echo "💡 提示: 新会话应首先读取任务管理器文件，然后继续执行当前任务"
echo ""
echo "📋 快速开始:"
echo "   1. 查看任务管理器: cat $TASK_MANAGER | jq ."
echo "   2. 查看详细记录: cat /Users/chengming/.openclaw/workspace/memory/2026-03-29.md"
echo "   3. 立即继续: 执行任务队列中的下一个任务"