# TV Learning - Batch 4 New Extended 2 (Indices 60-100)
> Generated: 2026-04-19
> Scripts analyzed: 41 (indices 60 through 100)

---

## Summary

| # | Index | Name | Innovation | A-Share | Category |
|---|-------|------|:----------:|:-------:|----------|
| 1 | 60 | Session Strata Mapper JOAT | 3 | 2 | Session/Time |
| 2 | 61 | Market Structure Navigator JOAT | 3 | 3 | Structure |
| 3 | 62 | Metis Ladder Compression Engine v1.1 | 4 | 3 | Compression/Volatility |
| 4 | 63 | Volatility Terrain Engine JOAT | 4 | 3 | Volatility |
| 5 | 64 | BbtGQtya | 1 | 1 | Unknown |
| 6 | 65 | BdaYgaUE | 1 | 1 | Unknown |
| 7 | 66 | Ben James EMA21 Wick Sniper | 2 | 3 | EMA/Wick |
| 8 | 67 | Pullback Measured Move | 4 | 4 | Pullback/Price Target |
| 9 | 68 | HTF Level Prev M/W/D O/H/L | 2 | 3 | Multi-Timeframe Levels |
| 10 | 69 | XAUUSD Pro MTF Scalper | 2 | 2 | MTF Scalper |
| 11 | 70 | lib_pickmytrade | 1 | 1 | Utility Library |
| 12 | 71 | Pullback Marker Inside Bars | 3 | 3 | Pullback Detection |
| 13 | 72 | Order Flow Smart Footprint | 4 | 3 | Order Flow/Delta |
| 14 | 73 | AG Pro Value Shift Ladder | 3 | 3 | Value Area/Ladder |
| 15 | 74 | OR Nifty Regime | 3 | 2 | Opening Range/Regime |
| 16 | 75 | mtf trend cascade | 3 | 3 | Multi-Timeframe Trend |
| 17 | 76 | CIqpuXEC | 1 | 1 | Unknown |
| 18 | 77 | CMDiJjby | 1 | 1 | Unknown |
| 19 | 78 | RSI Div BROWNIETHERABBIT | 2 | 3 | RSI Divergence |
| 20 | 79 | Auto S/R MTF Bias | 3 | 4 | S/R + Multi-TF Bias |
| 21 | 80 | MES 5 Min ORB | 2 | 2 | Opening Range Breakout |
| 22 | 81 | Cc6q3BSU | 1 | 1 | Unknown |
| 23 | 82 | HA Straddle Strangle Signals v7 | 2 | 2 | Options/Heikin-Ashi |
| 24 | 83 | Abyan OB Wala | 2 | 3 | Order Block |
| 25 | 84 | HTF Fair Value Gaps Anchored | 3 | 3 | FVG/ICT |
| 26 | 85 | Flexible Moving Averages w/ MACD+RSI | 2 | 4 | MA/MACD/RSI Combo |
| 27 | 86 | Options Greeks Dashboard | 1 | 1 | Options Dashboard |
| 28 | 87 | MonsterBox Final Boss Scanner | 3 | 2 | Scanner/Multi-Signal |
| 29 | 88 | AG Pro Volatility Shape Classifier | 4 | 3 | Volatility Classification |
| 30 | 89 | Versatile Scalper | 2 | 3 | Scalper |
| 31 | 90 | H4 Abnormal Candle | 2 | 3 | Candle Anomaly |
| 32 | 91 | Minervini SEPA System | 4 | 4 | Trend/RS/Volume |
| 33 | 92 | Nexus Fusion Engine ML | 4 | 3 | ML/Fusion |
| 34 | 93 | AI Smart Assistant UI Toolkit | 1 | 1 | UI/Utility |
| 35 | 94 | 10 SMA 21 EMA Dotted | 1 | 3 | Simple MA Cross |
| 36 | 95 | Pivot High Low HH LL | 2 | 3 | Pivot/Structure |
| 37 | 96 | Custom Fractals | 2 | 3 | Fractal/Pattern |
| 38 | 97 | Trend Analysis Dashboard YPro | 2 | 3 | Trend Dashboard |
| 39 | 98 | DmBG9zK5 | 1 | 1 | Unknown |
| 40 | 99 | DrpqDrNv | 1 | 1 | Unknown |
| 41 | 100 | Swing to Swing Move Analyzer | 3 | 3 | Swing Analysis |

**Average Innovation**: 2.3 / 5
**Average A-Share Applicability**: 2.5 / 5

---

## Strategy Details

### #60 - Session Strata Mapper JOAT
- **URL**: https://www.tradingview.com/script/BMKydzAM-Session-Strata-Mapper-JOAT
- **Mathematical Core**: Time-based session mapping with strata decomposition across Asian, London, New York sessions. Maps price action into session layers (strata) to identify institutional activity windows.
- **Innovation**: 3/5 - Part of JOAT series; structured session decomposition is methodical but not mathematically novel.
- **A-Share Applicability**: 2/5 - Session-based approach targets forex/crypto 24h markets. A-shares have a single session with lunch break; limited applicability.
- **Key Concepts**: Session stratification, institutional time windows, killzone identification.

### #61 - Market Structure Navigator JOAT
- **URL**: https://www.tradingview.com/script/BU5FxNyR-Market-Structure-Navigator-JOAT
- **Mathematical Core**: Automated higher-high/higher-low and lower-high/lower-low detection using pivot-based algorithms. Maps market structure breaks (BOS) and change of character (CHoCH).
- **Innovation**: 3/5 - Solid implementation of smart money concepts; algorithmic BOS/CHoCH detection is well-executed.
- **A-Share Applicability**: 3/5 - Market structure concepts (HH/HL/LH/LL) are universal and applicable to A-shares with daily OHLCV.
- **Key Concepts**: Break of structure, change of character, swing point detection, trend phase identification.

### #62 - Metis Ladder Compression Engine v1.1
- **URL**: https://www.tradingview.com/script/BWBAoVET-Metis-Ladder-Compression-Engine-v1-1
- **Mathematical Core**: Price compression detection using a "ladder" algorithm that measures successive narrowing of price ranges across multiple periods. Compression ratio = min(range_n) / average(range_n) across a lookback window. Breakout signals generated when price escapes the compression zone.
- **Innovation**: 4/5 - Novel "ladder compression" concept measures volatility contraction systematically with a quantifiable ratio.
- **A-Share Applicability**: 3/5 - Volatility compression before breakout is relevant; A-share 10% limits may truncate some signals.
- **Key Concepts**: Volatility compression ratio, ladder pattern, breakout detection, range contraction.

### #63 - Volatility Terrain Engine JOAT
- **URL**: https://www.tradingview.com/script/BXtZu6Yf-Volatility-Terrain-Engine-JOAT
- **Mathematical Core**: Multi-dimensional volatility surface using ATR, Bollinger Band width, and Keltner Channel width combined into a composite "terrain" score. Maps volatility regimes as topographic features (peaks = high vol, valleys = low vol).
- **Innovation**: 4/5 - Creative topographic metaphor applied to volatility; composite volatility surface from multiple indicators.
- **A-Share Applicability**: 3/5 - Volatility regime identification works on any market. Daily OHLCV sufficient.
- **Key Concepts**: Composite volatility surface, regime mapping, ATR + BB + KC fusion, topographic volatility.

### #64 - BbtGQtya
- **URL**: https://www.tradingview.com/script/BbtGQtya
- **Mathematical Core**: [Fetch Failed] - Insufficient data to analyze.
- **Innovation**: 1/5 - Unable to assess.
- **A-Share Applicability**: 1/5 - Unable to assess.

### #65 - BdaYgaUE
- **URL**: https://www.tradingview.com/script/BdaYgaUE
- **Mathematical Core**: [Fetch Failed] - Insufficient data to analyze.
- **Innovation**: 1/5 - Unable to assess.
- **A-Share Applicability**: 1/5 - Unable to assess.

### #66 - Ben James EMA21 Wick Sniper
- **URL**: https://www.tradingview.com/script/Bg8VSKbP-Ben-James-EMA21-Wick-Sniper
- **Mathematical Core**: EMA(21) with wick rejection detection. Signal logic: when price creates a long wick piercing through EMA21 and closes back on the trend side, indicating a rejection. Uses wick-to-body ratio as a filter: wick_length / body_length > threshold.
- **Innovation**: 2/5 - Simple EMA wick rejection concept; commonly known technique with straightforward math.
- **A-Share Applicability**: 3/5 - EMA wick rejections work on daily bars. 10% limit may reduce extreme wick formations.
- **Key Concepts**: EMA21 dynamic S/R, wick rejection ratio, mean reversion at EMA.

### #67 - Pullback Measured Move
- **URL**: https://www.tradingview.com/script/BgCsV7WY-Pullback-Measured-Move
- **Mathematical Core**: Three-point swing structure (A-B-C pattern). Measures pullback range (B to C including wicks), then projects Target = B +/- (pullback_range x multiplier). Default multiplier = 2.0x, configurable to 1.0x (equal legs) or 1.618x (golden ratio). ATR-based minimum pullback filter: skip if |B-C| < min_fraction * ATR.
- **Innovation**: 4/5 - Clean mathematical framework for measured move projections with configurable multiplier and ATR noise filter. Practical and well-designed.
- **A-Share Applicability**: 4/5 - Swing structure + price target projection works perfectly on daily OHLCV. ATR filter handles 10% limit context.
- **Key Concepts**: A-B-C swing pattern, measured move projection (range x multiplier), ATR noise filter, golden ratio option.

### #68 - HTF Level: Prev M/W/D O/H/L + Current W/M Open + NY Open Level
- **URL**: https://www.tradingview.com/script/BhDJTHPd-HTF-Level-Prev-M-W-D-O-H-L-Current-W-M-Open-NY-Open-Level
- **Mathematical Core**: Anchored high-timeframe level extraction. Retrieves previous Monthly/Weekly/Daily Open, High, Low values and plots current Weekly/Monthly Open. Also plots NY Open (9:30 ET) level.
- **Innovation**: 2/5 - Standard HTF level plotting; well-organized but no mathematical innovation.
- **A-Share Applicability**: 3/5 - Previous M/W/D OHLC levels are relevant as support/resistance. NY Open less relevant for A-shares; replace with A-share market open.
- **Key Concepts**: HTF anchored levels, previous period OHLC, current period open, multi-timeframe reference.

### #69 - XAUUSD Pro MTF Scalper
- **URL**: https://www.tradingview.com/script/BiOXpp9i-XAUUSD-Pro
- **Mathematical Core**: Multi-timeframe scalping system combining: EMA(9/21/50/200) trend structure + RSI + MACD + Stochastic momentum filters + VWAP intraday positioning + ADX trend strength + ICT-inspired killzones. Signal requires alignment across 1m (execution), 5m (confirmation), 15m (bias).
- **Innovation**: 2/5 - Comprehensive multi-indicator MTF system, but combines well-known indicators without mathematical novelty.
- **A-Share Applicability**: 2/5 - Designed for XAUUSD scalping on 1m/5m. A-shares lack VWAP intraday data; 10% limits constrain scalping.
- **Key Concepts**: MTF alignment, EMA stack, momentum filter confluence, VWAP positioning, ICT killzones.

### #70 - lib_pickmytrade
- **URL**: https://www.tradingview.com/script/BnoJgkde-lib-pickmytrade
- **Mathematical Core**: Utility library for generating JSON webhook messages for the pickmytrade platform. Functions for entry (with 3 TP levels, partial quantities, SL), trail stop loss, and exit. Pure string formatting.
- **Innovation**: 1/5 - Not a trading strategy; a webhook utility library.
- **A-Share Applicability**: 1/5 - Platform-specific utility; no trading logic.
- **Key Concepts**: Webhook JSON formatting, multi-TP entry, trailing SL management.

### #71 - Pullback Marker Inside Bars Ignored by Shadow Quant Trader
- **URL**: https://www.tradingview.com/script/BqTdzk6y-Pullback-Marker-Inside-Bars-Ignored-by-Shadow-Quant-Trader
- **Mathematical Core**: Pullback detection algorithm that filters out inside bars (bars where H <= prev_H and L >= prev_L) to identify "true" pullback depth. Inside bars are treated as continuation/consolidation rather than directional movement. Pullback measured from swing extreme to deepest non-inside-bar low (or highest non-inside-bar high).
- **Innovation**: 3/5 - Smart filtering of inside bars to measure "true" pullback depth is a practical improvement over standard pullback measurement.
- **A-Share Applicability**: 3/5 - Inside bar filtering and pullback measurement work on daily OHLCV. Relevant in trending A-shares.
- **Key Concepts**: Inside bar filtering, true pullback depth, swing structure with consolidation removal.

### #72 - Order Flow Smart Footprint
- **URL**: https://www.tradingview.com/script/BrNW3Fku-Ninja-Trader-Order-Flow-Smart-Footprint
- **Mathematical Core**: Volume decomposition into buy/sell pressure per price level. Calculates: (1) Volume imbalance clusters using ratio threshold (buy_vol/sell_vol > ratio = bullish cluster); (2) Point of Control (POC) = price level with max volume; (3) Bar Delta = sum(market_buy_vol) - sum(market_sell_vol); (4) Panic zones where imbalance exceeds extreme threshold.
- **Innovation**: 4/5 - Thorough order flow footprint implementation with delta analysis, absorption detection, and panic zone identification.
- **A-Share Applicability**: 3/5 - Volume-based buy/sell decomposition works on A-share daily bars. Lacks tick-level data but daily volume delta approximation possible. 10% limits create interesting absorption patterns.
- **Key Concepts**: Volume imbalance ratio, POC, bar delta, absorption detection, panic buying/selling zones, smart money footprint.

### #73 - AG Pro Value Shift Ladder
- **URL**: https://www.tradingview.com/script/BxPKVrwy-AG-Pro-Value-Shift-Ladder-AGPro-Series
- **Mathematical Core**: Value area calculation (70% volume concentration zone) with ladder-style shift detection. Measures how the value area shifts between periods: value_area_shift = (current_VA_center - prev_VA_center) / ATR. Ladder formation = successive value area shifts in the same direction.
- **Innovation**: 3/5 - Value area shift tracking is a meaningful market structure concept; ladder formation is a clean organizational idea.
- **A-Share Applicability**: 3/5 - Value area concepts applicable to A-shares using daily volume profiles. Shift direction indicates institutional bias.
- **Key Concepts**: Value area calculation, value area shift ratio, ladder formation, institutional positioning.

### #74 - OR Nifty Regime
- **URL**: https://www.tradingview.com/script/C41wbFfJ-OR-Nifty-Regime
- **Mathematical Core**: Opening Range breakout system for Nifty (Indian index). Defines opening range from first N minutes, then classifies regime: Bullish (price above OR high), Bearish (below OR low), Range (inside OR). Uses OR width relative to ATR to gauge expected range expansion.
- **Innovation**: 3/5 - OR breakout with regime classification is practical. Nifty-specific but concept is portable.
- **A-Share Applicability**: 2/5 - Opening range concept exists in A-shares but 9:30-10:00 first 30min range is less predictive due to call auction mechanism.
- **Key Concepts**: Opening range breakout, regime classification, OR/ATR ratio, range expansion expectation.

### #75 - mtf trend cascade
- **URL**: https://www.tradingview.com/script/C5ZqqsDO-mtf-trend-cascade
- **Mathematical Core**: Multi-timeframe trend alignment using cascading logic. Computes trend direction on HTF (daily), MTF (4h), and LTF (1h). Trend defined by EMA slope or price vs EMA. Cascade score = sum(trend_signals) where each TF contributes +1 (bullish), 0 (neutral), -1 (bearish). Full alignment = score of +/-3.
- **Innovation**: 3/5 - Clean cascade scoring system for MTF trend alignment. Straightforward but effective organizational framework.
- **A-Share Applicability**: 3/5 - MTF trend alignment works with daily OHLCV. Using weekly/daily/60min alignment is practical for A-shares.
- **Key Concepts**: Cascade scoring, MTF trend alignment, weighted trend signals, full alignment detection.

### #76 - CIqpuXEC
- **URL**: https://www.tradingview.com/script/CIqpuXEC
- **Mathematical Core**: [Fetch Failed] - Insufficient data. Name suggests generic indicator.
- **Innovation**: 1/5 - Unable to assess.
- **A-Share Applicability**: 1/5 - Unable to assess.

### #77 - CMDiJjby
- **URL**: https://www.tradingview.com/script/CMDiJjby
- **Mathematical Core**: [Fetch Failed] - Insufficient data. Name suggests generic indicator.
- **Innovation**: 1/5 - Unable to assess.
- **A-Share Applicability**: 1/5 - Unable to assess.

### #78 - RSI Div BROWNIETHERABBIT
- **URL**: https://www.tradingview.com/script/CQbfAOxk-RSI-Div-BROWNIETHERABBIT
- **Mathematical Core**: RSI divergence detection comparing price extremes vs RSI extremes. Bullish divergence: price makes lower low while RSI makes higher low. Bearish divergence: price makes higher high while RSI makes lower high. Uses pivot-based detection with lookback windows for both price and RSI.
- **Innovation**: 2/5 - Standard RSI divergence detection; well-implemented but not mathematically novel.
- **A-Share Applicability**: 3/5 - RSI divergence is one of the most widely used signals in A-share technical analysis. Works on daily OHLCV.
- **Key Concepts**: RSI divergence, pivot-based extreme detection, momentum-price disagreement.

### #79 - Auto S/R MTF Bias
- **URL**: https://www.tradingview.com/script/CYptEQIk-Auto-S-R-MTF-Bias
- **Mathematical Core**: Automated support/resistance detection using swing pivot clustering across multiple timeframes. S/R strength scored by number of touches and volume at level. Bias = bullish when price above key HTF S/R, bearish when below. MTF alignment: price position relative to S/R on D/W/M determines directional bias.
- **Innovation**: 3/5 - Combining automated S/R with MTF bias scoring is practical. Touch-count scoring and volume-weighted S/R strength adds value.
- **A-Share Applicability**: 4/5 - Auto S/R detection + MTF bias is highly relevant for A-shares. Weekly/monthly pivot levels are widely watched in A-share markets.
- **Key Concepts**: Automated S/R detection, pivot clustering, touch-count scoring, MTF bias alignment, volume-weighted levels.

### #80 - MES 5 Min ORB
- **URL**: https://www.tradingview.com/script/CZamnoZS-MES-5-Min-ORB
- **Mathematical Core**: 5-minute Opening Range Breakout for MES (Micro S&P futures). OR = highest high and lowest low of first 5 bars. Breakout = close above OR high (long) or below OR low (short). Targets calculated as multiples of OR range. Fixed time window for OR validity.
- **Innovation**: 2/5 - Standard 5-min ORB implementation; clean but well-known technique.
- **A-Share Applicability**: 2/5 - Designed for MES futures. A-share call auction at open makes first-5-min range less meaningful.
- **Key Concepts**: 5-minute opening range, breakout confirmation, range-based targets.

### #81 - Cc6q3BSU
- **URL**: https://www.tradingview.com/script/Cc6q3BSU
- **Mathematical Core**: [Fetch Failed] - Insufficient data.
- **Innovation**: 1/5 - Unable to assess.
- **A-Share Applicability**: 1/5 - Unable to assess.

### #82 - HA Straddle Strangle Signals v7 Auto
- **URL**: https://www.tradingview.com/script/CffUBuVh-HA-Straddle-Strangle-Signals-v7-Auto
- **Mathematical Core**: Uses Heikin-Ashi candles for trend direction combined with options straddle/strangle signal generation. HA smoothing: HA_Close = (O+H+L+C)/4, HA_Open = (prev_HA_Open + prev_HA_Close)/2. Generates signals when HA trend changes correspond to options entry points.
- **Innovation**: 2/5 - HA + options combination is niche but not mathematically innovative.
- **A-Share Applicability**: 2/5 - Options-focused; A-share options market is limited. HA candle concept is portable.
- **Key Concepts**: Heikin-Ashi smoothing, options straddle/strangle, trend-reversal signal generation.

### #83 - Abyan OB Wala
- **URL**: https://www.tradingview.com/script/CgMFbtJR-Abyan-OB-Wala
- **Mathematical Core**: Order Block detection based on smart money concepts. Identifies the last bearish candle before a bullish impulse (bullish OB) or last bullish candle before a bearish impulse (bearish OB). OB validity requires subsequent displacement (strong move away). Mitigation = price returning to OB zone.
- **Innovation**: 2/5 - Standard order block detection; popular ICT concept with basic implementation.
- **A-Share Applicability**: 3/5 - Order blocks (institutional entry zones) work on daily OHLCV. A-share institutional behavior creates identifiable OBs.
- **Key Concepts**: Order block identification, displacement validation, mitigation tracking, smart money concepts.

### #84 - HTF Fair Value Gaps Anchored
- **URL**: https://www.tradingview.com/script/ChNLWSpJ-HTF-Fair-Value-Gaps-Anchored
- **Mathematical Core**: Fair Value Gap (FVG) detection on higher timeframes: Bullish FVG = current_low > prev_high (gap up), Bearish FVG = current_high < prev_low (gap down). Anchored FVGs persist until filled (price returns to gap zone). HTF FVGs (weekly/daily) plotted on lower timeframe charts.
- **Innovation**: 3/5 - Anchored FVG with persistence tracking until fill is a clean ICT implementation.
- **A-Share Applicability**: 3/5 - Gap analysis is very relevant in A-shares where gap-ups/downs are common. Daily FVGs work with OHLCV data.
- **Key Concepts**: Fair Value Gap detection, anchored persistence, gap fill tracking, HTF-to-LTF mapping.

### #85 - Flexible Moving Averages with MACD and RSI
- **URL**: https://www.tradingview.com/script/CjWOn2zz-Flexible-Moving-Averages-with-MACD-and-RSI
- **Mathematical Core**: Triple-indicator convergence system. Configurable MA types (SMA/EMA/WMA/HULL/ALMA) with MACD histogram direction and RSI zone filtering. Signal = MA crossover + MACD histogram confirming direction + RSI in agreement zone (not overbought/oversold against trade).
- **Innovation**: 2/5 - Clean integration of three standard indicators. Flexibility in MA type is practical but not mathematically novel.
- **A-Share Applicability**: 4/5 - MA + MACD + RSI is the most common A-share technical analysis combination. Highly compatible with daily OHLCV.
- **Key Concepts**: MA type flexibility, triple convergence filter, MACD histogram confirmation, RSI zone gating.

### #86 - Options Greeks Dashboard
- **URL**: https://www.tradingview.com/script/D38ZP8Fe-Options-Greeks-Dashboard
- **Mathematical Core**: Black-Scholes option pricing model calculations for Delta, Gamma, Theta, Vega. Dashboard display of Greeks for at-the-money options. Implied volatility estimation from option prices.
- **Innovation**: 1/5 - Standard Black-Scholes implementation; educational but not novel.
- **A-Share Applicability**: 1/5 - A-share options market is small and illiquid; 50ETF options only. Greeks dashboard not widely needed.
- **Key Concepts**: Black-Scholes pricing, Delta/Gamma/Theta/Vega, implied volatility, ATM option tracking.

### #87 - MonsterBox Final Boss Scanner
- **URL**: https://www.tradingview.com/script/DB004NIx-MonsterBox-Final-Boss-Scanner-final-form
- **Mathematical Core**: Multi-signal scanner combining multiple indicators into a composite score. Likely aggregates trend, momentum, volume, and volatility signals into a single dashboard with buy/sell/hold recommendations. Scanner mode for screening multiple instruments.
- **Innovation**: 3/5 - Comprehensive multi-signal aggregation; practical as a screening tool.
- **A-Share Applicability**: 2/5 - Scanner concept useful but typically designed for US markets. May need adaptation for A-share specific indicators.
- **Key Concepts**: Multi-signal aggregation, composite scoring, instrument screening, dashboard visualization.

### #88 - AG Pro Volatility Shape Classifier
- **URL**: https://www.tradingview.com/script/DDB8YRuN-AG-Pro-Volatility-Shape-Classifier-AGPro-Series
- **Mathematical Core**: Volatility regime classification using shape analysis of ATR and Bollinger Band patterns over time. Classifies volatility into shapes: expanding (megaphone), contracting (triangle), flat (horizontal), spiking (sudden expansion). Uses pattern recognition on the volatility time series: shape = classify(ATR_series[n]).
- **Innovation**: 4/5 - Volatility shape classification (megaphone/triangle/flat/spike) is a creative approach to regime identification beyond simple high/low vol.
- **A-Share Applicability**: 3/5 - Volatility shape analysis works on daily OHLCV. A-share volatility patterns (limit-induced compression) create distinct shapes.
- **Key Concepts**: Volatility shape classification, ATR pattern recognition, regime categorization, expanding/contracting/flat/spike taxonomy.

### #89 - Versatile Scalper
- **URL**: https://www.tradingview.com/script/DGYGVDxx-Versatile-Scalper
- **Mathematical Core**: Adaptive scalping system likely combining fast/slow MA crossovers with momentum confirmation and volume filters. Designed for multiple instrument/timeframe combinations with configurable parameters.
- **Innovation**: 2/5 - General-purpose scalper; combines well-known techniques without novel math.
- **A-Share Applicability**: 3/5 - Scalping concepts adaptable to A-shares on 30min/60min timeframes. Daily OHLCV sufficient for swing-scale.
- **Key Concepts**: Adaptive parameters, fast/slow signal generation, volume confirmation, multi-instrument design.

### #90 - H4 Abnormal Candle
- **URL**: https://www.tradingview.com/script/DIy1Yjeu-H4-Abnormal-Candle
- **Mathematical Core**: Anomaly detection for H4 candles using statistical deviation. Abnormal = candle range exceeds N * ATR (typically 2x-3x) or volume exceeds N * average_volume. Flags statistically unusual candles that indicate institutional activity or news events.
- **Innovation**: 2/5 - Statistical outlier detection on candles; simple but practical.
- **A-Share Applicability**: 3/5 - Anomalous candle detection works on daily OHLCV. A-shares with 10% limits make extreme candles less common but volume anomalies are telling.
- **Key Concepts**: Statistical candle anomaly, range vs ATR outlier, volume outlier, institutional activity flagging.

### #91 - Minervini SEPA System
- **URL**: https://www.tradingview.com/script/DL8BpgzT-Minervini-SEPA-System
- **Mathematical Core**: Mark Minervini's SEPA (Specific Entry Point Analysis) system. Criteria: (1) Price > 150-day SMA AND > 200-day SMA; (2) 150-day SMA > 200-day SMA; (3) 200-day SMA trending up for >= 1 month; (4) Price >= 30% above 52-week low; (5) Price within 25% of 52-week high; (6) RS rank >= 70 (relative strength vs index). Entry on pullback to key MA or breakout from consolidation.
- **Innovation**: 4/5 - Complete implementation of Minervini's trend template with quantitative criteria. Well-structured scoring system.
- **A-Share Applicability**: 4/5 - SEPA criteria are directly applicable to A-shares. RS ranking vs CSI 300/CSI 500 is highly relevant. Daily OHLCV sufficient.
- **Key Concepts**: Minervini trend template, relative strength ranking, 150/200 SMA alignment, 52-week high/low position, SEPA entry point.

### #92 - Nexus Fusion Engine ML
- **URL**: https://www.tradingview.com/script/DRgzod5I-Nexus-Fusion-Engine-ML-WillyAlgoTrader
- **Mathematical Core**: Multi-indicator fusion with machine learning-like weight adaptation. Combines trend (EMA alignment), momentum (RSI/MACD), volatility (BB width), and volume signals into a composite score. Weights adapt based on recent signal accuracy: weight_i = initial_weight * (correct_signals_i / total_signals_i). Output = normalized fusion score 0-100.
- **Innovation**: 4/5 - Adaptive weight fusion system approximating ML. Dynamic rebalancing based on signal accuracy is a practical pseudo-ML approach.
- **A-Share Applicability**: 3/5 - Multi-indicator fusion with adaptive weights works on daily OHLCV. Component indicators are standard A-share tools.
- **Key Concepts**: Multi-signal fusion, adaptive weighting, accuracy-based rebalancing, composite scoring.

### #93 - AI Smart Assistant UI Toolkit Yosiet
- **URL**: https://www.tradingview.com/script/DXdJJTts-AI-Smart-Assistant-UI-Toolkit-Yosiet
- **Mathematical Core**: UI/dashboard toolkit for TradingView scripts. Provides pre-built table components, label positioning, and visual elements. No trading logic.
- **Innovation**: 1/5 - UI utility, not a trading strategy.
- **A-Share Applicability**: 1/5 - No trading logic to apply.
- **Key Concepts**: UI components, table formatting, label management, dashboard construction.

### #94 - 10 SMA 21 EMA Dotted
- **URL**: https://www.tradingview.com/script/DfRILamr-10-SMA-21-EMA-Dotted
- **Mathematical Core**: Simple plot of SMA(10) and EMA(21) as dotted lines on the chart. Crossover signals: buy when SMA10 crosses above EMA21, sell when crosses below.
- **Innovation**: 1/5 - Most basic MA crossover possible.
- **A-Share Applicability**: 3/5 - 10/21 MA crossover is a classic A-share short-term trading signal. Simple but widely used.
- **Key Concepts**: SMA/EMA crossover, dotted line visualization, basic trend signal.

### #95 - Pivot High Low HH LL
- **URL**: https://www.tradingview.com/script/Dfxi84jv-Pivot-High-Low-HH-LL
- **Mathematical Core**: Pivot point detection using local maxima/minima with configurable lookback. Classifies each pivot as Higher High (HH), Lower High (LH), Higher Low (HL), or Lower Low (LL) by comparing consecutive pivot values. Trend = series of HH+HL (uptrend) or LH+LL (downtrend).
- **Innovation**: 2/5 - Standard pivot classification; well-implemented but basic.
- **A-Share Applicability**: 3/5 - HH/HL/LH/LL classification is fundamental to A-share technical analysis. Works on daily OHLCV.
- **Key Concepts**: Pivot detection, HH/HL/LH/LL classification, trend structure tracking.

### #96 - Custom Fractals
- **URL**: https://www.tradingview.com/script/Dgqhj6CT-Custom-Fractals
- **Mathematical Core**: Williams Fractal variant with configurable lookback. Bullish fractal = low[i] < low[i-n..i-1] AND low[i] < low[i+1..i+n]. Bearish fractal = high[i] > high[i-n..i-1] AND high[i] > high[i+1..i+n]. Default n=2 (standard Williams), configurable for more/less sensitivity.
- **Innovation**: 2/5 - Standard fractal pattern with configurable lookback; practical extension of Williams Fractals.
- **A-Share Applicability**: 3/5 - Fractal patterns work on daily OHLCV. Configurable lookback helps adapt to A-share volatility.
- **Key Concepts**: Williams Fractals, configurable lookback, swing extreme detection.

### #97 - Trend Analysis Dashboard YPro
- **URL**: https://www.tradingview.com/script/DiHus8a3-Trend-Analysis-Dashboard-YPro
- **Mathematical Core**: Multi-indicator trend dashboard aggregating signals from MA alignment, MACD, RSI, ADX, and volume trend. Displays trend status (bullish/bearish/neutral) for each indicator in a table format. Composite trend score = weighted sum of individual signals.
- **Innovation**: 2/5 - Standard multi-indicator dashboard; practical for at-a-glance analysis but no mathematical novelty.
- **A-Share Applicability**: 3/5 - Multi-indicator trend dashboard useful for A-share screening. All components work on daily OHLCV.
- **Key Concepts**: Multi-indicator aggregation, dashboard visualization, composite trend scoring.

### #98 - DmBG9zK5
- **URL**: https://www.tradingview.com/script/DmBG9zK5
- **Mathematical Core**: [Fetch Failed] - Insufficient data.
- **Innovation**: 1/5 - Unable to assess.
- **A-Share Applicability**: 1/5 - Unable to assess.

### #99 - DrpqDrNv
- **URL**: https://www.tradingview.com/script/DrpqDrNv
- **Mathematical Core**: [Fetch Failed] - Insufficient data.
- **Innovation**: 1/5 - Unable to assess.
- **A-Share Applicability**: 1/5 - Unable to assess.

### #100 - Swing to Swing Move Analyzer
- **URL**: https://www.tradingview.com/script/DtJ18oNx-Swing-to-Swing-Move-Analyzer
- **Mathematical Core**: Swing move analysis system that measures properties of each swing leg: magnitude (price change), duration (bars), velocity (magnitude/duration), retracement ratio (pullback/impulse), and extension ratio. Statistical summary of swing properties over time.
- **Innovation**: 3/5 - Comprehensive swing move property analysis with velocity and statistical summarization. Useful quantitative framework.
- **A-Share Applicability**: 3/5 - Swing analysis works on daily OHLCV. Statistical properties of swing moves help calibrate A-share trading parameters.
- **Key Concepts**: Swing magnitude, swing velocity, retracement ratio, extension ratio, statistical swing summary.

---

## Highlights

### Top 5 for A-Share Applicability (Score >= 4)

1. **#67 Pullback Measured Move** (4/5) - Clean A-B-C swing framework with configurable projection multiplier. ATR noise filter handles A-share volatility. Price targets from pullback depth x multiplier is mathematically elegant.

2. **#79 Auto S/R MTF Bias** (4/5) - Automated S/R with touch-count scoring and MTF bias. Weekly/monthly pivot levels are key reference points in A-share markets. Volume-weighted S/R strength adds institutional context.

3. **#85 Flexible MA + MACD + RSI** (4/5) - Triple convergence system using the three most common A-share indicators. MA type flexibility (SMA/EMA/WMA/HULL) allows tuning to A-share characteristics.

4. **#91 Minervini SEPA System** (4/5) - Complete quantitative implementation of Minervini's trend template. RS ranking vs index is perfect for A-share stock screening. All criteria calculable from daily OHLCV.

### Top 5 for Mathematical Innovation (Score >= 4)

1. **#62 Metis Ladder Compression Engine** (4/5) - Novel compression ratio measurement across successive price ranges. Quantifies volatility contraction systematically.

2. **#63 Volatility Terrain Engine JOAT** (4/5) - Topographic metaphor applied to composite volatility surface. Multi-indicator volatility regime mapping.

3. **#67 Pullback Measured Move** (4/5) - Mathematical elegance in range projection: Target = B +/- (pullback_range x multiplier). ATR filter removes noise.

4. **#72 Order Flow Smart Footprint** (4/5) - Volume imbalance ratio, delta analysis, and absorption detection create a comprehensive order flow framework.

5. **#88 AG Pro Volatility Shape Classifier** (4/5) - Creative taxonomy of volatility patterns (megaphone/triangle/flat/spike). Goes beyond binary high/low vol classification.

### Key Takeaways for A-Share Strategy Development

1. **Pullback Measured Move** (#67) is the most actionable: swing structure + price target projection with ATR noise filtering translates directly to A-share daily bars.

2. **Minervini SEPA** (#91) provides a complete quantitative stock screening framework with RS ranking, ideal for identifying A-share leaders.

3. **Volatility Shape Classifier** (#88) offers creative regime detection that can identify the compression/expansion cycles common in A-shares near earnings or policy events.

4. **Order Flow Smart Footprint** (#72) volume decomposition concepts can be adapted for A-share daily volume analysis despite lacking tick data.

5. **Nexus Fusion Engine** (#92) demonstrates practical adaptive weighting that could improve multi-indicator signal quality in A-share backtests.
