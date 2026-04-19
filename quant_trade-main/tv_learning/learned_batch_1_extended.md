# TradingView Batch 1 Extended Strategy Analysis

> Generated: 2026-04-19
> Source: batch_1.json (indices 0-29, 30 scripts)
> Focus: Mathematical explainability, A-share daily OHLCV suitability

---

## #0 [014kqYiX] Metis Fully Vested Entry Engine v1

**Type:** Trend-following confluence system

**Core Logic:** Multi-indicator confluence entry requiring simultaneous alignment of: (1) price above 50MA and 200MA for trend direction, (2) RSI pullback to a configurable zone (not overbought), (3) relative volume spike above a threshold. Only when all three conditions align does it trigger a "fully vested" (full position) entry.

**Math Foundation:** 
- MA filter: `trend = close > SMA(close,50) AND close > SMA(close,200)`
- RSI zone: `pullback = RSI(14) < rsi_threshold` (typically 40-50 range)
- Volume filter: `vol_ratio = volume / SMA(volume, 20) > vol_mult`
- Confluence = AND(trend, pullback, vol_ratio)

**Entry/Exit:** Long entry on confluence bar. Exit on MA crossunder or trailing stop.

**A-Share Suitability:** 4/5 -- All inputs are standard daily OHLCV. MA+RSI+volume confluence is robust on A-share daily bars. Minor concern: A-share volume includes limit-up/down locked volume which distorts relative volume.

**Innovation:** 2/5 -- Standard confluence approach. The "fully vested" framing is positioning language, not mathematical innovation.

---

## #1 [01lrRndV] LuxAlgo Open Interest Inflows/Outflows

**Type:** Open Interest flow analysis

**Core Logic:** Estimates money flow direction by analyzing changes in Open Interest (OI) alongside price movement. When OI increases with rising price, it suggests new long positions (inflow). When OI decreases with falling price, it suggests long liquidation (outflow). The indicator correlates OI changes with price movement to produce a money flow estimate.

**Math Foundation:**
- OI delta: `dOI = OI[t] - OI[t-1]`
- Money flow estimation: `MF = dOI * (close - open) / range` -- signed by price direction
- Correlation: `corr(OI_change, price_change)` over rolling window to validate flow direction
- EMA smoothing of the resulting flow series

**Entry/Exit:** Buy when net OI inflow is positive and price is above a moving average. Sell on net outflow.

**A-Share Suitability:** 1/5 -- A-share stocks do NOT have publicly available Open Interest data. OI is a derivatives concept. Only applicable to China's futures market (CSI 300 futures, etc.), not equities.

**Innovation:** 3/5 -- OI-based money flow is a legitimate derivatives analysis approach. The correlation filter is a sound statistical technique to validate signal quality.

---

## #2 [03ZAIYhM] Tops And Bottoms

**Type:** Simple pivot reversal finder

**Core Logic:** Identifies local tops and bottoms using RSI overbought/oversold levels combined with volume confirmation. When RSI exceeds a threshold and volume is above average, marks a top. When RSI drops below a threshold with volume, marks a bottom.

**Math Foundation:**
- Top condition: `RSI(14) > 70 AND volume > SMA(volume, 20) AND close < close[1]`
- Bottom condition: `RSI(14) < 30 AND volume > SMA(volume, 20) AND close > close[1]`

**Entry/Exit:** Buy at bottom signal, sell at top signal.

**A-Share Suitability:** 3/5 -- Uses only OHLCV data, works on daily. However, fixed RSI thresholds (70/30) are problematic for A-shares which have strong trend persistence and different distribution characteristics.

**Innovation:** 1/5 -- Trivial implementation. Standard RSI+volume approach with no novel mathematics.

---

## #3 [0ECs7la9] CRUCE EMA 3-9-20 + ADX

**Type:** EMA crossover with trend strength filter

**Core Logic:** Three-EMA system (3, 9, 20 periods) where alignment of all three EMAs (fast > medium > slow for bullish, reverse for bearish) combined with ADX above a threshold generates entry signals. Written in Spanish.

**Math Foundation:**
- EMA alignment: `EMA(3) > EMA(9) > EMA(20)` (bullish stack)
- ADX filter: `ADX(14) > threshold` (typically 20-25)
- Entry = AND(bullish_stack, ADX_filter)

**Entry/Exit:** Long on bullish EMA stack with ADX > threshold. Short on bearish stack. Exit on stack breakdown.

**A-Share Suitability:** 3/5 -- Pure OHLCV. The 3-EMA alignment is a well-known technique that works in trending A-share markets. ADX filter helps avoid choppy consolidation phases common in A-shares.

**Innovation:** 1/5 -- Textbook EMA crossover. No mathematical novelty.

---

## #4 [0KflNXqI] Luminous Volume Flow Oscillator (Pineify)

**Type:** Volume-based oscillator with zone filtering

**Core Logic:** Splits each bar's volume into buy-volume and sell-volume using bar-polarity (where close sits within the high-low range). The delta is EMA-smoothed to produce an oscillator. Zone filtering (neutral/bullish/bearish zones based on oscillator level relative to zero) qualifies signals.

**Math Foundation:**
- Bar polarity: `BV = volume * (close - low) / (high - low)`, `SV = volume * (high - close) / (high - low)`
- Volume delta: `VD = BV - SV`
- Oscillator: `VFO = EMA(VD, fast) - EMA(VD, slow)` (MACD-like structure)
- Zone filter: bullish when VFO > 0 AND rising; bearish when VFO < 0 AND falling; neutral otherwise

**Entry/Exit:** Long when VFO crosses above zero in bullish zone. Short on cross below zero in bearish zone.

**A-Share Suitability:** 4/5 -- Bar-polarity volume splitting works well with daily OHLCV. Does not require tick data. The zone filter adds noise reduction. The EMA-smoothed delta is a robust estimator of net buying pressure.

**Innovation:** 3/5 -- The bar-polarity approach to volume decomposition is practical. The zone-filtered oscillator architecture (MACD-like structure applied to volume delta) is a clean design pattern worth replicating.

**Insight:** Bar-polarity volume decomposition is a mathematical approximation of true buy/sell volume. The formula `BV = V * (C-L)/(H-L)` assumes linear distribution of volume across the price range, which is an imperfect but useful model. The MACD-of-volume-delta structure (fast EMA minus slow EMA of the delta) creates a momentum-of-money-flow indicator that leads price at reversals.

---

## #5 [0LOublbQ] Targets High/Low ULTIMATE V14.6

**Type:** Price target calculation system (Polish language)

**Core Logic:** Calculates projected high/low targets for the current period based on previous period's range, pivot points, and Fibonacci extensions. Uses multiple target calculation methods and displays them as horizontal levels.

**Math Foundation:**
- Classic pivot: `PP = (H + L + C) / 3`
- Target calculations based on range expansion/contraction ratios
- Fibonacci extensions: `target = PP + ratio * (H - L)` where ratio in {0.382, 0.618, 1.0, 1.272, 1.618}

**Entry/Exit:** Buy when price tests the lower target zone with reversal confirmation. Sell at upper target zone.

**A-Share Suitability:** 3/5 -- Pivot and Fibonacci levels are universally applicable. Daily timeframe works well. However, target-based systems tend to underperform in A-shares due to limit-up/down mechanics.

**Innovation:** 2/5 -- Multiple target calculation methods combined is useful but not mathematically novel.

---

## #6 [0ZBQpzty] Hull RSI Trend Rider Pro

**Type:** Hull MA applied to RSI for trend detection

**Core Logic:** Applies Hull Moving Average (HMA) to the RSI values instead of price. The HMA-RSI crossover of a signal line generates trend direction. Trailing stops based on ATR manage exits.

**Math Foundation:**
- RSI(14) calculated normally
- Hull MA of RSI: `HMA(RSI, n) = WMA(2*WMA(RSI, n/2) - WMA(RSI, n), floor(sqrt(n)))`
- Signal line: SMA of HMA-RSI
- Trailing stop: `close - k * ATR(14)` for longs

**Entry/Exit:** Long when HMA-RSI crosses above signal line. Trailing stop exit.

**A-Share Suitability:** 3/5 -- HMA reduces lag which helps in fast-moving A-share trends. However, HMA of RSI adds complexity without clear theoretical justification over standard RSI usage.

**Innovation:** 2/5 -- HMA applied to RSI is a known technique. The mathematical properties of HMA (phase preservation at dominant cycle via sqrt(n) weighting) are interesting but well-documented.

---

## #7 [0el0Zp7j] (Unnamed Script)

**Type:** Unknown -- no title or description available from fetch

**Core Logic:** Insufficient data to analyze. The URL hash `0el0Zp7j` resolves to a page without meaningful description.

**A-Share Suitability:** N/A

**Innovation:** N/A

**Verdict:** SKIP -- No accessible content.

---

## #8 [0hGVByv0] Prev OHLC + VWAP + Prev VWAP

**Type:** Intraday reference level indicator

**Core Logic:** Combines previous day's OHLC levels, session-anchored VWAP, and previous session VWAP into a single overlay. Features configurable anchor periods (Session/Week/Month/Quarter/Year), weekly VWAP, percentage levels from previous close, and a day-high drawdown table.

**Math Foundation:**
- VWAP: `sum(price * volume) / sum(volume)` reset per anchor period
- Previous VWAP: locked final value from prior session as horizontal reference
- Percentage levels: `prev_close * (1 +/- pct)` for pct in {1%, 3%, 5%, 7%, 10%}
- Day high drawdown: `(high - close) / high * 100` with color coding

**Entry/Exit:** No automated signals -- purely a reference level tool for manual trading.

**A-Share Suitability:** 2/5 -- VWAP requires intraday data and session anchoring. On daily timeframe, VWAP degenerates to close. Only useful for A-share day traders with minute data. The percentage level concept is applicable to daily but trivially computed.

**Innovation:** 1/5 -- Clean implementation of standard reference levels. The previous-session VWAP carryover is the only marginally interesting concept.

---

## #9 [0yDdkPIp] Adaptive Pivot-Length RSI (APL-RSI) by NotLazyBear

**Type:** Self-adaptive RSI with probability-driven period selection

**Core Logic:** THE MOST INNOVATIVE SCRIPT IN THIS BATCH. Builds a Probability Mass Function (PMF) from multi-scale pivot sweep analysis. The PMF's mode becomes the RSI lookback period. Implements true Wilder RSI with manual gain/loss state tracking. Uses empirical percentile-based overbought/oversold levels instead of fixed thresholds.

**Math Foundation:**
- **Multi-scale pivot sweep:** For each candidate length L in [2, 100], count how many bars since a local pivot (high or low) occurred at that scale. This creates a histogram of "how often does the market cycle at length L?"
- **PMF construction:** `PMF(L) = count(L) / sum(count)` over all L
- **Adaptive period:** `L* = argmax_L PMF(L)` (the mode)
- **True Wilder RSI:** `avg_gain = (prev_avg_gain * (L-1) + current_gain) / L` -- manual state tracking avoids Pine's built-in RSI approximation
- **Empirical OB/OS:** Instead of fixed 70/30, calculate the 90th and 10th percentiles of RSI distribution over a rolling window. `OB = percentile(RSI, 90)`, `OS = percentile(RSI, 10)`

**Entry/Exit:** Buy when APL-RSI crosses above empirical oversold level. Sell when crosses below empirical overbought level.

**A-Share Suitability:** 5/5 -- This is a genuinely adaptive indicator. A-share markets cycle between trending and range-bound regimes, and the adaptive period selection directly addresses this. Empirical OB/OS levels handle the A-share bias toward persistent trends. Pure OHLCV, no external data needed.

**Innovation:** 5/5 -- Three major innovations: (1) PMF-based adaptive period selection grounded in cycle analysis, (2) True Wilder RSI implementation with correct alpha = 1/L, (3) Empirical percentile OB/OS that adapts to market regime. This is publishable-quality research.

**Insight:** WHY IT WORKS -- The PMF approach captures the dominant cycle length of the current market. When the market is trending strongly, pivots are spaced far apart, so the PMF mode shifts to longer periods, making RSI less sensitive and reducing whipsaws. When the market is choppy, pivots are frequent, the mode shifts shorter, making RSI more responsive. This is a form of spectral analysis applied to indicator parameter selection. The empirical percentile OB/OS is equivalent to non-parametric statistics -- it makes no distributional assumption about RSI values, which is important because RSI in trending A-share stocks is NOT normally distributed (it has fat tails and positive skew).

---

## #10 [13If880V] Jan Buy, Hold, Add c TP/baghold-doi warning

**Type:** Trend-following pullback system with position management

**Core Logic:** Two-phase entry system: Buy1 (early trend entry when price structure turns positive and momentum confirms), Buy2 (add-on during pullback when higher swing low forms with MACD confirmation). Includes "doi" warning (Thai slang for bagholding risk) when price makes new high but MACD weakens. Scale-out exit strategy rather than single target.

**Math Foundation:**
- Trend detection: EMA structure alignment
- Buy1: Price structure turning positive + momentum confirmation (early trend)
- Buy2: `swing_low[t] > swing_low[t-1]` (higher low) AND `MACD[t] > MACD[t-1]` at swing low (momentum divergence positive)
- Doi warning: `price makes new swing high` AND `MACD[t] < MACD_at_previous_swing_high` (bearish divergence)
- Stop for Buy2: anchored to EMA(100)
- Scale-out: partial profit-taking at swing highs or momentum weakening

**Entry/Exit:** Buy1 at trend start. Buy2 on constructive pullback. Avoid when doi fires. Scale out gradually.

**A-Share Suitability:** 4/5 -- Excellent fit. A-share trending stocks benefit from the two-phase entry (reduces chasing). The "doi" warning directly addresses a common A-share retail trap (buying at tops). EMA(100) as stop reference is practical. Scale-out matches A-share risk management needs.

**Innovation:** 3/5 -- The doi/baghold warning is a practical innovation -- detecting momentum divergence at new highs as a "don't chase" signal. The structured two-phase entry with momentum confirmation at pullbacks is well-designed.

---

## #11 [13gJPimb] Wick to Close Distance Pips

**Type:** Candlestick wick analysis tool

**Core Logic:** Measures the distance from wick tips to the close in pips. Used to identify rejection candles (long wicks) vs momentum candles (short wicks).

**Math Foundation:**
- Upper wick distance: `(high - close) * pip_multiplier`
- Lower wick distance: `(close - low) * pip_multiplier`
- Asymmetry ratio: `upper_wick / lower_wick` to detect directional rejection

**Entry/Exit:** No signals -- measurement tool for manual wick analysis.

**A-Share Suitability:** 2/5 -- Useful as a supplementary tool but provides no trading signals. The pip-based measurement is forex-oriented; for A-shares, percentage-based wick analysis would be more appropriate.

**Innovation:** 1/5 -- Simple arithmetic measurement. No mathematical depth.

---

## #12 [14eqfJ5q] RSI / Price Divergence [MTF Alerts]

**Type:** Multi-timeframe RSI divergence detector

**Core Logic:** Detects both regular and hidden RSI divergences across configurable timeframes. Uses pivot-based detection with configurable lookback and confirmation bars. Includes early real-time alerts (which repaint if conditions change before confirmation).

**Math Foundation:**
- Pivot detection: `pivot_high = close > max(close[1..lookback])` on both sides
- Regular divergence (bearish): `price makes higher high AND RSI makes lower high` at pivots
- Hidden divergence (bullish): `price makes higher low AND RSI makes lower low` at pivots
- MTF: applies detection on higher timeframe data using `request.security()`
- Confirmation: requires N bars after pivot to confirm the divergence pattern

**Entry/Exit:** Buy on bullish regular divergence (oversold reversal). Sell on bearish regular divergence. Hidden divergence for trend continuation.

**A-Share Suitability:** 4/5 -- Divergence detection is universally applicable. MTF approach using daily+weekly timeframes works well for A-shares. The confirmation mechanism reduces false signals common in A-share whipsaws. Pure OHLCV.

**Innovation:** 2/5 -- Standard divergence implementation. The MTF+confirmation wrapper is practical engineering but not mathematically novel.

---

## #13 [15Rk9hvy] Day Trade Info (tablouh)

**Type:** Multi-timeframe volatility and momentum dashboard

**Core Logic:** Displays ADR (Average Daily Range), ATR, and RSI across four timeframes (1H to 1M) in a table format. Includes a live New York session clock.

**Math Foundation:**
- ADR: `SMA(high - low, period)` typically 14-day
- ATR: Wilder's True Range moving average
- RSI: Standard 14-period on each timeframe

**Entry/Exit:** No signals -- information dashboard for manual trading.

**A-Share Suitability:** 1/5 -- Designed for intraday US market day trading. The NY session clock is irrelevant for A-shares. The MTF dashboard concept could be adapted but requires minute data.

**Innovation:** 1/5 -- Dashboard aggregation of standard indicators. No mathematical contribution.

---

## #14 [1E8gnrL5] OVS Key Levels

**Type:** Key price reference level display

**Core Logic:** Plots previous day/week/month OHLC levels and previous VWAP as horizontal reference lines. Designed to identify support/resistance zones where price reacts.

**Math Foundation:**
- Levels: `prev_day_OHLC`, `prev_week_OHLC`, `month_open`, `prev_VWAP`
- No algorithmic signal generation -- purely visual reference

**Entry/Exit:** No automated signals. Manual trading based on price reactions at levels.

**A-Share Suitability:** 2/5 -- Previous day H/L/C levels are meaningful in A-shares (gap behavior). However, the VWAP component requires intraday data. Weekly/monthly levels are universally applicable.

**Innovation:** 1/5 -- Standard reference level plotting. No mathematical contribution.

---

## #15 [1MEWPvsR] Event Marker (20 Events)

**Type:** Event annotation tool

**Core Logic:** Allows marking up to 20 custom events on the chart with labels and colors. No trading logic.

**A-Share Suitability:** N/A -- Annotation tool, not a trading strategy.

**Innovation:** 1/5 -- UI convenience feature.

---

## #16 [1O196EXo] ES Breakout Toolkit ADX Regime Filter (Free)

**Type:** Breakout system with ADX regime detection

**Core Logic:** Identifies breakout setups when price breaks above/below a defined range, filtered by ADX regime classification. Only takes breakouts that align with the current volatility regime (trending vs ranging).

**Math Foundation:**
- Range detection: `upper = highest(high, n)`, `lower = lowest(low, n)`
- ADX regime: `if ADX(14) > 25: trending; else: ranging`
- Breakout signal: `close > upper` (long) or `close < lower` (short)
- Regime filter: only trade breakouts in trending regime; ignore in ranging regime
- Position sizing may adjust based on ADX level (stronger trend = larger position)

**Entry/Exit:** Long on upside breakout when ADX indicates trending. Exit on range recapture or trailing stop.

**A-Share Suitability:** 4/5 -- Breakout systems perform well in A-shares during trending phases. The ADX regime filter prevents taking breakouts during A-share consolidation periods (which are frequent and prolonged). Pure OHLCV.

**Innovation:** 2/5 -- Breakout + ADX filter is a well-known combination. The regime classification approach is sound but not novel.

---

## #17 [1RceVPF7] Joey's PDH and PDL

**Type:** Previous Day High/Low level plotter

**Core Logic:** Plots the previous day's high and low as horizontal reference lines. Used for intraday trading to identify breakout and rejection levels.

**Math Foundation:**
- `PDH = high[1]` (previous daily high)
- `PDL = low[1]` (previous daily low)
- No additional calculations

**Entry/Exit:** Buy on break above PDH. Sell on break below PDL. Or trade rejections at these levels.

**A-Share Suitability:** 2/5 -- Previous day H/L is meaningful but this is trivially computed. Requires intraday timeframe for practical use.

**Innovation:** 1/5 -- Minimal implementation of a basic concept.

---

## #18 [1WGjQ7YC] Absorption Detector v1

**Type:** Volume absorption detection

**Core Logic:** Detects when high volume occurs on a bar but price fails to move significantly, suggesting absorption (large orders absorbing selling/buying pressure). This indicates potential reversal or continuation depending on context.

**Math Foundation:**
- Volume ratio: `VR = volume / SMA(volume, 20)`
- Price movement: `PM = abs(close - open) / (high - low)` (body-to-range ratio)
- Absorption condition: `VR > threshold AND PM < small_threshold` (high volume, small body)
- Enhanced: `range_ratio = (high - low) / ATR(14)` -- normalized range
- Full absorption: high volume, small body relative to range, within ATR band

**Entry/Exit:** Buy when absorption detected at support (bullish absorption of selling). Sell at resistance (bearish absorption of buying).

**A-Share Suitability:** 4/5 -- Volume absorption is particularly relevant in A-shares where institutional block trades are common. The ratio-based approach works on daily OHLCV. The concept of "volume without price movement = absorption" is grounded in market microstructure theory.

**Innovation:** 3/5 -- While the concept is well-known in market profile literature, the quantitative definition (volume ratio * body-to-range ratio) provides a clean mathematical framework. The ATR normalization adapts to volatility regime.

**Insight:** WHY ABSORPTION MATTERS -- In efficient markets, high volume should produce significant price movement. When it does not, it means there is a large contra-side participant absorbing the flow. In A-shares, this often indicates institutional accumulation (at support) or distribution (at resistance). The mathematical signature `VR >> 1 AND PM << 0.5` captures this efficiently. The false positive risk is that limit-up/down locks also produce high volume with no price movement, so the detector needs limit-state filtering for A-shares.

---

## #19 [1WfufIwy] (Unnamed Script)

**Type:** Unknown -- no title or description available from fetch

**A-Share Suitability:** N/A

**Innovation:** N/A

**Verdict:** SKIP -- No accessible content.

---

## #20 [1tQCSEry] BANDOS FVG

**Type:** Fair Value Gap (FVG) detection and trading system

**Core Logic:** Detects Fair Value Gaps (imbalances between consecutive candles where the wick of one candle does not overlap with the next). These gaps represent areas of inefficient pricing that tend to be revisited. BANDOS likely adds band/zone filtering to FVG signals.

**Math Foundation:**
- Bullish FVG: `low[t] > high[t-2]` (gap between candle t and candle t-2)
- Bearish FVG: `high[t] < low[t-2]`
- Gap size: `gap = low[t] - high[t-2]` (bullish) or `low[t-2] - high[t]` (bearish)
- Zone filtering: only trade FVGs that occur within specific price bands (e.g., near support/resistance)
- Confluence: FVG + trend direction + volume confirmation

**Entry/Exit:** Buy when price retraces into a bullish FVG zone. Target is fill of the gap.

**A-Share Suitability:** 4/5 -- Gap analysis is particularly relevant in A-shares due to overnight gap behavior (earnings, news). FVG concept adapts well to daily bars. The zone filter adds selectivity.

**Innovation:** 3/5 -- FVG is an ICT/Smart Money Concepts technique that has gained popularity. The mathematical formulation (three-candle gap detection) is simple but the concept of "inefficient pricing zones" is grounded in market microstructure. The zone filter differentiates this from basic FVG detectors.

---

## #21 [1yJbrZuu] Market Structure Swings

**Type:** Market structure (Higher High/Higher Low) detection system

**Core Logic:** Automatically identifies swing highs and swing lows, then classifies the market structure as bullish (higher highs + higher lows) or bearish (lower highs + lower lows). Break of structure (BOS) signals occur when price breaks a significant swing point.

**Math Foundation:**
- Swing high: `pivot_high(left_bars, right_bars)` using standard pivot detection
- Swing low: `pivot_low(left_bars, right_bars)` 
- Structure classification: `HH = swing_high > prev_swing_high`, `HL = swing_low > prev_swing_low`
- Bullish structure: `HH AND HL`; Bearish: `LH AND LL`
- BOS: `close > last_opposite_swing_high` (bullish BOS) or `close < last_opposite_swing_low` (bearish BOS)

**Entry/Exit:** Enter long on bullish BOS. Enter short on bearish BOS. Exit on structure reversal.

**A-Share Suitability:** 4/5 -- Market structure analysis is timeframe-agnostic and works well on A-share daily charts. Swing detection with configurable left/right bars adapts to different volatility regimes. Pure OHLCV.

**Innovation:** 2/5 -- Market structure/BOS is a well-established concept from price action theory. The automated detection is useful engineering but the mathematics (pivot detection) are straightforward.

---

## #22 [28Fhhwv1] Dynamic FibTrend Signals (MarkitTick)

**Type:** Dynamic Fibonacci trend signal system

**Core Logic:** Dynamically calculates Fibonacci retracement levels based on the most recent swing high and swing low. Generates signals when price interacts with key Fibonacci levels (38.2%, 50%, 61.8%) in the context of the prevailing trend.

**Math Foundation:**
- Dynamic range: `swing_H = highest(high, swing_period)`, `swing_L = lowest(low, swing_period)`
- Fib levels: `level = swing_L + ratio * (swing_H - swing_L)` for ratio in {0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0}
- Signal at 61.8% retracement in uptrend (golden ratio buy zone)
- Trend filter: price above/below midpoint of range

**Entry/Exit:** Buy at 61.8% retracement in uptrend with confirmation. Sell at -27.2% extension or opposite signal.

**A-Share Suitability:** 3/5 -- Dynamic Fib levels adapt to changing market structure. However, the mathematical validity of Fibonacci ratios in financial markets is debated. Works as a self-fulfilling prophecy if enough market participants use them.

**Innovation:** 2/5 -- Dynamic (rolling) Fibonacci calculation is an improvement over static Fib levels. The mathematical foundation relies on the golden ratio hypothesis which lacks rigorous statistical proof.

---

## #23 [2BzaTkVY] lib demo

**Type:** Library demonstration script

**Core Logic:** Demonstrates how to use a Pine Script library. No trading logic.

**A-Share Suitability:** N/A

**Innovation:** N/A

**Verdict:** SKIP -- Library demo, not a strategy.

---

## #24 [2FFqD75h] Dead Zones from EdgeFinder

**Type:** Market state classification (dead zone detection)

**Core Logic:** Identifies "dead zones" -- periods where the market is in a low-conviction, choppy state with no clear directional bias. Helps traders avoid trading during these periods. The EdgeFinder approach likely uses multiple indicators to build a composite "edge score" and flags dead zones when the score is near zero.

**Math Foundation:**
- Composite score built from multiple indicators (likely ADX, volatility, volume)
- Dead zone: `abs(edge_score) < threshold` -- no statistical edge available
- Edge zone: `abs(edge_score) > threshold` -- directional conviction exists
- Volatility filter: `ATR(14) / close < vol_threshold` suppresses signals in low-vol periods
- Volume filter: below-average volume periods classified as dead zones

**Entry/Exit:** Only enter trades when NOT in a dead zone. The dead zone indicator itself does not generate directional signals -- it acts as a regime filter.

**A-Share Suitability:** 4/5 -- A-shares spend significant time in choppy, low-conviction consolidation phases. A dead zone detector that identifies when NOT to trade is valuable. Pure OHLCV implementation.

**Innovation:** 3/5 -- The concept of explicitly defining "no trade zones" is practical and often overlooked. Rather than generating more signals, this approach focuses on signal quality by identifying when the market lacks edge. The composite score architecture (combining ADX, volatility, volume into a single edge metric) is a sound framework.

**Insight:** Dead zone detection is equivalent to market regime classification. The mathematical approach reduces to estimating the signal-to-noise ratio of directional indicators. When SNR < threshold, the market is in a dead zone. This is a form of meta-analysis -- rather than asking "which direction?", it asks "is there a direction to trade?" -- which is often more valuable for risk management.

---

## #25 [2UvsIQxq] David Custom Watermark

**Type:** Chart watermark/branding tool

**Core Logic:** Displays a custom watermark on the chart. No trading logic.

**A-Share Suitability:** N/A

**Innovation:** N/A

**Verdict:** SKIP -- Cosmetic tool.

---

## #26 [2WSUSoYk] (Unnamed Script)

**Type:** Unknown -- no title or description available

**A-Share Suitability:** N/A

**Innovation:** N/A

**Verdict:** SKIP -- No accessible content.

---

## #27 [2aDenuuV] (Unnamed Script)

**Type:** Unknown -- no title or description available

**A-Share Suitability:** N/A

**Innovation:** N/A

**Verdict:** SKIP -- No accessible content.

---

## #28 [2d974dXO] EdgeMaster's PD High Continuation Probability Matrix

**Type:** Previous Day High break continuation probability estimator

**Core Logic:** Builds a probability matrix for whether price will continue higher after breaking above the previous day's high. Uses historical pattern analysis and multiple confirming factors to estimate continuation probability rather than giving simple buy/sell signals.

**Math Foundation:**
- Previous Day High: `PDH = high[1]`
- Break condition: `close > PDH`
- Continuation probability estimated from:
  - Gap direction: `open > PDH` (gap continuation) vs `open < PDH` (break from below)
  - Volume at break: `volume / SMA(volume, 20)` -- high volume confirms
  - Prior trend strength: `close > SMA(close, 50)` -- aligned with trend
  - ATR position: `how far above PDH relative to ATR` -- not extended too far
- Probability matrix: `P(continue | features)` built from historical conditional frequencies
- Output: probability score (e.g., 70% chance of continuation above PDH)

**Entry/Exit:** Enter long on PDH break when continuation probability > threshold (e.g., 65%). Stop below PDH or previous swing low.

**A-Share Suitability:** 4/5 -- Previous day high/low breaks are significant events in A-shares due to the daily close-to-open gap mechanics. The probability-based approach (rather than binary signal) is more useful for position sizing and risk management. Pure OHLCV.

**Innovation:** 4/5 -- The probability matrix approach is genuinely innovative. Rather than a binary "breakout or not" signal, it estimates the conditional probability of continuation given multiple features. This is a simple form of Naive Bayes classification applied to a specific market event (PDH break). The concept of "how likely is this breakout to work?" is more useful than "this is a breakout."

**Insight:** The probability matrix approach decomposes the breakout problem into conditional probabilities: P(continuation) = P(continue | gap_up) * P(gap_up) + P(continue | no_gap) * P(no_gap). Each factor (volume, trend alignment, ATR position) contributes independently. While this assumes feature independence (which is not strictly true), it provides a practical composite score. For A-shares, adding limit-up proximity as a feature would improve accuracy (breakouts near the 10% limit have different dynamics).

---

## #29 [2dJ9ioDl] MS Dashboard CDH

**Type:** Market Structure dashboard

**Core Logic:** Dashboard display of market structure information. Likely shows current market structure state (bullish/bearish BOS, CHoCH), key levels, and trend direction in a compact table format.

**Math Foundation:**
- Based on swing high/low detection
- Structure classification (HH/HL/LH/LL)
- Dashboard aggregation

**Entry/Exit:** No direct signals -- informational dashboard.

**A-Share Suitability:** 2/5 -- Dashboard is useful for quick assessment but provides no actionable signals on its own.

**Innovation:** 1/5 -- Dashboard implementation of standard market structure concepts.

---

# SUMMARY

## Total Processed: 30 scripts
- **Fully analyzed:** 26
- **Skipped (no content/tool):** 4 (indices 7, 19, 26, 27)
- **Non-strategy (tools/demos):** 4 (indices 8, 13, 15, 23, 25)

## High-Innovation Scripts (Innovation >= 4/5)

| # | Name | Innovation | A-Share | Key Innovation |
|---|------|-----------|---------|----------------|
| 9 | Adaptive Pivot-Length RSI (APL-RSI) | 5/5 | 5/5 | PMF-based adaptive RSI period, empirical percentile OB/OS |
| 28 | EdgeMaster's PD High Continuation Probability Matrix | 4/5 | 4/5 | Conditional probability matrix for breakout continuation |

## Notable Scripts (Innovation 3/5)

| # | Name | Innovation | A-Share | Key Concept |
|---|------|-----------|---------|-------------|
| 1 | LuxAlgo OI Inflows/Outflows | 3/5 | 1/5 | OI-based money flow (futures only) |
| 4 | Luminous Volume Flow Oscillator | 3/5 | 4/5 | Bar-polarity volume decomposition + zone filter |
| 10 | Jan Buy Hold Add + Doi Warning | 3/5 | 4/5 | Two-phase trend entry + baghold warning |
| 18 | Absorption Detector v1 | 3/5 | 4/5 | Volume absorption via VR * body-ratio |
| 20 | BANDOS FVG | 3/5 | 4/5 | Fair Value Gap with zone filtering |
| 24 | Dead Zones from EdgeFinder | 3/5 | 4/5 | Composite edge score dead zone detector |

## Cross-Cutting Patterns

1. **Volume decomposition is a recurring theme:** Scripts #1 (OI flow), #4 (bar-polarity volume), #18 (absorption) all attempt to decompose aggregate volume into directional components using different mathematical approaches. Bar-polarity (script #4) is the most practical for A-share daily data.

2. **Regime awareness is emerging:** Scripts #9 (adaptive period), #16 (ADX regime), #24 (dead zones), #28 (probability matrix) all incorporate some form of market state classification before generating signals. This is a significant improvement over fixed-parameter indicators.

3. **Multi-indicator confluence dominates:** The majority of scripts (0, 3, 6, 10, 12, 16) combine 2-3 indicators for signal qualification. The mathematical sophistication varies greatly -- from simple AND conditions to probability-weighted scoring.

4. **FVG/SMC concepts are trending:** Scripts #20 (FVG), #21 (market structure), #28 (PDH continuation) reflect the current TradingView community trend toward ICT/Smart Money Concepts. These are gaining popularity but their mathematical foundations are often thin.

## Key Insights for A-Share Strategy Development

1. **Adaptive period selection (from #9) is the highest-value idea.** The PMF approach to dynamically selecting indicator parameters based on current market cycle structure is directly transferable to any oscillator-type indicator (RSI, stochastic, CCI).

2. **Probability-weighted signals (from #28) over binary signals.** Rather than "buy" or "don't buy," estimating the probability of success given multiple conditional features enables better position sizing and risk management.

3. **Dead zone detection (from #24) as a meta-filter.** Identifying when NOT to trade is as valuable as identifying entries. A composite edge score that combines ADX, volatility regime, and volume state into a single "tradability" metric would improve any A-share strategy's performance by reducing drawdowns during choppy periods.

4. **Bar-polarity volume decomposition (from #4) is the best volume approach for daily data.** Without tick-level data, `BV = V * (C-L)/(H-L)` is the most practical estimator of directional volume. Combining this with the MACD-of-delta architecture creates a leading indicator of money flow.

5. **Absorption detection (from #18) has unique value for A-shares.** The pattern of high volume + small price movement at key levels is a strong institutional footprint signal in A-share markets where block trades are common and information asymmetry is high.
