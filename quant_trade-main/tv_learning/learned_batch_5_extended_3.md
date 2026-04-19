# Batch 5 Extended Learning (Scripts 60-89)
> Date: 2026-04-19

## Summary
- Total: 30
- Innovation >= 3: 10
- A-share applicable (>=3): 14

## Strategy Details

### 1. Hourly Direction Change Open Rays
- **URL**: https://www.tradingview.com/script/kO4uSQZU-Hourly-Direction-Change-Open-Rays
- **Category**: price_action
- **Math Core**: Tracks hourly open price levels and extends rays when directional bias changes, identifying intraday structure shifts
- **Innovation**: 2/5
- **A-share Applicability**: 2/5
- **Key Params**: hour_offset=0
- **Notes**: Simple hourly open tracking; designed for intraday futures. Limited use for daily-bar A-share trading.

### 2. Stochastic Divergence Pro V2
- **URL**: https://www.tradingview.com/script/kRKwaXDi-Stochastic-Divergence-Pro-V2
- **Category**: mean_reversion
- **Math Core**: Stochastic RSI divergence detection comparing price pivots vs oscillator pivots to find regular/hidden divergences
- **Innovation**: 2/5
- **A-share Applicability**: 4/5
- **Key Params**: stoch_length=14, smooth_k=3, smooth_d=3
- **Notes**: Standard stochastic divergence. Well-suited for A-share daily timeframe with 10% limits, as divergences appear clearly at extremes.

### 3. TORINVEST Macro Technical
- **URL**: https://www.tradingview.com/script/kVGSxRE0
- **Category**: multi_factor
- **Math Core**: Composite regime score system aggregating Risk-On (equities/BTC/copper/credit) vs Risk-Off (DXY/gold/CHF/JPY) with macro US housing+wages, rates/spreads, and RSI/CVD/MA technical layers
- **Innovation**: 4/5
- **A-share Applicability**: 2/5
- **Key Params**: regime_threshold=0.25
- **Notes**: Macro regime framework; very US-centric with DXY/VIX/US10Y. Concept adaptable to A-shares by replacing with CSI300/CNY/HIBOR equivalents. High conceptual value for regime-aware trading.

### 4. Daily Bias 5-Min Pro Strategy
- **URL**: https://www.tradingview.com/script/kZzDTCDd-Daily-Bias-5-Min-by-sam86-live-com
- **Category**: multi_factor
- **Math Core**: 9-point scoring engine combining daily EMA200+ADX trend filter, DEMA crossover timing, Q-Trend structure, UT Bot confirmation, VWAP, opening range, supply/demand zones, and volume/delta signals
- **Innovation**: 4/5
- **A-share Applicability**: 3/5
- **Key Params**: ema_length=200, adx_length=14, dema_fast=9, dema_slow=21, atr_sl_mult=1.5
- **Notes**: Comprehensive multi-layer intraday system with score-based entry. Scoring engine concept highly portable to A-share 30-min bars. VWAP chop filter is useful for A-share market-making conditions.

### 5. USDJPY Fundamental Panel
- **URL**: https://www.tradingview.com/script/kdK4aRau
- **Category**: multi_factor
- **Math Core**: Aggregates 3 fundamental bias signals from 5 movers: DXY for USD, NZDJPY/EURJPY for JPY, US10Y/VIX for carry trade
- **Innovation**: 2/5
- **A-share Applicability**: 1/5
- **Notes**: FX-specific fundamental panel. Not applicable to A-share equities.

### 6. SL-Session Levels + VWAP + EMAs
- **URL**: https://www.tradingview.com/script/kdbOh7tF-SL-Session-Levels-VWAP-EMAs
- **Category**: trend
- **Math Core**: Combines previous day H/L, Asia/London session H/L, VWAP, and multiple EMAs for session-based level identification
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: session_times configurable, ema_periods configurable
- **Notes**: Session-level overlay designed for forex futures. Asia session concept applicable but needs adaptation for A-share 9:30-15:00 trading hours.

### 7. Cumulative Applied Force Differential
- **URL**: https://www.tradingview.com/script/keGsJUHD-Cumulative-Applied-Force-Differential
- **Category**: volume
- **Math Core**: Session-aligned cumulative delta comparison: stores bar-indexed cumulative delta arrays for current and previous session, computes differential at each timepoint to measure relative buying/selling force acceleration/deceleration
- **Innovation**: 5/5
- **A-share Applicability**: 4/5
- **Key Params**: atr_zone_classification, session_bar_alignment
- **Notes**: Extremely innovative microstructure concept. Compares today's cumulative buying/selling pressure vs yesterday's at each bar index. ATR zone classification adds context. Highly applicable to A-share intraday patterns where session structure repeats.

### 8. Support / Resistance Transparent Bands
- **URL**: https://www.tradingview.com/script/kg6eQuNf
- **Category**: price_action
- **Math Core**: Pivot-based S/R zones rendered as semi-transparent bands capturing the real reaction area including wicks and noise around key levels
- **Innovation**: 2/5
- **A-share Applicability**: 4/5
- **Key Params**: pivot_left=5, pivot_right=5
- **Notes**: Practical concept of zones vs lines for S/R. Works well for A-shares where price often probes levels with wicks before confirming. Simple but effective.

### 9. SRJ India VIX Widget
- **URL**: https://www.tradingview.com/script/kgljaX7P-SRJ-India-VIX-Widget
- **Category**: volatility
- **Math Core**: India VIX display widget correlating volatility index levels with market sentiment
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Notes**: India-specific VIX dashboard. Concept applicable (use iVIX for A-shares) but script itself is not portable.

### 10. Aegis Prime Flow
- **URL**: https://www.tradingview.com/script/kiBLyYBm
- **Category**: multi_factor
- **Math Core**: WaveTrend oscillator algorithm combined with Money Flow Cloud (smoothed liquidity filter), Kinetic Power Bars (heat map at +/-90 levels), and Aegis Reversal Signals for momentum exhaustion detection
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: wavetrend_period=10, wavetrend_avg=21, ob_level=60, os_level=-60
- **Notes**: WaveTrend is a proven oscillator (EMA of channel index). Money Flow Cloud adds institutional bias layer. Good fit for A-share daily timeframe where overbought/oversold extremes matter with 10% limits.

### 11. Recent IPO VWAP (<= 4yrs)
- **URL**: https://www.tradingview.com/script/kinWUvIY-Recent-IPO-VWAP-4yrs
- **Category**: volume
- **Math Core**: Anchored VWAP from IPO bar (bar_index==0) with 4-year age filter auto-hiding on established stocks
- **Innovation**: 3/5
- **A-share Applicability**: 5/5
- **Key Params**: max_ipo_age_days=1461
- **Notes**: Excellent for A-share newly listed stocks. IPO VWAP represents institutional cost basis. 4-year filter is smart decluttering. Directly portable to A-share market with active IPO market.

### 12. MI4P 50% Rule Book Level Indicator
- **URL**: https://www.tradingview.com/script/kmEDpXsv-MI4P-50-Rule-Book-Level-Indicator
- **Category**: multi_factor
- **Math Core**: SMC framework anchoring Institutional High/Low from higher timeframe (Weekly default), computing 50% equilibrium zone, with A+ signal overlay (price vs 9EMA crossover with >2x average volume confirmation)
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: anchor_tf="W", pivot_left=5, pivot_right=5, volume_mult=2.0
- **Notes**: Clean institutional structure framework. The 50% equilibrium between ITL-ITH is a powerful mean-reversion concept. A+ volume-confirmed momentum signals at structural levels work well on A-shares.

### 13. FOOTPRINT BY CTR 2.0
- **URL**: https://www.tradingview.com/script/ko2EQb4L-FOOTPRINT-BY-CTR-2-0
- **Category**: volume
- **Math Core**: Three-component system: (1) vertical footprint estimating buy/sell volume + delta from OHLCV, (2) trapped buyer/seller detection at candle extremes, (3) liquidity sweep detection with auto-deleting forward-projected sweep zones
- **Innovation**: 4/5
- **A-share Applicability**: 3/5
- **Key Params**: swing_lookback configurable, sweep_zone_validation
- **Notes**: Impressive footprint simulation from OHLCV alone (no tick data). Trapped trader identification is clever. Liquidity sweep zones auto-delete when invalidated. The buy/sell volume estimation is approximate but provides useful directional context for A-shares.

### 14. CPR D/W/M Bull/Bear Stacking + 9/15 EMA
- **URL**: https://www.tradingview.com/script/kq3kNktW-CPR-D-W-M-Bull-Bear-Stacking-9-15-EMA
- **Category**: trend
- **Math Core**: Multi-timeframe Central Pivot Range (D/W/M) with bullish stacking detection (Daily CPR > Weekly CPR > Monthly CPR) and EMA 9/15 momentum confirmation
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: ema_fast=9, ema_slow=15
- **Notes**: CPR stacking is a well-known concept but this implementation is clean. Works on A-shares where pivot levels from previous day/week/month are widely watched. EMA 9/15 adds entry timing.

### 15. Fibonacci MA Trend Gap V1
- **URL**: https://www.tradingview.com/script/l7erV7F1-Fibonacci-MA-Trend-Gap-V1
- **Category**: mean_reversion
- **Math Core**: Squared variance oscillator: (price - aggregate_mean)^2 where aggregate_mean is the composite of up to 17 Fibonacci-sequence-length MAs (2,3,5,8...4181). Includes auto-divergence detection and dual signal lines.
- **Innovation**: 4/5
- **A-share Applicability**: 5/5
- **Key Params**: ma_type=HMA, num_fib_mas=17, divergence_lookback=14
- **Notes**: Highly innovative use of the full Fibonacci sequence as MA periods. The squared variance from the composite Fibonacci mean creates a statistically grounded overextension measure. 7 MA types available. Auto-divergence adds value. Excellent for A-share mean-reversion at 10% limit extremes.

### 16. Relevant Swings ICT Full Coverage
- **URL**: https://www.tradingview.com/script/l9ZBVMrP-Relevant-Swings-ICT-Full-Coverage
- **Category**: price_action
- **Math Core**: ICT-style swing detection with full coverage of internal/institutional swing highs/lows using configurable lookback periods
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Notes**: Standard ICT swing structure. Useful for A-share swing trading but conceptually common.

### 17. lBWgvwsb
- **URL**: https://www.tradingview.com/script/lBWgvwsb
- **Category**: [Fetch Failed - insufficient description]
- **Math Core**: Unknown - only hash ID available, page content not descriptive
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Notes**: [Fetch Failed] - URL slug has no descriptive name. Could not determine strategy type.

### 18. CPI Buy Sell Stop
- **URL**: https://www.tradingview.com/script/lNz4KGtR-CPI-Buy-Sell-Stop
- **Category**: trend
- **Math Core**: CPI (Cumulative Price Index) based buy/sell/stop signal generation with trend-following logic
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Notes**: Price-action based signal system. Moderately applicable to A-shares.

### 19. ORB 1 Hour High Low Alert EMA SMA
- **URL**: https://www.tradingview.com/script/lODBOB7a-ORB-1-Hour-High-Low-Alert-EMA-SMA
- **Category**: trend
- **Math Core**: Opening Range Breakout using first hour high/low levels with EMA/SMA confirmation for breakout validation
- **Innovation**: 2/5
- **A-share Applicability**: 4/5
- **Key Params**: orb_period=60min, ema_period=9, sma_period=21
- **Notes**: Classic ORB strategy. Directly applicable to A-shares using 9:30-10:30 as opening range. Works well with 10% daily limit structure.

### 20. lUs0AwDw
- **URL**: https://www.tradingview.com/script/lUs0AwDw
- **Category**: [Fetch Failed - insufficient description]
- **Math Core**: Unknown - only hash ID available
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Notes**: [Fetch Failed] - URL slug has no descriptive name.

### 21. Buy and Sell Type Splish 2
- **URL**: https://www.tradingview.com/script/lZhwMoMt-Buy-and-Sell-Type-Splish-2
- **Category**: mean_reversion
- **Math Core**: Buy/sell signal classification with type differentiation (trend vs reversal signals)
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Notes**: Categorization of buy/sell signals by type. Useful concept for signal quality filtering.

### 22. ES Breakout Toolkit Momentum Close Filter
- **URL**: https://www.tradingview.com/script/lfxfpdpx-ES-Breakout-Toolkit-Momentum-Close-Filter-Free
- **Category**: trend
- **Math Core**: Breakout toolkit with momentum-based close filter for ES futures, combining range breakout detection with momentum confirmation to filter false breakouts
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Notes**: Designed for ES but breakout-with-momentum-confirmation concept is universal. Adaptable to A-share index futures or equity breakouts.

### 23. ljPGHpNG
- **URL**: https://www.tradingview.com/script/ljPGHpNG
- **Category**: [Fetch Failed - insufficient description]
- **Math Core**: Unknown - only hash ID available
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Notes**: [Fetch Failed] - URL slug has no descriptive name.

### 24. llG7zzaP
- **URL**: https://www.tradingview.com/script/llG7zzaP
- **Category**: [Fetch Failed - insufficient description]
- **Math Core**: Unknown - only hash ID available
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Notes**: [Fetch Failed] - URL slug has no descriptive name.

### 25. Lion Share Trading Structure
- **URL**: https://www.tradingview.com/script/llNOIbcG-Lion-Share-Trading-Structure
- **Category**: price_action
- **Math Core**: Market structure mapping tool identifying swing points, BOS (break of structure), and CHoCH (change of character) for trend direction
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Notes**: Standard SMC/ICT market structure tool. BOS/CHoCH detection applicable to any market including A-shares.

### 26. Fractal Advanced Divergence
- **URL**: https://www.tradingview.com/script/lnvrkL80-Fractal-Advanced-Divergence
- **Category**: mean_reversion
- **Math Core**: Fractal pivot detection ON the oscillator itself (not price), then checks divergence at oscillator fractals with: (1) independent P1/P2 OB/OS zone filtering, (2) trendline intersection validation on both price and oscillator axes, (3) external indicator input mode for custom oscillator pipes. Supports RSI/CCI/Stochastic/MACD/External.
- **Innovation**: 5/5
- **A-share Applicability**: 5/5
- **Key Params**: fractal_lookback=2, os_p1=30, os_p2=30, ob_p1=70, ob_p2=70, max_pivots=30, min_bars_between=5, validate_intersection=true
- **Notes**: Exceptionally well-engineered divergence system. Finding fractals on the oscillator (not price) produces cleaner pivots. Trendline intersection validation eliminates structurally broken divergences. External input mode allows piping any custom oscillator. Ghost signal visualization for research. Highly applicable to A-shares - the rigorous filtering reduces false signals common in choppy A-share markets.

### 27. Delta Histogram
- **URL**: https://www.tradingview.com/script/ltrgx3kE-Delta-Histogram
- **Category**: volume
- **Math Core**: Delta histogram visualization showing net buying vs selling pressure per bar, estimated from OHLCV data
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Notes**: Standard delta estimation from candle structure. Useful for visual order flow context on A-share daily bars.

### 28. Short Volume Dynamic Safe
- **URL**: https://www.tradingview.com/script/m09cxkI0-Short-Volume-Dynamic-Safe
- **Category**: volume
- **Math Core**: Short volume analysis with dynamic safety thresholds, tracking short selling activity relative to total volume
- **Innovation**: 2/5
- **A-share Applicability**: 1/5
- **Notes**: US-market specific (FINRA short volume data). A-share short selling data is not readily available in same format.

### 29. Pure PA MS System
- **URL**: https://www.tradingview.com/script/m5UKrZxf-Pure-PA-MS-System
- **Category**: price_action
- **Math Core**: Pure price action market structure system identifying swing points, internal/external structure, and directional bias without indicators
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Notes**: Clean indicator-free structure analysis. Applicable universally including A-shares for swing trading structure identification.

### 30. mPR4WJca
- **URL**: https://www.tradingview.com/script/mPR4WJca
- **Category**: [Fetch Failed - insufficient description]
- **Math Core**: Unknown - only hash ID available
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Notes**: [Fetch Failed] - URL slug has no descriptive name.

## Highlights

Top 5 most innovative strategies (Innovation >= 4):

1. **Cumulative Applied Force Differential** (5/5) - Revolutionary session-aligned cumulative delta comparison measuring inter-session buying/selling force differentials. Best innovation in this batch.

2. **Fractal Advanced Divergence** (5/5) - Exceptionally engineered divergence system with oscillator-based fractal pivots, trendline intersection validation on both axes, and external indicator pipe mode. A research-grade tool.

3. **Fibonacci MA Trend Gap V1** (4/5) - Squared variance from composite 17-period Fibonacci MA aggregate creates statistically grounded overextension measure. Novel use of full Fibonacci sequence as MA periods.

4. **TORINVEST Macro Technical** (4/5) - Multi-layer regime scoring combining Risk-On/Off assets, macro fundamentals, and technicals into a single actionable regime framework. Concept adaptable to A-shares.

5. **Daily Bias 5-Min Pro Strategy** (4/5) - Comprehensive 9-point scoring engine combining trend/momentum/zone/volume/timing into score-based entry system with VWAP chop filter. Scoring engine architecture is highly portable.

Also notable: **FOOTPRINT BY CTR 2.0** (4/5) - Impressive three-component order flow simulation from OHLCV data alone.
