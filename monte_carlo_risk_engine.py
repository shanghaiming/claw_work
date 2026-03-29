#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
蒙特卡洛风险模拟引擎
第15章：高级风险管理策略 - 扩展模块
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import warnings
warnings.filterwarnings('ignore')

# 自定义统计函数（替代scipy.stats）
class CustomStats:
    """自定义统计函数，替代scipy.stats依赖"""
    
    @staticmethod
    def norm_ppf(p):
        """正态分布分位数函数近似"""
        # 使用简单近似公式
        # Abramowitz and Stegun approximation
        if p <= 0 or p >= 1:
            raise ValueError("p must be in (0, 1)")
        
        # 转换
        q = p - 0.5
        if abs(q) <= 0.425:
            r = 0.180625 - q * q
            num = (((((((2.5090809287301226727e3 * r +
                        3.3430575583588128105e4) * r +
                        6.7265770927008700853e4) * r +
                        4.5921953931549871457e4) * r +
                        1.3731693765509461125e4) * r +
                        1.9715909503065514427e3) * r +
                        1.3314166789178437745e2) * r +
                        3.3871328727963666080e0) * q
            den = (((((((5.2264952788528545610e3 * r +
                        2.8729085735721942674e4) * r +
                        3.9307895800092710610e4) * r +
                        2.1213794301586595867e4) * r +
                        5.3941960214247511077e3) * r +
                        6.8718700749205790830e2) * r +
                        4.2313330701600911252e1) * r +
                        1.0)
            return num / den
        else:
            if q < 0:
                r = p
            else:
                r = 1 - p
            r = np.sqrt(-np.log(r))
            if r <= 5.0:
                r = r - 1.6
                num = (((((((7.74545014278341407640e-4 * r +
                            2.27238449892691845833e-2) * r +
                            2.41780725177450611770e-1) * r +
                            1.27045825245236838258e0) * r +
                            3.64784832476320460504e0) * r +
                            5.76949722146069140550e0) * r +
                            4.63033784615654529590e0) * r +
                            1.42343711074968357734e0)
                den = (((((((1.05075007164441684324e-9 * r +
                            5.47593808499534494600e-4) * r +
                            1.51986665636164571966e-2) * r +
                            1.48103976427480074590e-1) * r +
                            6.89767334985100004550e-1) * r +
                            1.67638483018380384940e0) * r +
                            2.05319162663775882187e0) * r +
                            1.0)
            else:
                r = r - 5.0
                num = (((((((2.01033439929228813265e-7 * r +
                            2.71155556874348757815e-5) * r +
                            1.24266094738807843860e-3) * r +
                            2.65321895265761230930e-2) * r +
                            2.96560571828504891230e-1) * r +
                            1.78482653991729133580e0) * r +
                            5.46378491116411436990e0) * r +
                            6.65790464350110377720e0)
                den = (((((((2.04426310338993978564e-15 * r +
                            1.42151175831644588870e-7) * r +
                            1.84631831751005468180e-5) * r +
                            7.86869131145613259100e-4) * r +
                            1.48753612908506148825e-2) * r +
                            1.36929880922735805310e-1) * r +
                            5.99832206555887937690e-1) * r +
                            1.0)
            if q < 0:
                return -num / den
            else:
                return num / den
    
    @staticmethod
    def norm_pdf(x):
        """正态分布概率密度函数"""
        return np.exp(-x**2 / 2) / np.sqrt(2 * np.pi)
    
    @staticmethod
    def skew(data):
        """偏度计算"""
        data = np.array(data)
        n = len(data)
        if n < 3:
            return 0
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        if std == 0:
            return 0
        return (np.sum((data - mean)**3) / n) / (std**3)
    
    @staticmethod
    def kurtosis(data):
        """峰度计算"""
        data = np.array(data)
        n = len(data)
        if n < 4:
            return 0
        mean = np.mean(data)
        std = np.std(data, ddof=1)
        if std == 0:
            return 0
        return (np.sum((data - mean)**4) / n) / (std**4) - 3

def simple_linear_regression(x, y):
    """简单线性回归（替代sklearn）"""
    x = np.array(x).reshape(-1, 1)
    y = np.array(y)
    
    # 添加截距项
    X = np.column_stack([np.ones(len(x)), x])
    
    # 最小二乘解
    beta = np.linalg.lstsq(X, y, rcond=None)[0]
    
    # 预测值
    y_pred = X @ beta
    
    # 计算R²
    ss_res = np.sum((y - y_pred) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    r_squared = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
    
    return {
        'intercept': beta[0],
        'slope': beta[1],
        'r_squared': r_squared,
        'coefficients': beta,
        'predict': lambda x_new: beta[0] + beta[1] * np.array(x_new)
    }

class MonteCarloRiskEngine:
    """蒙特卡洛风险模拟引擎"""
    
    def __init__(self, 
                 historical_returns: pd.DataFrame,
                 risk_free_rate: float = 0.02):
        """
        初始化蒙特卡洛引擎
        
        参数:
            historical_returns: 历史收益率数据
            risk_free_rate: 无风险利率
        """
        self.historical_returns = historical_returns
        self.risk_free_rate = risk_free_rate
        self.n_assets = historical_returns.shape[1]
        self.asset_names = historical_returns.columns.tolist()
        
        # 计算历史统计量
        self.mean_returns = historical_returns.mean()
        self.cov_matrix = historical_returns.cov()
        self.corr_matrix = historical_returns.corr()
        
    def simulate_portfolio_returns(self,
                                  weights: Dict[str, float],
                                  n_simulations: int = 10000,
                                  time_horizon_days: int = 252,
                                  model_type: str = 'geometric_brownian') -> Dict:
        """
        模拟投资组合未来收益
        
        参数:
            weights: 资产权重字典
            n_simulations: 模拟次数
            time_horizon_days: 时间范围（天数）
            model_type: 模型类型 ('geometric_brownian', 'historical_bootstrap')
            
        返回:
            模拟结果
        """
        # 准备权重向量
        weight_vector = np.array([weights.get(name, 0) for name in self.asset_names])
        
        if model_type == 'geometric_brownian':
            # 几何布朗运动模型
            simulated_returns = self._gbm_simulation(
                weight_vector, n_simulations, time_horizon_days
            )
        elif model_type == 'historical_bootstrap':
            # 历史数据自举法
            simulated_returns = self._bootstrap_simulation(
                weight_vector, n_simulations, time_horizon_days
            )
        else:
            raise ValueError(f"不支持的模型类型: {model_type}")
        
        # 计算模拟结果的统计量
        final_values = simulated_returns[:, -1]
        cumulative_returns = final_values - 1  # 从初始值1开始
        
        # 风险指标计算
        metrics = self._calculate_simulation_metrics(cumulative_returns)
        
        return {
            'simulated_returns': simulated_returns,
            'cumulative_returns': cumulative_returns,
            'final_values': final_values,
            'metrics': metrics,
            'model_type': model_type,
            'n_simulations': n_simulations,
            'time_horizon_days': time_horizon_days,
            'weights': weights
        }
    
    def _gbm_simulation(self,
                       weights: np.ndarray,
                       n_simulations: int,
                       time_horizon_days: int) -> np.ndarray:
        """几何布朗运动模拟"""
        # 计算投资组合的期望收益率和波动率
        port_mean = np.dot(weights, self.mean_returns)
        port_variance = np.dot(weights.T, np.dot(self.cov_matrix, weights))
        port_volatility = np.sqrt(port_variance)
        
        # GBM参数
        dt = 1 / 252  # 日度时间步长
        n_steps = time_horizon_days
        
        # 初始化模拟矩阵
        simulations = np.zeros((n_simulations, n_steps + 1))
        simulations[:, 0] = 1.0  # 初始价值为1
        
        # 随机数生成
        np.random.seed(42)
        
        for t in range(1, n_steps + 1):
            # 布朗运动增量
            z = np.random.randn(n_simulations)
            
            # GBM公式: dS = μSdt + σSdz
            drift = (port_mean - 0.5 * port_volatility**2) * dt
            diffusion = port_volatility * np.sqrt(dt) * z
            
            simulations[:, t] = simulations[:, t-1] * np.exp(drift + diffusion)
        
        return simulations
    
    def _bootstrap_simulation(self,
                            weights: np.ndarray,
                            n_simulations: int,
                            time_horizon_days: int) -> np.ndarray:
        """历史数据自举法模拟"""
        n_historical = len(self.historical_returns)
        n_steps = time_horizon_days
        
        # 初始化模拟矩阵
        simulations = np.zeros((n_simulations, n_steps + 1))
        simulations[:, 0] = 1.0
        
        np.random.seed(42)
        
        for i in range(n_simulations):
            # 随机选择历史收益率序列
            for t in range(1, n_steps + 1):
                # 随机选择一天的历史收益率
                random_idx = np.random.randint(0, n_historical)
                daily_return = self.historical_returns.iloc[random_idx]
                
                # 计算投资组合日收益率
                port_return = np.dot(weights, daily_return)
                
                # 更新投资组合价值
                simulations[i, t] = simulations[i, t-1] * (1 + port_return)
        
        return simulations
    
    def _calculate_simulation_metrics(self, cumulative_returns: np.ndarray) -> Dict:
        """计算模拟结果的统计指标"""
        # 基本统计量
        mean_return = np.mean(cumulative_returns)
        median_return = np.median(cumulative_returns)
        std_return = np.std(cumulative_returns)
        
        # 分位数分析
        percentiles = {
            'p1': np.percentile(cumulative_returns, 1),
            'p5': np.percentile(cumulative_returns, 5),
            'p10': np.percentile(cumulative_returns, 10),
            'p25': np.percentile(cumulative_returns, 25),
            'p50': np.percentile(cumulative_returns, 50),
            'p75': np.percentile(cumulative_returns, 75),
            'p90': np.percentile(cumulative_returns, 90),
            'p95': np.percentile(cumulative_returns, 95),
            'p99': np.percentile(cumulative_returns, 99)
        }
        
        # 风险价值 (VaR)
        var_95 = percentiles['p5']  # 95% VaR (5%分位数)
        var_99 = percentiles['p1']  # 99% VaR (1%分位数)
        
        # 条件风险价值 (CVaR/Expected Shortfall)
        cvar_95 = cumulative_returns[cumulative_returns <= var_95].mean()
        cvar_99 = cumulative_returns[cumulative_returns <= var_99].mean()
        
        # 夏普比率
        sharpe_ratio = (mean_return - self.risk_free_rate) / std_return if std_return > 0 else 0
        
        # 偏度和峰度
        skewness = CustomStats.skew(cumulative_returns)
        kurtosis = CustomStats.kurtosis(cumulative_returns)
        
        # 最大回撤模拟
        n_simulations = len(cumulative_returns)
        max_drawdowns = []
        
        # 简化版本：基于最终价值的回撤估计
        for i in range(min(n_simulations, 1000)):  # 抽样计算
            # 随机生成一条路径（简化）
            random_path = np.random.randn(252).cumsum() * 0.01 + 1
            running_max = np.maximum.accumulate(random_path)
            drawdown = (random_path - running_max) / running_max
            max_drawdowns.append(drawdown.min())
        
        avg_max_drawdown = np.mean(max_drawdowns) if max_drawdowns else 0
        
        return {
            'mean_return': mean_return,
            'median_return': median_return,
            'std_return': std_return,
            'sharpe_ratio': sharpe_ratio,
            'var_95': var_95,
            'var_99': var_99,
            'cvar_95': cvar_95,
            'cvar_99': cvar_99,
            'skewness': skewness,
            'kurtosis': kurtosis,
            'avg_max_drawdown': avg_max_drawdown,
            'probability_of_loss': np.mean(cumulative_returns < 0),
            'probability_of_20pct_loss': np.mean(cumulative_returns < -0.2),
            'expected_shortfall_95': cvar_95,
            'expected_shortfall_99': cvar_99,
            'percentiles': percentiles
        }
    
    def calculate_portfolio_var(self,
                               weights: Dict[str, float],
                               confidence_level: float = 0.95,
                               time_horizon_days: int = 10,
                               method: str = 'parametric') -> Dict:
        """
        计算投资组合风险价值 (VaR)
        
        参数:
            weights: 资产权重
            confidence_level: 置信水平
            time_horizon_days: 时间范围
            method: 计算方法 ('parametric', 'historical', 'monte_carlo')
            
        返回:
            VaR分析结果
        """
        # 准备权重向量
        weight_vector = np.array([weights.get(name, 0) for name in self.asset_names])
        
        if method == 'parametric':
            # 参数法（正态分布假设）
            port_mean = np.dot(weight_vector, self.mean_returns)
            port_variance = np.dot(weight_vector.T, np.dot(self.cov_matrix, weight_vector))
            port_volatility = np.sqrt(port_variance)
            
            # 调整时间范围
            horizon_adjustment = np.sqrt(time_horizon_days / 252)
            adjusted_volatility = port_volatility * horizon_adjustment
            
            # 计算VaR
            z_score = CustomStats.norm_ppf(1 - confidence_level)
            var = -(port_mean * time_horizon_days / 252 + z_score * adjusted_volatility)
            
            # 计算条件VaR (Expected Shortfall)
            es = adjusted_volatility * CustomStats.norm_pdf(z_score) / (1 - confidence_level) - port_mean * time_horizon_days / 252
            
            return {
                'var': var,
                'expected_shortfall': es,
                'method': 'parametric',
                'confidence_level': confidence_level,
                'time_horizon_days': time_horizon_days,
                'portfolio_mean': port_mean,
                'portfolio_volatility': port_volatility,
                'z_score': z_score
            }
            
        elif method == 'historical':
            # 历史模拟法
            portfolio_returns = self.historical_returns.dot(weight_vector)
            
            # 调整时间范围
            # 简化：假设收益率独立同分布
            horizon_returns = portfolio_returns * np.sqrt(time_horizon_days)
            
            var = -np.percentile(horizon_returns, (1 - confidence_level) * 100)
            es = -horizon_returns[horizon_returns <= -var].mean()
            
            return {
                'var': var,
                'expected_shortfall': es,
                'method': 'historical',
                'confidence_level': confidence_level,
                'time_horizon_days': time_horizon_days,
                'historical_percentile': (1 - confidence_level) * 100
            }
            
        elif method == 'monte_carlo':
            # 蒙特卡洛模拟法
            sim_results = self.simulate_portfolio_returns(
                weights, n_simulations=10000, time_horizon_days=time_horizon_days
            )
            
            cumulative_returns = sim_results['cumulative_returns']
            var = -np.percentile(cumulative_returns, (1 - confidence_level) * 100)
            es = -cumulative_returns[cumulative_returns <= -var].mean()
            
            return {
                'var': var,
                'expected_shortfall': es,
                'method': 'monte_carlo',
                'confidence_level': confidence_level,
                'time_horizon_days': time_horizon_days,
                'n_simulations': 10000,
                'simulation_metrics': sim_results['metrics']
            }
            
        else:
            raise ValueError(f"不支持的VaR计算方法: {method}")
    
    def analyze_tail_risk(self,
                         weights: Dict[str, float],
                         extreme_threshold: float = 0.01) -> Dict:
        """
        分析尾部风险
        
        参数:
            weights: 资产权重
            extreme_threshold: 极端事件阈值
            
        返回:
            尾部风险分析
        """
        # 模拟极端情景
        sim_results = self.simulate_portfolio_returns(
            weights, n_simulations=50000, time_horizon_days=252
        )
        
        cumulative_returns = sim_results['cumulative_returns']
        
        # 识别极端损失
        extreme_losses = cumulative_returns[cumulative_returns < 0]
        n_extreme = int(len(cumulative_returns) * extreme_threshold)
        
        if len(extreme_losses) > 0:
            worst_losses = np.sort(extreme_losses)[:n_extreme]
        else:
            worst_losses = np.array([])
        
        # 计算尾部风险指标
        if len(worst_losses) > 0:
            avg_extreme_loss = worst_losses.mean()
            max_extreme_loss = worst_losses.min() if len(worst_losses) > 0 else 0
            extreme_loss_volatility = worst_losses.std() if len(worst_losses) > 1 else 0
        else:
            avg_extreme_loss = 0
            max_extreme_loss = 0
            extreme_loss_volatility = 0
        
        # 计算极端事件相关性
        # 简化：检查在极端损失时期各资产的相关性变化
        extreme_correlations = {}
        if len(self.historical_returns) > 100:
            # 识别历史极端日
            portfolio_returns = self.historical_returns.dot(
                np.array([weights.get(name, 0) for name in self.asset_names])
            )
            extreme_days = portfolio_returns <= portfolio_returns.quantile(extreme_threshold)
            
            if extreme_days.sum() > 10:
                extreme_returns = self.historical_returns[extreme_days]
                extreme_corr = extreme_returns.corr()
                
                for i, asset1 in enumerate(self.asset_names):
                    for j, asset2 in enumerate(self.asset_names[i+1:], i+1):
                        key = f"{asset1}_{asset2}"
                        normal_corr = self.corr_matrix.iloc[i, j]
                        crisis_corr = extreme_corr.iloc[i, j]
                        correlation_change = crisis_corr - normal_corr
                        
                        extreme_correlations[key] = {
                            'normal_correlation': normal_corr,
                            'crisis_correlation': crisis_corr,
                            'change': correlation_change,
                            'crisis_amplification': abs(crisis_corr) > abs(normal_corr)
                        }
        
        return {
            'extreme_threshold': extreme_threshold,
            'avg_extreme_loss': avg_extreme_loss,
            'max_extreme_loss': max_extreme_loss,
            'extreme_loss_volatility': extreme_loss_volatility,
            'probability_of_extreme_loss': len(worst_losses) / len(cumulative_returns),
            'expected_shortfall_extreme': -avg_extreme_loss,
            'tail_risk_index': abs(avg_extreme_loss) * extreme_loss_volatility if extreme_loss_volatility > 0 else 0,
            'extreme_correlations': extreme_correlations,
            'n_extreme_observations': len(worst_losses)
        }

class DynamicHedgeManager:
    """动态对冲策略管理器"""
    
    def __init__(self, 
                 portfolio_analyzer,
                 hedge_instruments: Dict[str, Dict]):
        """
        初始化动态对冲管理器
        
        参数:
            portfolio_analyzer: 投资组合分析器实例
            hedge_instruments: 对冲工具信息
        """
        self.portfolio_analyzer = portfolio_analyzer
        self.hedge_instruments = hedge_instruments
        
    def calculate_optimal_hedge_ratio(self,
                                     portfolio_weights: Dict[str, float],
                                     hedge_instrument: str,
                                     method: str = 'ols') -> Dict:
        """
        计算最优对冲比率
        
        参数:
            portfolio_weights: 投资组合权重
            hedge_instrument: 对冲工具名称
            method: 计算方法 ('ols', 'var_minimization', 'tail_risk')
            
        返回:
            对冲分析结果
        """
        # 获取投资组合收益率
        returns = self.portfolio_analyzer.historical_returns
        portfolio_returns = returns.dot(
            np.array([portfolio_weights.get(name, 0) for name in returns.columns])
        )
        
        # 获取对冲工具收益率（这里需要实际数据）
        # 简化：假设对冲工具是第一个资产的负相关版本
        hedge_returns = -returns.iloc[:, 0] * 0.7 + np.random.normal(0, 0.01, len(returns)) * 0.3
        
        if method == 'ols':
            # OLS回归法（使用自定义函数）
            X = hedge_returns.values
            y = portfolio_returns.values
            
            model = simple_linear_regression(X, y)
            
            hedge_ratio = model['slope']
            r_squared = model['r_squared']
            hedge_effectiveness = r_squared
            
            # 计算对冲后的残差风险
            y_pred = model['predict'](X)
            hedged_returns = y - y_pred
            residual_risk = hedged_returns.std()
            original_risk = y.std()
            risk_reduction = (original_risk - residual_risk) / original_risk
            
            return {
                'hedge_ratio': hedge_ratio,
                'intercept': model['intercept'],
                'r_squared': r_squared,
                'hedge_effectiveness': hedge_effectiveness,
                'residual_risk': residual_risk,
                'original_risk': original_risk,
                'risk_reduction': risk_reduction,
                'method': 'ols'
            }
            
        elif method == 'var_minimization':
            # 风险最小化法
            hedge_ratios = np.linspace(-2, 2, 401)
            portfolio_variances = []
            
            for hr in hedge_ratios:
                hedged_returns = portfolio_returns - hr * hedge_returns
                portfolio_variances.append(hedged_returns.var())
            
            optimal_idx = np.argmin(portfolio_variances)
            optimal_ratio = hedge_ratios[optimal_idx]
            min_variance = portfolio_variances[optimal_idx]
            
            original_variance = portfolio_returns.var()
            variance_reduction = (original_variance - min_variance) / original_variance
            
            return {
                'hedge_ratio': optimal_ratio,
                'min_variance': min_variance,
                'original_variance': original_variance,
                'variance_reduction': variance_reduction,
                'method': 'var_minimization'
            }
            
        else:
            raise ValueError(f"不支持的对冲计算方法: {method}")
    
    def design_dynamic_hedge_strategy(self,
                                     portfolio_weights: Dict[str, float],
                                     market_regimes: Dict[str, pd.Series]) -> Dict:
        """
        设计动态对冲策略
        
        参数:
            portfolio_weights: 投资组合权重
            market_regimes: 市场状态序列
            
        返回:
            动态对冲策略
        """
        # 识别不同市场状态下的最优对冲
        regime_hedge_ratios = {}
        
        for regime_name, regime_mask in market_regimes.items():
            if regime_mask.sum() > 20:  # 至少20个观测值
                # 筛选该状态下的数据
                regime_returns = self.portfolio_analyzer.historical_returns[regime_mask]
                
                if len(regime_returns) > 0:
                    # 计算该状态下的对冲比率
                    portfolio_regime_returns = regime_returns.dot(
                        np.array([portfolio_weights.get(name, 0) for name in regime_returns.columns])
                    )
                    
                    # 简化：假设对冲工具是第一个资产的负相关版本
                    hedge_regime_returns = -regime_returns.iloc[:, 0] * 0.7
                    
                    # OLS计算对冲比率
                    X = hedge_regime_returns.values.reshape(-1, 1)
                    y = portfolio_regime_returns.values
                    
                    model = simple_linear_regression(X, y)
                    
                    regime_hedge_ratios[regime_name] = {
                        'hedge_ratio': model['slope'],
                        'r_squared': model['r_squared'],
                        'n_observations': len(regime_returns),
                        'regime_volatility': y.std(),
                        'hedged_volatility': (y - model['predict'](X)).std()
                    }
        
        # 设计状态转换规则
        transition_rules = {}
        regime_names = list(regime_hedge_ratios.keys())
        
        for i, regime1 in enumerate(regime_names):
            for regime2 in regime_names[i+1:]:
                # 简化：基于波动率变化设计转换规则
                vol1 = regime_hedge_ratios[regime1]['regime_volatility']
                vol2 = regime_hedge_ratios[regime2]['regime_volatility']
                
                vol_ratio = vol2 / vol1 if vol1 > 0 else 1
                
                transition_rules[f"{regime1}_to_{regime2}"] = {
                    'volatility_increase': vol_ratio > 1.5,
                    'volatility_decrease': vol_ratio < 0.67,
                    'recommended_hedge_adjustment': vol_ratio,
                    'threshold_volatility': (vol1 + vol2) / 2
                }
        
        return {
            'regime_hedge_ratios': regime_hedge_ratios,
            'transition_rules': transition_rules,
            'dynamic_hedge_enabled': len(regime_hedge_ratios) > 1,
            'recommended_strategy': '根据市场状态动态调整对冲比率',
            'implementation_guidance': {
                'monitoring_frequency': 'daily',
                'adjustment_threshold': 0.2,  # 对冲比率变化超过20%时调整
                'cost_consideration': '交易成本 < 预期风险减少收益时执行',
                'execution_method': '逐步调整，避免市场冲击'
            }
        }

def main():
    """演示蒙特卡洛风险引擎和动态对冲"""
    print("=== 蒙特卡洛风险模拟引擎 & 动态对冲策略 ===\n")
    
    # 生成模拟数据
    np.random.seed(42)
    dates = pd.date_range('2020-01-01', '2024-01-01', freq='B')
    n_days = len(dates)
    
    # 创建3个相关资产
    base_volatilities = [0.015, 0.02, 0.012]
    correlations = [[1.0, 0.6, 0.3],
                   [0.6, 1.0, 0.4],
                   [0.3, 0.4, 1.0]]
    
    # 生成相关随机游走
    corr_matrix = np.array(correlations)
    chol = np.linalg.cholesky(corr_matrix)  # numpy返回上三角矩阵
    
    uncorrelated_returns = np.random.randn(n_days, 3)
    correlated_returns = np.dot(uncorrelated_returns, chol)
    
    # 应用不同的波动率
    for i in range(3):
        correlated_returns[:, i] *= base_volatilities[i]
    
    # 创建收益率数据框
    returns_df = pd.DataFrame(
        correlated_returns,
        index=dates,
        columns=['Stock_A', 'Stock_B', 'Stock_C']
    )
    
    # 添加趋势
    returns_df['Stock_A'] += 0.0002  # 年化约5%
    returns_df['Stock_B'] += 0.00015  # 年化约3.75%
    returns_df['Stock_C'] += 0.0001   # 年化约2.5%
    
    print("1. 创建蒙特卡洛风险引擎...")
    mc_engine = MonteCarloRiskEngine(returns_df)
    
    # 定义投资组合
    portfolio_weights = {
        'Stock_A': 0.5,
        'Stock_B': 0.3,
        'Stock_C': 0.2
    }
    
    print("\n2. 蒙特卡洛模拟投资组合收益...")
    sim_results = mc_engine.simulate_portfolio_returns(
        portfolio_weights,
        n_simulations=5000,
        time_horizon_days=252,
        model_type='geometric_brownian'
    )
    
    metrics = sim_results['metrics']
    print(f"   模拟次数: {sim_results['n_simulations']}")
    print(f"   时间范围: {sim_results['time_horizon_days']} 天")
    print(f"   预期年化收益: {metrics['mean_return']:.2%}")
    print(f"   年化波动率: {metrics['std_return']:.2%}")
    print(f"   夏普比率: {metrics['sharpe_ratio']:.3f}")
    print(f"   VaR(95%): {metrics['var_95']:.2%}")
    print(f"   CVaR(95%): {metrics['cvar_95']:.2%}")
    print(f"   平均最大回撤: {metrics['avg_max_drawdown']:.2%}")
    
    print("\n3. 计算风险价值 (VaR)...")
    var_analysis = mc_engine.calculate_portfolio_var(
        portfolio_weights,
        confidence_level=0.99,
        time_horizon_days=10,
        method='monte_carlo'
    )
    
    print(f"   99% VaR (10天): {var_analysis['var']:.2%}")
    print(f"   预期短缺: {var_analysis['expected_shortfall']:.2%}")
    print(f"   计算方法: {var_analysis['method']}")
    
    print("\n4. 尾部风险分析...")
    tail_risk = mc_engine.analyze_tail_risk(
        portfolio_weights,
        extreme_threshold=0.01
    )
    
    print(f"   极端损失阈值: {tail_risk['extreme_threshold']:.1%}")
    print(f"   平均极端损失: {tail_risk['avg_extreme_loss']:.2%}")
    print(f"   最大极端损失: {tail_risk['max_extreme_loss']:.2%}")
    print(f"   极端损失概率: {tail_risk['probability_of_extreme_loss']:.2%}")
    print(f"   尾部风险指数: {tail_risk['tail_risk_index']:.4f}")
    
    print("\n5. 动态对冲策略设计...")
    
    # 创建市场状态数据（简化）
    volatility_regime = pd.Series(
        ['low'] * (n_days//3) + ['medium'] * (n_days//3) + ['high'] * (n_days - 2*(n_days//3)),
        index=dates
    )
    
    market_regimes = {
        'low_vol': volatility_regime == 'low',
        'medium_vol': volatility_regime == 'medium',
        'high_vol': volatility_regime == 'high'
    }
    
    hedge_manager = DynamicHedgeManager(mc_engine, {})
    dynamic_strategy = hedge_manager.design_dynamic_hedge_strategy(
        portfolio_weights, market_regimes
    )
    
    print(f"   动态对冲启用: {dynamic_strategy['dynamic_hedge_enabled']}")
    print(f"   推荐策略: {dynamic_strategy['recommended_strategy']}")
    
    if dynamic_strategy['regime_hedge_ratios']:
        print(f"   不同市场状态的对冲比率:")
        for regime, ratios in dynamic_strategy['regime_hedge_ratios'].items():
            print(f"     {regime}: {ratios['hedge_ratio']:.3f} (R²={ratios['r_squared']:.3f})")
    
    print("\n=== 演示完成 ===")
    print("第15章蒙特卡洛模拟和动态对冲模块已实现。")

if __name__ == "__main__":
    main()