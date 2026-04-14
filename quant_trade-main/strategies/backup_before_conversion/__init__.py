"""
策略模块 - 统一接口
"""
from .base_strategy import BaseStrategy

# CSV版本策略适配器
try:
    from .csv_auto_select_adapter import CSVAutoSelectAdapter
    from .csv_price_action_adapter import CSVPriceActionAdapter
    from .csv_slide_wave_analysis import csv_slide_wave_analysis
except ImportError:
    pass

# 价格行为策略
try:
    from .price_action_ranges_market_structure_identifier import price_action_ranges_market_structure_identifier
    from .price_action_reversals_reversal_trading_basics import price_action_reversals_reversal_trading_basics
except ImportError:
    pass

# 基础策略
try:
    from .tradingview_strategy import tradingview_strategy
    from .ma_strategy_adapter import ma_strategy_adapter
    from .price_action_strategy import price_action_strategy
except ImportError:
    pass

__all__ = ['BaseStrategy']

# 动态添加可用策略
import os
import importlib

def discover_strategies():
    """发现所有策略"""
    strategies = {}
    strategies_dir = os.path.dirname(__file__)
    
    # 首先确保BaseStrategy可用
    try:
        from .base_strategy import BaseStrategy
    except Exception as e:
        print(f"BaseStrategy加载失败: {e}")
        return strategies
    
    for filename in os.listdir(strategies_dir):
        if filename.endswith('.py') and filename not in ['__init__.py', 'base_strategy.py']:
            strategy_name = filename[:-3]
            
            # 跳过已知的有问题的策略文件
            skip_files = [
                'ma_strategy_adapter.py',  # 需要core模块
                'csv_auto_select_adapter.py',  # 需要h11模块
                'tradingview_strategy.py',  # 需要talib模块
                'GRPO_strategy.py',  # 需要torch模块
                'GRPO_strategy_sim.py',  # 需要torch模块
                'price_action_strategy.py',  # 需要price_action_integration模块
                'csv_auto_select.py',  # 需要h11模块
            ]
            
            if filename in skip_files:
                print(f"⚠️  跳过有问题的策略文件: {filename}")
                continue
            
            try:
                # 使用importlib直接导入文件
                spec = importlib.util.spec_from_file_location(strategy_name, 
                    os.path.join(strategies_dir, filename))
                if spec is None:
                    continue
                
                module = importlib.util.module_from_spec(spec)
                
                # 执行模块，捕获所有异常
                try:
                    spec.loader.exec_module(module)
                except ImportError as e:
                    # 记录导入错误但不崩溃
                    print(f"⚠️  策略 {strategy_name} 导入依赖缺失: {e}")
                    continue
                except Exception as e:
                    # 其他错误也跳过
                    print(f"⚠️  策略 {strategy_name} 加载错误: {e}")
                    continue
                
                # 查找策略类
                found_class = None
                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if isinstance(attr, type):
                        try:
                            if issubclass(attr, BaseStrategy) and attr != BaseStrategy:
                                found_class = attr
                                break
                        except:
                            continue
                
                if found_class:
                    strategies[strategy_name] = found_class
                    print(f"✅ 加载策略: {strategy_name}")
                else:
                    print(f"⚠️  策略 {strategy_name} 未找到BaseStrategy子类")
                    
            except Exception as e:
                # 即使导入失败也不崩溃
                print(f"⚠️  策略 {strategy_name} 加载跳过: {e}")
                continue
    
    return strategies

# 自动发现策略（只有在直接运行或被明确要求时才执行）
if __name__ == '__main__' or os.environ.get('ENABLE_STRATEGY_DISCOVERY', '0') == '1':
    available_strategies = discover_strategies()
    for name, cls in available_strategies.items():
        globals()[name] = cls
        __all__.append(name)
    
    print(f"发现 {len(available_strategies)} 个可用策略")
else:
    # 不自动发现策略，减少导入时的输出
    available_strategies = {}
    # 只添加已知可用的策略
    try:
        from .ma_strategy import MovingAverageStrategy
        globals()['ma_strategy'] = MovingAverageStrategy
        __all__.append('ma_strategy')
        print("✅ 加载ma_strategy策略")
    except ImportError as e:
        print(f"⚠️  无法加载ma_strategy: {e}")
