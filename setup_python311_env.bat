@echo off
REM Setup Python 3.11 Environment for TTS Bridge (Windows)
REM This script creates a separate Python 3.11 environment for MeloTTS and Chatterbox

echo ==========================================
echo Python 3.11 TTS Bridge Environment Setup
echo ==========================================
echo.

REM Check if conda is available
where conda >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ Conda detected - using conda for environment creation[0m
    echo.
    
    REM Create conda environment with Python 3.11
    echo Creating conda environment 'tts-bridge-py311'...
    call conda create -y -n tts-bridge-py311 python=3.11
    
    echo.
    echo Activating environment...
    call conda activate tts-bridge-py311
    
    REM Install TTS engines
    echo.
    echo Installing MeloTTS...
    pip install MeloTTS
    
    echo.
    echo Installing Chatterbox TTS...
    pip install chatterbox-tts
    
    echo.
    echo Installing additional dependencies...
    pip install flask requests
    
    REM Get Python path
    for /f "delims=" %%i in ('where python') do set PYTHON311_PATH=%%i
    
    echo.
    echo ==========================================
    echo [32m✓ Setup Complete![0m
    echo ==========================================
    echo.
    echo Python 3.11 Path: %PYTHON311_PATH%
    echo Environment Name: tts-bridge-py311
    echo.
    echo To activate this environment in the future:
    echo   conda activate tts-bridge-py311
    echo.
    echo To deactivate:
    echo   conda deactivate
    echo.
    
    REM Save Python path to config file
    echo %PYTHON311_PATH% > .python311_path
    echo Python 3.11 path saved to .python311_path
    
    goto :end
)

REM Check if pyenv-win is available
where pyenv >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    echo [32m✓ Pyenv detected - using pyenv for environment creation[0m
    echo.
    
    REM Install Python 3.11.9 if not already installed
    pyenv versions | findstr "3.11.9" >nul
    if %ERRORLEVEL% NEQ 0 (
        echo Installing Python 3.11.9...
        pyenv install 3.11.9
    )
    
    REM Set local Python version
    echo Setting Python 3.11.9 as local version...
    pyenv local 3.11.9
    
    REM Create virtual environment
    echo Creating virtual environment 'tts-bridge-py311'...
    python -m venv tts-bridge-py311
    
    echo.
    echo Activating environment...
    call tts-bridge-py311\Scripts\activate.bat
    
    REM Install TTS engines
    echo.
    echo Installing MeloTTS...
    pip install MeloTTS
    
    echo.
    echo Installing Chatterbox TTS...
    pip install chatterbox-tts
    
    echo.
    echo Installing additional dependencies...
    pip install flask requests
    
    REM Get Python path
    set PYTHON311_PATH=%CD%\tts-bridge-py311\Scripts\python.exe
    
    echo.
    echo ==========================================
    echo [32m✓ Setup Complete![0m
    echo ==========================================
    echo.
    echo Python 3.11 Path: %PYTHON311_PATH%
    echo Environment Location: %CD%\tts-bridge-py311
    echo.
    echo To activate this environment in the future:
    echo   tts-bridge-py311\Scripts\activate.bat
    echo.
    echo To deactivate:
    echo   deactivate
    echo.
    
    REM Save Python path to config file
    echo %PYTHON311_PATH% > .python311_path
    echo Python 3.11 path saved to .python311_path
    
    goto :end
)

REM Neither conda nor pyenv found
echo [31m✗ Neither conda nor pyenv detected![0m
echo.
echo Please install one of the following:
echo   - Conda: https://docs.conda.io/en/latest/miniconda.html
echo   - Pyenv-win: https://github.com/pyenv-win/pyenv-win
echo.
echo Or manually create a Python 3.11 virtual environment:
echo   python3.11 -m venv tts-bridge-py311
echo   tts-bridge-py311\Scripts\activate.bat
echo   pip install MeloTTS chatterbox-tts flask requests
echo.
exit /b 1

:end
echo.
echo Next steps:
echo 1. Test the installation:
echo    %PYTHON311_PATH% -c "from melo.api import TTS; print('✓ MeloTTS OK')"
echo    %PYTHON311_PATH% -c "from chatterbox.tts import ChatterboxTTS; print('✓ Chatterbox OK')"
echo.
echo 2. The TTS bridge will automatically use this Python 3.11 environment
echo.
pause

