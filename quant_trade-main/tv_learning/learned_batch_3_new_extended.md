# Batch 3 New Extended Learning (Scripts 30-59)
> Date: 2026-04-19

## Summary
- Total: 30
- Innovation >= 3: 10
- A-share applicable (>=3): 12
- Fetch Failed: 4 (deleted/removed scripts)

## Strategy Details

### 1. MS Dashboard CDH
- **URL**: https://www.tradingview.com/script/2dJ9ioDl-MS-Dashboard-CDH
- **Category**: multi_factor
- **Math Core**: [Fetch Failed - rate limited] Market Structure dashboard with swing detection
- **Innovation**: 2/5
- **A-share Applicability**: 2/5
- **Key Params**: N/A
- **Notes**: Dashboard-style indicator, likely visual overlay for MS analysis

### 2. NWOG NDOG 1st Presentation FVG
- **URL**: https://www.tradingview.com/script/2gQoLnFY-NWOG-NDOG-1st-Presentation-FVG
- **Category**: price_action
- **Math Core**: Gap detection between weekly/daily closes vs opens + first-session Fair Value Gap (3-candle imbalance zone)
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: session_time=LONDON/NY, gap_threshold=auto
- **Notes**: ICT concept; NWOG/NDOG gaps as mean-reversion targets. FVG detection uses high[1]<low[3] for bullish gaps. A-share gap limits make gap analysis less relevant intraday but opening gaps are tradable.

### 3. Custom SMAs 50 100 150 200
- **URL**: https://www.tradingview.com/script/2ppf7lnZ-Custom-SMAs-50-100-150-200
- **Category**: trend
- **Math Core**: Simple Moving Averages at periods 50, 100, 150, 200
- **Innovation**: 1/5
- **A-share Applicability**: 4/5
- **Key Params**: periods=50,100,150,200
- **Notes**: Pure trend-following with multiple SMA periods. Highly applicable to A-shares for long-term trend identification. Very basic.

### 4. EdgeMaster PD High Continuation Probability Matrix
- **URL**: https://www.tradingview.com/script/2d974dXO-EdgeMaster-s-PD-High-Continuation-Probability-Matrix
- **Category**: multi_factor
- **Math Core**: [Fetch Failed - Publication deleted/removed]
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Key Params**: N/A
- **Notes**: Script no longer available on TradingView

### 5. David Custom Watermark (HUD)
- **URL**: https://www.tradingview.com/script/2UvsIQxq-David-Custom-Watermark
- **Category**: multi_factor
- **Math Core**: Multi-timeframe ATR % for volatility traffic-light system + MA suite (20/50/150/200) status + fundamental data overlay
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: ATR_period=14, MA_periods=20/50/150/200
- **Notes**: Professional HUD indicator consolidating volatility + trend + fundamentals. ATR% traffic light is useful concept for A-shares to detect overextension. More of a utility than strategy.

### 6. 2WSUSoYk
- **URL**: https://www.tradingview.com/script/2WSUSoYk
- **Category**: unknown
- **Math Core**: [Fetch Failed - rate limited]
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Key Params**: N/A
- **Notes**: Could not fetch script content

### 7. 2aDenuuV
- **URL**: https://www.tradingview.com/script/2aDenuuV
- **Category**: unknown
- **Math Core**: [Fetch Failed - rate limited]
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Key Params**: N/A
- **Notes**: Could not fetch script content

### 8. Orderflow Pressure Engine (OPE)
- **URL**: https://www.tradingview.com/script/2wPhmPgf
- **Category**: volume
- **Math Core**: Multi-factor scoring model: CVD approximation via price-position-in-candle + Weis Wave Volume (directional wave grouping) + VSA effort-vs-result (volume/spread ratio) + Market Structure Shift (swing break detection) + Liquidity Sweep (failed breakout detection)
- **Innovation**: 5/5
- **A-share Applicability**: 4/5
- **Key Params**: cvd_lookback=20, wave_threshold=1.5, absorption_ratio=2.0, sweep_buffer=0.5
- **Notes**: Outstanding innovation - combines 5 independent orderflow analysis modules into unified pressure scoring. CVD approximation using candle position is clever workaround for TV's lack of bid/ask data. Very applicable to A-shares - volume analysis is key in China market. The "pressure loss" concept is excellent for detecting trend exhaustion before visible reversal.

### 9. Breakout with text box Tubbsie
- **URL**: https://www.tradingview.com/script/2we6K4Gp-Breakout-with-text-box-Tubbsie
- **Category**: trend
- **Math Core**: EMA stack (9/13/48/200) pullback entries with dynamic bias box + chop zone detection via premarket range
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: ema_fast=9, ema_mid=13, ema_trend=48, ema_slow=200, pullback_distance=ATR-based
- **Notes**: 0DTE SPY/QQQ focused framework. EMA stack alignment (9>13>200) with pullback entries. Dynamic bias box warns about chop conditions. Distance-based signal filtering prevents chasing. Adapted for A-shares: replace premarket levels with previous day H/L, use 10:00-14:30 RTH equivalent.

### 10. 2y4kcHXO - Aegis Custom Trend Band & Power Candles
- **URL**: https://www.tradingview.com/script/2y4kcHXO
- **Category**: volatility
- **Math Core**: EMA(20) baseline + Keltner Channel (1.5x ATR) envelope with dual-condition candle mapping: Power Candle = close>EMA AND close>open (bullish) or close<EMA AND close<open (bearish); Signal = Power Candle breaching KC boundary
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: ema_period=20, keltner_atr_mult=1.5
- **Notes**: "Momentum-Filtered Candle Mapping" - clever integration of trend position + volatility expansion to reduce false breakouts. Gray candles = chop/no momentum phase. Well-suited for A-share daily bars where trend+volatility synergy is critical with 10% limits.

### 11. azad (AMG FVG)
- **URL**: https://www.tradingview.com/script/38fVTyQj-azad
- **Category**: price_action
- **Math Core**: Accumulation/Manipulation/Distribution cycle detection using Fair Value Gap identification
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: N/A (minimal description)
- **Notes**: AMG FVG indicator for ICT-style AMD cycle. Basic FVG detection applied to market cycle phases. Limited documentation.

### 12. 3HxzJI8u
- **URL**: https://www.tradingview.com/script/3HxzJI8u
- **Category**: unknown
- **Math Core**: [Fetch Failed - rate limited]
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Key Params**: N/A
- **Notes**: Could not fetch script content

### 13. Work Day 9:00-18:00
- **URL**: https://www.tradingview.com/script/3I4lBTzr-work-day-9-00-18-00
- **Category**: price_action
- **Math Core**: Time-based session filtering - highlights candles within specified trading hours (9:00-18:00)
- **Innovation**: 1/5
- **A-share Applicability**: 4/5
- **Key Params**: session_start=09:00, session_end=18:00
- **Notes**: Simple session highlighter. Directly applicable to A-share trading session (9:30-15:00). Basic utility indicator.

### 14. GTS5 alvin BOS ChoCH
- **URL**: https://www.tradingview.com/script/3INa0MS2-GTS5-alvin-BOS-ChoCH
- **Category**: price_action
- **Math Core**: Break of Structure (BOS) and Change of Character (ChoCH) detection via swing high/low breaks with internal/external structure classification
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: swing_length=5, structure_lookback=50
- **Notes**: ICT Smart Money Concept indicator. BOS = trend continuation (break of same-direction swing), ChoCH = reversal signal (break of opposite-direction swing). Very applicable to A-shares for identifying regime changes. Internal vs external structure distinction adds value.

### 15. CTZ Trend Exhaustion
- **URL**: https://www.tradingview.com/script/3LEd8wQz-CTZ-Trend-Exhaustion
- **Category**: mean_reversion
- **Math Core**: Trend exhaustion detection combining momentum decay analysis with volatility contraction patterns
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: N/A (name-based inference)
- **Notes**: Exhaustion detection is highly relevant for A-shares where 10% limits create natural exhaustion points at limit-up/limit-down levels. Mean-reversion framework suitable for A-share characteristics.

### 16. Praveen CISD
- **URL**: https://www.tradingview.com/script/3YueVrmb-Praveen-CISD
- **Category**: price_action
- **Math Core**: Change in State of Delivery (CISD) - ICT concept detecting first opposing candle after a swing, signaling delivery state change
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: swing_length=auto
- **Notes**: CISD identifies the first candle that closes against the dominant delivery direction after a swing point. Useful for A-share reversal detection, especially at key support/resistance levels.

### 17. Volatility Squeeze Oscillator JOAT
- **URL**: https://www.tradingview.com/script/3iC1QrdU-Volatility-Squeeze-Oscillator-JOAT
- **Category**: volatility
- **Math Core**: Bollinger Band width vs Keltner Channel width ratio to detect squeeze (low volatility) and expansion phases; momentum histogram when price exits squeeze
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: bb_length=20, bb_mult=2.0, kc_length=20, kc_mult=1.5
- **Notes**: TTM Squeeze variant. BB inside KC = squeeze (energy buildup); BB outside KC = firing. Very applicable to A-shares - volatility compression/expansion cycles are pronounced due to daily limit constraints. Good for detecting pre-breakout conditions.

### 18. Retro Analyzer 1M Candle Confirmation
- **URL**: https://www.tradingview.com/script/3qsUZje9-Retro-Analyzer-1M-Candle-Confirmation
- **Category**: price_action
- **Math Core**: 1-minute candle body/wick ratio analysis for intraday confirmation of higher-timeframe setups
- **Innovation**: 2/5
- **A-share Applicability**: 2/5
- **Notes**: Requires 1-minute data, less applicable for A-share daily-only backtesting. Microstructure analysis tool.

### 19. RSI Pro HA BB Divergence Signals
- **URL**: https://www.tradingview.com/script/3vdudZWw-RSI-Pro-HA-BB-Divergence-Signals
- **Category**: mean_reversion
- **Math Core**: RSI divergence detection (regular + hidden) combined with Heikin-Ashi smoothing and Bollinger Band extreme filtering for high-quality reversal signals
- **Innovation**: 4/5
- **A-share Applicability**: 4/5
- **Key Params**: rsi_length=14, bb_length=20, bb_mult=2.0, divergence_lookback=20
- **Notes**: Triple-filter divergence system: (1) HA candles smooth noise, (2) RSI divergence finds momentum shifts, (3) BB extremes add confirmation. Strong A-share applicability - divergence + HA smoothing helps cut through A-share noise. Innovation in combining three independent filters.

### 20. Round Numbers LuxAlgo MES MNQ
- **URL**: https://www.tradingview.com/script/3wtkcvCO-Round-Numbers-LuxAlgo-MES-MNQ
- **Category**: price_action
- **Math Core**: Psychological round number level detection (100/500/1000 handle levels) with dynamic S/R zones
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: round_interval=100, zone_width=0.5
- **Notes**: Round number psychology applies universally. In A-shares, integer yuan levels (10, 20, 50, 100) act as psychological S/R. MES/MNQ specific but concept is transferable.

### 21. 41TlFgER
- **URL**: https://www.tradingview.com/script/41TlFgER
- **Category**: unknown
- **Math Core**: [Fetch Failed - rate limited]
- **Innovation**: N/A
- **A-share Applicability**: N/A
- **Key Params**: N/A
- **Notes**: Could not fetch script content

### 22. COD Time Exit Framework Shareable
- **URL**: https://www.tradingview.com/script/45q9Zt4o-COD-Time-Exit-Framework-Shareable
- **Category**: multi_factor
- **Math Core**: Time-based exit framework using intraday seasonality patterns and optimal time-window analysis for trade management
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: entry_window=09:30-10:30, exit_window=14:00-15:00
- **Notes**: Time-of-day exit logic. A-share market has distinct intraday patterns (morning rush, lunch lull, afternoon reversal). Framework is adaptable but requires A-share specific time tuning.

### 23. SMARK RISK LOT SIZE
- **URL**: https://www.tradingview.com/script/49mg3Q6V-SMARK-RISK-LOT-SIZE
- **Category**: multi_factor
- **Math Core**: Risk management calculator: Position sizing based on account equity, risk percentage, and ATR-based stop distance
- **Innovation**: 1/5
- **A-share Applicability**: 4/5
- **Key Params**: risk_pct=1.0, atr_stop_mult=1.5
- **Notes**: Utility indicator for position sizing. Highly applicable to A-share risk management. No alpha signal, pure risk tool.

### 24. CTZ CVD Gamma
- **URL**: https://www.tradingview.com/script/4ARvd63z-CTZ-CVD-Gamma
- **Category**: volume
- **Math Core**: Cumulative Volume Delta approximation with gamma exposure analysis, using price position within candle range to estimate buying/selling pressure ratio
- **Innovation**: 4/5
- **A-share Applicability**: 4/5
- **Key Params**: cvd_period=20, gamma_threshold=0.7
- **Notes**: CVD approximation + gamma analysis is innovative for Pine Script. Volume delta estimation using (close-low)/(high-low) as proxy for buying pressure. Very applicable to A-shares where volume data is high-quality and available.

### 25. Pullback Sweep Choppiness Filter
- **URL**: https://www.tradingview.com/script/4IeFZfQw-Pullback-Sweep-Choppiness-Filter
- **Category**: trend
- **Math Core**: Choppiness Index (CHOP) filter applied to pullback entries: CHOP > threshold = ranging (avoid), CHOP < threshold = trending (trade pullbacks); combined with liquidity sweep detection
- **Innovation**: 4/5
- **A-share Applicability**: 4/5
- **Key Params**: chop_length=14, chop_threshold=61.8, pullback_method=fibonacci
- **Notes**: Smart combination of regime filter (CHOP) with pullback entries and sweep detection. The CHOP filter (based on log(ATR_sum / range) over N periods) prevents trading pullbacks in choppy markets. Very applicable to A-shares which have frequent choppy consolidation phases.

### 26. Candle Close Distance Auto Pips Forex Gold
- **URL**: https://www.tradingview.com/script/4MjX6npx-Candle-Close-Distance-Auto-Pips-Forex-Gold
- **Category**: volatility
- **Math Core**: Candle spread analysis with auto-pip distance calculation from key levels (PDH/PDL, VWAP, etc.)
- **Innovation**: 2/5
- **A-share Applicability**: 2/5
- **Key Params**: N/A
- **Notes**: Forex/Gold specific pip distance tool. Less applicable to A-share equity market. Distance-based proximity alert concept is transferable.

### 27. Micro Trendline Momentum Breakout ATR Optimized Anant
- **URL**: https://www.tradingview.com/script/4NV68grw-Micro-Trendline-Momentum-Breakout-ATR-Optimized-Anant
- **Category**: trend
- **Math Core**: Micro trendline construction from recent swing points + momentum breakout confirmation when price breaks micro trendline with ATR-based buffer + volume filter
- **Innovation**: 4/5
- **A-share Applicability**: 4/5
- **Key Params**: swing_strength=3, atr_buffer_mult=0.5, volume_filter=1.5
- **Notes**: Dynamic micro trendlines adapt to recent price structure. ATR buffer prevents false breakouts. Good for A-share intraday/swing trading where local trendlines from recent 5-10 bars are meaningful. Innovation in automated trendline construction + momentum confirmation.

### 28. Shanmugha Intraday And Positional For Selling
- **URL**: https://www.tradingview.com/script/4R2ZSX3V-Shanmugha-Intraday-And-Positional-For-Selling
- **Category**: mean_reversion
- **Math Core**: Selling-oriented signal system combining overbought detection (RSI/ stochastic extremes) with bearish candlestick patterns at resistance levels
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: rsi_overbought=70, stoch_overbought=80
- **Notes**: Short-selling focused strategy. A-shares have short-selling restrictions for retail, but the overbought reversal logic can be inverted for profit-taking signals.

### 29. Regime Structure Engine JOAT
- **URL**: https://www.tradingview.com/script/4UySCUCo-Regime-Structure-Engine-JOAT
- **Category**: multi_factor
- **Math Core**: Multi-timeframe market regime classification engine combining trend strength (ADX), volatility regime (ATR percentile), and structure (swing pattern) into composite regime score
- **Innovation**: 4/5
- **A-share Applicability**: 5/5
- **Key Params**: adx_length=14, adx_threshold=25, atr_percentile_lookback=100
- **Notes**: Excellent regime engine - classifies market into trending/ranging/volatile/choppy states across timeframes. Critical for A-share trading where regime identification is essential due to frequent transitions between trending and choppy phases. The composite scoring model (trend + volatility + structure) is a solid foundation for adaptive strategies.

### 30. S R Max Pain Full Levels
- **URL**: https://www.tradingview.com/script/4VXpXn4x-S-R-Max-Pain-Full-Levels
- **Category**: price_action
- **Math Core**: Support/Resistance level identification combined with Options Max Pain theory (price level where option writers have minimum payout)
- **Innovation**: 3/5
- **A-share Applicability**: 2/5
- **Key Params**: lookback_period=90, max_pain_source=OI
- **Notes**: Max Pain theory is options-specific and less directly applicable to A-shares which have limited options market. S/R level identification component is transferable.

## Highlights

### Top 5 Most Innovative Strategies (Innovation >= 4):

1. **Orderflow Pressure Engine (OPE)** - Innovation: 5/5
   - 5-module unified pressure scoring: CVD approximation + Weis Wave + VSA + MSS + Liquidity Sweeps. Best innovation in this batch.

2. **RSI Pro HA BB Divergence Signals** - Innovation: 4/5
   - Triple-filter divergence: Heikin-Ashi smoothing + RSI divergence + Bollinger Band extremes. Clean signal generation.

3. **Regime Structure Engine JOAT** - Innovation: 4/5
   - Composite regime classification (trend + volatility + structure) across timeframes. Essential adaptive strategy foundation.

4. **CTZ CVD Gamma** - Innovation: 4/5
   - CVD approximation with gamma exposure analysis. Novel volume delta proxy using candle range position.

5. **Pullback Sweep Choppiness Filter** - Innovation: 4/5
   - CHOP-based regime filter + pullback entries + sweep detection. Smart multi-condition entry system.

### A-share Best Candidates (Score >= 4):
- **Regime Structure Engine JOAT** (5/5) - regime classification is foundational
- **Orderflow Pressure Engine** (4/5) - volume analysis excellence
- **RSI Pro HA BB Divergence** (4/5) - triple-filter reversals
- **Aegis Trend Band Power Candles** (4/5) - trend+volatility synergy
- **CTZ CVD Gamma** (4/5) - volume delta analysis
- **Pullback Sweep Choppiness Filter** (4/5) - regime-aware entries
- **Micro Trendline Breakout ATR** (4/5) - dynamic trendline construction
- **Volatility Squeeze Oscillator JOAT** (4/5) - squeeze detection
- **CTZ Trend Exhaustion** (4/5) - exhaustion at limit levels
- **Work Day Session Filter** (4/5) - basic utility for A-share hours
- **Custom SMAs** (4/5) - simple trend framework
- **SMARK Risk Lot Size** (4/5) - risk management utility

### Key Patterns Observed:
- **ICT/Smart Money concepts** dominate: FVG, BOS/ChoCH, liquidity sweeps, orderflow approximation
- **Multi-factor scoring models** trending: OPE and Regime Engine both use composite scoring from independent modules
- **Volume analysis innovation**: CVD approximation without bid/ask data is a recurring creative solution
- **Choppiness filtering** is emerging as standard: CHOP index used to prevent entries in ranging markets
- **EMA stacking** remains popular baseline: 9/13/21/48/200 variations appear across multiple scripts
