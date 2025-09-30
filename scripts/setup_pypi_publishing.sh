#!/bin/bash

# YouTube Chat CLI - PyPI Publishing Setup Script
# This script helps set up everything needed for PyPI publishing

set -e  # Exit on any error

echo "🎙️ YouTube Chat CLI - PyPI Publishing Setup"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ] || [ ! -f "setup.py" ]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

print_info "Setting up PyPI publishing environment..."

# Step 1: Install required tools
print_info "Installing build tools..."
pip install --upgrade pip build twine

# Step 2: Clean previous builds
print_info "Cleaning previous builds..."
rm -rf build/ dist/ *.egg-info/
print_status "Build artifacts cleaned"

# Step 3: Build the package
print_info "Building the package..."
python setup.py sdist bdist_wheel
print_status "Package built successfully"

# Step 4: Validate the package
print_info "Validating the package..."
if command -v twine &> /dev/null; then
    twine check dist/*
    print_status "Package validation passed"
else
    print_warning "Twine not found in PATH, skipping validation"
fi

# Step 5: Check package contents
print_info "Package contents:"
echo "Source distribution: $(ls -lh dist/*.tar.gz | awk '{print $9, $5}')"
echo "Wheel distribution: $(ls -lh dist/*.whl | awk '{print $9, $5}')"

# Step 6: PyPI Token Setup Instructions
echo ""
print_info "PyPI Token Setup Instructions:"
echo "1. Go to https://pypi.org/account/register/ and create an account"
echo "2. Enable two-factor authentication (recommended)"
echo "3. Go to https://pypi.org/manage/account/ and create an API token"
echo "4. Set the token as an environment variable:"
echo "   export PYPI_TOKEN='pypi-your-token-here'"
echo ""

# Step 7: Check if token is set
if [ -z "$PYPI_TOKEN" ]; then
    print_warning "PYPI_TOKEN environment variable not set"
    echo "To publish to PyPI, you need to set your token:"
    echo "export PYPI_TOKEN='pypi-your-token-here'"
else
    print_status "PYPI_TOKEN is set"
fi

# Step 8: Publishing options
echo ""
print_info "Publishing Options:"
echo "1. Test on TestPyPI first (recommended):"
echo "   python scripts/publish_to_pypi.py --test"
echo ""
echo "2. Publish to PyPI:"
echo "   python scripts/publish_to_pypi.py"
echo ""
echo "3. Manual publishing:"
echo "   twine upload dist/*"
echo ""

# Step 9: Post-publication verification
print_info "After publishing, verify with:"
echo "pip install youtube-chat-cli"
echo "youtube-chat --version"
echo "youtube-chat --help"

print_status "Setup complete! Ready for PyPI publishing."

# Optional: Ask if user wants to publish now
echo ""
read -p "Do you want to publish to TestPyPI now? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -z "$PYPI_TEST_TOKEN" ]; then
        print_warning "PYPI_TEST_TOKEN not set. Please set it first:"
        echo "export PYPI_TEST_TOKEN='pypi-your-test-token-here'"
    else
        print_info "Publishing to TestPyPI..."
        python scripts/publish_to_pypi.py --test
    fi
fi
