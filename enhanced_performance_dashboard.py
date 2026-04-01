#!/usr/bin/env python3
"""
增强版纯Python绩效监控面板 - Phase 3剩余工作

扩展功能:
1. 实时数据更新和自动刷新
2. 策略组合对比分析
3. 性能警报和通知系统
4. 多维度可视化图表
5. 导出和报告生成

设计目标:
- 为Phase 3完成提供完整的绩效监控解决方案
- 支持task_011的长期运行和监控
- 提供用户友好的实时监控界面
"""

import os
import sys
import json
import time
import math
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple, Callable
from pathlib import Path
import threading
import http.server
import socketserver
import urllib.parse

print("=" * 80)
print("📊 增强版纯Python绩效监控面板 - Phase 3剩余工作")
print("=" * 80)
print("扩展功能: 实时更新、组合对比、警报系统、多维可视化")
print("开始时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("=" * 80)

# 配置
WORKSPACE_ROOT = Path("/Users/chengming/.openclaw/workspace")
BACKTEST_RESULTS_DIR = WORKSPACE_ROOT / "pure_python_backtest_results"
DASHBOARD_DATA_DIR = WORKSPACE_ROOT / "performance_dashboard_data" / "enhanced"
DASHBOARD_DATA_DIR.mkdir(parents=True, exist_ok=True)

class EnhancedPerformanceMonitor:
    """增强版绩效监控器"""
    
    def __init__(self):
        self.strategies = {}
        self.combinations = {}
        self.performance_history = []
        self.alerts = []
        self.last_update = datetime.now()
        self.update_interval = 30  # 秒
        
        # 监控指标配置
        self.metrics_config = {
            "total_return": {"min": -0.2, "max": 0.5, "weight": 1.0},
            "sharpe_ratio": {"min": -1.0, "max": 3.0, "weight": 0.8},
            "max_drawdown": {"min": 0.0, "max": 0.5, "weight": 0.7, "inverse": True},
            "win_rate": {"min": 0.0, "max": 1.0, "weight": 0.6},
            "trade_count": {"min": 0, "max": 500, "weight": 0.4},
            "avg_profit": {"min": -100, "max": 1000, "weight": 0.5}
        }
        
        # 警报配置
        self.alert_config = {
            "performance_drop": {"threshold": -0.05, "window": 10},
            "high_drawdown": {"threshold": 0.15, "window": 5},
            "low_sharpe": {"threshold": 0.1, "window": 10},
            "no_trades": {"threshold": 0, "window": 20}
        }
        
        # 启动后台更新线程
        self.running = True
        self.update_thread = threading.Thread(target=self._background_update)
        self.update_thread.daemon = True
        self.update_thread.start()
        
        print("✅ 增强版绩效监控器初始化完成")
        print(f"   更新间隔: {self.update_interval}秒")
        print(f"   监控指标: {len(self.metrics_config)}个")
        print(f"   警报规则: {len(self.alert_config)}条")
    
    def _background_update(self):
        """后台更新线程"""
        while self.running:
            try:
                self._scan_for_new_results()
                self._check_alerts()
                self._save_snapshot()
            except Exception as e:
                print(f"⚠️ 后台更新错误: {e}")
            
            time.sleep(self.update_interval)
    
    def _scan_for_new_results(self):
        """扫描新的回测结果"""
        scan_time = datetime.now()
        new_results_count = 0
        
        # 扫描回测结果目录
        if BACKTEST_RESULTS_DIR.exists():
            for result_file in BACKTEST_RESULTS_DIR.rglob("*.json"):
                try:
                    file_mtime = datetime.fromtimestamp(result_file.stat().st_mtime)
                    
                    # 检查是否是新的或更新的文件
                    if file_mtime > self.last_update:
                        with open(result_file, 'r', encoding='utf-8') as f:
                            result_data = json.load(f)
                        
                        # 提取策略信息
                        if isinstance(result_data, dict):
                            self._process_result(result_data, str(result_file))
                            new_results_count += 1
                        
                except Exception as e:
                    print(f"⚠️ 处理结果文件 {result_file} 时出错: {e}")
        
        # 扫描组合测试结果
        combinations_dir = BACKTEST_RESULTS_DIR / "top5_combinations"
        if combinations_dir.exists():
            for combo_file in combinations_dir.glob("*.json"):
                try:
                    file_mtime = datetime.fromtimestamp(combo_file.stat().st_mtime)
                    
                    if file_mtime > self.last_update:
                        with open(combo_file, 'r', encoding='utf-8') as f:
                            combo_data = json.load(f)
                        
                        self._process_combination_result(combo_data, str(combo_file))
                        new_results_count += 1
                        
                except Exception as e:
                    print(f"⚠️ 处理组合文件 {combo_file} 时出错: {e}")
        
        if new_results_count > 0:
            print(f"📥 扫描到 {new_results_count} 个新的回测结果")
        
        self.last_update = scan_time
    
    def _process_result(self, result_data: Dict, source_file: str):
        """处理单个回测结果"""
        # 提取策略信息
        strategy_name = result_data.get("strategy_name", "未知策略")
        strategy_id = f"{strategy_name}_{int(time.time())}"
        
        # 确保结果有基本结构
        if "total_return" not in result_data:
            # 尝试从不同格式中提取
            if "performance" in result_data:
                perf = result_data["performance"]
                result_data.update({
                    "total_return": perf.get("total_return", 0),
                    "sharpe_ratio": perf.get("sharpe_ratio", 0),
                    "max_drawdown": perf.get("max_drawdown", 0),
                    "trade_count": perf.get("trade_count", 0)
                })
        
        # 添加策略到监控
        self.strategies[strategy_id] = {
            "id": strategy_id,
            "name": strategy_name,
            "results": result_data,
            "source_file": source_file,
            "added_time": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "metrics": self._calculate_metrics(result_data)
        }
        
        # 添加到历史记录
        history_entry = {
            "timestamp": datetime.now().isoformat(),
            "strategy_id": strategy_id,
            "strategy_name": strategy_name,
            "total_return": result_data.get("total_return", 0),
            "sharpe_ratio": result_data.get("sharpe_ratio", 0),
            "max_drawdown": result_data.get("max_drawdown", 0)
        }
        self.performance_history.append(history_entry)
        
        # 限制历史记录大小
        if len(self.performance_history) > 1000:
            self.performance_history = self.performance_history[-1000:]
    
    def _process_combination_result(self, combo_data: Dict, source_file: str):
        """处理组合回测结果"""
        if isinstance(combo_data, list):
            # 处理结果列表
            for result in combo_data:
                if isinstance(result, dict):
                    result["is_combination"] = True
                    self._process_result(result, source_file)
        elif isinstance(combo_data, dict):
            # 处理单个组合结果
            if "results" in combo_data and isinstance(combo_data["results"], list):
                # 包含结果列表的报告
                for result in combo_data["results"]:
                    if isinstance(result, dict):
                        result["is_combination"] = True
                        self._process_result(result, source_file)
            else:
                # 单个组合结果
                combo_data["is_combination"] = True
                self._process_result(combo_data, source_file)
    
    def _calculate_metrics(self, result_data: Dict) -> Dict:
        """计算策略的综合指标"""
        metrics = {}
        
        for metric_name, config in self.metrics_config.items():
            value = result_data.get(metric_name, 0)
            
            # 归一化到0-1范围
            min_val = config["min"]
            max_val = config["max"]
            weight = config["weight"]
            
            if max_val - min_val != 0:
                normalized = (value - min_val) / (max_val - min_val)
                # 限制在0-1之间
                normalized = max(0.0, min(1.0, normalized))
                
                # 如果是逆指标（如回撤），取反
                if config.get("inverse", False):
                    normalized = 1.0 - normalized
                
                metrics[metric_name] = {
                    "value": value,
                    "normalized": normalized,
                    "weighted": normalized * weight
                }
            else:
                metrics[metric_name] = {
                    "value": value,
                    "normalized": 0.5,
                    "weighted": 0.5 * weight
                }
        
        # 计算综合评分
        total_weight = sum(config["weight"] for config in self.metrics_config.values())
        weighted_sum = sum(metric["weighted"] for metric in metrics.values())
        
        if total_weight > 0:
            overall_score = weighted_sum / total_weight
        else:
            overall_score = 0.5
        
        metrics["overall_score"] = {
            "value": overall_score,
            "normalized": overall_score,
            "weighted": overall_score
        }
        
        return metrics
    
    def _check_alerts(self):
        """检查性能警报"""
        current_time = datetime.now()
        
        for strategy_id, strategy in list(self.strategies.items()):
            metrics = strategy.get("metrics", {})
            results = strategy.get("results", {})
            
            # 检查性能下降
            total_return = results.get("total_return", 0)
            if total_return < self.alert_config["performance_drop"]["threshold"]:
                self._add_alert(
                    strategy_id,
                    "performance_drop",
                    f"策略 {strategy['name']} 表现不佳: 总回报 {total_return:.2%}",
                    "warning"
                )
            
            # 检查高回撤
            max_drawdown = results.get("max_drawdown", 0)
            if max_drawdown > self.alert_config["high_drawdown"]["threshold"]:
                self._add_alert(
                    strategy_id,
                    "high_drawdown",
                    f"策略 {strategy['name']} 回撤过高: {max_drawdown:.2%}",
                    "danger"
                )
            
            # 检查低夏普比率
            sharpe_ratio = results.get("sharpe_ratio", 0)
            if sharpe_ratio < self.alert_config["low_sharpe"]["threshold"]:
                self._add_alert(
                    strategy_id,
                    "low_sharpe",
                    f"策略 {strategy['name']} 夏普比率过低: {sharpe_ratio:.3f}",
                    "warning"
                )
            
            # 检查无交易
            trade_count = results.get("trade_count", 0)
            if trade_count <= self.alert_config["no_trades"]["threshold"]:
                self._add_alert(
                    strategy_id,
                    "no_trades",
                    f"策略 {strategy['name']} 无交易信号",
                    "info"
                )
        
        # 清理旧警报（保留最近100条）
        if len(self.alerts) > 100:
            self.alerts = self.alerts[-100:]
    
    def _add_alert(self, strategy_id: str, alert_type: str, message: str, level: str):
        """添加警报"""
        alert = {
            "id": f"alert_{int(time.time())}_{random.randint(1000, 9999)}",
            "timestamp": datetime.now().isoformat(),
            "strategy_id": strategy_id,
            "alert_type": alert_type,
            "message": message,
            "level": level,  # info, warning, danger
            "acknowledged": False
        }
        
        # 避免重复警报
        recent_alerts = [a for a in self.alerts[-20:] 
                        if a["strategy_id"] == strategy_id 
                        and a["alert_type"] == alert_type
                        and (datetime.now() - datetime.fromisoformat(a["timestamp"])).seconds < 300]
        
        if not recent_alerts:
            self.alerts.append(alert)
            print(f"🚨 新警报: {message}")
    
    def _save_snapshot(self):
        """保存监控快照"""
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "strategy_count": len(self.strategies),
            "combination_count": len([s for s in self.strategies.values() 
                                    if s.get("results", {}).get("is_combination", False)]),
            "alert_count": len([a for a in self.alerts if not a["acknowledged"]]),
            "top_strategies": self.get_top_strategies(5),
            "recent_alerts": self.alerts[-10:] if self.alerts else []
        }
        
        snapshot_file = DASHBOARD_DATA_DIR / f"snapshot_{int(time.time())}.json"
        with open(snapshot_file, 'w', encoding='utf-8') as f:
            json.dump(snapshot, f, ensure_ascii=False, indent=2)
        
        # 保留最近50个快照
        snapshots = list(DASHBOARD_DATA_DIR.glob("snapshot_*.json"))
        if len(snapshots) > 50:
            # 按时间排序并删除旧的
            snapshots.sort(key=lambda x: x.stat().st_mtime)
            for old_snapshot in snapshots[:-50]:
                old_snapshot.unlink()
    
    def get_top_strategies(self, count: int = 10) -> List[Dict]:
        """获取表现最好的策略"""
        strategies_with_score = []
        
        for strategy_id, strategy in self.strategies.items():
            metrics = strategy.get("metrics", {})
            overall_score = metrics.get("overall_score", {}).get("value", 0.5)
            
            strategies_with_score.append({
                "strategy_id": strategy_id,
                "name": strategy["name"],
                "overall_score": overall_score,
                "total_return": strategy.get("results", {}).get("total_return", 0),
                "sharpe_ratio": strategy.get("results", {}).get("sharpe_ratio", 0),
                "max_drawdown": strategy.get("results", {}).get("max_drawdown", 0),
                "trade_count": strategy.get("results", {}).get("trade_count", 0),
                "is_combination": strategy.get("results", {}).get("is_combination", False)
            })
        
        # 按综合评分排序
        strategies_with_score.sort(key=lambda x: x["overall_score"], reverse=True)
        
        return strategies_with_score[:count]
    
    def get_strategy_comparison(self, strategy_ids: List[str]) -> Dict:
        """比较多个策略"""
        comparison = {
            "timestamp": datetime.now().isoformat(),
            "strategies": [],
            "metrics_comparison": {}
        }
        
        for strategy_id in strategy_ids:
            if strategy_id in self.strategies:
                strategy = self.strategies[strategy_id]
                comparison["strategies"].append({
                    "id": strategy_id,
                    "name": strategy["name"],
                    "results": strategy.get("results", {}),
                    "metrics": strategy.get("metrics", {})
                })
        
        # 计算指标对比
        if comparison["strategies"]:
            metrics_to_compare = ["total_return", "sharpe_ratio", "max_drawdown", "win_rate", "trade_count"]
            
            for metric in metrics_to_compare:
                values = []
                for strategy in comparison["strategies"]:
                    value = strategy["results"].get(metric, 0)
                    values.append(value)
                
                if values:
                    comparison["metrics_comparison"][metric] = {
                        "values": values,
                        "average": sum(values) / len(values),
                        "max": max(values),
                        "min": min(values),
                        "range": max(values) - min(values) if values else 0
                    }
        
        return comparison
    
    def get_performance_trend(self, strategy_id: str, window: int = 20) -> List[Dict]:
        """获取策略性能趋势"""
        trend = []
        
        # 从历史记录中筛选该策略的数据
        strategy_history = [
            entry for entry in self.performance_history
            if entry["strategy_id"] == strategy_id
        ]
        
        # 按时间排序
        strategy_history.sort(key=lambda x: x["timestamp"])
        
        # 取最近的数据
        recent_history = strategy_history[-window:] if len(strategy_history) > window else strategy_history
        
        for entry in recent_history:
            trend.append({
                "timestamp": entry["timestamp"],
                "total_return": entry.get("total_return", 0),
                "sharpe_ratio": entry.get("sharpe_ratio", 0),
                "max_drawdown": entry.get("max_drawdown", 0)
            })
        
        return trend
    
    def generate_report(self, report_type: str = "daily") -> Dict:
        """生成绩效报告"""
        report = {
            "generated_at": datetime.now().isoformat(),
            "report_type": report_type,
            "summary": {
                "total_strategies": len(self.strategies),
                "total_combinations": len([s for s in self.strategies.values() 
                                         if s.get("results", {}).get("is_combination", False)]),
                "active_alerts": len([a for a in self.alerts if not a["acknowledged"]]),
                "monitoring_since": self.last_update.isoformat()
            },
            "top_performers": self.get_top_strategies(10),
            "recent_alerts": self.alerts[-20:] if self.alerts else [],
            "performance_summary": self._generate_performance_summary()
        }
        
        return report
    
    def _generate_performance_summary(self) -> Dict:
        """生成性能摘要"""
        if not self.strategies:
            return {}
        
        all_returns = []
        all_sharpes = []
        all_drawdowns = []
        
        for strategy in self.strategies.values():
            results = strategy.get("results", {})
            all_returns.append(results.get("total_return", 0))
            all_sharpes.append(results.get("sharpe_ratio", 0))
            all_drawdowns.append(results.get("max_drawdown", 0))
        
        return {
            "returns": {
                "average": sum(all_returns) / len(all_returns) if all_returns else 0,
                "median": sorted(all_returns)[len(all_returns) // 2] if all_returns else 0,
                "max": max(all_returns) if all_returns else 0,
                "min": min(all_returns) if all_returns else 0,
                "std": math.sqrt(sum((r - (sum(all_returns) / len(all_returns))) ** 2 for r in all_returns) / len(all_returns)) 
                       if len(all_returns) > 1 else 0
            },
            "sharpes": {
                "average": sum(all_sharpes) / len(all_sharpes) if all_sharpes else 0,
                "median": sorted(all_sharpes)[len(all_sharpes) // 2] if all_sharpes else 0,
                "max": max(all_sharpes) if all_sharpes else 0,
                "min": min(all_sharpes) if all_sharpes else 0
            },
            "drawdowns": {
                "average": sum(all_drawdowns) / len(all_drawdowns) if all_drawdowns else 0,
                "median": sorted(all_drawdowns)[len(all_drawdowns) // 2] if all_drawdowns else 0,
                "max": max(all_drawdowns) if all_drawdowns else 0,
                "min": min(all_drawdowns) if all_drawdowns else 0
            }
        }
    
    def stop(self):
        """停止监控器"""
        self.running = False
        if self.update_thread.is_alive():
            self.update_thread.join(timeout=5)
        
        # 保存最终状态
        final_state = {
            "stopped_at": datetime.now().isoformat(),
            "total_strategies_monitored": len(self.strategies),
            "total_alerts_generated": len(self.alerts),
            "final_snapshot": self.generate_report("final")
        }
        
        final_file = DASHBOARD_DATA_DIR / "final_state.json"
        with open(final_file, 'w', encoding='utf-8') as f:
            json.dump(final_state, f, ensure_ascii=False, indent=2)
        
        print("🛑 增强版绩效监控器已停止")

class EnhancedDashboardWebServer:
    """增强版Web服务器"""
    
    def __init__(self, monitor: EnhancedPerformanceMonitor, port: int = 8080):
        self.monitor = monitor
        self.port = port
        self.server = None
        
    def start(self):
        """启动Web服务器"""
        handler = self._create_handler()
        self.server = socketserver.TCPServer(("", self.port), handler)
        
        print(f"🌐 增强版Web服务器启动在端口 {self.port}")
        print(f"   访问地址: http://localhost:{self.port}")
        print(f"   监控面板: http://localhost:{self.port}/dashboard")
        
        server_thread = threading.Thread(target=self.server.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        
        return self.server
    
    def _create_handler(self):
        """创建HTTP请求处理器"""
        monitor = self.monitor
        
        class DashboardHandler(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                # 解析URL
                parsed_path = urllib.parse.urlparse(self.path)
                path = parsed_path.path
                
                # 设置响应头
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()
                
                # 路由处理
                if path == '/':
                    self._send_home_page()
                elif path == '/dashboard':
                    self._send_dashboard()
                elif path == '/api/strategies':
                    self._send_json(monitor.get_top_strategies(50))
                elif path == '/api/alerts':
                    self._send_json(monitor.alerts[-50:] if monitor.alerts else [])
                elif path == '/api/report':
                    self._send_json(monitor.generate_report())
                elif path.startswith('/api/strategy/'):
                    # 提取策略ID
                    strategy_id = path.split('/')[-1]
                    if strategy_id in monitor.strategies:
                        self._send_json(monitor.strategies[strategy_id])
                    else:
                        self.send_error(404, "策略未找到")
                else:
                    self.send_error(404, "页面未找到")
            
            def _send_home_page(self):
                """发送主页"""
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>增强版量化策略绩效监控面板</title>
                    <meta charset="utf-8">
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; }
                        .container { display: flex; margin-top: 20px; }
                        .sidebar { width: 250px; background: white; padding: 15px; border-radius: 5px; margin-right: 20px; }
                        .main { flex: 1; background: white; padding: 20px; border-radius: 5px; }
                        .card { background: #fff; border: 1px solid #ddd; border-radius: 5px; padding: 15px; margin-bottom: 15px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        .metric { font-size: 24px; font-weight: bold; color: #2c3e50; }
                        .label { color: #7f8c8d; font-size: 14px; }
                        .alert { padding: 10px; border-left: 4px solid #e74c3c; background: #fdf2f2; margin-bottom: 10px; }
                        .warning { border-left-color: #f39c12; background: #fef9f2; }
                        .info { border-left-color: #3498db; background: #f2f9fe; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                        th { background: #f8f9fa; }
                        .positive { color: #27ae60; }
                        .negative { color: #e74c3c; }
                        .nav { list-style: none; padding: 0; }
                        .nav li { padding: 10px; border-bottom: 1px solid #eee; }
                        .nav li:hover { background: #f8f9fa; }
                        .nav a { text-decoration: none; color: #2c3e50; display: block; }
                    </style>
                </head>
                <body>
                    <div class="header">
                        <h1>📊 增强版量化策略绩效监控面板</h1>
                        <p>Phase 3剩余工作 - 实时监控系统</p>
                    </div>
                    
                    <div class="container">
                        <div class="sidebar">
                            <ul class="nav">
                                <li><a href="/dashboard">📈 监控面板</a></li>
                                <li><a href="/api/strategies" target="_blank">📋 策略列表 (API)</a></li>
                                <li><a href="/api/alerts" target="_blank">🚨 警报列表 (API)</a></li>
                                <li><a href="/api/report" target="_blank">📊 绩效报告 (API)</a></li>
                            </ul>
                            
                            <div class="card">
                                <h3>系统状态</h3>
                                <div class="metric">""" + str(len(monitor.strategies)) + """</div>
                                <div class="label">监控策略数量</div>
                                
                                <div class="metric">""" + str(len([a for a in monitor.alerts if not a["acknowledged"]])) + """</div>
                                <div class="label">未处理警报</div>
                                
                                <div class="metric">""" + str(len([s for s in monitor.strategies.values() if s.get("results", {}).get("is_combination", False)])) + """</div>
                                <div class="label">组合策略数量</div>
                            </div>
                        </div>
                        
                        <div class="main">
                            <h2>欢迎使用增强版绩效监控面板</h2>
                            <p>这是一个纯Python实现的零依赖实时监控系统，专为量化策略绩效监控设计。</p>
                            
                            <div class="card">
                                <h3>主要功能</h3>
                                <ul>
                                    <li><strong>实时监控</strong>: 自动扫描和更新回测结果</li>
                                    <li><strong>智能警报</strong>: 基于性能指标的自动警报系统</li>
                                    <li><strong>策略排名</strong>: 多维度综合评分和排名</li>
                                    <li><strong>组合对比</strong>: 策略组合性能对比分析</li>
                                    <li><strong>趋势分析</strong>: 策略性能变化趋势跟踪</li>
                                    <li><strong>报告生成</strong>: 自动生成详细绩效报告</li>
                                </ul>
                            </div>
                            
                            <div class="card">
                                <h3>使用说明</h3>
                                <p>1. 将回测结果JSON文件放入 <code>pure_python_backtest_results/</code> 目录</p>
                                <p>2. 系统会自动扫描并监控新的结果</p>
                                <p>3. 访问 <a href="/dashboard">监控面板</a> 查看实时数据</p>
                                <p>4. 使用API接口获取结构化数据</p>
                            </div>
                            
                            <div class="card">
                                <h3>最近警报</h3>
                                """ + self._format_recent_alerts(monitor.alerts[-5:]) + """
                            </div>
                        </div>
                    </div>
                    
                    <script>
                        // 自动刷新页面
                        setTimeout(function() {
                            location.reload();
                        }, 30000); // 每30秒刷新
                    </script>
                </body>
                </html>
                """
                self.wfile.write(html.encode('utf-8'))
            
            def _send_dashboard(self):
                """发送监控面板"""
                # 获取数据
                top_strategies = monitor.get_top_strategies(10)
                recent_alerts = monitor.alerts[-10:] if monitor.alerts else []
                report = monitor.generate_report()
                
                html = """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>监控面板 - 增强版绩效监控</title>
                    <meta charset="utf-8">
                    <style>
                        body { font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }
                        .header { background: #2c3e50; color: white; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                        .dashboard-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
                        .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                        h2 { margin-top: 0; }
                        table { width: 100%; border-collapse: collapse; }
                        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }
                        th { background: #f8f9fa; }
                        .positive { color: #27ae60; }
                        .negative { color: #e74c3c; }
                        .alert { padding: 10px; margin: 5px 0; border-radius: 3px; }
                        .alert-danger { background: #fdf2f2; border-left: 4px solid #e74c3c; }
                        .alert-warning { background: #fef9f2; border-left: 4px solid #f39c12; }
                        .alert-info { background: #f2f9fe; border-left: 4px solid #3498db; }
                        .metric-badge { display: inline-block; padding: 3px 8px; border-radius: 10px; font-size: 12px; }
                        .metric-good { background: #d4edda; color: #155724; }
                        .metric-fair { background: #fff3cd; color: #856404; }
                        .metric-poor { background: #f8d7da; color: #721c24; }
                        .refresh-btn { background: #3498db; color: white; border: none; padding: 10px 15px; border-radius: 3px; cursor: pointer; }
                        .refresh-btn:hover { background: #2980b9; }
                    </style>
                    <script>
                        function formatPercent(value) {
                            return (value * 100).toFixed(2) + '%';
                        }
                        
                        function getMetricClass(value, type) {
                            if (type === 'return') {
                                if (value > 0.1) return 'metric-good';
                                if (value > 0) return 'metric-fair';
                                return 'metric-poor';
                            } else if (type === 'sharpe') {
                                if (value > 1) return 'metric-good';
                                if (value > 0.5) return 'metric-fair';
                                return 'metric-poor';
                            } else if (type === 'drawdown') {
                                if (value < 0.05) return 'metric-good';
                                if (value < 0.1) return 'metric-fair';
                                return 'metric-poor';
                            }
                            return '';
                        }
                    </script>
                </head>
                <body>
                    <div class="header">
                        <h1>📈 实时监控面板</h1>
                        <p>最后更新: """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """ | 
                           监控策略: """ + str(len(monitor.strategies)) + """ | 
                           警报: """ + str(len([a for a in monitor.alerts if not a["acknowledged"]])) + """
                           <button class="refresh-btn" onclick="location.reload()">刷新</button>
                        </p>
                    </div>
                    
                    <div class="dashboard-grid">
                        <!-- 策略排名 -->
                        <div class="card">
                            <h2>🏆 策略排名</h2>
                            <table>
                                <thead>
                                    <tr>
                                        <th>排名</th>
                                        <th>策略名称</th>
                                        <th>总回报</th>
                                        <th>夏普比率</th>
                                        <th>最大回撤</th>
                                        <th>评分</th>
                                    </tr>
                                </thead>
                                <tbody>
                """
                
                # 添加策略行
                for i, strategy in enumerate(top_strategies[:10], 1):
                    name = strategy['name']
                    total_return = strategy['total_return']
                    sharpe_ratio = strategy['sharpe_ratio']
                    max_drawdown = strategy['max_drawdown']
                    overall_score = strategy['overall_score']
                    
                    html += f"""
                                    <tr>
                                        <td>{i}</td>
                                        <td>{name[:20]}{'...' if len(name) > 20 else ''}</td>
                                        <td class="{'positive' if total_return > 0 else 'negative'}">{total_return:.2%}</td>
                                        <td>{sharpe_ratio:.3f}</td>
                                        <td>{max_drawdown:.2%}</td>
                                        <td><span class="metric-badge metric-good">{overall_score:.3f}</span></td>
                                    </tr>
                    """
                
                html += """
                                </tbody>
                            </table>
                        </div>
                        
                        <!-- 性能摘要 -->
                        <div class="card">
                            <h2>📊 性能摘要</h2>
                """
                
                # 添加性能摘要
                if report.get('performance_summary'):
                    perf = report['performance_summary']
                    html += f"""
                            <p><strong>平均回报:</strong> {perf['returns']['average']:.2%}</p>
                            <p><strong>最佳回报:</strong> {perf['returns']['max']:.2%}</p>
                            <p><strong>平均夏普比率:</strong> {perf['sharpes']['average']:.3f}</p>
                            <p><strong>平均最大回撤:</strong> {perf['drawdowns']['average']:.2%}</p>
                            <p><strong>策略总数:</strong> {report['summary']['total_strategies']}</p>
                            <p><strong>组合策略:</strong> {report['summary']['total_combinations']}</p>
                    """
                
                html += """
                        </div>
                        
                        <!-- 最近警报 -->
                        <div class="card">
                            <h2>🚨 最近警报</h2>
                """
                
                # 添加警报
                for alert in recent_alerts[-5:]:
                    level_class = f"alert-{alert['level']}"
                    html += f"""
                            <div class="alert {level_class}">
                                <strong>{alert['timestamp'][11:19]}</strong><br>
                                {alert['message']}
                            </div>
                    """
                
                if not recent_alerts:
                    html += "<p>暂无警报</p>"
                
                html += """
                        </div>
                        
                        <!-- 系统信息 -->
                        <div class="card">
                            <h2>⚙️ 系统信息</h2>
                            <p><strong>开始时间:</strong> """ + monitor.last_update.strftime("%Y-%m-%d %H:%M:%S") + """</p>
                            <p><strong>更新间隔:</strong> """ + str(monitor.update_interval) + """ 秒</p>
                            <p><strong>监控指标:</strong> """ + str(len(monitor.metrics_config)) + """ 个</p>
                            <p><strong>警报规则:</strong> """ + str(len(monitor.alert_config)) + """ 条</p>
                            <p><strong>数据目录:</strong> """ + str(DASHBOARD_DATA_DIR) + """</p>
                        </div>
                    </div>
                    
                    <script>
                        // 每30秒自动刷新
                        setTimeout(function() {
                            location.reload();
                        }, 30000);
                    </script>
                </body>
                </html>
                """
                self.wfile.write(html.encode('utf-8'))
            
            def _send_json(self, data):
                """发送JSON数据"""
                json_str = json.dumps(data, ensure_ascii=False, indent=2)
                self.wfile.write(json_str.encode('utf-8'))
            
            def _format_recent_alerts(self, alerts):
                """格式化最近警报"""
                if not alerts:
                    return "<p>暂无警报</p>"
                
                html = ""
                for alert in alerts[-5:]:
                    level_class = ""
                    if alert["level"] == "danger":
                        level_class = "alert-danger"
                    elif alert["level"] == "warning":
                        level_class = "alert-warning"
                    else:
                        level_class = "alert-info"
                    
                    html += f"""
                    <div class="alert {level_class}">
                        <strong>{alert['timestamp'][11:19]}</strong>: {alert['message']}
                    </div>
                    """
                
                return html
            
            def log_message(self, format, *args):
                """重写日志方法，减少控制台输出"""
                pass
        
        return DashboardHandler
    
    def stop(self):
        """停止Web服务器"""
        if self.server:
            self.server.shutdown()
            print("🛑 Web服务器已停止")

def main():
    """主函数"""
    print("🚀 启动增强版绩效监控面板")
    
    try:
        # 创建监控器
        monitor = EnhancedPerformanceMonitor()
        
        # 创建并启动Web服务器
        web_server = EnhancedDashboardWebServer(monitor, port=8081)
        web_server.start()
        
        print("\n" + "=" * 80)
        print("✅ 增强版绩效监控面板启动成功!")
        print("=" * 80)
        print("📊 监控器状态:")
        print(f"   策略数量: {len(monitor.strategies)}")
        print(f"   警报数量: {len(monitor.alerts)}")
        print(f"   更新间隔: {monitor.update_interval}秒")
        print("\n🌐 Web界面:")
        print("   http://localhost:8081 - 主页")
        print("   http://localhost:8081/dashboard - 监控面板")
        print("\n🔧 API接口:")
        print("   http://localhost:8081/api/strategies - 策略列表")
        print("   http://localhost:8081/api/alerts - 警报列表")
        print("   http://localhost:8081/api/report - 绩效报告")
        print("\n" + "=" * 80)
        print("📝 说明: 按Ctrl+C停止监控")
        print("=" * 80)
        
        # 保持主线程运行
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\n🛑 收到停止信号，正在关闭...")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 清理资源
        if 'monitor' in locals():
            monitor.stop()
        if 'web_server' in locals():
            web_server.stop()
        
        print("🎯 增强版绩效监控面板已关闭")
        print("📁 数据保存在:", DASHBOARD_DATA_DIR)

if __name__ == "__main__":
    main()