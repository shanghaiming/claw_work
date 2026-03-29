# stock_platform_visual.py - 最终修复版本
import os
import time
import logging
import threading
import json
from datetime import datetime
from pathlib import Path
import pandas as pd
import numpy as np

# Dash相关导入
from dash import Dash, html, dcc, Input, Output, State, callback_context
from dash.exceptions import PreventUpdate
import plotly.graph_objs as go

# 定时任务
from apscheduler.schedulers.background import BackgroundScheduler

# 模块导入
try:
    from fetch_daily_batch import fetch_daily_batch
    from fetch_weekly_batch import fetch_weekly_batch
    from process_batch import process_batch
    from process_batch_week import process_batch_week
    from auto_select import auto_select
except ImportError:
    # 如果模块不存在，创建空函数避免错误
    def fetch_daily_batch(): 
        print("模拟执行日线数据获取")
        return True
    
    def fetch_weekly_batch(): 
        print("模拟执行周线数据获取")
        return True
    
    def process_batch(): 
        print("模拟处理日线数据")
        return True
    
    def process_batch_week(): 
        print("模拟处理周线数据")
        return True
    
    def auto_select(strategy_id=1): 
        print(f"模拟执行自动选股，策略ID: {strategy_id}")
        # 返回示例股票代码
        return ['000001', '600036', '601318']

# 初始化主应用
app = Dash(__name__, suppress_callback_exceptions=True)
server = app.server

# 配置日志
def setup_logging():
    """设置完整的日志系统"""
    
    # 配置根日志记录器
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('app.log', encoding='UTF-8'),
            logging.StreamHandler()  # 同时输出到控制台
        ]
    )
    
    # 设置特定模块的日志级别
    logging.getLogger('apscheduler').setLevel(logging.WARNING)
    
    # 创建我们的应用日志记录器
    logger = logging.getLogger(__name__)
    return logger

# 初始化日志
logger = setup_logging()

# 创建数据目录
os.makedirs('analysis_results', exist_ok=True)
os.makedirs('analysis_results_week', exist_ok=True)
os.makedirs('strategy_output', exist_ok=True)

# 定时任务配置
scheduler = BackgroundScheduler(timezone="Asia/Shanghai")

# 用户认证配置
class AuthConfig:
    # 默认用户账户（在实际应用中应该使用数据库存储）
    USERS = {
        'muller718': 'zxcvbnm0717',
        'guest': 'guest'
    }
    
    # 会话超时时间（分钟）
    SESSION_TIMEOUT = 30

# 共享状态管理
class TaskStatus:
    data_task = None
    strategy_task = None
    current_strategy = None
    logs = []
    errors = []
    lock = threading.Lock()

# 用户会话管理
class UserSession:
    sessions = {}
    lock = threading.Lock()
    
    @classmethod
    def create_session(cls, username):
        """创建新会话"""
        session_id = str(hash(f"{username}{time.time()}"))
        expiry = time.time() + AuthConfig.SESSION_TIMEOUT * 60
        
        with cls.lock:
            cls.sessions[session_id] = {
                'username': username,
                'expiry': expiry,
                'created_at': time.time()
            }
        
        return session_id
    
    @classmethod
    def validate_session(cls, session_id):
        """验证会话有效性"""
        with cls.lock:
            if session_id not in cls.sessions:
                return False
            
            session = cls.sessions[session_id]
            if time.time() > session['expiry']:
                # 会话过期，删除
                del cls.sessions[session_id]
                return False
            
            # 更新过期时间
            session['expiry'] = time.time() + AuthConfig.SESSION_TIMEOUT * 60
            return True
    
    @classmethod
    def get_username(cls, session_id):
        """获取会话用户名"""
        with cls.lock:
            if session_id in cls.sessions:
                return cls.sessions[session_id]['username']
            return None
    
    @classmethod
    def logout(cls, session_id):
        """注销会话"""
        with cls.lock:
            if session_id in cls.sessions:
                del cls.sessions[session_id]
                return True
            return False
    
    @classmethod
    def cleanup_expired_sessions(cls):
        """清理过期会话"""
        current_time = time.time()
        with cls.lock:
            expired_sessions = [
                session_id for session_id, session in cls.sessions.items()
                if current_time > session['expiry']
            ]
            for session_id in expired_sessions:
                del cls.sessions[session_id]
            return len(expired_sessions)

def log(message, level="info"):
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    
    with TaskStatus.lock:
        TaskStatus.logs.append(entry)
        
        if level == "error":
            TaskStatus.errors.append(entry)
    
    getattr(logger, level)(message)

class ChartSyncState:
    xaxis_range = None
    autorange = True
    last_sync_time = 0
    sync_lock = threading.Lock()

# 股票数据管理器（保持不变）
class StockDataManager:
    """股票数据管理器 - 只从auto_select选择数据进行显示"""
    
    def __init__(self):
        self.selected_codes = []
        self.stock_data = {}
        self.current_index = 0
        self.current_timeframe = 'daily'
    
    def load_initial_data(self):
        """初始化加载数据 - 只加载一个示例股票"""
        try:
            selected_file = Path("strategy_output/selected_stocks.json")
            if selected_file.exists():
                with open(selected_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    codes = data.get("selected_codes", [])
                    if codes:
                        self.selected_codes = codes
                        self._load_stock_data()
                        return
            
            data_dirs = [Path("analysis_results"), Path("analysis_results_week")]
            
            for data_dir in data_dirs:
                if data_dir.exists():
                    files = list(data_dir.glob("*.csv"))
                    if files:
                        code = files[0].stem
                        self.selected_codes = [code]
                        self._load_stock_data()
                        return
            
            self.selected_codes = []
            self.stock_data = {}
            
        except Exception as e:
            print(f"初始化加载数据失败: {e}")
            self.selected_codes = []
            self.stock_data = {}
    
    def update_from_auto_select(self, codes):
        """从auto_select结果更新 - 完全替换选股结果"""
        if not codes:
            print("auto_select返回空列表")
            return
        
        print(f"更新选股结果: {len(codes)} 只股票")
        self.selected_codes = codes
        self.current_index = 0
        self._load_stock_data()
        self._save_selected_codes()
    
    def _load_stock_data(self):
        """加载选中的股票数据 - 从daily_data2和week_data2读取"""
        self.stock_data = {}
        loaded_codes = []
        
        for code in self.selected_codes:
            try:
                daily_path = Path("analysis_results") / f"{code}_analysis.csv"
                weekly_path = Path("analysis_results_week") / f"{code}_analysis.csv"
                
                stock_data = {}
                
                if daily_path.exists():
                    df_daily = pd.read_csv(daily_path, parse_dates=['trade_date']).sort_values('trade_date')
                    df_daily = df_daily.dropna(subset=['open', 'high', 'low', 'close'])
                    df_daily = df_daily.reset_index(drop=True)
                    stock_data['daily'] = df_daily
                    print(f"成功加载日线数据: {code}")
                else:
                    print(f"未找到股票 {code} 的日线数据文件")
                    continue
                
                if weekly_path.exists():
                    df_weekly = pd.read_csv(weekly_path, parse_dates=['trade_date']).sort_values('trade_date')
                    df_weekly = df_weekly.dropna(subset=['open', 'high', 'low', 'close'])
                    df_weekly = df_weekly.reset_index(drop=True)
                    stock_data['weekly'] = df_weekly
                    print(f"成功加载周线数据: {code}")
                else:
                    print(f"未找到股票 {code} 的周线数据文件")
                    stock_data['weekly'] = None
                
                self.stock_data[code] = stock_data
                loaded_codes.append(code)
                
            except Exception as e:
                print(f"加载股票 {code} 数据失败: {e}")
        
        self.selected_codes = loaded_codes
    
    def _save_selected_codes(self):
        """保存选股结果到文件"""
        try:
            output_dir = Path("strategy_output")
            output_dir.mkdir(exist_ok=True)
            
            with open(output_dir / "selected_stocks.json", "w", encoding="utf-8") as f:
                json.dump({
                    "selected_codes": self.selected_codes,
                    "update_time": pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "count": len(self.selected_codes),
                    "strategy_id": TaskStatus.current_strategy
                }, f, ensure_ascii=False, indent=2)
            
            print(f"选股结果已保存: {len(self.selected_codes)} 只股票")
        except Exception as e:
            print(f"保存选股结果失败: {e}")
    
    def get_current_stock_data(self):
        """获取当前显示的股票数据"""
        if not self.selected_codes:
            return None, None
        
        code = self.selected_codes[self.current_index]
        data_dict = self.stock_data.get(code, {})
        data = data_dict.get(self.current_timeframe)
        
        return code, data
    
    def set_timeframe(self, timeframe):
        """设置时间框架"""
        self.current_timeframe = timeframe
        return self.get_current_stock_data()
    
    def next_stock(self):
        """切换到下一只股票"""
        if len(self.selected_codes) > 1:
            self.current_index = (self.current_index + 1) % len(self.selected_codes)
        return self.get_current_stock_data()
    
    def prev_stock(self):
        """切换到上一只股票"""
        if len(self.selected_codes) > 1:
            self.current_index = (self.current_index - 1) % len(self.selected_codes)
        return self.get_current_stock_data()
    
    def select_stock(self, code):
        """选择特定股票"""
        if code in self.selected_codes:
            self.current_index = self.selected_codes.index(code)
        return self.get_current_stock_data()

# 初始化股票数据管理器
stock_manager = StockDataManager()
stock_manager.load_initial_data()

# 数据任务管道
def execute_data_pipeline(freq):
    try:
        log(f"开始{freq}级数据任务")
        with TaskStatus.lock:
            TaskStatus.data_task = freq
        
        if freq == 'daily':
            fetch_daily_batch()
            process_batch()
        else:
            fetch_weekly_batch()
            process_batch_week()
            
        log(f"{freq}级数据任务完成")
    except Exception as e:
        log(f"{freq}数据任务失败: {str(e)}", "error")
    finally:
        with TaskStatus.lock:
            TaskStatus.data_task = None

# 策略筛选管道
def execute_strategy_pipeline(strategy_id):
    try:
        log(f"开始策略筛选任务 - 策略{strategy_id}")
        with TaskStatus.lock:
            TaskStatus.strategy_task = True
            TaskStatus.current_strategy = strategy_id
        
        selected_codes = auto_select(strategy_id)
        stock_manager.update_from_auto_select(selected_codes)
        
        log(f"策略{strategy_id}筛选完成，选中 {len(selected_codes)} 只股票")
        
    except Exception as e:
        log(f"策略{strategy_id}筛选失败: {str(e)}", "error")
    finally:
        with TaskStatus.lock:
            TaskStatus.strategy_task = None

# 图表工具函数（保持不变）
def prepare_chart_data(df):
    if df is None:
        return None
        
    df = df.copy()
    df = df.sort_values('trade_date').reset_index(drop=True)
    df['date_str'] = df['trade_date'].dt.strftime('%Y-%m-%d')
    df['continuous_index'] = range(len(df))
    return df

def calculate_visible_range(df, x_range=None, margin_ratio=0.05, columns=None, fixed_range=None):
    if df is None:
        return None
        
    if x_range is None:
        visible_df = df
    else:
        start_idx, end_idx = int(x_range[0]), int(x_range[1])
        visible_df = df[
            (df['continuous_index'] >= max(0, start_idx)) & 
            (df['continuous_index'] <= min(len(df)-1, end_idx))
        ]
    
    if len(visible_df) == 0:
        if fixed_range:
            return fixed_range
        if columns:
            min_val = df[columns].min().min()
            max_val = df[columns].max().max()
        else:
            return None
    
    if fixed_range:
        return fixed_range
    
    if columns:
        visible_min = visible_df[columns].min().min()
        visible_max = visible_df[columns].max().max()
    else:
        return None
    
    data_range = visible_max - visible_min
    margin = data_range * margin_ratio
    
    if data_range == 0:
        margin = visible_max * 0.05 if visible_max != 0 else 0.1
    
    y_min = visible_min - margin
    y_max = visible_max + margin
    
    if 'volume' not in str(columns) and 'macd' not in str(columns):
        y_min = max(0, y_min)
    
    return [y_min, y_max]

def create_empty_figure(message="暂无数据"):
    fig = go.Figure()
    fig.update_layout(
        title=message,
        xaxis={'visible': False},
        yaxis={'visible': False},
        plot_bgcolor='white',
        margin=dict(l=60, r=40, t=60, b=40)
    )
    return fig

def create_price_chart(df, stock_code, x_range=None):
    if df is None:
        return create_empty_figure("无数据")
        
    fig = go.Figure()
    
    chart_df = prepare_chart_data(df)
    if chart_df is None:
        return create_empty_figure("数据格式错误")
    
    price_range = calculate_visible_range(chart_df, x_range, columns=['low', 'high'])
    
    fig.add_trace(go.Candlestick(
        x=chart_df['continuous_index'],
        open=chart_df['open'],
        high=chart_df['high'],
        low=chart_df['low'],
        close=chart_df['close'],
        name='价格',
        increasing_line_color='#ef5350',
        decreasing_line_color='#26a69a'
    ))
    
    if 'ma5' in chart_df.columns:
        fig.add_trace(go.Scatter(
            x=chart_df['continuous_index'], 
            y=chart_df['ma5'],
            line=dict(color='#ff9800', width=1.2),
            name='MA5',
            hovertemplate='<br>'.join([
                '日期: %{customdata}',
                'MA5: %{y:.2f}',
                '<extra></extra>'
            ]),
            customdata=chart_df['date_str']
        ))
    
    if 'ma10' in chart_df.columns:
        fig.add_trace(go.Scatter(
            x=chart_df['continuous_index'], 
            y=chart_df['ma10'],
            line=dict(color='#2196f3', width=1.2),
            name='MA10',
            hovertemplate='<br>'.join([
                '日期: %{customdata}',
                'MA10: %{y:.2f}',
                '<extra></extra>'
            ]),
            customdata=chart_df['date_str']
        ))
    
    n_ticks = min(10, len(chart_df))
    tick_indices = np.linspace(0, len(chart_df)-1, n_ticks, dtype=int)
    tick_values = [chart_df['continuous_index'].iloc[i] for i in tick_indices]
    tick_labels = [chart_df['date_str'].iloc[i] for i in tick_indices]
    
    fig.update_layout(
        title=f'{stock_code} - 价格走势',
        xaxis={
            'title': '',
            'rangeslider': {'visible': False},
            'type': 'linear',
            'fixedrange': False,
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikethickness': 1,
            'spikecolor': '#666',
            'showline': True,
            'showgrid': True,
            'gridcolor': '#f0f0f0',
            'zeroline': False,
            'tickvals': tick_values,
            'ticktext': tick_labels,
            'tickangle': 45,
            'showticklabels': False,
        },
        yaxis={
            'title': '价格',
            'fixedrange': False,
            'autorange': False,
            'range': price_range,
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikethickness': 1,
            'spikecolor': '#666',
            'showline': True,
            'showgrid': True,
            'gridcolor': '#f0f0f0',
            'zeroline': False,
        },
        showlegend=True,
        plot_bgcolor='white',
        height=350,
        margin=dict(l=60, r=40, t=60, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        dragmode='pan',
        hovermode='x',
        spikedistance=-1,
    )
    
    return fig

def create_volume_chart(df, x_range=None):
    if df is None:
        return create_empty_figure("无数据")
        
    chart_df = prepare_chart_data(df)
    if chart_df is None:
        return create_empty_figure("数据格式错误")
    
    volume_range = calculate_visible_range(chart_df, x_range, columns=['volume'])
    
    colors = ['#ef5350' if close >= open else '#26a69a' 
              for close, open in zip(chart_df['close'], chart_df['open'])]
    
    fig = go.Figure(go.Bar(
        x=chart_df['continuous_index'],
        y=chart_df['volume'],
        marker_color=colors,
        name='成交量',
        hovertemplate='<br>'.join([
            '日期: %{customdata}',
            '成交量: %{y}',
            '<extra></extra>'
        ]),
        customdata=chart_df['date_str']
    ))
    
    n_ticks = min(10, len(chart_df))
    tick_indices = np.linspace(0, len(chart_df)-1, n_ticks, dtype=int)
    tick_values = [chart_df['continuous_index'].iloc[i] for i in tick_indices]
    tick_labels = [chart_df['date_str'].iloc[i] for i in tick_indices]
    
    fig.update_layout(
        showlegend=False,
        xaxis={
            'title': '',
            'type': 'linear',
            'fixedrange': False,
            'showticklabels': False,
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikethickness': 1,
            'spikecolor': '#666',
            'showline': True,
            'showgrid': True,
            'gridcolor': '#f0f0f0',
            'tickvals': tick_values,
            'ticktext': tick_labels,
        },
        yaxis={
            'title': '成交量',
            'fixedrange': False,
            'autorange': False,
            'range': volume_range,
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikethickness': 1,
            'spikecolor': '#666',
            'showline': True,
            'showgrid': True,
            'gridcolor': '#f0f0f0',
        },
        plot_bgcolor='white',
        height=200,
        margin=dict(l=60, r=40, t=10, b=10),
        dragmode='pan',
        hovermode='x',
    )
    
    return fig

def create_macd_chart(df, x_range=None):
    if df is None:
        return create_empty_figure("无数据")
        
    chart_df = prepare_chart_data(df)
    if chart_df is None:
        return create_empty_figure("数据格式错误")
    
    macd_columns = ['macd']
    if 'diff' in chart_df.columns:
        macd_columns.append('diff')
    if 'dea' in chart_df.columns:
        macd_columns.append('dea')
    
    macd_range = calculate_visible_range(chart_df, x_range, columns=macd_columns)
    
    fig = go.Figure()
    
    colors = ['#ef5350' if macd >= 0 else '#26a69a' for macd in chart_df['macd']]
    fig.add_trace(go.Bar(
        x=chart_df['continuous_index'], 
        y=chart_df['macd'],
        marker_color=colors,
        name='MACD',
        opacity=0.6,
        hovertemplate='<br>'.join([
            '日期: %{customdata}',
            'MACD: %{y:.4f}',
            '<extra></extra>'
        ]),
        customdata=chart_df['date_str']
    ))
    
    if 'diff' in chart_df.columns:
        fig.add_trace(go.Scatter(
            x=chart_df['continuous_index'], 
            y=chart_df['diff'],
            line=dict(color='#ff6d00', width=1.5),
            name='DIF',
            hovertemplate='<br>'.join([
                '日期: %{customdata}',
                'DIF: %{y:.4f}',
                '<extra></extra>'
            ]),
            customdata=chart_df['date_str']
        ))
    
    if 'dea' in chart_df.columns:
        fig.add_trace(go.Scatter(
            x=chart_df['continuous_index'], 
            y=chart_df['dea'],
            line=dict(color='#2962ff', width=1.5),
            name='DEA',
            hovertemplate='<br>'.join([
                '日期: %{customdata}',
                'DEA: %{y:.4f}',
                '<extra></extra>'
            ]),
            customdata=chart_df['date_str']
        ))
    
    fig.add_hline(y=0, line_width=1, line_dash="dash", line_color="gray")
    
    n_ticks = min(10, len(chart_df))
    tick_indices = np.linspace(0, len(chart_df)-1, n_ticks, dtype=int)
    tick_values = [chart_df['continuous_index'].iloc[i] for i in tick_indices]
    tick_labels = [chart_df['date_str'].iloc[i] for i in tick_indices]
    
    fig.update_layout(
        showlegend=True,
        xaxis={
            'title': '',
            'type': 'linear',
            'fixedrange': False,
            'showticklabels': False,
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikethickness': 1,
            'spikecolor': '#666',
            'showline': True,
            'showgrid': True,
            'gridcolor': '#f0f0f0',
            'tickvals': tick_values,
            'ticktext': tick_labels,
        },
        yaxis={
            'title': 'MACD',
            'fixedrange': False,
            'autorange': False,
            'range': macd_range,
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikethickness': 1,
            'spikecolor': '#666',
            'showline': True,
            'showgrid': True,
            'gridcolor': '#f0f0f0',
        },
        plot_bgcolor='white',
        height=200,
        margin=dict(l=60, r=40, t=10, b=10),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        dragmode='pan',
        hovermode='x',
    )
    
    return fig

def create_wr_chart(df, x_range=None):
    if df is None:
        return create_empty_figure("无数据")
        
    chart_df = prepare_chart_data(df)
    if chart_df is None:
        return create_empty_figure("数据格式错误")
    
    wr_columns = []
    if 'wr5' in chart_df.columns:
        wr_columns.append('wr5')
    if 'wr10' in chart_df.columns:
        wr_columns.append('wr10')
    
    wr_range = calculate_visible_range(chart_df, x_range, columns=wr_columns, fixed_range=[-100, 0])
    
    fig = go.Figure()
    
    if 'wr5' in chart_df.columns:
        fig.add_trace(go.Scatter(
            x=chart_df['continuous_index'], 
            y=chart_df['wr5'],
            line=dict(color='#7b1fa2', width=1.5),
            name='WR5',
            hovertemplate='<br>'.join([
                '日期: %{customdata}',
                'WR5: %{y:.2f}',
                '<extra></extra>'
            ]),
            customdata=chart_df['date_str']
        ))
    
    if 'wr10' in chart_df.columns:
        fig.add_trace(go.Scatter(
            x=chart_df['continuous_index'], 
            y=chart_df['wr10'],
            line=dict(color='#00897b', width=1.5),
            name='WR10',
            hovertemplate='<br>'.join([
                '日期: %{customdata}',
                'WR10: %{y:.2f}',
                '<extra></extra>'
            ]),
            customdata=chart_df['date_str']
        ))
    
    fig.add_hline(y=-20, line_width=1, line_dash="dash", line_color="#ef5350")
    fig.add_hline(y=-80, line_width=1, line_dash="dash", line_color="#26a69a")
    
    n_ticks = min(10, len(chart_df))
    tick_indices = np.linspace(0, len(chart_df)-1, n_ticks, dtype=int)
    tick_values = [chart_df['continuous_index'].iloc[i] for i in tick_indices]
    tick_labels = [chart_df['date_str'].iloc[i] for i in tick_indices]
    
    fig.update_layout(
        showlegend=True,
        xaxis={
            'title': '交易日',
            'type': 'linear',
            'fixedrange': False,
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikethickness': 1,
            'spikecolor': '#666',
            'showline': True,
            'showgrid': True,
            'gridcolor': '#f0f0f0',
            'tickvals': tick_values,
            'ticktext': tick_labels,
            'tickangle': 45,
        },
        yaxis={
            'title': '威廉指标',
            'fixedrange': False,
            'autorange': False,
            'range': wr_range,
            'showspikes': True,
            'spikemode': 'across',
            'spikesnap': 'cursor',
            'spikethickness': 1,
            'spikecolor': '#666',
            'showline': True,
            'showgrid': True,
            'gridcolor': '#f0f0f0',
        },
        plot_bgcolor='white',
        height=200,
        margin=dict(l=60, r=40, t=10, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=10)
        ),
        dragmode='pan',
        hovermode='x',
    )
    
    return fig

# ========== 应用布局 ==========
app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    dcc.Store(id='session-id', storage_type='session'),
    html.Div(id='page-content', style={'height': '100vh', 'overflow': 'hidden'})
], style={'height': '100vh', 'overflow': 'hidden'})

# ========== 登录页面布局 ==========
login_layout = html.Div([
    html.Div([
        html.Div([
            html.Div([
                html.H1("🔐 量化分析平台", className="login-title"),
                html.P("专业的股票数据分析与策略平台", className="login-subtitle"),
                
                html.Div([
                    html.Div([
                        html.Label("👤 用户名", className="login-label"),
                        dcc.Input(
                            id='login-username',
                            type='text',
                            placeholder='请输入用户名',
                            className="login-input"
                        ),
                    ], className="input-group"),
                    
                    html.Div([
                        html.Label("🔒 密码", className="login-label"),
                        dcc.Input(
                            id='login-password',
                            type='password',
                            placeholder='请输入密码',
                            className="login-input"
                        ),
                    ], className="input-group"),
                    
                    html.Div(id='login-error', className="login-error"),
                    
                    html.Button(
                        "🚀 登录系统",
                        id='login-button',
                        n_clicks=0,
                        className="login-button"
                    ),
                ], className="login-form"),
                
                html.Div([
                    html.Hr(className="divider"),
                    html.P("演示账户", className="demo-title"),
                    html.Div([
                        html.Div([
                            html.Span("👑 管理员", className="demo-role"),
                            html.Span("admin / admin123", className="demo-account")
                        ], className="demo-item"),
                        html.Div([
                            html.Span("👤 普通用户", className="demo-role"),
                            html.Span("user / user123", className="demo-account")
                        ], className="demo-item"),
                        html.Div([
                            html.Span("👥 访客", className="demo-role"),
                            html.Span("guest / guest123", className="demo-account")
                        ], className="demo-item"),
                    ], className="demo-accounts"),
                ], className="demo-section"),
                
            ], className="login-card")
        ], className="login-center")
    ], className="login-background")
], className="login-page")

# ========== 数据管理页面布局 ==========
data_management_layout = html.Div([
    # 导航栏
    html.Div([
        html.A("📊 数据管理", href="/data_management", className="nav-link"),
        html.A("📈 股票分析", href="/analysis", className="nav-link"),
        html.Div([
            html.Span(id="user-info", className="user-info"),
            html.Button("🚪 退出", id="logout-button", n_clicks=0, className="logout-button")
        ], className="user-section")
    ], className="nav-bar"),
    
    # 主内容
    html.Div([
        html.H1("量化数据管理系统", className="header"),
        html.Div([
            html.Div([
                html.H3("📥 数据任务", className="panel-title"),
                html.Button("📊 日频数据任务", id="daily-btn", className="data-btn"),
                html.Button("📅 周频数据任务", id="weekly-btn", className="data-btn"),
                html.Div(id="data-status", className="status-box")
            ], className="data-panel"),
            html.Div([
                html.H3("🎯 策略任务", className="panel-title"),
                html.Div([
                    html.Button("🚀 策略1", id="strategy-btn-1", className="strategy-btn"),
                    html.Button("🚀 策略2", id="strategy-btn-2", className="strategy-btn"),
                    html.Button("🚀 策略3", id="strategy-btn-3", className="strategy-btn"),
                    html.Button("🚀 策略4", id="strategy-btn-4", className="strategy-btn"),
                    html.Button("🚀 策略5", id="strategy-btn-5", className="strategy-btn"),
                ], className="strategy-buttons-container"),
                html.Div(id="strategy-status", className="status-box")
            ], className="strategy-panel")
        ], className="control-container"),
        
        html.Div([
            html.H3("⚠️ 错误日志", className="panel-title"),
            html.Div(id="error-log", className="error-log-container")
        ], className="error-panel"),
        
        html.Div([
            html.H3("📋 系统日志", className="panel-title"),
            html.Div(id="live-log", className="log-container")
        ], className="log-panel"),
        dcc.Interval(id='refresh', interval=2000)
    ], className="data-management-content")
], className="data-management-page")

# ========== 股票分析页面布局 ==========
def get_analysis_layout():
    current_codes = stock_manager.selected_codes
    current_code = current_codes[0] if current_codes else None
    
    return html.Div([
        # 导航栏
        html.Div([
            html.A("📊 数据管理", href="/data_management", className="nav-link"),
            html.A("📈 股票分析", href="/analysis", className="nav-link"),
            html.Div([
                html.Span(id="user-info-analysis", className="user-info"),
                html.Button("🚪 退出", id="logout-button-analysis", n_clicks=0, className="logout-button")
            ], className="user-section")
        ], className="nav-bar"),
        
        # 主内容
        html.Div([
            # 头部控制栏
            html.Div([
                html.H1("股票分析系统", style={'flex': '1', 'margin': '0', 'fontSize': '28px'}),
                html.Div([
                    dcc.Dropdown(
                        id='stock-selector',
                        options=[{'label': code, 'value': code} for code in current_codes],
                        value=current_code,
                        style={'width': '120px', 'marginRight': '15px'}
                    ),
                    html.Button("◀ 上一个", id="prev-btn", n_clicks=0, 
                               className="nav-button"),
                    html.Button("下一个 ▶", id="next-btn", n_clicks=0,
                               className="nav-button"),
                    dcc.RadioItems(
                        id='timeframe-selector',
                        options=[
                            {'label': '日线', 'value': 'daily'},
                            {'label': '周线', 'value': 'weekly'}
                        ],
                        value='daily',
                        inline=True,
                        className="timeframe-selector"
                    )
                ], className="control-group")
            ], className="header-container"),
            
            # 存储组件
            dcc.Store(id='current-index', data=0),
            dcc.Store(id='sync-state', data={'xaxis_range': None, 'autorange': True}),
            
            # 纵向排列的同步图表容器
            html.Div([
                html.Div([
                    dcc.Graph(
                        id='price-chart',
                        config={
                            'displayModeBar': True,
                            'scrollZoom': True,
                            'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'eraseshape'],
                            'displaylogo': False
                        },
                        className='price-chart-graph'
                    )
                ], className='sync-chart-section'),
                
                html.Div([
                    dcc.Graph(
                        id='volume-chart',
                        config={
                            'displayModeBar': False,
                            'scrollZoom': True
                        },
                        className='volume-chart-graph'
                    )
                ], className='sync-chart-section'),
                
                html.Div([
                    dcc.Graph(
                        id='macd-chart',
                        config={
                            'displayModeBar': False,
                            'scrollZoom': True
                        },
                        className='macd-chart-graph'
                    )
                ], className='sync-chart-section'),
                
                html.Div([
                    dcc.Graph(
                        id='wr-chart',
                        config={
                            'displayModeBar': False,
                            'scrollZoom': True
                        },
                        className='wr-chart-graph'
                    )
                ], className='sync-chart-section')
            ], className='sync-charts-container')
        ], className="analysis-content")
    ], className="analysis-page")

# ========== 页面路由回调 ==========
@app.callback(
    [Output('page-content', 'children'),
     Output('session-id', 'data')],
    [Input('url', 'pathname')],
    [State('session-id', 'data')]
)
def display_page(pathname, session_id):
    """页面路由回调 - 修复版本"""
    print(f"页面路由: {pathname}, 会话: {session_id}")
    
    # 如果是登录页面，直接显示
    if pathname == '/login':
        print("显示登录页面")
        return login_layout, session_id
    
    # 验证会话
    if session_id and UserSession.validate_session(session_id):
        # 已登录状态
        username = UserSession.get_username(session_id)
        print(f"用户 {username} 已登录，显示 {pathname} 页面")
        
        if pathname == '/analysis':
            return get_analysis_layout(), session_id
        else:
            # 默认重定向到数据管理页面
            print("重定向到数据管理页面")
            return data_management_layout, session_id
    else:
        # 未登录状态，重定向到登录页面
        print("未登录，重定向到登录页面")
        return login_layout, None

# ========== 登录回调 ==========
@app.callback(
    [Output('url', 'pathname'),
     Output('login-error', 'children'),
     Output('session-id', 'data', allow_duplicate=True)],
    [Input('login-button', 'n_clicks')],
    [State('login-username', 'value'),
     State('login-password', 'value'),
     State('session-id', 'data')],
    prevent_initial_call=True
)
def login(n_clicks, username, password, current_session_id):
    """登录回调"""
    if n_clicks == 0:
        raise PreventUpdate
    
    if not username or not password:
        return '/login', "❌ 请输入用户名和密码", current_session_id
    
    # 验证用户凭据
    if username in AuthConfig.USERS and AuthConfig.USERS[username] == password:
        # 创建新会话
        session_id = UserSession.create_session(username)
        log(f"用户 {username} 登录成功")
        return '/data_management', "", session_id
    else:
        log(f"登录失败: 用户名 {username}")
        return '/login', "❌ 用户名或密码错误", current_session_id

# ========== 数据管理页面退出登录回调 ==========
@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('session-id', 'data', allow_duplicate=True)],
    [Input('logout-button', 'n_clicks')],  # 只监听数据管理页面的退出按钮
    [State('session-id', 'data')],
    prevent_initial_call=True
)
def logout_data_management(logout_clicks, session_id):
    """数据管理页面退出登录回调"""
    if not logout_clicks or logout_clicks == 0:
        raise PreventUpdate
    
    print(f"数据管理页面退出登录点击: {logout_clicks}")
    
    # 执行退出登录操作
    if session_id:
        username = UserSession.get_username(session_id)
        if username:
            UserSession.logout(session_id)
            log(f"用户 {username} 退出登录")
            print(f"用户 {username} 退出登录成功")
        else:
            log("退出登录: 无效的会话")
            print("退出登录: 无效的会话ID")
    
    print("重定向到登录页面")
    return '/login', None

# ========== 分析页面退出登录回调 ==========
@app.callback(
    [Output('url', 'pathname', allow_duplicate=True),
     Output('session-id', 'data', allow_duplicate=True)],
    [Input('logout-button-analysis', 'n_clicks')],  # 只监听分析页面的退出按钮
    [State('session-id', 'data')],
    prevent_initial_call=True
)
def logout_analysis(logout_clicks, session_id):
    """分析页面退出登录回调"""
    if not logout_clicks or logout_clicks == 0:
        raise PreventUpdate
    
    print(f"分析页面退出登录点击: {logout_clicks}")
    
    # 执行退出登录操作
    if session_id:
        username = UserSession.get_username(session_id)
        if username:
            UserSession.logout(session_id)
            log(f"用户 {username} 退出登录")
            print(f"用户 {username} 退出登录成功")
        else:
            log("退出登录: 无效的会话")
            print("退出登录: 无效的会话ID")
    
    print("重定向到登录页面")
    return '/login', None

# ========== 更新用户信息回调 ==========
@app.callback(
    Output('user-info', 'children'),
    [Input('url', 'pathname')],
    [State('session-id', 'data')]
)
def update_user_info_data_management(pathname, session_id):
    """更新数据管理页面用户信息"""
    if session_id and UserSession.validate_session(session_id):
        username = UserSession.get_username(session_id)
        return f"👤 欢迎, {username}"
    return ""

@app.callback(
    Output('user-info-analysis', 'children'),
    [Input('url', 'pathname')],
    [State('session-id', 'data')]
)
def update_user_info_analysis(pathname, session_id):
    """更新分析页面用户信息"""
    if session_id and UserSession.validate_session(session_id):
        username = UserSession.get_username(session_id)
        return f"👤 欢迎, {username}"
    return ""

# ========== 数据管理回调 ==========
@app.callback(
    [Output('live-log', 'children'),
     Output('error-log', 'children'),
     Output('data-status', 'children'),
     Output('strategy-status', 'children')],
    [Input('refresh', 'n_intervals'),
     Input('daily-btn', 'n_clicks'),
     Input('weekly-btn', 'n_clicks'),
     Input('strategy-btn-1', 'n_clicks'),
     Input('strategy-btn-2', 'n_clicks'),
     Input('strategy-btn-3', 'n_clicks'),
     Input('strategy-btn-4', 'n_clicks'),
     Input('strategy-btn-5', 'n_clicks')]
)
def update_interface(n, daily_clicks, weekly_clicks, 
                    strategy1_clicks, strategy2_clicks, strategy3_clicks, 
                    strategy4_clicks, strategy5_clicks):
    """数据管理页面回调 - 简化版本"""
    ctx = callback_context
    if ctx.triggered:
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id in ['daily-btn', 'weekly-btn']:
            freq = trigger_id.split('-')[0]
            threading.Thread(
                target=execute_data_pipeline,
                args=(freq,),
                daemon=True
            ).start()
        elif trigger_id.startswith('strategy-btn-'):
            strategy_id = int(trigger_id.split('-')[-1])
            threading.Thread(
                target=execute_strategy_pipeline,
                args=(strategy_id,),
                daemon=True
            ).start()
    
    with TaskStatus.lock:
        data_status_text = "日周数据任务: " + (TaskStatus.data_task or "空闲")
        
        strategy_status = "策略筛选任务: "
        if TaskStatus.strategy_task:
            strategy_status += f"进行中 (策略{TaskStatus.current_strategy})"
        else:
            strategy_status += "空闲"
            
        logs = [html.P(log, className="log-entry") for log in TaskStatus.logs[-10:]]
        errors = [html.P(error, className="error-entry") for error in TaskStatus.errors[-5:]]
    
    return logs, errors, data_status_text, strategy_status

# ========== 股票分析回调 ==========
def register_analysis_callbacks():
    """注册分析页面的回调函数"""
    
    @app.callback(
        [Output('stock-selector', 'options'),
         Output('stock-selector', 'value')],
        [Input('refresh', 'n_intervals')],
        [State('session-id', 'data')]
    )
    def update_stock_selector(n, session_id):
        """更新股票选择器的选项和值"""
        if not session_id or not UserSession.validate_session(session_id):
            raise PreventUpdate
            
        if not stock_manager.selected_codes:
            return [], None
        
        options = [{'label': code, 'value': code} for code in stock_manager.selected_codes]
        current_code, _ = stock_manager.get_current_stock_data()
        
        return options, current_code
    
    @app.callback(
        [Output('stock-selector', 'value', allow_duplicate=True),
         Output('current-index', 'data')],
        [Input('prev-btn', 'n_clicks'),
         Input('next-btn', 'n_clicks'),
         Input('stock-selector', 'value')],
        [State('current-index', 'data'),
         State('session-id', 'data')],
        prevent_initial_call=True
    )
    def update_stock_selection(prev_clicks, next_clicks, selected_stock, current_index, session_id):
        """更新股票选择"""
        if not session_id or not UserSession.validate_session(session_id):
            raise PreventUpdate
            
        ctx = callback_context
        if not ctx.triggered or not stock_manager.selected_codes:
            raise PreventUpdate
        
        trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
        
        if trigger_id == 'prev-btn':
            code, _ = stock_manager.prev_stock()
            return code, stock_manager.current_index
        elif trigger_id == 'next-btn':
            code, _ = stock_manager.next_stock()
            return code, stock_manager.current_index
        elif trigger_id == 'stock-selector' and selected_stock in stock_manager.selected_codes:
            code, _ = stock_manager.select_stock(selected_stock)
            return code, stock_manager.current_index
        
        raise PreventUpdate
    
    # 使用客户端回调实现图表同步
    app.clientside_callback(
        """
        function(priceRelayout, volumeRelayout, macdRelayout, wrRelayout, syncState) {
            const ctx = dash_clientside.callback_context;
            if (!ctx.triggered.length) return window.dash_clientside.no_update;
            
            const triggerId = ctx.triggered[0].prop_id;
            const triggerData = ctx.triggered[0].value;
            
            if (!triggerData) return window.dash_clientside.no_update;
            
            let newRange = null;
            let newAutorange = false;
            
            if (triggerData['xaxis.range']) {
                newRange = triggerData['xaxis.range'];
                newAutorange = false;
            } else if (triggerData['xaxis.range[0]'] && triggerData['xaxis.range[1]']) {
                newRange = [triggerData['xaxis.range[0]'], triggerData['xaxis.range[1]']];
                newAutorange = false;
            } else if (triggerData['xaxis.autorange']) {
                newAutorange = true;
                newRange = null;
            } else if (triggerData['autosize'] || triggerData['yaxis.autorange']) {
                return window.dash_clientside.no_update;
            }
            
            if (!newRange && !newAutorange) return window.dash_clientside.no_update;
            
            const updateObj = newAutorange ? 
                {'xaxis.autorange': true, 'yaxis.autorange': true} :
                {'xaxis.range': newRange};
                
            return [
                updateObj,
                updateObj,
                updateObj,
                updateObj,
                {'xaxis_range': newRange, 'autorange': newAutorange}
            ];
        }
        """,
        [Output('price-chart', 'relayoutData'),
         Output('volume-chart', 'relayoutData'),
         Output('macd-chart', 'relayoutData'),
         Output('wr-chart', 'relayoutData'),
         Output('sync-state', 'data')],
        [Input('price-chart', 'relayoutData'),
         Input('volume-chart', 'relayoutData'),
         Input('macd-chart', 'relayoutData'),
         Input('wr-chart', 'relayoutData')],
        [State('sync-state', 'data')]
    )
    
    @app.callback(
        [Output('price-chart', 'figure'),
         Output('volume-chart', 'figure'),
         Output('macd-chart', 'figure'),
         Output('wr-chart', 'figure')],
        [Input('stock-selector', 'value'),
         Input('timeframe-selector', 'value'),
         Input('sync-state', 'data')],
        [State('session-id', 'data')]
    )
    def update_all_charts(selected_stock, timeframe, sync_state, session_id):
        """统一更新所有图表"""
        if not session_id or not UserSession.validate_session(session_id):
            raise PreventUpdate
            
        code, df = stock_manager.set_timeframe(timeframe)
        
        if code is None or df is None:
            message = "暂无股票数据" if code is None else f"股票 {code} 的{timeframe}数据加载失败"
            empty_fig = create_empty_figure(message)
            return empty_fig, create_empty_figure(), create_empty_figure(), create_empty_figure()
        
        try:
            x_range = sync_state.get('xaxis_range') if sync_state else None
            
            price_fig = create_price_chart(df, code, x_range)
            volume_fig = create_volume_chart(df, x_range)
            macd_fig = create_macd_chart(df, x_range)
            wr_fig = create_wr_chart(df, x_range)
            
            if not sync_state.get('autorange', True) and x_range:
                for fig in [price_fig, volume_fig, macd_fig, wr_fig]:
                    fig.update_layout(xaxis_range=x_range)
            
            return price_fig, volume_fig, macd_fig, wr_fig
            
        except Exception as e:
            logger.error(f"更新图表失败: {e}")
            error_fig = create_empty_figure(f"数据加载失败: {str(e)}")
            return error_fig, create_empty_figure(), create_empty_figure(), create_empty_figure()

# 在应用启动时注册分析页面回调
register_analysis_callbacks()

# 会话清理定时任务
def cleanup_sessions():
    """定期清理过期会话"""
    try:
        cleaned_count = UserSession.cleanup_expired_sessions()
        if cleaned_count > 0:
            logger.info(f"清理了 {cleaned_count} 个过期会话")
    except Exception as e:
        logger.error(f"清理会话失败: {e}")

if __name__ == '__main__':
    # 启动定时任务
    scheduler.add_job(
        lambda: execute_data_pipeline('daily'),
        'cron',
        hour=16,
        minute=0,
        name="daily_pipeline"
    )
    scheduler.add_job(
        lambda: execute_data_pipeline('weekly'),
        'cron',
        day_of_week='fri',
        hour=17,
        name="weekly_pipeline"
    )
    # 添加会话清理任务（每小时执行一次）
    scheduler.add_job(
        cleanup_sessions,
        'interval',
        hours=1,
        name="session_cleanup"
    )
    scheduler.start()
    
    logger.info("启动量化分析系统...")
    print(f"初始化完成: 加载了 {len(stock_manager.selected_codes)} 只股票")
    print("默认登录账户:")
    print("  admin / admin123")
    print("  user / user123") 
    print("  guest / guest123")
    app.run(host='127.0.0.1', port=8080, debug=False)