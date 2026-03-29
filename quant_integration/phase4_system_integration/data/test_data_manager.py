#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试统一数据管理器
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_manager import UnifiedDataManager
import pandas as pd
import numpy as np


def test_local_file_source():
    """测试本地文件数据源"""
    print("="*60)
    print("测试1: 本地文件数据源")
    print("="*60)
    
    # 配置使用本地文件数据源
    config = {
        'cache_enabled': False,  # 测试时禁用缓存
        'preprocessing_enabled': True,
        'default_source': 'local',
        'local_data_dir': '/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration/data/example_data'
    }
    
    manager = UnifiedDataManager(config)
    
    # 查看可用符号
    symbols = manager.get_available_symbols()
    print(f"可用符号: {symbols}")
    
    if not symbols:
        print("⚠️ 没有找到本地数据文件")
        return False
    
    # 测试获取单个股票数据
    test_symbol = symbols[0]
    print(f"\n测试获取: {test_symbol}")
    
    try:
        data = manager.get_data(
            symbol=test_symbol,
            start_date='20240101',
            end_date='20241231',
            source='local',
            format='csv'
        )
        
        if data.empty:
            print(f"⚠️ 获取{test_symbol}数据为空")
            return False
        
        print(f"✅ 获取成功: {len(data)} 行, {len(data.columns)} 列")
        print(f"   时间范围: {data.index.min()} 到 {data.index.max()}")
        print(f"   数据列 (前10个): {list(data.columns)[:10]}")
        
        # 检查必要列
        required_cols = ['open', 'high', 'low', 'close']
        missing_cols = [col for col in required_cols if col not in data.columns]
        if missing_cols:
            print(f"⚠️ 缺少必要列: {missing_cols}")
            return False
        
        print(f"✅ 所有必要列都存在")
        
        # 显示数据预览
        print(f"\n数据预览 (前5行):")
        print(data[['open', 'high', 'low', 'close', 'volume']].head())
        
        return True
        
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_cache_functionality():
    """测试缓存功能"""
    print("\n" + "="*60)
    print("测试2: 缓存功能")
    print("="*60)
    
    config = {
        'cache_enabled': True,
        'cache_ttl_hours': 1,  # 短TTL便于测试
        'preprocessing_enabled': True,
        'default_source': 'local',
        'local_data_dir': '/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration/data/example_data'
    }
    
    manager = UnifiedDataManager(config)
    
    symbols = manager.get_available_symbols()
    if not symbols:
        print("⚠️ 没有可用符号")
        return False
    
    test_symbol = symbols[0]
    
    print(f"测试缓存: {test_symbol}")
    
    try:
        # 第一次获取 (应该从文件加载)
        print("第一次获取 (从文件加载)...")
        start_time = pd.Timestamp.now()
        data1 = manager.get_data(
            symbol=test_symbol,
            start_date='20240101',
            end_date='20241231',
            source='local',
            format='csv'
        )
        load_time1 = (pd.Timestamp.now() - start_time).total_seconds()
        print(f"  加载时间: {load_time1:.3f}秒")
        
        # 第二次获取 (应该从缓存加载)
        print("第二次获取 (从缓存加载)...")
        start_time = pd.Timestamp.now()
        data2 = manager.get_data(
            symbol=test_symbol,
            start_date='20240101',
            end_date='20241231',
            source='local',
            format='csv'
        )
        load_time2 = (pd.Timestamp.now() - start_time).total_seconds()
        print(f"  加载时间: {load_time2:.3f}秒")
        
        # 检查缓存是否加速
        if load_time2 < load_time1:
            print(f"✅ 缓存加速: {load_time1/load_time2:.1f}倍加速")
        else:
            print(f"⚠️ 缓存未加速: {load_time1:.3f}s vs {load_time2:.3f}s")
        
        # 检查数据一致性
        if data1.equals(data2):
            print(f"✅ 缓存数据与原始数据一致")
        else:
            print(f"⚠️ 缓存数据与原始数据不一致")
            print(f"   数据1形状: {data1.shape}")
            print(f"   数据2形状: {data2.shape}")
        
        # 清理缓存
        print("\n清理缓存...")
        manager.cleanup_cache(max_age_hours=0)  # 清理所有缓存
        
        return True
        
    except Exception as e:
        print(f"❌ 缓存测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_operations():
    """测试批量操作"""
    print("\n" + "="*60)
    print("测试3: 批量操作")
    print("="*60)
    
    config = {
        'cache_enabled': False,
        'preprocessing_enabled': True,
        'default_source': 'local',
        'local_data_dir': '/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration/data/example_data'
    }
    
    manager = UnifiedDataManager(config)
    
    symbols = manager.get_available_symbols()
    if not symbols:
        print("⚠️ 没有可用符号")
        return False
    
    # 测试多个符号
    test_symbols = symbols[:3]  # 前3个符号
    print(f"批量获取: {test_symbols}")
    
    try:
        batch_data = manager.get_multiple_symbols(
            symbols=test_symbols,
            start_date='20240101',
            end_date='20241231',
            source='local',
            format='csv'
        )
        
        print(f"✅ 批量获取完成: {len(batch_data)}/{len(test_symbols)} 成功")
        
        for symbol, data in batch_data.items():
            print(f"  {symbol}: {len(data)} 行, {len(data.columns)} 列")
            
            # 检查数据质量
            if data.empty:
                print(f"    ⚠️ 数据为空")
            elif data.isnull().any().any():
                null_counts = data.isnull().sum()
                null_cols = null_counts[null_counts > 0]
                print(f"    ⚠️ 包含空值列: {list(null_cols.index)[:5]}")
            else:
                print(f"    ✅ 数据质量良好")
        
        # 测试投资组合数据获取
        print(f"\n测试投资组合数据获取...")
        portfolio = {symbol: 0.33 for symbol in test_symbols}  # 等权重
        portfolio_data = manager.get_portfolio_data(
            portfolio=portfolio,
            start_date='20240101',
            end_date='20241231',
            source='local',
            format='csv'
        )
        
        print(f"✅ 投资组合数据获取: {len(portfolio_data)}/{len(portfolio)} 成功")
        
        return True
        
    except Exception as e:
        print(f"❌ 批量操作测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_preprocessing():
    """测试数据预处理"""
    print("\n" + "="*60)
    print("测试4: 数据预处理")
    print("="*60)
    
    config = {
        'cache_enabled': False,
        'preprocessing_enabled': True,
        'default_source': 'local',
        'local_data_dir': '/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration/data/example_data'
    }
    
    manager = UnifiedDataManager(config)
    
    symbols = manager.get_available_symbols()
    if not symbols:
        print("⚠️ 没有可用符号")
        return False
    
    test_symbol = symbols[0]
    
    print(f"测试预处理: {test_symbol}")
    
    try:
        # 获取预处理后的数据
        data = manager.get_data(
            symbol=test_symbol,
            start_date='20240101',
            end_date='20241231',
            source='local',
            format='csv'
        )
        
        # 检查技术指标
        technical_indicators = [
            'price_change', 'price_change_pct', 'price_range', 'price_range_pct',
            'ma_5', 'ma_10', 'ma_20', 'volume_ma_5', 'volume_ma_10',
            'ma_diff_5_20', 'ma_diff_pct_5_20', 'volatility_5', 'volatility_10',
            'rsi_14'
        ]
        
        found_indicators = [ind for ind in technical_indicators if ind in data.columns]
        missing_indicators = [ind for ind in technical_indicators if ind not in data.columns]
        
        print(f"✅ 找到的技术指标: {len(found_indicators)}/{len(technical_indicators)}")
        print(f"   已找到: {found_indicators[:5]}...")
        if missing_indicators:
            print(f"   未找到: {missing_indicators[:5]}...")
        
        # 检查指标计算是否正确
        print(f"\n检查指标计算:")
        
        # 检查移动平均线
        if 'ma_5' in data.columns and 'close' in data.columns:
            manual_ma = data['close'].rolling(window=5, min_periods=1).mean()
            ma_diff = (data['ma_5'] - manual_ma).abs().max()
            if ma_diff < 0.001:
                print(f"  ✅ MA_5 计算正确 (最大误差: {ma_diff:.6f})")
            else:
                print(f"  ⚠️ MA_5 计算可能有误 (最大误差: {ma_diff:.6f})")
        
        # 检查价格变化
        if 'price_change' in data.columns and 'close' in data.columns:
            manual_change = data['close'].diff()
            change_diff = (data['price_change'] - manual_change).abs().max()
            if change_diff < 0.001:
                print(f"  ✅ price_change 计算正确 (最大误差: {change_diff:.6f})")
            else:
                print(f"  ⚠️ price_change 计算可能有误 (最大误差: {change_diff:.6f})")
        
        # 检查数据完整性
        null_count = data.isnull().sum().sum()
        total_cells = data.size
        
        if null_count == 0:
            print(f"  ✅ 数据完整，无空值")
        else:
            null_percentage = null_count / total_cells * 100
            print(f"  ⚠️ 数据包含空值: {null_count}/{total_cells} ({null_percentage:.2f}%)")
            
            # 显示空值最多的列
            null_by_col = data.isnull().sum()
            null_by_col = null_by_col[null_by_col > 0]
            if len(null_by_col) > 0:
                print(f"     空值最多的列: {null_by_col.index.tolist()[:5]}")
        
        return len(found_indicators) > 5  # 至少找到5个技术指标
        
    except Exception as e:
        print(f"❌ 预处理测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_configuration():
    """测试配置系统"""
    print("\n" + "="*60)
    print("测试5: 配置系统")
    print("="*60)
    
    import json
    config_path = '/Users/chengming/.openclaw/workspace/quant_integration/phase4_system_integration/config/data_config.json'
    
    try:
        # 加载配置文件
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        print(f"✅ 配置文件加载成功: {config_path}")
        
        # 创建带配置的数据管理器
        merged_config = {
            'cache_enabled': config['data_manager']['cache_enabled'],
            'cache_ttl_hours': config['data_manager']['cache_ttl_hours'],
            'preprocessing_enabled': config['data_manager']['preprocessing_enabled'],
            'default_source': config['data_manager']['default_source'],
            'tushare_token': config['tushare']['token'],
            'local_data_dir': config['local_files']['base_dir'],
            'preprocessing_config': config['preprocessing']
        }
        
        manager = UnifiedDataManager(merged_config)
        
        print(f"✅ 使用配置文件初始化成功")
        print(f"   缓存: {'启用' if merged_config['cache_enabled'] else '禁用'}")
        print(f"   默认数据源: {merged_config['default_source']}")
        print(f"   预处理配置: {len(merged_config['preprocessing_config'])} 项")
        
        # 显示预处理配置
        preproc_config = merged_config['preprocessing_config']
        enabled_features = [k for k, v in preproc_config.items() if isinstance(v, bool) and v]
        print(f"   启用的预处理功能: {len(enabled_features)} 个")
        print(f"      {enabled_features[:5]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ 配置测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """运行所有测试"""
    print("统一数据管理器测试套件")
    print("="*60)
    
    test_results = []
    
    # 运行测试
    tests = [
        ("本地文件数据源", test_local_file_source),
        ("缓存功能", test_cache_functionality),
        ("批量操作", test_batch_operations),
        ("数据预处理", test_preprocessing),
        ("配置系统", test_configuration)
    ]
    
    for test_name, test_func in tests:
        try:
            print(f"\n▶️ 运行测试: {test_name}")
            result = test_func()
            test_results.append((test_name, result))
            
            if result:
                print(f"✅ {test_name}: 通过")
            else:
                print(f"❌ {test_name}: 失败")
                
        except Exception as e:
            print(f"❌ {test_name}: 出错 - {e}")
            import traceback
            traceback.print_exc()
            test_results.append((test_name, False))
    
    # 汇总结果
    print("\n" + "="*60)
    print("测试结果汇总")
    print("="*60)
    
    passed = sum(1 for _, result in test_results if result)
    total = len(test_results)
    
    for test_name, result in test_results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {test_name}: {status}")
    
    print(f"\n总计: {passed}/{total} 个测试通过")
    
    if passed == total:
        print("\n🎉 所有测试通过! 统一数据管理器功能完整")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)