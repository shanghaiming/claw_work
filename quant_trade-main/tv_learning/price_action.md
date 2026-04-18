# 价格行为 (Price Action) 交易理论

---

## 1. K线形态与市场心理

### 单根K线形态
| 形态 | 特征 | 含义 | 量化条件 |
|------|------|------|----------|
| 锤子线 | 下影线>实体2倍,上影线极短 | 下跌中可能反转 | `lower_shadow > 2*body AND upper_shadow < 0.1*range` |
| 流星线 | 上影线>实体2倍,下影线极短 | 上涨中可能反转 | `upper_shadow > 2*body AND lower_shadow < 0.1*range` |
| 十字星 | 实体极小(<范围5%) | 犹豫不决,可能变盘 | `body < 0.05 * range` |
| 大阳线 | 实体>范围70%,收盘>开盘 | 强势买方 | `body > 0.7*range AND close > open` |
| 大阴线 | 实体>范围70%,收盘<开盘 | 强势卖方 | `body > 0.7*range AND close < open` |

### 多根K线组合
| 形态 | 组成 | 含义 |
|------|------|------|
| 看涨吞没 | 前阴后阳,阳线完全包住阴线 | 空头力竭,多头接管 |
| 看跌吞没 | 前阳后阴,阴线完全包住阳线 | 多头力竭,空头接管 |
| 晨星 | 长阴+小实体(缺口)+长阳 | 底部反转三兵 |
| 暮星 | 长阳+小实体(缺口)+长阴 | 顶部反转三鸦 |

### 量化实现
```python
def detect_candlestick_patterns(df):
    """检测K线形态"""
    o, h, l, c = df['open'], df['high'], df['low'], df['close']
    body = abs(c - o)
    total_range = h - l
    upper_shadow = h - np.maximum(o, c)
    lower_shadow = np.minimum(o, c) - l
    
    patterns = {}
    # 锤子线(出现在下跌趋势中)
    patterns['hammer'] = (lower_shadow > 2 * body) & (upper_shadow < 0.1 * total_range)
    # 看涨吞没
    patterns['bullish_engulf'] = (c.shift(1) < o.shift(1)) & (c > o) & (c > o.shift(1)) & (o < c.shift(1))
    # 十字星
    patterns['doji'] = body < 0.05 * total_range
    return patterns
```

### 统计有效性注意
- 单纯K线形态的胜率通常在50-55%之间，不够高
- **必须结合位置**(支撑阻力位附近)和**趋势背景**(顺势形态更有效)
- 形态+确认(下一根K线验证)可提升胜率到60%+

---

## 2. 趋势结构与道氏理论

### 核心概念
- **上升趋势**: Higher Highs (HH) + Higher Lows (HL)
- **下降趋势**: Lower Highs (LH) + Lower Lows (LL)
- **趋势反转**: HH/HL 被打破 → 结构改变

### 量化识别算法
```python
def identify_market_structure(df, pivot_length=5):
    """识别市场结构(HH/HL/LH/LL)"""
    # 1. 找摆动高点和摆动低点
    highs = df['high'].values
    lows = df['low'].values
    
    swing_highs = []
    swing_lows = []
    
    for i in range(pivot_length, len(highs) - pivot_length):
        if highs[i] == max(highs[i-pivot_length:i+pivot_length+1]):
            swing_highs.append((i, highs[i]))
        if lows[i] == min(lows[i-pivot_length:i+pivot_length+1]):
            swing_lows.append((i, lows[i]))
    
    # 2. 判断结构
    structure = []
    for i in range(1, len(swing_highs)):
        hh = swing_highs[i][1] > swing_highs[i-1][1]  # 更高的高
        for j in range(1, len(swing_lows)):
            hl = swing_lows[j][1] > swing_lows[j-1][1]  # 更高的低
            if hh and hl:
                structure.append('uptrend')
            elif not hh and not hl:
                structure.append('downtrend')
            else:
                structure.append('ranging')
    
    return swing_highs, swing_lows, structure
```

### 趋势强度量化
```python
def trend_strength(df, period=20):
    """用ADX量化趋势强度"""
    # ADX > 25: 趋势明确
    # ADX < 20: 震荡
    # 方向: +DI > -DI 做多, 反之做空
    pass

def trend_quality(df, ma_period=50):
    """趋势质量评分"""
    # 1. 价格在MA上方/下方的比例
    above_ma = (df['close'] > df['close'].rolling(ma_period).mean()).mean()
    # 2. MA斜率
    ma = df['close'].rolling(ma_period).mean()
    slope = (ma.iloc[-1] - ma.iloc[-20]) / ma.iloc[-20]
    # 3. R平方(价格与MA的拟合度)
    # 综合评分 0-100
    score = above_ma * 50 + min(abs(slope) * 500, 50)
    return score
```

---

## 3. 支撑阻力与供需区

### 核心概念
- **支撑位**: 价格多次反弹的价位区域(买方聚集)
- **阻力位**: 价格多次回落的价位区域(卖方聚集)
- **供需区**: 机构大量建仓/平仓的价格区域

### 量化识别
```python
def find_support_resistance(df, n_touches=3, tolerance=0.02):
    """识别支撑阻力位"""
    # 1. 找所有摆动高点和低点
    pivot_points = []
    for i in range(2, len(df)-2):
        if df['high'].iloc[i] == max(df['high'].iloc[i-2:i+3]):
            pivot_points.append(df['high'].iloc[i])
        if df['low'].iloc[i] == min(df['low'].iloc[i-2:i+3]):
            pivot_points.append(df['low'].iloc[i])
    
    # 2. 聚类相近的价格点
    levels = []
    pivot_points.sort()
    i = 0
    while i < len(pivot_points):
        cluster = [pivot_points[i]]
        j = i + 1
        while j < len(pivot_points) and pivot_points[j] - pivot_points[i] < tolerance * pivot_points[i]:
            cluster.append(pivot_points[j])
            j += 1
        if len(cluster) >= n_touches:
            levels.append(np.mean(cluster))
        i = j
    
    return levels

def find_supply_demand_zones(df, lookback=50):
    """识别供需区"""
    zones = []
    # 供给区: 大阴线之前的价格区域(机构卖出区)
    # 需求区: 大阳线之前的价格区域(机构买入区)
    
    for i in range(lookback, len(df)):
        body_ratio = abs(df['close'].iloc[i] - df['open'].iloc[i]) / (df['high'].iloc[i] - df['low'].iloc[i] + 1e-10)
        vol_ratio = df['volume'].iloc[i] / df['volume'].iloc[i-5:i].mean()
        
        if body_ratio > 0.7 and vol_ratio > 1.5:  # 大实体+放量
            if df['close'].iloc[i] > df['open'].iloc[i]:  # 大阳线 → 需求区
                zones.append({
                    'type': 'demand',
                    'high': max(df['open'].iloc[i], df['close'].iloc[i]),
                    'low': min(df['open'].iloc[i], df['close'].iloc[i]),
                    'strength': vol_ratio
                })
            else:  # 大阴线 → 供给区
                zones.append({
                    'type': 'supply',
                    'high': max(df['open'].iloc[i], df['close'].iloc[i]),
                    'low': min(df['open'].iloc[i], df['close'].iloc[i]),
                    'strength': vol_ratio
                })
    
    return zones
```

### 支撑阻力转化的概率
- 强阻力被突破后变为强支撑(反之亦然)
- 突破有效性: 收盘价连续2天在突破位之上/下
- 假突破概率: 约30-40%, 需要成交量确认降低假突破

---

## 4. 威科夫理论 (Wyckoff)

### 累积阶段 (Accumulation)
1. **PS** (Preliminary Support): 初步支撑,放量下跌减速
2. **SC** (Selling Climax): 恐慌性抛售,巨量
3. **AR** (Automatic Rally): 空头回补反弹
4. **ST** (Secondary Test): 再次测试SC低点,缩量
5. **Spring**: 假跌破SC低点后快速反弹(主力吸筹完成)
6. **SOS** (Sign of Strength): 放量突破阻力
7. **LPS** (Last Point of Support): 回测突破位

### 派发阶段 (Distribution) — 镜像对称

### 量化识别
```python
def detect_wyckoff_accumulation(df, window=100):
    """检测威科夫累积模式"""
    recent = df.tail(window)
    
    # SC: 近期最低点附近的巨量
    sc_idx = recent['low'].idxmin()
    sc_volume = recent.loc[sc_idx, 'volume']
    avg_volume = recent['volume'].mean()
    is_sc = sc_volume > 2 * avg_volume
    
    # Spring: 价格跌破SC低点后快速反弹
    sc_low = recent.loc[sc_idx, 'low']
    after_sc = recent.loc[sc_idx:]
    spring = after_sc[after_sc['low'] < sc_low]
    is_spring = len(spring) > 0 and after_sc.iloc[-1]['close'] > sc_low
    
    # SOS: 放量突破AR高点
    ar_high = after_sc.iloc[:10]['high'].max()  # AR高点
    current_price = recent.iloc[-1]['close']
    is_sos = current_price > ar_high and recent.iloc[-1]['volume'] > avg_volume
    
    return {
        'has_climax': is_sc,
        'has_spring': is_spring,
        'has_sos': is_sos,
        'accumulation_score': sum([is_sc, is_spring, is_sos]) / 3
    }
```

---

## 5. Smart Money Concepts (SMC)

### 核心概念

#### Order Block (订单块)
- **定义**: 大幅波动前的最后一个反向K线(多头OB=大涨前最后一个阴线,空头OB反之)
- **量化**: 检测大阳线/大阴线，取其前一根反色K线的区间

```python
def find_order_blocks(df, min_body_ratio=0.6, min_vol_ratio=1.5):
    """识别订单块"""
    obs = []
    body = abs(df['close'] - df['open'])
    total_range = df['high'] - df['low']
    vol_ma = df['volume'].rolling(20).mean()
    
    for i in range(1, len(df)-1):
        is_large = body.iloc[i] / total_range.iloc[i] > min_body_ratio
        is_high_vol = df['volume'].iloc[i] > min_vol_ratio * vol_ma.iloc[i]
        
        if is_large and is_high_vol:
            if df['close'].iloc[i] > df['open'].iloc[i]:  # 大阳线
                # 前一根阴线作为需求OB
                if df['close'].iloc[i-1] < df['open'].iloc[i-1]:
                    obs.append({
                        'type': 'bullish_ob',
                        'high': max(df['open'].iloc[i-1], df['close'].iloc[i-1]),
                        'low': min(df['open'].iloc[i-1], df['close'].iloc[i-1]),
                        'index': i-1
                    })
            else:  # 大阴线
                if df['close'].iloc[i-1] > df['open'].iloc[i-1]:
                    obs.append({
                        'type': 'bearish_ob',
                        'high': max(df['open'].iloc[i-1], df['close'].iloc[i-1]),
                        'low': min(df['open'].iloc[i-1], df['close'].iloc[i-1]),
                        'index': i-1
                    })
    return obs
```

#### Fair Value Gap (FVG)
- **定义**: 三根K线之间的缺口 — 第一根高点 < 第三根低点(看涨FVG)
- **量化**: `high[i-1] < low[i+1]` (bullish) 或 `low[i-1] > high[i+1]` (bearish)

```python
def find_fvg(df):
    """识别公允价值缺口"""
    fvg_list = []
    for i in range(1, len(df)-1):
        # 看涨FVG: 前一根高点 < 后一根低点
        if df['high'].iloc[i-1] < df['low'].iloc[i+1]:
            fvg_list.append({
                'type': 'bullish_fvg',
                'top': df['low'].iloc[i+1],
                'bottom': df['high'].iloc[i-1],
                'mid': (df['low'].iloc[i+1] + df['high'].iloc[i-1]) / 2,
                'index': i
            })
        # 看跌FVG
        elif df['low'].iloc[i-1] > df['high'].iloc[i+1]:
            fvg_list.append({
                'type': 'bearish_fvg',
                'top': df['low'].iloc[i-1],
                'bottom': df['high'].iloc[i+1],
                'mid': (df['low'].iloc[i-1] + df['high'].iloc[i+1]) / 2,
                'index': i
            })
    return fvg_list
```

#### BOS (Break of Structure) 与 CHoCH (Change of Character)
- **BOS**: 同向结构突破(上升趋势中HH被突破) — 趋势延续
- **CHoCH**: 反向结构突破(上升趋势中前低被跌破) — 趋势可能反转

```python
def detect_bos_choch(swing_highs, swing_lows):
    """检测BOS和CHoCH"""
    events = []
    for i in range(1, len(swing_highs)):
        prev_high = swing_highs[i-1][1]
        curr_high = swing_highs[i][1]
        
        if curr_high > prev_high:
            events.append(('BOS_bull', swing_highs[i][0], curr_high))
        elif curr_high < prev_high:
            # 可能是CHoCH,检查是否打破了前一个higher high序列
            events.append(('CHoCH_bear', swing_highs[i][0], curr_high))
    return events
```

#### Liquidity Sweep (流动性扫荡)
- **定义**: 价格突破前高/前低(触发止损),然后快速反向
- **目的**: 机构获取流动性后反向操作

```python
def detect_liquidity_sweep(df, swing_highs, swing_lows, reversal_pct=0.003):
    """检测流动性扫荡"""
    sweeps = []
    
    for sh_idx, sh_price in swing_highs:
        # 检查后续是否有价格扫过这个高点后反转
        after = df.iloc[sh_idx+1:sh_idx+11]
        for j, row in after.iterrows():
            if row['high'] > sh_price:  # 突破了前高
                # 检查是否反转(收盘回到前高下方)
                if row['close'] < sh_price * (1 - reversal_pct):
                    sweeps.append({
                        'type': 'high_sweep',
                        'level': sh_price,
                        'sweep_price': row['high'],
                        'close': row['close'],
                        'index': j
                    })
                    break
    
    return sweeps
```

#### Premium/Discount Zone
- **均衡点** = 当前摆动区间的50%(斐波那契0.5)
- **Premium Zone**: 均衡点上方 — 做空区域
- **Discount Zone**: 均衡点下方 — 做多区域

```python
def premium_discount_zone(df, swing_length=50):
    """计算Premium/Discount区域"""
    recent_high = df['high'].rolling(swing_length).max().iloc[-1]
    recent_low = df['low'].rolling(swing_length).min().iloc[-1]
    equilibrium = (recent_high + recent_low) / 2
    
    current_price = df['close'].iloc[-1]
    zone = 'premium' if current_price > equilibrium else 'discount'
    zone_ratio = (current_price - recent_low) / (recent_high - recent_low)
    
    return {
        'zone': zone,
        'equilibrium': equilibrium,
        'premium_zone': (equilibrium, recent_high),
        'discount_zone': (recent_low, equilibrium),
        'price_position': zone_ratio  # 0=底部, 1=顶部
    }
```

---

## 6. 市场微观结构

### 订单流与Delta Volume
```python
def compute_cvd(df):
    """累计成交量差(Cumulative Volume Delta)近似"""
    # 用K线方向近似估算(无逐笔数据时)
    buy_vol = np.where(df['close'] > df['open'], df['volume'], 0)
    sell_vol = np.where(df['close'] < df['open'], df['volume'], 0)
    delta = buy_vol - sell_vol
    cvd = delta.cumsum()
    return cvd, delta
```

### VWAP交易
```python
def compute_vwap(df, anchor='session'):
    """计算VWAP"""
    typical_price = (df['high'] + df['low'] + df['close']) / 3
    vwap = (typical_price * df['volume']).cumsum() / df['volume'].cumsum()
    
    # VWAP标准差带
    deviation = np.sqrt(((typical_price - vwap)**2 * df['volume']).cumsum() / df['volume'].cumsum())
    upper = vwap + deviation
    lower = vwap - deviation
    
    return vwap, upper, lower
```

### Footprint分析(无逐笔数据的近似方法)
```python
def approximate_footprint(df):
    """用OHLCV数据近似足迹分析"""
    # 上影线成交量(卖压)
    upper_wick_vol = (df['high'] - np.maximum(df['open'], df['close'])) / (df['high'] - df['low'] + 1e-10) * df['volume']
    # 下影线成交量(买压)
    lower_wick_vol = (np.minimum(df['open'], df['close']) - df['low']) / (df['high'] - df['low'] + 1e-10) * df['volume']
    # 实体成交量(方向性)
    body_vol = abs(df['close'] - df['open']) / (df['high'] - df['low'] + 1e-10) * df['volume']
    
    return {
        'selling_pressure': upper_wick_vol,
        'buying_pressure': lower_wick_vol,
        'directional_volume': body_vol
    }
```

---

## 7. 价格行为量化策略框架

### 综合入场规则设计
```python
class PriceActionStrategy(BaseStrategy):
    """基于PA的综合策略框架"""
    
    def generate_signals(self):
        signals = []
        df = self.data
        
        # 1. 识别市场结构
        swing_highs, swing_lows, structure = identify_market_structure(df)
        
        # 2. 计算Premium/Discount区域
        zone_info = premium_discount_zone(df)
        
        # 3. 寻找订单块
        order_blocks = find_order_blocks(df)
        
        # 4. 寻找FVG
        fvg_list = find_fvg(df)
        
        # 5. 对每根K线检查入场条件
        for i in range(20, len(df)):
            price = df['close'].iloc[i]
            
            # 做多条件: Discount区 + 需求OB + 看涨FVG + BOS确认
            buy_conditions = [
                zone_info['zone'] == 'discount',
                any(ob['type'] == 'bullish_ob' and ob['low'] < price < ob['high'] for ob in order_blocks),
                any(fvg['type'] == 'bullish_fvg' and fvg['bottom'] < price < fvg['top'] for fvg in fvg_list),
                'BOS_bull' in [e[0] for e in detect_bos_choch(swing_highs, swing_lows)]
            ]
            
            if sum(buy_conditions) >= 3:
                signals.append({
                    'timestamp': df.index[i],
                    'action': 'buy',
                    'price': price,
                    'reason': f"PA: {sum(buy_conditions)}/4 conditions met"
                })
        
        self.signals = signals
        return signals
```

### 关键原则
1. **位置优先**: 先判断价格在结构的什么位置(Premium/Discount)
2. **确认优先**: 不追价,等价格回到关键区域后确认再入场
3. **多时间框架**: 高时间框架定方向,低时间框架找入场
4. **成交量验证**: 所有关键动作需要成交量配合
5. **风险管理**: 止损放在结构低点/高点下方,不固定点数
