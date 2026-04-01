#!/usr/bin/env python3
"""
测试TradingView网站访问 - 按照用户要求
用户指令: "多等等，别开始访问不了就退出，timeout设置长一点"
"""

import urllib.request
import socket
import time
from datetime import datetime

print("=" * 80)
print("🔗 测试TradingView网站访问 - 按照用户要求")
print("=" * 80)
print("用户指令: 多等等，别开始访问不了就退出，timeout设置长一点")
print("测试时间:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
print("测试URL: https://www.tradingview.com/scripts/")
print("=" * 80)

# 配置 (按照用户要求)
timeout_seconds = 60  # 长timeout
retry_count = 5       # 重试次数
retry_delay = 10      # 重试间隔

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
}

for attempt in range(1, retry_count + 1):
    print(f"\n尝试 {attempt}/{retry_count}:")
    print(f"  设置timeout: {timeout_seconds}秒")
    print(f"  开始时间: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # 设置超时
        socket.setdefaulttimeout(timeout_seconds)
        
        # 创建请求
        req = urllib.request.Request(
            "https://www.tradingview.com/scripts/",
            headers=headers
        )
        
        # 尝试访问
        start_time = time.time()
        response = urllib.request.urlopen(req, timeout=timeout_seconds)
        elapsed_time = time.time() - start_time
        
        # 检查响应
        status_code = response.getcode()
        content_type = response.headers.get('Content-Type', '未知')
        content_length = len(response.read(5000))  # 读取前5000字节
        
        print(f"  ✅ 连接成功!")
        print(f"     响应时间: {elapsed_time:.2f}秒")
        print(f"     状态码: {status_code}")
        print(f"     内容类型: {content_type}")
        print(f"     内容长度: {content_length} 字节 (预览)")
        
        # 检查是否包含TradingView内容
        response.seek(0)
        content_preview = response.read(1000).decode('utf-8', errors='ignore')
        if "tradingview" in content_preview.lower() or "scripts" in content_preview.lower():
            print(f"  ✅ 确认是TradingView网站")
        else:
            print(f"  ⚠️  内容可能不是TradingView")
        
        print(f"\n🎉 网络测试通过! 可以开始TradingView网站学习")
        print(f"   按照用户要求: 多等等的策略有效")
        exit(0)
        
    except socket.timeout:
        print(f"  ⏱️  Timeout (等待{timeout_seconds}秒无响应)")
    except urllib.error.URLError as e:
        print(f"  ❌ URL错误: {e.reason}")
    except Exception as e:
        print(f"  ⚠️  连接错误: {type(e).__name__}: {e}")
    
    # 如果不是最后一次尝试，等待后重试
    if attempt < retry_count:
        print(f"  ⏸️  等待{retry_delay}秒后重试...")
        time.sleep(retry_delay)

print(f"\n❌ 所有{retry_count}次尝试都失败了")
print("按照用户要求: 访问不了要第一时间汇报")
print("⚠️  网络访问失败，将启用备用学习系统")
exit(1)