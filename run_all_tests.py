#!/usr/bin/env python3
"""
Run all tests in the project, including both pytest tests and standalone test scripts
"""

import os
import sys
import subprocess
import glob

def run_pytest_tests():
    """Run all pytest tests"""
    print("=" * 60)
    print("Running pytest tests...")
    print("=" * 60)
    
    result = subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"])
    
    print("\n" + "=" * 60)
    print(f"pytest tests completed with exit code: {result.returncode}")
    print("=" * 60)
    
    return result.returncode

def run_standalone_script(script_path):
    """Run a standalone Python script"""
    print(f"\nRunning {os.path.basename(script_path)}...")
    print("-" * 60)
    
    result = subprocess.run([sys.executable, script_path])
    
    print("-" * 60)
    print(f"{os.path.basename(script_path)} completed with exit code: {result.returncode}")
    
    return result.returncode

def find_standalone_test_scripts():
    """Find all standalone test scripts in the tests directory"""
    scripts = []
    
    # Get all Python files in tests directory except __init__.py
    all_py_files = [f for f in glob.glob("tests/**/*.py", recursive=True)
                   if os.path.basename(f) != "__init__.py"]
    
    # Run pytest with --collect-only to get all pytest test files
    pytest_files = set()
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "tests/", "--collect-only", "-q"],
            capture_output=True, text=True, check=True
        )
        
        # Parse the output to get test file paths
        for line in result.stdout.strip().split('\n'):
            if line and '::' in line:
                # Extract file path from pytest output format
                file_path = line.split('::')[0]
                if file_path.endswith('.py'):
                    pytest_files.add(file_path)
    except subprocess.CalledProcessError:
        print("Warning: Could not determine pytest test files automatically.")
    
    # Add any Python file that's not a pytest test to standalone scripts
    for file_path in all_py_files:
        if file_path not in pytest_files:
            scripts.append(file_path)
    
    return scripts

def main():
    """Main function to run all tests"""
    print("Running all tests in the project...")
    print("\n" + "=" * 60)
    
    # Run pytest tests first
    pytest_exit_code = run_pytest_tests()
    
    # Find and run standalone test scripts
    standalone_scripts = find_standalone_test_scripts()
    
    if standalone_scripts:
        print("\n" + "=" * 60)
        print(f"Found {len(standalone_scripts)} standalone test scripts:")
        for script in standalone_scripts:
            print(f"  - {os.path.basename(script)}")
        
        script_exit_codes = []
        for script in standalone_scripts:
            exit_code = run_standalone_script(script)
            script_exit_codes.append(exit_code)
        
        # Check if all standalone scripts passed
        all_scripts_passed = all(code == 0 for code in script_exit_codes)
    else:
        print("\nNo standalone test scripts found.")
        all_scripts_passed = True
    
    # Determine overall result
    overall_success = (pytest_exit_code == 0) and all_scripts_passed
    
    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print(f"pytest tests: {'PASSED' if pytest_exit_code == 0 else 'FAILED'}")
    if standalone_scripts:
        print(f"Standalone scripts: {'PASSED' if all_scripts_passed else 'FAILED'}")
    print(f"Overall: {'ALL TESTS PASSED' if overall_success else 'SOME TESTS FAILED'}")
    print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if overall_success else 1)

if __name__ == "__main__":
    main()