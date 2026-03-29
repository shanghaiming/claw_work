import tushare as ts
import pandas as pd
from datetime import datetime, timedelta
import time
import os

YOUR_TUSHARE_TOKEN = '304d18af85c89131420917d9378d91824a3e12246c7f160b89b746c7'
EXCHANGE = 'SSE'             # 交易所代码（上海主板）
def main():
    # 设置Tushare凭证
    ts.set_token(YOUR_TUSHARE_TOKEN)
    pro = ts.pro_api()

    # 1. 获取基础数据
    print("正在获取基础数据...")
    df_basic = pro.stock_basic(
        exchange='',
        list_status='L',
        fields='ts_code,symbol,name,area,industry,list_date'
    )
    now = datetime.now()
    if now.hour >= 16:
        end_date = now.strftime('%Y%m%d')
    else:
        end_date = (now - timedelta(days=1)).strftime('%Y%m%d')
    
    start_date_cal = (now - timedelta(days=365)).strftime('%Y%m%d')
    df = pro.trade_cal(exchange=EXCHANGE, start_date=start_date_cal, end_date=end_date, is_open=1)
    latest_trade_date = df['cal_date'].max()
    print(latest_trade_date)
    # 打印基础数据样例（使用安全格式）
    print("\n基础数据样例：")
    #print(df_basic.head(3).to_string(index=False))  # 修复tabulate依赖问题

    

    df_daily = pro.daily(
        start_date='20100106',
        end_data='20250306',
        fields='ts_code,amount'
    )
    # 3. 合并数据（显式保留所有列）
    df = pd.merge(
        df_basic,
        df_daily,
        on='ts_code',
        how='left',
        suffixes=('', '_daily')
    )
    # 验证关键列
    if 'industry' not in df.columns:
        raise ValueError("合并后数据丢失industry字段")
    
    # 4. 基础过滤（可视化条件）
    print("\n执行基础过滤...")
    df_filtered = basic_filters(df)
    
    # 处理空数据情况
    if len(df_filtered) == 0:
        print("错误：基础过滤后无有效股票，请检查：")
        print("1. 当前日均成交额阈值：5000万元（可尝试降低）")
        print(f"2. 上市时间要求：≥{datetime.now().year - 3}年前上市")
        print("3. 是否所有ST股已被排除")
        return

    # 5. 市值分层
    print("\n执行市值分层筛选...")
    df_stratified = market_cap_stratification(df_filtered, pro, latest_trade_date)
    print(df_stratified)
    # 6. 行业均衡
    print("\n执行行业均衡调整...")
    df_final = industry_balancing(df_stratified, target_count=200)

    # 7. 结果验证
    validate_selection(df_final)

def basic_filters(df):
    # 条件1：排除ST股
    df = df[~df['name'].str.contains('ST')].copy()  # 避免SettingWithCopyWarning

    # 条件2：上市时间≥3年
    df.loc[:, 'list_date'] = pd.to_datetime(df['list_date'])
    three_years_ago = pd.to_datetime(datetime.now() - pd.DateOffset(years=3))
    df = df[df['list_date'] <= three_years_ago]

    # 条件3：日均成交额≥5000万（单位：元）
    df = df[df['amount'] >= 500000]

    return df

def market_cap_stratification(df, pro, trade_date):
    # 获取市值数据
    df_fina = pro.daily_basic(
        trade_date=trade_date,
        fields='ts_code,circ_mv'
    )
    
    # 安全合并（保留industry列）
    df = df.merge(
        df_fina,
        on='ts_code',
        how='left',
        suffixes=('', '_fina')
    )
    
    # 检查industry列
    if 'industry' not in df.columns:
        raise ValueError("合并后数据丢失industry字段")

    # 市值分层
    df['circ_mv_b'] = df['circ_mv'] / 10000  # 将万元转换为亿元
    df['scale'] = pd.cut(
        df['circ_mv_b'],
        bins=[0, 100, 500, float('inf')],
        labels=['small', 'mid', 'large']
    )

    # 安全抽样
    small_n = min(40, len(df[df['scale'] == 'small']))
    mid_n = min(100, len(df[df['scale'] == 'mid']))
    large_n = min(60, len(df[df['scale'] == 'large']))

    small = df[df['scale'] == 'small'].sample(n=small_n) if small_n > 0 else pd.DataFrame()
    mid = df[df['scale'] == 'mid'].sample(n=mid_n) if mid_n > 0 else pd.DataFrame()
    large = df[df['scale'] == 'large'].sample(n=large_n) if large_n > 0 else pd.DataFrame()

    return pd.concat([small, mid, large])

def industry_balancing(df, target_count=200):
    selected = []
    industry_counts = df['industry'].value_counts()
    total_samples = 0

    # 按行业比例抽样
    for industry in industry_counts.index:
        sub_df = df[df['industry'] == industry]
        n = max(1, int(target_count * (len(sub_df)/len(df))))
        if len(sub_df) > 0:
            selected.extend(sub_df.sample(n=min(n, len(sub_df))).index)
            total_samples += n

    # 补充剩余名额
    if total_samples < target_count:
        remaining = target_count - total_samples
        candidates = df.index.difference(selected)
        if len(candidates) > 0:
            selected.extend(
                candidates.to_series().sample(remaining, replace=True).tolist()
            )

    return df.loc[selected].sample(target_count, replace=len(selected)<target_count)

def validate_selection(df):
    print("\n--- 最终筛选结果 ---")
    print(f"股票数量：{len(df)}")
    
    # 打印统计信息
    print("\n行业分布：")
    print(df['industry'].value_counts().head(10).to_string())
    
    print("\n市值分布：")
    print(df['scale'].value_counts().to_string())
    current_script_dir = os.path.dirname(os.path.abspath(__file__))
    # 保存结果
    df[['ts_code', 'name', 'industry', 'circ_mv']].to_csv(
        os.path.join(current_script_dir, '../config/selected_stocks.csv'),
        index=False,
        encoding='utf_8_sig'
    )
    print("\n结果已保存至selected_stocks.csv")

if __name__ == "__main__":
    main()