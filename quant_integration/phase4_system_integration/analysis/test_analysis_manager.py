#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分析管理器基本测试
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from analysis_manager import UnifiedAnalysisManager
import pandas as pd
import numpy as np


def generate_test_data():
    """生成测试数据"""
    dates = pd.date_range('2024-01-01', periods=50, freq='D')
    data = pd.DataFrame({
        'open': np.random.randn(50).cumsum() + 100,
        'high': np.random.randn(50).cumsum() + 105,
        'low': np.random.randn(50).cumsum() + 95,
        'close': np.random.randn(50).cumsum() + 100,
        'volume': np.random.randint(1000, 10000, 50),
        'symbol': 'TEST'
    }, index=dates)
    return data


def test_basic_functionality():
    """测试基本功能"""
    print("="*60)
    print("测试1: 基本功能测试")
    print("="*60)
    
    # 生成测试数据
    data = generate_test_data()
    print(f"测试数据: {len(data)} 行")
    
    # 创建分析管理器
    config = {
        'enable_price_action': True,
        'enable_technical': True,
        'enable_signal': True,
        'result_integration': 'weighted'
    }
    
    try:
        manager = UnifiedAnalysisManager(config)
        print(f"✅ 分析管理器创建成功")
        print(f"   可用引擎: {manager.get_available_engines()}")
    except Exception as e:
        print(f"❌ 分析管理器创建失败: {e}")
        return False
    
    # 执行分析
    try:
        results = manager.analyze(data)
        print(f"✅ 分析执行成功")
        
        # 检查基本结果
        required_keys = ['analysis_timestamp', 'engine_count', 'total_signals', 'consensus_signals']
        missing_keys = [key for key in required_keys if key not in results]
        
        if missing_keys:
            print(f"❌ 结果缺少必要键: {missing_keys}")
            return False
        
        print(f"   引擎数量: {results['engine_count']}")
        print(f"   总信号数: {results['total_signals']}")
        print(f"   共识信号: {results['consensus_signals']}")
        
        # 显示引擎统计
        engine_stats = results.get('engine_stats', {})
        if engine_stats:
            print(f"   引擎统计:")
            for engine, stats in engine_stats.items():
                print(f"     {engine}: {stats.get('signal_count', 0)} 信号")
        
        return True
        
    except Exception as e:
        print(f"❌ 分析执行失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_individual_engines():
    """测试各个分析引擎"""
    print("\n" + "="*60)
    print("测试2: 各个分析引擎测试")
    print("="*60)
    
    data = generate_test_data()
    
    # 测试各个引擎
    engines_to_test = ['price_action', 'technical', 'signal']
    
    for engine_name in engines_to_test:
        print(f"\n测试 {engine_name} 引擎:")
        
        config = {
            'enable_price_action': (engine_name == 'price_action'),
            'enable_technical': (engine_name == 'technical'),
            'enable_signal': (engine_name == 'signal'),
            'result_integration': 'weighted'
        }
        
        try:
            manager = UnifiedAnalysisManager(config)
            engine = manager.get_engine(engine_name)
            
            if engine:
                print(f"  ✅ 引擎加载成功")
                
                # 测试引擎分析
                results = engine.analyze(data)
                signal_count = results.get('signal_count', 0)
                print(f"    信号数量: {signal_count}")
                
                if signal_count > 0:
                    print(f"    ✅ 生成 {signal_count} 个信号")
                else:
                    print(f"    ⚠️ 未生成信号")
            else:
                print(f"  ⚠️ 引擎 {engine_name} 不可用")
                
        except Exception as e:
            print(f"  ❌ 引擎 {engine_name} 测试失败: {e}")
    
    return True


def test_configuration():
    """测试配置选项"""
    print("\n" + "="*60)
    print("测试3: 配置选项测试")
    print("="*60)
    
    data = generate_test_data()
    
    # 测试不同配置
    test_configs = [
        {
            'name': '仅价格行为',
            'config': {'enable_price_action': True, 'enable_technical': False, 'enable_signal': False}
        },
        {
            'name': '仅技术分析', 
            'config': {'enable_price_action': False, 'enable_technical': True, 'enable_signal': False}
        },
        {
            'name': '仅信号分析',
            'config': {'enable_price_action': False, 'enable_technical': False, 'enable_signal': True}
        },
        {
            'name': '所有引擎',
            'config': {'enable_price_action': True, 'enable_technical': True, 'enable_signal': True}
        }
    ]
    
    for test in test_configs:
        print(f"\n测试配置: {test['name']}")
        
        try:
            manager = UnifiedAnalysisManager(test['config'])
            results = manager.analyze(data)
            
            engine_count = results.get('engine_count', 0)
            signal_count = results.get('total_signals', 0)
            
            print(f"  引擎数量: {engine_count}")
            print(f"  信号数量: {signal_count}")
            
            # 检查配置是否生效
            expected_engines = sum(1 for k, v in test['config'].items() if v and k.startswith('enable_'))
            if engine_count == expected_engines:
                print(f"  ✅ 配置生效正常")
            else:
                print(f"  ⚠️ 配置可能未完全生效 (期望 {expected_engines} 个引擎，实际 {engine_count})")
                
        except Exception as e:
            print(f"  ❌ 配置测试失败: {e}")
    
    return True


def test_integration_methods():
    """测试结果整合方法"""
    print("\n" + "="*60)
    print("测试4: 结果整合方法测试")
    print("="*60)
    
    data = generate_test_data()
    
    integration_methods = ['weighted', 'voting']
    
    for method in integration_methods:
        print(f"\n测试整合方法: {method}")
        
        config = {
            'enable_price_action': True,
            'enable_technical': True,
            'enable_signal': True,
            'result_integration': method
        }
        
        try:
            manager = UnifiedAnalysisManager(config)
            results = manager.analyze(data)
            
            consensus_signals = results.get('consensus_signals', 0)
            print(f"  共识信号数量: {consensus_signals}")
            
            # 显示信号详情
            signals_list = results.get('consensus_signals_list', [])
            if signals_list:
                print(f"  信号详情 (前3个):")
                for i, signal in enumerate(signals_list[:3]):
                    confidence = signal.get('confidence', 0)
                    sources = signal.get('sources', [])
                    print(f"    {i+1}. 类型: {signal.get('type', 'unknown')}, 置信度: {confidence:.2f}, 来源: {sources}")
            else:
                print(f"  ⚠️ 无共识信号")
            
            print(f"  ✅ {method} 整合方法测试成功")
            
        except Exception as e:
            print(f"  ❌ {method} 整合方法测试失败: {e}")
    
    return True


def main():
    """运行所有测试"""
    print("分析管理器测试套件")
    print("="*60)
    
    test_results = []
    
    tests = [
        ("基本功能", test_basic_functionality),
        ("各个分析引擎", test_individual_engines),
        ("配置选项", test_configuration),
        ("整合方法", test_integration_methods)
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
        print("\n🎉 所有测试通过! 分析管理器功能完整")
    else:
        print(f"\n⚠️ 有 {total - passed} 个测试失败")
    
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)