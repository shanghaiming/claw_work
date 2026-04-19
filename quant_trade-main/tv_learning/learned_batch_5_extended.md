# Batch 5 Strategy Analysis (Index 0-29)

**Date:** 2026-04-19
**Source:** batch_5.json (121 scripts, first 30 processed)

---

## [0] ebIjXmQR - ICT Multi Strategy Scalper PRO v3

**URL:** https://www.tradingview.com/script/ebIjXmQR-ICT-Multi-Strategy-Scalper-PRO-v3
**Category:** ICT / Chart Patterns / Multi-Strategy Scalper
**Indicators Used:** ICT concepts (likely FVG, OB, Silver Bullet patterns), multi-strategy confluence
**Entry/Exit Conditions:** Multiple ICT strategy signals combined in a scalper framework; exact logic not fully documented (minimal description on page)
**A-Share Daily Suitability:** No - ICT scalping concepts are optimized for intraday futures/forex markets
**Mathematical Foundation:** Pattern recognition of institutional market structure concepts
**Innovation Rating:** 2/5 (multi-strategy aggregation is common, ICT-specific)
**Notes:** Open-source, 286 uses, 19 likes. Tagged as "Chart patterns". Minimal description available - the actual Pine code would reveal specific logic.

---

## [1] ex5eKUo1 - Higher/Lower Close Count PRO+

**URL:** https://www.tradingview.com/script/ex5eKUo1-Higher-Lower-Close-Count-PRO-Daily-close-counts
**Category:** Statistical Counting / Mean Reversion Context
**Indicators Used:** Raw close comparison (no traditional indicator)
**Entry/Exit Conditions:** Counts consecutive days closing higher/lower; displays historical max up/down runs in table for context
**A-Share Daily Suitability:** Yes - uses daily close data only, pure statistical context
**Mathematical Foundation:** Binary consecutive directional close counting; run-length statistics
**Innovation Rating:** 2/5 (straightforward statistical counting tool)
**Notes:** Contextual tool rather than direct signal generator. Useful for understanding how unusual a current streak is relative to history.

---

## [2] f2qqYN1c - Daily Trading Times UTC+2

**URL:** https://www.tradingview.com/script/f2qqYN1c-Daily-Trading-Times-UTC-2-By-NickZZ
**Category:** Session / Time-Based
**Indicators Used:** Time-based session markers only
**Entry/Exit Conditions:** Marks best intraday trading times for ILM/IFVG strategies
**A-Share Daily Suitability:** No - forex/session-specific, UTC time-based, irrelevant for A-share daily data
**Mathematical Foundation:** None (pure time overlay)
**Innovation Rating:** 1/5 (no mathematical strategy logic)
**Notes:** Utility tool for forex/session traders only.

---

## [3] f8lJ6xr0 - Pigo 848 Trend NQGC

**URL:** https://www.tradingview.com/script/f8lJ6xr0
**Category:** Trend Detection / Futures-Specific
**Indicators Used:** Sentiment-based trend signals (strong/medium/weak classification)
**Entry/Exit Conditions:** Spots trends on NQ and GC futures with strong, medium, and weak signal classification
**A-Share Daily Suitability:** No - designed specifically for NQ (Nasdaq) and GC (Gold) futures
**Mathematical Foundation:** Unclear from minimal description; tagged "sentiment"
**Innovation Rating:** 1/5 (insufficient documentation to assess)
**Notes:** Very minimal description. Open-source with 69 uses. Targeted at futures traders.

---

## [4] fHvBm6UW - Mapa de Liquidaciones (Liquidation Map)

**URL:** https://www.tradingview.com/script/fHvBm6UW
**Category:** Market Microstructure / Liquidation Estimation
**Indicators Used:** Volume, Open Interest, Leverage formulas
**Entry/Exit Conditions:** Identifies estimated leveraged liquidation zones via heatmap visualization
**A-Share Daily Suitability:** Partially - A-shares lack the same leveraged futures ecosystem, but the mathematical framework is transferable
**Mathematical Foundation:**
- Long liquidation = price * (1 - 1/leverage)
- Short liquidation = price * (1 + 1/leverage)
- Accumulates volume/OI at theoretical liquidation levels
- Creates heatmap of estimated forced-selling zones
**Innovation Rating:** 4/5 (novel liquidation estimation framework with practical heat mapping)
**Key Insight:** By estimating where leveraged positions would be liquidated, this creates a "gravity map" of price levels where cascading forced sales/buy-ins would occur. The math is simple (inverse leverage distance from current price) but the concept of aggregating volume at these theoretical levels creates a powerful visual representation of market fragility.

---

## [5] fRXnVB3Q - Multi-Indicator Screener 30 Assets

**URL:** https://www.tradingview.com/script/fRXnVB3Q-Multi-Indicator-Screener-30-Assets
**Category:** Market Breadth / Multi-Asset Screener
**Indicators Used:** RSI, MACD, EMA Slope, OBV Trend, Supertrend, VWAP, ADX/DMI, BB %B, Stoch RSI, Vol Delta (10 total)
**Entry/Exit Conditions:** Classifies each of 30 assets as Strong Bullish, Weak Bullish, Weak Bearish, or Strong Bearish using dual-condition filters per indicator
**A-Share Daily Suitability:** Yes conceptually - the 10 indicator framework works on any OHLCV data. Would need custom A-share ticker lists.
**Mathematical Foundation:**
- EMA Slope: atan(ema_change / (pts_per_bar x slope_period)) x 180 / pi (geometric slope in degrees, normalized against 200-bar range)
- Vol Delta: (2*close - high - low) / (high - low), smoothed with EMA - approximates within-bar buying/selling pressure
- RSI dual filter: RSI vs 50 midline AND vs RSI's own SMA
- MACD histogram direction change (acceleration vs deceleration)
- OBV dual-MA crossover with trend confirmation
**Innovation Rating:** 4/5 (comprehensive multi-indicator breadth system with novel Vol Delta approximation)
**Key Insight:** The Vol Delta formula (2*close - high - low) / (high - low) is a clever approximation of within-bar buying/selling pressure. When close equals high, delta = +1; when close equals low, delta = -1. This normalizes bar-level directional pressure without requiring tick data. The EMA slope calculation with degree normalization creates a universal, asset-independent angle measurement.

---

## [6] ff7qSzca - SMA8 Reversion Simple

**URL:** https://www.tradingview.com/script/ff7qSzca
**Category:** Mean Reversion / Statistical Probability
**Indicators Used:** SMA(8), deviation thresholds, historical probability matrix
**Entry/Exit Conditions:**
- Signal fires when price deviates beyond configurable threshold from SMA8
- Tracks whether price returns to SMA within max candles
- Classifies signals into 4x3 matrix (distance level x time elapsed)
- Weak (<40%), Neutral (40-60%), Good (60-75%), Very Strong (>75%) return probability
**A-Share Daily Suitability:** Yes - works on any asset/timeframe, pure OHLCV
**Mathematical Foundation:**
- 4x3 contingency matrix: 4 distance ranges x 3 time ranges (early/mid/late)
- 12 independent cells, each with historical return-to-SMA rate
- Statistical base built from asset's own historical data
- Zero repaint - confirmed bars only
**Innovation Rating:** 4/5 (novel self-calibrating mean reversion probability matrix)
**Key Insight:** Rather than using fixed deviation levels, this indicator builds a per-asset, per-situation historical probability database. The 4x3 matrix (distance x time) is a practical implementation of conditional probability: P(return_to_SMA | distance_level, time_elapsed). This is a data-driven approach where the indicator "learns" the reversion characteristics of each specific asset. The "best zone" feature identifies the historically most profitable distance+time combination.

---

## [7] fuBvjSaj - Open Interest with Futures Matcher

**URL:** https://www.tradingview.com/script/fuBvjSaj-open-interest-with-futures-matcher
**Category:** Utility / Open Interest Tool
**Indicators Used:** Open Interest, futures contract matching
**Entry/Exit Conditions:** Matches spot contracts to futures (.P suffix) for OI calculation
**A-Share Daily Suitability:** No - futures-specific, A-share OI data differs fundamentally
**Mathematical Foundation:** Contract symbol matching and OI data retrieval
**Innovation Rating:** 1/5 (utility tool, not a strategy)
**Notes:** Pure data utility for futures traders needing OI visibility.

---

## [8] g0QS5WSP - CISD AND FVG

**URL:** https://www.tradingview.com/script/g0QS5WSP-CISD-AND-FVG
**Category:** Smart Money Concepts (SMC)
**Indicators Used:** BOS (Break of Structure), CHOCH (Change of Character), CISD (Change in State of Delivery), FVG (Fair Value Gap), IFVG (Intermediate FVG)
**Entry/Exit Conditions:**
- Detects market structure breaks (BOS/CHOCH)
- Identifies CISD zones (institutional order flow shift)
- Maps FVG zones that transition to IFVG (intermediate/mitigated gaps)
- Confluence of structure + gap zones for entry
**A-Share Daily Suitability:** Yes - pure price-action based, works on OHLCV
**Mathematical Foundation:** Swing high/low detection, price gap identification (high[1] < low[+1] or vice versa), structure break confirmation via close beyond swing points
**Innovation Rating:** 3/5 (clean implementation of SMC framework)
**Key Insight:** The CISD concept (Change in State of Delivery) is interesting - it identifies when institutional order flow changes direction, creating potential S/R zones. Combined with FVG/IFVG, it creates a multi-layered price structure map without requiring any mathematical indicators.

---

## [9] g0jGKt3K - MNQ OR Retest Breakout 5m

**URL:** https://www.tradingview.com/script/g0jGKt3K-MNQ-OR-Retest-Breakout-5m
**Category:** Opening Range Breakout
**Indicators Used:** Opening Range (first 15min high/low), session time filters
**Entry/Exit Conditions:** Opening Range (first 15min) breakout + retest entry; NY and Asia session specific
**A-Share Daily Suitability:** Partially - ORB concept is universal but session times are US-market specific
**Mathematical Foundation:** Session high/low tracking within defined time window
**Innovation Rating:** 2/5 (standard ORB with retest filter)
**Notes:** The retest entry adds one layer of confirmation beyond basic ORB.

---

## [10] g2vSmtry - Classic EMA 9/21 Crossover

**URL:** https://www.tradingview.com/script/g2vSmtry-Classic-EMA-9-21-crossover-with-Buy-Sell-signal
**Category:** Moving Average Crossover
**Indicators Used:** EMA(9), EMA(21)
**Entry/Exit Conditions:** EMA(9) crosses EMA(21) -> Buy/Sell signals. Best on Daily/Weekly/Monthly timeframes
**A-Share Daily Suitability:** Yes - universal, works on any OHLCV data
**Mathematical Foundation:** Standard EMA crossover: EMA(t) = alpha * close + (1-alpha) * EMA(t-1), where alpha = 2/(period+1)
**Innovation Rating:** 1/5 (textbook EMA crossover)
**Notes:** Baseline strategy. Useful as benchmark.

---

## [11] g4zjCqpe - Session Levels IQ [TradingIQ]

**URL:** https://www.tradingview.com/script/g4zjCqpe-Session-Levels-IQ-TradingIQ
**Category:** Session Expansion Statistics / Probability Grid
**Indicators Used:** Session open price, percentage distance grid, historical hit-rate tracking
**Entry/Exit Conditions:**
- Builds percentage-distance levels outward from session open
- Tracks hit rate per level across historical sessions
- Measures typical follow-through (median move-after-hit) for each level
- Identifies "normal" vs "unusual" expansion zones
**A-Share Daily Suitability:** Yes - works with daily session data, concept directly applicable
**Mathematical Foundation:**
- Percentage grid: level_price = session_open * (1 +/- n*spacing%)
- Hit rate = count(level_touched) / count(sessions)
- Median follow-through after each level hit
- Normal range = configurable percentage defining typical vs unusual expansion
**Innovation Rating:** 4/5 (novel session expansion probability framework with move-after-hit tracking)
**Key Insight:** This transforms session opens from a single reference point into a full statistical framework. By measuring not just "how often" price reaches a level but "what happens after" it reaches that level, it creates a conditional probability surface: P(large_continuation | level_touched). The normal vs unusual zone distinction is effectively an empirical outlier detection system.

---

## [12] g7XzbpVB - Marubozu Candlesticks

**URL:** https://www.tradingview.com/script/g7XzbpVB-Marubozu-Candlesticks
**Category:** Candlestick Pattern Recognition
**Indicators Used:** Raw OHLC pattern matching, horizontal S/R extension
**Entry/Exit Conditions:**
- Detects candles with no wicks (full body candles = Marubozu)
- Extends horizontal S/R levels from the open price (where the flat side is)
- Multi-timeframe detection in V2
**A-Share Daily Suitability:** Yes - pure price action, no market-specific logic
**Mathematical Foundation:** Pattern matching: body == range (no upper/lower wick beyond body)
**Innovation Rating:** 2/5 (standard candlestick pattern + S/R extension)
**Notes:** The S/R extension from the open price of a Marubozu is a practical addition.

---

## [13] gcPZFTFt - Multi-Length Displaced MA Indicator

**URL:** https://www.tradingview.com/script/gcPZFTFt-Multi-Length-Displaced-MA-Indicator
**Category:** Multi-Timeframe Moving Average System
**Indicators Used:** DMA (Displaced Moving Average), SMA, EMA, VWMA across 5 roles
**Entry/Exit Conditions:**
- MA1 (Momentum Trigger): length=5, offset=3 - immediate momentum shifts
- MA2 (Short-Term Trend): length=9, offset=5 - fast-moving trend
- MA3 (Institutional Pivot): length=21 - mean reversion zone
- MA4 (Decision Line): length=50 - bull/bear threshold
- MA5 (Trend Anchor): length=200 - macro bias
- Entry: MA1 crosses MA2; Support at MA3/MA4; Noise filter via displacement
**A-Share Daily Suitability:** Yes - standard OHLCV, no market-specific logic
**Mathematical Foundation:**
- DMA = SMA(close, length)[offset] (time-shifted moving average)
- Positive displacement shifts MA forward (creates "buffer" zone)
- Negative displacement shifts backward (reveals lead/lag relationships)
- Each MA slot supports SMA, EMA, VWMA, or DMA type selection
**Innovation Rating:** 3/5 (well-structured 5-role MA hierarchy with displacement buffer concept)
**Key Insight:** The displacement concept creates a "forward-looking buffer" - by shifting a fast MA forward, you require price to have sustained its move beyond the displaced line, effectively filtering whipsaws. The 5-role hierarchy (Momentum -> Short-Term -> Institutional -> Decision -> Anchor) maps cleanly to different market participant timeframes.

---

## [14] gFDJ3T0g - Aegis The Alchemist Quantum

**URL:** https://www.tradingview.com/script/gFDJ3T0g
**Category:** Trend-Momentum Hybrid
**Indicators Used:** Hull Moving Average (HMA), RSI smoothed with EMA
**Entry/Exit Conditions:**
- Quantum Rail (HMA): Yellow/Purple color for bullish/bearish trend bias
- Momentum Crossover: RSI smoothed with EMA, signals when momentum breaks 50-level IN THE DIRECTION of the Quantum Rail trend
- L/S (Long/Short) labels based on confluence of trend + momentum
- Power Index: intensity of current move as percentage
**A-Share Daily Suitability:** Yes - standard OHLCV, no market-specific logic
**Mathematical Foundation:**
- HMA = WMA(2*WMA(close, n/2) - WMA(close, n), sqrt(n)) - reduced lag via weighted differencing
- EMA-smoothed RSI crossing 50 level as momentum gate
- Directional filter: only signal in direction of HMA trend
**Innovation Rating:** 3/5 (clean trend-momentum confluence with HMA as trend filter)
**Key Insight:** The "directional gate" concept - only taking momentum signals that align with the HMA trend direction - is a simple but effective noise filter. The Power Index as a percentage measure of move intensity is useful for position sizing context.

---

## [15] geMQrUra - BearMetricsBlack

**URL:** https://www.tradingview.com/script/geMQrUra
**Category:** Portfolio Management / Statistics
**Indicators Used:** Portfolio statistics (modified from original BearMetric script)
**Entry/Exit Conditions:** N/A - this is a portfolio metrics display tool
**A-Share Daily Suitability:** Yes conceptually, but it's a display/visualization tool
**Mathematical Foundation:** Standard portfolio statistics (Sharpe, drawdown, etc. - assumed from "BearMetrics" parent)
**Innovation Rating:** 1/5 (minor visual modification of existing script - black text version)
**Notes:** Explicitly credited as a text-color modification of the original BearMetric script. Not a standalone strategy.

---

## [16] gGHRwDOJ - Ford Swing Line

**URL:** https://www.tradingview.com/script/gGHRwDOJ-Ford-Swing-Line
**Category:** Price Structure / Swing Tracking
**Indicators Used:** Raw price highs/lows
**Entry/Exit Conditions:** Tracks most recent high/low, signals HH (Higher High) and LL (Lower Low) formation
**A-Share Daily Suitability:** Yes - pure price structure
**Mathematical Foundation:** Basic swing high/low tracking with trend structure identification
**Innovation Rating:** 1/5 (basic swing high/low tracking)
**Notes:** Simple price structure utility.

---

## [17] gKs2ojOP - Advanced Dual Hull Cross Suite V9

**URL:** https://www.tradingview.com/script/gKs2ojOP-Advanced-Dual-Hull-Cross-Suite-V9
**Category:** Moving Average Crossover (Advanced)
**Indicators Used:** THMA(16), HMA(14) - Triple Hull MA and standard Hull MA
**Entry/Exit Conditions:**
- Fast: THMA(16) cross Slow: HMA(14)
- Selectable HMA/EHMA/THMA variants
- Slope-based color changes as early warning
- Cross signals with slope confirmation
**A-Share Daily Suitability:** Yes - standard OHLCV, no market-specific logic
**Mathematical Foundation:**
- HMA = WMA(2*WMA(close, n/2) - WMA(close, n), sqrt(n))
- EHMA = EMA variant of Hull construction
- THMA = Triple WMA construction (WMA of WMA of WMA) for extreme responsiveness
- Slope calculation for early-direction detection
**Innovation Rating:** 3/5 (dual-variation Hull MA with selectable types)
**Key Insight:** Hull MA's sqrt(n) final smoothing reduces lag while maintaining smoothness - a mathematical tradeoff between responsiveness and noise filtering. The THMA variant takes this further with triple WMA nesting, creating maximum responsiveness at the cost of more noise. The slope-based color change acts as an early-warning system before the actual crossover occurs.

---

## [18] gLqfgM60 - Strong Support/Resistance Only (Flow >= 5)

**URL:** https://www.tradingview.com/script/gLqfgM60
**Category:** Support/Resistance with Volume-Flow Strength Filter
**Indicators Used:** Pivots, ATR, Volume * Body Ratio * Direction (Flow Proxy)
**Entry/Exit Conditions:**
- Detect pivot highs/lows with lookback period
- Filter: only show S/R zones where Flow Strength >= 5x average
- Flow = volume * bodyRatio * direction (signed directional volume weighted by candle quality)
- Draw ATR-scaled boxes around qualifying pivots
**A-Share Daily Suitability:** Yes - pure OHLCV with volume, directly applicable
**Mathematical Foundation:**
- bodyRatio = |close - open| / (high - low) - measures how "decisive" the candle is
- flowProxy = volume * bodyRatio * direction (+1/-1)
- flowStrength = |flowProxy| / SMA(|flowProxy|, 20) - ratio of current flow to average
- Zone width = ATR(200) * multiplier
- Only zones with flowStrength >= threshold (default 5.0) are drawn
**Innovation Rating:** 3/5 (volume-weighted body ratio as "flow" strength for S/R qualification)
**Key Insight:** The flow proxy formula (volume * body_ratio * direction) is a clever way to measure conviction: a candle with a large body relative to its range AND high volume AND directional close indicates strong institutional participation. The 5x threshold means only pivots formed during exceptional conviction are marked as S/R, filtering out noise zones created by indecisive candles.

---

## [19] gT6UWKv7 - EMA Trend Vol Desviacion TDC

**URL:** https://www.tradingview.com/script/gT6UWKv7
**Category:** EMA + Volume Confirmation + Volatility Bands
**Indicators Used:** EMA(50), StdDev bands, Volume SMA(20), net volume pressure
**Entry/Exit Conditions:**
- EMA changes color (green/red) based on price position
- Signal: candle body fully crosses EMA (open on one side, close on the other) AND volume > 1.1x average
- Volume labels on confirmed crosses
- Net volume pressure panel (cumulative bullish - bearish volume over N days)
- Signal repetition filter: no consecutive same-direction signals
**A-Share Daily Suitability:** Yes - works on any OHLCV data
**Mathematical Foundation:**
- EMA(50) with dynamic coloring
- StdDev bands: EMA +/- multiplier * stdev(close, period) - Bollinger-style envelope
- Volume filter: current_volume > sensitivity * SMA(volume, 20)
- Full body cross: (open < EMA and close > EMA) or (open > EMA and close < EMA)
- Net pressure: sum(volume on bullish crosses) - sum(volume on bearish crosses) over N days
**Innovation Rating:** 3/5 (triple-layer filter: full-body EMA cross + volume confirmation + net pressure context)
**Key Insight:** The requirement that the entire candle body must cross the EMA (not just a wick) combined with volume confirmation creates a high-quality signal filter. The net volume pressure panel provides context: if you're about to enter long but net pressure is strongly negative, the trade has a headwind. The repetition filter prevents signal clustering.

---

## [20] gfZEmKUh - Shaven Identifier

**URL:** https://www.tradingview.com/script/gfZEmKUh-Shaven-Identifier
**Category:** Candlestick Pattern Recognition
**Indicators Used:** Raw OHLC pattern matching, horizontal S/R extension
**Entry/Exit Conditions:**
- Detects bullish candles with no bottom wick (shaven bottom)
- Detects bearish candles with no top wick (shaven top)
- Extends S/R lines from the open price (the "flat" side of the candle)
- Multi-timeframe detection capability
**A-Share Daily Suitability:** Yes - pure price action
**Mathematical Foundation:** Pattern matching: low == open (bullish shaven) or high == open (bearish shaven)
**Innovation Rating:** 2/5 (candlestick pattern + S/R extension)
**Notes:** Similar concept to Marubozu but focuses on the "shaven" side specifically and extends S/R from the flat side.

---

## [21] gg86FQWy - CTZ CVD Divergence

**URL:** https://www.tradingview.com/script/gg86FQWy-CTZ-CVD-Divergence
**Category:** Volume Divergence
**Indicators Used:** CVD (Cumulative Volume Delta), divergence detection
**Entry/Exit Conditions:** CVD divergence signals - price makes new high/low but CVD does not confirm
**A-Share Daily Suitability:** Partially - CVD requires volume data; A-share daily volume works but true delta requires tick data
**Mathematical Foundation:** Cumulative Volume Delta divergence: price HH/LL without corresponding CVD HH/LL
**Innovation Rating:** 2/5 (standard divergence application to volume delta)
**Notes:** CVD approximation may be limited on daily data without actual bid/ask information.

---

## [22] gidoT7f9 - Trend Momentum Algionics Ribbon Pressure Field

**URL:** https://www.tradingview.com/script/gidoT7f9-Trend-Momentum-Algionics-Ribbon-Pressure-Field
**Category:** Multi-Layer Trend / Momentum Ribbon
**Indicators Used:** Algionics Ribbon (multiple moving average ribbon), pressure field visualization
**Entry/Exit Conditions:** Ribbon expansion/contraction for trend strength; pressure field for momentum direction
**A-Share Daily Suitability:** Yes - standard OHLCV
**Mathematical Foundation:** Multi-period MA ribbon with momentum-weighted pressure visualization
**Innovation Rating:** 3/5 (ribbon + pressure field combination)
**Notes:** This strategy was previously analyzed and backtested in earlier batches (referenced in memory as AlgionicsRibbon +21.2% optimized).

---

## [23] gloOuWwW - HS Capital EMAs

**URL:** https://www.tradingview.com/script/gloOuWwW-HS-Capital-EMA-s
**Category:** Multi-EMA System
**Indicators Used:** Multiple EMAs (specific periods not documented in visible content)
**Entry/Exit Conditions:** EMA ribbon/crossover system by HS Capital
**A-Share Daily Suitability:** Yes - standard EMA system
**Mathematical Foundation:** Multiple EMA crossover/ribbon analysis
**Innovation Rating:** 2/5 (standard multi-EMA system)
**Notes:** Likely a trend-following EMA ribbon with custom periods.

---

## [24] guscJmRn - US10Y DXY Structure Dashboard

**URL:** https://www.tradingview.com/script/guscJmRn-US10Y-DXY-Structure-Dashboard
**Category:** Macro Dashboard
**Indicators Used:** US 10-Year Treasury Yield, DXY (Dollar Index), structure analysis
**Entry/Exit Conditions:** Dashboard showing US10Y and DXY market structure for macro context
**A-Share Daily Suitability:** No - forex/bond specific, designed for US macro context
**Mathematical Foundation:** Cross-asset structure analysis
**Innovation Rating:** 1/5 (macro dashboard, not a tradeable strategy)
**Notes:** Useful for macro context but not a direct trading strategy for A-shares.

---

## [25] gwA0e7EY - Zuri FVG Imbalance Reaction Zones 2.0

**URL:** https://www.tradingview.com/script/gwA0e7EY-Zuri-FVG-Imbalance-Reaction-Zones-2-0
**Category:** Smart Money Concepts / Fair Value Gap
**Indicators Used:** FVG (Fair Value Gap) detection, imbalance zones, reaction zone mapping
**Entry/Exit Conditions:** Identifies FVG/imbalance zones and maps them as reaction zones where price is likely to return
**A-Share Daily Suitability:** Yes - pure price-action based, works on OHLCV
**Mathematical Foundation:** FVG = gap between candle[1].low and candle[+1].high (or vice versa) where candle[0] doesn't fill the gap
**Innovation Rating:** 2/5 (FVG implementation with zone mapping)
**Notes:** V2.0 suggests improvements over original. Part of the broader SMC framework.

---

## [26] gyq3Jq14 - Marco Top Detector

**URL:** https://www.tradingview.com/script/gyq3Jq14-Marco-Top-Detector
**Category:** Top/Bottom Detection
**Indicators Used:** Pattern-based top detection
**Entry/Exit Conditions:** Detects potential market tops based on price patterns
**A-Share Daily Suitability:** Yes - price-pattern based
**Mathematical Foundation:** Pattern recognition for swing top formation
**Innovation Rating:** 2/5 (top detection tool)
**Notes:** Contextual tool for identifying potential reversal zones.

---

## [27] h4qlxSL7 - EMA 4 EMA 9 Cross

**URL:** https://www.tradingview.com/script/h4qlxSL7-EMA-4-EMA-9-Cross
**Category:** Moving Average Crossover (Fast)
**Indicators Used:** EMA(4), EMA(9)
**Entry/Exit Conditions:** EMA(4) crosses EMA(9) for entry/exit signals
**A-Share Daily Suitability:** Yes - universal, works on any OHLCV data
**Mathematical Foundation:** Standard EMA crossover with very short periods
**Innovation Rating:** 1/5 (textbook fast EMA crossover)
**Notes:** Very short-period EMAs (4/9) generate frequent signals, suitable for scalping or as momentum filters.

---

## [28] h6pDtjUc - Daily Open 5 Minute Range Box Any Timeframe

**URL:** https://www.tradingview.com/script/h6pDtjUc-Daily-Open-5-Minute-Range-Box-Any-Timeframe
**Category:** Opening Range / Daily Reference
**Indicators Used:** Daily open price, 5-minute opening range
**Entry/Exit Conditions:** Draws daily open level and 5-minute opening range box, usable on any timeframe
**A-Share Daily Suitability:** Yes - daily open is a universal reference
**Mathematical Foundation:** Daily open tracking with initial range measurement
**Innovation Rating:** 2/5 (practical opening range reference tool)
**Notes:** Utility for visualizing the daily open and initial range as reference levels.

---

## [29] h8hFCBxv - Aura Trend Cloud Navigator [Pineify]

**URL:** https://www.tradingview.com/script/h8hFCBxv-Aura-Trend-Cloud-Navigator-Pineify
**Category:** Adaptive Trend + Volatility Cloud
**Indicators Used:** TRAMA (Trend Regularity Adaptive Moving Average), ATR cloud
**Entry/Exit Conditions:**
- TRAMA as adaptive trend line
- ATR envelope scaled by multiplier forms volatility cloud
- Trend direction from TRAMA slope
- Cloud boundaries as dynamic S/R
**A-Share Daily Suitability:** Yes - pure OHLCV, regime-adaptive
**Mathematical Foundation:**
- Binary signal = 1 if (new HH or new LL in lookback period), else 0
- Coefficient = SMA(binary_signal, lookback) -- measures frequency of new extremes
- SQUARED coefficient: baseline = baseline + coefficient^2 * (close - baseline)
- Squaring creates nonlinear regime switching (coefficient drops to near-zero in ranges)
- ATR envelope: baseline +/- multiplier * ATR(period)
**Innovation Rating:** 5/5 (novel trend regularity detection via extreme-frequency counting + nonlinear squaring)
**Key Insight:** The key philosophical insight is measuring "how often" price makes new extremes rather than "how much" it moves. The squaring operation creates a sharp regime transition: in a strong trend, the coefficient is high and squared coefficient is very high (fast tracking); in a range, the coefficient drops to near-zero and squared coefficient approaches zero even faster (frozen baseline). This is mathematically elegant: it treats market regime as a nonlinear function of structural progress frequency, creating a built-in ranging vs trending detector within the MA formula itself.

---

## Summary

### Total Processed: 30 scripts (index 0-29)

### High-Innovation Strategies (>= 4):

| # | Script ID | Name | Rating | Key Innovation |
|---|-----------|------|--------|----------------|
| 4 | fHvBm6UW | Mapa de Liquidaciones | 4 | Leveraged liquidation zone estimation via inverse-leverage math |
| 5 | fRXnVB3Q | Multi-Indicator Screener 30 Assets | 4 | 10-indicator breadth system with Vol Delta approximation |
| 6 | ff7qSzca | SMA8 Reversion Simple | 4 | Self-calibrating 4x3 conditional probability matrix for mean reversion |
| 11 | g4zjCqpe | Session Levels IQ | 4 | Session expansion probability framework with move-after-hit tracking |
| 29 | h8hFCBxv | Aura Trend Cloud Navigator | 5 | TRAMA with nonlinear frequency-squared regime detection |

### Cross-Cutting Mathematical Patterns:

1. **Adaptive Speed via Market Regime:** TRAMA (script 29) and the SMA8 reversion (script 6) both adapt their behavior based on market conditions, but via entirely different mechanisms - frequency counting vs conditional probability.

2. **Volume-Weighted Conviction:** Scripts 4 (liquidation flow), 18 (flow-strength S/R), and 19 (volume-confirmed EMA cross) all use volume as a conviction filter, but each applies it differently: leverage estimation, body-ratio weighting, and threshold confirmation.

3. **Directional Gates / Multi-Condition Filters:** Scripts 5 (dual-condition RSI), 14 (trend-gated momentum), and 19 (full-body + volume + net pressure) all employ multi-condition entry filters to reduce false signals.

4. **Statistical Self-Calibration:** Scripts 6 (SMA8 matrix) and 11 (Session Levels IQ) build per-asset statistical databases rather than using fixed parameters, making them inherently adaptive.

5. **Nonlinear Transformations for Regime Detection:** TRAMA's squaring operation (script 29) is the most mathematically novel approach in this batch, creating an implicit regime switcher from a continuous formula.

### Key Philosophical Insights:

1. **Frequency over Magnitude (TRAMA):** Measuring how often price reaches new extremes (frequency) is more informative for regime detection than measuring how far it moves (magnitude). Squaring the frequency creates sharp regime boundaries.

2. **Conditional Probability Surfaces (SMA8, Session Levels):** Building historical probability matrices conditioned on both distance and time dimensions provides vastly more information than simple threshold-based signals.

3. **Volume as Conviction (Flow Proxy):** Volume * body_ratio * direction is a simple but powerful formula that measures not just "how much" participation there was, but "how decisive" the participation was - a proxy for institutional conviction.

4. **Liquidation Gravity Maps:** Estimating where forced selling/buying would occur creates a self-fulfilling framework - these are levels where cascading liquidations create non-linear price impact.

5. **Displacement as Noise Filter:** Shifting moving averages forward in time creates a "sustainability buffer" - a price move must persist beyond the displaced MA to generate a signal, filtering ephemeral spikes.
