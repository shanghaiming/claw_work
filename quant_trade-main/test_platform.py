#!/usr/bin/env python3
"""
快速测试脚本 - 测试量化平台功能
"""
import subprocess
import sys
import os
import time

project_root = "/Users/chengming/.openclaw/workspace/quant_trade-main"
sys.path.insert(0, project_root)

def test_cli_commands():
    """测试CLI命令"""
    print("🧪 测试CLI命令...")
    
    commands = [
        ["python", "cli.py", "strategy", "list", "--simple"],
        ["python", "cli.py", "backtest", "--strategy", "ma_strategy", "--symbol", "000001.SZ", "--initial-cash", "100000"],
        ["python", "cli.py", "select", "--strategy-id", "1", "--limit", "3", "--format", "text"]
    ]
    
    python_exe = sys.executable
    
    for cmd in commands:
        cmd[0] = python_exe
        print(f"\n🔧 执行: {' '.join(cmd)}")
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=project_root, timeout=30)
            if result.returncode == 0:
                print(f"✅ 成功")
                if "select" in cmd:
                    # 选股输出可能很长，只显示一部分
                    lines = result.stdout.strip().split('\n')
                    for line in lines[-5:]:
                        print(f"   {line}")
            else:
                print(f"❌ 失败: {result.stderr[:100]}")
        except subprocess.TimeoutExpired:
            print(f"⏰ 超时")
        except Exception as e:
            print(f"⚠️  错误: {e}")
    
def test_dashboard_api():
    """测试看板API"""
    print("\n🧪 测试看板API...")
    
    # 启动看板
    print("启动看板...")
    python_exe = sys.executable
    dashboard_script = os.path.join(project_root, "dashboard.py")
    
    # 使用subprocess启动
    proc = subprocess.Popen(
        [python_exe, dashboard_script, "--port", "8083", "--debug"],
        cwd=project_root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    time.sleep(3)  # 等待启动
    
    try:
        # 测试健康检查
        import urllib.request
        import json
        
        try:
            req = urllib.request.Request("http://127.0.0.1:8083/api/health")
            response = urllib.request.urlopen(req, timeout=5)
            data = json.load(response)
            print(f"✅ 健康检查: {data.get('status')}")
        except Exception as e:
            print(f"❌ 健康检查失败: {e}")
        
        # 测试仪表盘统计
        try:
            req = urllib.request.Request("http://127.0.0.1:8083/api/dashboard/stats")
            response = urllib.request.urlopen(req, timeout=5)
            data = json.load(response)
            if data.get('success'):
                stats = data['data']
                print(f"✅ 仪表盘统计: {stats['strategy_count']}策略, {stats['stock_count']}股票")
        except Exception as e:
            print(f"❌ 仪表盘统计失败: {e}")
            
    finally:
        # 停止看板
        proc.terminate()
        proc.wait()

def check_system():
    """检查系统状态"""
    print("\n🔍 系统检查...")
    
    # 检查关键文件
    files = [
        "cli.py",
        "dashboard.py",
        "stock_select.py",
        "strategies/csv_auto_select.py",
        "backtest/runner.py",
        "simple_dashboard.py"  # 旧版，应该存在但不使用
    ]
    
    for file in files:
        path = os.path.join(project_root, file)
        if os.path.exists(path):
            size = os.path.getsize(path)
            print(f"✅ {file}: {size:,} bytes")
        else:
            print(f"❌ {file}: 不存在")
    
    # 检查数据目录
    data_dirs = ["data/daily_data2", "data/week_data2"]
    for dir_path in data_dirs:
        path = os.path.join(project_root, dir_path)
        if os.path.exists(path):
            files_count = len([f for f in os.listdir(path) if f.endswith('.csv')])
            print(f"✅ {dir_path}: {files_count}个CSV文件")
        else:
            print(f"❌ {dir_path}: 不存在")

def main():
    print("=" * 60)
    print("🔬 量化平台功能测试")
    print("=" * 60)
    
    check_system()
    test_cli_commands()
    test_dashboard_api()
    
    print("\n" + "=" * 60)
    print("📋 测试完成")
    print("=" * 60)

if __name__ == "__main__":
    main()