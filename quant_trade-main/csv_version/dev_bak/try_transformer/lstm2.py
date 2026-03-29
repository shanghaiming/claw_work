import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import warnings
import os
import random
import time
from collections import deque
from datetime import datetime
# 忽略特定警告
warnings.filterwarnings("ignore", category=UserWarning, message=".*dropout.*")

# ==================== 1. 全局配置 ====================
DATA_PATH = fr"E:\stock\csv_version\out_analysis_results"
MODEL_SAVE_PATH = fr"E:\stock\csv_version\best_rl_model_{datetime.now().strftime('%Y%m%d')}.pth"
RESULTS_DIR = fr"E:\stock\csv_version\out_analysis_results"
SEQ_LEN = 60
BATCH_SIZE = 128
EPISODES = 1000
INITIAL_BALANCE = 10000
LEARNING_RATE = 0.0001
GAMMA = 0.99
TRAIN_TEST_SPLIT_RATIO = 0.8
TRANSACTION_COST_PCT = 0.0015


# ==================== 2. 数据加载与特征工程 ====================
def load_and_prepare_all_data(path, feature_columns):

    print(f"开始从 {path} 加载所有CSV文件...")
    if not os.path.exists(path): raise FileNotFoundError(f"错误：找不到数据路径 '{path}'。")
    all_files = [os.path.join(path, f) for f in os.listdir(path) if f.endswith('.csv')]
    if not all_files: raise ValueError("错误：在指定路径下没有找到任何 .csv 文件。")
    df_list = [pd.read_csv(file, index_col='trade_date', parse_dates=True) for file in all_files]
    full_df = pd.concat(df_list)
    full_df.sort_index(inplace=True)
    full_df['ts_code'] = full_df['ts_code'].astype(str)
    cols_to_drop = ['circ_mv', 'action', 'support', 'resistance', 'future_5d_return']
    full_df = full_df.drop(columns=[col for col in cols_to_drop if col in full_df.columns], errors='ignore')
    full_df.replace([np.inf, -np.inf], np.nan, inplace=True)
    full_df = full_df.dropna()
    print(f"数据加载和合并完成，共 {len(full_df)} 行。")
    full_df['daily_return'] = full_df.groupby('ts_code')['close'].pct_change().fillna(0)
    valid_features = [col for col in feature_columns if col in full_df.columns]
    print(f"找到 {len(valid_features)} 个有效特征用于训练。")
    scaler = StandardScaler()
    full_df[valid_features] = scaler.fit_transform(full_df[valid_features])
    data_dict = {name: group for name, group in full_df.groupby('ts_code')}
    print(f"数据预处理完成，共处理 {len(data_dict)} 支股票。")
    return data_dict, valid_features, scaler


# ==================== 3. 模型与环境 ====================
class EnhancedLSTM_Policy(nn.Module):
    def __init__(self, input_size, hidden_size, num_actions=3):

        super().__init__()
        self.lstm1 = nn.LSTM(input_size, hidden_size, batch_first=True);
        self.dropout1 = nn.Dropout(0.3)
        self.lstm2 = nn.LSTM(hidden_size, hidden_size // 2, batch_first=True);
        self.dropout2 = nn.Dropout(0.3)
        self.attention = nn.Sequential(nn.Linear(hidden_size // 2, 1), nn.Tanh())
        self.fc = nn.Sequential(
            nn.Linear(hidden_size // 2, 128), nn.ReLU(), nn.Dropout(0.3),
            nn.Linear(128, 64), nn.ReLU(), nn.Linear(64, num_actions))

    def forward(self, x):
        out1, _ = self.lstm1(x);
        out1 = self.dropout1(out1)
        out2, _ = self.lstm2(out1);
        out2 = self.dropout2(out2)
        attention_weights = torch.softmax(self.attention(out2), dim=1)
        context_vector = torch.sum(attention_weights * out2, dim=1)
        action_logits = self.fc(context_vector)
        return torch.softmax(action_logits, dim=-1), attention_weights


class TradingEnv:
    def __init__(self, initial_balance=INITIAL_BALANCE):
        self.data, self.feature_columns = None, None
        self.initial_balance = initial_balance

    def load_new_stock(self, data, feature_columns):
        self.data = data.reset_index(drop=True)
        self.feature_columns = feature_columns
        self.reset()

    def reset(self):
        self.balance = self.initial_balance
        self.shares, self.avg_cost = 0, 0
        self.current_step = SEQ_LEN
        if len(self.data) <= self.current_step + 1:
            raise ValueError(f"数据长度({len(self.data)})不足以进行初始化。")
        self.max_steps = len(self.data) - 2
        self.portfolio_values = [self.initial_balance]
        self.actions = []
        return self._get_state_seq()

    def _get_state_seq(self):
        start_idx = max(0, self.current_step - SEQ_LEN)
        end_idx = self.current_step
        seq_df = self.data.iloc[start_idx:end_idx][self.feature_columns].copy()
        if seq_df.empty: return np.zeros((SEQ_LEN, len(self.feature_columns)))
        first_values = seq_df.iloc[0]
        normalized_seq = seq_df / (first_values + 1e-7) - 1
        normalized_seq.replace([np.inf, -np.inf], 0, inplace=True);
        normalized_seq.fillna(0, inplace=True)
        return normalized_seq.values

    def step(self, action):
        self.actions.append(action)
        current_price = self.data.iloc[self.current_step]['close']
        if action == 1 and self.balance > 0:
            shares_bought = self.balance / current_price
            cost = shares_bought * current_price * (1 + TRANSACTION_COST_PCT)
            total_cost = self.avg_cost * self.shares + cost
            self.shares += shares_bought
            self.avg_cost = total_cost / self.shares if self.shares > 0 else 0
            self.balance = 0
        elif action == 2 and self.shares > 0:
            self.balance += self.shares * current_price * (1 - TRANSACTION_COST_PCT)
            self.shares, self.avg_cost = 0, 0
        self.current_step += 1
        done = self.current_step >= self.max_steps
        next_price = self.data.iloc[self.current_step]['close']
        portfolio_value = self.balance + self.shares * next_price
        self.portfolio_values.append(portfolio_value)
        reward = self.calculate_reward(next_price)
        return self._get_state_seq(), reward, done, portfolio_value

    def calculate_reward(self, current_price):
        reward = 0
        market_return = self.data.iloc[self.current_step]['daily_return']
        if self.shares > 0:
            reward += market_return * 100
            if self.avg_cost > 0:
                unrealized_pnl = (current_price - self.avg_cost) / self.avg_cost
                reward += unrealized_pnl * 10
        else:
            reward -= market_return * 100
        if (self.shares > 0 and market_return > 0.03) or (self.shares == 0 and market_return < -0.03):
            reward += 15
        elif (self.shares > 0 and market_return < -0.03) or (self.shares == 0 and market_return > 0.03):
            reward -= 20
        return reward


# ==================== 4. 训练与回测函数 ====================
def train(train_data_dict, feature_columns, device):
    print("\n开始训练模型...")
    INPUT_DIM, HIDDEN_SIZE, NUM_ACTIONS = len(feature_columns), 256, 3
    model = EnhancedLSTM_Policy(INPUT_DIM, HIDDEN_SIZE, NUM_ACTIONS).to(device)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE, weight_decay=1e-5)
    env = TradingEnv()
    roi_window = deque(maxlen=20)
    best_avg_roi = -np.inf
    stock_codes = list(train_data_dict.keys())
    for episode in range(EPISODES):
        stock_to_train = random.choice(stock_codes)
        env.load_new_stock(train_data_dict[stock_to_train], feature_columns)
        state_seq = env.reset()
        rewards, log_probs = [], []
        done = False
        while not done:
            state_tensor = torch.FloatTensor(state_seq).unsqueeze(0).to(device)
            action_probs, _ = model(state_tensor)
            dist = Categorical(action_probs)
            action = dist.sample()
            log_prob = dist.log_prob(action)
            next_state, reward, done, portfolio_value = env.step(action.item())
            rewards.append(reward)
            log_probs.append(log_prob)
            state_seq = next_state
            if len(rewards) >= BATCH_SIZE or done:
                if len(rewards) > 0:
                    returns = []
                    R = 0
                    for r in reversed(rewards): R = r + GAMMA * R; returns.insert(0, R)
                    returns = torch.tensor(returns).float().to(device)
                    if returns.std() > 1e-7: returns = (returns - returns.mean()) / returns.std()
                    policy_loss = [-log_prob * R for log_prob, R in zip(log_probs, returns)]
                    optimizer.zero_grad()
                    loss = torch.stack(policy_loss).sum()
                    loss.backward()
                    torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
                    optimizer.step()
                    rewards, log_probs = [], []
        final_value = portfolio_value
        roi = (final_value - INITIAL_BALANCE) / INITIAL_BALANCE
        roi_window.append(roi)
        if len(roi_window) == roi_window.maxlen:
            current_avg_roi = np.mean(roi_window)
            if current_avg_roi > best_avg_roi:
                best_avg_roi = current_avg_roi
                torch.save(model.state_dict(), MODEL_SAVE_PATH)
                print(f"新最佳模型已保存，最近{roi_window.maxlen}轮平均ROI: {best_avg_roi * 100:.2f}%")
        print(
            f'Episode {episode + 1}/{EPISODES}, Stock: {stock_to_train}, Portfolio: ${final_value:.2f}, ROI: {roi * 100:.2f}%')
    return model


def backtest(model, test_data_dict, feature_columns, device):
    print("开始回测...")
    model.eval()
    env = TradingEnv()
    all_results = {}
    for stock_code, test_df in test_data_dict.items():
        if  not stock_code.startswith("0"):
            continue
        print(stock_code)
        env.load_new_stock(test_df, feature_columns)
        state_seq = env.reset()
        done = False
        while not done:
            state_tensor = torch.FloatTensor(state_seq).unsqueeze(0).to(device)
            with torch.no_grad():
                action_probs, _ = model(state_tensor)
                action = torch.argmax(action_probs).item()
            state_seq, _, done, _ = env.step(action)
        bnh_df = test_df.iloc[SEQ_LEN:].copy()
        first_day_price = bnh_df['close'].iloc[0]
        shares_bought = INITIAL_BALANCE / first_day_price
        bnh_values = (shares_bought * bnh_df['close']).tolist()
        all_results[stock_code] = {'values': env.portfolio_values, 'actions': env.actions, 'bnh_values': bnh_values}
    return all_results


# ==================== 5. 主程序  ====================
if __name__ == "__main__":
    start_time = time.time()
    if not os.path.exists(RESULTS_DIR):
        os.makedirs(RESULTS_DIR)

    feature_columns = [
        'low', 'amount', 'high', 'close', 'volume', 'open', 'diff', 'dea', 'macd',
        'ma5', 'ma8', 'ma13', 'ma21', 'ma34', 'ma55', 'vr', 'tsma5', 'tsma8',
        'tsma13', 'er', 'var', 'sma', 'std', 'upper', 'lower', 'up_mark',
        'down_mark', 'shadow_ratio', 'wr5', 'wr55', 'ma_trend_change_win1',
        'ma_trend_change_win2', 'cross_events', 'divergence_status',
        'divergence_status_macd', 'divergence_status_vr', 'divergence_status_wr5',
        'trend_direction', 'is_range', 'start_type', 'end_type', 'wave_number',
        'move_type', 'subwaves', 'target'
    ]

    try:
        all_data_dict, valid_feature_columns, scaler = load_and_prepare_all_data(DATA_PATH, feature_columns)
    except (FileNotFoundError, ValueError) as e:
        print(e)
        exit()

    # --- 增加数据长度安全检查 ---
    train_dict, test_dict = {}, {}
    for code, df in all_data_dict.items():

        min_length_required = int(SEQ_LEN / TRAIN_TEST_SPLIT_RATIO) + 2
        if len(df) < min_length_required:
            print(f"警告：股票 {code} 的数据量过小 ({len(df)}行)，已跳过。")
            continue

        split_point = int(len(df) * TRAIN_TEST_SPLIT_RATIO)

        if split_point > SEQ_LEN and (len(df) - split_point) > SEQ_LEN:
            train_dict[code] = df.iloc[:split_point]
            test_dict[code] = df.iloc[split_point:]
        else:
            print(f"警告：股票 {code} 划分后的数据量不足，已跳过。")

    if not train_dict:
        raise ValueError("经过筛选后，没有足够的数据用于训练。请检查文件内容或减少SEQ_LEN。")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备: {device}")
    print(f"最终将使用 {len(train_dict)} 支股票进行训练。")

    try:
        
        if os.path.exists(MODEL_SAVE_PATH):
            print(f"发现已训练的模型，直接加载从 {MODEL_SAVE_PATH}")
            best_model = EnhancedLSTM_Policy(len(valid_feature_columns), 256, 3).to(device)
            best_model.load_state_dict(torch.load(MODEL_SAVE_PATH))
        else:
            print("未发现模型，开始新的训练...")
            trained_model = train(train_dict, valid_feature_columns, device)
            best_model = trained_model

        print("已加载最佳模型")
        backtest_results = backtest(best_model, test_dict, valid_feature_columns, device)

        print("\n" + "=" * 60)
        full_report_path = os.path.join(RESULTS_DIR, 'performance_metrics.txt')
        with open(full_report_path, 'w') as f:
            for stock_code, result in backtest_results.items():
                portfolio_values = result['values'];
                actions = result['actions'];
                bnh_values = result['bnh_values']
                final_value = portfolio_values[-1];
                roi = (final_value - INITIAL_BALANCE) / INITIAL_BALANCE
                report_str = (f"股票 {stock_code}:\n"
                              f"  - 智能体策略 | 最终价值: ${final_value:,.2f} | 总回报率: {roi * 100:.2f}%\n"
                              f"  - 买入持有   | 最终价值: ${bnh_values[-1]:,.2f} | 总回报率: {(bnh_values[-1] / INITIAL_BALANCE - 1) * 100:.2f}%\n"
                              f"{'-' * 30}\n")
                print(report_str);
                f.write(report_str)
                plt.figure(figsize=(14, 7))
                plt.plot(portfolio_values, label='RL Agent Strategy', color='royalblue')
                plt.plot(bnh_values, label='Buy and Hold Strategy', color='darkorange', linestyle='--')
                plt.title(f'Backtest Comparison for {stock_code}');
                plt.xlabel('Time Steps in Test Period');
                plt.ylabel('Value ($)')
                plt.legend();
                plt.grid(True)
                plt.savefig(os.path.join(RESULTS_DIR, f'backtest_comparison_{stock_code}.png'));
                plt.close()

        print("=" * 60)
        print(f"回测完成，结果图表和指标报告已保存到 '{RESULTS_DIR}' 文件夹。")

    except Exception as e:
        print(f"训练或回测过程中发生错误: {e}")
        import traceback

        traceback.print_exc()