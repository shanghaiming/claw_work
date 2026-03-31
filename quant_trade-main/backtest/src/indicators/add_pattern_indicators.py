#!/usr/bin/env python3
"""
添加模式识别指标以补足100个指标
"""

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

import json
import os
from datetime import datetime

# 配置
PATTERN_INDICATORS = [
    "CDL2CROWS", "CDL3BLACKCROWS", "CDL3INSIDE", "CDL3LINESTRIKE", "CDL3OUTSIDE",
    "CDL3STARSINSOUTH", "CDL3WHITESOLDIERS", "CDLABANDONEDBABY", "CDLADVANCEBLOCK",
    "CDLBELTHOLD", "CDLBREAKAWAY", "CDLCLOSINGMARUBOZU", "CDLCONCEALBABYSWALL",
    "CDLCOUNTERATTACK", "CDLDARKCLOUDCOVER", "CDLDOJI", "CDLDOJISTAR",
    "CDLDRAGONFLYDOJI", "CDLENGULFING", "CDLEVENINGDOJISTAR", "CDLEVENINGSTAR",
    "CDLGAPSIDESIDEWHITE", "CDLGRAVESTONEDOJI", "CDLHAMMER", "CDLHANGINGMAN",
    "CDLHARAMI", "CDLHARAMICROSS", "CDLHIGHWAVE", "CDLHIKKAKE", "CDLHIKKAKEMOD",
    "CDLHOMINGPIGEON", "CDLIDENTICAL3CROWS", "CDLINNECK", "CDLINVERTEDHAMMER",
    "CDLKICKING", "CDLKICKINGBYLENGTH", "CDLLADDERBOTTOM", "CDLLONGLEGGEDDOJI",
    "CDLLONGLINE", "CDLMARUBOZU", "CDLMATCHINGLOW", "CDLMATHOLD", "CDLMORNINGDOJISTAR",
    "CDLMORNINGSTAR", "CDLONNECK", "CDLPIERCING", "CDLRICKSHAWMAN", "CDLRISEFALL3METHODS",
    "CDLSEPARATINGLINES", "CDLSHOOTINGSTAR", "CDLSHORTLINE", "CDLSPINNINGTOP",
    "CDLSTALLEDPATTERN", "CDLSTICKSANDWICH", "CDLTAKURI", "CDLTASUKIGAP",
    "CDLTHRUSTING", "CDLTRISTAR", "CDLUNIQUE3RIVER", "CDLUPSIDEGAP2CROWS",
    "CDLXSIDEGAP3METHODS"
]

def add_pattern_indicators():
    """添加模式识别指标"""
    output_dir = "tradingview_100_indicators"
    
    # 确保目录存在
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 读取现有指标
    existing_files = os.listdir(output_dir)
    existing_indicators = [f.replace('.py', '').upper() for f in existing_files if f.endswith('.py')]
    
    print(f"现有指标数量: {len(existing_indicators)}")
    
    # 选择需要添加的指标
    added_count = 0
    target_additional = 100 - len(existing_indicators)
    
    for pattern in PATTERN_INDICATORS:
        if added_count >= target_additional:
            break
            
        if pattern.lower() + '.py' in existing_files:
            continue
        
        # 生成指标文件
        generate_pattern_indicator(pattern, output_dir)
        added_count += 1
        print(f"添加模式识别指标: {pattern} ({added_count}/{target_additional})")
    
    print(f"成功添加 {added_count} 个模式识别指标")
    print(f"总指标数量: {len(existing_indicators) + added_count}")
    
    # 更新__init__.py
    update_init_file(output_dir)

def generate_pattern_indicator(pattern_name: str, output_dir: str):
    """生成模式识别指标文件"""
    code = f'''"""
{pattern_name} - 蜡烛图形态识别指标

基于TA-Lib的{pattern_name}函数实现
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import numpy as np
import talib

class TV_{pattern_name}:
    """TradingView风格的{pattern_name}蜡烛图形态指标"""
    
    def __init__(self):
        """初始化指标"""
        self.name = "{pattern_name}"
        self.description = "蜡烛图形态识别: {pattern_name}"
        self.author = "OpenClaw量化系统"
        self.version = "1.0.0"
        
    def calculate(self, open, high, low, close):
        """
        计算{pattern_name}形态
        
        参数:
            open: 开盘价序列
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
        
        返回:
            result: 形态识别结果 (通常为0, 100, -100)
        """
        try:
            result = talib.{pattern_name}(open, high, low, close)
            return result
        except Exception as e:
            print(f"计算指标{{self.name}}时出错: {{e}}")
            return None
    
    def signal(self, open, high, low, close):
        """
        生成交易信号
        
        参数:
            open: 开盘价序列
            high: 最高价序列
            low: 最低价序列
            close: 收盘价序列
        
        返回:
            signal: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
        """
        try:
            values = self.calculate(open, high, low, close)
            if values is None:
                return np.zeros_like(close)
            
            # 蜡烛图形态信号: 通常正数表示看涨，负数表示看跌
            signal = np.zeros_like(values)
            
            for i in range(len(values)):
                if values[i] > 0:
                    signal[i] = 1  # 看涨信号
                elif values[i] < 0:
                    signal[i] = -1  # 看跌信号
            
            return signal
        except Exception as e:
            print(f"生成信号时出错: {{e}}")
            return np.zeros_like(close)
    
    def plot_style(self):
        """返回绘图样式配置"""
        return {{
            "name": self.name,
            "type": "histogram",
            "color": "#FF6B6B",
            "linewidth": 1,
            "title": self.name,
            "trackPrice": False
        }}

def {pattern_name.lower()}(open, high, low, close):
    """
    简化的函数接口
    
    参数:
        open: 开盘价序列
        high: 最高价序列
        low: 最低价序列
        close: 收盘价序列
    
    返回:
        result: 形态识别结果
    """
    indicator = TV_{pattern_name}()
    return indicator.calculate(open, high, low, close)

if __name__ == "__main__":
    # 测试代码
    np.random.seed(42)
    n = 100
    
    # 生成测试数据
    open = np.random.uniform(95, 105, n)
    high = np.random.uniform(100, 110, n)
    low = np.random.uniform(90, 100, n)
    close = np.random.uniform(95, 105, n)
    
    # 创建指标实例
    indicator = TV_{pattern_name}()
    
    # 测试计算
    try:
        result = indicator.calculate(open, high, low, close)
        print(f"{{indicator.name}} 测试完成")
        print(f"结果形状: {{result.shape if hasattr(result, 'shape') else len(result)}}")
        print(f"前10个值: {{result[:10] if hasattr(result, '__len__') else result}}")
        
        # 测试信号生成
        signal = indicator.signal(open, high, low, close)
        print(f"信号统计 - 买入: {{np.sum(signal == 1)}}, 卖出: {{np.sum(signal == -1)}}, 持有: {{np.sum(signal == 0)}}")
    except Exception as e:
        print(f"测试失败: {{e}}")
'''
    
    filename = f"{pattern_name.lower()}.py"
    filepath = os.path.join(output_dir, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)

def update_init_file(output_dir: str):
    """更新__init__.py文件"""
    init_file = os.path.join(output_dir, "__init__.py")
    
    if not os.path.exists(init_file):
        print(f"初始化文件不存在: {init_file}")
        return
    
    # 读取现有内容
    with open(init_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 查找所有导入语句的结束位置
    lines = content.split('\n')
    import_end = 0
    for i, line in enumerate(lines):
        if line.startswith('__all__'):
            import_end = i
            break
    
    if import_end == 0:
        print("无法找到__all__开始位置")
        return
    
    # 获取现有指标列表
    existing_imports = []
    for line in lines[:import_end]:
        if line.startswith('from .'):
            existing_imports.append(line)
    
    # 获取所有.py文件
    py_files = [f for f in os.listdir(output_dir) if f.endswith('.py') and f != '__init__.py']
    
    # 生成新的导入语句
    new_imports = []
    for py_file in py_files:
        indicator_name = py_file.replace('.py', '')
        class_name = f"TV_{indicator_name.upper()}"
        if indicator_name == indicator_name.lower():
            # 已经是小写，说明是模式识别指标
            class_name = f"TV_{indicator_name.upper()}"
        else:
            # 可能是混合大小写
            class_name = f"TV_{indicator_name}"
        
        import_line = f"from .{indicator_name} import {class_name}, {indicator_name}"
        if import_line not in existing_imports and import_line not in new_imports:
            new_imports.append(import_line)
    
    # 生成新的__all__列表
    all_list = []
    for py_file in py_files:
        indicator_name = py_file.replace('.py', '')
        class_name = f"TV_{indicator_name.upper()}"
        if indicator_name == indicator_name.lower():
            class_name = f"TV_{indicator_name.upper()}"
        else:
            class_name = f"TV_{indicator_name}"
        
        all_list.append(f'    "{class_name}",')
        all_list.append(f'    "{indicator_name}",')
    
    # 重建文件内容
    header = '''"""
TradingView风格指标库 (基于TA-Lib)

包含100个TradingView风格的技术指标，每个指标都有标准化的接口：
1. calculate() - 计算指标值
2. signal() - 生成交易信号
3. plot_style() - 获取绘图样式

生成时间: {datetime}
指标总数: {count}
"""

'''.format(datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"), count=len(py_files))
    
    import_section = '\n'.join(sorted(new_imports))
    all_section = '__all__ = [\n' + '\n'.join(sorted(set(all_list))) + '\n]'
    
    new_content = header + import_section + '\n\n' + all_section + '\n'
    
    with open(init_file, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print(f"更新初始化文件: {init_file}")

if __name__ == "__main__":
    add_pattern_indicators()