# TV Learning Progress Tracker
> 自动维护 — 每次学习/回测后更新
> 最后更新: 2026-04-19

## 总览

| 指标 | 数值 |
|------|------|
| 总脚本数 | 998 |
| 已学习 | ~900 (90%, 25个学习文件) |
| 未学习 | ~98 (部分rate-limit失败) |
| 已转Python | 20 (8 Tier1 + 9 Tier2 + 3 Batch2/3高创新) |
| 已回测 | 31 |
| 有效策略 | 18 (top: NW +75%, VDP +41.1%, IRLS +29.1%, Epan +25.3%, PVS +22.7%, AR +20.5%, Traffic +18%, KijunRSI +13.3%, CP +13%, FibCloud +11.5%, Weinstein +11.9%, RC +10.9%, OBV +8.8%, CCI +7.7%, ARM +7.7%, VT +6.9%, Dema +5.1%, HAR-RV +5.3%) |

## Batch学习进度

### Page-based (早期, 94个)
| 文件 | 策略数 | 状态 |
|------|--------|------|
| page_1_7.md | 30 | ✅ |
| page_8_14.md | 8 | ✅ |
| page_15_21.md | 10 | ✅ |
| page_15_21_full.md | 12 | ✅ |
| page_22_28.md | 14 | ✅ |
| page_29_35.md | 8 | ✅ |
| page_36_42.md | 12 | ✅ |

### Agent爬取 (2026-04-19, 233个)
| 文件 | 策略数 | 状态 |
|------|--------|------|
| page_43_55.md | 67 | ✅ |
| page_56_70.md | 22 | ✅ |
| page_71_85.md | 19 | ✅ |
| page_101_120.md | 87 | ✅ |
| page_121_120.md | 38 | ✅ |

### Batch-based (2026-04-19, ~235个有实质内容)
| 文件 | 脚本数 | 已学习 | 状态 |
|------|--------|--------|------|
| learned_batch_1.md | 79 | 79/121 | ✅ |
| learned_batch_2.md | 4 | 4/121 | 🔴 极低 |
| learned_batch_3.md | 4 | 4/121 | 🔴 极低 |
| learned_batch_3_new.md | 4 | 4/98 | 🔴 极低 |
| learned_batch_4.md | 121 | 121/121 | ✅ |
| learned_batch_4_new.md | 5 | 5/101 | 🔴 极低 |
| learned_batch_5.md | 9 | 9/121 | 🔴 极低 |
| learned_batch_6.md | 9 | 9/124 | 🔴 极低 |

### 待学习 (约436个)
- batch_1.json剩余: ~42
- batch_2.json剩余: ~117
- batch_3.json剩余: ~117
- batch_3_new.json剩余: ~94
- batch_4.json剩余: ~0 (done in learned_batch_4.md)
- batch_4_new.json剩余: ~96
- batch_5.json剩余: ~112
- batch_6.json剩余: ~115

## 理论学习
| 文件 | 内容 | 状态 |
|------|------|------|
| price_action.md | Al Brooks PA理论 | ✅ |
| probability_theory.md | Fisher/Bayes/统计检验 | ✅ |

## 策略转换+回测进度

### Batch 8 (Tier 1, 8策略) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| NadarayaWatson | nadaraya_watson_strategy.py | +75.0% avg, 25/27 | ✅ 保留 |
| AlgionicsRibbon | algionics_ribbon_strategy.py | +20.5% avg(opt), 27/27 | ✅ 保留 |
| SmartLiquidity | smart_liquidity_trend_strategy.py | +1.5% avg | ⚠️ 微利 |
| FibSwingProb | fib_swing_probability_strategy.py | +1.5% avg | ⚠️ 微利 |
| FractalLiquidity | fractal_liquidity_strategy.py | +0.7% avg | ⚠️ 微利 |
| MetisLadder | metis_ladder_strategy.py | +0.2% avg | ⚠️ 微利 |
| UndercutRally | undercut_rally_strategy.py | +0.0% avg | ❌ 淘汰 |
| InstPressure | institutional_pressure_strategy.py | -0.4% avg | ❌ 淘汰 |

### Tier 2 (15策略) — 部分完成
1. CCI RSI Derged HA Signal MA — ⏳ 待实现
2. Daily Deviation Range + Gap Stats — ⏳ 待实现
3. Regression-Aligned Candlestick Architect — ✅ regression_candlestick_strategy.py (**+10.9% avg, 27/27**) ✅ 保留
4. Session-Indexed CVD Differential — ⏳ 待实现(A股无session分时)
5. Quad BB Multi-TF Fusion — ⏳ 待实现
6. Hurst/KFD/Entropy Regime — ✅ hurst_regime_strategy.py (+0.7% avg, 20/27)
7. Epanechnikov Kernel Confluence — ✅ epanechnikov_confluence_strategy.py (**+25.3% avg, 27/27**)
8. Proportional Volume Split — ✅ proportional_volume_split_strategy.py (**+22.7% avg, 27/27**) ✅ 保留
9. Supply/Demand ATR Zones — ✅ supply_demand_atr_zone_strategy.py (+0.0% avg, 2/27) ❌ 淘汰(信号太少)
10. Volume Delta Pressure — ✅ volume_delta_pressure_strategy.py (**+41.1% avg, 27/27**) ✅ 保留(强)
11. Volatility Terrain Engine — ✅ volatility_terrain_strategy.py (+6.9% avg, 26/27) ✅ 可用
12. Volume Strength Shift MMT — ⏳ 待实现
13. Adaptive Regime Momentum — ✅ 已存在 adaptive_regime_momentum_strategy.py
14. Traffic Light Strategy — ✅ traffic_light_strategy.py (**+18.0% avg, 27/27**)
15. Hanning Window FIR System — ✅ hanning_fir_strategy.py (+1.0% avg, 21/27) ⚠️ 微利-FIR日线太慢

### Batch 9 (Tier 2, 3策略) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| EpanechnikovConf | epanechnikov_confluence_strategy.py | +25.3% avg, 27/27 | ✅ 保留 |
| TrafficLight | traffic_light_strategy.py | +18.0% avg, 27/27 | ✅ 保留 |
| HurstRegime | hurst_regime_strategy.py | +0.7% avg, 20/27 | ⚠️ 微利 |

### 本次新增学习 (batch 2/3/5/6 extended, 120个策略)
| 文件 | 策略数 | Innovation≥3 | A股可用 | 亮点 |
|------|--------|-------------|---------|------|
| learned_batch_2_extended.md | 30 | 15 | 13 | 趋势/统计 |
| learned_batch_3_extended.md | 30 | 9 | 20 | HAR-RV(5/5), 111%陷阱(4/5) |
| learned_batch_5_extended.md | 30 | 31 | 6 | TRAMA非线性(5/5), 条件概率矩阵(4/5) |
| learned_batch_6_extended.md | 30 | 14 | 3 | Kalman滤波器库(5/5), VWAP反应引擎 |

### 本次新增学习 (batch 5/6 extended_2, ~60个策略)
| 文件 | 策略数 | Innovation≥3 | 亮点 |
|------|--------|-------------|------|
| learned_batch_5_extended_2.md | 30 | 14 | 9点评分引擎(5/5), Force Differential(5/5), Liquidation Heatmap(5/5) |
| learned_batch_6_extended_2.md | 30 | ~8 | 待深入分析 |

### Batch 10 (HAR-RV + Liquidity Trap) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| HARRVSentinel | har_rv_sentinel_strategy.py | +5.3% avg, 22/27 | ✅ 可用(波动率预测) |
| LiquidityTrap | liquidity_trap_strategy.py | -0.0% avg, 3/27 | ❌ 淘汰(A股信号太少) |

### Batch 11 (Supply/Demand ATR + Volume Delta Pressure) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| SupplyDemandATR | supply_demand_atr_zone_strategy.py | +0.0% avg, 2/27 | ❌ 淘汰(信号太少) |
| VolDeltaPressure | volume_delta_pressure_strategy.py | **+41.1% avg, 27/27** | ✅ 保留(强) |

### Batch 12 (PropVolSplit + VolTerrain) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| PropVolSplit | proportional_volume_split_strategy.py | **+22.7% avg, 27/27** | ✅ 保留 |
| VolTerrain | volatility_terrain_strategy.py | +6.9% avg, 26/27 | ✅ 可用(波动率过滤) |

### Batch 13 (RegCandle + HanningFIR) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| RegCandle | regression_candlestick_strategy.py | **+10.9% avg, 27/27** | ✅ 保留 |
| HanningFIR | hanning_fir_strategy.py | +1.0% avg, 21/27 | ⚠️ 微利(FIR日线太慢) |

### Batch 14 (IRLS) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| IRLS | irls_strategy.py | **+29.1% avg, 27/27** | ✅ 保留(强) |

### Batch 15 (Pre-existing: Weinstein/OBV/PocketPivot/VWAP) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| WeinsteinStage | weinstein_stage_strategy.py | +11.9% avg, 25/27 | ✅ 保留 |
| OBVDivergence | obv_divergence_strategy.py | +8.8% avg, 23/27 | ✅ 可用 |
| PocketPivot | pocket_pivot_strategy.py | +1.9% avg, 17/27 | ⚠️ 微利(交易过多) |
| VWAPDeviation | vwap_deviation_strategy.py | -0.6% avg, 1/27 | ❌ 淘汰(VWAP日线不适用) |

### Batch 16 (Pre-existing: ConvergenceProtocol) — ✅ 完成
| 策略 | 文件 | 回测结果 | 状态 |
|------|------|----------|------|
| ConvergenceProtocol | convergence_protocol_strategy.py | **+13.0% avg, 27/27** | ✅ 保留 |

### 扩展学习 (batch 1-6 extended) — 进行中
| 文件 | 策略数 | Innovation≥3 | 状态 |
|------|--------|-------------|------|
| learned_batch_1_extended.md | 30 | ~15 | ✅ |
| learned_batch_1_extended_2.md | 30 | ~10 | 🔄 agent运行中 |
| learned_batch_2_extended.md | 30 | 15 | ✅ |
| learned_batch_2_extended_2.md | 30 | ~12 | ✅ |
| learned_batch_3_extended.md | 30 | 9 | ✅ |
| learned_batch_3_extended_2.md | 30 | ~10 | 🔄 agent运行中 |
| learned_batch_3_new.md | 30 | ~10 | ✅ |
| learned_batch_3_new_extended.md | 30 | ~8 | 🔄 agent运行中 |
| learned_batch_4_new.md | 30 | ~12 | ✅ |
| learned_batch_5_extended.md | 30 | 31 | ✅ |
| learned_batch_5_extended_2.md | 30 | 14 | ✅ |
| learned_batch_5_extended_3.md | 30 | ~8 | ✅ |
| learned_batch_6_extended.md | 30 | 14 | ✅ |
| learned_batch_6_extended_2.md | 30 | ~8 | ✅ |
| learned_batch_6_extended_3.md | 30 | ~8 | 🔄 agent运行中 |

## 跨Batch创新模式 (数学洞察)

### 1. ATR区域聚类 (batch 3,4,5,6反复出现)
- **数学**: ATR比率阈值量化支撑/阻力, 替代主观判断
- **哲学**: 波动率是市场情绪的度量, 区域是情绪凝聚的容器

### 2. 分形+流动性区域 (batch 3,5,6独立实现)
- **数学**: Williams分形在ATR容差内收敛 = 高质量区域
- **哲学**: 市场在时间分形上自相似, 流动性在分形节点聚集

### 3. 对数归一化体积压力 (batch_6 uusIBLke)
- **数学**: log(volume)归一化使体积压力与价格尺度无关
- **哲学**: 相对变化比绝对变化更能反映市场动力

### 4. Sigmoid概率门控 (batch 1,4反复出现)
- **数学**: σ(x) = 1/(1+e^{-x}) 将多因子质量压缩到[0,1]
- **哲学**: 决策边界应该是概率性的, 不是确定性的

### 5. Latch状态机 (batch 1,5)
- **数学**: 数学边界(0/50/100)锁存防止信号闪烁
- **哲学**: 状态转换需要能量阈值, 类似物理学中的相变

### 6. 百分位排名自适应阈值 (batch 3,4,6)
- **数学**: 滚动窗口内排名使指标自适应当前市场
- **哲学**: 没有绝对标准, 只有相对标准; 市场评价自身
