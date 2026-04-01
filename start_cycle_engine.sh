#!/bin/bash
# 长期回测循环引擎启动脚本

echo "================================================================"
echo "🚀 长期回测循环引擎启动脚本"
echo "================================================================"
echo "启动时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "用户指令: '继续做回测吧' + '确认, 开始开发'"
echo "执行模式: 通宵回测 (22:37-06:37, 8小时)"
echo "目标: 运行长期回测循环系统，生成45+策略回测结果"
echo "================================================================"

# 设置工作目录
cd /Users/chengming/.openclaw/workspace

# 检查Python环境
echo "🔧 检查Python环境..."
python3 --version

# 检查必要文件
echo "📁 检查必要文件..."
if [ -f "long_term_backtest_cycle_engine.py" ]; then
    echo "✅ long_term_backtest_cycle_engine.py 存在"
else
    echo "❌ long_term_backtest_cycle_engine.py 不存在"
    exit 1
fi

# 创建结果目录
echo "📂 创建结果目录..."
mkdir -p long_term_cycle_results
mkdir -p long_term_cycle_results/backtest_results
mkdir -p long_term_cycle_results/optimization_results
mkdir -p long_term_cycle_results/knowledge_base

# 显示当前状态
echo "📊 显示当前状态..."
if [ -f "cycle_state.json" ]; then
    echo "📄 发现已保存状态文件，将恢复执行"
    echo "   状态文件: cycle_state.json"
    echo "   创建时间: $(stat -f "%Sm" cycle_state.json 2>/dev/null || echo "未知")"
else
    echo "🆕 无保存状态，开始新循环"
fi

# 启动引擎
echo "🚀 启动长期回测循环引擎..."
echo "================================================================"

# 运行Python引擎
python3 long_term_backtest_cycle_engine.py

# 检查执行结果
if [ $? -eq 0 ]; then
    echo "✅ 长期回测循环引擎执行完成"
    echo "   结果目录: long_term_cycle_results/"
    echo "   状态文件: cycle_state.json"
    echo "   报告文件: long_term_cycle_results/final_cycle_engine_report.json"
else
    echo "❌ 长期回测循环引擎执行失败"
    echo "   错误码: $?"
fi

echo "================================================================"
echo "📅 完成时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo "================================================================"