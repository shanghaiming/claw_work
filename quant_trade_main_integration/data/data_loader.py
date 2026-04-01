#!/usr/bin/env python3
"""
数据加载模块 - 统一数据加载和处理
基于simple_backtest.py的数据功能扩展
"""

import os
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Union, Any
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DataLoader:
    """
    数据加载器 - 加载和预处理市场数据
    """
    
    def __init__(self, base_data_path: Optional[str] = None):
        """
        初始化数据加载器
        
        Args:
            base_data_path: 基础数据路径，默认为quant_trade-main/data/
        """
        if base_data_path is None:
            # 默认使用quant_trade-main数据目录
            self.base_data_path = "/Users/chengming/.openclaw/workspace/quant_trade-main/data"
        else:
            self.base_data_path = base_data_path
        
        # 数据缓存
        self.data_cache = {}
        logger.info(f"数据加载器初始化，基础路径: {self.base_data_path}")
    
    def load_csv(self, file_path: str, date_col: str = 'date', 
                 parse_dates: bool = True, index_col: Optional[str] = None,
                 **kwargs) -> pd.DataFrame:
        """
        加载CSV文件
        
        Args:
            file_path: CSV文件路径
            date_col: 日期列名
            parse_dates: 是否解析日期
            index_col: 索引列名
            **kwargs: pandas.read_csv参数
            
        Returns:
            数据DataFrame
        """
        try:
            logger.info(f"加载CSV文件: {file_path}")
            
            # 读取CSV
            df = pd.read_csv(file_path, **kwargs)
            
            # 解析日期
            if parse_dates and date_col in df.columns:
                df[date_col] = pd.to_datetime(df[date_col])
                if index_col is None:
                    df.set_index(date_col, inplace=True)
            
            # 设置索引
            if index_col and index_col in df.columns:
                df.set_index(index_col, inplace=True)
            
            # 标准化列名（小写）
            df.columns = [col.lower().strip() for col in df.columns]
            
            # 确保必要的列存在
            required_cols = ['open', 'high', 'low', 'close', 'volume']
            missing_cols = [col for col in required_cols if col not in df.columns]
            if missing_cols:
                logger.warning(f"CSV文件缺少必要列: {missing_cols}")
            
            logger.info(f"CSV加载成功: {file_path}, 形状: {df.shape}")
            return df
            
        except Exception as e:
            logger.error(f"加载CSV文件失败 {file_path}: {e}")
            raise
    
    def load_stock_data(self, stock_code: str, data_type: str = 'daily', 
                       start_date: Optional[str] = None,
                       end_date: Optional[str] = None) -> pd.DataFrame:
        """
        加载股票数据
        
        Args:
            stock_code: 股票代码，如 '000001.SZ'
            data_type: 数据类型，'daily'（日线）、'week'（周线）、'30min'、'5min'
            start_date: 开始日期，格式 'YYYY-MM-DD'
            end_date: 结束日期，格式 'YYYY-MM-DD'
            
        Returns:
            股票数据DataFrame
        """
        # 构建文件路径
        data_dir_map = {
            'daily': 'daily_data2',
            'week': 'week_data2', 
            '30min': '30min',
            '5min': '5min'
        }
        
        if data_type not in data_dir_map:
            raise ValueError(f"不支持的数据类型: {data_type}，可用类型: {list(data_dir_map.keys())}")
        
        data_dir = data_dir_map[data_type]
        file_path = os.path.join(self.base_data_path, data_dir, f"{stock_code}.csv")
        
        if not os.path.exists(file_path):
            # 尝试查找类似文件
            logger.warning(f"数据文件不存在: {file_path}")
            # 查找目录下的所有CSV文件
            dir_path = os.path.join(self.base_data_path, data_dir)
            if os.path.exists(dir_path):
                csv_files = [f for f in os.listdir(dir_path) if f.endswith('.csv')]
                logger.info(f"目录 {dir_path} 中的CSV文件: {csv_files[:5]}")
            
            # 使用测试数据
            return self._create_test_data(stock_code, data_type)
        
        # 加载数据
        df = self.load_csv(file_path)
        
        # 日期过滤
        if start_date:
            start_date = pd.to_datetime(start_date)
            df = df[df.index >= start_date]
        
        if end_date:
            end_date = pd.to_datetime(end_date)
            df = df[df.index <= end_date]
        
        # 缓存数据
        cache_key = f"{stock_code}_{data_type}"
        self.data_cache[cache_key] = df
        
        logger.info(f"股票数据加载成功: {stock_code} ({data_type}), 形状: {df.shape}, "
                   f"时间范围: {df.index.min()} 到 {df.index.max()}")
        
        return df
    
    def _create_test_data(self, stock_code: str, data_type: str, 
                         days: int = 500) -> pd.DataFrame:
        """
        创建测试数据（当实际数据不可用时）
        
        Args:
            stock_code: 股票代码
            data_type: 数据类型
            days: 数据天数
            
        Returns:
            测试数据DataFrame
        """
        logger.info(f"创建测试数据: {stock_code} ({data_type})")
        
        # 生成日期
        if data_type == 'daily':
            freq = 'D'
        elif data_type == 'week':
            freq = 'W'
        elif data_type == '30min':
            freq = '30min'
            days = days * 16  # 每天16个30分钟
        elif data_type == '5min':
            freq = '5min'
            days = days * 78  # 每天78个5分钟
        else:
            freq = 'D'
        
        dates = pd.date_range(end=pd.Timestamp.now(), periods=days, freq=freq)
        
        # 生成随机价格数据（随机游走）
        np.random.seed(hash(stock_code) % 10000)
        returns = np.random.randn(len(dates)) * 0.02  # 2%日波动
        prices = 100 * np.exp(np.cumsum(returns))  # 从100开始
        
        # 生成OHLCV数据
        df = pd.DataFrame(index=dates)
        df['open'] = prices * (1 + np.random.randn(len(dates)) * 0.005)
        df['high'] = df['open'] * (1 + np.abs(np.random.randn(len(dates)) * 0.01))
        df['low'] = df['open'] * (1 - np.abs(np.random.randn(len(dates)) * 0.01))
        df['close'] = prices
        df['volume'] = np.random.randint(10000, 1000000, len(dates))
        
        # 确保high >= low, high >= open, high >= close, etc.
        df['high'] = df[['open', 'high', 'close']].max(axis=1)
        df['low'] = df[['open', 'low', 'close']].min(axis=1)
        
        logger.info(f"测试数据创建完成: {stock_code}, 形状: {df.shape}")
        return df
    
    def load_multiple_stocks(self, stock_codes: List[str], data_type: str = 'daily',
                           start_date: Optional[str] = None,
                           end_date: Optional[str] = None) -> Dict[str, pd.DataFrame]:
        """
        加载多个股票数据
        
        Args:
            stock_codes: 股票代码列表
            data_type: 数据类型
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            股票数据字典，键为股票代码，值为DataFrame
        """
        stock_data = {}
        
        for stock_code in stock_codes:
            try:
                df = self.load_stock_data(stock_code, data_type, start_date, end_date)
                stock_data[stock_code] = df
                logger.info(f"加载股票 {stock_code} 完成，数据点: {len(df)}")
            except Exception as e:
                logger.error(f"加载股票 {stock_code} 失败: {e}")
        
        return stock_data
    
    def preprocess_data(self, df: pd.DataFrame, 
                       fill_method: str = 'ffill',
                       add_technical_indicators: bool = True) -> pd.DataFrame:
        """
        预处理数据
        
        Args:
            df: 原始数据DataFrame
            fill_method: 缺失值填充方法
            add_technical_indicators: 是否添加技术指标
            
        Returns:
            预处理后的DataFrame
        """
        df_processed = df.copy()
        
        # 处理缺失值
        if df_processed.isnull().any().any():
            logger.info(f"处理缺失值，方法: {fill_method}")
            if fill_method == 'ffill':
                df_processed = df_processed.fillna(method='ffill')
            elif fill_method == 'bfill':
                df_processed = df_processed.fillna(method='bfill')
            else:
                df_processed = df_processed.fillna(method='ffill').fillna(method='bfill')
        
        # 添加技术指标
        if add_technical_indicators:
            df_processed = self._add_technical_indicators(df_processed)
        
        return df_processed
    
    def _add_technical_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        添加技术指标
        
        Args:
            df: 数据DataFrame
            
        Returns:
            添加技术指标后的DataFrame
        """
        df_ind = df.copy()
        
        # 移动平均
        for window in [5, 10, 20, 50, 100, 200]:
            df_ind[f'ma_{window}'] = df_ind['close'].rolling(window=window).mean()
        
        # 指数移动平均
        for window in [12, 26]:
            df_ind[f'ema_{window}'] = df_ind['close'].ewm(span=window, adjust=False).mean()
        
        # MACD
        ema_12 = df_ind['close'].ewm(span=12, adjust=False).mean()
        ema_26 = df_ind['close'].ewm(span=26, adjust=False).mean()
        df_ind['macd'] = ema_12 - ema_26
        df_ind['macd_signal'] = df_ind['macd'].ewm(span=9, adjust=False).mean()
        df_ind['macd_hist'] = df_ind['macd'] - df_ind['macd_signal']
        
        # RSI
        delta = df_ind['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df_ind['rsi'] = 100 - (100 / (1 + rs))
        
        # 布林带
        df_ind['bb_middle'] = df_ind['close'].rolling(window=20).mean()
        bb_std = df_ind['close'].rolling(window=20).std()
        df_ind['bb_upper'] = df_ind['bb_middle'] + 2 * bb_std
        df_ind['bb_lower'] = df_ind['bb_middle'] - 2 * bb_std
        
        # 成交量相关
        df_ind['volume_ma'] = df_ind['volume'].rolling(window=20).mean()
        df_ind['volume_ratio'] = df_ind['volume'] / df_ind['volume_ma']
        
        # 价格变化
        df_ind['returns'] = df_ind['close'].pct_change()
        df_ind['log_returns'] = np.log(df_ind['close'] / df_ind['close'].shift(1))
        
        # 波动率
        df_ind['volatility'] = df_ind['returns'].rolling(window=20).std() * np.sqrt(252)
        
        logger.info(f"技术指标添加完成，总列数: {len(df_ind.columns)}")
        return df_ind
    
    def save_data(self, df: pd.DataFrame, file_path: str, 
                 format: str = 'csv', **kwargs) -> None:
        """
        保存数据
        
        Args:
            df: 数据DataFrame
            file_path: 保存路径
            format: 保存格式，'csv'或'parquet'
            **kwargs: 保存参数
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            if format == 'csv':
                df.to_csv(file_path, **kwargs)
            elif format == 'parquet':
                df.to_parquet(file_path, **kwargs)
            else:
                raise ValueError(f"不支持的保存格式: {format}")
            
            logger.info(f"数据保存成功: {file_path}, 格式: {format}")
            
        except Exception as e:
            logger.error(f"数据保存失败 {file_path}: {e}")
            raise
    
    def get_data_info(self, df: pd.DataFrame) -> Dict[str, Any]:
        """
        获取数据信息
        
        Args:
            df: 数据DataFrame
            
        Returns:
            数据信息字典
        """
        if df is None or df.empty:
            return {}
        
        info = {
            'shape': df.shape,
            'date_range': {
                'start': df.index.min().strftime('%Y-%m-%d') if hasattr(df.index.min(), 'strftime') else str(df.index.min()),
                'end': df.index.max().strftime('%Y-%m-%d') if hasattr(df.index.max(), 'strftime') else str(df.index.max()),
                'days': (df.index.max() - df.index.min()).days if hasattr(df.index.max() - df.index.min(), 'days') else len(df)
            },
            'columns': list(df.columns),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'missing_values': df.isnull().sum().to_dict(),
            'price_stats': {
                'open_mean': df['open'].mean() if 'open' in df.columns else None,
                'high_mean': df['high'].mean() if 'high' in df.columns else None,
                'low_mean': df['low'].mean() if 'low' in df.columns else None,
                'close_mean': df['close'].mean() if 'close' in df.columns else None,
                'volume_mean': df['volume'].mean() if 'volume' in df.columns else None
            },
            'returns_stats': {
                'mean_return': df['returns'].mean() if 'returns' in df.columns else None,
                'std_return': df['returns'].std() if 'returns' in df.columns else None,
                'sharpe_ratio': (df['returns'].mean() / df['returns'].std() * np.sqrt(252)) 
                               if 'returns' in df.columns and df['returns'].std() > 0 else None
            } if 'returns' in df.columns else {}
        }
        
        return info


if __name__ == "__main__":
    """数据加载器测试"""
    import sys
    import os
    
    # 添加路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 测试数据加载器
    print("测试数据加载器...")
    
    # 创建数据加载器
    loader = DataLoader()
    
    # 测试创建测试数据
    test_data = loader._create_test_data("TEST001.SZ", "daily", days=100)
    print(f"测试数据形状: {test_data.shape}")
    print(f"测试数据列名: {test_data.columns.tolist()}")
    print(f"测试数据前5行:\n{test_data.head()}")
    
    # 测试数据预处理
    processed_data = loader.preprocess_data(test_data)
    print(f"预处理后数据形状: {processed_data.shape}")
    print(f"预处理后列名: {processed_data.columns.tolist()}")
    
    # 测试数据信息
    data_info = loader.get_data_info(processed_data)
    print(f"数据信息:")
    print(f"  形状: {data_info['shape']}")
    print(f"  时间范围: {data_info['date_range']['start']} 到 {data_info['date_range']['end']}")
    print(f"  列数: {len(data_info['columns'])}")
    
    print("数据加载器测试完成!")