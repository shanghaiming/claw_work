#!/usr/bin/env python3
"""
TA-Lib全面指标探索器

功能:
1. 探索TA-Lib所有可用指标函数
2. 分类整理指标（趋势、动量、波动率、成交量等）
3. 为每个指标生成参数说明和使用示例
4. 创建指标组合模板
5. 生成指标探索报告
"""

import talib
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Callable
import inspect
import json
import warnings
from datetime import datetime
warnings.filterwarnings('ignore')

print("=" * 80)
print("📊 TA-Lib全面指标探索器")
print(f"TA-Lib版本: {talib.__version__}")
print("=" * 80)

class TALibComprehensiveExplorer:
    """TA-Lib全面指标探索器"""
    
    def __init__(self):
        self.all_functions = self._get_all_talib_functions()
        self.function_categories = self._categorize_functions()
        self.function_details = self._extract_function_details()
        
    def _get_all_talib_functions(self) -> List[str]:
        """获取所有TA-Lib函数"""
        functions = []
        for name in dir(talib):
            if not name.startswith('_') and callable(getattr(talib, name)):
                functions.append(name)
        return functions
    
    def _categorize_functions(self) -> Dict[str, List[str]]:
        """将函数按类别分类"""
        categories = {
            '趋势指标': [],
            '动量指标': [],
            '波动率指标': [],
            '成交量指标': [],
            '周期指标': [],
            '数学变换': [],
            '模式识别': [],
            '统计指标': [],
            '其他指标': []
        }
        
        # 关键词映射
        keyword_mapping = {
            '趋势指标': ['MA', 'EMA', 'SMA', 'WMA', 'TRIMA', 'DEMA', 'TEMA', 'HT_TRENDLINE', 
                       'SAR', 'SAREXT', 'ADX', 'ADXR', 'APO', 'AROON', 'AROONOSC', 
                       'CCI', 'DX', 'MACD', 'MACDEXT', 'MACDFIX', 'MFI', 'MINUS_DI', 
                       'MINUS_DM', 'MOM', 'PLUS_DI', 'PLUS_DM', 'ROC', 'ROCP', 'ROCR', 
                       'ROCR100', 'RSI', 'STOCH', 'STOCHF', 'STOCHRSI', 'TRIX', 'ULTOSC',
                       'WILLR', 'BOP', 'CMO', 'PPO', 'T3'],
            '动量指标': ['MOM', 'ROC', 'ROCP', 'ROCR', 'ROCR100', 'RSI', 'STOCH', 'STOCHF',
                       'STOCHRSI', 'WILLR', 'CMO', 'PPO', 'TRIX', 'ULTOSC', 'ADX', 'ADXR',
                       'AROON', 'AROONOSC', 'CCI', 'DX', 'MACD', 'MACDEXT', 'MACDFIX'],
            '波动率指标': ['ATR', 'NATR', 'TRANGE', 'BBANDS', 'DEMA', 'TEMA', 'HT_TRENDLINE',
                        'KAMA', 'MAMA', 'FAMA', 'T3', 'MIDPOINT', 'MIDPRICE', 'SAR', 'SAREXT',
                        'STDDEV', 'VAR'],
            '成交量指标': ['AD', 'ADOSC', 'OBV', 'VOLUME_PROFILE', 'VWAP'],
            '周期指标': ['HT_DCPERIOD', 'HT_DCPHASE', 'HT_PHASOR', 'HT_SINE', 'HT_TRENDMODE'],
            '数学变换': ['ACOS', 'ASIN', 'ATAN', 'CEIL', 'COS', 'COSH', 'EXP', 'FLOOR', 'LN', 
                       'LOG10', 'SIN', 'SINH', 'SQRT', 'TAN', 'TANH'],
            '模式识别': ['CDL2CROWS', 'CDL3BLACKCROWS', 'CDL3INSIDE', 'CDL3LINESTRIKE', 
                       'CDL3OUTSIDE', 'CDL3STARSINSOUTH', 'CDL3WHITESOLDIERS', 
                       'CDLABANDONEDBABY', 'CDLADVANCEBLOCK', 'CDLBELTHOLD', 
                       'CDLBREAKAWAY', 'CDLCLOSINGMARUBOZU', 'CDLCONCEALBABYSWALL', 
                       'CDLCOUNTERATTACK', 'CDLDARKCLOUDCOVER', 'CDLDOJI', 
                       'CDLDOJISTAR', 'CDLDRAGONFLYDOJI', 'CDLENGULFING', 
                       'CDLEVENINGDOJISTAR', 'CDLEVENINGSTAR', 'CDLGAPSIDESIDEWHITE', 
                       'CDLGRAVESTONEDOJI', 'CDLHAMMER', 'CDLHANGINGMAN', 
                       'CDLHARAMI', 'CDLHARAMICROSS', 'CDLHIGHWAVE', 'CDLHIKKAKE', 
                       'CDLHIKKAKEMOD', 'CDLHOMINGPIGEON', 'CDLIDENTICAL3CROWS', 
                       'CDLINNECK', 'CDLINVERTEDHAMMER', 'CDLKICKING', 
                       'CDLKICKINGBYLENGTH', 'CDLLADDERBOTTOM', 'CDLLONGLEGGEDDOJI', 
                       'CDLLONGLINE', 'CDLMARUBOZU', 'CDLMATCHINGLOW', 'CDLMATHOLD', 
                       'CDLMORNINGDOJISTAR', 'CDLMORNINGSTAR', 'CDLONNECK', 
                       'CDLPIERCING', 'CDLRICKSHAWMAN', 'CDLRISEFALL3METHODS', 
                       'CDLSEPARATINGLINES', 'CDLSHOOTINGSTAR', 'CDLSHORTLINE', 
                       'CDLSPINNINGTOP', 'CDLSTALLEDPATTERN', 'CDLSTICKSANDWICH', 
                       'CDLTAKURI', 'CDLTASUKIGAP', 'CDLTHRUSTING', 'CDLTRISTAR', 
                       'CDLUNIQUE3RIVER', 'CDLUPSIDEGAP2CROWS', 'CDLXSIDEGAP3METHODS'],
            '统计指标': ['BETA', 'CORREL', 'LINEARREG', 'LINEARREG_ANGLE', 'LINEARREG_INTERCEPT',
                       'LINEARREG_SLOPE', 'STDDEV', 'TSF', 'VAR']
        }
        
        for func_name in self.all_functions:
            matched = False
            for category, keywords in keyword_mapping.items():
                for keyword in keywords:
                    if keyword in func_name:
                        categories[category].append(func_name)
                        matched = True
                        break
                if matched:
                    break
            
            if not matched:
                categories['其他指标'].append(func_name)
        
        return categories
    
    def _extract_function_details(self) -> Dict[str, Dict[str, Any]]:
        """提取函数详细信息"""
        details = {}
        
        for func_name in self.all_functions:
            try:
                func = getattr(talib, func_name)
                sig = inspect.signature(func)
                
                params = []
                for param_name, param in sig.parameters.items():
                    if param_name == 'self':
                        continue
                    
                    param_info = {
                        'name': param_name,
                        'type': str(param.annotation) if param.annotation != inspect.Parameter.empty else 'any',
                        'default': param.default if param.default != inspect.Parameter.empty else None,
                        'kind': str(param.kind)
                    }
                    params.append(param_info)
                
                # 获取函数文档字符串
                doc = inspect.getdoc(func) or "暂无文档"
                
                details[func_name] = {
                    'name': func_name,
                    'doc': doc[:200] + '...' if len(doc) > 200 else doc,
                    'parameters': params,
                    'parameter_count': len(params)
                }
                
            except Exception as e:
                details[func_name] = {
                    'name': func_name,
                    'error': str(e),
                    'parameters': [],
                    'parameter_count': 0
                }
        
        return details
    
    def get_function_count_by_category(self) -> Dict[str, int]:
        """获取各类别函数数量"""
        return {category: len(funcs) for category, funcs in self.function_categories.items()}
    
    def generate_comprehensive_report(self) -> Dict[str, Any]:
        """生成全面探索报告"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'talib_version': talib.__version__,
            'total_functions': len(self.all_functions),
            'functions_by_category': self.get_function_count_by_category(),
            'category_details': {},
            'parameter_statistics': {
                'functions_with_parameters': {},
                'average_parameters': 0
            },
            'recommended_combinations': self._generate_recommended_combinations()
        }
        
        # 详细类别信息
        for category, funcs in self.function_categories.items():
            report['category_details'][category] = {
                'count': len(funcs),
                'functions': funcs[:20]  # 只显示前20个
            }
        
        # 参数统计
        param_counts = [self.function_details[func]['parameter_count'] for func in self.all_functions]
        report['parameter_statistics']['average_parameters'] = np.mean(param_counts) if param_counts else 0
        
        param_dist = {}
        for count in param_counts:
            param_dist[count] = param_dist.get(count, 0) + 1
        report['parameter_statistics']['parameter_distribution'] = param_dist
        
        return report
    
    def _generate_recommended_combinations(self) -> List[Dict[str, Any]]:
        """生成推荐的指标组合"""
        combinations = [
            {
                'name': '趋势跟踪组合',
                'description': '适用于趋势市场',
                'indicators': ['EMA', 'MACD', 'ADX', 'ATR'],
                'usage': 'EMA判断趋势方向，MACD确认趋势强度，ADX衡量趋势力度，ATR用于风险管理'
            },
            {
                'name': '均值回归组合',
                'description': '适用于震荡市场',
                'indicators': ['BBANDS', 'RSI', 'STOCH', 'MFI'],
                'usage': '布林带识别超买超卖，RSI和随机指标确认信号，MFI验证成交量'
            },
            {
                'name': '突破交易组合',
                'description': '适用于突破行情',
                'indicators': ['SAR', 'AROON', 'CCI', 'VOLUME'],
                'usage': '抛物线转向识别突破点，AROON衡量趋势强度，CCI判断超买超卖，成交量确认突破'
            },
            {
                'name': '动量策略组合',
                'description': '适用于动量交易',
                'indicators': ['MOM', 'ROC', 'TRIX', 'WILLR'],
                'usage': '多个动量指标确认动量方向，避免假信号'
            },
            {
                'name': '多时间框架组合',
                'description': '多时间框架分析',
                'indicators': ['HT_TRENDLINE', 'HT_DCPERIOD', 'HT_PHASOR', 'HT_SINE'],
                'usage': '希尔伯特变换指标进行多时间框架分析'
            }
        ]
        return combinations
    
    def create_indicator_template(self, indicator_name: str) -> str:
        """为指定指标创建使用模板"""
        if indicator_name not in self.function_details:
            return f"指标 {indicator_name} 未找到"
        
        details = self.function_details[indicator_name]
        
        template = f'''# {indicator_name} 指标使用模板

## 功能描述
{details['doc']}

## 参数说明
'''
        
        for param in details['parameters']:
            default_str = f" (默认: {param['default']})" if param['default'] is not None else ""
            template += f"- **{param['name']}**: 类型 {param['type']}{default_str}\n"
        
        template += f'''
## 使用示例
```python
import talib
import numpy as np

# 准备数据
close_prices = np.random.random(100) * 100  # 示例收盘价数据

# 使用 {indicator_name}
try:
    # 根据参数数量调用指标
    result = talib.{indicator_name}(close_prices)
    print(f"{indicator_name} 结果: {{result}}")
except Exception as e:
    print(f"计算 {indicator_name} 时出错: {{e}}")

# 实际应用中需要根据指标要求提供正确的参数
# 大多数指标需要OHLC数据，而不仅仅是收盘价
'''
        
        return template
    
    def generate_all_templates(self) -> Dict[str, str]:
        """为所有指标生成模板"""
        templates = {}
        for func_name in self.all_functions[:50]:  # 限制数量，避免太大
            templates[func_name] = self.create_indicator_template(func_name)
        return templates
    
    def save_report_to_file(self, filename: str = "talib_comprehensive_report.json"):
        """保存报告到文件"""
        report = self.generate_comprehensive_report()
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 报告已保存到: {filename}")
        
        # 同时保存简要摘要
        summary_file = filename.replace('.json', '_summary.txt')
        with open(summary_file, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("TA-Lib全面指标探索报告摘要\n")
            f.write("=" * 80 + "\n\n")
            f.write(f"生成时间: {report['generated_at']}\n")
            f.write(f"TA-Lib版本: {report['talib_version']}\n")
            f.write(f"总指标数量: {report['total_functions']}\n\n")
            
            f.write("各类别指标数量:\n")
            for category, count in report['functions_by_category'].items():
                f.write(f"  {category}: {count}个\n")
            
            f.write(f"\n平均参数数量: {report['parameter_statistics']['average_parameters']:.1f}\n")
            
            f.write("\n推荐的指标组合:\n")
            for i, combo in enumerate(report['recommended_combinations'], 1):
                f.write(f"{i}. {combo['name']}: {combo['description']}\n")
                f.write(f"   指标: {', '.join(combo['indicators'])}\n")
        
        print(f"✅ 摘要已保存到: {summary_file}")
        return filename

def main():
    """主函数"""
    print("🔍 开始探索TA-Lib指标...")
    
    # 创建探索器
    explorer = TALibComprehensiveExplorer()
    
    # 显示基本信息
    print(f"📊 发现 {len(explorer.all_functions)} 个TA-Lib指标函数")
    
    # 显示类别分布
    print("\n📈 指标类别分布:")
    for category, count in explorer.get_function_count_by_category().items():
        print(f"  {category}: {count}个指标")
    
    # 生成并保存报告
    print("\n📝 生成详细报告...")
    report_file = explorer.save_report_to_file()
    
    # 为常用指标生成模板
    print("\n📋 为常用指标生成使用模板...")
    common_indicators = ['EMA', 'RSI', 'MACD', 'BBANDS', 'ATR', 'ADX', 'STOCH', 'SAR']
    for indicator in common_indicators:
        if indicator in explorer.all_functions:
            template = explorer.create_indicator_template(indicator)
            template_file = f"indicator_template_{indicator}.txt"
            with open(template_file, 'w', encoding='utf-8') as f:
                f.write(template)
            print(f"  ✅ {indicator}模板已保存到: {template_file}")
    
    print("\n" + "=" * 80)
    print("🎯 TA-Lib全面探索完成!")
    print("=" * 80)
    print("\n下一步建议:")
    print("1. 查看生成的报告: talib_comprehensive_report.json")
    print("2. 阅读指标模板文件了解具体使用方法")
    print("3. 使用indicator_combination_framework.py进行指标组合测试")
    print("4. 参考推荐组合开发交易策略")

if __name__ == "__main__":
    main()