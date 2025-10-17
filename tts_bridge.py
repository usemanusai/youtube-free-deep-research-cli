#!/usr/bin/env python3.11
"""
TTS Bridge - Python 3.11 Subprocess Bridge for MeloTTS and Chatterbox

This script runs in a Python 3.11 environment and provides TTS generation
for engines that are incompatible with Python 3.13.

Usage:
    python tts_bridge.py --engine melotts --text "Hello world" --output output.wav
    python tts_bridge.py --engine chatterbox --text "Hello world" --output output.wav

Author: Augment Agent
Date: September 30, 2025
"""

import sys
import json
import argparse
import logging
from pathlib import Path
from typing import Optional

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def generate_melotts(
    text: str,
    output_file: str,
    language: str = "EN-US",
    speed: float = 1.0,
    voice_index: int = 0
) -> str:
    """
    Generate audio using MeloTTS.
    
    Args:
        text: Text to synthesize
        output_file: Output WAV file path
        language: Language code (EN-US, EN-BR, EN-AU, EN-Default, ES, FR, ZH, JP, KR)
        speed: Speech speed (0.5 to 2.0)
        voice_index: Voice index for the language
    
    Returns:
        Path to generated audio file
    """
    try:
        logger.info(f"Initializing MeloTTS for language: {language}")
        from melo.api import TTS
        
        # Extract language code (e.g., "EN" from "EN-US")
        lang_code = language.split("-")[0]
        
        # Initialize TTS
        tts = TTS(language=lang_code, device='cpu')
        speaker_ids = tts.hps.data.spk2id
        
        # Get speaker ID
        if language in speaker_ids:
            speaker_id = speaker_ids[language]
        else:
            # Fallback to first available speaker for the language
            available_speakers = [k for k in speaker_ids.keys() if k.startswith(lang_code)]
            if available_speakers:
                speaker_id = speaker_ids[available_speakers[0]]
                logger.warning(f"Language {language} not found, using {available_speakers[0]}")
            else:
                raise ValueError(f"No speakers found for language: {lang_code}")
        
        logger.info(f"Generating audio with speaker: {speaker_id}")
        
        # Generate audio
        tts.tts_to_file(
            text=text,
            speaker_id=speaker_id,
            output_path=output_file,
            speed=speed
        )
        
        logger.info(f"✅ MeloTTS audio generated: {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"❌ MeloTTS generation failed: {e}")
        raise


def generate_chatterbox(
    text: str,
    output_file: str,
    audio_prompt: Optional[str] = None,
    exaggeration: float = 0.5,
    cfg_weight: float = 0.5,
    language_id: Optional[str] = None
) -> str:
    """
    Generate audio using Chatterbox TTS.
    
    Args:
        text: Text to synthesize
        output_file: Output WAV file path
        audio_prompt: Path to reference audio for voice cloning
        exaggeration: Emotion exaggeration level (0.0 to 1.0)
        cfg_weight: Classifier-free guidance weight (0.0 to 1.0)
        language_id: Language ID for multilingual model (e.g., 'en', 'fr', 'zh')
    
    Returns:
        Path to generated audio file
    """
    try:
        import torchaudio as ta
        
        # Determine which model to use
        if language_id and language_id != 'en':
            logger.info(f"Initializing Chatterbox Multilingual for language: {language_id}")
            from chatterbox.mtl_tts import ChatterboxMultilingualTTS
            model = ChatterboxMultilingualTTS.from_pretrained(device="cpu")
        else:
            logger.info("Initializing Chatterbox English TTS")
            from chatterbox.tts import ChatterboxTTS
            model = ChatterboxTTS.from_pretrained(device="cpu")
        
        logger.info(f"Generating audio (exaggeration={exaggeration}, cfg_weight={cfg_weight})")
        
        # Generate audio
        if language_id and language_id != 'en':
            wav = model.generate(
                text,
                audio_prompt_path=audio_prompt,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight,
                language_id=language_id
            )
        else:
            wav = model.generate(
                text,
                audio_prompt_path=audio_prompt,
                exaggeration=exaggeration,
                cfg_weight=cfg_weight
            )
        
        # Save audio
        ta.save(output_file, wav, model.sr)
        
        logger.info(f"✅ Chatterbox audio generated: {output_file}")
        return output_file
        
    except Exception as e:
        logger.error(f"❌ Chatterbox generation failed: {e}")
        raise


def main():
    """Main entry point for TTS bridge."""
    parser = argparse.ArgumentParser(
        description='TTS Bridge - Python 3.11 subprocess for MeloTTS and Chatterbox'
    )
    
    # Required arguments
    parser.add_argument(
        '--engine',
        required=True,
        choices=['melotts', 'chatterbox'],
        help='TTS engine to use'
    )
    parser.add_argument(
        '--text',
        required=True,
        help='Text to synthesize'
    )
    parser.add_argument(
        '--output',
        required=True,
        help='Output audio file path'
    )
    
    # MeloTTS arguments
    parser.add_argument(
        '--language',
        default='EN-US',
        help='Language code for MeloTTS (EN-US, EN-BR, ES, FR, ZH, JP, KR)'
    )
    parser.add_argument(
        '--speed',
        type=float,
        default=1.0,
        help='Speech speed (0.5 to 2.0)'
    )
    parser.add_argument(
        '--voice-index',
        type=int,
        default=0,
        help='Voice index for the language'
    )
    
    # Chatterbox arguments
    parser.add_argument(
        '--audio-prompt',
        default=None,
        help='Path to reference audio for voice cloning (Chatterbox)'
    )
    parser.add_argument(
        '--exaggeration',
        type=float,
        default=0.5,
        help='Emotion exaggeration level (0.0 to 1.0, Chatterbox)'
    )
    parser.add_argument(
        '--cfg-weight',
        type=float,
        default=0.5,
        help='Classifier-free guidance weight (0.0 to 1.0, Chatterbox)'
    )
    parser.add_argument(
        '--language-id',
        default=None,
        help='Language ID for multilingual Chatterbox (en, fr, zh, etc.)'
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    try:
        # Generate audio based on engine
        if args.engine == 'melotts':
            result = generate_melotts(
                text=args.text,
                output_file=args.output,
                language=args.language,
                speed=args.speed,
                voice_index=args.voice_index
            )
        elif args.engine == 'chatterbox':
            result = generate_chatterbox(
                text=args.text,
                output_file=args.output,
                audio_prompt=args.audio_prompt,
                exaggeration=args.exaggeration,
                cfg_weight=args.cfg_weight,
                language_id=args.language_id
            )
        else:
            raise ValueError(f"Unknown engine: {args.engine}")
        
        # Return success response
        response = {
            "success": True,
            "output": result,
            "engine": args.engine
        }
        print(json.dumps(response))
        sys.exit(0)
        
    except Exception as e:
        # Return error response
        response = {
            "success": False,
            "error": str(e),
            "engine": args.engine
        }
        print(json.dumps(response), file=sys.stderr)
        logger.exception("TTS generation failed")
        sys.exit(1)


if __name__ == "__main__":
    main()

