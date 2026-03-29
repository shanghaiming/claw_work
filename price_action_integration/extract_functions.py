#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
提取ipynb文件中的函数定义
"""

import json
import os
import re


def extract_functions_from_ipynb(ipynb_path):
    """从ipynb文件中提取所有函数定义"""
    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"读取文件失败 {ipynb_path}: {e}")
        return {}
    
    all_functions = {}
    current_function = None
    function_code = []
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source_lines = cell['source']
            if isinstance(source_lines, list):
                source = ''.join(source_lines)
            else:
                source = source_lines
            
            # 按行处理
            lines = source.split('\n')
            
            for line in lines:
                # 检查函数定义
                func_match = re.match(r'^\s*def\s+(\w+)\s*\(', line)
                if func_match:
                    # 保存前一个函数
                    if current_function and function_code:
                        all_functions[current_function] = '\n'.join(function_code)
                    
                    # 开始新函数
                    current_function = func_match.group(1)
                    function_code = [line]
                elif current_function is not None:
                    # 继续收集当前函数的代码
                    function_code.append(line)
                elif line.strip().startswith('class '):
                    # 类定义，暂时不处理
                    pass
    
    # 保存最后一个函数
    if current_function and function_code:
        all_functions[current_function] = '\n'.join(function_code)
    
    return all_functions


def extract_all_code_from_ipynb(ipynb_path):
    """提取ipynb中的所有代码"""
    try:
        with open(ipynb_path, 'r', encoding='utf-8') as f:
            nb = json.load(f)
    except Exception as e:
        print(f"读取文件失败 {ipynb_path}: {e}")
        return ""
    
    all_code = []
    
    for cell in nb['cells']:
        if cell['cell_type'] == 'code':
            source_lines = cell['source']
            if isinstance(source_lines, list):
                source = ''.join(source_lines)
            else:
                source = source_lines
            
            all_code.append(source)
    
    return '\n\n# ============================================\n\n'.join(all_code)


def main():
    """主函数"""
    # 文件路径
    ipynb_files = {
        'spike_bake': '/Users/chengming/downloads/spike_bake.ipynb',
        'ma_compensat': '/Users/chengming/downloads/ma_compensat.ipynb',
        'cluster': '/Users/chengming/downloads/cluster.ipynb',
        'position_energy': '/Users/chengming/downloads/仓位势能分析.ipynb',
        'stategy_momentum': '/Users/chengming/downloads/quant_trade-main/csv_version/stategy_momentum.ipynb',
        'price_volume': '/Users/chengming/downloads/quant_trade-main/csv_version/price_vol_int.ipynb'
    }
    
    # 创建输出目录
    output_dir = 'extracted_modules'
    os.makedirs(output_dir, exist_ok=True)
    
    print("开始提取ipynb文件中的函数...")
    print("=" * 60)
    
    for name, path in ipynb_files.items():
        print(f"\n处理: {name}")
        
        if not os.path.exists(path):
            print(f"  文件不存在: {path}")
            continue
        
        try:
            # 提取所有代码
            all_code = extract_all_code_from_ipynb(path)
            
            # 提取函数
            functions = extract_functions_from_ipynb(path)
            
            # 保存所有代码
            code_filename = os.path.join(output_dir, f"{name}_all_code.py")
            with open(code_filename, 'w', encoding='utf-8') as f:
                f.write(f"# 从 {name}.ipynb 提取的完整代码\n")
                f.write("#" * 80 + "\n\n")
                f.write(all_code)
            
            print(f"  保存完整代码到: {code_filename}")
            print(f"  提取到 {len(functions)} 个函数")
            
            # 打印函数名
            for func_name in sorted(functions.keys()):
                print(f"    - {func_name}")
            
            # 保存函数定义
            if functions:
                func_filename = os.path.join(output_dir, f"{name}_functions.py")
                with open(func_filename, 'w', encoding='utf-8') as f:
                    f.write(f"# 从 {name}.ipynb 提取的函数定义\n")
                    f.write("#" * 80 + "\n\n")
                    f.write("import numpy as np\n")
                    f.write("import pandas as pd\n")
                    f.write("import matplotlib.pyplot as plt\n")
                    f.write("\n\n")
                    
                    for func_name, func_code in functions.items():
                        f.write(f"# {'='*60}\n")
                        f.write(f"# {func_name}\n")
                        f.write(f"# {'='*60}\n")
                        f.write(func_code)
                        f.write("\n\n")
                
                print(f"  保存函数定义到: {func_filename}")
            
        except Exception as e:
            print(f"  处理失败: {e}")
    
    print("\n" + "=" * 60)
    print("提取完成！")


if __name__ == "__main__":
    main()