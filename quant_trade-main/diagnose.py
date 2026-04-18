#!/usr/bin/env python3
"""
诊断量化平台策略导入问题
"""
import sys
import os
import importlib

print("🔍 QuantTrade策略导入诊断")
print("=" * 60)

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)
print(f"项目根目录: {project_root}")
print(f"Python路径[0]: {sys.path[0]}")

# 测试1: 导入BaseStrategy
print("\n1. 测试BaseStrategy导入...")
try:
    from strategies.base_strategy import BaseStrategy
    print("   ✅ BaseStrategy导入成功")
    print(f"     类: {BaseStrategy}")
    print(f"     模块: {BaseStrategy.__module__}")
except Exception as e:
    print(f"   ❌ BaseStrategy导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试2: 直接导入ma_strategy模块
print("\n2. 测试ma_strategy模块导入...")
try:
    ma_module = importlib.import_module('strategies.ma_strategy')
    print("   ✅ ma_strategy模块导入成功")
    print(f"     模块属性: {dir(ma_module)}")
    
    # 查找类
    classes = [attr for attr in dir(ma_module) 
               if not attr.startswith('_') and isinstance(getattr(ma_module, attr), type)]
    print(f"     找到的类: {classes}")
    
    # 检查MovingAverageStrategy
    if 'MovingAverageStrategy' in dir(ma_module):
        ma_class = getattr(ma_module, 'MovingAverageStrategy')
        print(f"   ✅ MovingAverageStrategy类存在")
        print(f"     父类: {ma_class.__bases__}")
        print(f"     是否继承BaseStrategy: {issubclass(ma_class, BaseStrategy)}")
    else:
        print(f"   ❌ MovingAverageStrategy类不存在")
        
except Exception as e:
    print(f"   ❌ ma_strategy模块导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试3: 测试其他策略依赖
print("\n3. 测试策略依赖...")
dependencies = {
    'tqdm': 'tqdm',
    'talib': 'talib', 
    'torch': 'torch',
    'flask': 'flask',
    'pandas': 'pandas',
    'numpy': 'numpy'
}

for name, module_name in dependencies.items():
    try:
        module = importlib.import_module(module_name)
        print(f"   ✅ {name}: 已安装 ({getattr(module, '__version__', '未知版本')})")
    except ImportError as e:
        print(f"   ❌ {name}: 未安装 ({e})")

# 测试4: 测试策略发现器
print("\n4. 测试BacktestRunner...")
try:
    from backtest.runner import BacktestRunner
    print("   ✅ BacktestRunner导入成功")
    
    runner = BacktestRunner()
    strategies = runner.list_strategies()
    print(f"     发现 {len(strategies)} 个策略: {strategies}")
    
    # 检查每个策略
    for name, cls in runner.strategies.items():
        print(f"     {name}: {cls}")
        
except Exception as e:
    print(f"   ❌ BacktestRunner导入失败: {e}")
    import traceback
    traceback.print_exc()

# 测试5: 直接运行runner.py
print("\n5. 直接运行runner.py...")
try:
    import subprocess
    result = subprocess.run(
        [sys.executable, os.path.join(project_root, 'backtest', 'runner.py')],
        capture_output=True,
        text=True,
        timeout=5
    )
    print(f"   退出码: {result.returncode}")
    if result.stdout:
        print(f"   输出: {result.stdout[:200]}...")
    if result.stderr:
        print(f"   错误: {result.stderr[:200]}...")
except Exception as e:
    print(f"   运行失败: {e}")

print("\n" + "=" * 60)
print("诊断完成")