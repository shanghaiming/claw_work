import pandas as pd
from pathlib import Path
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from process_single import process_single_stock  # ✅ 确保已导入
import os
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上上一级目录
def process_batch():
    """批处理入口"""
    parser = argparse.ArgumentParser(description="批量处理股票数据文件")
    parser.add_argument(
        "-t", "--target_file",  # ✅ 添加短选项 -t
        type=str, 
        help="要处理的特定 TS 代码（如 000001.SZ），使用 -t 可快速输入"
    )
    args = parser.parse_args()
    
    # 固定路径参数（直接修改函数体即可调整）
    output_dir = os.path.join(SCRIPT_DIR, "../data/analyzed/5min")# 输出目录)
    data_dir = os.path.join(SCRIPT_DIR, "../data/raw/5min")    # 数据目录
    
    # 获取待处理文件列表
    if args.target_file:
        file_list = [Path(data_dir) / f"{args.target_file}.csv"]
    else:
        file_list = list(Path(data_dir).glob("*.csv"))
    
    # 并行处理配置
    #max_workers = min(320, len(file_list))  # 根据 CPU 核数调整
    max_workers = 10
    executor = ThreadPoolExecutor(max_workers=max_workers)
    future_to_ts_code = {
    executor.submit(process_single_stock, csv_file.stem): csv_file.stem
    for csv_file in file_list
    }
    
    processed_count = 0
    failed_count = 0
    failure_log = []
    
    for future in as_completed(future_to_ts_code):
        ts_code = future_to_ts_code[future]
        try:
            success = future.result()
            if success:
                processed_count += 1
            else:
                failed_count += 1
                failure_log.append(ts_code)
        except Exception as e:
            print(f"\n❌ 文件 {ts_code} 处理异常:", str(e))
            failed_count += 1
            failure_log.append(ts_code)
    
    # 输出统计结果
    print(f"\n批量处理完成:")
    print(f"✅ 成功处理: {processed_count} 个文件")
    print(f"⚠️ 失败处理: {failed_count} 个文件")
    if failure_log:
        print(f"失败文件列表: {', '.join(failure_log)}")

if __name__ == "__main__":
   process_batch() 