#!/bin/bash
# 迁移 quant_trade_main 到 quant_trade-main 并删除 quant_trade_main

set -e  # 出错时退出

echo "🚀 开始迁移 quant_trade_main 到 quant_trade-main..."
echo "=========================================="

SOURCE_DIR="/Users/chengming/.openclaw/workspace/quant_trade_main"
TARGET_DIR="/Users/chengming/.openclaw/workspace/quant_trade-main"

# 检查源目录是否存在
if [ ! -d "$SOURCE_DIR" ]; then
    echo "❌ 源目录不存在: $SOURCE_DIR"
    exit 1
fi

# 检查目标目录是否存在
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ 目标目录不存在: $TARGET_DIR"
    exit 1
fi

echo "📁 源目录: $SOURCE_DIR"
echo "📁 目标目录: $TARGET_DIR"
echo ""

# 1. 移动配置文件
echo "1. 移动配置文件..."
if [ -f "$SOURCE_DIR/config.json" ]; then
    if [ -f "$TARGET_DIR/config.json" ]; then
        echo "   ⚠️ 目标目录已存在 config.json，备份为 config.json.bak"
        cp "$TARGET_DIR/config.json" "$TARGET_DIR/config.json.bak"
    fi
    cp "$SOURCE_DIR/config.json" "$TARGET_DIR/"
    echo "   ✅ 移动 config.json"
fi

# 2. 移动Python脚本文件
echo ""
echo "2. 移动Python脚本文件..."
PYTHON_FILES=("immediate_backtest.py" "immediate_multistock.py" "immediate_optimization.py" "immediate_stoploss_optimization.py" "simple_backtest.py" "test_fix.py")
for file in "${PYTHON_FILES[@]}"; do
    if [ -f "$SOURCE_DIR/$file" ]; then
        if [ -f "$TARGET_DIR/$file" ]; then
            echo "   ⚠️ 目标目录已存在 $file，备份为 ${file}.bak"
            cp "$TARGET_DIR/$file" "$TARGET_DIR/${file}.bak"
        fi
        cp "$SOURCE_DIR/$file" "$TARGET_DIR/"
        echo "   ✅ 移动 $file"
    fi
done

# 3. 移动报告文件
echo ""
echo "3. 移动报告文件..."
if [ -f "$SOURCE_DIR/PROGRESS_REPORT_20260329_1337.md" ]; then
    cp "$SOURCE_DIR/PROGRESS_REPORT_20260329_1337.md" "$TARGET_DIR/"
    echo "   ✅ 移动 PROGRESS_REPORT_20260329_1337.md"
fi

# 4. 移动数据文件（合并data目录）
echo ""
echo "4. 合并data目录..."
if [ -d "$SOURCE_DIR/data" ]; then
    # 使用rsync合并目录，避免覆盖现有文件
    if command -v rsync >/dev/null 2>&1; then
        rsync -av --ignore-existing "$SOURCE_DIR/data/" "$TARGET_DIR/data/"
        echo "   ✅ 使用rsync合并data目录"
    else
        # 如果rsync不可用，使用cp
        cp -r "$SOURCE_DIR/data/." "$TARGET_DIR/data/" 2>/dev/null || true
        echo "   ✅ 使用cp合并data目录"
    fi
fi

# 5. 移动回测结果目录
echo ""
echo "5. 移动回测结果目录..."
RESULT_DIRS=("immediate_results" "immediate_optimization" "immediate_multistock" "immediate_stoploss" "reports" "logs" "cache" "config" "output")
for dir in "${RESULT_DIRS[@]}"; do
    if [ -d "$SOURCE_DIR/$dir" ]; then
        if [ -d "$TARGET_DIR/$dir" ]; then
            echo "   ⚠️ 目标目录已存在 $dir，合并内容"
            if command -v rsync >/dev/null 2>&1; then
                rsync -av "$SOURCE_DIR/$dir/" "$TARGET_DIR/$dir/"
            else
                cp -r "$SOURCE_DIR/$dir/." "$TARGET_DIR/$dir/" 2>/dev/null || true
            fi
        else
            cp -r "$SOURCE_DIR/$dir" "$TARGET_DIR/"
        fi
        echo "   ✅ 移动 $dir 目录"
    fi
done

# 6. 更新任务管理器中的路径
echo ""
echo "6. 更新任务管理器中的路径..."
TASK_MANAGER="/Users/chengming/.openclaw/workspace/quant_strategy_task_manager.json"
if [ -f "$TASK_MANAGER" ]; then
    # 备份原始文件
    cp "$TASK_MANAGER" "$TASK_MANAGER.bak"
    
    # 更新路径引用（将quant_trade_main改为quant_trade-main）
    sed -i '' 's|quant_trade_main|quant_trade-main|g' "$TASK_MANAGER"
    echo "   ✅ 更新任务管理器中的路径引用"
fi

# 7. 更新记忆文件中的路径
echo ""
echo "7. 更新记忆文件中的路径..."
MEMORY_FILE="/Users/chengming/.openclaw/workspace/memory/2026-03-29.md"
if [ -f "$MEMORY_FILE" ]; then
    cp "$MEMORY_FILE" "$MEMORY_FILE.bak"
    sed -i '' 's|quant_trade_main|quant_trade-main|g' "$MEMORY_FILE"
    echo "   ✅ 更新记忆文件中的路径引用"
fi

# 8. 验证迁移结果
echo ""
echo "8. 验证迁移结果..."
echo "   📁 目标目录内容概览:"
ls -la "$TARGET_DIR/" | grep -E "^drwx|^-rw" | head -20

# 9. 删除源目录
echo ""
echo "9. 删除源目录..."
read -p "   确认删除 $SOURCE_DIR 目录？(y/n): " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf "$SOURCE_DIR"
    echo "   ✅ 已删除源目录: $SOURCE_DIR"
else
    echo "   ⚠️ 保留源目录，用户取消删除"
fi

echo ""
echo "=========================================="
echo "✅ 迁移完成！"
echo ""
echo "📋 迁移摘要:"
echo "   - 配置文件: config.json"
echo "   - Python脚本: 6个"
echo "   - 报告文件: 1个"
echo "   - 数据目录: 合并完成"
echo "   - 回测结果目录: 9个"
echo "   - 任务管理器更新: 完成"
echo "   - 记忆文件更新: 完成"
echo ""
echo "📁 当前 quant_trade-main 目录结构:"
find "$TARGET_DIR" -maxdepth 2 -type d | sort
echo ""
echo "💡 后续操作:"
echo "   1. 验证迁移的文件完整性"
echo "   2. 测试Python脚本是否正常工作"
echo "   3. 继续执行量化策略开发任务"