# TV Batch 6 Extended 2: Index 30-59 Learning Results

Date: 2026-04-19

---

### [30] o8dmBLcv - (Unnamed)
- **Type:** Utility/Unknown
- **Core Logic:** Insufficient description to analyze. URL with no descriptive name.
- **Math:** N/A
- **A-Share:** No - cannot evaluate
- **Innovation:** 1

### [31] oC9m0JpD - Swing Fibonacci BigBeluga
- **Type:** Fibonacci / Swing Analysis
- **Core Logic:** Swing-based Fibonacci retracement/extension tool. Identifies swing highs/lows and plots Fib levels between them. Likely auto-detects recent swing structure.
- **Math:** Fibonacci ratios (0.236, 0.382, 0.5, 0.618, 0.786) applied to price swings. Golden ratio phi = 1.618 basis.
- **A-Share:** Yes - Fibonacci is timeframe-agnostic and works on daily OHLCV
- **Innovation:** 1 - Standard Fibonacci retracement, no new math

### [32] oEpoSDyY - HEDGE FUND Liquidity Sniper
- **Type:** Liquidity Detection / ICT
- **Core Logic:** Detects liquidity pools (buy-side/sell-side) where retail stops cluster. Marks areas where price is likely to sweep before reversing. Likely uses swing structure and equal highs/lows detection.
- **Math:** Swing fractal detection, equal-highs/low clustering with tolerance bands
- **A-Share:** No - primarily designed for intraday forex/futures with session-based liquidity models
- **Innovation:** 2 - Useful concept but common ICT pattern

### [33] oFk7wbld - Gneus 3m HA HM Strategy TP Text
- **Type:** Heikin-Ashi / Scalping
- **Core Logic:** 3-minute Heikin-Ashi with Hull MA crossover strategy. Uses HA candles for trend filtering and HM for entry signals. Displays TP levels as text.
- **Math:** HA(close) = (O+H+L+C)/4, Hull MA = WMA(2*WMA(n/2) - WMA(n), sqrt(n))
- **A-Share:** No - 3-minute scalping strategy, not suitable for daily
- **Innovation:** 1

### [34] oJp0vm8c - Kure 909 Clarity
- **Type:** Trend Following / Multi-indicator
- **Core Logic:** Clarity-based trend system using multiple moving averages or momentum filters to reduce noise. "909" likely refers to parameter set (9, 0, 9 or similar).
- **Math:** Moving average crossover with trend clarity scoring
- **A-Share:** Yes - MA-based trend following works on daily
- **Innovation:** 2

### [35] oPYJ7RpJ - (Unnamed)
- **Type:** Unknown
- **Core Logic:** No description available.
- **Math:** N/A
- **A-Share:** No
- **Innovation:** 1

### [36] oPZA3pgr - Xiznit Scalper
- **Type:** Scalping / Momentum
- **Core Logic:** Quick scalping indicator likely using short-period momentum oscillators or micro-trend detection. Designed for fast entries/exits.
- **Math:** Short-period RSI/MACD divergence or micro-structure breakout
- **A-Share:** No - scalping only
- **Innovation:** 1

### [37] oStJQWHN - Absorption Overlay
- **Type:** Volume Analysis / Order Flow
- **Core Logic:** Detects absorption events where large volume prevents price from moving (high volume + small range candle). Indicates institutional activity absorbing selling/buying pressure.
- **Math:** Absorption = Volume_i / ATR_i > threshold AND |Close - Open| / Range < compression_ratio. The ratio of volume to price movement reveals hidden demand/supply.
- **A-Share:** Yes - volume-to-range ratio analysis is excellent for A-share daily data, especially with high retail participation creating absorption patterns
- **Innovation:** 3
- **Insight:** Absorption detection is grounded in the information-theoretic insight that high information content (volume) with low price change indicates a participant absorbing the opposite side. The mathematical basis: Entropy(Volume) >> Entropy(Price movement) => institutional presence. This can be adapted for A-share daily as large volumes on narrow-range days near key levels.

### [38] oU4jOvjQ - Fractal Liquidity Map JOAT
- **Type:** Multi-Timeframe Fractal / Liquidity
- **Core Logic:** Maps fractal-based liquidity levels across multiple timeframes. "JOAT" (Jack of All Trades) suggests comprehensive multi-TF analysis. Identifies where liquidity clusters exist based on fractal swing pivots.
- **Math:** Williams Fractals (n-bar high/low patterns) aggregated across timeframes with proximity-based clustering
- **A-Share:** Yes - fractal-based S/R works well on daily charts
- **Innovation:** 2

### [39] ocGCsTyY - ORB VWAP RSI Signals
- **Type:** Opening Range Breakout / Multi-indicator
- **Core Logic:** Combines Opening Range Breakout with VWAP anchoring and RSI momentum confirmation. Trades breakout of opening range when VWAP supports direction and RSI confirms momentum.
- **Math:** ORB levels = High/Low of first N minutes. VWAP = cumsum(price*volume)/cumsum(volume). RSI = 100 - 100/(1 + avg_gain/avg_loss). Triple confirmation system.
- **A-Share:** No - intraday ORB requires minute-level data
- **Innovation:** 2

### [40] ooqcJajL - lesh ghoti april (Psychological Levels + Time Filter)
- **Type:** Psychological Levels / Support-Resistance
- **Core Logic:** Plots psychological "bank levels" (round numbers like 100, 500, 1000) with time restriction filter. Round numbers act as magnets for orders due to human cognitive bias toward clean numbers.
- **Math:** Round_number = ceil(price/interval) * interval. The cognitive anchoring effect: humans cluster orders at round numbers creating self-fulfilling support/resistance.
- **A-Share:** Yes - psychological levels (e.g., 3000, 3500 on Shanghai Composite) are very significant in A-shares due to retail dominance
- **Innovation:** 2 - Well executed concept but not novel

### [41] otXz09gY - Trinity Triple RMA
- **Type:** Multi-MA Trend System
- **Core Logic:** Three Wilder's Smoothed Moving Averages (RMA 9, 21, 50) that change color based on slope direction. Background highlights when all three align. Provides "2 out of 3" early warning signals.
- **Math:** RMA = alpha * close + (1-alpha) * RMA[1], where alpha = 1/period. This is Wilder's smoothing (used in ATR, RSI). Alignment = all three rising or all three falling.
- **A-Share:** Yes - triple MA alignment is a solid trend filter for daily A-shares
- **Innovation:** 2 - Well-designed but standard multi-MA approach

### [42] pJqDBkVx - Smart Liquidity Trend Engine V9.0
- **Type:** Fractal Clustering / Liquidity Detection
- **Core Logic:** Weighted Multi-TF Fractal Clustering Algorithm. Simultaneously scans fractals on LTF (weight=1) and HTF (weight=3). Clusters nearby fractals within ATR-based proximity into "Liquidity Zones" with strength scores (Lv.1-5). Entry requires: zone proximity + displacement/engulfing confirmation + EMA200 slope trend alignment. V-Reversal override at strong zones (>=Lv.4).
- **Math:** Fractal clustering: merge fractals within ATR*k distance. Strength = sum of weights (HTF=3, LTF=1). Zone validity requires score >= 3. Displacement = body > ATR * multiplier. Invalidation: candle closes beyond zone boundary. Trend = slope of EMA200 (ta.rising/ta.falling).
- **A-Share:** Yes with adaptation - the fractal clustering with strength scoring is excellent for daily S/R identification, but session filtering needs to be replaced with A-share trading hours
- **Innovation:** 4
- **Insight:** The key innovation is the weighted fractal clustering algorithm with adaptive ATR-based proximity thresholds. This solves the problem of "too many pivot lines" by mathematically merging nearby pivots into meaningful zones. The strength scoring system (HTF fractals worth 3x LTF) is an elegant way to weight information quality. The concept that support/resistance is not permanent (zone invalidation on close) aligns with the Bayesian updating principle: prior beliefs (zone strength) are updated by new evidence (price closes beyond zone).

### [43] pOecPGQm - Futures to CFD Precision Mapper
- **Type:** Cross-Market Arbitrage / Utility
- **Core Logic:** Maps Futures prices (GC1!, NQ1!) to corresponding CFD prices (XAUUSD, NAS100) using dynamic basis calculation with 20-period standard deviation for "Safe Buffer" against spread widening. Auto-detects symbols and forces mintick precision.
- **Math:** Basis = Futures_price - CFD_price. Safe_Buffer = 20-period stdev(basis). Adjusted_SL = target_price +/- Safe_Buffer. This is essentially a dynamic z-score of the basis spread.
- **A-Share:** No - specific to Futures-to-CFD mapping, not applicable to A-share daily
- **Innovation:** 3
- **Insight:** The statistical approach to basis risk (using rolling standard deviation as a dynamic buffer) is mathematically sound. It recognizes that the spread between correlated instruments is itself a mean-reverting process, and the variance of that process determines the "safety margin." This is essentially a Bollinger Band applied to the basis itself.

### [44] pXOvCfBU - Real-time Engulfing Alert with Time Filter
- **Type:** Candlestick Pattern / Alert
- **Core Logic:** Detects bullish/bearish engulfing patterns with time-of-day filtering. Simple pattern recognition with session context.
- **Math:** Bullish Engulf: Close > Open AND Close > Open[1] AND Open < Close[1]. Bearish Engulf: inverse.
- **A-Share:** No - too simple, intraday focused
- **Innovation:** 1

### [45] pfbNpPsQ - KalmanEngineLib
- **Type:** Signal Processing Library / Kalman Filter
- **Core Logic:** Full N-state Kalman filter library in Pine v6. Implements packed upper-triangular covariance storage (47% memory savings), sequential scalar measurement updates in Joseph form for numerical stability, Mahalanobis gating with Ledoit-Wolf shrinkage, adaptive noise estimation (windowed MLE for Q, innovation z-score ratchet for R), online coupling estimation via nested scalar Kalman, multi-scale trajectory storage with Pearson cross-correlation for lag calibration, and k-step covariance propagation.
- **Math:** Core Kalman equations: x_pred = F*x + B*u, P_pred = F*P*F' + Q, innovation = z - H*x_pred, S = H*P_pred*H' + R, K = P_pred*H'*inv(S), x_update = x_pred + K*innovation, P_update = (I-K*H)*P_pred*(I-K*H)' + K*R*K' (Joseph form). Mahalanobis distance = sqrt(innovation'*inv(S)*innovation). Adaptive Q via windowed MLE: Q_hat = (1/N)*sum(innovation*innovation') - avg(P_pred). Trajectory xcorr at lag k = pearson(x[t], x[t-k]).
- **A-Share:** Yes - this is a general-purpose library that can be used to build A-share daily strategies. Kalman filtering on daily OHLCV is highly applicable for noise reduction and trend estimation.
- **Innovation:** 5
- **Insight:** This is the most mathematically rigorous Pine Script library encountered. The packed upper-triangular covariance storage (n*(n+1)/2 vs n^2) is a classic optimization from numerical linear algebra. The Joseph form update (P+ = (I-KH)P-(I-KH)' + KRK') is preferred over the standard form because it guarantees positive semi-definiteness of P even with numerical errors. The Ledoit-Wolf shrinkage for near-singular covariance matrices is borrowed from portfolio optimization theory. The nested scalar Kalman for coupling estimation (gamma_lag) is an elegant way to estimate cross-variable relationships online. The KMEMA output (adaptive EMA modulated by innovation shock and confidence) is essentially a Kalman-filtered moving average that adapts its responsiveness to how surprising new observations are - this is the key extractable insight for A-share strategy building.

### [46] pi85RVXh - AG Pro Session VWAP Reaction Engine
- **Type:** Session VWAP / Reaction Mapping
- **Core Logic:** Maps how price reacts around a selected session VWAP (Asia/London/NY/custom). Classifies reactions into three families: Reclaim (price recovers VWAP), Reject (price fails at VWAP), Bounce (price uses VWAP as springboard). Uses reaction corridors, confirmed reaction zones, and compact bias panels.
- **Math:** Session VWAP = cumulative(price*volume) / cumulative(volume) within session window. Reaction classification based on structural price behavior relative to VWAP: Reclaim = close crosses above VWAP after being below with confirmation candles. Reject = close fails at VWAP after approach. Bounce = price touches VWAP corridor and reverses.
- **A-Share:** No - session-based VWAP requires intraday data. However, the concept of classifying price-VWAP interaction (reclaim/reject/bounce) is transferable to daily VWAP analysis.
- **Innovation:** 3
- **Insight:** The reaction classification taxonomy (reclaim/reject/bounce) is a useful framework for understanding institutional behavior around VWAP. In A-shares, a similar approach could use daily VWAP or sector-level VWAP to classify institutional activity. The math is straightforward but the structural categorization of reactions adds analytical value.

### [47] ponegJHM - Koda 30% Stop Overlay
- **Type:** Risk Management / Volatility-Based Stops
- **Core Logic:** Converts daily ATR into actionable stop-loss levels anchored to session opens. The "30% Rule" = minimum stop distance is 30% of daily ATR from session open. Plots upper/lower bands at Session_Open +/- 0.3*ATR_Daily for Asian/London/NY sessions.
- **Math:** Stop_band = Session_Open +/- 0.3 * ATR(Daily, 14). The 30% rule: if price hasn't moved 30% of its daily range from the open, your stop is too tight and vulnerable to normal volatility noise.
- **A-Share:** No - intraday session-based, but the concept of volatility-anchored stops is transferable. On A-share daily charts, using 30% of weekly ATR as minimum stop distance from entry is a valid adaptation.
- **Innovation:** 3
- **Insight:** The philosophical insight is powerful: "Your stop shouldn't be based on what you're willing to lose - it should be based on what the market normally moves." This translates ATR from a descriptive statistic into a decision tool. The 30% threshold is heuristic but grounded: it represents the boundary between "normal noise" and "meaningful displacement." For A-share daily strategies, this could be adapted as: Stop = Entry +/- k * ATR(Weekly), where k is calibrated to the specific stock's volatility profile.

### [48] ppEwWYS5 - Buy Sell Signals
- **Type:** Unknown / Test Script
- **Core Logic:** Test script with no real description. Placeholder/spam content.
- **Math:** N/A
- **A-Share:** No
- **Innovation:** 1

### [49] q58ifTtW - ICT Session Candle Counter
- **Type:** Session Analysis / Utility
- **Core Logic:** Counts candles within each ICT session (Tokyo, London, NY) and killzone window. Labels each candle with its sequential number within the active session. Supports trim-overlap when sessions overlap.
- **Math:** Sequential counting within time-bounded windows. Session boundaries defined by exchange hours with DST adjustment.
- **A-Share:** No - intraday session counting not relevant for daily
- **Innovation:** 1

### [50] q8eZ6kK4 - (Unnamed)
- **Type:** Unknown
- **Core Logic:** No description available.
- **Math:** N/A
- **A-Share:** No
- **Innovation:** 1

### [51] qFpxiyof - VALOR SESSIONS KEY LEVELS
- **Type:** Session Levels / Key Price Levels
- **Core Logic:** Plots session-based key levels including NY AM/Lunch/PM, Asia, London session highs/lows, NWOG (New Week Opening Gap), and PDH/PDL (Previous Day High/Low). Classic ICT-style level mapping.
- **Math:** PDH/PDL = previous day's highest high / lowest low. NWOG = Monday open vs Friday close gap. Session levels = high/low within defined session time windows.
- **A-Share:** No - intraday session-based
- **Innovation:** 1

### [52] qNRMNTSn - v18 Inside/Outside Bar Levels
- **Type:** Price Action / Bar Pattern
- **Core Logic:** Detects Inside Bars (high <= prev high AND low >= prev low) and Outside Bars (high > prev high AND low < prev low). Plots breakout levels at high+offset and low-offset. Latest setup replaces previous, historical markers remain.
- **Math:** Inside Bar: H <= H[1] AND L >= L[1]. Outside Bar: H > H[1] AND L < L[1]. Breakout_level = H + offset or L - offset. This is a compression/expansion model.
- **A-Share:** Yes - Inside/Outside bar detection is clean price action that works on daily A-shares. Inside bars represent consolidation before expansion; outside bars represent volatility expansion.
- **Innovation:** 2

### [53] qOG3HIxG - Bitcoin Production Cost KenshinC
- **Type:** Fundamental / Cost Basis
- **Core Logic:** Estimates Bitcoin's production cost based on mining difficulty, hash rate, and energy costs. Provides a fundamental floor price for BTC.
- **Math:** Production_cost = (Difficulty * 2^32 / Hashrate) * Energy_cost_per_kWh * Power_consumption_W. This models the marginal cost of mining one BTC.
- **A-Share:** No - BTC-specific fundamental model
- **Innovation:** 3
- **Insight:** The concept of a production-cost floor is borrowed from commodity economics (e.g., gold mining cost as price support). The math models the thermodynamic floor: energy cost to produce one unit of BTC. This is applicable to A-shares in the mining/energy sector where production cost provides fundamental support/resistance.

### [54] qOOuJvFp - (Unnamed)
- **Type:** Unknown
- **Core Logic:** No description available.
- **Math:** N/A
- **A-Share:** No
- **Innovation:** 1

### [55] qUOqtsZe - Big Order Gap Detector
- **Type:** Order Flow / Gap Detection
- **Core Logic:** Detects price gaps that indicate large institutional orders. Identifies fair value gaps (FVG) and imbalances where price moved too fast for normal order flow, suggesting big money involvement.
- **Math:** FVG = |High[i] - Low[i+2]| > threshold (bullish gap) or |Low[i] - High[i+2]| > threshold (bearish gap). The gap represents a zone where no significant trading occurred.
- **A-Share:** Yes - FVG detection works on daily charts. A-share stocks with limit-up/down moves frequently create gaps that act as support/resistance.
- **Innovation:** 2

### [56] qUgTfgpK - M15 Scalp V1
- **Type:** Scalping / 15-minute
- **Core Logic:** 15-minute scalping strategy with undisclosed logic. Likely uses short-period indicators for quick entries/exits.
- **Math:** Unknown specific math
- **A-Share:** No - 15-minute scalping
- **Innovation:** 1

### [57] qXqxbdam - (Unnamed)
- **Type:** Unknown
- **Core Logic:** No description available.
- **Math:** N/A
- **A-Share:** No
- **Innovation:** 1

### [58] qZVzyaxP - (Unnamed)
- **Type:** Unknown
- **Core Logic:** No description available.
- **Math:** N/A
- **A-Share:** No
- **Innovation:** 1

### [59] qar313Qr - PURECELL DBZENO
- **Type:** Custom Oscillator / Hybrid
- **Core Logic:** Custom indicator named "PURECELL DBZENO" - likely a hybrid oscillator combining multiple signal processing techniques. "DBZENO" may reference Zeno's paradox (halving distances) or a dual-band zero-lag approach.
- **Math:** Likely zero-lag signal processing with dual bands. "DB" suggests dual-band, "ZENO" suggests progressive halving or convergence analysis.
- **A-Share:** Possibly - depends on implementation
- **Innovation:** 2

---

## Summary

**Total Processed:** 30 scripts (index 30-59)

**High-Innovation List (>=3):**
1. **[45] KalmanEngineLib** - Innovation: 5 - Full N-state Kalman filter library with packed covariance, Mahalanobis gating, adaptive noise, trajectory storage
2. **[42] Smart Liquidity Trend Engine V9.0** - Innovation: 4 - Weighted multi-TF fractal clustering with ATR proximity merging and strength scoring
3. **[43] Futures to CFD Precision Mapper** - Innovation: 3 - Dynamic basis spread analysis with statistical safety buffers
4. **[37] Absorption Overlay** - Innovation: 3 - Volume-to-range ratio detection of institutional absorption
5. **[46] AG Pro Session VWAP Reaction Engine** - Innovation: 3 - Reaction taxonomy (reclaim/reject/bounce) for VWAP interaction
6. **[47] Koda 30% Stop Overlay** - Innovation: 3 - ATR-based volatility stop framework with actionable rule
7. **[53] Bitcoin Production Cost** - Innovation: 3 - Fundamental cost basis modeling

**Cross-Cutting Patterns:**
1. **Session-Based Dominance:** The majority of scripts (8+) are session-based intraday tools (ICT sessions, killzones, opening ranges). This reflects the current TV community's heavy focus on intraday forex/futures trading with ICT methodology. These are NOT directly applicable to A-share daily but the underlying math concepts (VWAP, absorption, reaction classification) are transferable.

2. **Fractal Clustering as S/R:** Multiple scripts use fractal-based pivot detection with clustering algorithms. The trend is moving away from "every pivot gets a line" toward "nearby pivots merge into zones with strength scores." This is a significant improvement for reducing noise.

3. **Kalman Filtering Emergence:** The KalmanEngineLib represents a step-change in Pine Script sophistication. Moving from simple moving averages to full state-space models with adaptive noise estimation. This is the direction quant trading should evolve.

4. **Psychological/Round Numbers:** Scripts recognizing that round numbers create self-fulfilling S/R due to order clustering. Highly relevant for A-shares given retail dominance.

5. **Volatility-Based Decision Frameworks:** Koda 30% Stop and similar tools converting ATR from descriptive to actionable. The pattern is: measure volatility -> set threshold -> make decision. This "volatility normalization" is mathematically superior to fixed-percentage stops.

**Key Insights:**

1. **Kalman Filter for A-Shares:** The KalmanEngineLib's KMEMA (adaptive EMA modulated by innovation shock) is directly extractable for A-share daily strategies. When the innovation (difference between predicted and actual price) is large, the filter adapts faster. This provides superior trend following during regime changes while maintaining smoothness during consolidation.

2. **Fractal Zone Strength Scoring:** The weighted clustering approach (HTF fractals worth 3x LTF) can be adapted for A-share daily as: Daily pivot = weight 1, Weekly pivot = weight 3, Monthly pivot = weight 5. Merge pivots within 0.5*ATR(20) into zones. Require minimum score of 3 to validate.

3. **Absorption on A-Share Daily:** High volume + narrow range days on A-shares near key levels (especially near 10% limit-up/down thresholds) are strong signals. The math: if Volume_rank > 80th percentile AND |C-O|/Range < 0.3, then absorption detected.

4. **The "Volatility-as-Decision" Paradigm:** Instead of fixed parameters, all thresholds should be functions of recent volatility. The 30% ATR rule is a concrete example. For A-shares: stop_loss = entry +/- 0.3 * ATR(20, daily), take_profit = entry +/- 0.6 * ATR(20, daily) for 2:1 reward/risk.
