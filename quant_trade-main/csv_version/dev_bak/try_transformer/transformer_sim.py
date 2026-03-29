import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, WhiteKernel, Matern
from sklearn.preprocessing import StandardScaler
from torch.distributions import Categorical
import os
import warnings
import talib
# 忽略警告
warnings.filterwarnings('ignore')

# 配置设置
class Config:
    SEED = 42
    TRAIN_RATIO = 0.8  # 训练集比例
    
    # 特征参数
    WINDOW_SIZE = 30  # 时间窗口大小
    FEATURE_DIM = 8  # 特征维度
    
    # GRPO 参数
    GP_KERNEL = RBF(length_scale=1.0) + Matern(nu=1.5) + WhiteKernel(noise_level=0.5)
    POLICY_LR = 3e-4
    VALUE_LR = 1e-3
    GAMMA = 0.99  # 折扣因子
    LAMBDA = 0.95  # GAE参数
    BATCH_SIZE = 64
    EPOCHS = 100
    CLIP_EPSILON = 0.2
    
    # 交易参数
    TRANSACTION_FEE = 0.001  # 交易费率
    RISK_FREE_RATE = 0 # 年化无风险利率
    INITIAL_CAPITAL = 10000  # 初始资金
    
    # 保存路径
    MODEL_PATH = fr'E:\stock\csv_version\grpo_trading_model_20250811_sim.pth'

# 设置随机种子
torch.manual_seed(Config.SEED)
np.random.seed(Config.SEED)

# 交易环境
class TradingEnv:
    def __init__(self, data, window_size, transaction_fee=0.001):
        self.data = data
        self.window_size = window_size
        self.transaction_fee = transaction_fee
        self.reset()
        
    def reset(self):
        self.current_step = self.window_size
        self.position = 0  # 0: 空仓, 1: 满仓
        self.cash = Config.INITIAL_CAPITAL
        self.stock_value = 0
        self.portfolio_value = [self.cash] * (self.window_size + 1)
        self.actions = [0] * (self.window_size + 1)
        self.done = False
        return self.get_state()
    
    def get_state(self):
        """获取当前状态窗口"""
        start_idx = self.current_step - self.window_size
        end_idx = self.current_step
        state = self.data.iloc[start_idx:end_idx][Config.feature_cols].values
        return state
    
    def step(self, action):
        prev_position = self.position
        self.position = action
        
        # 获取当日价格信息
        current_price = self.data.iloc[self.current_step]['close']
        current_return = self.data.iloc[self.current_step]['returns']
        
        # 计算交易成本
        transaction_cost = 0
        if prev_position != action:
            # 计算交易金额（全仓买入或卖出）
            trade_amount = self.portfolio_value[-1]
            transaction_cost = trade_amount * self.transaction_fee
        
        # 更新投资组合价值
        if action == 1:  # 买入或持股
            # 如果是买入操作，计算可购买的股票数量
            if prev_position == 0:
                self.stock_value = (self.portfolio_value[-1] - transaction_cost) / current_price
                portfolio_value = self.stock_value * current_price
            else:  # 继续持有
                portfolio_value = self.stock_value * current_price
        else:  # 卖出或持现
            if prev_position == 1:  # 卖出
                portfolio_value = self.stock_value * current_price - transaction_cost
                self.cash = portfolio_value
                self.stock_value = 0
            else:  # 继续持现
                portfolio_value = self.cash * (1 + Config.RISK_FREE_RATE / 252)
                self.cash = portfolio_value
        
        # 计算奖励
        reward = self.calculate_reward(portfolio_value, action, prev_position, current_return)
        
        # 更新状态
        self.portfolio_value.append(portfolio_value)
        self.actions.append(action)
        self.current_step += 1
        
        # 检查是否结束
        if self.current_step >= len(self.data) - 1:
            self.done = True
            
        next_state = self.get_state()
        return next_state, reward, self.done, portfolio_value
    
    def calculate_reward(self, portfolio_value, action, prev_position, market_return):
        """计算强化学习奖励"""
        # 基础回报
        simple_return = (portfolio_value / self.portfolio_value[-1]) - 1
        
        # 方向奖励
        direction_reward = 1 if (action == 1 and market_return > 0) or (action == 0 and market_return < 0) else -1
        
        # 状态转换奖励
        transition_reward = 0
        if prev_position != action:
            if action == 1:  # 买入
                transition_reward = 0.5 if market_return > 0 else -0.5
            else:  # 卖出
                transition_reward = 0.5 if market_return < 0 else -0.5
        
        # 风险调整奖励
        volatility = self.data.iloc[self.current_step]['volatility']
        risk_adjustment = -0.2 * volatility * action  # 持股时波动惩罚
        
        # 组合奖励
        reward = simple_return + 0.3 * direction_reward + transition_reward + risk_adjustment
        return reward

# Transformer 特征提取器
class FeatureExtractor(nn.Module):
    def __init__(self, input_dim, d_model=64, nhead=4, num_layers=2, dropout=0.1):
        super().__init__()
        self.d_model = d_model
        self.embedding = nn.Linear(input_dim, d_model)
        self.pos_encoder = self.PositionalEncoding(d_model, dropout)
        encoder_layer = nn.TransformerEncoderLayer(
            d_model, nhead, dim_feedforward=4*d_model, dropout=dropout
        )
        self.transformer = nn.TransformerEncoder(encoder_layer, num_layers)
        
    class PositionalEncoding(nn.Module):
        def __init__(self, d_model, dropout=0.1, max_len=5000):
            super().__init__()
            self.dropout = nn.Dropout(p=dropout)
            position = torch.arange(max_len).unsqueeze(1)
            div_term = torch.exp(torch.arange(0, d_model, 2) * (-np.log(10000.0) / d_model))
            pe = torch.zeros(max_len, 1, d_model)
            pe[:, 0, 0::2] = torch.sin(position * div_term)
            pe[:, 0, 1::2] = torch.cos(position * div_term)
            self.register_buffer('pe', pe)

        def forward(self, x):
            x = x + self.pe[:x.size(0)]
            return self.dropout(x)
        
    def forward(self, x):
        # x: [batch, seq_len, features] -> [seq_len, batch, features]
        x = self.embedding(x) * np.sqrt(self.d_model)
        x = x.permute(1, 0, 2)  # [seq_len, batch, features]
        x = self.pos_encoder(x)
        x = self.transformer(x)
        return x[-1]  # 返回最后时间步的特征 [batch, d_model]

# GRPO 代理
class GRPOAgent:
    def __init__(self, feature_extractor, state_dim, action_dim, config):
        self.feature_extractor = feature_extractor
        self.config = config
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # 策略网络
        self.policy_net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, action_dim)
        )
        
        # 价值网络
        self.value_net = nn.Sequential(
            nn.Linear(state_dim, 64),
            nn.ReLU(),
            nn.Linear(64, 1)
        )
        
        # 高斯过程回归器
        self.gp = GaussianProcessRegressor(
            kernel=config.GP_KERNEL,
            alpha=1e-5,
            normalize_y=True,
            n_restarts_optimizer=3
        )
        
        # 优化器
        self.policy_optim = optim.Adam(
            list(feature_extractor.parameters()) + list(self.policy_net.parameters()),
            lr=config.POLICY_LR
        )
        
        self.value_optim = optim.Adam(
            self.value_net.parameters(),
            lr=config.VALUE_LR
        )
        
        # 经验池
        self.memory = []
        self.episode_states = []
        self.episode_rewards = []
    
    def act(self, state):
        """根据状态选择动作"""
        state_tensor = torch.FloatTensor(state).unsqueeze(0)  # [1, seq_len, features]
        
        with torch.no_grad():
            features = self.feature_extractor(state_tensor)  # [1, d_model]
            logits = self.policy_net(features)
            dist = Categorical(logits=logits)
            action = dist.sample()
            log_prob = dist.log_prob(action)
            value = self.value_net(features)
            
        return action.item(), log_prob.item(), value.item()
    
    def update_gp(self):
        """使用当前经验更新高斯过程奖励模型"""
        if not self.episode_states:
            return
        
        states = np.array(self.episode_states)
        rewards = np.array(self.episode_rewards)
        
        # 提取特征
        with torch.no_grad():
            state_tensor = torch.FloatTensor(states)
            features = self.feature_extractor(state_tensor).numpy()
        
        # 拟合高斯过程
        self.gp.fit(features, rewards)
        
        # 清空episode数据
        self.episode_states = []
        self.episode_rewards = []
    
    def update_policy(self):
        """使用GRPO更新策略"""
        if len(self.memory) < self.config.BATCH_SIZE:
            return
        
        # 从内存中提取数据
        states, actions, old_log_probs, rewards, values = zip(*self.memory)
        states = np.array(states)
        actions = np.array(actions)
        old_log_probs = np.array(old_log_probs)
        rewards = np.array(rewards)
        values = np.array(values)
        
        # 计算GAE (Generalized Advantage Estimation)
        advantages = np.zeros_like(rewards)
        last_advantage = 0
        for t in reversed(range(len(rewards))):
            if t == len(rewards) - 1:
                next_value = 0
            else:
                next_value = values[t+1]
            
            delta = rewards[t] + self.config.GAMMA * next_value - values[t]
            advantages[t] = delta + self.config.GAMMA * self.config.LAMBDA * last_advantage
            last_advantage = advantages[t]
        
        # 使用GP预测奖励分布
        with torch.no_grad():
            state_tensor = torch.FloatTensor(states)
            features = self.feature_extractor(state_tensor).numpy()
        
        # GP预测奖励分布
        mu, sigma = self.gp.predict(features, return_std=True)
        
        # 根据不确定性调整奖励
        adjusted_rewards = mu + 0.5 * sigma  # 鼓励探索不确定性高的区域
        
        # 转换为张量
        states_tensor = torch.FloatTensor(states)
        actions_tensor = torch.LongTensor(actions)
        old_log_probs_tensor = torch.FloatTensor(old_log_probs)
        advantages_tensor = torch.FloatTensor(advantages)
        adjusted_rewards_tensor = torch.FloatTensor(adjusted_rewards)
        
        # 策略更新
        for _ in range(3):  # 多次更新
            features = self.feature_extractor(states_tensor)
            logits = self.policy_net(features)
            dist = Categorical(logits=logits)
            log_probs = dist.log_prob(actions_tensor)
            entropy = dist.entropy().mean()
            
            # GRPO损失函数
            ratios = torch.exp(log_probs - old_log_probs_tensor.detach())
            surr1 = ratios * advantages_tensor
            surr2 = torch.clamp(ratios, 1 - self.config.CLIP_EPSILON, 
                                1 + self.config.CLIP_EPSILON) * advantages_tensor
            policy_loss = -torch.min(surr1, surr2).mean()
            
            # 价值函数更新
            values_pred = self.value_net(features).squeeze()
            value_loss = 0.5 * (values_pred - adjusted_rewards_tensor.detach()).pow(2).mean()
            
            # 总损失
            loss = policy_loss + value_loss - 0.01 * entropy
            
            # 梯度下降
            self.policy_optim.zero_grad()
            self.value_optim.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(self.feature_extractor.parameters(), 0.5)
            torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 0.5)
            self.policy_optim.step()
            self.value_optim.step()
        
        # 清空内存
        self.memory = []
    
    def save_model(self, path):
        """保存模型"""
        torch.save({
            'feature_extractor': self.feature_extractor.state_dict(),
            'policy_net': self.policy_net.state_dict(),
            'value_net': self.value_net.state_dict(),
        }, path)
        print(f"模型已保存至 {path}")
    
    def load_model(self, path):
        """加载模型"""
        if os.path.exists(path):
            checkpoint = torch.load(path)
            self.feature_extractor.load_state_dict(checkpoint['feature_extractor'])
            self.policy_net.load_state_dict(checkpoint['policy_net'])
            self.value_net.load_state_dict(checkpoint['value_net'])
            print(f"已从 {path} 加载模型")
            return True
        return False


# 回测系统
class Backtester:
    def __init__(self, env, policy_net, feature_extractor):
        self.env = env
        self.policy_net = policy_net
        self.feature_extractor = feature_extractor
        self.results = {}
        self.results_r = {}
        
    def run_backtest(self):
        """运行回测"""
        state = self.env.reset()
        done = False
        portfolio_values = [self.env.portfolio_value[-1]]
        actions = [0]
        dates = [self.env.data.iloc[self.env.window_size]['Date']]
        
        while not done:
            state_tensor = torch.FloatTensor(state).unsqueeze(0)
            with torch.no_grad():
                features = self.feature_extractor(state_tensor)
                logits = self.policy_net(features)
                action = torch.argmax(logits).item()
            
            next_state, _, done, portfolio_value = self.env.step(action)
            portfolio_values.append(portfolio_value)
            actions.append(action)
            dates.append(self.env.data.iloc[self.env.current_step]['Date'])
            state = next_state
        
        # 计算性能指标
        returns = pd.Series(portfolio_values).pct_change().dropna()
        cumulative_returns = (returns + 1).cumprod() - 1
        max_drawdown = self.calculate_max_drawdown(portfolio_values)
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        
        # 保存结果
        self.results = {
            'dates': dates,
            'portfolio_values': portfolio_values,
            'actions': actions,
            'returns': returns,
            'cumulative_returns': cumulative_returns,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'final_value': portfolio_values[-1]
        }
        self.results_r = {
            'dates': dates,            
            'actions': actions
        }
        pd.DataFrame(self.results_r).to_csv('trading_results_tf_sim.csv', index=False)
        return self.results
    
    def calculate_max_drawdown(self, values):
        """计算最大回撤"""
        peak = values[0]
        max_drawdown = 0
        for value in values:
            if value > peak:
                peak = value
            drawdown = (peak - value) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        return max_drawdown
    
    def calculate_sharpe_ratio(self, returns, risk_free_rate=Config.RISK_FREE_RATE):
        """计算年化夏普比率"""
        excess_returns = returns - risk_free_rate / 252
        if excess_returns.std() == 0:
            return 0
        sharpe_ratio = np.sqrt(252) * excess_returns.mean() / excess_returns.std()
        return sharpe_ratio
    
    def plot_results(self):
        """绘制回测结果"""
        if not self.results:
            print("请先运行回测")
            return
            
        plt.figure(figsize=(15, 10))
        
        # 投资组合价值
        plt.subplot(2, 1, 1)
        plt.plot(self.results['dates'], self.results['portfolio_values'], label='投资组合价值')
        plt.title('投资组合价值变化')
        plt.xlabel('日期')
        plt.ylabel('价值')
        plt.legend()
        plt.grid(True)
        
        # 仓位变化
        plt.subplot(2, 1, 2)
        plt.step(self.results['dates'], self.results['actions'], where='post', label='仓位')
        plt.title('仓位变化 (0=现金, 1=股票)')
        plt.xlabel('日期')
        plt.ylabel('仓位')
        plt.ylim(-0.1, 1.1)
        plt.yticks([0, 1], ['现金', '股票'])
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.show()
        
        # 打印性能指标
        print(f"\n回测结果 ({len(self.results['portfolio_values'])} 个交易日):")
        print(f"初始资金: ${Config.INITIAL_CAPITAL:,.2f}")
        print(f"最终投资组合价值: ${self.results['final_value']:,.2f}")
        print(f"总收益率: {((self.results['final_value']/Config.INITIAL_CAPITAL)-1)*100:.2f}%")
        print(f"最大回撤: {self.results['max_drawdown']*100:.2f}%")
        print(f"年化夏普比率: {self.results['sharpe_ratio']:.2f}")
    
    def buy_and_hold_strategy(self):
        """买入持有策略作为基准"""
        values = [Config.INITIAL_CAPITAL]
        for i in range(self.env.window_size, len(self.env.data)):
            if i == self.env.window_size:
                # 在开始时全仓买入
                price = self.env.data.iloc[i]['close']
                shares = Config.INITIAL_CAPITAL / price
                value = shares * price
            else:
                current_price = self.env.data.iloc[i]['close']
                value = shares * current_price
            values.append(value)
        
        returns = pd.Series(values).pct_change().dropna()
        cumulative_returns = (returns + 1).cumprod() - 1
        max_drawdown = self.calculate_max_drawdown(values)
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        
        return {
            'portfolio_values': values,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'final_value': values[-1]
        }


# 主程序
def main():
    # 设置特征列名
    Config.feature_cols = ['low', 'amount', 'high', 'close', 'volume', 'open', 'diff',
       'dea', 'macd', 'ma5', 'ma8', 'ma13', 'ma21', 'rsi', 'returns', 'volatility']   
    
    ts_code = "000063.SZ" 
    file_path = fr"E:\stock\backtest\data\analyzed\5min\{ts_code}_analysis.csv"
    available_columns = pd.read_csv(file_path, nrows=0).columns.tolist()
    columns_to_read = list(set(Config.feature_cols + ['trade_date']) & set(available_columns))
    df = pd.read_csv(file_path, usecols=columns_to_read, index_col='trade_date', parse_dates=True)         
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(20, min_periods=5).std()
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['Date'] = df.index
    df = df.dropna(subset=Config.feature_cols)
    print(df.columns)
    print(f"数据加载完成: {len(df)} 行, {len(df.columns)} 列")

    # 3. 应用特征工程
    data = df
    feature_columns = Config.feature_cols # 添加你使用的所有特征列名
    a = feature_columns + ['Date']
    # 4. 数据标准化
    scaler = StandardScaler()
    scaled_features = scaler.fit_transform(data[feature_columns])
    data[feature_columns] = scaled_features
    
    # 分割训练集和测试集
    train_size = int(len(data) * Config.TRAIN_RATIO)
    train_data = data.iloc[:train_size][a]
    test_data = data.iloc[train_size:][a]
    
    print(f"数据集大小: 总共 {len(data)} 天, 训练集 {len(train_data)} 天, 测试集 {len(test_data)} 天")
    
    # 2. 创建环境和模型
    train_env = TradingEnv(train_data, Config.WINDOW_SIZE, Config.TRANSACTION_FEE)
    test_env = TradingEnv(test_data, Config.WINDOW_SIZE, Config.TRANSACTION_FEE)
    
    feature_extractor = FeatureExtractor(
        input_dim=len(Config.feature_cols),
        d_model=64,
        nhead=4,
        num_layers=2
    )
    
    agent = GRPOAgent(
        feature_extractor=feature_extractor,
        state_dim=64,  # 特征提取器的输出维度
        action_dim=2,  # 买入/卖出
        config=Config
    )
    
    # 尝试加载已有模型
    if not agent.load_model(Config.MODEL_PATH):
        # 3. 训练模型
        print("开始使用GRPO训练模型...")
        train_rewards = []
        
        for epoch in range(Config.EPOCHS):
            state = train_env.reset()
            done = False
            total_reward = 0
            step_count = 0
            
            while not done:
                # 选择动作
                action, log_prob, value = agent.act(state)
                
                # 执行动作
                next_state, reward, done, _ = train_env.step(action)
                total_reward += reward
                step_count += 1
                
                # 存储经验
                agent.memory.append((state, action, log_prob, reward, value))
                agent.episode_states.append(state)
                agent.episode_rewards.append(reward)
                
                # 定期更新
                if step_count % Config.BATCH_SIZE == 0:
                    # 更新高斯过程模型
                    agent.update_gp()
                    
                    # 更新策略
                    agent.update_policy()
                
                # 更新状态
                state = next_state
            
            # 每轮结束更新
            if agent.episode_states:
                agent.update_gp()
                agent.update_policy()
            
            train_rewards.append(total_reward)
            
            # 打印进度
            portfolio_value = train_env.portfolio_value[-1]
            print(f"Epoch {epoch+1}/{Config.EPOCHS}, 总奖励: {total_reward:.2f}, 组合价值: ${portfolio_value:,.2f}")
        
        # 保存训练好的模型
        agent.save_model(Config.MODEL_PATH)
        
        # 绘制训练奖励曲线
        plt.figure(figsize=(10, 5))
        plt.plot(train_rewards)
        plt.title('训练奖励曲线')
        plt.xlabel('Epoch')
        plt.ylabel('总奖励')
        plt.grid(True)
        plt.show()
    
    # 4. 在测试集上回测
    print("\n在测试集上运行回测...")
    backtester = Backtester(test_env, agent.policy_net, agent.feature_extractor)
    test_results = backtester.run_backtest()
    
    # 绘制结果
    backtester.plot_results()
    
    # 5. 与买入持有策略对比
    print("\n与买入持有策略对比...")
    bh_results = backtester.buy_and_hold_strategy()
    
    # 对齐数据长度
    min_len = min(len(test_results['dates']), len(test_results['portfolio_values']), 
                 len(bh_results['portfolio_values']))
    test_dates = test_results['dates'][:min_len]
    test_values = test_results['portfolio_values'][:min_len]
    bh_values = bh_results['portfolio_values'][:min_len]
    
    # 绘制对比图
    plt.figure(figsize=(12, 6))
    plt.plot(test_dates, test_values, label='GRPO策略')
    plt.plot(test_dates, bh_values, label='买入持有策略')
    plt.title('策略对比')
    plt.xlabel('日期')
    plt.ylabel('投资组合价值')
    plt.legend()
    plt.grid(True)
    plt.show()
    
    # 打印对比结果
    print("\n策略性能对比:")
    print(f"{'指标':<15} | {'GRPO策略':>15} | {'买入持有':>15}")
    print("-" * 50)
    print(f"{'初始资金':<15} | ${Config.INITIAL_CAPITAL:>15,.2f} | ${Config.INITIAL_CAPITAL:>15,.2f}")
    print(f"{'最终价值':<15} | ${test_results['final_value']:>15,.2f} | ${bh_results['final_value']:>15,.2f}")
    print(f"{'总收益率':<15} | {((test_results['final_value']/Config.INITIAL_CAPITAL)-1)*100:>15.2f}% | {((bh_results['final_value']/Config.INITIAL_CAPITAL)-1)*100:>15.2f}%")
    print(f"{'最大回撤':<15} | {test_results['max_drawdown']*100:>15.2f}% | {bh_results['max_drawdown']*100:>15.2f}%")
    print(f"{'夏普比率':<15} | {test_results['sharpe_ratio']:>15.2f} | {bh_results['sharpe_ratio']:>15.2f}")

if __name__ == "__main__":
    main()