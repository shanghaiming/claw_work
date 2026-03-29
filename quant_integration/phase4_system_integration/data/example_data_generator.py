#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
示例数据生成器 - 生成测试数据用于系统开发和测试

功能:
1. 生成模拟股票数据
2. 创建技术指标特征
3. 保存为多种格式
4. 与统一数据管理器兼容
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')


class ExampleDataGenerator:
    """示例数据生成器"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化示例数据生成器
        
        参数:
            base_dir: 数据保存目录，如果为None则使用默认目录
        """
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            self.base_dir = Path(__file__).parent / 'example_data'
        
        self.base_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 示例数据生成器初始化: {self.base_dir}")
    
    def generate_stock_data(self, symbol: str, days: int = 365, 
                          start_price: float = 100.0, 
                          volatility: float = 0.02,
                          trend: float = 0.0001) -> pd.DataFrame:
        """
        生成模拟股票数据
        
        参数:
            symbol: 股票代码
            days: 生成的天数
            start_price: 起始价格
            volatility: 波动率
            trend: 趋势 (每日平均涨幅)
        
        返回:
            DataFrame包含OHLCV数据
        """
        print(f"生成{symbol}模拟数据: {days}天, 起始价{start_price}, 波动率{volatility}, 趋势{trend}")
        
        # 生成日期范围
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        dates = pd.date_range(start=start_date, end=end_date, freq='D')
        
        # 生成价格序列 (几何布朗运动)
        n = len(dates)
        dt = 1 / 252  # 假设252个交易日
        
        # 随机游走
        random_shocks = np.random.randn(n) * volatility * np.sqrt(dt)
        drift = trend * dt
        returns = drift + random_shocks
        
        # 价格序列
        price_series = start_price * np.exp(np.cumsum(returns))
        
        # 生成OHLC数据
        data = []
        for i in range(n):
            base_price = price_series[i]
            
            # 日内波动
            intraday_vol = volatility * 0.5  # 日内波动小于日间波动
            open_price = base_price * (1 + np.random.randn() * intraday_vol * 0.1)
            high_price = open_price * (1 + abs(np.random.randn()) * intraday_vol * 0.3)
            low_price = open_price * (1 - abs(np.random.randn()) * intraday_vol * 0.3)
            close_price = base_price * (1 + np.random.randn() * intraday_vol * 0.2)
            
            # 确保价格合理性
            high_price = max(open_price, close_price, high_price)
            low_price = min(open_price, close_price, low_price)
            
            # 成交量 (与价格变化相关)
            price_change = abs(close_price - open_price) / open_price
            volume = np.random.randint(10000, 1000000) * (1 + price_change * 10)
            
            data.append({
                'date': dates[i],
                'symbol': symbol,
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': int(volume),
                'amount': round(close_price * volume, 2)
            })
        
        df = pd.DataFrame(data)
        df.set_index('date', inplace=True)
        df.sort_index(inplace=True)
        
        print(f"生成完成: {len(df)} 行, 价格范围: {df['close'].min():.2f}-{df['close'].max():.2f}")
        return df
    
    def generate_multiple_stocks(self, symbols: List[str], **kwargs) -> Dict[str, pd.DataFrame]:
        """
        生成多个股票的数据
        
        参数:
            symbols: 股票代码列表
            **kwargs: 传递给generate_stock_data的参数
        
        返回:
            字典 {symbol: DataFrame}
        """
        results = {}
        
        for i, symbol in enumerate(symbols):
            # 为每个股票设置不同的参数
            start_price = 100.0 + i * 10  # 不同起始价
            volatility = 0.015 + i * 0.005  # 不同波动率
            trend = 0.00005 * (1 if i % 2 == 0 else -1)  # 不同趋势方向
            
            df = self.generate_stock_data(
                symbol=symbol,
                start_price=start_price,
                volatility=volatility,
                trend=trend,
                **kwargs
            )
            results[symbol] = df
        
        print(f"生成 {len(results)} 个股票数据完成")
        return results
    
    def add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加技术指标 (与数据预处理器兼容)
        
        参数:
            df: 原始OHLCV数据
        
        返回:
            添加技术指标后的DataFrame
        """
        df_processed = df.copy()
        
        # 基本指标
        df_processed['price_change'] = df_processed['close'].diff()
        df_processed['price_change_pct'] = df_processed['close'].pct_change() * 100
        df_processed['price_range'] = df_processed['high'] - df_processed['low']
        df_processed['price_range_pct'] = df_processed['price_range'] / df_processed['low'] * 100
        
        # 移动平均线
        for window in [5, 10, 20, 30, 50]:
            df_processed[f'ma_{window}'] = df_processed['close'].rolling(window=window, min_periods=1).mean()
        
        # 成交量指标
        if 'volume' in df_processed.columns:
            for window in [5, 10, 20]:
                df_processed[f'volume_ma_{window}'] = df_processed['volume'].rolling(window=window, min_periods=1).mean()
            df_processed['volume_ratio'] = df_processed['volume'] / df_processed['volume'].rolling(window=20, min_periods=1).mean()
        
        # 趋势指标
        if 'ma_5' in df_processed.columns and 'ma_20' in df_processed.columns:
            df_processed['ma_diff_5_20'] = df_processed['ma_5'] - df_processed['ma_20']
            df_processed['ma_diff_pct_5_20'] = df_processed['ma_diff_5_20'] / df_processed['ma_20'] * 100
        
        # 波动率指标
        if 'price_change_pct' in df_processed.columns:
            for window in [5, 10, 20]:
                df_processed[f'volatility_{window}'] = df_processed['price_change_pct'].rolling(window=window).std()
        
        # 动量指标 (简化RSI)
        if 'price_change' in df_processed.columns:
            gains = df_processed['price_change'].where(df_processed['price_change'] > 0, 0)
            losses = -df_processed['price_change'].where(df_processed['price_change'] < 0, 0)
            avg_gain = gains.rolling(window=14).mean()
            avg_loss = losses.rolling(window=14).mean()
            rs = avg_gain / avg_loss.replace(0, 1)
            df_processed['rsi_14'] = 100 - (100 / (1 + rs))
        
        print(f"技术指标添加完成: {len(df_processed.columns)} 列")
        return df_processed
    
    def save_data(self, df: pd.DataFrame, symbol: str, 
                 formats: List[str] = None, overwrite: bool = True):
        """
        保存数据到文件
        
        参数:
            df: 要保存的DataFrame
            symbol: 股票代码 (用于文件名)
            formats: 保存格式列表 ['csv', 'parquet', 'feather']
            overwrite: 是否覆盖已存在文件
        """
        if formats is None:
            formats = ['csv', 'parquet']
        
        saved_files = []
        
        for file_format in formats:
            file_path = self.base_dir / f"{symbol}.{file_format}"
            
            # 检查文件是否存在
            if file_path.exists() and not overwrite:
                print(f"文件已存在，跳过: {file_path}")
                continue
            
            try:
                if file_format == 'csv':
                    df.to_csv(file_path)
                elif file_format == 'parquet':
                    df.to_parquet(file_path)
                elif file_format == 'feather':
                    df.reset_index().to_feather(file_path)  # feather需要重置索引
                else:
                    print(f"不支持的格式: {file_format}")
                    continue
                
                saved_files.append(file_path)
                print(f"✅ 保存 {symbol} 数据: {file_path} ({len(df)} 行)")
                
            except Exception as e:
                print(f"❌ 保存 {symbol} 到 {file_format} 失败: {e}")
        
        return saved_files
    
    def generate_and_save_example_dataset(self, num_stocks: int = 10, 
                                        days_per_stock: int = 365):
        """
        生成并保存示例数据集
        
        参数:
            num_stocks: 股票数量
            days_per_stock: 每个股票的天数
        """
        # 生成股票代码
        symbols = [f"TEST{i:03d}.SZ" for i in range(1, num_stocks + 1)]
        
        print(f"开始生成示例数据集: {num_stocks} 个股票, 各 {days_per_stock} 天")
        print(f"保存目录: {self.base_dir}")
        
        # 生成数据
        all_data = self.generate_multiple_stocks(
            symbols=symbols,
            days=days_per_stock
        )
        
        # 保存数据
        total_rows = 0
        saved_files = []
        
        for symbol, df in all_data.items():
            # 添加技术指标
            df_with_indicators = self.add_technical_indicators(df)
            
            # 保存
            files = self.save_data(df_with_indicators, symbol)
            saved_files.extend(files)
            total_rows += len(df)
        
        # 创建数据集信息文件
        info_file = self.base_dir / 'dataset_info.json'
        info = {
            'generated_at': datetime.now().isoformat(),
            'num_stocks': num_stocks,
            'days_per_stock': days_per_stock,
            'total_rows': total_rows,
            'symbols': symbols,
            'saved_files': [str(f) for f in saved_files],
            'data_columns': list(df_with_indicators.columns) if len(all_data) > 0 else []
        }
        
        import json
        with open(info_file, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"\n🎉 示例数据集生成完成:")
        print(f"  股票数量: {num_stocks}")
        print(f"  总数据行数: {total_rows}")
        print(f"  保存文件: {len(saved_files)} 个")
        print(f"  信息文件: {info_file}")
        
        return all_data, info


# ========== 使用示例 ==========

def example_usage():
    """使用示例"""
    print("="*60)
    print("示例数据生成器使用示例")
    print("="*60)
    
    # 创建生成器
    generator = ExampleDataGenerator()
    
    # 示例1: 生成单个股票数据
    print("\n1. 生成单个股票数据:")
    df_single = generator.generate_stock_data(
        symbol="TEST001.SZ",
        days=100,
        start_price=50.0,
        volatility=0.015,
        trend=0.0002
    )
    
    print(f"生成数据: {len(df_single)} 行")
    print(f"列: {list(df_single.columns)}")
    print(f"日期范围: {df_single.index.min()} 到 {df_single.index.max()}")
    print(f"价格范围: {df_single['close'].min():.2f} - {df_single['close'].max():.2f}")
    
    # 示例2: 添加技术指标
    print("\n2. 添加技术指标:")
    df_with_indicators = generator.add_technical_indicators(df_single)
    print(f"原始列数: {len(df_single.columns)}")
    print(f"处理后列数: {len(df_with_indicators.columns)}")
    print(f"新增技术指标: {[c for c in df_with_indicators.columns if c not in df_single.columns][:10]}...")
    
    # 示例3: 保存数据
    print("\n3. 保存数据:")
    saved_files = generator.save_data(df_with_indicators, "TEST001.SZ")
    print(f"保存的文件: {saved_files}")
    
    # 示例4: 生成完整示例数据集
    print("\n4. 生成完整示例数据集:")
    all_data, info = generator.generate_and_save_example_dataset(
        num_stocks=5,  # 少量股票用于测试
        days_per_stock=50
    )
    
    print(f"数据集信息:")
    print(f"  生成时间: {info['generated_at']}")
    print(f"  股票数量: {info['num_stocks']}")
    print(f"  总行数: {info['total_rows']}")
    
    # 示例5: 验证数据可加载性
    print("\n5. 验证数据可加载性:")
    try:
        # 尝试加载保存的数据
        for symbol in info['symbols'][:2]:  # 只测试前2个
            csv_path = generator.base_dir / f"{symbol}.csv"
            if csv_path.exists():
                df_loaded = pd.read_csv(csv_path, index_col='date', parse_dates=True)
                print(f"  ✅ {symbol}: 加载成功, {len(df_loaded)} 行, {len(df_loaded.columns)} 列")
            else:
                print(f"  ⚠️ {symbol}: CSV文件不存在")
    except Exception as e:
        print(f"  验证失败: {e}")
    
    print(f"\n✅ 示例数据生成器测试完成")
    print(f"数据目录: {generator.base_dir}")


if __name__ == "__main__":
    example_usage()