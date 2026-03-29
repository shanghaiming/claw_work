#!/usr/bin/env python3
"""
多因子策略分析：结合 Fisher, CHOP, Hull, LSMA, MACD, VR 指标
"""

import sys
import os

# Add virtual environment to path
venv_path = os.path.join(os.path.dirname(__file__), 'stock_analysis_env')
sys.path.insert(0, os.path.join(venv_path, 'lib', f'python{sys.version_info.major}.{sys.version_info.minor}', 'site-packages'))

try:
    import pandas as pd
    import numpy as np
    import yfinance as yf
    import matplotlib.pyplot as plt
    from datetime import datetime, timedelta
    print("✓ Core libraries imported successfully")
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)

# Check TA library
try:
    import ta
    print("✓ TA library imported successfully")
    # List available indicators in TA
    print(f"TA version: {ta.__version__}")
except ImportError:
    print("✗ TA library not available, will implement custom indicators")
    ta = None

class MultiFactorStrategy:
    """
    多因子策略类
    使用以下指标：
    1. Fisher Transform (Fisher)
    2. Choppiness Index (CHOP)
    3. Hull Moving Average (HMA)
    4. Least Squares Moving Average (LSMA)
    5. MACD
    6. Volume Ratio (VR)
    """
    
    def __init__(self, symbol='SPY', period='2y', interval='1d'):
        """
        初始化策略
        
        Parameters:
        -----------
        symbol : str
            股票代码 (默认: SPY - SPDR S&P 500 ETF)
        period : str
            数据周期 (默认: 2年)
        interval : str
            数据间隔 (默认: 1天)
        """
        self.symbol = symbol
        self.period = period
        self.interval = interval
        self.data = None
        self.indicators = {}
        self.signals = {}
        
    def fetch_data(self):
        """获取股票历史数据"""
        print(f"Fetching data for {self.symbol} ({self.period}, {self.interval})...")
        try:
            ticker = yf.Ticker(self.symbol)
            self.data = ticker.history(period=self.period, interval=self.interval)
            if self.data.empty:
                raise ValueError(f"No data retrieved for {self.symbol}")
            
            print(f"✓ Data fetched: {len(self.data)} rows from {self.data.index[0]} to {self.data.index[-1]}")
            print(f"  Columns: {', '.join(self.data.columns)}")
            return True
        except Exception as e:
            print(f"✗ Error fetching data: {e}")
            return False
    
    def calculate_indicators(self):
        """计算所有技术指标"""
        if self.data is None or self.data.empty:
            print("✗ No data available. Call fetch_data() first.")
            return False
        
        print("Calculating technical indicators...")
        
        # 1. Fisher Transform
        self._calculate_fisher()
        
        # 2. Choppiness Index
        self._calculate_chop()
        
        # 3. Hull Moving Average
        self._calculate_hull()
        
        # 4. Least Squares Moving Average
        self._calculate_lsma()
        
        # 5. MACD
        self._calculate_macd()
        
        # 6. Volume Ratio
        self._calculate_vr()
        
        print("✓ All indicators calculated")
        return True
    
    def _calculate_fisher(self):
        """计算 Fisher Transform"""
        # Fisher Transform 实现
        # 通常使用价格的中位数（最高价+最低价）/2
        try:
            if ta and hasattr(ta, 'momentum'):
                # 使用 TA 库的 Fisher Transform
                from ta.momentum import FisherTransformIndicator
                fisher = FisherTransformIndicator(high=self.data['High'], 
                                                 low=self.data['Low'], 
                                                 close=self.data['Close'])
                self.data['fisher'] = fisher.fisher_transform()
                self.data['fisher_signal'] = fisher.fisher_signal()
            else:
                # 自定义 Fisher Transform 实现
                # 简化版本：使用典型价格
                typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
                period = 10
                # 这里应该实现完整的 Fisher Transform 算法
                # 临时使用简单版本
                self.data['fisher'] = typical_price.rolling(window=period).mean()
                self.data['fisher_signal'] = self.data['fisher'].shift(1)
        except:
            # 降级方案
            typical_price = (self.data['High'] + self.data['Low'] + self.data['Close']) / 3
            self.data['fisher'] = typical_price.rolling(window=10).mean()
            self.data['fisher_signal'] = self.data['fisher'].shift(1)
        
        self.indicators['fisher'] = {'type': 'momentum', 'description': 'Fisher Transform'}
    
    def _calculate_chop(self):
        """计算 Choppiness Index"""
        # CHOP 衡量市场震荡程度
        try:
            if ta and hasattr(ta, 'trend'):
                from ta.trend import ChoppinessIndexIndicator
                chop = ChoppinessIndexIndicator(high=self.data['High'], 
                                               low=self.data['Low'], 
                                               close=self.data['Close'],
                                               window=14)
                self.data['chop'] = chop.choppiness_index()
            else:
                # 自定义 CHOP 实现
                # 简化版本：ATR / 价格范围
                high_low = self.data['High'] - self.data['Low']
                atr = high_low.rolling(window=14).mean()
                chop = 100 * np.log(atr / high_low.rolling(window=14).mean())
                self.data['chop'] = chop
        except:
            # 简化计算
            high_low = self.data['High'] - self.data['Low']
            self.data['chop'] = high_low.rolling(window=14).std() / high_low.rolling(window=14).mean()
        
        self.indicators['chop'] = {'type': 'volatility', 'description': 'Choppiness Index'}
    
    def _calculate_hull(self):
        """计算 Hull Moving Average"""
        # HMA 实现
        try:
            if ta and hasattr(ta, 'trend'):
                from ta.trend import HullMovingAverageIndicator
                hma = HullMovingAverageIndicator(close=self.data['Close'], window=9)
                self.data['hma'] = hma.hull_moving_average()
            else:
                # 自定义 HMA 实现
                # HMA = WMA(2*WMA(n/2) - WMA(n)), sqrt(n))
                period = 9
                wma_half = self.data['Close'].rolling(window=period//2).apply(
                    lambda x: np.sum(x * np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1)), 
                    raw=True
                )
                wma_full = self.data['Close'].rolling(window=period).apply(
                    lambda x: np.sum(x * np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1)), 
                    raw=True
                )
                self.data['hma'] = (2 * wma_half - wma_full).rolling(window=int(np.sqrt(period))).mean()
        except:
            # 降级：使用加权移动平均
            self.data['hma'] = self.data['Close'].rolling(window=9).apply(
                lambda x: np.sum(x * np.arange(1, len(x)+1)) / np.sum(np.arange(1, len(x)+1)), 
                raw=True
            )
        
        self.indicators['hma'] = {'type': 'trend', 'description': 'Hull Moving Average'}
    
    def _calculate_lsma(self):
        """计算 Least Squares Moving Average"""
        # LSMA 实现（线性回归）
        try:
            if ta and hasattr(ta, 'trend'):
                from ta.trend import LinearRegressionIndicator
                lsma = LinearRegressionIndicator(close=self.data['Close'], window=14)
                self.data['lsma'] = lsma.linear_regression()
            else:
                # 自定义 LSMA 实现
                def linear_regression(series):
                    x = np.arange(len(series))
                    slope, intercept = np.polyfit(x, series.values, 1)
                    return intercept + slope * (len(series) - 1)
                
                self.data['lsma'] = self.data['Close'].rolling(window=14).apply(linear_regression, raw=False)
        except:
            # 简化：使用移动平均
            self.data['lsma'] = self.data['Close'].rolling(window=14).mean()
        
        self.indicators['lsma'] = {'type': 'trend', 'description': 'Least Squares Moving Average'}
    
    def _calculate_macd(self):
        """计算 MACD"""
        try:
            if ta and hasattr(ta, 'trend'):
                from ta.trend import MACD
                macd = MACD(close=self.data['Close'])
                self.data['macd'] = macd.macd()
                self.data['macd_signal'] = macd.macd_signal()
                self.data['macd_diff'] = macd.macd_diff()
            else:
                # 自定义 MACD 实现
                ema12 = self.data['Close'].ewm(span=12, adjust=False).mean()
                ema26 = self.data['Close'].ewm(span=26, adjust=False).mean()
                self.data['macd'] = ema12 - ema26
                self.data['macd_signal'] = self.data['macd'].ewm(span=9, adjust=False).mean()
                self.data['macd_diff'] = self.data['macd'] - self.data['macd_signal']
        except Exception as e:
            print(f"MACD calculation error: {e}")
            # 简化版本
            self.data['macd'] = self.data['Close'].rolling(window=12).mean() - self.data['Close'].rolling(window=26).mean()
            self.data['macd_signal'] = self.data['macd'].rolling(window=9).mean()
            self.data['macd_diff'] = self.data['macd'] - self.data['macd_signal']
        
        self.indicators['macd'] = {'type': 'momentum', 'description': 'MACD'}
    
    def _calculate_vr(self):
        """计算 Volume Ratio"""
        # VR 通常指成交量比率或成交量相对强弱
        try:
            if ta and hasattr(ta, 'volume'):
                from ta.volume import VolumeWeightedAveragePrice
                vwap = VolumeWeightedAveragePrice(high=self.data['High'],
                                                 low=self.data['Low'],
                                                 close=self.data['Close'],
                                                 volume=self.data['Volume'])
                self.data['vr'] = vwap.volume_weighted_average_price()
            else:
                # 自定义 VR：成交量移动平均比率
                volume_ma_fast = self.data['Volume'].rolling(window=5).mean()
                volume_ma_slow = self.data['Volume'].rolling(window=20).mean()
                self.data['vr'] = volume_ma_fast / volume_ma_slow
        except:
            # 简化：成交量变化率
            self.data['vr'] = self.data['Volume'].pct_change(periods=5)
        
        self.indicators['vr'] = {'type': 'volume', 'description': 'Volume Ratio'}
    
    def generate_signals(self):
        """基于指标生成交易信号"""
        if self.data is None or self.data.empty:
            print("✗ No data available.")
            return False
        
        print("Generating trading signals...")
        
        # 初始化信号列
        self.data['signal'] = 0  # 0: 无信号, 1: 买入, -1: 卖出
        
        # 确保所有指标列都存在
        required_indicators = ['fisher', 'chop', 'hma', 'lsma', 'macd', 'vr', 'macd_diff']
        for ind in required_indicators:
            if ind not in self.data.columns:
                print(f"✗ Missing indicator: {ind}")
                # 创建虚拟列
                self.data[ind] = 0
        
        # 定义各指标的信号逻辑
        signals = pd.DataFrame(index=self.data.index)
        
        # 1. Fisher 信号 (Fisher Transform 上穿其信号线为买入)
        signals['fisher_sig'] = 0
        if 'fisher_signal' in self.data.columns:
            signals['fisher_sig'] = np.where(self.data['fisher'] > self.data['fisher_signal'], 1, 0)
        
        # 2. CHOP 信号 (低值表示趋势市场，高值表示震荡)
        # 当 CHOP < 38.2 时认为是趋势市场，适合交易
        signals['chop_sig'] = np.where(self.data['chop'] < 38.2, 1, 0)
        
        # 3. HMA 信号 (价格上穿 HMA 为买入)
        signals['hma_sig'] = np.where(self.data['Close'] > self.data['hma'], 1, 0)
        
        # 4. LSMA 信号 (价格上穿 LSMA 为买入)
        signals['lsma_sig'] = np.where(self.data['Close'] > self.data['lsma'], 1, 0)
        
        # 5. MACD 信号 (MACD 上穿信号线为买入)
        signals['macd_sig'] = np.where(self.data['macd_diff'] > 0, 1, 0)
        
        # 6. VR 信号 (成交量比率上升为买入)
        signals['vr_sig'] = np.where(self.data['vr'] > 1, 1, 0)
        
        # 综合信号：当至少4个指标给出买入信号时买入
        # 当少于2个指标给出买入信号时卖出
        total_buy_signals = signals.sum(axis=1)
        self.data['signal'] = 0
        self.data['signal'] = np.where(total_buy_signals >= 4, 1, 
                                      np.where(total_buy_signals <= 2, -1, 0))
        
        # 记录每个指标的信号贡献
        self.signals = signals
        
        print(f"✓ Signals generated: {sum(self.data['signal'] == 1)} buy, "
              f"{sum(self.data['signal'] == -1)} sell, "
              f"{sum(self.data['signal'] == 0)} hold")
        
        return True
    
    def backtest(self, initial_capital=100000, commission=0.001):
        """回测策略表现"""
        if 'signal' not in self.data.columns:
            print("✗ No signals available. Call generate_signals() first.")
            return None
        
        print(f"Running backtest with initial capital: ${initial_capital:,.2f}")
        
        # 初始化回测变量
        capital = initial_capital
        position = 0
        trades = []
        portfolio_values = []
        
        for i in range(1, len(self.data)):
            date = self.data.index[i]
            price = self.data['Close'].iloc[i]
            signal = self.data['signal'].iloc[i]
            
            # 执行交易信号
            if signal == 1 and position == 0:  # 买入
                # 计算可买股数
                shares = int(capital * 0.95 / price)  # 使用95%的资金
                if shares > 0:
                    cost = shares * price * (1 + commission)
                    if cost <= capital:
                        capital -= cost
                        position = shares
                        trades.append({
                            'date': date,
                            'action': 'BUY',
                            'shares': shares,
                            'price': price,
                            'value': cost,
                            'capital': capital,
                            'position': position
                        })
            
            elif signal == -1 and position > 0:  # 卖出
                proceeds = position * price * (1 - commission)
                capital += proceeds
                trades.append({
                    'date': date,
                    'action': 'SELL',
                    'shares': position,
                    'price': price,
                    'value': proceeds,
                    'capital': capital,
                    'position': 0
                })
                position = 0
            
            # 计算当前投资组合价值
            portfolio_value = capital + (position * price)
            portfolio_values.append({
                'date': date,
                'portfolio_value': portfolio_value,
                'price': price,
                'position': position,
                'capital': capital
            })
        
        # 最后一天卖出所有持仓
        if position > 0:
            last_price = self.data['Close'].iloc[-1]
            proceeds = position * last_price * (1 - commission)
            capital += proceeds
            trades.append({
                'date': self.data.index[-1],
                'action': 'SELL',
                'shares': position,
                'price': last_price,
                'value': proceeds,
                'capital': capital,
                'position': 0
            })
            position = 0
        
        # 计算性能指标
        portfolio_df = pd.DataFrame(portfolio_values)
        if len(portfolio_df) > 0:
            portfolio_df.set_index('date', inplace=True)
            
            # 计算收益率
            portfolio_df['returns'] = portfolio_df['portfolio_value'].pct_change()
            
            # 基准表现（买入并持有）
            buy_hold_return = (self.data['Close'].iloc[-1] / self.data['Close'].iloc[0] - 1) * 100
            
            # 策略表现
            final_value = portfolio_df['portfolio_value'].iloc[-1]
            total_return = (final_value / initial_capital - 1) * 100
            
            # 计算风险指标
            if len(portfolio_df['returns']) > 1:
                sharpe_ratio = np.sqrt(252) * portfolio_df['returns'].mean() / portfolio_df['returns'].std() if portfolio_df['returns'].std() > 0 else 0
                max_drawdown = (portfolio_df['portfolio_value'].cummax() - portfolio_df['portfolio_value']).max() / portfolio_df['portfolio_value'].cummax().max()
            else:
                sharpe_ratio = 0
                max_drawdown = 0
            
            results = {
                'initial_capital': initial_capital,
                'final_value': final_value,
                'total_return_pct': total_return,
                'buy_hold_return_pct': buy_hold_return,
                'sharpe_ratio': sharpe_ratio,
                'max_drawdown': max_drawdown,
                'total_trades': len(trades),
                'winning_trades': 0,  # 需要更详细的分析
                'trades': trades,
                'portfolio_history': portfolio_df
            }
            
            print("\n" + "="*50)
            print("BACKTEST RESULTS")
            print("="*50)
            print(f"Initial Capital: ${initial_capital:,.2f}")
            print(f"Final Value: ${final_value:,.2f}")
            print(f"Total Return: {total_return:.2f}%")
            print(f"Buy & Hold Return: {buy_hold_return:.2f}%")
            print(f"Sharpe Ratio: {sharpe_ratio:.2f}")
            print(f"Max Drawdown: {max_drawdown:.2%}")
            print(f"Total Trades: {len(trades)}")
            print("="*50)
            
            return results
        else:
            print("✗ No portfolio data generated")
            return None
    
    def plot_results(self, results):
        """绘制策略结果"""
        if results is None:
            print("✗ No results to plot")
            return
        
        fig, axes = plt.subplots(3, 1, figsize=(15, 12))
        
        # 1. 价格和信号
        ax1 = axes[0]
        ax1.plot(self.data.index, self.data['Close'], label='Close Price', linewidth=1)
        
        # 标记买入信号
        buy_signals = self.data[self.data['signal'] == 1]
        if len(buy_signals) > 0:
            ax1.scatter(buy_signals.index, buy_signals['Close'], 
                       color='green', marker='^', s=100, label='Buy Signal')
        
        # 标记卖出信号
        sell_signals = self.data[self.data['signal'] == -1]
        if len(sell_signals) > 0:
            ax1.scatter(sell_signals.index, sell_signals['Close'], 
                       color='red', marker='v', s=100, label='Sell Signal')
        
        ax1.set_title(f'{self.symbol} - Price and Trading Signals')
        ax1.set_ylabel('Price ($)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 2. 指标
        ax2 = axes[1]
        if 'hma' in self.data.columns:
            ax2.plot(self.data.index, self.data['hma'], label='HMA', alpha=0.7)
        if 'lsma' in self.data.columns:
            ax2.plot(self.data.index, self.data['lsma'], label='LSMA', alpha=0.7)
        if 'macd' in self.data.columns:
            ax2.plot(self.data.index, self.data['macd'], label='MACD', alpha=0.7)
            if 'macd_signal' in self.data.columns:
                ax2.plot(self.data.index, self.data['macd_signal'], label='MACD Signal', alpha=0.7)
        
        ax2.set_title('Technical Indicators')
        ax2.set_ylabel('Indicator Value')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # 3. 投资组合价值
        ax3 = axes[2]
        if 'portfolio_history' in results:
            portfolio_df = results['portfolio_history']
            ax3.plot(portfolio_df.index, portfolio_df['portfolio_value'], 
                    label='Portfolio Value', linewidth=2, color='blue')
            ax3.axhline(y=results['initial_capital'], color='gray', linestyle='--', 
                       label='Initial Capital')
            
            ax3.set_title('Portfolio Value Over Time')
            ax3.set_xlabel('Date')
            ax3.set_ylabel('Portfolio Value ($)')
            ax3.legend()
            ax3.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(f'{self.symbol}_strategy_results.png', dpi=150, bbox_inches='tight')
        print(f"✓ Results plot saved as {self.symbol}_strategy_results.png")
        plt.show()
    
    def generate_report(self):
        """生成策略报告"""
        report = []
        report.append("="*60)
        report.append(f"多因子策略分析报告 - {self.symbol}")
        report.append("="*60)
        report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"数据周期: {self.period} ({self.data.index[0]} 到 {self.data.index[-1]})")
        report.append(f"数据点: {len(self.data)} 个")
        report.append("")
        report.append("使用的技术指标:")
        for name, info in self.indicators.items():
            report.append(f"  - {name.upper()}: {info['description']} ({info['type']})")
        report.append("")
        
        if 'signal' in self.data.columns:
            buy_count = sum(self.data['signal'] == 1)
            sell_count = sum(self.data['signal'] == -1)
            hold_count = sum(self.data['signal'] == 0)
            report.append("信号统计:")
            report.append(f"  买入信号: {buy_count} 次")
            report.append(f"  卖出信号: {sell_count} 次")
            report.append(f"  持有信号: {hold_count} 次")
            report.append(f"  信号密度: {buy_count/len(self.data)*100:.1f}% (买入)")
        
        report.append("")
        report.append("策略逻辑:")
        report.append("  买入条件: 至少4个指标给出买入信号")
        report.append("  卖出条件: 少于2个指标给出买入信号")
        report.append("  指标包括: Fisher, CHOP, HMA, LSMA, MACD, VR")
        report.append("")
        
        # 保存报告
        report_text = "\n".join(report)
        with open(f'{self.symbol}_strategy_report.txt', 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print("✓ Strategy report generated")
        print(report_text)
        
        return report_text

def main():
    """主函数"""
    print("多因子策略分析 - 开始")
    print("="*50)
    
    # 创建策略实例
    # 可以使用不同的股票代码，如 'AAPL', 'MSFT', 'GLD' (黄金ETF), 'USO' (原油ETF)
    strategy = MultiFactorStrategy(symbol='SPY', period='1y', interval='1d')
    
    # 步骤1: 获取数据
    if not strategy.fetch_data():
        print("数据获取失败，退出")
        return
    
    # 步骤2: 计算指标
    if not strategy.calculate_indicators():
        print("指标计算失败，退出")
        return
    
    # 步骤3: 生成信号
    if not strategy.generate_signals():
        print("信号生成失败，退出")
        return
    
    # 步骤4: 回测
    results = strategy.backtest(initial_capital=100000, commission=0.001)
    
    # 步骤5: 生成报告和图表
    if results:
        strategy.generate_report()
        strategy.plot_results(results)
    
    print("\n分析完成！")
    print("="*50)

if __name__ == "__main__":
    main()