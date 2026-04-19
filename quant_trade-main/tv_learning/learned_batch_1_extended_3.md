# Batch 1 Extended Learning 3 (Scripts 90-120)
> Date: 2026-04-19

## Summary
- Total: 31
- Fetched: 8
- Fetch Failed: 23
- Innovation >= 3: 3
- A-share applicable (>=3): 5

## Strategy Details

### 1. Gold Swing More Trades 50 SL 100 TP
- **URL**: https://www.tradingview.com/script/8b1AgVrV-Gold-Swing-More-Trades-50-SL-100-TP
- **Category**: trend
- **Math Core**: EMA 20/50 crossover trend filter + RSI(58/42) confirmation. Fixed 0.1 lot, 50 pip SL, triple TP at 100/150/250 pips
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: EMA 20/50, RSI 58/42, 50 pip SL, 100/150/250 pip TP
- **Notes**: Basic EMA crossover + RSI strategy. Backtested on 1H Gold with 40.97% win rate, PF 1.386. The EMA+RSI logic is applicable to A-shares, but pip-based SL/TP needs conversion to percentage-based stops (considering 10% daily limit).

### 2. Stock Checklist Indicator
- **URL**: https://www.tradingview.com/script/8biF57mN-Stock-Checklist-Indicator
- **Category**: trend
- **Math Core**: Momentum stock checklist following Camel Finance methodology. Multiple trend criteria displayed as a dashboard
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: Trend analysis checklist criteria
- **Notes**: Educational momentum stock screening tool. Works across all asset classes. The checklist approach is useful for A-share stock screening but would need adaptation for A-share specific indicators (e.g., replacing S&P 500 benchmark with CSI 300).

### 3. Hexatap
- **URL**: https://www.tradingview.com/script/8f041qcZ-Hexatap
- **Category**: price_action
- **Math Core**: 6-point reversal pattern detector: scans swing points confirming trending structure (3 ascending highs / 3 descending lows), identifies supply/demand zones, validates liquidity sweeps. Fibonacci 0.382-0.618 golden ratio entry zones. ATR-based noise filtering for swing detection
- **Innovation**: 4/5
- **A-share Applicability**: 4/5
- **Key Params**: Swing Lookback, Min Swing Size (ATR), Zone Sweep Threshold, Zone Extend bars, Fibonacci levels (0.382, 0.500, 0.618, 0.786)
- **Notes**: Sophisticated pattern recognition combining structure breaks, supply/demand zones, and Fibonacci golden ratio entries. A+/A- setup grading adds quality filtering. Very applicable to A-shares as it uses only OHLCV data and swing point analysis. Works on any timeframe. The 6-point structure (initial range -> break -> sweep -> re-sweep -> entry) is a clean formalization of smart money concepts.

### 4. AVS VWAP EMA Pullback Pro
- **URL**: https://www.tradingview.com/script/8iyycJbD-AVS-VWAP-EMA-Pullback-Pro
- **Category**: trend
- **Math Core**: VWAP + EMA trend definition (price > VWAP + fast EMA > slow EMA for longs), pullback to VWAP/EMA zone with reclaim/rejection + RSI confirmation, ADX/DMI chop filter (minimum ADX threshold), session time filter (07:00-20:00), ATR-based stops, dual TP via qty_percent split
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: Fast/Slow EMA periods, VWAP, ADX minimum threshold (~18-22), RSI confirmation level, session window, ATR multiplier for SL, TP1/TP2 levels
- **Notes**: Well-structured intraday trend following system. The VWAP pullback + ADX filter combination reduces choppy trades. For A-shares, would need session adjustment to 9:30-15:00 CST. VWAP calculation from OHLCV is straightforward. Dual TP approach (partial + runner) is sound risk management.

### 5. ORB Sessions London New York Asia
- **URL**: https://www.tradingview.com/script/9M9NwqsX-ORB-Sessions-London-New-York-Asia-Zyntra
- **Category**: price_action
- **Math Core**: Opening Range Breakout - marks High and Low of first 15-minute candle per session (London 09:00 CET, NY 15:30 CET, Asia/Tokyo 01:00-02:00 CET). Automatic daylight saving adjustment for Asia session
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: Session start times, 15-min chart, auto DST adjustment
- **Notes**: Clean ORB implementation for 3 major forex sessions. For A-shares, the concept of opening range breakout is highly relevant - A-share market opens at 9:30 CST with first 15-30 minutes establishing the initial range. Would need session time adaptation but the logic transfers directly.

### 6. JPM Collar Levels + PDL and PWH Levels
- **URL**: https://www.tradingview.com/script/9UrphCSc-JPM-Collar-Levels-PDL-and-PWH-Levels
- **Category**: options
- **Math Core**: JP Morgan Hedged Equity quarterly collar: sell OTM call ~3-5% above S&P 500, buy put spread for downside protection. Creates defined-range payoff profile. Displays collar levels with PDL (Previous Day Low) and PWH (Previous Week High)
- **Innovation**: 2/5
- **A-share Applicability**: 1/5
- **Key Params**: Quarterly collar strikes, 3-5% OTM call, put spread levels
- **Notes**: S&P 500 specific institutional options strategy. Not applicable to A-shares which lack liquid individual stock options and have different market structure. The PDL/PWH concept is universal but the collar strategy itself is US-market specific.

### 7. 9ZO0Wa08
- **URL**: https://www.tradingview.com/script/9ZO0Wa08
- **Category**: unknown
- **Math Core**: [Fetch Failed]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

### 8. 9cckfn7S
- **URL**: https://www.tradingview.com/script/9cckfn7S
- **Category**: unknown
- **Math Core**: [Fetch Failed]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

### 9. HA Signals on Regular Candles
- **URL**: https://www.tradingview.com/script/9ewY0OQg-author-strategy-ha-signals-on-regular-candles
- **Category**: trend
- **Math Core**: Chandelier Exit + Zero-Lag SMMA (Smoothed Moving Average). Heikin Ashi signals calculated on HA candles, entries executed on regular candles. Long: buy signal + price above ZL SMMA, stop below signal candle. Short: sell signal + price below ZL SMMA, stop above signal candle. Exit on cross of ZL SMMA
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: Chandelier Exit period/multiplier, ZL SMMA period, HA signal detection
- **Notes**: Smart dual-candle approach: use HA's noise-filtered signals for direction, regular candles for realistic execution. The Chandelier Exit provides dynamic trailing stops. ZL SMMA (zero-lag smoothed MA) reduces lag. Highly applicable to A-shares as it only uses OHLCV data and produces clean trend-following signals.

### 10. Stage 2 RS Volume Accumulation
- **URL**: https://www.tradingview.com/script/9mzlyP6T-Stage-2-RS-Volume-Accumulation
- **Category**: unknown
- **Math Core**: [Fetch Failed]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

### 11. Sequential Momentum
- **URL**: https://www.tradingview.com/script/9oVVEqwQ-Sequential-Momentum
- **Category**: unknown
- **Math Core**: [Fetch Failed]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

### 12. 9t1cCTAv
- **URL**: https://www.tradingview.com/script/9t1cCTAv
- **Category**: unknown
- **Math Core**: [Fetch Failed]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

### 13. CTZ BTC Cost Of Production
- **URL**: https://www.tradingview.com/script/9yE5Qgjw-CTZ-BTC-Cost-Of-Production
- **Category**: fundamental
- **Math Core**: [Fetch Failed] - Bitcoin mining cost of production model
- **Innovation**: 2/5
- **A-share Applicability**: 1/5

### 14. Key Levels H L Opens
- **URL**: https://www.tradingview.com/script/A52MLFdv-Key-Levels-H-L-Opens
- **Category**: price_action
- **Math Core**: [Fetch Failed] - Key levels from High/Low/Open prices
- **Innovation**: 1/5
- **A-share Applicability**: 2/5

### 15. Financial Freedom
- **URL**: https://www.tradingview.com/script/A8jEErM6-Financial-Freedom
- **Category**: pivot
- **Math Core**: Previous Day High (green), Previous Day Low (red), 50% midpoint level (yellow). Simple pivot-style level indicator
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: Previous day OHLC
- **Notes**: Very basic PDH/PDL/50% level indicator. These levels are universally applicable and provide useful reference points, but the implementation is trivial.

### 16. EMA 5 13 Crossover Indicator
- **URL**: https://www.tradingview.com/script/AJi0VNrZ-EMA-5-13-Crossover-Indicator
- **Category**: trend
- **Math Core**: [Fetch Failed] - EMA 5/13 crossover signals
- **Innovation**: 1/5
- **A-share Applicability**: 2/5

### 17. Custom Period Separator 3H 1D
- **URL**: https://www.tradingview.com/script/AMTLfoEf-Custom-Period-Separator-3H-1D
- **Category**: utility
- **Math Core**: [Fetch Failed] - Period separator lines at 3H and 1D intervals
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

### 18. GANN Wheel Square of Nine KG
- **URL**: https://www.tradingview.com/script/AQ3mVNut-GANN-Wheel-Square-of-Nine-KG
- **Category**: gann
- **Math Core**: [Fetch Failed] - Gann Wheel / Square of Nine calculation
- **Innovation**: 3/5
- **A-share Applicability**: 2/5

### 19. Conflux 4
- **URL**: https://www.tradingview.com/script/ARBm4EWj-Conflux-4
- **Category**: unknown
- **Math Core**: [Fetch Failed]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

### 20. Murphy Timeframe Lens
- **URL**: https://www.tradingview.com/script/AWaMc5gi-Murphy-Timeframe-Lens
- **Category**: multi_tf
- **Math Core**: [Fetch Failed] - Multi-timeframe analysis lens (likely John Murphy MTF approach)
- **Innovation**: 2/5
- **A-share Applicability**: 2/5

### 21. Daye's True Opens Quarterly Theory
- **URL**: https://www.tradingview.com/script/AWcPTIRa-Daye-s-True-Opens-Quarterly-Theory
- **Category**: price_action
- **Math Core**: [Fetch Failed] - Quarterly opening price theory / true opens
- **Innovation**: 2/5
- **A-share Applicability**: 2/5

### 22. amit EMA Breakdown Pullback SELL
- **URL**: https://www.tradingview.com/script/AWyaFjIj-amit-EMA-Breakdown-Pullback-SELL
- **Category**: trend
- **Math Core**: [Fetch Failed] - EMA breakdown pullback short strategy
- **Innovation**: 2/5
- **A-share Applicability**: 3/5

### 23. Fed Chair Changes Daily Returns
- **URL**: https://www.tradingview.com/script/AamnXoon-Fed-Chair-Changes-Daily-Returns-1-3-6-12-months
- **Category**: fundamental
- **Math Core**: [Fetch Failed] - Fed Chair change impact on daily returns across timeframes
- **Innovation**: 2/5
- **A-share Applicability**: 1/5

### 24. Bookmap Traps
- **URL**: https://www.tradingview.com/script/AhH1CM72-Bookmap-Traps
- **Category**: orderflow
- **Math Core**: [Fetch Failed] - Order flow trap detection (Bookmap-style)
- **Innovation**: 3/5
- **A-share Applicability**: 1/5

### 25. MapleStax CBC
- **URL**: https://www.tradingview.com/script/AppLGbrI-MapleStax-CBC
- **Category**: unknown
- **Math Core**: [Fetch Failed]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

### 26. PRO FINAL OI OPTION S R
- **URL**: https://www.tradingview.com/script/Aux0Wuep-PRO-FINAL-OI-OPTION-S-R
- **Category**: options
- **Math Core**: [Fetch Failed] - Open Interest options-based support/resistance
- **Innovation**: 2/5
- **A-share Applicability**: 1/5

### 27. News Impact Analyzer
- **URL**: https://www.tradingview.com/script/B3fRF62o-News-Impact-Analyzer-forexobroker
- **Category**: fundamental
- **Math Core**: [Fetch Failed] - News event impact analysis
- **Innovation**: 2/5
- **A-share Applicability**: 1/5

### 28. Key Levels ONH ONL PDH PDL
- **URL**: https://www.tradingview.com/script/B6GKlUjx-Key-Levels-ONH-ONL-PDH-PDL
- **Category**: pivot
- **Math Core**: [Fetch Failed] - Overnight New High/Low + Previous Day High/Low levels
- **Innovation**: 1/5
- **A-share Applicability**: 2/5

### 29. Stage2 Pro by Ketan
- **URL**: https://www.tradingview.com/script/B7wEgVoZ-Stage2-Pro-by-Ketan
- **Category**: trend
- **Math Core**: [Fetch Failed] - Stage 2 breakout identification (Minervini-style)
- **Innovation**: 2/5
- **A-share Applicability**: 3/5

### 30. Asia 786 Fib Levels
- **URL**: https://www.tradingview.com/script/BCqvvGrk-Asia-786-Fib-Levels
- **Category**: fibonacci
- **Math Core**: [Fetch Failed] - Asian session Fibonacci 0.786 retracement levels
- **Innovation**: 2/5
- **A-share Applicability**: 2/5

### 31. BFH87fmb
- **URL**: https://www.tradingview.com/script/BFH87fmb
- **Category**: unknown
- **Math Core**: [Fetch Failed]
- **Innovation**: 1/5
- **A-share Applicability**: 1/5

## Highlights

### Top Innovation (Innovation >= 3)
1. **Hexatap** (4/5) - 6-point reversal pattern with supply/demand zones, liquidity sweep validation, Fibonacci golden ratio entry zones, A+/A- grading
2. **AVS VWAP EMA Pullback Pro** (3/5) - Multi-layer trend following: VWAP+EMA trend + pullback + ADX chop filter + session filter + dual TP
3. **HA Signals on Regular Candles** (3/5) - Dual-candle approach: HA for signal generation, regular candles for execution, Chandelier Exit + ZL SMMA

### A-Share Best Candidates (Applicability >= 3)
1. **Hexatap** (4/5) - Only needs OHLCV, swing point analysis works on any market, ATR-based filtering adapts to A-share volatility
2. **AVS VWAP EMA Pullback Pro** (4/5) - VWAP pullback concept directly transferable, adjust session to 9:30-15:00 CST, ADX filter helps with A-share chop
3. **HA Signals on Regular Candles** (4/5) - OHLCV-only, HA signal filtering reduces noise in A-share daily bars, Chandelier Exit provides adaptive stops
4. **Gold Swing EMA+RSI** (3/5) - Simple EMA crossover + RSI, needs pip-to-percentage conversion for A-share 10% daily limits
5. **ORB Sessions** (3/5) - Opening range breakout concept highly relevant for A-shares (9:30-10:00 CST range), needs session time adaptation
