"""
TradingView风格组合指标库

基于5种设计模式的组合指标和自定义指标：
1. 自适应设计模式 (20个指标)
2. 复合系统模式 (20个指标)  
3. 风险管理集成模式 (15个指标)
4. 可视化增强模式 (15个指标)
5. 市场结构分析模式 (10个指标)

生成时间: 2026-03-30 20:27:04
设计思想来源: TradingView社区指标深度分析
"""

# 导入各个模式的指标

# adaptive_design 模式指标
try:
    from .adaptive_design import *
except ImportError:
    print(f"无法导入{'adaptive_design'}模式指标")

# composite_system 模式指标
try:
    from .composite_system import *
except ImportError:
    print(f"无法导入{'composite_system'}模式指标")

# risk_management_integration 模式指标
try:
    from .risk_management_integration import *
except ImportError:
    print(f"无法导入{'risk_management_integration'}模式指标")

# visualization_enhancement 模式指标
try:
    from .visualization_enhancement import *
except ImportError:
    print(f"无法导入{'visualization_enhancement'}模式指标")

# market_structure_analysis 模式指标
try:
    from .market_structure_analysis import *
except ImportError:
    print(f"无法导入{'market_structure_analysis'}模式指标")

__all__ = [
    # 各个模式的指标类将在运行时动态添加
]

# 动态收集所有可用的指标类
def collect_indicators():
    """收集所有可用的指标类"""
    import os
    import importlib
    
    all_indicators = {}
    
    # 遍历所有模式目录
    for pattern_name in os.listdir(os.path.dirname(__file__)):
        pattern_dir = os.path.join(os.path.dirname(__file__), pattern_name)
        if os.path.isdir(pattern_dir) and pattern_name != "__pycache__":
            try:
                # 导入模式模块
                pattern_module = importlib.import_module(f".{pattern_name}", __package__)
                
                # 收集模块中的所有TV_开头的类
                for attr_name in dir(pattern_module):
                    if attr_name.startswith("TV_"):
                        all_indicators[attr_name] = getattr(pattern_module, attr_name)
                        
            except ImportError as e:
                print(f"无法导入模式 {{pattern_name}}: {{e}}")
    
    return all_indicators

# 提供全局访问函数
def get_available_indicators():
    """获取所有可用的指标类"""
    return collect_indicators()
