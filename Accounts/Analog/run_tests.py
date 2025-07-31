#!/usr/bin/env python3
"""
Test runner script for Package Manager tests
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type=None, verbose=False, coverage=False, markers=None):
    """Run the test suite with specified options"""
    
    # Base pytest command
    cmd = ["python", "-m", "pytest"]
    
    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")
    
    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    # Add markers filter
    if markers:
        cmd.extend(["-m", markers])
    
    # Add specific test files based on type
    if test_type:
        test_files = {
            "cli": "test_package_manager_cli.py",
            "vscode": "test_package_manager_vscode.py", 
            "integration": "test_project_integration.py",
            "auth": "test_authentication.py",
            "all": "."
        }
        
        if test_type in test_files:
            cmd.append(test_files[test_type])
        else:
            print(f"Unknown test type: {test_type}")
            print(f"Available types: {', '.join(test_files.keys())}")
            return 1
    
    # Run the tests
    print(f"Running command: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    return result.returncode


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run Package Manager tests")
    
    parser.add_argument(
        "--type", "-t",
        choices=["cli", "vscode", "integration", "auth", "all"],
        default="all",
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--coverage", "-c",
        action="store_true", 
        help="Generate coverage report"
    )
    
    parser.add_argument(
        "--markers", "-m",
        help="Run tests with specific markers (e.g., 'not slow')"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Run only quick tests (exclude slow and integration tests)"
    )
    
    args = parser.parse_args()
    
    # Set markers for quick tests
    if args.quick:
        args.markers = "not slow and not integration"
    
    # Run tests
    exit_code = run_tests(
        test_type=args.type,
        verbose=args.verbose,
        coverage=args.coverage,
        markers=args.markers
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()