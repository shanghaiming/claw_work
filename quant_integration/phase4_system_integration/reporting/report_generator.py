#!/usr/bin/env python3
"""
统一报告生成系统 - 量化交易分析报告生成工具

功能:
1. 文本报告生成 (Markdown, HTML, PDF)
2. 数据摘要统计
3. 信号摘要报告
4. 绩效分析报告
5. 风险分析报告
6. 策略对比报告

设计原则:
- 模块化: 独立报告模块，易于组合
- 可定制: 模板系统，支持自定义报告格式
- 多格式: 支持Markdown、HTML、JSON等多种格式
- 生产就绪: 错误处理，日志记录，性能优化
"""

import os
import json
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Union, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import warnings

class ReportFormat(Enum):
    """报告格式枚举"""
    MARKDOWN = "markdown"
    HTML = "html"
    JSON = "json"
    TEXT = "text"

class ReportType(Enum):
    """报告类型枚举"""
    SUMMARY = "summary"           # 摘要报告
    PERFORMANCE = "performance"   # 绩效报告
    RISK = "risk"                 # 风险报告
    SIGNAL = "signal"             # 信号报告
    STRATEGY_COMPARISON = "strategy_comparison"  # 策略对比报告
    FULL = "full"                 # 完整报告

@dataclass
class ReportMetrics:
    """报告指标数据类"""
    # 基本指标
    start_date: str
    end_date: str
    total_days: int
    total_trades: int
    
    # 绩效指标
    cumulative_return: float
    annual_return: float
    annual_volatility: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown: float
    max_drawdown_duration: int
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    
    # 风险指标
    var_95: float
    cvar_95: float
    beta: Optional[float] = None
    alpha: Optional[float] = None
    tracking_error: Optional[float] = None
    
    # 交易统计
    avg_holding_period: float = 0.0
    avg_trade_return: float = 0.0
    best_trade: float = 0.0
    worst_trade: float = 0.0
    
    # 自定义指标
    custom_metrics: Optional[Dict[str, Any]] = None

class ReportGenerator:
    """统一报告生成系统"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        初始化报告生成系统
        
        Args:
            config: 配置字典，包含:
                - output_dir: 输出目录 (默认: './reports')
                - default_format: 默认报告格式 (默认: ReportFormat.MARKDOWN)
                - template_dir: 模板目录 (可选)
                - enable_caching: 启用缓存 (默认: True)
                - language: 报告语言 (默认: 'zh-CN')
        """
        self.config = config or {}
        self.output_dir = self.config.get('output_dir', './reports')
        self.default_format = ReportFormat(self.config.get('default_format', 'markdown'))
        self.template_dir = self.config.get('template_dir')
        self.enable_caching = self.config.get('enable_caching', True)
        self.language = self.config.get('language', 'zh-CN')
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
        
        # 初始化缓存
        self._cache = {}
    
    def generate_report(self,
                       report_type: Union[str, ReportType],
                       data: Dict[str, Any],
                       format: Optional[Union[str, ReportFormat]] = None,
                       output_path: Optional[str] = None,
                       title: Optional[str] = None) -> str:
        """
        生成报告
        
        Args:
            report_type: 报告类型
            data: 报告数据
            format: 报告格式 (如为None则使用默认格式)
            output_path: 输出路径 (如为None则自动生成)
            title: 报告标题
            
        Returns:
            生成的报告文件路径
        """
        # 参数处理
        if isinstance(report_type, str):
            report_type = ReportType(report_type.lower())
        
        if isinstance(format, str):
            format = ReportFormat(format.lower())
        elif format is None:
            format = self.default_format
        
        # 生成报告内容
        if format == ReportFormat.MARKDOWN:
            content = self._generate_markdown_report(report_type, data, title)
            file_ext = '.md'
        elif format == ReportFormat.HTML:
            content = self._generate_html_report(report_type, data, title)
            file_ext = '.html'
        elif format == ReportFormat.JSON:
            content = self._generate_json_report(report_type, data, title)
            file_ext = '.json'
        elif format == ReportFormat.TEXT:
            content = self._generate_text_report(report_type, data, title)
            file_ext = '.txt'
        else:
            raise ValueError(f"不支持的报告格式: {format}")
        
        # 确定输出路径
        if output_path:
            # 确保文件扩展名正确
            if not output_path.endswith(file_ext):
                output_path += file_ext
            full_path = output_path
        else:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_name = report_type.value
            if title:
                report_name = f"{title.replace(' ', '_').lower()}_{report_name}"
            full_path = os.path.join(self.output_dir, f'{report_name}_{timestamp}{file_ext}')
        
        # 保存报告
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return full_path
    
    def _generate_markdown_report(self,
                                 report_type: ReportType,
                                 data: Dict[str, Any],
                                 title: Optional[str] = None) -> str:
        """生成Markdown格式报告"""
        
        # 根据报告类型选择生成函数
        if report_type == ReportType.SUMMARY:
            return self._generate_markdown_summary(data, title)
        elif report_type == ReportType.PERFORMANCE:
            return self._generate_markdown_performance(data, title)
        elif report_type == ReportType.RISK:
            return self._generate_markdown_risk(data, title)
        elif report_type == ReportType.SIGNAL:
            return self._generate_markdown_signal(data, title)
        elif report_type == ReportType.STRATEGY_COMPARISON:
            return self._generate_markdown_strategy_comparison(data, title)
        elif report_type == ReportType.FULL:
            return self._generate_markdown_full(data, title)
        else:
            raise ValueError(f"不支持的报告类型: {report_type}")
    
    def _generate_markdown_summary(self,
                                  data: Dict[str, Any],
                                  title: Optional[str] = None) -> str:
        """生成Markdown摘要报告"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_title = title or "量化交易分析摘要报告"
        
        # 提取数据
        metrics = data.get('metrics', {})
        summary_stats = data.get('summary_stats', {})
        signals = data.get('signals', [])
        
        # 计算信号统计
        buy_signals = [s for s in signals if s.get('type') == 'buy']
        sell_signals = [s for s in signals if s.get('type') == 'sell']
        
        # 生成报告内容
        content = f"""# {report_title}

**生成时间**: {timestamp}  
**报告类型**: 交易分析摘要  
**数据范围**: {summary_stats.get('start_date', '未知')} - {summary_stats.get('end_date', '未知')}

---

## 📊 关键指标概览

| 指标 | 数值 | 评价 |
|------|------|------|
| **累计收益率** | {metrics.get('cumulative_return', 0):.2%} | {"✅ 优秀" if metrics.get('cumulative_return', 0) > 0.1 else "⚠️ 一般" if metrics.get('cumulative_return', 0) > 0 else "❌ 亏损"} |
| **年化收益率** | {metrics.get('annual_return', 0):.2%} | {"✅ 优秀" if metrics.get('annual_return', 0) > 0.15 else "⚠️ 一般" if metrics.get('annual_return', 0) > 0 else "❌ 亏损"} |
| **夏普比率** | {metrics.get('sharpe_ratio', 0):.2f} | {"✅ 优秀" if metrics.get('sharpe_ratio', 0) > 1.0 else "⚠️ 一般" if metrics.get('sharpe_ratio', 0) > 0 else "❌ 不佳"} |
| **最大回撤** | {metrics.get('max_drawdown', 0):.2%} | {"✅ 优秀" if abs(metrics.get('max_drawdown', 0)) < 0.1 else "⚠️ 一般" if abs(metrics.get('max_drawdown', 0)) < 0.2 else "❌ 高风险"} |
| **胜率** | {metrics.get('win_rate', 0):.2%} | {"✅ 优秀" if metrics.get('win_rate', 0) > 0.5 else "⚠️ 一般" if metrics.get('win_rate', 0) > 0.4 else "❌ 不佳"} |

---

## 📈 绩效摘要

### 收益分析
- **累计收益率**: {metrics.get('cumulative_return', 0):.2%}
- **年化收益率**: {metrics.get('annual_return', 0):.2%}
- **年化波动率**: {metrics.get('annual_volatility', 0):.2%}
- **盈亏比**: {metrics.get('profit_factor', 0):.2f}

### 交易统计
- **总交易次数**: {metrics.get('total_trades', 0)}
- **胜率**: {metrics.get('win_rate', 0):.2%}
- **平均盈利**: {metrics.get('avg_win', 0):.2%}
- **平均亏损**: {metrics.get('avg_loss', 0):.2%}
- **最佳交易**: {metrics.get('best_trade', 0):.2%}
- **最差交易**: {metrics.get('worst_trade', 0):.2%}

### 风险调整收益
- **夏普比率**: {metrics.get('sharpe_ratio', 0):.2f}
- **索提诺比率**: {metrics.get('sortino_ratio', 0):.2f}
- **卡玛比率**: {metrics.get('calmar_ratio', 0) if 'calmar_ratio' in metrics else 'N/A':.2f}

---

## 📡 信号摘要

### 信号统计
- **总信号数**: {len(signals)}
- **买入信号**: {len(buy_signals)} 个
- **卖出信号**: {len(sell_signals)} 个
- **信号频率**: {len(signals) / max(1, summary_stats.get('total_days', 1)):.2f} 信号/天

### 最近信号 (最近5个)
"""
        
        # 添加最近信号
        recent_signals = sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)[:5]
        for i, signal in enumerate(recent_signals):
            signal_type = signal.get('type', 'unknown')
            signal_time = signal.get('timestamp', '')
            signal_price = signal.get('price', 0)
            signal_reason = signal.get('reason', '')
            signal_confidence = signal.get('confidence', 0)
            
            content += f"- **{signal_type.upper()}** ({signal_time}): 价格 {signal_price:.2f}, 原因: {signal_reason}, 置信度: {signal_confidence:.2%}\n"
        
        content += """
---

## ⚠️ 风险提示

### 主要风险指标
- **最大回撤**: {:.2%} (持续时间: {} 天)
- **VaR (95%)**: {:.2%}
- **CVaR (95%)**: {:.2%}
- **波动率**: {:.2%}
""".format(
    metrics.get('max_drawdown', 0),
    metrics.get('max_drawdown_duration', 0),
    metrics.get('var_95', 0),
    metrics.get('cvar_95', 0),
    metrics.get('annual_volatility', 0)
)

        content += """
### 风险评估
"""
        
        # 风险评估逻辑
        max_dd = abs(metrics.get('max_drawdown', 0))
        sharpe = metrics.get('sharpe_ratio', 0)
        win_rate = metrics.get('win_rate', 0)
        
        risk_assessment = []
        
        if max_dd > 0.2:
            risk_assessment.append("- **回撤风险**: 高风险 (最大回撤 > 20%)")
        elif max_dd > 0.1:
            risk_assessment.append("- **回撤风险**: 中风险 (最大回撤 10%-20%)")
        else:
            risk_assessment.append("- **回撤风险**: 低风险 (最大回撤 < 10%)")
        
        if sharpe < 0:
            risk_assessment.append("- **收益风险比**: 不佳 (夏普比率 < 0)")
        elif sharpe < 0.5:
            risk_assessment.append("- **收益风险比**: 一般 (夏普比率 0-0.5)")
        elif sharpe < 1.0:
            risk_assessment.append("- **收益风险比**: 良好 (夏普比率 0.5-1.0)")
        else:
            risk_assessment.append("- **收益风险比**: 优秀 (夏普比率 > 1.0)")
        
        if win_rate < 0.4:
            risk_assessment.append("- **胜率风险**: 高风险 (胜率 < 40%)")
        elif win_rate < 0.5:
            risk_assessment.append("- **胜率风险**: 中风险 (胜率 40%-50%)")
        else:
            risk_assessment.append("- **胜率风险**: 低风险 (胜率 > 50%)")
        
        content += "\n".join(risk_assessment) + "\n"

        content += """
---

## 💡 建议与改进

### 短期建议 (1-4周)
1. **监控关键水平**: 关注主要支撑/阻力位，调整交易计划
2. **风险管理**: 根据当前波动率调整仓位规模
3. **信号验证**: 对低置信度信号进行额外验证

### 中期建议 (1-3个月)
1. **策略优化**: 基于历史表现优化策略参数
2. **多样化**: 考虑引入相关性较低的策略或资产
3. **自动化**: 完善信号执行和风险控制自动化

### 长期建议 (3-6个月)
1. **系统升级**: 升级分析框架，引入机器学习模型
2. **市场拓展**: 扩展到其他相关市场或品种
3. **绩效归因**: 建立详细的绩效归因分析系统

---

## 📝 免责声明

1. **历史表现不代表未来**: 过去的表现不能保证未来的结果
2. **风险自担**: 所有投资决策需自行承担风险
3. **专业建议**: 本报告不构成专业投资建议，仅供分析参考
4. **数据准确性**: 报告基于提供的数据生成，不对数据准确性负责
5. **系统风险**: 量化交易系统存在技术故障和模型风险

---

**报告生成系统**: OpenClaw量化交易分析框架  
**版本**: 1.0.0  
**生成时间**: {}  

> 注意: 本报告为自动生成，如有疑问请咨询专业顾问。
""".format(timestamp)

        return content
    
    def _generate_markdown_performance(self,
                                      data: Dict[str, Any],
                                      title: Optional[str] = None) -> str:
        """生成Markdown绩效报告"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_title = title or "量化交易绩效分析报告"
        
        # 提取数据
        metrics = data.get('metrics', {})
        returns_data = data.get('returns', {})
        trades = data.get('trades', [])
        
        # 计算额外指标
        if 'returns_series' in returns_data:
            returns_series = returns_data['returns_series']
            if isinstance(returns_series, (pd.Series, list)):
                returns_array = np.array(returns_series)
                positive_returns = returns_array[returns_array > 0]
                negative_returns = returns_array[returns_array < 0]
                
                if len(positive_returns) > 0:
                    avg_positive_return = np.mean(positive_returns)
                else:
                    avg_positive_return = 0
                    
                if len(negative_returns) > 0:
                    avg_negative_return = np.mean(negative_returns)
                else:
                    avg_negative_return = 0
                
                # 计算偏度和峰度
                if len(returns_array) > 0:
                    skewness = pd.Series(returns_array).skew()
                    kurtosis = pd.Series(returns_array).kurtosis()
                else:
                    skewness = 0
                    kurtosis = 0
            else:
                avg_positive_return = 0
                avg_negative_return = 0
                skewness = 0
                kurtosis = 0
        else:
            avg_positive_return = metrics.get('avg_win', 0)
            avg_negative_return = metrics.get('avg_loss', 0)
            skewness = 0
            kurtosis = 0
        
        # 计算月度收益率
        monthly_returns = {}
        if 'returns_series' in returns_data and isinstance(returns_data['returns_series'], pd.Series):
            returns_series = returns_data['returns_series']
            monthly_returns_series = returns_series.resample('M').apply(lambda x: (1 + x).prod() - 1)
            monthly_returns = monthly_returns_series.to_dict()
        
        content = f"""# {report_title}

**生成时间**: {timestamp}  
**报告类型**: 绩效分析报告

---

## 📊 绩效指标总览

### 收益指标
| 指标 | 数值 | 行业对比 |
|------|------|----------|
| **累计收益率** | {metrics.get('cumulative_return', 0):.2%} | {"高于平均" if metrics.get('cumulative_return', 0) > 0.08 else "低于平均"} |
| **年化收益率** | {metrics.get('annual_return', 0):.2%} | {"优秀 (>15%)" if metrics.get('annual_return', 0) > 0.15 else "良好 (8-15%)" if metrics.get('annual_return', 0) > 0.08 else "一般 (<8%)"} |
| **年化波动率** | {metrics.get('annual_volatility', 0):.2%} | {"低波动" if metrics.get('annual_volatility', 0) < 0.15 else "中波动" if metrics.get('annual_volatility', 0) < 0.25 else "高波动"} |

### 风险调整收益
| 指标 | 数值 | 评价 |
|------|------|------|
| **夏普比率** | {metrics.get('sharpe_ratio', 0):.2f} | {"优秀 (>1.0)" if metrics.get('sharpe_ratio', 0) > 1.0 else "良好 (0.5-1.0)" if metrics.get('sharpe_ratio', 0) > 0.5 else "一般 (<0.5)"} |
| **索提诺比率** | {metrics.get('sortino_ratio', 0):.2f} | {"优秀 (>1.5)" if metrics.get('sortino_ratio', 0) > 1.5 else "良好 (1.0-1.5)" if metrics.get('sortino_ratio', 0) > 1.0 else "一般 (<1.0)"} |
| **卡玛比率** | {metrics.get('calmar_ratio', 0) if 'calmar_ratio' in metrics else 'N/A':.2f} | - |

### 交易统计
| 指标 | 数值 | 说明 |
|------|------|------|
| **总交易次数** | {metrics.get('total_trades', 0)} | 统计期间内所有交易 |
| **胜率** | {metrics.get('win_rate', 0):.2%} | 盈利交易占比 |
| **盈亏比** | {metrics.get('profit_factor', 0):.2f} | 总盈利/总亏损 |
| **平均盈利** | {avg_positive_return:.2%} | 盈利交易平均收益率 |
| **平均亏损** | {avg_negative_return:.2%} | 亏损交易平均收益率 |

---

## 📈 收益分析

### 收益分布特征
- **收益偏度**: {skewness:.3f} {"(右偏，大收益较多)" if skewness > 0.1 else "(左偏，大亏损较多)" if skewness < -0.1 else "(近似对称)"}
- **收益峰度**: {kurtosis:.3f} {"(尖峰厚尾，极端值较多)" if kurtosis > 3 else "(平峰薄尾，极端值较少)" if kurtosis < 3 else "(正态分布)"}
- **收益稳定性**: {"稳定" if metrics.get('annual_volatility', 0) < 0.2 else "中等" if metrics.get('annual_volatility', 0) < 0.3 else "波动较大"}

### 月度收益分析
"""
        
        # 添加月度收益表格
        if monthly_returns:
            content += "| 月份 | 收益率 | 评价 |\n|------|--------|------|\n"
            
            for month, return_value in list(monthly_returns.items())[-12:]:  # 最近12个月
                month_str = month.strftime('%Y-%m')
                return_pct = return_value * 100
                
                if return_pct > 5:
                    evaluation = "✅ 优秀"
                elif return_pct > 0:
                    evaluation = "📈 良好"
                elif return_pct > -5:
                    evaluation = "⚠️ 一般"
                else:
                    evaluation = "❌ 较差"
                
                content += f"| {month_str} | {return_value:.2%} | {evaluation} |\n"
        else:
            content += "*月度收益数据不可用*\n"
        
        content += """
### 收益持续性
"""
        
        # 分析收益持续性
        if 'returns_series' in returns_data and isinstance(returns_data['returns_series'], pd.Series):
            returns_series = returns_data['returns_series']
            
            # 计算连续盈利/亏损
            positive_streaks = []
            negative_streaks = []
            current_streak = 0
            current_sign = 0
            
            for r in returns_series:
                if r > 0:
                    if current_sign == 1:
                        current_streak += 1
                    else:
                        if current_sign == -1 and current_streak > 0:
                            negative_streaks.append(current_streak)
                        current_streak = 1
                        current_sign = 1
                elif r < 0:
                    if current_sign == -1:
                        current_streak += 1
                    else:
                        if current_sign == 1 and current_streak > 0:
                            positive_streaks.append(current_streak)
                        current_streak = 1
                        current_sign = -1
            
            if positive_streaks:
                avg_positive_streak = np.mean(positive_streaks)
                max_positive_streak = np.max(positive_streaks)
            else:
                avg_positive_streak = 0
                max_positive_streak = 0
                
            if negative_streaks:
                avg_negative_streak = np.mean(negative_streaks)
                max_negative_streak = np.max(negative_streaks)
            else:
                avg_negative_streak = 0
                max_negative_streak = 0
            
            content += f"""
- **平均连续盈利天数**: {avg_positive_streak:.1f} 天
- **最长连续盈利**: {max_positive_streak} 天
- **平均连续亏损天数**: {avg_negative_streak:.1f} 天  
- **最长连续亏损**: {max_negative_streak} 天
"""
        else:
            content += "*收益持续性分析数据不可用*\n"
        
        content += """
---

## 📉 回撤分析

### 回撤指标
| 指标 | 数值 | 说明 |
|------|------|------|
| **最大回撤** | {:.2%} | 从峰值到谷值的最大跌幅 |
| **回撤持续时间** | {} 天 | 最长回撤持续时间 |
| **平均回撤** | {:.2%} | 所有回撤的平均值 |
| **回撤恢复时间** | {} 天 | 平均恢复时间 |
""".format(
    metrics.get('max_drawdown', 0),
    metrics.get('max_drawdown_duration', 0),
    metrics.get('avg_drawdown', 0) if 'avg_drawdown' in metrics else 'N/A',
    metrics.get('recovery_time', 0) if 'recovery_time' in metrics else 'N/A'
)

        content += """
### 回撤深度分布
"""
        
        # 回撤深度分析
        if 'drawdown_series' in data:
            drawdown_series = data['drawdown_series']
            if isinstance(drawdown_series, (pd.Series, list)):
                drawdown_array = np.array(drawdown_series)
                
                # 计算回撤深度分布
                shallow_dd = np.sum(drawdown_array > -0.05)  # 浅度回撤 (<5%)
                moderate_dd = np.sum((drawdown_array <= -0.05) & (drawdown_array > -0.1))  # 中度回撤 (5-10%)
                deep_dd = np.sum((drawdown_array <= -0.1) & (drawdown_array > -0.2))  # 深度回撤 (10-20%)
                severe_dd = np.sum(drawdown_array <= -0.2)  # 严重回撤 (>20%)
                
                total_dd = len(drawdown_array)
                
                if total_dd > 0:
                    content += f"""
- **浅度回撤 (<5%)**: {shallow_dd} 次 ({shallow_dd/total_dd:.1%})
- **中度回撤 (5-10%)**: {moderate_dd} 次 ({moderate_dd/total_dd:.1%})
- **深度回撤 (10-20%)**: {deep_dd} 次 ({deep_dd/total_dd:.1%})
- **严重回撤 (>20%)**: {severe_dd} 次 ({severe_dd/total_dd:.1%})
"""
                else:
                    content += "*回撤分布数据不可用*\n"
            else:
                content += "*回撤分布数据不可用*\n"
        else:
            content += "*回撤分布数据不可用*\n"
        
        content += """
---

## 📋 交易分析

### 交易质量评估
"""
        
        # 交易质量评估
        win_rate = metrics.get('win_rate', 0)
        profit_factor = metrics.get('profit_factor', 0)
        avg_win_avg_loss_ratio = abs(avg_positive_return / avg_negative_return) if avg_negative_return != 0 else 0
        
        quality_assessment = []
        
        if win_rate > 0.6:
            quality_assessment.append("✅ **胜率高**: 超过60%的交易盈利，表现优秀")
        elif win_rate > 0.5:
            quality_assessment.append("📈 **胜率良好**: 50%-60%的交易盈利，表现良好")
        elif win_rate > 0.4:
            quality_assessment.append("⚠️ **胜率一般**: 40%-50%的交易盈利，需要改进")
        else:
            quality_assessment.append("❌ **胜率低**: 低于40%的交易盈利，需要重大改进")
        
        if profit_factor > 2.0:
            quality_assessment.append("✅ **盈亏比优秀**: 盈利是亏损的2倍以上，风险控制好")
        elif profit_factor > 1.5:
            quality_assessment.append("📈 **盈亏比良好**: 盈利是亏损的1.5-2倍，风险控制良好")
        elif profit_factor > 1.0:
            quality_assessment.append("⚠️ **盈亏比一般**: 盈利略高于亏损，需要优化")
        else:
            quality_assessment.append("❌ **盈亏比差**: 亏损大于盈利，需要重大改进")
        
        if avg_win_avg_loss_ratio > 2.0:
            quality_assessment.append("✅ **平均盈亏比优秀**: 平均盈利是平均亏损的2倍以上")
        elif avg_win_avg_loss_ratio > 1.5:
            quality_assessment.append("📈 **平均盈亏比良好**: 平均盈利是平均亏损的1.5-2倍")
        elif avg_win_avg_loss_ratio > 1.0:
            quality_assessment.append("⚠️ **平均盈亏比一般**: 平均盈利略高于平均亏损")
        else:
            quality_assessment.append("❌ **平均盈亏比差**: 平均亏损大于平均盈利")
        
        content += "\n".join(quality_assessment) + "\n"
        
        # 添加交易列表（最近10笔）
        if trades and len(trades) > 0:
            content += """
### 最近交易记录 (最近10笔)
| 日期 | 类型 | 价格 | 收益率 | 持有天数 | 状态 |
|------|------|------|--------|----------|------|
"""
            
            recent_trades = sorted(trades, key=lambda x: x.get('entry_date', ''), reverse=True)[:10]
            for trade in recent_trades:
                entry_date = trade.get('entry_date', '')
                trade_type = trade.get('type', '')
                entry_price = trade.get('entry_price', 0)
                exit_price = trade.get('exit_price', 0)
                pnl = trade.get('pnl', 0)
                pnl_pct = trade.get('pnl_pct', 0)
                holding_days = trade.get('holding_days', 0)
                status = trade.get('status', '')
                
                # 确定状态符号
                if status == 'closed':
                    if pnl > 0:
                        status_symbol = "✅ 盈利"
                    elif pnl < 0:
                        status_symbol = "❌ 亏损"
                    else:
                        status_symbol = "➖ 平局"
                elif status == 'open':
                    status_symbol = "⏳ 持仓中"
                else:
                    status_symbol = status
                
                content += f"| {entry_date} | {trade_type} | {entry_price:.2f} | {pnl_pct:.2%} | {holding_days} | {status_symbol} |\n"
        
        content += """
---

## 🎯 绩效评级与改进建议

### 综合绩效评级
"""
        
        # 综合评级逻辑
        sharpe = metrics.get('sharpe_ratio', 0)
        max_dd = abs(metrics.get('max_drawdown', 0))
        annual_return = metrics.get('annual_return', 0)
        win_rate = metrics.get('win_rate', 0)
        
        score = 0
        score += 3 if sharpe > 1.0 else 2 if sharpe > 0.5 else 1
        score += 3 if max_dd < 0.1 else 2 if max_dd < 0.15 else 1
        score += 3 if annual_return > 0.15 else 2 if annual_return > 0.08 else 1
        score += 3 if win_rate > 0.55 else 2 if win_rate > 0.45 else 1
        
        if score >= 11:
            rating = "★★★★★ 优秀"
            rating_desc = "策略表现优秀，各项指标均衡，风险控制良好"
        elif score >= 9:
            rating = "★★★★ 良好"
            rating_desc = "策略表现良好，有改进空间但整体稳健"
        elif score >= 7:
            rating = "★★★ 一般"
            rating_desc = "策略表现一般，需要优化某些方面"
        elif score >= 5:
            rating = "★★ 有待改进"
            rating_desc = "策略需要重大改进，存在明显缺陷"
        else:
            rating = "★ 不达标"
            rating_desc = "策略表现不达标，建议重新设计"
        
        content += f"""
- **综合评级**: {rating}
- **评级说明**: {rating_desc}
- **评分详情**: 
  - 夏普比率: {"优秀 (3分)" if sharpe > 1.0 else "良好 (2分)" if sharpe > 0.5 else "一般 (1分)"}
  - 最大回撤: {"优秀 (3分)" if max_dd < 0.1 else "良好 (2分)" if max_dd < 0.15 else "一般 (1分)"}
  - 年化收益: {"优秀 (3分)" if annual_return > 0.15 else "良好 (2分)" if annual_return > 0.08 else "一般 (1分)"}
  - 胜率: {"优秀 (3分)" if win_rate > 0.55 else "良好 (2分)" if win_rate > 0.45 else "一般 (1分)"}
- **总分**: {score}/12

### 改进优先级
"""
        
        # 改进建议
        improvements = []
        
        if sharpe < 0.5:
            improvements.append("1. **提高夏普比率**: 优化风险调整收益，降低波动性或提高收益")
        if max_dd > 0.15:
            improvements.append("2. **控制回撤**: 加强风险管理，设置更严格的止损")
        if win_rate < 0.45:
            improvements.append("3. **提高胜率**: 优化入场时机，增加信号过滤条件")
        if profit_factor < 1.2:
            improvements.append("4. **提高盈亏比**: 优化出场策略，让盈利奔跑，及时止损")
        if avg_win_avg_loss_ratio < 1.5:
            improvements.append("5. **优化平均盈亏比**: 提高平均盈利，降低平均亏损")
        
        if not improvements:
            improvements.append("1. **保持策略稳定性**: 当前策略表现良好，建议保持参数稳定")
            improvements.append("2. **适度多样化**: 考虑加入低相关性的辅助策略")
            improvements.append("3. **监控市场变化**: 关注市场结构变化，及时调整策略")
        
        content += "\n".join(improvements) + "\n"

        content += """
---

## 📝 报告说明

1. **数据来源**: 本报告基于提供的交易数据和市场数据生成
2. **计算方法**: 绩效指标采用行业标准计算方法
3. **假设条件**: 假设交易成本为{}，滑点为{}
4. **时间范围**: 报告覆盖{}至{}的数据
5. **更新频率**: 建议每月更新一次绩效报告

---

**报告生成时间**: {}
**生成系统**: OpenClaw量化交易分析框架
**报告版本**: 1.0.0

> 注意: 本报告仅供参考，不构成投资建议。过去表现不代表未来结果。
""".format(
    data.get('transaction_cost', '0.03%'),
    data.get('slippage', '0.01%'),
    data.get('start_date', '未知'),
    data.get('end_date', '未知'),
    timestamp
)

        return content
    
    def _generate_markdown_risk(self,
                               data: Dict[str, Any],
                               title: Optional[str] = None) -> str:
        """生成Markdown风险报告"""
        
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        report_title = title or "量化交易风险分析报告"
        
        # 提取数据
        risk_metrics = data.get('risk_metrics', {})
        var_data = data.get('var_analysis', {})
        stress_tests = data.get('stress_tests', {})
        correlation_matrix = data.get('correlation_matrix', {})
        
        content = f"""# {report_title}

**生成时间**: {timestamp}  
**报告类型**: 风险分析报告

---

## ⚠️ 风险指标总览

### 市场风险
| 指标 | 数值 | 风险等级 |
|------|------|----------|
| **波动率 (年化)** | {risk_metrics.get('volatility', 0):.2%} | {"低风险" if risk_metrics.get('volatility', 0) < 0.15 else "中风险" if risk_metrics.get('volatility', 0) < 0.25 else "高风险"} |
| **Beta系数** | {risk_metrics.get('beta', 1.0):.2f} | {"低系统风险" if abs(risk_metrics.get('beta', 1.0) - 1.0) < 0.2 else "中系统风险" if abs(risk_metrics.get('beta', 1.0) - 1.0) < 0.5 else "高系统风险"} |
| **跟踪误差** | {risk_metrics.get('tracking_error', 0):.2%} | {"低" if risk_metrics.get('tracking_error', 0) < 0.05 else "中" if risk_metrics.get('tracking_error', 0) < 0.1 else "高"} |

### 下行风险
| 指标 | 数值 | 说明 |
|------|------|------|
| **最大回撤** | {risk_metrics.get('max_drawdown', 0):.2%} | 历史最大亏损幅度 |
| **VaR (95%)** | {risk_metrics.get('var_95', 0):.2%} | 95%置信度下的最大日亏损 |
| **CVaR (95%)** | {risk_metrics.get('cvar_95', 0):.2%} | 超过VaR的平均亏损 |
| **下行波动率** | {risk_metrics.get('downside_volatility', 0):.2%} | 负收益的波动率 |

### 流动性风险
| 指标 | 数值 | 评估 |
|------|------|------|
| **平均成交量** | {risk_metrics.get('avg_volume', 0):.0f} | {"高流动性" if risk_metrics.get('avg_volume', 0) > 1000000 else "中等流动性" if risk_metrics.get('avg_volume', 0) > 100000 else "低流动性"} |
| **成交量波动率** | {risk_metrics.get('volume_volatility', 0):.2%} | {"稳定" if risk_metrics.get('volume_volatility', 0) < 0.3 else "波动较大"} |
| **买卖价差** | {risk_metrics.get('bid_ask_spread', 0):.2%} | {"窄" if risk_metrics.get('bid_ask_spread', 0) < 0.001 else "中等" if risk_metrics.get('bid_ask_spread', 0) < 0.005 else "宽"} |

---

## 📉 风险价值 (VaR) 分析

### VaR计算结果
"""
        
        if var_data:
            for confidence_level, var_value in var_data.items():
                if isinstance(var_value, dict):
                    var_val = var_value.get('value', 0)
                    var_method = var_value.get('method', '未知')
                else:
                    var_val = var_value
                    var_method = '历史模拟法'
                
                content += f"- **{confidence_level} VaR**: {var_val:.2%} (方法: {var_method})\n"
        else:
            content += "*VaR分析数据不可用*\n"
        
        content += """
### CVaR (条件风险价值)
"""
        
        if 'cvar_analysis' in data:
            cvar_data = data['cvar_analysis']
            for confidence_level, cvar_value in cvar_data.items():
                content += f"- **{confidence_level} CVaR**: {cvar_value:.2%}\n"
        else:
            content += "*CVaR分析数据不可用*\n"
        
        content += """
### VaR回测
"""
        
        if 'var_backtest' in data:
            var_backtest = data['var_backtest']
            violations = var_backtest.get('violations', 0)
            total_days = var_backtest.get('total_days', 0)
            violation_rate = violations / total_days if total_days > 0 else 0
            expected_rate = 0.05  # 对于95% VaR
            
            content += f"""
- **违反次数**: {violations} 次
- **总观察日**: {total_days} 天
- **违反率**: {violation_rate:.2%}
- **预期违反率**: {expected_rate:.2%}
- **检验结果**: {"✅ 通过" if abs(violation_rate - expected_rate) < 0.01 else "⚠️ 接近" if abs(violation_rate - expected_rate) < 0.02 else "❌ 未通过"}
"""
        else:
            content += "*VaR回测数据不可用*\n"
        
        content += """
---

## 🧪 压力测试

### 历史极端情景
"""
        
        if stress_tests:
            for scenario, result in stress_tests.items():
                if isinstance(result, dict):
                    loss = result.get('loss', 0)
                    recovery_days = result.get('recovery_days', 0)
                    content += f"- **{scenario}**: 亏损 {loss:.2%}, 恢复时间 {recovery_days} 天\n"
                else:
                    content += f"- **{scenario}**: 亏损 {result:.2%}\n"
        else:
            content += "*压力测试数据不可用*\n"
        
        content += """
### 假设极端情景
"""
        
        # 假设情景分析
        hypothetical_scenarios = {
            '市场崩盘 (-20%)': risk_metrics.get('max_drawdown', 0) * 1.5 if 'max_drawdown' in risk_metrics else 0,
            '流动性枯竭': risk_metrics.get('var_95', 0) * 2 if 'var_95' in risk_metrics else 0,
            '波动率飙升 (3倍)': risk_metrics.get('volatility', 0) * 3 if 'volatility' in risk_metrics else 0,
            '相关性突破': risk_metrics.get('cvar_95', 0) * 1.8 if 'cvar_95' in risk_metrics else 0
        }
        
        for scenario, estimated_loss in hypothetical_scenarios.items():
            content += f"- **{scenario}**: 预计亏损 {estimated_loss:.2%}\n"
        
        content += """
---

## 🔗 相关性分析

### 资产相关性矩阵
"""
        
        if correlation_matrix and isinstance(correlation_matrix, dict):
            # 简化的相关性描述
            high_corr = []
            low_corr = []
            negative_corr = []
            
            for asset1, correlations in correlation_matrix.items():
                if isinstance(correlations, dict):
                    for asset2, corr in correlations.items():
                        if asset1 != asset2:
                            if corr > 0.7:
                                high_corr.append(f"{asset1}-{asset2}")
                            elif corr < -0.3:
                                negative_corr.append(f"{asset1}-{asset2}")
                            elif corr < 0.3:
                                low_corr.append(f"{asset1}-{asset2}")
            
            content += f"""
- **高度相关 (>0.7)**: {len(high_corr)} 对资产
- **低度相关 (<0.3)**: {len(low_corr)} 对资产  
- **负相关 (<-0.3)**: {len(negative_corr)} 对资产
"""
            
            if high_corr:
                content += "\n**主要高度相关资产对**:\n"
                for pair in high_corr[:5]:  # 只显示前5个
                    content += f"  - {pair}\n"
        else:
            content += "*相关性矩阵数据不可用*\n"
        
        content += """
### 分散化效果评估
"""
        
        # 分散化评估
        if correlation_matrix:
            # 计算平均相关性
            all_correlations = []
            if isinstance(correlation_matrix, dict):
                for asset1, correlations in correlation_matrix.items():
                    if isinstance(correlations, dict):
                        for asset2, corr in correlations.items():
                            if asset1 != asset2:
                                all_correlations.append(corr)
            
            if all_correlations:
                avg_correlation = np.mean(all_correlations)
                
                if avg_correlation < 0.2:
                    diversification = "✅ 优秀"
                    diversification_desc = "资产间相关性低，分散化效果优秀"
                elif avg_correlation < 0.4:
                    diversification = "📈 良好"
                    diversification_desc = "资产间相关性中等，分散化效果良好"
                elif avg_correlation < 0.6:
                    diversification = "⚠️ 一般"
                    diversification_desc = "资产间相关性较高，分散化效果一般"
                else:
                    diversification = "❌ 较差"
                    diversification_desc = "资产间相关性高，分散化效果差"
                
                content += f"""
- **平均相关性**: {avg_correlation:.3f}
- **分散化效果**: {diversification}
- **评估说明**: {diversification_desc}
"""
            else:
                content += "*分散化评估数据不足*\n"
        else:
            content += "*分散化评估数据不可用*\n"
        
        content += """
---

## 🛡️ 风险管理建议

### 风险控制措施
"""
        
        # 风险控制建议
        volatility = risk_metrics.get('volatility', 0)
        max_dd = abs(risk_metrics.get('max_drawdown', 0))
        var_95 = abs(risk_metrics.get('var_95', 0))
        
        risk_controls = []
        
        if volatility > 0.25:
            risk_controls.append("1. **降低仓位**: 当前波动率较高，建议降低总体仓位至正常水平的70-80%")
        elif volatility > 0.15:
            risk_controls.append("1. **适度减仓**: 波动率中等偏高，建议适当降低仓位")
        else:
            risk_controls.append("1. **保持仓位**: 波动率在合理范围内，可保持当前仓位")
        
        if max_dd > 0.2:
            risk_controls.append("2. **严格止损**: 历史最大回撤超过20%，建议设置更严格的止损线（如5-8%）")
        elif max_dd > 0.15:
            risk_controls.append("2. **加强止损**: 回撤较大，建议加强止损管理（如8-10%）")
        else:
            risk_controls.append("2. **正常止损**: 回撤在可接受范围内，保持正常止损设置（如10-12%）")
        
        if var_95 > 0.05:
            risk_controls.append("3. **增加保证金**: VaR值较高，建议增加交易保证金，提高安全边际")
        else:
            risk_controls.append("3. **正常保证金**: VaR值在正常范围内，保持当前保证金水平")
        
        # 相关性建议
        if 'correlation_matrix' in data:
            risk_controls.append("4. **优化资产配置**: 根据相关性分析优化投资组合，降低集中风险")
        else:
            risk_controls.append("4. **分散投资**: 建议分散投资到相关性较低的资产或策略")
        
        # 压力测试建议
        if stress_tests:
            worst_scenario = max([v.get('loss', 0) if isinstance(v, dict) else v for v in stress_tests.values()], default=0)
            if worst_scenario > 0.3:
                risk_controls.append("5. **极端情况预案**: 历史极端情景亏损超过30%，需制定极端情况应对预案")
            elif worst_scenario > 0.2:
                risk_controls.append("5. **压力测试监控**: 关注压力测试结果，准备应对措施")
        
        content += "\n".join(risk_controls) + "\n"
        
        content += """
### 风险监控指标
建议每日/每周监控以下风险指标:
1. **日度VaR**: 监控每日风险价值是否超出阈值
2. **实时回撤**: 监控当前回撤与历史最大回撤的比较
3. **波动率变化**: 关注波动率的异常变化
4. **相关性变化**: 监控资产间相关性的结构性变化
5. **流动性指标**: 关注成交量、买卖价差等流动性指标

### 风险限额
基于当前分析，建议设置以下风险限额:
- **单日亏损限额**: {:.2%} (基于VaR分析)
- **单笔交易风险**: 不超过总资金的2%
- **行业集中度**: 不超过总资金的20%
- **总风险暴露**: 不超过总资金的150%
""".format(abs(risk_metrics.get('var_95', 0)) * 1.5 if 'var_95' in risk_metrics else 0.03)

        content += """
---

## 📋 风险报告总结

### 主要风险点
"""
        
        # 识别主要风险点
        risk_points = []
        
        if volatility > 0.25:
            risk_points.append("- **高波动风险**: 市场波动率较高，价格变动剧烈")
        if max_dd > 0.2:
            risk_points.append("- **大幅回撤风险**: 历史最大回撤超过20%，下行风险较大")
        if 'var_95' in risk_metrics and abs(risk_metrics['var_95']) > 0.05:
            risk_points.append("- **极端亏损风险**: VaR值较高，存在较大日亏损风险")
        if 'correlation_matrix' in data:
            risk_points.append("- **相关性风险**: 部分资产高度相关，分散化效果有限")
        if 'liquidity_risk' in data.get('additional_risks', {}):
            risk_points.append("- **流动性风险**: 在市场压力时期可能存在流动性问题")
        
        if not risk_points:
            risk_points.append("- **风险总体可控**: 各项风险指标在合理范围内")
            risk_points.append("- **分散化良好**: 投资组合分散化效果较好")
            risk_points.append("- **风险调整收益合理**: 风险与收益匹配度良好")
        
        content += "\n".join(risk_points) + "\n"
        
        content += """
### 总体风险评估
基于以上分析，总体风险评估如下:
"""
        
        # 总体风险评估
        risk_score = 0
        risk_score += 3 if volatility > 0.25 else 2 if volatility > 0.15 else 1
        risk_score += 3 if max_dd > 0.2 else 2 if max_dd > 0.15 else 1
        risk_score += 3 if 'var_95' in risk_metrics and abs(risk_metrics['var_95']) > 0.05 else 2 if 'var_95' in risk_metrics and abs(risk_metrics['var_95']) > 0.03 else 1
        
        if risk_score >= 8:
            overall_risk = "🔴 高风险"
            risk_desc = "多项风险指标显示高风险，需要立即采取风险控制措施"
        elif risk_score >= 6:
            overall_risk = "🟡 中高风险"
            risk_desc = "部分风险指标偏高，需要加强风险监控和控制"
        elif risk_score >= 4:
            overall_risk = "🟢 中等风险"
            risk_desc = "风险水平适中，在正常监控下可接受"
        elif risk_score >= 2:
            overall_risk = "🔵 中低风险"
            risk_desc = "风险水平较低，风险控制良好"
        else:
            overall_risk = "⚪ 低风险"
            risk_desc = "风险水平很低，安全性高"
        
        content += f"""
- **风险等级**: {overall_risk}
- **评估说明**: {risk_desc}
- **风险评分**: {risk_score}/9
  - 波动率风险: {"高 (3分)" if volatility > 0.25 else "中 (2分)" if volatility > 0.15 else "低 (1分)"}
  - 回撤风险: {"高 (3分)" if max_dd > 0.2 else "中 (2分)" if max_dd > 0.15 else "低 (1分)"}
  - 极端风险: {"高 (3分)" if 'var_95' in risk_metrics and abs(risk_metrics['var_95']) > 0.05 else "中 (2分)" if 'var_95' in risk_metrics and abs(risk_metrics['var_95']) > 0.03 else "低 (1分)"}
"""

        content += """
---

## 📝 重要声明

1. **风险认知**: 所有投资都有风险，本金可能损失
2. **历史局限性**: 历史风险分析不能完全预测未来风险
3. **模型风险**: 风险模型基于假设，可能存在模型风险
4. **极端事件**: 黑天鹅事件可能超出模型预测范围
5. **持续监控**: 风险状况会随时间变化，需要持续监控

---

**报告生成时间**: {}
**风险模型版本**: 1.0.0
**置信水平**: 95%

> 风险提示: 本报告为风险分析工具，不构成风险管理建议。实际风险管理需结合具体情况。
""".format(timestamp)

        return content
    
    def _generate_markdown_signal(self,
                                 data: Dict[str, Any],
                                 title: Optional[str] = None) -> str:
        """生成Markdown信号报告"""
        # 简化实现，实际应包含完整信号报告
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""# 交易信号报告

**生成时间**: {timestamp}

## 信号统计
- 总信号数: {len(data.get('signals', []))}
- 买入信号: {len([s for s in data.get('signals', []) if s.get('type') == 'buy'])}
- 卖出信号: {len([s for s in data.get('signals', []) if s.get('type') == 'sell'])}

## 最近信号
"""
        
        signals = data.get('signals', [])
        recent_signals = sorted(signals, key=lambda x: x.get('timestamp', ''), reverse=True)[:10]
        
        for signal in recent_signals:
            content += f"- {signal.get('timestamp')}: {signal.get('type')} @ {signal.get('price')} (置信度: {signal.get('confidence', 0):.2%})\n"
        
        return content
    
    def _generate_markdown_strategy_comparison(self,
                                             data: Dict[str, Any],
                                             title: Optional[str] = None) -> str:
        """生成Markdown策略对比报告"""
        # 简化实现
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f"""# 策略对比报告

**生成时间**: {timestamp}

## 对比策略
"""
        
        strategies = data.get('strategies', [])
        for i, strategy in enumerate(strategies):
            content += f"### 策略{i+1}: {strategy.get('name', '未命名')}\n"
            metrics = strategy.get('metrics', {})
            content += f"- 年化收益: {metrics.get('annual_return', 0):.2%}\n"
            content += f"- 夏普比率: {metrics.get('sharpe_ratio', 0):.2f}\n"
            content += f"- 最大回撤: {metrics.get('max_drawdown', 0):.2%}\n\n"
        
        return content
    
    def _generate_markdown_full(self,
                               data: Dict[str, Any],
                               title: Optional[str] = None) -> str:
        """生成Markdown完整报告"""
        # 组合各个部分
        summary = self._generate_markdown_summary(data, title)
        performance = self._generate_markdown_performance(data, "绩效分析")
        risk = self._generate_markdown_risk(data, "风险分析")
        
        return f"{summary}\n\n{performance}\n\n{risk}"
    
    def _generate_html_report(self,
                             report_type: ReportType,
                             data: Dict[str, Any],
                             title: Optional[str] = None) -> str:
        """生成HTML格式报告"""
        # 简化的HTML报告，实际应使用模板引擎
        markdown_content = self._generate_markdown_report(report_type, data, title)
        
        # 简单的Markdown到HTML转换
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>{title or '量化交易报告'}</title>
    <style>
        body {{ font-family: Arial, sans-serif; line-height: 1.6; margin: 40px; }}
        h1 {{ color: #333; border-bottom: 2px solid #eee; }}
        h2 {{ color: #555; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f5f5f5; }}
    </style>
</head>
<body>
{markdown_content.replace('#', '<h1>').replace('##', '<h2>').replace('###', '<h3>').replace('\n', '<br>')}
</body>
</html>
"""
        
        return html_content
    
    def _generate_json_report(self,
                             report_type: ReportType,
                             data: Dict[str, Any],
                             title: Optional[str] = None) -> str:
        """生成JSON格式报告"""
        report_data = {
            'metadata': {
                'title': title or f'{report_type.value}报告',
                'generated_at': datetime.now().isoformat(),
                'report_type': report_type.value,
                'format': 'json'
            },
            'data': data
        }
        
        return json.dumps(report_data, ensure_ascii=False, indent=2)
    
    def _generate_text_report(self,
                             report_type: ReportType,
                             data: Dict[str, Any],
                             title: Optional[str] = None) -> str:
        """生成纯文本格式报告"""
        # 简化的文本报告
        markdown_content = self._generate_markdown_report(report_type, data, title)
        
        # 移除Markdown标记
        text_content = markdown_content
        text_content = text_content.replace('#', '').replace('**', '').replace('|', ' ')
        
        return text_content

# 示例使用
if __name__ == "__main__":
    # 创建报告生成器
    config = {
        'output_dir': './reports',
        'default_format': 'markdown',
        'language': 'zh-CN'
    }
    
    generator = ReportGenerator(config)
    
    print("✅ 报告生成系统已初始化")
    print(f"📁 输出目录: {generator.output_dir}")
    
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
            'cvar_95': -0.045
        },
        'summary_stats': {
            'start_date': '2024-01-01',
            'end_date': '2024-12-31',
            'total_days': 365
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
            }
        ]
    }
    
    # 生成摘要报告
    print("\n📄 生成示例报告中...")
    
    summary_report = generator.generate_report(
        report_type='summary',
        data=example_data,
        title='示例交易分析报告'
    )
    
    print(f"✅ 摘要报告已生成: {summary_report}")
    
    # 生成绩效报告
    performance_report = generator.generate_report(
        report_type='performance',
        data=example_data,
        title='示例绩效分析报告'
    )
    
    print(f"✅ 绩效报告已生成: {performance_report}")
    
    # 生成风险报告
    risk_data = {
        'risk_metrics': example_data['metrics'],
        'var_analysis': {
            '95%': {'value': -0.032, 'method': '历史模拟法'},
            '99%': {'value': -0.048, 'method': '历史模拟法'}
        },
        'stress_tests': {
            '2020-03': {'loss': -0.215, 'recovery_days': 85},
            '2008-10': {'loss': -0.287, 'recovery_days': 120}
        }
    }
    
    risk_report = generator.generate_report(
        report_type='risk',
        data=risk_data,
        title='示例风险分析报告'
    )
    
    print(f"✅ 风险报告已生成: {risk_report}")
    
    print("\n🎉 报告生成系统示例完成!")