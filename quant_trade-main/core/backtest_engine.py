"""
回测引擎 - 执行策略回测并生成绩效报告
"""
import pandas as pd
import numpy as np
from datetime import timedelta
from .performance import PerformanceAnalyzer
from pandas import Timestamp
import time

class BacktestEngine:
    def __init__(self, data: pd.DataFrame, strategy_class, initial_cash=1e6, commission=0.0003):
        self.data = data.copy()
        self.strategy_class = strategy_class
        self.initial_cash = float(initial_cash)
        self.commission = commission
        self.trades = []

        # 状态跟踪
        self.current_holding = None
        self.current_position = 0
        self.current_cash = self.initial_cash
        self.entry_price = 0.0
        self.entry_commission = 0.0
        self.cumulative_profit = 0.0

    def run_backtest(self, strategy_params: dict):
        """执行回测"""
        self.start_time = time.time()

        print(f"开始回测")
        print(f"初始资金: {self.initial_cash:,.2f}")
        print(f"回测时间范围: {self.data.index.min()} 到 {self.data.index.max()}")
        print(f"策略参数: {strategy_params}")
        print("-" * 80)

        # 重置状态
        self.current_holding = None
        self.current_position = 0
        self.current_cash = self.initial_cash
        self.entry_price = 0.0
        self.entry_commission = 0.0
        self.cumulative_profit = 0.0
        self.trades = []

        # 生成信号
        strategy = self.strategy_class(self.data, strategy_params)
        signals = strategy.generate_signals()

        if not signals:
            print("警告: 未生成任何交易信号")
            return self._generate_empty_results()

        print(f"生成 {len(signals)} 个交易信号")
        signals = sorted(signals, key=lambda x: x['timestamp'])

        print("开始执行交易...")

        # 执行所有交易
        for i, signal in enumerate(signals):
            if i % 10 == 0 or i == len(signals) - 1:
                progress = (i / len(signals)) * 100
                print(f"交易进度: {progress:.1f}% ({i}/{len(signals)}) | 累计盈亏: {self.cumulative_profit:+.2f}")

            timestamp = signal['timestamp']
            action = signal['action']
            symbol = signal['symbol']

            # 找到对应时间点的股票数据
            time_data = self.data.loc[timestamp]
            if isinstance(time_data, pd.Series):
                time_data = pd.DataFrame([time_data])

            stock_data = time_data[time_data['symbol'] == symbol]
            if len(stock_data) == 0:
                print(f"警告: 找不到股票 {symbol} 在时间 {timestamp} 的数据")
                continue

            stock_data = stock_data.iloc[0]
            price = stock_data['open']

            # 执行交易
            if action == 'buy':
                self._execute_buy(timestamp, symbol, price)
            elif action == 'sell':
                self._execute_sell(timestamp, symbol, price)

        # 构建正确的资金曲线
        equity_curve = self._build_correct_equity_curve()

        total_time = time.time() - self.start_time
        print(f"\n回测完成! 总耗时: {total_time:.2f}秒")
        print(f"总交易笔数: {len(self.trades)}")
        print(f"最终累计盈亏: {self.cumulative_profit:+.2f}")
        print(f"最终现金: {self.current_cash:,.2f}")

        # 计算最终净值（考虑持仓）
        final_equity = self._calculate_final_equity()
        print(f"最终净值: {final_equity:,.2f}")

        # 使用正确的资金曲线进行绩效分析
        analyzer = PerformanceAnalyzer(
            equity_curve=equity_curve,
            timestamps=equity_curve.index,
            trades=self.trades,
            initial_cash=self.initial_cash
        )
        report = analyzer.generate_report()

        return {
            'equity_curve': equity_curve,
            'trades_list': self.trades,
            **report
        }

    def _execute_buy(self, timestamp, symbol, price):
        """执行买入操作 - 区分开多仓和平空仓"""
        if self.current_holding is not None and self.current_holding != symbol:
            print(f"[{timestamp}] 忽略买入 {symbol}: 已有其他持仓 {self.current_holding}")
            return

        # 计算最大可买股数
        max_shares = int(self.current_cash / (price * (1 + self.commission)))
        if max_shares == 0:
            print(f"[{timestamp}] 买入 {symbol} 失败: 资金不足")
            return

        shares_to_trade = max_shares
        cost = shares_to_trade * price * (1 + self.commission)
        commission_total = price * self.commission * shares_to_trade

        # 判断是开多仓还是平空仓
        if self.current_position < 0 and self.current_holding == symbol:
            # 平空仓
            action_type = 'cover_short'

            # 计算盈亏
            entry_commission_total = self.entry_commission * abs(self.current_position)
            exit_commission_total = commission_total
            profit = (self.entry_price - price) * abs(self.current_position) - entry_commission_total - exit_commission_total

            # 更新累计盈亏
            self.cumulative_profit += profit

            print(f"[{timestamp}] 平空仓 {symbol}: {abs(self.current_position)}股 @ {price:.2f}, "
                  f"单笔盈亏: {profit:+.2f}, 累计盈亏: {self.cumulative_profit:+.2f}")
        else:
            # 开多仓
            action_type = 'buy'
            profit = 0.0
            print(f"[{timestamp}] 开多仓 {symbol}: {shares_to_trade}股 @ {price:.2f}, 成本: {cost:.2f}")

        # 更新状态
        self.current_cash -= cost
        self.current_position = shares_to_trade
        self.current_holding = symbol
        self.entry_price = price
        self.entry_commission = price * self.commission

        # 记录交易
        self.trades.append({
            'timestamp': pd.Timestamp(timestamp),
            'action': action_type,
            'symbol': symbol,
            'price': price,
            'shares': shares_to_trade,
            'commission': commission_total,
            'cash_before': self.current_cash + cost,
            'cash_after': self.current_cash,
            'profit': profit
        })

    def _execute_sell(self, timestamp, symbol, price):
        """执行卖出操作 - 区分平多仓和开空仓"""
        if self.current_holding is None:
            # 开空仓
            action_type = 'short'

            # 计算最大可卖空股数
            max_shares = int(self.current_cash / (price * (1 + self.commission)))
            if max_shares == 0:
                print(f"[{timestamp}] 开空仓 {symbol} 失败: 资金不足")
                return

            shares_to_trade = max_shares
            revenue = shares_to_trade * price * (1 - self.commission)
            commission_total = price * self.commission * shares_to_trade

            # 更新状态
            self.current_cash += revenue
            self.current_position = -shares_to_trade
            self.current_holding = symbol
            self.entry_price = price
            self.entry_commission = price * self.commission

            # 记录交易
            self.trades.append({
                'timestamp': pd.Timestamp(timestamp),
                'action': action_type,
                'symbol': symbol,
                'price': price,
                'shares': shares_to_trade,
                'commission': commission_total,
                'cash_before': self.current_cash - revenue,
                'cash_after': self.current_cash,
                'profit': 0.0
            })

            print(f"[{timestamp}] 开空仓 {symbol}: {shares_to_trade}股 @ {price:.2f}, 收入: {revenue:.2f}")

        elif self.current_holding == symbol and self.current_position > 0:
            # 平多仓
            action_type = 'sell'
            shares_to_trade = self.current_position
            revenue = shares_to_trade * price * (1 - self.commission)
            commission_per_share = price * self.commission
            commission_total = commission_per_share * shares_to_trade

            # 计算盈亏
            entry_commission_total = self.entry_commission * shares_to_trade
            exit_commission_total = commission_per_share * shares_to_trade
            profit = (price - self.entry_price) * shares_to_trade - entry_commission_total - exit_commission_total

            # 更新状态
            self.current_cash += revenue
            self.current_position = 0
            self.current_holding = None
            self.cumulative_profit += profit

            # 记录交易
            self.trades.append({
                'timestamp': pd.Timestamp(timestamp),
                'action': action_type,
                'symbol': symbol,
                'price': price,
                'shares': shares_to_trade,
                'commission': commission_total,
                'cash_before': self.current_cash - revenue,
                'cash_after': self.current_cash,
                'profit': profit
            })

            print(f"[{timestamp}] 平多仓 {symbol}: {shares_to_trade}股 @ {price:.2f}, "
                  f"单笔盈亏: {profit:+.2f}, 累计盈亏: {self.cumulative_profit:+.2f}")
        else:
            print(f"[{timestamp}] 忽略卖出 {symbol}: 无此持仓或持仓不匹配")

    def _build_correct_equity_curve(self):
        """构建正确的资金曲线"""
        print("构建资金曲线...")

        # 按时间顺序处理
        unique_times = sorted(self.data.index.unique())
        equity_values = []

        # 创建交易时间映射
        trade_times = {trade['timestamp']: trade for trade in self.trades}

        # 模拟回放：按时间顺序重建状态
        current_cash = self.initial_cash
        current_position = 0
        current_holding = None
        entry_price = 0.0

        for timestamp in unique_times:
            # 检查是否有交易在这个时间点
            if timestamp in trade_times:
                trade = trade_times[timestamp]
                # 更新状态
                current_cash = trade['cash_after']
                current_holding = trade['symbol']

                if trade['action'] in ['buy', 'cover_short']:
                    current_position = trade['shares']
                elif trade['action'] in ['sell', 'short']:
                    if trade['action'] == 'sell':
                        current_position = 0
                        current_holding = None
                    else:  # short
                        current_position = -trade['shares']

            # 计算当前时间点的总资产
            if current_holding and current_position != 0:
                # 找到持仓股票在当前时间点的价格
                time_data = self.data.loc[timestamp]
                if isinstance(time_data, pd.Series):
                    if time_data['symbol'] == current_holding:
                        price = time_data['close']
                        portfolio_value = current_cash + abs(current_position) * price
                    else:
                        portfolio_value = current_cash
                else:
                    holding_data = time_data[time_data['symbol'] == current_holding]
                    if len(holding_data) > 0:
                        price = holding_data.iloc[0]['close']
                        portfolio_value = current_cash + abs(current_position) * price
                    else:
                        portfolio_value = current_cash
            else:
                portfolio_value = current_cash

            equity_values.append(portfolio_value)

        # 创建资金曲线Series
        equity_curve = pd.Series(equity_values, index=unique_times)

        print(f"资金曲线构建完成，最终净值: {equity_curve.iloc[-1]:,.2f}")
        return equity_curve

    def _calculate_final_equity(self):
        """计算最终净值"""
        final_equity = self.current_cash

        # 如果有持仓，加上持仓的当前价值
        if self.current_holding and self.current_position != 0:
            last_time = self.data.index.max()
            time_data = self.data.loc[last_time]

            if isinstance(time_data, pd.Series):
                if time_data['symbol'] == self.current_holding:
                    price = time_data['close']
                    final_equity = self.current_cash + abs(self.current_position) * price
            else:
                holding_data = time_data[time_data['symbol'] == self.current_holding]
                if len(holding_data) > 0:
                    price = holding_data.iloc[0]['close']
                    final_equity = self.current_cash + abs(self.current_position) * price

        return final_equity

    def _generate_empty_results(self):
        """生成空结果"""
        empty_curve = pd.Series([self.initial_cash], index=[self.data.index[0]])

        return {
            'equity_curve': empty_curve,
            'trades_list': [],
            'summary': {
                'total_return': 0.0,
                'annualized_return': 0.0,
                'trade_count': 0,
                'date_range': f"{self.data.index.min()} 到 {self.data.index.max()}"
            },
            'drawdown': {'max_drawdown': 0.0, 'drawdown_series': empty_curve},
            'risk_return': {'sharpe_ratio': 0.0},
            'trades': {'win_rate': 0.0, 'profit_factor': 0.0}
        }

    def save_trades(self, filename: str):
        if not self.trades:
            print("警告: 无交易记录可保存")
            return

        trades_df = pd.DataFrame(self.trades)
        trades_df.to_csv(filename, index=False)
        print(f"交易记录已保存到: {filename}, 共 {len(self.trades)} 笔交易")
