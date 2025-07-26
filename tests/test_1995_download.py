#!/usr/bin/env python3
"""
Test script to download all data from 1995 from any agency and validate the results.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path so we can import the main script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_download_test():
    """Run the 1995 download test"""
    print("=" * 60)
    print("TESTING: Download all data from 1995 (any agency)")
    print("=" * 60)
    
    # Clean up any existing test data
    test_data_dir = Path("./test_data_1995")
    if test_data_dir.exists():
        print(f"Cleaning up existing test data directory: {test_data_dir}")
        subprocess.run(["rm", "-rf", str(test_data_dir)], check=True)
    
    # Create test data directory
    test_data_dir.mkdir(exist_ok=True)
    
    # Set environment variables for test
    env = os.environ.copy()
    env['MIRRULATIONS_DESTINATION_PATH'] = str(test_data_dir)
    env['RCLONE_CONFIG_FILE'] = './rclone.conf.example'
    
    print(f"Test data will be downloaded to: {test_data_dir}")
    print("Running command: python mirrulations_downloader.py --year 1995 --noconfirm")
    
    start_time = time.time()
    
    # Run the download command
    try:
        result = subprocess.run([
            "python", "mirrulations_downloader.py", 
            "--year", "1995",
            "--noconfirm"
        ], 
        env=env,
        text=True,
        capture_output=True,
        timeout=600  # 10 minute timeout (year downloads can be larger)
        )
        
        end_time = time.time()
        elapsed_time = end_time - start_time
        
        print(f"Download completed in {elapsed_time:.2f} seconds")
        print(f"Return code: {result.returncode}")
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
            
    except subprocess.TimeoutExpired:
        print("ERROR: Download timed out after 10 minutes")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run download command: {e}")
        return False
    
    # Validate the results
    return validate_1995_results(test_data_dir)

def validate_1995_results(test_data_dir):
    """Validate that the 1995 download results are reasonable"""
    print("\n" + "=" * 60)
    print("VALIDATING: 1995 download results")
    print("=" * 60)
    
    success = True
    
    # Check that both derived-data and raw-data directories exist
    derived_data_dir = test_data_dir / "derived-data"
    raw_data_dir = test_data_dir / "raw-data"
    
    if not derived_data_dir.exists():
        print(f"ERROR: Expected derived-data directory not found: {derived_data_dir}")
        success = False
    else:
        print(f"✓ Found derived-data directory: {derived_data_dir}")
    
    if not raw_data_dir.exists():
        print(f"ERROR: Expected raw-data directory not found: {raw_data_dir}")
        success = False
    else:
        print(f"✓ Found raw-data directory: {raw_data_dir}")
    
    # Find agencies that have 1995 data
    agencies_with_1995_data = set()
    
    if raw_data_dir.exists():
        for agency_dir in raw_data_dir.iterdir():
            if agency_dir.is_dir():
                # Look for dockets with 1995 in the name
                for docket_dir in agency_dir.iterdir():
                    if docket_dir.is_dir() and "-1995-" in docket_dir.name:
                        agencies_with_1995_data.add(agency_dir.name)
                        break
    
    print(f"✓ Found agencies with 1995 data: {sorted(agencies_with_1995_data)}")
    
    if len(agencies_with_1995_data) == 0:
        print("ERROR: No agencies found with 1995 data")
        success = False
    
    # Count total files and validate 1995 pattern
    total_files = 0
    dockets_1995 = set()
    
    for data_type in ["derived-data", "raw-data"]:
        data_dir = test_data_dir / data_type
        if data_dir.exists():
            for agency_dir in data_dir.iterdir():
                if agency_dir.is_dir():
                    for docket_dir in agency_dir.iterdir():
                        if docket_dir.is_dir():
                            # Check if this docket is from 1995
                            if "-1995-" in docket_dir.name:
                                dockets_1995.add(docket_dir.name)
                                # Count files in this docket
                                for file_path in docket_dir.rglob("*"):
                                    if file_path.is_file():
                                        total_files += 1
                            elif "-1995-" not in docket_dir.name:
                                # This shouldn't happen - we should only have 1995 dockets
                                print(f"WARNING: Found non-1995 docket: {docket_dir.name}")
    
    print(f"✓ Found {len(dockets_1995)} dockets from 1995")
    print(f"✓ Found {total_files} total files")
    
    if len(dockets_1995) == 0:
        print("ERROR: No 1995 dockets found")
        success = False
    
    # Show sample dockets
    if len(dockets_1995) > 0:
        sample_dockets = sorted(list(dockets_1995))[:10]
        print(f"  Sample 1995 dockets: {sample_dockets}")
        
        # Validate that all sample dockets actually contain 1995
        for docket in sample_dockets:
            if "-1995-" not in docket:
                print(f"ERROR: Docket {docket} doesn't contain 1995 pattern")
                success = False
    
    # Check for expected file types
    file_extensions = set()
    for file_path in test_data_dir.rglob("*"):
        if file_path.is_file():
            file_extensions.add(file_path.suffix.lower())
    
    print(f"✓ Found file extensions: {sorted(file_extensions)}")
    
    # Calculate total size
    total_size = 0
    if test_data_dir.exists():
        for file_path in test_data_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"✓ Total download size: {total_size_mb:.2f} MB")
    
    # Validate that we have multiple agencies (1995 should have data from various agencies)
    if len(agencies_with_1995_data) < 2:
        print(f"WARNING: Expected multiple agencies for 1995, but only found: {agencies_with_1995_data}")
    
    if success:
        print("\n🎉 1995 download test PASSED!")
    else:
        print("\n❌ 1995 download test FAILED!")
    
    return success

if __name__ == "__main__":
    success = run_download_test()
    sys.exit(0 if success else 1)
