# TradingView Batch 6 Learning Notes
# Source: batch_6.json (124 scripts, IDs o-z prefix range)
# Processed: 2026-04-19

## Statistics
| Category | Count |
|----------|-------|
| Total scripts | 124 |
| Deep analyzed (webReader) | 6 |
| Name-classified | 56 |
| ID-only (no name) | 29 |
| Tool/utility/duplicate/skip | 33 |

---

## Deep-Analyzed Strategies (webReader verified)

### 1. Smart Liquidity & Trend Engine V9.0 (pJqDBkVx) - hammywong
**URL:** https://www.tradingview.com/script/pJqDBkVx-Smart-Liquidity-Trend-Engine-V9-0
**Category:** Liquidity / Multi-timeframe Fractal Clustering
**Rating:** 5/5 (A-stock)

**Core Logic:**
Weighted Multi-Timeframe Fractal Clustering Algorithm for dynamic liquidity zone detection. Scans fractals simultaneously on LTF (weight=1) and HTF (weight=3). When multiple fractals form within ATR-defined proximity, they merge into a single "Liquidity Zone" with strength scoring Lv.1 to Lv.5. HTF fractals (3 pts) instantly validate a zone; 3 LTF fractals (1+1+1) also validate. Zone invalidation: candle closes beyond zone boundary = "Ghost" zone, stops participating in signals. Two-stage signal execution: "TAP" (price wicks into zone, preparation only) then "Diamond" (requires proximity + momentum displacement/engulfing + EMA200 slope trend alignment). V-Reversal override: counter-trend Diamond allowed at Lv.4+ zones.

**Key Innovation:**
- Weighted MTF fractal clustering (HTF fractal = 3x weight of LTF)
- ATR-based zone merging instead of fixed-pip clustering
- Strength scoring (Lv.1-5) with minimum validation threshold
- Ghost zone invalidation mechanism (closed-beyond = dead)
- Two-stage signal execution (TAP preparation -> Diamond execution)
- V-Reversal override at strong zones (counter-trend exception)
- Trend determined by EMA200 slope (rising/falling), not crossover

**Indicators:** Fractals (LTF + HTF), ATR, EMA(200), Candlestick Patterns (Engulfing, Displacement)
**A-stock Adaptability:** Very High. Pure OHLC + ATR. Fractal clustering concept is market-agnostic. ATR-based zone merging adapts to any volatility regime. Two-stage signal system (TAP then Diamond) is a rigorous entry framework. The weighted MTF approach can use A-share timeframes (15min/60min/Daily).

---

### 2. Institutional Pressure Oscillator [Quantum Algo] (uusIBLke) - Quantum-Algo
**URL:** https://www.tradingview.com/script/uusIBLke-Institutional-Pressure-Oscillator-Quantum-Algo
**Category:** Volume Analysis / Institutional Flow Detection
**Rating:** 5/5 (A-stock)

**Core Logic:**
Five-stage institutional pressure measurement:
1. Logarithmic Price Differential: log-returns between bars (price-scale invariant)
2. Adaptive Noise Gate: 30-bar rolling stdev of log-returns x Sensitivity parameter = dynamic threshold. Moves below threshold = zero pressure attribution
3. Participation Normalization: rolling average volume baseline, single-bar contribution capped at configurable multiple (Participation Cap). Prevents anomalous spikes from distorting
4. Directional Classification: bars passing noise gate get capped volume as + (up) or - (down)
5. Cumulative Pressure + Signal: classified pressure summed over accumulation window, divided by baseline, optionally smoothed. EMA trigger line + conviction histogram (oscillator minus trigger)

**Key Innovation:**
- Logarithmic normalization: same parameters work on any instrument/price level
- Adaptive noise gate filters low-conviction choppy bars
- Participation cap prevents flash crash / wash trade distortion
- Conviction histogram shows acceleration/deceleration of pressure
- Price-scale invariant by design (no manual adjustment needed)

**Indicators:** Volume, Log-returns, Rolling Stdev, EMA
**A-stock Adaptability:** Very High. The log-normalization makes it instrument-agnostic. The noise gate concept is especially valuable for A-shares which have price limits (10%/20%) creating choppy zones. Participation cap handles volume anomalies common in A-share early trading session. No tick/session dependency. All inputs are standard OHLCV.

---

### 3. SHK CCI+RSI Merged | HA Signal MA | Dual Divergence v6 (rnsaf4Tn) - Syed_Hussain_K
**URL:** https://www.tradingview.com/script/rnsaf4Tn-SHK-CCI-RSI-Merged-HA-Signal-MA-Dual-Divergence-v6
**Category:** Oscillator / Multi-indicator Fusion
**Rating:** 4/5 (A-stock)

**Core Logic:**
Fuses CCI and RSI into a single blended oscillator. RSI is first normalized onto CCI scale: RSI 50->0, RSI 70->+100, RSI 30->-100. Blended = (CCI + Normalized RSI) / 2. Two-line system: Line 1 = blended oscillator with dynamic 4-state coloring (strong/weak bull/bear based on position relative to Signal MA and zero line). Line 2 = Signal MA (EMA/SMA/WMA selectable) colored by Heikin Ashi candle direction. Dual divergence engine: CCI+RSI blended divergence (solid lines) and RSI-only divergence (dashed lines), running simultaneously with independent lookback and threshold tuning.

**Key Innovation:**
- RSI normalization onto CCI scale creates unified overbought/oversold zones
- 4-state coloring: (above/below MA) x (above/below zero) = strong/weak bull/bear
- Signal MA colored by Heikin Ashi direction (early trend change warning before price confirms)
- Dual independent divergence engines (blended vs RSI-only)
- 14 built-in alert conditions covering all signal states

**Indicators:** CCI, RSI, Heikin Ashi, EMA/SMA/WMA
**A-stock Adaptability:** High. Standard indicators only. The RSI-onto-CCI normalization is a clean mathematical technique applicable anywhere. HA-colored MA provides early warning without requiring tick data. Dual divergence engine is universally valuable.

---

### 4. Daily Deviation Range and Gap Stats - NikaQuant (xv3h3KJE) - NikaQuant
**URL:** https://www.tradingview.com/script/xv3h3KJE-Daily-Deviation-Range-and-Gap-Stats-NikaQuant
**Category:** Statistical Range Analysis / Gap Tracking
**Rating:** 4/5 (A-stock)

**Core Logic:**
Three integrated modules:
1. Session Range Deviation: Captures H/L of 5-min closes during configurable time window. Once locked, projects 6 deviation level pairs at Fibonacci-style multiples (1, 2.5, 5, 8, 13, 19x range) above and below
2. Gap Tracker: Captures gap line at configurable time (5-min bar close). Monitors for fill during next session's window. Locks at fill bar
3. Historical Statistics Engine: Rolling per-level touch frequency, mean-revert frequency, close-inside frequency, gap fill rate, fill-time distribution. Generates context-aware trade-setup suggestions with stop/target based on historical probability

Strict 5-minute internal data resolution regardless of chart timeframe. Dual-path data fetch adapts to chart TF. Time-remaining guard suppresses late-session setups.

**Key Innovation:**
- Session-range deviation framework (not rolling ATR-based) anchored to user-defined window
- 6 Fibonacci-style deviation multiples (1, 2.5, 5, 8, 13, 19)
- Integrated gap tracker with fill-time distribution statistics
- Per-level historical probability engine with trade suggestions
- Time-remaining guard for late-session suppression
- Strict 5-min internal resolution across all chart timeframes

**Indicators:** Session H/L, Gap Price, Rolling Statistics
**A-stock Adaptability:** High. The concept maps directly to A-share opening range (9:30-10:00). Gap statistics are highly relevant for A-shares (overnight gap fill is a well-known pattern). Deviation multiples from session range can replace ATR-based targets. Statistics engine needs A-share session time adaptation. The 5-min internal resolution matches A-share standard bar size.

---

### 5. Regression-Aligned Candlestick Architect [MarkitTick] (y2960js2) - MarkitTick
**URL:** https://www.tradingview.com/script/y2960js2-Regression-Aligned-Candlestick-Architect-MarkitTick
**Category:** Candlestick Pattern Recognition / Statistical Channel
**Rating:** 4/5 (A-stock)

**Core Logic:**
Fuses three engines:
1. CHoCH Detection: Pivot-based change of character detection (customizable lookback). When price closes beyond opposing pivot, CHoCH registered
2. Anchored Linear Regression Channel (LRC): Resets and re-anchors at each CHoCH point. OLS-derived regression line + 2 standard deviation bands. Historical channels preserved
3. Candlestick Pattern Recognition with Strength Tiers: Each candle deconstructed into body size, range, shadow ratios. Rigid tolerance thresholds (Doji = body/range < 5%). 5-tier strength classification:
   - S1 Indecision (Doji, Spinning Top)
   - S2 Weak (Hanging Man, Inverted Hammer)
   - S3 Moderate (Harami, Piercing Line, Dark Cloud)
   - S4 Strong (Engulfing, Morning/Evening Star, Marubozu)
   - S5 Extreme (Three White Soldiers, Breakaway Gap)
Patterns filtered by SMA trend alignment. Webhook templates for automation.

**Key Innovation:**
- CHoCH-anchored LRC that resets on structural breaks
- 5-tier quantitative candlestick strength matrix
- Pattern-SMA trend alignment filter (removes counter-trend noise)
- OLS regression with population stdev bands (68%/95% containment)
- Quantitative candlestick deconstruction (body/range ratios replace visual assessment)
- Historical LRC preservation for structural review

**Indicators:** Pivot Points, Linear Regression, SMA, Candlestick Patterns, ATR
**A-stock Adaptability:** High. All OHLC-based. CHoCH + anchored LRC is market-agnostic. Quantitative candlestick scoring removes subjective interpretation. The 5-tier strength system provides clear filter levels for A-share strategies.

---

### 6. TBM SMT Divergence Institutional (yRMDeG3C) - teodormv18
**URL:** https://www.tradingview.com/script/yRMDeG3C-TBM-SMT-Divergence-Institutional
**Category:** Inter-market Divergence
**Rating:** 2/5 (A-stock)

**Core Logic:**
Detects SMT (Smart Money Technique) Divergences between MNQ1! (micro Nasdaq futures) and MES1! (micro S&P futures). When one index makes a higher high while the other fails to confirm, it signals institutional divergence.

**Key Innovation:**
- Inter-market divergence detection between correlated instruments
- Specific to MNQ/MES pair

**Indicators:** Dual-instrument price comparison
**A-stock Adaptability:** Low. Hard-coded to US futures (MNQ1!/MES1!). The inter-market divergence concept is valid for A-shares (e.g., CSI300 vs CSI500 divergence) but requires complete rewrite of instrument references. Concept only.

---

## Name-Classified Strategies (by keyword matching)

### Trend Following (12)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| oC9m0JpD | Swing Fibonacci BigBeluga | Fibonacci, Swing | Swing fib levels |
| oFk7wbld | Gneus 3m HA HM Strategy TP Text | HA, HM | 3-min HA strategy |
| oJp0vm8c | Kure 909 Clarity | Clarity | Trend clarity |
| otXz09gY | Trinity Triple RMA | Triple RMA | Triple RMA system |
| pi85RVXh | AG Pro Session VWAP Reaction Engine | VWAP, Session | VWAP reaction engine |
| sK37XQpW | AG Pro Reference Price Operating Map | Reference Price | Price operating map |
| t09YjxPn | Master Options Swing Momentum Trend Filter | Swing, Momentum | Swing + trend filter |
| vBJN76eZ | PhantomFlow Trend Candles V2 | Trend Candles | Trend candle system |
| xCcNqktY | EMA Triple Cross Alert | EMA | Triple EMA cross |
| xLU11bGQ | RSI EMA Dot Long Below Short Above | RSI, EMA | RSI-EMA dot signals |
| zIMSRViX | trendshift | Trend | Trend shift detector |
| zrTDo2K2 | OneTrades Trend Dashboard | Trend | Multi-TF trend board |

### Momentum / Oscillator (6)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| oPZA3pgr | Xiznit Scalper | Scalper | Scalping system |
| qUgTfgpK | M15 Scalp V1 | Scalper | 15-min scalping |
| rnsaf4Tn | SHK CCI RSI Merged HA Signal MA Dual Div v6 | CCI, RSI, HA | **DEEP analyzed** |
| uvZ46BZ2 | Momentum Strategy Public | Momentum | Momentum strategy |
| vhhq6ETk | RSIOMA v3 | RSI, MA | RSI of MA hybrid |
| zCEZ1mUT | BUZAIN GOLD SCALPER | Gold, Scalper | Gold-specific scalper |

### Volatility / Envelope (5)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| u17uwQql | Dual Structure BB Ribbon HIGH LOW 20 2 | Bollinger Bands | Dual BB ribbon |
| uCwVfcbY | Volume Band Asymmetric Dynamic Volatility Envelopes | Volume, Volatility | Asymmetric vol envelopes |
| twXzXevr | ATR Multiplier Table With Label | ATR | ATR multiplier display |
| zNPRdAiF | Iterative Locally Periodic Envelope | Envelope | Statistical envelope |
| zgT5XBsS | DXY vs GOLD Equilibrium Oscillator | DXY, Gold | Cross-asset oscillator |

### Order Flow / Volume (8)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| oEpoSDyY | HEDGE FUND Liquidity Sniper | Liquidity | Liquidity hunting |
| oStJQWHN | Absorption Overlay | Absorption | Order absorption |
| pfbNpPsQ | KalmanEngineLib | Kalman Filter | Kalman filter library |
| qUOqtsZe | Big Order Gap Detector | Order Gap | Large order detection |
| qn9EkFgv | Relative Volume at Time customised | RelVol | Time-based rel vol |
| uusIBLke | Institutional Pressure Oscillator Quantum Algo | Volume, Log-returns | **DEEP analyzed** |
| vRoVkK4o | ZT Real-Time Volume Multi-Timeframe | Volume | MTF real-time vol |
| xOekDucq | Custom Volume by Spicy | Volume | Custom volume |
| xq8codji | Cumulative Delta Line | Delta | Cumulative delta |

### Support/Resistance / Levels (10)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| qFpxiyof | VALOR SESSIONS KEY LEVELS | Session, Levels | Session key levels |
| qNRMNTSn | v18 Inside Outside Bar Levels | Inside/Outside Bar | IOB level system |
| qdRebFU0 | No Wick Open Highlighter Repairs | No Wick | No-wick open detection |
| rq4nqDX4 | Next Open Close Marker | Open/Close | Open/close marker |
| sPXYNzzD | Dae Levels | Levels | Custom level system |
| vBN62Clh | Key Levels Open Premarket Yesterday | Key Levels | Premarket levels |
| wGy6HpZd | Clean Key Levels Map | Key Levels | Clean level map |
| y958MLtN | Intraday Key Levels | Key Levels | Intraday levels |
| yLnxq7mp | RF Daily Levels | Daily Levels | Daily level system |
| zZKMZCxc | Nilesh HL Lines | H/L Lines | High/Low lines |
| zX8AIPME | Yesterday's OCHL Session relative JH | OCHL | Yesterday's OHLC |

### Multi-factor (5)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| ocGCsTyY | ORB VWAP RSI Signals | ORB, VWAP, RSI | Triple confluence |
| pJqDBkVx | Smart Liquidity Trend Engine V9 | Liquidity, Fractal, ATR | **DEEP analyzed** |
| qfc4Ts7L | Alfred Master Indicator | Multi | Master multi-factor |
| r8sDJypc | HTF Candles Vector Coloring PVSRA | HTF, PVSRA | PVSRA vector analysis |
| y2960js2 | Regression Aligned Candlestick Architect MarkitTick | CHoCH, LRC, Candlestick | **DEEP analyzed** |

### ICT / Smart Money Concepts (4)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| oEpoSDyY | HEDGE FUND Liquidity Sniper | Liquidity | Liquidity hunting |
| pJqDBkVx | Smart Liquidity Trend Engine V9 | Smart Money | SMC + fractal clustering |
| q58ifTtW | ICT Session Candle Counter | ICT, Session | ICT session tool |
| zWN7yCHe | ICT Full Stack AMD Sweep CHoCH FVG Confirmed | ICT Full Stack | AMD+Sweep+CHoCH+FVG |

### Session / Time-based (6)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| rA1w96HK | Wednesday open close | Time | Wed open/close |
| s7I2QN8o | ORB Breakout Reset Alert 9 30 10 00 ET | ORB | Opening range breakout |
| sOn26gCk | Futures Daily Pivot Zones | Pivots | Futures daily pivots |
| smPYGxQ6 | CTZ Session Guide Beginner Friendly | Session | Session guide |
| ykUgpDy8 | Session Highs Lows london asia | Session | London/Asia levels |
| zeNNaF14 | ORB 6 30 Breakout Highlight | ORB | Time-specific breakout |
| zHx2tA1f | Piku 15m 4H Range 12 am NY Candle | Range | Time-range system |

### Candlestick / Pattern (3)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| qar313Qr | PURECELL DBZENO | Pattern | Pattern system |
| ziDBibMI | Pin Bar Detector SSFX | Pin Bar | Pin bar detection |
| rMIEPfOo | ZigzagkillerV2 | Zigzag | Zigzag-based pattern |

### Statistical / Quantitative (3)
| ID | Name | Key Indicators | Notes |
|----|------|---------------|-------|
| rGJ2Esgc | Annual Return V6 | Return | Annual return calc |
| srpcnkGT | Kelly Criterion Curve | Kelly | Position sizing |
| xv3h3KJE | Daily Deviation Range and Gap Stats NikaQuant | Deviation, Gap, Stats | **DEEP analyzed** |

---

## ID-Only Scripts (29 - no descriptive name, skipped)
o8dmBLcv, oPYJ7RpJ, pOecPGQm, pXOvCfBU, q8eZ6kK4, qOOuJvFp, qXqxbdam, qZVzyaxP, qcnxjwRQ, qetKgBK2, qmuk6WNR, r02iwvuJ, slaJ8Qzu, tJKXei0R, taQw02pe, tqziIXDl, u2yUlEyn, u5LslSAD, uN9qxjGi, uZBvQM2E, usaC0pkN, vZR43Z0o, w6ZZzhwp, wqLijNbF, wsDJSqy7, x1FDCCNw, x8rkJOjn, xKnoLvKT, xwCTOKJt, ywQ1rNVC, yzRsHEYb, zOmdPyCV, zjQbWcTj

---

## Tool/Utility/Duplicate/Skip (33)
| ID | Name | Reason |
|----|------|--------|
| ooqcJajL | lesh ghoti april | Named but unclear purpose |
| ppEwWYS5 | Buy Sell signals | Too generic |
| ponegJHM | Koda 30 Stop Overlay | Stop management tool |
| qOG3HIxG | Bitcoin Production Cost KenshinC | Crypto fundamental |
| qmkPgplE | Seasons percentage KenshinC | Seasonal stats tool |
| qvoGOVnz | BTC Average Daily Returns by Day | Crypto-specific |
| rSrj5GG3 | SHK 3 MA EMA WMA VWAP Triangle Cross | MA cross variant |
| sNA3wTTg | MTF Candle Bias Table | Dashboard tool |
| sa6WEM84 | Peer Relative Breakdown Strategy | Relative analysis |
| siAWIOA2 | Quad Triple EMA Trend Bands | EMA bands (in batch_5) |
| sluD2VpY | Descriptive Statistics Variance | Statistical tool |
| suBe4kGp | Clock | Clock widget |
| tfA1MYS1 | Custom 4 MA Probability KenshinC English | MA probability tool |
| trJpyFCU | Watermark | Watermark utility |
| u5PorsIZ | Universal ATR Position Sizer Volatility Context | Position sizer (batch_3 dup) |
| unKw2grX | The Octopus Pullback Long Entry EMA MACD | EMA+MACD pullback |
| vMov3pbZ | Splinxzzz NQ MNQ Zones 1M | NQ-specific zones |
| vOCtLsjp | MTF Quadrant Previous Anchor Volume Profile | Volume profile tool |
| vTM0VOeb | MFB Footprints | Footprint tool |
| vW4dwXyF | NQ 5m Alert Framework Dashboard Trade Levels | NQ-specific alerts |
| w1N7UGfk | Bull Monsters Crypto Toolkit | Crypto-specific |
| w8Sxspz1 | Stage2 Pro by Ketan | Duplicate (in batch_5) |
| wRwGJHMg | EMA 9 20 Yellow Signal with Price | Basic EMA signal |
| xOekDucq | Custom Volume by Spicy | Volume display |
| yRMDeG3C | TBM SMT Divergence Institutional | **DEEP analyzed** (US futures only) |
| zLcvM9ly | Fast MA Pullback Alarm for TST Trender | MA pullback alert |
| zOtCgk90 | Sathish SMA Ribbon 5-10-20-50-100-150-200 | SMA ribbon (in batch_5) |
| zyMJz4UA | US Elections Forward Returns and Market Cycles | US politics-specific |

---

## Key Innovation Themes

### 1. Weighted MTF Fractal Clustering (pJqDBkVx) -- HIGHEST PRIORITY
- HTF fractals weighted 3x vs LTF
- ATR-based zone merging (not fixed-pip)
- Strength scoring with Ghost invalidation
- Two-stage signal: TAP (preparation) -> Diamond (execution)
- **A-stock value:** 5/5 - Directly implementable with OHLC + ATR

### 2. Log-Normalized Institutional Pressure (uusIBLke) -- HIGHEST PRIORITY
- Log-returns for price-scale invariance
- Adaptive noise gate filters choppy bars
- Participation cap prevents anomalous spike distortion
- Conviction histogram shows pressure momentum
- **A-stock value:** 5/5 - Universal volume pressure system

### 3. Session Range Deviation + Gap Stats (xv3h3KJE) -- HIGH PRIORITY
- Session-range-anchored deviation levels (not rolling ATR)
- Fibonacci-style multiples (1, 2.5, 5, 8, 13, 19)
- Integrated gap tracker with fill statistics
- Per-level historical probability engine
- **A-stock value:** 4/5 - Maps to A-share opening range perfectly

### 4. CHoCH-Anchored Regression + Candlestick Strength (y2960js2) -- HIGH PRIORITY
- LRC resets on structural breaks (CHoCH)
- 5-tier quantitative candlestick strength matrix
- OLS regression with stdev bands
- **A-stock value:** 4/5 - Market-agnostic statistical approach

### 5. CCI+RSI Fusion with HA-Colored MA (rnsaf4Tn) -- MEDIUM PRIORITY
- RSI normalized onto CCI scale
- 4-state signal coloring
- Dual independent divergence engines
- **A-stock value:** 4/5 - Clean oscillator fusion technique

---

## Convertibility Assessment

| Strategy | A-stock Fit | Complexity | Key Blocker |
|----------|------------|------------|-------------|
| Smart Liquidity Trend Engine V9 | 5/5 | High | None - pure OHLC+ATR |
| Institutional Pressure Oscillator | 5/5 | Medium | None - standard OHLCV |
| Daily Deviation Range + Gap Stats | 4/5 | Medium | Need A-share session times |
| Regression Candlestick Architect | 4/5 | High | None - pure OHLC |
| SHK CCI+RSI Merged | 4/5 | Low | None - standard indicators |
| TBM SMT Divergence | 2/5 | Low | US futures hard-coded |

---

## Cross-Batch Pattern Analysis

### Recurring High-Value Patterns (Seen Across Multiple Batches)
1. **ATR-based zone clustering** (batch_3, 4, 5, 6) - Confirmed as dominant pattern
2. **Fractal + liquidity zone systems** (batch_3, 5, 6) - Multiple independent implementations
3. **Log-normalized volume pressure** (batch_6 uusIBLke) - Novel technique not seen before
4. **Session-range-anchored deviation** (batch_6 xv3h3KJE) - Superior to rolling ATR approaches
5. **CHoCH-anchored regression channels** (batch_6 y2960js2) - Structural break detection

### Author Ecosystem Notes
- **JOAT** (officialjackofalltrades): Fractal Liquidity Map (batch_6 oU4jOvjQ, also in batch_3_new) - consistently high quality
- **Quantum Algo**: Institutional Pressure Oscillator - professional-grade with clean architecture
- **NikaQuant**: Deviation Range + Gap Stats - rigorous statistical approach with probability engine
- **MarkitTick**: Regression Candlestick Architect - quantitative candlestick analysis
- **AGPro Series**: Multiple session/VWAP tools (pi85RVXh, sK37XQpW) - session analysis suite

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
| batch_6 | 124 | 6 | 56 | 62 |
| **Total** | **736** | **155** | **374** | **206** |
