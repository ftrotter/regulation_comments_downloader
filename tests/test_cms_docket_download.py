#!/usr/bin/env python3
"""
Test script to download the specific docket CMS-2025-0050 and validate the results.
"""

import os
import sys
import subprocess
import time
from pathlib import Path

# Add parent directory to path so we can import the main script
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def run_download_test():
    """Run the CMS-2025-0050 docket download test"""
    print("=" * 60)
    print("TESTING: Download specific docket CMS-2025-0050")
    print("=" * 60)
    
    # Clean up any existing test data
    test_data_dir = Path("./test_data_cms_docket")
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
    print("Running command: python mirrulations_bulk_downloader.py --docket CMS-2025-0050")
    
    start_time = time.time()
    
    # Run the download command
    try:
        result = subprocess.run([
            "python", "mirrulations_bulk_downloader.py",
            "--docket", "CMS-2025-0050",
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
    return validate_cms_docket_results(test_data_dir)

def validate_cms_docket_results(test_data_dir):
    """Validate that the CMS-2025-0050 docket download results are reasonable"""
    print("\n" + "=" * 60)
    print("VALIDATING: CMS-2025-0050 docket download results")
    print("=" * 60)
    
    success = True
    target_docket = "CMS-2025-0050"
    
    # Check that both derived-data and raw-data directories exist
    derived_data_dir = test_data_dir / "derived-data" / "CMS" / target_docket
    raw_data_dir = test_data_dir / "raw-data" / "CMS" / target_docket
    
    if not derived_data_dir.exists():
        print(f"WARNING: Expected derived-data directory not found: {derived_data_dir}")
        # This might be OK if there's no derived data for this docket
    else:
        print(f"✓ Found derived-data directory: {derived_data_dir}")
    
    if not raw_data_dir.exists():
        print(f"ERROR: Expected raw-data directory not found: {raw_data_dir}")
        success = False
    else:
        print(f"✓ Found raw-data directory: {raw_data_dir}")
    
    # Check that we ONLY have the CMS agency and the specific docket
    cms_agency_dir_derived = test_data_dir / "derived-data" / "CMS"
    cms_agency_dir_raw = test_data_dir / "raw-data" / "CMS"
    
    # Check raw-data structure
    if raw_data_dir.exists():
        # Verify that we only have the target docket
        raw_dockets = []
        if cms_agency_dir_raw.exists():
            for item in cms_agency_dir_raw.iterdir():
                if item.is_dir():
                    raw_dockets.append(item.name)
        
        print(f"✓ Found dockets in raw-data/CMS: {raw_dockets}")
        
        if target_docket not in raw_dockets:
            print(f"ERROR: Target docket {target_docket} not found in raw-data")
            success = False
        
        # Should only have the target docket
        if len(raw_dockets) > 1:
            print(f"WARNING: Expected only {target_docket}, but found: {raw_dockets}")
        elif len(raw_dockets) == 1 and raw_dockets[0] == target_docket:
            print(f"✓ Correctly found only target docket: {target_docket}")
    
    # Check derived-data structure (if it exists)
    if derived_data_dir.exists():
        derived_dockets = []
        if cms_agency_dir_derived.exists():
            for item in cms_agency_dir_derived.iterdir():
                if item.is_dir():
                    derived_dockets.append(item.name)
        
        print(f"✓ Found dockets in derived-data/CMS: {derived_dockets}")
        
        if target_docket in derived_dockets and len(derived_dockets) == 1:
            print(f"✓ Correctly found only target docket in derived-data: {target_docket}")
    
    # Check that we don't have any other agencies
    other_agencies_raw = []
    other_agencies_derived = []
    
    raw_data_root = test_data_dir / "raw-data"
    if raw_data_root.exists():
        for item in raw_data_root.iterdir():
            if item.is_dir() and item.name != "CMS":
                other_agencies_raw.append(item.name)
    
    derived_data_root = test_data_dir / "derived-data"
    if derived_data_root.exists():
        for item in derived_data_root.iterdir():
            if item.is_dir() and item.name != "CMS":
                other_agencies_derived.append(item.name)
    
    if other_agencies_raw:
        print(f"ERROR: Found unexpected agencies in raw-data: {other_agencies_raw}")
        success = False
    else:
        print("✓ Correctly found only CMS agency in raw-data")
    
    if other_agencies_derived:
        print(f"ERROR: Found unexpected agencies in derived-data: {other_agencies_derived}")
        success = False
    else:
        print("✓ Correctly found only CMS agency (or no agencies) in derived-data")
    
    # Count files in the target docket
    total_files = 0
    file_extensions = set()
    
    for data_type_dir in [derived_data_dir, raw_data_dir]:
        if data_type_dir.exists():
            for file_path in data_type_dir.rglob("*"):
                if file_path.is_file():
                    total_files += 1
                    file_extensions.add(file_path.suffix.lower())
    
    print(f"✓ Found {total_files} total files in docket {target_docket}")
    print(f"✓ Found file extensions: {sorted(file_extensions)}")
    
    if total_files == 0:
        print("ERROR: No files found in the target docket")
        success = False
    
    # Check for expected file types
    expected_extensions = {'.json', '.htm'}
    found_expected = expected_extensions.intersection(file_extensions)
    if not found_expected:
        print(f"WARNING: Expected to find files with extensions {expected_extensions}")
        print(f"But only found: {sorted(file_extensions)}")
    
    # Calculate total size
    total_size = 0
    if test_data_dir.exists():
        for file_path in test_data_dir.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size
    
    total_size_mb = total_size / (1024 * 1024)
    print(f"✓ Total download size: {total_size_mb:.2f} MB")
    
    # Verify docket naming pattern
    if "-2025-" not in target_docket:
        print(f"ERROR: Target docket {target_docket} doesn't follow expected pattern")
        success = False
    else:
        print(f"✓ Docket {target_docket} follows expected naming pattern")
    
    # List some sample files to verify content
    sample_files = []
    for file_path in test_data_dir.rglob("*"):
        if file_path.is_file():
            sample_files.append(str(file_path.relative_to(test_data_dir)))
            if len(sample_files) >= 5:
                break
    
    if sample_files:
        print(f"✓ Sample files downloaded:")
        for file_path in sample_files:
            print(f"  - {file_path}")
    
    if success:
        print(f"\n🎉 CMS-2025-0050 docket download test PASSED!")
    else:
        print(f"\n❌ CMS-2025-0050 docket download test FAILED!")
    
    return success

if __name__ == "__main__":
    success = run_download_test()
    sys.exit(0 if success else 1)
