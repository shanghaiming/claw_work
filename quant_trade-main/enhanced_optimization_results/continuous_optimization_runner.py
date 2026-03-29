#!/usr/bin/env python3
# 自动持续优化脚本
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from continuous_optimization_enhanced import (
    load_multiple_stocks, MovingAverageStrategyEnhanced,
    EnhancedBacktestEngine, optimize_parameters
)

# 配置
STOCKS = ['000001.SZ', '000002.SZ', '000004.SZ', '000006.SZ', '000008.SZ', '000009.SZ', '000010.SZ', '000011.SZ', '000012.SZ', '000014.SZ']
PARAM_SPACE = {'short_window': [3, 5, 8, 13, 21, 34], 'long_window': [21, 34, 55, 89, 144, 233], 'stop_loss': [0.01, 0.015, 0.02, 0.025, 0.03], 'take_profit': [0.03, 0.04, 0.05, 0.06, 0.08, 0.1], 'use_rsi_filter': [True, False], 'rsi_period': [14, 21, 28], 'rsi_overbought': [70, 75, 80], 'rsi_oversold': [20, 25, 30]}
ITERATIONS = 30  # 每次运行迭代次数
RUN_INTERVAL_HOURS = 1  # 运行间隔(小时)

print("🔄 自动持续优化启动...")
# 这里可以添加定时循环逻辑
