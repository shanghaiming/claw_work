import os
import sys
from h11 import ERROR
import pandas as pd
from datetime import datetime, timedelta
from sympy import true
import tushare as ts
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import logging
import psutil

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
            logging.FileHandler('app.log', encoding='UTF-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
)
logger = logging.getLogger(__name__)
# 自定义分块函数
def chunks(lst, size):
    for i in range(0, len(lst), size):
        yield lst[i:i+size]

# 配置参数
TOKEN = '304d18af85c89131420917d9378d91824a3e12246c7f160b89b746c7'  # 替换为您的实际Token
STOCK_LIST_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'stocks_list.csv')  # 本地股票列表文件
DAILY_DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'daily_data2')   # 存放日线数据的文件夹
EXCHANGE = 'SSE'             # 交易所代码（上海主板）

#BATCH_SIZE = 1             # 每个线程处理的股票数量 初次
BATCH_SIZE = 1000             # 每个线程处理的股票数量 增量 <6000/time interval
THREAD_POOL_SIZE = 1         # 线程池大小（根据网络环境调整）

# 新增常量定义
LAST_RUN_FILE = os.path.join(DAILY_DATA_DIR, 'last_run_date.txt')  # 存储最后运行日期的文件路径

def init_pro():
    return ts.pro_api(TOKEN)

def get_last_trade_day(pro):
    try:
        now = datetime.now()
        if now.hour >= 15:
         end_date = now.strftime('%Y%m%d')
        else:
         end_date = (now - timedelta(days=1)).strftime('%Y%m%d')
    
        start_date_cal = (now - timedelta(days=365)).strftime('%Y%m%d')
        df = pro.trade_cal(exchange=EXCHANGE, start_date=start_date_cal, end_date=end_date, is_open=1)
    
        if df.empty:
            raise ValueError("未找到有效交易日数据")
    except ValueError as e:
        logger.error(f"[ERROR] fetch_data failed: {e}")
        raise ERROR
       
    return df['cal_date'].max()

def load_stock_list(pro, stock_list_file):
    """
    加载本地股票列表，如果不存在则从Tushare获取并保存。
    
    参数：
    - pro: Tushare Pro接口实例
    - stock_list_file (str): 股票列表文件路径
    
    返回：
    - stock_df (DataFrame): 股票列表
    """
    if os.path.exists(stock_list_file):
        stock_df = pd.read_csv(stock_list_file)
        stock_df = stock_df['ts_code'].tolist()
        logger.info(f"已加载本地股票列表，共 {len(stock_df)} 条数据")
    else:
        logger.info("本地不存在股票列表文件，正在从Tushare拉取...")
        stock_df = pro.stock_basic(
            ts_code='',
            name='',
            exchange='',
            list_status='L',
            fields=[
                "ts_code",
                "symbol",
                "name",
                "area",
                "industry",
                "list_date"
            ]
        )
        if not stock_df.empty:
            stock_df.to_csv(stock_list_file, index=False, encoding='utf-8-sig')
            stock_df = stock_df['ts_code'].tolist()
            logger.info(f"股票列表已保存到 {stock_list_file}")
        else:
            raise ValueError("未获取到股票数据。")
    return stock_df

def fetch_data(pro, ts_codes, start_date_str, end_date_str):
    start_time = time.time()
    try:
        all_data = pd.DataFrame()
        current_end = datetime.strptime(start_date_str, '%Y%m%d')
        end_date = datetime.strptime(end_date_str, '%Y%m%d')
        
        # 检查日期范围是否有效
        if current_end > end_date:
            logging.info(f"[WARN] 无效日期范围: {start_date_str} > {end_date_str}")
            return pd.DataFrame()
        
        while current_end <= end_date:
            batch_end = min(current_end + timedelta(days=6000), end_date)
            batch_end_str = batch_end.strftime('%Y%m%d')
            
            # 统计API请求耗时
            api_start = time.time()
            df = pro.daily(ts_code=','.join(ts_codes), 
                           start_date=current_end.strftime('%Y%m%d'), 
                           end_date=batch_end_str,
                           fields=[
            "ts_code", "trade_date", "open", "high", "low", "close", "pre_close",
            "change", "pct_chg", "vol", "amount"
        ])
            api_duration = time.time() - api_start
            logging.info(f"[DEBUG] API请求耗时: {api_duration:.2f}秒, 股票数: {len(ts_codes)}")        
            if not df.empty:
                all_data = pd.concat([all_data, df])
                
            else: 
                logging.info(f"[WARN] 未获取到股票数据: {','.join(ts_codes)}") 
                raise
             
            current_end = batch_end + timedelta(days=1)
            
        all_data = all_data[all_data['trade_date'].str.match(r'^\d{8}$')]
        all_data['trade_date'] = all_data['trade_date'].astype(str)
        
        return all_data
    except Exception as e:
        logger.error(f"[ERROR] fetch_data failed: {e}")
        raise ERROR
        #return pd.DataFrame()

def save_data(df, data_dir):
    try:
        # 强制全局排序
        df['trade_date'] = df['trade_date'].astype(int)
        df = df.sort_values('trade_date',ascending=False).reset_index(drop=True)
        df = df[["ts_code", "trade_date", "open", "high", "low", "close", "pre_close",
                "change", "pct_chg", "vol", "amount"
            ]]
        df = df.drop_duplicates(subset=['ts_code', 'trade_date'])
        
        for ts_code in df['ts_code'].unique():
            file_path = os.path.join(data_dir, f"{ts_code}.csv")
            subset = df[df['ts_code'] == ts_code]
            
            # 如果文件已存在，则读取现有数据并合并
            if os.path.exists(file_path):
                existing_df = pd.read_csv(file_path)
                # 合并新旧数据
                combined = pd.concat([existing_df, subset]).drop_duplicates(subset=['trade_date'])
                combined = combined.sort_values('trade_date', ascending=False)
                combined.to_csv(file_path, index=False)
                logger.info(f"Updated {len(subset)} records for {ts_code} (total: {len(combined)})")
            else:
                subset.to_csv(file_path, index=False)
                logger.info(f"Saved {len(subset)} records for {ts_code}")
    except Exception as e:
        logger.error(f"[ERROR] fetch_data failed: {e}", file=sys.stderr)
        raise ERROR

def save_last_run_date(last_date: str):
    """保存最后运行日期到文件"""
    try:
        with open(LAST_RUN_FILE, 'w') as f:
            f.write(last_date)
        logger.info(f"成功保存最后运行日期: {last_date}")
    except Exception as e:
        logger.error(f"保存最后运行日期失败: {str(e)}")
        raise

def load_last_run_date():
    """加载最后运行日期"""
    if os.path.exists(LAST_RUN_FILE):
        with open(LAST_RUN_FILE, 'r') as f:
            return f.read().strip()
    
class PerformanceMonitor:
    def __init__(self):
        self.start_time = time.time()
        self.data_count = 0
    
    def record(self, message):
        elapsed = time.time() - self.start_time
        self.data_count += 1
        logging.info(f"[PERFORMANCE] {message} - 总耗时: {elapsed:.2f}秒, 已处理数据: {self.data_count}")

def process_stocks(pro, stock_list, data_dir):
    monitor = PerformanceMonitor()
    monitor.record("初始化完成")
    
    # 获取最后交易日
    last_trade_day = get_last_trade_day(pro)
    end_date_str = last_trade_day
    
    # 获取上次运行日期
    last_run_date = load_last_run_date()
    
    # 设置起始日期
    if last_run_date:
        # 使用上次运行日期的下一天作为起始
        start_date = (datetime.strptime(last_run_date, '%Y%m%d') + timedelta(days=1)).strftime('%Y%m%d')
        logger.info(f"增量更新模式: {start_date} 至 {end_date_str}")
    else:
        # 首次运行，获取1000天数据
        start_date = (datetime.strptime(end_date_str, '%Y%m%d') - timedelta(days=5000)).strftime('%Y%m%d')
        logger.info(f"全量更新模式: {start_date} 至 {end_date_str}")
    
    if start_date > end_date_str:
        logger.info("无需更新：起始日期大于结束日期")
        return
    
    # 使用线程池并行处理批次
    with ThreadPoolExecutor(max_workers=THREAD_POOL_SIZE) as executor:
        future_to_batch = {}
        for batch in chunks(stock_list, BATCH_SIZE):
            future = executor.submit(fetch_data, pro, batch, start_date, end_date_str)
            future_to_batch[future] = batch
        
        for future in as_completed(future_to_batch):
            batch = future_to_batch[future]
            try:
                batch_data = future.result()
                if not batch_data.empty:
                    save_data(batch_data, data_dir)
                    monitor.record(f"保存数据: {batch}")
            except Exception as e: 
                logger.error(f"[ERROR] Batch {batch} processing failed: {e}")
                raise ERROR
    
    # 保存本次运行日期
    save_last_run_date(last_trade_day)

def fetch_daily_batch():
    pro = init_pro()
    stock_list = load_stock_list(pro, STOCK_LIST_FILE)
    
    # 监控进程资源
    process = psutil.Process(os.getpid())
    
    try:
        process_stocks(pro, stock_list, DAILY_DATA_DIR)
        return True
    except Exception as e:
        logger.error(f"[ERROR] 主程序异常: {e}")
        raise ERROR
    finally:
        # 终止监控并输出最终资源占用
        logger.info(f"[PERFORMANCE] 程序终止 - 内存占用: {process.memory_info().rss / 1024 ** 2:.2f}MB")
        logger.info(f"[PERFORMANCE] CPU占用: {process.cpu_percent(interval=1)}%")


if __name__ == "__main__":
    fetch_daily_batch()