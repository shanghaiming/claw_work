#!/usr/bin/env python3
"""
IPython Notebook解析器
解析quant_trade-main/csv_version/目录下的策略notebook
提取策略逻辑、参数、信号生成代码
"""

import json
import os
import re
from typing import Dict, List, Any, Optional
import pandas as pd

class IpynbParser:
    """IPython Notebook解析器"""
    
    def __init__(self, notebook_path: str):
        self.notebook_path = notebook_path
        self.notebook_name = os.path.basename(notebook_path)
        self.metadata = {}
        self.code_cells = []
        self.markdown_cells = []
        self.strategy_info = {}
        
    def parse(self) -> Dict[str, Any]:
        """解析notebook文件"""
        print(f"📖 解析notebook: {self.notebook_name}")
        
        try:
            with open(self.notebook_path, 'r', encoding='utf-8') as f:
                notebook_data = json.load(f)
        except UnicodeDecodeError:
            with open(self.notebook_path, 'r', encoding='gbk') as f:
                notebook_data = json.load(f)
        except Exception as e:
            print(f"❌ 读取文件失败: {e}")
            return {}
        
        # 提取元数据
        self.metadata = notebook_data.get('metadata', {})
        
        # 解析单元格
        cells = notebook_data.get('cells', [])
        
        for i, cell in enumerate(cells):
            cell_type = cell.get('cell_type', '')
            source = ''.join(cell.get('source', []))
            
            if cell_type == 'code':
                self.code_cells.append({
                    'index': i,
                    'source': source,
                    'outputs': cell.get('outputs', [])
                })
            elif cell_type == 'markdown':
                self.markdown_cells.append({
                    'index': i,
                    'source': source
                })
        
        print(f"   发现 {len(self.code_cells)} 个代码单元格")
        print(f"   发现 {len(self.markdown_cells)} 个markdown单元格")
        
        # 分析策略信息
        self._analyze_strategy()
        
        return self.strategy_info
    
    def _analyze_strategy(self):
        """分析策略信息"""
        # 从文件名推测策略类型
        name_lower = self.notebook_name.lower()
        
        # 策略类型映射
        strategy_types = {
            'cluster': '聚类分析策略',
            'ma_compensat': '补偿移动平均策略',
            'frama': 'FRAMA自适应移动平均策略',
            'fft': '傅里叶变换策略',
            'price_vol': '价量分析策略',
            'momentum': '动量策略',
            'future': '期货策略',
            'rectangle': '矩形整理策略',
            'spike': '尖峰回调策略',
            'stdg': '标准差策略'
        }
        
        # 确定策略类型
        strategy_type = '未知策略'
        for key, value in strategy_types.items():
            if key in name_lower:
                strategy_type = value
                break
        
        # 从markdown单元格提取描述
        description = ''
        for cell in self.markdown_cells:
            source = cell['source']
            if source and len(source) > 50:  # 取第一个较长的markdown作为描述
                description = source[:200] + '...' if len(source) > 200 else source
                break
        
        # 分析代码单元格，寻找策略参数和信号生成
        parameters = self._extract_parameters()
        signal_code = self._extract_signal_code()
        
        self.strategy_info = {
            'notebook_name': self.notebook_name,
            'strategy_type': strategy_type,
            'description': description,
            'parameters': parameters,
            'signal_code_snippets': signal_code,
            'code_cell_count': len(self.code_cells),
            'markdown_cell_count': len(self.markdown_cells),
            'file_size_kb': os.path.getsize(self.notebook_path) / 1024
        }
    
    def _extract_parameters(self) -> Dict[str, Any]:
        """提取策略参数"""
        parameters = {}
        
        # 常见参数模式
        param_patterns = [
            r'(\w+)\s*=\s*(\d+\.?\d*)',  # 参数赋值
            r'window\s*=\s*(\d+)',  # 窗口参数
            r'period\s*=\s*(\d+)',  # 周期参数
            r'threshold\s*=\s*(\d+\.?\d*)',  # 阈值参数
            r'ma(\d+)\s*=',  # 移动平均参数
        ]
        
        all_code = '\n'.join([cell['source'] for cell in self.code_cells])
        
        # 寻找明显的参数定义
        lines = all_code.split('\n')
        for line in lines:
            line = line.strip()
            # 跳过注释和空行
            if not line or line.startswith('#') or line.startswith('//'):
                continue
            
            # 检查常见参数模式
            for pattern in param_patterns:
                matches = re.findall(pattern, line)
                for match in matches:
                    if isinstance(match, tuple) and len(match) == 2:
                        param_name, param_value = match
                        try:
                            # 尝试转换数值
                            if '.' in param_value:
                                parameters[param_name] = float(param_value)
                            else:
                                parameters[param_name] = int(param_value)
                        except:
                            parameters[param_name] = param_value
                    elif isinstance(match, str):
                        # 对于单个匹配的情况（如window=20）
                        if 'window' in line.lower():
                            value = re.findall(r'=\s*(\d+)', line)
                            if value:
                                parameters['window'] = int(value[0])
        
        return parameters
    
    def _extract_signal_code(self) -> List[str]:
        """提取信号生成代码片段"""
        signal_keywords = [
            'buy', 'sell', 'signal', 'entry', 'exit',
            'long', 'short', 'position', 'trade',
            'cross', 'break', '突破', '买入', '卖出'
        ]
        
        signal_snippets = []
        
        for cell in self.code_cells:
            source = cell['source'].lower()
            # 检查是否包含信号相关关键词
            if any(keyword in source for keyword in signal_keywords):
                # 提取相关行
                lines = cell['source'].split('\n')
                relevant_lines = []
                for line in lines:
                    line_lower = line.lower()
                    if any(keyword in line_lower for keyword in signal_keywords):
                        relevant_lines.append(line.strip())
                
                if relevant_lines:
                    snippet = '\n'.join(relevant_lines[:10])  # 最多10行
                    if len(snippet) > 50:  # 只保留有内容的片段
                        signal_snippets.append(snippet)
        
        return signal_snippets[:5]  # 最多返回5个片段
    
    def generate_strategy_adapter(self) -> str:
        """生成策略适配器代码模板"""
        strategy_name = self.notebook_name.replace('.ipynb', '').replace('-', '_').replace(' ', '_')
        
        template = f'''#!/usr/bin/env python3
"""
{self.strategy_info['strategy_type']}适配器
基于 {self.notebook_name} 生成的策略适配器
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any

class {strategy_name.capitalize()}Strategy:
    """{self.strategy_info['strategy_type']}"""
    
    def __init__(self, params: Dict):
        """初始化策略"""
        self.params = params
        # 从解析的参数设置默认值
        default_params = {json.dumps(self.strategy_info['parameters'], indent=2)}
        for key, value in default_params.items():
            if key not in self.params:
                self.params[key] = value
        
    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """生成交易信号"""
        # 这里需要实现具体的信号生成逻辑
        # 基于原始notebook中的代码
        
        signals = []
        
        # 示例信号生成逻辑（需要根据实际策略修改）
        # if some_condition:
        #     signals.append({{
        #         'timestamp': data.index[i],
        #         'action': 'buy',
        #         'price': data['close'].iloc[i],
        #         'reason': 'strategy_signal'
        #     }})
        
        return signals
'''

        return template
    
    def save_analysis_report(self, output_dir: str):
        """保存分析报告"""
        os.makedirs(output_dir, exist_ok=True)
        
        report_path = os.path.join(output_dir, f"{self.notebook_name}_analysis.json")
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.strategy_info, f, ensure_ascii=False, indent=2)
        
        print(f"💾 分析报告保存到: {report_path}")
        
        # 同时保存适配器模板
        adapter_template = self.generate_strategy_adapter()
        adapter_path = os.path.join(output_dir, f"{self.notebook_name}_adapter.py")
        
        with open(adapter_path, 'w', encoding='utf-8') as f:
            f.write(adapter_template)
        
        print(f"💾 适配器模板保存到: {adapter_path}")

def scan_ipynb_directory(directory_path: str) -> List[Dict[str, Any]]:
    """扫描目录下的所有ipynb文件"""
    print(f"🔍 扫描目录: {directory_path}")
    
    ipynb_files = []
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.endswith('.ipynb'):
                full_path = os.path.join(root, file)
                ipynb_files.append({
                    'path': full_path,
                    'name': file,
                    'size_kb': os.path.getsize(full_path) / 1024
                })
    
    print(f"   发现 {len(ipynb_files)} 个ipynb文件")
    return ipynb_files

def main():
    """主函数"""
    print("=" * 80)
    print("📚 IPython Notebook策略解析器")
    print("=" * 80)
    
    # 扫描目录
    ipynb_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/csv_version"
    output_dir = "/Users/chengming/.openclaw/workspace/ipynb_analysis_results"
    
    ipynb_files = scan_ipynb_directory(ipynb_dir)
    
    # 解析前几个文件作为示例
    sample_files = ipynb_files[:5]  # 先解析5个作为示例
    
    all_strategies = []
    
    for file_info in sample_files:
        print(f"\n{'='*60}")
        
        parser = IpynbParser(file_info['path'])
        strategy_info = parser.parse()
        
        if strategy_info:
            all_strategies.append(strategy_info)
            
            # 显示摘要信息
            print(f"📊 策略摘要:")
            print(f"   名称: {strategy_info['notebook_name']}")
            print(f"   类型: {strategy_info['strategy_type']}")
            print(f"   参数: {len(strategy_info['parameters'])} 个")
            print(f"   信号代码片段: {len(strategy_info['signal_code_snippets'])} 个")
            
            # 保存分析结果
            parser.save_analysis_report(output_dir)
    
    # 生成汇总报告
    if all_strategies:
        summary = {
            'total_analyzed': len(all_strategies),
            'strategies': all_strategies,
            'strategy_types': {},
            'average_parameters': sum(len(s['parameters']) for s in all_strategies) / len(all_strategies)
        }
        
        # 统计策略类型
        for strategy in all_strategies:
            stype = strategy['strategy_type']
            summary['strategy_types'][stype] = summary['strategy_types'].get(stype, 0) + 1
        
        summary_path = os.path.join(output_dir, "analysis_summary.json")
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n📈 分析汇总:")
        print(f"   分析文件数: {summary['total_analyzed']}")
        print(f"   策略类型分布: {summary['strategy_types']}")
        print(f"   平均参数数量: {summary['average_parameters']:.1f}")
        print(f"💾 汇总报告保存到: {summary_path}")
    
    print("\n" + "=" * 80)
    print("🏁 解析完成")

if __name__ == "__main__":
    main()