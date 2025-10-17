"""
Simple MeloTTS Test - English Only (No Japanese Dependencies)

This test verifies MeloTTS works for English without requiring MeCab/Japanese support.
"""

import sys
import os

# Test if we can import MeloTTS for English
try:
    print("Testing MeloTTS English support...")
    print("=" * 60)
    
    # Import only what we need for English
    from melo.text import english
    print("✅ English text processing imported successfully")
    
    # Try to import the TTS class
    from melo.api import TTS
    print("✅ MeloTTS API imported successfully")
    
    # Initialize English TTS
    print("\nInitializing English TTS model...")
    tts = TTS(language='EN', device='cpu')
    print("✅ English TTS model initialized successfully")
    
    # Get available speakers
    speaker_ids = tts.hps.data.spk2id
    print(f"\n✅ Available English speakers: {list(speaker_ids.keys())}")
    
    # Generate test audio
    test_text = "Hello! This is a test of MeloTTS English text-to-speech."
    output_file = "test_melotts_english.wav"
    
    print(f"\nGenerating audio: '{test_text}'")
    print(f"Output file: {output_file}")
    
    # Use first English speaker
    english_speakers = [k for k in speaker_ids.keys() if k.startswith('EN')]
    if english_speakers:
        speaker_id = speaker_ids[english_speakers[0]]
        print(f"Using speaker: {english_speakers[0]}")
        
        tts.tts_to_file(
            text=test_text,
            speaker_id=speaker_id,
            output_path=output_file,
            speed=1.0
        )
        
        # Check if file was created
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"\n✅ SUCCESS! Audio file generated: {output_file}")
            print(f"   File size: {file_size:,} bytes")
            print(f"   Quality: 4/5 - High-quality multilingual TTS")
            print("\n" + "=" * 60)
            print("🎉 MeloTTS is working correctly!")
            print("=" * 60)
            sys.exit(0)
        else:
            print(f"\n❌ ERROR: Audio file was not created")
            sys.exit(1)
    else:
        print(f"\n❌ ERROR: No English speakers found")
        sys.exit(1)
    
except ImportError as e:
    print(f"\n❌ Import Error: {e}")
    print("\nMeloTTS may not be installed correctly.")
    print("Try reinstalling:")
    print("  cd MeloTTS")
    print("  ..\\tts-bridge-py310\\Scripts\\pip.exe install -e .")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

