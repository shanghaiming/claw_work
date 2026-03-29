import pandas as pd
from pathlib import Path
import talib
import numpy as np
import argparse
import os
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上上一级目录
def calculate_kdj_talib(close, high, low, n=9):
    """
    基于 TA-Lib 的 KDJ 指标计算
    """
    # 计算 N 日极值
    max_high = high.rolling(window=n).max()
    min_low = low.rolling(window=n).min()
    
    # 计算 RSV
    rsv = (close - min_low) / (max_high - min_low)
    
    # 计算 K/D/J
    k = talib.SMA(rsv, timeperiod=3)
    d = talib.SMA(k, timeperiod=3)
    j = 3 * k - 2 * d
    
    return k, d, j

def process_single_stock(ts_code: str = "000001.SZ") -> bool:
    """处理单个 CSV 文件并生成分析结果
    
    Args:
        ts_code (str): 股票 TS 代码（默认: 000001.SZ），自动拼接 ".csv" 后缀
        
    Returns:
        bool: 处理是否成功
    """
    # 固定路径参数（直接修改函数体即可调整）
    output_dir = os.path.join(SCRIPT_DIR, "../data/analyzed/30min")# 输出目录)
    data_dir = os.path.join(SCRIPT_DIR, "../data/raw/30min")    # 数据目录
    
    csv_filename = f"{ts_code}.csv"
    input_path = Path(data_dir) / csv_filename
    output_path = Path(output_dir) / f"{ts_code}_analysis.csv"
    
    required_columns = {
        'ts_code', 'datetime', 'open', 'high', 
        'low', 'close', 'volume', 'amount','name','industry','circ_mv'
    }
    
    try:
        # 解析 trade_date 列并按时间降序排序（最新日期在前）
        df_raw = pd.read_csv(
            input_path,
            parse_dates=['datetime'],  # 解析日期列为 datetime 类型
            usecols=lambda x: x in required_columns
        )
        #df_raw = df_raw.sort_values(by='trade_date', ascending=True)  # 反向排序
        
        #print(f"✅ 实际读取的列名: {df_raw.columns.tolist()}")
        
        # 设置 ts_code 为索引并保留原列
        df = df_raw.set_index('ts_code', drop=False)
        df = df.rename(columns={'datetime': 'trade_date'})
        # 计算技术指标
        close_prices = df['close'].values
        macd, signal, hist = talib.MACD(
            close_prices,
            fastperiod=12, slowperiod=26, signalperiod=9
        )
        df['macd'] = macd
        df['macd_signal'] = signal
        df['macd_his'] = hist 
        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma8'] = df['close'].rolling(window=8).mean()
        df['ma13'] = df['close'].rolling(window=13).mean()
        df['ma21'] = df['close'].rolling(window=21).mean()
        df['rsi'] = talib.RSI(df['close'], timeperiod=14)
        
        
        # 计算 KDJ
        n = 9  # KDJ 默认周期
        if len(df) >= n:
            # 确保数据是按日期排序的
            #df_sorted = df.sort_values('trade_date').reset_index(drop=True)
            kdj_k, kdj_d, kdj_j = calculate_kdj_talib(
                df['close'],
                df['high'],
                df['low'],
                n  # ✅ 明确传递 n 参数
            )
            df['k'] = kdj_k
            df['d'] = kdj_d
            df['j'] = kdj_j
        else:
            print("⚠️ 数据量不足，KDJ 需要至少9日数据")
        # 保存结果到 CSV
        #print(df['kdj_d'])
        df.to_csv(output_path, index=False)
        #print(f"✅ 分析结果已保存: {output_path}")
        #df = df.dropna(subset=['ma5', 'rsi', 'macd', 'macd_signal', 'kdj_k', 'kdj_d', 'kdj_j'])
        return True
    
    except Exception as e:
        print(f"❌ 文件加载失败: {input_path}")
        print(f"错误详情: {e}")
        return None
def main():
    """单文件处理入口"""
    parser = argparse.ArgumentParser(description="处理单个股票数据文件")
    parser.add_argument(
        "-t", "--ts_code", 
        default="000063.SZ",  # 添加默认值
        type=str, 
        help="要处理的 TS 代码（默认: 000001.SZ）"
    )
    args = parser.parse_args()
    
    success = process_single_stock(args.ts_code)
    #print(f"\n最终结果: {'✅ 成功' if success else '⚠️ 失败'}")

if __name__ == "__main__":
    main()