#!/usr/bin/env python3
import sys
import subprocess

libs = ['pandas', 'numpy', 'yfinance', 'ta', 'talib']

print("Checking Python libraries...")
for lib in libs:
    try:
        __import__(lib)
        print(f"✓ {lib} is available")
    except ImportError:
        print(f"✗ {lib} is NOT available")

# Check if we can install via pip
print("\nChecking pip availability...")
try:
    subprocess.run([sys.executable, '-m', 'pip', '--version'], capture_output=True, check=True)
    print("✓ pip is available")
except:
    print("✗ pip is not available")