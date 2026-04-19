# Batch 3 New - TradingView Strategy Analysis (Indices 0-29)
# Source: batch_3_new.json (100 scripts total, processing indices 0-29)
# Generated: 2026-04-19

---

## Script Analysis

### 0. Metis Fully Vested Entry Engine v1 [014kqYiX]
- **URL**: https://www.tradingview.com/script/014kqYiX-Metis-Fully-Vested-Entry-Engine-v1
- **Category**: multi_factor
- **Math Core**: Multi-factor pullback entry in confirmed uptrend. 50MA > 200MA trend filter, RSI(14) pullback zone (30-50), relative volume confirmation (> 1.0x average), price proximity to 50MA. Signal generated only on first qualifying bar to avoid repetition.
- **Innovation**: 2/5 - Standard MA crossover + RSI pullback framework with volume filter
- **A-Share Applicability**: 3/5 - MA trend filter + RSI + volume works on A-share daily bars, but pullback entry logic may underperform in A-share 10% limit environments
- **Key Params**: MA_Fast=50, MA_Slow=200, RSI_Length=14, RSI_Pullback_Low=30, RSI_Pullback_High=50, Vol_Length=20

---

### 1. Money Inflows & Outflows [xiaofashi/LuxAlgo] [01lrRndV]
- **URL**: https://www.tradingview.com/script/01lrRndV
- **Category**: volume
- **Math Core**: Open Interest (OI) based money flow analysis. Uses EMA(13) smoothing and correlation(13) between price and OI to detect inflows/outflows. OI rising + price rising = inflow; OI falling + price falling = outflow.
- **Innovation**: 3/5 - Novel application of OI correlation to classify money flow direction
- **A-Share Applicability**: 2/5 - Requires OI data which is not standard for A-share equities (futures only)
- **Key Params**: EMA_Length=13, Correlation_Length=13

---

### 2. FVG Full System ATR Filters Stacking [03YOQhxh]
- **URL**: https://www.tradingview.com/script/03YOQhxh-FVG-Full-System-ATR-Filters-Stacking
- **Category**: multi_factor
- **Math Core**: Fair Value Gap detection combined with stacked ATR filters. FVG = gap between bar[2] low and bar[0] high (bullish) or bar[2] high and bar[0] low (bearish). ATR filters validate gap significance by comparing gap size to ATR multiplier thresholds.
- **Innovation**: 2/5 - Standard FVG concept with ATR validation layer
- **A-Share Applicability**: 3/5 - FVG works on daily OHLCV but A-share 10% limits reduce gap frequency
- **Key Params**: ATR_Length=14, ATR_Multiplier=1.5, FVG_Min_Size_ATR=0.5

---

### 3. Tops And Bottoms [03ZAIYhM]
- **URL**: https://www.tradingview.com/script/03ZAIYhM-Tops-And-Bottoms
- **Category**: price_action
- **Math Core**: RSI(14) + volume confirmation for swing top/bottom detection. RSI overbought (>70) + declining volume at swing high = top. RSI oversold (<30) + declining volume at swing low = bottom. Uses pivot high/low with left/right lookback windows.
- **Innovation**: 1/5 - Classic RSI + volume divergence approach
- **A-Share Applicability**: 3/5 - Works on A-share daily but RSI thresholds may need adjustment for trending A-share markets
- **Key Params**: RSI_Length=14, RSI_Overbought=70, RSI_Oversold=30, Pivot_Left=5, Pivot_Right=5

---

### 4. CRUCE EMA 3-9-20 PRO FLEX + ADX [0ECs7la9]
- **URL**: https://www.tradingview.com/script/0ECs7la9
- **Category**: trend
- **Math Core**: Triple EMA crossover system (EMA 3, 9, 20) with ADX trend strength filter. Entry when EMA(3) > EMA(9) > EMA(20) and ADX > 20. Exit on reverse cross. ADX acts as regime gate - no trades when ADX < 20 (no trend).
- **Innovation**: 1/5 - Standard triple EMA crossover with ADX filter
- **A-Share Applicability**: 4/5 - Simple and effective on A-share daily; EMA crossover well-suited for trending A-share stocks
- **Key Params**: EMA_Fast=3, EMA_Mid=9, EMA_Slow=20, ADX_Length=14, ADX_Threshold=20

---

### 5. Luminous Volume Flow Oscillator [Pineify] [0KflNXqI]
- **URL**: https://www.tradingview.com/script/0KflNXqI-Luminous-Volume-Flow-Oscillator-Pineify
- **Category**: volume
- **Math Core**: Bar polarity volume delta calculation. For bullish bars: volume * ((close - low) / (high - low)). For bearish bars: -volume * ((high - close) / (high - low)). Smoothed with EMA(14), signal line SMA(9). Oscillator measures cumulative buying vs selling pressure.
- **Innovation**: 3/5 - Clean bar-polarity volume decomposition into directional flow
- **A-Share Applicability**: 4/5 - Pure OHLCV-based, high-quality A-share volume data makes this effective
- **Key Params**: EMA_Length=14, SMA_Signal=9

---

### 6. Targets High/Low ULTIMATE V14.6 [0LOublbQ]
- **URL**: https://www.tradingview.com/script/0LOublbQ
- **Category**: volatility
- **Math Core**: Market breadth indicator for target price levels. Uses advancing/declining issues ratio and up-volume/down-volume ratio to compute projected high/low targets. Essentially a breadth-based price projection system.
- **Innovation**: 1/5 - Standard breadth-based target calculation
- **A-Share Applicability**: 2/5 - Requires market breadth data (advancing/declining issues) which is not directly available in A-share daily data
- **Key Params**: Lookback=20

---

### 7. Hull RSI Trend Rider Pro [0ZBQpzty]
- **URL**: https://www.tradingview.com/script/0ZBQpzty-Hull-RSI-Trend-Rider-Pro
- **Category**: trend
- **Math Core**: Hull Moving Average applied to RSI values. HMA(RSI, period) creates a smoother, less lagging RSI signal. Trailing stop (ATR-based) provides exit mechanism. Entry when HMA-RSI crosses above signal line in uptrend (price > MA200).
- **Innovation**: 2/5 - HMA smoothing of RSI is straightforward but effective
- **A-Share Applicability**: 3/5 - Works on A-share daily; HMA lag reduction helpful for A-share momentum plays
- **Key Params**: RSI_Length=14, HMA_Length=14, ATR_Trailing_Length=14, ATR_Trailing_Multi=2.0, MA_Trend=200

---

### 8. [Fetch Failed] [0el0Zp7j]
- **URL**: https://www.tradingview.com/script/0el0Zp7j
- **Status**: Script may be private, deleted, or unlisted. No data available.

---

### 9. [Fetch Failed] [0hGVByv0]
- **URL**: https://www.tradingview.com/script/0hGVByv0
- **Status**: Rate limited. Could not fetch page content.

---

### 10. Adaptive Pivot Length RSI [0yDdkPIp]
- **URL**: https://www.tradingview.com/script/0yDdkPIp-Adaptive-Pivot-Length-RSI
- **Category**: mean_reversion
- **Math Core**: RSI with dynamically adjusted lookback period. The pivot length adapts based on recent market volatility - higher volatility = shorter lookback for faster response, lower volatility = longer lookback for stability. Uses ATR ratio (short ATR / long ATR) to modulate the RSI period.
- **Innovation**: 3/5 - Adaptive RSI period based on volatility regime is a useful improvement over fixed-period RSI
- **A-Share Applicability**: 4/5 - Pure OHLCV, ATR-based adaptation works well with A-share volatility patterns
- **Key Params**: RSI_Base_Length=14, ATR_Short=7, ATR_Long=28, RSI_Min=7, RSI_Max=28

---

### 11. [Fetch Failed] [13If880V]
- **URL**: https://www.tradingview.com/script/13If880V
- **Status**: Rate limited. Could not fetch page content.

---

### 12. Wick to Close Distance Pips [13gJPimb]
- **URL**: https://www.tradingview.com/script/13gJPimb-Wick-to-Close-Distance-Pips
- **Category**: price_action
- **Math Core**: Measures distance from high to close (upper wick) and low to close (lower wick) in pips. Upper_wick = High - Close, Lower_wick = Close - Low. Used to detect rejection candles and pressure direction.
- **Innovation**: 2/5 - Simple wick analysis, useful as a building block but not a standalone strategy
- **A-Share Applicability**: 3/5 - Works on A-share OHLCV but pip-based measurement needs adaptation for A-share price ranges
- **Key Params**: None (measurement tool)

---

### 13. RSI Price Divergence MTF Alerts [14eqfJ5q]
- **URL**: https://www.tradingview.com/script/14eqfJ5q-RSI-Price-Divergence-MTF-Alerts
- **Category**: mean_reversion
- **Math Core**: Multi-timeframe RSI divergence detection. Bullish divergence: price makes lower low but RSI makes higher low. Bearish divergence: price makes higher high but RSI makes lower high. Scans multiple timeframes (15m, 1H, 4H, Daily) for divergence confluence.
- **Innovation**: 2/5 - Standard RSI divergence with MTF overlay
- **A-Share Applicability**: 4/5 - RSI divergence on A-share daily/60min is well-proven; MTF confluence adds robustness
- **Key Params**: RSI_Length=14, Timeframes=[15m, 60m, 240m, D], Pivot_Lookback=10

---

### 14. Day trade info tablouh [15Rk9hvy]
- **URL**: https://www.tradingview.com/script/15Rk9hvy-Day-trade-info-tablouh
- **Category**: volatility
- **Math Core**: Multi-timeframe volatility and momentum dashboard. Computes ADR (Average Daily Range) and ATR across multiple timeframes, combined with RSI momentum readings. Dashboard display for quick intraday assessment.
- **Innovation**: 2/5 - Information aggregation dashboard, not a signal generator
- **A-Share Applicability**: 3/5 - ADR/ATR dashboard useful for A-share day traders but not a tradable strategy
- **Key Params**: ATR_Length=14, RSI_Length=14

---

### 15. OVS Key Levels [1E8gnrL5]
- **URL**: https://www.tradingview.com/script/1E8gnrL5-OVS-Key-Levels
- **Category**: price_action
- **Math Core**: Key support/resistance level identification based on pivot points and historical swing highs/lows. Levels scored by number of touches and volume at each level. Strongest levels have most touches + highest volume.
- **Innovation**: 1/5 - Standard pivot-based S/R with volume scoring
- **A-Share Applicability**: 4/5 - Pivot S/R levels work well on A-share daily charts; volume confirmation is additive
- **Key Params**: Pivot_Left=5, Pivot_Right=5, Min_Touches=3

---

### 16. [Fetch Failed] [1MEWPvsR]
- **URL**: https://www.tradingview.com/script/1MEWPvsR-Event-Marker-20-Events
- **Status**: Rate limited. Could not fetch page content.

---

### 17. ES Breakout Toolkit ADX Regime Filter Free [1O196EXo]
- **URL**: https://www.tradingview.com/script/1O196EXo-ES-Breakout-Toolkit-ADX-Regime-Filter-Free
- **Category**: multi_factor
- **Math Core**: ADX-based regime classification into 3 states: Trending (ADX>25, DI+>DI- or DI->DI+), Ranging (ADX<20), Transitional (20<ADX<25). Within trending regime, breakout signals generated when price exceeds Donchian channel with DI direction confirmation. Slope tracking of ADX for regime transition early warning.
- **Innovation**: 3/5 - Three-state ADX regime model with slope-based transition detection is more nuanced than binary trend/range
- **A-Share Applicability**: 4/5 - ADX regime classification works on all markets; Donchian breakout is universal
- **Key Params**: ADX_Length=14, ADX_Trend=25, ADX_Range=20, Donchian_Length=20

---

### 18. Joey's PDH and PDL [1RceVPF7]
- **URL**: https://www.tradingview.com/script/1RceVPF7-Joey-s-PDH-and-PDL
- **Category**: price_action
- **Math Core**: Plots previous day's high and low as horizontal reference lines. PDH = highest high of previous session, PDL = lowest low of previous session. Simple reference for intraday mean reversion or breakout targets.
- **Innovation**: 1/5 - Basic previous day range levels
- **A-Share Applicability**: 4/5 - Previous day H/L levels are universally useful including A-share daily trading
- **Key Params**: None (uses previous session OHLC)

---

### 19. Absorption Detector v1 [1WGjQ7YC]
- **URL**: https://www.tradingview.com/script/1WGjQ7YC-Absorption-Detector-v1
- **Category**: volume
- **Math Core**: Detects absorption patterns in order flow. Absorption occurs when price fails to advance despite high volume at extreme levels (near high or low). Uses volume * proximity-to-extreme metric. High volume near bar high + price rejection = absorption of sellers; High volume near bar low + price rejection = absorption of buyers.
- **Innovation**: 2/5 - Volume-at-extreme rejection concept is known but implementation is clean
- **A-Share Applicability**: 3/5 - OHLCV-based proxy works on A-share but true absorption detection requires Level 2 data
- **Key Params**: Volume_Multiplier=1.5, Proximity_Threshold=0.2 (20% of range from extreme)

---

### 20. [Fetch Failed] [1WfufIwy]
- **URL**: https://www.tradingview.com/script/1WfufIwy
- **Status**: Rate limited. Could not fetch page content.

---

### 21. [Fetch Failed] [1tQCSEry]
- **URL**: https://www.tradingview.com/script/1tQCSEry-20-BANDOS-FVG
- **Status**: Rate limited. Could not fetch page content.

---

### 22. Market Structure Swings [1yJbrZuu]
- **URL**: https://www.tradingview.com/script/1yJbrZuu-Market-Structure-Swings
- **Category**: price_action
- **Math Core**: Three-level swing detection system: Regular (5-bar fractal), Intermediate (15-bar pivot), Major (50-bar structural swing). Uses fractal pattern recognition + pivot point analysis + trend structure classification. Swings labeled as HH/HL/LH/LL for structure tracking. BOS (Break of Structure) and CHoCH (Change of Character) detected at each level.
- **Innovation**: 2/5 - Multi-scale swing analysis with SMC labeling is increasingly common
- **A-Share Applicability**: 4/5 - Pure price-based structure analysis works universally; 3-level granularity useful for A-share swing trading
- **Key Params**: Regular_Length=5, Intermediate_Length=15, Major_Length=50

---

### 23. Dynamic FibTrend Signals MarkitTick [28Fhhwv1]
- **URL**: https://www.tradingview.com/script/28Fhhwv1-Dynamic-FibTrend-Signals-MarkitTick
- **Category**: trend
- **Math Core**: SuperTrend ATR-based trend direction + Pivot swing structure + Dynamic Fibonacci retracement grid (0%, 23.6%, 38.2%, 50%, 61.8%, 78.6%, 100%). Auto-calculates entry at Fib 50% or 61.8% pullback zone with ATR-based SL and R:R ratio TP. Based on Volatility Clustering theory - after low volatility (tight SuperTrend), high volatility moves follow.
- **Innovation**: 3/5 - Integration of SuperTrend + Fib grid + auto risk geometry in one system
- **A-Share Applicability**: 4/5 - All components (SuperTrend, Fib, ATR) work on A-share daily OHLCV
- **Key Params**: ATR_Length=10, ATR_Factor=3.0, Swing_Lookback=10, Fib_Lookback=50, Risk_Reward=2.0

---

### 24. EQH/EQL Liquidity Zones LuxAlgo [29faH0pr]
- **URL**: https://www.tradingview.com/script/29faH0pr-EQH-EQL-Liquidity-Zones-LuxAlgo
- **Category**: price_action
- **Math Core**: Pivot-based Equal Highs/Lows (EQH/EQL) detection with percentage threshold. Two pivot highs within equality_threshold% are marked as EQH; two pivot lows within threshold are EQL. Dynamic zone merging: zones within merge_distance% are combined. Volume-weighted zone scoring. Sweep detection: price pierces zone then reverses = liquidity sweep. SMC (Smart Money Concept) framework.
- **Innovation**: 3/5 - Automated EQH/EQL detection with zone merging and sweep detection
- **A-Share Applicability**: 4/5 - Pivot-based liquidity zones work on A-share daily; sweep detection useful for A-share stop-loss hunting analysis
- **Key Params**: Pivot_Left=5, Pivot_Right=5, Equality_Threshold=0.05%, Max_Active_Zones=10, Merge_Distance=0.1%

---

### 25. [Fetch Failed] [2BzaTkVY]
- **URL**: https://www.tradingview.com/script/2BzaTkVY-lib-demo
- **Status**: Rate limited. Likely a library demo, not a standalone strategy.

---

### 26. Dead Zones from EdgeFinder [2FFqD75h]
- **URL**: https://www.tradingview.com/script/2FFqD75h-Dead-Zones-from-EdgeFinder
- **Category**: volatility
- **Math Core**: Genetic-algorithm generated daily price zones for 5-minute intraday scalping. Zones are pre-computed externally by EdgeFinder's GA engine based on historical price patterns. The Pine Script displays these zones. Tags: forecasting, regressions. Zones represent "dead" areas where price tends to stall or reverse.
- **Innovation**: 3/5 - External GA-generated zone system is an interesting approach but relies on external computation
- **A-Share Applicability**: 2/5 - Zones are pre-generated externally and may be market-specific; not self-contained for A-share adaptation
- **Key Params**: Zone_Generation=External (EdgeFinder GA)

---

### 27. [Fetch Failed] [2FZ6IMlN]
- **URL**: https://www.tradingview.com/script/2FZ6IMlN
- **Status**: Rate limited. Could not fetch page content.

---

### 28. Kaufman Efficiency Ratio Gate NovaLens [2Ghnhfqg]
- **URL**: https://www.tradingview.com/script/2Ghnhfqg-Kaufman-Efficiency-Ratio-Gate-NovaLens
- **Category**: trend
- **Math Core**: Kaufman Efficiency Ratio (KER) = abs(close - close[length]) / sum(abs(close - close[1]), length). KER measures trend quality: values near 1 = clean trend, near 0 = noise/choppy. Used as a gate/filter: only take signals from other indicators when KER > threshold. Prevents entries during choppy, directionless markets.
- **Innovation**: 3/5 - KER as a signal quality gate is an elegant filter concept
- **A-Share Applicability**: 4/5 - Pure price-based, works on A-share daily; effective at filtering out A-share choppy consolidation periods
- **Key Params**: KER_Length=20, KER_Threshold=0.3

---

### 29. Auto Adaptive MA Profiles PRO [2RPafiIe]
- **URL**: https://www.tradingview.com/script/2RPafiIe-Adaptive-Spectral-Bands-JOAT
- **Category**: multi_factor
- **Math Core**: Dynamic MA profile auto-switching per timeframe with 9 MA types (SMA, EMA, WMA, VWMA, HMA, RMA, DEMA, TEMA, ZLEMA). "Gear shifting" logic: fast TFs (1m-15m) use HMA/ZLEMA for responsiveness; slow TFs (Daily+) use institutional SMA for stability. Volume-based ATR Supertrend provides independent trend confirmation. Pine Screener for multi-asset filtering. No repaint.
- **Innovation**: 4/5 - Novel auto-adaptive MA type selection per timeframe creates a self-tuning system that eliminates manual parameter optimization
- **A-Share Applicability**: 4/5 - All 9 MA types work on A-share OHLCV; auto-TF adaptation means same code works on 60min or daily without parameter changes
- **Key Params**: Per-TF MA type/period (auto), Supertrend_ATR_Period=10, Supertrend_Factor=3.0

---

## Highlights - Top Innovative Strategies (Innovation >= 4)

| # | Name | Innovation | A-Share | Key Innovation |
|---|------|-----------|---------|----------------|
| 29 | Auto Adaptive MA Profiles PRO | 4/5 | 4/5 | Auto-adaptive MA type per timeframe (9 MA types, "gear shifting" logic) |

---

## Summary Statistics

| Metric | Count |
|--------|-------|
| Total scripts processed | 30 |
| Successfully fetched & analyzed | 21 |
| Fetch failed (rate limit/private) | 9 |
| Innovation >= 4 | 1 |
| A-Share Applicability >= 4 | 12 |

### Category Distribution

| Category | Count |
|----------|-------|
| trend | 4 |
| multi_factor | 4 |
| price_action | 5 |
| volume | 3 |
| volatility | 3 |
| mean_reversion | 2 |
| fetch_failed | 9 |

### Innovation Distribution

| Score | Count |
|-------|-------|
| 4/5 | 1 |
| 3/5 | 7 |
| 2/5 | 8 |
| 1/5 | 5 |
| N/A (fetch failed) | 9 |

### A-Share Applicability Distribution

| Score | Count |
|-------|-------|
| 4/5 | 12 |
| 3/5 | 7 |
| 2/5 | 2 |
| N/A (fetch failed) | 9 |
