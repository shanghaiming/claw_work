"""
简单测试六因子策略核心功能
"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# 生成简单的测试数据
np.random.seed(42)
dates = [datetime(2025, 1, 1) + timedelta(days=i) for i in range(100)]
test_df = pd.DataFrame({
    'open': np.random.normal(100, 5, 100).cumsum() + 100,
    'high': np.random.normal(105, 5, 100).cumsum() + 105,
    'low': np.random.normal(95, 5, 100).cumsum() + 95,
    'close': np.random.normal(100, 5, 100).cumsum() + 100,
    'volume': np.random.randint(10000, 100000, 100)
}, index=dates)

print("测试数据生成完成:")
print(f"形状: {test_df.shape}")
print(f"列: {test_df.columns.tolist()}")
print(f"价格范围: {test_df['close'].min():.2f} - {test_df['close'].max():.2f}")
print()

# 测试LSMA函数
try:
    from multi_factor_strategy_v2 import calculate_lsma
    lsma_result = calculate_lsma(test_df, n=20)
    print(f"✅ LSMA计算成功")
    print(f"   非空值: {lsma_result.notna().sum()}个")
    print(f"   范围: {lsma_result.min():.2f} - {lsma_result.max():.2f}")
except Exception as e:
    print(f"❌ LSMA计算失败: {e}")
print()

# 测试Fisher Transform
try:
    from multi_factor_strategy_v2 import calculate_fisher_transform
    fisher_result = calculate_fisher_transform(test_df, n=10)
    print(f"✅ Fisher Transform计算成功")
    print(f"   非空值: {fisher_result.notna().sum()}个")
    print(f"   范围: {fisher_result.min():.2f} - {fisher_result.max():.2f}")
except Exception as e:
    print(f"❌ Fisher Transform计算失败: {e}")
print()

# 测试Choppiness Index
try:
    from multi_factor_strategy_v2 import calculate_choppiness_index
    chop_result = calculate_choppiness_index(test_df, n=14)
    print(f"✅ Choppiness Index计算成功")
    print(f"   非空值: {chop_result.notna().sum()}个")
    print(f"   范围: {chop_result.min():.2f} - {chop_result.max():.2f}")
except Exception as e:
    print(f"❌ Choppiness Index计算失败: {e}")
print()

# 测试Hull MA
try:
    from multi_factor_strategy_v2 import calculate_hull_moving_average
    hma_result = calculate_hull_moving_average(test_df, n=20)
    print(f"✅ Hull MA计算成功")
    print(f"   非空值: {hma_result.notna().sum()}个")
    print(f"   范围: {hma_result.min():.2f} - {hma_result.max():.2f}")
except Exception as e:
    print(f"❌ Hull MA计算失败: {e}")
print()

# 测试完整指标计算
try:
    from multi_factor_strategy_v2 import calculate_all_indicators
    df_with_indicators = calculate_all_indicators(test_df)
    print(f"✅ 完整指标计算成功")
    print(f"   原始列数: {test_df.shape[1]}, 计算后列数: {df_with_indicators.shape[1]}")
    
    # 检查六因子
    six_factors = ['fisher', 'chop', 'lsma', 'hma', 'macd', 'vr']
    missing = [factor for factor in six_factors if factor not in df_with_indicators.columns]
    if missing:
        print(f"   缺失因子: {missing}")
    else:
        print(f"   所有六因子计算成功")
        
        # 显示六因子统计
        print(f"   六因子统计:")
        for factor in six_factors:
            mean_val = df_with_indicators[factor].mean()
            print(f"     {factor:10} 均值: {mean_val:8.3f}")
    
    # 检查综合得分
    if 'six_factor_score' in df_with_indicators.columns:
        score = df_with_indicators['six_factor_score'].mean()
        print(f"   六因子综合得分均值: {score:.3f}")
        
except Exception as e:
    print(f"❌ 完整指标计算失败: {e}")
    import traceback
    traceback.print_exc()