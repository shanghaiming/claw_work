#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一数据管理器 - 整合quant_trade-main项目的数据获取、处理和访问功能

功能:
1. 多数据源支持 (tushare API、本地文件、数据库)
2. 统一数据格式和接口
3. 数据预处理和特征工程
4. 缓存和性能优化
5. 错误处理和日志记录
"""

import os
import sys
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union, Tuple
from datetime import datetime, timedelta
from pathlib import Path
import logging
import warnings
import json
import pickle
import hashlib
from abc import ABC, abstractmethod
warnings.filterwarnings('ignore')

# 添加项目路径以便导入现有组件
sys.path.append('/Users/chengming/.openclaw/workspace/quant_integration/phase1_fixes/fixes')

# 导入现有的数据适配器
try:
    from data_adapter import DataAdapter
    DATA_ADAPTER_AVAILABLE = True
except ImportError:
    print("⚠️ 无法导入DataAdapter，将使用简化实现")
    DATA_ADAPTER_AVAILABLE = False


class DataSource(ABC):
    """数据源抽象基类 - 定义统一的数据获取接口"""
    
    @abstractmethod
    def fetch_data(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """获取指定符号和时间范围的数据"""
        pass
    
    @abstractmethod
    def get_available_symbols(self) -> List[str]:
        """获取可用的交易符号列表"""
        pass
    
    @abstractmethod
    def get_source_name(self) -> str:
        """获取数据源名称"""
        pass


class TushareDataSource(DataSource):
    """Tushare API数据源 - 基于quant_trade-main的fetch_daily_batch.py"""
    
    def __init__(self, token: Optional[str] = None):
        """
        初始化Tushare数据源
        
        参数:
            token: Tushare API token，如果为None则尝试从环境变量或配置文件获取
        """
        self.token = token or self._get_token()
        self._init_tushare()
        
    def _get_token(self) -> str:
        """获取Tushare token"""
        # 首先尝试从环境变量获取
        token = os.getenv('TUSHARE_TOKEN')
        if token:
            return token
        
        # 尝试从配置文件获取
        config_path = Path(__file__).parent.parent / 'config' / 'tushare_config.json'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    return config.get('token', '')
            except:
                pass
        
        # 使用quant_trade-main中的默认token
        return '304d18af85c89131420917d9378d91824a3e12246c7f160b89b746c7'
    
    def _init_tushare(self):
        """初始化Tushare"""
        try:
            import tushare as ts
            ts.set_token(self.token)
            self.pro = ts.pro_api()
            print(f"✅ Tushare数据源初始化成功 (token: {self.token[:10]}...)")
        except ImportError:
            print("⚠️ Tushare库未安装，Tushare数据源将不可用")
            self.pro = None
        except Exception as e:
            print(f"⚠️ Tushare初始化失败: {e}")
            self.pro = None
    
    def get_source_name(self) -> str:
        return "Tushare"
    
    def get_available_symbols(self) -> List[str]:
        """获取可用股票代码列表"""
        if not self.pro:
            return []
        
        try:
            # 获取A股列表
            df = self.pro.stock_basic(exchange='', list_status='L', fields='ts_code,symbol,name,area,industry,list_date')
            return df['ts_code'].tolist()[:100]  # 限制数量，避免API限制
        except Exception as e:
            print(f"获取股票列表失败: {e}")
            return []
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        获取股票日线数据
        
        参数:
            symbol: 股票代码 (如: 000001.SZ)
            start_date: 开始日期 (格式: YYYYMMDD)
            end_date: 结束日期 (格式: YYYYMMDD)
            **kwargs: 其他参数
        
        返回:
            DataFrame包含OHLCV数据
        """
        if not self.pro:
            raise RuntimeError("Tushare未正确初始化")
        
        try:
            # 获取日线数据
            df = self.pro.daily(ts_code=symbol, start_date=start_date, end_date=end_date)
            
            if df.empty:
                print(f"警告: 未找到{symbol}在{start_date}到{end_date}的数据")
                return pd.DataFrame()
            
            # 重命名列以匹配标准格式
            df = df.rename(columns={
                'trade_date': 'date',
                'ts_code': 'symbol',
                'open': 'open',
                'high': 'high', 
                'low': 'low',
                'close': 'close',
                'vol': 'volume',
                'amount': 'amount'
            })
            
            # 转换日期格式
            df['date'] = pd.to_datetime(df['date'], format='%Y%m%d')
            
            # 设置索引
            df.set_index('date', inplace=True)
            df.sort_index(inplace=True)
            
            print(f"✅ 获取{symbol}数据: {len(df)}行, {df.index.min()} 到 {df.index.max()}")
            return df
            
        except Exception as e:
            print(f"获取{symbol}数据失败: {e}")
            raise


class LocalFileDataSource(DataSource):
    """本地文件数据源 - 基于quant_trade-main的csv数据"""
    
    def __init__(self, base_dir: Optional[str] = None):
        """
        初始化本地文件数据源
        
        参数:
            base_dir: 数据目录，如果为None则使用quant_trade-main的默认目录
        """
        if base_dir:
            self.base_dir = Path(base_dir)
        else:
            # 使用quant_trade-main的默认数据目录
            quant_main_dir = Path("/Users/chengming/downloads/quant_trade-main")
            self.base_dir = quant_main_dir / "csv_version" / "daily_data2"
        
        # 确保目录存在
        self.base_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 本地文件数据源初始化: {self.base_dir}")
    
    def get_source_name(self) -> str:
        return "LocalFile"
    
    def get_available_symbols(self) -> List[str]:
        """获取可用的本地文件符号列表"""
        symbols = []
        
        # 查找CSV文件
        for file_path in self.base_dir.glob("*.csv"):
            symbol = file_path.stem
            symbols.append(symbol)
        
        # 查找Parquet文件
        for file_path in self.base_dir.glob("*.parquet"):
            symbol = file_path.stem
            symbols.append(symbol)
        
        return sorted(set(symbols))
    
    def fetch_data(self, symbol: str, start_date: str, end_date: str, **kwargs) -> pd.DataFrame:
        """
        从本地文件加载数据
        
        参数:
            symbol: 股票代码
            start_date: 开始日期 (格式: YYYYMMDD)
            end_date: 结束日期 (格式: YYYYMMDD)
            **kwargs: 其他参数 (如文件格式)
        
        返回:
            DataFrame包含OHLCV数据
        """
        file_format = kwargs.get('format', 'csv')
        file_path = self.base_dir / f"{symbol}.{file_format}"
        
        if not file_path.exists():
            print(f"警告: 文件不存在 {file_path}")
            return pd.DataFrame()
        
        try:
            # 根据格式加载数据
            if file_format == 'csv':
                df = pd.read_csv(file_path)
            elif file_format == 'parquet':
                df = pd.read_parquet(file_path)
            elif file_format == 'feather':
                df = pd.read_feather(file_path)
            else:
                raise ValueError(f"不支持的文件格式: {file_format}")
            
            # 标准化列名
            df = self._standardize_columns(df)
            
            # 过滤日期范围
            if 'date' in df.columns:
                df['date'] = pd.to_datetime(df['date'])
                
                try:
                    start_dt = pd.to_datetime(start_date, format='%Y%m%d')
                    end_dt = pd.to_datetime(end_date, format='%Y%m%d')
                    
                    # 检查数据日期范围
                    data_start = df['date'].min()
                    data_end = df['date'].max()
                    
                    if start_dt <= data_end and end_dt >= data_start:
                        # 有重叠日期范围
                        df = df[(df['date'] >= start_dt) & (df['date'] <= end_dt)]
                    else:
                        # 无重叠日期范围，返回所有数据并发出警告
                        print(f"⚠️ 请求日期范围({start_date}-{end_date})与数据范围({data_start.date()}-{data_end.date()})无重叠，返回所有数据")
                    
                    df.set_index('date', inplace=True)
                except Exception as e:
                    print(f"⚠️ 日期过滤失败: {e}，返回所有数据")
                    df.set_index('date', inplace=True)
            
            df.sort_index(inplace=True)
            print(f"✅ 加载{symbol}数据: {len(df)}行, 从 {file_path}")
            return df
            
        except Exception as e:
            print(f"加载{symbol}数据失败: {e}")
            raise
    
    def _standardize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """标准化数据列名"""
        column_mapping = {}
        
        # 尝试识别和标准化列名
        for col in df.columns:
            col_lower = col.lower()
            
            if 'date' in col_lower or 'time' in col_lower:
                column_mapping[col] = 'date'
            elif 'open' in col_lower:
                column_mapping[col] = 'open'
            elif 'high' in col_lower:
                column_mapping[col] = 'high'
            elif 'low' in col_lower:
                column_mapping[col] = 'low'
            elif 'close' in col_lower:
                column_mapping[col] = 'close'
            elif 'vol' in col_lower or 'volume' in col_lower:
                column_mapping[col] = 'volume'
            elif 'symbol' in col_lower or 'code' in col_lower:
                column_mapping[col] = 'symbol'
        
        # 应用重命名
        if column_mapping:
            df = df.rename(columns=column_mapping)
        
        return df


class CacheManager:
    """缓存管理器 - 提高数据访问性能"""
    
    def __init__(self, cache_dir: Optional[str] = None):
        """
        初始化缓存管理器
        
        参数:
            cache_dir: 缓存目录，如果为None则使用默认目录
        """
        if cache_dir:
            self.cache_dir = Path(cache_dir)
        else:
            self.cache_dir = Path(__file__).parent / 'cache'
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        print(f"✅ 缓存管理器初始化: {self.cache_dir}")
    
    def get_cache_key(self, symbol: str, start_date: str, end_date: str, 
                     source: str, **kwargs) -> str:
        """生成缓存键"""
        params_str = f"{symbol}_{start_date}_{end_date}_{source}_{str(kwargs)}"
        return hashlib.md5(params_str.encode()).hexdigest()
    
    def get_cache_path(self, cache_key: str) -> Path:
        """获取缓存文件路径"""
        return self.cache_dir / f"{cache_key}.pkl"
    
    def get(self, cache_key: str) -> Optional[pd.DataFrame]:
        """从缓存获取数据"""
        cache_path = self.get_cache_path(cache_key)
        
        if cache_path.exists():
            try:
                with open(cache_path, 'rb') as f:
                    data = pickle.load(f)
                print(f"📦 从缓存加载: {cache_key[:8]}...")
                return data
            except Exception as e:
                print(f"缓存加载失败: {e}")
        
        return None
    
    def set(self, cache_key: str, data: pd.DataFrame, ttl_hours: int = 24):
        """设置缓存数据"""
        cache_path = self.get_cache_path(cache_key)
        
        try:
            with open(cache_path, 'wb') as f:
                pickle.dump(data, f)
            print(f"💾 保存到缓存: {cache_key[:8]}... (TTL: {ttl_hours}小时)")
            
            # 设置过期时间（通过文件修改时间）
            os.utime(cache_path, None)
        except Exception as e:
            print(f"缓存保存失败: {e}")
    
    def cleanup(self, max_age_hours: int = 72):
        """清理过期缓存"""
        current_time = datetime.now()
        
        for cache_file in self.cache_dir.glob("*.pkl"):
            file_mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
            age_hours = (current_time - file_mtime).total_seconds() / 3600
            
            if age_hours > max_age_hours:
                try:
                    cache_file.unlink()
                    print(f"🗑️ 清理过期缓存: {cache_file.name}")
                except Exception as e:
                    print(f"缓存清理失败: {e}")


class DataPreprocessor:
    """数据预处理器 - 基于quant_trade-main的process_single.py"""
    
    def __init__(self):
        """初始化数据预处理器"""
        print("✅ 数据预处理器初始化")
    
    def process(self, df: pd.DataFrame, config: Optional[Dict] = None) -> pd.DataFrame:
        """
        处理原始数据，添加技术指标和特征
        
        参数:
            df: 原始OHLCV数据
            config: 处理配置
        
        返回:
            处理后的DataFrame
        """
        if df.empty:
            return df
        
        df_processed = df.copy()
        
        # 默认配置
        if config is None:
            config = {
                'add_basic_indicators': True,
                'add_volume_indicators': True,
                'add_trend_indicators': True,
                'add_volatility_indicators': True,
                'add_momentum_indicators': True,
                'add_pattern_features': False  # 需要更多数据
            }
        
        # 基本指标
        if config['add_basic_indicators']:
            df_processed = self._add_basic_indicators(df_processed)
        
        # 成交量指标
        if config['add_volume_indicators']:
            df_processed = self._add_volume_indicators(df_processed)
        
        # 趋势指标
        if config['add_trend_indicators']:
            df_processed = self._add_trend_indicators(df_processed)
        
        # 波动率指标
        if config['add_volatility_indicators']:
            df_processed = self._add_volatility_indicators(df_processed)
        
        # 动量指标
        if config['add_momentum_indicators']:
            df_processed = self._add_momentum_indicators(df_processed)
        
        print(f"✅ 数据处理完成: 原始{len(df)}行 → 处理后{len(df_processed)}行, {len(df_processed.columns)}列")
        return df_processed
    
    def _add_basic_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加基本技术指标"""
        if 'close' not in df.columns:
            return df
        
        df_processed = df.copy()
        
        # 价格变化
        price_change = df['close'].diff()
        price_change_pct = df['close'].pct_change() * 100
        
        df_processed['price_change'] = price_change.values if hasattr(price_change, 'values') else price_change
        df_processed['price_change_pct'] = price_change_pct.values if hasattr(price_change_pct, 'values') else price_change_pct
        
        # 价格区间
        price_range = df['high'] - df['low']
        price_range_pct = price_range / df['low'] * 100
        
        df_processed['price_range'] = price_range.values if hasattr(price_range, 'values') else price_range
        df_processed['price_range_pct'] = price_range_pct.values if hasattr(price_range_pct, 'values') else price_range_pct
        
        # 收盘位置
        high_low_diff = (df['high'] - df['low']).replace(0, 1)
        close_position = (df['close'] - df['low']) / high_low_diff
        
        df_processed['close_position'] = close_position.values if hasattr(close_position, 'values') else close_position
        
        return df_processed
    
    def _add_volume_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加成交量指标"""
        if 'volume' not in df.columns:
            return df
        
        df_processed = df.copy()
        
        # 成交量移动平均 - 确保返回Series
        for window in [5, 10, 20]:
            volume_ma = df['volume'].rolling(window=window, min_periods=1).mean()
            df_processed[f'volume_ma_{window}'] = volume_ma.values if hasattr(volume_ma, 'values') else volume_ma
        
        # 成交量比率
        volume_ma_20 = df['volume'].rolling(window=20, min_periods=1).mean()
        df_processed['volume_ratio'] = df['volume'] / volume_ma_20
        
        # 价量关系
        if 'price_change_pct' in df.columns:
            price_volume_corr = df['price_change_pct'].rolling(window=20).corr(df['volume'])
            df_processed['price_volume_corr'] = price_volume_corr.values if hasattr(price_volume_corr, 'values') else price_volume_corr
        
        return df_processed
    
    def _add_trend_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加趋势指标"""
        if 'close' not in df.columns:
            return df
        
        # 移动平均线
        for window in [5, 10, 20, 30, 50, 100]:
            df[f'ma_{window}'] = df['close'].rolling(window=window, min_periods=1).mean()
        
        # 移动平均线关系
        if 'ma_5' in df.columns and 'ma_20' in df.columns:
            df['ma_diff_5_20'] = df['ma_5'] - df['ma_20']
            df['ma_diff_pct_5_20'] = df['ma_diff_5_20'] / df['ma_20'] * 100
        
        # 指数移动平均
        for span in [12, 26]:
            df[f'ema_{span}'] = df['close'].ewm(span=span, adjust=False).mean()
        
        return df
    
    def _add_volatility_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加波动率指标"""
        if 'close' not in df.columns:
            return df
        
        # 收益率标准差
        for window in [5, 10, 20]:
            if 'price_change_pct' in df.columns:
                df[f'volatility_{window}'] = df['price_change_pct'].rolling(window=window).std()
        
        # ATR (平均真实范围)
        if all(col in df.columns for col in ['high', 'low', 'close']):
            high_low = df['high'] - df['low']
            high_close_prev = abs(df['high'] - df['close'].shift())
            low_close_prev = abs(df['low'] - df['close'].shift())
            tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            df['atr_14'] = tr.rolling(window=14).mean()
        
        return df
    
    def _add_momentum_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加动量指标"""
        if 'close' not in df.columns:
            return df
        
        # RSI
        if 'price_change' in df.columns:
            gains = df['price_change'].where(df['price_change'] > 0, 0)
            losses = -df['price_change'].where(df['price_change'] < 0, 0)
            avg_gain = gains.rolling(window=14).mean()
            avg_loss = losses.rolling(window=14).mean()
            rs = avg_gain / avg_loss.replace(0, 1)
            df['rsi_14'] = 100 - (100 / (1 + rs))
        
        # MACD
        if 'ema_12' in df.columns and 'ema_26' in df.columns:
            df['macd'] = df['ema_12'] - df['ema_26']
            df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
            df['macd_histogram'] = df['macd'] - df['macd_signal']
        
        return df


class UnifiedDataManager:
    """
    统一数据管理器 - 主入口点
    
    整合:
    1. 多数据源 (Tushare、本地文件、现有数据适配器)
    2. 缓存管理
    3. 数据预处理
    4. 统一数据接口
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化统一数据管理器
        
        参数:
            config: 配置字典
        """
        # 默认配置
        self.config = config or {
            'cache_enabled': True,
            'cache_ttl_hours': 24,
            'preprocessing_enabled': True,
            'default_source': 'tushare',  # tushare, local, adapter
            'tushare_token': None,
            'local_data_dir': None,
            'adapter_config': None
        }
        
        # 初始化组件
        self.cache_manager = CacheManager() if self.config['cache_enabled'] else None
        self.preprocessor = DataPreprocessor() if self.config['preprocessing_enabled'] else None
        
        # 初始化数据源
        self.data_sources = {}
        self._init_data_sources()
        
        print(f"✅ 统一数据管理器初始化完成")
        print(f"   可用数据源: {list(self.data_sources.keys())}")
        print(f"   缓存: {'启用' if self.config['cache_enabled'] else '禁用'}")
        print(f"   预处理: {'启用' if self.config['preprocessing_enabled'] else '禁用'}")
    
    def _init_data_sources(self):
        """初始化数据源"""
        # Tushare数据源
        try:
            tushare_token = self.config.get('tushare_token')
            self.data_sources['tushare'] = TushareDataSource(token=tushare_token)
        except Exception as e:
            print(f"⚠️ Tushare数据源初始化失败: {e}")
        
        # 本地文件数据源
        try:
            local_dir = self.config.get('local_data_dir')
            self.data_sources['local'] = LocalFileDataSource(base_dir=local_dir)
        except Exception as e:
            print(f"⚠️ 本地文件数据源初始化失败: {e}")
        
        # 现有数据适配器
        if DATA_ADAPTER_AVAILABLE:
            try:
                adapter_config = self.config.get('adapter_config', {})
                self.data_sources['adapter'] = DataAdapter(**adapter_config)
            except Exception as e:
                print(f"⚠️ 数据适配器初始化失败: {e}")
    
    def get_data(self, symbol: str, start_date: str, end_date: str, 
                source: Optional[str] = None, **kwargs) -> pd.DataFrame:
        """
        获取数据 - 统一入口点
        
        参数:
            symbol: 交易符号
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            source: 数据源名称 (tushare, local, adapter)，如果为None则使用默认
            **kwargs: 其他参数
        
        返回:
            处理后的DataFrame
        """
        # 确定数据源
        if source is None:
            source = self.config['default_source']
        
        if source not in self.data_sources:
            raise ValueError(f"不支持的数据源: {source}，可用: {list(self.data_sources.keys())}")
        
        data_source = self.data_sources[source]
        
        # 检查缓存
        cache_key = None
        if self.cache_manager:
            cache_key = self.cache_manager.get_cache_key(symbol, start_date, end_date, source, **kwargs)
            cached_data = self.cache_manager.get(cache_key)
            if cached_data is not None:
                return cached_data
        
        print(f"📥 从{source}获取{symbol}数据: {start_date} 到 {end_date}")
        
        # 获取原始数据
        try:
            if source == 'adapter':
                # 数据适配器的特殊处理
                raw_data = data_source.load_data(symbol=symbol, start_date=start_date, end_date=end_date, **kwargs)
            else:
                # 标准数据源
                raw_data = data_source.fetch_data(symbol, start_date, end_date, **kwargs)
            
            if raw_data.empty:
                print(f"⚠️ 未获取到{symbol}数据")
                return pd.DataFrame()
            
            # 数据预处理
            if self.preprocessor:
                processed_data = self.preprocessor.process(raw_data)
            else:
                processed_data = raw_data
            
            # 保存到缓存
            if self.cache_manager and cache_key:
                self.cache_manager.set(cache_key, processed_data, self.config['cache_ttl_hours'])
            
            return processed_data
            
        except Exception as e:
            print(f"❌ 获取{symbol}数据失败: {e}")
            raise
    
    def get_available_symbols(self, source: Optional[str] = None) -> List[str]:
        """获取可用交易符号列表"""
        if source is None:
            source = self.config['default_source']
        
        if source not in self.data_sources:
            raise ValueError(f"不支持的数据源: {source}")
        
        return self.data_sources[source].get_available_symbols()
    
    def get_multiple_symbols(self, symbols: List[str], start_date: str, end_date: str,
                           source: Optional[str] = None, **kwargs) -> Dict[str, pd.DataFrame]:
        """批量获取多个符号的数据"""
        results = {}
        
        for symbol in symbols:
            try:
                data = self.get_data(symbol, start_date, end_date, source, **kwargs)
                if not data.empty:
                    results[symbol] = data
                    print(f"✅ 已获取 {symbol}: {len(data)} 行")
                else:
                    print(f"⚠️ {symbol} 无数据")
            except Exception as e:
                print(f"❌ {symbol} 获取失败: {e}")
        
        print(f"📊 批量获取完成: {len(results)}/{len(symbols)} 个符号成功")
        return results
    
    def get_portfolio_data(self, portfolio: Dict[str, float], start_date: str, end_date: str,
                          source: Optional[str] = None, **kwargs) -> Dict[str, pd.DataFrame]:
        """获取投资组合数据"""
        symbols = list(portfolio.keys())
        return self.get_multiple_symbols(symbols, start_date, end_date, source, **kwargs)
    
    def cleanup_cache(self, max_age_hours: int = 72):
        """清理过期缓存"""
        if self.cache_manager:
            self.cache_manager.cleanup(max_age_hours)


# ========== 使用示例 ==========

def example_usage():
    """使用示例"""
    print("="*60)
    print("统一数据管理器使用示例")
    print("="*60)
    
    # 创建数据管理器
    config = {
        'cache_enabled': True,
        'preprocessing_enabled': True,
        'default_source': 'tushare',
        'tushare_token': None  # 使用默认或环境变量
    }
    
    manager = UnifiedDataManager(config)
    
    # 示例1: 获取单个股票数据
    print("\n1. 获取单个股票数据:")
    try:
        # 获取平安银行数据
        data = manager.get_data(
            symbol='000001.SZ',
            start_date='20240101',
            end_date='20240328',
            source='tushare'
        )
        
        if not data.empty:
            print(f"获取成功: {len(data)} 行数据")
            print(f"时间范围: {data.index.min()} 到 {data.index.max()}")
            print(f"数据列: {list(data.columns[:10])}...")  # 只显示前10列
        else:
            print("获取失败或无数据")
    except Exception as e:
        print(f"示例1失败: {e}")
    
    # 示例2: 查看可用符号
    print("\n2. 查看可用符号:")
    try:
        symbols = manager.get_available_symbols(source='tushare')
        print(f"可用符号数量: {len(symbols)}")
        print(f"前10个符号: {symbols[:10]}")
    except Exception as e:
        print(f"示例2失败: {e}")
    
    # 示例3: 批量获取数据
    print("\n3. 批量获取数据:")
    try:
        test_symbols = ['000001.SZ', '000002.SZ', '000063.SZ'][:2]  # 限制数量
        batch_data = manager.get_multiple_symbols(
            symbols=test_symbols,
            start_date='20240101',
            end_date='20240110',  # 短时间范围
            source='tushare'
        )
        
        print(f"批量获取结果: {len(batch_data)}/{len(test_symbols)} 成功")
        for symbol, df in batch_data.items():
            print(f"  {symbol}: {len(df)} 行, {len(df.columns)} 列")
    except Exception as e:
        print(f"示例3失败: {e}")
    
    # 示例4: 使用本地文件数据源
    print("\n4. 使用本地文件数据源:")
    try:
        # 创建本地数据管理器
        local_config = {
            'default_source': 'local',
            'local_data_dir': '/Users/chengming/downloads/quant_trade-main/csv_version/daily_data2',
            'cache_enabled': True,
            'preprocessing_enabled': True
        }
        
        local_manager = UnifiedDataManager(local_config)
        local_symbols = local_manager.get_available_symbols()
        print(f"本地可用符号: {len(local_symbols)} 个")
        
        if local_symbols:
            # 尝试加载第一个本地文件
            first_symbol = local_symbols[0]
            local_data = local_manager.get_data(
                symbol=first_symbol,
                start_date='20200101',
                end_date='20241231',
                source='local',
                format='csv'
            )
            
            if not local_data.empty:
                print(f"本地数据加载成功: {first_symbol}, {len(local_data)} 行")
            else:
                print("本地数据加载失败或无数据")
    except Exception as e:
        print(f"示例4失败: {e}")
    
    print(f"\n✅ 统一数据管理器示例完成")


if __name__ == "__main__":
    example_usage()