#!/usr/bin/env python3
"""
深度IPython Notebook解析器
解析quant_trade-main/csv_version/目录下的所有策略notebook
"""

import json
import os
import re
import sys
from typing import Dict, List, Any, Optional
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class DeepIpynbParser:
    """深度IPython Notebook解析器"""
    
    def __init__(self, notebook_path: str):
        self.notebook_path = notebook_path
        self.notebook_name = os.path.basename(notebook_path)
        self.metadata = {}
        self.code_cells = []
        self.markdown_cells = []
        self.strategy_info = {}
        
    def deep_parse(self) -> Dict[str, Any]:
        """深度解析notebook文件"""
        print(f"🔍 深度解析: {self.notebook_name}")
        
        try:
            with open(self.notebook_path, 'r', encoding='utf-8') as f:
                notebook_data = json.load(f)
        except UnicodeDecodeError:
            try:
                with open(self.notebook_path, 'r', encoding='gbk') as f:
                    notebook_data = json.load(f)
            except:
                print(f"❌ 编码错误: {self.notebook_name}")
                return {}
        except Exception as e:
            print(f"❌ 读取失败 {self.notebook_name}: {e}")
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
        
        # 深度分析策略信息
        self._deep_analyze_strategy()
        
        return self.strategy_info
    
    def _deep_analyze_strategy(self):
        """深度分析策略信息"""
        # 策略类型识别
        name_lower = self.notebook_name.lower()
        
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
            'stdg': '标准差策略',
            'regression': '回归策略',
            'line': '线性分析策略',
            'kline': 'K线模式策略',
            'limit': '涨停板策略',
            'check': '检验策略',
            'test': '测试策略',
            'index': '指数策略',
            'g': 'G策略',
            'comp': '补偿策略',
            'bake': '回测策略'
        }
        
        # 确定策略类型
        strategy_type = '未知策略'
        for key, value in strategy_types.items():
            if key in name_lower:
                strategy_type = value
                break
        
        # 提取详细描述
        description = self._extract_detailed_description()
        
        # 深度参数提取
        parameters = self._deep_extract_parameters()
        
        # 信号逻辑分析
        signal_logic = self._analyze_signal_logic()
        
        # 导入分析
        imports = self._analyze_imports()
        
        # 数据源分析
        data_sources = self._analyze_data_sources()
        
        # 性能指标分析
        performance_metrics = self._analyze_performance_metrics()
        
        self.strategy_info = {
            'notebook_name': self.notebook_name,
            'strategy_type': strategy_type,
            'description': description,
            'parameters': parameters,
            'signal_logic': signal_logic,
            'imports': imports,
            'data_sources': data_sources,
            'performance_metrics': performance_metrics,
            'code_cell_count': len(self.code_cells),
            'markdown_cell_count': len(self.markdown_cells),
            'file_size_kb': os.path.getsize(self.notebook_path) / 1024,
            'analysis_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    
    def _extract_detailed_description(self) -> str:
        """提取详细描述"""
        descriptions = []
        
        for cell in self.markdown_cells:
            source = cell['source'].strip()
            if source and len(source) > 20:  # 有一定长度的markdown
                descriptions.append(source)
        
        # 合并所有描述
        full_description = '\n\n'.join(descriptions)
        
        if len(full_description) > 500:
            return full_description[:500] + '...'
        return full_description if full_description else '无描述'
    
    def _deep_extract_parameters(self) -> Dict[str, Any]:
        """深度提取参数"""
        parameters = {}
        
        all_code = '\n'.join([cell['source'] for cell in self.code_cells])
        
        # 寻找参数定义模式
        param_patterns = [
            # 标准赋值
            (r'(\w+)\s*=\s*(\d+\.?\d*)', 'numeric'),
            (r'(\w+)\s*=\s*["\']([^"\']+)["\']', 'string'),
            (r'(\w+)\s*=\s*(True|False|None)', 'boolean'),
            
            # 窗口/周期参数
            (r'window\s*[=:]\s*(\d+)', 'window'),
            (r'period\s*[=:]\s*(\d+)', 'period'),
            (r'lookback\s*[=:]\s*(\d+)', 'lookback'),
            
            # 阈值参数
            (r'threshold\s*[=:]\s*(\d+\.?\d*)', 'threshold'),
            (r'level\s*[=:]\s*(\d+\.?\d*)', 'level'),
            
            # 移动平均参数
            (r'ma(\d+)\s*=', 'ma'),
            (r'sma(\d+)\s*=', 'sma'),
            (r'ema(\d+)\s*=', 'ema'),
            
            # 其他常见参数
            (r'alpha\s*[=:]\s*(\d+\.?\d*)', 'alpha'),
            (r'beta\s*[=:]\s*(\d+\.?\d*)', 'beta'),
            (r'gamma\s*[=:]\s*(\d+\.?\d*)', 'gamma'),
        ]
        
        for pattern, param_type in param_patterns:
            matches = re.findall(pattern, all_code, re.IGNORECASE)
            for match in matches:
                if isinstance(match, tuple) and len(match) == 2:
                    param_name, param_value = match
                    parameters[param_name] = self._parse_param_value(param_value, param_type)
                elif isinstance(match, str):
                    # 处理单个匹配
                    param_name = param_type
                    parameters[param_name] = self._parse_param_value(match, param_type)
        
        return parameters
    
    def _parse_param_value(self, value: str, param_type: str) -> Any:
        """解析参数值"""
        try:
            if param_type in ['numeric', 'window', 'period', 'lookback', 'threshold', 'level', 'alpha', 'beta', 'gamma']:
                if '.' in value:
                    return float(value)
                else:
                    return int(value)
            elif param_type == 'boolean':
                return value.lower() == 'true'
            else:
                return value
        except:
            return value
    
    def _analyze_signal_logic(self) -> Dict[str, Any]:
        """分析信号逻辑"""
        signal_keywords = {
            'buy': ['buy', 'long', '买入', '做多'],
            'sell': ['sell', 'short', '卖出', '做空'],
            'entry': ['entry', 'enter', '入场', '进场'],
            'exit': ['exit', '离场', '出场'],
            'signal': ['signal', 'sign', '信号'],
            'condition': ['if', 'when', '条件', '满足'],
            'cross': ['cross', 'crossover', '金叉', '死叉'],
            'break': ['break', '突破', '跌破'],
            'position': ['position', '仓位', '持仓']
        }
        
        signal_logic = {
            'buy_conditions': [],
            'sell_conditions': [],
            'entry_rules': [],
            'exit_rules': [],
            'signal_frequency': 0
        }
        
        all_code = '\n'.join([cell['source'] for cell in self.code_cells])
        lines = all_code.split('\n')
        
        for line in lines:
            line_lower = line.lower()
            
            # 检查买入条件
            if any(keyword in line_lower for keyword in signal_keywords['buy']):
                if 'if' in line_lower or 'when' in line_lower:
                    signal_logic['buy_conditions'].append(line.strip())
            
            # 检查卖出条件
            if any(keyword in line_lower for keyword in signal_keywords['sell']):
                if 'if' in line_lower or 'when' in line_lower:
                    signal_logic['sell_conditions'].append(line.strip())
            
            # 检查入场规则
            if any(keyword in line_lower for keyword in signal_keywords['entry']):
                signal_logic['entry_rules'].append(line.strip())
            
            # 检查出场规则
            if any(keyword in line_lower for keyword in signal_keywords['exit']):
                signal_logic['exit_rules'].append(line.strip())
        
        # 统计信号相关行数
        signal_lines = 0
        for line in lines:
            if any(keyword in line.lower() for keyword in sum(signal_keywords.values(), [])):
                signal_lines += 1
        
        signal_logic['signal_frequency'] = signal_lines / len(lines) if lines else 0
        
        # 限制列表长度
        for key in ['buy_conditions', 'sell_conditions', 'entry_rules', 'exit_rules']:
            signal_logic[key] = signal_logic[key][:10]
        
        return signal_logic
    
    def _analyze_imports(self) -> List[str]:
        """分析导入的库"""
        imports = set()
        
        for cell in self.code_cells:
            lines = cell['source'].split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    imports.add(line)
        
        return list(imports)[:20]  # 最多20个
    
    def _analyze_data_sources(self) -> List[str]:
        """分析数据源"""
        data_sources = set()
        
        all_code = '\n'.join([cell['source'] for cell in self.code_cells])
        
        # 常见数据文件模式
        patterns = [
            r'\.csv',
            r'\.xlsx',
            r'\.xls',
            r'\.h5',
            r'\.feather',
            r'\.parquet',
            r'read_csv',
            r'read_excel',
            r'pd\.read_',
            r'数据',
            r'data'
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, all_code, re.IGNORECASE)
            if matches:
                data_sources.add(pattern)
        
        return list(data_sources)
    
    def _analyze_performance_metrics(self) -> List[str]:
        """分析性能指标"""
        metrics = set()
        
        all_code = '\n'.join([cell['source'] for cell in self.code_cells])
        
        performance_keywords = [
            'sharpe', '夏普',
            'return', '收益率',
            'drawdown', '回撤',
            'win_rate', '胜率',
            'profit', '利润',
            'loss', '亏损',
            'ratio', '比率',
            'performance', '绩效',
            'metric', '指标',
            'evaluate', '评估'
        ]
        
        for keyword in performance_keywords:
            if keyword.lower() in all_code.lower():
                metrics.add(keyword)
        
        return list(metrics)
    
    def generate_detailed_adapter(self, output_dir: str):
        """生成详细适配器"""
        strategy_name = self.notebook_name.replace('.ipynb', '').replace('-', '_').replace(' ', '_')
        
        adapter_code = f'''#!/usr/bin/env python3
"""
{self.strategy_info['strategy_type']}详细适配器
基于 {self.notebook_name} 深度解析生成的策略适配器

分析时间: {self.strategy_info['analysis_time']}
策略类型: {self.strategy_info['strategy_type']}
参数数量: {len(self.strategy_info['parameters'])}
信号条件: {len(self.strategy_info['signal_logic']['buy_conditions'])}个买入条件, {len(self.strategy_info['signal_logic']['sell_conditions'])}个卖出条件
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
import warnings
warnings.filterwarnings('ignore')

class {strategy_name.capitalize()}Strategy:
    """{self.strategy_info['strategy_type']}"""
    
    def __init__(self, params: Optional[Dict] = None):
        """初始化策略"""
        self.params = params or {{}}
        
        # 默认参数（从原始notebook提取）
        self.default_params = {json.dumps(self.strategy_info['parameters'], indent=4, ensure_ascii=False)}
        
        # 合并参数
        for key, value in self.default_params.items():
            if key not in self.params:
                self.params[key] = value
        
        print(f"🔧 初始化 {self.strategy_info['strategy_type']}")
        print(f"   参数数量: {{len(self.params)}}")
        
    def generate_signals(self, data: pd.DataFrame) -> List[Dict]:
        """
        生成交易信号
        
        基于原始策略逻辑:
        {json.dumps(self.strategy_info['signal_logic'], indent=4, ensure_ascii=False)}
        """
        signals = []
        
        # TODO: 实现具体的信号生成逻辑
        # 基于 self.strategy_info['signal_logic'] 中的条件
        
        # 示例实现（需要根据实际策略修改）
        if len(data) > 20:
            # 简单移动平均交叉策略示例
            data = data.copy()
            short_window = self.params.get('window', 5)
            long_window = self.params.get('window', 20) * 2  # 假设长周期是短周期的2倍
            
            data['ma_short'] = data['close'].rolling(window=short_window).mean()
            data['ma_long'] = data['close'].rolling(window=long_window).mean()
            
            for i in range(1, len(data)):
                if pd.isna(data['ma_short'].iloc[i]) or pd.isna(data['ma_long'].iloc[i]):
                    continue
                
                timestamp = data.index[i]
                price = data['close'].iloc[i]
                
                # 金叉买入
                prev_short = data['ma_short'].iloc[i-1]
                prev_long = data['ma_long'].iloc[i-1]
                curr_short = data['ma_short'].iloc[i]
                curr_long = data['ma_long'].iloc[i]
                
                if prev_short <= prev_long and curr_short > curr_long:
                    signals.append({{
                        'timestamp': timestamp,
                        'action': 'buy',
                        'price': price,
                        'reason': 'ma_golden_cross',
                        'confidence': 0.6,
                        'source_strategy': '{strategy_name}'
                    }})
                # 死叉卖出
                elif prev_short >= prev_long and curr_short < curr_long:
                    signals.append({{
                        'timestamp': timestamp,
                        'action': 'sell', 
                        'price': price,
                        'reason': 'ma_death_cross',
                        'confidence': 0.6,
                        'source_strategy': '{strategy_name}'
                    }})
        
        print(f"📊 {{self.strategy_info['strategy_type']}} 生成 {{len(signals)}} 个信号")
        return signals
    
    def get_strategy_info(self) -> Dict:
        """获取策略信息"""
        return {{
            'name': '{strategy_name}',
            'type': '{self.strategy_info['strategy_type']}',
            'parameters': self.params,
            'signal_logic_summary': self.strategy_info['signal_logic'],
            'imports_required': self.strategy_info['imports']
        }}

# 测试函数
def test_strategy():
    """测试策略"""
    import os
    
    # 加载测试数据
    data_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/data"
    test_file = os.path.join(data_dir, "daily_data2", "000001.SZ.csv")
    
    if os.path.exists(test_file):
        df = pd.read_csv(test_file)
        df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
        df.sort_values('trade_date', inplace=True)
        df.set_index('trade_date', inplace=True)
        df = df[['open', 'high', 'low', 'close', 'vol']].iloc[:100]
        
        # 创建策略
        strategy = {strategy_name.capitalize()}Strategy()
        signals = strategy.generate_signals(df)
        
        print(f"\\n🧪 策略测试结果:")
        print(f"   数据行数: {{len(df)}}")
        print(f"   生成信号: {{len(signals)}}")
        
        if signals:
            buy_signals = [s for s in signals if s['action'] == 'buy']
            sell_signals = [s for s in signals if s['action'] == 'sell']
            print(f"   买入信号: {{len(buy_signals)}}")
            print(f"   卖出信号: {{len(sell_signals)}}")
    else:
        print("❌ 测试数据不存在")

if __name__ == "__main__":
    test_strategy()
'''
        
        os.makedirs(output_dir, exist_ok=True)
        adapter_path = os.path.join(output_dir, f"{self.notebook_name}_detailed_adapter.py")
        
        with open(adapter_path, 'w', encoding='utf-8') as f:
            f.write(adapter_code)
        
        print(f"💾 详细适配器保存到: {adapter_path}")

def scan_and_parse_all_ipynb(directory_path: str, output_dir: str, max_workers: int = 4):
    """扫描并解析所有ipynb文件"""
    print(f"🔍 开始深度扫描目录: {directory_path}")
    
    # 查找所有ipynb文件
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
    
    print(f"📁 发现 {len(ipynb_files)} 个ipynb文件")
    
    if not ipynb_files:
        return []
    
    # 使用多线程并行解析
    all_strategies = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_file = {}
        
        for file_info in ipynb_files[:20]:  # 先解析前20个
            parser = DeepIpynbParser(file_info['path'])
            future = executor.submit(parser.deep_parse)
            future_to_file[future] = file_info['name']
        
        # 收集结果
        completed = 0
        for future in as_completed(future_to_file):
            filename = future_to_file[future]
            try:
                strategy_info = future.result()
                if strategy_info:
                    all_strategies.append(strategy_info)
                    
                    # 生成详细适配器
                    parser = DeepIpynbParser([f['path'] for f in ipynb_files if f['name'] == filename][0])
                    parser.strategy_info = strategy_info
                    parser.generate_detailed_adapter(output_dir)
                    
                    completed += 1
                    print(f"✅ 完成解析: {filename} ({completed}/{len(future_to_file)})")
            except Exception as e:
                print(f"❌ 解析失败 {filename}: {e}")
    
    return all_strategies

def main():
    """主函数"""
    print("=" * 80)
    print("🔬 深度IPython Notebook解析器")
    print("=" * 80)
    
    ipynb_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/csv_version"
    output_dir = "/Users/chengming/.openclaw/workspace/deep_ipynb_analysis"
    
    if not os.path.exists(ipynb_dir):
        print(f"❌ 目录不存在: {ipynb_dir}")
        return
    
    # 扫描并解析所有ipynb文件
    all_strategies = scan_and_parse_all_ipynb(ipynb_dir, output_dir, max_workers=4)
    
    # 生成汇总报告
    if all_strategies:
        summary = {
            'total_analyzed': len(all_strategies),
            'strategies': all_strategies,
            'strategy_types_summary': {},
            'parameters_summary': {
                'total_parameters': sum(len(s['parameters']) for s in all_strategies),
                'avg_parameters': sum(len(s['parameters']) for s in all_strategies) / len(all_strategies),
                'max_parameters': max(len(s['parameters']) for s in all_strategies),
                'min_parameters': min(len(s['parameters']) for s in all_strategies)
            },
            'signal_logic_summary': {
                'total_buy_conditions': sum(len(s['signal_logic']['buy_conditions']) for s in all_strategies),
                'total_sell_conditions': sum(len(s['signal_logic']['sell_conditions']) for s in all_strategies),
                'avg_signal_frequency': sum(s['signal_logic']['signal_frequency'] for s in all_strategies) / len(all_strategies)
            },
            'analysis_time': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 统计策略类型
        for strategy in all_strategies:
            stype = strategy['strategy_type']
            summary['strategy_types_summary'][stype] = summary['strategy_types_summary'].get(stype, 0) + 1
        
        # 保存汇总报告
        summary_path = os.path.join(output_dir, "deep_analysis_summary.json")
        os.makedirs(os.path.dirname(summary_path), exist_ok=True)
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"\n📈 深度分析汇总:")
        print(f"   分析文件数: {summary['total_analyzed']}")
        print(f"   策略类型分布: {summary['strategy_types_summary']}")
        print(f"   参数统计: 平均{summary['parameters_summary']['avg_parameters']:.1f}个/策略")
        print(f"   信号条件: {summary['signal_logic_summary']['total_buy_conditions']}个买入条件, {summary['signal_logic_summary']['total_sell_conditions']}个卖出条件")
        print(f"   平均信号频率: {summary['signal_logic_summary']['avg_signal_frequency']:.3f}")
        print(f"💾 详细分析报告保存到: {summary_path}")
    
    print("\n" + "=" * 80)
    print("🏁 深度解析完成")

if __name__ == "__main__":
    main()