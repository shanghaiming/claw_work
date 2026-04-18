# TradingView 策略学习笔记 - Page 1~7

> 数据来源: TradingView 热门脚本 (2026年4月)
> 跳过: 描述过短/无实质内容的策略 (如 RPS Bot, retardwicks, stdvCOOCHIE 等)

---

## 1. SuperTrend Take-Profit Dimensions [AlgoAlpha]

**URL**: https://www.tradingview.com/script/tb1TiNJe-SuperTrend-Take-Profit-Dimensions-AlgoAlpha/

**核心逻辑**: 运行标准 SuperTrend 并记录每个确认的 zigzag pivot，将 pivot 按多空方向存入不同池，然后计算当前 bar 在多个独立维度（成交量/时间/价格位置）上与历史 pivot 的相似度，输出一个 0-100 的综合得分来辅助止盈决策。

**技术指标**: SuperTrend (ATR-based trailing stop), ZigZag Pivot, Relative Volume Percentile, Position in Range

**策略类型**: 趋势跟踪 (止盈辅助)

**适用市场/时间框架**: 日内流动性品种，所有时间框架

**创新点**:
- 多维度条件直方图评分: 不仅看价格，还结合成交量百分位、一天中的时间、近期范围中的价格位置三个不相关维度
- 支持 4 个独立轴（3个内置 + 1个用户自定义 0-100 信号源），每个轴的评分都以上下文条件为基准
- 不预测方向，只给出"当前环境与历史趋势终点有多相似"的数据支持，帮助趋势跟随者决定何时收紧管理

---

## 2. Momentum Terrain 3D [LuxAlgo]

**URL**: https://www.tradingview.com/script/WgcQ7iYB-Momentum-Terrain-3D-LuxAlgo/

**核心逻辑**: 同时计算多个回看长度的 RSI，将 RSI 的周期维度（快慢）、时间维度（历史到当前）和数值维度（0-100）投射到 3D 地形图中，通过地形起伏直观展示短长期动量的协同与背离。

**技术指标**: RSI (多周期，从 min 5 到 max 60), 3D 投影渲染 (三角变换 Yaw/Pitch), OB/OS Pillar

**策略类型**: 动量

**适用市场/时间框架**: 所有市场，适合需要同时监控多周期动量的场景

**创新点**:
- 将多周期 RSI 映射到 3D 地形，X轴=时间，Y轴=回看长度，Z轴=RSI值
- 用 Pine Script 的 polyline 和 matrix 系统实现 3D 渲染引擎
- "统一地形"（整个地形同步升高）= 全周期动量一致；"前景下沉后景高" = 趋势中的回调
- 地形平坦 = 震荡/无方向市场

---

## 3. Statistical VWAP Study: Session and RTH VWAP

**URL**: https://www.tradingview.com/script/Wyyu0A2w-Statistical-VWAP-study-Session-and-RTH-VWAP/

**核心逻辑**: 计算两条独立的 VWAP（Session VWAP 锚定盘前/自定义时段，RTH VWAP 锚定常规交易时段开盘），以两者中点为锚，构建包含对称/非对称标准差带、MAD带、百分位带、偏差VWAP 等完整统计框架，并跟踪两者交叉、回测事件的胜率和时间分布。

**技术指标**: VWAP (双线独立), Volume-Weighted Standard Deviation, Median Absolute Deviation, Percentile Bands, 偏差VWAP

**策略类型**: 均值回归 / 支撑阻力

**适用市场/时间框架**: 股指期货为主，1min-15min 日内

**创新点**:
- Session VWAP 会在创出新高时动态重新锚定（high-anchored VWAP），而非固定在首根 bar
- 非对称标准差带: 分别计算上/下半区各自的 volume-weighted variance，比对称带更真实反映方向性偏斜
- 完整的统计面板: 胜率追踪、VWAP回测/交叉的平均次数、事件时间分布（峰值时段）、每小时事件计数
- MAD 带与 sigma 带对比可识别"少数极端 bar 膨胀了波动率"

---

## 4. Reversal Probability & Signals

**URL**: https://www.tradingview.com/script/Vg1GzKm7-Reversal-Probability-Signals/

**核心逻辑**: 使用 Pine Script 内置的 KNN 机器学习算法，同时计算 8 个不同长度的 CCI 作为特征集，在历史 pivot 高/低点处记录特征向量，每根新 bar 计算与历史样本的欧几里得距离，取 K 个最近邻投票决定当前 bar 形成反转 pivot 的概率。

**技术指标**: CCI (8个长度从10到200), KNN 分类器, Pivot Points

**策略类型**: 均值回归 (反转预测)

**适用市场/时间框架**: 所有市场，建议配合趋势环境使用

**创新点**:
- 纯 Pine Script 实现 KNN 机器学习，无需外部数据
- 两步信号逻辑: 概率先超过上阈值(80%)=极端条件，然后回落穿过下阈值(50%)=确认反转开始，避免在强趋势中过早入场
- 动态 K 值: 根据可用数据量自动缩放并取奇数，防止平票
- 同时收集"非目标"随机样本构建平衡数据集

---

## 5. Market Structure Adaptive RSI

**URL**: https://www.tradingview.com/script/hyrV5uP1-Market-Structure-Adaptive-RSI/

**核心逻辑**: 根据 CHoCH（特征变化）和 BOS（结构突破）事件动态切换 RSI 模式: CHoCH 后切到正常模式（无平滑/回调模式），BOS 后切到趋势模式（平滑）；连续同向结构事件越多，平滑长度越短，RSI 越快，以便在延伸趋势中及早发现回调。

**技术指标**: RSI (自适应长度), EMA (动态平滑), Pivot Points (多长度1-5), CHoCH/BOS 标记

**策略类型**: 趋势跟踪 / 动量

**适用市场/时间框架**: 所有市场，特别适合有明显波段结构的市场

**创新点**:
- 将市场结构事件（CHoCH/BOS）作为 RSI 平滑长度的控制信号，实现"制度切换"
- 核心洞察: 连续同向结构事件越多 -> 回调概率越高 -> 应该让 RSI 更快
- 多 Pivot 长度同时分析市场结构，聚合事件后选择最大 pivot 的突破，减少噪音
- 在趋势中逐渐加快 RSI，在结构变化时重置，兼顾稳定性和灵敏度

---

## 6. Adaptive Fourier Transform CCI [QuantAlgo]

**URL**: https://www.tradingview.com/script/KWRHKdqw-Adaptive-Fourier-Transform-CCI-QuantAlgo/

**核心逻辑**: 用离散傅里叶变换(DFT)检测价格的主导周期，将 CCI 的回看长度设为该周期，使 CCI 自然适应快速高频率和慢速长周期市场环境。先用高通滤波器去趋势，再用 Super Smoother 去噪，然后 DFT 扫描候选周期找最强谱能量。

**技术指标**: CCI (自适应长度), Discrete Fourier Transform (DFT), 高通滤波器, Super Smoother 滤波器, EMA

**策略类型**: 动量 / 波动率

**适用市场/时间框架**: 所有市场，提供 Fast Response (5min-1H) 和 Smooth Trend (Daily-Weekly) 两个预设

**创新点**:
- 将信号处理领域的频谱分析引入 CCI: 高通滤波 -> Super Smoother -> DFT 主导周期检测 -> 自适应 CCI 长度
- 不需要手动调整周期参数，指标自动适配当前市场的"节奏"
- 最终自适应长度 = clamp(round(dominantPeriod x lengthMult), 5, 60)
- 预设 Fast/Smooth 两种模式，分别适配日内和波段

---

## 7. CCI Regime Oscillator

**URL**: https://www.tradingview.com/script/R1Xog6Lv-CCI-Regime-Oscillator/

**核心逻辑**: 使用 CCI 着色来可视化当前价格与历史价格趋势的偏离程度，通过颜色线（绿/红/灰）判断多头/空头/中性状态，并在极早期标记买点（绿点）和卖点（红点）。

**技术指标**: CCI (Commodity Channel Index)

**策略类型**: 均值回归

**适用市场/时间框架**: 所有市场

**创新点**: 描述较简短，核心是将 CCI 的偏离度以颜色直观呈现，实现早期买卖点标记。思路直接但实用性有限。

---

## 8. 7-Point Structural Oscillator [Tension]

**URL**: https://www.tradingview.com/script/HoOmIwBl-7-Point-Structural-Oscillator-Tension/

**核心逻辑**: 构建由7个关键结构坐标组成的7维参考框架（前/当前 swing high/low, 摆动间最高/最低/中点），计算当前价格相对于这7个结构格点的净位移（结构张力），正值=多头结构主导，负值=空头主导。

**技术指标**: Swing High/Low (Pivot Points), Inter-Swing Max/Min, Structural Midpoint, 张力指标

**策略类型**: 支撑阻力 / 趋势跟踪

**适用市场/时间框架**: 有清晰波段结构的市场（股票/外汇/加密货币），不适用于极端波动或低流动性

**创新点**:
- 将"市场几何"概念量化: 不是简单看价格和均线的距离，而是看价格与7个关键结构点（包括摆动间局部阻力/支撑/均衡面）的综合关系
- 零线交叉 = 突破结构均衡; 极值区 = 可能均值回归
- 支持背离分析: 价格新高但张力更低 = 结构弱化
- 多时间框架建议: 大周期(10)定方向，小周期(5)定入场

---

## 9. Haar Wavelet Range Filter [Jamallo]

**URL**: https://www.tradingview.com/script/82NYRAdD-Haar-Wavelet-Range-Filter-Jamallo/

**核心逻辑**: 使用 Maximal Overlap Discrete Wavelet Transform (MODWT) 配合 Haar 基函数将价格分解为趋势系数（Scaling）和噪声系数（Detail），通过 Detail 能量的自适应阈值产生阶梯式趋势线，在盘整时保持平坦、在真实波动变化时果断移动。

**技术指标**: MODWT Haar 小波变换, Detail Energy (自适应阈值), 线性插值百分位带

**策略类型**: 趋势跟踪

**适用市场/时间框架**: 所有市场，分解级别1-5可从2bar到32bar

**创新点**:
- 从时间域转向频率域处理价格: 解决传统均线"太快怕噪音/太慢怕滞后"的根本矛盾
- MODWT（而非标准 DWT）使滤波器平移不变，不会在新增 bar 时"跳动"或重绘
- 非参数百分位带替代标准差带，不假设正态分布
- 阶梯式输出: 盘整时几乎不动，趋势时果断切换

---

## 10. RSI Pro (HA + BB + Divergence + Signals)

**URL**: https://www.tradingview.com/script/3vdudZWw-RSI-Pro-HA-BB-Divergence-Signals/

**核心逻辑**: 将 RSI 增强为 Heikin Ashi K 线形式以平滑可视化，叠加 Bollinger Bands 提供波动率上下文，自动检测价格-RSI 背离，并基于 BB 回归逻辑生成买卖信号（RSI 穿出下轨后回归 = 买入，穿出上轨后回归 = 卖出）。

**技术指标**: RSI, Heikin Ashi 转换, Bollinger Bands, 背离检测, RSI MA

**策略类型**: 动量 / 均值回归

**适用市场/时间框架**: 趋势或波动率扩张环境

**创新点**:
- 将 HA 平滑思想应用到 RSI 上（而非价格），生成 RSI HA K 线更好地可视化动量变化
- 信号基于 BB re-entry: RSI 跌出下轨后回归内部 + 看涨确认 = 买，RSI 升出上轨后回归内部 + 看跌确认 = 卖
- 多层融合: 动量(RSI) + 波动率(BB) + 结构(背离) + 信号 在一个工具中

---

## 11. Smart Trader, Episode 06, Isotropic Trend Lines

**URL**: https://www.tradingview.com/script/ZSgx4eSy-Smart-Trader-Episode-06-Isotropic-Trend-Lines/

**核心逻辑**: 在 Isotropic Coordinate System (ICS) 中构建趋势线，先用 Yang-Zhang 波动率估计器将价格标准化为 sigma 单位，然后在 6 个尺度（素数块周期 3/7/13/19/29/47）上并行检测趋势角度，最终将多尺度角度聚类为可用趋势线。

**技术指标**: Yang-Zhang 波动率估计器, ICS 坐标系, 多尺度角度检测, 聚类算法, 趋势线几何

**策略类型**: 趋势跟踪 / 支撑阻力

**适用市场/时间框架**: 所有市场，学术级工具

**创新点**:
- sigma 标准化坐标系使趋势角度成为结构属性，独立于图表显示比例
- 6 个并行尺度使用素数块周期，覆盖从微观到宏观的波动层次
- 角度聚类将多尺度检测结果合并为连贯趋势线，消除单尺度噪声

---

## 12. Magic Hour: Master Playbook [Dokakuri Study]

**URL**: https://www.tradingview.com/script/qppVP2FI-Magic-Hour-Master-Playbook-Dokakuri-Study/

**核心逻辑**: 基于 13 年 NQ 历史数据统计，发现 07:00 NY 时间前后存在 83.4% 的均值回归概率。以该时间窗口为核心，构建 Z1-Z6 扩展区域映射系统，辅助日内统计套利。

**技术指标**: 统计均值回归, 时间窗口分析 (Golden Hour), Zone 扩展映射 (Z1-Z6), 历史胜率追踪

**策略类型**: 均值回归 / 统计套利

**适用市场/时间框架**: NQ/ES 期货，1min-5min 日内

**创新点**:
- 13 年数据的统计验证，07:00 NY "黄金时刻" 83.4% 回归率
- Z1-Z6 六级区域映射，从核心区到极端延伸区的完整分类
- 不是技术指标而是统计框架，以历史概率为核心决策依据

---

## 13. Liquidity Contour Engine [JOAT]

**URL**: https://www.tradingview.com/script/pUkFnZnK-Liquidity-Contour-Engine-JOAT/

**核心逻辑**: 通过计算买卖双方流动性池的空间分布，构建流动性等高线图。识别关键流动性聚集区域（买卖止损密集区），跟踪价格在不同流动性区域间的移动路径，辅助判断市场操控方向。

**技术指标**: 流动性池识别, 等高线映射, 买卖止损聚集区, 区域间移动追踪

**策略类型**: 流动性分析 / 市场结构

**适用市场/时间框架**: 所有流动性充足的市场

**创新点**:
- 将流动性分布可视化为等高线地形图，直觉理解"流动性引力"
- 追踪价格在买方/卖方流动性池之间的移动路径
- 与 JOAT 系列其他模块（波动率/成交量/结构）形成完整分析框架

---

## 14. Volumetric Structure Engine [JOAT]

**URL**: https://www.tradingview.com/script/MD1PrIxW-Volumetric-Structure-Engine-JOAT/

**核心逻辑**: 通过 per-leg volume delta 分析市场结构质量。在确认的摆动高低点之间累积成交量 delta，用颜色编码标记每段结构的质量（机构级 vs 散户级），将成交量维度融入市场结构分析。

**技术指标**: Per-Leg Volume Delta, Swing Points, 结构质量评分, 颜色编码成交量

**策略类型**: 成交量分析 / 市场结构

**适用市场/时间框架**: 所有市场，特别适合日内

**创新点**:
- 不是简单看 total delta，而是按确认的摆动区间分段累积 volume delta
- 结构段的颜色编码直接反映"这波移动是机构驱动的还是散户推动的"
- 将成交量信息与价格结构事件精确关联，而非全局模糊对应

---

## 15. Merged EMA Crossover & Pullback Analyzer

**URL**: https://www.tradingview.com/script/p8mAdBcy-Merged-EMA-Crossover-Pullback-Analyzer/

**核心逻辑**: 融合 EMA 交叉信号和回调分析，在 EMA 交叉确认趋势方向后，识别价格回到 EMA 区域的回调机会。同时标记交叉点和有效回调入场点，提供完整的趋势跟踪入场框架。

**技术指标**: EMA (多周期), 交叉检测, 回调识别, 入场信号

**策略类型**: 趋势跟踪

**适用市场/时间框架**: 所有市场，趋势环境

**创新点**:
- 将趋势确认（EMA交叉）和入场优化（回调）合二为一
- 避免追高入场，等待回调到 EMA 区域再进场

---

## 16. Trendlines with Breaks [EXCAVO]

**URL**: https://www.tradingview.com/script/J49l5VTa-Trendlines-with-Breaks-EXCAVO/

**核心逻辑**: 自动从 pivot 高低点构建动态趋势线，用 ATR 容差合并相近的趋势线触点，要求至少 3 次历史验证。检测趋势线突破事件，标记突破点和回测点。

**技术指标**: Pivot Points, 动态趋势线, ATR 合并容差, 突破检测, 历史验证计数

**策略类型**: 趋势跟踪 / 突破

**适用市场/时间框架**: 所有市场

**创新点**:
- ATR 基础的合并容差解决"趋势线太密"的问题
- 3+ 触点验证过滤低质量趋势线
- scale-safe 延伸避免趋势线在不同缩放比例下失真

---

## 17. Volatility Terrain Engine [JOAT]

**URL**: https://www.tradingview.com/script/BXtZu6Yf-Volatility-Terrain-Engine-JOAT/

**核心逻辑**: 用快/慢 ATR 比率构建波动率状态振荡器，结合 ATR 百分位排名将每根 bar 分类为 Expansion/Compression/Transition 三种状态。检测 squeeze（双条件：快 ATR < 82% 慢 ATR 且低于自身均线）和 expansion burst（比率 > 1.25 且连续上升）。

**技术指标**: 双 ATR 比率振荡器, ATR 百分位排名, Squeeze 检测, Expansion Burst 检测, 三重平滑信号线

**策略类型**: 波动率分析 / 状态分类

**适用市场/时间框架**: 所有市场，作为策略选择的前置过滤器

**创新点**:
- 快/慢 ATR 比率比单一 ATR 更有上下文意义，同一 ATR 值在不同历史背景下含义不同
- Squeeze 使用双条件过滤单 bar 噪声，避免误报
- 四态直方图着色（扩张正/衰减正/扩张负/衰减负）比简单正负分类更细粒度
- 核心理念: 先判断波动率环境，再选择对应策略（趋势 vs 回归）

---

## 18. Convergence Protocol [JOAT]

**URL**: https://www.tradingview.com/script/JH9IMLVt-Convergence-Protocol-JOAT/

**核心逻辑**: 四模块（结构趋势/波动率状态/Delta 压力/流动性结构突破）收敛策略，通过 5 种独立入场机制（共融评分/基线回调/Squeeze 突破/Delta 交叉/Sweep 反转）覆盖市场周期不同阶段。0-7 共融评分系统将每个模块的贡献二值化后汇总。

**技术指标**: SMEMA 双平滑均线, ATR 波动率状态, Delta Pressure EMA, BOS/CHoCH 结构, Squeeze 检测, 0-7 共融评分

**策略类型**: 多路径策略系统

**适用市场/时间框架**: 趋势市场为主，加密货币/股票

**创新点**:
- 5 种入场机制覆盖完整市场周期: 高置信入场/趋势回调/波动率扩张/动量启动/Sweep 反转
- 0-7 共融评分将 4 个不相关维度量化为单一信念指标
- 双 TP + 拖尾止损: TP1 锁定 50% 仓位(1.2R)，剩余仓位用 ATR 拖尾追踪
- Regime Exit: 当波动率状态翻转时直接平仓，避免持有逆态仓位

---

## 19. Adaptive Keltner Channel [NovaLens]

**URL**: https://www.tradingview.com/script/JvLi7BPI-Adaptive-Keltner-Channel-NovaLens/

**核心逻辑**: 在经典 Keltner Channel 基础上，让通道乘数随 ATR 百分位排名自适应调整: 低波动时通道加宽（过滤噪音），高波动时通道收窄（保留突破信号意义）。状态感知的 center reclaim 信号追踪最近触及的 band，只有从对应 band 回归中心才算有效信号。

**技术指标**: EMA 中心线, ATR 通道带, ATR 百分位自适应, Bollinger-inside-Keltner Squeeze, 状态感知中心回归信号

**策略类型**: 波动率通道 / 突破 / 均值回归

**适用市场/时间框架**: 所有市场，提供 Reactive/Balanced/Smooth 三种预设

**创新点**:
- 自适应方向与 Bollinger Bands 相反: 高波动时收紧而非放宽，使突破信号在各状态下保持有效性
- 状态感知 center reclaim: 记录最近触及的 band，只有从该 band 回归中心才触发信号
- 三种预设 (Reactive/Balanced/Smooth) 覆盖从短线到波段的不同需求
- 内置 Squeeze 检测 + 释放标记，提供完整的波动率压缩-扩张框架

---

## 20. Liquidity Sweep Detector [QuantAlgo]

**URL**: https://www.tradingview.com/script/t7zABHiE-Liquidity-Sweep-Detector-QuantAlgo/

**核心逻辑**: 检测价格突破 swing 高低点后回归的流动性扫荡事件。Bearish Sweep = 价格突破高点后回落（扫 buy stops 后下跌），Bullish Sweep = 价格突破低点后回升（扫 sell stops 后上涨）。标记买卖方流动性目标区域和关键时间窗口。

**技术指标**: Swing High/Low, 流动性区域检测, Sweep 标记, 时间窗口高亮

**策略类型**: 流动性分析 / 反转

**适用市场/时间框架**: 外汇/黄金/加密货币，所有时间框架

**创新点**:
- 核心洞察: 机构通过扫止损获取流动性后再推动真实方向
- 双向流动性区域映射: 红色=卖方目标（下方），绿色=买方目标（上方）
- 时间高亮辅助识别高概率流动性事件时段

---

## 21. Iteratively Reweighted Least Squares Range Filter [Jamallo]

**URL**: https://www.tradingview.com/script/4dEDbPX3-Iteratively-Reweighted-Least-Squares-Range-Filter-Jamallo/

**核心逻辑**: 使用 IRLS 鲁棒统计引擎评估回看窗口中每根 bar 的可信度: 高信任 bar（在 sigma 内）全额权重，低信任 bar 半权重，异常值零权重。加权平均产生共识价格，再通过 Deadband Quantizer 产生阶梯式趋势线。引用 Li & Deng (2026) arXiv:2603.08158 论文。

**技术指标**: IRLS 共识引擎, 自适应 sigma 权重, Schmitt-trigger 迟滞, Deadband 量化器, Sample-and-Hold 波动率带

**策略类型**: 趋势跟踪 / 噪声过滤

**适用市场/时间框架**: 所有市场

**创新点**:
- 三阶段处理: IRLS 共识 -> Deadband 量化 -> Sample-and-Hold 带
- Schmitt-trigger 迟滞机制防止 bar 在信任状态间闪烁
- 波动率带只在滤波器步进时更新（Sample-and-Hold），反映"上次决定性移动"的条件而非实时噪声
- 阶梯式输出: 盘整时保持平坦，趋势时果断切换，不存在均线的"拖尾"

---

## 22. VWaves Squeeze Phase-Momentum Lifecycle Detector

**URL**: https://www.tradingview.com/script/blYXqwL1-VWaves-Squeeze-Phase-Momentum-Lifecycle-Detector/

**核心逻辑**: 结合成交量波浪分析和 squeeze 检测，追踪动量的完整生命周期: 从压缩蓄势（Squeeze）到方向性突破（Expansion）再到衰竭（Exhaustion）。通过成交量加权的波浪相位标记每个阶段。

**技术指标**: 成交量波浪, Squeeze 检测, 动量相位分析, 生命周期标记

**策略类型**: 波动率 / 动量

**适用市场/时间框架**: 所有市场

**创新点**:
- 将波动率周期（压缩->扩张->衰竭）视为可追踪的生命周期
- 成交量加权区分真实突破和虚假突破
- 完整的状态机框架，每个状态对应不同的交易策略

---

## 23. Enhanced Buy/Sell Profile Logic

**URL**: https://www.tradingview.com/script/3N3T5EpE-Enhanced-Buy-Sell-Profile-Logic/

**核心逻辑**: 将买卖压力估算与滚动成交量分布图结合。基于 K 线实体/影线的买卖量估算叠加 Rolling Volume Profile，计算 POC（最大成交量价位）、VAH/VAL（70% 价值区域高低）、VWMP（成交量加权中位价），并检测 imbalance/cluster 区域。Transition K 线标记压力方向变化: 买压主导 -> 卖压主导（或反向）时在方向确认前提前预警。

**技术指标**: 买卖压力估算, Rolling Volume Profile, POC/VAH/VAL/VWMP, Imbalance/Cluster 区域检测, Transition K 线

**策略类型**: 成交量分析 / 买卖压力 / 日内

**适用市场/时间框架**: 日内交易为主，所有市场

**创新点**:
- Transition K 线概念: 在压力方向完全确认之前就发出预警信号
- 将买卖压力与成交量分布融合，而非分开使用
- Imbalance/Cluster 区域标记识别流动性真空地带
- Rolling Volume Profile 避免固定时间窗口的局限

---

## 24. Candle Volume Architecture [JOAT]

**URL**: https://www.tradingview.com/script/2JQi0AHv-Candle-Volume-Architecture-JOAT/

**核心逻辑**: 为每个自动检测的摆动（swing）构建独立的成交量分布图。在每个 swing 区间内统计成交量分布，用 opacity 缩放的 bin 柱状图可视化，标记 POC（双宽度线）和 Value Area（70% 区域方框）。Dashboard 显示当前价格与最近 POC 的距离。

**技术指标**: Swing 检测, 成交量分布 (Volume Profile), POC, Value Area (70%), Opacity 缩放 bin 可视化, POC 接近度检测

**策略类型**: 成交量结构分析 / 叠加层指标

**适用市场/时间框架**: 所有市场，所有时间框架

**创新点**:
- 基于自动检测的 swing 区间动态构建 volume profile，而非固定时间窗口
- Opacity 缩放使高成交量区域视觉突出，低成交量区域透明
- POC 双宽度线 + Value Area 方框的视觉层次清晰
- Dashboard 实时显示价格与最近 POC 的距离，辅助入场/出场决策

---

## 25. Kelly Criterion Curve

**URL**: https://www.tradingview.com/script/Bq3m4ZgD-Kelly-Criterion-Curve/

**核心逻辑**: 绘制 Kelly 增长函数 g(f) = mu*f - 0.5*sigma^2*f^2，将杠杆/仓位大小分为五个区域: Underinvesting（低杠杆浪费机会）、Optimal（Full Kelly 附近）、High Risk（超出最优但仍有正期望）、Never Logical（负增长）、Suicidal（加速亏损）。标记 Full Kelly 和 Half Kelly 位置。

**技术指标**: Kelly Criterion 增长函数, 均值/方差估计, 杠杆分区标记, Full Kelly / Half Kelly 标记

**策略类型**: 仓位管理 / 资金管理

**适用市场/时间框架**: 所有市场，用于策略参数优化和风险管理

**创新点**:
- 将抽象的 Kelly 公式可视化: 直观展示不同杠杆下的复合增长率
- 五区域分类比简单的"最优杠杆"更具操作指导意义
- Half Kelly 标记符合实际交易中的保守实践（Half Kelly 是业界推荐的保守使用方式）
- 示例: BTC 的 mu/sigma 比显示即使 2x 杠杆也可能处于 High Risk 区域

---

## 26. Delta Pressure Gauge [JOAT]

**URL**: https://www.tradingview.com/script/Ozmyallz-Delta-Pressure-Gauge-JOAT/

**核心逻辑**: 基于 body-quality 加权的 delta 振荡器。每根 K 线的成交量按方向（涨/跌）乘以实体质量比（实体/总振幅）加权: 全实体 K 线贡献 100% 成交量，十字星贡献 0%。通过 rolling maximum normalization 归一化到 [-1, +1] 范围，使指标跨品种跨周期可比。

**技术指标**: Body-quality 加权 Delta, EMA 波浪线, 信号线, 30-bar 滚动累积 Delta, 资金流压力线, 背离检测, Histogram

**策略类型**: 成交量压力 / 振荡器

**适用市场/时间框架**: 所有市场，所有时间框架

**创新点**:
- Body-quality 过滤: 十字星等犹豫 K 线的成交量权重为零，减少噪音
- Rolling maximum normalization: 无需预热期，从第一根 bar 起就可用，且始终在 [-1, +1] 范围内
- 三个独立视角: 波浪振荡器 + 累积 delta cloud + 资金流线，三个维度验证同一成交量压力问题
- Histogram 四态着色: 不仅显示方向，还显示变化速率

---

## 27. Session Strata Mapper [JOAT]

**URL**: https://www.tradingview.com/script/BMKydzAM-Session-Strata-Mapper-JOAT/

**核心逻辑**: 追踪三个关键日内价格水平的叠加指标: Premarket 区间 (04:00-09:30 ET)、Initial Balance 区间 (09:30-10:30 ET) 和前日高低点/中点。IB 区间可以投射最多 4 级扩展目标 (IB+1x, IB+2x 等)。每个 session 的区间实时扩展，结束后固定。

**技术指标**: Session 检测, Premarket Range, Initial Balance, IB Extension, 前日高低中点, 实时 Dashboard

**策略类型**: 日内结构 / 突破

**适用市场/时间框架**: 日内交易，美股为主

**创新点**:
- 三种 session 类型整合在单一可视化系统中（Premarket + IB + 前日）
- IB 扩展投射基于机构交易者实际使用的倍数
- Session confluence: 当 Premarket/IB 与前日高低点对齐时，形成更强势的反应区域
- 实时扩展 zone box: 区间随 session 进行动态扩大

---

## 28. Path-Based Session Volume Profile [CLEVER]

**URL**: https://www.tradingview.com/script/Hb3CrKMt-Path-Based-Session-Volume-Profile-CLEVER/

**核心逻辑**: 会话级成交量分布工具，创新之处在于 path-aware 分配逻辑: 不将整根 K 线的成交量分配到单一价格（如收盘价），而是根据 OHLC 路径将成交量按比例分配到 K 线 range 覆盖的所有价格行。支持 Split Volume 和 Delta Heatmap 两种可视化模式。

**技术指标**: Session 隔离 Volume Profile, OHLC path-aware 分配, POC, Value Area (VAH/VAL), HVN/LVN, Split Volume / Delta Heatmap 可视化

**策略类型**: 成交量分布 / 结构分析

**适用市场/时间框架**: 日内交易，期货/外汇

**创新点**:
- Path-aware 分配: 根据 K 线 OHLC range 与价格行的重叠比例分配成交量，减少单点分配偏差
- 增量累积模型: 每根 bar 只添加新数据，不重算历史，保证实时与历史行为一致
- Session 严格隔离: 不同 session 的成交量不混合，每个 profile 独立
- 双可视化模式: Split Volume 观察买卖分离，Delta Heatmap 观察不平衡强度

---

## 29. Adaptive Spectral Bands [JOAT]

**URL**: https://www.tradingview.com/script/2RPafiIe-Adaptive-Spectral-Bands-JOAT/

**核心逻辑**: 六层 Hann Window FIR 滤波器丝带 + 波动率自适应 ATR 包络 + 三态 regime 分类器 + 自动支撑/阻力区域发现。Hann Window 是数字信号处理中的升余弦加权函数，产生近零过冲和陡峭频率滚降的滤波器，在等效频率截止下相位延迟严格低于 EMA/DEMA。

**技术指标**: 6 层 Hann Window FIR 滤波器, ATR 百分位自适应包络, ADX 三态 regime 分类, 自动 S/R 区域发现, Dashboard

**策略类型**: 趋势跟踪 / 波动率分析

**适用市场/时间框架**: 所有市场，建议 5 分钟以上

**创新点**:
- Hann FIR 滤波器在数学上严格优于 EMA: 同等频率截止下相位延迟更低
- 丝带宽度编码趋势动量: 宽分离=强趋势，压缩=盘整
- ATR 乘数随波动率百分位自适应: 低波动收紧（减少假突破），高波动加宽（容纳突破 K 线）
- S/R 区域从 ribbon crossover 自动发现: 基于频域拐点而非任意 pivot

### 策略 30: Volume Order Blocks [1M LTF]
- **核心逻辑**: 检测多空 Order Block 后，利用固定 1 分钟低阶时间框架数据在每个 Block 内部构建 Volume Profile，精确定位 Block 内最高成交量集中区域作为真正的反应区
- **技术指标**: Order Block 检测、1M LTF Volume Profile、Pivot 结构、内部价格分层
- **策略类型**: SMC / 订单流工具
- **适用市场/时间框架**: 通用，日内交易为主
- **创新点**: 区别于传统 OB 工具仅标记矩形区域，此脚本将 Block 拆分为多个价格层级并建立内部成交量分布，帮助交易者找到 Block 内的"真实反应区"而非整个区间

### 策略 31: TraxisLab Confluence Engine
- **核心逻辑**: 将 7 个独立维度的市场信号（BOS/CHoCH、CVD 压力、Delta 背离、VSA 吸收/高潮、流动性扫荡、溢价/折价区、FVG）融合为一个 0-100 的动态多空 Confluence Score
- **技术指标**: 内部 CVD 模型、Delta Divergence、VSA Effort vs Result、流动性扫荡、Premium/Discount Zone、FVG 评分系统
- **策略类型**: 多维度融合 / SMC + 订单流
- **适用市场/时间框架**: 日内及波段
- **创新点**: FVG 带评分（gap 大小+成交量+位置+结构距离）；VSA 吸收/高潮检测；Confluence Score 多组件加权，tooltip 解释触发原因

### 策略 32: AG Pro Repricing Belt Engine
- **核心逻辑**: 识别重新定价带——市场消化强势位移脉冲的紧凑价格带——追踪价格回访时的交互结果，通过两阶段生命周期（Active->Held/Shallow/Failed/Expired）评估消化区质量
- **技术指标**: ATR 归一化脉冲检测、Qualifying Touch 模型、状态转换机
- **策略类型**: 区域反应质量评估 / 供需区工具
- **适用市场/时间框架**: 15m-1D
- **创新点**: (1) 冲量触发而非摆动点触发；(2) Qualifying Touch 过滤轻触；(3) 两阶段生命周期——Held 可被升级为 Shallow/Failed；(4) 三种带宽模式

### 策略 33: Risk Management Engine (Anonycryptous)
- **核心逻辑**: 完全不看价格的纯风险管理仪表盘——三层风险等级（Full/Half/Quarter）动态调整仓位，基于 Pivot 结构自动止损，会话锁定机制+跨日赤字结转系统
- **技术指标**: Pivot 结构止损、R:R 可视化、仓位公式: Contracts = floor(Risk / (Stop Ticks x Tick Value))
- **策略类型**: 风险管理 / 账户保护工具
- **适用市场/时间框架**: 期货日内（MNQ/ES），通用
- **创新点**: 三层手动风险等级培养纪律；Carryover 跨日赤字结转；会话锁定阻止过度交易；强制手动记录培养问责习惯

---

## 关键收获总结

### 高频出现的技术方向
1. **自适应/动态参数**: 不再使用固定回看期，而是根据市场状态动态调整 (策略 5, 6, 9, 19, 20)
2. **多维度/多信号融合**: 单一指标不够，需要组合不相关的维度 (策略 1, 3, 8, 18)
3. **机器学习/统计方法**: KNN分类、频谱分析、小波变换、IRLS鲁棒统计等 (策略 4, 6, 9, 21)
4. **市场结构感知**: 将 CHoCH/BOS、Pivot 等结构事件纳入指标逻辑 (策略 5, 8, 14, 16, 18)
5. **VWAP 深度应用**: 不仅是基准线，还做统计带、交叉事件追踪 (策略 3)
6. **波动率状态分类**: 不再只看 ATR 数值，而是分类为 Expansion/Compression/Transition (策略 17, 18, 19)
7. **流动性分析**: 从价格结构推断机构行为，识别 stop hunt 模式 (策略 13, 20)
8. **成交量分布 (Volume Profile) 深度应用**: POC/Value Area/买卖压力多层分析 (策略 23, 24)
9. **数学资金管理模型**: Kelly Criterion 等量化框架用于仓位管理 (策略 25)
10. **角度/几何转换**: 将传统指标斜率转为角度或余弦空间，提供更直观的信号 (策略 35, 42)
11. **成交量加权动量**: 在经典公式（如 RSI）之前先用成交量缩放价格行为 (策略 36)
12. **多时间框架仓位管理**: 同时在多个 TF 计算波动率和仓位 (策略 37)
13. **0DTE 专用架构**: 针对 0DTE 期权的特化系统设计 (策略 38)
14. **学术模型工程化**: HAR-RV 等学术波动率模型在实盘工具中的落地 (策略 39)
15. **ICT 概念融合**: 将现代 ICT（Smart Money Concepts）与传统技术分析结合 (策略 40)
16. **价格速度/真空探测**: 不看成交量而看价格通过速度来识别关键区域 (策略 41)
17. **非对称入场/出场逻辑**: 入场需要多维度确认，出场追求速度 (策略 42)
18. **清洁图表仪表盘**: 将多维信息整合为表格，保持图表干净 (策略 43)

### 值得借鉴的思路
- **密度匹配评分** (策略1): 不预测方向，而是告诉"当前环境和历史转折点有多相似"
- **制度切换** (策略5): 同一个指标在不同市场状态下用不同参数
- **频率域分析** (策略6, 9): 傅里叶/小波变换检测主导周期，从"价格随时间变化"转为"信号在频率域的分布"
- **KNN 反转概率** (策略4): 纯 Pine Script 实现的轻量 ML，用多维 CCI 向量做模式匹配
- **7点结构张力** (策略8): 将摆动点的空间关系量化为单一振荡器读数
- **多路径入场架构** (策略18): 5种独立入场机制覆盖市场周期不同阶段
- **波动率前置过滤** (策略17): 先判断"市场有没有能量移动"，再决定用什么策略
- **IRLS 鲁棒共识** (策略21): 不是平等对待每根 bar，而是根据偏离度动态分配信任权重
- **状态感知信号** (策略19): 记录最近触及的 band，使中心回归信号具有上下文
- **统计套利时间窗口** (策略12): 13年数据验证特定时段的高回归概率
- **Transition K 线预警** (策略23): 在买卖压力方向确认前提前标记方向变化
- **Swing 区间 Volume Profile** (策略24): 基于价格结构而非固定时间窗口构建成交量分布
- **Kelly 五区域杠杆地图** (策略25): 将最优杠杆理论转化为可操作的分区图
- **Block 内部 Volume Profile** (策略30): 在 OB 内部建立微观成交量分布，精确定位反应区
- **7 维 Confluence Score** (策略31): 将结构/压力/背离/VSA/扫荡/FVG/溢价折价统一为单一评分
- **冲量触发+两阶段生命周期** (策略32): 消化区不是静态矩形，而是有生命周期的状态机
- **行为纪律工程** (策略33): 不分析价格，只分析交易者自身行为，用机制设计培养纪律
- **EMA 角度自动阈值** (策略35): 将指标斜率转为角度，用正态分布四分位数自动设定分类阈值
- **成交量加权 RSI** (策略36): 在 RSI 公式之前用成交量缩放价格行为，大幅提高灵敏度
- **三层 TF 波动率天气** (策略37): 不给单一 ATR 数值，而是给出 LOW/NORMAL/HIGH 的波动率天气预报+VIX 恐惧过滤
- **0DTE 分层确认评分** (策略38): 5 指标层层叠加而非并行投票，每层必须通过才计入总分
- **HAR-RV 波动率预测** (策略39): 学术异质自回归模型将日/周/月已实现波动率组合为前瞻预测
- **ORB + ICT 融合评分** (策略40): 经典开盘区间突破与 ICT 智能货币概念的量化融合
- **价格真空走廊** (策略41): 用价格通过速度（而非成交量）识别低阻力水平走廊
- **门控买入/非门控卖出** (策略42): 入场需多维度确认，出场追求速度的不对称架构
- **清洁图表仪表盘** (策略43): 零图表杂乱的多维信息整合——全部通过表格呈现

### 策略 34: Institutional Sniper Signal (Lite v3.5)
- **核心逻辑**: 4 层过滤引擎——(1)15 年历史季节性数据库过滤、(2)H4 13 个机构指标委员会投票（需 10/13 共识）、(3)H1 EMA20 回调区定位、(4)Fractal 突破触发——输出精确的 Buy/Sell Stop 挂单位置和 ATR 动态止损
- **技术指标**: 季节性数据库（Forex/NASDAQ）、13 个 H4 指标委员会（EMA200/50、WMA100、SAR、Bollinger、Ichimoku、DEMA、TEMA 等）、H1 EMA20、Fractal 突破、ATR 止损
- **策略类型**: 多时间框架突破交易系统
- **适用市场/时间框架**: Forex/NASDAQ，M30 执行+H4 过滤+H1 回调
- **创新点**: (1) 季节性严格模式——脚本内置 15 年外汇/指数月度统计，可阻止逆季节性交易；(2) 委员会投票机制——13 个不相关指标需达到超级多数（10/13）才释放信号；(3) 输出挂单而非市价单——给出精确的 Buy/Sell Stop 位和 ATR 动态止损位；(4) Anti-Overtrading——每日信号上限保护资本

### 策略 35: EMA Slope Angle Autothreshold V3
- **核心逻辑**: 计算 EMA 的变化率并转换为角度（度），通过 atan() 将斜率映射为度数，然后利用正态分布四分位数自动设定阈值，将趋势分为 FLAT/RISING/FALLING 三种状态
- **技术指标**: EMA（可调周期）、atan() 角度转换、正态分布四分位自动阈值
- **策略类型**: 趋势状态分类 / 自适应指标
- **适用市场/时间框架**: 通用，所有时间框架（Pine v6，无 MTF 调用）
- **创新点**: (1) 将 EMA 斜率从数值转为角度，更直观；(2) 自动阈值基于正态分布四分位数而非固定值，适应不同波动环境；(3) FLAT/RISING/FALLING 三态分类可嵌套到任何策略的趋势过滤器中

### 策略 36: Inflow/Outflow Index (IOI) — Volume-Weighted RSI
- **核心逻辑**: 将价格行为乘以实际成交量后应用 RSI 风格公式，创建高灵敏度动量振荡器。买入/卖出压力分别用成交量加权，EMA 平滑后组合为 0-100 范围的指标
- **技术指标**: 成交量加权买入/卖出计算、EMA 平滑、RSI 风格公式（0-100）
- **策略类型**: 动量振荡器 / 资金流指标
- **适用市场/时间框架**: 通用，适合所有流动性品种
- **创新点**: (1) 传统 RSI 只用价格变化，IOI 在 RSI 公式之前先用成交量缩放价格行为；(2) 极端区域 >80/<20 具有高敏感性，能更快检测到资金流入/流出转折；(3) 成交量作为权重而非简单叠加，信息密度更高

### 策略 37: Universal ATR Position Sizer + Volatility Context
- **核心逻辑**: 三层时间框架（当前 TF、自定义高时间框架、日线）同步计算 ATR 仓位大小，自动检测品种的点值（期货/外汇/股票/加密），提供波动率天气报告（LOW/NORMAL/HIGH）和 VIX 恐惧指数过滤
- **技术指标**: Triple-TF ATR、自动点值检测、波动率状态分类（LOW/NORMAL/HIGH）、VIX Fear Index（CALM<15/ALERT 15-25/FEAR>25）
- **策略类型**: 仓位管理 / 波动率上下文工具
- **适用市场/时间框架**: 全品种通用（期货/外汇/股票/加密），所有时间框架
- **创新点**: (1) 三层 TF 同步计算，解决单一 TF 波动率盲区；(2) 自动检测品种类型和点值，无需手动配置；(3) VIX 恐惧指数分级过滤为仓位决策提供情绪环境参考；(4) "波动率天气报告"概念——不是给出一个数字，而是给出 LOW/NORMAL/HIGH 的直觉化判断

### 策略 38: SPX 0DTE Scalper v3
- **核心逻辑**: 5 个独立指标层叠确认（EMA Ribbon + VWAP + RSI/MACD + Squeeze + Volume），4 个时间框架对齐（Daily/6H/90M/15M），输出 1-5 分的 Confluence Score，仅在 0DTE 交易日和特定交易时段内激活信号
- **技术指标**: EMA Ribbon、VWAP、RSI、MACD、TTM Squeeze、成交量确认、4-TF 对齐
- **策略类型**: 0DTE 日内剥头皮 / 多时间框架共振系统
- **适用市场/时间框架**: SPX/SPY 0DTE 期权，15M 执行 + 90M/6H/Daily 过滤
- **创新点**: (1) 5 指标分层层叠而非并行投票——每层必须通过才计入总分；(2) 4-TF 对齐确保从宏观到微观方向一致；(3) 智能 0DTE 日历过滤——只在期权到期日激活；(4) 交易时段过滤避免开盘/收盘噪音

### 策略 39: HValpha Sentinel v6 — HAR-RV Volatility Engine
- **核心逻辑**: 使用异质自回归已实现波动率（HAR-RV）模型，将短期/中期/长期已实现波动率组合为单一前瞻预测，结合动量+制度+风险三维对齐的 P1 信号，采用分数 Kelly 仓位管理器，附带 VaR/CVaR 实时监控
- **技术指标**: HAR-RV 模型（日/周/月 RV 加权）、动量指标、制度分类、分数 Kelly Criterion、VaR（Value at Risk）、CVaR（Expected Shortfall）
- **策略类型**: 波动率预测 + 风险管理引擎
- **适用市场/时间框架**: ETH/BTC/SOL，1H 为主
- **创新点**: (1) HAR-RV 是学术界的波动率预测模型，将三个时间尺度的已实现波动率组合预测——比单一 ATR 更有理论支撑；(2) 分数 Kelly（不用全 Kelly）在激进和保守之间取平衡；(3) P1 信号要求动量+制度+风险三维全部对齐，减少假信号；(4) VaR/CVaR 监控提供尾部风险可视性

### 策略 40: ORB + FVG — FIB Dashboard (ICT Confluence)
- **核心逻辑**: 15 分钟开盘区间突破（ORB）+ ICT 公允价值缺口（FVG）+ 订单块（OB），9 因子 Confluence Score 评估信号质量，要求 Fibonacci 回调确认入场，附带实时胜率追踪仪表盘
- **技术指标**: 15-min ORB、ICT FVG、Order Blocks、Fibonacci 回调、9 因子 Confluence Score
- **策略类型**: 日内突破 + ICT 智能货币概念
- **适用市场/时间框架**: QQQ/SPY/NQ，15M 执行
- **创新点**: (1) 9 因子评分系统将 ORB/FVG/OB/Fib 四种独立方法量化为统一分数；(2) Fibonacci 回调作为入场过滤器——不是突破就进，而是等回调到 Fib 位；(3) 实时胜率追踪仪表盘，持续验证策略有效性；(4) ICT 概念与经典 ORB 的融合，桥接两种方法论

### 策略 41: AG Pro Price Vacuum Atlas
- **核心逻辑**: 通过"每切片时间"直方图（与 bar 范围/ATR 成反比加权）映射价格快速通过的水平走廊，追踪走廊生命周期（Fresh → Entered → Passed/Rejected），通常同时显示 1-4 个活跃走廊
- **技术指标**: 时间/切片直方图、ATR 归一化、百分位阈值（仅基于已访问切片）
- **策略类型**: 价格行为地图 / 区域识别工具
- **适用市场/时间框架**: 通用，日内为主
- **创新点**: (1) "价格真空"概念——价格快速通过的区域意味着低阻力，回访时可能再次快速通过；(2) 生命周期追踪（Fresh→Entered→Passed/Rejected）赋予走廊动态而非静态属性；(3) 百分位阈值仅基于已访问切片，避免未交易区域的统计污染；(4) 时间加权而非成交量加权——捕捉"速度"而非"量"

### 策略 42: Quantum Trend & Exhaustion SMC
- **核心逻辑**: "门控买入"——COS（Cosine Oscillator Signal）交叉信号必须经过 SuperTrend 同向确认才触发入场；"非门控卖出"——退出时不需要确认，实现快速顶部离场。结合 SMC 订单块标记关键结构
- **技术指标**: COS（余弦振荡器信号）、SuperTrend、SMC Order Blocks、动态 SuperTrend Cloud
- **策略类型**: 趋势跟踪 + SMC 融合系统
- **适用市场/时间框架**: 通用，15M-4H
- **创新点**: (1) "门控买入/非门控卖出"不对称逻辑——入场需要多维度确认，出场追求速度；(2) COS 信号是较少见的余弦函数振荡器，与传统 RSI/MACD 不相关；(3) SuperTrend Cloud 将静态线变为动态区域，提供更灵活的止损参考

### 策略 43: Vantage-X (2.1) — Clean Chart Dashboard
- **核心逻辑**: 将趋势（EMA 50/200 + EMA 20/50 + EMA 9/21 交叉）、动量（RSI + Stochastic RSI）、资金流（滚动订单流代理 + 前日资金流锁定）整合为非侵入式表格仪表盘，图表零杂乱
- **技术指标**: EMA 50/200、EMA 20/50、EMA 9/21 交叉、RSI、Stochastic RSI、FLOW（滚动订单流代理）、PD FLOW（前日资金流）
- **策略类型**: 多维度仪表盘 / 清洁图表架构
- **适用市场/时间框架**: 通用，所有时间框架
- **创新点**: (1) "清洁图表"哲学——所有信息通过表格呈现，图表上不画任何线条/标记；(2) FLOW 和 PD FLOW 是纯计算得出的订单流代理，不需要 tick 数据；(3) 三组 EMA 交叉覆盖长/中/短三个趋势周期；(4) PD FLOW（前日资金流）锁定后不变，提供锚定参考点
