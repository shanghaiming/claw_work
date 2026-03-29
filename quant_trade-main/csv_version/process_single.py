from h11 import ERROR
import pandas as pd
from pathlib import Path
import numpy as np
import argparse
import os
import matplotlib.pyplot as plt
from numpy.lib.stride_tricks import sliding_window_view
import datetime
import logging

CONFIG = {
    "PERIODS": [5, 8, 13, 21, 34, 55],  # 需要计算的周期
    "MIN_DATA_DAYS": 55,                # 需要的最少数据天数
    "BATCH_SIZE": 300                  # 分批处理数量
}

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
            logging.FileHandler('app.log', encoding='UTF-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
)
logger = logging.getLogger(__name__)

def calculate_williams_r(data, period=5, high_col='high', low_col='low', close_col='close'):
    """
    计算威廉指标（Williams %R），适配DataFrame输入
    
    参数：
    data : DataFrame
        必须包含最高价、最低价、收盘价列（列名可自定义）
    period : int
        计算周期（默认14）
    high_col, low_col, close_col : str
        指定最高价、最低价、收盘价的列名
    
    返回：
    Series
        Williams %R值，与原始数据索引对齐
    """
    # 确保输入是DataFrame
    if not isinstance(data, pd.DataFrame):
        raise ValueError("输入数据必须是Pandas DataFrame")
    
    # 检查必要的列是否存在
    required_cols = [high_col, low_col, close_col]
    missing_cols = [col for col in required_cols if col not in data.columns]
    if missing_cols:
        raise KeyError(f"缺失必要列: {missing_cols}")
    
    # 计算滚动窗口内的最高价和最低价
    highest_high = data[high_col].rolling(window=period, min_periods=period).max()
    lowest_low = data[low_col].rolling(window=period, min_periods=period).min()
    
    # 计算Williams %R
    numerator = highest_high - data[close_col]
    denominator = highest_high - lowest_low
    williams_r1 = (numerator / denominator) * -100
    
    # 处理分母为零的情况（设为NaN）
    williams_r1 = williams_r1.where(denominator != 0, float('nan'))
    williams_r =williams_r1.ewm(span=period, adjust=False).mean()
    
    return williams_r.rename(f'Williams_%R_{period}')    

def process_single_stock(ts_code: str = "000001.SZ") -> bool:
    """处理单个 CSV 文件并生成分析结果
    
    Args:
        ts_code (str): 股票 TS 代码（默认: 000001.SZ），自动拼接 ".csv" 后缀
        
    Returns:
        bool: 处理是否成功
    """
    # 固定路径参数（直接修改函数体即可调整）
    data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'daily_data2')      # 数据目录
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)),'analysis_results')  # 输出目录
    
    csv_filename = f"{ts_code}.csv"
    input_path = Path(data_dir) / csv_filename
    output_path = Path(output_dir) / f"{ts_code}_analysis.csv"       
    required_columns = {
        'ts_code', 'trade_date', 'open', 'high', 
        'low', 'close', 'vol', 'change'
    }
    
    try:
        # 解析 trade_date 列并按时间降序排序（最新日期在前）
        # 读取原始数据（仅必要的列）
        df_raw = pd.read_csv(
            input_path,
            parse_dates=['trade_date'],
            usecols=lambda x: x in required_columns
        ).sort_values('trade_date', ascending=True)
        
        # 增量检查：如果分析结果已存在
        if output_path.exists():
            # 读取已有分析结果的最后日期
            existing_df = pd.read_csv(output_path, parse_dates=['trade_date'])
            last_processed_date = existing_df['trade_date'].max()
            logger.info(last_processed_date)
            
            # 筛选需要处理的新数据
            new_data = df_raw[df_raw['trade_date'] > last_processed_date]
            
            if new_data.empty:
                logger.info(f"✅ 无新数据需要处理: {ts_code}")
                return True
                
            logger.info(f"🔁 发现 {len(new_data)} 条新数据，进行增量计算")
            
            # 获取历史数据用于指标计算（保留足够的历史窗口）
            max_window = 55  # 最大计算窗口
            historical_data = df_raw[df_raw['trade_date'] <= last_processed_date].tail(max_window)
            
            # 合并历史数据和新数据
            df_combined = pd.concat([historical_data, new_data], ignore_index=False)
            df = df_combined.copy()
        else:
            logger.info(f"🆕 首次处理: {ts_code}")
            df = df_raw.copy()
        # 设置 ts_code 为索引并保留原列        
        df = df.rename(columns={'vol': 'volume'})
        df.set_index('trade_date', inplace=True)  # 设置日期为索引
        # 计算技术指标
        fast_ema = df['close'].ewm(span=12, adjust=False).mean()
        slow_ema = df['close'].ewm(span=26, adjust=False).mean()
        df['diff'] = fast_ema - slow_ema
        df['dea'] = df['diff'].ewm(span=9, adjust=False).mean()
        df['macd'] = 2 * (df['diff'] - df['dea'])

        df['ma5'] = df['close'].rolling(window=5).mean()
        df['ma8'] = df['close'].rolling(window=8).mean()
        df['ma13'] = df['close'].rolling(window=13).mean()
        df['ma21'] = df['close'].rolling(window=21).mean()
        df['ma34'] = df['close'].rolling(window=34).mean()
        df['ma55'] = df['close'].rolling(window=55).mean()
        df['LC'] = df['close'].shift(1)
        df['CLOSE_LC'] = df['close'] - df['LC']
        # 计算VR指标
        av = df['volume'].where(df['close'] > df['LC'], 0)
        bv = df['volume'].where(df['close'] < df['LC'], 0)
        cv = df['volume'].where(df['close'] == df['LC'], 0)
        df['vr'] = (av.rolling(26).sum() + cv.rolling(26).sum()/2) / \
              (bv.rolling(26).sum() + cv.rolling(26).sum()/2 + 1e-7) * 100

        variances = []
        closes = df['close'].values
        for period in CONFIG["PERIODS"]:
            period_data = closes[-period:]
            variances.append(np.var(period_data, ddof=1)/(closes*closes))  # 样本方差  
        df['var'] = np.mean(variances)        
        df['wr5'] = calculate_williams_r(df, period=5)
        df['wr55'] = calculate_williams_r(df, period=55)  
        df = df.drop(['LC','CLOSE_LC'], axis=1)

        # ===== 结果保存 =====
        if output_path.exists():
            # 增量模式：只追加新数据
            new_results = df.iloc[-len(new_data):]
            new_results.to_csv(output_path, mode='a', header=False, index=True)
        else:
            # 全量模式：创建新文件
            df.to_csv(output_path, index=True)

        return True
    
    except Exception as e:
        logger.error(f"❌ 文件加载失败: {input_path}")
        logger.error(f"错误详情: {e}")
        raise ValueError(f"错误详情: {e}")


def main():
    """单文件处理入口"""
    parser = argparse.ArgumentParser(description="处理单个股票数据文件")
    parser.add_argument(
        "-t", "--ts_code", 
        default="000001.SZ",  # 添加默认值
        type=str, 
        help="要处理的 TS 代码（默认: 000001.SZ）"
    )
    args = parser.parse_args()
    
    success = process_single_stock(args.ts_code)
    logger.info(f"\n最终结果: {'✅ 成功' if success else '⚠️ 失败'}")

if __name__ == "__main__":
    main()