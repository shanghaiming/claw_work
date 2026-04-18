import sys
import os
import importlib

# 添加当前目录到路径
sys.path.insert(0, '/Users/chengming/.openclaw/workspace/quant_trade-main')

# 创建一个虚拟的 price_action_integration 模块
import strategies.price_action_integration.optimized_integration_engine as dummy_engine
import strategies.price_action_integration.price_action_rules_integrator as dummy_rules

# 测试导入 strategies 模块
try:
    import strategies
    print("✅ strategies 模块导入成功")
except Exception as e:
    print(f"❌ strategies 模块导入失败: {e}")
    sys.exit(1)

# 测试 discover_strategies 函数
try:
    strategies_list = strategies.discover_strategies()
    print(f"\n发现 {len(strategies_list)} 个策略:")
    for name in strategies_list:
        print(f"  - {name}")
except Exception as e:
    print(f"❌ 策略发现失败: {e}")
    
# 检查特定策略
test_strategies = [
    'price_action_strategy',
    'simple_ma_strategy',
    'ma_strategy',
    'transformer',
    'tradingview_strategy'
]

print("\n逐个测试策略导入:")
for strat_name in test_strategies:
    try:
        # 尝试导入
        spec = importlib.util.spec_from_file_location(
            strat_name, 
            f"/Users/chengming/.openclaw/workspace/quant_trade-main/strategies/{strat_name}.py"
        )
        if spec is None:
            print(f"❌ {strat_name}: 找不到文件")
            continue
            
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        
        # 查找 BaseStrategy 的子类
        from strategies.base_strategy import BaseStrategy
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if isinstance(attr, type) and attr != BaseStrategy:
                try:
                    if issubclass(attr, BaseStrategy):
                        print(f"✅ {strat_name}: 找到策略类 {attr_name}")
                        break
                except:
                    pass
        else:
            print(f"⚠️  {strat_name}: 未找到继承 BaseStrategy 的类")
    except ImportError as e:
        print(f"❌ {strat_name}: 导入依赖失败 - {e}")
    except Exception as e:
        print(f"❌ {strat_name}: 导入失败 - {e}")