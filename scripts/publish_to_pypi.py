#!/usr/bin/env python3
"""
Script to build and publish YouTube Chat CLI to PyPI.

This script handles:
1. Package validation
2. Building source distribution and wheel
3. Publishing to PyPI with secure token management
4. Cleanup of build artifacts

Usage:
    python scripts/publish_to_pypi.py --test    # Publish to TestPyPI
    python scripts/publish_to_pypi.py           # Publish to PyPI
"""

import os
import sys
import subprocess
import shutil
import argparse
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

try:
    from youtube_chat_cli import __version__
except ImportError:
    print("❌ Error: Could not import youtube_chat_cli package")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)


def run_command(cmd, check=True):
    """Run a shell command and return the result."""
    print(f"🔧 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    
    if check and result.returncode != 0:
        print(f"❌ Command failed with return code {result.returncode}")
        sys.exit(1)
    
    return result


def clean_build_artifacts():
    """Clean up build artifacts."""
    print("🧹 Cleaning build artifacts...")
    
    artifacts = ["build", "dist", "*.egg-info"]
    for pattern in artifacts:
        for path in Path(".").glob(pattern):
            if path.is_dir():
                shutil.rmtree(path)
                print(f"   Removed directory: {path}")
            else:
                path.unlink()
                print(f"   Removed file: {path}")


def validate_package():
    """Validate the package configuration."""
    print("✅ Validating package configuration...")
    
    # Check required files exist
    required_files = ["README.md", "LICENSE", "pyproject.toml", "src/youtube_chat_cli/__init__.py"]
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Required file missing: {file_path}")
            return False
    
    # Check version consistency
    print(f"📦 Package version: {__version__}")
    
    # Validate pyproject.toml
    try:
        import tomllib
        with open("pyproject.toml", "rb") as f:
            config = tomllib.load(f)
        
        if config["project"]["version"] != __version__:
            print(f"❌ Version mismatch in pyproject.toml: {config['project']['version']} != {__version__}")
            return False
            
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        return False
    
    print("✅ Package validation passed")
    return True


def build_package():
    """Build the package."""
    print("🔨 Building package...")
    
    # Install build dependencies
    run_command("pip install --upgrade build twine")
    
    # Build the package
    run_command("python -m build")
    
    # Validate the built package
    print("🔍 Validating built package...")
    run_command("python -m twine check dist/*")
    
    print("✅ Package built successfully")


def publish_package(test_pypi=False):
    """Publish the package to PyPI."""
    if test_pypi:
        print("🚀 Publishing to TestPyPI...")
        repository = "--repository testpypi"
        url = "https://test.pypi.org/project/youtube-chat-cli/"
    else:
        print("🚀 Publishing to PyPI...")
        repository = ""
        url = "https://pypi.org/project/youtube-chat-cli/"
    
    # Check for PyPI token
    token_env = "PYPI_TEST_TOKEN" if test_pypi else "PYPI_TOKEN"
    if not os.getenv(token_env):
        print(f"❌ {token_env} environment variable not set")
        print(f"Please set your PyPI token:")
        print(f"export {token_env}='your-token-here'")
        return False
    
    # Upload to PyPI
    cmd = f"python -m twine upload {repository} dist/*"
    result = run_command(cmd, check=False)
    
    if result.returncode == 0:
        print(f"✅ Package published successfully!")
        print(f"🔗 View at: {url}")
        return True
    else:
        print("❌ Failed to publish package")
        return False


def main():
    parser = argparse.ArgumentParser(description="Build and publish YouTube Chat CLI to PyPI")
    parser.add_argument("--test", action="store_true", help="Publish to TestPyPI instead of PyPI")
    parser.add_argument("--skip-validation", action="store_true", help="Skip package validation")
    parser.add_argument("--skip-build", action="store_true", help="Skip building (use existing dist/)")
    parser.add_argument("--clean-only", action="store_true", help="Only clean build artifacts")
    
    args = parser.parse_args()
    
    print("🎙️ YouTube Chat CLI - PyPI Publisher")
    print("=" * 50)
    
    if args.clean_only:
        clean_build_artifacts()
        return
    
    # Step 1: Clean previous builds
    clean_build_artifacts()
    
    # Step 2: Validate package
    if not args.skip_validation:
        if not validate_package():
            sys.exit(1)
    
    # Step 3: Build package
    if not args.skip_build:
        build_package()
    
    # Step 4: Publish package
    success = publish_package(test_pypi=args.test)
    
    if success:
        print("\n🎉 Publication completed successfully!")
        print("\nNext steps:")
        print("1. Test the installation: pip install youtube-chat-cli")
        print("2. Verify the package works: youtube-chat --help")
        print("3. Update the GitHub release with the new version")
    else:
        print("\n❌ Publication failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
