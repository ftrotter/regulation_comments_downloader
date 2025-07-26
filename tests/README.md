# Mirrulations Downloader Test Suite

This directory contains comprehensive tests for the mirrulations_downloader.py script. The tests validate different download patterns and ensure the script works correctly with the new folder structure.

## Test Scripts

### 1. `test_ahrq_download.py`
**Purpose**: Download all AHRQ files and validate results
- Downloads all files for the AHRQ agency
- Validates both `derived-data/AHRQ/` and `raw-data/AHRQ/` directories
- Checks for expected file types and docket patterns
- Verifies AHRQ-specific docket naming conventions

### 2. `test_2007_download.py`
**Purpose**: Download all data from 2007 (any agency) and validate results
- Downloads all files from 2007 across all agencies
- Validates that only dockets with "-2007-" pattern are downloaded
- Checks for multiple agencies having 2007 data
- Ensures proper year filtering functionality

### 3. `test_cms_docket_download.py`
**Purpose**: Download specific docket CMS-2025-0050 and validate results
- Downloads only the specified CMS-2025-0050 docket
- Validates that only CMS agency data is downloaded
- Ensures only the target docket is present
- Verifies docket-specific filtering functionality

### 4. `run_all_tests.py`
**Purpose**: Master test runner that executes all tests and reports results
- Runs all individual test scripts
- Provides comprehensive reporting
- Checks prerequisites before running tests
- Reports overall pass/fail status

## Running the Tests

### Prerequisites
1. Ensure you're in the project root directory
2. Activate your virtual environment: `source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Ensure `rclone.conf.example` is properly configured

### Run All Tests
```bash
python tests/run_all_tests.py
```

### Run Individual Tests
```bash
# Test AHRQ download
python tests/test_ahrq_download.py

# Test 2007 data download
python tests/test_2007_download.py

# Test specific docket download
python tests/test_cms_docket_download.py
```

## Test Data Directories

Each test creates its own isolated test data directory:
- `test_data_ahrq/` - AHRQ test data
- `test_data_2007/` - 2007 test data
- `test_data_cms_docket/` - CMS docket test data

These directories are automatically cleaned up before each test run.

## What the Tests Validate

### Folder Structure
- Correct creation of `derived-data/` and `raw-data/` directories
- Proper agency subdirectories
- Correct docket organization

### File Filtering
- Agency-specific filtering works correctly
- Year-based filtering works correctly
- Docket-specific filtering works correctly
- File type filtering (when using `--textonly`)

### Data Integrity
- Files are actually downloaded
- File counts are reasonable
- File extensions match expectations
- Directory structure matches the new mirrulations format

### Pattern Matching
- Include patterns are generated correctly
- rclone commands are constructed properly
- Only expected data is downloaded (no extra agencies/years/dockets)

## Expected Results

### AHRQ Test
- Should download files from multiple AHRQ dockets across various years
- Should include both derived-data and raw-data
- Should contain `.json`, `.htm`, and other file types
- Should only contain AHRQ agency data

### 2007 Test
- Should download files from multiple agencies that have 2007 data
- Should only contain dockets with "-2007-" in the name
- Should include agencies like AHRQ, CMS, EPA, etc. (depending on what's available)
- Should demonstrate year filtering across agencies

### CMS Docket Test
- Should download only CMS-2025-0050 docket
- Should only contain CMS agency data
- Should only contain the specified docket
- Should demonstrate precise docket filtering

## Troubleshooting

### Common Issues

1. **rclone connection errors**: Ensure `rclone.conf.example` is properly configured
2. **Permission errors**: Make sure test scripts are executable (`chmod +x tests/*.py`)
3. **Timeout errors**: Some downloads may take longer; adjust timeout values if needed
4. **Missing dependencies**: Ensure virtual environment is activated and dependencies installed

### Test Failures

If tests fail, check:
1. Network connectivity to the mirrulations S3 bucket
2. rclone configuration is correct
3. Environment variables are set properly
4. Virtual environment has required packages

### Debug Mode

For more detailed output, you can run individual tests and examine their output directly. Each test provides comprehensive logging of what it's doing and what it finds.

## Test Development

### Adding New Tests

To add a new test:
1. Create a new test script in the `tests/` directory
2. Follow the pattern of existing tests
3. Add the new test to `run_all_tests.py`
4. Update this README

### Test Structure

Each test should:
1. Clean up any existing test data
2. Set up isolated test environment
3. Run the download command
4. Validate the results comprehensively
5. Report clear pass/fail status
6. Clean up after itself

## Performance Notes

- AHRQ test: ~10-30 seconds (depending on data size)
- 2007 test: ~1-5 minutes (larger dataset)
- CMS docket test: ~10-30 seconds (single docket)
- Total test suite: ~2-10 minutes

Times may vary based on network speed and data availability.
