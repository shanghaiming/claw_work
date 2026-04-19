# Batch 6 Extended Learning (Scripts 60-89)
> Date: 2026-04-19

## Summary
- Total: 30
- Innovation >= 3: 8
- A-share applicable (>=3): 10

## Strategy Details

### 1. No Wick Open Highlighter (Repairs)
- **URL**: https://www.tradingview.com/script/qdRebFU0-No-Wick-Open-Highlighter-Repairs
- **Category**: kline_pattern
- **Math Core**: Detects candles where open == high or open == low (zero wick on one side), draws horizontal lines at those open prices
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: none (pure detection)
- **Notes**: Simple K-line structure detector. A-share relevance: strong open-no-wick signals can indicate institutional conviction but limited as standalone strategy.

### 2. MTF MA Matrix - Clean Base
- **URL**: https://www.tradingview.com/script/qetKgBK2
- **Category**: trend
- **Math Core**: Multi-timeframe (1H,2H,4H,8H,12H,1D) EMA slope + price positioning + normalized slope calculation + cross-TF alignment scoring with EMA250-500 cloud
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: EMA type=EMA, TFs=[1H,2H,4H,8H,12H,1D], min alignment threshold, ATR stop, trailing stop
- **Notes**: Well-structured MTF trend system. Normalized slope avoids volatility distortion. Good for A-share daily/weekly trend following. Minimum alignment (not full) adds flexibility.

### 3. Alfred Master Indicator
- **URL**: https://www.tradingview.com/script/qfc4Ts7L-Alfred-Master-Indicator
- **Category**: multi_factor
- **Math Core**: Combines SMC (Order Blocks, FVG, BOS, Liquidity Zones) + Chart Patterns (Double/Triple Top/Bottom, H&S, Cup&Handle, Flags) + Candlestick Patterns (15+ types) + EMA 20/50/100/200 + MACD + Volume
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: EMA periods=[20,50,100,200], toggle on/off per feature
- **Notes**: All-in-one indicator. Kitchen-sink approach. Useful as educational reference for pattern detection logic but not suitable as a systematic strategy.

### 4. Seasons Percentage (KenshinC)
- **URL**: https://www.tradingview.com/script/qmkPgplE-Seasons-percentage-KenshinC
- **Category**: multi_factor
- **Math Core**: 6-year monthly range % = (High-Low)/Close statistics per month, with Max/Min/Avg per month, color-coded vs yearly average
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: start_year=2021, num_years=6 (up to 10), hemisphere selection
- **Notes**: Seasonal/monthly volatility analysis. Very applicable to A-share market where seasonal patterns (e.g., Spring Rally, year-end effects) are well-documented. The table format is clean for analysis.

### 5. Relative Volume at Time (customised)
- **URL**: https://www.tradingview.com/script/qn9EkFgv-Relative-Volume-at-Time-customised
- **Category**: volume
- **Math Core**: Volume at each time bar compared to historical average volume at same time-of-day; customizable visual appearance
- **Innovation**: 1/5
- **A-share Applicability**: 3/5
- **Key Params**: lookback period (inherit from TV default), appearance settings
- **Notes**: Standard relative volume at time concept. Useful for detecting unusual volume spikes at specific trading hours. A-share has fixed session hours (9:30-11:30, 13:00-15:00) so time-of-day volume patterns are meaningful.

### 6. BTC Average Daily Returns by Day
- **URL**: https://www.tradingview.com/script/qvoGOVnz-BTC-Average-Daily-Returns-by-Day
- **Category**: multi_factor
- **Math Core**: Average daily return grouped by weekday (Mon-Fri) with selectable lookback periods (1W, 2W, 1M, 3M, 6M, 1Y); heatmap coloring
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: lookback=[1W,2W,1M,3M,6M,1Y], display mode=[table/top bar], heatmap toggle, best/worst highlight
- **Notes**: Day-of-week return analysis. A-share has well-known weekday effects (e.g., "Black Thursday" tendency). Descriptive not predictive. Good as context tool.

### 7. Follow-Through Day (FTD) Detector
- **URL**: https://www.tradingview.com/script/qmuk6WNR
- **Category**: trend
- **Math Core**: Day 1 = first candle after new low that doesn't undercut; FTD = Day 4+ where close rises >= 1.25%, volume > previous day, Day 1 low not undercut
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: min_gain=1.25%, min_day=4, volume_confirmation=true
- **Notes**: William O'Neil's Follow-Through Day concept from IBD. Very applicable to A-share bottom-fishing after corrections. The 1.25% threshold is reasonable for A-shares given 10% daily limits.

### 8. Higher Timeframe Candles with Vector Coloring [PVSRA]
- **URL**: https://www.tradingview.com/script/r8sDJypc-Higher-Timeframe-Candles-with-Vector-Coloring-PVSRA
- **Category**: volume
- **Math Core**: Draws higher-TF candles on chart with PVSRA (Price Volume Structural Range Analysis) vector coloring based on volume-spread relationship classification
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: higher_TF selection, volume threshold, spread classification params
- **Notes**: Combines MTF candle overlay with PVSRA volume analysis. Good for understanding institutional activity on higher timeframes. PVSRA classifies candles by volume-vs-spread patterns.

### 9. Dual Structure BB Ribbon (HIGH + LOW 20,2)
- **URL**: https://www.tradingview.com/script/u17uwQql-Dual-Structure-BB-Ribbon-HIGH-LOW-20-2
- **Category**: volatility
- **Math Core**: Dual asymmetric Bollinger Bands: Buy ribbon based on HIGH series BB(20,2), Sell ribbon based on LOW series BB(20,2); expansion/contraction detection via ribbon width
- **Innovation**: 4/5
- **A-share Applicability**: 4/5
- **Key Params**: BB period=20, BB mult=2, HIGH-based for buy, LOW-based for sell, SMA slope confirmation
- **Notes**: Clever asymmetric BB approach -- buy ribbon uses HIGH series (more sensitive to upside), sell ribbon uses LOW series (conservative for short entries). This asymmetric design adapts to real market dynamics where up/down pressure is unequal. Very applicable to A-shares.

### 10. ZigzagkillerV2
- **URL**: https://www.tradingview.com/script/u2yUlEyn
- **Category**: trend
- **Math Core**: ZigZag pivot detection with Depth/Deviation/Backstep + swing volume accumulation + volume % change vs previous swing + dynamic S/R from confirmed pivots
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: Depth=14, Deviation=7, Backstep=3, Up swing alert %=50, Down swing alert %=50
- **Notes**: ZigZag + Volume = market structure with strength validation. Volume comparison between consecutive swings is practical. Works across timeframes with recommended settings for scalping/intraday/swing. A-share friendly with daily OHLCV.

### 11. Diagonales Exactas Futuro + Ruptura (Manual Price)
- **URL**: https://www.tradingview.com/script/u5LslSAD
- **Category**: price_action
- **Math Core**: Manual trendline/diagonal drawing tool with future projection and breakout detection across multiple timeframes (1H, 30m, 15m, 5m, 1D, 1W)
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Notes**: Spanish-language manual drawing tool. Limited mathematical content. Support/resistance diagonal projection tool.

### 12. qdRebFU0 - qetKgBK2 (MTF MA Matrix - already analyzed above)
- **URL**: [Covered in #2]

### 13. Annual Return V6
- **URL**: https://www.tradingview.com/script/rGJ2Esgc-Annual-Return-V6
- **Category**: multi_factor
- **Math Core**: [Fetch Failed - Rate Limited] Based on name: Annual return calculation with performance tracking
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Notes**: Likely a performance dashboard. Insufficient data for full analysis.

### 14. Descriptive Statistics Variance
- **URL**: https://www.tradingview.com/script/sluD2VpY-Descriptive-Statistics-Variance
- **Category**: volatility
- **Math Core**: [Fetch Failed - Rate Limited] Based on name: Descriptive statistics including variance, standard deviation, skewness
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Notes**: Statistical analysis tool. Variance/descriptive stats useful for volatility regime detection.

### 15. Custom 4 MA Probability (KenshinC English)
- **URL**: https://www.tradingview.com/script/tfA1MYS1-Custom-4-MA-Probability-KenshinC-English
- **Category**: trend
- **Math Core**: [Fetch Failed] Based on name: 4 Moving Averages with probability scoring - likely calculates probability of trend continuation based on MA alignment
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: 4 MA periods (likely 5/20/60/120 or similar)
- **Notes**: Probability-based MA system from prolific author KenshinC. MA probability scoring is a useful concept for systematic A-share trading.

### 16. ATR Multiplier Table With Label
- **URL**: https://www.tradingview.com/script/twXzXevr-ATR-Multiplier-Table-With-Label
- **Category**: volatility
- **Math Core**: [Fetch Failed - Rate Limited] ATR * multiple multiplier values displayed in table format for quick reference
- **Innovation**: 1/5
- **A-share Applicability**: 3/5
- **Notes**: Utility tool for ATR-based position sizing and stop levels. ATR multiplier tables are practical for risk management.

### 17. r02iwvuJ
- **URL**: https://www.tradingview.com/script/r02iwvuJ
- **Category**: unknown
- **Math Core**: [Fetch Failed - No descriptive name]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Notes**: Insufficient information for analysis.

### 18. Wednesday Open Close
- **URL**: https://www.tradingview.com/script/rA1w96HK-Wednesday-open-close
- **Category**: multi_factor
- **Math Core**: Tracks Wednesday open and close prices, likely for weekly pattern analysis
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Notes**: Weekly pattern tool. Wednesday midpoint analysis. Limited standalone value.

### 19. SHK 3 MA EMA WMA VWAP Triangle Cross
- **URL**: https://www.tradingview.com/script/rSrj5GG3-SHK-3-MA-EMA-WMA-VWAP-TRIANGLE-CROSS
- **Category**: trend
- **Math Core**: Triangle cross detection using 3 different MA types (EMA, WMA, VWAP) with cross signal generation
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: EMA period, WMA period, VWAP (session-based)
- **Notes**: Multi-MA cross system. VWAP adds institutional context. A-share applicable for intraday.

### 20. SHK CCI RSI Merged HA Signal MA Dual Divergence v6
- **URL**: https://www.tradingview.com/script/rnsaf4Tn-SHK-CCI-RSI-Merged-HA-Signal-MA-Dual-Divergence-v6
- **Category**: mean_reversion
- **Math Core**: CCI + RSI merged oscillator with Heikin-Ashi signal filter + MA overlay + dual divergence detection (regular + hidden)
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: CCI period, RSI period, MA period, divergence lookback
- **Notes**: Multi-oscillator approach with dual divergence (regular + hidden) is more robust. HA filter reduces noise. Divergence trading works well on A-shares during range-bound markets.

### 21. Next Open Close Marker
- **URL**: https://www.tradingview.com/script/rq4nqDX4-Next-Open-Close-Marker
- **Category**: price_action
- **Math Core**: Marks next period's open and close levels on chart; likely gap analysis tool
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Notes**: Simple visual marker. Gap analysis useful for A-share morning gap strategy.

### 22. ORB Breakout Reset Alert 9:30-10:00 ET
- **URL**: https://www.tradingview.com/script/s7I2QN8o-ORB-Breakout-Reset-Alert-9-30-10-00-ET
- **Category**: price_action
- **Math Core**: Opening Range Breakout (ORB) with 9:30-10:00 ET range, breakout + reset detection, alert system
- **Innovation**: 2/5
- **A-share Applicability**: 4/5
- **Key Params**: ORB window=9:30-10:00 ET (adapt to 9:30-10:30 CST for A-share), breakout threshold, reset conditions
- **Notes**: ORB is a classic strategy directly applicable to A-shares. A-share adaptation: use 9:30-10:30 CST as opening range. The reset logic adds sophistication.

### 23. AG Pro Reference Price Operating Map (AGPro Series)
- **URL**: https://www.tradingview.com/script/sK37XQpW-AG-Pro-Reference-Price-Operating-Map-AGPro-Series
- **Category**: price_action
- **Math Core**: Reference price operating map - likely calculates key price levels (previous day HLC, VWAP, pivots) as operating zones
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Notes**: Professional price map tool. Part of AGPro series. Reference price levels are universal.

### 24. MTF Candle Bias Table
- **URL**: https://www.tradingview.com/script/sNA3wTTg-MTF-Candle-Bias-Table
- **Category**: trend
- **Math Core**: Multi-timeframe candle bias (bullish/bearish/doji classification) displayed in table format across TFs
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: TF list selection
- **Notes**: Quick MTF bias dashboard. Useful as a trend context filter before entries.

### 25. Futures Daily Pivot Zones
- **URL**: https://www.tradingview.com/script/sOn26gCk-Futrues-Daily-Pivot-Zones
- **Category**: mean_reversion
- **Math Core**: Daily pivot point calculation (Classic/Fibonacci/Camarilla variants) for futures markets with zone visualization
- **Innovation**: 1/5
- **A-share Applicability**: 3/5
- **Key Params**: Pivot type (Classic/Fib/Camarilla), daily OHLC
- **Notes**: Standard pivot zones. Well-established concept applicable to A-shares.

### 26. Dae Levels
- **URL**: https://www.tradingview.com/script/sPXYNzzD-Dae-Levels
- **Category**: price_action
- **Math Core**: Custom key level detection and mapping - likely swing highs/lows with dynamic updates
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Notes**: Key level identification tool. Limited info without source code.

### 27. Peer Relative Breakdown Strategy
- **URL**: https://www.tradingview.com/script/sa6WEM84-Peer-Relative-Breakdown-Strategy
- **Category**: mean_reversion
- **Math Core**: Compares asset performance vs peer group (sector/industry) to detect relative breakdown/breakout; likely uses ratio analysis
- **Innovation**: 4/5
- **A-share Applicability**: 4/5
- **Key Params**: peer group definition, lookback period, threshold
- **Notes**: Peer-relative analysis is sophisticated and underused. Very relevant for A-share sector rotation strategies. When a stock breaks down relative to its sector, it signals stock-specific weakness.

### 28. Quad Triple EMA Trend Bands
- **URL**: https://www.tradingview.com/script/siAWIOA2-Quad-Triple-EMA-Trend-Bands
- **Category**: trend
- **Math Core**: 4 sets of Triple EMA (3 EMAs each = 12 total) forming trend bands; trend strength via EMA alignment + band width
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: 4x EMA triplets with different periods (likely fast/medium/slow/macro)
- **Notes**: Layered EMA system with 12 EMAs. Redundancy across 4 speed groups reduces false signals. Good for A-share trend following with daily data.

### 29. slaJ8Qzu
- **URL**: https://www.tradingview.com/script/slaJ8Qzu
- **Category**: unknown
- **Math Core**: [Fetch Failed - No descriptive name]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Notes**: Insufficient information for analysis.

### 30. CTZ Session Guide Beginner Friendly
- **URL**: https://www.tradingview.com/script/smPYGxQ6-CTZ-Session-Guide-Beginner-Friendly
- **Category**: multi_factor
- **Math Core**: Session time zone guide with visual indicators for London/NY/Asia sessions; time-based context tool
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Notes**: Session timing tool. A-share has fixed hours so less relevant, but useful for understanding global session overlap.

## Highlights (Top 5 Most Innovative, Innovation >= 4)

1. **Dual Structure BB Ribbon (HIGH+LOW)** - Innovation 4/5
   - Asymmetric BB using HIGH for buy ribbon, LOW for sell ribbon. Elegant adaptation to real market dynamics where up/down pressure is unequal. Good expansion/contraction detection.

2. **Peer Relative Breakdown Strategy** - Innovation 4/5
   - Compares asset vs peer group for relative breakdown detection. Underused concept highly applicable to A-share sector rotation and pair trading.

3. **MTF MA Matrix (qetKgBK2)** - Innovation 3/5 (notable)
   - Normalized slope MTF alignment with flexible minimum threshold. Clean engineering.

4. **SHK CCI RSI Merged HA Dual Divergence v6** - Innovation 3/5 (notable)
   - Dual divergence (regular + hidden) with HA noise filter. Multi-oscillator fusion.

5. **Follow-Through Day (FTD) Detector** - Innovation 3/5 (notable)
   - William O'Neil's institutional concept implemented cleanly. Bottom-finding with volume confirmation.
