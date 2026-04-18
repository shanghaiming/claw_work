#!/usr/bin/env python3
import sys
import traceback

project_root = "/Users/chengming/.openclaw/workspace/quant_trade-main"
sys.path.insert(0, project_root)

print("测试 base_strategy 导入...")
try:
    import strategies.base_strategy
    print("✅ base_strategy 导入成功")
except Exception as e:
    print(f"❌ 导入失败: {e}")
    traceback.print_exc()