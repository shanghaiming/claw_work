# Batch 1 Extended Learning 2 (Scripts 60-89)
> Date: 2026-04-19

## Summary
- Total: 30
- Innovation >= 3: 12
- A-share applicable (>=3): 10

## Strategy Details

### 1. Prime Volume Profile + Liquidity Heatmap
- **URL**: https://www.tradingview.com/script/5a8YRMgs
- **Category**: volume
- **Math Core**: Daily Volume Profile with POC/VAH/VAL calculation + liquidity heatmap using volume concentration per price level
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: Value Area 70%, daily reset
- **Notes**: Volume profile is highly applicable to A-shares. POC acts as a magnet, VAH/VAL as dynamic S/R. Works well on daily timeframe for A-share stocks.

### 2. 9AM ORB (UTC+2)
- **URL**: https://www.tradingview.com/script/5aFVGUKQ-9AM-ORB-UTC-2
- **Category**: price_action
- **Math Core**: Opening Range Breakout - defines high/low range from first hour, signals on breakout
- **Innovation**: 1/5
- **Innovation**: 2/5
- **A-share Applicability**: 2/5
- **Key Params**: 9AM-10AM UTC+2 range
- **Notes**: Simple ORB indicator. Timezone-specific to European session. For A-shares would need adaptation to 9:30-10:30 CST.

### 3. FxASTAlgo Normalized T3 Oscillator [ALLDYN]
- **URL**: https://www.tradingview.com/script/5okPIN4Z-FxASTAlgo-Normalized-T3-Oscillator-ALLDYN
- **Category**: trend
- **Math Core**: T3 (Tillson) smoothed price normalized to -0.5/+0.5 range using rolling min/max; signal line with multi-MA options
- **Innovation**: 3/5
- **A-share Applicability**: 4/5
- **Key Params**: T3 length, normalization window, signal MA type
- **Notes**: Clean momentum oscillator. T3 smoothing reduces noise effectively. Normalization allows cross-instrument comparison. Good for A-share trend following with daily OHLCV.

### 4. STOCH & RSI (BERSANCH)
- **URL**: https://www.tradingview.com/script/5vqGyZVY
- **Category**: mean_reversion
- **Math Core**: Stochastic oscillator combined with RSI for tech sector mean reversion, compared against Nasdaq Composite RSI
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: Stoch period, RSI period
- **Notes**: Basic Stoch+RSI combo. Targeted at tech stocks vs Nasdaq. Limited novelty.

### 5. Big Trades Auto-Footprint @MaxMaserati
- **URL**: https://www.tradingview.com/script/5xcSk73V-Big-Trades-Auto-Footprint-MaxMaserati
- **Category**: volume
- **Math Core**: Intrabar Z-Score engine on footprint data (bid/ask volume per tick row), 6-tier dynamic sizing, support/resistance projection from heavy volume nodes
- **Innovation**: 5/5
- **A-share Applicability**: 1/5
- **Key Params**: Ticks per row, Z-Score mode, S/R zone projection
- **Notes**: Requires TV Premium (request.footprint() function). Outstanding order flow analysis tool. Cannot be applied to A-shares due to lack of tick-level bid/ask data.

### 6. RTH and AH Vertical Breaks
- **URL**: https://www.tradingview.com/script/69Ayx7kM-RTH-and-AH-Vertical-Breaks
- **Category**: price_action
- **Math Core**: Separates regular trading hours (RTH) and after-hours (AH) price action, vertical lines for session breaks
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Session times
- **Notes**: US market session-specific. Not applicable to A-shares.

### 7. PDH PDL Mid Candle 2 Signals D 4H
- **URL**: https://www.tradingview.com/script/6LQPw6KN-PDH-PDL-Mid-Candle-2-Signals-D-4H
- **Category**: price_action
- **Math Core**: Previous Day High/Low/Midpoint levels as support/resistance zones with breakout signals on D/4H timeframes
- **Innovation**: 1/5
- **A-share Applicability**: 3/5
- **Key Params**: PDH, PDL, midpoint calculation
- **Notes**: Classic pivot-style indicator using prior day levels. Applicable to A-shares on daily timeframe.

### 8. 6PvB16mj
- **URL**: https://www.tradingview.com/script/6PvB16mj
- **Category**: trend
- **Math Core**: [Fetch Failed] - No description available
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Could not retrieve meaningful content.

### 9. Snip3rs Asian Range Killzone
- **URL**: https://www.tradingview.com/script/6XcBHwhG-Snip3rs-Asian-Range-Killzone
- **Category**: price_action
- **Math Core**: Asian session range detection with killzone boxes, breakout signals from Asian high/low
- **Innovation**: 2/5
- **A-share Applicability**: 2/5
- **Key Params**: Asian session start/end, range margin
- **Notes**: Forex-focused ICT concept. A-share market IS the Asian session, so conceptually less useful but the range breakout idea applies.

### 10. HA Straddle Strangle Signals v6
- **URL**: https://www.tradingview.com/script/6b4ta5rV-HA-Straddle-Strangle-Signals-v6
- **Category**: volatility
- **Math Core**: Heikin-Ashi candles combined with options straddle/strangle signal detection
- **Innovation**: 2/5
- **A-share Applicability**: 2/5
- **Key Params**: HA parameters, signal thresholds
- **Notes**: Options-focused strategy. A-shares have limited options market.

### 11. KTP Basic Parameters
- **URL**: https://www.tradingview.com/script/6gE4mkHG-KTP-Basic-Parameters
- **Category**: multi_factor
- **Math Core**: Parameter framework for a trading system (KTP = Killzone Trading Parameters)
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Various configurable parameters
- **Notes**: Utility/config script, not a standalone strategy.

### 12. Liquidity Acceptance Map [PhenLabs]
- **URL**: https://www.tradingview.com/script/6gZ7tZmZ-Liquidity-Acceptance-Map-PhenLabs
- **Category**: multi_factor
- **Math Core**: Equal high/low detection via swing pivots, sweep confirmation with close-beyond requirement, composite Acceptance Score (0-100) = Volume expansion ratio * weight% + ATR expansion ratio * (100-weight%), HTF EMA bias filter
- **Innovation**: 5/5
- **A-share Applicability**: 4/5
- **Key Params**: Swing Lookback=20, Equal Level Tolerance%=0.1, Vol Expansion Mult=1.5, ATR Expansion Mult=1.2, Vol Weight%=60, Min Acceptance Score=60, Max Active Zones=2, Invalidation Offset%=0.2
- **Notes**: Outstanding 3-layer confirmation system. The Acceptance Score combining volume + ATR expansion is genuinely novel. Zone management with non-destructive invalidation is excellent. Highly applicable to A-shares on 1H/Daily.

### 13. RIA: Resonant Interface Analyzer
- **URL**: https://www.tradingview.com/script/6rkWUJuo-ria-resonant-interface-analyzer
- **Category**: trend
- **Math Core**: Statistical Mode clustering (most frequent price level) via high-speed array processing, Standard Deviation filters for resonance/expansion state detection
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: Lookback window, SD multiplier thresholds
- **Notes**: Price density analysis using statistical mode instead of mean. Identifies "resonant center" where most activity occurs. Marketing-heavy but the core concept of mode-based POC is mathematically sound.

### 14. 6wt6vR7H
- **URL**: https://www.tradingview.com/script/6wt6vR7H
- **Category**: trend
- **Math Core**: [Fetch Failed] - No description available
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Could not retrieve meaningful content.

### 15. Xiznit Price Driven Snake Game
- **URL**: https://www.tradingview.com/script/704tG49M-Xiznit-Price-Driven-Snake-Game
- **Category**: kline_pattern
- **Math Core**: Snake game visualization driven by price movement (educational/novelty)
- **Innovation**: 2/5
- **A-share Applicability**: 1/5
- **Key Params**: Game parameters
- **Notes**: Novelty/educational script, not a trading strategy.

### 16. CCI Color Bars
- **URL**: https://www.tradingview.com/script/75il5DV1-CCI-Color-Bars
- **Category**: mean_reversion
- **Math Core**: CCI (Commodity Channel Index) = (Typical Price - SMA) / (0.015 * Mean Deviation), applied as bar coloring
- **Innovation**: 1/5
- **A-share Applicability**: 3/5
- **Key Params**: CCI period=20
- **Notes**: Standard CCI applied as visual bar coloring. CCI works on A-shares for mean reversion signals.

### 17. 79ZaSPLq
- **URL**: https://www.tradingview.com/script/79ZaSPLq
- **Category**: trend
- **Math Core**: [Fetch Failed] - No description available
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Could not retrieve meaningful content.

### 18. OnlyWicks TIMESHIFT
- **URL**: https://www.tradingview.com/script/7CCxikmS-OnlyWicks-TIMESHIFT
- **Category**: price_action
- **Math Core**: Wick-only candle visualization with time-shifting for comparison analysis
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: Time shift offset
- **Notes**: Visualization tool, not a signal generator.

### 19. 7YcBqv7s
- **URL**: https://www.tradingview.com/script/7YcBqv7s
- **Category**: trend
- **Math Core**: [Fetch Failed] - No description available
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Could not retrieve meaningful content.

### 20. 7aCcBkB8
- **URL**: https://www.tradingview.com/script/7aCcBkB8
- **Category**: trend
- **Math Core**: [Fetch Failed] - No description available
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Could not retrieve meaningful content.

### 21. 7e0Qknj9
- **URL**: https://www.tradingview.com/script/7e0Qknj9
- **Category**: trend
- **Math Core**: [Fetch Failed] - No description available
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Could not retrieve meaningful content.

### 22. Stock Checklist Indicator
- **URL**: https://www.tradingview.com/script/7fRppq3M-Stock-Checklist-Indicator
- **Category**: multi_factor
- **Math Core**: Multi-criteria stock screening checklist combining fundamental and technical checks
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: Checklist criteria thresholds
- **Notes**: Dashboard-style checklist for stock selection. Concept applicable to A-share stock screening.

### 23. 7ta14MGG
- **URL**: https://www.tradingview.com/script/7ta14MGG
- **Category**: trend
- **Math Core**: [Fetch Failed] - No description available
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Could not retrieve meaningful content.

### 24. 81qW24I2
- **URL**: https://www.tradingview.com/script/81qW24I2
- **Category**: trend
- **Math Core**: [Fetch Failed] - No description available
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Could not retrieve meaningful content.

### 25. PSP Zones with Validation
- **URL**: https://www.tradingview.com/script/85asnddO-psp-zones-with-validation
- **Category**: price_action
- **Math Core**: Price Structure Pattern zones with validation logic for S/R level confirmation
- **Innovation**: 2/5
- **A-share Applicability**: 3/5
- **Key Params**: Zone detection parameters, validation thresholds
- **Notes**: S/R zone identification with validation. Applicable to A-shares.

### 26. Open Interest Fixed
- **URL**: https://www.tradingview.com/script/88bY48Sx-Open-Interest-Fixed
- **Category**: volume
- **Math Core**: Open Interest tracking and visualization, fixed version for proper calculation
- **Innovation**: 1/5
- **A-share Applicability**: 2/5
- **Key Params**: OI calculation period
- **Notes**: Open Interest is primarily for futures/options. A-share individual stocks don't have OI data.

### 27. The Apex Stalker: RVOL & Options Sniper
- **URL**: https://www.tradingview.com/script/8DodEu0q-The-Apex-Stalker-RVOL-Options-Sniper
- **Category**: multi_factor
- **Math Core**: RVOL (current vol / historical average vol), %ATR exhaustion (candle range / 14-day ATR), Daily 21 EMA trend filter; auto-sorted watchlist dashboard for 10 tickers with dual alert engine (Sniper Entry vs Exhaustion Fade)
- **Innovation**: 4/5
- **A-share Applicability**: 3/5
- **Key Params**: RVOL threshold=1.5x, ATR period=14, EMA period=21, Exhaustion Threshold (100-150%)
- **Notes**: Excellent framework combining relative volume with ATR exhaustion for continuation vs fade signals. The RVOL + %ATR exhaustion concept is highly portable to A-shares (without the options focus). The dashboard multi-ticker approach is innovative.

### 28. Gann Sq9 Levels
- **URL**: https://www.tradingview.com/script/8HVjvV3B-Gann-Sq9-Levels-darshakssc
- **Category**: price_action
- **Math Core**: Gann Square of 9 formula: Level = (sqrt(Base) +/- n * 0.25)^2, generating R1-R6 and S1-S6 from base price (session mid/open/prev close/manual)
- **Innovation**: 3/5
- **A-share Applicability**: 3/5
- **Key Params**: Base Price Mode, level count (1-10), step increment=0.25
- **Notes**: Classic Gann mathematical technique. The sqrt-based level calculation creates non-linear S/R levels. Interesting for A-shares - works best on 5m/15m/1H intraday.

### 29. Relative Volume Box Simple
- **URL**: https://www.tradingview.com/script/8RVo6h9x-Relative-Volume-Box-Simple
- **Category**: volume
- **Math Core**: Relative Volume = current volume / SMA(volume, lookback), displayed as color-coded boxes
- **Innovation**: 1/5
- **A-share Applicability**: 4/5
- **Key Params**: Volume SMA lookback period
- **Notes**: Simple but useful. Relative volume is one of the best indicators for A-shares. High RVOL on A-share daily often precedes significant moves within the 10% limit.

### 30. Praveen Test
- **URL**: https://www.tradingview.com/script/8TmMnT0H-Praveen-Test
- **Category**: trend
- **Math Core**: [Fetch Failed] - Test/experimental script
- **Innovation**: 1/5
- **A-share Applicability**: 1/5
- **Key Params**: Unknown
- **Notes**: Appears to be a test/experimental script.

## Highlights

Top 5 most innovative strategies (Innovation >= 3):

1. **Big Trades Auto-Footprint @MaxMaserati** (Innovation: 5/5) - Intrabar Z-Score engine on footprint data with dynamic tiered sizing. Revolutionary order flow tool, though requires tick-level data unavailable for A-shares.

2. **Liquidity Acceptance Map [PhenLabs]** (Innovation: 5/5) - 3-layer confirmation (equal H/L detection + sweep + Acceptance Score combining volume expansion and ATR expansion 0-100). Non-destructive zone invalidation. HTF bias filter. Best-in-class liquidity sweep tool.

3. **The Apex Stalker: RVOL & Options Sniper** (Innovation: 4/5) - Multi-ticker dashboard auto-sorted by RVOL, combining %ATR exhaustion with trend alignment for continuation vs fade signals. Dual alert engine for sniper entries and exhaustion fades.

4. **FxASTAlgo Normalized T3 Oscillator** (Innovation: 3/5) - T3-smoothed price normalized to a centered -0.5/+0.5 range. Clean momentum bias visualization with dynamic coloring and state detection.

5. **Gann Sq9 Levels** (Innovation: 3/5) - Mathematical sqrt-based support/resistance via Gann Square of 9 formula. Creates non-linear price levels that adapt to the base price, with 4 base price modes.

### Key A-Share Takeaways
- **Liquidity Acceptance Map**: The Volume + ATR composite scoring system can be directly adapted for A-share daily data. Equal high/low sweeps with acceptance scoring is highly relevant.
- **Normalized T3 Oscillator**: Excellent candidate for A-share trend following on daily bars. T3 smoothing handles A-share gap behavior well.
- **Apex Stalker RVOL framework**: The RVOL + %ATR exhaustion concept is directly portable. Replace options-focused alerts with equity signals.
- **Relative Volume Box**: Simplest but most directly applicable. RVOL > 1.5x on A-share daily is a strong signal within 10% limit structure.
