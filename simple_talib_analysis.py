#!/usr/bin/env python3
"""
简单分析TA-Lib函数和现有指标
"""

import json
import os

# 加载TA-Lib报告
with open('talib_comprehensive_report.json', 'r', encoding='utf-8') as f:
    talib_data = json.load(f)

print("=" * 80)
print("📊 TA-Lib函数分析")
print("=" * 80)

# 获取所有函数
all_talib_functions = []
for category, info in talib_data['category_details'].items():
    functions = info.get('functions', [])
    all_talib_functions.extend(functions)

print(f"TA-Lib总函数数: {talib_data['total_functions']}")
print(f"实际函数列表数: {len(all_talib_functions)}")

# 查看类别分布
print(f"\n📈 类别分布:")
for category, info in talib_data['category_details'].items():
    functions = info.get('functions', [])
    print(f"  {category}: {len(functions)} 个函数")

# 获取现有指标
existing_indicators = []
if os.path.exists('tradingview_100_indicators'):
    for filename in os.listdir('tradingview_100_indicators'):
        if filename.endswith('.py') and filename != '__init__.py':
            indicator_name = filename[:-3]  # 去掉.py
            existing_indicators.append(indicator_name)

print(f"\n📋 现有指标数: {len(existing_indicators)}")

# 检查哪些TA-Lib函数已经实现
print(f"\n🔍 检查已实现的TA-Lib函数:")
implemented_count = 0
for func in all_talib_functions:
    # 检查是否存在对应的指标文件
    # 注意: 指标文件名可能是小写
    func_lower = func.lower()
    found = False
    
    for indicator in existing_indicators:
        if func_lower == indicator.lower():
            implemented_count += 1
            found = True
            break
    
    # 检查去掉stream_前缀
    if func.startswith('stream_'):
        base_func = func[7:].lower()
        for indicator in existing_indicators:
            if base_func == indicator.lower():
                if not found:
                    implemented_count += 1
                found = True
                break

print(f"  已实现的TA-Lib函数: {implemented_count}")
print(f"  未实现的TA-Lib函数: {len(all_talib_functions) - implemented_count}")

# 列出一些未实现的函数
print(f"\n📝 部分未实现的TA-Lib函数:")
unimplemented = []
for func in all_talib_functions:
    func_lower = func.lower()
    found = False
    
    for indicator in existing_indicators:
        if func_lower == indicator.lower():
            found = True
            break
    
    if not found and func.startswith('stream_'):
        base_func = func[7:].lower()
        for indicator in existing_indicators:
            if base_func == indicator.lower():
                found = True
                break
    
    if not found:
        unimplemented.append(func)

# 显示前20个
for i, func in enumerate(unimplemented[:20]):
    print(f"  {i+1:2d}. {func}")

print(f"\n📊 统计:")
print(f"  TA-Lib总函数: {len(all_talib_functions)}")
print(f"  已实现函数: {implemented_count}")
print(f"  未实现函数: {len(unimplemented)}")
print(f"  实现比例: {implemented_count/len(all_talib_functions)*100:.1f}%")

# 按类别分析未实现函数
print(f"\n🎯 按类别分析未实现函数:")
for category, info in talib_data['category_details'].items():
    functions = info.get('functions', [])
    unimplemented_in_category = []
    
    for func in functions:
        func_lower = func.lower()
        found = False
        
        for indicator in existing_indicators:
            if func_lower == indicator.lower():
                found = True
                break
        
        if not found and func.startswith('stream_'):
            base_func = func[7:].lower()
            for indicator in existing_indicators:
                if base_func == indicator.lower():
                    found = True
                    break
        
        if not found:
            unimplemented_in_category.append(func)
    
    if unimplemented_in_category:
        print(f"  {category}: {len(unimplemented_in_category)} 个未实现")

# 保存结果
result = {
    'total_talib_functions': len(all_talib_functions),
    'existing_indicators': len(existing_indicators),
    'implemented_talib_functions': implemented_count,
    'unimplemented_talib_functions': len(unimplemented),
    'unimplemented_by_category': {},
    'sample_unimplemented': unimplemented[:50]
}

for category, info in talib_data['category_details'].items():
    functions = info.get('functions', [])
    unimplemented_in_category = []
    
    for func in functions:
        func_lower = func.lower()
        found = False
        
        for indicator in existing_indicators:
            if func_lower == indicator.lower():
                found = True
                break
        
        if not found and func.startswith('stream_'):
            base_func = func[7:].lower()
            for indicator in existing_indicators:
                if base_func == indicator.lower():
                    found = True
                    break
        
        if not found:
            unimplemented_in_category.append(func)
    
    if unimplemented_in_category:
        result['unimplemented_by_category'][category] = {
            'count': len(unimplemented_in_category),
            'functions': unimplemented_in_category[:20]
        }

with open('talib_implementation_analysis.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)

print(f"\n✅ 分析完成! 结果已保存到: talib_implementation_analysis.json")
print(f"\n💡 建议:")
print(f"  1. 从 {len(unimplemented)} 个未实现TA-Lib函数中选择")
print(f"  2. 创建组合指标和自定义指标填补剩余数量")
print(f"  3. 目标是达到总计200个指标")