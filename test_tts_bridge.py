"""
Test script for TTS Bridge - Verify MeloTTS and Chatterbox work via Python 3.11 subprocess

This script tests the TTS bridge functionality to ensure MeloTTS and Chatterbox
can generate audio via the Python 3.11 subprocess bridge.

Usage:
    python test_tts_bridge.py

Author: Augment Agent
Date: September 30, 2025
"""

import os
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Test texts
TEST_TEXTS = {
    "short": "Hello, this is a test of the text-to-speech bridge.",
    "medium": "Welcome to the TTS bridge test. This system allows MeloTTS and Chatterbox to run in Python 3.11 while the main application uses Python 3.13. This provides the best audio quality available.",
    "long": """
    This is a comprehensive test of the TTS bridge system. The bridge allows us to use 
    high-quality TTS engines like MeloTTS and Chatterbox that require Python 3.11, 
    while maintaining our main application in Python 3.13. MeloTTS provides 4 out of 5 
    quality with excellent multilingual support. Chatterbox provides 4.5 out of 5 quality 
    with the most natural and expressive speech available in open-source TTS systems.
    """
}


def test_bridge_availability():
    """Test if TTS bridge is available."""
    logger.info("=" * 60)
    logger.info("TEST 1: TTS Bridge Availability")
    logger.info("=" * 60)
    
    try:
        from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient
        logger.info("✅ TTS Bridge client module imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Failed to import TTS Bridge client: {e}")
        return False


def test_python311_detection():
    """Test if Python 3.11 can be detected."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Python 3.11 Detection")
    logger.info("=" * 60)
    
    try:
        from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient
        
        # Try to initialize bridge
        bridge = TTSBridgeClient()
        logger.info(f"✅ Python 3.11 detected at: {bridge.python311_path}")
        logger.info(f"✅ Bridge script found at: {bridge.bridge_script}")
        return True
        
    except FileNotFoundError as e:
        logger.error(f"❌ Python 3.11 not found: {e}")
        logger.info("\n📋 To fix this:")
        logger.info("   1. Run: setup_python311_env.bat (Windows) or setup_python311_env.sh (Linux/Mac)")
        logger.info("   2. Or set PYTHON311_PATH environment variable")
        logger.info("   3. Or create .python311_path file with the path")
        return False
    except Exception as e:
        logger.error(f"❌ Bridge initialization failed: {e}")
        return False


def test_melotts_generation():
    """Test MeloTTS audio generation."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: MeloTTS Audio Generation")
    logger.info("=" * 60)
    
    try:
        from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient
        
        bridge = TTSBridgeClient()
        output_file = "test_melotts_output.wav"
        
        logger.info("Generating MeloTTS audio...")
        result = bridge.generate_melotts(
            text=TEST_TEXTS["medium"],
            output_file=output_file,
            language="EN-US",
            speed=1.0
        )
        
        # Verify file exists
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            logger.info(f"✅ MeloTTS audio generated: {result}")
            logger.info(f"   File size: {file_size:,} bytes")
            logger.info(f"   Quality: 4/5 - High-quality multilingual TTS")
            return True
        else:
            logger.error(f"❌ Output file not found: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ MeloTTS generation failed: {e}")
        logger.exception("Full traceback:")
        return False


def test_chatterbox_generation():
    """Test Chatterbox audio generation."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Chatterbox Audio Generation")
    logger.info("=" * 60)
    
    try:
        from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient
        
        bridge = TTSBridgeClient()
        output_file = "test_chatterbox_output.wav"
        
        logger.info("Generating Chatterbox audio...")
        logger.info("⚠️  Note: First run may take longer (model download)")
        
        result = bridge.generate_chatterbox(
            text=TEST_TEXTS["medium"],
            output_file=output_file,
            exaggeration=0.5
        )
        
        # Verify file exists
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            logger.info(f"✅ Chatterbox audio generated: {result}")
            logger.info(f"   File size: {file_size:,} bytes")
            logger.info(f"   Quality: 4.5/5 - HIGHEST QUALITY, expressive TTS")
            return True
        else:
            logger.error(f"❌ Output file not found: {result}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Chatterbox generation failed: {e}")
        logger.exception("Full traceback:")
        return False


def test_tts_service_integration():
    """Test TTS service integration with bridge."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: TTS Service Integration")
    logger.info("=" * 60)
    
    try:
        from youtube_chat_cli_main.tts_service import TTSService
        
        # Initialize TTS service
        tts = TTSService()
        
        logger.info(f"TTS Bridge available: {tts.tts_bridge_available}")
        
        if not tts.tts_bridge_available:
            logger.error("❌ TTS Bridge not available in TTS service")
            return False
        
        # Test MeloTTS via service
        logger.info("\nTesting MeloTTS via TTS service...")
        output_file = "test_service_melotts.wav"
        result = tts.generate_audio_melotts_bridge(
            text=TEST_TEXTS["short"],
            output_file=output_file
        )
        
        if os.path.exists(result):
            logger.info(f"✅ MeloTTS via service: {result}")
        else:
            logger.error(f"❌ MeloTTS service test failed")
            return False
        
        # Test Chatterbox via service
        logger.info("\nTesting Chatterbox via TTS service...")
        output_file = "test_service_chatterbox.wav"
        result = tts.generate_audio_chatterbox_bridge(
            text=TEST_TEXTS["short"],
            output_file=output_file
        )
        
        if os.path.exists(result):
            logger.info(f"✅ Chatterbox via service: {result}")
        else:
            logger.error(f"❌ Chatterbox service test failed")
            return False
        
        logger.info("\n✅ TTS Service integration successful!")
        return True
        
    except Exception as e:
        logger.error(f"❌ TTS service integration failed: {e}")
        logger.exception("Full traceback:")
        return False


def main():
    """Run all tests."""
    logger.info("\n" + "=" * 60)
    logger.info("TTS BRIDGE TEST SUITE")
    logger.info("=" * 60)
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Working directory: {os.getcwd()}")
    logger.info("")
    
    results = {
        "Bridge Availability": test_bridge_availability(),
        "Python 3.11 Detection": test_python311_detection(),
    }
    
    # Only run generation tests if Python 3.11 is detected
    if results["Python 3.11 Detection"]:
        results["MeloTTS Generation"] = test_melotts_generation()
        results["Chatterbox Generation"] = test_chatterbox_generation()
        results["TTS Service Integration"] = test_tts_service_integration()
    else:
        logger.warning("\n⚠️  Skipping generation tests - Python 3.11 not detected")
        logger.info("Please run setup_python311_env.bat or setup_python311_env.sh first")
    
    # Print summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUMMARY")
    logger.info("=" * 60)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    logger.info("")
    logger.info(f"Total: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        logger.info("\n🎉 ALL TESTS PASSED! TTS Bridge is working correctly!")
        logger.info("\n📋 Next steps:")
        logger.info("   1. Run your podcast generation with improved audio quality")
        logger.info("   2. The system will automatically use Chatterbox (4.5/5) or MeloTTS (4/5)")
        logger.info("   3. Enjoy natural, expressive podcast audio!")
    else:
        logger.warning(f"\n⚠️  {total_tests - passed_tests} test(s) failed")
        logger.info("\n📋 Troubleshooting:")
        logger.info("   1. Ensure Python 3.11 environment is set up")
        logger.info("   2. Run: setup_python311_env.bat (Windows) or setup_python311_env.sh (Linux/Mac)")
        logger.info("   3. Check that MeloTTS and Chatterbox are installed in Python 3.11 environment")
    
    logger.info("\n" + "=" * 60)
    
    return passed_tests == total_tests


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

