#!/usr/bin/env python3
"""
强制恢复系统 - task_011 自动恢复机制

功能:
1. 新会话启动时自动检查是否有待恢复任务
2. 强制读取恢复指令并执行
3. 记录恢复状态和结果
4. 确保任务连续性

使用方式:
新会话启动时运行: python3 auto_resume_task_011.py
"""

import os
import json
import sys
from pathlib import Path
from datetime import datetime

print("=" * 80)
print("🔧 强制恢复系统 - task_011 自动恢复机制")
print("=" * 80)

# 路径配置
WORKSPACE_ROOT = Path("/Users/chengming/.openclaw/workspace")
RESUME_INSTRUCTIONS = WORKSPACE_ROOT / "SESSION_RESUME_INSTRUCTIONS.md"
TASK_MANAGER = WORKSPACE_ROOT / "quant_strategy_task_manager.json"
RESUME_CHECKPOINT = WORKSPACE_ROOT / "RESUME_CHECKPOINT.json"

def create_resume_checkpoint():
    """创建恢复检查点"""
    checkpoint = {
        "created_at": datetime.now().isoformat(),
        "task_id": "task_011",
        "current_phase": "phase_3",
        "status": "needs_resume",
        "last_progress": "Phase 2完成，Phase 3开始",
        "resume_instructions_file": str(RESUME_INSTRUCTIONS),
        "required_actions": [
            "读取SESSION_RESUME_INSTRUCTIONS.md",
            "检查网络状态(TradingView访问)",
            "创建continuous_backtest_optimization_cycle.py",
            "开始策略回测循环",
            "每2小时汇报进度"
        ],
        "user_instructions": [
            "学习100个TradingView脚本",
            "在quant_trade-main做策略整合和回测",
            "反复组合不同策略做遍历回测",
            "一直做下去"
        ]
    }
    
    with open(RESUME_CHECKPOINT, 'w', encoding='utf-8') as f:
        json.dump(checkpoint, f, indent=2, ensure_ascii=False)
    
    print(f"✅ 创建恢复检查点: {RESUME_CHECKPOINT}")
    return checkpoint

def read_resume_instructions():
    """读取恢复指令"""
    if not RESUME_INSTRUCTIONS.exists():
        print(f"❌ 恢复指令文件不存在: {RESUME_INSTRUCTIONS}")
        return None
    
    try:
        with open(RESUME_INSTRUCTIONS, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📋 读取恢复指令: {RESUME_INSTRUCTIONS}")
        print("-" * 40)
        print(content[:500] + "..." if len(content) > 500 else content)
        print("-" * 40)
        
        return content
    except Exception as e:
        print(f"❌ 读取恢复指令失败: {e}")
        return None

def check_task_status():
    """检查任务状态"""
    if not TASK_MANAGER.exists():
        print(f"❌ 任务管理器不存在: {TASK_MANAGER}")
        return None
    
    try:
        with open(TASK_MANAGER, 'r', encoding='utf-8') as f:
            task_data = json.load(f)
        
        # 查找task_011
        tasks = task_data.get("current_task_queue", {}).get("tasks", [])
        task_011 = None
        for task in tasks:
            if task.get("task_id") == "task_011":
                task_011 = task
                break
        
        if task_011:
            print(f"✅ 找到任务task_011:")
            print(f"   描述: {task_011.get('description', 'N/A')}")
            print(f"   状态: {task_011.get('status', 'N/A')}")
            print(f"   当前阶段: {task_011.get('current_phase', 'N/A')}")
            return task_011
        else:
            print("❌ 未找到task_011")
            return None
            
    except Exception as e:
        print(f"❌ 读取任务管理器失败: {e}")
        return None

def generate_resume_script():
    """生成自动恢复脚本"""
    resume_script = WORKSPACE_ROOT / "resume_task_011.sh"
    
    script_content = """#!/bin/bash
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
            print(f'任务状态: {task.get(\"status\", \"N/A\")}')
            print(f'当前阶段: {task.get(\"current_phase\", \"N/A\")}')
            print(f'创建时间: {task.get(\"created_at\", \"N/A\")}')
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
"""
    
    with open(resume_script, 'w', encoding='utf-8') as f:
        f.write(script_content)
    
    # 设置执行权限
    os.chmod(resume_script, 0o755)
    
    print(f"✅ 生成自动恢复脚本: {resume_script}")
    return resume_script

def main():
    """主函数"""
    print(f"工作空间: {WORKSPACE_ROOT}")
    print(f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 1. 检查恢复检查点
    if RESUME_CHECKPOINT.exists():
        print(f"📌 发现恢复检查点: {RESUME_CHECKPOINT}")
        try:
            with open(RESUME_CHECKPOINT, 'r', encoding='utf-8') as f:
                checkpoint = json.load(f)
            print(f"   任务ID: {checkpoint.get('task_id')}")
            print(f"   状态: {checkpoint.get('status')}")
            print(f"   创建时间: {checkpoint.get('created_at')}")
        except Exception as e:
            print(f"❌ 读取检查点失败: {e}")
    else:
        print("📌 无恢复检查点，创建新检查点")
        create_resume_checkpoint()
    
    # 2. 读取恢复指令
    print("\n📖 读取恢复指令...")
    instructions = read_resume_instructions()
    
    # 3. 检查任务状态
    print("\n🔍 检查任务状态...")
    task_status = check_task_status()
    
    # 4. 生成自动恢复脚本
    print("\n🛠️ 生成自动恢复工具...")
    resume_script = generate_resume_script()
    
    # 5. 显示恢复行动计划
    print("\n🎯 恢复行动计划:")
    print("=" * 40)
    
    if task_status:
        if task_status.get("status") == "IN_PROGRESS":
            print("⚡ 任务正在进行中，需要继续执行")
            current_phase = task_status.get("current_phase", "unknown")
            print(f"   当前阶段: {current_phase}")
            
            if current_phase == "phase_3":
                print("   立即行动: 创建连续回测优化循环系统")
                print("   目标文件: continuous_backtest_optimization_cycle.py")
            elif current_phase == "phase_1":
                print("   立即行动: 学习TradingView脚本")
                print("   目标: 分析100个脚本设计思想")
        else:
            print("📊 任务状态异常，需要检查")
    else:
        print("❓ 任务状态未知，按照恢复指令执行")
    
    print("\n📋 关键文件:")
    print(f"   恢复指令: {RESUME_INSTRUCTIONS}")
    print(f"   任务管理器: {TASK_MANAGER}")
    print(f"   恢复检查点: {RESUME_CHECKPOINT}")
    print(f"   自动恢复脚本: {resume_script}")
    
    print("\n🚀 执行命令:")
    print(f"   # 运行自动恢复脚本")
    print(f"   ./resume_task_011.sh")
    print()
    print(f"   # 或直接读取恢复指令")
    print(f"   cat {RESUME_INSTRUCTIONS}")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)