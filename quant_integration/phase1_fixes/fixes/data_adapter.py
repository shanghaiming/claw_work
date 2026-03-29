#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据适配器 - 统一数据加载接口
修复quant_trade-main项目的数据加载问题，支持跨平台和可配置路径
"""

import os
import glob
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Union, Tuple
from pathlib import Path
import sys
import warnings
warnings.filterwarnings('ignore')


class DataAdapter:
    """
    数据适配器 - 统一加载量化交易数据
    
    功能:
    1. 替换硬编码的Windows路径
    2. 支持多种数据源配置
    3. 统一数据格式和接口
    4. 跨平台兼容性
    5. 错误处理和日志
    """
    
    # 支持的数据格式
    SUPPORTED_FORMATS = ['csv', 'parquet', 'feather', 'hdf5']
    
    # 必需的数据列（OHLC）
    REQUIRED_OHLC_COLUMNS = {'open', 'high', 'low', 'close'}
    
    # 支持的日期列名
    DATE_COLUMN_NAMES = ['trade_date', 'date', 'datetime', 'time', 'timestamp']
    
    def __init__(self, data_dir: Optional[str] = None, 
                 timeframe: str = "5min",
                 config_file: Optional[str] = None):
        """
        初始化数据适配器
        
        参数:
            data_dir: 数据目录路径（如果为None，则尝试自动检测）
            timeframe: 数据时间周期
            config_file: 配置文件路径
        """
        # 初始化配置
        self.data_dir = data_dir
        self.timeframe = timeframe
        self.config_file = config_file
        
        # 如果没有提供data_dir，尝试自动检测
        if self.data_dir is None:
            self.data_dir = self._auto_detect_data_dir()
        
        # 确保目录存在
        self._ensure_data_directory()
        
        # 缓存已加载的数据
        self._data_cache = {}
    
    def _auto_detect_data_dir(self) -> str:
        """
        自动检测数据目录
        
        尝试以下位置:
        1. 当前目录下的 data/analyzed/{timeframe}
        2. 项目根目录下的 data/analyzed/{timeframe}
        3. 用户主目录下的量化数据目录
        """
        possible_paths = [
            # 当前目录结构
            os.path.join(".", "data", "analyzed", self.timeframe),
            # 项目目录结构（假设在quant_trade-main目录下运行）
            os.path.join(".", "backtest", "data", "analyzed", self.timeframe),
            # 绝对路径（原始Windows路径的跨平台转换）
            self._convert_windows_path(r"E:\stock\backtest\data\analyzed\5min"),
            # 用户主目录
            os.path.expanduser(f"~/stock_data/analyzed/{self.timeframe}"),
        ]
        
        for path in possible_paths:
            abs_path = os.path.abspath(path)
            if os.path.exists(abs_path):
                print(f"自动检测到数据目录: {abs_path}")
                return abs_path
        
        # 如果没有找到，使用默认路径（但会创建目录）
        default_path = os.path.join(".", "data", "analyzed", self.timeframe)
        print(f"警告: 未找到数据目录，使用默认路径: {default_path}")
        return default_path
    
    def _convert_windows_path(self, windows_path: str) -> str:
        """
        将Windows路径转换为当前平台的路径
        
        示例:
            r"E:\stock\backtest\data\analyzed\5min" -> 
            macOS/Linux: "/Volumes/E/stock/backtest/data/analyzed/5min" 或回退路径
        """
        # 如果是Windows绝对路径（如 E:\...）
        if len(windows_path) > 2 and windows_path[1:3] == ":\\":
            drive = windows_path[0]
            
            # 在macOS/Linux上，尝试映射到/Volumes/
            if sys.platform != 'win32':
                # 移除驱动器和反斜杠，替换为正斜杠
                path_without_drive = windows_path[2:].replace('\\', '/')
                # 尝试/Volumes/映射
                possible_paths = [
                    f"/Volumes/{drive}{path_without_drive}",
                    f"/mnt/{drive}{path_without_drive}",
                    os.path.join("/media", drive, path_without_drive.lstrip('/')),
                ]
                
                for path in possible_paths:
                    if os.path.exists(path):
                        return path
            
            # 如果找不到映射，返回一个合理的回退路径
            path_without_drive = windows_path[2:].replace('\\', '/')
            return os.path.join("./windows_drive_mapping", drive.lower(), path_without_drive)
        
        return windows_path.replace('\\', '/')
    
    def _ensure_data_directory(self):
        """确保数据目录存在，如果不存在则创建并添加示例文件"""
        if not os.path.exists(self.data_dir):
            print(f"创建数据目录: {self.data_dir}")
            os.makedirs(self.data_dir, exist_ok=True)
            
            # 创建README文件说明数据格式
            self._create_data_readme()
            
            # 创建示例数据文件
            self._create_example_data()
    
    def _create_data_readme(self):
        """创建数据目录的README文件"""
        readme_path = os.path.join(self.data_dir, "README.md")
        readme_content = f"""# 量化交易数据目录

## 目录结构
```
{self.data_dir}/
├── 000001.SZ.csv     # 股票数据文件（平安银行）
├── 000002.SZ.csv     # 股票数据文件（万科A）
├── 000063.SZ.csv     # 股票数据文件（中兴通讯）
└── ...
```

## 数据格式要求

每个CSV文件必须包含以下列：

### 必需列
- `trade_date`: 交易日期时间（格式: YYYY-MM-DD HH:MM:SS）
- `open`: 开盘价
- `high`: 最高价
- `low`: 最低价
- `close`: 收盘价

### 可选列
- `volume`: 成交量
- `amount`: 成交额
- 各种技术指标列（如macd, rsi, ma5等）

### 文件命名规则
- 格式: `股票代码.csv`
- 示例: `000001.SZ.csv`, `000002.SZ.csv`

## 获取数据

### 方式1: 使用Tushare等数据API
```python
import tushare as ts

# 设置token
ts.set_token('your_token_here')
pro = ts.pro_api()

# 获取5分钟数据
df = pro.ticks('000001.SZ', start_date='2024-01-01', end_date='2024-01-31')
df.to_csv('000001.SZ.csv', index=False)
```

### 方式2: 使用示例数据
本目录已包含示例数据文件，可用于测试回测系统。

## 配置

在运行回测时，可以通过以下方式指定数据目录：

```bash
# 使用默认目录
python main_fixed.py

# 指定数据目录
python main_fixed.py --data-dir ./your_data_directory

# 指定时间周期
python main_fixed.py --timeframe 5min
```
"""
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"已创建README文件: {readme_path}")
    
    def _create_example_data(self):
        """创建示例数据文件（用于测试）"""
        example_symbols = ['000001.SZ', '000002.SZ', '000063.SZ']
        
        for symbol in example_symbols:
            file_path = os.path.join(self.data_dir, f"{symbol}.csv")
            
            if not os.path.exists(file_path):
                df = self._generate_example_data(symbol)
                df.to_csv(file_path, index=False)
                print(f"已创建示例数据文件: {file_path} ({len(df)} 行)")
    
    def _generate_example_data(self, symbol: str, n_days: int = 30) -> pd.DataFrame:
        """生成示例数据"""
        # 生成日期时间序列（假设5分钟数据）
        dates = pd.date_range('2024-01-01', periods=n_days * 48, freq='5min')
        
        # 基础价格（模拟股票走势）
        base_price = 10.0 + np.random.randn() * 2
        
        # 生成价格序列（包含趋势和波动）
        np.random.seed(hash(symbol) % 10000)
        
        # 随机游走生成价格
        returns = np.random.normal(0.0001, 0.01, len(dates))
        price = base_price * np.exp(np.cumsum(returns))
        
        # 生成OHLC数据
        df = pd.DataFrame({
            'trade_date': dates,
            'open': price * (1 + np.random.uniform(-0.002, 0.002, len(dates))),
            'high': price * (1 + np.random.uniform(0, 0.005, len(dates))),
            'low': price * (1 + np.random.uniform(-0.005, 0, len(dates))),
            'close': price,
            'volume': np.random.lognormal(10, 1, len(dates)),
            'symbol': symbol,
        })
        
        # 确保high是最高价，low是最低价
        df['high'] = df[['open', 'high', 'low', 'close']].max(axis=1)
        df['low'] = df[['open', 'high', 'low', 'close']].min(axis=1)
        
        return df
    
    def load_all_stock_data(self, max_files: Optional[int] = None) -> pd.DataFrame:
        """
        加载所有股票数据（替代原main.py中的load_all_stock_data函数）
        
        参数:
            max_files: 最大加载文件数（用于测试）
        
        返回:
            合并后的DataFrame，包含所有股票数据
        """
        print(f"加载数据目录: {self.data_dir}")
        
        # 查找所有CSV文件
        file_pattern = os.path.join(self.data_dir, "*.csv")
        matched_files = glob.glob(file_pattern)
        
        if not matched_files:
            raise FileNotFoundError(f"目录 {self.data_dir} 下没有找到任何CSV文件")
        
        # 限制文件数量（用于测试）
        if max_files and max_files < len(matched_files):
            matched_files = matched_files[:max_files]
            print(f"限制加载 {max_files} 个文件（测试模式）")
        
        print(f"找到 {len(matched_files)} 个股票数据文件")
        
        all_data = []
        loaded_count = 0
        
        for file_path in matched_files:
            try:
                # 从文件名提取股票代码
                filename = os.path.basename(file_path)
                file_symbol = filename.replace('.csv', '')
                
                # 检查缓存
                cache_key = f"{file_symbol}_{self.timeframe}"
                if cache_key in self._data_cache:
                    df_single = self._data_cache[cache_key]
                else:
                    # 读取CSV文件
                    df_single = pd.read_csv(file_path)
                    
                    # 查找日期列
                    date_column = None
                    for col in self.DATE_COLUMN_NAMES:
                        if col in df_single.columns:
                            date_column = col
                            break
                    
                    if date_column is None:
                        # 尝试第一列
                        if len(df_single.columns) > 0:
                            date_column = df_single.columns[0]
                        else:
                            print(f"警告: 文件 {filename} 没有列，跳过")
                            continue
                    
                    # 解析日期列
                    df_single[date_column] = pd.to_datetime(df_single[date_column], errors='coerce')
                    
                    # 验证必需列（OHLC）
                    missing_cols = self.REQUIRED_OHLC_COLUMNS - set(df_single.columns)
                    if missing_cols:
                        print(f"警告: 文件 {filename} 缺少列 {missing_cols}，跳过")
                        continue
                    
                    # 设置索引
                    df_single.set_index(date_column, inplace=True)
                    
                    # 缓存数据
                    self._data_cache[cache_key] = df_single
                
                # 添加股票代码列（如果不存在）
                if 'symbol' not in df_single.columns:
                    df_single = df_single.copy()
                    df_single['symbol'] = file_symbol
                
                # 限制数据量（防止内存问题）
                df_single = df_single.tail(1000)  # 最多1000行
                
                all_data.append(df_single)
                loaded_count += 1
                
                print(f"成功加载: {filename} -> {file_symbol}, 数据行数: {len(df_single)}")
                
            except Exception as e:
                print(f"警告: 加载文件 {file_path} 失败: {e}")
                continue
        
        if not all_data:
            raise ValueError("所有股票文件加载失败")
        
        # 合并所有数据
        combined_data = pd.concat(all_data, ignore_index=False)
        combined_data = combined_data.sort_index()
        
        # 获取股票代码列表
        symbols_clean = combined_data['symbol'].unique().tolist()
        
        print(f"\n数据加载完成:")
        print(f"  成功加载文件: {loaded_count}/{len(matched_files)}")
        print(f"  合并后总数据行数: {len(combined_data)}")
        print(f"  包含股票数量: {len(symbols_clean)}")
        print(f"  股票列表: {symbols_clean[:10]}{'...' if len(symbols_clean) > 10 else ''}")
        print(f"  时间范围: {combined_data.index.min()} 到 {combined_data.index.max()}")
        
        return combined_data
    
    def load_single_stock_data(self, symbol: str, timeframe: Optional[str] = None) -> pd.DataFrame:
        """
        加载单个股票数据（兼容data_loader.py接口）
        
        参数:
            symbol: 股票代码
            timeframe: 时间周期
        
        返回:
            单个股票的DataFrame
        """
        if timeframe is None:
            timeframe = self.timeframe
        
        # 构建文件路径
        file_pattern = os.path.join(self.data_dir, f"{symbol}*.csv")
        matched_files = glob.glob(file_pattern)
        
        # 严格文件数量检查（与data_loader.py一致）
        if len(matched_files) > 1:
            raise ValueError(f"发现多个匹配文件:\n" + "\n".join(matched_files))
        if not matched_files:
            raise FileNotFoundError(f"找不到匹配文件: {symbol}*.csv 在目录 {self.data_dir}")
        
        # 加载数据
        file_path = matched_files[0]
        
        try:
            # 尝试读取CSV文件
            df = pd.read_csv(file_path)
            
            # 查找日期列（支持多种列名）
            date_columns = ['trade_date', 'date', 'datetime', 'time', 'timestamp']
            date_column = None
            
            for col in date_columns:
                if col in df.columns:
                    date_column = col
                    break
            
            if date_column is None:
                # 如果没有找到标准日期列，尝试第一列
                if len(df.columns) > 0:
                    date_column = df.columns[0]
                    print(f"警告: 未找到标准日期列，使用第一列 '{date_column}' 作为日期")
                else:
                    raise ValueError("CSV文件没有列")
            
            # 解析日期列
            df[date_column] = pd.to_datetime(df[date_column], errors='coerce')
            df.set_index(date_column, inplace=True)
            
            # 检查必要列（除了日期列）
            required_ohlc = {'open', 'high', 'low', 'close'}
            missing_cols = required_ohlc - set(df.columns)
            if missing_cols:
                raise ValueError(f"文件 {file_path} 缺少必要列: {missing_cols}")
            
            # 添加symbol列（如果不存在）
            if 'symbol' not in df.columns:
                df = df.copy()
                df['symbol'] = symbol
            
            return df.sort_index()
            
        except Exception as e:
            raise ValueError(f"加载文件 {file_path} 失败: {e}")
    
    def get_available_symbols(self) -> List[str]:
        """获取可用的股票代码列表"""
        file_pattern = os.path.join(self.data_dir, "*.csv")
        matched_files = glob.glob(file_pattern)
        
        symbols = []
        for file_path in matched_files:
            filename = os.path.basename(file_path)
            symbol = filename.replace('.csv', '')
            symbols.append(symbol)
        
        return sorted(symbols)
    
    def validate_data_directory(self) -> Dict[str, Any]:
        """验证数据目录和文件"""
        result = {
            'directory_exists': False,
            'directory_path': self.data_dir,
            'total_files': 0,
            'valid_files': 0,
            'invalid_files': [],
            'available_symbols': [],
            'timeframe': self.timeframe,
        }
        
        # 检查目录是否存在
        if not os.path.exists(self.data_dir):
            return result
        
        result['directory_exists'] = True
        
        # 查找CSV文件
        file_pattern = os.path.join(self.data_dir, "*.csv")
        matched_files = glob.glob(file_pattern)
        result['total_files'] = len(matched_files)
        
        # 验证每个文件
        for file_path in matched_files:
            try:
                filename = os.path.basename(file_path)
                symbol = filename.replace('.csv', '')
                
                # 快速检查文件（只读取前几行）
                df_sample = pd.read_csv(file_path, nrows=5)
                
                # 检查必需列（OHLC）
                missing_cols = self.REQUIRED_OHLC_COLUMNS - set(df_sample.columns)
                if not missing_cols:
                    result['valid_files'] += 1
                    result['available_symbols'].append(symbol)
                else:
                    result['invalid_files'].append({
                        'file': filename,
                        'missing_columns': list(missing_cols)
                    })
                    
            except Exception as e:
                result['invalid_files'].append({
                    'file': os.path.basename(file_path),
                    'error': str(e)
                })
        
        return result
    
    def print_data_summary(self):
        """打印数据目录摘要"""
        validation = self.validate_data_directory()
        
        print("\n" + "="*60)
        print("数据目录摘要")
        print("="*60)
        
        print(f"\n📁 目录信息:")
        print(f"  路径: {validation['directory_path']}")
        print(f"  存在: {'是' if validation['directory_exists'] else '否'}")
        
        if validation['directory_exists']:
            print(f"\n📊 文件统计:")
            print(f"  总文件数: {validation['total_files']}")
            print(f"  有效文件: {validation['valid_files']}")
            print(f"  无效文件: {len(validation['invalid_files'])}")
            
            if validation['valid_files'] > 0:
                print(f"\n📈 可用股票 ({len(validation['available_symbols'])} 只):")
                symbols = validation['available_symbols']
                print(f"  {', '.join(symbols[:10])}{'...' if len(symbols) > 10 else ''}")
            
            if validation['invalid_files']:
                print(f"\n⚠️  无效文件详情:")
                for invalid in validation['invalid_files'][:3]:
                    if 'missing_columns' in invalid:
                        print(f"  {invalid['file']}: 缺少列 {invalid['missing_columns']}")
                    else:
                        print(f"  {invalid['file']}: {invalid['error']}")
                if len(validation['invalid_files']) > 3:
                    print(f"  还有 {len(validation['invalid_files']) - 3} 个无效文件...")
        else:
            print(f"\n❌ 目录不存在，请检查路径或创建目录")
            print(f"  预期路径: {self.data_dir}")
            print(f"  可以通过以下方式创建示例数据:")
            print(f"    adapter = DataAdapter(data_dir='./data/analyzed/5min')")
            print(f"    adapter._create_example_data()")
        
        print("\n" + "="*60)


# 便捷函数
def load_all_stock_data_fixed(data_dir: Optional[str] = None, 
                             timeframe: str = "5min",
                             max_files: Optional[int] = None) -> pd.DataFrame:
    """
    修复版的load_all_stock_data函数（直接替代原函数）
    
    使用示例:
        # 在main.py中替换原来的load_all_stock_data函数
        from data_adapter import load_all_stock_data_fixed as load_all_stock_data
    """
    adapter = DataAdapter(data_dir=data_dir, timeframe=timeframe)
    return adapter.load_all_stock_data(max_files=max_files)


if __name__ == "__main__":
    # 测试数据适配器
    print("测试数据适配器...")
    
    # 创建适配器实例
    adapter = DataAdapter()
    
    # 打印数据摘要
    adapter.print_data_summary()
    
    # 测试加载数据（如果存在）
    validation = adapter.validate_data_directory()
    if validation['valid_files'] > 0:
        print("\n测试数据加载...")
        try:
            data = adapter.load_all_stock_data(max_files=2)  # 只加载2个文件测试
            print(f"成功加载数据，形状: {data.shape}")
            print(f"列名: {list(data.columns)}")
            print(f"索引类型: {type(data.index)}")
        except Exception as e:
            print(f"数据加载失败: {e}")
    else:
        print("\n没有有效数据文件，创建示例数据...")
        adapter._create_example_data()
        adapter.print_data_summary()