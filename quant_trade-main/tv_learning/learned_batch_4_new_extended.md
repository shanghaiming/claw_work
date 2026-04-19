# Batch 4 New Extended -- TV Strategy Analysis (Indices 30-59)

> Processed: 2026-04-19 | 30 scripts | Source: batch_4_new.json

---

## Summary

| # | Name | Math Core | Innovation | A-Share |
|---|------|-----------|------------|---------|
| 30 | Liquidity Reaction Market Context | Session range analysis + SMA200 | 2 | 2 |
| 31 | CTZ BTC Cost Of Production | Power-law mining cost floor: alpha * difficulty^0.45 / issuance_daily | 5 | 1 |
| 32 | Key Levels H/L Opens | MTF OHLC level plotting (monthly/weekly/daily) | 1 | 3 |
| 33 | Daily Bias Bull/Bear/Neutral | Swing structure + MA50/200 trend filter | 2 | 4 |
| 34 | Financial Freedom | PDH/PDL + 50% midpoint levels | 1 | 3 |
| 35 | RS During Market Correction | Sector relative strength ranking via price_ratio vs index | 2 | 3 |
| 36 | Vigilant Asset Allocation VAA | 13612W momentum scoring: mom = 12*r1 + 4*r3 + 2*r6 + r12; breadth-based rotation | 4 | 4 |
| 37 | EMA 5/13 Crossover | Dual EMA cross + MTF dashboard | 1 | 3 |
| 38 | Custom Period Separator 3H-1D | Time-based adaptive vertical lines | 1 | 2 |
| 39 | GANN Wheel Square of Nine | Geometric spiral: sqrt(price), 360-degree rotation, 1deg=1day time projection | 3 | 2 |
| 40 | Vantage-X 3.0 | Multi-EMA dashboard (9/21, 20/50, 50/200) + RSI + StochRSI + order flow proxy | 2 | 3 |
| 41 | Conflux 4 | 4-filter confluence: VWMA+EMA trend, RSI momentum, Supertrend volatility, ADX strength | 3 | 4 |
| 42 | Murphy Timeframe Lens | MTF OHLC compression with progressive range tracking (no look-ahead bias) | 2 | 3 |
| 43 | Daye's True Opens (QT) | Quarterly Theory: Q2 open as pivot across 5 timeframes (session/day/week/month/year) | 3 | 2 |
| 44 | amit EMA Breakdown Pullback | EMA-based breakdown + pullback entry | 1 | 3 |
| 45 | Fed Chair Changes Daily Returns | Event study: returns across Fed chair tenures (1/3/6/12-month windows) | 2 | 1 |
| 46 | XAUUSD Auto Strategy | EMA trend + ATR SL/TP + risk% lot sizing; MT5 connector | 1 | 2 |
| 47 | Bookmap Traps | Order flow trap detection (requires Bookmap-style data) | 2 | 1 |
| 48 | MapleStax CBC | Candle-by-Candle bull/bear control: close vs prior bar's high/low; EMA9/20 cloud + VWAP | 3 | 3 |
| 49 | PRO FINAL OI OPTION S/R | Open Interest + Options-based support/resistance | 2 | 1 |
| 50 | Adv Simple Volume w/ Pocket Pivots | Pocket pivot detection: price up on volume > any down-volume in prior N days | 3 | 4 |
| 51 | AG Pro Mean Reversion Corridors | Mean reversion bands with Z-score / Bollinger-style corridors | 2 | 3 |
| 52 | News Impact Analyzer | Event-driven: price change measurement around news events | 1 | 1 |
| 53 | Key Levels ONH/ONL/PDH/PDL | Overnight High/Low + Previous Day High/Low level plotting | 1 | 3 |
| 54 | Stage2 Pro by Ketan | Minervini Stage 2: RS line + price vs MAs + volume contraction/expansion | 3 | 4 |
| 55 | Asia 786 Fib Levels | Fibonacci 0.786 retracement from Asian session range | 1 | 2 |
| 56 | BFH87fmb | Unknown (name-only, no descriptive title) | N/A | N/A |
| 57 | BHhJyAT1 | Unknown (name-only, no descriptive title) | N/A | N/A |
| 58 | BJDRgy7z | Unknown (name-only, no descriptive title) | N/A | N/A |
| 59 | Alvarium CC | Crypto correlation / cycle indicator | 2 | 1 |

**Averages (excl. N/A):** Innovation: 1.95 | A-Share: 2.5

---

## Strategy Details

### #30 -- Liquidity Reaction Market Context Framework
- **URL:** https://www.tradingview.com/script/9t1cCTAv
- **Math Core:** Session-based range analysis (Asia/London/NY ranges) + SMA200 trend filter + gap analysis
- **Category:** Market Context / Intraday Framework
- **Innovation: 2** -- Session range tracking is common; the multi-session context approach adds some value
- **A-Share: 2** -- Session times are NY-oriented (not matching A-share 9:30-15:00 CST sessions); would need re-timing
- **Key Insight:** Categorizes market context (trending/ranging/choppy) based on session range expansion vs contraction

### #31 -- CTZ BTC Cost Of Production
- **URL:** https://www.tradingview.com/script/9yE5Qgjw-CTZ-BTC-Cost-Of-Production
- **Math Core:** Power-law mining cost model: `cost_floor = alpha * difficulty^0.45 / issuance_daily`, with cycle bands
- **Category:** On-Chain / Fundamental Model
- **Innovation: 5** -- Sophisticated fundamental-to-technical bridge; power-law relationship between mining difficulty and production cost creates quantifiable floor
- **A-Share: 1** -- BTC-specific; requires on-chain data (difficulty, issuance) not available for A-share equities
- **Key Insight:** The power-law exponent 0.45 captures the sub-linear scaling of mining cost with difficulty -- a genuine structural insight into BTC valuation

### #32 -- Key Levels H/L + Opens
- **URL:** https://www.tradingview.com/script/A52MLFdv-Key-Levels-H-L-Opens
- **Math Core:** Simple OHLC level extraction from monthly/weekly/daily timeframes
- **Category:** Levels / Utility
- **Innovation: 1** -- Basic level plotting, no computation beyond reading HTF values
- **A-Share: 3** -- Clean MTF levels work universally; daily OHLC available
- **Key Insight:** None notable; purely visual utility

### #33 -- Daily Bias Bull/Bear/Neutral
- **URL:** https://www.tradingview.com/script/A8ijZZFy-Daily-Bias-Bull-Bear-Neutral-Phil-Vo
- **Math Core:** Swing high/low detection + MA50/MA200 alignment for directional bias classification
- **Category:** Trend Bias / Directional Filter
- **Innovation: 2** -- Standard swing structure + MA filter, well-executed but not novel
- **A-Share: 4** -- Works with daily OHLCV; MA crossovers and swing detection translate directly
- **Key Insight:** Clean 3-state classification (bull/bear/neutral) is a useful regime filter for systematic strategies

### #34 -- Financial Freedom
- **URL:** https://www.tradingview.com/script/A8jEErM6-Financial-Freedom
- **Math Core:** PDH/PDL + (PDH+PDL)/2 midpoint level
- **Category:** Levels / Day Trading
- **Innovation: 1** -- Trivial arithmetic: previous day high/low and 50% midpoint
- **A-Share: 3** -- Previous day levels universally available; midpoint is a classic pivot
- **Key Insight:** None notable

### #35 -- Relative Strength During Market Correction
- **URL:** https://www.tradingview.com/script/ABlI2wJW-Relative-Strength-During-Market-Correction
- **Math Core:** `RS = close / index_close`, ranked across universe during correction periods (index < MA)
- **Category:** Stock Screening / Relative Strength
- **Innovation: 2** -- Sector RS filtering during corrections is a known O'Neil/Milindri approach
- **A-Share: 3** -- Works with sector/index ratios; needs sector index data for A-share market
- **Key Insight:** Identifying stocks that hold RS during corrections is a proven stock-picking filter

### #36 -- Vigilant Asset Allocation (VAA)
- **URL:** https://www.tradingview.com/script/AGViqeuJ-Vigilant-Asset-Allocation-VAA
- **Math Core:** `13612W momentum score = 12*r(1m) + 4*r(3m) + 2*r(6m) + r(12m)`; breadth signal from % assets above SMA; offensive/defensive rotation
- **Category:** Asset Allocation / Tactical Rotation
- **Innovation: 4** -- Well-documented academic framework (Keller, 2019) with weighted momentum + breadth shield. The 13-6-12-1 weighting is empirically derived
- **A-Share: 4** -- Momentum scoring uses only price returns; breadth uses % above SMA. Both work on A-share daily data. Rotation between equity/bond is directly applicable
- **Key Insight:** The VAA-G4 variant (offensive: SPY/VEA/EEM/AGG, defensive: SHV/IEF/LQD/SHY) can be adapted to A-share: CSI300/CSI500/CSI1000 + bond ETF rotation with breadth shield

### #37 -- EMA 5/13 Crossover Indicator
- **URL:** https://www.tradingview.com/script/AJi0VNrZ-EMA-5-13-Crossover-Indicator
- **Math Core:** `signal = EMA(5) crosses EMA(13)` with MTF dashboard
- **Category:** Trend Following / Moving Average
- **Innovation: 1** -- Textbook EMA crossover, oldest signal in technical analysis
- **A-Share: 3** -- EMA crossover works on any daily OHLCV data
- **Key Insight:** The MTF dashboard showing multiple timeframe EMA states is the only added value

### #38 -- Custom Period Separator 3H-1D
- **URL:** https://www.tradingview.com/script/AMTLfoEf-Custom-Period-Separator-3H-1D
- **Math Core:** Time-based session boundary detection for vertical line placement
- **Category:** Utility / Visual
- **Innovation: 1** -- Purely visual utility, no trading signal
- **A-Share: 2** -- Would need customization for A-share session times
- **Key Insight:** None notable

### #39 -- GANN Wheel Square of Nine
- **URL:** https://www.tradingview.com/script/AQ3mVNut-GANN-Wheel-Square-of-Nine-KG
- **Math Core:** Spiral number grid: `n-th ring value = (2n-1)^2`; price projections via `sqrt(price) +/- degree_step`; time via `1deg = 1 day (365/360)`
- **Category:** Geometric / Gann Methods
- **Innovation: 3** -- Interesting mathematical construction (spiral numbers, geometric angle projections), though subjective in application
- **A-Share: 2** -- Price-level projections could work, but the geometric/degree system is market-agnostic and unvalidated for A-share regime
- **Key Insight:** The Square of Nine spiral formula `value(n) = n^2` placed on a 2D grid creates angular relationships at 45/90/180/270 degrees that map to price levels. The math is elegant even if the trading application is debatable

### #40 -- Vantage-X 3.0
- **URL:** https://www.tradingview.com/script/AQxfmHcn-Vantage-X-3-0
- **Math Core:** Multi-EMA system (9/21 fast, 20/50 mid, 50/200 macro) + RSI + StochRSI K-value + rolling order flow proxy (buy vs sell pressure)
- **Category:** Dashboard / Multi-Signal
- **Innovation: 2** -- Well-organized dashboard but combines standard indicators; the "FLOW" proxy (rolling buy vs sell pressure) is simple
- **A-Share: 3** -- All components use daily OHLCV; EMA/RSI/SRSI work universally
- **Key Insight:** The "PD FLOW" (previous day flow locked) concept provides a static session directional bias from yesterday's order flow -- a useful context layer

### #41 -- Conflux 4
- **URL:** https://www.tradingview.com/script/ARBm4EWj-Conflux-4
- **Math Core:** 4-filter AND-gate confluence: (1) VWMA+EMA trend alignment, (2) RSI threshold (55/45), (3) Supertrend direction, (4) ADX > 25. Trailing stop via Supertrend/ATR/fixed%. Trade block: entry + 4 TP levels + trailing after TP1.
- **Category:** Confluence Signal / Trade Management
- **Innovation: 3** -- Clean multi-filter confluence system with well-designed trade management (breakeven move after TP1). The AND-gate logic reduces noise meaningfully
- **A-Share: 4** -- All filters (VWMA, EMA, RSI, Supertrend, ADX) work on daily OHLCV. The preset system (scalp/day/swing) adapts to different holding periods. ATR-based SL respects the 10% limit context
- **Key Insight:** The 4-filter AND-gate is a disciplined signal framework. For A-share adaptation, the Supertrend period should be tuned for 10% daily limits (wider stops may be needed), and the RSI 55/45 thresholds may need adjustment for the A-share T+1 constraint

### #42 -- Murphy Timeframe Lens
- **URL:** https://www.tradingview.com/script/AWaMc5gi-Murphy-Timeframe-Lens
- **Math Core:** MTF OHLC compression with progressive high/low tracking (expanding boundaries as bar develops, no look-ahead)
- **Category:** Multi-Timeframe / Visualization
- **Innovation: 2** -- The progressive range tracking (no look-ahead) is a good engineering choice, but the core concept (viewing HTF on current chart) is standard
- **A-Share: 3** -- MTF compression works universally; progressive boundaries prevent unrealistic signals
- **Key Insight:** The "two timeframes higher" principle (e.g., 15m structure on 1m chart) provides optimal noise reduction without excessive lag -- a practical heuristic

### #43 -- Daye's True Opens [Quarterly Theory]
- **URL:** https://www.tradingview.com/script/AWcPTIRa-Daye-s-True-Opens-Quarterly-Theory
- **Math Core:** Quarterly Theory cycles: Q1 Accumulation, Q2 Manipulation (True Open), Q3 Distribution, Q4 Continuation. True Open = open of Q2 across 5 timeframes (session/day/week/month/year)
- **Category:** Market Structure / ICT-Style
- **Innovation: 3** -- Novel cyclical framework with multi-timeframe alignment. The "True Open = Q2 open" concept provides structured reference points
- **A-Share: 2** -- Session times are NY-oriented (19:30/01:30/07:30/13:30 NY time); would need complete re-timing for A-share sessions (9:30-11:30, 13:00-15:00 CST). The quarterly cycle concept could be adapted
- **Key Insight:** The 4-quarter cycle structure (Accumulation/Manipulation/Distribution/Continuation) applied fractally across timeframes is a useful mental model for market phases

### #44 -- amit EMA Breakdown Pullback SELL
- **URL:** https://www.tradingview.com/script/AWyaFjIj-amit-EMA-Breakdown-Pullback-SELL
- **Math Core:** EMA filter for trend direction + breakdown below support + pullback to EMA for short entry
- **Category:** Mean Reversion / Pullback
- **Innovation: 1** -- Standard breakdown-pullback pattern using EMA as dynamic resistance
- **A-Share: 3** -- EMA-based pullback works on daily data; T+1 constraint means you can't short in traditional sense
- **Key Insight:** Short-only strategy; for A-share, could be inverted for pullback-long entries in uptrend

### #45 -- Fed Chair Changes Daily Returns
- **URL:** https://www.tradingview.com/script/AamnXoon-Fed-Chair-Changes-Daily-Returns-1-3-6-12-months
- **Math Core:** Event study: average daily returns across Fed chair tenure periods at 1/3/6/12-month windows
- **Category:** Event Study / Macroeconomic
- **Innovation: 2** -- Clean event study framework; empirical but descriptive rather than predictive
- **A-Share: 1** -- US Fed-specific; PBoC governor changes could be analogous but would require separate data
- **Key Insight:** Useful as a template for event-driven analysis; the multi-window return comparison is a good analytical framework

### #46 -- XAUUSD Auto Strategy Connector Ready
- **URL:** https://www.tradingview.com/script/Ae37AI2n-XAUUSD-Auto-Strategy-Connector-Ready
- **Math Core:** EMA trend filter + ATR-based SL/TP (`SL = entry - k*ATR`, `TP = entry + m*ATR`); risk% lot sizing
- **Category:** Automated Trading / Gold-specific
- **Innovation: 1** -- Standard EMA+ATR strategy with MT5 connector; no novel math
- **A-Share: 2** -- EMA+ATR framework is universal, but the MT5 connector and gold-specific tuning limit direct applicability
- **Key Insight:** The risk-based lot sizing (`lots = risk_amount / (SL_distance * pip_value)`) is a correct position sizing formula worth remembering

### #47 -- Bookmap Traps
- **URL:** https://www.tradingview.com/script/AhH1CM72-Bookmap-Traps
- **Math Core:** Order flow trap detection based on volume at price levels + price rejection patterns
- **Category:** Order Flow / Market Microstructure
- **Innovation: 2** -- Trap detection concept is interesting but requires tick-level order book data
- **A-Share: 1** -- Requires Bookmap-style Level 2/order book data not typically available for A-share daily analysis
- **Key Insight:** The "trap" concept (large resting orders absorbed then price reverses) is a sound microstructural idea but hard to implement without real-time depth data

### #48 -- MapleStax CBC (Candle by Candle)
- **URL:** https://www.tradingview.com/script/AppLGbrI-MapleStax-CBC
- **Math Core:** Bull/bear state machine: `bull = close > prior_high`, `bear = close < prior_low` (state persists until invalidated). FOBO = consecutive flips. EMA9/20 cloud + VWAP + EMA200. NYSE opening range (9:30 ET, configurable minutes).
- **Category:** Bar-by-Bar Analysis / Regime Detection
- **Innovation: 3** -- Clean state machine for bar-by-bar control tracking. The FOBO (consecutive flip) concept filters out whipsaw. Combines micro (CBC) with macro (EMA cloud, VWAP) effectively
- **A-Share: 3** -- The CBC state machine works on any OHLCV data. VWAP requires intraday data (available). Session/opening range needs re-timing to 9:30 CST. EMA cloud works universally
- **Key Insight:** The CBC state machine (close > prior high = bull, close < prior low = bear, else hold) is a minimal, clean trend-following algorithm that could be a building block for A-share strategies

### #49 -- PRO FINAL OI OPTION S/R
- **URL:** https://www.tradingview.com/script/Aux0Wuep-PRO-FINAL-OI-OPTION-S-R
- **Math Core:** Open Interest analysis + options strike price concentration for S/R levels
- **Category:** Options / Derivatives
- **Innovation: 2** -- OI-based S/R is a known approach; options data integration adds value
- **A-Share: 1** -- Requires options OI data; A-share options market (50ETF options) has limited strike coverage and data availability
- **Key Insight:** High OI strikes act as magnet/resistance -- a concept applicable wherever options data is available

### #50 -- Advanced Simple Volume w/ Pocket Pivots
- **URL:** https://www.tradingview.com/script/B1qzsliR-Advanced-Simple-Volume-With-Pocket-Pivots
- **Math Core:** Pocket pivot: `volume > max(down_volume, N)` where price is up; requires `close > MA(min_period)` as trend filter. Additional volume metrics: VMA, relative volume, up/down volume ratios.
- **Category:** Volume Analysis / O'Neil Method
- **Innovation: 3** -- Pocket pivot concept from Gil Morales/Dr. Chris Kacher; identifies institutional accumulation via volume signature on up-days exceeding all down-volume in lookback
- **A-Share: 4** -- Volume-based, uses only daily OHLCV. The pocket pivot concept (up-day volume > all down-volume in N days) translates directly. MA trend filter works universally. Very compatible with A-share daily data
- **Key Insight:** Pocket pivots are high-conviction institutional footprints. For A-share, combining with the 10% daily limit: a stock hitting pocket pivot near the upper limit is an especially strong signal

### #51 -- AG Pro Mean Reversion Corridors
- **URL:** https://www.tradingview.com/script/B2aMfpd2-AG-Pro-Mean-Reversion-Corridors-AGPro-Series
- **Math Core:** Mean reversion bands: Z-score deviation from moving average with dynamic corridor width based on volatility regime
- **Category:** Mean Reversion / Statistical
- **Innovation: 2** -- Standard mean reversion framework with adaptive bands; well-executed but not novel mathematically
- **A-Share: 3** -- Z-score mean reversion works on any daily OHLCV; however, 10% daily limits can create "stuck" extremes that don't revert within the corridor timeframe
- **Key Insight:** Mean reversion in A-share context needs wider corridors (or a floor/ceiling filter for limit-hit stocks) to account for the 10% daily constraint

### #52 -- News Impact Analyzer
- **URL:** https://www.tradingview.com/script/B3fRF62o-News-Impact-Analyzer-forexobroker
- **Math Core:** Price change measurement around news timestamps (pre-event vs post-event windows)
- **Category:** Event Analysis / Fundamental
- **Innovation: 1** -- Simple before/after price comparison around news events
- **A-Share: 1** -- Requires news event timestamps; forex-oriented
- **Key Insight:** None notable

### #53 -- Key Levels ONH/ONL/PDH/PDL
- **URL:** https://www.tradingview.com/script/B6GKlUjx-Key-Levels-ONH-ONL-PDH-PDL
- **Math Core:** Overnight High/Low + Previous Day High/Low level plotting
- **Category:** Levels / Day Trading
- **Innovation: 1** -- Simple level extraction; overnight range is a known day trading concept
- **A-Share: 3** -- Previous day H/L available; overnight range concept maps to A-share pre-market auction range
- **Key Insight:** The overnight range (ONH-ONL) as a breakout zone is a practical intraday concept for A-share's 9:15-9:25 call auction

### #54 -- Stage2 Pro by Ketan
- **URL:** https://www.tradingview.com/script/B7wEgVoZ-Stage2-Pro-by-Ketan
- **Math Core:** Minervini Stage 2 identification: `price > MA(50) > MA(150) > MA(200)` + `MA(200) rising` + `RS_line > MA(RS_line)` + volume contraction/expansion patterns
- **Category:** Stock Screening / Minervini SEPA
- **Innovation: 3** -- Well-implemented Minervini Stage 2 criteria with multiple confirmation layers
- **A-Share: 4** -- All criteria (MA alignment, RS line, volume patterns) use daily OHLCV. The Stage 2 concept is highly relevant for A-share growth stock selection. RS line can be computed vs CSI300
- **Key Insight:** Minervini's Stage 2 template (MA alignment + RS outperformance + proper base formation) is one of the most systematically validated stock selection frameworks for A-share adaptation

### #55 -- Asia 786 Fib Levels
- **URL:** https://www.tradingview.com/script/BCqvvGrk-Asia-786-Fib-Levels
- **Math Core:** Fibonacci 0.786 retracement from Asian session range high/low
- **Category:** Fibonacci / Session-based
- **Innovation: 1** -- Single Fibonacci level from session range; the 0.786 level specifically
- **A-Share: 2** -- Asian session concept maps to A-share morning session, but the 0.786 level has no special significance in A-share empirical testing
- **Key Insight:** The 0.786 retracement (4th root of price ratio) is a less common Fib level; the Asian session anchor is forex-centric

### #56 -- BFH87fmb
- **URL:** https://www.tradingview.com/script/BFH87fmb
- **Math Core:** Unknown -- no descriptive title available
- **Category:** Unknown
- **Innovation: N/A**
- **A-Share: N/A**
- **Key Insight:** Page not fetched; name-only entry

### #57 -- BHhJyAT1
- **URL:** https://www.tradingview.com/script/BHhJyAT1
- **Math Core:** Unknown -- no descriptive title available
- **Category:** Unknown
- **Innovation: N/A**
- **A-Share: N/A**
- **Key Insight:** Page not fetched; name-only entry

### #58 -- BJDRgy7z
- **URL:** https://www.tradingview.com/script/BJDRgy7z
- **Math Core:** Unknown -- no descriptive title available
- **Category:** Unknown
- **Innovation: N/A**
- **A-Share: N/A**
- **Key Insight:** Page not fetched; name-only entry

### #59 -- Alvarium CC
- **URL:** https://www.tradingview.com/script/BL9TB60O-Alvarium-CC
- **Math Core:** Crypto correlation / cycle composite analysis
- **Category:** Crypto / Cycle
- **Innovation: 2** -- Correlation and cycle composite concept for crypto assets
- **A-Share: 1** -- Crypto-specific; cycle concept could be adapted but requires separate calibration
- **Key Insight:** Correlation-based asset selection (low-correlation basket) is a portfolio optimization concept applicable across markets

---

## Highlights

### Top Innovation (4-5)
1. **#31 CTZ BTC Cost Of Production (5)** -- Power-law mining cost floor model; genuine structural insight into BTC fundamental valuation
2. **#36 VAA Vigilant Asset Allocation (4)** -- Academic-quality momentum+breadth rotation framework; 13612W scoring is empirically validated

### Top A-Share Applicability (4)
1. **#33 Daily Bias (4)** -- Clean swing+MA bias filter translates directly to daily A-share data
2. **#36 VAA (4)** -- Momentum+breadth rotation framework adaptable to CSI300/CSI500 + bond ETF rotation
3. **#41 Conflux 4 (4)** -- 4-filter confluence system with all components (VWMA, EMA, RSI, Supertrend, ADX) available on daily OHLCV
4. **#50 Pocket Pivots (4)** -- Volume-based institutional footprint detection works perfectly with A-share daily volume data
5. **#54 Stage2 Pro (4)** -- Minervini Stage 2 screening with MA alignment + RS line + volume patterns; all daily OHLCV compatible

### Key Learnings for A-Share Strategies

1. **13612W Momentum Scoring** (from #36): `score = 12*r(1m) + 4*r(3m) + 2*r(6m) + r(12m)` -- weighted momentum captures multiple timeframe trends. Adapt for A-share: use CSI300/CSI500/CSI1000 + bond ETF universe

2. **Pocket Pivot Detection** (from #50): `volume > max(down_volume_N)` on an up-day with `close > MA` -- institutional accumulation signal. For A-share: combine with 10% limit proximity for extra conviction

3. **Minervini Stage 2 Template** (from #54): `price > MA50 > MA150 > MA200` + rising MA200 + RS_line > MA(RS_line) -- systematic growth stock screening. Compute RS vs CSI300 for A-share adaptation

4. **CBC State Machine** (from #48): `bull = close > prior_high`, `bear = close < prior_low` -- minimal bar-by-bar regime detection. Clean building block for trend-following subsystems

5. **4-Filter AND-Gate** (from #41): Trend(VWMA+EMA) AND Momentum(RSI) AND Volatility(Supertrend) AND Strength(ADX) -- disciplined confluence system. Each filter independently reduces noise; AND-gate ensures high selectivity

### Strategies to Skip for A-Share
- #31 (BTC-specific), #45 (Fed-specific), #46 (Gold/MT5), #47 (requires L2 data), #49 (requires options OI), #52 (forex news), #55 (Asian session = forex), #59 (crypto-specific)

---

*End of batch_4_new analysis (indices 30-59)*
