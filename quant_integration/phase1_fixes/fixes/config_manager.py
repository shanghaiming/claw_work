#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置管理器 - 统一管理quant_trade-main项目的配置
支持多种配置源：配置文件、环境变量、命令行参数、默认值
"""

import os
import json
import argparse
from typing import Dict, Any, Optional, Union
from pathlib import Path
import sys

# 可选导入yaml
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("警告: PyYAML未安装，YAML配置文件支持已禁用")
    print("安装: pip install pyyaml")


class ConfigManager:
    """
    配置管理器
    
    配置优先级（从高到低）：
    1. 命令行参数
    2. 环境变量
    3. 配置文件
    4. 默认值
    """
    
    # 默认配置
    DEFAULT_CONFIG = {
        "data": {
            "base_dir": "./data",  # 数据基础目录
            "analyzed_subdir": "analyzed",  # 分析数据子目录
            "timeframe": "5min",  # 默认时间周期
            "cache_enabled": True,  # 是否启用缓存
            "cache_dir": "./cache",  # 缓存目录
        },
        "backtest": {
            "initial_cash": 1000000.0,  # 初始资金
            "commission": 0.0003,  # 佣金率
            "slippage": 0.0001,  # 滑点
        },
        "paths": {
            # 平台无关的默认路径
            "default_data_path": "{base_dir}/{analyzed_subdir}/{timeframe}",
            "example_data_path": "./example_data",
        },
        "logging": {
            "level": "INFO",
            "file": "./logs/backtest.log",
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        }
    }
    
    # 环境变量映射
    ENV_VAR_MAPPING = {
        "QUANT_DATA_DIR": ("data.base_dir", str),
        "QUANT_TIMEFRAME": ("data.timeframe", str),
        "QUANT_INITIAL_CASH": ("backtest.initial_cash", float),
        "QUANT_COMMISSION": ("backtest.commission", float),
        "QUANT_LOG_LEVEL": ("logging.level", str),
    }
    
    def __init__(self, config_file: Optional[str] = None, 
                 env_prefix: str = "QUANT"):
        """
        初始化配置管理器
        
        参数:
            config_file: 配置文件路径（JSON或YAML）
            env_prefix: 环境变量前缀
        """
        self.config = self.DEFAULT_CONFIG.copy()
        self.env_prefix = env_prefix
        
        # 加载配置文件
        if config_file and os.path.exists(config_file):
            self.load_config_file(config_file)
        
        # 应用环境变量
        self.apply_environment_variables()
        
        # 确保路径存在
        self.ensure_directories()
    
    def load_config_file(self, config_file: str):
        """加载配置文件（JSON或YAML）"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                if config_file.endswith('.json'):
                    file_config = json.load(f)
                elif config_file.endswith('.yaml') or config_file.endswith('.yml'):
                    if YAML_AVAILABLE:
                        file_config = yaml.safe_load(f)
                    else:
                        raise ImportError("PyYAML未安装，无法加载YAML配置文件")
                else:
                    raise ValueError(f"不支持的配置文件格式: {config_file}")
            
            # 深度合并配置
            self._deep_merge(self.config, file_config)
            print(f"已加载配置文件: {config_file}")
            
        except ImportError as e:
            print(f"警告: {e}")
            print(f"跳过配置文件 {config_file}")
        except Exception as e:
            print(f"警告: 加载配置文件 {config_file} 失败: {e}")
    
    def apply_environment_variables(self):
        """应用环境变量到配置"""
        for env_var, (config_path, type_converter) in self.ENV_VAR_MAPPING.items():
            env_value = os.environ.get(env_var)
            if env_value is not None:
                try:
                    # 类型转换
                    if type_converter == bool:
                        # 布尔值特殊处理
                        converted_value = env_value.lower() in ('true', '1', 'yes', 'y')
                    else:
                        converted_value = type_converter(env_value)
                    
                    # 设置配置值
                    self.set_config_value(config_path, converted_value)
                    print(f"环境变量 {env_var}={env_value} 应用到 {config_path}")
                    
                except (ValueError, TypeError) as e:
                    print(f"警告: 环境变量 {env_var} 值 '{env_value}' 转换失败: {e}")
    
    def set_config_value(self, config_path: str, value: Any):
        """
        设置配置值（支持点分隔路径）
        
        示例:
            set_config_value("data.base_dir", "./new_data")
            set_config_value("backtest.initial_cash", 2000000)
        """
        path_parts = config_path.split('.')
        current = self.config
        
        # 导航到父节点
        for part in path_parts[:-1]:
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # 设置值
        current[path_parts[-1]] = value
    
    def get_config_value(self, config_path: str, default: Any = None) -> Any:
        """
        获取配置值（支持点分隔路径）
        
        示例:
            get_config_value("data.base_dir") -> "./data"
            get_config_value("backtest.initial_cash") -> 1000000.0
        """
        path_parts = config_path.split('.')
        current = self.config
        
        try:
            for part in path_parts:
                current = current[part]
            return current
        except (KeyError, TypeError):
            return default
    
    def ensure_directories(self):
        """确保必要的目录存在"""
        directories = [
            self.get_data_directory(),
            self.get_config_value("data.cache_dir"),
            os.path.dirname(self.get_config_value("logging.file")),
        ]
        
        for directory in directories:
            if directory:
                os.makedirs(directory, exist_ok=True)
    
    def get_data_directory(self, timeframe: Optional[str] = None) -> str:
        """
        获取数据目录路径
        
        参数:
            timeframe: 时间周期（如 "5min", "30min"），如果为None则使用配置值
        
        返回:
            完整的数据目录路径
        """
        if timeframe is None:
            timeframe = self.get_config_value("data.timeframe")
        
        base_dir = self.get_config_value("data.base_dir")
        analyzed_subdir = self.get_config_value("data.analyzed_subdir")
        
        # 构造路径（平台无关）
        data_dir = os.path.join(base_dir, analyzed_subdir, timeframe)
        
        # 展开用户目录（如 ~/ 开头）
        data_dir = os.path.expanduser(data_dir)
        
        # 转换为绝对路径
        data_dir = os.path.abspath(data_dir)
        
        return data_dir
    
    def create_arg_parser(self) -> argparse.ArgumentParser:
        """创建命令行参数解析器"""
        parser = argparse.ArgumentParser(
            description='量化交易回测系统 - 配置参数',
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        
        # 数据相关参数
        parser.add_argument(
            '--data-dir',
            type=str,
            help=f'数据基础目录 (默认: {self.get_config_value("data.base_dir")})'
        )
        
        parser.add_argument(
            '--timeframe',
            type=str,
            choices=['1min', '5min', '15min', '30min', '60min', 'daily'],
            help=f'数据时间周期 (默认: {self.get_config_value("data.timeframe")})'
        )
        
        # 回测相关参数
        parser.add_argument(
            '--initial-cash',
            type=float,
            help=f'初始资金 (默认: {self.get_config_value("backtest.initial_cash"):,.2f})'
        )
        
        parser.add_argument(
            '--commission',
            type=float,
            help=f'交易佣金率 (默认: {self.get_config_value("backtest.commission")})'
        )
        
        parser.add_argument(
            '--config-file',
            type=str,
            help='配置文件路径 (JSON或YAML)'
        )
        
        # 策略选择参数（与原始main.py兼容）
        parser.add_argument(
            '--strategy',
            type=str,
            default='MovingAverage',
            choices=['MovingAverage'],
            help='选择回测策略（默认: MovingAverage）'
        )
        
        parser.add_argument(
            '--strategy-params',
            type=str,
            default='{}',
            help='策略参数，JSON格式（例如：\'{"short_window":5, "long_window":20}\')'
        )
        
        parser.add_argument(
            '--refresh',
            action='store_true',
            help='全量更新模式：强制重新预处理数据并训练模型'
        )
        
        return parser
    
    def apply_command_line_args(self, args: argparse.Namespace):
        """应用命令行参数到配置"""
        # 数据相关
        if args.data_dir:
            self.set_config_value("data.base_dir", args.data_dir)
        
        if args.timeframe:
            self.set_config_value("data.timeframe", args.timeframe)
        
        # 回测相关
        if args.initial_cash:
            self.set_config_value("backtest.initial_cash", args.initial_cash)
        
        if args.commission:
            self.set_config_value("backtest.commission", args.commission)
        
        # 重新确保目录存在（因为路径可能已更改）
        self.ensure_directories()
    
    def save_config(self, file_path: str, format: str = 'json'):
        """保存配置到文件"""
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if format == 'json':
                    json.dump(self.config, f, indent=2, ensure_ascii=False)
                elif format in ['yaml', 'yml']:
                    if YAML_AVAILABLE:
                        yaml.dump(self.config, f, default_flow_style=False, allow_unicode=True)
                    else:
                        raise ImportError("PyYAML未安装，无法保存YAML配置文件")
                else:
                    raise ValueError(f"不支持的格式: {format}")
            
            print(f"配置已保存到: {file_path}")
            
        except ImportError as e:
            print(f"警告: {e}")
            print(f"使用JSON格式保存配置")
            # 回退到JSON格式
            json_file_path = file_path.replace('.yaml', '.json').replace('.yml', '.json')
            self.save_config(json_file_path, 'json')
        except Exception as e:
            print(f"保存配置失败: {e}")
    
    def print_summary(self):
        """打印配置摘要"""
        print("\n" + "="*60)
        print("配置摘要")
        print("="*60)
        
        print(f"\n📁 数据配置:")
        print(f"  数据目录: {self.get_data_directory()}")
        print(f"  时间周期: {self.get_config_value('data.timeframe')}")
        print(f"  缓存启用: {self.get_config_value('data.cache_enabled')}")
        
        print(f"\n💰 回测配置:")
        print(f"  初始资金: {self.get_config_value('backtest.initial_cash'):,.2f}")
        print(f"  佣金率: {self.get_config_value('backtest.commission'):.4f}")
        print(f"  滑点: {self.get_config_value('backtest.slippage'):.4f}")
        
        print(f"\n📊 日志配置:")
        print(f"  日志级别: {self.get_config_value('logging.level')}")
        print(f"  日志文件: {self.get_config_value('logging.file')}")
        
        # 检查数据目录是否存在
        data_dir = self.get_data_directory()
        if os.path.exists(data_dir):
            csv_files = [f for f in os.listdir(data_dir) if f.endswith('.csv')]
            print(f"\n📈 数据目录状态:")
            print(f"  目录存在: 是")
            print(f"  CSV文件数: {len(csv_files)}")
            if csv_files:
                print(f"  示例文件: {csv_files[:3]}{'...' if len(csv_files) > 3 else ''}")
        else:
            print(f"\n⚠️  数据目录状态:")
            print(f"  目录存在: 否")
            print(f"  请创建目录或通过 --data-dir 参数指定数据目录")
        
        print("\n" + "="*60)
    
    def _deep_merge(self, target: Dict, source: Dict):
        """深度合并字典（递归合并嵌套字典）"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value


# 单例实例
_config_instance = None

def get_config(config_file: Optional[str] = None) -> ConfigManager:
    """获取配置管理器实例（单例模式）"""
    global _config_instance
    if _config_instance is None:
        _config_instance = ConfigManager(config_file)
    return _config_instance


if __name__ == "__main__":
    # 测试配置管理器
    config = ConfigManager()
    config.print_summary()
    
    # 测试命令行参数解析
    parser = config.create_arg_parser()
    test_args = parser.parse_args([])
    print(f"\n命令行参数解析测试: {test_args}")