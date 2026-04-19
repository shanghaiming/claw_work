#!/usr/bin/env python3
"""Fetch and summarize TradingView scripts from batch_4_new.json"""
import json
import re
import urllib.request
import urllib.error
import ssl
import time
import sys

BATCH_FILE = "/Users/chengming/.openclaw/workspace/quant_trade-main/tv_learning/batch_4_new.json"
OUTPUT_FILE = "/Users/chengming/.openclaw/workspace/quant_trade-main/tv_learning/batch4_new_raw.json"

# Already deep-analyzed via webReader - skip these
DEEP_ANALYZED = {
    '7v1PWf2e', '82NYRAdD', '9HQHCV2q', 'B2aMfpd2', 'BWBAoVET',
    'BXtZu6Yf', 'DDB8YRuN', 'DL8BpgzT', 'DRgzod5I',
}

# Pure ID-only entries (no name, just hash)
ID_ONLY = {'7aCcBkB8', '7e0Qknj9', '7ta14MGG', '81qW24I2', '9ZO0Wa08', '9cckfn7S',
           '9t1cCTAv', 'BFH87fmb', 'BHhJyAT1', 'BJDRgy7z', 'BbtGQtya', 'BdaYgaUE',
           'Cc6q3BSU', 'CIqpuXEC', 'CMDiJjby', 'DmBG9zK5', 'DrpqDrNv'}

# Tools/utilities to skip
TOOLS = {'AMTLfoEf', 'BnoJgkde', 'D38ZP8Fe', 'DXdJJTts'}

# Test/duplicate to skip
SKIP = {'8TmMnT0H'}

seen_urls = set()

def fetch_url(url):
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
    }
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=15) as resp:
            html = resp.read().decode('utf-8', errors='replace')
        return html
    except Exception as e:
        return None

def extract_description(html):
    if not html:
        return None
    # Meta description
    meta_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    if meta_match:
        desc = meta_match.group(1)
        desc = desc.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
        if len(desc) > 50:
            return desc
    # og:description
    og_match = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
    if og_match:
        desc = og_match.group(1)
        desc = desc.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>').replace('&#39;', "'").replace('&quot;', '"')
        if len(desc) > 50:
            return desc
    # JSON-LD content
    content_match = re.search(r'"content"\s*:\s*"([^"]{100,})"', html)
    if content_match:
        content = content_match.group(1)
        content = content.replace('\\n', '\n').replace('\\t', '\t')
        content = content.replace('&amp;', '&').replace('&lt;', '<').replace('&gt;', '>')
        return content
    # Page content div
    content_div = re.search(r'class="tv-chart-description"[^>]*>(.*?)</div>', html, re.DOTALL)
    if content_div:
        text = re.sub(r'<[^>]+>', '', content_div.group(1))
        text = text.strip()
        if len(text) > 50:
            return text
    return None

def classify_strategy(name, desc):
    if not desc:
        return None
    name_lower = name.lower()
    desc_lower = desc.lower()

    skip_kw = ['position size calculator', 'color theme', '3d render', 'candle counter',
               'clock', 'timer', 'session time', 'drawing tool']
    for kw in skip_kw:
        if kw in name_lower or kw in desc_lower:
            return None
    if len(desc) < 80:
        return None

    indicators = []
    indicator_patterns = {
        'RSI': r'\bRSI\b', 'MACD': r'\bMACD\b', 'EMA': r'\bEMA\b', 'SMA': r'\bSMA\b',
        'Bollinger Bands': r'\bBollinger\b|\bBB\s', 'ATR': r'\bATR\b', 'VWAP': r'\bVWAP\b',
        'Stochastic': r'\bStochastic\b|\bStoch\b', 'ADX': r'\bADX\b',
        'Ichimoku': r'\bIchimoku\b|\bKumo\b|\bTenkan\b|\bKijun\b',
        'Keltner Channel': r'\bKeltner\b', 'Pivot Points': r'\b[Pp]ivot\b',
        'Volume': r'\b[Vv]olume\b', 'Fibonacci': r'\bFibonacci\b|\bFib\b',
        'Hull MA': r'\bHull\b', 'Supertrend': r'\bSupertrend\b', 'OBV': r'\bOBV\b',
        'CCI': r'\bCCI\b', 'Divergence': r'\b[Dd]ivergence\b',
        'Fair Value Gap': r'\bFair Value Gap\b|\bFVG\b', 'Order Block': r'\bOrder Block\b|\bOB\b',
        'Liquidity': r'\b[Ll]iquidity\b', 'Moving Average': r'\b[Mm]oving [Aa]verage\b|\bMA\b',
        'Fractals': r'\b[Ff]ractal\b', 'Heikin Ashi': r'\bHeikin\b|\bHA\b',
        'Market Structure': r'\b[Mm]arket [Ss]tructure\b', 'Regression': r'\b[Rr]egression\b',
    }
    for ind_name, pattern in indicator_patterns.items():
        if re.search(pattern, desc):
            indicators.append(ind_name)

    strategy_type = "多因子"
    type_keywords = {
        '趋势跟踪': ['trend following', 'trend track', 'moving average cross', 'breakout'],
        '动量': ['momentum', 'oscillator', 'stoch', 'rsi', 'macd'],
        '均值回归': ['mean reversion', 'pullback', 'oversold', 'overbought'],
        '波动率': ['volatility', 'squeeze', 'bollinger', 'keltner', 'atr'],
        '支撑阻力': ['support resistance', 'pivot', 'level', 'zone', 'supply demand'],
        '订单流': ['order flow', 'footprint', 'bookmap', 'order block', 'liquidity sweep'],
    }
    for stype, keywords in type_keywords.items():
        for kw in keywords:
            if kw in desc_lower:
                strategy_type = stype
                break

    core_logic = desc[:500].replace('\n', ' ').strip()
    if len(core_logic) > 400:
        core_logic = core_logic[:400] + "..."

    needs_tick = any(kw in desc_lower for kw in ['tick data', 'real-time order', 'level 2', 'order book', 'footprint'])
    needs_session = any(kw in desc_lower for kw in ['rth', 'session', 'pre-market', 'after-hours', 'globex'])
    if needs_tick:
        convertibility = "低"
    elif needs_session:
        convertibility = "中"
    else:
        convertibility = "高"

    innovations = []
    if 'decay' in desc_lower or 'aging' in desc_lower:
        innovations.append("信号衰减/老化机制")
    if 'multi-timeframe' in desc_lower or 'mtf' in desc_lower:
        innovations.append("多时间框架对齐")
    if 'quality' in desc_lower and ('score' in desc_lower or 'rating' in desc_lower):
        innovations.append("质量评分系统")
    if 'regime' in desc_lower:
        innovations.append("市场状态/行情检测")
    if 'confluence' in desc_lower:
        innovations.append("多因子汇合确认")
    if 'knn' in desc_lower or 'k-nearest' in desc_lower:
        innovations.append("KNN机器学习")
    if 'wavelet' in desc_lower:
        innovations.append("小波变换频域分析")
    if 'sigmoid' in desc_lower:
        innovations.append("Sigmoid概率评分")
    if not innovations:
        innovations.append("常规指标组合")

    market = "通用"
    if 'futures' in desc_lower or 'es ' in desc_lower or 'nq' in desc_lower:
        market = "期货(ES/NQ/CL/GC)"
    elif 'forex' in desc_lower or 'eurusd' in desc_lower:
        market = "外汇"
    elif 'bitcoin' in desc_lower or 'btc' in desc_lower or 'crypto' in desc_lower:
        market = "加密货币"
    elif 'gold' in desc_lower or 'xauusd' in desc_lower:
        market = "黄金"

    timeframe = "多周期"
    if 'scalp' in desc_lower:
        timeframe = "1-5分钟(剥头皮)"
    elif 'intraday' in desc_lower or '15-min' in desc_lower:
        timeframe = "15分钟-4小时(日内)"
    elif 'swing' in desc_lower or 'daily' in desc_lower:
        timeframe = "日线(波段)"

    return {
        'core_logic': core_logic,
        'indicators': indicators if indicators else ['价格行为'],
        'strategy_type': strategy_type,
        'market': market,
        'timeframe': timeframe,
        'innovations': innovations,
        'convertibility': convertibility,
    }

def main():
    with open(BATCH_FILE, 'r') as f:
        scripts = json.load(f)

    results = []
    total = len(scripts)
    substantial = 0
    skipped = 0
    failed = 0

    for i, script in enumerate(scripts):
        name = script['name']
        url = script['url']
        script_id = name.split()[0] if name else ''

        # Check duplicates
        if url in seen_urls:
            print(f"[{i+1}/{total}] SKIP (duplicate): {name}")
            skipped += 1
            results.append({'idx': i+1, 'name': name, 'url': url, 'status': 'DUPLICATE'})
            continue
        seen_urls.add(url)

        # Deep analyzed - mark as such
        if script_id in DEEP_ANALYZED:
            print(f"[{i+1}/{total}] DEEP (already analyzed): {name}")
            results.append({'idx': i+1, 'name': name, 'url': url, 'status': 'DEEP_ANALYZED'})
            continue

        # ID-only
        if script_id in ID_ONLY:
            print(f"[{i+1}/{total}] SKIP (ID-only): {name}")
            skipped += 1
            results.append({'idx': i+1, 'name': name, 'url': url, 'status': 'ID_ONLY'})
            continue

        # Tools
        if script_id in TOOLS:
            print(f"[{i+1}/{total}] SKIP (tool): {name}")
            skipped += 1
            results.append({'idx': i+1, 'name': name, 'url': url, 'status': 'TOOL'})
            continue

        # Skip list
        if script_id in SKIP:
            print(f"[{i+1}/{total}] SKIP (blacklist): {name}")
            skipped += 1
            results.append({'idx': i+1, 'name': name, 'url': url, 'status': 'SKIPPED'})
            continue

        # Gann - non-quant
        if 'gann' in name.lower() or 'sq9' in name.lower():
            print(f"[{i+1}/{total}] SKIP (gann/non-quant): {name}")
            skipped += 1
            results.append({'idx': i+1, 'name': name, 'url': url, 'status': 'NON_QUANT'})
            continue

        print(f"[{i+1}/{total}] Fetching: {name}")

        html = fetch_url(url)
        if not html:
            print(f"  -> FAILED to fetch")
            failed += 1
            results.append({'idx': i+1, 'name': name, 'url': url, 'status': 'FAILED'})
            time.sleep(1)
            continue

        desc = extract_description(html)
        info = classify_strategy(name, desc)

        if info is None:
            print(f"  -> SKIPPED (no substantial content)")
            skipped += 1
            results.append({'idx': i+1, 'name': name, 'url': url, 'status': 'SKIPPED_NO_CONTENT'})
        else:
            print(f"  -> OK ({info['strategy_type']})")
            substantial += 1
            results.append({
                'idx': i+1, 'name': name, 'url': url, 'status': 'OK',
                'info': info, 'desc': desc[:300] if desc else None
            })

        time.sleep(0.8)

    # Save raw results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nDone! Written to {OUTPUT_FILE}")
    print(f"Total: {total}, Substantial: {substantial}, Skipped: {skipped}, Failed: {failed}, Deep: {len(DEEP_ANALYZED)}")

if __name__ == "__main__":
    main()
