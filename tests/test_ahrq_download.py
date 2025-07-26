#!/usr/bin/env python3
"""
Test script to download all AHRQ files and validate the results.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path so we can import the main script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_download_test():
    """Run the AHRQ download test"""
    print("=" * 60)
    print("TESTING: Download all AHRQ files")
    print("=" * 60)
    
    # Clean up any existing test data
    test_data_dir = Path("./test_data_ahrq")
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
    print("Running command: python mirrulations_downloader.py --agency AHRQ")
    
    start_time = time.time()
    
    # Run the download command
    try:
        result = subprocess.run([
            "python", "mirrulations_downloader.py", 
            "--agency", "AHRQ",
            "--noconfirm"
        ], 
        env=env,
        text=True,
        capture_output=True,
        timeout=300  # 5 minute timeout
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
        print("ERROR: Download timed out after 5 minutes")
        return False
    except Exception as e:
        print(f"ERROR: Failed to run download command: {e}")
        return False
    
    # Validate the results
    return validate_ahrq_results(test_data_dir)

def validate_ahrq_results(test_data_dir):
    """Validate that the AHRQ download results are reasonable"""
    print("\n" + "=" * 60)
    print("VALIDATING: AHRQ download results")
    print("=" * 60)
    
    success = True
    
    # Check that both derived-data and raw-data directories exist
    derived_data_dir = test_data_dir / "derived-data" / "AHRQ"
    raw_data_dir = test_data_dir / "raw-data" / "AHRQ"
    
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
    
    # Count files in each directory
    if derived_data_dir.exists():
        derived_files = list(derived_data_dir.rglob("*"))
        derived_file_count = len([f for f in derived_files if f.is_file()])
        print(f"✓ Found {derived_file_count} files in derived-data/AHRQ")
        
        if derived_file_count == 0:
            print("WARNING: No files found in derived-data/AHRQ")
            success = False
    
    if raw_data_dir.exists():
        raw_files = list(raw_data_dir.rglob("*"))
        raw_file_count = len([f for f in raw_files if f.is_file()])
        print(f"✓ Found {raw_file_count} files in raw-data/AHRQ")
        
        if raw_file_count == 0:
            print("ERROR: No files found in raw-data/AHRQ")
            success = False
    
    # Check for expected file types (should include all file types, not just text)
    if raw_data_dir.exists():
        file_extensions = set()
        for file_path in raw_data_dir.rglob("*"):
            if file_path.is_file():
                file_extensions.add(file_path.suffix.lower())
        
        print(f"✓ Found file extensions: {sorted(file_extensions)}")
        
        # Should have various file types since we're not using --textonly
        expected_extensions = {'.json', '.htm'}
        found_expected = expected_extensions.intersection(file_extensions)
        if not found_expected:
            print(f"WARNING: Expected to find files with extensions {expected_extensions}")
            print(f"But only found: {sorted(file_extensions)}")
    
    # Check for AHRQ-specific docket patterns
    if raw_data_dir.exists():
        ahrq_dockets = set()
        for docket_dir in raw_data_dir.iterdir():
            if docket_dir.is_dir() and docket_dir.name.startswith("AHRQ-"):
                ahrq_dockets.add(docket_dir.name)
        
        print(f"✓ Found {len(ahrq_dockets)} AHRQ dockets")
        if len(ahrq_dockets) > 0:
            print(f"  Sample dockets: {sorted(list(ahrq_dockets))[:5]}")
        else:
            print("ERROR: No AHRQ dockets found")
            success = False
    
    # Calculate total size
    total_size = 0
    if test_data_dir.exists():
        for file_path in test_data_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"✓ Total download size: {total_size_mb:.2f} MB")
    
    if success:
        print("\n🎉 AHRQ download test PASSED!")
    else:
        print("\n❌ AHRQ download test FAILED!")
    
    return success

if __name__ == "__main__":
    success = run_download_test()
    sys.exit(0 if success else 1)
