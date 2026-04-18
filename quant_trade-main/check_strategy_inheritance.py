#!/usr/bin/env python3
"""
检查所有策略是否继承 BaseStrategy
"""

import sys
import os
import importlib.util
import traceback

project_root = "/Users/chengming/.openclaw/workspace/quant_trade-main"
sys.path.insert(0, project_root)

from strategies.base_strategy import BaseStrategy

print("="*80)
print("检查策略继承关系")
print("="*80)

strategies_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/strategies"
failed_strategies = []
success_strategies = []

# 获取所有Python文件
py_files = [f for f in os.listdir(strategies_dir) 
           if f.endswith('.py') and f != '__init__.py' and f != 'base_strategy.py' and not f.endswith('.backup')]

print(f"找到 {len(py_files)} 个策略文件")

for filename in py_files:
    strategy_name = filename[:-3]
    filepath = os.path.join(strategies_dir, filename)
    
    print(f"\n检查: {filename}")
    
    try:
        # 动态导入模块
        spec = importlib.util.spec_from_file_location(strategy_name, filepath)
        if spec is None:
            print(f"  ❌ 无法创建spec")
            failed_strategies.append((filename, "无法创建spec"))
            continue
            
        module = importlib.util.module_from_spec(spec)
        
        # 执行模块
        try:
            spec.loader.exec_module(module)
        except ImportError as e:
            print(f"  ⚠️  导入依赖失败: {e}")
            # 检查是否有BaseStrategy子类定义
            # 即使导入失败，也可能有类定义
            pass
        except Exception as e:
            print(f"  ⚠️  模块执行错误: {e}")
            # 继续检查类定义
        
        # 查找 BaseStrategy 的子类
        found_classes = []
        for attr_name in dir(module):
            try:
                attr = getattr(module, attr_name)
                if isinstance(attr, type) and attr != BaseStrategy:
                    if issubclass(attr, BaseStrategy):
                        found_classes.append(attr_name)
            except (TypeError, AttributeError):
                continue
        
        if found_classes:
            print(f"  ✅ 找到 {len(found_classes)} 个BaseStrategy子类: {', '.join(found_classes)}")
            success_strategies.append((filename, found_classes))
        else:
            print(f"  ❌ 未找到BaseStrategy子类")
            # 检查文件内容是否有类定义
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'class ' in content and 'BaseStrategy' in content:
                    print(f"     ⚠️  文件包含'BaseStrategy'但未找到有效子类")
                    failed_strategies.append((filename, "有BaseStrategy引用但未找到子类"))
                else:
                    print(f"     ℹ️  文件未引用BaseStrategy")
                    failed_strategies.append((filename, "未引用BaseStrategy"))
                    
    except Exception as e:
        print(f"  ❌ 检查失败: {e}")
        traceback.print_exc()
        failed_strategies.append((filename, str(e)))

print("\n" + "="*80)
print("检查结果")
print("="*80)

print(f"✅ 成功检查的策略: {len(success_strategies)}")
for filename, classes in success_strategies[:10]:  # 只显示前10个
    print(f"  - {filename}: {', '.join(classes)}")
if len(success_strategies) > 10:
    print(f"    ... 还有 {len(success_strategies)-10} 个")

print(f"\n❌ 失败/未继承的策略: {len(failed_strategies)}")
for filename, error in failed_strategies[:10]:
    print(f"  - {filename}: {error}")
if len(failed_strategies) > 10:
    print(f"    ... 还有 {len(failed_strategies)-10} 个")

# 关键策略检查
print("\n" + "="*80)
print("关键策略检查")
print("="*80)

key_strategies = [
    'ma_strategy',
    'simple_ma_strategy', 
    'tradingview_strategy',
    'price_action_strategy',
    'transformer',
    'price_action_strategy_adapter'
]

for strategy in key_strategies:
    filepath = os.path.join(strategies_dir, f"{strategy}.py")
    if os.path.exists(filepath):
        print(f"✅ {strategy}.py 存在")
    else:
        print(f"❌ {strategy}.py 不存在")

if failed_strategies:
    print(f"\n⚠️  发现 {len(failed_strategies)} 个策略未继承BaseStrategy")
    print("需要修复这些策略以确保统一的回测接口")
    sys.exit(1)
else:
    print("\n🎉 所有策略都继承BaseStrategy！")