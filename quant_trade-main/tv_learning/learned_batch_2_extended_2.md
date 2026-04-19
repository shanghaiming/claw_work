# Batch 2 Extended Learning (Scripts 30-59)
> Date: 2026-04-19

## Summary
- Total: 30
- Innovation >= 3: 10
- A-share applicable (>=3): 16

## Strategy Details

### 1. 10 SMA & 21 EMA (Dotted)
- **URL**: https://www.tradingview.com/script/DfRILamr-10-SMA-21-EMA-Dotted/
- **Category**: trend
- **Math Core**: SMA(10) and EMA(21) plotted as dotted circles; uses SMA as trend-following anchor and EMA as pyramid/exit line
- **Innovation**: 1/5
- **A-share Applicability**: 3/5
- **Key Params**: SMA_period=10, EMA_period=21
- **Notes**: Ultra-simple dual moving average; minimal code. Useful as a trend filter component but not a standalone strategy.

### 2. Pivot High/Low (HH/LL)
- **URL**: https://www.tradingview.com/script/Dfxi84jv-Pivot-High-Low-HH-LL/
- **Category**: price_action
- **Math Core**: ta.pivothigh/ta.pivotlow with N-bar left/right confirmation window; labels swing extremes as HH/LL
- **Innovation**: 1/5
- **A-share Applicability**: 4/5
- **Key Params**: N=5 (bars left and right)
- **Notes**: Clean pivot detection using standard Pine functions. Good building block for market structure analysis. Offsets labels to actual pivot bar.

### 3. Custom Fractals
- **URL**: https://www.tradingview.com/script/Dgqhj6CT-Custom-Fractals/
- **Category**: price_action
- **Math Core**: Williams Fractals with customizable left/right bar inputs + RSI confirmation filter (RSI > 65 overbought / < 35 oversold) for fractal validation
- **Innovation**: 2/5
- **A-share Applicability**: 4/5
- **Key Params**: leftBars=13, rightBars=2, nonRepaint=true, RSI_length=14, RSI_OB=65, RSI_OS=35, pivotLineBars=8
- **Notes**: Adds RSI confirmation to classic fractals for higher-quality pivot signals. Non-repaint mode is crucial for backtesting. Horizontal S/R lines from fractals are a nice touch.

### 4. Trend Analysis Dashboard YPro
- **URL**: https://www.tradingview.com/script/DiHus8a3-Trend-Analysis-Dashboard-YPro/
- **Category**: multi_factor
- **Math Core**: Aggregates ADX, multiple Moving Averages, and RSI into a composite trend confidence score displayed on a dashboard
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: Best for 15m/1h/4h timeframes; ADX, MA, RSI lengths configurable
- **Notes**: Multi-indicator dashboard approach. Composite scoring is conceptually useful but the implementation is standard. Best as a trend environment filter.

### 5. Aegis Pulse & Energy
- **URL**: https://www.tradingview.com/script/DmBG9zK5/
- **Category**: multi_factor
- **Math Core**: Combines ADX (trend strength) with MFI (Money Flow Index) and MFI-20SMA crossover to classify energy states: strong energy (ADX>25 & MFI>avg), weak energy, or neutral
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: ADX_length=14, MFI_length=14, threshold=25
- **Notes**: Dual-axis indicator (ADX line + MFI histogram). The energy state classification is a clean binary filter. Korean-language UI but logic is clear.

### 6. Daily Separator
- **URL**: https://www.tradingview.com/script/DrpqDrNv/
- **Category**: price_action
- **Math Core**: Time-based vertical line separator for intraday charts; draws lines at configurable hour with configurable backward offset in bars
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: heure_ref=23, decalage_heures=6, line_color=gray, epaisseur=1
- **Notes**: Utility script for session visualization. French-language UI. Not a trading strategy - purely visual.

### 7. Swing-to-Swing Move Analyzer
- **URL**: https://www.tradingview.com/script/DtJ18oNx-Swing-to-Swing-Move-Analyzer/
- **Category**: price_action
- **Math Core**: Detects swing highs/lows, measures the percentage move between consecutive swing points, and displays Fib retracement levels for each swing
- **Innovation**: 2/5
- **A-share Applicability**: 4/5
- **Key Params**: Swing detection period, Fib levels display
- **Notes**: Useful for measuring swing amplitude statistics. The move-size analysis can help calibrate profit targets and stop losses on A-shares.

### 8. OBV + Bollinger Bands + Reversal Signal + EMA Cross
- **URL**: https://www.tradingview.com/script/E9mJ40SZ-OBV-Bollinger-Bands-Reversal-Signal-EMA-Cross/
- **Category**: volume
- **Math Core**: OBV rendered as candlestick/Heikin-Ashi candles overlaid with Bollinger Bands; multiple signal modes: Scalp (fast EMA cross), Swing (EMA vs BB basis), Trend (EMA 20/50), Manual (full confluence)
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: mode=Manual, EMA1=9, EMA2=13, BB_length=20, BB_mult=2.0, HA_candles=true
- **Notes**: Volume-based confluence system. OBV-Heikin-Ashi candles are a creative visualization. The 4-mode signal system is well-designed for different market conditions. Volume analysis is very relevant for A-shares.

### 9. Key Intraday Levels
- **URL**: https://www.tradingview.com/script/EF6wUbmQ-Key-Intraday-Levels/
- **Category**: price_action
- **Math Core**: Plots key intraday price levels including previous day H/L/C, session opens, and pivot points on intraday charts
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: Various session time inputs, level display toggles
- **Notes**: Standard key level indicator. Useful for intraday reference but not a strategy on its own. Primarily designed for US markets with specific session times.

### 10. Iteratively Reweighted Least Squares (IRLS) [Jamallo]
- **URL**: https://www.tradingview.com/script/EHhyqcML-Iteratively-Reweighted-Least-Squares-IRLS-Jamallo/
- **Category**: trend
- **Math Core**: L1-robust price smoother using IRLS with Hardy weight function: w(j) = 1/sqrt(dist(j)^2 + epsilon^2). Uses adaptive epsilon from average H-L range. Sparse reweighting: only top s_ratio*N samples vote. Multiple configurable passes.
- **Innovation**: 5/5
- **A-share Applicability**: 4/5
- **Key Params**: window=20, iterations=3, sparsity_ratio=0.3, source=close
- **Notes**: Highly mathematical and novel. IRLS is a robust statistics technique rarely seen in trading indicators. The sparsity control (only closest N% of samples vote) creates an adaptive, outlier-resistant smoother. Could be very effective for filtering noise in A-share markets with limit-up/limit-down events. Best innovation in this batch.

### 11. Multi Session Highlighter PRO
- **URL**: https://www.tradingview.com/script/ETH7ssuN-Multi-Session-Highlighter-PRO/
- **Category**: price_action
- **Math Core**: Tracks up to 5 custom time sessions, draws session ranges (boxes), H/L levels with optional extensions, tracks precise origin points
- **Innovation**: 2/5
- **A-share Applicability**: 2/5
- **Key Params**: timezone, days_back=5, up to 5 sessions, HL extend options
- **Notes**: Comprehensive session visualization tool. Best for forex/futures with multiple trading sessions. Less relevant for A-shares which have a single unified session.

### 12. retardwicks
- **URL**: https://www.tradingview.com/script/EdQ3xzvZ-retardwicks/
- **Category**: price_action
- **Math Core**: Wick-based POI and rejection detection with volume profile and fractal elements
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: [Closed source - code not accessible]
- **Notes**: [Fetch Failed - Closed source script. Description mentions wick POI, rejections, volume profile, orderflow, moon fractals]

### 13. Color RSI
- **URL**: https://www.tradingview.com/script/EiG966fR-Color-RSI/
- **Category**: mean_reversion
- **Math Core**: Standard RSI with color zones: red for overbought (>=70), green for oversold (<=30), gray for neutral. Includes optional divergence calculation.
- **Innovation**: 1/5
- **A-share Applicability**: 3/5
- **Key Params**: RSI_length=14, OVB=70, OVS=30
- **Notes**: Simple RSI with visual color coding. Divergence feature is optional (off by default). Very basic but functional.

### 14. CSK Timeframe Fair Value Gaps (fade)
- **URL**: https://www.tradingview.com/script/EkMU5EEH-CSK-Timeframe-Fair-Value-Gaps-fade-CSKyle/
- **Category**: price_action
- **Math Core**: Multi-timeframe Fair Value Gap detection with bar count tracking; FVG type with top/bot/isBullish/createdBar fields; boxes drawn with fading transparency
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: MTF alignment, max_boxes=500, max_bars_back=2000
- **Notes**: Solid FVG implementation with custom types. The fade effect is practical for chart readability. MTF alignment adds confluence. FVGs are relevant for A-share gap analysis.

### 15. Position Size Calculator CENTRAL
- **URL**: https://www.tradingview.com/script/EmXnJDlf/
- **Category**: multi_factor
- **Math Core**: Position size = Risk Amount / (Stop Loss * Pip Value); auto-detects forex pairs and JPY pairs for pip size calculation
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: balance=10000, riskPercent=1, sl_pips=13, manual_pip_value toggle
- **Notes**: Risk management utility, not a strategy. Designed for forex pip-based calculations. Would need modification for A-share lot sizing.

### 16. CTZ Expected Move Suite
- **URL**: https://www.tradingview.com/script/EmczUrDx-CTZ-Expected-Move-Suite/
- **Category**: volatility
- **Math Core**: ATR-based expected move projection with dynamic S/R, Fibonacci retracement, and risk/reward system; projects EM bands at 1x and 1.5x ATR multipliers
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: ATR_length=14, EM_mult1=1.0, EM_mult2=1.5, Fib levels configurable
- **Notes**: Comprehensive expected move toolkit. The ATR-based band projection is mathematically sound for daily expected range. Useful for A-share daily limit awareness.

### 17. NQ Matrix Core Model (BETA)
- **URL**: https://www.tradingview.com/script/EpHwH0MI-NQ-Matrix-Core-Model-BETA-VerA01-260415/
- **Category**: price_action
- **Math Core**: Fixed point-based framework projecting percentage-based downside levels from daily high for NQ futures; pre-defined level array with probability annotations
- **Innovation**: 2/5
- **A-share Applicability**: 1/5
- **Key Params**: NQ-specific point levels (100, 125, 150...1450), probability percentages hardcoded
- **Notes**: NQ-specific library (not standalone indicator). Hardcoded levels make it non-transferable. The percentage-based approach from daily high is conceptually interesting but implementation is too instrument-specific.

### 18. Sentinel SMC Pro - Institutional Flow 3
- **URL**: https://www.tradingview.com/script/EpP75Txv-Sentinel-SMC-Pro-Institutional-Flow-3/
- **Category**: multi_factor
- **Math Core**: Smart Money Concepts (SMC) system with Order Blocks, Fair Value Gaps, Break of Structure, and liquidity sweeps; non-repainting (barstate.isconfirmed gated); designed for 5M timeframe
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: Recommended for USDJPY/EURUSD/XAUUSD on 5M, SMC parameters configurable
- **Notes**: Comprehensive SMC implementation with non-repainting guarantee. Combines multiple institutional flow concepts. The SMC methodology has gained popularity but effectiveness on A-shares with daily limits is unproven.

### 19. Market Wave PRO ELITE
- **URL**: https://www.tradingview.com/script/Eqi2c3KE/
- **Category**: multi_factor
- **Math Core**: Multi-indicator scoring system: HMA(55) + EMA(200) + HTF EMA for trend, WaveTrend oscillator for momentum, RSI(14) + ADX(14) for strength, Bollinger Bands for volatility; composite score -4 to +4 with A+ signals requiring score >= 2
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: HMA=55, EMA=200, HTF=5m, WaveTrend_ch=10/avg=14, BB=20/2.0, RSI=14, ADX=14
- **Notes**: Well-designed multi-factor scoring system. The WaveTrend + volatility regime + score filtering creates a systematic approach. Good template for A-share strategy development.

### 20. Apex ATR Exhaustion Bands
- **URL**: https://www.tradingview.com/script/EtixA1xJ-Apex-ATR-Exhaustion-Bands/
- **Category**: volatility
- **Math Core**: Daily ATR-based exhaustion boundary: upperLimit = prevClose + ATR*(exhaustPct/100), lowerLimit = prevClose - ATR*(exhaustPct/100); uses previous day's close and ATR to project today's expected travel range
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: ATR_length=14, exhaustPct=100% (indices) or 130-150% (high-beta), visibility=intraday/all
- **Notes**: Clean exhaustion detection concept. When price reaches the full ATR travel from yesterday's close, it's statistically exhausted. Very relevant for A-shares where daily limits cap movement. The exhaustPct parameter allows tuning for different volatility regimes.

### 21. Important Extremes
- **URL**: https://www.tradingview.com/script/ExGRwjYj-important-extremes/
- **Category**: price_action
- **Math Core**: Pivot-based S/R levels with minimum distance filter (minDistancePct); maintains a capped array of most recent levels; deduplicates nearby levels
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: length=5, maxLevels=5, minDistancePct=0.1%
- **Notes**: Clean S/R level tracker with deduplication. Russian-language UI but logic is clear. The minimum distance filter prevents cluttered levels - good design choice.

### 22. Trend + Momentum + FVG Signals
- **URL**: https://www.tradingview.com/script/F0F0xrXY-Trend-Momentum-FVG-Signals/
- **Category**: multi_factor
- **Math Core**: 3-layer system: Trend (EMA 21/50/200 crossover), Momentum (RSI 14 with OB/OS + MACD 12/26/9), Fair Value Gaps; signals require trend alignment + momentum confirmation + FVG presence
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: EMA_fast=21, EMA_slow=50, EMA_trend=200, RSI=14/70/30, MACD=12/26/9
- **Notes**: Well-structured confluence system for crypto futures. The 3-layer approach (trend + momentum + FVG) is systematic and reproducible. Good template for building A-share strategies.

### 23. Tidal Volume Oscillator [JOAT]
- **URL**: https://www.tradingview.com/script/F9wbW2sl-Tidal-Volume-Oscillator-JOAT/
- **Category**: volume
- **Math Core**: Volume-weighted momentum score normalized to [-100, +100] range, with Fourier-inspired exponential decay smoothing pass to reduce noise without phase lag, scaled by ATR for volatility normalization
- **Innovation**: 4/5
- **A-share Applicability**: 4/5
- **Key Params**: VZO_length=14, smoothing=5, signalLen=9, fourierWindow=20, fourierBlend=0.4, momentumLookback=8
- **Notes**: Sophisticated volume oscillator. The Fourier-inspired smoothing is novel - uses exponential decay in frequency domain to reduce noise without lag. Volume-weighted momentum is highly relevant for A-shares where volume data is freely available and meaningful.

### 24. Two-Bar Fib Retrace Strategy [Futures]
- **URL**: https://www.tradingview.com/script/FBjy1vIq-Two-Bar-Fib-Retrace-Strategy-Futures/
- **Category**: price_action
- **Math Core**: Identifies 2-bar impulse moves with rising volume, waits for 50-61.8% Fibonacci retracement into the 2nd bar's range; VWAP trend filter (longs above, shorts below); layered with ICT institutional levels
- **Innovation**: 4/5
- **A-share Applicability**: 3/5
- **Key Params**: Fib retracement 50-61.8%, VWAP filter, volume confirmation, 5M recommended timeframe
- **Notes**: Elegant 2-bar price action strategy. The combination of impulse detection + volume confirmation + precise Fib retracement + VWAP filter is well-conceived. Would need adaptation for A-shares (no VWAP in traditional sense, different volume profile).

### 25. SQZ Pro JS [MTF + ADX + Divergencias + Giros]
- **URL**: https://www.tradingview.com/script/FH0wCI7H/
- **Category**: volatility
- **Math Core**: Squeeze Momentum reconstruction with MTF alignment, ADX filtering, divergence detection (PRO logic), and reversal signals
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: [Closed source - code not accessible. Description references TTM Squeeze with multi-timeframe + ADX + divergence layers]
- **Notes**: [Partial Fetch - Closed source. Description indicates a comprehensive squeeze momentum system with professional divergence logic. Spanish-language UI.]

### 26. CTZ Vol Mom BBWP Dashboard
- **URL**: https://www.tradingview.com/script/FJNQYPwY-CTZ-Vol-Mom-BBWP-Dashboard/
- **Category**: volatility
- **Math Core**: Triple-layer dashboard: ATR expansion/contraction state (RANGING/BREAKOUT/BREAKDOWN), ROC momentum direction (Bullish/Bearish), BBWP (Bollinger Band Width Percentile) for historical volatility rank using piecewise array-based percentile approach
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: ATR_length, ROC_length, BBWP_lookback, state thresholds configurable
- **Notes**: Excellent volatility state machine. The ATR state engine classifies market into actionable states. BBWP percentile rank adds historical context. This 3-layer approach is directly useful for A-share regime detection.

### 27. H4 Open Times
- **URL**: https://www.tradingview.com/script/FPFZWtCp-H4-open-times/
- **Category**: price_action
- **Math Core**: Time-based level plotting at specific NY times (18:00, 22:00, 02:00, 06:00, 09:30, 10:00); horizontal + vertical lines at each time slot
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: NY timezone times hardcoded
- **Notes**: Simple time-based level marker for US session. Not relevant for A-share markets which operate on completely different time zones.

### 28. WTI 4H Trend Band
- **URL**: https://www.tradingview.com/script/FoRVpK4c/
- **Category**: trend
- **Math Core**: Dual Supertrend system (main ATR=14/mult=3.0 + early ATR=10/mult=2.0) combined with EMA 21/50/100; strict mode requires all EMA alignment; strong signal detection (BUY+/SELL+) when both Supertrends align
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: EMA 21/50/100, Supertrend1: ATR=14/factor=3.0, Supertrend2: ATR=10/factor=2.0, strictMode=true
- **Notes**: Clean dual-Supertrend approach with EMA trend filter. The early band (faster Supertrend) provides earlier signals while the main band confirms. Well-suited for trending commodities but adaptable.

### 29. ORB Breakout Signal
- **URL**: https://www.tradingview.com/script/Fp2BK07P-ORB-Breakout-Signal/
- **Category**: price_action
- **Math Core**: [Publication not found - page returns 404]
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Key Params**: N/A
- **Notes**: [Fetch Failed - Publication has been removed or is unavailable]

### 30. Yield Curve Regime
- **URL**: https://www.tradingview.com/script/FsCkxqrz/
- **Category**: multi_factor
- **Math Core**: Classifies US Treasury yield curve into 6 canonical regimes by comparing short-maturity (default 2Y) and long-maturity (default 10Y) yields against their values N bars ago; regime classification drives dashboard display with delta trend arrow and strength meter
- **Innovation**: 4/5
- **A-share Applicability**: 2/5
- **Key Params**: shortSymbol=US02Y, longSymbol=US10Y, offset bars configurable
- **Notes**: Sophisticated macro regime indicator. The 6-regime classification system is well-thought-out for macro analysis. However, it's designed for US Treasury yields and would need significant adaptation for China bond market. The regime classification methodology could inspire similar approaches for A-share market breadth indicators.

## Highlights

Top 5 most innovative strategies (Innovation >= 4):

1. **Iteratively Reweighted Least Squares (IRLS) [Jamallo]** (5/5) - True robust statistics applied to price smoothing. The Hardy weight function with adaptive epsilon and sparsity control is genuinely novel in trading indicators. Could revolutionize noise filtering for A-shares.

2. **Tidal Volume Oscillator [JOAT]** (4/5) - Fourier-inspired smoothing on a volume-weighted momentum score. The frequency-domain noise reduction without phase lag is a sophisticated mathematical approach rarely seen in community scripts.

3. **Two-Bar Fib Retrace Strategy [Futures]** (4/5) - Elegant simplicity: 2-bar impulse + volume confirmation + precise Fib retracement + VWAP filter. Well-conceived price action system with clear mechanical rules.

4. **Yield Curve Regime** (4/5) - Sophisticated macro regime classification into 6 states. The methodology of comparing current vs. N-bars-ago values for regime detection is transferable to other asset classes.

5. **Market Wave PRO ELITE** (3/5 - honorable mention) - Clean multi-factor scoring system with WaveTrend, volatility regime, and composite score filtering. Good systematic template though individual components are standard.
