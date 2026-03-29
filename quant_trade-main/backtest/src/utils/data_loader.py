import os
import glob
import pandas as pd

def load_data(timeframe: str, symbol: str) -> pd.DataFrame:
    """
    严格匹配唯一文件（必须且只能存在一个匹配文件）
    :param timeframe: 时间周期（5min/30min）
    :param symbol: 股票代码（格式：数字.字母，如000063.SZ）
    """
    try:
        # ----- 路径构建 -----
        base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        target_dir = os.path.join(base_dir, "data", "analyzed", timeframe)
        
        # ----- 文件名匹配逻辑 -----
        safe_symbol = glob.escape(symbol)
        file_pattern = os.path.join(target_dir, f"{safe_symbol}*.csv")
        matched_files = glob.glob(file_pattern)
        
        # ----- 严格文件数量检查 -----
        if len(matched_files) > 1:
            raise ValueError(f"发现多个匹配文件:\n" + "\n".join(matched_files))
        if not matched_files:
            raise FileNotFoundError(f"找不到匹配文件: {symbol}*.csv 在目录 {target_dir}")
        
        # ----- 单文件读取与校验 -----
        file_path = matched_files[0]
        
        # 尝试读取文件并处理列名
        df = pd.read_csv(file_path, parse_dates=['trade_date'])
        df.set_index('trade_date', inplace=True)
        
        # 检查必要列是否存在
        required_columns = {'open', 'high', 'low', 'close'}
        missing = required_columns - set(df.columns)
        if missing:
            raise ValueError(f"文件 {file_path} 缺少必要列: {missing}")
            
        return df.sort_index()

    except ValueError as ve:
        # 处理列名缺失的特定错误
        if "Missing column provided to 'parse_dates'" in str(ve):
            try:
                # 尝试获取实际列名帮助调试
                cols = pd.read_csv(file_path, nrows=0).columns.tolist()
                new_msg = f"CSV文件缺少'trade_date'列，现有列名: {cols}"
                raise ValueError(new_msg) from None
            except:
                raise ValueError("文件格式错误，无法读取列名") from None
        raise ValueError(f"数据验证失败: {str(ve)}") from ve
        
    except FileNotFoundError as fe:
        raise FileNotFoundError(f"数据文件不存在: {str(fe)}") from fe
        
    except Exception as e:
        raise RuntimeError(f"数据加载失败: {str(e)}") from e