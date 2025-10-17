#!/bin/bash
# Setup Python 3.11 Environment for TTS Bridge
# This script creates a separate Python 3.11 environment for MeloTTS and Chatterbox

set -e

echo "=========================================="
echo "Python 3.11 TTS Bridge Environment Setup"
echo "=========================================="
echo ""

# Check if conda is available
if command -v conda &> /dev/null; then
    echo "✅ Conda detected - using conda for environment creation"
    
    # Create conda environment with Python 3.11
    echo "Creating conda environment 'tts-bridge-py311'..."
    conda create -y -n tts-bridge-py311 python=3.11
    
    echo ""
    echo "Activating environment..."
    source "$(conda info --base)/etc/profile.d/conda.sh"
    conda activate tts-bridge-py311
    
    # Install TTS engines
    echo ""
    echo "Installing MeloTTS..."
    pip install MeloTTS
    
    echo ""
    echo "Installing Chatterbox TTS..."
    pip install chatterbox-tts
    
    echo ""
    echo "Installing additional dependencies..."
    pip install flask requests
    
    # Get Python path
    PYTHON311_PATH=$(which python)
    
    echo ""
    echo "=========================================="
    echo "✅ Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Python 3.11 Path: $PYTHON311_PATH"
    echo "Environment Name: tts-bridge-py311"
    echo ""
    echo "To activate this environment in the future:"
    echo "  conda activate tts-bridge-py311"
    echo ""
    echo "To deactivate:"
    echo "  conda deactivate"
    echo ""
    
    # Save Python path to config file
    echo "$PYTHON311_PATH" > .python311_path
    echo "Python 3.11 path saved to .python311_path"
    
elif command -v pyenv &> /dev/null; then
    echo "✅ Pyenv detected - using pyenv for environment creation"
    
    # Install Python 3.11.9 if not already installed
    if ! pyenv versions | grep -q "3.11.9"; then
        echo "Installing Python 3.11.9..."
        pyenv install 3.11.9
    fi
    
    # Create virtual environment
    echo "Creating pyenv virtualenv 'tts-bridge-py311'..."
    pyenv virtualenv 3.11.9 tts-bridge-py311
    
    echo ""
    echo "Activating environment..."
    pyenv activate tts-bridge-py311
    
    # Install TTS engines
    echo ""
    echo "Installing MeloTTS..."
    pip install MeloTTS
    
    echo ""
    echo "Installing Chatterbox TTS..."
    pip install chatterbox-tts
    
    echo ""
    echo "Installing additional dependencies..."
    pip install flask requests
    
    # Get Python path
    PYTHON311_PATH=$(pyenv which python)
    
    echo ""
    echo "=========================================="
    echo "✅ Setup Complete!"
    echo "=========================================="
    echo ""
    echo "Python 3.11 Path: $PYTHON311_PATH"
    echo "Environment Name: tts-bridge-py311"
    echo ""
    echo "To activate this environment in the future:"
    echo "  pyenv activate tts-bridge-py311"
    echo ""
    echo "To deactivate:"
    echo "  pyenv deactivate"
    echo ""
    
    # Save Python path to config file
    echo "$PYTHON311_PATH" > .python311_path
    echo "Python 3.11 path saved to .python311_path"
    
else
    echo "❌ Neither conda nor pyenv detected!"
    echo ""
    echo "Please install one of the following:"
    echo "  - Conda: https://docs.conda.io/en/latest/miniconda.html"
    echo "  - Pyenv: https://github.com/pyenv/pyenv"
    echo ""
    echo "Or manually create a Python 3.11 virtual environment:"
    echo "  python3.11 -m venv tts-bridge-py311"
    echo "  source tts-bridge-py311/bin/activate"
    echo "  pip install MeloTTS chatterbox-tts flask requests"
    echo ""
    exit 1
fi

echo ""
echo "Next steps:"
echo "1. Test the installation:"
echo "   $PYTHON311_PATH -c 'from melo.api import TTS; print(\"✅ MeloTTS OK\")'"
echo "   $PYTHON311_PATH -c 'from chatterbox.tts import ChatterboxTTS; print(\"✅ Chatterbox OK\")'"
echo ""
echo "2. The TTS bridge will automatically use this Python 3.11 environment"
echo ""

