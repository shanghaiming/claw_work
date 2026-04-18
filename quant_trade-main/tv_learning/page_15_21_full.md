# TradingView Strategy Learning Report - Pages 15-21

Generated: 2026-04-18

---

## Strategy 1: Adaptive Regime Momentum [JOAT]
- **URL**: https://www.tradingview.com/script/7v1PWf2e-Adaptive-Regime-Momentum-JOAT/
- **Page**: 17
- **Strategy Type**: Trend-following / Multi-layer confirmation
- **Technical Indicators**: ALMA (Arnaud Legoux Moving Average), ZLMA (Zero-Lag Moving Average), Volume RSI, RSI(14), ATR
- **Core Logic**: Requires three independent conditions to align before entry: (1) multi-bar ComboMA slope confirmation across N consecutive bars (ALMA+ZLMA blend), (2) price position relative to ComboMA, and (3) volume-based demand filter (Volume RSI). Exits use layered system with ATR-based stop/take-profit plus adaptive trail exits on slope reversal.
- **Innovation / Key Takeaway**:
  - The **multi-bar slope confirmation** is the key differentiator -- slope must be consistently positive/negative across N consecutive bars, not just one bar. This filters out single-bar flickers and false signals during consolidation.
  - **ComboMA** blends ALMA (smooth, reduced lag) with ZLMA (lag-compensated) to offset each other's weaknesses.
  - Stop/TP anchored to `strategy.position_avg_price` (actual fill price) rather than signal bar close -- more accurate backtesting.
  - Non-repainting via `barstate.isconfirmed`.

---

## Strategy 2: Confluence Signal Engine [JOAT]
- **URL**: https://www.tradingview.com/script/zZe9WPl6-Confluence-Signal-Engine-JOAT/
- **Page**: 17
- **Strategy Type**: Confluence scoring / Multi-dimension signal engine
- **Technical Indicators**: EMA (fast/slow), Price Z-Score, Volume RSI, RSI with slope, Structural Position (range midpoint), ATR ratio (volatility context)
- **Core Logic**: Assigns a composite score [-1, +1] by evaluating six deliberately uncorrelated dimensions of market behavior: (1) EMA alignment (trend), (2) Price Z-Score (statistical deviation), (3) Volume pressure, (4) RSI momentum quality, (5) Structural range position, (6) Volatility context. Each dimension scores +1, -1, or 0; summed and normalized. Signals fire when score exceeds configurable thresholds.
- **Innovation / Key Takeaway**:
  - The key insight is that standard multi-indicator approaches combine correlated signals (RSI, MACD, Stochastic all measure momentum). This engine deliberately selects six **uncorrelated dimensions** -- trend, statistics, volume, momentum quality, structure, and volatility -- so genuine agreement represents real confluence.
  - **24-cell gradient confidence meter** provides continuous conviction reading, not binary signal.
  - Gradient bar coloring proportional to conviction level.

---

## Strategy 3: Dynamic Grid & Martingale Bot (v6)
- **URL**: https://www.tradingview.com/script/co5pap8M/
- **Page**: 15
- **Strategy Type**: Grid trading / Martingale cost-averaging
- **Technical Indicators**: ADX, EMA(200)
- **Core Logic**: Trend-following automated strategy with built-in recovery mechanism. Enters only when ADX > 15 (strong trend) and price > EMA 200 (long-term uptrend). If price drops by a configured percentage after entry, automatically adds to position with increased size (Martingale multiplier). Takes profit when price reaches target above the average position price.
- **Innovation / Key Takeaway**:
  - Uses `strategy.position_avg_price` for dynamic break-even calculation as new orders fill.
  - JSON-formatted alert messages for automated webhook execution with brokers.
  - Practical Martingale implementation with clear risk warning -- suitable only for high-liquidity blue-chip stocks, not for extended downtrends.
  - Time filter restricts operation to specific exchange hours.

---

## Strategy 4: Correlation Thermal Matrix [ShigemiQuant]
- **URL**: https://www.tradingview.com/script/RKTSnOkH-Correlation-Thermal-Matrix-ShigemiQuant/
- **Page**: 16
- **Strategy Type**: Portfolio risk management / Correlation analysis
- **Technical Indicators**: Pearson Correlation, K-Means Clustering (ML)
- **Core Logic**: Builds a live pairwise correlation heatmap for up to 15 symbols, then applies K-Means clustering to automatically group symbols sharing similar correlation behavior. Produces a block-diagonal matrix where hidden risk clusters become visible.
- **Innovation / Key Takeaway**:
  - **K-Means clustering** applied to correlation profiles -- groups symbols whose full row of correlations are similar, not just pairwise correlation.
  - Block-diagonal sorting makes structural patterns immediately visible.
  - Practical workflow: (1) Detect risk clusters with CTM, (2) Find independent momentum signals, (3) Size positions by per-cluster exposure rather than per-symbol.
  - Regime change early warning when correlations break from historical patterns.

---

## Strategy 5: Lorentzian Classification [ICT Edition] [SRT298]
- **URL**: https://www.tradingview.com/script/JRzYIXvD-Lorentzian-Classification-ICT-Edition-SRT298/
- **Page**: 18
- **Strategy Type**: ML-based signal classification / ICT methodology
- **Technical Indicators**: Approximate Nearest Neighbors (Lorentzian distance), RSI, Wave Trend, CCI, ADX, RSI-9, Nadaraya-Watson Kernel Regression, 1H EMA structure (9/21/50)
- **Core Logic**: Preserves the original ML model (5-feature pattern matching with Lorentzian distance nearest neighbors and Nadaraya-Watson kernel filter), then adds ICT-specific context filters: Killzone restriction (limits signals to institutional order flow windows), HTF bias agreement (1H trend must align with signal direction), and conviction tiers (STRONG/MODERATE/WEAK based on prediction strength).
- **Innovation / Key Takeaway**:
  - **Killzone filtering** -- signals only fire during specific high-probability windows (NY AM Silver Bullet 10-11:00, PM Silver Bullet 14-15:00).
  - **HTF bias agreement** -- prevents fighting the higher timeframe, a core ICT principle.
  - **Conviction tiers** with configurable prediction threshold -- at least N of 8 nearest neighbors must agree.
  - Context-rich alerts include tier, killzone, HTF bias, and prediction score.

---

## Strategy 6: Predictive Monte Carlo Engine [LuxAlgo]
- **URL**: https://www.tradingview.com/script/rJJu2iQh-Predictive-Monte-Carlo-Engine-LuxAlgo/
- **Page**: 20
- **Strategy Type**: Probabilistic forecasting / Simulation
- **Technical Indicators**: ATR, SMA (trend regime), RSI (momentum regime), Geometric Brownian Motion, Random Walk, Historical Bootstrapping
- **Core Logic**: Generates hundreds of potential price paths using probabilistic simulations to project future price distribution. Offers three methods: GBM (log-normal distribution), Simple Random Walk (normal distribution), and Historical Shuffle (bootstrapping actual returns to preserve fat tails). Applies regime filtering to only use historical data matching the current market environment.
- **Innovation / Key Takeaway**:
  - **Regime-filtered simulations** -- when "Trend" or "Momentum" regime selected, only uses data from past bars matching the current market environment.
  - **Historical Shuffle (Bootstrapping)** preserves the actual distribution characteristics including fat tails, unlike Gaussian models.
  - **Fading S/R Zones** with horizontal gradient representing increasing uncertainty over time.
  - Anchor Mode to lock projections and observe how price reacted against historical Monte Carlo levels.

---

## Strategy 7: Gap Fill + Opening Range Strategy
- **URL**: https://www.tradingview.com/script/aydoOjNc-Gap-Fill-Opening-Range-Strategy/
- **Page**: 21
- **Strategy Type**: Day trading / Gap fill + ORB
- **Technical Indicators**: ATR, Opening Range (High/Low of first X minutes)
- **Core Logic**: Combines gap detection (today's open vs yesterday's close) with opening range breakout. Trades either gap fill (mean reversion) or ORB breakout (continuation) based on price reaction in the early session. Designed for US markets with frequent overnight gaps.
- **Innovation / Key Takeaway**:
  - Dual-logic approach: gap fill (mean reversion) OR breakout (continuation).
  - ATR-based risk/reward for stop and target calculation.
  - Simple, practical day trading framework for volatile markets.

---

## Strategy 8: Top Bottom Reversal Signals (RSI + MACD + BB + Pivot)
- **URL**: https://www.tradingview.com/script/KThB5Ucl-Top-Bottom-Reversal-Signals-RSI-MACD-BB-Pivot/
- **Page**: 15
- **Strategy Type**: Reversal detection
- **Technical Indicators**: RSI, MACD, Bollinger Bands, Pivot Points
- **Core Logic**: Combines four indicators to identify potential market tops and bottoms. Uses RSI overbought/oversold, MACD divergences, Bollinger Band extremes, and Pivot levels for confluence-based reversal signals.
- **Innovation / Key Takeaway**:
  - Multi-indicator confluence approach for reversal detection.
  - Combines momentum (RSI), trend (MACD), volatility (BB), and structural (Pivot) dimensions.
  - Description is minimal -- likely a straightforward implementation.

---

## Strategy 9: RSI + MFI + Volume + SMC + Divergence [Daily/Weekly Optimized]
- **URL**: https://www.tradingview.com/script/ORshnQEz-RSI-MFI-Volume-SMC-Divergence-Daily-Weekly-Optimized/
- **Page**: 15
- **Strategy Type**: Multi-indicator confluence / Bottom-Top detection
- **Technical Indicators**: RSI, MFI (Money Flow Index), Volume, Smart Money Concepts (SMC), Divergence
- **Core Logic**: Combines RSI, MFI, volume analysis, Smart Money Concepts, and divergence detection, optimized for daily and weekly timeframes. Designed to identify market tops and bottoms.
- **Innovation / Key Takeaway**:
  - Integration of **Smart Money Concepts** (order blocks, liquidity zones) with traditional indicators.
  - Multi-timeframe optimization (daily/weekly).

---

## Strategy 10: Momentum Shift [B de Rijk]
- **URL**: https://www.tradingview.com/script/jyLy3AjM-Momentum-Shift-B-de-Rijk/
- **Page**: 15
- **Strategy Type**: Momentum detection / Signal alerting
- **Technical Indicators**: Custom momentum calculation (rising/falling conditions)
- **Core Logic**: Detects momentum shift points and plots directional arrows (up/down) on the chart. Enhanced with real-time alert functionality using `alert()` function with `alert.freq_once_per_bar` to avoid duplicates.
- **Innovation / Key Takeaway**:
  - Clean implementation of real-time alerts perfectly aligned with visual signals.
  - `alert.freq_once_per_bar` pattern prevents alert spam.

---

## Strategy 11: Dual ORB (London & New York) | v6
- **URL**: https://www.tradingview.com/script/dWhq8bNn-Dual-ORB-London-New-York-v6/
- **Page**: 21
- **Strategy Type**: Session-based ORB
- **Technical Indicators**: Opening Range High/Low
- **Core Logic**: Plots London ORB (9-9:15 GMT+2) and New York ORB (3:30-3:45 GMT+2) with customizable time windows. Marks the high and low of the first 15 minutes for each session.
- **Innovation / Key Takeaway**:
  - Dual session ORB approach captures both European and US session opens.
  - Simple, practical framework for session-based breakout trading.

---

## Summary of Key Learnings

### Recurring Patterns Across These Strategies

1. **Multi-layer Confirmation**: The best strategies (Adaptive Regime Momentum, Confluence Engine) require multiple independent conditions to agree before signaling. The key insight is using **uncorrelated dimensions** rather than stacking correlated momentum oscillators.

2. **ALMA + ZLMA ComboMA**: Blending two complementary moving average types (ALMA for smoothness, ZLMA for lag compensation) creates a superior trend-following backbone.

3. **Multi-bar Slope Confirmation**: Requiring N consecutive bars of consistent MA slope direction filters out noise and prevents false entries during consolidations.

4. **Volume RSI as Demand Validation**: RSI applied to raw volume (not price) confirms whether a move has participation behind it -- elevated volume validates the signal.

5. **Killzone/Session Filtering**: Multiple strategies use session-based filters (ICT Killzones, ORB windows) to restrict signals to high-probability time windows.

6. **ATR-Based Risk Management**: Nearly all strategies use ATR multiples for stop-loss, take-profit, and trail exits, adapting to current volatility regime.

7. **Machine Learning Integration**: K-Means clustering for portfolio correlation analysis, Lorentzian distance for pattern matching, and Monte Carlo simulations for price forecasting represent the cutting edge.

8. **Regime Awareness**: Strategies increasingly incorporate regime detection (trend/momentum/volatility) to filter signals based on market environment.

9. **Non-repainting**: Best practices require `barstate.isconfirmed` gating and anchoring stops/TPs to actual fill prices.

10. **Gap + ORB Combination**: Combining overnight gap detection with opening range breakout provides a practical framework for day trading volatile markets.
