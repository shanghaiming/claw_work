# 新的测试脚本
import sys
import os
import pandas as pd
import numpy as np

# 添加当前目录到路径
sys.path.insert(0, '/Users/chengming/.openclaw/workspace/quant_trade-main')

print("="*60)
print("策略导入与回测接口测试")
print("="*60)

# 创建测试数据
dates = pd.date_range('2025-01-01', periods=100, freq='D')
test_data = pd.DataFrame({
    'open': np.random.randn(100).cumsum() + 100,
    'high': np.random.randn(100).cumsum() + 105,
    'low': np.random.randn(100).cumsum() + 95,
    'close': np.random.randn(100).cumsum() + 100,
    'volume': np.random.randint(1000, 10000, 100),
    'symbol': '000001.SZ'
}, index=dates)

# 测试策略
test_cases = [
    ('ma_strategy', 'MovingAverageStrategy', {'short_window': 3, 'long_window': 5}),
    ('simple_ma_strategy', 'SimpleMovingAverageStrategy', {'short_window': 3, 'long_window': 5}),
]

print("\n1. 直接测试关键策略导入:")
for module_name, class_name, params in test_cases:
    print(f"\n测试 {module_name}...")
    try:
        # 直接导入模块
        module_path = f"/Users/chengming/.openclaw/workspace/quant_trade-main/strategies/{module_name}.py"
        import importlib.util
        spec = importlib.util.spec_from_file_location(module_name, module_path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 查找策略类
        StrategyClass = getattr(module, class_name)
        
        # 实例化策略
        strategy = StrategyClass(test_data, params)
        
        # 生成信号
        signals = strategy.generate_signals()
        
        print(f"  ✅ 导入成功，策略类: {class_name}")
        
        if signals:
            print(f"  ✅ 生成 {len(signals)} 个信号")
            if isinstance(signals, list) and len(signals) > 0 and isinstance(signals[0], dict):
                print(f"  ✅ 信号格式正确 (List[Dict])")
                # 显示一个示例信号
                print(f"    示例信号: {signals[0]}")
            else:
                print(f"  ⚠️  信号格式问题: {type(signals)}")
        else:
            print(f"  ⚠️  未生成信号")
            
    except Exception as e:
        print(f"  ❌ 失败: {e}")

# 测试回测系统
print("\n" + "="*60)
print("2. 测试回测系统...")
print("="*60)

# 测试回测引擎
backtest_engine_path = "/Users/chengming/.openclaw/workspace/quant_trade-main/backtest/src/backtest/engine.py"
try:
    import importlib.util
    spec = importlib.util.spec_from_file_location("backtest_engine", backtest_engine_path)
    engine_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(engine_module)
    
    print("✅ BacktestEngine 导入成功")
    
    # 创建回测引擎实例
    engine = engine_module.BacktestEngine()
    print("✅ BacktestEngine 实例化成功")
    
    # 测试数据加载
    data_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/data"
    if os.path.exists(data_dir):
        print(f"✅ 数据目录存在: {data_dir}")
        
        # 检查数据文件
        import glob
        csv_files = glob.glob(os.path.join(data_dir, "**", "*.csv"), recursive=True)
        print(f"  发现 {len(csv_files)} 个CSV文件")
        
        if csv_files:
            print(f"  示例文件: {os.path.basename(csv_files[0])}")
    else:
        print(f"⚠️  数据目录不存在: {data_dir}")
    
except Exception as e:
    print(f"❌ 回测系统测试失败: {e}")

# 测试 backtest/main.py
print("\n" + "="*60)
print("3. 测试回测主程序...")
print("="*60)

main_script = "/Users/chengming/.openclaw/workspace/quant_trade-main/backtest/main.py"
if os.path.exists(main_script):
    print(f"✅ main.py 文件存在")
    
    # 运行 --list-strategies 命令
    import subprocess
    try:
        cmd = ["/Users/chengming/.openclaw/workspace/quant_env/bin/python", main_script, "--list-strategies"]
        result = subprocess.run(cmd, capture_output=True, text=True, cwd="/Users/chengming/.openclaw/workspace/quant_trade-main")
        
        if result.returncode == 0:
            print("✅ --list-strategies 命令执行成功")
            # 提取策略列表
            for line in result.stdout.split('\n'):
                if "发现" in line and "个策略" in line:
                    print(f"  {line}")
        else:
            print(f"❌ 命令执行失败: {result.stderr[:200]}")
    except Exception as e:
        print(f"❌ 执行失败: {e}")
else:
    print(f"❌ main.py 文件不存在")

print("\n" + "="*60)
print("测试完成")
print("="*60)