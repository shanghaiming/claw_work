#!/usr/bin/env python3
"""
快速开始示例 - 统一量化交易分析系统

这个示例演示了如何使用统一量化交易分析系统的基本功能。
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def example_data_pipeline():
    """示例1: 数据管道"""
    print("=" * 60)
    print("示例1: 数据管道")
    print("=" * 60)
    
    try:
        from data.data_manager import UnifiedDataManager
        
        # 创建数据管理器
        config = {
            'cache_enabled': True,
            'preprocessing_enabled': False,  # 简化示例，禁用预处理
            'default_source': 'local',
            'local_data_dir': './data/example_data'
        }
        
        manager = UnifiedDataManager(config)
        
        # 获取数据
        data = manager.get_data(
            symbol='TEST001.SZ',
            start_date='20200101',
            end_date='20301231',
            source='local',
            format='csv'
        )
        
        if data is not None:
            print(f"✅ 数据获取成功!")
            print(f"   数据形状: {data.shape}")
            print(f"   列名: {list(data.columns)}")
            print(f"   时间范围: {data.index.min()} 至 {data.index.max()}")
        else:
            print("❌ 数据获取失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print()

def example_analysis_pipeline():
    """示例2: 分析管道"""
    print("=" * 60)
    print("示例2: 分析管道")
    print("=" * 60)
    
    try:
        # 首先获取数据
        from data.data_manager import UnifiedDataManager
        
        data_config = {
            'cache_enabled': True,
            'preprocessing_enabled': False,
            'default_source': 'local',
            'local_data_dir': './data/example_data'
        }
        
        data_manager = UnifiedDataManager(data_config)
        data = data_manager.get_data('TEST001.SZ', '20200101', '20301231')
        
        if data is None:
            print("❌ 数据获取失败，跳过分析示例")
            return
        
        # 现在进行分析
        from analysis.analysis_manager import UnifiedAnalysisManager
        
        analysis_config = {
            'enable_price_action': True,
            'enable_technical': True,
            'enable_signal': True,
            'result_integration': 'weighted'
        }
        
        analysis_manager = UnifiedAnalysisManager(analysis_config)
        results = analysis_manager.analyze(data)
        
        if results:
            print(f"✅ 分析完成!")
            print(f"   总信号数: {results.get('total_signals', 0)}")
            print(f"   共识信号: {results.get('consensus_signals', 0)}")
            
            # 显示前3个信号
            signals = results.get('consensus_signals_list', [])
            if signals:
                print(f"   高质量信号示例:")
                for i, signal in enumerate(signals[:3]):
                    print(f"     {i+1}. {signal.get('type')} - {signal.get('reason')} "
                          f"(置信度: {signal.get('confidence', 0):.2%})")
        else:
            print("❌ 分析失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print()

def example_strategy_pipeline():
    """示例3: 策略管道"""
    print("=" * 60)
    print("示例3: 策略管道")
    print("=" * 60)
    
    try:
        from strategies.strategy_integration import StrategyExecutionPipeline
        
        config = {
            'data_config': {
                'cache_enabled': True,
                'local_data_dir': './data/example_data'
            },
            'analysis_config': {
                'enable_price_action': True,
                'enable_technical': True
            },
            'strategy_config': {
                'strategy_names': ['MovingAverageAdapter']
            }
        }
        
        pipeline = StrategyExecutionPipeline(config)
        
        # 执行管道
        results = pipeline.execute_pipeline(
            symbols=['TEST001.SZ'],
            start_date='20200101',
            end_date='20301231',
            strategy_names=['MovingAverageAdapter']
        )
        
        if results:
            print(f"✅ 策略管道执行完成!")
            print(f"   总信号: {results.get('total_signals', 0)}")
            print(f"   可用策略: {results.get('available_strategies', [])}")
            
            # 显示管道状态
            status = pipeline.get_pipeline_status()
            print(f"   管道状态: {status.get('status', 'unknown')}")
            print(f"   处理时间: {status.get('processing_time', 0):.2f}秒")
        else:
            print("❌ 策略管道执行失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print()

def example_reporting_pipeline():
    """示例4: 报告管道"""
    print("=" * 60)
    print("示例4: 报告管道")
    print("=" * 60)
    
    try:
        # 创建示例数据
        import pandas as pd
        import numpy as np
        from datetime import datetime
        
        # 生成示例绩效数据
        np.random.seed(42)
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        returns = np.random.randn(100) * 0.01
        cumulative_returns = (1 + returns).cumprod() - 1
        drawdown = cumulative_returns - cumulative_returns.expanding().max()
        
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
                'total_trades': 125
            },
            'returns': {
                'returns_series': pd.Series(returns, index=dates),
                'cumulative_returns': cumulative_returns,
                'drawdown': drawdown
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
        
        # 生成报告
        from reporting.report_generator import ReportGenerator
        
        report_config = {
            'output_dir': './example_reports',
            'default_format': 'markdown',
            'language': 'zh-CN'
        }
        
        generator = ReportGenerator(report_config)
        
        # 生成摘要报告
        report_path = generator.generate_report(
            report_type='summary',
            data=example_data,
            title='示例交易分析报告'
        )
        
        if report_path and os.path.exists(report_path):
            print(f"✅ 报告生成成功!")
            print(f"   报告文件: {report_path}")
            print(f"   文件大小: {os.path.getsize(report_path)} 字节")
            
            # 显示报告摘要
            with open(report_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"   报告行数: {len(lines)}")
                
                # 显示前5行
                print(f"   报告预览:")
                for i, line in enumerate(lines[:10]):
                    if line.strip():
                        print(f"     {line[:80]}..." if len(line) > 80 else f"     {line}")
        else:
            print("❌ 报告生成失败")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print()

def example_visualization_pipeline():
    """示例5: 可视化管道"""
    print("=" * 60)
    print("示例5: 可视化管道")
    print("=" * 60)
    
    try:
        # 创建示例数据
        import pandas as pd
        import numpy as np
        
        dates = pd.date_range('2024-01-01', periods=100, freq='D')
        price_data = pd.DataFrame({
            'date': dates,
            'open': np.random.randn(100).cumsum() + 100,
            'high': np.random.randn(100).cumsum() + 102,
            'low': np.random.randn(100).cumsum() + 98,
            'close': np.random.randn(100).cumsum() + 100,
            'volume': np.random.randint(1000, 10000, 100)
        })
        
        signals = [
            {
                'timestamp': dates[20],
                'type': 'buy',
                'price': price_data['close'].iloc[20],
                'reason': '示例买入信号',
                'confidence': 0.75
            },
            {
                'timestamp': dates[60],
                'type': 'sell',
                'price': price_data['close'].iloc[60],
                'reason': '示例卖出信号',
                'confidence': 0.68
            }
        ]
        
        performance_data = {
            'returns': pd.Series(np.random.randn(100) * 0.01, index=dates),
            'cumulative_returns': (1 + np.random.randn(100) * 0.01).cumprod() - 1,
            'drawdown': np.random.randn(100) * 0.02 - 0.05,
            'metrics': {
                'annual_return': 0.156,
                'sharpe_ratio': 1.24,
                'max_drawdown': -0.087
            }
        }
        
        example_data = {
            'price_data': price_data,
            'signals': signals,
            'performance': performance_data,
            'metrics': performance_data['metrics']
        }
        
        # 生成可视化
        from reporting.visualizer import TradingVisualizer
        
        visualizer_config = {
            'output_dir': './example_visualizations',
            'figure_size': (12, 8),
            'dpi': 100,
            'save_format': 'png'
        }
        
        visualizer = TradingVisualizer(visualizer_config)
        
        # 生成价格图表
        price_chart = visualizer.plot_price_with_signals(
            price_data=price_data,
            signals=signals,
            title='示例: 价格与交易信号'
        )
        
        if price_chart:
            print(f"✅ 价格图表生成成功!")
            print(f"   图表文件: {price_chart}")
            
            # 生成绩效图表
            performance_chart = visualizer.plot_performance_metrics(
                performance_data=performance_data,
                title='示例: 策略绩效分析'
            )
            
            if performance_chart:
                print(f"✅ 绩效图表生成成功!")
                print(f"   图表文件: {performance_chart}")
            else:
                print("⚠️ 绩效图表生成失败 (可能需要matplotlib)")
        else:
            print("⚠️ 价格图表生成失败 (可能需要matplotlib)")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print()

def example_full_system():
    """示例6: 完整系统"""
    print("=" * 60)
    print("示例6: 完整系统 (使用main.py)")
    print("=" * 60)
    
    try:
        import subprocess
        import sys
        
        # 检查main.py是否存在
        main_path = os.path.join(os.path.dirname(__file__), '..', 'main.py')
        if not os.path.exists(main_path):
            print("❌ main.py 不存在")
            return
        
        # 运行状态检查
        print("运行系统状态检查...")
        result = subprocess.run(
            [sys.executable, main_path, 'status'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(main_path)
        )
        
        if result.returncode == 0:
            print("✅ 系统状态检查成功!")
            
            # 显示状态摘要
            lines = result.stdout.split('\n')
            for line in lines:
                if '系统信息:' in line or '模块状态:' in line or '配置摘要:' in line:
                    print(line)
                elif '✅' in line or '❌' in line:
                    print(f"   {line}")
        else:
            print(f"❌ 系统状态检查失败: {result.stderr}")
        
        print()
        
        # 生成配置模板
        print("生成配置模板...")
        config_result = subprocess.run(
            [sys.executable, main_path, 'config', '--output', 'example_config.json'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(main_path)
        )
        
        if config_result.returncode == 0:
            print("✅ 配置模板生成成功!")
            print(f"   配置文件: {os.path.join(os.path.dirname(main_path), 'example_config.json')}")
        else:
            print(f"❌ 配置模板生成失败: {config_result.stderr}")
            
    except Exception as e:
        print(f"❌ 错误: {e}")
    
    print()

def main():
    """主函数"""
    print("\n" + "=" * 60)
    print("统一量化交易分析系统 - 快速开始示例")
    print("=" * 60)
    print()
    
    # 创建输出目录
    os.makedirs('./example_reports', exist_ok=True)
    os.makedirs('./example_visualizations', exist_ok=True)
    
    # 运行所有示例
    examples = [
        example_data_pipeline,
        example_analysis_pipeline,
        example_strategy_pipeline,
        example_reporting_pipeline,
        example_visualization_pipeline,
        example_full_system
    ]
    
    for i, example_func in enumerate(examples, 1):
        print(f"\n示例 {i}/{len(examples)}")
        example_func()
    
    print("=" * 60)
    print("所有示例完成!")
    print("=" * 60)
    
    # 显示总结
    print("\n🎯 总结:")
    print("1. 数据管道: 获取和处理市场数据")
    print("2. 分析管道: 市场分析和信号生成")
    print("3. 策略管道: 策略执行和信号处理")
    print("4. 报告管道: 生成各种格式的报告")
    print("5. 可视化管道: 创建图表和可视化")
    print("6. 完整系统: 使用main.py命令行界面")
    
    print("\n📁 生成的文件:")
    if os.path.exists('./example_reports'):
        reports = os.listdir('./example_reports')
        if reports:
            print(f"   报告文件: {len(reports)} 个文件在 example_reports/")
    
    if os.path.exists('./example_visualizations'):
        visuals = os.listdir('./example_visualizations')
        if visuals:
            print(f"   可视化文件: {len(visuals)} 个文件在 example_visualizations/")
    
    print("\n🚀 下一步:")
    print("1. 查看生成的报告和可视化文件")
    print("2. 修改 example_config.json 配置文件")
    print("3. 运行完整管道: python main.py run --help")
    print("4. 参考 docs/README.md 获取详细文档")
    
    print("\n💡 提示: 系统需要以下依赖:")
    print("   pip install pandas numpy matplotlib seaborn plotly")

if __name__ == "__main__":
    main()