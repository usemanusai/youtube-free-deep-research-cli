#!/usr/bin/env python3
"""
Package validation script for YouTube Chat CLI.

This script validates the package structure and configuration
before publishing to PyPI.
"""

import os
import sys
import subprocess
from pathlib import Path

def check_file_exists(file_path, description):
    """Check if a required file exists."""
    if Path(file_path).exists():
        print(f"✅ {description}: {file_path}")
        return True
    else:
        print(f"❌ {description} missing: {file_path}")
        return False

def check_version_consistency():
    """Check version consistency across files."""
    print("\n📋 Checking version consistency...")
    
    versions = {}
    
    # Check pyproject.toml
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('version = '):
                    versions['pyproject.toml'] = line.split('"')[1]
                    break
    except Exception as e:
        print(f"❌ Error reading pyproject.toml: {e}")
        return False
    
    # Check setup.py
    try:
        with open("setup.py", "r") as f:
            content = f.read()
            for line in content.split('\n'):
                if 'version=' in line and '"' in line:
                    versions['setup.py'] = line.split('"')[1]
                    break
    except Exception as e:
        print(f"❌ Error reading setup.py: {e}")
        return False
    
    # Check __init__.py
    try:
        with open("src/youtube_chat_cli/__init__.py", "r") as f:
            content = f.read()
            for line in content.split('\n'):
                if line.strip().startswith('__version__ = '):
                    versions['__init__.py'] = line.split('"')[1]
                    break
    except Exception as e:
        print(f"❌ Error reading __init__.py: {e}")
        return False
    
    # Check consistency
    if len(set(versions.values())) == 1:
        version = list(versions.values())[0]
        print(f"✅ Version consistent across all files: {version}")
        return True
    else:
        print("❌ Version inconsistency found:")
        for file, version in versions.items():
            print(f"   {file}: {version}")
        return False

def check_package_structure():
    """Check package structure."""
    print("\n📁 Checking package structure...")
    
    required_files = [
        ("README.md", "README file"),
        ("LICENSE", "License file"),
        ("pyproject.toml", "Modern Python packaging config"),
        ("setup.py", "Legacy setuptools config"),
        ("MANIFEST.in", "File inclusion rules"),
        ("src/youtube_chat_cli/__init__.py", "Package init file"),
        ("src/youtube_chat_cli/cli/main.py", "CLI entry point"),
    ]
    
    all_exist = True
    for file_path, description in required_files:
        if not check_file_exists(file_path, description):
            all_exist = False
    
    return all_exist

def check_entry_points():
    """Check entry points configuration."""
    print("\n🔗 Checking entry points...")
    
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            if 'youtube-chat = "youtube_chat_cli.cli.main:main"' in content:
                print("✅ Entry point 'youtube-chat' configured")
            else:
                print("❌ Entry point 'youtube-chat' not found")
                return False
                
            if 'youtube-chat-cli = "youtube_chat_cli.cli.main:main"' in content:
                print("✅ Entry point 'youtube-chat-cli' configured")
            else:
                print("❌ Entry point 'youtube-chat-cli' not found")
                return False
        
        return True
    except Exception as e:
        print(f"❌ Error checking entry points: {e}")
        return False

def check_dependencies():
    """Check dependencies configuration."""
    print("\n📦 Checking dependencies...")
    
    try:
        with open("pyproject.toml", "r") as f:
            content = f.read()
            
        # Check for essential dependencies
        essential_deps = [
            "click>=8.0.0",
            "python-dotenv>=1.0.0",
            "requests>=2.25.0",
            "rich>=13.0.0"
        ]
        
        missing_deps = []
        for dep in essential_deps:
            if dep.split(">=")[0] not in content:
                missing_deps.append(dep)
        
        if missing_deps:
            print("❌ Missing essential dependencies:")
            for dep in missing_deps:
                print(f"   {dep}")
            return False
        else:
            print("✅ Essential dependencies configured")
            return True
            
    except Exception as e:
        print(f"❌ Error checking dependencies: {e}")
        return False

def validate_build():
    """Validate that the package can be built."""
    print("\n🔨 Validating package build...")
    
    # Clean previous builds
    for path in ["build", "dist"]:
        if Path(path).exists():
            import shutil
            shutil.rmtree(path)
    
    # Try to build
    try:
        result = subprocess.run(
            ["python", "setup.py", "sdist", "bdist_wheel"],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Package builds successfully")
        
        # Check if files were created
        dist_files = list(Path("dist").glob("*"))
        if len(dist_files) >= 2:
            print(f"✅ Created {len(dist_files)} distribution files:")
            for file in dist_files:
                size = file.stat().st_size / 1024  # KB
                print(f"   {file.name} ({size:.1f} KB)")
        else:
            print("❌ Expected distribution files not created")
            return False
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        print(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Build error: {e}")
        return False

def main():
    """Main validation function."""
    print("🎙️ YouTube Chat CLI - Package Validation")
    print("=" * 50)
    
    # Change to project root if needed
    if not Path("pyproject.toml").exists():
        print("❌ Must be run from project root directory")
        sys.exit(1)
    
    checks = [
        ("Package Structure", check_package_structure),
        ("Version Consistency", check_version_consistency),
        ("Entry Points", check_entry_points),
        ("Dependencies", check_dependencies),
        ("Build Process", validate_build),
    ]
    
    results = []
    for check_name, check_func in checks:
        print(f"\n{'='*20} {check_name} {'='*20}")
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print(f"❌ {check_name} failed with error: {e}")
            results.append((check_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*50}")
    
    passed = 0
    for check_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{len(results)} checks passed")
    
    if passed == len(results):
        print("\n🎉 All validations passed! Package is ready for PyPI publication.")
        print("\nNext steps:")
        print("1. Set up PyPI token: export PYPI_TOKEN='your-token'")
        print("2. Test publish: python scripts/publish_to_pypi.py --test")
        print("3. Publish: python scripts/publish_to_pypi.py")
        return 0
    else:
        print(f"\n❌ {len(results) - passed} validation(s) failed. Please fix the issues before publishing.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
