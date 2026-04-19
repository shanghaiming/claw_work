# TV Batch 5 Extended 4 - Scripts 90-121 Analysis

**Date:** 2026-04-19
**Range:** batch_5.json indices 90-121 (32 scripts)
**Methodology:** webReader fetch + Pine Script code analysis

---

## Summary

| # | Index | Script Name | Innovation | A-Share | Category |
|---|-------|-------------|:----------:|:-------:|----------|
| 1 | 90 | Trend Momentum Algionics Ribbon Pressure Field | 5 | 4 | Ribbon/Pressure |
| 2 | 91 | HS Capital EMA's | 1 | 2 | EMA/Trend |
| 3 | 92 | US10Y DXY Structure Dashboard | 1 | 1 | Macro/Dashboard |
| 4 | 93 | Zuri FVG Imbalance Reaction Zones 2.0 | 3 | 3 | FVG/SMC |
| 5 | 94 | Marco Top Detector | 2 | 3 | Pivot Detection |
| 6 | 95 | EMA 4 / EMA 9 Cross | 1 | 2 | EMA Cross |
| 7 | 96 | Daily Open 5-Minute Range Box | 2 | 3 | Opening Range |
| 8 | 97 | Aura Trend Cloud Navigator (Pineify) | 3 | 4 | Adaptive MA |
| 9 | 98 | Stage2 Pro by Ketan | 3 | 3 | MTF Trend |
| 10 | 99 | EMA 5/8/13 + RSI 70/30 Strategy | 1 | 3 | EMA+RSI |
| 11 | 100 | Key Levels: Prev Day + Premarket + Dual 5m Open | 2 | 3 | Key Levels |
| 12 | 101 | Gold Prime | - | - | FETCH FAILED |
| 13 | 102 | PhantomFlow V4.1 Gold Indicator | - | - | FETCH FAILED |
| 14 | 103 | Fairbourn Pivots RTH MTF | - | - | FETCH FAILED |
| 15 | 104 | hWUajDEi (unknown) | - | - | FETCH FAILED |
| 16 | 105 | hlG9YfOd (unknown) | - | - | FETCH FAILED |
| 17 | 106 | hyonJDZ9 (unknown) | - | - | FETCH FAILED |
| 18 | 107 | ATR TP Levels | - | - | FETCH FAILED |
| 19 | 108 | SHEMAR HMA ST SMC Confidence Filter | - | - | FETCH FAILED |
| 20 | 109 | Fib for Killzone | - | - | FETCH FAILED |
| 21 | 110 | iM3LCAjq (unknown) | - | - | FETCH FAILED |
| 22 | 111 | MyLibrary | - | - | FETCH FAILED |
| 23 | 112 | iaDXfwDX (unknown) | - | - | FETCH FAILED |
| 24 | 113 | EMA21 55 100 200 v1.3 | - | - | FETCH FAILED |
| 25 | 114 | CTZ Auto Fib Vol POC Confluence | - | - | FETCH FAILED |
| 26 | 115 | Trading Plan Configurable | - | - | FETCH FAILED |
| 27 | 116 | Execution Discipline | - | - | FETCH FAILED |
| 28 | 117 | Vantage X 2.1 | - | - | FETCH FAILED |
| 29 | 118 | Padayappa | - | - | FETCH FAILED |
| 30 | 119 | 4H Session Volume Profile | - | - | FETCH FAILED |
| 31 | 120 | Accumulation Distribution Oscillator ADO | - | - | FETCH FAILED |
| 32 | 121 | Absorption Detector v3.1 | - | - | FETCH FAILED |

**Stats:** 11 successfully analyzed, 21 fetch failed or insufficient data
**Avg Innovation (analyzed):** 2.2 / 5
**Avg A-Share Applicability (analyzed):** 2.9 / 5

---

## Strategy Details

### 1. Trend Momentum (Algionics) - Ribbon Pressure Field [Index 90]

**URL:** `https://www.tradingview.com/script/gidoT7f9-Trend-Momentum-Algionics-Ribbon-Pressure-Field`
**Innovation:** 5/5 | **A-Share:** 4/5

**Mathematical Core:**
- 28-line EMA ribbon spanning periods 20-236 in steps of 8
- Multi-stage smoothing kernel: `ama = (EMA + SMA) / 2`, then secondary kernel `k = ceil(len * 0.08)`, `kl = EMA(ama, k)`, final = `(kl + SMA(kl, k+2)) / 2`
- **Force Boundary:** `bullForce = max(price - ribbon_min, 0)`, `bearForce = min(price - ribbon_max, 0)`
- **Distance-Weighted Pressure Ratio:** Each ribbon line's distance from price is measured individually. Lines below contribute bull pressure proportional to distance. Ratio = bull_sum / total_sum * 100
- **Bias Line:** `biasLine = bearForce + (bullForce - bearForce) * (bull_dom / 100)` -- dual-input convergence of boundary + pressure
- **Latch-based state engine:** Only flips at extremes (0 or 100). States: Trend/Hold/Weakening/Reversal Warning
- **Geometric mean** for smoothing length: `GM_LEN = round(sqrt(20 * 236))` = natural interaction scale

**Key Innovation:**
The distance-weighted pressure measurement is genuinely novel. Instead of simple line count above/below price (like standard ribbon indicators), it sums the absolute distance to each line, creating a pressure gradient field. The dual-separation architecture (Force Boundary + Pressure Ratio computed independently, converging only at Bias Line) is elegant.

**A-Share Applicability:**
All math uses OHLCV only. The ribbon concept translates well to daily timeframe with 10% limits. The state engine's latch mechanism at 0/100 extremes is robust for A-share regime detection. Periods 20-236 span medium-to-long term suitable for daily bars. High applicability.

---

### 2. HS Capital EMA's [Index 91]

**URL:** `https://www.tradingview.com/script/gloOuWwW-HS-Capital-EMA-s`
**Innovation:** 1/5 | **A-Share:** 2/5

**Mathematical Core:**
- EMA crossover system with engulfing candle filter
- Basic trend-following using moving average alignment
- Entry confirmation via engulfing candlestick patterns

**Key Innovation:**
Minimal innovation. Standard EMA trend + engulfing pattern combination. No novel math.

**A-Share Applicability:**
Basic EMA crossover works but lacks specificity for A-share constraints. Engulfing patterns less reliable with 10% daily limits.

---

### 3. US10Y + DXY Structure Dashboard [Index 92]

**URL:** `https://www.tradingview.com/script/guscJmRn-US10Y-DXY-Structure-Dashboard`
**Innovation:** 1/5 | **A-Share:** 1/5

**Mathematical Core:**
- Dashboard displaying US 10Y Treasury yield and DXY correlation
- Inverse correlation visualization between bonds and dollar

**Key Innovation:**
No algorithmic innovation. Visual dashboard for macro correlation.

**A-Share Applicability:**
Not applicable. US-specific macro instruments (US10Y, DXY). A-share market has different macro drivers.

---

### 4. Zuri FVG Imbalance Reaction Zones 2.0 [Index 93]

**URL:** `https://www.tradingview.com/script/gwA0e7EY-Zuri-FVG-Imbalance-Reaction-Zones-2-0`
**Innovation:** 3/5 | **A-Share:** 3/5

**Mathematical Core:**
- Fair Value Gap (FVG) detection: 3-candle pattern where candle[1].low > candle[3].high (bearish) or candle[1].high < candle[3].low (bullish)
- Session-open and weekend gap filtering to identify "true" flow-formed FVGs only
- Zone lifecycle management: fresh -> tapped -> directional reaction -> invalidated on close through opposite side with buffer
- Visual update on price interaction (tap detection, directional shift)

**Key Innovation:**
The reaction-based zone tracking is notable. Instead of static FVG marking, zones update dynamically based on price interaction type. The session-open filtering removes false FVGs from gaps. The buffer-based invalidation prevents premature deletion.

**A-Share Applicability:**
FVG concept works on daily charts. The 10% limit constraint means gaps are bounded but FVGs still form after limit-open moves. Weekend filtering is relevant (Saturday/Sunday gaps). However, intraday focus and session-specific logic (US RTH) need adaptation for A-share trading hours.

---

### 5. Marco Top Detector [Index 94]

**URL:** `https://www.tradingview.com/script/gyq3Jq14-Marco-Top-Detector`
**Innovation:** 2/5 | **A-Share:** 3/5

**Mathematical Core:**
- ATR-linked percentage deviation threshold for swing detection
- Look-back/look-forward depth window to verify pivot is local extreme
- Dynamic label updating: labels "drag" higher/lower if price continues pushing before reversal confirmation
- Offset precision: labels placed at actual bar of the high/low, not confirmation bar

**Key Innovation:**
The ATR-linked deviation threshold adapts pivot sensitivity to current volatility. The auto-updating label system is practical. However, the core is standard pivot detection with ATR scaling.

**A-Share Applicability:**
ATR-based deviation works well with daily bars. The depth parameter can be tuned for A-share market structure. The offset precision (placing at actual extreme bar) is universally useful. Moderate applicability.

---

### 6. EMA 4 / EMA 9 Cross [Index 95]

**URL:** `https://www.tradingview.com/script/h4qlxSL7-EMA-4-EMA-9-Cross`
**Innovation:** 1/5 | **A-Share:** 2/5

**Mathematical Core:**
- EMA(4) and EMA(9) crossover with VWAP filter
- Buy: Close above both EMAs (green band) AND crossing up VWAP, OR close above EMAs but far below VWAP
- Sell: Close below both EMAs (red band) AND crossing down VWAP, OR close below EMAs but far above VWAP
- Designed for 5-minute timeframe

**Key Innovation:**
None. Very basic EMA crossover + VWAP interaction logic.

**A-Share Applicability:**
VWAP requires intraday data. The dual condition (EMA alignment + VWAP position) adds some filtering but is too simple for systematic A-share trading. Low applicability for daily-only constraint.

---

### 7. Daily Open 5-Minute Range Box [Index 96]

**URL:** `https://www.tradingview.com/script/h6pDtjUc-Daily-Open-5-Minute-Range-Box-Any-Timeframe`
**Innovation:** 2/5 | **A-Share:** 3/5

**Mathematical Core:**
- Captures the high-low range of the first 5-minute candle of the day
- Projects this range as a horizontal box across all timeframes
- Acts as "liquidity anchor" for intraday positioning
- Used for compression vs. expansion identification
- Constraint framework: trades only when price behavior around this range aligns with HTF bias

**Key Innovation:**
The concept of using the first 5-minute range as a structural reference across timeframes is clean and practical. Not mathematically complex but conceptually sound as a "opening balance" tool.

**A-Share Applicability:**
The opening range concept translates well to A-shares. The first 5-minute bar (9:30-9:35) captures early auction imbalance. Adaptable to daily timeframe thinking. However, the intraday-specific design limits direct daily-only applicability.

---

### 8. Aura Trend Cloud Navigator (Pineify) [Index 97]

**URL:** `https://www.tradingview.com/script/h8hFCBxv-Aura-Trend-Cloud-Navigator-Pineify`
**Innovation:** 3/5 | **A-Share:** 4/5

**Mathematical Core:**
- **Trend Regularity Adaptive Moving Average (TRAMA):**
  1. Binary signal: 1 if new highest high OR lowest low over lookback (default 99), else 0
  2. Average of binary signal via SMA, then SQUARED: `coefficient = SMA(binary, 99)^2`
  3. Recursive baseline: `baseline += coefficient * (close - baseline)`
  4. Squaring creates nonlinear response: coefficient drops sharply in ranges, rises steeply in trends
- ATR envelope: `upper = baseline + mult * ATR(14)`, `lower = baseline - mult * ATR(14)`
- Crossover signals filtered by adaptive regime

**Key Innovation:**
The "trend regularity" approach measures how often new extremes occur rather than price direction or momentum. Squaring the coefficient means the MA practically freezes in ranges (coefficient near 0) and tracks closely in trends (coefficient near 1). This is a clean alternative to Kaufman's efficiency ratio or Chande's volatility scaling. The all-or-nothing response is distinctive.

**A-Share Applicability:**
Excellent. Uses only OHLCV. The 99-period default on daily charts captures medium-term trends. The "frozen in ranges" behavior is valuable for A-shares where prolonged consolidation is common before limit-move breakouts. The ATR cloud adapts to 10% limit-driven volatility. High applicability.

---

### 9. Stage2 Pro by Ketan [Index 98]

**URL:** `https://www.tradingview.com/script/hB9sdX6j-Stage2-Pro-by-Ketan`
**Innovation:** 3/5 | **A-Share:** 3/5

**Mathematical Core:**
- Multi-timeframe trend classification system:
  - Weekly Stage-2 trend identification (price > MA, making higher highs/lows)
  - Weekly Higher High confirmation
  - Monthly RSI strength filter
  - Relative Strength vs. NIFTY MidSmall 400 benchmark
- Trade stance classification: STRONG BUY / BUY / WATCHLIST / AVOID
- Hard sell rule: entire candle below Monthly 18 MA triggers exit

**Key Innovation:**
The structured MTF scoring system with clear classification tiers is practical. The "hard sell below monthly 18 MA" rule provides a non-negotiable risk management floor. However, individual components are standard technical analysis.

**A-Share Applicability:**
The MTF framework concept is transferable but needs A-share adaptation. The benchmark comparison (NIFTY MidSmall 400) must be replaced with CSI 500 or similar. Monthly MA exit rule works on daily bars. Moderate applicability with adaptation.

---

### 10. EMA 5/8/13 + RSI 70/30 Strategy [Index 99]

**URL:** `https://www.tradingview.com/script/hLWS8cHh`
**Innovation:** 1/5 | **A-Share:** 3/5

**Mathematical Core:**
- Fibonacci-based EMA periods (5, 8, 13) for trend alignment
- RSI with 70/30 threshold for overbought/oversold confirmation
- Entry on EMA alignment + RSI extreme
- Designed for 15-minute and shorter timeframes; recommends daily/weekly/monthly for longer-term

**Key Innovation:**
None. Standard EMA ribbon + RSI combination using Fibonacci sequence periods.

**A-Share Applicability:**
Basic EMA+RSI combo works on daily timeframe. The Fibonacci periods (5,8,13) are short enough for reasonable responsiveness on daily bars with 10% limits. However, no novel filtering or adaptation for A-share specifics.

---

### 11. Key Levels: Prev Day + Premarket + Dual 5m Open [Index 100]

**URL:** `https://www.tradingview.com/script/hMdGqRZp-Key-Levels-Prev-Day-Premarket-Dual-5m-Open`
**Innovation:** 2/5 | **A-Share:** 3/5

**Mathematical Core:**
- Previous Day High/Low levels
- Pre-Market High/Low levels
- Dual 5-minute opening range: separate AM and PM session ranges
- All levels drawn as horizontal lines for structure reference

**Key Innovation:**
The dual AM/PM session opening range is a practical refinement. Clean level identification system for intraday structure trading. No mathematical novelty but good practical design.

**A-Share Applicability:**
Previous day H/L is universally applicable. Pre-market levels are relevant for A-shares (9:15-9:25 auction). The AM/PM session split maps to A-share morning/afternoon sessions (9:30-11:30 / 13:00-15:00). Moderate applicability with session time adaptation.

---

## Highlights

### Top Innovation: Trend Momentum Algionics Ribbon Pressure Field
The distance-weighted pressure ratio across a 28-line EMA ribbon is the most mathematically sophisticated approach in this batch. The dual-separation architecture (Force Boundary computed independently from Pressure Ratio, converging only at the Bias Line) creates a clean decomposition of "how far is price from the field" vs. "how is pressure distributed within the field." The latch-based state engine using only structural boundaries (0, 50, 100) rather than arbitrary thresholds is elegant.

### Best A-Share Candidate: Aura Trend Cloud Navigator (TRAMA)
The Trend Regularity Adaptive MA offers the strongest A-share applicability. Its key property -- practically freezing in consolidation and tracking closely in trends -- directly addresses the challenge of A-share trading where prolonged ranges precede sudden limit-move breakouts. The squaring of the trend regularity coefficient creates a binary-like regime switch that is well-suited to the A-share market structure. All math uses daily OHLCV only.

### Notable Concept: Zuri FVG Imbalance Reaction Zones
The lifecycle management of FVG zones (fresh -> tapped -> directional reaction -> invalidated) with session-open filtering is a practical improvement over static FVG indicators. Adaptable to A-share daily charts where gap moves from limit opens create true inefficiencies.

### Files Analyzed (indices 101-121): Insufficient data
Scripts at indices 101-121 either returned no meaningful Pine Script content in the webReader response (TradingView shows these as interactive chart pages without exposing source code in the HTML), or the pages returned minimal data. These would require direct Pine Script source access or TradingView's API to analyze properly.

---

## Actionable Takeaways for A-Share Strategy Development

1. **TRAMA (Trend Regularity Adaptive MA):** Implement `coefficient = SMA(new_extreme_binary, period)^2` recursive baseline. Period 99 on daily captures trend regime well. The nonlinear squaring is the key insight -- create near-binary regime detection from smooth inputs.

2. **Distance-Weighted Ribbon Pressure:** Replace simple ribbon line count with sum-of-distances approach. This captures the pressure gradient, not just majority direction. For A-shares, a shorter ribbon (periods 5-60, step 5) would be more responsive.

3. **Latch-Based State Engine:** Use mathematical extremes (all lines above/below price) for state transitions rather than arbitrary thresholds. This eliminates parameter sensitivity in regime classification.

4. **FVG Lifecycle with Session Filter:** Adapt the zone lifecycle concept for A-share daily charts. Filter out gaps caused by overnight news (similar to session-open filter). Track zone interaction for reaction confirmation.
