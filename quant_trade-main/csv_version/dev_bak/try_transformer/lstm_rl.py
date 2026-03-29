import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt

# ==================== 需要你自定义的部分 ====================
# 1. 加载你的数据
# 替换为你的数据文件路径
data = pd.read_csv('your_financial_data.csv', parse_dates=['date'])

# 2. 创建特征工程函数 - 根据你的数据特征调整
def create_features(df):
    """创建技术指标特征 - 根据你的数据修改"""
    df = df.copy()
    
    # 基本价格特征
    df['returns'] = df['close'].pct_change()
    
    # 技术指标 - 根据你的需求添加/删除
    # 确保你安装了TA-Lib: pip install TA-Lib
    import talib
    df['rsi'] = talib.RSI(df['close'], timeperiod=14)
    df['macd'], df['macd_signal'], _ = talib.MACD(df['close'])
    df['ema20'] = talib.EMA(df['close'], timeperiod=20)
    df['adx'] = talib.ADX(df['high'], df['low'], df['close'], timeperiod=14)
    df['atr'] = talib.ATR(df['high'], df['low'], df['close'], timeperiod=14)
    
    # 波动率
    df['volatility'] = df['returns'].rolling(20).std()
    
    # 滞后特征
    for lag in [1, 2, 3, 5, 10]:
        df[f'return_lag_{lag}'] = df['returns'].shift(lag)
    
    # 添加你自己的自定义特征...
    
    return df.dropna()

# 3. 应用特征工程
featured_data = create_features(data)
feature_columns = ['returns', 'rsi', 'macd', 'ema20', 'volatility']  # 添加你使用的所有特征列名

# 4. 数据标准化
scaler = StandardScaler()
scaled_features = scaler.fit_transform(featured_data[feature_columns])
featured_data[feature_columns] = scaled_features
# =========================================================

# 训练参数
SEQ_LEN = 30  # LSTM输入序列长度
BATCH_SIZE = 64
EPISODES = 500
INITIAL_BALANCE = 10000
RISK_FREE_RATE = 0.02 / 252  # 日无风险利率

# 交易环境
class TradingEnv:
    def __init__(self, data, initial_balance=INITIAL_BALANCE):
        self.data = data.reset_index(drop=True)
        self.initial_balance = initial_balance
        self.reset()
        
    def reset(self):
        self.balance = self.initial_balance
        self.shares = 0
        self.current_step = SEQ_LEN  # 从足够长的序列后开始
        self.max_steps = len(self.data) - 1
        self.portfolio_values = [self.initial_balance]
        self.actions = []
        self.peak = self.initial_balance
        return self._get_state_seq()
    
    def _get_state_seq(self):
        """获取当前序列的状态"""
        start_idx = max(0, self.current_step - SEQ_LEN)
        return self.data.iloc[start_idx:self.current_step][feature_columns].values
    
    def step(self, action):
        # 记录动作
        self.actions.append(action)
        
        current_row = self.data.iloc[self.current_step]
        current_price = current_row['close']
        prev_value = self.balance + self.shares * current_price
        
        # 执行动作
        if action == 0:  # 持有
            pass
        elif action == 1:  # 买入
            if self.balance > 0:
                shares_bought = self.balance / current_price
                self.shares += shares_bought
                self.balance = 0
        elif action == 2:  # 卖出
            if self.shares > 0:
                self.balance += self.shares * current_price
                self.shares = 0
        
        # 移动到下一步
        self.current_step += 1
        if self.current_step > self.max_steps:
            done = True
            current_price = self.data.iloc[-1]['close']
        else:
            done = False
            current_row = self.data.iloc[self.current_step]
            current_price = current_row['close']
        
        # 计算新资产价值
        portfolio_value = self.balance + self.shares * current_price
        self.portfolio_values.append(portfolio_value)
        
        # 更新资产峰值
        if portfolio_value > self.peak:
            self.peak = portfolio_value
        
        # 计算最大回撤
        drawdown = (self.peak - portfolio_value) / self.peak if self.peak > 0 else 0
        
        # 计算日收益率
        daily_return = (portfolio_value / prev_value) - 1 if prev_value > 0 else 0
        
        # 计算奖励 - 夏普比率变体
        reward = daily_return - RISK_FREE_RATE
        
        # 加入回撤惩罚
        if drawdown > 0.05:  # 回撤超过5%
            reward -= 0.1 * drawdown
            
        # 加入交易惩罚
        if action != 0:  # 交易动作
            reward -= 0.001
        
        # 检查是否结束
        done = done or (self.current_step >= self.max_steps)
        
        return self._get_state_seq(), reward, done, portfolio_value

# LSTM策略网络
class LSTM_Policy(nn.Module):
    def __init__(self, input_size, hidden_size, num_actions):
        super().__init__()
        self.lstm = nn.LSTM(input_size, hidden_size, batch_first=True, dropout=0.2)
        self.fc = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(32, num_actions)
        )
        
    def forward(self, x):
        out, _ = self.lstm(x)
        out = self.fc(out[:, -1, :])  # 取序列最后一个输出
        return torch.softmax(out, dim=-1)

# 初始化环境
env = TradingEnv(featured_data)

# 模型参数
INPUT_DIM = len(feature_columns)
HIDDEN_SIZE = 128
NUM_ACTIONS = 3  # 0=持有, 1=买入, 2=卖出

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = LSTM_Policy(INPUT_DIM, HIDDEN_SIZE, NUM_ACTIONS).to(device)
optimizer = optim.Adam(model.parameters(), lr=0.0001, weight_decay=1e-5)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, 'max', patience=10, factor=0.5, verbose=True)

# 训练函数
def train(env, model, optimizer, episodes=EPISODES, batch_size=BATCH_SIZE):
    episode_returns = []
    best_portfolio = INITIAL_BALANCE
    
    for episode in range(episodes):
        state_seq = env.reset()
        states, actions, rewards, log_probs = [], [], [], []
        done = False
        episode_rewards = 0
        
        while not done:
            # 准备输入序列
            state_tensor = torch.FloatTensor(state_seq).unsqueeze(0).to(device)
            
            # 模型预测
            action_probs = model(state_tensor)
            dist = Categorical(action_probs)
            action = dist.sample()
            log_prob = dist.log_prob(action)
            
            # 执行动作
            next_state, reward, done, portfolio_value = env.step(action.item())
            
            # 存储数据
            states.append(state_seq)
            actions.append(action)
            rewards.append(reward)
            log_probs.append(log_prob)
            
            # 更新状态
            state_seq = next_state
            episode_rewards += reward
            
            # 批量更新
            if len(rewards) >= batch_size or done:
                # 计算折扣回报
                returns = []
                R = 0
                for r in reversed(rewards):
                    R = r + 0.99 * R  # 折扣因子
                    returns.insert(0, R)
                
                returns = torch.tensor(returns).float().to(device)
                
                # 标准化回报
                returns = (returns - returns.mean()) / (returns.std() + 1e-7)
                
                # 计算损失
                policy_loss = []
                for log_prob, R in zip(log_probs, returns):
                    policy_loss.append(-log_prob * R)
                
                # 反向传播
                optimizer.zero_grad()
                loss = torch.stack(policy_loss).sum()
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                optimizer.step()
                
                # 重置
                states, actions, rewards, log_probs = [], [], [], []
        
        # 记录表现
        final_value = portfolio_value
        roi = (final_value - INITIAL_BALANCE) / INITIAL_BALANCE
        episode_returns.append(roi)
        
        # 学习率调整
        scheduler.step(final_value)
        
        # 保存最佳模型
        if final_value > best_portfolio:
            best_portfolio = final_value
            torch.save(model.state_dict(), 'best_portfolio_model.pth')
        
        print(f'Episode {episode+1}/{episodes}, Portfolio: ${final_value:.2f}, ROI: {roi*100:.2f}%')
    
    return episode_returns

# 训练模型
print("开始训练模型...")
returns_history = train(env, model, optimizer)

# 可视化训练结果
plt.figure(figsize=(12, 6))
plt.plot(returns_history)
plt.title('ROI During Training')
plt.xlabel('Episode')
plt.ylabel('Return on Investment')
plt.grid(True)
plt.savefig('training_roi.png')
plt.show()

# 回测函数
def backtest(env, model):
    state_seq = env.reset()
    done = False
    portfolio_values = [env.initial_balance]
    
    while not done:
        state_tensor = torch.FloatTensor(state_seq).unsqueeze(0).to(device)
        
        with torch.no_grad():
            action_probs = model(state_tensor)
            action = torch.argmax(action_probs).item()
        
        state_seq, _, done, portfolio_value = env.step(action)
        portfolio_values.append(portfolio_value)
    
    return portfolio_values

# 加载最佳模型
model.load_state_dict(torch.load('best_portfolio_model.pth'))
model.eval()

# 回测表现
print("回测最佳模型...")
env_backtest = TradingEnv(featured_data)
portfolio_values = backtest(env_backtest, model)

# 可视化回测结果
plt.figure(figsize=(14, 7))
plt.plot(portfolio_values, label='Portfolio Value')
plt.title('Portfolio Value During Backtesting')
plt.xlabel('Time Step')
plt.ylabel('Value ($)')
plt.legend()
plt.grid(True)
plt.savefig('backtest_portfolio.png')
plt.show()

# 计算关键指标
final_value = portfolio_values[-1]
roi = (final_value - INITIAL_BALANCE) / INITIAL_BALANCE
annualized_roi = (1 + roi) ** (252 / len(portfolio_values)) - 1  # 假设252个交易日

# 计算最大回撤
peak = INITIAL_BALANCE
max_drawdown = 0
for value in portfolio_values:
    if value > peak:
        peak = value
    drawdown = (peak - value) / peak
    if drawdown > max_drawdown:
        max_drawdown = drawdown

print("\n" + "="*50)
print(f"初始投资: ${INITIAL_BALANCE:,.2f}")
print(f"最终价值: ${final_value:,.2f}")
print(f"总回报率: {roi*100:.2f}%")
print(f"年化回报率: {annualized_roi*100:.2f}%")
print(f"最大回撤: {max_drawdown*100:.2f}%")
print("="*50)

# 保存交易信号
featured_data['signal'] = 0
featured_data['portfolio_value'] = INITIAL_BALANCE
env_save = TradingEnv(featured_data)
state_seq = env_save.reset()
done = False

while not done:
    current_step = env_save.current_step
    state_tensor = torch.FloatTensor(state_seq).unsqueeze(0).to(device)
    
    with torch.no_grad():
        action_probs = model(state_tensor)
        action = torch.argmax(action_probs).item()
    
    featured_data.loc[current_step, 'signal'] = action
    state_seq, _, done, portfolio_value = env_save.step(action)
    featured_data.loc[current_step, 'portfolio_value'] = portfolio_value

# 保存结果
featured_data.to_csv('trading_signals_and_portfolio.csv', index=False)
print("交易信号和组合价值已保存到 'trading_signals_and_portfolio.csv'")