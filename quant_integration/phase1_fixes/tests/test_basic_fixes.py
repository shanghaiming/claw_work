#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本修复测试 - 验证第一阶段修复的核心功能
"""

import sys
import os
import pandas as pd
import numpy as np

# 添加父目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'fixes'))

from fixes.config_manager import ConfigManager
from fixes.data_adapter import DataAdapter


def test_config_manager():
    """测试配置管理器"""
    print("测试配置管理器...")
    
    # 创建配置管理器
    config = ConfigManager()
    
    # 测试基本功能
    assert config.get_config_value("data.base_dir") == "./data", "默认base_dir不正确"
    assert config.get_config_value("data.timeframe") == "5min", "默认timeframe不正确"
    assert config.get_config_value("backtest.initial_cash") == 1000000.0, "默认initial_cash不正确"
    
    # 测试路径获取
    data_dir = config.get_data_directory()
    assert "data/analyzed/5min" in data_dir, "数据目录路径不正确"
    
    # 测试命令行参数解析器
    parser = config.create_arg_parser()
    test_args = parser.parse_args([])
    assert test_args.strategy == "MovingAverage", "默认策略不正确"
    
    print("✓ 配置管理器测试通过")
    return True


def test_data_adapter():
    """测试数据适配器"""
    print("\n测试数据适配器...")
    
    # 创建数据适配器
    adapter = DataAdapter(data_dir="./test_data", timeframe="5min")
    
    # 验证数据目录
    assert os.path.exists(adapter.data_dir), "数据目录未创建"
    
    # 验证数据摘要
    summary = adapter.validate_data_directory()
    assert summary['directory_exists'], "数据目录不存在"
    
    # 如果没有数据文件，创建示例数据
    if summary['valid_files'] == 0:
        print("创建示例数据...")
        adapter._create_example_data()
        summary = adapter.validate_data_directory()
    
    assert summary['valid_files'] > 0, "没有有效数据文件"
    
    # 测试加载数据
    try:
        data = adapter.load_all_stock_data(max_files=1)
        assert not data.empty, "加载的数据为空"
        assert 'symbol' in data.columns, "数据缺少symbol列"
        assert 'open' in data.columns, "数据缺少open列"
        assert 'high' in data.columns, "数据缺少high列"
        assert 'low' in data.columns, "数据缺少low列"
        assert 'close' in data.columns, "数据缺少close列"
        print(f"✓ 数据加载测试通过: {len(data)} 行, {len(data['symbol'].unique())} 只股票")
    except Exception as e:
        print(f"✗ 数据加载失败: {e}")
        return False
    
    # 测试单个股票加载
    try:
        symbols = adapter.get_available_symbols()
        if symbols:
            symbol_data = adapter.load_single_stock_data(symbols[0])
            assert not symbol_data.empty, "单个股票数据为空"
            print(f"✓ 单个股票加载测试通过: {symbols[0]}, {len(symbol_data)} 行")
    except Exception as e:
        print(f"✗ 单个股票加载失败: {e}")
        return False
    
    # 清理测试目录
    import shutil
    if os.path.exists("./test_data"):
        shutil.rmtree("./test_data")
    
    print("✓ 数据适配器测试通过")
    return True


def test_windows_path_conversion():
    """测试Windows路径转换"""
    print("\n测试Windows路径转换...")
    
    adapter = DataAdapter()
    
    # 测试Windows路径转换
    windows_path = r"E:\stock\backtest\data\analyzed\5min"
    converted_path = adapter._convert_windows_path(windows_path)
    
    # 验证转换结果
    assert '\\' not in converted_path, "转换后的路径仍包含反斜杠"
    
    if sys.platform != 'win32':
        # 在非Windows系统上，应该转换为平台相关路径
        assert not converted_path.startswith("E:"), "Windows驱动器未被正确转换"
        print(f"✓ Windows路径转换测试通过: {windows_path} -> {converted_path}")
    else:
        print(f"✓ Windows系统，路径保持原样: {converted_path}")
    
    return True


def test_fixed_main_imports():
    """测试修复版main.py的导入"""
    print("\n测试修复版main.py导入...")
    
    try:
        # 测试导入修复模块
        from fixes.main_fixed import parse_args, load_all_stock_data_fixed_wrapper
        
        # 测试参数解析
        import argparse
        test_args = ["--data-dir", "./test_data", "--timeframe", "5min"]
        
        # 模拟命令行参数解析
        import sys
        original_argv = sys.argv
        sys.argv = ['test.py'] + test_args
        
        try:
            # 由于parse_args需要实际解析，我们只测试导入
            print("✓ 修复版main.py模块导入成功")
            
            # 测试配置管理器单例
            from fixes.config_manager import get_config
            config1 = get_config()
            config2 = get_config()
            assert config1 is config2, "配置管理器不是单例"
            print("✓ 配置管理器单例测试通过")
            
        finally:
            sys.argv = original_argv
            
    except ImportError as e:
        print(f"✗ 导入失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 其他错误: {e}")
        return False
    
    return True


def test_strategy_import():
    """测试策略导入"""
    print("\n测试策略导入...")
    
    # 检查src目录是否存在
    src_dir = "/Users/chengming/.openclaw/workspace/quant_integration/phase1_fixes/fixes/src"
    if not os.path.exists(src_dir):
        print("✗ src目录不存在")
        return False
    
    # 尝试导入策略
    try:
        sys.path.append(src_dir)
        
        # 尝试导入移动平均策略
        from strategies.ma_strategy import MovingAverageStrategy
        print("✓ MovingAverageStrategy导入成功")
        
        # 尝试导入回测引擎
        from backtest.engine import BacktestEngine
        print("✓ BacktestEngine导入成功")
        
        # 尝试导入性能分析器
        from backtest.performance import PerformanceAnalyzer
        print("✓ PerformanceAnalyzer导入成功")
        
        return True
        
    except ImportError as e:
        print(f"✗ 策略导入失败: {e}")
        print("可能需要检查src目录结构或修复导入路径")
        return False
    except Exception as e:
        print(f"✗ 其他导入错误: {e}")
        return False


def main():
    """运行所有测试"""
    print("="*60)
    print("第一阶段修复 - 基本功能测试")
    print("="*60)
    
    test_results = []
    
    # 运行测试
    test_results.append(("配置管理器", test_config_manager()))
    test_results.append(("数据适配器", test_data_adapter()))
    test_results.append(("Windows路径转换", test_windows_path_conversion()))
    test_results.append(("修复版main.py导入", test_fixed_main_imports()))
    test_results.append(("策略导入", test_strategy_import()))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        if result:
            print(f"✓ {test_name}: 通过")
            passed += 1
        else:
            print(f"✗ {test_name}: 失败")
            failed += 1
    
    print(f"\n总计: {passed} 通过, {failed} 失败")
    
    if failed == 0:
        print("\n✅ 所有测试通过! 第一阶段修复基本功能验证成功")
        print("\n下一步:")
        print("1. 运行修复版回测系统: python fixes/main_fixed.py")
        print("2. 使用示例数据测试: python fixes/main_fixed.py --data-dir ./data/analyzed/5min")
        print("3. 查看修复效果和日志输出")
    else:
        print(f"\n❌ 有 {failed} 个测试失败，请检查问题")
    
    print("="*60)
    
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)