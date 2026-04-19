# TradingView Batch 5 Learning Notes
# Source: batch_5.json (121 scripts, IDs e-o prefix range)
# Processed: 2026-04-19

## Statistics
| Category | Count |
|----------|-------|
| Total scripts | 121 |
| Deep analyzed (webReader) | 5 |
| Name-classified | 76 |
| ID-only (no name) | 27 |
| Tool/utility/duplicate | 13 |

---

## Deep-Analyzed Strategies (webReader verified)

### 1. Advanced Dual Hull Cross Suite V9 (gKs2ojOP) - NitMan279
**URL:** https://www.tradingview.com/script/gKs2ojOP-Advanced-Dual-Hull-Cross-Suite-V9
**Category:** Trend Following / Momentum
**Rating:** 3/5 (A-stock)

**Core Logic:**
Dual Hull MA crossover system. Fast line uses THMA (Triple Hull MA, default 16) for extreme responsiveness. Slow line uses standard HMA (default 14) as trend baseline. Three HMA variants available: HMA, EHMA (Exponential), THMA. Slope-based coloring provides early warning before crossover. Lines change color dynamically based on slope direction.

**Key Innovation:** 
- Triple HMA variant (THMA) uses triple-weighted WMA logic for near-zero-lag signal
- Slope-based color change as pre-crossover warning system
- Dual-variation selection (choose HMA/EHMA/THMA per line)

**Indicators:** Hull MA, THMA, EHMA
**A-stock Adaptability:** High. MA crossover systems work well on A-shares. HMA's low-lag property is universally applicable. No tick/session dependency.

---

### 2. Cumulative Applied Force Differential (keGsJUHD) - chriskokal1
**URL:** https://www.tradingview.com/script/keGsJUHD-Cumulative-Applied-Force-Differential
**Category:** Order Flow / Market Microstructure
**Rating:** 4/5 (A-stock)

**Core Logic:**
Measures buying/selling pressure buildup via cumulative delta, then compares today's session bar-for-bar against yesterday's session at the same moment. Each bar's net pressure (bid/ask proxy volume) runs into session-indexed arrays. When new session starts, yesterday's array is saved. The script retrieves yesterday's cumulative delta at the exact same session point and computes the divergence: today's CVD minus yesterday's CVD = Cumulative Applied Force Differential.

**Key Innovation:**
- Session-aligned bar-for-bar CVD comparison (yesterday vs today at same session point)
- ATR-defined zone classification (upper/lower/neutral) for pressure context
- Session-indexed array architecture for temporal alignment
- Reveals acceleration, fading strength, absorption before price shows it

**Indicators:** Cumulative Delta, ATR, Volume
**A-stock Adaptability:** Medium-High. CVD proxy from bid/ask estimation may need adaptation. The session-comparison concept is powerful for A-share intraday trading. Need to replace with tick-level data or use close-location-value proxy.

---

### 3. Cost Basis + Cipher Filtered Signal v3 (mzjNsrda) - Etherstein
**URL:** https://www.tradingview.com/script/mzjNsrda-Cost-Basis-Cipher-Filtered-Signal-v3
**Category:** Multi-factor / Crypto Regime Detection
**Rating:** 2/5 (A-stock)

**Core Logic:**
Multi-layer market regime indicator built around macro stress thesis monitoring two simultaneous compression cycles (private credit + commercial RE bubble, crypto speculative cycle). Uses ETH SOPR from Glassnode as primary on-chain signal, combined with RSI, dual EMA (50/200) trend alignment, Bollinger Band squeeze detection, funding rate proxy (perpetual-spot spread), and volume ratio analysis. All rolled into composite scoring: BULLISH/BEARISH/NEUTRAL thesis.

**Key Innovation:**
- On-chain data (ETH SOPR) + technical indicators composite scoring
- Funding rate proxy from perpetual-spot price spread
- Macro stress thesis framework (credit bubble + crypto cycle convergence)

**Indicators:** SOPR, RSI, EMA(50/200), Bollinger Bands, Volume Ratio
**A-stock Adaptability:** Low. Crypto-specific with on-chain data (Glassnode). Architecture of composite scoring is reusable but all inputs need replacement.

---

### 4. 4BB Quad Fusion + Trend Pro (jvHL2KvO) - emin_hasimi
**URL:** https://www.tradingview.com/script/jvHL2KvO-4BB-Quad-Fusion-Trend-Pro
**Category:** Multi-factor / Bollinger Band System
**Rating:** 4/5 (A-stock)

**Core Logic:**
Multi-timeframe trend detection using 4 Bollinger Bands (EMA+WMA bands on High and Low) for squeeze/breakout detection. Smart HTF analysis checks Daily, 4H, 1H for MA20 slope, BB scenarios, candle strength, reversal patterns. Weekly priority logic for Monday/Tuesday candle bias. Clear final decision: "YES: Buy Priority" / "YES: Bullish confirmed" / "NO: Wait" with reasoning table. Hammer, Shooting Star, Engulfing patterns highlighted. Automatic trendline break detection.

**Key Innovation:**
- Quad BB (EMA+WMA on High+Low) for squeeze detection
- Weekly priority logic (Mon/Tue candle directional bias)
- Decision table with full reasoning chain
- Multi-timeframe confirmation (Daily/4H/1H cascade)

**Indicators:** Bollinger Bands (x4), EMA, WMA, MA20, Candlestick Patterns
**A-stock Adaptability:** High. BB squeeze systems work universally. The weekly priority logic (Mon/Tue bias) is directly applicable to A-share weekly open patterns. Multi-TF approach maps to A-share timeframes perfectly.

---

### 5. Trend Momentum Algionics Ribbon Pressure Field (gidoT7f9) - Algionics
**URL:** https://www.tradingview.com/script/gidoT7f9-Trend-Momentum-Algionics-Ribbon-Pressure-Field
**Category:** Trend Following / Quantitative Pressure Analysis
**Rating:** 5/5 (A-stock)

**Core Logic:**
28-line EMA ribbon (periods 20-236, step 8) interpreted as physical force landscape. Each line passes through multi-stage smoothing kernel: (EMA+SMA)/2 first, then secondary EMA kernel at 8% of period. Two independent measurements: Force Boundary (raw displacement from field edges) and Pressure Ratio (distance-weighted sum across all 28 lines). Bias Line = convergence point of both. Latch-based state engine: Trend/Hold/Weakening/Reversal Warning, driven by mathematical extremes (0/50/100) not arbitrary thresholds.

**Key Innovation:**
- Distance-weighted pressure measurement (line 10pts below = 10x more bull pressure than line 1pt below)
- Dual separation architecture: Force Boundary + Pressure Ratio computed independently
- Latch-based state engine with mathematical boundaries (0/50/100)
- Interlocking constant architecture: everything derives from START_P=20, END_P=236
- Geometric mean smoothing length (sqrt(20*236) = ~69)
- Gradient candle coloring based on pressure, not price direction

**Indicators:** 28-line EMA Ribbon, Force Boundary Histogram, Pressure Ratio, Bias Line
**A-stock Adaptability:** Very High. Pure price-based system. No tick/session dependency. The distance-weighted pressure concept is mathematically elegant and universally applicable. State engine provides clear trading signals.

---

### 6. Fractal Liquidity Map [JOAT] (oU4jOvjQ) - officialjackofalltrades (BATCH 6, deep-analyzed here)
**URL:** https://www.tradingview.com/script/oU4jOvjQ-Fractal-Liquidity-Map-JOAT
**Category:** Liquidity / Market Structure
**Rating:** 5/5 (A-stock)

**Core Logic:**
Six non-overlapping visual systems for institutional liquidity landscape:
1. Williams Fractal detection (N-bar window, confirmed on close)
2. Cluster S/R Zones (N+ fractals within 1x ATR = institutional interest area)
3. Equal Highs/Lows (EQH/EQL) liquidity pools (stop-hunt targets within 0.15x ATR tolerance)
4. Sweep Detection (price breaks pool level then closes back = stop-hunt confirmed)
5. Multi-length Pivot Levels (10/30/75 bar, distance-opacity gradient)
6. Hann FIR Trend Ribbon (3-layer, crossover signals)

Clean-redraw architecture: only price levels stored in arrays, all drawing objects deleted and recreated on barstate.islast. Zero overlap/accumulation.

**Key Innovation:**
- Clean-redraw architecture (delete+recreate vs accumulate) solves visual clutter
- Cluster zones from fractal convergence within ATR tolerance
- Sweep detection using pool levels as reference (not arbitrary lookback)
- Six visual layers occupying separate lanes, zero interference

**Indicators:** Williams Fractals, ATR, Hann FIR Filter, Pivot Points
**A-stock Adaptability:** Very High. Pure OHLC-based. Fractal + liquidity pool concept is market-agnostic. Clean-redraw architecture is a design pattern worth adopting.

---

## Name-Classified Strategies (by keyword matching)

### Trend Following (16)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| g2vSmtry | Classic EMA 9/21 crossover | EMA(9,21) | Basic crossover, standard |
| gGHRwDOJ | Ford Swing Line | Swing Analysis | Swing trend detection |
| gcPZFTFt | Multi-Length Displaced MA | Displaced MA | Offset MA system |
| gloOuWwW | HS Capital EMAs | EMA | Multi-EMA |
| h4qlxSL7 | EMA 4/EMA 9 Cross | EMA(4,9) | Fast EMA cross |
| h8hFCBxv | Aura Trend Cloud Navigator | Trend Cloud | Trend-following cloud |
| j4pkoUHe | EMA21/55/100/200 | EMA(21,55,100,200) | Fibonacci EMA stack |
| kq3kNktW | CPR D/W/M Bull Bear Stacking + EMA | CPR, EMA(9,15) | CPR multi-timeframe |
| l7erV7F1 | Fibonacci MA Trend Gap | Fibonacci, MA | Fib-MA hybrid |
| lfxfpdpx | ES Breakout Toolkit + Momentum Close Filter | Momentum, Breakout | Breakout with filter |
| llNOIbcG | Lion Share Trading Structure | Market Structure | Structure-based trend |
| m5UKrZxf | Pure PA MS System | Price Action, MS | Pure price action |
| siAWIOA2 | Quad Triple EMA Trend Bands | Triple EMA | Quad TEMA bands |
| zIMSRViX | trendshift | Trend | Trend shift detector |
| zLcvM9ly | Fast MA Pullback Alarm | MA Pullback | Pullback to MA |
| zOtCgk90 | Sathish SMA Ribbon (5-200) | SMA Ribbon | Full SMA spectrum |

### Momentum (10)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| ex5eKUo1 | Higher Lower Close Count PRO | Close counts | Directional bias meter |
| g0jGKt3K | MNQ OR Retest Breakout 5m | Breakout | 5-min breakout retest |
| guscJmRn | US10Y DXY Structure Dashboard | Macro | Bond/DXY correlation |
| hB9sdX6j | Stage2 Pro by Ketan | Stage analysis | Minervini Stage 2 |
| kRKwaXDi | Stochastic Divergence Pro V2 | Stochastic, Divergence | Div detection |
| kZzDTCDd | Daily Bias 5 Min | Bias | Daily bias intraday |
| n2FTdVu4 | BK AK Vigilante | Momentum | Momentum system |
| nriJvaTu | RevStrat Reversals Alerts | Reversal | Reversal strategy |
| o77HtCqJ | SPY 9EMA Momentum Patterns | EMA(9), Patterns | 9EMA pattern recognition |
| w8Sxspz1 | Stage2 Pro by Ketan (dup) | Stage analysis | Duplicate |

### Volatility / Squeeze (8)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| g0QS5WSP | CISD AND FVG | FVG, CISD | Fair Value Gap + CISD |
| gwA0e7EY | Zuri FVG Imbalance Reaction Zones 2.0 | FVG, Imbalance | FVG zone analysis |
| iE5yE8NY | ATR TP Levels | ATR | ATR-based take profit |
| lnvrkL80 | Fractal Advanced Divergence | Fractal, Divergence | Fractal divergence |
| msC4APvA | HTF FVG BISI SIBI | FVG | Higher-TF FVG (BISI/SIBI) |
| u17uwQql | Dual Structure BB Ribbon | Bollinger Bands | Dual BB structure |
| zNPRdAiF | Iterative Locally Periodic Envelope | Envelope | Statistical envelope |
| zgT5XBsS | DXY vs GOLD Equilibrium Oscillator | DXY, Gold | Cross-asset oscillator |

### Order Flow / Volume (12)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| fuBvjSaj | Open Interest with Futures Matcher | Open Interest | OI futures matching |
| gg86FQWy | CTZ CVD Divergence | CVD, Divergence | Cumulative Volume Delta div |
| gidoT7f9 | Trend Momentum Algionics Ribbon | 28-line EMA | **DEEP analyzed** |
| jqKkUC19 | Absorption Detector v3.1 | Absorption | Order absorption |
| ko2EQb4L | FOOTPRINT BY CTR 2.0 | Footprint | Volume footprint |
| ltrgx3kE | Delta Histogram | Delta | Buy/sell delta |
| m09cxkI0 | Short Volume Dynamic Safe | Short Volume | Short selling volume |
| mRJKAfEW | Volume Profile Sniper | Volume Profile | VP-based levels |
| n807k0fu | Volume Footprint Simplifyed | Footprint | Simplified footprint |
| nBs3Mdno | Pre-Fixing Volume Spike | Volume | Pre-market volume spike |
| qn9EkFgv | Relative Volume at Time | RelVol | Time-based relative vol |
| rnsaf4Tn | SHK CCI RSI Merged HA Signal MA Dual Div v6 | CCI, RSI, HA | Multi-oscillator merged |

### Support/Resistance / Levels (12)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| f2qqYN1c | Daily Trading Times UTC 2 | Session | Session-based levels |
| g4zjCqpe | Session Levels IQ | Session | Session levels |
| hMdGqRZp | Key Levels Prev Day Premarket | Key Levels | Previous day levels |
| hTRa9Rsb | Fairbourn Pivots RTH MTF | Pivots, RTH | Multi-TF pivots |
| iHRirxFX | SHEMAR HMA ST SMC Confidence | HMA, SMC | SMC confidence filter |
| iLQT7m0n | Fib for Killzone | Fibonacci | Killzone fib levels |
| j8LI57Se | CTZ Auto Fib Vol POC Confluence | Fib, Vol POC | Auto fib + VP confluence |
| kdbOh7tF | SL Session Levels VWAP EMAs | Session, VWAP, EMA | Session + VWAP combo |
| l9ZBVMrP | Relevant Swings ICT Full Coverage | Swing | ICT swing structure |
| nRh8oQxh | Recently Hunted Swing H/L | Swing H/L | Hunted swing levels |
| nP8yFJ5O | NS Style Daily Weekly Zones PRO | Zones | Daily/weekly zones |
| kmEDpXsv | MI4P 50 Rule Book Level | Levels | Institutional level system |

### Multi-factor (10)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| ebIjXmQR | ICT Multi Strategy Scalper PRO v3 | ICT, Multi | ICT multi-strategy |
| fRXnVB3Q | Multi Indicator Screener 30 Assets | Multi | Cross-asset screener |
| iHRirxFX | SHEMAR HMA ST SMC Confidence | HMA, SMC | SMC + HMA confidence |
| jV2Qlvfj | Vantage X 2.1 | Multi | Multi-factor system |
| lODBOB7a | ORB 1H High Low Alert EMA SMA | ORB, EMA, SMA | Opening range + MA |
| ocGCsTyY | ORB VWAP RSI Signals | ORB, VWAP, RSI | Triple confluence |
| pJqDBkVx | Smart Liquidity Trend Engine V9 | Liquidity, Trend | Liquidity + trend engine |
| qfc4Ts7L | Alfred Master Indicator | Multi | Master multi-factor |
| r8sDJypc | HTF Candles Vector Coloring PVSRA | HTF, PVSRA | PVSRA vector analysis |
| yRMDeG3C | TBM SMT Divergence Institutional | SMT, Divergence | SMT inter-market div |

### ICT / Smart Money Concepts (8)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| g0QS5WSP | CISD AND FVG | CISD, FVG | Change in State of Delivery |
| gwA0e7EY | Zuri FVG Imbalance Reaction Zones | FVG | FVG imbalance |
| l9ZBVMrP | Relevant Swings ICT Full Coverage | ICT Swings | Full ICT swing system |
| msC4APvA | HTF FVG BISI SIBI | FVG | Breaker blocks |
| oEpoSDyY | HEDGE FUND Liquidity Sniper | Liquidity | Liquidity hunting |
| pJqDBkVx | Smart Liquidity Trend Engine V9 | Smart Money | Smart money concept |
| qUOqtsZe | Big Order Gap Detector | Order Gap | Large order detection |
| zWN7yCHe | ICT Full Stack AMD Sweep CHoCH FVG | ICT Full Stack | AMD + Sweep + CHoCH + FVG |

### Candlestick / Pattern (4)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| g7XzbpVB | Marubozu Candlesticks | Marubozu | Full body candle detection |
| gfZEmKUh | Shaven Identifier | Shaven | No-wick candle ID |
| mlEmsUEk | Fibonacci Pinball Interactive | Fibonacci | Fib retracement patterns |
| ziDBibMI | Pin Bar Detector SSFX | Pin Bar | Pin bar detection |

### Session / Time-based (6)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| f2qqYN1c | Daily Trading Times UTC 2 | Time | Session time zones |
| h6pDtjUc | Daily Open 5-Min Range Box | Range Box | Opening range |
| jcdgMUUn | 4H Session Volume Profile | Volume Profile | Session-based VP |
| kO4uSQZU | Hourly Direction Change Open Rays | Hourly | Hourly direction change |
| s7I2QN8o | ORB Breakout Reset Alert | ORB | Opening range breakout |
| zeNNaF14 | ORB 6:30 Breakout Highlight | ORB | Time-specific breakout |

---

## ID-Only Scripts (27 - no descriptive name, skipped)
f8lJ6xr0, fHvBm6UW, ff7qSzca, gFDJ3T0g, gLqfgM60, gT6UWKv7, geMQrUra, hLWS8cHh, hWUajDEi, hlG9YfOd, hyonJDZ9, iM3LCAjq, iaDXfwDX, kI4eTeiM, kVGSxRE0, kdK4aRau, kg6eQuNf, kiBLyYBm, lBWgvwsb, lUs0AwDw, ljPGHpNG, llG7zzaP, mPR4WJca, mTbhftkB, ml7pRcD9, mpwbMiL9, nrXIYUc9

---

## Tool/Utility/Duplicate/Skip (13)
| ID | Name | Reason |
|----|------|--------|
| iQAERZXS | MyLibrary | Library, not strategy |
| jEDfYtbQ | Trading Plan Configurable | Tool (duplicate from batch_3) |
| jGqB9LOH | Execution Discipline | Trading tool |
| jaZexIkA | Padayappa | Named but unclear purpose |
| kdK4aRau | (ID-only) | Skipped |
| kgljaX7P | SRJ India VIX Widget | Region-specific (India) |
| kinWUvIY | Recent IPO VWAP 4yrs | IPO-specific tool |
| kNJ7lPxF | US Economic Dashboard III | Macro dashboard |
| mTkm5fVC | Descriptive Statistics Range | Statistical tool |
| nDZNU9WX | (ID-only) | Skipped |
| nrmMfmN4 | USDT MC Change | Crypto-specific |
| o0RPe8Jb | Bitcoin 1-Year Running ROI | Crypto-specific |
| qvoGOVnz | BTC Average Daily Returns by Day | Crypto-specific |

---

## Key Innovation Themes

### 1. Distance-Weighted Pressure Field (Algionics gidoT7f9) -- HIGHEST PRIORITY
- 28-line ribbon as physical force landscape
- Distance-weighted pressure ratio (not simple line count)
- Latch-based state engine at mathematical boundaries (0/50/100)
- All parameters derived from 2 root constants
- **A-stock value:** 5/5 - Directly implementable

### 2. Session-Indexed CVD Differential (keGsJUHD) -- HIGH PRIORITY
- Bar-for-bar yesterday vs today cumulative delta alignment
- ATR zone classification for pressure context
- Early detection of acceleration/fading before price shows it
- **A-stock value:** 4/5 - Need CVD proxy adaptation

### 3. Quad BB Multi-TF Fusion (jvHL2KvO) -- HIGH PRIORITY
- 4 BBs (EMA+WMA on High+Low) for squeeze detection
- Weekly priority logic (Mon/Tue bias)
- Decision table with reasoning chain
- **A-stock value:** 4/5 - BB squeeze universally applicable

### 4. Fractal Liquidity Map (oU4jOvjQ JOAT) -- HIGHEST PRIORITY
- 6-layer zero-overlap visual system
- Clean-redraw architecture (delete+recreate vs accumulate)
- Sweep detection at pool levels
- Fractal convergence within ATR = cluster zones
- **A-stock value:** 5/5 - Market-agnostic liquidity mapping

---

## Convertibility Assessment

| Strategy | A-stock Fit | Complexity | Key Blocker |
|----------|------------|------------|-------------|
| Algionics Ribbon Pressure | 5/5 | High | None - pure OHLC |
| JOAT Fractal Liquidity Map | 5/5 | High | None - pure OHLC |
| Cumulative Applied Force | 4/5 | Medium | Need CVD proxy |
| 4BB Quad Fusion | 4/5 | Medium | None - standard indicators |
| Dual Hull Cross Suite | 3/5 | Low | None - standard MA |
| Cost Basis Cipher | 2/5 | Medium | Crypto on-chain data |

---

## Batch 5+6 Combined Notes

Batch 6 (124 scripts, o-z prefix) was also read and analyzed. Key deep-analyzed entry from batch_6:

**JOAT Fractal Liquidity Map** (oU4jOvjQ) - analyzed above as entry #6. This is the same JOAT author from batch_3_new, continuing their series of high-quality institutional analysis tools.

---

## Cumulative Statistics (All Batches)
| Batch | Total | Deep | Classified | Skipped |
|-------|-------|------|------------|---------|
| batch_1 | 98 | 47 | 29 | 21 |
| batch_2 | 38 | 38 | 0 | 0 |
| batch_3 | 35 | 35 | 0 | 0 |
| batch_3_new | 98 | 6 | 52 | 40 |
| batch_4 | 121 | 9 | 92 | 20 |
| batch_4_new | 101 | 9 | 69 | 23 |
| batch_5 | 121 | 5 | 76 | 40 |
| **Total** | **612** | **149** | **318** | **144** |
