#!/usr/bin/env python3
"""Fetch and summarize TradingView scripts from batch_4.json - v2 with live output"""
import json
import re
import urllib.request
import urllib.error
import ssl
import time
import sys

BATCH_FILE = "/Users/chengming/.openclaw/workspace/quant_trade-main/tv_learning/batch_4.json"
OUTPUT_FILE = "/Users/chengming/.openclaw/workspace/quant_trade-main/tv_learning/learned_batch_4.md"

def log(msg):
    print(msg, flush=True)

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
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        return None

def extract_description(html):
    if not html:
        return None
    # meta description
    m = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    if m:
        desc = m.group(1).replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&#39;',"'").replace('&quot;','"')
        if len(desc) > 50:
            return desc
    # og:description
    m = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', html)
    if m:
        desc = m.group(1).replace('&amp;','&').replace('&lt;','<').replace('&gt;','>').replace('&#39;',"'").replace('&quot;','"')
        if len(desc) > 50:
            return desc
    # JSON content
    m = re.search(r'"content"\s*:\s*"([^"]{100,})"', html)
    if m:
        content = m.group(1).replace('\\n','\n').replace('\\t','\t').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>')
        return content
    # chart description div
    m = re.search(r'class="tv-chart-description"[^>]*>(.*?)</div>', html, re.DOTALL)
    if m:
        text = re.sub(r'<[^>]+>', '', m.group(1)).strip()
        if len(text) > 50:
            return text
    return None

def extract_title(html):
    if not html:
        return None
    m = re.search(r'<title>([^<]+)</title>', html)
    if m:
        title = m.group(1).strip()
        if 'TradingView' in title:
            parts = title.split('—')
            if parts:
                return parts[0].strip()
    return None

def classify_strategy(name, desc):
    if not desc or len(desc) < 80:
        return None
    dl = desc.lower()
    nl = name.lower()
    # Skip pure tools
    skip_kw = ['position size calculator','color theme','3d render','candle counter','clock','timer','session time','drawing tool']
    for kw in skip_kw:
        if kw in nl or kw in dl:
            return None
    # Extract indicators
    indicators = []
    ind_patterns = {
        'RSI': r'\bRSI\b', 'MACD': r'\bMACD\b', 'EMA': r'\bEMA\b', 'SMA': r'\bSMA\b',
        'Bollinger Bands': r'\bBollinger\b|\bBB\s', 'ATR': r'\bATR\b', 'VWAP': r'\bVWAP\b',
        'Stochastic': r'\bStochastic\b|\bStoch\b', 'ADX': r'\bADX\b',
        'Ichimoku': r'\bIchimoku\b|\bKumo\b|\bTenkan\b|\bKijun\b',
        'Keltner Channel': r'\bKeltner\b', 'Pivot Points': r'\b[Pp]ivot\b',
        'Volume': r'\b[Vv]olume\b', 'Fibonacci': r'\bFibonacci\b|\bFib\b',
        'Hull MA': r'\bHull\b', 'Supertrend': r'\bSupertrend\b', 'OBV': r'\bOBV\b',
        'CCI': r'\bCCI\b', 'Divergence': r'\b[Dd]ivergence\b',
        'Fair Value Gap': r'\bFair Value Gap\b|\bFVG\b', 'Order Block': r'\bOrder Block\b',
        'Liquidity': r'\b[Ll]iquidity\b', 'Moving Average': r'\b[Mm]oving [Aa]verage\b|\bMA\b',
        'Fractals': r'\b[Ff]ractal\b', 'Heikin Ashi': r'\bHeikin\b',
        'Market Structure': r'\b[Mm]arket [Ss]tructure\b', 'Regression': r'\b[Rr]egression\b',
    }
    for ind_name, pat in ind_patterns.items():
        if re.search(pat, desc):
            indicators.append(ind_name)
    # Strategy type
    strategy_type = "多因子"
    type_kw = {
        '趋势跟踪': ['trend following','trend track','moving average cross','breakout'],
        '动量': ['momentum','oscillator','stoch','rsi','macd'],
        '均值回归': ['mean reversion','pullback','oversold','overbought'],
        '波动率': ['volatility','squeeze','bollinger','keltner','atr'],
        '支撑阻力': ['support resistance','pivot','level','zone','supply demand'],
        '订单流': ['order flow','footprint','bookmap','order block','liquidity sweep'],
    }
    for stype, kws in type_kw.items():
        for kw in kws:
            if kw in dl:
                strategy_type = stype
                break
    # Core logic
    core_logic = desc[:500].replace('\n',' ').strip()
    if len(core_logic) > 400:
        core_logic = core_logic[:400] + "..."
    # Convertibility
    needs_tick = any(kw in dl for kw in ['tick data','real-time order','level 2','order book','footprint'])
    needs_session = any(kw in dl for kw in ['rth','session','pre-market','after-hours','globex'])
    convertibility = "低" if needs_tick else ("中" if needs_session else "高")
    # Innovation
    innovations = []
    if 'decay' in dl or 'aging' in dl: innovations.append("信号衰减/老化机制")
    if 'multi-timeframe' in dl or 'mtf' in dl: innovations.append("多时间框架对齐")
    if 'quality' in dl and ('score' in dl or 'rating' in dl): innovations.append("质量评分系统")
    if 'regime' in dl: innovations.append("市场状态/行情检测")
    if 'stretch' in dl: innovations.append("过度延伸检测避免追涨")
    if 'confluence' in dl: innovations.append("多因子汇合确认")
    if 'playbook' in dl: innovations.append("策略手册分类")
    if 'z-score' in dl: innovations.append("Z-Score标准化偏差")
    if 'harmonic' in dl: innovations.append("谐波模式识别")
    if 'fibonacci' in dl or 'fib' in dl: innovations.append("斐波那契回撤/扩展")
    if 'correlation' in dl: innovations.append("跨品种相关性分析")
    if 'seasonal' in dl or 'cycle' in dl: innovations.append("周期/季节性分析")
    if not innovations: innovations.append("常规指标组合")
    # Market
    market = "通用"
    if 'futures' in dl or 'es ' in dl or 'nq' in dl: market = "期货(ES/NQ/CL/GC)"
    elif 'forex' in dl or 'eurusd' in dl: market = "外汇"
    elif 'bitcoin' in dl or 'btc' in dl or 'crypto' in dl: market = "加密货币"
    elif 'gold' in dl or 'xauusd' in dl: market = "黄金"
    # Timeframe
    timeframe = "多周期"
    if 'scalp' in dl: timeframe = "1-5分钟(剥头皮)"
    elif 'intraday' in dl or '15-min' in dl: timeframe = "15分钟-4小时(日内)"
    elif 'swing' in dl or 'daily' in dl: timeframe = "日线(波段)"
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

    total = len(scripts)
    results = []
    substantial = 0
    skipped = 0
    failed = 0
    seen_urls = set()

    for i, script in enumerate(scripts):
        name = script['name']
        url = script['url']

        if url in seen_urls:
            log(f"[{i+1}/{total}] SKIP (dup): {name}")
            skipped += 1
            results.append((i+1, name, url, "DUPLICATE", None))
            continue
        seen_urls.add(url)

        log(f"[{i+1}/{total}] Fetching: {name}")
        html = fetch_url(url)
        if not html:
            log(f"  -> FAILED")
            failed += 1
            results.append((i+1, name, url, "FAILED", None))
            time.sleep(0.5)
            continue

        desc = extract_description(html)
        title = extract_title(html)
        info = classify_strategy(name, desc)

        if info is None:
            log(f"  -> SKIP (no substantial content)")
            skipped += 1
            results.append((i+1, name, url, "SKIPPED", None, desc[:200] if desc else ""))
        else:
            log(f"  -> OK ({info['strategy_type']})")
            substantial += 1
            results.append((i+1, name, url, "OK", info, title))

        time.sleep(0.6)

    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Batch 4 - TradingView 脚本学习总结\n\n")
        f.write(f"生成时间: {time.strftime('%Y-%m-%d %H:%M')}\n")
        f.write(f"总共: {total} 个脚本\n")
        f.write(f"有实质内容: {substantial} 个\n")
        f.write(f"跳过/无内容: {skipped} 个\n")
        f.write(f"获取失败: {failed} 个\n\n")
        f.write("---\n\n")

        for entry in results:
            idx = entry[0]
            name = entry[1]
            url = entry[2]
            status = entry[3]
            info = entry[4]

            f.write(f"## {idx}. {name}\n\n")
            f.write(f"- **URL**: {url}\n")

            if status == "OK" and info:
                f.write(f"- **核心逻辑**: {info['core_logic']}\n")
                f.write(f"- **技术指标**: {', '.join(info['indicators'])}\n")
                f.write(f"- **策略类型**: {info['strategy_type']}\n")
                f.write(f"- **适用市场/时间框架**: {info['market']} / {info['timeframe']}\n")
                f.write(f"- **创新点**: {', '.join(info['innovations'])}\n")
                f.write(f"- **可转换性**: {info['convertibility']}\n")
            elif status == "DUPLICATE":
                f.write(f"- **状态**: 跳过 - 重复URL\n")
            elif status == "SKIPPED":
                f.write(f"- **状态**: 跳过 - 无实质策略内容或纯工具\n")
            elif status == "FAILED":
                f.write(f"- **状态**: 获取失败\n")

            f.write("\n---\n\n")

    log(f"\nDone! Written to {OUTPUT_FILE}")
    log(f"Total: {total}, Substantial: {substantial}, Skipped: {skipped}, Failed: {failed}")

if __name__ == "__main__":
    main()
