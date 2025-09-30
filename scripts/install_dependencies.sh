#!/bin/bash
"""
Installation script for YouTube Chat CLI dependencies.
"""

set -e  # Exit on any error

echo "YouTube Chat CLI - Dependency Installation Script"
echo "================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | cut -d' ' -f2)
required_version="3.8"

if python3 -c "import sys; exit(0 if sys.version_info >= (3, 8) else 1)"; then
    print_success "Python $python_version is compatible"
else
    print_error "Python 3.8+ is required. Found: $python_version"
    exit 1
fi

# Check if pip is available
print_status "Checking pip availability..."
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed. Please install pip first."
    exit 1
fi
print_success "pip3 is available"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install package in development mode
print_status "Installing YouTube Chat CLI in development mode..."
pip install -e .

# Install optional TTS dependencies
read -p "Install TTS dependencies? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing TTS dependencies..."
    pip install -e ".[tts]"
    print_success "TTS dependencies installed"
fi

# Install development dependencies
read -p "Install development dependencies? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Installing development dependencies..."
    pip install -e ".[dev]"
    print_success "Development dependencies installed"
fi

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    print_status "Creating .env file from template..."
    cp examples/sample_config.env .env
    print_warning "Please edit .env file and add your API keys"
else
    print_status ".env file already exists"
fi

# Test installation
print_status "Testing installation..."
if python -c "import youtube_chat_cli; print('Import successful')"; then
    print_success "Installation test passed"
else
    print_error "Installation test failed"
    exit 1
fi

# Display next steps
echo
echo "================================================="
print_success "Installation completed successfully!"
echo
echo "Next steps:"
echo "1. Edit .env file and add your API keys:"
echo "   - YOUTUBE_API_KEY (required)"
echo "   - OPENROUTER_API_KEY (optional, for AI features)"
echo "   - N8N_WEBHOOK_URL (optional, for n8n integration)"
echo
echo "2. Test the CLI:"
echo "   python cli.py --help"
echo "   python -m youtube_chat_cli.cli.main --help"
echo
echo "3. Install TTS libraries (optional):"
echo "   python cli.py tts install-all --cpu-only"
echo
echo "4. Start monitoring channels:"
echo "   python cli.py channel add https://youtube.com/@channelname"
echo "   python cli.py service start --daemon"
echo
echo "For more information, see the README.md file."
