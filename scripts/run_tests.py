#!/usr/bin/env python3
"""
Master Test Runner for File Search Engine

This script discovers and runs all unit tests in the tests directory.
It provides detailed output and summary statistics.

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py --quick      # Run quick tests only (skip slow model tests)
    python run_tests.py --verbose    # Extra verbose output
    python run_tests.py --coverage   # Run with coverage report (requires pytest-cov)
"""

import unittest
import sys
import os
import argparse
import time

# Add the workspace directory (project root) to the Python path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a colored header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")

def run_quick_tests():
    """Run only quick unit tests (skip slow model loading tests)."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test modules except slow ones
    quick_modules = [
        'backend.tests.test_api',
        'backend.tests.test_database',
        'backend.tests.test_file_processing',
        'backend.tests.test_indexing',
        'backend.tests.test_search',
        'backend.tests.test_model_manager',
        'backend.tests.test_benchmarks',
        'backend.tests.test_config_and_edge_cases',
    ]
    
    for module in quick_modules:
        try:
            suite.addTests(loader.loadTestsFromName(module))
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not load {module}: {e}{Colors.ENDC}")
    
    return suite

def run_all_tests():
    """Run all tests including slow model comparison tests."""
    loader = unittest.TestLoader()
    tests_dir = os.path.join(PROJECT_ROOT, 'backend', 'tests')
    suite = loader.discover(tests_dir, pattern='test_*.py', top_level_dir=PROJECT_ROOT)
    return suite

def main():
    parser = argparse.ArgumentParser(description='Run File Search Engine tests')
    parser.add_argument('--quick', action='store_true', 
                       help='Run quick tests only (skip slow model tests)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Extra verbose output')
    parser.add_argument('--coverage', action='store_true',
                       help='Run with coverage (requires pytest-cov)')
    parser.add_argument('--pattern', '-p', type=str, default='test_*.py',
                       help='Test file pattern to match')
    args = parser.parse_args()
    
    print_header("FILE SEARCH ENGINE TEST SUITE")
    
    start_time = time.time()
    
    # Check for pytest with coverage
    if args.coverage:
        try:
            import pytest
            print("Running with pytest-cov...")
            sys.exit(pytest.main([
                os.path.join(PROJECT_ROOT, 'backend', 'tests'),
                '-v',
                f'--cov={os.path.join(PROJECT_ROOT, "backend")}',
                '--cov-report=html',
                '--cov-report=term-missing'
            ]))
        except ImportError:
            print(f"{Colors.YELLOW}pytest-cov not installed. Running with unittest...{Colors.ENDC}")
    
    # Select test suite
    if args.quick:
        print(f"{Colors.YELLOW}Running QUICK tests (skipping slow model tests)...{Colors.ENDC}\n")
        suite = run_quick_tests()
    else:
        print(f"Running ALL tests...\n")
        suite = run_all_tests()
    
    # Create test runner
    verbosity = 2 if args.verbose else 1
    runner = unittest.TextTestRunner(verbosity=verbosity, buffer=True)
    
    # Run tests
    result = runner.run(suite)
    
    # Calculate duration
    duration = time.time() - start_time
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_tests = result.testsRun
    failures = len(result.failures)
    errors = len(result.errors)
    skipped = len(result.skipped)
    passed = total_tests - failures - errors - skipped
    
    print(f"  Total Tests:  {total_tests}")
    print(f"  {Colors.GREEN}Passed:       {passed}{Colors.ENDC}")
    if failures > 0:
        print(f"  {Colors.RED}Failed:       {failures}{Colors.ENDC}")
    else:
        print(f"  Failed:       {failures}")
    if errors > 0:
        print(f"  {Colors.RED}Errors:       {errors}{Colors.ENDC}")
    else:
        print(f"  Errors:       {errors}")
    if skipped > 0:
        print(f"  {Colors.YELLOW}Skipped:      {skipped}{Colors.ENDC}")
    else:
        print(f"  Skipped:      {skipped}")
    print(f"\n  Duration:     {duration:.2f}s")
    
    # Print failures details
    if result.failures:
        print(f"\n{Colors.RED}{Colors.BOLD}FAILURES:{Colors.ENDC}")
        for test, traceback in result.failures:
            print(f"\n  ✗ {test}")
            print(f"    {traceback.split(chr(10))[0]}")
    
    # Print errors details
    if result.errors:
        print(f"\n{Colors.RED}{Colors.BOLD}ERRORS:{Colors.ENDC}")
        for test, traceback in result.errors:
            print(f"\n  ✗ {test}")
            print(f"    {traceback.split(chr(10))[0]}")
    
    # Final status
    if failures == 0 and errors == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.ENDC}\n")
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.ENDC}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())