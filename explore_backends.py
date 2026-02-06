#!/usr/bin/env python3
"""Script to explore DeepAgents backend components."""

import sys
from pprint import pprint

# Add src directory to path
sys.path.insert(0, 'c:\\Users\\zhl83\\Desktop\\deepagents-edward\\src')

from deepagents.backends import StateBackend, StoreBackend, BackendProtocol, CompositeBackend

def explore_backends():
    """Explore backend components."""
    print("=== Exploring DeepAgents Backends ===\n")
    
    # Check module structure
    print("1. Module attributes:")
    print(f"   - StateBackend: {StateBackend}")
    print(f"   - StoreBackend: {StoreBackend}")
    print(f"   - BackendProtocol: {BackendProtocol}")
    print(f"   - CompositeBackend: {CompositeBackend}")
    print()
    
    # Check StateBackend
    print("2. StateBackend details:")
    print(f"   - Methods: {[m for m in dir(StateBackend) if not m.startswith('_')]}")
    print()
    
    # Check StoreBackend  
    print("3. StoreBackend details:")
    print(f"   - Methods: {[m for m in dir(StoreBackend) if not m.startswith('_')]}")
    print()
    
    # Check dependencies needed for initialization
    print("4. Checking ToolRuntime dependency:")
    try:
        from deepagents.runtime import ToolRuntime
        print(f"   - Found ToolRuntime: {ToolRuntime}")
        
        # Try to get more info about ToolRuntime
        print(f"   - ToolRuntime methods: {[m for m in dir(ToolRuntime) if not m.startswith('_')]}")
        
    except ImportError as e:
        print(f"   - ToolRuntime import failed: {e}")
    except Exception as e:
        print(f"   - Error checking ToolRuntime: {e}")
    
    print()
    
    # Look for alternative backend initialization
    print("5. Checking if there's a simple way to create backends:")
    print("   - Checking deepagents module structure...")
    
    try:
        import deepagents
        print(f"   - deepagents modules: {[m for m in dir(deepagents) if not m.startswith('_')]}")
        
        # Check if there are any factory methods or utilities
        if hasattr(deepagents, 'backends'):
            print(f"   - deepagents.backends has: {[m for m in dir(deepagents.backends) if not m.startswith('_')]}")
            
    except Exception as e:
        print(f"   - Error exploring deepagents module: {e}")

if __name__ == "__main__":
    explore_backends()