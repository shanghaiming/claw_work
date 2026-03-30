"""
TradingView风格指标库 (基于TA-Lib)

包含100个TradingView风格的技术指标，每个指标都有标准化的接口：
1. calculate() - 计算指标值
2. signal() - 生成交易信号
3. plot_style() - 获取绘图样式

生成时间: 2026-03-30 18:55:49
指标总数: 99
"""

from .cdl2crows import TV_CDL2CROWS, cdl2crows
from .cdl3blackcrows import TV_CDL3BLACKCROWS, cdl3blackcrows
from .cdl3inside import TV_CDL3INSIDE, cdl3inside
from .cdl3linestrike import TV_CDL3LINESTRIKE, cdl3linestrike
from .cdl3outside import TV_CDL3OUTSIDE, cdl3outside
from .cdl3whitesoldiers import TV_CDL3WHITESOLDIERS, cdl3whitesoldiers
from .cdlabandonedbaby import TV_CDLABANDONEDBABY, cdlabandonedbaby
from .cdlbelthold import TV_CDLBELTHOLD, cdlbelthold
from .cdlbreakaway import TV_CDLBREAKAWAY, cdlbreakaway
from .cdlconcealbabyswall import TV_CDLCONCEALBABYSWALL, cdlconcealbabyswall
from .cdlcounterattack import TV_CDLCOUNTERATTACK, cdlcounterattack
from .cdldarkcloudcover import TV_CDLDARKCLOUDCOVER, cdldarkcloudcover
from .cdldoji import TV_CDLDOJI, cdldoji
from .cdldojistar import TV_CDLDOJISTAR, cdldojistar
from .cdldragonflydoji import TV_CDLDRAGONFLYDOJI, cdldragonflydoji
from .cdlengulfing import TV_CDLENGULFING, cdlengulfing
from .cdleveningdojistar import TV_CDLEVENINGDOJISTAR, cdleveningdojistar
from .cdleveningstar import TV_CDLEVENINGSTAR, cdleveningstar
from .cdlgapsidesidewhite import TV_CDLGAPSIDESIDEWHITE, cdlgapsidesidewhite
from .cdlgravestonedoji import TV_CDLGRAVESTONEDOJI, cdlgravestonedoji
from .cdlhammer import TV_CDLHAMMER, cdlhammer
from .cdlharami import TV_CDLHARAMI, cdlharami
from .cdlharamicross import TV_CDLHARAMICROSS, cdlharamicross
from .cdlhighwave import TV_CDLHIGHWAVE, cdlhighwave
from .cdlhikkake import TV_CDLHIKKAKE, cdlhikkake
from .cdlhikkakemod import TV_CDLHIKKAKEMOD, cdlhikkakemod
from .cdlhomingpigeon import TV_CDLHOMINGPIGEON, cdlhomingpigeon
from .cdlidentical3crows import TV_CDLIDENTICAL3CROWS, cdlidentical3crows
from .cdlinneck import TV_CDLINNECK, cdlinneck
from .cdlinvertedhammer import TV_CDLINVERTEDHAMMER, cdlinvertedhammer
from .cdlkicking import TV_CDLKICKING, cdlkicking
from .cdlkickingbylength import TV_CDLKICKINGBYLENGTH, cdlkickingbylength
from .cdllongleggeddoji import TV_CDLLONGLEGGEDDOJI, cdllongleggeddoji
from .chain import TV_CHAIN, chain
from .get_compatibility import TV_GET_COMPATIBILITY, get_compatibility
from .get_function_groups import TV_GET_FUNCTION_GROUPS, get_function_groups
from .get_functions import TV_GET_FUNCTIONS, get_functions
from .get_unstable_period import TV_GET_UNSTABLE_PERIOD, get_unstable_period
from .set_compatibility import TV_SET_COMPATIBILITY, set_compatibility
from .set_unstable_period import TV_SET_UNSTABLE_PERIOD, set_unstable_period

__all__ = [
    "TV_ACCBANDS",
    "TV_AD",
    "TV_ADD",
    "TV_ADOSC",
    "TV_ADX",
    "TV_ADXR",
    "TV_APO",
    "TV_AROON",
    "TV_AROONOSC",
    "TV_ATR",
    "TV_AVGDEV",
    "TV_AVGPRICE",
    "TV_BBANDS",
    "TV_BETA",
    "TV_BOP",
    "TV_CCI",
    "TV_CDL2CROWS",
    "TV_CDL3BLACKCROWS",
    "TV_CDL3INSIDE",
    "TV_CDL3LINESTRIKE",
    "TV_CDL3OUTSIDE",
    "TV_CDL3STARSINSOUTH",
    "TV_CDL3WHITESOLDIERS",
    "TV_CDLABANDONEDBABY",
    "TV_CDLADVANCEBLOCK",
    "TV_CDLBELTHOLD",
    "TV_CDLBREAKAWAY",
    "TV_CDLCLOSINGMARUBOZU",
    "TV_CDLCONCEALBABYSWALL",
    "TV_CDLCOUNTERATTACK",
    "TV_CDLDARKCLOUDCOVER",
    "TV_CDLDOJI",
    "TV_CDLDOJISTAR",
    "TV_CDLDRAGONFLYDOJI",
    "TV_CDLENGULFING",
    "TV_CDLEVENINGDOJISTAR",
    "TV_CDLEVENINGSTAR",
    "TV_CDLGAPSIDESIDEWHITE",
    "TV_CDLGRAVESTONEDOJI",
    "TV_CDLHAMMER",
    "TV_CDLHANGINGMAN",
    "TV_CDLHARAMI",
    "TV_CDLHARAMICROSS",
    "TV_CDLHIGHWAVE",
    "TV_CDLHIKKAKE",
    "TV_CDLHIKKAKEMOD",
    "TV_CDLHOMINGPIGEON",
    "TV_CDLIDENTICAL3CROWS",
    "TV_CDLINNECK",
    "TV_CDLINVERTEDHAMMER",
    "TV_CDLKICKING",
    "TV_CDLKICKINGBYLENGTH",
    "TV_CDLLADDERBOTTOM",
    "TV_CDLLONGLEGGEDDOJI",
    "TV_CDLMARUBOZU",
    "TV_CDLMATCHINGLOW",
    "TV_CDLMATHOLD",
    "TV_CDLRICKSHAWMAN",
    "TV_CHAIN",
    "TV_CMO",
    "TV_CORREL",
    "TV_DEMA",
    "TV_DIV",
    "TV_DX",
    "TV_EMA",
    "TV_GET_COMPATIBILITY",
    "TV_GET_FUNCTIONS",
    "TV_GET_FUNCTION_GROUPS",
    "TV_GET_UNSTABLE_PERIOD",
    "TV_HT_DCPERIOD",
    "TV_HT_DCPHASE",
    "TV_HT_PHASOR",
    "TV_HT_SINE",
    "TV_HT_TRENDLINE",
    "TV_HT_TRENDMODE",
    "TV_IMI",
    "TV_KAMA",
    "TV_LINEARREG",
    "TV_LINEARREG_ANGLE",
    "TV_LINEARREG_INTERCEPT",
    "TV_LINEARREG_SLOPE",
    "TV_MEDPRICE",
    "TV_MIDPOINT",
    "TV_MIDPRICE",
    "TV_MIN",
    "TV_MININDEX",
    "TV_MULT",
    "TV_NATR",
    "TV_OBV",
    "TV_SET_COMPATIBILITY",
    "TV_SET_UNSTABLE_PERIOD",
    "TV_STDDEV",
    "TV_SUB",
    "TV_SUM",
    "TV_TRANGE",
    "TV_TSF",
    "TV_TYPPRICE",
    "TV_VAR",
    "TV_WCLPRICE",
    "accbands",
    "ad",
    "add",
    "adosc",
    "adx",
    "adxr",
    "apo",
    "aroon",
    "aroonosc",
    "atr",
    "avgdev",
    "avgprice",
    "bbands",
    "beta",
    "bop",
    "cci",
    "cdl2crows",
    "cdl3blackcrows",
    "cdl3inside",
    "cdl3linestrike",
    "cdl3outside",
    "cdl3starsinsouth",
    "cdl3whitesoldiers",
    "cdlabandonedbaby",
    "cdladvanceblock",
    "cdlbelthold",
    "cdlbreakaway",
    "cdlclosingmarubozu",
    "cdlconcealbabyswall",
    "cdlcounterattack",
    "cdldarkcloudcover",
    "cdldoji",
    "cdldojistar",
    "cdldragonflydoji",
    "cdlengulfing",
    "cdleveningdojistar",
    "cdleveningstar",
    "cdlgapsidesidewhite",
    "cdlgravestonedoji",
    "cdlhammer",
    "cdlhangingman",
    "cdlharami",
    "cdlharamicross",
    "cdlhighwave",
    "cdlhikkake",
    "cdlhikkakemod",
    "cdlhomingpigeon",
    "cdlidentical3crows",
    "cdlinneck",
    "cdlinvertedhammer",
    "cdlkicking",
    "cdlkickingbylength",
    "cdlladderbottom",
    "cdllongleggeddoji",
    "cdlmarubozu",
    "cdlmatchinglow",
    "cdlmathold",
    "cdlrickshawman",
    "chain",
    "cmo",
    "correl",
    "dema",
    "div",
    "dx",
    "ema",
    "get_compatibility",
    "get_function_groups",
    "get_functions",
    "get_unstable_period",
    "ht_dcperiod",
    "ht_dcphase",
    "ht_phasor",
    "ht_sine",
    "ht_trendline",
    "ht_trendmode",
    "imi",
    "kama",
    "linearreg",
    "linearreg_angle",
    "linearreg_intercept",
    "linearreg_slope",
    "medprice",
    "midpoint",
    "midprice",
    "min",
    "minindex",
    "mult",
    "natr",
    "obv",
    "set_compatibility",
    "set_unstable_period",
    "stddev",
    "sub",
    "sum",
    "trange",
    "tsf",
    "typprice",
    "var",
    "wclprice",
]
