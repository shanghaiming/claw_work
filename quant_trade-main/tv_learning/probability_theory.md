# 概率论与统计推断在量化交易中的应用

---

## 1. 条件概率与贝叶斯推断

### 核心概念
- **条件概率**: P(A|B) = P(A∩B) / P(B) — 在B已发生条件下A发生的概率
- **贝叶斯定理**: P(H|D) = P(D|H) * P(H) / P(D) — 根据观测数据更新假设概率
- **先验/后验**: 先验是交易前的信念，后验是看到数据后的更新信念

### 交易应用
1. **信号可靠性评估**: 
   - 先验: 某RSI金叉信号的默认胜率(如55%)
   - 似然: 在当前市场状态下该信号的历史表现
   - 后验: 更新后的胜率估计
   
2. **动态止损调整**:
   ```python
   def bayesian_stop_loss(prior_win_rate, recent_wins, recent_losses):
       # Beta分布共轭先验
       alpha = prior_win_rate * 100 + recent_wins
       beta = (1 - prior_win_rate) * 100 + recent_losses
       posterior_mean = alpha / (alpha + beta)
       # 胜率下降时收紧止损
       stop_multiplier = max(0.5, min(2.0, posterior_mean / prior_win_rate))
       return base_stop * stop_multiplier
   ```

3. **多信号融合**:
   - 每个信号给出独立的 P(上涨|信号)
   - 用朴素贝叶斯或贝叶斯网络融合多信号
   - 融合后概率 > 阈值才执行交易

---

## 2. 随机过程与金融时间序列

### 核心概念
- **随机游走**: P(t) = P(t-1) + ε, ε ~ N(0,σ²)
- **几何布朗运动(GBM)**: dS = μSdt + σSdW (W是维纳过程)
- **马尔可夫性质**: 未来状态只依赖当前状态，与历史无关

### 交易应用
1. **市场状态转换(马尔可夫链)**:
   ```python
   # 定义市场状态
   states = ['bull', 'bear', 'range']
   # 转移矩阵(从历史数据估计)
   transition_matrix = {
       'bull': {'bull': 0.7, 'bear': 0.1, 'range': 0.2},
       'bear': {'bull': 0.1, 'bear': 0.6, 'range': 0.3},
       'range': {'bull': 0.2, 'bear': 0.2, 'range': 0.6},
   }
   # 当前状态 → 最可能的状态路径 → 调整策略参数
   ```

2. **蒙特卡洛模拟**:
   ```python
   def monte_carlo_price(S0, mu, sigma, T, n_sims=10000):
       dt = 1/252
       prices = np.zeros((n_sims, int(T*252)))
       prices[:, 0] = S0
       for t in range(1, prices.shape[1]):
           z = np.random.standard_normal(n_sims)
           prices[:, t] = prices[:, t-1] * np.exp((mu - 0.5*sigma**2)*dt + sigma*np.sqrt(dt)*z)
       return prices
   
   # 计算VaR: 5%分位数就是95%置信度的VaR
   final_prices = monte_carlo_price(current_price, mu, sigma, 20)
   var_95 = np.percentile(final_prices[:, -1], 5)
   ```

3. **均值回归检测**: 
   -ADF检验判断价格序列是否平稳
   - Hurst指数: H<0.5均值回归, H=0.5随机游走, H>0.5趋势

---

## 3. 统计检验与过拟合防范

### 核心概念
- **假设检验**: H0(无效) vs H1(策略有效)
- **p值**: 在H0下观察到当前或更极端结果的概率
- **多重检验修正**: 测试多个策略时，Bonferroni修正 p_threshold = 0.05/N

### 交易应用
1. **策略显著性检验**:
   ```python
   from scipy import stats
   def strategy_significance(returns, benchmark_returns):
       # t检验: 策略超额收益是否显著非零
       excess = returns - benchmark_returns
       t_stat, p_value = stats.ttest_1samp(excess, 0)
       # 要求p < 0.05 且 夏普 > 1.0
       sharpe = excess.mean() / excess.std() * np.sqrt(252)
       return p_value < 0.05 and sharpe > 1.0
   ```

2. **过拟合检测**:
   - **样本外测试**: 训练集60%, 验证集20%, 测试集20%
   - **Walk-forward验证**: 滚动窗口训练和测试
   - **Bootstrap**: 对收益序列重采样1000次，检查策略在重采样数据上的表现分布
   - **CSCV(Combinatorially Symmetric Cross-Validation)**: 将数据分N段，取所有C(N,N/2)种训练/测试组合

3. **最小样本量**:
   - 交易次数 < 30: 统计不显著
   - 月度收益 > 60个月(5年): 才能可靠评估
   - 经验法则: 至少2个完整牛熊周期

---

## 4. 概率分布与风险管理

### 核心概念
- **正态分布局限**: 金融收益有肥尾(峰度>3)和偏度
- **学生t分布**: 比正态分布更好的收益建模(自由度越低，尾部越肥)
- **极值理论(EVT)**: 专门建模分布的极端尾部

### 交易应用
1. **肥尾效应**:
   ```python
   def estimate_tail_risk(returns, confidence=0.99):
       # 用广义帕累托分布(GPD)拟合尾部
       from scipy.stats import genpareto
       threshold = np.percentile(returns, 5)  # 取最差的5%
       tail_data = threshold - returns[returns < threshold]
       params = genpareto.fit(tail_data)
       # 计算极端VaR
       evt_var = genpareto.ppf(confidence, *params)
       return evt_var
   ```

2. **Copula函数** (多资产依赖):
   ```python
   # Gaussian Copula: 捕获资产间的非线性相关性
   # 用途: 组合风险计算、配对交易
   # 步骤:
   # 1. 将每个资产的收益转换为均匀分布(经验CDF)
   # 2. 用Copula函数建模联合分布
   # 3. 从联合分布采样计算组合风险
   ```

3. **波动率建模**:
   - **历史波动率**: σ = std(returns) * sqrt(252)
   - **EWMA**: σ²_t = λ*σ²_{t-1} + (1-λ)*r²_{t-1}, λ=0.94
   - **GARCH(1,1)**: σ²_t = ω + α*r²_{t-1} + β*σ²_{t-1}

---

## 5. 信息论与交易

### 核心概念
- **熵**: H(X) = -Σ p(x)log(p(x)) — 不确定性的度量
- **互信息**: I(X;Y) = H(X) - H(X|Y) — 两个变量共享的信息量
- **KL散度**: D_KL(P||Q) = Σ P(x)log(P(x)/Q(x)) — 两个分布的差异

### 交易应用
1. **特征选择**:
   ```python
   from sklearn.feature_selection import mutual_info_regression
   # 计算每个技术指标与未来收益的互信息
   mi_scores = mutual_info_regression(features_df, future_returns)
   # 选择互信息最高的特征
   ```

2. **市场状态检测** (KL散度):
   ```python
   def detect_regime_change(recent_returns, historical_dist):
       # 用KL散度衡量当前分布与历史分布的偏离
       from scipy.stats import entropy
       recent_hist, _ = np.histogram(recent_returns, bins=50, density=True)
       hist_hist, _ = np.histogram(historical_dist, bins=50, density=True)
       kl_div = entropy(recent_hist + 1e-10, hist_hist + 1e-10)
       return kl_div  # 值越大，市场状态变化越大
   ```

3. **市场不确定性指标**:
   - 用滚动窗口计算收益分布的熵
   - 高熵 = 高不确定性 = 减少仓位
   - 低熵 = 明确方向 = 增加仓位

---

## 6. 贝叶斯优化与参数调优

### 核心概念
- **贝叶斯优化**: 用概率模型(高斯过程)指导超参数搜索
- **采集函数**: Expected Improvement, Upper Confidence Bound
- **比网格搜索高效**: 用更少的试验找到更优参数

### 交易应用
1. **策略参数优化**:
   ```python
   from skopt import gp_minimize
   from skopt.space import Real, Integer
   
   def objective(params):
       ma_fast, ma_slow, rsi_period = params
       strategy = MAStrategy(data, ma_fast=int(ma_fast), ma_slow=int(ma_slow))
       signals = strategy.generate_signals()
       sharpe = compute_sharpe(signals)
       return -sharpe  # 最小化负夏普
   
   space = [Integer(5, 30, name='ma_fast'),
            Integer(20, 120, name='ma_slow'),
            Integer(7, 28, name='rsi_period')]
   
   result = gp_minimize(objective, space, n_calls=50, random_state=42)
   ```

2. **概率校准**:
   - 策略输出的"买入概率"需要校准
   - 用Platt Scaling或Isotonic Regression将原始分数映射到真实概率
   - 校准后的概率可以直接用于凯利公式计算仓位

3. **凯利公式**:
   ```python
   def kelly_fraction(win_prob, avg_win, avg_loss):
       """计算最优仓位比例"""
       b = avg_win / avg_loss  # 盈亏比
       f = (win_prob * b - (1 - win_prob)) / b
       return max(0, f)  # 不允许做空
   # 实际使用: kelly * 0.5 (半凯利) 降低风险
   ```
