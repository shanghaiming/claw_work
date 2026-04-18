#!/usr/bin/env python3
"""
批量修复策略导入脚本
将 'from base_strategy import BaseStrategy' 改为 'from strategies.base_strategy import BaseStrategy'
"""

import os
import re
import sys

project_root = "/Users/chengming/.openclaw/workspace/quant_trade-main"
strategies_dir = os.path.join(project_root, "strategies")

print("="*80)
print("批量修复策略导入")
print("="*80)

# 模式1: from base_strategy import BaseStrategy
pattern1 = re.compile(r'^from\s+base_strategy\s+import\s+BaseStrategy', re.MULTILINE)
# 模式2: import base_strategy 或 from .base_strategy import BaseStrategy
pattern2 = re.compile(r'^from\s+\.base_strategy\s+import\s+BaseStrategy', re.MULTILINE)

fixed_files = []
error_files = []

# 遍历所有Python文件
for filename in os.listdir(strategies_dir):
    if filename.endswith('.py') and filename not in ['__init__.py', 'base_strategy.py', 'simple_test.py']:
        filepath = os.path.join(strategies_dir, filename)
        
        print(f"\n检查: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            original_content = content
            
            # 修复模式1
            if pattern1.search(content):
                content = pattern1.sub('from strategies.base_strategy import BaseStrategy', content)
                print(f"  ✅ 修复 'from base_strategy import BaseStrategy'")
            
            # 修复模式2  
            if pattern2.search(content):
                content = pattern2.sub('from strategies.base_strategy import BaseStrategy', content)
                print(f"  ✅ 修复 'from .base_strategy import BaseStrategy'")
            
            # 如果内容有变化，保存文件
            if content != original_content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                fixed_files.append(filename)
                print(f"  💾 文件已更新")
            else:
                # 检查是否有 base_strategy 引用但未使用正确导入
                if 'BaseStrategy' in content and 'strategies.base_strategy' not in content:
                    print(f"  ⚠️  文件包含 'BaseStrategy' 但可能使用不正确的导入")
                else:
                    print(f"  ✓ 无需修复")
        
        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            error_files.append((filename, str(e)))

print("\n" + "="*80)
print("修复完成")
print("="*80)

if fixed_files:
    print(f"✅ 修复了 {len(fixed_files)} 个文件:")
    for f in fixed_files:
        print(f"  - {f}")
else:
    print("✅ 没有文件需要修复")

if error_files:
    print(f"\n❌ 处理失败 {len(error_files)} 个文件:")
    for f, e in error_files:
        print(f"  - {f}: {e}")

# 验证修复
print("\n" + "="*80)
print("验证修复")
print("="*80)

# 测试导入关键文件
test_files = ['ma_strategy.py', 'simple_ma_strategy.py', 'tradingview_strategy.py', 
              'price_action_strategy.py', 'transformer.py', 'price_action_strategy_adapter.py']

sys.path.insert(0, project_root)

for test_file in test_files:
    filepath = os.path.join(strategies_dir, test_file)
    if os.path.exists(filepath):
        print(f"\n验证 {test_file}...")
        try:
            # 动态导入测试
            module_name = test_file[:-3]
            spec = __import__(f'strategies.{module_name}', fromlist=['*'])
            print(f"  ✅ 导入成功")
            
            # 检查是否有 BaseStrategy 子类
            from strategies.base_strategy import BaseStrategy
            found_classes = []
            for attr_name in dir(spec):
                try:
                    attr = getattr(spec, attr_name)
                    if isinstance(attr, type) and attr != BaseStrategy:
                        if issubclass(attr, BaseStrategy):
                            found_classes.append(attr_name)
                except:
                    pass
            
            if found_classes:
                print(f"  ✅ 找到 {len(found_classes)} 个BaseStrategy子类: {', '.join(found_classes)}")
            else:
                print(f"  ⚠️  未找到BaseStrategy子类")
                
        except ImportError as e:
            print(f"  ❌ 导入失败: {e}")
        except Exception as e:
            print(f"  ⚠️  其他错误: {e}")

print("\n" + "="*80)
print("批量修复完成")
print("="*80)