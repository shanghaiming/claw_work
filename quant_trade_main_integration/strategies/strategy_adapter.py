#!/usr/bin/env python3
"""
策略适配器 - 将workspace策略转换为统一接口
支持TradingView指标、Python策略、IPython Notebook策略的适配
"""

import os
import sys
import importlib
import inspect
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional, List, Callable, Type
import logging
from pathlib import Path
import json

from ..core.strategy_base import StrategyBase

logger = logging.getLogger(__name__)


class WorkspaceStrategyAdapter(StrategyBase):
    """
    workspace策略适配器
    将任意workspace策略包装为统一接口
    """
    
    def __init__(self, workspace_strategy_instance: Any, 
                 adapter_config: Optional[Dict[str, Any]] = None,
                 strategy_name: Optional[str] = None):
        """
        初始化适配器
        
        Args:
            workspace_strategy_instance: workspace策略实例
            adapter_config: 适配器配置
            strategy_name: 策略名称（如未提供则自动生成）
        """
        self.workspace_strategy = workspace_strategy_instance
        self.adapter_config = adapter_config or {}
        
        # 自动检测策略名称
        if strategy_name is None:
            strategy_name = self._detect_strategy_name()
        
        # 提取策略参数
        params = self._extract_strategy_params()
        
        super().__init__(name=strategy_name, params=params)
        
        # 数据转换状态
        self.data_converted = None
        self.last_signal = None
        
        logger.info(f"workspace策略适配器创建: {strategy_name}")
    
    def _detect_strategy_name(self) -> str:
        """自动检测策略名称"""
        strategy_obj = self.workspace_strategy
        
        # 尝试获取类名
        if hasattr(strategy_obj, '__class__'):
            class_name = strategy_obj.__class__.__name__
        else:
            class_name = type(strategy_obj).__name__
        
        # 尝试获取模块名
        if hasattr(strategy_obj, '__module__'):
            module_name = strategy_obj.__module__
        else:
            module_name = 'unknown'
        
        # 生成策略名称
        name = f"workspace_{module_name}_{class_name}"
        return name[:50]  # 限制长度
    
    def _extract_strategy_params(self) -> Dict[str, Any]:
        """提取策略参数"""
        params = {}
        strategy_obj = self.workspace_strategy
        
        # 方法1: 检查是否有params属性
        if hasattr(strategy_obj, 'params'):
            try:
                if callable(strategy_obj.params):
                    params = strategy_obj.params()
                else:
                    params = strategy_obj.params
            except:
                pass
        
        # 方法2: 检查初始化参数
        elif hasattr(strategy_obj, '__init__'):
            try:
                init_signature = inspect.signature(strategy_obj.__init__)
                for param_name, param in init_signature.parameters.items():
                    if param_name != 'self' and param.default != inspect.Parameter.empty:
                        params[param_name] = param.default
            except:
                pass
        
        # 方法3: 检查常见参数属性
        common_param_names = ['window', 'period', 'threshold', 'short_window', 
                             'long_window', 'fast_period', 'slow_period', 'signal_period']
        
        for param_name in common_param_names:
            if hasattr(strategy_obj, param_name):
                try:
                    params[param_name] = getattr(strategy_obj, param_name)
                except:
                    pass
        
        return params
    
    def _convert_data_format(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        转换数据格式为workspace策略期望的格式
        
        Args:
            data: 统一格式数据
            
        Returns:
            workspace策略格式数据
        """
        # 默认不转换，直接返回
        # 子类可以重写此方法进行特定格式转换
        
        data_converted = data.copy()
        
        # 确保有必要的列
        required_cols = ['open', 'high', 'low', 'close', 'volume']
        for col in required_cols:
            if col not in data_converted.columns:
                logger.warning(f"数据缺少列: {col}")
        
        # 重命名列以适应不同策略（如有需要）
        column_mapping = self.adapter_config.get('column_mapping', {})
        if column_mapping:
            data_converted = data_converted.rename(columns=column_mapping)
        
        return data_converted
    
    def _convert_signal_format(self, workspace_signal: Any) -> Dict[str, Any]:
        """
        转换信号格式为统一格式
        
        Args:
            workspace_signal: workspace策略生成的信号
            
        Returns:
            统一格式信号字典
        """
        signal = {
            'signal_type': 'hold',
            'confidence': 0.5,
            'price': 0.0,
            'reason': 'workspace策略信号',
            'timestamp': pd.Timestamp.now(),
            'raw_signal': workspace_signal
        }
        
        # 根据workspace信号类型进行转换
        if workspace_signal is None:
            signal['signal_type'] = 'hold'
            signal['confidence'] = 0.3
            
        elif isinstance(workspace_signal, (int, float, np.number)):
            # 数值信号：正数为买入，负数为卖出
            signal_value = float(workspace_signal)
            if signal_value > 0:
                signal['signal_type'] = 'buy'
                signal['confidence'] = min(abs(signal_value), 1.0)
            elif signal_value < 0:
                signal['signal_type'] = 'sell'
                signal['confidence'] = min(abs(signal_value), 1.0)
            else:
                signal['signal_type'] = 'hold'
                signal['confidence'] = 0.3
                
        elif isinstance(workspace_signal, str):
            # 字符串信号
            signal_str = workspace_signal.lower()
            if 'buy' in signal_str or 'long' in signal_str or '买入' in signal_str:
                signal['signal_type'] = 'buy'
                signal['confidence'] = 0.7
            elif 'sell' in signal_str or 'short' in signal_str or '卖出' in signal_str:
                signal['signal_type'] = 'sell'
                signal['confidence'] = 0.7
            elif 'hold' in signal_str or '等待' in signal_str or '观望' in signal_str:
                signal['signal_type'] = 'hold'
                signal['confidence'] = 0.5
                
        elif isinstance(workspace_signal, dict):
            # 字典信号
            signal.update(workspace_signal)
            
            # 标准化信号类型
            if 'action' in signal and 'signal_type' not in signal:
                signal['signal_type'] = signal.pop('action')
                
            # 确保必要字段
            if 'signal_type' not in signal:
                signal['signal_type'] = 'hold'
            if 'confidence' not in signal:
                signal['confidence'] = 0.5
                
        elif isinstance(workspace_signal, (list, tuple)) and len(workspace_signal) >= 2:
            # 元组/列表信号：通常为(信号类型, 置信度)
            signal['signal_type'] = str(workspace_signal[0]).lower()
            if len(workspace_signal) > 1:
                signal['confidence'] = float(workspace_signal[1])
        
        # 确保信号类型有效
        valid_types = ['buy', 'sell', 'hold']
        if signal['signal_type'] not in valid_types:
            logger.warning(f"无效信号类型: {signal['signal_type']}, 转换为hold")
            signal['signal_type'] = 'hold'
        
        # 确保置信度在[0,1]范围内
        signal['confidence'] = max(0.0, min(1.0, signal['confidence']))
        
        return signal
    
    def on_data(self, data: pd.DataFrame) -> None:
        """
        处理市场数据，传递给workspace策略
        
        Args:
            data: 市场数据DataFrame
        """
        self.data = data.copy()
        
        try:
            # 转换数据格式
            data_converted = self._convert_data_format(data)
            self.data_converted = data_converted
            
            # 调用workspace策略的数据处理方法
            # 方法1: 尝试调用on_data方法
            if hasattr(self.workspace_strategy, 'on_data'):
                self.workspace_strategy.on_data(data_converted)
                
            # 方法2: 尝试调用process_data方法
            elif hasattr(self.workspace_strategy, 'process_data'):
                self.workspace_strategy.process_data(data_converted)
                
            # 方法3: 尝试调用update方法
            elif hasattr(self.workspace_strategy, 'update'):
                self.workspace_strategy.update(data_converted)
                
            # 方法4: 尝试调用fit_predict方法（机器学习策略）
            elif hasattr(self.workspace_strategy, 'fit_predict'):
                # 对于机器学习策略，可能需要训练
                pass
                
            else:
                logger.info(f"策略 {self.name} 没有标准数据处理方法，跳过数据处理")
                
        except Exception as e:
            logger.error(f"策略 {self.name} 数据处理失败: {e}")
            # 继续执行，可能策略不需要显式数据处理
    
    def generate_signal(self) -> Dict[str, Any]:
        """
        生成交易信号，调用workspace策略的信号生成方法
        
        Returns:
            统一格式信号字典
        """
        if self.data_converted is None:
            return {'signal_type': 'hold', 'confidence': 0.0, 'reason': '数据未准备好'}
        
        try:
            workspace_signal = None
            
            # 方法1: 尝试调用generate_signal方法
            if hasattr(self.workspace_strategy, 'generate_signal'):
                workspace_signal = self.workspace_strategy.generate_signal()
                
            # 方法2: 尝试调用predict方法
            elif hasattr(self.workspace_strategy, 'predict'):
                if self.data_converted is not None:
                    workspace_signal = self.workspace_strategy.predict(self.data_converted)
                    
            # 方法3: 尝试调用get_signal方法
            elif hasattr(self.workspace_strategy, 'get_signal'):
                workspace_signal = self.workspace_strategy.get_signal()
                
            # 方法4: 尝试调用decision_function方法
            elif hasattr(self.workspace_strategy, 'decision_function'):
                if self.data_converted is not None:
                    workspace_signal = self.workspace_strategy.decision_function(self.data_converted)
                    
            # 方法5: 尝试调用__call__方法
            elif callable(self.workspace_strategy):
                workspace_signal = self.workspace_strategy(self.data_converted)
                
            else:
                # 如果策略没有标准信号生成方法，使用默认逻辑
                workspace_signal = self._generate_default_signal()
            
            # 转换信号格式
            signal = self._convert_signal_format(workspace_signal)
            
            # 添加当前价格
            if self.data_converted is not None and len(self.data_converted) > 0:
                latest_data = self.data_converted.iloc[-1]
                if 'close' in latest_data:
                    signal['price'] = float(latest_data['close'])
                elif 'price' in latest_data:
                    signal['price'] = float(latest_data['price'])
            
            self.last_signal = signal
            self.signals.append(signal)
            
            logger.debug(f"策略 {self.name} 生成信号: {signal}")
            return signal
            
        except Exception as e:
            logger.error(f"策略 {self.name} 信号生成失败: {e}")
            return {'signal_type': 'hold', 'confidence': 0.0, 'reason': f'信号生成失败: {e}'}
    
    def _generate_default_signal(self) -> Any:
        """生成默认信号（当策略没有标准信号生成方法时）"""
        # 这里可以实现一些启发式规则
        
        # 示例：基于移动平均的简单信号
        if self.data_converted is not None and len(self.data_converted) > 20:
            try:
                closes = self.data_converted['close'].values
                
                # 计算简单移动平均
                ma_short = np.mean(closes[-5:]) if len(closes) >= 5 else closes[-1]
                ma_long = np.mean(closes[-20:]) if len(closes) >= 20 else closes[-1]
                
                # 生成信号
                if ma_short > ma_long:
                    return ('buy', 0.6)
                elif ma_short < ma_long:
                    return ('sell', 0.6)
                else:
                    return ('hold', 0.5)
                    
            except:
                pass
        
        # 默认返回持有
        return ('hold', 0.5)
    
    def get_workspace_strategy_info(self) -> Dict[str, Any]:
        """获取workspace策略信息"""
        info = {
            'adapter_name': self.name,
            'workspace_strategy_type': type(self.workspace_strategy).__name__,
            'workspace_strategy_module': getattr(self.workspace_strategy, '__module__', 'unknown'),
            'adapter_config': self.adapter_config,
            'detected_methods': []
        }
        
        # 检测策略支持的方法
        strategy_obj = self.workspace_strategy
        
        method_patterns = {
            'data_processing': ['on_data', 'process_data', 'update', 'fit', 'transform'],
            'signal_generation': ['generate_signal', 'predict', 'get_signal', 'decision_function'],
            'parameter_management': ['get_params', 'set_params', 'get_parameters', 'set_parameters'],
            'training': ['fit', 'train', 'fit_predict']
        }
        
        for category, methods in method_patterns.items():
            for method in methods:
                if hasattr(strategy_obj, method):
                    info['detected_methods'].append({
                        'category': category,
                        'method': method,
                        'callable': callable(getattr(strategy_obj, method))
                    })
        
        return info


class TradingViewIndicatorAdapter(WorkspaceStrategyAdapter):
    """
    TradingView指标适配器
    专门用于适配TradingView风格的技术指标
    """
    
    def __init__(self, indicator_function: Callable, 
                 indicator_name: str,
                 indicator_params: Optional[Dict[str, Any]] = None):
        """
        初始化TradingView指标适配器
        
        Args:
            indicator_function: 指标函数
            indicator_name: 指标名称
            indicator_params: 指标参数
        """
        self.indicator_function = indicator_function
        self.indicator_name = indicator_name
        self.indicator_params = indicator_params or {}
        
        # 创建伪策略实例
        class IndicatorStrategy:
            def __init__(self, func, params):
                self.func = func
                self.params = params
                self.data = None
            
            def process_data(self, data):
                self.data = data
            
            def generate_signal(self):
                if self.data is None:
                    return 0
                
                try:
                    # 调用指标函数
                    result = self.func(self.data, **self.params)
                    
                    # 简化处理：取最后一个值作为信号
                    if isinstance(result, (pd.Series, np.ndarray, list)):
                        if len(result) > 0:
                            return float(result[-1])
                        else:
                            return 0
                    elif isinstance(result, (int, float, np.number)):
                        return float(result)
                    else:
                        return 0
                        
                except Exception as e:
                    logger.error(f"指标计算失败: {e}")
                    return 0
        
        # 创建伪策略实例
        workspace_strategy = IndicatorStrategy(indicator_function, self.indicator_params)
        
        super().__init__(
            workspace_strategy_instance=workspace_strategy,
            adapter_config={'indicator_type': 'tradingview'},
            strategy_name=f"TV_{indicator_name}"
        )
        
        # 更新参数
        self.params.update(self.indicator_params)
    
    def _convert_signal_format(self, workspace_signal: Any) -> Dict[str, Any]:
        """
        专门处理TradingView指标信号
        
        Args:
            workspace_signal: 指标输出值
            
        Returns:
            统一格式信号
        """
        signal_value = float(workspace_signal) if workspace_signal is not None else 0.0
        
        # TradingView指标通常输出数值，需要转换为交易信号
        # 这里使用简单的阈值规则
        signal = {
            'signal_type': 'hold',
            'confidence': 0.5,
            'indicator_value': signal_value,
            'indicator_name': self.indicator_name,
            'reason': f'TradingView指标: {self.indicator_name} = {signal_value:.4f}'
        }
        
        # 简单阈值规则（可根据指标类型调整）
        if signal_value > 0.5:
            signal['signal_type'] = 'buy'
            signal['confidence'] = min(abs(signal_value), 1.0)
        elif signal_value < -0.5:
            signal['signal_type'] = 'sell'
            signal['confidence'] = min(abs(signal_value), 1.0)
        
        return signal


class StrategyAdapterFactory:
    """
    策略适配器工厂
    自动检测和创建适配器
    """
    
    @staticmethod
    def create_adapter(workspace_strategy: Any, 
                      adapter_type: str = 'auto',
                      **kwargs) -> WorkspaceStrategyAdapter:
        """
        创建策略适配器
        
        Args:
            workspace_strategy: workspace策略（函数、类实例、模块等）
            adapter_type: 适配器类型，'auto'为自动检测
            **kwargs: 适配器参数
            
        Returns:
            策略适配器实例
        """
        logger.info(f"创建策略适配器，类型: {adapter_type}")
        
        if adapter_type == 'auto':
            # 自动检测策略类型
            adapter_type = StrategyAdapterFactory._detect_strategy_type(workspace_strategy)
            logger.info(f"自动检测到策略类型: {adapter_type}")
        
        # 根据类型创建适配器
        if adapter_type == 'tradingview_indicator':
            # TradingView指标
            indicator_name = kwargs.get('indicator_name', 'unknown_indicator')
            indicator_params = kwargs.get('indicator_params', {})
            
            return TradingViewIndicatorAdapter(
                indicator_function=workspace_strategy,
                indicator_name=indicator_name,
                indicator_params=indicator_params
            )
            
        elif adapter_type == 'python_class':
            # Python类策略
            strategy_name = kwargs.get('strategy_name', None)
            adapter_config = kwargs.get('adapter_config', {})
            
            return WorkspaceStrategyAdapter(
                workspace_strategy_instance=workspace_strategy,
                adapter_config=adapter_config,
                strategy_name=strategy_name
            )
            
        elif adapter_type == 'python_function':
            # Python函数策略，包装为类
            class FunctionWrapper:
                def __init__(self, func, func_params=None):
                    self.func = func
                    self.func_params = func_params or {}
                    self.data = None
                
                def process_data(self, data):
                    self.data = data
                
                def generate_signal(self):
                    if self.data is not None:
                        try:
                            return self.func(self.data, **self.func_params)
                        except Exception as e:
                            logger.error(f"函数策略执行失败: {e}")
                            return 0
                    return 0
            
            wrapper = FunctionWrapper(workspace_strategy, kwargs.get('func_params', {}))
            
            return WorkspaceStrategyAdapter(
                workspace_strategy_instance=wrapper,
                adapter_config={'type': 'function_wrapper'},
                strategy_name=kwargs.get('strategy_name', f"func_{workspace_strategy.__name__}")
            )
            
        else:
            # 默认适配器
            logger.warning(f"未知适配器类型: {adapter_type}，使用默认适配器")
            
            return WorkspaceStrategyAdapter(
                workspace_strategy_instance=workspace_strategy,
                adapter_config={'detected_type': adapter_type},
                strategy_name=kwargs.get('strategy_name', 'unknown_strategy')
            )
    
    @staticmethod
    def _detect_strategy_type(strategy_obj: Any) -> str:
        """自动检测策略类型"""
        
        # 检查是否为函数
        if callable(strategy_obj) and not isinstance(strategy_obj, type):
            # 检查函数名是否包含tradingview相关关键词
            func_name = getattr(strategy_obj, '__name__', '').lower()
            tv_keywords = ['tradingview', 'tv_', '_tv', 'indicator', 'ta_', '_ta']
            
            if any(keyword in func_name for keyword in tv_keywords):
                return 'tradingview_indicator'
            else:
                return 'python_function'
        
        # 检查是否为类实例
        elif hasattr(strategy_obj, '__class__'):
            class_name = strategy_obj.__class__.__name__.lower()
            module_name = getattr(strategy_obj.__class__, '__module__', '').lower()
            
            # 检查类名或模块名
            tv_keywords = ['tradingview', 'indicator', 'ta']
            if any(keyword in class_name or keyword in module_name for keyword in tv_keywords):
                return 'tradingview_indicator'
            else:
                return 'python_class'
        
        # 检查是否为类
        elif isinstance(strategy_obj, type):
            return 'python_class'
        
        # 默认类型
        else:
            return 'unknown'


def load_tradingview_indicator(indicator_path: str) -> Optional[Callable]:
    """
    加载TradingView指标
    
    Args:
        indicator_path: 指标文件路径
        
    Returns:
        指标函数，失败返回None
    """
    try:
        # 将路径转换为模块路径
        indicator_path = Path(indicator_path)
        
        if not indicator_path.exists():
            logger.error(f"指标文件不存在: {indicator_path}")
            return None
        
        # 动态导入模块
        module_name = indicator_path.stem
        spec = importlib.util.spec_from_file_location(module_name, indicator_path)
        module = importlib.util.module_from_spec(spec)
        
        # 添加路径
        sys.path.insert(0, str(indicator_path.parent))
        
        # 执行模块
        spec.loader.exec_module(module)
        
        # 查找指标函数
        # TradingView指标通常有main函数或与文件名相同的函数
        indicator_func = None
        
        # 尝试获取main函数
        if hasattr(module, 'main'):
            indicator_func = module.main
        # 尝试获取与模块名相同的函数
        elif hasattr(module, module_name):
            indicator_func = getattr(module, module_name)
        # 尝试查找第一个可调用对象
        else:
            for attr_name in dir(module):
                if not attr_name.startswith('_'):
                    attr = getattr(module, attr_name)
                    if callable(attr) and not isinstance(attr, type):
                        indicator_func = attr
                        break
        
        if indicator_func is None:
            logger.error(f"在模块 {indicator_path} 中未找到指标函数")
            return None
        
        logger.info(f"TradingView指标加载成功: {indicator_path} -> {indicator_func.__name__}")
        return indicator_func
        
    except Exception as e:
        logger.error(f"加载TradingView指标失败 {indicator_path}: {e}")
        return None


def scan_workspace_strategies(workspace_root: str = "/Users/chengming/.openclaw/workspace") -> List[Dict[str, Any]]:
    """
    扫描workspace策略
    
    Args:
        workspace_root: workspace根目录
        
    Returns:
        策略信息列表
    """
    strategies_info = []
    
    # TradingView指标目录
    tv_directories = [
        'tradingview_indicators',
        'tradingview_100_indicators',
        'tradingview_math_indicators',
        'tradingview_composite_indicators'
    ]
    
    for tv_dir in tv_directories:
        tv_path = Path(workspace_root) / tv_dir
        if tv_path.exists() and tv_path.is_dir():
            logger.info(f"扫描TradingView指标目录: {tv_path}")
            
            # 扫描Python文件
            for py_file in tv_path.glob("*.py"):
                try:
                    indicator_func = load_tradingview_indicator(str(py_file))
                    if indicator_func:
                        strategies_info.append({
                            'type': 'tradingview_indicator',
                            'name': py_file.stem,
                            'file_path': str(py_file),
                            'function': indicator_func,
                            'category': tv_dir
                        })
                except Exception as e:
                    logger.error(f"扫描指标文件失败 {py_file}: {e}")
    
    logger.info(f"扫描完成，找到 {len(strategies_info)} 个策略")
    return strategies_info


if __name__ == "__main__":
    """策略适配器测试"""
    import sys
    import os
    
    # 添加路径
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # 测试策略适配器
    print("测试策略适配器...")
    
    # 测试1: 创建简单函数策略适配器
    def simple_signal_generator(data):
        """简单信号生成函数"""
        if len(data) > 0:
            latest_close = data['close'].iloc[-1]
            if latest_close > 100:
                return 1.0  # 买入信号
            elif latest_close < 90:
                return -1.0  # 卖出信号
        return 0.0  # 持有
    
    adapter1 = StrategyAdapterFactory.create_adapter(
        simple_signal_generator,
        adapter_type='python_function',
        strategy_name='simple_signal'
    )
    
    print(f"适配器1创建成功: {adapter1.name}")
    print(f"适配器1参数: {adapter1.params}")
    
    # 测试2: 扫描workspace策略
    strategies = scan_workspace_strategies()
    print(f"扫描到 {len(strategies)} 个策略")
    
    if strategies:
        for i, strategy in enumerate(strategies[:3]):  # 显示前3个
            print(f"策略{i+1}: {strategy['name']} ({strategy['type']})")
    
    print("策略适配器测试完成!")