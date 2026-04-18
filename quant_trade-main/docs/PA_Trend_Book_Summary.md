# Al Brooks - Trading Price Action Trends: Comprehensive Extraction

## Complete reference for implementing trend-following strategies in Python.
## Source: Chinese translation of Al Brooks' "Trading Price Action Trends" (full 406-page scanned PDF)

---

## 1. TREND IDENTIFICATION

### 1.1 Basic Trend Structure
- **Uptrend**: Series of higher highs (HH) and higher lows (HL). Each swing high > prior swing high; each swing low > prior swing low.
- **Downtrend**: Series of lower highs (LH) and lower lows (LL). Each swing high < prior swing high; each swing low < prior swing low.
- **Trading Range**: Neither HH/HL nor LH/LL pattern. Overlapping bars, price oscillates between support and resistance.

### 1.2 The 20-Period EMA
- The ONLY indicator used. Serves as a reference, not a signal generator.
- **Price above EMA + slope up = bullish bias**. Price below EMA + slope down = bearish bias.
- In strong trends, price stays on one side of EMA for extended periods ("always in" direction).
- EMA acts as magnetic support/resistance during pullbacks.
- **EMA Gap Bar (20 Gap Bar)**: When a bar's body does not overlap the EMA at all. This is a sign of trend strength. A setup occurring at the EMA gap (e.g., High 2 at EMA with gap) is a reliable trend continuation signal.

### 1.3 "Always In" Concept
- At every moment, the market is "Always In Long" or "Always In Short."
- Determined by: if you had to enter right now with a market order, which direction gives the best probability?
- The "Always In" direction is the trend direction. Trade only in that direction until evidence of reversal.

### 1.4 Bar Counting System (High 1/2/3/4, Low 1/2/3/4)
- **High 1**: First pullback low in an uptrend (touches or crosses below EMA). Often too early to buy.
- **High 2 (ABC Pullback)**: Second pullback low = standard pullback entry. This is the most reliable pullback buy signal in an uptrend. Equivalent to an ABC correction pattern.
- **High 3 (Wedge Bull Flag)**: Third pullback low = wedge pattern. Three pushes down in an uptrend. Still a buy signal but trend may be weakening.
- **High 4**: Fourth pullback = deeper correction, trend more questionable. May become a trading range.
- **Low 1/2/3/4**: Mirror image for downtrends. Low 2 = standard pullback sell signal.

### 1.5 Trend Strength Classification
- **Strong trend (Spike)**: 1-3 consecutive large trend bars with very little overlap, possibly gapping. Price far from EMA. Strong directional conviction.
- **Channel**: After the spike, price transitions into a sloped trading range. Still trending but with more overlap and pullbacks.
- **Weak trend**: Many overlapping bars, frequent EMA tests, small bodies with tails. Still making HH/HL or LH/LL but lacking conviction.

### 1.6 Spike and Channel Model (Chapter 21)
- **Spike phase**: 1-3 very strong trend bars at the beginning of a move. The spike establishes the "Always In" direction.
- **Channel phase**: After the spike, the market enters a sloped trading range (channel). Price still trends but with two-way trading.
- **Thin area**: In strong channels, bars cluster tightly along the EMA or trend line. Price barely pulls back. This is a sign of trend persistence.
- A strong spike often leads to a channel, and the channel can last much longer than expected.
- **Consecutive climaxes**: 
  - 2 climaxes in a trend usually lead to at least a two-leg pullback
  - 3 climaxes often lead to a larger reversal

---

## 2. TREND CONTINUATION PATTERNS

### 2.1 High 2 / Low 2 (ABC Pullback) -- THE Core Pattern
- **Definition**: Two pullbacks to the EMA (or trend line) in a trend. The second pullback = High 2 (uptrend) or Low 2 (downtrend).
- **Entry**: Buy above the High 2 signal bar high (uptrend) / Sell below the Low 2 signal bar low (downtrend).
- **Signal bar requirements**: Should be a bull reversal bar (for buys) or bear reversal bar (for sells). Ideally closes near its high (buy) or low (sell).
- **Reliability**: This is the highest-probability trend continuation pattern. Works in all timeframes.

### 2.2 Double Bottom Pullback (Uptrend) / Double Top Bear Flag (Downtrend)
- **Double Bottom Pullback**: In an uptrend, price makes two attempts to pull back but holds at roughly the same level. Then resumes up.
- **Double Top Bear Flag**: In a downtrend, price bounces twice to roughly the same level, then resumes down. This is the mirror image.
- **Entry**: Buy above the second bottom (or the bar that reverses up from it) / Sell below the second top.

### 2.3 Wedge Bull Flag / Wedge Bear Flag
- **Wedge Bull Flag**: Three pushes down in an uptrend (High 3). Each push is slightly lower but momentum diminishes. Buy above the third push's reversal bar.
- **Wedge Bear Flag**: Three pushes up in a downtrend (Low 3). Each push is slightly higher but momentum diminishes. Sell below the third push's reversal bar.
- **Wedge adjustment sideways**: If a wedge pattern moves mostly sideways instead of pulling back, the trend is extremely strong. This is the strongest continuation signal.

### 2.4 20 Gap Bar Setup
- When a bar's body does not touch the 20 EMA in a trend, and a pullback occurs to the EMA, any continuation signal at the EMA (High 2, double bottom pullback, etc.) is a "20 gap bar" setup.
- These have higher probability than normal pullback setups because the gap shows trend strength.

### 2.5 Inside Bar (ii/iii) Breakouts
- **Inside bar (ii)**: Two consecutive inside bars (each contained within the prior). The breakout from the second inside bar is a continuation signal.
- **Inside-inside-inside (iii)**: Three consecutive inside bars. Even higher probability breakout.
- **Entry**: Enter on the breakout of the mother bar range in the trend direction.
- **ioi pattern**: Inside bar followed by outside bar followed by inside bar. The breakout of the ioi range is a continuation signal.

### 2.6 Micro Channel Breakout Pullback
- In a strong trend, price may form a micro channel (3-10 bars with overlapping bodies but trending directionally).
- When the micro channel breaks against the trend briefly and then resumes, that breakout pullback is a high-probability continuation entry.

### 2.7 Trend Line and Trend Channel Line Breakouts
- **Trend line breakout pullback**: When price breaks a trend line in a trend but then pulls back to test the broken trend line, that test is often a continuation entry IF the original trend was strong.
- **Trend channel line**: Drawn parallel to the trend line through the opposite swing points. When price touches the channel line, expect a pullback. When it breaks the channel line, the move may be climaxing.

### 2.8 Measured Moves and Measured Gaps
- **Measured move**: After a breakout spike, the target is often equal to the spike height (measured from breakout point).
- **Measured gap**: When a gap occurs in a trend, the measured move from the gap often equals the prior leg height.
- These provide targets for trend continuation trades.

### 2.9 Final Flag Pattern
- A tight trading range that forms late in a trend. When price breaks out of the final flag in the trend direction, the measured move = the flag height.
- When price breaks back INTO the final flag against the trend, it becomes a final flag reversal. This often leads to a two-legged move.

### 2.10 Failed Breakout Continuation
- When a breakout against the trend fails (e.g., breaking below a swing low in an uptrend but immediately reversing back up), this is a strong continuation signal.
- Failed breakouts trap counter-trend traders, who must cover, fueling the continuation.

---

## 3. PULLBACK ENTRY STRATEGIES

### 3.1 Standard Pullback Entry (High 2 / Low 2)
- **Rule**: Wait for two pullback attempts in the trend direction. Enter on the second pullback.
- **Stop**: Place 1-2 ticks below the signal bar low (for buys) or above the signal bar high (for sells).
- **Target**: Measured move from the signal bar, or prior swing high/low, or 2x risk.

### 3.2 EMA Pullback Entry
- In a trend, wait for price to pull back to or slightly beyond the 20 EMA.
- Look for a reversal bar or a High 2/Low 2 setup at the EMA.
- **Entry**: Above the reversal bar high (buy) or below the reversal bar low (sell).
- Works best when EMA is sloped in the trend direction.

### 3.3 Trend Line Pullback Entry
- Draw a trend line connecting swing lows (uptrend) or swing highs (downtrend).
- When price pulls back to the trend line, look for a reversal signal bar.
- **Entry**: On the breakout above the signal bar in the trend direction.
- More reliable on the first and second touch of the trend line.

### 3.4 Limit Order Entry (Advanced)
- In strong trends, experienced traders use limit orders to buy on pullbacks.
- Place limit order at or below the prior bar's low in a strong uptrend.
- Works because strong trends have shallow pullbacks and bars often dip before continuing.
- **Only use in confirmed strong trends** where the "Always In" direction is clear.

### 3.5 Breakout Pullback Entry
- After a breakout above resistance (uptrend) or below support (downtrend), wait for price to pull back to test the breakout level.
- Enter when price reverses at the breakout level (former resistance becomes support, or vice versa).
- This is one of the highest-probability entries.

### 3.6 Small Pullback Trend Entry (Chapter 23)
- On small pullback trend days, maximum pullback is only 10-30% of average daily range.
- Most buy signal bars in strong trends look like false breakouts (weak-looking signals).
- **Key insight**: Weak-looking buy signals in strong uptrends are actually signs of trend strength.
- Use 2-point money stop (tight stop) in strong trends.
- Enter on any pullback to EMA, prior bar low, or trend line.

---

## 4. BREAKOUT TRADING RULES

### 4.1 Breakout Bar Characteristics
- A breakout bar should be a strong trend bar (large body, small or no tail against the breakout direction).
- The larger the breakout bar, the more reliable the breakout.
- Breakout bars that gap away from the prior bar are particularly strong.

### 4.2 Breakout Entry Rules
- **Enter on stop** above/below the breakout bar (or the signal bar).
- **Do NOT enter on breakouts of trading ranges** unless there is a strong spike (1-3 very large bars). Most breakout attempts from trading ranges FAIL.
- Breakouts from tight flags or wedges in trends have higher probability.
- After a breakout, the first pullback to the breakout level is usually a buy/sell setup.

### 4.3 Failed Breakout Rules
- If a breakout fails within 1-3 bars, the failure itself becomes a trading signal in the opposite direction.
- **Failed breakout buy**: Bear breakout below support fails, price reverses back above. Buy above the failure bar.
- **Failed breakout sell**: Bull breakout above resistance fails, price reverses back below. Sell below the failure bar.
- Failed breakouts are among the highest-probability setups.

### 4.4 Second Breakout Entry
- If the first breakout fails, a second breakout attempt in the same direction has higher probability.
- Conversely, if a second breakout also fails, the market is likely in a trading range.

### 4.5 Breakout from Opening Range (Chapter 22-23)
- **Opening range < 25% of average daily range**: Potential trend day. Trade breakouts in either direction.
- **Opening range ~50% of average daily range**: More likely a trending trading range day.
- After opening range forms (typically first 1-2 hours), the breakout from that range determines the trend direction.
- Most breakout attempts from trading ranges fail, but when they succeed, the measured move often equals the range height.

---

## 5. TREND STRENGTH MEASUREMENT

### 5.1 Visual Assessment
- **Strong trend**: Large trend bars, minimal overlap, price stays far from EMA, shallow pullbacks.
- **Moderate trend**: Mix of trend bars and doji, price oscillates around EMA but makes directional progress.
- **Weak trend**: Small bars with tails, frequent EMA crossovers, deep pullbacks, overlapping bars.

### 5.2 Spike Strength
- Count the number of consecutive strong trend bars in the spike.
- 1 bar = minor spike; 2-3 bars = strong spike; 4+ bars = very strong spike.
- The larger the spike, the more likely the channel phase will be prolonged.

### 5.3 Channel Characteristics
- **Tight channel**: Bars cluster along EMA, minimal pullbacks. Very strong trend.
- **Broad channel**: Wide swings but still making HH/HL or LH/LL. Moderate strength.
- **Channel breaking into spike acceleration**: When a channel suddenly produces a spike in the trend direction, trend is accelerating (step pattern acceleration).

### 5.4 Consecutive Climaxes
- A climax = a very strong move at the end of a trend leg.
- **1 climax**: Normal trend behavior, trend may continue.
- **2 consecutive climaxes**: At minimum, a two-leg pullback is expected.
- **3 consecutive climaxes**: Larger reversal likely. The trend is exhausting.

### 5.5 Micro Gap Presence
- Micro gaps (small gaps between bar bodies) in the trend direction indicate strong conviction.
- More micro gaps = stronger trend.

### 5.6 EMA Relationship
- **Price consistently on one side of EMA**: Strong trend.
- **Price oscillating around EMA**: Weak trend or trading range.
- **EMA slope**: Steep slope = strong trend; flat EMA = range or weak trend.
- **20 gap bars**: Bars whose bodies don't touch EMA show exceptional trend strength.

---

## 6. WHEN TRENDS END (EXhaustion and Reversal Signals)

### 6.1 Climax Patterns
- **Buy climax**: Very large bull trend bar(s) late in an uptrend, often with a gap. Price may push above a trend channel line. This is exhaustion, not strength.
- **Sell climax**: Very large bear trend bar(s) late in a downtrend. Mirror image.
- After a climax, expect at least a two-leg pullback (minimum).

### 6.2 Trend Channel Line Overthrow
- When price breaks above a trend channel line (uptrend) or below it (downtrend), it often represents a climax.
- The overthrow-and-reverse pattern signals at least a two-leg pullback.
- If the overthrow is very extreme, the reversal may be larger.

### 6.3 Three Pushes (Wedge) Exhaustion
- Three pushes up in an uptrend (or three pushes down in a downtrend) = wedge exhaustion pattern.
- Each push is weaker than the previous (smaller bars, more tails, less momentum).
- After the third push, sell/buy the reversal.
- This is the opposite of a wedge flag (which is continuation). The distinguishing factor: three pushes INTO a trend channel line vs. three pushes TOWARD the EMA.

### 6.4 Shrinking Steps (Contracting Steps)
- In a step pattern (broad channel), if each new push is smaller than the previous, momentum is declining.
- This "contracting steps" pattern often leads to a two-leg reversal and trend line break.

### 6.5 Failed High 2 / Low 2
- If a High 2 buy setup in an uptrend fails (price goes below the High 2 signal bar low), the uptrend may be ending.
- Similarly, a failed Low 2 sell setup suggests the downtrend may be ending.
- Two consecutive failed pullback entries = strong sign of trend reversal.

### 6.6 Double Top/Bottom at EMA
- In an uptrend, if price bounces to the EMA twice and fails to push higher, forming a double top at/near the EMA, the trend may reverse.
- This is different from a double bottom pullback (which is bullish). Here, the double top AT the EMA is bearish.

### 6.7 Trend Line Break + Failure to Make New Extremes
- If the trend line breaks AND the next push fails to make a new higher high (uptrend) or new lower low (downtrend), the trend has likely ended.
- This is confirmed when price then breaks the last swing low (uptrend) or last swing high (downtrend).

### 6.8 Final Flag Reversal
- A tight trading range (final flag) forms late in a trend.
- If price breaks INTO the final flag in the opposite direction, the trend has ended.
- Minimum target = measured move equal to the flag height in the reversal direction.

### 6.9 Outside Bars at Extremes
- An outside bar (bar that engulfs the prior bar) at a trend extreme, especially after a climax, is a reversal signal.
- The larger the outside bar relative to recent bars, the more significant the reversal signal.

### 6.10 Consecutive Climaxes Rule (Quantitative)
- **2 climaxes**: Expect at least a two-leg pullback (possibly a trading range or minor reversal).
- **3 climaxes**: Expect a larger reversal. The trend is truly exhausting.
- This can be measured by counting instances where consecutive trend legs have accelerating momentum that then suddenly stalls.

---

## 7. STOP LOSS PLACEMENT

### 7.1 Standard Stop
- **1-2 ticks below the signal bar low** (for buys) or **1-2 ticks above the signal bar high** (for sells).
- This is the default approach.

### 7.2 Money Stop
- In strong trends, use a fixed "money stop" (e.g., 2 points for E-mini S&P).
- Tight stops work in strong trends because if the entry is correct, price should move quickly in your favor.
- If stopped out with a money stop, the trade was wrong and the loss is small.

### 7.3 Swing Point Stop
- For swing trades, place stop below the most recent swing low (buy) or above the most recent swing high (sell).
- Wider stop but allows for more normal pullback behavior.

### 7.4 EMA-Based Stop
- In trending markets, if price closes on the wrong side of the EMA and the next bar does not reverse back, exit.
- Works as a trailing stop mechanism.

### 7.5 Widening Stop Rule
- **Never widen your stop**. If the original stop is hit, the trade thesis was wrong. Accept the loss.
- Exception: After a partial profit take, you may move stop to breakeven on the remaining position.

---

## 8. TREND CONTINUATION VS REVERSAL SIGNALS

### 8.1 Continuation Signals (Trend Remains Intact)
1. High 2 / Low 2 at EMA succeeds (price resumes in trend direction).
2. Pullback holds above prior swing low (uptrend) or below prior swing high (downtrend).
3. Trend line holds on test (bounce off trend line in trend direction).
4. Breakout pullback succeeds (price pulls back to breakout level and resumes).
5. Inside bar breakout in trend direction.
6. 20 gap bar setup at EMA.
7. Wedge flag (High 3 / Low 3) succeeds.
8. Double bottom pullback (uptrend) / Double top bear flag (downtrend) succeeds.
9. Failed counter-trend breakout (breakout against trend fails).

### 8.2 Reversal Signals (Trend May Be Ending)
1. Climax bar(s) followed by reversal bar.
2. Trend channel line overthrow and reversal.
3. Three pushes to a channel line (wedge exhaustion).
4. Failed High 2 / Low 2 (pullback entry fails).
5. Consecutive climaxes (2+ = minimum two-leg pullback; 3+ = larger reversal).
6. Double top at EMA (uptrend) / Double bottom at EMA (downtrend).
7. Trend line break + failure to make new extremes.
8. Final flag breakout against the trend.
9. Large outside bar at trend extreme.
10. Shrinking steps (contracting step pattern = momentum loss).
11. Price closes below prior swing low (uptrend) / above prior swing high (downtrend).

### 8.3 Decision Framework
- After a climax, ALWAYS expect at least a two-leg pullback.
- The first pullback after a climax is usually tradeable in the reversal direction.
- If the pullback is shallow and the trend resumes, the climax was not a true climax.
- Use the "Always In" concept: if you're unsure, ask "which direction would I enter right now?"

---

## 9. POSITION MANAGEMENT DURING TRENDS

### 9.1 Swing vs Scalp
- **Scalp**: Quick trade, target 1-2 points, exit on first sign of weakness.
- **Swing**: Hold for larger move, target measured move or 2:1 reward/risk minimum.
- In strong trends, swing trades are preferred. In channels, scalping both directions is possible.

### 9.2 Partial Profit Taking
- Take partial profit at 1x risk (first target).
- Move stop to breakeven on remaining position.
- Let the remainder run to the measured move target or until a reversal signal appears.

### 9.3 Adding to Positions (Scaling In)
- In experienced hands, add to winning positions on pullbacks (High 2 / Low 2 at EMA).
- Only add if the original trend is still "Always In" the same direction.
- Each add should be treated as a separate trade with its own stop.

### 9.4 Trailing Stop Guidelines
- In a spike, use a tight trailing stop (below each bar).
- In a channel, use a wider trailing stop (below swing lows in uptrend).
- When a climax occurs, tighten the stop immediately.

### 9.5 Time-of-Day Considerations
- **First 1-2 hours**: Highest volatility, breakouts and trend establishment.
- **Mid-day**: Lower volume, more likely to form trading ranges.
- **Last 1-2 hours**: Trends often resume. Be prepared for trend continuation into the close.
- **~11:00 AM PST**: Sharp brief reversal common in strong trends (shakeout of weak hands).
- **FOMC reports**: Create temporary spikes; do not react until bar closes.

### 9.6 Critical Trading Rules
1. **Wait for bar close** before making trading decisions. Never react to intra-bar price movement.
2. **Never trade counter-trend** just because the risk looks small. The risk is larger than it appears.
3. **Strong trends have weak setups** -- weak-looking buy signals in strong uptrends are actually signs of trend strength.
4. In strong trends, buying below the prior bar's low (or at the EMA) with a limit order is valid.
5. Most breakout attempts from trading ranges fail. Trade the breakout pullback instead.
6. When in doubt, trade in the "Always In" direction.
7. A 60% win rate with proper risk management is a strong edge. Do not seek 80%+ accuracy.
8. Probability-based trading: every trade is 50-50 at best to some degree. Focus on risk/reward.

---

## 10. ADDITIONAL PATTERNS AND CONCEPTS

### 10.1 Trend Resumption Day (Chapter 25)
- Early trend followed by hours of trading range, then trend resumes into close.
- When early trend is strong and market goes sideways for hours, be prepared for resumption.
- Traders accumulate positions in both directions during the range. When breakout occurs, the losing side must cover, accelerating the move.
- Resumption may take 1-3 days to complete (multi-day pattern).
- **Gap test**: On large gap days, market often tests the opening level before the trend starts.

### 10.2 Step Pattern / Broad Channel (Chapter 26)
- A variant of trending trading range day with at least 3 segments.
- Wide swings but swing highs and lows trend in one direction.
- Each breakout usually has a breakout test (pullback beyond the breakout point).
- If breakouts become progressively smaller = contracting steps = momentum declining = potential reversal.
- Step patterns are often just flags on higher timeframes.

### 10.3 Trending Trading Range Day (Chapter 22)
- Opening range is 1/3 to 1/2 of average daily range.
- Most breakout attempts from trading ranges fail.
- Second reversals in trading ranges are usually reliable for scalps.
- After 3 pushes in one direction, expect reversal attempt.
- Magnetic attraction: price tends to get drawn to the opposite end of the range.

### 10.4 Trend from the Open (Chapter 23)
- Opening range < 25% of average daily range signals potential trend day.
- Small pullback trend days: max pullback only 10-30% of average daily range.
- Occur roughly 1-2 times per month.
- Larger pullback (150-200% of earlier pullbacks) usually appears in the last 2 hours.
- If first trade is stopped out, consider reversing for a swing trade.
- Strong trends often form double top/bottom patterns before launching in the trend direction.

### 10.5 Micro Channels (Chapter 16)
- 3-10 consecutive bars with overlapping bodies trending in one direction.
- Breakout of micro channel in trend direction is a continuation signal.
- Breakout against micro channel that fails = strong continuation signal.
- Micro channels show extreme trend strength.

### 10.6 Barbed Wire (Tight Trading Range)
- Multiple doji bars with overlapping ranges. Both sides and both ends of each bar are being tested.
- Dangerous to trade -- high probability of whipsaw.
- Breakout from barbed wire in either direction has only about 50% reliability.
- Best approach: wait for breakout and then trade the breakout pullback.

### 10.7 Outside Bars
- Bar that engulfs the prior bar's range.
- At trend extremes, outside bars are reversal signals.
- In trends, outside bars in the trend direction are continuation signals.
- Outside bar followed by inside bar (oi pattern) creates a breakout setup.

### 10.8 Reversal Bar Requirements
- **Bull reversal bar**: Opens near its low, closes near its high, and closes above the prior bar's close. The lower tail should be at least 50% of the bar's range.
- **Bear reversal bar**: Opens near its high, closes near its low, and closes below the prior bar's close. The upper tail should be at least 50% of the bar's range.
- Large reversal bars at extremes are more significant than small ones.
- A reversal bar is only a signal -- it requires confirmation (entry above/below the signal bar).

---

## 11. PYTHON IMPLEMENTATION GUIDE

### 11.1 Data Structure Requirements
```
Each bar needs:
- open, high, low, close, volume
- 20-period EMA value
- Bar type classification: bull_trend, bear_trend, doji, bull_reversal, bear_reversal, outside, inside
- Swing high/low detection
```

### 11.2 Core Functions to Implement
1. `detect_swing_points(bars, left=3, right=3)` -- Identify swing highs and lows
2. `compute_trend_structure(swings)` -- Classify HH/HL/LH/LL patterns
3. `compute_ema(bars, period=20)` -- 20-period EMA
4. `detect_bar_type(bar, prev_bar)` -- Classify each bar type
5. `count_pullbacks(bars, ema, trend_direction)` -- High 1/2/3/4 or Low 1/2/3/4
6. `detect_wedge(bars, n_pushes=3)` -- Three-push patterns
7. `detect_double_bottom_pullback(bars)` -- Double bottom in uptrend
8. `detect_double_top_bear_flag(bars)` -- Double top in downtrend
9. `measure_spike_strength(bars)` -- Count and size of consecutive trend bars
10. `detect_climax(bars)` -- Climax bars at extremes
11. `detect_trend_channel(bars)` -- Trend line and channel line
12. `compute_always_in_direction(bars)` -- Determine the "Always In" direction
13. `detect_inside_bars(bars)` -- ii/iii/ioi patterns
14. `detect_breakout(bars, level)` -- Breakout detection
15. `detect_failed_breakout(bars, level)` -- Failed breakout detection

### 11.3 Entry Signal Priority (Highest to Lowest)
1. Failed breakout in trend direction
2. High 2 / Low 2 at EMA with 20 gap bar
3. Breakout pullback (first pullback after breakout)
4. High 2 / Low 2 at EMA (standard)
5. Double bottom pullback / Double top bear flag
6. Wedge bull/bear flag (High 3 / Low 3)
7. Inside bar breakout (ii/iii)
8. Trend line bounce
9. Micro channel breakout pullback

### 11.4 Exit Signal Priority
1. Climax bar followed by reversal bar (exit immediately)
2. Trend channel line overthrow (tighten stop)
3. Consecutive climax #2+ (exit or tighten)
4. Failed High 2 / Low 2 (exit on failure)
5. Trend line break + no new extremes (exit)
6. Double top at EMA in uptrend (exit)
7. Final flag breakout against trend (exit and reverse)

### 11.5 Risk Management Parameters
- Default stop: 1-2 ticks beyond signal bar extreme
- Strong trend stop: 2-point money stop
- Swing trade stop: Below last swing low (buy) / above last swing high (sell)
- Risk per trade: 1-2% of account
- Minimum reward:risk = 2:1 for swing trades, 1:1 for scalps
- Partial profit: 50% at 1x risk, 50% at measured move target

### 11.6 Trend State Machine
```
States: NO_TREND, SPIKE, CHANNEL, EXHAUSTING, REVERSING
Transitions:
- NO_TREND -> SPIKE: 1-3 strong trend bars breaking range
- SPIKE -> CHANNEL: Overlapping bars begin, EMA catches up
- CHANNEL -> EXHAUSTING: Climax bar, channel line overthrow, 3+ pushes
- EXHAUSTING -> REVERSING: Failed pullback entry, double top/bottom at EMA
- REVERSING -> NO_TREND: Range established, or
- REVERSING -> SPIKE: Strong reversal spike in opposite direction
- CHANNEL -> SPIKE: Step acceleration (stronger spike in same direction)
```
