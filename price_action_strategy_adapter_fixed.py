#!/usr/bin/env python3
"""
价格行为策略适配器（修复版）
修复配置问题，确保包含所有必要配置键
"""

import sys
import os
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

# 添加路径
sys.path.append('/Users/chengming/.openclaw/workspace')

print("=" * 80)
print("🚀 价格行为策略适配器（修复版）")
print("=" * 80)

# 导入价格行为引擎
try:
    from price_action_integration.optimized_integration_engine import OptimizedPriceActionIntegrationEngine
    from price_action_integration.price_action_rules_integrator import PriceActionRulesIntegrator
    print("✅ 成功导入价格行为策略模块")
except ImportError as e:
    print(f"❌ 导入失败: {e}")
    sys.exit(1)

# 获取引擎的默认配置
def get_default_engine_config() -> Dict[str, Any]:
    """获取价格行为引擎的完整默认配置"""
    # 创建临时引擎实例以获取默认配置
    temp_engine = OptimizedPriceActionIntegrationEngine()
    return temp_engine.config

# 简化的价格行为策略适配器
class SimplePriceActionStrategy:
    """简化版价格行为策略"""
    
    def __init__(self, params: Dict):
        self.params = params
        self.engine = None
        self.data = None
        
        # 使用完整配置
        self.engine_config = get_default_engine_config()
        
        # 合并用户参数
        if 'engine_config' in params:
            for key, value in params['engine_config'].items():
                if key in self.engine_config:
                    if isinstance(value, dict) and isinstance(self.engine_config[key], dict):
                        self.engine_config[key].update(value)
                    else:
                        self.engine_config[key] = value
        
        print(f"🔧 使用完整引擎配置:")
        for key in self.engine_config:
            print(f"   - {key}")
    
    def initialize(self, data: pd.DataFrame):
        """初始化"""
        self.data = data.copy()
        self.engine = OptimizedPriceActionIntegrationEngine(self.engine_config)
        self.engine.load_data(self.data)
        print("✅ 引擎初始化完成")
    
    def generate_signals(self) -> List[Dict]:
        """生成简化的交易信号"""
        if self.engine is None:
            raise ValueError("引擎未初始化")
        
        print("🎯 运行价格行为分析...")
        
        # 运行分析
        try:
            results = self.engine.run_analysis()
            print("✅ 分析完成")
        except Exception as e:
            print(f"❌ 分析失败: {e}")
            return []
        
        # 简化的信号生成逻辑
        signals = []
        
        # 使用补偿移动平均线生成信号（最简单的逻辑）
        cma_results = results.get('compensated_ma', {})
        if 'cma_values' in cma_results:
            cma_values = cma_results['cma_values']
            
            for i in range(1, len(self.data)):
                if i >= len(cma_values):
                    continue
                    
                current_price = self.data['close'].iloc[i]
                prev_price = self.data['close'].iloc[i-1]
                current_cma = cma_values[i]
                prev_cma = cma_values[i-1] if i > 0 else cma_values[i]
                
                current_time = self.data.index[i]
                
                # 简单交叉信号
                if prev_cma <= prev_price and current_cma > current_price:
                    signals.append({
                        'timestamp': current_time,
                        'action': 'buy',
                        'price': current_price,
                        'reason': 'cma_golden_cross'
                    })
                elif prev_cma >= prev_price and current_cma < current_price:
                    signals.append({
                        'timestamp': current_time,
                        'action': 'sell',
                        'price': current_price,
                        'reason': 'cma_death_cross'
                    })
        
        print(f"📊 生成 {len(signals)} 个信号")
        return signals

# 数据加载函数
def load_test_data():
    """加载测试数据"""
    data_dir = "/Users/chengming/.openclaw/workspace/quant_trade-main/data"
    file_path = os.path.join(data_dir, "daily_data2", "000001.SZ.csv")
    
    df = pd.read_csv(file_path)
    df['trade_date'] = pd.to_datetime(df['trade_date'], format='%Y%m%d')
    df.sort_values('trade_date', inplace=True)
    df.set_index('trade_date', inplace=True)
    
    # 重命名列
    column_mapping = {
        'open': 'open',
        'high': 'high',
        'low': 'low',
        'close': 'close',
        'vol': 'volume'
    }
    
    result_df = pd.DataFrame()
    for old_col, new_col in column_mapping.items():
        if old_col in df.columns:
            result_df[new_col] = df[old_col]
    
    # 截取部分数据以加快测试
    result_df = result_df.iloc[:200]  # 前200个交易日
    
    print(f"✅ 加载测试数据: {len(result_df)} 行")
    return result_df

# 与现有回测框架集成
def run_simple_backtest(signals: List[Dict], data: pd.DataFrame):
    """运行简单回测"""
    if not signals:
        print("❌ 无信号，跳过回测")
        return None
    
    # 简单回测逻辑
    initial_capital = 1000000
    capital = initial_capital
    position = 0
    entry_price = 0
    
    trades = []
    
    for signal in signals:
        if signal['action'] == 'buy' and position == 0:
            # 买入
            position = 1
            entry_price = signal['price']
            trades.append({
                'timestamp': signal['timestamp'],
                'action': 'buy',
                'price': entry_price
            })
        elif signal['action'] == 'sell' and position == 1:
            # 卖出
            position = 0
            exit_price = signal['price']
            pnl = (exit_price - entry_price) / entry_price
            trades.append({
                'timestamp': signal['timestamp'],
                'action': 'sell',
                'price': exit_price,
                'pnl': pnl
            })
    
    # 计算绩效
    if trades:
        sell_trades = [t for t in trades if t['action'] == 'sell']
        if sell_trades:
            total_return = sum(t['pnl'] for t in sell_trades) / len(sell_trades)
            win_trades = [t for t in sell_trades if t['pnl'] > 0]
            win_rate = len(win_trades) / len(sell_trades) if sell_trades else 0
            
            print(f"\n📈 回测结果:")
            print(f"   交易次数: {len(sell_trades)}")
            print(f"   平均收益率: {total_return:.2%}")
            print(f"   胜率: {win_rate:.2%}")
            
            return {
                'trades_count': len(sell_trades),
                'avg_return': total_return,
                'win_rate': win_rate
            }
    
    return None

# 主函数
def main():
    print("\n🔬 开始价格行为策略测试...")
    
    # 1. 加载数据
    data = load_test_data()
    
    # 2. 创建策略
    params = {
        'engine_config': {
            'pivot_detection': {'prominence_factor': 0.5},
            'compensated_ma': {'window': 20}
        }
    }
    
    strategy = SimplePriceActionStrategy(params)
    
    # 3. 初始化
    strategy.initialize(data)
    
    # 4. 生成信号
    signals = strategy.generate_signals()
    
    # 5. 运行回测
    if signals:
        results = run_simple_backtest(signals, data)
        
        # 6. 保存结果
        signals_df = pd.DataFrame(signals)
        output_path = "/Users/chengming/.openclaw/workspace/price_action_test_results.csv"
        signals_df.to_csv(output_path, index=False)
        print(f"\n💾 信号保存到: {output_path}")
        
        if results:
            print("\n🎉 价格行为策略测试成功!")
            print(f"✅ 适配器开发完成")
            print(f"✅ 策略集成完成")
            print(f"✅ 回测运行完成")
            
            # 更新任务管理器
            update_task_manager(results)
        else:
            print("\n⚠️ 信号生成但回测失败")
    else:
        print("\n❌ 未生成任何信号")

def update_task_manager(results: Dict):
    """更新任务管理器状态"""
    try:
        import json
        import datetime
        
        task_manager_path = "/Users/chengming/.openclaw/workspace/quant_strategy_task_manager.json"
        
        with open(task_manager_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 更新task_001状态
        current_time = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).isoformat()
        
        for task in data['current_task_queue']['tasks']:
            if task['task_id'] == 'task_001':
                task['status'] = 'COMPLETED'
                task['completion_time'] = current_time
                task['output_files'] = ["price_action_test_results.csv"]
                task['results'] = results
                break
        
        # 更新最后时间
        data['task_system']['last_updated'] = current_time
        
        # 写入更新
        with open(task_manager_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 任务管理器更新完成")
        
    except Exception as e:
        print(f"⚠️ 更新任务管理器失败: {e}")

if __name__ == "__main__":
    main()
    print("\n" + "=" * 80)
    print("🏁 程序结束")