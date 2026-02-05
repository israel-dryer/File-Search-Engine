#!/usr/bin/env python3
"""
Master Test Runner for File Search Engine

This script discovers and runs all unit tests in the tests directory.
It provides detailed output with a LIVE PROGRESS BAR and summary statistics.

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
    CYAN = '\033[96m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    """Print a colored header."""
    print(f"\n{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{text:^60}{Colors.ENDC}")
    print(f"{Colors.BLUE}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


class ProgressTestResult(unittest.TestResult):
    """Custom TestResult that shows a progress bar and current test name."""
    
    def __init__(self, total_tests, stream=sys.stdout):
        super().__init__()
        self.total_tests = total_tests
        self.current_test = 0
        self.stream = stream
        self.passed = 0
        self.start_time = time.time()
        
    def _print_progress(self, status_char, test_name, color=Colors.GREEN):
        """Print progress bar with current test info."""
        self.current_test += 1
        percentage = (self.current_test / self.total_tests) * 100
        bar_width = 30
        filled = int(bar_width * self.current_test / self.total_tests)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # Get short test name
        short_name = str(test_name).split(' ')[0]
        if len(short_name) > 40:
            short_name = short_name[:37] + '...'
        
        elapsed = time.time() - self.start_time
        
        # Print progress line
        self.stream.write(f"\r{Colors.CYAN}[{bar}] {percentage:5.1f}%{Colors.ENDC} ")
        self.stream.write(f"({self.current_test}/{self.total_tests}) ")
        self.stream.write(f"{color}{status_char}{Colors.ENDC} ")
        self.stream.write(f"{short_name:<45} ")
        self.stream.write(f"[{elapsed:.1f}s]")
        self.stream.write(" " * 10)  # Clear any leftover chars
        self.stream.write("\n")
        self.stream.flush()
        
    def startTest(self, test):
        super().startTest(test)
        
    def addSuccess(self, test):
        super().addSuccess(test)
        self.passed += 1
        self._print_progress('✓', test, Colors.GREEN)
        
    def addFailure(self, test, err):
        super().addFailure(test, err)
        self._print_progress('✗', test, Colors.RED)
        
    def addError(self, test, err):
        super().addError(test, err)
        self._print_progress('E', test, Colors.RED)
        
    def addSkip(self, test, reason):
        super().addSkip(test, reason)
        self._print_progress('S', test, Colors.YELLOW)


class ProgressTestRunner:
    """Test runner that uses ProgressTestResult for visual progress."""
    
    def __init__(self, stream=sys.stdout):
        self.stream = stream
        
    def run(self, suite):
        """Run the test suite with progress tracking."""
        # Count total tests
        total_tests = suite.countTestCases()
        print(f"{Colors.CYAN}Found {total_tests} tests to run...{Colors.ENDC}\n")
        
        # Create result with progress tracking
        result = ProgressTestResult(total_tests, self.stream)
        
        # Run tests
        suite(result)
        
        return result


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
        'backend.tests.test_security',
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
    
    # Create test runner with progress bar
    runner = ProgressTestRunner()
    
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
    passed = result.passed
    
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
            # Print first few lines of traceback
            lines = traceback.split('\n')
            for line in lines[:5]:
                print(f"    {line}")
    
    # Print errors details
    if result.errors:
        print(f"\n{Colors.RED}{Colors.BOLD}ERRORS:{Colors.ENDC}")
        for test, traceback in result.errors:
            print(f"\n  ✗ {test}")
            lines = traceback.split('\n')
            for line in lines[:5]:
                print(f"    {line}")
    
    # Final status
    if failures == 0 and errors == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED!{Colors.ENDC}\n")
        
        # Cleanup test data from production database
        try:
            from backend import database
            database.cleanup_test_data()
        except Exception as e:
            print(f"{Colors.YELLOW}Warning: Could not cleanup test data: {e}{Colors.ENDC}")
        
        return 0
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.ENDC}\n")
        return 1


if __name__ == '__main__':
    sys.exit(main())