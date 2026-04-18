#!/usr/bin/env python3
"""
选股功能模块
基于csv_auto_select.py的选股功能
"""
import os
import sys
import json

project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

def run_stock_selection(strategy_id=1, output_format='text'):
    """
    运行选股功能
    
    Args:
        strategy_id: 策略ID (1-5)
        output_format: 输出格式 ('text', 'json', 'csv')
    """
    try:
        # 导入选股函数
        from strategies.csv_auto_select import auto_select
        
        print(f"🔍 开始选股 (策略ID: {strategy_id})")
        print("=" * 50)
        
        # 执行选股
        selected_stocks = auto_select(strategy_id=strategy_id)
        
        if not selected_stocks:
            print("❌ 选股失败，未返回股票列表")
            return None
            
        print(f"✅ 选股完成，找到 {len(selected_stocks)} 只股票")
        
        # 输出结果
        if output_format == 'json':
            result = {
                'strategy_id': strategy_id,
                'selected_stocks': selected_stocks,
                'count': len(selected_stocks)
            }
            return json.dumps(result, ensure_ascii=False, indent=2)
        elif output_format == 'csv':
            csv_output = "股票代码\n"
            for stock in selected_stocks:
                csv_output += f"{stock}\n"
            return csv_output
        else:  # text
            print("\n📈 推荐股票列表:")
            print("-" * 30)
            for i, stock in enumerate(selected_stocks, 1):
                print(f"{i:3d}. {stock}")
            print("-" * 30)
            print(f"总计: {len(selected_stocks)} 只股票")
            print("=" * 50)
            
            # 同时保存到文件
            output_file = os.path.join(project_root, 'selected_stocks.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                for stock in selected_stocks:
                    f.write(f"{stock}\n")
            print(f"📄 结果已保存到: {output_file}")
            
            return selected_stocks
            
    except Exception as e:
        print(f"❌ 选股过程出错: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == '__main__':
    # 简单测试
    import argparse
    parser = argparse.ArgumentParser(description='选股功能测试')
    parser.add_argument('--strategy-id', type=int, default=1, help='策略ID (1-5)')
    parser.add_argument('--format', choices=['text', 'json', 'csv'], default='text', help='输出格式')
    
    args = parser.parse_args()
    result = run_stock_selection(args.strategy_id, args.format)
    
    if args.format == 'json' and result:
        print(result)
    elif args.format == 'csv' and result:
        print(result)