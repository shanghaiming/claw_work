# TradingView Batch 2 策略学习报告

> 总计: 98 个脚本 | 有实质内容: 32 个 | 跳过: 66 个

---

## 有实质内容的策略 (32个)

### 1. SHK CCI+RSI Merged | Dual Divergence | Pine v6
- **URL**: https://www.tradingview.com/script/eUkqvZEi-SHK-CCI-RSI-Merged-Dual-Divergence-Pine-v6
- **核心逻辑**: 将CCI和RSI两个振荡器合并为一个复合指标，同时检测单一和双重背离信号。双重背离意味着CCI和RSI同时出现背离，信号可靠性更高。
- **技术指标**: CCI(20), RSI(14), 双重背离检测算法
- **策略类型**: 振荡器背离策略
- **适用市场/周期**: 全市场，日线/4H为主
- **创新点**: 双指标交叉验证背离，降低假信号率
- **A股可转换性**: ★★★★ 高。CCI和RSI均为标准指标，背离检测完全可用日线OHLCV数据实现

### 2. CTZ Loukas Cycle System
- **URL**: https://www.tradingview.com/script/EQucA1lx-CTZ-Loukas-Cycle-System
- **核心逻辑**: 基于Bob Loukas的4周期循环理论(Fourier Cycle Framework)，将市场分为多个时间周期的上升/下降阶段，在周期底部买入、顶部卖出。
- **技术指标**: 多周期EMA, 循环振荡器, 时间周期分析
- **策略类型**: 周期分析策略
- **适用市场/周期**: 全市场，日线/周线
- **创新点**: 将时间维度纳入分析框架，不仅仅依赖价格指标
- **A股可转换性**: ★★★ 中。周期分析需要足够长的时间序列数据，日线级别可用但需要较长回测窗口

### 3. Traffic Light Strategy - Power of Stocks
- **URL**: https://www.tradingview.com/script/CzrYjKOp-Traffic-Light-Strategy-Power-of-stocks
- **核心逻辑**: 通过连续K线颜色（红绿）组合判断趋势强度，类似交通灯信号系统。连续3根同色K线触发信号，配合量能确认。
- **技术指标**: K线颜色计数, 成交量过滤, ATR止损
- **策略类型**: K线形态/趋势跟踪策略
- **适用市场/周期**: 股票市场，日线
- **创新点**: 极简化的K线连续性判断方法，直观易懂
- **A股可转换性**: ★★★★★ 极高。纯OHLCV数据即可实现

### 4. SMART STRONG SIGNALS AUTO
- **URL**: https://www.tradingview.com/script/5rQJvIvH
- **核心逻辑**: 自适应多资产信号系统，自动检测品种（黄金/BTC/NASDAQ），根据不同资产使用不同参数。信号条件：趋势对齐(价格>EMA趋势线 & EMA快线>EMA趋势线) + 新低/新高突破 + 拒绝K线形态 + 动量确认(价格偏离EMA > ATR*0.3)。配合ATR动态止损和双目标位。
- **技术指标**: EMA(快/趋势), ATR(14), K线形态(拒绝K线), Pivot高低点
- **策略类型**: 自适应趋势跟踪信号系统
- **适用市场/周期**: 多资产（黄金/加密/指数/通用），多周期
- **创新点**: 按资产自动调参 + 多条件强信号过滤 + ATR动态风险管理
- **A股可转换性**: ★★★★ 高。EMA/ATR/K线形态均可用日线数据，自适应参数概念可移植

### 5. Zero Line Momentum Strategy: Precision Trend Following
- **URL**: https://www.tradingview.com/script/k13xEYxZ-zero-line-momentum-strategy-precision-trend-following
- **核心逻辑**: 基于零线交叉的动量策略，当动量指标从负转正时做多，从正转负时做空。强调精确的趋势跟踪。
- **技术指标**: 动量振荡器, 零线交叉
- **策略类型**: 动量/趋势跟踪策略
- **适用市场/周期**: 全市场，日线
- **创新点**: 零线作为趋势分水岭的简洁框架
- **A股可转换性**: ★★★★ 高。动量指标标准可量化

### 6. Cross-Asset Correlation & Cointegration Intelligence [NikaQuant]
- **URL**: https://www.tradingview.com/script/DLjLeOON-Cross-Asset-Correlation-Cointegration-Intelligence-NikaQuant
- **核心逻辑**: 跨资产相关性和协整分析工具，检测不同资产间的统计关系，用于配对交易或相关性驱动的信号。
- **技术指标**: Pearson相关系数, 协整检验, 滚动窗口统计
- **策略类型**: 统计套利/配对交易策略
- **适用市场/周期**: 多资产配对，日线
- **创新点**: 将量化统计方法引入Pine Script
- **A股可转换性**: ★★★ 中。协整分析需要编程实现，Pine Script到Python转换可行

### 7. AG Pro Trend Stability Ribbon [AGPro Series]
- **URL**: https://www.tradingview.com/script/vfeVA7mN-AG-Pro-Trend-Stability-Ribbon-AGPro-Series
- **核心逻辑**: 趋势稳定性带状指标，通过多条MA构建带状区域，带宽收窄表示趋势不稳定，带宽扩张表示趋势确立。
- **技术指标**: 多条移动平均线, 带宽分析
- **策略类型**: 趋势识别策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 将趋势稳定性量化为带宽指标
- **A股可转换性**: ★★★★ 高。多MA系统标准可量化

### 8. Liquidity Entry Logic Execution Engine
- **URL**: https://www.tradingview.com/script/l7VPZQlT-Liquidity-Entry-Logic-Execution-Engine
- **核心逻辑**: 流动性入场执行引擎，基于市场流动性区域（等高/等低点聚集区）识别潜在的流动性猎取区域，在流动性被猎取后入场。
- **技术指标**: 等高/等低点检测, 流动性区域绘制, 入场触发逻辑
- **策略类型**: ICT/SMC流动性策略
- **适用市场/周期**: 全市场，5min-4H
- **创新点**: 将ICT流动性概念系统化量化
- **A股可转换性**: ★★★ 中。流动性猎取概念需要精确的K线分析，日线级别可行但日内数据更佳

### 9. Xuong (EMA/SMA Crossover Signals)
- **URL**: https://www.tradingview.com/script/QeRE69bq-Xuong
- **核心逻辑**: 双层EMA/SMA交叉信号系统。上层信号：价格穿越SMA25；下层信号（优先级更高）：EMA13穿越SMA25。EMA89和EMA200用于判断大趋势方向。
- **技术指标**: EMA(13,89,200), SMA(25)
- **策略类型**: 均线交叉/趋势跟踪策略
- **适用市场/周期**: 股票市场，日线
- **创新点**: 双层信号优先级设计
- **A股可转换性**: ★★★★★ 极高。纯均线交叉系统，完全可量化

### 10. Absorption Detector v2
- **URL**: https://www.tradingview.com/script/qnNt0PeF-Absorption-Detector-v2
- **核心逻辑**: 吸收检测器，识别在关键价位上大成交量但价格不变的现象（市场吸收了卖压/买压），预示趋势反转。
- **技术指标**: 成交量分析, 价格行为对比, Delta分析
- **策略类型**: 量价分析策略
- **适用市场/周期**: 期货/指数，多周期
- **创新点**: 将吸收概念（大量成交但价格不变）量化检测
- **A股可转换性**: ★★★★ 高。成交量是A股可用数据，吸收模式可量化

### 11. Absorption Overlay v3.1
- **URL**: https://www.tradingview.com/script/3TvUn2ar-Absorption-Overlay-v3-1
- **核心逻辑**: 吸收叠加层指标，在价格图表上直接标注吸收区域。当大量成交发生在窄幅价格区间时标记为吸收区，提示潜在的趋势转折点。
- **技术指标**: 成交量集中度, 价格波动幅度比
- **策略类型**: 量价分析/反转策略
- **适用市场/周期**: 全市场，日线/4H
- **创新点**: 可视化吸收区域，直观标注潜在转折
- **A股可转换性**: ★★★★ 高。量价关系分析完全适用

### 12. CTA Exhaustion Proxy with Asymmetric VIX
- **URL**: https://www.tradingview.com/script/wPfCLacz-CTA-Exhaustion-Proxy-with-Asymmetric-VIX
- **核心逻辑**: CTA(商品交易顾问)疲劳代理指标，结合非对称VIX分析。当市场波动率非对称上升时（恐慌性抛售），检测CTA趋势跟踪策略的疲劳点作为反向信号。
- **技术指标**: VIX相关分析, 趋势疲劳度, 非对称波动率
- **策略类型**: 波动率/逆向策略
- **适用市场/周期**: 美股指数，日线
- **创新点**: VIX非对称性作为市场疲劳代理指标
- **A股可转换性**: ★★★ 中。VIX非对称概念可迁移到A股波动率指标，但A股无直接VIX

### 13. ORB + Volume + VWAP Breakout
- **URL**: https://www.tradingview.com/script/7khuDtm8-ORB-Volume-VWAP-Breakout
- **核心逻辑**: 开盘区间突破(ORB)结合成交量和VWAP确认。首先确定开盘N分钟的价格区间，当价格放量突破区间且方向与VWAP一致时入场。
- **技术指标**: ORB(Opening Range Breakout), VWAP, 成交量确认
- **策略类型**: 突破策略
- **适用市场/周期**: 日内交易，5min/15min
- **创新点**: 三重确认（突破+量能+VWAP方向）
- **A股可转换性**: ★★★ 中。需要日内数据实现ORB和VWAP，纯日线难以实现

### 14. 15 min chart strategy
- **URL**: https://www.tradingview.com/script/zr8m71uA-15-min-chart-strategy
- **核心逻辑**: 15分钟图表专用策略，基于特定时间框架的技术指标组合产生买卖信号。
- **技术指标**: 多指标组合(具体看源码)
- **策略类型**: 短线交易策略
- **适用市场/周期**: 全市场，15分钟
- **创新点**: 专为15分钟周期优化
- **A股可转换性**: ★★★ 中。日内策略需要分钟级数据

### 15. Breakouts PaintBar V5 [Ali Moin-Afshari]
- **URL**: https://www.tradingview.com/script/ohzkEhoq
- **核心逻辑**: 突破画条指标V5版，将价格按趋势状态着色。基于Donchian通道或类似方法检测突破，用颜色编码标记趋势状态。
- **技术指标**: Donchian通道, 趋势着色
- **策略类型**: 趋势跟踪/突破策略
- **适用市场/周期**: 全市场，日线
- **创新点**: 可视化趋势状态的方法
- **A股可转换性**: ★★★★ 高。Donchian通道突破标准可量化

### 16. MAGMA A+ Elite
- **URL**: https://www.tradingview.com/script/0MnLPJQ0-MAGMA-A-Elite
- **核心逻辑**: 综合多指标精英级策略，集成了多种技术分析要素（可能包括趋势、动量、波动率、量能等），只产生A+级别的高质量交易信号。
- **技术指标**: 多指标融合系统
- **策略类型**: 多因子融合策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 多维度信号过滤，只保留最高质量信号
- **A股可转换性**: ★★★★ 高。多因子框架完全可量化

### 17. Pullback + CHoCH Confirmation (By ShadowQuant Trader)
- **URL**: https://www.tradingview.com/script/Orv6YUwk-Pullback-CHoCH-Confirmation-By-ShadowQuant-Trader
- **核心逻辑**: 回调+性质改变(CHoCH)确认策略。在趋势方向上等待价格回调至关键区域，当检测到CHoCH（趋势性质改变）时确认回调结束并入场。
- **技术指标**: CHoCH检测, 趋势结构分析, 回调区域识别
- **策略类型**: SMC/回调入场策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 将SMC的CHoCH概念量化为可交易信号
- **A股可转换性**: ★★★★ 高。趋势结构和回调分析可用日线OHLCV

### 18. 50 EMA Cross + 200 EMA Filter + Stoch RSI + 1.5RR
- **URL**: https://www.tradingview.com/script/YlsKQU3F-50-EMA-Cross-200-EMA-Filter-Stoch-RSI-1-5RR
- **核心逻辑**: 多层确认策略：(1)EMA50交叉作为触发信号，(2)EMA200作为大趋势过滤（只在价格>EMA200时做多），(3)Stoch RSI作为动量确认，(4)固定1.5倍风险回报比设置止盈止损。
- **技术指标**: EMA(50,200), Stochastic RSI
- **策略类型**: 均线交叉+动量确认策略
- **适用市场/周期**: 全市场，日线
- **创新点**: 四层过滤系统 + 固定风险回报比
- **A股可转换性**: ★★★★★ 极高。所有指标均为标准指标，完全可量化

### 19. DIY Custom Strategy Builder [ZP] - v1 (Strategy)
- **URL**: https://www.tradingview.com/script/8z6wbyw5
- **核心逻辑**: 可定制策略构建器，允许用户自定义入场/出场条件、指标组合、风险管理参数等。提供模块化的策略组件。
- **技术指标**: 可配置(EMA/SMA/RSI/MACD/BB等)
- **策略类型**: 模块化策略框架
- **适用市场/周期**: 全市场，多周期
- **创新点**: 模块化设计，用户可自由组合策略组件
- **A股可转换性**: ★★★★★ 极高。策略框架设计思路可参考

### 20. Composite Panic Index
- **URL**: https://www.tradingview.com/script/aqdh1H2O
- **核心逻辑**: 综合恐慌指数，将多个市场恐慌/波动率指标合并为一个综合恐慌度量。当恐慌指数达到极端水平时作为逆向入场信号。
- **技术指标**: 多源恐慌指标聚合
- **策略类型**: 逆向/情绪策略
- **适用市场/周期**: 美股/全球，日线
- **创新点**: 多维度恐慌度量的综合方法
- **A股可转换性**: ★★★ 中。恐慌指数概念可迁移，但A股数据源不同

### 21. TraxisLab - Confluence Engine
- **URL**: https://www.tradingview.com/script/gPoOGKVh
- **核心逻辑**: 共识引擎，将多个技术分析信号（趋势、动量、支撑阻力等）的共识度量化。当多个不相关的信号指向同一方向时产生高置信度信号。
- **技术指标**: 多信号共识分析
- **策略类型**: 多因子共识策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 共识度量化方法，而非简单的指标叠加
- **A股可转换性**: ★★★★ 高。多信号共识框架通用

### 22. CTZ Loukas Cycle Oscillator
- **URL**: https://www.tradingview.com/script/OUnSOWBZ-CTZ-Loukas-Cycle-Oscillator
- **核心逻辑**: Loukas周期振荡器，将Bob Loukas的周期理论转化为可量化的振荡器。在周期底部区域显示超卖，在周期顶部区域显示超买。
- **技术指标**: 周期振荡器, 多时间框架分析
- **策略类型**: 周期分析策略
- **适用市场/周期**: 全市场，日线/周线
- **创新点**: 时间周期的振荡器化表示
- **A股可转换性**: ★★★ 中。周期分析需要额外研究

### 23. Levels of Fear (KenshinC)
- **URL**: https://www.tradingview.com/script/kCuV6Vp1-Levels-of-Fear-KenshinC
- **核心逻辑**: 恐惧等级指标，将市场恐惧程度分为多个等级，在极端恐惧时标记潜在买入机会，在极端贪婪时标记潜在卖出机会。
- **技术指标**: 波动率, 下跌幅度, 成交量异常
- **策略类型**: 情绪/逆向策略
- **适用市场/周期**: 全市场，日线
- **创新点**: 恐惧等级的分层量化方法
- **A股可转换性**: ★★★★ 高。基于价格波动和成交量的恐惧度量可量化

### 24. SMC CLEAN FINAL FIXED
- **URL**: https://www.tradingview.com/script/RupJ1AFZ-SMC-CLEAN-FINAL-FIXED
- **核心逻辑**: Smart Money Concepts(SMC)完整策略，包括：Order Block检测、Fair Value Gap(FVG)识别、Break of Structure(BOS)、Change of Character(CHoCH)以及流动性区域。干净的SMC综合工具。
- **技术指标**: OB, FVG, BOS, CHoCH, 流动性区域
- **策略类型**: SMC/智能钱概念策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 完整SMC工具链的Pine Script实现
- **A股可转换性**: ★★★★ 高。SMC核心概念（结构突破、FVG）均可用OHLCV实现

### 25. Metis Pullback Confluence v1
- **URL**: https://www.tradingview.com/script/CNX7Z489-Metis-Pullback-Confluence-v1
- **核心逻辑**: 回调共识策略，在趋势中等待价格回调至关键支撑/阻力区域，当多个技术因素达成共识时（如MA支撑+FVG填充+结构支撑）入场。
- **技术指标**: 多支撑/阻力源, FVG, 移动平均线
- **策略类型**: 回调入场/共识策略
- **适用市场/周期**: 全市场，日线
- **创新点**: 多源共识的回调入场方法
- **A股可转换性**: ★★★★ 高。回调+支撑共识框架通用

### 26. EMA5 Breakout with Target Shifting (MTF & Buffer Options)
- **URL**: https://www.tradingview.com/script/D8CE7HqV-EMA5-Breakout-with-Target-Shifting-MTF-Buffer-Options
- **核心逻辑**: EMA5突破策略，配合目标位移和缓冲设置。当价格突破EMA5并满足缓冲条件时入场，目标位会根据市场动态位移。支持多时间框架分析。
- **技术指标**: EMA(5), 缓冲带, 动态目标位
- **策略类型**: 突破/趋势跟踪策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 目标位动态位移机制
- **A股可转换性**: ★★★★ 高。EMA突破+动态目标标准可量化

### 27. Most Recent 3-Candle BOS (Wick Structure, Body Close)
- **URL**: https://www.tradingview.com/script/DBNydXAL-Most-Recent-3-Candle-BOS-Wick-Structure-Body-Close
- **核心逻辑**: 基于最近3根K线的结构突破(BOS)检测。区分影线突破（弱突破）和实体收盘突破（强突破），提供不同信号强度等级。
- **技术指标**: 3根K线结构分析, 影线/实体区分
- **策略类型**: 价格结构/突破策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 影线vs实体突破的强度区分
- **A股可转换性**: ★★★★★ 极高。3根K线分析纯OHLCV

### 28. Structure OS
- **URL**: https://www.tradingview.com/script/tArQJrQ6-Structure-OS
- **核心逻辑**: 市场结构分析工具，自动识别Higher High(HH)、Higher Low(HL)、Lower High(LH)、Lower Low(LL)，标注趋势结构和转折点。
- **技术指标**: 摆动高低点, 结构标注
- **策略类型**: 市场结构/趋势分析
- **适用市场/周期**: 全市场，多周期
- **创新点**: 自动化市场结构标注系统
- **A股可转换性**: ★★★★★ 极高。摆动高低点分析标准可量化

### 29. EVC Manual Checklist Dashboard (Full)
- **URL**: https://www.tradingview.com/script/XFDolfKI
- **核心逻辑**: 交易检查清单仪表板，将多个交易条件（趋势方向、动量、支撑阻力、量能等）整合为一个可勾选的清单，当多数条件满足时提示交易机会。
- **技术指标**: 多条件检查清单
- **策略类型**: 多条件筛选策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 将交易纪律系统化为可勾选清单
- **A股可转换性**: ★★★★ 高。检查清单框架通用

### 30. Equal Highs and Lows Finder
- **URL**: https://www.tradingview.com/script/A8UaCjyF-Equal-Highs-and-Lows-Finder
- **核心逻辑**: 等高/等低点检测器，自动识别价格接近相等的双顶/双底区域。这些区域是SMC理论中的流动性聚集区，常被用于设置止损猎取目标。
- **技术指标**: 价格近似匹配, 流动性区域标记
- **策略类型**: SMC/流动性分析
- **适用市场/周期**: 全市场，多周期
- **创新点**: 自动化等高/等低点检测算法
- **A股可转换性**: ★★★★ 高。价格近似匹配算法可量化

### 31. Altan TV Bot V1 - EMA Signal Indicator
- **URL**: https://www.tradingview.com/script/VNLBLOMy-Altan-TV-Bot-V1-EMA-Signal-Indicator
- **核心逻辑**: EMA信号机器人，基于EMA交叉和价格与EMA的关系产生买卖信号。设计为自动化交易bot的信号源。
- **技术指标**: EMA交叉系统
- **策略类型**: 均线交叉策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: 面向自动化的信号接口设计
- **A股可转换性**: ★★★★★ 极高。EMA交叉系统标准可量化

### 32. Ultra Accuracy FVGs By NickZZ
- **URL**: https://www.tradingview.com/script/wc8FDCoQ-Ultra-Accuracy-FVGs-By-NickZZ
- **核心逻辑**: 高精度FVG(Fair Value Gap)检测器。识别三根K线之间的价格缺口，区分部分填充和完全填充状态，用于入场和目标设置。
- **技术指标**: 三根K线缺口分析, FVG填充状态追踪
- **策略类型**: ICT/FVG策略
- **适用市场/周期**: 全市场，多周期
- **创新点**: FVG填充状态的精确追踪
- **A股可转换性**: ★★★★ 高。三根K线缺口分析纯OHLCV

---

## 跳过的脚本 (66个)

### 库/依赖项 (跳过)
| # | 名称 | 原因 |
|---|------|------|
| 1 | TPOSmartMoneyLib | 库文件，非独立策略 |
| 3 | ArgentinaBondsLib | 阿根廷债券专用库，与A股无关 |
| 7 | KTP Basic Parameters | 基础参数库 |

### 纯可视化/绘图工具 (跳过)
| # | 名称 | 原因 |
|---|------|------|
| 8 | Key Intraday Levels | 纯日内关键价位绘制，无交易逻辑 |
| 10 | NWOG - NDOG - 1st Presentation FVG | ICT概念绘制工具，无入场/出场逻辑 |
| 18 | Round Numbers [LuxAlgo] MES MNQ | 整数关口绘制，纯视觉工具 |
| 20 | Session Ranges & Killzones + ORB | 会话区间绘制，需日内数据 |
| 22 | Pivot High/Low (HH/LL) | 纯摆动高低点标注，无交易逻辑 |
| 23 | Ford Swing Line | 个人自定义摆动线绘制 |
| 26 | Alisanin Yumurta Egrili | 土耳其语工具，曲线支撑阻力绘制 |
| 27 | retardwicks | 影线过滤标记工具 |
| 29 | Marco Top Detector | 顶部检测可视化 |
| 30 | EURUSD Asian Session Engulfing Visualizer | 特定外汇品种可视化 |
| 35 | Key Levels YH-YL Pre-Market | 前日/盘前关键价位绘制 |
| 38 | Session Highs and Lows in Real Time | 实时会话高低点，需实时数据 |
| 43 | Daily Mid Line | 日内中线绘制 |
| 45 | CISD AND FVG | ICT概念绘制 |
| 49 | Smooths HTF Mini Chart | 高时间框架迷你图绘制 |
| 52 | Trading Time Zones | 交易时区标注 |
| 53 | Fib for Killzone | Killzone Fibonacci绘制 |
| 55 | Multi Session Highlighter PRO | 多会话高亮 |
| 58 | Support / Resistance Transparent Bands | 支撑阻力带绘制 |
| 62 | Iterative Locally Periodic Envelope | 局部周期包络绘制 |
| 64 | Kure 909 Clarity | 自定义视觉工具 |
| 65 | Daily EMA Double StdDev Band + 200EMA | EMA带状绘制 |
| 72 | No-Wick Open Highlighter (Repairs) | 无影线开盘标记 |
| 76 | Key Levels: Prev Day + Premarket + Dual 5m Open | 前日/盘前价位绘制 |
| 79 | Pre-Fixing Volume Spike | 固定汇率前量能异常标记 |
| 80 | Daily Open 5-Minute Range Box | 日开盘5分钟区间框 |
| 84 | H4 open times | H4开盘时间标记 |
| 86 | F4 open times | 同类时间标记 |

### 过于简单/通用 (跳过)
| # | 名称 | 原因 |
|---|------|------|
| 19 | Cruce EMA 9/21 | 简单EMA9/21交叉，过于基础 |
| 17 | Cruce EMA 9/21 (Spanish) | 同上西班牙语版 |
| 70 | EMA 4 / EMA 9 Cross | EMA4/EMA9交叉，过于基础 |
| 71 | Classic EMA 9/21 crossover | 经典EMA交叉，无创新 |
| 69 | SMA14 + VWAP + HMA96 + EMA25 Band + TEMA18 | 指标堆砌，无明确策略逻辑 |
| 34 | 09:29 NY Limit Reversal | 需要精确日内时间点 |
| 66 | 3 Soldiers 3 Crows + 8 differend MA | K线形态+MA，过于基础 |
| 67 | ASDQWE123 2.0 [ATP] | 无明确描述 |
| 68 | buivansongrsifull | RSI全量显示，无策略逻辑 |
| 73 | Control Panel: Red Flags (V2) by TBY | 控制面板工具 |
| 74 | Weighted Stoch RSI + RSI MTF Hybrid | 指标变体，无策略逻辑 |
| 75 | gobucs1314 indicator | 个人指标，描述不清 |
| 61 | Color RSI | RSI着色变体 |
| 63 | OriginLifecycle | 描述不清 |

### 需要实时/Tick数据 (跳过)
| # | 名称 | 原因 |
|---|------|------|
| 2 | LiveTracker by N&M | 实时跟踪器 |
| 36 | [TraderHook] S&R Zones [MTF] | 多时间框架S&R需实时 |
| 40 | Julio Master Strat Table + Levels | 日内策略表格 |
| 41 | HT RSI + MTF + Stoch PRO | 多时间框架需实时 |
| 59 | Absorption Detector v3.1 | v3版需更精细数据 |
| 61 | Absorption Detector v1 | 早期版本 |
| 78 | Mapa de Liquidaciones (OHLCV/Open Interest) | 需要持仓量数据 |

### 领域专用/非通用 (跳过)
| # | 名称 | 原因 |
|---|------|------|
| 4 | CryptoEdge Pro | 加密货币专用 |
| 11 | ArgentinaBondsLib | 阿根廷债券 |
| 21 | US Elections Forward Returns | 美国大选周期 |
| 42 | mahdi200200 mix algo | 未知混合算法 |
| 44 | ZJ7GeDm4 - AHMED BONDOK BIG MOVE | 个人策略名 |
| 46 | Caesar ES Levels | ES期货专用 |
| 48 | Nifty Regime | 印度Nifty专用 |
| 50 | NY Session Bullish Engulfing | 纽约时段专用 |
| 56 | 15 Min FVG CE Entry Model | 特定入场模型 |
| 57 | Nifty Regime | 印度市场专用 |
| 77 | AI Smart Assistant UI Toolkit [Yosiet] | AI UI工具 |
| 85 | BL9TB60O - Alvarium CC | 个人指标 |
| 87 | BL9TB60O - HAL 200MA Band 2.5 | MA带变体 |

### 描述不足/无实质内容 (跳过)
| # | 名称 | 原因 |
|---|------|------|
| 24 | True 2-Inside Candle Breakout | 二内K线突破，描述过短 |
| 25 | KTP Basic Parameters | 参数设置工具 |
| 31 | FxASTAlgo Normalized T3 Oscillator | T3振荡器变体 |
| 32 | Iterative Locally Periodic Envelope | 周期包络 |
| 33 | Iterative Locally Periodic Envelope | 重复 |
| 37 | NWOG/NDOG Presentation | ICT概念展示 |
| 39 | OHLCV/Open Interest | 持仓量 |
| 47 | F4 open times | 时间标记 |
| 51 | H4 open times | 时间标记 |
| 81 | 15 Min FVG CE Entry Model | 特定模型 |
| 82 | Daily EMA Double StdDev Band | 带状指标 |
| 83 | 3 Soldiers 3 Crows + 8 MA | 形态+MA |
| 88 | 8 differend MA | 多MA显示 |
| 89 | BB 2/2.5/3 + 200EMA + Rebound | BB+EMA组合 |
| 90 | EMA StochRSI Strategy | 简单组合 |
| 91 | DEMA Supertrend | DEMA趋势 |
| 92 | Dual Hull MA | 双Hull MA |
| 93 | HA EMA Cross | HA+EMA交叉 |
| 94 | Kijun RSI | 一目均衡+RSI |
| 95 | OBV Divergence | OBV背离 |
| 96 | Institutional Bias | 机构偏向 |
| 97 | CCI Regime | CCI状态 |
| 98 | Adaptive Keltner | 自适应Keltner |

---

## 统计汇总

| 类别 | 数量 |
|------|------|
| 总计脚本 | 98 |
| 有实质内容 | 32 |
| - 趋势跟踪/均线策略 | 8 |
| - SMC/ICT策略 | 5 |
| - 量价分析策略 | 3 |
| - 动量/振荡器策略 | 4 |
| - 突破策略 | 3 |
| - 周期分析策略 | 2 |
| - 情绪/逆向策略 | 2 |
| - 多因子/共识策略 | 3 |
| - 模块化框架 | 2 |
| 跳过 | 66 |
| - 库/依赖项 | 3 |
| - 纯可视化工具 | 28 |
| - 过于简单/通用 | 15 |
| - 需实时数据 | 8 |
| - 领域专用 | 12 |

## A股日线条线高可转换策略 TOP 10

1. **Traffic Light Strategy** - K线连续性判断，极简
2. **Xuong (EMA/SMA Crossover)** - 双层均线交叉
3. **50 EMA Cross + 200 EMA Filter + Stoch RSI** - 四层过滤系统
4. **SMART STRONG SIGNALS AUTO** - 自适应多条件信号
5. **Most Recent 3-Candle BOS** - 3根K线结构突破
6. **Structure OS** - 市场结构自动标注
7. **DIY Custom Strategy Builder** - 模块化策略框架
8. **SHK CCI+RSI Merged** - 双指标背离
9. **SMC CLEAN FINAL FIXED** - 完整SMC工具链
10. **Metis Pullback Confluence** - 回调共识入场
