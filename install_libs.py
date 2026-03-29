#!/usr/bin/env python3
import subprocess
import sys
import time

print("Installing required libraries for stock analysis...")

# Upgrade pip first
print("\n1. Upgrading pip...")
try:
    subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                   capture_output=True, check=True, text=True)
    print("✓ pip upgraded")
except Exception as e:
    print(f"✗ pip upgrade failed: {e}")

# Install core libraries
core_libs = ['pandas', 'numpy', 'yfinance', 'ta']
for lib in core_libs:
    print(f"\n2. Installing {lib}...")
    try:
        result = subprocess.run([sys.executable, '-m', 'pip', 'install', lib], 
                               capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {lib} installed successfully")
        else:
            print(f"✗ {lib} installation failed: {result.stderr[:200]}")
    except Exception as e:
        print(f"✗ {lib} installation error: {e}")

# Also install matplotlib for plotting
print("\n3. Installing matplotlib for visualization...")
try:
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'matplotlib'], 
                   capture_output=True, check=True, text=True)
    print("✓ matplotlib installed")
except Exception as e:
    print(f"✗ matplotlib installation failed: {e}")

# Verify installations
print("\n4. Verifying installations...")
for lib in core_libs + ['matplotlib']:
    try:
        __import__(lib)
        print(f"✓ {lib} successfully imported")
    except ImportError:
        print(f"✗ {lib} failed to import")

print("\nInstallation process complete!")