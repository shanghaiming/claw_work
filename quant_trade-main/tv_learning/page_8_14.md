# TradingView 策略学习笔记 - Page 8~14

> 抓取时间: 2026-04-18
> 来源: TradingView 公开脚本 (pages 8-14, 共168个策略)
> 筛选: 仅保留描述详细、有明确策略逻辑的脚本，跳过纯工具/描述过短的

---

## Page 8

### 1. Simple Long Only Bot
- **URL**: https://www.tradingview.com/script/7YZu94L1-Simple-Long-Only-Bot/
- **核心逻辑**: 全自动长线趋势跟踪机器人，通过 TradingView Webhook + Python 服务器连接 Interactive Brokers 自动下单。仅在确认上升趋势时入场，价格突破 50 EMA 确认动量，跌破则出场。
- **技术指标**: 50 EMA (入场), 200 EMA (趋势确认)
- **策略类型**: 趋势跟踪
- **适用市场/时间框架**: SPY/QQQ 等主要 ETF，日线级别
- **创新点**: 完整的自动化交易流水线 (TradingView Alert -> Webhook -> Python Server -> IBKR)，适合学习如何将 Pine Script 策略接入实盘自动执行。纯做多设计避免做空风险。

### 2. Volatility Vault - EMA Tap Scanner
- **URL**: https://www.tradingview.com/script/ejjXqMNM-Volatility-Vault-EMA-Tap-Scanner/
- **核心逻辑**: 多时间框架 EMA 扫描器，静默监控 9/21/50/100/200 EMA 跨越最多 21 个时间框架（从 1 秒到周线），仅当价格接近或触碰某 EMA 时才激活显示。绿色=从上方触碰（支撑），红色=从下方触碰（阻力），橙色=接近中。
- **技术指标**: EMA (9, 21, 50, 100, 200) x 21 个时间框架
- **策略类型**: 支撑阻力 / 多时间框架分析
- **适用市场/时间框架**: 通用，1 秒到周线
- **创新点**: 动态表格设计 -- 不画满屏 EMA 线，只在价格接近关键 EMA 时才弹出对应的行。核心时间框架 (5m/15m/1H/4H/1D) 固定置顶高亮。当多个时间框架在同一 EMA 值激活时，形成高概率反应区。可配置 TAP/NEAR 阈值适配不同波动率品种。

### 3. SMA + MACD + RSI Signals
- **URL**: https://www.tradingview.com/script/9aK2KxwB-SMA-MACD-RSI-Signals/
- **核心逻辑**: 三重确认日内信号系统。做多需 10 SMA 上穿 20 SMA + MACD > Signal + RSI > 50 同时满足；做空条件反之。
- **技术指标**: SMA (10, 20), MACD, RSI
- **策略类型**: 动量 / 趋势跟踪
- **适用市场/时间框架**: 日内 5 分钟
- **创新点**: 简洁的三重过滤设计，适合初学者理解多指标共振入场。每个指标负责不同维度（趋势方向/动量/强度）。

### 4. 50 EMA Cross + 200 EMA Filter + Stoch RSI Indicator
- **URL**: https://www.tradingview.com/script/gAbvCgpk-50-EMA-Cross-200-EMA-Filter-Stoch-RSI-Indicator/
- **核心逻辑**: 价格站上 50 EMA 和 200 EMA，且 Stoch RSI 处于超卖区域时入场，在趋势中寻找回踩入场点。
- **技术指标**: EMA (50, 200), Stochastic RSI
- **策略类型**: 趋势跟踪
- **适用市场/时间框架**: 通用
- **创新点**: 趋势过滤 + 超卖回踩的组合，在主趋势中利用 Stoch RSI 寻找最佳入场时机。

### 5. Institutional CVD Divergence [Eduardo T.]
- **URL**: https://www.tradingview.com/script/bUeDoJy5-Institutional-CVD-Divergence-Eduardo-T/
- **核心逻辑**: 轻量级累积成交量差 (CVD) 背离代理指标。将多空成交量聚合与价格行为解耦，实时标记背离异常。用于映射机构流动性扫荡，在 NFP 或高波动窗口不会冻结平台。
- **技术指标**: CVD (Cumulative Volume Delta), 背离检测
- **策略类型**: 订单流 / 机构级别
- **适用市场/时间框架**: 期货/加密货币，所有时间框架
- **创新点**: 解决了传统 CVD 指标的历史噪声聚合和渲染卡顿问题。作为结构转变的基线过滤器，在部署更重的 tick 解析模型之前使用。"机构流动性扫荡"检测是亮点。

### 6. Ultimate Composite Scalper
- **URL**: https://www.tradingview.com/script/pCDEXHyW-Ultimate-Composite-Scalper/
- **核心逻辑**: 趋势+动量组合剥头皮指标。做多需 EMA9 > EMA21 + 价格 > VWAP + RSI > 50 三重对齐；做空反之。不满足时标记为震荡（灰色K线）。仅在趋势首次翻转的那根K线上触发信号，且限定 9:30-15:45 EST 交易时段。
- **技术指标**: EMA (9, 21), VWAP, RSI
- **策略类型**: 动量 / 剥头皮
- **适用市场/时间框架**: 日内，美股 RTH 时段
- **创新点**: K线染色系统（绿=多头/红=空头/灰=震荡）提供直观的市场状态可视化。信号只在趋势翻转的第一根K线触发，避免信号轰炸。时间过滤器限制在美股常规交易时段。

---

## Page 9

### 7. AG Pro Fixed Range Control Box [AGPro Series]
- **URL**: https://www.tradingview.com/script/KBVbDH0o-AG-Pro-Fixed-Range-Control-Box-AGPro-Series/
- **核心逻辑**: 固定范围成交量分布控制盒，可视化指定价格区间的成交量分布，识别高成交量节点 (HVN) 和低成交量节点 (LVN)。
- **技术指标**: Volume Profile (固定范围)
- **策略类型**: 订单流 / 支撑阻力
- **适用市场/时间框架**: 通用
- **创新点**: AGPro 系列工具之一，专注于成交量分布分析。

### 8. SPX 0DTE Scalper (Empowerment Assets)
- **URL**: https://www.tradingview.com/script/XPFFCoZ1-SPX-0DTE-Scalper-Empowerment-Assets/
- **核心逻辑**: 标普 500 当日到期 (0DTE) 期权日内的剥头皮策略，针对 0DTE 特有的 Gamma 效应和高波动性设计。
- **技术指标**: 隐含指标组合
- **策略类型**: 波动率 / 剥头皮
- **适用市场/时间框架**: SPX/SPY，日内（0DTE 到期日）
- **创新点**: 专门针对 0DTE 期权到期的日内策略，利用到期日特有的 Gamma 加速和 Pin Risk 特征。

### 9. PPO Divergence Strategy
- **URL**: https://www.tradingview.com/script/WrEqzgAo-PPO-Divergence-Strategy/
- **核心逻辑**: 基于价格百分比振荡器 (PPO) 的背离策略，检测价格与 PPO 之间的顶背离和底背离。
- **技术指标**: PPO (Percentage Price Oscillator)
- **策略类型**: 均值回归 / 背离
- **适用市场/时间框架**: 通用
- **创新点**: PPO 相比 MACD 使用百分比而非绝对值，更适合比较不同价格的品种。

### 10. Pattern Match Price Projection
- **URL**: https://www.tradingview.com/script/zzwiM7w8-Pattern-Match-Price-Projection/
- **核心逻辑**: 识别当前价格形态，在历史数据中搜索相似形态，基于历史匹配结果预测未来价格走势。
- **技术指标**: 形态匹配算法
- **策略类型**: 其他 (形态学/机器学习)
- **适用市场/时间框架**: 通用
- **创新点**: 将当前的 N 根 K 线序列与历史数据做相似度匹配，用历史统计给出未来 N 根 K 线的价格投影。本质上是基于 KNN (K-Nearest Neighbors) 的非参数预测。

### 11. Custom Risk Interval VWAP
- **URL**: https://www.tradingview.com/script/LDvrKrO1-Custom-Risk-Interval-VWAP/
- **核心逻辑**: 可自定义起始时间的 VWAP，支持按风险区间（非标准时段）计算 VWAP 值。
- **技术指标**: VWAP (自定义区间)
- **策略类型**: 支撑阻力
- **适用市场/时间框架**: 日内
- **创新点**: 传统 VWAP 从开盘开始计算，此工具允许自定义起始点，适配夜盘、盘前等非标准交易时段。

### 12. Merged EMA Crossover & Pullback Analyzer
- **URL**: https://www.tradingview.com/script/w9LfP7hY-Merged-EMA-Crossover-Pullback-Analyzer/
- **核心逻辑**: 同时监控 EMA 交叉信号和回踩入场的综合分析器，在趋势确立后等待价格回踩至 EMA 再入场。
- **技术指标**: EMA 多周期
- **策略类型**: 趋势跟踪
- **适用市场/时间框架**: 通用
- **创新点**: 合并了两种入场方式（交叉突破和回踩入场），给交易者更多选择。

---

## Page 10

### 13. RHODL Z-Score [TheSnake3Run]
- **URL**: https://www.tradingview.com/script/Nj0sSuJx-RHODL-Z-Score-TheSnake3Run/
- **核心逻辑**: RHODL (Realized HODL) 比率的 Z-Score 标准化版本，用于识别比特币宏观周期顶部和底部。
- **技术指标**: RHODL Ratio, Z-Score
- **策略类型**: 其他 (链上分析/宏观周期)
- **适用市场/时间框架**: BTC，周线/月线
- **创新点**: 将链上指标 RHODL 引入 TradingView，通过 Z-Score 标准化后可以更清晰地识别 BTC 的宏观超买/超卖状态。

### 14. Kaufman Efficiency Ratio Gate [NovaLens]
- **URL**: https://www.tradingview.com/script/2Ghnhfqg-Kaufman-Efficiency-Ratio-Gate-NovaLens/
- **核心逻辑**: 使用 Kaufman 效率比率 (KER) 作为交易门控过滤器。KER 衡量价格运动的"效率"（净变化/总波动），高效率=趋势市，低效率=震荡市。仅在市场展现趋势效率时才允许交易信号通过。
- **技术指标**: Kaufman Efficiency Ratio (KER)
- **策略类型**: 波动率 / 趋势过滤
- **适用市场/时间框架**: 通用
- **创新点**: 将 KER 作为"门控"机制而非直接交易信号。低效率时自动关闭交易，高效率时才允许入场。可作为任何趋势策略的叠加过滤器使用。

### 15. ALIZET - Sector-Aware Signal Scanner
- **URL**: https://www.tradingview.com/script/LhGGZr0r-ALIZET-Sector-Aware-Signal-Scanner-Auto-Sector/
- **核心逻辑**: 板块感知型信号扫描器，自动识别股票所属板块，在板块轮动背景下生成交易信号。
- **技术指标**: 板块相对强度 + 技术信号组合
- **策略类型**: 动量 / 板块轮动
- **适用市场/时间框架**: 美股，日线
- **创新点**: 将个股技术信号与其所属板块的轮动状态结合，避免在逆板块趋势时入场。

### 16. Turtle Trading Strategy with ATR Stop + Pyramiding
- **URL**: https://www.tradingview.com/script/HYco13Su-Turtle-Trading-Strategy-with-ATR-Stop-Pyramiding/
- **核心逻辑**: 经典海龟交易法则的完整实现。入场：价格突破 20 日最高价（需在 200 MA 之上）。加仓：每上涨 0.5 ATR 加仓一次，最多 4 次。出场：价格跌破 10 日最低价 或 跌破 2x ATR 追踪止损。
- **技术指标**: Donchian Channel (20/10), 200 MA, ATR (20)
- **策略类型**: 趋势跟踪 / 突破
- **适用市场/时间框架**: 通用，日线
- **创新点**: 完整的海龟交易系统实现，包含金字塔加仓逻辑 (每 0.5 ATR 加仓)、ATR 追踪止损、以及仓位管理 (每次 25% 资金)。经典的趋势跟踪策略框架，值得学习其资金管理和加仓逻辑。

### 17. Bigul Price Action Analysis by AnkitGupta
- **URL**: https://www.tradingview.com/script/J3Jelj20-Bigul-Price-Action-Analysis-by-AnkitGupta/
- **核心逻辑**: 纯价格行为分析工具，识别关键价格结构如高/低点、供需区、市场结构突破等。
- **技术指标**: Price Action (价格行为)
- **策略类型**: 支撑阻力
- **适用市场/时间框架**: 通用
- **创新点**: 无需任何技术指标的纯价格结构分析。

---

## Page 11

### 18. Qing LRC + S/R + EMA (Trend Cross Logic)
- **URL**: https://www.tradingview.com/script/ZDhizQgu-Qing-LRC-S-R-EMA-Trend-Cross-Logic/
- **核心逻辑**: 线性回归通道 (LRC) + 支撑阻力位 + EMA 趋势交叉的三合一系统。在 LRC 通道内识别支撑阻力，用 EMA 交叉确认趋势方向。
- **技术指标**: 线性回归通道, EMA, 支撑阻力
- **策略类型**: 趋势跟踪 / 支撑阻力
- **适用市场/时间框架**: 通用
- **创新点**: 将统计学的线性回归通道与传统技术分析结合，提供数学化的趋势边界。

### 19. BTC MTF Engulfing Flip Strategy (1H, 2X)
- **URL**: https://www.tradingview.com/script/XGqSzuxJ-BTC-MTF-Engulfing-Flip-Strategy-1H-2X/
- **核心逻辑**: BTC 多时间框架吞没翻转策略。在 1 小时图上执行，2 倍杠杆。核心信号为看涨/看跌吞没形态，结合多时间框架确认。
- **技术指标**: 多时间框架吞没形态
- **策略类型**: 动量 / K线形态
- **适用市场/时间框架**: BTC，1H
- **创新点**: 专门为 BTC 优化的吞没策略，包含杠杆管理和多时间框架过滤。

### 20. EvolveX Weinstein Stages v2
- **URL**: https://www.tradingview.com/script/xShdxXHH-EvolveX-Weinstein-Stages-v2/
- **核心逻辑**: 基于 Stan Weinstein 的四阶段市场周期理论 (Stage 1 底部/Stage 2 上涨/Stage 3 顶部/Stage 4 下跌)，自动识别当前所处的市场阶段。
- **技术指标**: 30 WMA, 阶段分类算法
- **策略类型**: 趋势跟踪
- **适用市场/时间框架**: 通用，周线级别
- **创新点**: 将 Weinstein 经典的四阶段理论量化实现，为交易者提供当前市场所处阶段的自动判断。Stage 2 才做多，Stage 4 才做空。

### 21. Dynamic Regime Matrix [Adaptive 5-Layer System]
- **URL**: https://www.tradingview.com/script/tJJU9S3O/
- **核心逻辑**: 专业级 5 层过滤系统。第 1 层: 高时间框架制度过滤 (Chikou Span + ADX 分类为趋势/震荡/风暴)。第 2 层: 波动率门控 (ATR/SMA 交叉，低波动时关闭交易)。第 3 层: 趋势确认 (EMA 带对齐 + Chikou 确认)。第 4 层: 入场触发 (CCI + RSI 隐蔽背离)。第 5 层: 风险管理 (自动计算 ATR 止损和两个止盈目标)。
- **技术指标**: Chikou Span, ADX, ATR, SMA, EMA Ribbon, CCI, RSI
- **策略类型**: 趋势跟踪 (多层级过滤)
- **适用市场/时间框架**: 指数期货 (日经/NQ/ES)，3m/5m
- **创新点**: 本页最值得深入研究的策略。5 层架构设计精妙：(1) "风暴模式"识别极端过度延伸波动并自动关闭交易；(2) 自动模式根据 ADX 强度动态调整参数（强趋势时放宽波动率门控、扩大 TP 目标、缩短 CCI 触发周期）；(3) 诊断面板实时显示每层过滤器的通过/失败状态；(4) 严格不重绘。

### 22. Monthly Armed + Weekly Trigger MACD Backtest with Nifty Table
- **URL**: https://www.tradingview.com/script/cddzPyX0-Monthly-Armed-Weekly-Trigger-MACD-Backtest-with-Nifty-Table/
- **核心逻辑**: 使用月线确定大方向，周线 MACD 作为触发信号。两层时间框架确认后执行交易。
- **技术指标**: MACD (周线), 趋势方向 (月线)
- **策略类型**: 趋势跟踪 / 多时间框架
- **适用市场/时间框架**: Nifty 50，周线/月线
- **创新点**: "Armed" 概念 -- 月线给出方向后"武装"系统，等待周线 MACD 触发。两个时间框架的逻辑关系清晰：月线定方向，周线定时机。

### 23. OBV Divergence Finder - Jeff 2026
- **URL**: https://www.tradingview.com/script/paz68Avj-OBV-Divergence-Finder-Jeff-2026/
- **核心逻辑**: 能量潮指标 (OBV) 背离探测器，检测价格与 OBV 之间的顶背离（看跌）和底背离（看涨）。
- **技术指标**: OBV (On Balance Volume)
- **策略类型**: 均值回归 / 背离
- **适用市场/时间框架**: 通用
- **创新点**: OBV 是累积性指标，其背离比普通振荡器的背离更能反映资金流向的真实变化。

### 24. Qing (EMA + MACD + Squeeze)
- **URL**: https://www.tradingview.com/script/PxAUrVvp-Qing-EMA-MACD-Squeeze/
- **核心逻辑**: EMA 趋势方向 + MACD 动量确认 + TTM Squeeze 波动率压缩的三合一系统。在波动率收缩 (squeeze) 释放时结合 EMA 和 MACD 方向入场。
- **技术指标**: EMA, MACD, TTM Squeeze (Bollinger Bands + Keltner Channels)
- **策略类型**: 波动率 / 趋势跟踪
- **适用市场/时间框架**: 通用
- **创新点**: Squeeze (布林带收缩到 Keltner 通道内部) 是波动率极端压缩的信号，释放时往往伴随强烈方向性运动。将波动率分析与趋势/动量指标结合，提供完整的入场框架。

### 25. Milman's Crypto Breadth: % Above MA
- **URL**: https://www.tradingview.com/script/oWT4ZTll-Milman-s-Crypto-Breadth-Above-MA/
- **核心逻辑**: 加密货币市场宽度指标，计算所有主要加密货币中有多少百分比的价格位于其移动平均线之上。高百分比=市场整体强势，低百分比=弱势。
- **技术指标**: 市场宽度 (% Above MA)
- **策略类型**: 其他 (市场宽度/宏观)
- **适用市场/时间框架**: 加密货币市场整体，日线
- **创新点**: 类似股票市场中的 A/D 线或新高新低指数，但针对加密货币市场。可用于判断加密市场整体是处于风险偏好 (Risk-On) 还是风险规避 (Risk-Off) 状态。

### 26. MTF Trend Cascade
- **URL**: https://www.tradingview.com/script/C5ZqqsDO-mtf-trend-cascade/
- **核心逻辑**: 多时间框架趋势级联系统。将多个时间框架的趋势状态堆叠显示，只有当所有时间框架趋势方向一致时才给出高确信度信号。
- **技术指标**: 多时间框架趋势指标
- **策略类型**: 趋势跟踪 / 多时间框架
- **适用市场/时间框架**: 通用
- **创新点**: "级联"概念 -- 从高时间框架到低时间框架依次确认趋势，类似瀑布式的多级过滤。

### 27. Momentum Shift [BdeRijk]
- **URL**: https://www.tradingview.com/script/TmHj12y5-Momentum-Shift-BdeRijk/
- **核心逻辑**: 动量转换检测器，识别动量从正转负或从负转正的关键拐点。
- **技术指标**: 动量指标组合
- **策略类型**: 动量
- **适用市场/时间框架**: 通用
- **创新点**: 专注于动量转换 (shift) 的检测，而非动量本身的方向。

---

## Page 12

### 28. BTC Scalper by Sandip
- **URL**: https://www.tradingview.com/script/Ufg2YGEz-BTC-Scalper-by-Sandip/
- **核心逻辑**: 专门为 BTC 设计的剥头皮策略，针对加密货币特有的波动率和流动性特征优化。
- **技术指标**: 定制指标组合
- **策略类型**: 剥头皮
- **适用市场/时间框架**: BTC，短线
- **创新点**: 专门针对 BTC 特有的波动率和 24/7 市场特征优化。

### 29. VROC Percentage Standardized Momentum Indicator
- **URL**: https://www.tradingview.com/script/ExSJtOB9-VROC-Percentage-Standardized-Momentum-Indicator-RevisedVersion/
- **核心逻辑**: 成交量变化率 (VROC) 的标准化版本，将成交量变化转化为百分比形式，便于跨品种比较。
- **技术指标**: VROC (Volume Rate of Change), 标准化处理
- **策略类型**: 波动率 / 动量
- **适用市场/时间框架**: 通用
- **创新点**: 标准化后的 VROC 可以跨品种比较，解决了不同价格/成交量级别品种无法直接比较成交量变化的问题。

### 30. AG Pro Volatility Shape Classifier
- **URL**: https://www.tradingview.com/script/DDB8YRuN-AG-Pro-Volatility-Shape-Classifier-AGPro-Series/
- **核心逻辑**: 波动率形态分类器，将当前市场波动率模式分类为不同的"形状"（如三角形收缩、扩张、均匀等），根据波动率形态预测后续走势。
- **技术指标**: 波动率形态分析
- **策略类型**: 波动率
- **适用市场/时间框架**: 通用
- **创新点**: 将波动率的"形状"作为分类维度，超越了简单的"高/低波动率"二元分类。

### 31. Pro MTF Trend Dashboard [11 TFs]
- **URL**: https://www.tradingview.com/script/egWmIuN1-pro-mtf-trend-dashboard-11-tfs/
- **核心逻辑**: 覆盖 11 个时间框架的趋势仪表盘，一目了然地显示从 1 分钟到月线的趋势方向。
- **技术指标**: 多时间框架趋势分析
- **策略类型**: 趋势跟踪
- **适用市场/时间框架**: 通用，全时间框架
- **创新点**: 11 个时间框架的趋势状态压缩在一个面板中，快速评估多时间框架一致性。

### 32. AG Pro Value Migration Bands [AGPro Series]
- **URL**: https://www.tradingview.com/script/wGKF0kAU-AG-Pro-Value-Migration-Bands-AGPro-Series/
- **核心逻辑**: 价值迁移带，追踪成交量加权价值区间的移动方向，识别"价值"从旧区间迁移到新区间的过程。
- **技术指标**: Volume Profile, 价值区间追踪
- **策略类型**: 支撑阻力 / 订单流
- **适用市场/时间框架**: 通用
- **创新点**: "价值迁移"概念 -- 当成交量加权价值区从旧位置移动到新位置，代表市场参与者共识的转移，是趋势确认的重要信号。

### 33. Relative Strength During Market Correction
- **URL**: https://www.tradingview.com/script/ABlI2wJW-Relative-Strength-During-Market-Correction/
- **核心逻辑**: 专门在市场回调期间识别相对强势股的工具。在大盘下跌时，逆势上涨或跌幅最小的股票往往在大盘反弹时领涨。
- **技术指标**: 相对强度 (RS), 市场回调检测
- **策略类型**: 动量 / 相对强度
- **适用市场/时间框架**: 美股，日线
- **创新点**: 不是通用的 RS 指标，而是专门在"市场回调"这种特定环境下的 RS 分析。这种环境下表现强势的股票具有特殊意义。

---

## Page 13

### 34. NSE F&O OI Analysis Indicator
- **URL**: https://www.tradingview.com/script/KRqTcqtl-NSE-F-O-OI-Analysis-indicator/
- **核心逻辑**: 印度 NSE 期货和期权未平仓量 (OI) 分析工具，追踪 OI 变化识别支撑阻力和市场情绪。
- **技术指标**: Open Interest (OI) 分析
- **策略类型**: 订单流
- **适用市场/时间框架**: 印度 NSE F&O，日内
- **创新点**: 将期权市场的 OI 数据纳入分析，OI 聚集区往往是强力支撑/阻力。

### 35. BTC CME Weekend Gap Tracker
- **URL**: https://www.tradingview.com/script/HunddRzh-BTC-CME-Weekend-Gap-Tracker/
- **核心逻辑**: 追踪 BTC CME 期货的周末跳空缺口。CME 周五收盘到周日开盘之间的价格差距，历史上大概率会被回补。
- **技术指标**: 缺口追踪
- **策略类型**: 均值回归
- **适用市场/时间框架**: BTC，周末缺口
- **创新点**: 利用传统金融市场 (CME 期货) 与加密货币 24/7 市场之间的时间差，CME 休息期间的 BTC 价格变动会在 CME 重开时形成缺口，这些缺口有很高的回补概率。

### 36. AG Pro Mean Reversion Corridors [AGPro Series]
- **URL**: https://www.tradingview.com/script/B2aMfpd2-AG-Pro-Mean-Reversion-Corridors-AGPro-Series/
- **核心逻辑**: 均值回归走廊，基于统计学的价格偏离度构建交易通道。当价格偏离均值到统计显著水平时入场，预期回归均值。
- **技术指标**: 统计偏离度, 均值回归通道
- **策略类型**: 均值回归
- **适用市场/时间框架**: 震荡市
- **创新点**: 用统计学方法（标准差、Z-Score）定义"过度偏离"，提供量化而非主观的均值回归入场标准。

### 37. XAG Hybrid Sniper [Snowball V8.1]
- **URL**: https://www.tradingview.com/script/Iq9pwZtu-XAG-Hybrid-Sniper-Snowball-V8-1/
- **核心逻辑**: 专为白银 (XAG/USD) 设计的混合狙击策略。"雪球"概念意味着逐步累积利润。结合趋势和均值回归元素。
- **技术指标**: 混合指标组合
- **策略类型**: 混合 (趋势+均值回归)
- **适用市场/时间框架**: XAG/USD 白银
- **创新点**: 专门针对白银特有的波动率和流动性特征优化，"雪球"式的渐进加仓/止盈逻辑。

### 38. BTC Potential Energy
- **URL**: https://www.tradingview.com/script/s9RAL9EM-BTC-Potential-Energy/
- **核心逻辑**: 将物理学中的"势能"概念应用于 BTC 价格分析。价格在某个方向上累积的"势能"越大，释放时运动越剧烈。
- **技术指标**: 势能指标 (自定义)
- **策略类型**: 波动率 / 其他
- **适用市场/时间框架**: BTC
- **创新点**: 用物理学势能的概念量化价格压缩/蓄力程度。高势能 = 即将爆发大行情，低势能 = 市场已释放能量进入盘整。

---

## Page 14

### 39. Minervini SEPA System
- **URL**: https://www.tradingview.com/script/DL8BpgzT-Minervini-SEPA-System/
- **核心逻辑**: 完整实现 Mark Minervini 的 SEPA (特定入场点分析) 方法论。系统实时评分 8 项 Trend Template 标准：(1) 价格 > 150/200 MA, (2) 150 MA > 200 MA, (3) 200 MA 上升趋势, (4) 50 MA > 150/200 MA, (5) 价格 > 50 MA, (6) 高于 52 周低点 25%, (7) 距 52 周高点 25% 以内, (8) RS 评级 > 70。VCP (波动率收缩形态) 检测：ATR < 60% 的 50 日均量 AND 成交量 < 70% 的 50 日均量。突破信号：Stage 2 确认 + 收盘价突破最近 pivot high + 前一根在 pivot 之下 + 成交量 > 140% 均量。
- **技术指标**: SMA (50, 150, 200), ATR, Volume, RS Rating (vs SPY), VCP 检测
- **策略类型**: 趋势跟踪 / 突破 (成长股选股)
- **适用市场/时间框架**: 美股成长股，日线
- **创新点**: **本批最有价值的策略之一。** 完整实现了 Minervini 的选股-评分-监控-入场四步流程：(1) 自动 8 项标准评分；(2) 实时 VCP 检测 (ATR 收缩 + 成交量萎缩)；(3) 成交量确认的突破信号。背景颜色系统 (蓝=Stage 2/绿=VCP 形成) 提供即时视觉反馈。包含完整的资金管理规则 (1% 风险，3:1 盈亏比)。

### 40. Greenblatt ROC
- **URL**: https://www.tradingview.com/script/mk7Q8Sy6-Greenblatt-ROC/
- **核心逻辑**: 基于 Joel Greenblatt 的"神奇公式"思路，使用变动率 (ROC) 排名识别相对强势股。
- **技术指标**: ROC (Rate of Change)
- **策略类型**: 动量 / 相对强度
- **适用市场/时间框架**: 美股，日线/周线
- **创新点**: Greenblatt 的神奇公式核心是买入"好公司+便宜价格"，ROC 用于量化"好公司"的动量维度。

### 41. XAUUSD Flow Profile PRO CLEAN MTF
- **URL**: https://www.tradingview.com/script/Si8oZ6Ex/
- **核心逻辑**: 黄金 (XAU/USD) 多时间框架成交量分布分析，追踪不同时间框架的资金流向。
- **技术指标**: Volume Profile (多时间框架)
- **策略类型**: 订单流 / 支撑阻力
- **适用市场/时间框架**: XAU/USD 黄金，多时间框架
- **创新点**: 专为黄金市场优化的 Volume Profile，黄金市场的流动性分布与股票/加密货币显著不同。

### 42. Forex Strong Weak Analysis (FX SW)
- **URL**: https://www.tradingview.com/script/cP9tErtS-Forex-Strong-Weak-Analysis-FX-SW/
- **核心逻辑**: 外汇强势弱势分析，同时对所有主要货币对进行强度排名，找出最强和最弱货币。做多最强货币/做空最弱货币。
- **技术指标**: 货币强度指数
- **策略类型**: 动量 / 相对强度
- **适用市场/时间框架**: 外汇市场，多时间框架
- **创新点**: 外汇交易的核心逻辑 -- 货币对是两个货币的比率，因此分析单个货币的强弱比分析货币对本身更有意义。做多最强 vs 做空最弱是外汇市场最高概率的交易方式之一。

### 43. Vantage-X [3.0]
- **URL**: https://www.tradingview.com/script/AQxfmHcn-Vantage-X-3-0/
- **核心逻辑**: Vantage-X 综合交易系统的第三版，集成多种分析方法的复合策略系统。
- **技术指标**: 复合指标系统
- **策略类型**: 混合
- **适用市场/时间框架**: 通用
- **创新点**: 第三版迭代，说明经过实战验证和持续优化。

### 44. Squeeze Momentum + MACD Overlay
- **URL**: https://www.tradingview.com/script/a8UWODO4-Squeeze-Momentum-MACD-Overlay/
- **核心逻辑**: TTM Squeeze 波动率收缩 + 动量方向 + MACD 确认的三合一叠加指标。在 Squeeze 释放时，动量和 MACD 共同确认方向后入场。
- **技术指标**: TTM Squeeze, 动量指标, MACD
- **策略类型**: 波动率 / 动量
- **适用市场/时间框架**: 通用
- **创新点**: 将三个独立的确认维度（波动率收缩释放、动量方向、MACD 趋势）叠加在一起，形成高确信度的入场信号。

### 45. EMA Super Cloud
- **URL**: https://www.tradingview.com/script/Ylj7UWgD/
- **核心逻辑**: 多条 EMA 形成的"超级云带"，通过 EMA 带的宽度、颜色和方向判断趋势强度和方向。
- **技术指标**: 多条 EMA 组成的云带
- **策略类型**: 趋势跟踪
- **适用市场/时间框架**: 通用
- **创新点**: 将多条 EMA 之间的区域填充为"云"，云的宽度反映趋势强度，颜色反映方向，方向变化提供趋势转换信号。类似一目均衡表的云带概念但基于 EMA。

---

## 重点策略推荐 (Top Picks)

### 最值得深入研究:

1. **Dynamic Regime Matrix [5-Layer]** - 本批最复杂的系统化策略框架，5 层过滤架构设计精妙，"风暴模式"和自动参数调整机制值得借鉴。适合构建自适应策略系统。

2. **Minervini SEPA System** - 完整的成长股交易系统，从选股 (8项标准评分) 到入场 (VCP + 突破) 到风控 (ATR止损) 的全流程。适合A股/美股成长股交易。

3. **Turtle Trading Strategy with ATR Stop** - 经典趋势跟踪策略的完整实现，金字塔加仓和 ATR 追踪止损是资金管理的教科书。

4. **Institutional CVD Divergence** - 机构级 CVD 背离分析，轻量化设计解决了传统 CVD 工具的痛点。适合期货和加密货币市场。

5. **Kaufman Efficiency Ratio Gate** - 简洁但强大的趋势过滤器，KER 作为交易门控的概念可以叠加到任何策略上。

### 按策略类型分类:

| 类型 | 代表策略 |
|------|---------|
| 趋势跟踪 | Simple Long Only Bot, Turtle Trading, Dynamic Regime Matrix, Minervini SEPA |
| 均值回归 | AG Pro Mean Reversion Corridors, BTC CME Weekend Gap |
| 动量 | Ultimate Composite Scalper, SMA+MACD+RSI, Momentum Shift |
| 波动率 | Volatility Vault EMA Tap, Squeeze+MACD, VROC Standardized |
| 订单流 | Institutional CVD Divergence, NSE F&O OI, AG Pro Value Migration |
| 支撑阻力 | XAUUSD Flow Profile, Custom Risk Interval VWAP |
| 多时间框架 | Pro MTF Trend Dashboard, MTF Trend Cascade, Qing (EMA+MACD+Squeeze) |
| 宏观/市场宽度 | RHODL Z-Score, Crypto Breadth % Above MA, Forex Strong Weak |

### 可借鉴的通用设计模式:

1. **多层过滤架构** (Dynamic Regime Matrix) - HTF 方向 -> 波动率门控 -> 趋势确认 -> 入场触发 -> 风控输出
2. **评分系统** (Minervini SEPA) - 多维标准量化评分，阈值触发
3. **门控机制** (KER Gate) - 用效率指标作为开关，低效时不交易
4. **VCP 检测** (Minervini SEPA) - ATR 收缩 + 成交量萎缩 = 蓄力阶段
5. **金字塔加仓** (Turtle Trading) - 每 N 倍 ATR 加仓一次，限最大次数
6. **时间过滤** (Ultimate Composite Scalper) - 限定交易时段避免低流动性
7. **自动参数调整** (Dynamic Regime Matrix) - 根据 ADX 强弱动态调整灵敏度
