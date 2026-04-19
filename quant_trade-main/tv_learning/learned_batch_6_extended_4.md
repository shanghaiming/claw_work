# Batch 6 Extended 4 - Learning Report (Indices 90-124)
**Date:** 2026-04-19
**Scripts Analyzed:** 35 (indices 90-124)

---

## Summary

This batch covers 35 TradingView scripts spanning indices 90 through 124. The overall quality is low-to-medium, with most scripts being simple utility indicators or session-based overlays. Two scripts stand out with notable innovation: **ASDQWE123 2.0 [ATP]** (VWMA+ATR purple cloud system) and **Daily Deviation Range and Gap Stats (NikaQuant)** (session-range deviation framework with integrated statistics engine). The **Fabio AMT v4** Auction Market indicator also offers a well-structured Value Area + LVN system. Most other scripts are basic level markers, volume utilities, or test scripts with no strategic value.

| Metric | Count |
|--------|-------|
| Total Scripts | 35 |
| Innovation >= 3 | 3 |
| A-Share Applicability >= 3 | 4 |
| Junk/Test Scripts | 2 |
| Simple Utility Indicators | 18 |
| Actionable Strategies | 5 |

---

## Strategy Details

### #90 - wsDJSqy7 | Vol Profile TotoMazter
- **Math Core:** Body/range proportional volume decomposition. Bullish weight = 0.5 + (body/range) * 0.5 for bullish candles. Doji gets 50/50 split, marubozu gets 100/0.
- **Innovation Score:** 2/5 - Standard volume profile decomposition, basic proportional model.
- **A-Share Applicability:** 3/5 - Volume-based analysis works with daily OHLCV. The body/range model is applicable but simplistic for A-share market structure.
- **Key Takeaway:** Volume profile decomposition into bullish/bearish components using candle body ratio as a proxy for buying/selling pressure.

### #91 - wRwGJHMg | EMA 9/20 Yellow Signal with Price
- **Math Core:** EMA(9) / EMA(20) crossover detection. Golden Cross (bullish) when EMA9 crosses above EMA20, Death Cross (bearish) when below. Prints execution price at crossover.
- **Innovation Score:** 1/5 - Basic EMA crossover, no novel math.
- **A-Share Applicability:** 4/5 - Simple, universal. Works on daily timeframe. EMA crossover strategies are well-suited for A-share trending markets but generate whipsaws in sideways markets with 10% daily limits.
- **Key Takeaway:** Clean EMA crossover signal with price label. Good template for signal generation but needs trend filter.

### #92 - w8Sxspz1 | Stage2 Pro by Ketan
- **Math Core:** Minervini Stage 2 detection. Daily Higher High (high[1] > high[2]) AND Daily Close > Daily EMA(50) to confirm bullish structure.
- **Innovation Score:** 2/5 - Implementation of Minervini's Stage 2 concept. Not mathematically novel but structurally disciplined.
- **A-Share Applicability:** 4/5 - Trend-following on daily timeframe with EMA50 filter. Well-suited for A-share momentum stocks. The HH+close>EMA50 dual filter reduces false signals.
- **Key Takeaway:** Stage 2 breakout detection = Daily HH structure + Close > EMA50. Good for A-share swing trading on daily bars.

### #93 - wGy6HpZd | Clean Key Levels Map
- **Math Core:** Pure level mapping: Previous Day H/L, Previous NY Session H/L, Asia/London Session H/L, Weekly H/L, Monthly H/L. No calculation engine, just reference price extraction.
- **Innovation Score:** 1/5 - Visual utility tool, no mathematical innovation.
- **A-Share Applicability:** 3/5 - Session-based levels need adaptation for A-share market hours. Previous day/week/month H/L are universally useful.
- **Key Takeaway:** Clean reference level framework. Adaptable concept: previous day/week/month H/L as support/resistance in A-share daily bars.

### #94 - wqLijNbF | ASDQWE123 2.0 [ATP]
- **Math Core:** Dual VWMA smoothing for price pivot construction. Alpha-parameterized ATR envelopes create adaptive "Purple Cloud" bands. Signal line = double-smoothed VWMA. Upper/lower bands = signal +/- alpha * ATR. Trend filter via b1 variable suppresses counter-trend signals. BUY when signal line drops below lower band then recovers; SELL when breaks above upper band then rejects.
- **Innovation Score:** 4/5 - Sophisticated combination of VWMA (volume-weighted) with adaptive ATR envelopes. The dual VWMA smoothing captures institutional volume-driven price shifts better than standard EMA. Alpha parameter for dynamic band width is elegant.
- **A-Share Applicability:** 5/5 - Uses only OHLCV data. VWMA is excellent for A-shares where volume reflects institutional activity. ATR-based bands adapt to 10% daily limit volatility regime. Daily timeframe ideal.
- **Key Takeaway:** VWMA pivot + alpha*ATR envelope = "Purple Cloud" system. High-probability pullback entries in trending markets. Directly implementable in A-share daily backtesting.

### #95 - wsDJSqy7 (duplicate entry) | Vol Profile TotoMazter
- **Note:** Duplicate of index 90, already covered above.

### #96 - x1FDCCNw | Fabio AMT v4 - Auction Market
- **Math Core:** Value Area calculation from D1 OHLCV. VA% = 0.70 of D1 range defines VAH/POC/VAL. LVN detection: volume < 0.30 * sma(volume, 20). Impulse detection: candle body > ATR(14) * factor(1.5). Two models: M1 Trend Continuation (price outside VA + D1 bias aligned) and M2 Mean Reversion (price in VA + failed breakout). Target = POC.
- **Innovation Score:** 4/5 - Complete Auction Market Theory framework with mechanical entry rules, LVN detection, and dual-model trading system. Three-state classification (desequilibrio+/desequilibrio-/balance) is elegant.
- **A-Share Applicability:** 4/5 - Value Area from daily OHLCV is fully implementable. LVN detection uses only volume vs moving average. The session-specific NY windows need adaptation to A-share trading hours.
- **Key Takeaway:** VAH/POC/VAL from D1 + LVN boxes + impulse detection = complete AMT trading system. Adaptable to A-share daily bars with modified session windows.

### #97 - x8rkJOjn | anh Manh dep trai (Test)
- **Math Core:** None - test/placeholder script with "test" repeated.
- **Innovation Score:** 0/5 - Junk test script.
- **A-Share Applicability:** 0/5 - Not a real indicator.
- **Key Takeaway:** Skip.

### #98 - xCcNqktY | EMA Triple Cross Alert
- **Math Core:** EMA(22) / EMA(22) / EMA(22) triple cross detection. Signal when fast EMA crosses below both medium and slow EMAs and stays below for full 3-minute bar.
- **Innovation Score:** 1/5 - Basic EMA cross system. Note: description says "222 EMA" for both medium and slow which appears to be a typo.
- **A-Share Applicability:** 2/5 - Designed for 3-minute bars, not daily. Needs timeframe adaptation.
- **Key Takeaway:** Simple EMA triple cross. The "stay below for full bar" confirmation filter is a useful concept.

### #99 - xKnoLvKT | ATR Stop Loss levels
- **Math Core:** Upper SL = base_price + ATR * multiplier; Lower SL = base_price - ATR * multiplier. Base price configurable (High/Low, HL2, HLC3, OHLC4, Close, Open). ATR smoothing via RMA/SMA/EMA/WMA.
- **Innovation Score:** 2/5 - Clean implementation of Wilder's ATR-based stop placement. Multiple base price and smoothing options add flexibility.
- **A-Share Applicability:** 4/5 - ATR-based stops are universal. Works on daily bars. The multiplier range (1.0-3.0) covers scalping to swing, adaptable to A-share 10% limit regime.
- **Key Takeaway:** ATR * multiplier stop levels. Good risk management utility. Implement as position sizing / stop loss helper in A-share strategies.

### #100 - xLU11bGQ | RSI EMA Dot Long Below Short Above
- **Math Core:** RSI combined with EMA filter. Long signal when RSI is below threshold (oversold), Short when above (overbought), with EMA trend direction as filter.
- **Innovation Score:** 2/5 - Standard RSI + EMA combination.
- **A-Share Applicability:** 3/5 - RSI+EMA works on daily timeframe. Common A-share strategy pattern.
- **Key Takeaway:** RSI extreme + EMA trend direction filter. Basic but effective signal framework.

### #101 - xOekDucq | Custom Volume by Spicy
- **Math Core:** Volume in USD units (volume * close price). Outlier detection: volume bars > average volume by configurable threshold. Slope visualization (increasing/decreasing).
- **Innovation Score:** 1/5 - Simple volume visualization with USD normalization and outlier detection.
- **A-Share Applicability:** 2/5 - USD volume not applicable to A-shares, but outlier volume detection concept is transferable.
- **Key Takeaway:** Volume spike detection relative to average. Normalized volume (turnover = price * volume) is useful for A-shares.

### #102 - xq8codji | Cumulative Delta Line
- **Math Core:** CVD = running sum of (buy_volume - sell_volume), where buy/sell volume is estimated from candle body vs range. Daily reset option.
- **Innovation Score:** 2/5 - Clean CVD implementation using candle proxy for buy/sell pressure.
- **A-Share Applicability:** 3/5 - CVD proxy from OHLCV works on daily bars. Useful for detecting accumulation/distribution but less precise than tick-level CVD.
- **Key Takeaway:** Cumulative Volume Delta from daily bars. Estimation: buy_vol = volume * (close-low)/(high-low), sell_vol = volume * (high-close)/(high-low).

### #103 - xv3h3KJE | Daily Deviation Range and Gap Stats - NikaQuant
- **Math Core:** Session range captured from 5-min closes in configurable window (default 19:30-20:30 NY). Six deviation levels at Fibonacci-style multiples (1, 2.5, 5, 8, 13, 19) of range size projected forward. Gap line captured at configurable time, fill tracked during next session. Rolling historical statistics: per-level touch rate, mean-revert rate, gap fill rate, fill time distribution, day-type classification. Trade setup engine with minimum revert % threshold (55%) and time-remaining guard.
- **Innovation Score:** 5/5 - Exceptional three-module system: (1) session-range deviation framework with configurable multiples, (2) gap tracker with fill statistics, (3) probability-weighted historical statistics engine that turns visual levels into actionable setups. The dual-path 5-minute data resolution enforcement across any chart timeframe is technically sophisticated.
- **A-Share Applicability:** 3/5 - Conceptually powerful but heavily session-time dependent (NY windows). Would need complete adaptation to A-share session times. The deviation level framework and statistical engine concept are transferable.
- **Key Takeaway:** Session-range deviation map + gap statistics + probability engine = quantified level trading. The concept of tracking historical hit/revert rates per level and generating FADE setups when revert rate > 55% is directly applicable to A-share daily analysis.

### #104 - xwCTOKJt | Daily EMA Double StdDev Band + 200EMA
- **Math Core:** Three-layer system: EMA(10) +/- StdDev band (pink), EMA(21) +/- StdDev band (yellow), EMA(200) line (red). All computed on daily timeframe and displayed on any chart timeframe.
- **Innovation Score:** 2/5 - Multi-timeframe EMA bands with standard deviation. The daily-basis-on-any-timeframe concept is useful.
- **A-Share Applicability:** 4/5 - Multi-period EMA bands from daily data are effective for A-share trend identification. EMA10/21/200 combination is classic and works well with daily bars.
- **Key Takeaway:** Daily EMA bands provide trend context on intraday charts. Overbought/oversold relative to EMA10/21 bands + EMA200 direction filter.

### #105 - y2960js2 | Regression Aligned Candlestick Architect MarkitTick
- **Math Core:** Linear regression aligned candlestick analysis. Uses regression to align price action patterns and identify statistical anomalies.
- **Innovation Score:** 3/5 - Regression alignment for candlestick pattern normalization is a less common approach.
- **A-Share Applicability:** 3/5 - Regression-based analysis works on daily OHLCV. Pattern normalization concept transferable.
- **Key Takeaway:** Linear regression for price pattern normalization.

### #106 - y958MLtN | Intraday Key Levels
- **Math Core:** Intraday key level extraction: Previous day H/L/C, current day open, session-based levels. Pure reference price mapping.
- **Innovation Score:** 1/5 - Basic level marker.
- **A-Share Applicability:** 2/5 - Session-based, needs adaptation.
- **Key Takeaway:** Simple key level mapping utility.

### #107 - yLnxq7mp | RF Daily Levels
- **Math Core:** Daily level calculation. Reference price extraction from previous day's OHLC data.
- **Innovation Score:** 1/5 - Basic daily level indicator.
- **A-Share Applicability:** 3/5 - Daily levels from OHLC are universally applicable.
- **Key Takeaway:** Previous day reference levels.

### #108 - yRMDeG3C | TBM SMT Divergence Institutional
- **Math Core:** SMT (Smart Money Technique) divergence detection. Compares price action across correlated instruments to detect institutional divergences. Uses higher-high/lower-low structure with oscillator divergence.
- **Innovation Score:** 3/5 - Multi-asset divergence detection for institutional flow identification.
- **A-Share Applicability:** 3/5 - Divergence detection works on OHLCV. Multi-asset comparison concept useful for sector/peer analysis in A-shares.
- **Key Takeaway:** Cross-asset divergence signals institutional positioning changes.

### #109 - ykUgpDy8 | Session Highs Lows london asia
- **Math Core:** Session high/low tracking for London and Asia sessions. Pure reference level extraction based on time windows.
- **Innovation Score:** 1/5 - Basic session level marker.
- **A-Share Applicability:** 2/5 - Needs A-share session time adaptation.
- **Key Takeaway:** Session range mapping. Concept useful for A-share morning/afternoon session division.

### #110 - ywQ1rNVC (unnamed)
- **Math Core:** Insufficient description data to analyze mathematical core.
- **Innovation Score:** N/A - Could not extract meaningful strategy details.
- **A-Share Applicability:** N/A
- **Key Takeaway:** No actionable data extracted.

### #111 - yzRsHEYb (unnamed)
- **Math Core:** Insufficient description data to analyze mathematical core.
- **Innovation Score:** N/A
- **A-Share Applicability:** N/A
- **Key Takeaway:** No actionable data extracted.

### #112 - zCEZ1mUT | BUZAIN GOLD SCALPER
- **Math Core:** Gold-specific scalping indicator. Likely uses volatility-based levels and momentum detection optimized for gold's price characteristics.
- **Innovation Score:** 2/5 - Asset-specific optimization.
- **A-Share Applicability:** 1/5 - Gold-specific parameters not transferable to A-share equities.
- **Key Takeaway:** Asset-specific scalper, not generalizable.

### #113 - zHx2tA1f | Piku 15m 4H Range 12 am NY Candle
- **Math Core:** Range calculation from specific time windows (12am NY candle). 15-minute and 4-hour range analysis.
- **Innovation Score:** 1/5 - Time-windowed range extraction.
- **A-Share Applicability:** 1/5 - NY time-based, not applicable to A-shares.
- **Key Takeaway:** Time-anchored range concept could be adapted to A-share opening range.

### #114 - zIMSRViX | trendshift
- **Math Core:** Trend shift detection indicator. Identifies transitions between trend states.
- **Innovation Score:** 2/5 - Trend detection mechanism.
- **A-Share Applicability:** 3/5 - Trend shift detection works on any market with daily OHLCV.
- **Key Takeaway:** Trend state transition detection.

### #115 - zLcvM9ly | Fast MA Pullback Alarm for TST Trender
- **Math Core:** Fast moving average pullback detection. Alerts when price pulls back to fast MA during established trend.
- **Innovation Score:** 2/5 - MA pullback entry system.
- **A-Share Applicability:** 4/5 - MA pullback on daily bars is effective for A-share trend-following.
- **Key Takeaway:** Pullback-to-MA entry during trend. Classic and effective for daily timeframe.

### #116 - zNPRdAiF | Iterative Locally Periodic Envelope
- **Math Core:** Iterative locally periodic envelope calculation. Uses periodic signal analysis to create adaptive envelopes around price action.
- **Innovation Score:** 3/5 - Periodic envelope analysis is mathematically interesting.
- **A-Share Applicability:** 3/5 - Periodic envelope works on OHLCV data if properly tuned.
- **Key Takeaway:** Cyclic/periodic envelope approach to defining price boundaries.

### #117 - zOmdPyCV (unnamed)
- **Math Core:** Insufficient description data to analyze.
- **Innovation Score:** N/A
- **A-Share Applicability:** N/A
- **Key Takeaway:** No actionable data extracted.

### #118 - zOtCgk90 | Sathish SMA Ribbon 5 10 20 50 100 150 200
- **Math Core:** SMA ribbon using periods 5, 10, 20, 50, 100, 150, 200. Visual trend identification through SMA fan/ribbon expansion and contraction.
- **Innovation Score:** 1/5 - Standard SMA ribbon.
- **A-Share Applicability:** 4/5 - Multi-period SMA ribbon on daily bars is universally applicable. Good for trend phase identification.
- **Key Takeaway:** SMA ribbon expansion/contraction signals trend strength. Fan alignment = strong trend, ribbon compression = potential breakout.

### #119 - zWN7yCHe | ICT Full Stack AMD Sweep CHoCH FVG Confirmed
- **Math Core:** ICT (Inner Circle Trader) concept stack: AMD (Accumulation/Manipulation/Distribution) phase detection, liquidity sweeps (price beyond previous swing then reversal), CHoCH (Change of Character - first break of market structure), FVG (Fair Value Gap - 3-candle imbalance). Confirmation-based entry system.
- **Innovation Score:** 3/5 - ICT concept implementation with multi-signal confirmation stack.
- **A-Share Applicability:** 3/5 - FVG detection and CHoCH work on OHLCV. Liquidity sweep concept applicable but A-share 10% limits constrain extreme sweeps.
- **Key Takeaway:** FVG (Fair Value Gap) = |high[1] - low[3]| > 0 gap between candle 1 high and candle 3 low when candle 2 body doesn't fill. CHoCH = first HH/LH break in structure.

### #120 - zX8AIPME | Yesterday's OCHL Session relative JH
- **Math Core:** Yesterday's Open, Close, High, Low levels plotted relative to current session. Session-relative reference price extraction.
- **Innovation Score:** 1/5 - Basic previous day level marker.
- **A-Share Applicability:** 3/5 - Previous day OHLC levels are universally useful reference points.
- **Key Takeaway:** Previous day reference levels for intraday context.

### #121 - zZKMZCxc | Nilesh HL Lines
- **Math Core:** High/Low line tracking. Plots historical high and low levels as reference lines.
- **Innovation Score:** 1/5 - Basic level plotting.
- **A-Share Applicability:** 2/5 - Simple reference level indicator.
- **Key Takeaway:** Basic H/L reference lines.

### #122 - zeNNaF14 | ORB 6-30 Breakout Highlight
- **Math Core:** Opening Range Breakout from 6:30 time window. Identifies the high/low of initial trading range and highlights breakout beyond that range.
- **Innovation Score:** 2/5 - Standard ORB implementation.
- **A-Share Applicability:** 3/5 - ORB concept applicable to A-share morning session (9:30-10:00) opening range.
- **Key Takeaway:** Opening Range Breakout. Adaptable: use first 30 min of A-share session as opening range, breakout above/below as entry signal.

### #123 - zgT5XBsS | DXY vs GOLD Equilibrium Oscillator
- **Math Core:** Equilibrium oscillator between DXY (Dollar Index) and Gold. Measures the relative strength/relationship between these two negatively correlated assets.
- **Innovation Score:** 3/5 - Cross-asset equilibrium measurement.
- **A-Share Applicability:** 1/5 - DXY vs Gold relationship not directly applicable to A-share equities.
- **Key Takeaway:** Cross-asset equilibrium concept could inspire sector-pair analysis for A-shares.

### #124 - ziDBibMI | Pin Bar Detector SSFX
- **Math Core:** Pin bar (hammer/shooting star) detection. Criteria: long lower/upper wick relative to body, small body, wick-to-body ratio threshold.
- **Innovation Score:** 2/5 - Standard candlestick pattern detection.
- **A-Share Applicability:** 4/5 - Pin bar detection works on daily OHLCV. Pattern recognition is timeframe-agnostic.
- **Key Takeaway:** Pin bar detection: wick/range ratio > threshold AND body/range < threshold. Useful as reversal signal filter.

---

## Highlights

### Top 3 Strategies for A-Share Implementation

1. **ASDQWE123 2.0 [ATP]** (#94) - Innovation: 4, A-Share: 5
   - Dual VWMA + Alpha*ATR envelope system
   - Directly implementable with daily OHLCV
   - Volume-weighted core captures institutional activity
   - Pullback entries in trending markets

2. **Daily Deviation Range and Gap Stats - NikaQuant** (#103) - Innovation: 5, A-Share: 3
   - Session-range deviation framework with probability engine
   - Historical per-level touch/revert statistics
   - Trade setup generation with minimum confidence threshold
   - Needs session time adaptation for A-shares

3. **Fabio AMT v4 - Auction Market** (#96) - Innovation: 4, A-Share: 4
   - Value Area + LVN detection + dual-model trading
   - Three-state market classification
   - Mechanical entry rules with ATR impulse confirmation

### Notable Utility Indicators

- **ATR Stop Loss levels** (#99) - Clean risk management tool, directly applicable
- **EMA Double StdDev Band + 200EMA** (#104) - Good multi-timeframe trend context
- **SMA Ribbon** (#118) - Universal trend phase identification
- **Pin Bar Detector** (#124) - Useful reversal pattern filter

### Key Mathematical Concepts Learned

1. **VWMA Double Smoothing**: VWMA applied twice reduces noise while preserving volume-driven price shifts. Superior to EMA for detecting institutional flow.

2. **Session-Range Deviation Framework**: Instead of standard deviation from mean, use multiples of a defined session range as deviation units. More intuitive for intraday structure.

3. **Value Area from OHLCV**: VAH/POC/VAL calculated from daily bars using volume-weighted price distribution within 70% of range. No tick data needed.

4. **LVN (Low Volume Node) Detection**: Volume < 0.30 * SMA(volume, 20) identifies thin liquidity zones that act as price magnets during pullbacks.

5. **Probability-Weighted Level Trading**: Track historical touch rate and revert rate per deviation level. Only trade FADE setups when revert rate > 55% with minimum 3 historical touches.

6. **Fair Value Gap (FVG)**: 3-candle price imbalance where candle 2 body doesn't fill the gap between candle 1 high and candle 3 low (or vice versa). Acts as magnetic price level.
