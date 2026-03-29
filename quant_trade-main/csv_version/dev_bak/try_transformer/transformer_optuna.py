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
import gc
import optuna  # 导入Optuna
from optuna.trial import TrialState

# 忽略警告
warnings.filterwarnings('ignore')

# 配置设置 - 现在这些将成为超参数搜索空间
class Config:
    SEED = 42
    TRAIN_RATIO = 0.8  # 训练集比例
    
    # 特征参数 (将作为超参数进行优化)
    WINDOW_SIZE = 30  # 时间窗口大小
    FEATURE_DIM = 10  # 特征维度 (优化后)
    
    # GRPO 参数 (将作为超参数进行优化)
    POLICY_LR = 1e-4  # 降低学习率
    VALUE_LR = 5e-4   # 降低学习率
    UE_LR = 5e-5      # 降低学习率
    GAMMA = 0.99  # 折扣因子
    LAMBDA = 0.95  # GAE参数
    BATCH_SIZE = 64
    EPOCHS = 30
    CLIP_EPSILON = 0.2
    
    # 交易参数
    TRANSACTION_FEE = 0.001  # 交易费率
    RISK_FREE_RATE = 0  # 年化无风险利率
    INITIAL_CAPITAL = 10000  # 初始资金
    
    # 设备设置
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    
    # 保存路径
    MODEL_PATH = f'grpo_trading_model_{datetime.now().strftime("%Y%m%d")}_optuna.pth'
    
    # 特征选择
    FEATURE_SELECTION_K = 10  # 选择最重要的K个特征
    
    # Optuna相关设置
    OPTUNA_N_TRIALS = 50  # 要运行的试验次数
    OPTUNA_TIMEOUT = 3600 * 600  # 6小时超时

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

# 交易环境 (优化后的动作空间)
class TradingEnv:
    def __init__(self, data, window_size, transaction_fee=0.001):
        # 确保数据包含action列
        if 'action' not in data.columns:
            raise ValueError("数据必须包含'action'列")
        self.data = data
        self.window_size = window_size
        self.transaction_fee = transaction_fee
        self.reset()
        
    def reset(self):
        self.current_step = self.window_size
        self.position = 1  # 初始为持有状态 (1)
        self.cash = Config.INITIAL_CAPITAL
        self.stock_value = Config.INITIAL_CAPITAL / self.data.iloc[self.window_size-1]['close'] # 初始满仓
        self.portfolio_value = [Config.INITIAL_CAPITAL] * (self.window_size + 1)
        self.actions = [1] * (self.window_size + 1)  # 初始动作为持有
        self.done = False
        self.consecutive_correct = 0   # 连续正确预测次数
        self.consecutive_hold = 0      # 连续持仓天数
        return self.get_state()
    
    def get_state(self):
        start_idx = self.current_step - self.window_size
        end_idx = self.current_step
        state = self.data.iloc[start_idx:end_idx][Config.feature_cols].values
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
        actions = [self.env.actions[-1]]
        dates = [self.env.data.iloc[self.env.window_size]['Date']]
        
        while not done:
            state_tensor = torch.FloatTensor(state).unsqueeze(0).to(Config.device)
            
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
        trade_cnt = np.sum(np.diff(actions) != 0)  # 计算交易次数
        
        # 保存结果
        self.results = {
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
        self.results_r = {
            'dates': dates,            
            'actions': actions
        }
        pd.DataFrame(self.results_r).to_csv('trading_results_optimized.csv', index=False)
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
        plt.title('仓位变化 (0=现金, 1=持有, 2=股票)')
        plt.xlabel('日期')
        plt.ylabel('仓位')
        plt.yticks([0, 1, 2], ['现金', '持有', '股票'])
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
        print(f"交易次数: {self.results['trade_cnt']}")
    
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
        
        # 经验池
        self.memory = []
        #self.episode_states = []
        #self.episode_rewards = []
        self.epsilon = 0.3
        self.epsilon_decay = 0.995
        self.min_epsilon = 0.05

    def decay_epsilon(self):
        self.epsilon = max(self.min_epsilon, self.epsilon * self.epsilon_decay)
        
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

# 使用Optuna进行超参数优化的目标函数
def objective(trial):
    """Optuna目标函数，用于超参数优化"""
    # 设置随机种子
    set_seed(Config.SEED)
    
    # 定义超参数搜索空间
    params = {
        'WINDOW_SIZE': trial.suggest_categorical('WINDOW_SIZE', [20, 30, 40, 50]),
        'POLICY_LR': trial.suggest_loguniform('POLICY_LR', 1e-5, 1e-3),
        'VALUE_LR': trial.suggest_loguniform('VALUE_LR', 1e-5, 1e-3),
        'UE_LR': trial.suggest_loguniform('UE_LR', 1e-6, 1e-4),
        'GAMMA': trial.suggest_uniform('GAMMA', 0.9, 0.999),
        'LAMBDA': trial.suggest_uniform('LAMBDA', 0.9, 0.999),
        'BATCH_SIZE': trial.suggest_categorical('BATCH_SIZE', [32, 64, 128]),
        'CLIP_EPSILON': trial.suggest_uniform('CLIP_EPSILON', 0.1, 0.3),
        'FEATURE_SELECTION_K': trial.suggest_categorical('FEATURE_SELECTION_K', [5, 10, 15]),
        'd_model': trial.suggest_categorical('d_model', [32, 64, 128]),
        'nhead': trial.suggest_categorical('nhead', [2, 4, 8]),
        'num_layers': trial.suggest_int('num_layers', 1, 3),
        'dropout': trial.suggest_uniform('dropout', 0.1, 0.5),
    }
    
    # 更新配置
    for key, value in params.items():
        setattr(Config, key, value)
    
    # 1. 加载数据
    ts_code = "000063.SZ" 
    file_path = fr"E:\stock\backtest\data\analyzed\5min\{ts_code}_analysis.csv"
    df = pd.read_csv(file_path, index_col='trade_date', parse_dates=True)
    
    # 移除不必要的列
    df = df.drop(columns=['circ_mv', 'support', 'resistance', 'ts_code'], errors='ignore')
    
    # 添加必要特征
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(20, min_periods=5).std()
    df['Date'] = df.index
    df = df.dropna()
    
    # 检查数据中的NaN值
    print("检查数据中的NaN值...")
    nan_counts = df.isna().sum()
    print(nan_counts[nan_counts > 0])
    
    # 如果有NaN值，填充为0
    df = df.fillna(0)
    
    print(f"数据加载完成: {len(df)} 行, {len(df.columns)} 列")
    
    # 2. 特征工程和选择
    all_features = [col for col in df.columns if col not in ['Date', 'returns', 'volatility', 'action']]
    
    # 分割训练集和测试集
    train_size = int(len(df) * Config.TRAIN_RATIO)
    train_data = df.iloc[:train_size]
    test_data = df.iloc[train_size:]
    
    # 特征选择 (只在训练集上进行)
    Config.feature_cols = select_features(
        train_data, 
        all_features, 
        k=Config.FEATURE_SELECTION_K
    )
    
    print(f"使用特征: {Config.feature_cols}, 数量: {len(Config.feature_cols)}")
    
    # 3. 数据标准化
    scaler = StandardScaler()
    train_data[Config.feature_cols] = scaler.fit_transform(train_data[Config.feature_cols])
    test_data[Config.feature_cols] = scaler.transform(test_data[Config.feature_cols])
    
    # 检查标准化后的数据是否有NaN或无穷大
    if np.isinf(train_data[Config.feature_cols]).any().any() or np.isnan(train_data[Config.feature_cols]).any().any():
        print("警告: 标准化后的数据包含NaN或无穷大值!")
        # 替换NaN和无穷大
        train_data[Config.feature_cols] = train_data[Config.feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
        test_data[Config.feature_cols] = test_data[Config.feature_cols].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    print(f"数据集大小: 总共 {len(df)} 天, 训练集 {len(train_data)} 天, 测试集 {len(test_data)} 天")
    
    # 4. 创建环境和模型
    train_env = TradingEnv(train_data, Config.WINDOW_SIZE, Config.TRANSACTION_FEE)
    
    feature_extractor = FeatureExtractor(
        input_dim=len(Config.feature_cols),
        d_model=Config.d_model,
        nhead=Config.nhead,
        num_layers=Config.num_layers,
        dropout=Config.dropout
    ).to(Config.device)
    
    agent = GRPOAgent(
        feature_extractor=feature_extractor,
        state_dim=Config.d_model,  # 特征提取器的输出维度
        action_dim=3,  # 0=卖出, 1=持有, 2=买入
        config=Config
    )
    
    # 5. 训练模型
    print("开始使用GRPO训练模型...")
    
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
        state = train_env.reset()
        done = False
        total_reward = 0
        step_count = 0
        portfolio_value = Config.INITIAL_CAPITAL
        # 每轮训练使用的临时存储
        episode_states = []  # 改为局部变量
        episode_rewards = []  # 改为局部变量
        
        while not done:
            # 检查状态是否包含NaN
            if np.isnan(state).any():
                state = np.nan_to_num(state, nan=0.0)

            # 获取当前专家信号
            expert_action = train_env.data.iloc[train_env.current_step]['action']    
            # 选择动作
            action, log_prob, value = agent.act(state, expert_action=expert_action)
            
            # 执行动作
            next_state, reward, done, portfolio_value = train_env.step(action)
            total_reward += reward
            step_count += 1
            
            # 存储经验
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
        
        # 向Optuna报告中间值，允许提前终止
        trial.report(current_avg_reward, epoch)
        
        # 处理提前终止
        if trial.should_prune():
            raise optuna.TrialPruned()
    
    # 返回最终的平均奖励作为优化目标
    return current_avg_reward

# 主程序
def main():
    # 创建Optuna study对象
    study = optuna.create_study(
        direction="maximize",  # 我们希望最大化平均奖励
        sampler=optuna.samplers.TPESampler(),  # 使用TPE采样器
        pruner=optuna.pruners.MedianPruner()  # 使用中值剪枝器
    )
    
    # 开始超参数优化
    study.optimize(objective, n_trials=Config.OPTUNA_N_TRIALS, timeout=Config.OPTUNA_TIMEOUT)
    
    # 输出最佳试验结果
    print("最佳试验:")
    trial = study.best_trial
    print(f"  值: {trial.value}")
    print("  参数: ")
    for key, value in trial.params.items():
        print(f"    {key}: {value}")
    
    # 可视化优化过程
    try:
        fig = optuna.visualization.plot_optimization_history(study)
        fig.show()
        
        fig = optuna.visualization.plot_param_importances(study)
        fig.show()
    except:
        print("无法显示可视化图表，可能缺少依赖")
    
    # 使用最佳超参数重新训练最终模型
    print("\n使用最佳超参数训练最终模型...")
    
    # 更新配置为最佳参数
    for key, value in trial.params.items():
        setattr(Config, key, value)
    
    # 设置最终训练的轮数
    Config.EPOCHS = 500  # 增加训练轮数以获得更好的性能
    
    # 重新运行目标函数，但这次不进行剪枝，并且保存最终模型
    final_reward = objective(optuna.trial.FixedTrial(trial.params))
    print(f"最终模型训练完成，平均奖励: {final_reward}")
    
    # 加载测试数据进行最终评估
    ts_code = "000063.SZ" 
    file_path = fr"E:\stock\backtest\data\analyzed\5min\{ts_code}_analysis.csv"
    df = pd.read_csv(file_path, index_col='trade_date', parse_dates=True)
    
    # 移除不必要的列
    df = df.drop(columns=['circ_mv', 'support', 'resistance', 'ts_code'], errors='ignore')
    
    # 添加必要特征
    df['returns'] = df['close'].pct_change()
    df['volatility'] = df['returns'].rolling(20, min_periods=5).std()
    df['Date'] = df.index
    df = df.dropna().fillna(0)
    
    # 分割训练集和测试集
    train_size = int(len(df) * Config.TRAIN_RATIO)
    test_data = df.iloc[train_size:]
    
    # 特征选择 (使用与训练时相同的特征)
    all_features = [col for col in df.columns if col not in ['Date', 'returns', 'volatility', 'action']]
    Config.feature_cols = select_features(
        df.iloc[:train_size], 
        all_features, 
        k=Config.FEATURE_SELECTION_K
    )
    
    # 数据标准化
    scaler = StandardScaler()
    train_data = df.iloc[:train_size]
    test_data[Config.feature_cols] = scaler.fit_transform(train_data[Config.feature_cols])
    
    # 创建测试环境
    test_env = TradingEnv(test_data, Config.WINDOW_SIZE, Config.TRANSACTION_FEE)
    
    # 创建特征提取器
    feature_extractor = FeatureExtractor(
        input_dim=len(Config.feature_cols),
        d_model=Config.d_model,
        nhead=Config.nhead,
        num_layers=Config.num_layers,
        dropout=Config.dropout
    ).to(Config.device)
    
    # 创建代理并加载最佳模型
    agent = GRPOAgent(
        feature_extractor=feature_extractor,
        state_dim=Config.d_model,
        action_dim=3,
        config=Config
    )
    
    # 加载最佳模型
    agent.load_model(Config.MODEL_PATH)
    
    # 在测试集上运行回测
    print("\n在测试集上运行回测...")
    backtester = Backtester(test_env, agent.policy_net, agent.feature_extractor)
    test_results = backtester.run_backtest()
    
    # 绘制结果
    backtester.plot_results()
    
    # 与买入持有策略对比
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
    print(f"{'交易次数':<15} | {test_results['trade_cnt']:>15} | {'N/A':>15}")

if __name__ == "__main__":
    main()