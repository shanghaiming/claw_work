#!/usr/bin/env python3
"""
生成TA-Lib数学变换指标
这些是剩余的20个数学函数：ACOS, ASIN, ATAN, CEIL, COS, COSH, EXP, FLOOR, LN, LOG10, SIN, SINH, SQRT, TAN, TANH
以及它们的stream_版本
"""

# 整合适配 - 自动添加
from backtest.src.strategies.base_strategy import BaseStrategy

import os
import numpy as np
import talib
from datetime import datetime

# 数学函数列表（包括stream_版本）
MATH_FUNCTIONS = [
    "ACOS", "ASIN", "ATAN", "CEIL", "COS", "COSH", "EXP", "FLOOR", "LN", "LOG10",
    "SIN", "SINH", "SQRT", "TAN", "TANH",
    "stream_ACOS", "stream_ASIN", "stream_ATAN", "stream_CEIL", "stream_COS"
]

# 输出目录
OUTPUT_DIR = "tradingview_math_indicators"

def generate_math_indicator_class(func_name: str) -> str:
    """生成数学变换指标的TradingView风格类"""
    # 确定基函数名（去掉stream_前缀）
    base_name = func_name.replace("stream_", "")
    
    # 获取函数文档
    try:
        func = getattr(talib, func_name)
        doc = func.__doc__ or ""
    except:
        doc = ""
    
    # 数学函数描述
    math_descriptions = {
        "ACOS": "反余弦函数，计算实数的反余弦值",
        "ASIN": "反正弦函数，计算实数的反正弦值", 
        "ATAN": "反正切函数，计算实数的反正切值",
        "CEIL": "向上取整函数，返回不小于输入值的最小整数",
        "COS": "余弦函数，计算角度的余弦值",
        "COSH": "双曲余弦函数",
        "EXP": "指数函数，计算e的x次幂",
        "FLOOR": "向下取整函数，返回不大于输入值的最大整数",
        "LN": "自然对数函数，计算以e为底的对数",
        "LOG10": "常用对数函数，计算以10为底的对数",
        "SIN": "正弦函数，计算角度的正弦值",
        "SINH": "双曲正弦函数",
        "SQRT": "平方根函数，计算非负实数的平方根",
        "TAN": "正切函数，计算角度的正切值",
        "TANH": "双曲正切函数"
    }
    
    description = math_descriptions.get(base_name, "数学变换函数")
    if func_name.startswith("stream_"):
        description += " (流式版本，支持实时更新)"
    
    class_name = f"TV_{func_name}"
    
    code = f'''"""
{class_name} - TradingView风格的{func_name}数学变换指标

{description}
基于TA-Lib的{func_name}函数实现
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import numpy as np
import pandas as pd
import talib

class {class_name}:
    """TradingView风格的{func_name}数学变换指标"""
    
    def __init__(self):
        """初始化指标"""
        self.name = "{func_name}"
        self.description = "{description}"
        self.author = "OpenClaw量化系统"
        self.version = "1.0.0"
        
    def calculate(self, real):
        """
        计算{func_name}指标
        
        参数:
            real: 输入序列
        
        返回:
            result: 数学变换结果
        """
        try:
            result = talib.{func_name}(real)
            return result
        except Exception as e:
            print(f"计算指标{{self.name}}时出错: {{e}}")
            return None
    
    def signal(self, real, threshold=0.5):
        """
        生成交易信号（基于数学变换的极端值）
        
        参数:
            real: 输入序列
            threshold: 信号阈值
        
        返回:
            signal: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
        """
        try:
            values = self.calculate(real)
            if values is None:
                return np.zeros_like(real)
            
            # 数学变换信号的生成逻辑
            signal = np.zeros_like(values)
            
            # 根据函数类型生成不同的信号
            if "{base_name}" in ["ACOS", "ASIN"]:
                # 反三角函数，值域在特定范围内
                for i in range(1, len(values)):
                    if values[i] > threshold and values[i-1] <= threshold:
                        signal[i] = -1  # 值过高，卖出信号
                    elif values[i] < -threshold and values[i-1] >= -threshold:
                        signal[i] = 1   # 值过低，买入信号
                        
            elif "{base_name}" in ["CEIL", "FLOOR"]:
                # 取整函数，检测整数关口突破
                for i in range(1, len(values)):
                    if abs(values[i] - values[i-1]) >= 0.9:  # 接近整数变化
                        if values[i] > values[i-1]:
                            signal[i] = 1   # 向上突破整数关口
                        else:
                            signal[i] = -1  # 向下跌破整数关口
                            
            elif "{base_name}" in ["EXP", "LN", "LOG10"]:
                # 指数和对数函数，检测增长率变化
                for i in range(2, len(values)):
                    if values[i-1] != 0:
                        growth = values[i] / values[i-1]
                        if growth > 1 + threshold:
                            signal[i] = 1   # 快速增长
                        elif growth < 1 - threshold:
                            signal[i] = -1  # 快速下降
                            
            elif "{base_name}" in ["SIN", "COS", "TAN", "SINH", "COSH", "TANH"]:
                # 三角函数，检测周期性变化
                for i in range(1, len(values)):
                    if values[i] > threshold and values[i-1] <= threshold:
                        signal[i] = -1  # 达到峰值
                    elif values[i] < -threshold and values[i-1] >= -threshold:
                        signal[i] = 1   # 达到谷值
                        
            elif "{base_name}" == "SQRT":
                # 平方根函数，检测平方根增长率
                for i in range(2, len(values)):
                    if values[i-1] > 0:
                        growth = values[i] / values[i-1]
                        if growth > 1 + threshold/2:
                            signal[i] = 1   # 快速增长
                        elif growth < 1 - threshold/2:
                            signal[i] = -1  # 快速下降
            
            return signal
        except Exception as e:
            print(f"生成信号时出错: {{e}}")
            return np.zeros_like(real)
    
    def plot_style(self):
        """返回绘图样式配置"""
        # 根据函数类型选择颜色
        color_map = {{
            "ACOS": "#FF6B6B",
            "ASIN": "#4ECDC4", 
            "ATAN": "#45B7D1",
            "CEIL": "#96CEB4",
            "COS": "#FECA57",
            "COSH": "#FF9FF3",
            "EXP": "#54A0FF",
            "FLOOR": "#5F27CD",
            "LN": "#00D2D3",
            "LOG10": "#FF9F43",
            "SIN": "#EE5A24",
            "SINH": "#C4E538",
            "SQRT": "#12CBC4",
            "TAN": "#FDA7DF",
            "TANH": "#ED4C67"
        }}
        
        color = color_map.get("{base_name}", "#2962FF")
        
        return {{
            "name": self.name,
            "type": "line",
            "color": color,
            "linewidth": 1,
            "title": self.name,
            "trackPrice": False,
            "description": self.description
        }}

def {func_name.lower()}(real):
    """
    简化的函数接口
    
    参数:
        real: 输入序列
    
    返回:
        result: 数学变换结果
    """
    indicator = {class_name}()
    return indicator.calculate(real)

if __name__ == "__main__":
    # 测试代码
    np.random.seed(42)
    n = 100
    
    # 生成测试数据
    real = np.random.uniform(-0.9, 0.9, n)  # 对于三角函数，保持在定义域内
    
    # 特殊处理某些函数
    if "{base_name}" in ["SQRT", "LN", "LOG10"]:
        real = np.random.uniform(0.1, 10, n)  # 正数
    elif "{base_name}" in ["ACOS", "ASIN"]:
        real = np.random.uniform(-0.9, 0.9, n)  # 保持在[-1, 1]范围内
    
    # 创建指标实例
    indicator = {class_name}()
    
    # 测试计算
    try:
        result = indicator.calculate(real)
        print(f"{{indicator.name}} 测试完成")
        print(f"结果形状: {{result.shape if hasattr(result, 'shape') else len(result)}}")
        print(f"前10个值: {{result[:10] if hasattr(result, '__len__') else result}}")
        
        # 测试信号生成
        signal = indicator.signal(real, threshold=0.5)
        print(f"信号统计 - 买入: {{np.sum(signal == 1)}}, 卖出: {{np.sum(signal == -1)}}, 持有: {{np.sum(signal == 0)}}")
    except Exception as e:
        print(f"测试失败: {{e}}")
'''
    return code

def save_indicator_file(func_name: str, code: str):
    """保存指标文件"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    filename = f"{func_name.lower()}.py"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)
    
    print(f"生成数学指标: {func_name} -> {filepath}")

def create_init_file(func_names: list):
    """创建__init__.py文件"""
    init_content = f'''"""
TradingView风格数学变换指标库 (基于TA-Lib)

包含{len(func_names)}个数学变换指标，每个指标都有标准化的接口：
1. calculate() - 计算数学变换值
2. signal() - 生成基于数学变换的交易信号
3. plot_style() - 获取绘图样式

生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
指标总数: {len(func_names)}
"""

'''
    
    # 添加导入语句
    for func_name in func_names:
        class_name = f"TV_{func_name}"
        init_content += f"from .{func_name.lower()} import {class_name}, {func_name.lower()}\n"
    
    init_content += "\n__all__ = [\n"
    for func_name in func_names:
        class_name = f"TV_{func_name}"
        init_content += f'    "{class_name}",\n    "{func_name.lower()}",\n'
    init_content += "]\n"
    
    filepath = os.path.join(OUTPUT_DIR, "__init__.py")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(init_content)
    
    print(f"创建初始化文件: {filepath}")

def main():
    print("=" * 80)
    print("🧮 生成TA-Lib数学变换指标")
    print("=" * 80)
    
    print(f"📊 需要生成 {len(MATH_FUNCTIONS)} 个数学变换指标")
    
    generated_count = 0
    failed_functions = []
    
    for i, func_name in enumerate(MATH_FUNCTIONS, 1):
        try:
            print(f"  [{i}/{len(MATH_FUNCTIONS)}] 生成 {func_name}...")
            
            # 生成指标类代码
            code = generate_math_indicator_class(func_name)
            
            # 保存文件
            save_indicator_file(func_name, code)
            
            generated_count += 1
        except Exception as e:
            print(f"  ✗ 生成 {func_name} 失败: {e}")
            failed_functions.append(func_name)
    
    # 创建初始化文件
    print("📁 创建初始化文件...")
    successful_functions = [f for f in MATH_FUNCTIONS if f not in failed_functions]
    create_init_file(successful_functions)
    
    print("=" * 80)
    print(f"✅ 数学变换指标生成完成!")
    print(f"   成功生成: {generated_count}/{len(MATH_FUNCTIONS)}")
    print(f"   失败: {len(failed_functions)}")
    if failed_functions:
        print(f"   失败的函数: {failed_functions}")
    print(f"   输出目录: {OUTPUT_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()