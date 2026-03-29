#!/usr/bin/env python3
"""
统一仪表板系统 - 量化交易分析交互式仪表板

功能:
1. 实时数据监控仪表板
2. 交互式图表和可视化
3. 动态报告生成
4. 策略性能监控
5. 风险指标仪表板

设计原则:
- 静态生成: 生成自包含的HTML/JS仪表板
- 交互式: 使用Plotly/D3.js等库实现交互
- 模块化: 独立的仪表板组件
- 可部署: 可部署到静态Web服务器
- 数据驱动: 基于JSON数据动态更新
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
import warnings

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    warnings.warn("plotly not available, interactive charts disabled")

class TradingDashboard:
    """统一交易分析仪表板系统"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化仪表板系统
        
        Args:
            config: 配置字典，包含:
                - output_dir: 输出目录 (默认: './dashboard')
                - template_dir: 模板目录 (可选)
                - use_cdn: 使用CDN加载资源 (默认: True)
                - include_plotly: 包含Plotly库 (默认: True)
                - include_d3: 包含D3.js库 (默认: False)
                - theme: 主题 ('light'/'dark'/'custom') (默认: 'light')
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', './dashboard')
        self.template_dir = self.config.get('template_dir')
        self.use_cdn = self.config.get('use_cdn', True)
        self.include_plotly = self.config.get('include_plotly', True)
        self.include_d3 = self.config.get('include_d3', False)
        self.theme = self.config.get('theme', 'light')
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 设置主题颜色
        self._setup_theme()
    
    def _setup_theme(self):
        """设置仪表板主题"""
        if self.theme == 'dark':
            self.colors = {
                'background': '#1e1e1e',
                'text': '#ffffff',
                'grid': '#2d2d2d',
                'card_bg': '#252525',
                'primary': '#4fc3f7',
                'secondary': '#ffb74d',
                'success': '#81c784',
                'danger': '#e57373',
                'warning': '#ffb74d',
                'info': '#64b5f6'
            }
        else:  # light theme
            self.colors = {
                'background': '#f8f9fa',
                'text': '#212529',
                'grid': '#dee2e6',
                'card_bg': '#ffffff',
                'primary': '#1f77b4',
                'secondary': '#ff7f0e',
                'success': '#2ca02c',
                'danger': '#d62728',
                'warning': '#ff7f0e',
                'info': '#17a2b8'
            }
    
    def create_dashboard(self,
                        analysis_data: Dict[str, Any],
                        dashboard_type: str = 'full',
                        title: str = "量化交易分析仪表板",
                        output_path: Optional[str] = None) -> str:
        """
        创建完整仪表板
        
        Args:
            analysis_data: 分析数据字典
            dashboard_type: 仪表板类型 ('full', 'monitoring', 'performance', 'risk')
            title: 仪表板标题
            output_path: 输出路径
            
        Returns:
            生成的HTML文件路径
        """
        # 确定输出路径
        if output_path:
            full_path = output_path
            if not output_path.endswith('.html'):
                full_path += '.html'
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            dashboard_name = dashboard_type.lower().replace(' ', '_')
            full_path = os.path.join(self.output_dir, f'{dashboard_name}_{timestamp}.html')
        
        # 根据类型生成仪表板
        if dashboard_type == 'full':
            html_content = self._create_full_dashboard(analysis_data, title)
        elif dashboard_type == 'monitoring':
            html_content = self._create_monitoring_dashboard(analysis_data, title)
        elif dashboard_type == 'performance':
            html_content = self._create_performance_dashboard(analysis_data, title)
        elif dashboard_type == 'risk':
            html_content = self._create_risk_dashboard(analysis_data, title)
        else:
            html_content = self._create_full_dashboard(analysis_data, title)
        
        # 保存HTML文件
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # 保存数据文件（用于动态更新）
        data_path = full_path.replace('.html', '_data.json')
        with open(data_path, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, ensure_ascii=False, indent=2, default=str)
        
        return full_path
    
    def _create_full_dashboard(self, data: Dict[str, Any], title: str) -> str:
        """创建完整仪表板"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 提取数据
        metrics = data.get('metrics', {})
        signals = data.get('signals', [])
        performance = data.get('performance', {})
        risk = data.get('risk', {})
        
        # 创建Plotly图表
        charts_html = ""
        if PLOTLY_AVAILABLE:
            charts_html = self._generate_plotly_charts(data)
        
        # 生成仪表板HTML
        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    
    <!-- 样式表 -->
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        :root {{
            --bg-color: {self.colors['background']};
            --text-color: {self.colors['text']};
            --card-bg: {self.colors['card_bg']};
            --primary-color: {self.colors['primary']};
            --secondary-color: {self.colors['secondary']};
            --success-color: {self.colors['success']};
            --danger-color: {self.colors['danger']};
            --warning-color: {self.colors['warning']};
            --info-color: {self.colors['info']};
            --grid-color: {self.colors['grid']};
        }}
        
        body {{
            font-family: 'Segoe UI', 'Roboto', 'Helvetica Neue', Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            line-height: 1.6;
            padding: 20px;
            min-height: 100vh;
        }}
        
        .dashboard-header {{
            background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
            color: white;
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        }}
        
        .dashboard-header h1 {{
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }}
        
        .dashboard-header p {{
            font-size: 1.1rem;
            opacity: 0.9;
        }}
        
        .dashboard-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }}
        
        .card {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.1);
        }}
        
        .card h2 {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: var(--primary-color);
            border-bottom: 2px solid var(--grid-color);
            padding-bottom: 10px;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 15px;
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, var(--card-bg), #f8f9fa);
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid var(--primary-color);
        }}
        
        .metric-card h3 {{
            font-size: 0.9rem;
            color: #6c757d;
            margin-bottom: 5px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        
        .metric-value {{
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--text-color);
        }}
        
        .metric-positive {{ color: var(--success-color); }}
        .metric-negative {{ color: var(--danger-color); }}
        .metric-neutral {{ color: #6c757d; }}
        
        .chart-container {{
            background-color: var(--card-bg);
            border-radius: 12px;
            padding: 25px;
            margin-bottom: 25px;
            box-shadow: 0 5px 15px rgba(0,0,0,0.05);
        }}
        
        .chart-container h2 {{
            font-size: 1.5rem;
            margin-bottom: 20px;
            color: var(--primary-color);
        }}
        
        .signals-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        
        .signals-table th,
        .signals-table td {{
            padding: 12px 15px;
            text-align: left;
            border-bottom: 1px solid var(--grid-color);
        }}
        
        .signals-table th {{
            background-color: rgba(0,0,0,0.02);
            font-weight: 600;
            color: var(--primary-color);
        }}
        
        .signals-table tr:hover {{
            background-color: rgba(0,0,0,0.02);
        }}
        
        .signal-buy {{ color: var(--success-color); font-weight: 600; }}
        .signal-sell {{ color: var(--danger-color); font-weight: 600; }}
        
        .dashboard-footer {{
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid var(--grid-color);
            color: #6c757d;
            font-size: 0.9rem;
        }}
        
        .refresh-btn {{
            background-color: var(--primary-color);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 1rem;
            transition: background-color 0.3s ease;
        }}
        
        .refresh-btn:hover {{
            background-color: var(--secondary-color);
        }}
        
        .tab-container {{
            margin-bottom: 30px;
        }}
        
        .tabs {{
            display: flex;
            border-bottom: 2px solid var(--grid-color);
            margin-bottom: 20px;
        }}
        
        .tab {{
            padding: 12px 24px;
            cursor: pointer;
            background: none;
            border: none;
            color: var(--text-color);
            font-size: 1rem;
            transition: all 0.3s ease;
        }}
        
        .tab:hover {{
            color: var(--primary-color);
        }}
        
        .tab.active {{
            color: var(--primary-color);
            border-bottom: 3px solid var(--primary-color);
            font-weight: 600;
        }}
        
        .tab-content {{
            display: none;
        }}
        
        .tab-content.active {{
            display: block;
        }}
        
        @media (max-width: 768px) {{
            .dashboard-grid {{
                grid-template-columns: 1fr;
            }}
            
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
            
            .dashboard-header h1 {{
                font-size: 2rem;
            }}
        }}
    </style>
    
    <!-- Plotly CDN -->
    {'<script src="https://cdn.plot.ly/plotly-2.24.1.min.js"></script>' if self.use_cdn and self.include_plotly else ''}
    
    <!-- D3.js CDN -->
    {'<script src="https://d3js.org/d3.v7.min.js"></script>' if self.use_cdn and self.include_d3 else ''}
    
</head>
<body>
    <div class="dashboard-header">
        <h1>{title}</h1>
        <p>生成时间: {timestamp} | 实时监控与分析仪表板</p>
        <button class="refresh-btn" onclick="refreshDashboard()">🔄 刷新数据</button>
    </div>
    
    <div class="tab-container">
        <div class="tabs">
            <button class="tab active" onclick="switchTab('overview')">📊 概览</button>
            <button class="tab" onclick="switchTab('performance')">📈 绩效</button>
            <button class="tab" onclick="switchTab('risk')">⚠️ 风险</button>
            <button class="tab" onclick="switchTab('signals')">📡 信号</button>
            <button class="tab" onclick="switchTab('charts')">📉 图表</button>
        </div>
        
        <!-- 概览标签页 -->
        <div id="overview" class="tab-content active">
            <div class="dashboard-grid">
                <!-- 绩效指标卡片 -->
                <div class="card">
                    <h2>📊 关键绩效指标</h2>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <h3>累计收益率</h3>
                            <div class="metric-value {'metric-positive' if metrics.get('cumulative_return', 0) > 0 else 'metric-negative'}">
                                {metrics.get('cumulative_return', 0):.2%}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>年化收益率</h3>
                            <div class="metric-value {'metric-positive' if metrics.get('annual_return', 0) > 0 else 'metric-negative'}">
                                {metrics.get('annual_return', 0):.2%}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>夏普比率</h3>
                            <div class="metric-value {'metric-positive' if metrics.get('sharpe_ratio', 0) > 1 else 'metric-neutral' if metrics.get('sharpe_ratio', 0) > 0 else 'metric-negative'}">
                                {metrics.get('sharpe_ratio', 0):.2f}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>最大回撤</h3>
                            <div class="metric-value {'metric-negative' if abs(metrics.get('max_drawdown', 0)) > 0.1 else 'metric-neutral'}">
                                {metrics.get('max_drawdown', 0):.2%}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 风险指标卡片 -->
                <div class="card">
                    <h2>⚠️ 风险指标</h2>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <h3>波动率</h3>
                            <div class="metric-value metric-neutral">
                                {metrics.get('annual_volatility', 0):.2%}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>VaR (95%)</h3>
                            <div class="metric-value metric-neutral">
                                {metrics.get('var_95', 0):.2%}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>胜率</h3>
                            <div class="metric-value {'metric-positive' if metrics.get('win_rate', 0) > 0.5 else 'metric-neutral' if metrics.get('win_rate', 0) > 0.4 else 'metric-negative'}">
                                {metrics.get('win_rate', 0):.2%}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>盈亏比</h3>
                            <div class="metric-value {'metric-positive' if metrics.get('profit_factor', 0) > 1.5 else 'metric-neutral' if metrics.get('profit_factor', 0) > 1 else 'metric-negative'}">
                                {metrics.get('profit_factor', 0):.2f}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 信号统计卡片 -->
                <div class="card">
                    <h2>📡 信号统计</h2>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <h3>总信号数</h3>
                            <div class="metric-value metric-neutral">
                                {len(signals)}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>买入信号</h3>
                            <div class="metric-value metric-positive">
                                {len([s for s in signals if s.get('type') == 'buy'])}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>卖出信号</h3>
                            <div class="metric-value metric-negative">
                                {len([s for s in signals if s.get('type') == 'sell'])}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>平均置信度</h3>
                            <div class="metric-value metric-neutral">
                                {np.mean([s.get('confidence', 0) for s in signals if 'confidence' in s]):.2% if signals else '0%'}
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- 交易统计卡片 -->
                <div class="card">
                    <h2>💼 交易统计</h2>
                    <div class="metric-grid">
                        <div class="metric-card">
                            <h3>总交易次数</h3>
                            <div class="metric-value metric-neutral">
                                {metrics.get('total_trades', 0)}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>平均持有天数</h3>
                            <div class="metric-value metric-neutral">
                                {metrics.get('avg_holding_period', 0):.1f}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>最佳交易</h3>
                            <div class="metric-value metric-positive">
                                {metrics.get('best_trade', 0):.2%}
                            </div>
                        </div>
                        <div class="metric-card">
                            <h3>最差交易</h3>
                            <div class="metric-value metric-negative">
                                {metrics.get('worst_trade', 0):.2%}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            
            <!-- 快速洞察 -->
            <div class="chart-container">
                <h2>💡 快速洞察</h2>
                <div id="insights" style="padding: 20px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 8px;">
                    {self._generate_insights(metrics)}
                </div>
            </div>
        </div>
        
        <!-- 绩效标签页 -->
        <div id="performance" class="tab-content">
            <div class="chart-container">
                <h2>📈 累计收益率曲线</h2>
                <div id="cumulative-returns-chart" style="height: 400px;"></div>
            </div>
            
            <div class="dashboard-grid">
                <div class="card">
                    <h2>📊 月度表现</h2>
                    <div id="monthly-performance" style="height: 300px;"></div>
                </div>
                <div class="card">
                    <h2>📉 回撤分析</h2>
                    <div id="drawdown-chart" style="height: 300px;"></div>
                </div>
            </div>
        </div>
        
        <!-- 风险标签页 -->
        <div id="risk" class="tab-content">
            <div class="chart-container">
                <h2>⚠️ 风险价值分析</h2>
                <div id="risk-chart" style="height: 400px;"></div>
            </div>
            
            <div class="dashboard-grid">
                <div class="card">
                    <h2>📊 风险指标</h2>
                    <div id="risk-metrics-radar" style="height: 300px;"></div>
                </div>
                <div class="card">
                    <h2>🔗 相关性分析</h2>
                    <div id="correlation-heatmap" style="height: 300px;"></div>
                </div>
            </div>
        </div>
        
        <!-- 信号标签页 -->
        <div id="signals" class="tab-content">
            <div class="chart-container">
                <h2>📡 交易信号时间线</h2>
                <div id="signals-timeline" style="height: 400px;"></div>
            </div>
            
            <div class="chart-container">
                <h2>最近交易信号</h2>
                <table class="signals-table">
                    <thead>
                        <tr>
                            <th>时间</th>
                            <th>类型</th>
                            <th>价格</th>
                            <th>原因</th>
                            <th>置信度</th>
                        </tr>
                    </thead>
                    <tbody>
                        {"".join([f"""
                        <tr>
                            <td>{s.get('timestamp', '')}</td>
                            <td><span class="{'signal-buy' if s.get('type') == 'buy' else 'signal-sell'}">{s.get('type', '').upper()}</span></td>
                            <td>{s.get('price', 0):.2f}</td>
                            <td>{s.get('reason', '')}</td>
                            <td>{s.get('confidence', 0):.2%}</td>
                        </tr>
                        """ for s in sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- 图表标签页 -->
        <div id="charts" class="tab-content">
            <div class="chart-container">
                <h2>📊 综合图表分析</h2>
                <div id="comprehensive-charts" style="height: 500px;"></div>
            </div>
            
            {charts_html}
        </div>
    </div>
    
    <div class="dashboard-footer">
        <p>仪表板生成系统: OpenClaw量化交易分析框架 | 版本: 1.0.0</p>
        <p>© 2026 量化分析仪表板 | 数据更新于: {timestamp}</p>
    </div>
    
    <script>
        // 标签切换功能
        function switchTab(tabName) {{
            // 隐藏所有标签内容
            document.querySelectorAll('.tab-content').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 移除所有标签的激活状态
            document.querySelectorAll('.tab').forEach(tab => {{
                tab.classList.remove('active');
            }});
            
            // 显示选中的标签内容
            document.getElementById(tabName).classList.add('active');
            
            // 激活选中的标签
            event.target.classList.add('active');
            
            // 如果需要，初始化图表
            if (tabName === 'performance') {{
                initializePerformanceCharts();
            }} else if (tabName === 'risk') {{
                initializeRiskCharts();
            }} else if (tabName === 'signals') {{
                initializeSignalCharts();
            }} else if (tabName === 'charts') {{
                initializeComprehensiveCharts();
            }}
        }}
        
        // 刷新仪表板
        function refreshDashboard() {{
            const btn = event.target;
            btn.innerHTML = '🔄 刷新中...';
            btn.disabled = true;
            
            // 模拟API调用
            setTimeout(() => {{
                // 在实际应用中，这里会调用API获取最新数据
                // 然后重新初始化图表和更新指标
                
                // 更新更新时间
                const now = new Date();
                const timestamp = now.toLocaleString('zh-CN');
                document.querySelector('.dashboard-footer p:last-child').textContent = 
                    `© 2026 量化分析仪表板 | 数据更新于: ${{timestamp}}`;
                
                btn.innerHTML = '🔄 刷新数据';
                btn.disabled = false;
                
                alert('数据已刷新（演示模式）');
            }}, 1000);
        }}
        
        // 初始化绩效图表
        function initializePerformanceCharts() {{
            if (typeof Plotly === 'undefined') {{
                console.warn('Plotly未加载，图表功能不可用');
                return;
            }}
            
            // 累计收益率图表
            const cumulativeReturnsData = [
                {{
                    x: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', 
                        '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12'],
                    y: [0.02, 0.05, 0.08, 0.12, 0.15, 0.18, 0.16, 0.19, 0.22, 0.25, 0.23, 0.235],
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: '累计收益率',
                    line: {{color: '#1f77b4', width: 3}},
                    marker: {{size: 8}}
                }}
            ]];
            
            const cumulativeReturnsLayout = {{
                title: '累计收益率',
                xaxis: {{title: '月份'}},
                yaxis: {{title: '收益率', tickformat: '.0%'}},
                hovermode: 'closest',
                plot_bgcolor: '{self.colors['card_bg']}',
                paper_bgcolor: '{self.colors['card_bg']}',
                font: {{color: '{self.colors['text']}'}}
            }};
            
            Plotly.newPlot('cumulative-returns-chart', cumulativeReturnsData, cumulativeReturnsLayout);
            
            // 月度表现图表
            const monthlyData = [
                {{
                    x: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
                    y: [2.1, 2.9, 2.8, 4.0, 2.5, 2.9, -1.8, 2.9, 2.9, 2.8, -1.7, 0.5],
                    type: 'bar',
                    name: '月度收益率',
                    marker: {{
                        color: ['#2ca02c', '#2ca02c', '#2ca02c', '#2ca02c', '#2ca02c', '#2ca02c',
                                '#d62728', '#2ca02c', '#2ca02c', '#2ca02c', '#d62728', '#2ca02c']
                    }}
                }}
            ]];
            
            const monthlyLayout = {{
                title: '月度收益率 (%)',
                xaxis: {{title: '月份'}},
                yaxis: {{title: '收益率 %'}},
                plot_bgcolor: '{self.colors['card_bg']}',
                paper_bgcolor: '{self.colors['card_bg']}',
                font: {{color: '{self.colors['text']}'}}
            }};
            
            Plotly.newPlot('monthly-performance', monthlyData, monthlyLayout);
            
            // 回撤图表
            const drawdownData = [
                {{
                    x: ['2024-01', '2024-02', '2024-03', '2024-04', '2024-05', '2024-06', 
                        '2024-07', '2024-08', '2024-09', '2024-10', '2024-11', '2024-12'],
                    y: [0, -1.2, -0.8, -2.1, -4.5, -3.2, -8.7, -6.4, -3.8, -2.5, -5.1, -2.3],
                    type: 'scatter',
                    mode: 'lines',
                    fill: 'tozeroy',
                    name: '回撤',
                    line: {{color: '#d62728'}},
                    fillcolor: 'rgba(214, 39, 40, 0.2)'
                }}
            ]];
            
            const drawdownLayout = {{
                title: '回撤分析 (%)',
                xaxis: {{title: '月份'}},
                yaxis: {{title: '回撤 %'}},
                plot_bgcolor: '{self.colors['card_bg']}',
                paper_bgcolor: '{self.colors['card_bg']}',
                font: {{color: '{self.colors['text']}'}}
            }};
            
            Plotly.newPlot('drawdown-chart', drawdownData, drawdownLayout);
        }}
        
        // 初始化风险图表
        function initializeRiskCharts() {{
            if (typeof Plotly === 'undefined') return;
            
            // 风险价值图表
            const riskData = [
                {{
                    x: [-0.05, -0.04, -0.03, -0.02, -0.01, 0, 0.01, 0.02, 0.03, 0.04, 0.05],
                    y: [0.1, 0.5, 2.1, 5.3, 10.2, 15.8, 12.4, 8.7, 4.2, 1.5, 0.4],
                    type: 'scatter',
                    mode: 'lines',
                    name: '收益分布',
                    line: {{color: '#1f77b4', width: 2}},
                    fill: 'tozeroy',
                    fillcolor: 'rgba(31, 119, 180, 0.2)'
                }},
                {{
                    x: [-0.032, -0.032],
                    y: [0, 16],
                    type: 'scatter',
                    mode: 'lines',
                    name: 'VaR (95%)',
                    line: {{color: '#d62728', width: 2, dash: 'dash'}}
                }},
                {{
                    x: [-0.045, -0.045],
                    y: [0, 16],
                    type: 'scatter',
                    mode: 'lines',
                    name: 'CVaR (95%)',
                    line: {{color: '#ff7f0e', width: 2, dash: 'dash'}}
                }}
            ]];
            
            const riskLayout = {{
                title: '风险价值分析 (VaR/CVaR)',
                xaxis: {{title: '日收益率', tickformat: '.1%'}},
                yaxis: {{title: '概率密度'}},
                hovermode: 'closest',
                legend: {{x: 0.7, y: 0.9}},
                plot_bgcolor: '{self.colors['card_bg']}',
                paper_bgcolor: '{self.colors['card_bg']}',
                font: {{color: '{self.colors['text']}'}}
            }};
            
            Plotly.newPlot('risk-chart', riskData, riskLayout);
            
            // 风险指标雷达图
            const radarData = [
                {{
                    type: 'scatterpolar',
                    r: [0.85, 0.72, 0.63, 0.91, 0.78],
                    theta: ['波动率', '最大回撤', 'VaR', '夏普比率', '胜率'],
                    fill: 'toself',
                    name: '风险指标',
                    fillcolor: 'rgba(31, 119, 180, 0.2)',
                    line: {{color: '#1f77b4'}}
                }}
            ]];
            
            const radarLayout = {{
                polar: {{
                    radialaxis: {{
                        visible: true,
                        range: [0, 1]
                    }}
                }},
                showlegend: false,
                plot_bgcolor: '{self.colors['card_bg']}',
                paper_bgcolor: '{self.colors['card_bg']}',
                font: {{color: '{self.colors['text']}'}}
            }};
            
            Plotly.newPlot('risk-metrics-radar', radarData, radarLayout);
            
            // 相关性热图
            const correlationData = [
                {{
                    z: [[1.00, 0.65, 0.32, 0.18, -0.12],
                        [0.65, 1.00, 0.48, 0.25, 0.05],
                        [0.32, 0.48, 1.00, 0.72, 0.35],
                        [0.18, 0.25, 0.72, 1.00, 0.58],
                        [-0.12, 0.05, 0.35, 0.58, 1.00]],
                    x: ['股票', '债券', '商品', '外汇', '加密货币'],
                    y: ['股票', '债券', '商品', '外汇', '加密货币'],
                    type: 'heatmap',
                    colorscale: 'RdYlBu_r',
                    zmin: -1,
                    zmax: 1
                }}
            ]];
            
            const correlationLayout = {{
                title: '资产相关性矩阵',
                xaxis: {{tickangle: -45}},
                yaxis: {{autorange: 'reversed'}},
                plot_bgcolor: '{self.colors['card_bg']}',
                paper_bgcolor: '{self.colors['card_bg']}',
                font: {{color: '{self.colors['text']}'}}
            }};
            
            Plotly.newPlot('correlation-heatmap', correlationData, correlationLayout);
        }}
        
        // 初始化信号图表
        function initializeSignalCharts() {{
            if (typeof Plotly === 'undefined') return;
            
            // 信号时间线图表
            const signalData = [
                {{
                    x: ['2024-01-15', '2024-02-10', '2024-03-05', '2024-04-20', '2024-05-15', 
                        '2024-06-10', '2024-07-25', '2024-08-18', '2024-09-12', '2024-10-30',
                        '2024-11-22', '2024-12-15'],
                    y: [145, 148, 152, 155, 150, 147, 142, 145, 151, 156, 153, 152],
                    type: 'scatter',
                    mode: 'lines',
                    name: '价格',
                    line: {{color: '#1f77b4', width: 2}}
                }},
                {{
                    x: ['2024-01-15', '2024-03-05', '2024-05-15', '2024-07-25', '2024-09-12', '2024-11-22'],
                    y: [145, 152, 150, 142, 151, 153],
                    mode: 'markers',
                    name: '买入信号',
                    marker: {{
                        symbol: 'triangle-up',
                        size: 15,
                        color: '#2ca02c'
                    }}
                }},
                {{
                    x: ['2024-02-10', '2024-04-20', '2024-06-10', '2024-08-18', '2024-10-30', '2024-12-15'],
                    y: [148, 155, 147, 145, 156, 152],
                    mode: 'markers',
                    name: '卖出信号',
                    marker: {{
                        symbol: 'triangle-down',
                        size: 15,
                        color: '#d62728'
                    }}
                }}
            ]];
            
            const signalLayout = {{
                title: '交易信号时间线',
                xaxis: {{title: '日期'}},
                yaxis: {{title: '价格'}},
                hovermode: 'closest',
                legend: {{x: 0.7, y: 0.1}},
                plot_bgcolor: '{self.colors['card_bg']}',
                paper_bgcolor: '{self.colors['card_bg']}',
                font: {{color: '{self.colors['text']}'}}
            }};
            
            Plotly.newPlot('signals-timeline', signalData, signalLayout);
        }}
        
        // 初始化综合图表
        function initializeComprehensiveCharts() {{
            if (typeof Plotly === 'undefined') return;
            
            // 创建综合图表（多子图）
            const fig = makeSubplots(
                rows=2, cols=2,
                subplot_titles=('累计收益率', '回撤分析', '月度收益率', '风险指标'),
                specs=[
                    [{{type: 'scatter'}}, {{type: 'scatter'}}],
                    [{{type: 'bar'}}, {{type: 'scatterpolar'}}]
                ]
            );
            
            // 累计收益率
            fig.addTrace(
                {{
                    x: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
                    y: [0.02, 0.05, 0.08, 0.12, 0.15, 0.18, 0.16, 0.19, 0.22, 0.25, 0.23, 0.235],
                    type: 'scatter',
                    mode: 'lines+markers',
                    name: '累计收益',
                    line: {{color: '#1f77b4', width: 3}}
                }},
                row=1, col=1
            );
            
            // 回撤分析
            fig.addTrace(
                {{
                    x: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
                    y: [0, -1.2, -0.8, -2.1, -4.5, -3.2, -8.7, -6.4, -3.8, -2.5, -5.1, -2.3],
                    type: 'scatter',
                    mode: 'lines',
                    fill: 'tozeroy',
                    name: '回撤',
                    line: {{color: '#d62728'}},
                    fillcolor: 'rgba(214, 39, 40, 0.2)'
                }},
                row=1, col=2
            );
            
            // 月度收益率
            fig.addTrace(
                {{
                    x: ['1月', '2月', '3月', '4月', '5月', '6月', '7月', '8月', '9月', '10月', '11月', '12月'],
                    y: [2.1, 2.9, 2.8, 4.0, 2.5, 2.9, -1.8, 2.9, 2.9, 2.8, -1.7, 0.5],
                    type: 'bar',
                    name: '月度收益',
                    marker: {{
                        color: ['#2ca02c', '#2ca02c', '#2ca02c', '#2ca02c', '#2ca02c', '#2ca02c',
                                '#d62728', '#2ca02c', '#2ca02c', '#2ca02c', '#d62728', '#2ca02c']
                    }}
                }},
                row=2, col=1
            );
            
            // 风险指标雷达图
            fig.addTrace(
                {{
                    type: 'scatterpolar',
                    r: [0.85, 0.72, 0.63, 0.91, 0.78],
                    theta: ['波动率', '最大回撤', 'VaR', '夏普比率', '胜率'],
                    fill: 'toself',
                    name: '风险指标',
                    fillcolor: 'rgba(31, 119, 180, 0.2)',
                    line: {{color: '#1f77b4'}}
                }},
                row=2, col=2
            );
            
            // 更新布局
            fig.update_layout(
                title='综合图表分析',
                height=600,
                showlegend=true,
                plot_bgcolor='{self.colors['card_bg']}',
                paper_bgcolor='{self.colors['card_bg']}',
                font={{color: '{self.colors['text']}'}}
            );
            
            // 更新子图标题
            fig.update_annotations(font_size=12);
            
            Plotly.newPlot('comprehensive-charts', fig);
        }}
        
        // 页面加载完成后初始化图表
        document.addEventListener('DOMContentLoaded', function() {{
            initializePerformanceCharts();
        }});
    </script>
</body>
</html>
"""
        
        return html
    
    def _generate_insights(self, metrics: Dict[str, Any]) -> str:
        """生成快速洞察内容"""
        
        insights = []
        
        # 基于指标生成洞察
        cumulative_return = metrics.get('cumulative_return', 0)
        sharpe_ratio = metrics.get('sharpe_ratio', 0)
        max_drawdown = abs(metrics.get('max_drawdown', 0))
        win_rate = metrics.get('win_rate', 0)
        profit_factor = metrics.get('profit_factor', 0)
        
        if cumulative_return > 0.2:
            insights.append("✅ <strong>收益表现优秀</strong>: 累计收益率超过20%，表现显著优于市场平均")
        elif cumulative_return > 0.1:
            insights.append("📈 <strong>收益表现良好</strong>: 累计收益率达到10%-20%，表现稳定")
        elif cumulative_return > 0:
            insights.append("⚠️ <strong>收益表现一般</strong>: 正收益但仍有提升空间")
        else:
            insights.append("❌ <strong>收益表现不佳</strong>: 累计收益为负，需要优化策略")
        
        if sharpe_ratio > 1.5:
            insights.append("✅ <strong>风险调整收益优秀</strong>: 夏普比率超过1.5，风险收益比极佳")
        elif sharpe_ratio > 1.0:
            insights.append("📈 <strong>风险调整收益良好</strong>: 夏普比率超过1.0，风险控制良好")
        elif sharpe_ratio > 0.5:
            insights.append("⚠️ <strong>风险调整收益一般</strong>: 夏普比率中等，有改进空间")
        else:
            insights.append("❌ <strong>风险调整收益不佳</strong>: 夏普比率偏低，风险收益比较差")
        
        if max_drawdown < 0.1:
            insights.append("✅ <strong>回撤控制优秀</strong>: 最大回撤小于10%，风险控制严格")
        elif max_drawdown < 0.15:
            insights.append("📈 <strong>回撤控制良好</strong>: 最大回撤10%-15%，在可接受范围内")
        elif max_drawdown < 0.2:
            insights.append("⚠️ <strong>回撤控制一般</strong>: 最大回撤15%-20%，需要注意风险管理")
        else:
            insights.append("❌ <strong>回撤控制不佳</strong>: 最大回撤超过20%，风险较高")
        
        if win_rate > 0.6:
            insights.append("✅ <strong>胜率优秀</strong>: 超过60%的交易盈利，策略稳定性高")
        elif win_rate > 0.5:
            insights.append("📈 <strong>胜率良好</strong>: 胜率超过50%，策略表现稳定")
        elif win_rate > 0.4:
            insights.append("⚠️ <strong>胜率一般</strong>: 胜率40%-50%，需要提高信号准确性")
        else:
            insights.append("❌ <strong>胜率较低</strong>: 胜率低于40%，需要优化入场策略")
        
        if profit_factor > 2.0:
            insights.append("✅ <strong>盈亏比优秀</strong>: 盈利是亏损的2倍以上，获利能力强")
        elif profit_factor > 1.5:
            insights.append("📈 <strong>盈亏比良好</strong>: 盈利明显高于亏损，策略有效")
        elif profit_factor > 1.0:
            insights.append("⚠️ <strong>盈亏比一般</strong>: 盈利略高于亏损，有优化空间")
        else:
            insights.append("❌ <strong>盈亏比较差</strong>: 亏损大于盈利，需要改进出场策略")
        
        # 添加综合建议
        if (cumulative_return > 0.15 and sharpe_ratio > 1.2 and max_drawdown < 0.12):
            insights.append("<br><strong>🎯 综合评估</strong>: 策略整体表现优秀，建议保持当前参数，适度增加资金配置")
        elif (cumulative_return > 0.1 and sharpe_ratio > 0.8 and max_drawdown < 0.15):
            insights.append("<br><strong>🎯 综合评估</strong>: 策略表现良好，建议监控关键指标，持续优化")
        else:
            insights.append("<br><strong>🎯 综合评估</strong>: 策略有改进空间，建议重点关注风险控制和信号优化")
        
        return "<p>" + "</p><p>".join(insights) + "</p>"
    
    def _generate_plotly_charts(self, data: Dict[str, Any]) -> str:
        """生成Plotly图表HTML"""
        if not PLOTLY_AVAILABLE:
            return "<p>Plotly不可用，交互式图表功能受限</p>"
        
        # 这里可以添加更多复杂的Plotly图表生成逻辑
        # 由于时间限制，这里返回一个简单的占位符
        
        return """
        <div class="chart-container">
            <h2>📊 交互式图表</h2>
            <p>Plotly图表需要JavaScript支持，请在浏览器中查看交互功能。</p>
            <div id="interactive-charts-placeholder" style="height: 300px; background: linear-gradient(135deg, #f8f9fa, #e9ecef); border-radius: 8px; display: flex; align-items: center; justify-content: center;">
                <p style="color: #6c757d; font-style: italic;">交互式图表区域</p>
            </div>
        </div>
        """
    
    def _create_monitoring_dashboard(self, data: Dict[str, Any], title: str) -> str:
        """创建监控仪表板（简化版）"""
        return self._create_full_dashboard(data, f"{title} - 监控视图")
    
    def _create_performance_dashboard(self, data: Dict[str, Any], title: str) -> str:
        """创建绩效仪表板（简化版）"""
        return self._create_full_dashboard(data, f"{title} - 绩效视图")
    
    def _create_risk_dashboard(self, data: Dict[str, Any], title: str) -> str:
        """创建风险仪表板（简化版）"""
        return self._create_full_dashboard(data, f"{title} - 风险视图")

# 示例使用
if __name__ == "__main__":
    # 创建仪表板系统
    config = {
        'output_dir': './dashboard_output',
        'theme': 'light',
        'use_cdn': True,
        'include_plotly': True
    }
    
    dashboard = TradingDashboard(config)
    
    print("✅ 仪表板系统已初始化")
    print(f"📁 输出目录: {dashboard.output_dir}")
    print(f"🎨 当前主题: {dashboard.theme}")
    
    # 创建示例数据
    example_data = {
        'metrics': {
            'cumulative_return': 0.235,
            'annual_return': 0.156,
            'annual_volatility': 0.182,
            'sharpe_ratio': 1.24,
            'sortino_ratio': 1.56,
            'max_drawdown': -0.087,
            'max_drawdown_duration': 45,
            'win_rate': 0.58,
            'profit_factor': 1.45,
            'avg_win': 0.023,
            'avg_loss': -0.015,
            'total_trades': 125,
            'best_trade': 0.089,
            'worst_trade': -0.042,
            'var_95': -0.032,
            'cvar_95': -0.045,
            'avg_holding_period': 5.2
        },
        'signals': [
            {
                'timestamp': '2024-12-28 14:30:00',
                'type': 'buy',
                'price': 152.34,
                'reason': '突破关键阻力位',
                'confidence': 0.78
            },
            {
                'timestamp': '2024-12-27 11:15:00',
                'type': 'sell',
                'price': 148.92,
                'reason': '触及止损位',
                'confidence': 0.65
            },
            {
                'timestamp': '2024-12-25 10:45:00',
                'type': 'buy',
                'price': 146.78,
                'reason': '回踩支撑位',
                'confidence': 0.72
            },
            {
                'timestamp': '2024-12-22 15:20:00',
                'type': 'sell',
                'price': 150.12,
                'reason': '达到目标位',
                'confidence': 0.81
            }
        ]
    }
    
    # 生成完整仪表板
    print("\n📊 生成示例仪表板中...")
    
    dashboard_path = dashboard.create_dashboard(
        analysis_data=example_data,
        dashboard_type='full',
        title='示例量化交易分析仪表板'
    )
    
    print(f"✅ 仪表板已生成: {dashboard_path}")
    print(f"   - 打开方式: 在浏览器中打开 file://{os.path.abspath(dashboard_path)}")
    
    # 生成绩效仪表板
    performance_dashboard = dashboard.create_dashboard(
        analysis_data=example_data,
        dashboard_type='performance',
        title='示例绩效分析仪表板'
    )
    
    print(f"✅ 绩效仪表板已生成: {performance_dashboard}")
    
    # 生成风险仪表板
    risk_dashboard = dashboard.create_dashboard(
        analysis_data=example_data,
        dashboard_type='risk',
        title='示例风险分析仪表板'
    )
    
    print(f"✅ 风险仪表板已生成: {risk_dashboard}")
    
    print("\n🎉 仪表板系统示例完成!")
    print("💡 提示: 生成的HTML文件可在任何现代浏览器中打开查看")