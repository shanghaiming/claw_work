#!/usr/bin/env python3
"""
从TA-Lib生成TradingView风格指标库
目标：生成100个TradingView风格的指标

步骤：
1. 从talib_comprehensive_report.json加载指标分类
2. 选择100个最相关的指标（去除重复和stream_版本）
3. 为每个指标生成TradingView风格的Python类
4. 保存到tradingview_100_indicators目录
"""

import json
import os
import re
from typing import List, Dict, Any, Set
import talib
import inspect
from datetime import datetime

# 配置
TARGET_INDICATOR_COUNT = 100
OUTPUT_DIR = "tradingview_100_indicators"
REPORT_FILE = "talib_comprehensive_report.json"

def load_indicator_report() -> Dict[str, Any]:
    """加载TA-Lib指标报告"""
    with open(REPORT_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def deduplicate_indicators(category_details: Dict[str, Dict]) -> List[str]:
    """去重指标列表，移除stream_前缀的重复项"""
    all_indicators = set()
    
    for category, data in category_details.items():
        if category == "模式识别":
            continue  # 跳过模式识别，不适合作为独立指标
        if category == "数学变换":
            continue  # 跳过纯数学函数
        indicators = data.get("functions", [])
        for indicator in indicators:
            # 移除stream_前缀
            if indicator.startswith("stream_"):
                base_name = indicator[7:]  # 移除"stream_"
                if base_name in indicators:
                    continue  # 跳过流式版本
            all_indicators.add(indicator)
    
    return sorted(list(all_indicators))

def select_top_indicators(all_indicators: List[str], target_count: int) -> List[str]:
    """选择最重要的指标"""
    # 优先级：趋势指标 > 动量指标 > 波动率指标 > 成交量指标 > 其他
    
    # 先按类别排序（手动分类，因为原始报告分类不完整）
    trend_keywords = ['MA', 'EMA', 'SMA', 'WMA', 'DEMA', 'TEMA', 'TRIMA', 'KAMA', 'MAMA', 'SAR', 'AROON', 'ADX', 'CCI', 'DX', 'MACD', 'STOCH', 'RSI', 'MOM', 'ROC', 'WILLR', 'ULTOSC', 'CMO', 'PPO', 'APO', 'BOP', 'MFI', 'TRIX']
    volatility_keywords = ['ATR', 'BBANDS', 'NATR', 'STDDEV', 'VAR', 'TRANGE', 'MIDPOINT', 'MIDPRICE']
    volume_keywords = ['AD', 'OBV', 'ADOSC', 'ADD']
    cycle_keywords = ['HT_', 'SINE', 'PHASOR', 'DCPERIOD', 'DCPHASE']
    statistical_keywords = ['CORREL', 'LINEARREG', 'LINEARREG_ANGLE', 'LINEARREG_INTERCEPT', 'LINEARREG_SLOPE', 'TSF', 'VAR', 'STDDEV']
    
    categorized = {
        'trend': [],
        'volatility': [],
        'volume': [],
        'cycle': [],
        'statistical': [],
        'other': []
    }
    
    for indicator in all_indicators:
        indicator_upper = indicator.upper()
        found = False
        
        # 检查趋势指标
        for keyword in trend_keywords:
            if keyword.upper() in indicator_upper:
                categorized['trend'].append(indicator)
                found = True
                break
        
        if found:
            continue
            
        # 检查波动率指标
        for keyword in volatility_keywords:
            if keyword.upper() in indicator_upper:
                categorized['volatility'].append(indicator)
                found = True
                break
        
        if found:
            continue
            
        # 检查成交量指标
        for keyword in volume_keywords:
            if keyword.upper() in indicator_upper:
                categorized['volume'].append(indicator)
                found = True
                break
        
        if found:
            continue
            
        # 检查周期指标
        for keyword in cycle_keywords:
            if keyword.upper() in indicator_upper:
                categorized['cycle'].append(indicator)
                found = True
                break
        
        if found:
            continue
            
        # 检查统计指标
        for keyword in statistical_keywords:
            if keyword.upper() in indicator_upper:
                categorized['statistical'].append(indicator)
                found = True
                break
        
        if not found:
            categorized['other'].append(indicator)
    
    # 选择指标，确保总数达到target_count
    selected = []
    
    # 优先选择趋势指标
    selected.extend(categorized['trend'][:50])  # 最多50个趋势指标
    
    # 添加其他类别
    remaining = target_count - len(selected)
    if remaining > 0:
        selected.extend(categorized['volatility'][:15])
    
    remaining = target_count - len(selected)
    if remaining > 0:
        selected.extend(categorized['volume'][:10])
    
    remaining = target_count - len(selected)
    if remaining > 0:
        selected.extend(categorized['cycle'][:10])
    
    remaining = target_count - len(selected)
    if remaining > 0:
        selected.extend(categorized['statistical'][:10])
    
    remaining = target_count - len(selected)
    if remaining > 0:
        selected.extend(categorized['other'][:remaining])
    
    # 如果还不够，从趋势指标中补充
    if len(selected) < target_count:
        additional_needed = target_count - len(selected)
        trend_remaining = categorized['trend'][50:]  # 已取50个
        selected.extend(trend_remaining[:additional_needed])
    
    return selected[:target_count]

def get_talib_function_info(indicator_name: str) -> Dict[str, Any]:
    """获取TA-Lib函数的详细信息"""
    try:
        func = getattr(talib, indicator_name)
        
        # 获取函数签名
        sig = inspect.signature(func)
        params = list(sig.parameters.keys())
        
        # 获取文档字符串
        doc = func.__doc__ or ""
        
        # 确定函数类型（输入类型）
        func_type = "unknown"
        if 'high' in params and 'low' in params and 'close' in params:
            func_type = "price_based"
        elif 'real' in params:
            func_type = "price_based"  # 可能是收盘价
        elif 'volume' in params:
            func_type = "volume_based"
        else:
            func_type = "general"
        
        return {
            "name": indicator_name,
            "parameters": params,
            "doc": doc[:500] if doc else "",  # 截断
            "type": func_type
        }
    except Exception as e:
        print(f"获取函数信息失败 {indicator_name}: {e}")
        return {
            "name": indicator_name,
            "parameters": [],
            "doc": "",
            "type": "unknown"
        }

def generate_tradingview_indicator_class(indicator_info: Dict[str, Any]) -> str:
    """生成TradingView风格的指标类"""
    name = indicator_info["name"]
    params = indicator_info["parameters"]
    func_type = indicator_info["type"]
    
    # 类名
    class_name = f"TV_{name}"
    
    # 生成参数注释
    param_docs = ""
    for param in params:
        if param in ['high', 'low', 'close', 'open', 'volume']:
            param_docs += f"        {param}: {param}序列\n"
        elif param in ['timeperiod', 'period', 'fastperiod', 'slowperiod', 'signalperiod']:
            param_docs += f"        {param}: 周期参数 (默认值根据TA-Lib)\n"
        elif param in ['nbdevup', 'nbdevdn', 'acceleration', 'maximum']:
            param_docs += f"        {param}: 技术参数\n"
        else:
            param_docs += f"        {param}: 参数\n"
    
    # 生成函数调用参数
    call_params = ", ".join(params)
    
    # 确定输入数据
    if func_type == "price_based":
        inputs = "high, low, close"
        # 检查是否需要open
        if 'open' in params:
            inputs = "open, high, low, close"
    elif func_type == "volume_based":
        inputs = "volume"
        if 'high' in params and 'low' in params and 'close' in params:
            inputs = "high, low, close, volume"
    else:
        inputs = "close"  # 默认
    
    # 生成类的代码
    code = f'''"""
{class_name} - TradingView风格的{name}指标

基于TA-Lib的{name}函数实现
生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

import numpy as np
import pandas as pd
import talib

class {class_name}:
    """TradingView风格的{name}指标"""
    
    def __init__(self):
        """初始化指标"""
        self.name = "{name}"
        self.description = "基于TA-Lib {name}函数的TradingView风格实现"
        self.author = "OpenClaw量化系统"
        self.version = "1.0.0"
        
    def calculate(self, {call_params}):
        """
        计算{name}指标
        
        参数:
{param_docs}
        返回:
            result: 指标结果
        """
        try:
            result = talib.{name}({call_params})
            return result
        except Exception as e:
            print(f"计算指标{{self.name}}时出错: {{e}}")
            return None
    
    def signal(self, {call_params}, threshold=0):
        """
        生成交易信号
        
        参数:
{param_docs}
            threshold: 信号阈值
        
        返回:
            signal: 交易信号 (1: 买入, -1: 卖出, 0: 持有)
        """
        try:
            values = self.calculate({call_params})
            if values is None:
                return np.zeros_like({params[0] if params else 'close'})
            
            # 默认信号生成逻辑（可根据指标类型定制）
            signal = np.zeros_like(values)
            
            # 简单阈值信号
            if len(values.shape) == 1:  # 一维数组
                for i in range(1, len(values)):
                    if values[i] > threshold and values[i-1] <= threshold:
                        signal[i] = 1  # 买入
                    elif values[i] < -threshold and values[i-1] >= -threshold:
                        signal[i] = -1  # 卖出
            else:
                # 多维数组，取第一列
                if values.shape[1] > 0:
                    col_values = values[:, 0]
                    for i in range(1, len(col_values)):
                        if col_values[i] > threshold and col_values[i-1] <= threshold:
                            signal[i] = 1
                        elif col_values[i] < -threshold and col_values[i-1] >= -threshold:
                            signal[i] = -1
            
            return signal
        except Exception as e:
            print(f"生成信号时出错: {{e}}")
            return np.zeros_like({params[0] if params else 'close'})
    
    def plot_style(self):
        """返回绘图样式配置"""
        return {{
            "name": self.name,
            "type": "line",
            "color": "#2962FF",
            "linewidth": 1,
            "title": self.name,
            "trackPrice": True
        }}

def {name.lower()}({call_params}):
    """
    简化的函数接口
    
    参数:
{param_docs}
    返回:
        result: 指标结果
    """
    indicator = {class_name}()
    return indicator.calculate({call_params})

if __name__ == "__main__":
    # 测试代码
    np.random.seed(42)
    n = 100
    
    # 生成测试数据
    high = np.random.uniform(100, 110, n)
    low = np.random.uniform(90, 100, n)
    close = np.random.uniform(95, 105, n)
    
    # 创建指标实例
    indicator = {class_name}()
    
    # 测试计算
    try:
        result = indicator.calculate({call_params})
        print(f"{{indicator.name}} 测试完成")
        print(f"结果形状: {{result.shape if hasattr(result, 'shape') else len(result)}}")
        print(f"前10个值: {{result[:10] if hasattr(result, '__len__') else result}}")
        
        # 测试信号生成
        signal = indicator.signal({call_params}, threshold=0)
        print(f"信号统计 - 买入: {{np.sum(signal == 1)}}, 卖出: {{np.sum(signal == -1)}}, 持有: {{np.sum(signal == 0)}}")
    except Exception as e:
        print(f"测试失败: {{e}}")
'''
    return code

def save_indicator_file(indicator_name: str, code: str):
    """保存指标文件"""
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    filename = f"{indicator_name.lower()}.py"
    filepath = os.path.join(OUTPUT_DIR, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(code)
    
    print(f"生成指标: {indicator_name} -> {filepath}")

def create_init_file(indicators: List[str]):
    """创建__init__.py文件"""
    init_content = '''"""
TradingView风格指标库 (基于TA-Lib)

包含100个TradingView风格的技术指标，每个指标都有标准化的接口：
1. calculate() - 计算指标值
2. signal() - 生成交易信号
3. plot_style() - 获取绘图样式

生成时间: {datetime}
指标总数: {count}
"""

'''
    init_content = init_content.format(
        datetime=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        count=len(indicators)
    )
    
    # 添加导入语句
    for indicator in indicators:
        class_name = f"TV_{indicator}"
        init_content += f"from .{indicator.lower()} import {class_name}, {indicator.lower()}\n"
    
    init_content += "\n__all__ = [\n"
    for indicator in indicators:
        class_name = f"TV_{indicator}"
        init_content += f'    "{class_name}",\n    "{indicator.lower()}",\n'
    init_content += "]\n"
    
    filepath = os.path.join(OUTPUT_DIR, "__init__.py")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(init_content)
    
    print(f"创建初始化文件: {filepath}")

def create_summary_report(indicators: List[str], report_file: str = "tradingview_100_indicators_summary.json"):
    """创建指标库摘要报告"""
    summary = {
        "generated_at": datetime.now().isoformat(),
        "total_indicators": len(indicators),
        "indicators": indicators,
        "source": "TA-Lib",
        "output_directory": OUTPUT_DIR,
        "description": "100个TradingView风格的技术指标库，基于TA-Lib实现"
    }
    
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    
    print(f"创建摘要报告: {report_file}")

def main():
    print("=" * 80)
    print("🎯 生成100个TradingView风格指标")
    print("=" * 80)
    
    # 1. 加载指标报告
    print("📊 加载TA-Lib指标报告...")
    report = load_indicator_report()
    category_details = report.get("category_details", {})
    
    # 2. 去重指标
    print("🔄 去重指标列表...")
    all_indicators = deduplicate_indicators(category_details)
    print(f"去重后指标总数: {len(all_indicators)}")
    
    # 3. 选择100个指标
    print(f"🎯 选择{TARGET_INDICATOR_COUNT}个指标...")
    selected_indicators = select_top_indicators(all_indicators, TARGET_INDICATOR_COUNT)
    print(f"已选择 {len(selected_indicators)} 个指标")
    
    # 4. 为每个指标生成代码
    print("⚙️ 生成指标代码...")
    generated_count = 0
    failed_indicators = []
    
    for i, indicator in enumerate(selected_indicators, 1):
        try:
            print(f"  [{i}/{len(selected_indicators)}] 生成 {indicator}...")
            
            # 获取TA-Lib函数信息
            info = get_talib_function_info(indicator)
            
            # 生成TradingView指标类
            code = generate_tradingview_indicator_class(info)
            
            # 保存文件
            save_indicator_file(indicator, code)
            
            generated_count += 1
        except Exception as e:
            print(f"  ✗ 生成 {indicator} 失败: {e}")
            failed_indicators.append(indicator)
    
    # 5. 创建初始化文件
    print("📁 创建初始化文件...")
    create_init_file(selected_indicators)
    
    # 6. 创建摘要报告
    print("📋 创建摘要报告...")
    create_summary_report(selected_indicators)
    
    print("=" * 80)
    print(f"✅ 指标生成完成!")
    print(f"   成功生成: {generated_count}/{TARGET_INDICATOR_COUNT}")
    print(f"   失败: {len(failed_indicators)}")
    if failed_indicators:
        print(f"   失败的指标: {failed_indicators}")
    print(f"   输出目录: {OUTPUT_DIR}")
    print("=" * 80)

if __name__ == "__main__":
    main()