#!/usr/bin/env python3
"""
Master test runner script to run all download tests and report results.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

def run_test_script(script_name, description):
    """Run a single test script and return success status"""
    print("\n" + "=" * 80)
    print(f"RUNNING: {description}")
    print("=" * 80)
    
    script_path = Path(__file__).parent / script_name
    
    if not script_path.exists():
        print(f"ERROR: Test script not found: {script_path}")
        return False
    
    start_time = time.time()
    
    try:
        # Run the test script
        result = subprocess.run([
            sys.executable, str(script_path)
        ], 
        cwd=Path(__file__).parent.parent,  # Run from project root
        capture_output=True,
        text=True,
        timeout=900  # 15 minute timeout per test
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"\nTest completed in {elapsed_time:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        # Always show the output
        if result.stdout:
            print("\nTest Output:")
            print(result.stdout)
        
        if result.stderr:
            print("\nTest Errors:")
            print(result.stderr)
        
        return result.returncode == 0
        
    except subprocess.TimeoutExpired:
        print(f"ERROR: Test {script_name} timed out after 15 minutes")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run test {script_name}: {e}")
        return False

def main():
    """Run all tests and report overall results"""
    print("=" * 80)
    print("MIRRULATIONS DOWNLOADER - COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print("This test suite will validate the mirrulations_bulk_downloader.py script")
    print("by testing different download patterns and validating results.")
    print()
    print("Tests to run:")
    print("1. Download all AHRQ files")
    print("2. Download all data from 1995 (any agency)")
    print("3. Download specific docket CMS-2025-0050")
    print()
    
    # Ensure we're running from the project root
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    print(f"Running tests from: {project_root}")
    
    # Check prerequisites
    print("\nChecking prerequisites...")
    
    # Check if main script exists
    main_script = project_root / "mirrulations_bulk_downloader.py"
    if not main_script.exists():
        print(f"ERROR: Main script not found: {main_script}")
        return False
    print("✓ Main script found")
    
    # Check if rclone config exists
    rclone_config = project_root / "rclone.conf.example"
    if not rclone_config.exists():
        print(f"ERROR: Rclone config not found: {rclone_config}")
        return False
    print("✓ Rclone config found")
    
    # Check if we're in a virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✓ Running in virtual environment")
    else:
        print("WARNING: Not running in virtual environment - dependencies may not be available")
    
    print("\nStarting test execution...")
    
    # Define tests to run
    tests = [
        ("test_ahrq_download.py", "Download all AHRQ files"),
        ("test_1995_download.py", "Download all data from 1995 (any agency)"),
        ("test_cms_docket_download.py", "Download specific docket CMS-2025-0050")
    ]
    
    # Track results
    results = {}
    start_time = time.time()
    
    # Run each test
    for script_name, description in tests:
        success = run_test_script(script_name, description)
        results[description] = success
    
    end_time = time.time()
    total_elapsed = end_time - start_time
    
    # Report final results
    print("\n" + "=" * 80)
    print("FINAL TEST RESULTS")
    print("=" * 80)
    
    passed = 0
    failed = 0
    
    for description, success in results.items():
        status = "PASSED" if success else "FAILED"
        emoji = "🎉" if success else "❌"
        print(f"{emoji} {description}: {status}")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    print(f"\nSummary: {passed} passed, {failed} failed")
    print(f"Total execution time: {total_elapsed:.2f} seconds")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! The mirrulations downloader is working correctly.")
        return True
    else:
        print(f"\n❌ {failed} TEST(S) FAILED! Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
