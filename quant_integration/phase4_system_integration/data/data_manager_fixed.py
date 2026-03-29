#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据预处理器修复版 - 解决pandas赋值问题
"""

import pandas as pd
import numpy as np
from typing import Dict


class DataPreprocessorFixed:
    """数据预处理器修复版 - 使用更安全的赋值方法"""
    
    def __init__(self):
        """初始化数据预处理器"""
        print("✅ 数据预处理器修复版初始化")
    
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
                'add_pattern_features': False
            }
        
        # 基本指标
        if config['add_basic_indicators']:
            df_processed = self._add_basic_indicators_safe(df_processed)
        
        # 成交量指标
        if config['add_volume_indicators']:
            df_processed = self._add_volume_indicators_safe(df_processed)
        
        # 趋势指标
        if config['add_trend_indicators']:
            df_processed = self._add_trend_indicators_safe(df_processed)
        
        # 波动率指标
        if config['add_volatility_indicators']:
            df_processed = self._add_volatility_indicators_safe(df_processed)
        
        # 动量指标
        if config['add_momentum_indicators']:
            df_processed = self._add_momentum_indicators_safe(df_processed)
        
        print(f"✅ 数据处理完成: 原始{len(df)}行 → 处理后{len(df_processed)}行, {len(df_processed.columns)}列")
        return df_processed
    
    def _add_basic_indicators_safe(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加基本技术指标 (安全版本)"""
        if 'close' not in df.columns:
            return df
        
        # 使用assign方法避免直接赋值问题
        result = df.copy()
        
        # 价格变化
        if 'close' in result.columns:
            result = result.assign(
                price_change=result['close'].diff(),
                price_change_pct=result['close'].pct_change() * 100
            )
        
        # 价格区间
        if all(col in result.columns for col in ['high', 'low']):
            result = result.assign(
                price_range=result['high'] - result['low'],
                price_range_pct=(result['high'] - result['low']) / result['low'].replace(0, 1) * 100
            )
        
        return result
    
    def _add_volume_indicators_safe(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加成交量指标 (安全版本)"""
        if 'volume' not in df.columns:
            return df
        
        result = df.copy()
        
        # 成交量移动平均
        for window in [5, 10, 20]:
            col_name = f'volume_ma_{window}'
            result[col_name] = result['volume'].rolling(window=window, min_periods=1).mean().values
        
        # 成交量比率
        result['volume_ratio'] = (result['volume'] / 
                                 result['volume'].rolling(window=20, min_periods=1).mean()).values
        
        return result
    
    def _add_trend_indicators_safe(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加趋势指标 (安全版本)"""
        if 'close' not in df.columns:
            return df
        
        result = df.copy()
        
        # 移动平均线
        for window in [5, 10, 20, 30, 50, 100]:
            col_name = f'ma_{window}'
            result[col_name] = result['close'].rolling(window=window, min_periods=1).mean().values
        
        # 移动平均线关系
        if 'ma_5' in result.columns and 'ma_20' in result.columns:
            result['ma_diff_5_20'] = (result['ma_5'] - result['ma_20']).values
            result['ma_diff_pct_5_20'] = (result['ma_diff_5_20'] / result['ma_20'].replace(0, 1) * 100).values
        
        # 指数移动平均
        for span in [12, 26]:
            col_name = f'ema_{span}'
            result[col_name] = result['close'].ewm(span=span, adjust=False).mean().values
        
        return result
    
    def _add_volatility_indicators_safe(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加波动率指标 (安全版本)"""
        if 'close' not in df.columns:
            return df
        
        result = df.copy()
        
        # 收益率标准差
        if 'price_change_pct' in result.columns:
            for window in [5, 10, 20]:
                col_name = f'volatility_{window}'
                result[col_name] = result['price_change_pct'].rolling(window=window).std().values
        
        # ATR (平均真实范围)
        if all(col in result.columns for col in ['high', 'low', 'close']):
            high_low = result['high'] - result['low']
            high_close_prev = abs(result['high'] - result['close'].shift())
            low_close_prev = abs(result['low'] - result['close'].shift())
            tr = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            result['atr_14'] = tr.rolling(window=14).mean().values
        
        return result
    
    def _add_momentum_indicators_safe(self, df: pd.DataFrame) -> pd.DataFrame:
        """添加动量指标 (安全版本)"""
        if 'close' not in df.columns:
            return df
        
        result = df.copy()
        
        # RSI
        if 'price_change' in result.columns:
            gains = result['price_change'].where(result['price_change'] > 0, 0)
            losses = -result['price_change'].where(result['price_change'] < 0, 0)
            avg_gain = gains.rolling(window=14).mean()
            avg_loss = losses.rolling(window=14).mean()
            rs = avg_gain / avg_loss.replace(0, 1)
            result['rsi_14'] = (100 - (100 / (1 + rs))).values
        
        # MACD
        if 'ema_12' in result.columns and 'ema_26' in result.columns:
            result['macd'] = (result['ema_12'] - result['ema_26']).values
            result['macd_signal'] = result['macd'].ewm(span=9, adjust=False).mean().values
            result['macd_histogram'] = (result['macd'] - result['macd_signal']).values
        
        return result