import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest, f_regression
from torch.distributions import Categorical
import os
import warnings
import math 
import random
from datetime import datetime
import logging
import gc

# 忽略警告
warnings.filterwarnings('ignore')

# 配置设置
class Config:
    SEED = 42
    TRAIN_RATIO = 0.8  # 训练集比例
    
    # 特征参数
    WINDOW_SIZE = 30  # 时间窗口大小
    FEATURE_DIM = 10  # 特征维度 (优化后)
    
    # GRPO 参数
    POLICY_LR = 1e-4  # 降低学习率
    VALUE_LR = 5e-4   # 降低学习率
    UE_LR = 5e-5      # 降低学习率
    GAMMA = 0.99  # 折扣因子
    LAMBDA = 0.95  # GAE参数
    BATCH_SIZE = 64
    EPOCHS = 3000
    CLIP_EPSILON = 0.2
    
    # 交易参数
    TRANSACTION_FEE = 0.001  # 交易费率
    RISK_FREE_RATE = 0  # 年化无风险利率
    INITIAL_CAPITAL = 10000  # 初始资金
    
    # 设备设置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 保存路径
    MODEL_PATH = f'grpo_trading_model_{datetime.now().strftime("%Y%m%d")}_multi_optmem.pth'
    #MODEL_PATH = f'grpo_trading_model_20250820_multi_optmem.pth'
    
    # 特征选择
    FEATURE_SELECTION_K = 10  # 选择最重要的K个特征
    DATA_PATH = r"E:\stock\backtest\data\analyzed\5min"  # 数据目录路径
    STOCK_CODES = []  # 股票代码列表
    TEST_STOCKS = []  # 测试股票列表


# 添加内存清理函数
def cleanup_memory():
    """清理内存"""
    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

# 设置随机种子
def set_seed(seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    random.seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

set_seed(Config.SEED)

# 交易环境 (优化后的动作空间)
class TradingEnv:
    def __init__(self, window_size, transaction_fee=0.001):
        self.window_size = window_size
        self.transaction_fee = transaction_fee
        self.data = None
        self.feature_cols = None
        
    def load_new_stock(self, data, feature_cols):
        """加载新股票数据"""
        self.data = data
        self.feature_cols = feature_cols
        self.reset()
        
    def reset(self):
        if self.data is None:
            raise ValueError("未加载股票数据")
            
        self.current_step = self.window_size
        self.position = 1  # 初始为持有状态 (1)
        self.cash = Config.INITIAL_CAPITAL
        self.stock_value = Config.INITIAL_CAPITAL / self.data.iloc[self.window_size-1]['close']  # 初始满仓
        self.portfolio_value = [Config.INITIAL_CAPITAL] * (self.window_size + 1)
        self.actions = [1] * (self.window_size + 1)  # 初始动作为持有
        self.done = False
        self.consecutive_correct = 0   # 连续正确预测次数
        self.consecutive_hold = 0      # 连续持仓天数
        return self.get_state()
    
    def get_state(self):
        start_idx = self.current_step - self.window_size
        end_idx = self.current_step
        state = self.data.iloc[start_idx:end_idx][self.feature_cols].values
        return state
    
    def step(self, action):
        prev_position = self.position
        execute_trade = False
        
        # 解释动作:
        # 0: 卖出 (转为现金)
        # 1: 持有 (保持当前仓位)
        # 2: 买入 (转为满仓)
        
        if action == 0:  # 卖出
            new_position = 0
            if prev_position == 1:  # 之前持有股票，需要卖出
                execute_trade = True
        elif action == 2:  # 买入
            new_position = 1
            if prev_position == 0:  # 之前持有现金，需要买入
                execute_trade = True
        else:  # 持有
            new_position = prev_position
        
        self.position = new_position
        
        # 更新连续持仓计数器
        if new_position == 1:
            self.consecutive_hold += 1
        else:
            self.consecutive_hold = 0

        # 获取当日价格信息
        current_price = self.data.iloc[self.current_step]['close']
        current_return = self.data.iloc[self.current_step]['returns']
        
        # 计算交易成本
        transaction_cost = 0
        if execute_trade:
            # 计算交易金额
            trade_amount = self.portfolio_value[-1]
            transaction_cost = trade_amount * self.transaction_fee
        
        # 更新投资组合价值
        if new_position == 1:  # 持有股票
            if execute_trade:  # 执行买入
                # 扣除交易成本后买入
                self.stock_value = (self.portfolio_value[-1] - transaction_cost) / current_price
                portfolio_value = self.stock_value * current_price
            else:  # 继续持有
                portfolio_value = self.stock_value * current_price
        else:  # 持有现金
            if execute_trade:  # 执行卖出
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
        """改进的奖励函数 - 基于专家信号"""
        # 获取专家信号
        expert_action = self.data.iloc[self.current_step]['action']
        
        # 基础收益
        portfolio_return = (portfolio_value / self.portfolio_value[-1]) - 1
        
        # 专家信号奖励
        expert_reward = 0.0
        
        # 情况1：专家标记为低点（action=2），鼓励买入
        if expert_action == 2:
            if action == 2:  # 在低点买入 - 强奖励
                expert_reward = 0.5
            elif action == 0:  # 在低点卖出 - 强惩罚
                expert_reward = -0.5
        
        # 情况2：专家标记为高点（action=1），鼓励卖出
        elif expert_action == 1:
            if action == 0:  # 在高点卖出 - 强奖励
                expert_reward = 0.5
            elif action == 2:  # 在高点买入 - 强惩罚
                expert_reward = -0.5
        
        # 情况3：非关键位置（action=0），中性反馈
        else:
            if action == 2 and market_return > 0:  # 在普通位置正确买入
                expert_reward = 0.1
            elif action == 0 and market_return < 0:  # 在普通位置正确卖出
                expert_reward = 0.1
        
        # 交易成本惩罚（只在实际交易发生时）
        transaction_penalty = 0
        if action != 1 and prev_position != self.position:  # 实际执行了交易
            transaction_penalty = -0.001
        
        # 组合奖励 = 基础收益 + 专家信号奖励 + 交易成本惩罚
        reward = portfolio_return * 100 + expert_reward + transaction_penalty
        
        # 添加少量市场收益奖励
        if self.position == 1:  # 持有时获得市场收益
            reward += market_return * 5
        
        # 限制奖励范围
        return np.clip(reward, -2, 2)
# 特征选择函数
def select_features(train_data, feature_cols, target_col='returns', k=10):
    """选择最重要的K个特征"""
    X = train_data[feature_cols]
    # 使用次日收益率作为目标
    y = train_data[target_col].shift(-1).fillna(0)
    
    # 选择与目标相关性最高的特征
    selector = SelectKBest(score_func=f_regression, k=k)
    selector.fit(X.iloc[:-1], y.iloc[:-1])  # 避免使用最后一天的NaN
    
    selected_features = X.columns[selector.get_support()]
    print(f"Selected features: {list(selected_features)}")
    return selected_features

# 加载和准备所有数据
def load_and_prepare_all_data(path):
    print(f"开始从 {path} 加载所有CSV文件...")
    if not os.path.exists(path): 
        raise FileNotFoundError(f"错误：找不到数据路径 '{path}'。")
    
    all_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    if not all_files: 
        raise ValueError("错误：在指定路径下没有找到任何 .csv 文件。")
    
    df_list = []
    for file in all_files:
        try:
            temp_df = pd.read_csv(file)
            
            # 从文件名提取股票代码
            filename = os.path.basename(file)
            ts_code = filename.split('_')[0]
            temp_df['ts_code'] = ts_code
            
            # 添加必要特征
            temp_df['returns'] = temp_df['close'].pct_change()
            temp_df['volatility'] = temp_df['returns'].rolling(20, min_periods=5).std()
            temp_df['Date'] = pd.to_datetime(temp_df['trade_date'])
            temp_df = temp_df.drop(columns=['circ_mv', 'support', 'resistance', 'future_5d_return'], errors='ignore')
            temp_df = temp_df.dropna()
            
            # 添加到列表
            df_list.append(temp_df)
            
            # 记录股票代码
            if ts_code not in Config.STOCK_CODES:
                Config.STOCK_CODES.append(ts_code)
                
        except Exception as e:
            print(f"警告：加载或处理文件 {os.path.basename(file)} 失败: {e}")
    
    if not df_list: 
        raise ValueError("错误：未能成功加载任何数据。")
    
    # 合并所有数据
    full_df = pd.concat(df_list, ignore_index=True)
    
    
    # 确定特征列
    all_features = [col for col in full_df.columns if col not in ['Date', 'action', 'returns', 'volatility', 'ts_code', 'trade_date']]
    
    # 分割训练集和测试集
    train_size = int(len(full_df) * Config.TRAIN_RATIO)
    train_data = full_df.iloc[:train_size]
    test_data = full_df.iloc[train_size:]
    
    # 特征选择 (只在训练集上进行)
    selected_features = select_features(
        train_data, 
        all_features, 
        k=Config.FEATURE_SELECTION_K
    )
    
    print(f"使用特征: {list(selected_features)}, 数量: {len(selected_features)}")
    
    # 标准化数据
    scaler = StandardScaler()
    full_df[selected_features] = scaler.fit_transform(full_df[selected_features])
    
    # 按股票代码分组
    data_dict = {}
    for ts_code, group in full_df.groupby('ts_code'):
        # 确保数据长度足够
        if len(group) > Config.WINDOW_SIZE * 2:
            data_dict[ts_code] = group
            # 添加测试股票
            if ts_code not in Config.TEST_STOCKS and group['Date'].min() < pd.Timestamp('2023-01-01'):
                Config.TEST_STOCKS.append(ts_code)
        else:
            print(f"跳过股票 {ts_code}: 数据长度不足 ({len(group)} 条记录)")
    
    print(f"数据预处理完成，共处理 {len(data_dict)} 支股票。")
    print(f"可用测试股票: {Config.TEST_STOCKS}")
    
    return data_dict, list(selected_features), scaler

# Transformer 特征提取器 (优化版)
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
        self.layer_norm = nn.LayerNorm(d_model)
        self.dropout = nn.Dropout(dropout)
        
    class PositionalEncoding(nn.Module):
        def __init__(self, d_model, dropout=0.1, max_len=5000):
            super().__init__()
            self.dropout = nn.Dropout(p=dropout)
            
            div_term = torch.exp(torch.arange(0, d_model, 2) * (-math.log(10000.0) / d_model))
            position = torch.arange(max_len).unsqueeze(1)
            pe = torch.zeros(max_len, 1, d_model)
            pe[:, 0, 0::2] = torch.sin(position * div_term)
            pe[:, 0, 1::2] = torch.cos(position * div_term)
            self.register_buffer('pe', pe)

        def forward(self, x):
            x = x + self.pe[:x.size(0)]
            return self.dropout(x)
        
    def forward(self, x):
        # 安全处理NaN
        if torch.isnan(x).any():
            x = torch.nan_to_num(x, nan=0.0)
        
        # 检查输入维度
        if x.dim() == 2:
            # 添加批次维度: [seq_len, features] -> [1, seq_len, features]
            x = x.unsqueeze(0)
        elif x.dim() == 3:
            # 已经是批次形式: [batch, seq_len, features]
            pass
        else:
            raise ValueError(f"输入维度 {x.dim()} 不支持")
            
        # 1. 嵌入层
        # 输入形状: [batch_size, seq_len, input_dim]
        # 输出形状: [batch_size, seq_len, d_model]
        x = self.embedding(x) * math.sqrt(self.d_model)
        
        # 2. 调整维度顺序 [batch, seq_len, features] -> [seq_len, batch, features]
        x = x.permute(1, 0, 2)
        
        # 3. 添加位置编码
        x = self.pos_encoder(x)
        
        # 4. Transformer编码
        x = self.transformer(x)
        
        # 5. 取最后时间步的特征 [seq_len, batch, features] -> [batch, features]
        last_output = x[-1]
        
        # 6. 安全归一化
        last_output = torch.nan_to_num(last_output, nan=0.0)
        
        # 7. 应用层归一化
        normalized_output = self.layer_norm(last_output)
        
        # 8. 添加Dropout防止过拟合
        normalized_output = self.dropout(normalized_output)
        
        # 9. 数值稳定性处理
        normalized_output = torch.clamp(normalized_output, min=-10, max=10)
        
        return normalized_output

# 不确定性估计器 (替代高斯过程)
class UncertaintyEstimator(nn.Module):
    def __init__(self, input_dim, hidden_dim=64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),  # 添加层归一化
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.LayerNorm(hidden_dim),  # 添加层归一化
            nn.Linear(hidden_dim, 2)  # 输出均值和方差
        )
        
    def forward(self, x):
        output = self.net(x)
        mean = output[:, 0]
        log_var = output[:, 1]
        var = torch.exp(log_var) + 1e-6  # 防止方差为零
        return mean, var

# 策略网络 (增强版)
class PolicyNet(nn.Module):
    def __init__(self, input_dim, output_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 256),
            nn.LayerNorm(256),
            nn.ReLU(),  # 使用ReLU代替GELU
            nn.Dropout(0.1),  # 添加Dropout
            nn.Linear(256, 128),
            nn.LayerNorm(128),
            nn.ReLU(),  # 使用ReLU代替GELU
            nn.Dropout(0.1),  # 添加Dropout
            nn.Linear(128, 64),
            nn.LayerNorm(64),
            nn.ReLU(),  # 使用ReLU代替GELU
            nn.Dropout(0.1),  # 添加Dropout
            nn.Linear(64, output_dim)
        )
        
    def forward(self, x):
        x = self.net(x)
        # 数值稳定性处理
        x = torch.clamp(x, min=-10, max=10)
        return x

# 价值网络 (增强版)
class ValueNet(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(input_dim, 128),
            nn.ReLU(),
            nn.Dropout(0.1),  # 添加Dropout
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.1),  # 添加Dropout
            nn.Linear(64, 1)
        )
        
    def forward(self, x):
        x = self.net(x)
        # 数值稳定性处理
        x = torch.clamp(x, min=-100, max=100)
        return x

# GRPO 代理 (使用不确定性估计器)
class GRPOAgent:
    def __init__(self, feature_extractor, state_dim, action_dim, config):
        self.feature_extractor = feature_extractor
        self.config = config
        self.state_dim = state_dim
        self.action_dim = action_dim
        
        # 策略网络
        self.policy_net = PolicyNet(state_dim, action_dim).to(config.device)
        
        # 价值网络
        self.value_net = ValueNet(state_dim).to(config.device)
        
        # 不确定性估计器
        self.uncertainty_estimator = UncertaintyEstimator(state_dim).to(config.device)
        
        # 优化器
        self.policy_optim = optim.Adam(
            list(feature_extractor.parameters()) + list(self.policy_net.parameters()),
            lr=config.POLICY_LR,
            weight_decay=1e-5  # 添加权重衰减
        )
        
        self.value_optim = optim.Adam(
            self.value_net.parameters(),
            lr=config.VALUE_LR,
            weight_decay=1e-5  # 添加权重衰减
        )
        
        self.ue_optim = optim.Adam(
            self.uncertainty_estimator.parameters(),
            lr=config.UE_LR,
            weight_decay=1e-5  # 添加权重衰减
        )
        # 经验池 - 限制大小防止内存泄漏
        self.memory = []
        self.max_memory_size = 100000  # 限制内存大小
        self.epsilon = 0.3
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.05

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)

    def add_to_memory(self, state, action, log_prob, reward, value):
        """添加经验到内存，限制内存大小"""
        if len(self.memory) >= self.max_memory_size:
            # 移除最旧的10%的经验
            remove_count = int(self.max_memory_size * 0.1)
            self.memory = self.memory[remove_count:]
        self.memory.append((state, action, log_prob, reward, value))

    def act(self, state, expert_action=None):
        # 确保状态是二维数组 [window_size, features]
        state = np.array(state)
        if state.ndim == 1:
            state = state.reshape(1, -1)
        
        # 转换为张量并添加批次维度
        state_tensor = torch.FloatTensor(state).to(self.config.device)
        
        with torch.no_grad():
            features = self.feature_extractor(state_tensor)
            
            # 数值稳定性检查
            if torch.isnan(features).any():
                features = torch.nan_to_num(features, nan=0.0)
            
            logits = self.policy_net(features)
            
            # 数值稳定性检查
            if torch.isnan(logits).any():
                logits = torch.nan_to_num(logits, nan=0.0)
            
            dist = Categorical(logits=logits)
            
            # 探索-利用平衡
            #探索-利用平衡
            if np.random.rand() < self.epsilon:
                # 如果有专家信号，使用专家信号引导探索
                if expert_action is not None:
                    if expert_action == 2:  # 低点区域
                        action = np.random.choice([2, 1], p=[0.8, 0.2])
                    elif expert_action == 1:  # 高点区域
                        action = np.random.choice([0, 1], p=[0.8, 0.2])
                    else:  # 中性区域
                        action = np.random.randint(3)
                else:
                    # 没有专家信号，完全随机探索
                    action = np.random.randint(3)
                action_tensor = torch.tensor([action], device=logits.device)
                log_prob = dist.log_prob(action_tensor).item()
            else:
                action_tensor = dist.sample()
                action = action_tensor.item()
                log_prob = dist.log_prob(action_tensor).item()
            
            value = self.value_net(features).item()
        
        return action, log_prob, value

    def update_uncertainty(self, states, rewards):
        """更新不确定性估计器"""
        # 确保状态是三维数组 [batch_size, window_size, features]
        states = np.array(states)
        if states.ndim == 2:
            # 添加批次维度
            states = states.reshape(1, states.shape[0], states.shape[1])
        
        states_tensor = torch.FloatTensor(states).to(self.config.device)
        rewards_tensor = torch.FloatTensor(rewards).to(self.config.device)
        
        # 训练不确定性估计器
        self.uncertainty_estimator.train()
        for _ in range(3):
            features = self.feature_extractor(states_tensor)
            
            # 数值稳定性检查
            if torch.isnan(features).any():
                features = torch.nan_to_num(features, nan=0.0)
            
            mean, var = self.uncertainty_estimator(features)
            loss = F.gaussian_nll_loss(mean, rewards_tensor, var)
            
            self.ue_optim.zero_grad()
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.uncertainty_estimator.parameters(), 1.0)
            
            self.ue_optim.step()
        
        self.uncertainty_estimator.eval()
        return mean.detach().cpu().numpy(), var.detach().cpu().numpy()

    def update_policy(self):
        """使用GRPO更新策略"""
        if len(self.memory) < self.config.BATCH_SIZE:
            return
        
        # 从内存中提取数据
        states, actions, old_log_probs, rewards, values = zip(*self.memory)
        
        # 确保状态是三维数组 [batch_size, window_size, features]
        states = np.array(states)
        if states.ndim == 2:
            # 添加批次维度
            states = states.reshape(1, states.shape[0], states.shape[1])
        
        # 转换为numpy数组
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
        
        # 使用不确定性估计器预测奖励分布
        states_tensor = torch.FloatTensor(states).to(self.config.device)
        
        # 数值稳定性检查
        if torch.isnan(states_tensor).any():
            states_tensor = torch.nan_to_num(states_tensor, nan=0.0)
        
        with torch.no_grad():
            features = self.feature_extractor(states_tensor)
            
            # 数值稳定性检查
            if torch.isnan(features).any():
                features = torch.nan_to_num(features, nan=0.0)
        
        # 预测奖励分布
        mu, var = self.uncertainty_estimator(features)
        sigma = torch.sqrt(var)
        
        # 根据不确定性调整奖励
        adjusted_rewards = mu + 0.5 * sigma  # 鼓励探索不确定性高的区域
        
        # 转换为张量并移动到正确设备
        states_tensor = torch.FloatTensor(states).to(self.config.device)
        actions_tensor = torch.LongTensor(actions).to(self.config.device)
        old_log_probs_tensor = torch.FloatTensor(old_log_probs).to(self.config.device)
        advantages_tensor = torch.FloatTensor(advantages).to(self.config.device)
        adjusted_rewards_tensor = adjusted_rewards.detach()  # 不需要梯度
        
        # 策略更新
        self.feature_extractor.train()
        self.policy_net.train()
        self.value_net.train()
        
        for _ in range(3):  # 多次更新
            # 获取特征和logits
            features = self.feature_extractor(states_tensor)
            
            # 数值稳定性检查
            if torch.isnan(features).any():
                features = torch.nan_to_num(features, nan=0.0)
            
            logits = self.policy_net(features)
            
            # 数值稳定性检查
            if torch.isnan(logits).any():
                logits = torch.nan_to_num(logits, nan=0.0)
            
            # 创建分布
            dist = Categorical(logits=logits)
            
            # 计算对数概率和熵
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
            
            # 数值稳定性检查
            if torch.isnan(values_pred).any():
                values_pred = torch.nan_to_num(values_pred, nan=0.0)
            
            value_loss = 0.5 * (values_pred - adjusted_rewards_tensor.detach()).pow(2).mean()
            
            # 价值函数正则化
            value_loss += 0.001 * (values_pred ** 2).mean()
            
            # 总损失
            loss = policy_loss + value_loss - 0.01 * entropy
            
            # 梯度下降
            self.policy_optim.zero_grad()
            self.value_optim.zero_grad()
            loss.backward()
            
            # 梯度裁剪
            torch.nn.utils.clip_grad_norm_(self.feature_extractor.parameters(), 1.0)
            torch.nn.utils.clip_grad_norm_(self.policy_net.parameters(), 1.0)
            torch.nn.utils.clip_grad_norm_(self.value_net.parameters(), 1.0)
            
            self.policy_optim.step()
            self.value_optim.step()
        
        self.feature_extractor.eval()
        self.policy_net.eval()
        self.value_net.eval()
        
        # 清空内存
        self.memory = []

    def save_model(self, path):
        """保存模型"""
        torch.save({
            'feature_extractor': self.feature_extractor.state_dict(),
            'policy_net': self.policy_net.state_dict(),
            'value_net': self.value_net.state_dict(),
            'uncertainty_estimator': self.uncertainty_estimator.state_dict(),
        }, path)
        print(f"模型已保存至 {path}")
    
    def load_model(self, path):
        """加载模型"""
        if os.path.exists(path):
            checkpoint = torch.load(path)
            self.feature_extractor.load_state_dict(checkpoint['feature_extractor'])
            self.policy_net.load_state_dict(checkpoint['policy_net'])
            self.value_net.load_state_dict(checkpoint['value_net'])
            self.uncertainty_estimator.load_state_dict(checkpoint['uncertainty_estimator'])
            print(f"已从 {path} 加载模型")
            return True
        return False

# 回测系统 (支持多股票测试)
class Backtester:
    def __init__(self, policy_net, feature_extractor):
        self.policy_net = policy_net
        self.feature_extractor = feature_extractor
        self.results = {}
        
    def run_backtest(self, env):
        """在指定环境上运行回测"""
        state = env.reset()
        done = False
        portfolio_values = [env.portfolio_value[-1]]
        actions = [env.actions[-1]]
        dates = [env.data.iloc[env.window_size]['Date']]
        
        while not done:
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(Config.device)
            
            with torch.no_grad():
                features = self.feature_extractor(state_tensor)
                logits = self.policy_net(features)
                action = torch.argmax(logits).item()
            
            next_state, _, done, portfolio_value = env.step(action)
            portfolio_values.append(portfolio_value)
            actions.append(action)
            dates.append(env.data.iloc[env.current_step]['Date'])
            state = next_state
        
        # 计算性能指标
        returns = pd.Series(portfolio_values).pct_change().dropna()
        cumulative_returns = (returns + 1).cumprod() - 1
        max_drawdown = self.calculate_max_drawdown(portfolio_values)
        sharpe_ratio = self.calculate_sharpe_ratio(returns)
        trade_cnt = np.sum(np.diff(actions) != 0)  # 计算交易次数
        
        # 保存结果
        stock_results = {
            'dates': dates,
            'portfolio_values': portfolio_values,
            'actions': actions,
            'returns': returns,
            'cumulative_returns': cumulative_returns,
            'max_drawdown': max_drawdown,
            'sharpe_ratio': sharpe_ratio,
            'final_value': portfolio_values[-1],
            'trade_cnt': trade_cnt
        }
        
        return stock_results
    
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
    
    def plot_results(self, results, stock_name):
        """绘制回测结果"""
        if not results:
            print("请先运行回测")
            return
            
        plt.figure(figsize=(15, 10))
        
        # 投资组合价值
        plt.subplot(2, 1, 1)
        plt.plot(results['dates'], results['portfolio_values'], label='投资组合价值')
        plt.title(f'{stock_name} - 投资组合价值变化')
        plt.xlabel('日期')
        plt.ylabel('价值')
        plt.legend()
        plt.grid(True)
        
        # 仓位变化
        plt.subplot(2, 1, 2)
        plt.step(results['dates'], results['actions'], where='post', label='仓位')
        plt.title(f'{stock_name} - 仓位变化 (0=现金, 1=持有, 2=股票)')
        plt.xlabel('日期')
        plt.ylabel('仓位')
        plt.yticks([0, 1, 2], ['现金', '持有', '股票'])
        plt.legend()
        plt.grid(True)
        
        plt.tight_layout()
        plt.savefig(f'{stock_name}_backtest_results.png')
        plt.show()
        
        # 打印性能指标
        print(f"\n{stock_name} 回测结果 ({len(results['portfolio_values'])} 个交易日):")
        print(f"初始资金: ${Config.INITIAL_CAPITAL:,.2f}")
        print(f"最终投资组合价值: ${results['final_value']:,.2f}")
        print(f"总收益率: {((results['final_value']/Config.INITIAL_CAPITAL)-1)*100:.2f}%")
        print(f"最大回撤: {results['max_drawdown']*100:.2f}%")
        print(f"年化夏普比率: {results['sharpe_ratio']:.2f}")
        print(f"交易次数: {results['trade_cnt']}")
    
    def buy_and_hold_strategy(self, data):
        """买入持有策略作为基准"""
        values = [Config.INITIAL_CAPITAL]
        window_size = Config.WINDOW_SIZE
        
        for i in range(window_size, len(data)):
            if i == window_size:
                # 在开始时全仓买入
                price = data.iloc[i]['close']
                shares = Config.INITIAL_CAPITAL / price
                value = shares * price
            else:
                current_price = data.iloc[i]['close']
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
    
    def run_multi_stock_test(self, data_dict, feature_cols, num_stocks=5):
        """在多支股票上运行回测"""
        self.results = {}
        test_stocks = random.sample(Config.TEST_STOCKS, min(num_stocks, len(Config.TEST_STOCKS)))
        
        for stock in test_stocks:
            print(f"\n在 {stock} 上运行回测...")
            env = TradingEnv(Config.WINDOW_SIZE, Config.TRANSACTION_FEE)
            env.load_new_stock(data_dict[stock], feature_cols)
            
            # 运行策略回测
            strategy_results = self.run_backtest(env)
            self.results[stock] = strategy_results
            
            # 运行买入持有策略
            bh_results = self.buy_and_hold_strategy(data_dict[stock])
            
            # 绘制结果
            self.plot_results(strategy_results, stock)
            
            # 保存结果到CSV
            results_df = pd.DataFrame({
                'Date': strategy_results['dates'],
                'Portfolio_Value': strategy_results['portfolio_values'],
                'Action': strategy_results['actions']
            })
            results_df.to_csv(f'{stock}_trading_results.csv', index=False)
            
            # 打印对比结果
            print("\n策略性能对比:")
            print(f"{'指标':<15} | {'GRPO策略':>15} | {'买入持有':>15}")
            print("-" * 50)
            print(f"{'初始资金':<15} | ${Config.INITIAL_CAPITAL:>15,.2f} | ${Config.INITIAL_CAPITAL:>15,.2f}")
            print(f"{'最终价值':<15} | ${strategy_results['final_value']:>15,.2f} | ${bh_results['final_value']:>15,.2f}")
            print(f"{'总收益率':<15} | {((strategy_results['final_value']/Config.INITIAL_CAPITAL)-1)*100:>15.2f}% | {((bh_results['final_value']/Config.INITIAL_CAPITAL)-1)*100:>15.2f}%")
            print(f"{'最大回撤':<15} | {strategy_results['max_drawdown']*100:>15.2f}% | {bh_results['max_drawdown']*100:>15.2f}%")
            print(f"{'夏普比率':<15} | {strategy_results['sharpe_ratio']:>15.2f} | {bh_results['sharpe_ratio']:>15.2f}")
        
        return self.results

# 主程序
def main():
    # 1. 加载所有股票数据
    print("加载所有股票数据...")
    try:
        data_dict, feature_cols, scaler = load_and_prepare_all_data(Config.DATA_PATH)
        print(f"成功加载 {len(data_dict)} 支股票数据")
    except Exception as e:
        print(f"加载数据时出错: {e}")
        return
    
    if not data_dict:
        print("错误：没有可用的股票数据")
        return
        
    # 2. 创建环境和模型
    train_env = TradingEnv(Config.WINDOW_SIZE, Config.TRANSACTION_FEE)
    
    feature_extractor = FeatureExtractor(
        input_dim=len(feature_cols),
        d_model=64,
        nhead=4,
        num_layers=2,
        dropout=0.2
    ).to(Config.device)
    
    agent = GRPOAgent(
        feature_extractor=feature_extractor,
        state_dim=64,  # 特征提取器的输出维度
        action_dim=3,  # 0=卖出, 1=持有, 2=买入
        config=Config
    )
    
    # 3. 训练模型
    print("开始使用GRPO训练模型...")
    
    # 尝试加载已有模型
    if not agent.load_model(Config.MODEL_PATH):
        train_rewards = []
        avg_rewards = []
        best_avg_reward = -float('inf')
        
        # 学习率调度器
        scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            agent.policy_optim, 
            mode='max', 
            factor=0.5, 
            patience=10
        )
        
        for epoch in range(Config.EPOCHS):
            # 随机选择一支股票
            stock_to_train = random.choice(list(data_dict.keys()))
            print(f"Epoch {epoch+1}/{Config.EPOCHS}: 训练股票 {stock_to_train}")
            
            # 每轮训练使用的临时存储
            episode_states = []  # 改为局部变量
            episode_rewards = []  # 改为局部变量
            # 加载股票数据到环境
            train_env.load_new_stock(data_dict[stock_to_train], feature_cols)
            
            # 重置环境
            state = train_env.reset()
            done = False
            total_reward = 0
            step_count = 0
            portfolio_value = Config.INITIAL_CAPITAL
            
            while not done:
                # 检查状态是否包含NaN
                if np.isnan(state).any():
                    state = np.nan_to_num(state, nan=0.0)
                # 获取当前专家信号
                expert_action = train_env.data.iloc[train_env.current_step]['action'] 
                    
                # 选择动作
                action, log_prob, value = agent.act(state, expert_action)
                
                # 执行动作
                next_state, reward, done, portfolio_value = train_env.step(action)
                total_reward += reward
                step_count += 1
                
                # 存储经验
                #agent.add_to_memory(state, action, log_prob, reward, value)
                agent.memory.append((state, action, log_prob, reward, value))
                episode_states.append(state)
                episode_rewards.append(reward)
                
                # 定期更新不确定性估计器
                if step_count % 10 == 0 and len(episode_states) >= 10:
                    states = np.array(episode_states[-100:])
                    rewards = np.array(episode_rewards[-100:])
                    
                    # 检查奖励是否有NaN
                    if np.isnan(rewards).any():
                        rewards = np.nan_to_num(rewards, nan=0.0)
                    
                    agent.update_uncertainty(states, rewards)
                
                # 定期更新策略
                if step_count % 50 == 0 and len(agent.memory) >= Config.BATCH_SIZE:
                    agent.update_policy()
                
                # 更新状态
                state = next_state
            
            # 每轮结束更新
            if len(agent.memory) >= Config.BATCH_SIZE:
                agent.update_policy()
            
            # 衰减探索率
            agent.decay_epsilon()
            
            # 记录训练进度
            train_rewards.append(total_reward)
            
            # 计算最近10轮的平均奖励
            if len(train_rewards) >= 10:
                current_avg_reward = np.mean(train_rewards[-10:])
            else:
                current_avg_reward = np.mean(train_rewards) if train_rewards else total_reward
            avg_rewards.append(current_avg_reward)
            
            # 更新学习率
            scheduler.step(total_reward)
            
            # 保存最佳模型
            if current_avg_reward > best_avg_reward:
                best_avg_reward = current_avg_reward
                agent.save_model(Config.MODEL_PATH)
                print(f"保存最佳模型 (平均奖励: {current_avg_reward:.2f})")
            
            # 打印进度
            print(f"Epoch {epoch+1}/{Config.EPOCHS}, 总奖励: {total_reward:.2f}, 组合价值: ${portfolio_value:,.2f}, 探索率: {agent.epsilon:.3f}")
            
            # 检查模型参数是否有NaN
            for name, param in agent.policy_net.named_parameters():
                if torch.isnan(param).any():
                    print(f"警告: 策略网络参数 {name} 包含NaN值!")
                    # 尝试修复: 将NaN替换为0
                    param.data = torch.nan_to_num(param.data, nan=0.0)
            
            for name, param in agent.value_net.named_parameters():
                if torch.isnan(param).any():
                    print(f"警告: 价值网络参数 {name} 包含NaN值!")
                    # 尝试修复: 将NaN替换为0
                    param.data = torch.nan_to_num(param.data, nan=0.0)
            # 在训练循环中定期调用
            if epoch % 10 == 0:
                cleanup_memory()
        
        # 绘制训练奖励曲线
        plt.figure(figsize=(10, 5))
        plt.plot(train_rewards, label='每轮奖励')
        plt.plot(avg_rewards, label='平均奖励(10轮)', linewidth=2)
        plt.title('训练奖励曲线')
        plt.xlabel('Epoch')
        plt.ylabel('总奖励')
        plt.legend()
        plt.grid(True)
        plt.savefig('training_rewards.png')
        plt.show()
    
    # 4. 在多支测试股票上运行回测
    print("\n在多支测试股票上运行回测...")
    backtester = Backtester(agent.policy_net, agent.feature_extractor)
    test_results = backtester.run_multi_stock_test(data_dict, feature_cols, num_stocks=5)
    
    # 5. 生成综合报告
    print("\n生成综合回测报告...")
    final_values = []
    total_returns = []
    max_drawdowns = []
    sharpe_ratios = []
    trade_counts = []
    
    for stock, results in test_results.items():
        final_values.append(results['final_value'])
        total_returns.append((results['final_value']/Config.INITIAL_CAPITAL)-1)
        max_drawdowns.append(results['max_drawdown'])
        sharpe_ratios.append(results['sharpe_ratio'])
        trade_counts.append(results['trade_cnt'])
        
        print(f"{stock}: 最终价值 ${results['final_value']:,.2f}, 收益率 {total_returns[-1]*100:.2f}%")
    
    # 计算平均性能指标
    avg_final_value = np.mean(final_values)
    avg_total_return = np.mean(total_returns)
    avg_max_drawdown = np.mean(max_drawdowns)
    avg_sharpe_ratio = np.mean(sharpe_ratios)
    avg_trade_count = np.mean(trade_counts)
    
    print("\n综合性能报告:")
    print(f"测试股票数量: {len(test_results)}")
    print(f"平均最终价值: ${avg_final_value:,.2f}")
    print(f"平均总收益率: {avg_total_return*100:.2f}%")
    print(f"平均最大回撤: {avg_max_drawdown*100:.2f}%")
    print(f"平均夏普比率: {avg_sharpe_ratio:.2f}")
    print(f"平均交易次数: {avg_trade_count:.1f}")

if __name__ == "__main__":
    main()