"""
TradingView风格数学变换指标库 (基于TA-Lib)

包含20个数学变换指标，每个指标都有标准化的接口：
1. calculate() - 计算数学变换值
2. signal() - 生成基于数学变换的交易信号
3. plot_style() - 获取绘图样式

生成时间: 2026-03-30 20:23:09
指标总数: 20
"""

from .acos import TV_ACOS, acos
from .asin import TV_ASIN, asin
from .atan import TV_ATAN, atan
from .ceil import TV_CEIL, ceil
from .cos import TV_COS, cos
from .cosh import TV_COSH, cosh
from .exp import TV_EXP, exp
from .floor import TV_FLOOR, floor
from .ln import TV_LN, ln
from .log10 import TV_LOG10, log10
from .sin import TV_SIN, sin
from .sinh import TV_SINH, sinh
from .sqrt import TV_SQRT, sqrt
from .tan import TV_TAN, tan
from .tanh import TV_TANH, tanh
from .stream_acos import TV_stream_ACOS, stream_acos
from .stream_asin import TV_stream_ASIN, stream_asin
from .stream_atan import TV_stream_ATAN, stream_atan
from .stream_ceil import TV_stream_CEIL, stream_ceil
from .stream_cos import TV_stream_COS, stream_cos

__all__ = [
    "TV_ACOS",
    "acos",
    "TV_ASIN",
    "asin",
    "TV_ATAN",
    "atan",
    "TV_CEIL",
    "ceil",
    "TV_COS",
    "cos",
    "TV_COSH",
    "cosh",
    "TV_EXP",
    "exp",
    "TV_FLOOR",
    "floor",
    "TV_LN",
    "ln",
    "TV_LOG10",
    "log10",
    "TV_SIN",
    "sin",
    "TV_SINH",
    "sinh",
    "TV_SQRT",
    "sqrt",
    "TV_TAN",
    "tan",
    "TV_TANH",
    "tanh",
    "TV_stream_ACOS",
    "stream_acos",
    "TV_stream_ASIN",
    "stream_asin",
    "TV_stream_ATAN",
    "stream_atan",
    "TV_stream_CEIL",
    "stream_ceil",
    "TV_stream_COS",
    "stream_cos",
]
