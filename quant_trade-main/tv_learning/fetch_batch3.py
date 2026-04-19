#!/usr/bin/env python3
"""Fetch and analyze TradingView scripts from batch_3.json"""
import json
import urllib.request
import re
import time
import sys

def fetch_description(url):
    """Fetch TradingView script page and extract description content."""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        resp = urllib.request.urlopen(req, timeout=15)
        html = resp.read().decode('utf-8', errors='replace')

        # Extract meta description
        desc_match = re.search(r'<meta name="description" content="([^"]*)"', html)
        og_desc = re.search(r'<meta property="og:description" content="([^"]*)"', html)
        title_match = re.search(r'<title>([^<]+)</title>', html)

        # Try to find the main content in the page
        # Look for the script description block
        content = ""
        if desc_match:
            content = desc_match.group(1)
        elif og_desc:
            content = og_desc.group(1)

        title = title_match.group(1).replace(' — Indicator by', ' by').replace(' — TradingView', '') if title_match else "Unknown"

        # Also try to find longer description in the HTML body
        # TradingView puts script description in a specific div
        body_match = re.search(r'"description"\s*:\s*"((?:[^"\\]|\\.)*)"', html)
        if body_match:
            longer = body_match.group(1).encode().decode('unicode_escape')
            if len(longer) > len(content):
                content = longer

        return title, content[:3000]  # Limit content length
    except Exception as e:
        return None, f"FETCH_ERROR: {str(e)}"

def main():
    with open('/Users/chengming/.openclaw/workspace/quant_trade-main/tv_learning/batch_3.json', 'r') as f:
        scripts = json.load(f)

    print(f"Total scripts to process: {len(scripts)}")

    results = []
    for i, script in enumerate(scripts):
        name = script.get('name', 'Unknown')
        url = script.get('url', '')
        print(f"[{i+1}/{len(scripts)}] Fetching: {name}...")
        sys.stdout.flush()

        title, desc = fetch_description(url)
        results.append({
            'index': i + 1,
            'name': name,
            'title': title or name,
            'url': url,
            'description': desc
        })

        # Small delay to be polite
        time.sleep(0.3)

    # Save raw results
    with open('/Users/chengming/.openclaw/workspace/quant_trade-main/tv_learning/batch3_raw.json', 'w') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Saved raw results to batch3_raw.json")

if __name__ == '__main__':
    main()
