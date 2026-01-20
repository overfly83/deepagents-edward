#!/usr/bin/env python3
"""
Check deepagents package information.
"""
import sys
import subprocess

# Try to import deepagents
print("Trying to import deepagents...")
try:
    import deepagents
    print(f"Success! deepagents version: {deepagents.__version__}")
    print(f"Module path: {deepagents.__file__}")
except ImportError as e:
    print(f"Failed to import deepagents: {e}")
    
# Check installed packages
print("\nChecking installed packages...")
subprocess.run([sys.executable, "-m", "pip", "list", "--format=columns"], check=True)