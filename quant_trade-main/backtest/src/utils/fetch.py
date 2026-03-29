import os
import pandas as pd
import logging
import re

# 获取当前脚本的上上一级目录
SCRIPT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # 上上一级目录
CONFIG = {
    "DATA_BASE_DIR": "/Users/chengming/Downloads/",  # 替换成您的绝对路径
    "LOG_DIRECTORY": SCRIPT_DIR,
    "INPUT_STOCKS_FILE": os.path.join(SCRIPT_DIR, "config", "selected_stocks.csv"),  # 动态路径
    "OUTPUT_COLUMNS": ["datetime", "open", "high", "low", "close", "volume", "amount"],  
    "DATE_FORMAT": "%Y-%m-%d %H:%M:%S"
}

def setup_logging():
    """初始化日志系统"""
    log_dir = CONFIG["LOG_DIRECTORY"]
    try:
        if not os.path.isdir(log_dir):
            os.makedirs(log_dir)
            logging.info(f"Created log directory: {log_dir}")
    except Exception as e:
        logging.error(f"Failed to create log directory: {str(e)}")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
        handlers=[
            logging.FileHandler(os.path.join(log_dir, "data_loader.log")),
            logging.StreamHandler()
        ]
    )

def load_selected_stocks(config_path):
    """加载选股列表，带异常处理"""
    try:
        logging.info(f"Loading selected stocks from: {config_path}")
        df = pd.read_csv(config_path)
        
        # 确保必要列存在
        required_columns = ["ts_code", "name", "industry", "circ_mv"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            logging.warning(f"Missing columns in config file: {missing_cols}")
            return pd.DataFrame()
        
        # 返回指定列的数据框（不进行任何NA过滤）
        return df[required_columns]
    except FileNotFoundError:
        logging.error(f"Config file not found: {config_path}")
        return pd.DataFrame()
    except pd.errors.ParserError:
        logging.error(f"Failed to parse config file: {config_path}")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Unexpected error loading stocks: {str(e)}")
        return pd.DataFrame()

def parse_stock_data(file_path):
    """解析单只股票数据文件，严格保留NA值"""
    try:
        logging.info(f"Parsing stock data from: {file_path}")
        # 读取所有列并过滤无效列
        df = pd.read_csv(
            file_path,
            usecols=lambda x: x.strip() and x != "index"
        )
        
        # 动态获取数据列名
        file_columns = df.columns.tolist()
        logging.debug(f"File columns detected: {file_columns}")
        
        # 安全过滤输出列（仅保留数据文件和配置要求的列）
        valid_columns = list(set(file_columns) & set(CONFIG["OUTPUT_COLUMNS"]))
        df = df[valid_columns]
        
        # 转换数值列为浮点数（非强制，保留原始类型）
        numeric_cols = ["open", "high", "low", "close", "amount", "volume"]
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df
    
    except Exception as e:
        logging.error(f"Unexpected error parsing data: {str(e)}")
        return pd.DataFrame()

def batch_load_stock_data(stocks, start_year, end_year):
    """批量加载股票数据，逐文件校验路径和完整性"""
    stock_data = {}  # 使用字典存储各股票数据，键为ts_code
    for stock in stocks:
        ts_code, name, industry, circ_mv = stock  # 解包所有字段
        
        year_data = []
        for year in range(start_year, end_year + 1):
            # 动态生成文件名（交换ts_code的前后部分）
            parts = ts_code.split('.')
            if len(parts) != 2:
                logging.warning(f"Invalid ts_code format: {ts_code}")
                continue
            file_name = f"{parts[1]}.{parts[0]}.csv"
            
            # 生成文件路径
            file_path = os.path.join(
                CONFIG["DATA_BASE_DIR"], 
                str(year), 
                file_name
            )
            
            # 校验路径存在性
            if not os.path.exists(file_path):
                logging.warning(f"File not found: {file_path}")
                continue
            
            # 解析数据
            df = parse_stock_data(file_path)
            if not df.empty:
                year_data.append(df)
        
        # 合并该股票各年份数据
        if year_data:
            combined = pd.concat(year_data).sort_values("datetime").reset_index(drop=True)
            # 注入股票信息
            combined["ts_code"] = ts_code
            combined["name"] = name
            combined["industry"] = industry
            combined["circ_mv"] = circ_mv
            stock_data[ts_code] = combined
    
    return stock_data


def resample_30min(df):
    """将5分钟数据重采样为30分钟数据"""
    try:
        # 确保datetime是正确的时间类型并设为索引
        df = df.copy()
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.set_index('datetime', inplace=True)
        
        # 定义重采样规则
        resample_rules = {
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum',
            'amount': 'sum'
        }
        
        # 执行重采样
        df_30min = df.resample('30min').agg(resample_rules).dropna()
        
        # 重置索引并重新排序
        df_30min = df_30min.reset_index()
        df_30min = df_30min[CONFIG["OUTPUT_COLUMNS"]]  # 保持列顺序
        
        return df_30min
    except Exception as e:
        logging.error(f"Resampling failed: {str(e)}")
        return pd.DataFrame()

def save_stock_data(data_dict, output_dir):
    """保存不同时间周期的股票数据"""
    # 创建输出目录结构
    dir_5min = os.path.join(output_dir, "5min")
    dir_30min = os.path.join(output_dir, "30min")
    os.makedirs(dir_5min, exist_ok=True)
    os.makedirs(dir_30min, exist_ok=True)
    
    for ts_code, df in data_dict.items():
        try:
            # 原始5分钟数据
            raw_path = os.path.join(dir_5min, f"{ts_code}.csv")
            df.to_csv(raw_path, index=False)
            logging.info(f"Saved 5min data: {raw_path}")
            
            # 生成30分钟数据
            df_30min = resample_30min(df)
            if not df_30min.empty:
                # 添加元数据列
                df_30min['ts_code'] = ts_code.split('_')[0]  # 移除可能的后缀
                resampled_path = os.path.join(dir_30min, f"{ts_code}_30min.csv")
                df_30min.to_csv(resampled_path, index=False)
                logging.info(f"Saved 30min data: {resampled_path}")
                
        except Exception as e:
            logging.error(f"Failed to save {ts_code} data: {str(e)}")

if __name__ == "__main__":
    setup_logging()
    
    # 加载选股列表
    stocks_df = load_selected_stocks(CONFIG["INPUT_STOCKS_FILE"])
    if stocks_df.empty:
        logging.error("No valid stocks loaded")
        exit()
    
    # 批量加载数据
    start_year = 2022
    end_year = 2024
    data = batch_load_stock_data(stocks_df.itertuples(index=False, name=None), start_year, end_year)
    
    # 保存结果（包含5分钟和30分钟数据）
    output_dir = os.path.join(SCRIPT_DIR,  "../data/raw")
    save_stock_data(data, output_dir)