#!/usr/bin/env python3
"""
自主学习和回测循环系统 - 核心实现
基于TradingView社区内容自主学习交易策略，自动回测验证，建立长期循环
"""

import json
import numpy as np
import pandas as pd
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import hashlib
import os

# ============================================================================
# 策略表示框架
# ============================================================================

class StrategyCondition:
    """策略条件基类"""
    
    def __init__(self, indicator: str, condition: str, value: Any, 
                 timeframe: str = "1d", lookback: int = 1):
        """
        初始化策略条件
        
        参数:
            indicator: 指标名称 (如 "RSI", "MA", "Price")
            condition: 条件类型 (如 ">", "<", "cross_above", "breaks")
            value: 条件值 (如 30, "support_level", "MA20")
            timeframe: 时间框架 (如 "1d", "4h", "1h")
            lookback: 回溯周期 (默认1，表示当前bar)
        """
        self.indicator = indicator
        self.condition = condition
        self.value = value
        self.timeframe = timeframe
        self.lookback = lookback
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "indicator": self.indicator,
            "condition": self.condition,
            "value": self.value,
            "timeframe": self.timeframe,
            "lookback": self.lookback
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'StrategyCondition':
        """从字典创建"""
        return cls(
            indicator=data.get("indicator", ""),
            condition=data.get("condition", ""),
            value=data.get("value", ""),
            timeframe=data.get("timeframe", "1d"),
            lookback=data.get("lookback", 1)
        )
    
    def __str__(self) -> str:
        return f"{self.indicator}({self.timeframe}) {self.condition} {self.value}"


class TradingStrategy:
    """交易策略表示类"""
    
    # 策略类型常量
    TREND_FOLLOWING = "trend_following"
    MEAN_REVERSION = "mean_reversion"
    BREAKOUT = "breakout"
    MOMENTUM = "momentum"
    COMPOSITE = "composite"
    
    def __init__(self, 
                 name: str,
                 strategy_type: str,
                 description: str = "",
                 source: str = "tradingview",
                 created_at: str = None):
        """
        初始化交易策略
        
        参数:
            name: 策略名称
            strategy_type: 策略类型 (趋势跟踪、均值回归等)
            description: 策略描述
            source: 策略来源 (如 "tradingview", "generated", "manual")
            created_at: 创建时间
        """
        self.name = name
        self.strategy_type = strategy_type
        self.description = description
        self.source = source
        self.created_at = created_at or datetime.now().isoformat()
        
        # 策略条件
        self.entry_conditions: List[StrategyCondition] = []
        self.exit_conditions: List[StrategyCondition] = []
        
        # 风险管理
        self.risk_management = {
            "stop_loss_type": "fixed",  # fixed, trailing, atr
            "stop_loss_value": 2.0,     # 百分比或ATR倍数
            "take_profit_type": "fixed", # fixed, trailing, rrr
            "take_profit_value": 4.0,   # 百分比或风险回报比
            "position_sizing": "fixed",  # fixed, kelly, volatility
            "max_position_size": 0.1,   # 最大仓位比例
        }
        
        # 策略参数
        self.parameters: Dict[str, Dict] = {}
        
        # 绩效指标 (回测后填充)
        self.performance: Optional[Dict] = None
        
        # 生成唯一ID
        self.id = self._generate_id()
    
    def _generate_id(self) -> str:
        """生成策略唯一ID"""
        content = f"{self.name}_{self.strategy_type}_{self.created_at}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def add_entry_condition(self, condition: StrategyCondition):
        """添加入场条件"""
        self.entry_conditions.append(condition)
    
    def add_exit_condition(self, condition: StrategyCondition):
        """添加出场条件"""
        self.exit_conditions.append(condition)
    
    def set_parameter(self, name: str, default: Any, min_val: Any = None, 
                     max_val: Any = None, step: Any = None):
        """设置策略参数"""
        self.parameters[name] = {
            "default": default,
            "min": min_val,
            "max": max_val,
            "step": step,
            "optimizable": min_val is not None and max_val is not None
        }
    
    def set_risk_management(self, **kwargs):
        """设置风险管理参数"""
        self.risk_management.update(kwargs)
    
    def to_dict(self) -> Dict:
        """转换为字典"""
        return {
            "id": self.id,
            "name": self.name,
            "strategy_type": self.strategy_type,
            "description": self.description,
            "source": self.source,
            "created_at": self.created_at,
            "entry_conditions": [c.to_dict() for c in self.entry_conditions],
            "exit_conditions": [c.to_dict() for c in self.exit_conditions],
            "risk_management": self.risk_management,
            "parameters": self.parameters,
            "performance": self.performance
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TradingStrategy':
        """从字典创建策略"""
        strategy = cls(
            name=data.get("name", "未命名策略"),
            strategy_type=data.get("strategy_type", cls.TREND_FOLLOWING),
            description=data.get("description", ""),
            source=data.get("source", "unknown"),
            created_at=data.get("created_at")
        )
        
        # 添加入场条件
        for cond_data in data.get("entry_conditions", []):
            strategy.add_entry_condition(StrategyCondition.from_dict(cond_data))
        
        # 添加出场条件
        for cond_data in data.get("exit_conditions", []):
            strategy.add_exit_condition(StrategyCondition.from_dict(cond_data))
        
        # 设置风险管理
        if "risk_management" in data:
            strategy.risk_management.update(data["risk_management"])
        
        # 设置参数
        if "parameters" in data:
            strategy.parameters = data["parameters"]
        
        # 设置绩效
        if "performance" in data:
            strategy.performance = data["performance"]
        
        return strategy
    
    def to_backtest_code(self, framework: str = "backtrader") -> str:
        """
        转换为回测框架代码
        
        参数:
            framework: 回测框架名称 (backtrader, zipline, vectorbt等)
        
        返回:
            回测代码字符串
        """
        if framework == "backtrader":
            return self._generate_backtrader_code()
        elif framework == "vectorbt":
            return self._generate_vectorbt_code()
        else:
            return self._generate_generic_code()
    
    def _generate_backtrader_code(self) -> str:
        """生成Backtrader回测代码"""
        code = f'''
# 策略: {self.name}
# 类型: {self.strategy_type}
# 生成时间: {self.created_at}

import backtrader as bt

class {self.name.replace(' ', '_')}Strategy(bt.Strategy):
    params = (
        # 策略参数
'''
        
        # 添加参数
        for param_name, param_info in self.parameters.items():
            default = param_info.get('default', 0)
            code += f"        ('{param_name}', {default}),  # 默认值: {default}\n"
        
        code += '''    )
    
    def __init__(self):
        # 指标初始化
'''
        
        # 添加入场条件描述
        if self.entry_conditions:
            code += "        # 入场条件:\n"
            for cond in self.entry_conditions:
                code += f"        # {cond}\n"
        
        # 添加出场条件描述
        if self.exit_conditions:
            code += "        # 出场条件:\n"
            for cond in self.exit_conditions:
                code += f"        # {cond}\n"
        
        code += '''    
    def next(self):
        # 交易逻辑
        pass
        
    def notify_order(self, order):
        # 订单通知
        pass
        
    def notify_trade(self, trade):
        # 交易通知
        pass
'''
        
        return code
    
    def _generate_vectorbt_code(self) -> str:
        """生成VectorBT回测代码"""
        # 简化版本，实际需要更复杂实现
        return f'''
# VectorBT代码生成
# 策略: {self.name}
# 这是一个简化版本，实际需要更完整实现

import vectorbt as vbt

# 策略逻辑需要根据具体条件实现
# 这里返回模板代码
'''
    
    def _generate_generic_code(self) -> str:
        """生成通用回测代码模板"""
        return f'''
# 通用策略模板: {self.name}
# 策略类型: {self.strategy_type}
# 入场条件: {len(self.entry_conditions)}个
# 出场条件: {len(self.exit_conditions)}个

def initialize(context):
    """初始化函数"""
    # 策略初始化代码
    pass

def handle_data(context, data):
    """数据处理函数"""
    # 交易逻辑代码
    pass

def analyze(context, results):
    """分析函数"""
    # 回测结果分析
    pass
'''
    
    def __str__(self) -> str:
        return (f"策略: {self.name} ({self.strategy_type})\n"
                f"描述: {self.description[:50]}...\n"
                f"入场条件: {len(self.entry_conditions)}个\n"
                f"出场条件: {len(self.exit_conditions)}个\n"
                f"参数: {len(self.parameters)}个")

# ============================================================================
# 自主学习模块
# ============================================================================

class ContentParser:
    """内容解析器 - 解析TradingView指标描述和策略图表"""
    
    def __init__(self, knowledge_base_path: str = None):
        """初始化内容解析器"""
        self.knowledge_base = self._load_knowledge_base(knowledge_base_path)
        
        # 常见指标和策略模式
        self.common_patterns = {
            "trend_following": [
                "moving average crossover",
                "trend following", 
                "breakout",
                "higher high higher low"
            ],
            "mean_reversion": [
                "rsi oversold",
                "bollinger bands squeeze",
                "mean reversion",
                "oversold bounce"
            ],
            "breakout": [
                "breakout",
                "resistance break",
                "support break",
                "consolidation breakout"
            ],
            "momentum": [
                "momentum",
                "rsi divergence",
                "macd crossover",
                "volume spike"
            ]
        }
    
    def _load_knowledge_base(self, path: str) -> Dict:
        """加载知识库"""
        if path and os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        
        # 返回空知识库
        return {"indicators": {}, "strategies": {}, "patterns": {}}
    
    def parse_indicator_description(self, description: str) -> Dict:
        """
        解析指标描述文本
        
        参数:
            description: 指标描述文本
        
        返回:
            解析后的指标信息
        """
        result = {
            "name": "",
            "type": "",
            "parameters": {},
            "calculation": "",
            "usage": "",
            "confidence": 0.0
        }
        
        # 简单关键词匹配 (简化实现)
        text_lower = description.lower()
        
        # 检测指标类型
        if any(word in text_lower for word in ["trend", "direction", "moving average"]):
            result["type"] = "trend"
            result["confidence"] += 0.3
        if any(word in text_lower for word in ["momentum", "oscillator", "rsi", "stochastic"]):
            result["type"] = "momentum"
            result["confidence"] += 0.3
        if any(word in text_lower for word in ["volatility", "atr", "bollinger"]):
            result["type"] = "volatility"
            result["confidence"] += 0.3
        if any(word in text_lower for word in ["volume", "money flow"]):
            result["type"] = "volume"
            result["confidence"] += 0.3
        
        # 提取参数 (简单正则匹配)
        import re
        
        # 寻找数字参数
        param_patterns = [
            r'(\d+)\s*(?:period|day|hour|minute)',
            r'parameter\s*[:=]\s*(\d+(?:\.\d+)?)',
            r'default\s*[:=]\s*(\d+(?:\.\d+)?)'
        ]
        
        for pattern in param_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                param_name = f"param_{len(result['parameters']) + 1}"
                result["parameters"][param_name] = float(match) if '.' in match else int(match)
        
        # 提取指标名称 (取第一行或关键词)
        lines = description.split('\n')
        if lines:
            result["name"] = lines[0].strip()[:50]
        
        # 计算置信度
        if result["type"]:
            result["confidence"] += 0.2
        if result["parameters"]:
            result["confidence"] += 0.2
        if len(description) > 50:
            result["confidence"] += 0.1
        
        result["confidence"] = min(1.0, result["confidence"])
        
        return result
    
    def parse_strategy_chart(self, chart_description: str) -> Dict:
        """
        解析策略图表描述
        
        参数:
            chart_description: 图表描述文本
        
        返回:
            解析后的策略信息
        """
        result = {
            "strategy_type": "",
            "entry_signals": [],
            "exit_signals": [],
            "indicators_used": [],
            "confidence": 0.0
        }
        
        text_lower = chart_description.lower()
        
        # 检测策略类型
        for strategy_type, patterns in self.common_patterns.items():
            for pattern in patterns:
                if pattern in text_lower:
                    result["strategy_type"] = strategy_type
                    result["confidence"] += 0.4
                    break
            if result["strategy_type"]:
                break
        
        # 检测入场信号
        entry_keywords = ["buy", "long", "entry", "enter", "go long", "purchase"]
        exit_keywords = ["sell", "short", "exit", "close", "stop loss", "take profit"]
        
        lines = chart_description.split('\n')
        for line in lines:
            line_lower = line.lower()
            
            # 检查入场信号
            if any(keyword in line_lower for keyword in entry_keywords):
                signal = self._extract_signal_from_line(line)
                if signal:
                    result["entry_signals"].append(signal)
                    result["confidence"] += 0.1
            
            # 检查出场信号
            if any(keyword in line_lower for keyword in exit_keywords):
                signal = self._extract_signal_from_line(line)
                if signal:
                    result["exit_signals"].append(signal)
                    result["confidence"] += 0.1
        
        # 检测使用的指标
        common_indicators = ["rsi", "macd", "ma", "moving average", "bollinger", 
                           "stochastic", "atr", "volume", "adx", "ichimoku"]
        
        for indicator in common_indicators:
            if indicator in text_lower:
                result["indicators_used"].append(indicator)
                result["confidence"] += 0.05
        
        result["confidence"] = min(1.0, result["confidence"])
        
        return result
    
    def _extract_signal_from_line(self, line: str) -> Dict:
        """从文本行中提取交易信号"""
        # 简化实现，实际需要更复杂的NLP处理
        return {
            "text": line.strip(),
            "conditions": [],
            "confidence": 0.5
        }
    
    def generate_strategy_from_content(self, 
                                      indicator_desc: str = "",
                                      chart_desc: str = "") -> TradingStrategy:
        """
        从内容生成交易策略
        
        参数:
            indicator_desc: 指标描述
            chart_desc: 图表描述
        
        返回:
            生成的交易策略
        """
        # 解析内容
        indicator_info = self.parse_indicator_description(indicator_desc) if indicator_desc else {}
        strategy_info = self.parse_strategy_chart(chart_desc) if chart_desc else {}
        
        # 确定策略名称和类型
        strategy_name = indicator_info.get("name", "Generated Strategy")
        if not strategy_name or strategy_name == "":
            strategy_name = "TradingView Strategy"
        
        strategy_type = strategy_info.get("strategy_type", "")
        if not strategy_type:
            # 根据内容推断类型
            if "trend" in indicator_desc.lower():
                strategy_type = TradingStrategy.TREND_FOLLOWING
            elif "reversion" in indicator_desc.lower() or "oversold" in indicator_desc.lower():
                strategy_type = TradingStrategy.MEAN_REVERSION
            else:
                strategy_type = TradingStrategy.TREND_FOLLOWING  # 默认
        
        # 创建策略
        strategy = TradingStrategy(
            name=strategy_name,
            strategy_type=strategy_type,
            description=f"从TradingView内容生成的策略\n指标描述: {indicator_desc[:100]}...\n图表描述: {chart_desc[:100]}...",
            source="tradingview_generated"
        )
        
        # 添加入场条件 (简化)
        if strategy_info.get("entry_signals"):
            for signal in strategy_info["entry_signals"][:3]:  # 最多3个入场条件
                condition = StrategyCondition(
                    indicator="Price",  # 简化，实际应根据信号确定
                    condition="breaks",
                    value="resistance",
                    timeframe="1d"
                )
                strategy.add_entry_condition(condition)
        else:
            # 默认入场条件
            condition = StrategyCondition(
                indicator="RSI",
                condition="<",
                value=30,
                timeframe="1d"
            )
            strategy.add_entry_condition(condition)
        
        # 添加出场条件 (简化)
        if strategy_info.get("exit_signals"):
            for signal in strategy_info["exit_signals"][:2]:  # 最多2个出场条件
                condition = StrategyCondition(
                    indicator="Price",
                    condition="breaks",
                    value="support",
                    timeframe="1d"
                )
                strategy.add_exit_condition(condition)
        else:
            # 默认出场条件
            condition = StrategyCondition(
                indicator="RSI",
                condition=">",
                value=70,
                timeframe="1d"
            )
            strategy.add_exit_condition(condition)
        
        # 设置参数
        for param_name, param_value in indicator_info.get("parameters", {}).items():
            strategy.set_parameter(
                name=param_name,
                default=param_value,
                min_val=param_value * 0.5 if isinstance(param_value, (int, float)) else None,
                max_val=param_value * 1.5 if isinstance(param_value, (int, float)) else None
            )
        
        # 设置风险管理
        strategy.set_risk_management(
            stop_loss_type="fixed",
            stop_loss_value=2.0,
            take_profit_type="rrr",
            take_profit_value=2.0,
            position_sizing="fixed",
            max_position_size=0.1
        )
        
        return strategy

# ============================================================================
# 回测集成模块
# ============================================================================

class BacktestIntegrator:
    """回测集成器 - 将策略转换为可回测代码并执行回测"""
    
    def __init__(self, data_provider=None):
        """初始化回测集成器"""
        self.data_provider = data_provider
        self.results_cache = {}  # 缓存回测结果
    
    def run_backtest(self, strategy: TradingStrategy, 
                    data: pd.DataFrame = None,
                    initial_capital: float = 100000,
                    timeframe: str = "1d") -> Dict:
        """
        运行策略回测
        
        参数:
            strategy: 交易策略
            data: 回测数据 (DataFrame)
            initial_capital: 初始资金
            timeframe: 时间框架
        
        返回:
            回测结果字典
        """
        # 生成回测代码
        backtest_code = strategy.to_backtest_code()
        
        # 简化回测执行 (实际需要完整回测引擎)
        # 这里返回模拟结果
        result = self._simulate_backtest(strategy, initial_capital)
        
        # 更新策略绩效
        strategy.performance = result
        
        # 缓存结果
        self.results_cache[strategy.id] = {
            "strategy": strategy.to_dict(),
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def _simulate_backtest(self, strategy: TradingStrategy, 
                          initial_capital: float) -> Dict:
        """模拟回测结果 (简化实现)"""
        # 在实际系统中，这里应该执行真正的回测
        # 现在返回模拟数据用于演示
        
        np.random.seed(int(hashlib.md5(strategy.id.encode()).hexdigest(), 16) % 2**32)
        
        # 模拟绩效指标
        total_return = np.random.uniform(-20, 100)  # -20% 到 100%
        sharpe_ratio = np.random.uniform(0, 2.0)
        max_drawdown = np.random.uniform(-50, -5)
        win_rate = np.random.uniform(30, 70)
        
        return {
            "initial_capital": initial_capital,
            "final_capital": initial_capital * (1 + total_return/100),
            "total_return_percent": total_return,
            "annual_return_percent": total_return * np.random.uniform(0.8, 1.2),
            "sharpe_ratio": sharpe_ratio,
            "max_drawdown_percent": max_drawdown,
            "win_rate_percent": win_rate,
            "total_trades": np.random.randint(10, 100),
            "profit_factor": np.random.uniform(0.8, 3.0),
            "calmar_ratio": abs(total_return / max_drawdown) if max_drawdown != 0 else 0,
            "backtest_period": "2020-01-01 to 2023-12-31",
            "backtest_framework": "simulated",
            "timestamp": datetime.now().isoformat(),
            "notes": "这是模拟回测结果，实际回测需要真实数据和完整回测引擎"
        }
    
    def generate_report(self, strategy: TradingStrategy, 
                       result: Dict) -> str:
        """生成回测报告"""
        report = f"""
# 回测报告: {strategy.name}
## 策略信息
- 策略ID: {strategy.id}
- 策略类型: {strategy.strategy_type}
- 创建时间: {strategy.created_at}
- 数据来源: {strategy.source}

## 绩效摘要
- 初始资金: ${result.get('initial_capital', 0):,.2f}
- 最终资金: ${result.get('final_capital', 0):,.2f}
- 总收益率: {result.get('total_return_percent', 0):.2f}%
- 年化收益率: {result.get('annual_return_percent', 0):.2f}%
- 夏普比率: {result.get('sharpe_ratio', 0):.2f}
- 最大回撤: {result.get('max_drawdown_percent', 0):.2f}%
- 胜率: {result.get('win_rate_percent', 0):.2f}%
- 总交易次数: {result.get('total_trades', 0)}
- 盈利因子: {result.get('profit_factor', 0):.2f}

## 策略条件
### 入场条件 ({len(strategy.entry_conditions)}个)
"""
        
        for i, cond in enumerate(strategy.entry_conditions, 1):
            report += f"{i}. {cond}\n"
        
        report += """
### 出场条件 ({len(strategy.exit_conditions)}个)
"""
        
        for i, cond in enumerate(strategy.exit_conditions, 1):
            report += f"{i}. {cond}\n"
        
        report += f"""
## 风险管理
{json.dumps(strategy.risk_management, indent=2, ensure_ascii=False)}

## 参数配置
{json.dumps(strategy.parameters, indent=2, ensure_ascii=False)}

## 回测详情
- 回测框架: {result.get('backtest_framework', '未知')}
- 回测周期: {result.get('backtest_period', '未知')}
- 生成时间: {result.get('timestamp', '未知')}
- 备注: {result.get('notes', '无')}
"""
        
        return report

# ============================================================================
# 循环控制模块
# ============================================================================

class LearningCycleController:
    """学习循环控制器 - 管理学习-回测-优化循环"""
    
    def __init__(self, 
                 knowledge_base_path: str = None,
                 output_dir: str = "./cycle_output"):
        """初始化循环控制器"""
        self.parser = ContentParser(knowledge_base_path)
        self.backtester = BacktestIntegrator()
        self.output_dir = output_dir
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
        
        # 循环状态
        self.cycle_count = 0
        self.strategies_generated = 0
        self.strategies_tested = 0
        self.best_strategies = []
        
        # 循环配置
        self.config = {
            "max_cycles": 100,           # 最大循环次数
            "strategies_per_cycle": 3,   # 每轮生成策略数
            "min_performance_threshold": 0.0,  # 最小绩效阈值
            "optimization_enabled": True,      # 是否启用优化
            "knowledge_accumulation": True     # 是否积累知识
        }
    
    def run_cycle(self, 
                  indicator_content: str = "",
                  chart_content: str = "") -> Dict:
        """
        运行一个完整的学习-回测循环
        
        参数:
            indicator_content: 指标描述内容
            chart_content: 图表描述内容
        
        返回:
            循环结果
        """
        self.cycle_count += 1
        print(f"🚀 开始第 {self.cycle_count} 轮学习-回测循环")
        
        cycle_result = {
            "cycle_number": self.cycle_count,
            "start_time": datetime.now().isoformat(),
            "strategies_generated": 0,
            "strategies_tested": 0,
            "successful_strategies": [],
            "failed_strategies": [],
            "best_strategy": None,
            "end_time": None
        }
        
        # 1. 学习阶段: 从内容生成策略
        print("📚 学习阶段: 解析内容并生成策略...")
        strategies = []
        
        for i in range(self.config["strategies_per_cycle"]):
            strategy = self.parser.generate_strategy_from_content(
                indicator_desc=indicator_content,
                chart_desc=chart_content
            )
            strategy.name = f"{strategy.name}_Cycle{self.cycle_count}_V{i+1}"
            strategies.append(strategy)
            self.strategies_generated += 1
            cycle_result["strategies_generated"] += 1
        
        print(f"  生成 {len(strategies)} 个策略")
        
        # 2. 回测阶段: 测试生成的策略
        print("📊 回测阶段: 测试策略性能...")
        
        for strategy in strategies:
            print(f"  回测策略: {strategy.name}")
            
            # 运行回测
            result = self.backtester.run_backtest(strategy)
            self.strategies_tested += 1
            cycle_result["strategies_tested"] += 1
            
            # 评估策略
            performance = result.get("total_return_percent", 0)
            
            if performance >= self.config["min_performance_threshold"]:
                cycle_result["successful_strategies"].append({
                    "strategy_id": strategy.id,
                    "name": strategy.name,
                    "performance": performance,
                    "sharpe_ratio": result.get("sharpe_ratio", 0)
                })
                
                # 更新最佳策略列表
                self._update_best_strategies(strategy, result)
            else:
                cycle_result["failed_strategies"].append({
                    "strategy_id": strategy.id,
                    "name": strategy.name,
                    "performance": performance,
                    "reason": "绩效低于阈值"
                })
        
        # 3. 优化阶段: 基于结果优化学习
        if self.config["optimization_enabled"] and cycle_result["successful_strategies"]:
            print("⚡ 优化阶段: 基于回测结果优化学习...")
            self._optimize_learning(cycle_result["successful_strategies"])
        
        # 4. 知识积累阶段: 保存成功策略
        if self.config["knowledge_accumulation"] and cycle_result["successful_strategies"]:
            print("💾 知识积累阶段: 保存成功策略...")
            self._accumulate_knowledge(cycle_result["successful_strategies"])
        
        # 确定本轮最佳策略
        if cycle_result["successful_strategies"]:
            best = max(cycle_result["successful_strategies"], key=lambda x: x["performance"])
            cycle_result["best_strategy"] = best
        
        cycle_result["end_time"] = datetime.now().isoformat()
        
        # 保存循环结果
        self._save_cycle_result(cycle_result)
        
        print(f"✅ 第 {self.cycle_count} 轮循环完成")
        print(f"   成功策略: {len(cycle_result['successful_strategies'])}")
        print(f"   失败策略: {len(cycle_result['failed_strategies'])}")
        
        if cycle_result["best_strategy"]:
            print(f"   最佳策略: {cycle_result['best_strategy']['name']} "
                  f"(收益率: {cycle_result['best_strategy']['performance']:.2f}%)")
        
        return cycle_result
    
    def _update_best_strategies(self, strategy: TradingStrategy, result: Dict):
        """更新最佳策略列表"""
        performance = result.get("total_return_percent", 0)
        
        # 添加到最佳策略列表
        self.best_strategies.append({
            "strategy": strategy.to_dict(),
            "performance": result,
            "cycle_number": self.cycle_count
        })
        
        # 按绩效排序，保留前10个
        self.best_strategies.sort(key=lambda x: x["performance"].get("total_return_percent", 0), 
                                 reverse=True)
        if len(self.best_strategies) > 10:
            self.best_strategies = self.best_strategies[:10]
    
    def _optimize_learning(self, successful_strategies: List[Dict]):
        """基于成功策略优化学习过程"""
        # 分析成功策略的共同特征
        # 这里可以更新解析器的知识库或调整生成策略的参数
        # 简化实现: 记录成功模式
        pass
    
    def _accumulate_knowledge(self, successful_strategies: List[Dict]):
        """积累知识到知识库"""
        # 将成功策略保存到知识库
        knowledge_file = os.path.join(self.output_dir, "knowledge_base.json")
        
        knowledge = {}
        if os.path.exists(knowledge_file):
            with open(knowledge_file, 'r', encoding='utf-8') as f:
                knowledge = json.load(f)
        
        # 添加新知识
        if "successful_strategies" not in knowledge:
            knowledge["successful_strategies"] = []
        
        knowledge["successful_strategies"].extend(successful_strategies)
        knowledge["last_updated"] = datetime.now().isoformat()
        knowledge["total_cycles"] = self.cycle_count
        
        # 保存知识库
        with open(knowledge_file, 'w', encoding='utf-8') as f:
            json.dump(knowledge, f, indent=2, ensure_ascii=False)
        
        print(f"   知识库已更新，累计成功策略: {len(knowledge['successful_strategies'])}")
    
    def _save_cycle_result(self, cycle_result: Dict):
        """保存循环结果到文件"""
        filename = os.path.join(self.output_dir, f"cycle_{self.cycle_count:03d}.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(cycle_result, f, indent=2, ensure_ascii=False)
    
    def run_multiple_cycles(self, num_cycles: int = 5, 
                           content_provider=None) -> List[Dict]:
        """
        运行多个循环
        
        参数:
            num_cycles: 循环次数
            content_provider: 内容提供函数
        
        返回:
            所有循环结果
        """
        all_results = []
        
        for i in range(num_cycles):
            # 获取内容 (简化: 使用示例内容)
            if content_provider:
                indicator_content, chart_content = content_provider()
            else:
                indicator_content = self._get_example_indicator_content()
                chart_content = self._get_example_chart_content()
            
            # 运行单个循环
            result = self.run_cycle(indicator_content, chart_content)
            all_results.append(result)
            
            # 检查是否达到停止条件
            if self.cycle_count >= self.config["max_cycles"]:
                print(f"⚠️ 达到最大循环次数 {self.config['max_cycles']}，停止运行")
                break
        
        return all_results
    
    def _get_example_indicator_content(self) -> str:
        """获取示例指标描述内容"""
        return """
        Supertrend Indicator
        The Supertrend indicator is a trend-following indicator that uses 
        Average True Range (ATR) to identify trend direction. 
        Parameters: ATR period = 10, multiplier = 3.0
        Buy when Supertrend turns green, sell when it turns red.
        """
    
    def _get_example_chart_content(self) -> str:
        """获取示例图表描述内容"""
        return """
        RSI Strategy Chart
        Buy when RSI drops below 30 (oversold) and starts rising.
        Sell when RSI rises above 70 (overbought) and starts falling.
        Use 14-period RSI on daily timeframe.
        Stop loss at 2% below entry, take profit at 4% above entry.
        """

    def get_summary(self) -> Dict:
        """获取循环系统摘要"""
        return {
            "total_cycles": self.cycle_count,
            "strategies_generated": self.strategies_generated,
            "strategies_tested": self.strategies_tested,
            "best_strategies_count": len(self.best_strategies),
            "output_dir": self.output_dir,
            "config": self.config,
            "timestamp": datetime.now().isoformat()
        }

# ============================================================================
# 主函数和示例
# ============================================================================

def main():
    """主函数 - 演示自主学习和回测循环系统"""
    print("=" * 60)
    print("自主学习和回测循环系统")
    print("基于TradingView社区内容自主学习交易策略")
    print("=" * 60)
    
    # 1. 初始化循环控制器
    print("🔄 初始化循环控制器...")
    controller = LearningCycleController(
        output_dir="./learning_cycle_output"
    )
    
    # 2. 运行几个示例循环
    print("\n🚀 开始运行学习-回测循环...")
    results = controller.run_multiple_cycles(num_cycles=3)
    
    # 3. 显示摘要
    print("\n📈 循环系统摘要:")
    summary = controller.get_summary()
    print(f"总循环次数: {summary['total_cycles']}")
    print(f"生成策略数: {summary['strategies_generated']}")
    print(f"测试策略数: {summary['strategies_tested']}")
    print(f"最佳策略数: {summary['best_strategies_count']}")
    print(f"输出目录: {summary['output_dir']}")
    
    # 4. 显示最佳策略
    if controller.best_strategies:
        print("\n🏆 最佳策略:")
        for i, best in enumerate(controller.best_strategies[:3], 1):
            strategy_data = best["strategy"]
            performance = best["performance"]
            print(f"{i}. {strategy_data['name']}")
            print(f"   收益率: {performance.get('total_return_percent', 0):.2f}%")
            print(f"   夏普比率: {performance.get('sharpe_ratio', 0):.2f}")
            print(f"   最大回撤: {performance.get('max_drawdown_percent', 0):.2f}%")
    
    # 5. 演示单个策略生成和回测
    print("\n🔧 演示单个策略生成和回测:")
    parser = ContentParser()
    
    # 示例内容
    indicator_desc = """
    Moving Average Crossover Strategy
    Buy when 50-day MA crosses above 200-day MA (Golden Cross).
    Sell when 50-day MA crosses below 200-day MA (Death Cross).
    Use daily timeframe for trend identification.
    """
    
    chart_desc = """
    Golden Cross Chart on S&P 500
    Shows buy signals when short MA crosses above long MA.
    Historical backtest shows good performance in trending markets.
    """
    
    # 生成策略
    strategy = parser.generate_strategy_from_content(indicator_desc, chart_desc)
    print(f"生成的策略: {strategy.name}")
    print(f"策略类型: {strategy.strategy_type}")
    print(f"入场条件: {len(strategy.entry_conditions)}个")
    print(f"出场条件: {len(strategy.exit_conditions)}个")
    
    # 运行回测
    backtester = BacktestIntegrator()
    result = backtester.run_backtest(strategy)
    
    print(f"\n回测结果:")
    print(f"总收益率: {result.get('total_return_percent', 0):.2f}%")
    print(f"夏普比率: {result.get('sharpe_ratio', 0):.2f}")
    print(f"最大回撤: {result.get('max_drawdown_percent', 0):.2f}%")
    
    # 6. 保存系统状态
    print(f"\n💾 系统状态已保存到: {controller.output_dir}/")
    print("=" * 60)
    print("✅ 自主学习和回测循环系统演示完成")
    print("=" * 60)

if __name__ == "__main__":
    main()