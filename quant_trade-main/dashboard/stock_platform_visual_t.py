from flask import Flask, request, jsonify, send_file
import os
import time
import threading
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import logging
# 定时任务
from apscheduler.schedulers.background import BackgroundScheduler

# 导入您的真实数据获取模块
try:
    from fetch_daily_batch import fetch_daily_batch
    from fetch_weekly_batch import fetch_weekly_batch  
    from process_batch import process_batch
    from process_batch_week import process_batch_week
    from auto_select import auto_select
    REAL_DATA = True
except ImportError:
    REAL_DATA = False
    print("警告: 使用模拟数据模式")

app = Flask(__name__)

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 高效内存缓存
class DataCache:
    def __init__(self):
        self.stock_data = {}  # 缓存完整数据
        self.selected_stocks = []
        self.last_update = {}
        self.cache_ttl = 300  # 5分钟缓存
        self.data_availability = {}
        
    def get_stock_data(self, code, timeframe='daily'):
        """从缓存获取股票完整数据"""
        cache_key = f"{code}_{timeframe}"
        
        # 检查缓存是否有效
        if cache_key in self.stock_data:
            if time.time() - self.last_update.get(cache_key, 0) < self.cache_ttl:
                return self.stock_data[cache_key]
        
        # 从文件系统加载完整数据
        data = self._load_from_filesystem(code, timeframe)
        if data is not None:
            self.stock_data[cache_key] = data
            self.last_update[cache_key] = time.time()
            self.data_availability[cache_key] = True
        else:
            self.data_availability[cache_key] = False
        
        return data
    
    def _load_from_filesystem(self, code, timeframe):
        """从文件系统加载股票完整数据 - 按时间升序排列"""
        try:
            if timeframe == 'daily':
                file_path = f"analysis_results/{code}_analysis.csv"
            else:
                file_path = f"analysis_results_week/{code}_analysis.csv"
            
            if not os.path.exists(file_path):
                logger.warning(f"数据文件不存在: {file_path}")
                return None
            
            # 高效读取CSV
            df = pd.read_csv(file_path, parse_dates=['trade_date'])
            # 按日期升序排列，确保最老的数据在前，最新的在后
            df = df.sort_values('trade_date', ascending=True).reset_index(drop=True)
            
            # 转换为前端需要的格式
            result = {
                'dates': df['trade_date'].dt.strftime('%Y-%m-%d').tolist(),
                'open': df['open'].fillna(0).tolist(),
                'high': df['high'].fillna(0).tolist(), 
                'low': df['low'].fillna(0).tolist(),
                'close': df['close'].fillna(0).tolist(),
                'volume': df['volume'].fillna(0).tolist() if 'volume' in df.columns else [0] * len(df),
            }
            
            # 添加技术指标
            indicators = ['ma5', 'ma10', 'macd', 'diff', 'dea', 'wr5', 'wr10']
            for indicator in indicators:
                if indicator in df.columns:
                    result[indicator] = df[indicator].fillna(0).tolist()
            
            logger.info(f"成功加载股票数据: {code}_{timeframe}, 数据点: {len(result['dates'])}")
            return result
            
        except Exception as e:
            logger.error(f"加载股票数据失败 {code}_{timeframe}: {e}")
            return None
    
    def get_data_range(self, code, timeframe='daily', start_idx=0, end_idx=100):
        """获取数据范围 - 按需返回数据片段"""
        full_data = self.get_stock_data(code, timeframe)
        if not full_data:
            return None
            
        total_length = len(full_data['dates'])
        start_idx = max(0, start_idx)
        end_idx = min(total_length, end_idx)
        
        if start_idx >= end_idx:
            return None
            
        # 提取范围数据
        range_data = {}
        for key in full_data:
            if isinstance(full_data[key], list):
                range_data[key] = full_data[key][start_idx:end_idx]
            else:
                range_data[key] = full_data[key]
                
        return {
            'data': range_data,
            'start_idx': start_idx,
            'end_idx': end_idx,
            'total_length': total_length,
            'has_more': end_idx < total_length
        }
    
    def has_data(self, code, timeframe='daily'):
        """检查股票是否有数据"""
        cache_key = f"{code}_{timeframe}"
        if cache_key in self.data_availability:
            return self.data_availability[cache_key]
        
        # 如果不知道，检查文件系统
        if timeframe == 'daily':
            file_path = f"analysis_results/{code}_analysis.csv"
        else:
            file_path = f"analysis_results_week/{code}_analysis.csv"
        
        return os.path.exists(file_path)
    
    def update_selected_stocks(self, stocks):
        """更新选中的股票列表并预加载数据"""
        self.selected_stocks = stocks
        # 预加载这些股票的完整数据到缓存
        for code in stocks:
            for timeframe in ['daily', 'weekly']:
                if self.has_data(code, timeframe):
                    self.get_stock_data(code, timeframe)
    
    def clear_cache(self):
        """清空缓存"""
        self.stock_data.clear()
        self.last_update.clear()

# 初始化缓存
data_cache = DataCache()

# 任务状态管理 (保持不变)
class TaskManager:
    def __init__(self):
        self.data_task = None
        self.strategy_task = None
        self.logs = []
        self.errors = []
        self.lock = threading.Lock()
    
    def log(self, message, level='info'):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        
        with self.lock:
            if level == 'error':
                self.errors.append(entry)
                if len(self.errors) > 100:
                    self.errors.pop(0)
                logger.error(message)
            else:
                self.logs.append(entry)
                if len(self.logs) > 100:
                    self.logs.pop(0)
                logger.info(message)
    
    def get_status(self):
        with self.lock:
            return {
                'data_task': self.data_task,
                'strategy_task': self.strategy_task,
                'logs': self.logs[-20:],
                'errors': self.errors[-20:],
                'stocks': data_cache.selected_stocks
            }

task_manager = TaskManager()

# 用户认证
users = {'muller718': 'zxcvbnm0717'}
sessions = {}

# 数据任务执行 (保持不变)
def execute_data_pipeline(freq):
    task_manager.data_task = freq
    try:
        task_manager.log(f"开始执行{freq}数据任务")
        
        if REAL_DATA:
            if freq == 'daily':
                success = fetch_daily_batch()
                if success:
                    process_batch()
                else:
                    raise Exception("日线数据获取失败")
            else:
                success = fetch_weekly_batch()
                if success:
                    process_batch_week()
                else:
                    raise Exception("周线数据获取失败")
        else:
            time.sleep(2)
            task_manager.log(f"{freq}数据模拟完成")
        
        data_cache.clear_cache()
        
        if data_cache.selected_stocks:
            data_cache.update_selected_stocks(data_cache.selected_stocks)
        
        task_manager.log(f"{freq}数据任务完成")
        
    except Exception as e:
        error_msg = f"{freq}数据任务失败: {str(e)}"
        task_manager.log(error_msg, 'error')
    finally:
        task_manager.data_task = None

def execute_strategy_pipeline(strategy_id):
    task_manager.strategy_task = strategy_id
    try:
        task_manager.log(f"开始执行策略{strategy_id}筛选")
        
        if REAL_DATA:
            selected_stocks = auto_select(strategy_id)
        else:
            time.sleep(1)
            selected_stocks = ['000001', '600036', '601318', '000858', '600519']
        
        data_cache.update_selected_stocks(selected_stocks)
        
        try:
            with open('selected_stocks.json', 'w', encoding='utf-8') as f:
                json.dump({
                    'stocks': selected_stocks,
                    'strategy_id': strategy_id,
                    'timestamp': datetime.now().isoformat()
                }, f, ensure_ascii=False, indent=2)
        except Exception as e:
            task_manager.log(f"保存选股结果失败: {e}", 'error')
        
        task_manager.log(f"策略{strategy_id}完成，选中{len(selected_stocks)}只股票")
        
    except Exception as e:
        error_msg = f"策略{strategy_id}失败: {str(e)}"
        task_manager.log(error_msg, 'error')
    finally:
        task_manager.strategy_task = None

# 初始化加载选股结果
def load_initial_stocks():
    try:
        if os.path.exists('selected_stocks.json'):
            with open('selected_stocks.json', 'r', encoding='utf-8') as f:
                data = json.load(f)
                stocks = data.get('stocks', [])
                if stocks:
                    data_cache.update_selected_stocks(stocks)
                    task_manager.log(f"加载选股结果: {len(stocks)} 只股票")
                    return
        
        stocks = []
        for data_dir in ['analysis_results', 'analysis_results_week']:
            if os.path.exists(data_dir):
                for file in os.listdir(data_dir):
                    if file.endswith('_analysis.csv'):
                        code = file.replace('_analysis.csv', '')
                        if code not in stocks:
                            stocks.append(code)
        
        if stocks:
            data_cache.update_selected_stocks(stocks[:10])
            task_manager.log(f"从数据目录加载: {len(stocks)} 只股票")
        else:
            default_stocks = ['000001', '600036']
            data_cache.update_selected_stocks(default_stocks)
            task_manager.log("使用默认股票列表")
            
    except Exception as e:
        task_manager.log(f"初始化股票数据失败: {e}", 'error')

# API路由
@app.route('/')
def index():
    return send_file('index.html')

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '').strip()
        password = data.get('password', '').strip()
        
        if not username or not password:
            return jsonify({'success': False, 'message': '用户名和密码不能为空'})
        
        if username in users and users[username] == password:
            session_id = str(hash(f"{username}{time.time()}"))
            sessions[session_id] = {
                'username': username,
                'login_time': time.time()
            }
            task_manager.log(f"用户 {username} 登录成功")
            return jsonify({'success': True, 'session_id': session_id})
        
        return jsonify({'success': False, 'message': '用户名或密码错误'})
    
    except Exception as e:
        task_manager.log(f"登录异常: {str(e)}", 'error')
        return jsonify({'success': False, 'message': '登录处理异常'})

@app.route('/api/execute_task', methods=['POST'])
def execute_task():
    try:
        data = request.get_json()
        task_type = data.get('type')
        task_id = data.get('id')
        
        if task_type == 'data':
            freq = task_id
            if freq not in ['daily', 'weekly']:
                return jsonify({'success': False, 'message': '无效的频率参数'})
            
            threading.Thread(target=execute_data_pipeline, args=(freq,), daemon=True).start()
            return jsonify({'success': True, 'message': f'{freq}数据任务开始执行'})
        
        elif task_type == 'strategy':
            try:
                strategy_id = int(task_id)
                if strategy_id < 1 or strategy_id > 5:
                    return jsonify({'success': False, 'message': '策略ID必须在1-5之间'})
            except:
                return jsonify({'success': False, 'message': '无效的策略ID'})
            
            threading.Thread(target=execute_strategy_pipeline, args=(strategy_id,), daemon=True).start()
            return jsonify({'success': True, 'message': f'策略{strategy_id}开始执行'})
        
        return jsonify({'success': False, 'message': '未知任务类型'})
    
    except Exception as e:
        task_manager.log(f"执行任务异常: {str(e)}", 'error')
        return jsonify({'success': False, 'message': '任务执行异常'})

@app.route('/api/status')
def get_status():
    status = task_manager.get_status()
    return jsonify(status)

@app.route('/api/stock_data_range/<code>')
def get_stock_data_range(code):
    """根据范围加载股票数据 - 核心API"""
    timeframe = request.args.get('timeframe', 'daily')
    start_idx = int(request.args.get('start', 0))
    end_idx = int(request.args.get('end', 100))
    
    result = data_cache.get_data_range(code, timeframe, start_idx, end_idx)
    
    if result:
        return jsonify({
            'success': True,
            'data': result['data'],
            'code': code,
            'timeframe': timeframe,
            'start_idx': result['start_idx'],
            'end_idx': result['end_idx'],
            'total_length': result['total_length'],
            'has_more': result['has_more']
        })
    
    return jsonify({'success': False, 'message': '股票数据不存在'})

@app.route('/api/stock_info/<code>')
def get_stock_info(code):
    """获取股票数据基本信息（总数据量等）"""
    timeframe = request.args.get('timeframe', 'daily')
    
    full_data = data_cache.get_stock_data(code, timeframe)
    if not full_data:
        return jsonify({'success': False, 'message': '股票数据不存在'})
    
    return jsonify({
        'success': True,
        'total_length': len(full_data['dates']),
        'code': code,
        'timeframe': timeframe
    })

@app.route('/api/check_stock_data/<code>')
def check_stock_data(code):
    timeframe = request.args.get('timeframe', 'daily')
    has_data = data_cache.has_data(code, timeframe)
    
    return jsonify({
        'success': True,
        'has_data': has_data,
        'code': code,
        'timeframe': timeframe
    })

@app.route('/api/test')
def test():
    return jsonify({
        'message': '服务正常', 
        'real_data': REAL_DATA,
        'stock_count': len(data_cache.selected_stocks),
        'timestamp': datetime.now().isoformat()
    })

# 忽略Chrome DevTools的请求
@app.route('/.well-known/appspecific/com.chrome.devtools.json')
def ignore_chrome_devtools():
    return '', 204


scheduler = BackgroundScheduler(timezone="Asia/Shanghai")
if __name__ == '__main__':
    # 启动定时任务
    scheduler.add_job(
        lambda: execute_data_pipeline('daily'),
        'cron',
        hour=17,
        minute=20,
        name="daily_pipeline"
    )
    scheduler.add_job(
        lambda: execute_strategy_pipeline('1'),
        'cron',
        hour=17,
        minute=30,
        name="daily_pipeline"
    )
    scheduler.add_job(
        lambda: execute_data_pipeline('weekly'),
        'cron',
        day_of_week='fri',
        hour=23,
        name="weekly_pipeline"
    )
    
    scheduler.start()

    print("=" * 60)
    print("🚀 股票分析平台 - 高效缓存版本")
    print("=" * 60)
    
    load_initial_stocks()
    
    print("访问地址: http://127.0.0.1:8080")
    print("=" * 60)
    
    task_manager.log("系统启动完成")
    
    app.run(host='127.0.0.1', port=8080, debug=False, threaded=True)