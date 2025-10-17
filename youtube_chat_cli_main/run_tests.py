#!/usr/bin/env python
"""
JAEGIS NexusSync - Test Runner

Comprehensive test runner with multiple test suites and reporting options.
"""

import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, description):
    """Run a command and print results."""
    print(f"\n{'='*70}")
    print(f"  {description}")
    print(f"{'='*70}\n")
    
    result = subprocess.run(cmd, shell=True)
    
    if result.returncode != 0:
        print(f"\n❌ {description} FAILED")
        return False
    else:
        print(f"\n✅ {description} PASSED")
        return True


def run_unit_tests(verbose=False):
    """Run unit tests only."""
    cmd = "pytest tests/ -m 'not integration' -v" if verbose else "pytest tests/ -m 'not integration'"
    return run_command(cmd, "Unit Tests")


def run_integration_tests(verbose=False):
    """Run integration tests only."""
    cmd = "pytest tests/ -m integration -v" if verbose else "pytest tests/ -m integration"
    return run_command(cmd, "Integration Tests")


def run_all_tests(verbose=False):
    """Run all tests."""
    cmd = "pytest tests/ -v" if verbose else "pytest tests/"
    return run_command(cmd, "All Tests")


def run_coverage_tests():
    """Run tests with coverage report."""
    cmd = "pytest tests/ --cov=youtube_chat_cli_main --cov-report=term-missing --cov-report=html"
    return run_command(cmd, "Tests with Coverage")


def run_specific_test(test_path, verbose=False):
    """Run a specific test file or test."""
    cmd = f"pytest {test_path} -v" if verbose else f"pytest {test_path}"
    return run_command(cmd, f"Specific Test: {test_path}")


def run_linting():
    """Run code linting."""
    success = True
    
    # Flake8
    if not run_command("flake8 youtube_chat_cli_main/ --max-line-length=120 --extend-ignore=E203,W503", "Flake8 Linting"):
        success = False
    
    # Black check
    if not run_command("black youtube_chat_cli_main/ --check", "Black Formatting Check"):
        success = False
    
    return success


def run_type_checking():
    """Run type checking with mypy."""
    return run_command("mypy youtube_chat_cli_main/ --ignore-missing-imports", "Type Checking (mypy)")


def run_full_ci():
    """Run full CI pipeline (linting, type checking, all tests with coverage)."""
    print("\n" + "="*70)
    print("  FULL CI PIPELINE")
    print("="*70)
    
    success = True
    
    # Linting
    if not run_linting():
        success = False
        print("\n⚠️  Linting failed, but continuing...")
    
    # Type checking
    if not run_type_checking():
        success = False
        print("\n⚠️  Type checking failed, but continuing...")
    
    # Tests with coverage
    if not run_coverage_tests():
        success = False
    
    if success:
        print("\n" + "="*70)
        print("  ✅ FULL CI PIPELINE PASSED")
        print("="*70)
    else:
        print("\n" + "="*70)
        print("  ❌ FULL CI PIPELINE FAILED")
        print("="*70)
    
    return success


def main():
    """Main test runner."""
    parser = argparse.ArgumentParser(
        description="JAEGIS NexusSync Test Runner",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run all tests
  python run_tests.py --all
  
  # Run unit tests only
  python run_tests.py --unit
  
  # Run integration tests only
  python run_tests.py --integration
  
  # Run tests with coverage
  python run_tests.py --coverage
  
  # Run specific test file
  python run_tests.py --test tests/test_rag_engine.py
  
  # Run full CI pipeline
  python run_tests.py --ci
  
  # Run linting only
  python run_tests.py --lint
  
  # Run type checking only
  python run_tests.py --type-check
        """
    )
    
    parser.add_argument('--all', action='store_true', help='Run all tests')
    parser.add_argument('--unit', action='store_true', help='Run unit tests only')
    parser.add_argument('--integration', action='store_true', help='Run integration tests only')
    parser.add_argument('--coverage', action='store_true', help='Run tests with coverage report')
    parser.add_argument('--test', type=str, help='Run specific test file or test')
    parser.add_argument('--lint', action='store_true', help='Run linting only')
    parser.add_argument('--type-check', action='store_true', help='Run type checking only')
    parser.add_argument('--ci', action='store_true', help='Run full CI pipeline')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    # If no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return 0
    
    success = True
    
    # Run requested tests
    if args.ci:
        success = run_full_ci()
    elif args.lint:
        success = run_linting()
    elif args.type_check:
        success = run_type_checking()
    elif args.coverage:
        success = run_coverage_tests()
    elif args.unit:
        success = run_unit_tests(args.verbose)
    elif args.integration:
        success = run_integration_tests(args.verbose)
    elif args.test:
        success = run_specific_test(args.test, args.verbose)
    elif args.all:
        success = run_all_tests(args.verbose)
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())

