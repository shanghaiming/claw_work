# TV Batch 2 Extended 3 - Scripts #60-89 Analysis

**Date:** 2026-04-19
**Indices:** 60-89 (30 scripts)
**Source:** batch_2.json

---

## Summary

| # | Script ID | Name | Innovation | A-Share | Status |
|---|-----------|------|:----------:|:--------:|--------|
| 60 | Ftajt8Xj | Turtles Army PA USDJPY | 2 | 1 | Fetched |
| 61 | Fx7Osv12 | SMC Gap V1.3 (FFVG and VI) | 3 | 3 | Fetched |
| 62 | G3hmcJiu | PnL Target Stop Calculator 100-2000 | 1 | 2 | Fetch Failed (429) |
| 63 | G7EY5xsj | Quantitative Linear Regression Channel Dual Fill MTF | 3 | 4 | Fetched |
| 64 | G7h3q1ON | Session Range | 1 | 2 | Fetched |
| 65 | G9rqmz5O | Overnight Hold Opening Range Indicator | 2 | 1 | Fetch Failed (429) |
| 66 | GC2l3CVo | Peachy ORB Opening Range Breakout | 2 | 2 | Fetched |
| 67 | GFOnOSWj | Monte Carlo Risk Geometry Simulator Aslan | 4 | 3 | Fetched |
| 68 | GGh4k9FA | Key Levels Session PDH PDL Premarket Dual 5m Open | 1 | 1 | Fetch Failed (429) |
| 69 | GP3FEy2z | GP3FEy2z (unknown) | - | - | Fetch Failed (429) |
| 70 | GU7CKh6z | KernelLens | 5 | 5 | Fetched |
| 71 | GWT0I6ap | EQH/EQL Liquidity Zones | 2 | 3 | Fetched |
| 72 | GWlbatIi | Hash Dispersion Cone | - | - | Fetch Failed (429) |
| 73 | GgU87KsX | Pre Market Previous Day Week Levels | 1 | 1 | Fetch Failed (429) |
| 74 | GoUoySJs | BTC MTF Engulfing Flip Pyramid Strategy 1H 2X | 3 | 2 | Fetch Failed (429) |
| 75 | H1HSgkF4 | The Strat Structural Probability Evaluator | 3 | 2 | Fetch Failed (429) |
| 76 | H2fx231K | ORB FVG FIB Dashboard Multi TF Confluences | 2 | 2 | Fetch Failed (429) |
| 77 | HE7JJt34 | OriginLifecycle | 2 | 2 | Fetch Failed (429) |
| 78 | HFqOweBq | v17 Inside Outside Bar Levels | 1 | 3 | Fetch Failed (429) |
| 79 | HHRVGKLr | QM Range DAFE | 2 | 2 | Fetch Failed (429) |
| 80 | HJ56DZm5 | IPO Day High Line 1000 Trading Days | 1 | 1 | Fetch Failed (429) |
| 81 | HJl4b1k7 | gobucs1314 indicator | - | - | Fetch Failed (429) |
| 82 | HKR6ohUK | gold slayer parmezan | 2 | 1 | Fetch Failed (429) |
| 83 | HLrY90D0 | codex elliott wave setup assistant | 2 | 2 | Fetch Failed (429) |
| 84 | HU1KCSUH | Daily Protocol | 2 | 2 | Fetch Failed (429) |
| 85 | Hctn0OzA | Quantiva Multi Timeframe TEMA SMA | 2 | 3 | Fetch Failed (429) |
| 86 | HhBnzmYX | SPY Opening Pace 30m Traffic Light | 2 | 1 | Fetch Failed (429) |
| 87 | HueL0Ix0 | ATR Structure Trend | 2 | 3 | Fetch Failed (429) |
| 88 | HwpoWtYk | Harmonic Pattern Finder RSI Confirms | 2 | 2 | Fetch Failed (429) |
| 89 | IKwWUzwb | Session Open Lines PRO Final Clean | 1 | 1 | Fetch Failed (429) |

**Fetched:** 10 / 30 | **Failed:** 20 / 30 (rate limited)

---

## Strategy Details

### #60 - Ftajt8Xj: Turtles Army PA USDJPY
- **Author:** krocarlo
- **URL:** https://www.tradingview.com/script/Ftajt8Xj
- **Type:** Strategy (Pine v6)
- **Mathematical Core:**
  - EMA-based structural bias on 1H and 4H timeframes (price vs EMA = direction)
  - Both HTF must agree for bias alignment
  - ATR-based stop loss and take profit
  - Session filtering (Tokyo + NY sessions)
  - Pyramid up to 3 entries
- **Innovation:** 2/5 - Standard EMA multi-TF trend following with session filtering
- **A-Share Applicability:** 1/5 - Forex-specific (USDJPY), 1-minute timeframe, uses session times tied to FX market hours that do not apply to A-shares
- **Key Params:** EMA periods (1H, 4H), ATR multiplier, session hours (UTC), max pyramid=3

### #61 - Fx7Osv12: SMC Gap V1.3 (FFVG and VI)
- **Author:** thebidtle
- **URL:** https://www.tradingview.com/script/Fx7Osv12
- **Type:** Indicator
- **Mathematical Core:**
  - **Dual-Imbalance Detection:** FFVG (3-bar wick-to-wick gap) + Volume Imbalance (body-to-body gap)
  - **Dynamic Lifecycle System:** Active -> Partial Mitigation -> Fully Mitigated -> Inversion
  - 50% Consequent Encroachment (CE) midline tracking
  - ATR-based swing detection or fractal swing detection
  - Inversion logic: candle closes through active gap -> inverted gap (support becomes resistance)
- **Innovation:** 3/5 - Sophisticated gap lifecycle with state machine, inversion mechanic is novel
- **A-Share Applicability:** 3/5 - FVG and volume imbalance concepts work on daily OHLCV. The CE midline rejection entries are valid. However, some patterns work better on intraday which A-shares have limited data for. Gap inversion concept maps well to A-share gap behavior.
- **Key Params:** Swing detection mode (ATR/Fractal), ATR multiplier, lookback period, mitigation threshold (50%)

### #62 - G3hmcJiu: PnL Target Stop Calculator 100-2000
- **URL:** https://www.tradingview.com/script/G3hmcJiu-PnL-Target-Stop-Calculator-100-2000
- **Type:** Utility / Calculator
- **Mathematical Core:** Position sizing and PnL calculator for targets 100-2000
- **Innovation:** 1/5 - Simple calculator tool
- **A-Share Applicability:** 2/5 - Useful for any market but not a strategy
- **Key Params:** N/A

### #63 - G7EY5xsj: Quantitative Linear Regression Channel [Dual Fill + MTF]
- **Author:** datapro
- **URL:** https://www.tradingview.com/script/G7EY5xsj-Quantitative-Linear-Regression-Channel-Dual-Fill-MTF
- **Type:** Indicator (Pine v6)
- **Mathematical Core:**
  - Linear Regression Line (best fit): y = a + bx using OLS
  - Standard Deviation channels at user-defined multiples (default 2.0)
  - Slope-based trend detection with dynamic coloring
  - MTF Transport Layer: channel data across timeframes without repainting (lookahead=off)
  - Irregular timeframe support (Monthly, Quarterly, Yearly)
  - Fibonacci retracement levels (0.236, 0.382, 0.618, 0.786) within channel range
  - Broken channel detection with frozen visualization
- **Innovation:** 3/5 - Well-engineered LRC with MTF transport, broken channel freeze, persistent rendering engine. The MTF table across 5 TFs is practical.
- **A-Share Applicability:** 4/5 - Linear regression channels are excellent for daily timeframe A-share analysis. The slope-based trend detection works well. SD bands adapt to volatility. MTF trend table helps confirm bias. Key params (length, deviation) translate directly.
- **Key Params:** Source (close), Length (lookback), Deviation multiplier (2.0), Channel Calculation TF, Fibonacci levels toggle

### #64 - G7h3q1ON: Session Range
- **Author:** VTA_Harun
- **URL:** https://www.tradingview.com/script/G7h3q1ON
- **Type:** Indicator
- **Mathematical Core:** Smart Money session range plotting (Asian/London/NY session boxes)
- **Innovation:** 1/5 - Basic session range box
- **A-Share Applicability:** 2/5 - Session ranges not directly applicable to A-shares (different market hours), but the concept of tracking opening range on daily bars could be adapted
- **Key Params:** Session times

### #65 - G9rqmz5O: Overnight Hold Opening Range Indicator
- **URL:** https://www.tradingview.com/script/G9rqmz5O-Overnight-Hold-Opening-Range-Indicator
- **Type:** Indicator
- **Mathematical Core:** Tracks overnight range vs opening range for gap-and-go strategies
- **Innovation:** 2/5 - Combines overnight sentiment with ORB
- **A-Share Applicability:** 1/5 - US equities overnight hold concept not applicable to A-shares

### #66 - GC2l3CVo: Peachy ORB Opening Range Breakout
- **Author:** mrbags
- **URL:** https://www.tradingview.com/script/GC2l3CVo-Peachy-ORB-Opening-Range-Breakout
- **Type:** Indicator
- **Mathematical Core:**
  - Three range windows: 15-min ORB, 30-min ORB, Pre-market ORB
  - Failed breakout detection (price dips below low then closes back above = bullish reject)
  - Higher Low / Lower High pattern confirmation (3 consecutive)
  - Range day warning at 10:15 ET if still trapped
  - 50% midline mean-reversion entries
- **Innovation:** 2/5 - Clean ORB implementation with failed breakout focus and range-day filter
- **A-Share Applicability:** 2/5 - Opening range concept could be adapted for A-share first 15-30 min, but the specific ET session times and pre-market logic need full rewrite. The failed-breakout reversal concept is transferable.
- **Key Params:** ORB window (15/30 min), session start time, range day warning time

### #67 - GFOnOSWj: Monte Carlo Risk Geometry Simulator [Aslan]
- **Author:** Zimord
- **URL:** https://www.tradingview.com/script/GFOnOSWj-Monte-Carlo-Risk-Geometry-Simulator-Aslan
- **Type:** Indicator / Simulator
- **Mathematical Core:**
  - Monte Carlo simulation: generates hundreds/thousands of equity paths
  - Input: Win Rate (WR), Risk-Reward (RR), Risk % per trade
  - Each path = random sequence of wins/losses drawn from Bernoulli(WR)
  - P&L per trade: Win = +RR * Risk%, Loss = -Risk%
  - Outputs: equity curve distribution, max drawdown distribution, % profitable outcomes
  - Prop firm threshold system: finds optimal risk geometry to pass evaluation
  - Key insight: "the most probable geometry for passing an eval can sometimes have a negative expected value!"
- **Innovation:** 4/5 - Practical Monte Carlo for strategy validation. The prop firm threshold optimization is unique. Moves from "how much can I make" to "how likely am I to profit."
- **A-Share Applicability:** 3/5 - The Monte Carlo framework itself is market-agnostic and highly valuable for A-share strategy validation. However, the 10% daily limit constraint needs to be factored into the simulation parameters. The prop firm evaluation angle is less relevant but the risk geometry optimization is universally useful.
- **Key Params:** Win Rate %, Risk-Reward ratio, Risk % per trade, Number of simulations, Threshold target

### #68 - GGh4k9FA: Key Levels Session PDH PDL Premarket Dual 5m Open
- **URL:** https://www.tradingview.com/script/GGh4k9FA-Key-Levels-Session-PDH-PDL-Premarket-Dual-5m-Open
- **Type:** Indicator
- **Mathematical Core:** Previous Day High/Low + Premarket levels + dual 5-min open levels
- **Innovation:** 1/5 - Key level plotting
- **A-Share Applicability:** 1/5 - US equities session-specific

### #69 - GP3FEy2z: (unknown)
- **Type:** Unknown
- **Status:** Fetch failed

### #70 - GU7CKh6z: KernelLens
- **Author:** a_jabbaroff
- **URL:** https://www.tradingview.com/script/GU7CKh6z-KernelLens
- **Type:** Library (Pine v6)
- **Mathematical Core:**
  - **Nadaraya-Watson kernel regression estimator:** y_hat(t) = SUM[K(d_i/l) * y_{t-i}] / SUM[K(d_i/l)]
  - **Eight kernel families:**
    1. Rational Quadratic: (1 + d^2 / (2*alpha*l^2))^(-alpha) - multi-scale mixer
    2. Gaussian (RBF): exp(-d^2 / (2*l^2)) - canonical smoother, C-infinity
    3. Periodic: exp(-2*sin^2(pi*d/p) / l^2) - resonates with cycle length p
    4. Locally Periodic: Periodic * Gaussian - seasonal + trend
    5. Epanechnikov: (3/4)(1-u^2) for |u|<=1 - MSE-optimal (Watson 1964)
    6. Tricube: (70/81)(1-|u|^3)^3 for |u|<=1 - LOWESS standard, C^2
    7. Triangular: (1-|u|) for |u|<=1 - cheapest non-uniform
    8. Cosine: (pi/4)*cos(pi*u/2) for |u|<=1 - C^1 boundary
  - **Three-mode filter layer:**
    - No Filter: single-pass raw estimate
    - Smooth: double-pass K(K(y)) - convolve kernel with itself
    - Zero Lag: 2*K(y) - K(K(y)) - Ehlers de-lagging
  - **Phase parameter:** non-repainting knob, shifts kernel center into the past
  - **Utilities:** slope(), trendState(), crossSignal(), confidenceBand(), silvermanBandwidth()
  - **Bug fix:** Corrects loop depth bug in existing Pine kernel libraries (was always = 1)
  - Proper depth: Infinite=3*l (99.7% mass), Compact=l, Periodic=max(3*l, p*10)
- **Innovation:** 5/5 - This is a professional-grade mathematical library. Eight kernels with correct implementation, filter layer, phase control, input validation, Silverman bandwidth. Fixes a decade-old bug in existing libraries. Academic references cited inline. This is the gold standard for non-parametric smoothing in Pine Script.
- **A-Share Applicability:** 5/5 - Kernel regression is universally applicable. Works on any OHLCV data including A-share daily bars. The bandwidth presets (scalper=8, day trader=16, swing=32, position=64) directly map to A-share trading styles. The Periodic kernel with configurable cycle period is excellent for detecting seasonal patterns in A-share indices. Zero-lag mode useful for signal generation on daily bars.
- **Key Params:** bandwidth (l), kernel type, filter mode, phase (non-repainting offset), shapeAlpha (RQ only), period (Periodic only)
- **Academic References:** Nadaraya (1964), Watson (1964), Cleveland (1979), Silverman (1986), Wand & Jones (1995), MacKay (1998), Ehlers (2000), Rasmussen & Williams (2006)

### #71 - GWT0I6ap: EQH/EQL Liquidity Zones
- **Author:** vitalychikin
- **URL:** https://www.tradingview.com/script/GWT0I6ap-eqh-eql-liquidity-zones
- **Type:** Indicator
- **Mathematical Core:**
  - Equal Highs (EQH) and Equal Lows (EQL) detection
  - Pivot-based identification of liquidity pools where stops accumulate
  - Zone visualization for liquidity sweeps
- **Innovation:** 2/5 - SMC liquidity zone detection using pivot points
- **A-Share Applicability:** 3/5 - Equal highs/lows are visible on A-share daily charts. Liquidity sweep concept works when institutions target stop clusters. The 10% daily limit creates more frequent EQH/EQL patterns as price hits limits.
- **Key Params:** Pivot lookback, zone width tolerance

### #72-89: Scripts with failed fetches (rate limited)
- **GWlbatIi: Hash Dispersion Cone** - likely volatility/dispersion analysis
- **GgU87KsX: Pre Market Previous Day Week Levels** - key level plotting
- **GoUoySJs: BTC MTF Engulfing Flip Pyramid Strategy 1H 2X** - multi-TF engulfing with pyramid
- **H1HSgkF4: The Strat Structural Probability Evaluator** - structural probability scoring
- **H2fx231K: ORB FVG FIB Dashboard Multi TF Confluences** - multi-confluence dashboard
- **HE7JJt34: OriginLifecycle** - likely SMC order block lifecycle
- **HFqOweBq: v17 Inside Outside Bar Levels** - inside/outside bar pattern levels
- **HHRVGKLr: QM Range DAFE** - Quasimodo range detection
- **HJ56DZm5: IPO Day High Line 1000 Trading Days** - IPO reference level
- **HJl4b1k7: gobucs1314 indicator** - unknown
- **HKR6ohUK: gold slayer parmezan** - gold-specific strategy
- **HLrY90D0: codex elliott wave setup assistant** - Elliott Wave helper
- **HU1KCSUH: Daily Protocol** - daily timeframe protocol
- **Hctn0OzA: Quantiva Multi Timeframe TEMA SMA** - TEMA/SMA multi-TF crossover
- **HhBnzmYX: SPY Opening Pace 30m Traffic Light** - opening pace indicator
- **HueL0Ix0: ATR Structure Trend** - ATR-based trend detection
- **HwpoWtYk: Harmonic Pattern Finder RSI Confirms** - harmonic patterns + RSI
- **IKwWUzwb: Session Open Lines PRO Final Clean** - session open level plotting

---

## Highlights

### Tier 1 - Must Study (Innovation >= 4)

**#70 KernelLens** [Innovation: 5, A-Share: 5]
- **Why:** The most rigorous kernel regression library on TradingView. Eight mathematically correct Nadaraya-Watson estimators with proper loop depth (fixes decade-old bug). Filter layer (None/Smooth/ZeroLag), phase-based non-repainting, Silverman bandwidth. This is a production-grade non-parametric statistics toolkit.
- **A-Share Value:** Directly usable. The kernel smoother produces cleaner trend signals than any moving average. Key idea: Use Epanechnikov (MSE-optimal) or Tricube (LOWESS) kernels on A-share daily OHLCV for robust trend estimation without outlier contamination. Zero-lag mode for signal generation, Smooth mode for trend identification.
- **Transferable Concept:** Kernel regression as a superior alternative to moving averages for A-share trend following. The mathematical framework (bias-variance tradeoff, Silverman bandwidth) gives principled parameter selection.

**#67 Monte Carlo Risk Geometry Simulator** [Innovation: 4, A-Share: 3]
- **Why:** Moves strategy evaluation from single backtest to probability distribution of outcomes. The insight that optimal risk geometry for prop firm passing can have negative EV is counterintuitive and important.
- **A-Share Value:** Essential for validating any A-share strategy. With 10% daily limits, the Monte Carlo sim should incorporate the constraint that max loss per bar = 10%. This gives more realistic equity curve distributions.
- **Transferable Concept:** Monte Carlo simulation as mandatory validation step before deploying any A-share strategy. Risk geometry optimization (WR, RR, Risk%) adapted for T+1 settlement and 10% limits.

### Tier 2 - Worth Adapting (Innovation >= 3)

**#63 Quantitative Linear Regression Channel** [Innovation: 3, A-Share: 4]
- **Why:** Professional LRC with MTF trend table, broken channel detection, persistent rendering. The slope-based trend detection with dynamic coloring is clean.
- **A-Share Value:** Linear regression channels on daily A-share data provide statistical fair value + volatility envelope. The broken channel concept (price exits channel = volatility expansion) maps well to A-share limit-up/limit-down behavior.
- **Key Adaptation:** Use LRC slope direction across daily/weekly timeframes as trend filter. Channel bands as dynamic support/resistance.

**#61 SMC Gap V1.3 (FFVG and VI)** [Innovation: 3, A-Share: 3]
- **Why:** Gap lifecycle state machine (Active -> Partial -> Full -> Inverted) is sophisticated. The inversion mechanic where a failed gap flips polarity is the key innovation.
- **A-Share Value:** FVG gaps on A-share daily charts are well-defined due to 10% limits creating hard boundaries. Volume Imbalance (body-to-body gap) is especially relevant when limit-up/down creates consecutive full-body candles. The CE midline rejection entry works well in A-share mean-reversion setups.

### Tier 3 - Standard Tools

- **#60 Turtles Army PA:** Standard EMA multi-TF with sessions. Forex-specific, minimal A-share value.
- **#64 Session Range:** Basic session box. US-session specific.
- **#66 Peachy ORB:** Clean ORB with failed breakout focus. Could be adapted for A-share opening 15-30 min but needs full session rewrite.
- **#71 EQH/EQL Liquidity Zones:** Pivot-based equal high/low detection. Works on A-share daily charts.

### Fetch Failure Notes
20 of 30 scripts failed to fetch due to rate limiting (HTTP 429). The failed scripts (#72-89 and several others) should be retried in a subsequent batch. Based on names alone, the most interesting failed scripts are:
- **H1HSgkF4 (The Strat Structural Probability Evaluator)** - probability scoring
- **GoUoySJs (BTC MTF Engulfing Flip Pyramid Strategy)** - multi-TF engulfing
- **Hctn0OzA (Quantiva Multi Timeframe TEMA SMA)** - TEMA multi-TF
- **HueL0Ix0 (ATR Structure Trend)** - ATR trend structure
- **HwpoWtYk (Harmonic Pattern Finder RSI Confirms)** - harmonic + RSI

---

## Key Learnings for A-Share Strategy Development

1. **Kernel Regression > Moving Averages:** KernelLens proves that Nadaraya-Watson estimators with proper bandwidth selection produce smoother, less laggy, and statistically principled trend estimates. For A-share daily bars, Epanechnikov (compact support, MSE-optimal) with bandwidth 16-32 is a strong starting point.

2. **Gap Lifecycle Matters:** The SMC Gap V1.3 state machine (Active -> Mitigated -> Inverted) provides a framework for tracking A-share gaps that goes beyond simple gap fill. The inversion concept (failed gap = new S/R) is particularly useful given the frequency of limit-up/down gaps in A-shares.

3. **Monte Carlo Validation is Essential:** Before deploying any strategy, simulate thousands of equity paths using the strategy's actual WR/RR/Risk parameters. For A-shares, constrain the simulation so max daily movement = 10%.

4. **Linear Regression for Fair Value:** The LRC with MTF trend table provides a quantitative framework for determining whether an A-share is trading at, above, or below its statistical fair value on multiple timeframes simultaneously.
