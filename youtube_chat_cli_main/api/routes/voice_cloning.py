"""Voice cloning API endpoints with advanced prosody control."""

import os
import logging
from typing import Optional, List
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import aiofiles

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1/voice-clone", tags=["voice-cloning"])


# Pydantic models for request/response validation
class VoiceGenerateRequest(BaseModel):
    """Request model for voice generation with advanced parameters."""
    voice_id: int = Field(..., description="ID of cloned voice")
    text: str = Field(..., description="Text to synthesize")
    speed: float = Field(default=1.0, ge=0.5, le=2.0, description="Speech rate multiplier")
    pitch: float = Field(default=0.0, ge=-12, le=12, description="Pitch adjustment in semitones")
    exaggeration: float = Field(default=0.5, ge=0.25, le=2.0, description="Emotional exaggeration")
    cfg_weight: float = Field(default=0.5, ge=0.0, le=1.0, description="Classifier-free guidance weight")
    temperature: float = Field(default=0.9, ge=0.0, le=2.0, description="Randomness/variation")
    top_p: float = Field(default=0.95, ge=0.0, le=1.0, description="Nucleus sampling parameter")
    min_p: float = Field(default=0.1, ge=0.0, le=1.0, description="Minimum probability threshold")
    emotion: str = Field(
        default="neutral",
        description="Emotion type: neutral, happy, sad, angry, joyful, excited, surprised, curious, confident, empathetic"
    )
    emphasis: Optional[List[str]] = Field(default=None, description="Words to emphasize")
    pause_before: int = Field(default=0, ge=0, le=5000, description="Pause before text in milliseconds")
    pause_after: int = Field(default=0, ge=0, le=5000, description="Pause after text in milliseconds")
    breath_frequency: int = Field(default=0, ge=0, le=20, description="Insert breath every N words")
    seed: Optional[int] = Field(default=None, description="Random seed for reproducibility")

    class Config:
        json_schema_extra = {
            "example": {
                "voice_id": 1,
                "text": "Hello, this is a test.",
                "speed": 1.0,
                "pitch": 0,
                "exaggeration": 0.5,
                "cfg_weight": 0.5,
                "temperature": 0.9,
                "emotion": "happy",
                "emphasis": ["test"],
                "pause_before": 0,
                "pause_after": 0,
                "breath_frequency": 0
            }
        }


class VoiceGenerateResponse(BaseModel):
    """Response model for voice generation."""
    success: bool
    output_path: str
    text_length: int
    voice_id: int
    parameters: dict = Field(description="Parameters used for generation")


class VoiceParametersResponse(BaseModel):
    """Response model for voice parameters."""
    speed: float
    pitch: float
    exaggeration: float
    cfg_weight: float
    temperature: float
    top_p: float
    min_p: float
    emotion: str
    pause_before: int
    pause_after: int
    breath_frequency: int

# Lazy import to avoid circular dependencies
_voice_service = None


def get_voice_service():
    """Get or initialize voice cloning service."""
    global _voice_service
    if _voice_service is None:
        try:
            from youtube_chat_cli_main.services.voice_cloning_service import VoiceCloningService
            _voice_service = VoiceCloningService()
        except Exception as e:
            logger.error(f"Failed to initialize voice cloning service: {e}")
            raise HTTPException(status_code=500, detail="Voice cloning service unavailable")
    return _voice_service


@router.post("/upload-reference")
async def upload_reference_audio(
    name: str,
    file: UploadFile = File(...),
    consent_ip: Optional[str] = None
):
    """Upload reference audio for voice cloning.

    Args:
        name: Name for the cloned voice
        file: Audio file (WAV, MP3, FLAC)
        consent_ip: IP address for consent tracking

    Returns:
        Voice information
    """
    try:
        service = get_voice_service()

        # Save uploaded file temporarily
        temp_path = f"/tmp/{file.filename}"
        os.makedirs("/tmp", exist_ok=True)

        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Create voice
        voice_info = service.create_voice(
            name=name,
            reference_audio=temp_path,
            consent_ip=consent_ip
        )

        # Clean up temp file
        if os.path.exists(temp_path):
            os.remove(temp_path)

        logger.info(f"✅ Voice '{name}' uploaded successfully")
        return voice_info

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")


@router.get("/voices")
async def list_voices():
    """List all cloned voices.

    Returns:
        List of voice information
    """
    try:
        service = get_voice_service()
        voices = service.list_voices()
        return {"voices": voices, "total": len(voices)}
    except Exception as e:
        logger.error(f"Failed to list voices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=VoiceGenerateResponse)
async def generate_speech(
    request: VoiceGenerateRequest,
    background_tasks: BackgroundTasks = None
):
    """Generate speech with cloned voice and advanced prosody control.

    Args:
        request: Voice generation request with all parameters
        background_tasks: Background task manager

    Returns:
        Generated audio file path and metadata
    """
    try:
        service = get_voice_service()

        # Generate output path
        output_file = f"/tmp/voice_output_{request.voice_id}_{hash(request.text)}.wav"

        # Generate speech with all advanced parameters
        output_path = service.generate_speech(
            voice_id=request.voice_id,
            text=request.text,
            output_file=output_file,
            speed=request.speed,
            pitch=request.pitch,
            exaggeration=request.exaggeration,
            cfg_weight=request.cfg_weight,
            temperature=request.temperature,
            top_p=request.top_p,
            min_p=request.min_p,
            emotion=request.emotion,
            emphasis=request.emphasis,
            pause_before=request.pause_before,
            pause_after=request.pause_after,
            breath_frequency=request.breath_frequency,
            seed=request.seed
        )

        # Prepare response with parameters
        parameters = {
            "speed": request.speed,
            "pitch": request.pitch,
            "exaggeration": request.exaggeration,
            "cfg_weight": request.cfg_weight,
            "temperature": request.temperature,
            "top_p": request.top_p,
            "min_p": request.min_p,
            "emotion": request.emotion,
            "pause_before": request.pause_before,
            "pause_after": request.pause_after,
            "breath_frequency": request.breath_frequency
        }

        # Schedule cleanup
        if background_tasks:
            background_tasks.add_task(cleanup_file, output_path)

        logger.info(f"✅ Speech generated: voice_id={request.voice_id}, emotion={request.emotion}, "
                   f"pitch={request.pitch}st, speed={request.speed}x")

        return VoiceGenerateResponse(
            success=True,
            output_path=output_path,
            text_length=len(request.text),
            voice_id=request.voice_id,
            parameters=parameters
        )

    except ValueError as e:
        logger.error(f"Invalid parameters: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/voices/{voice_id}")
async def delete_voice(voice_id: int):
    """Delete a cloned voice.

    Args:
        voice_id: ID of voice to delete

    Returns:
        Success status
    """
    try:
        service = get_voice_service()
        success = service.delete_voice(voice_id)

        if not success:
            raise HTTPException(status_code=404, detail=f"Voice {voice_id} not found")

        return {"success": True, "message": f"Voice {voice_id} deleted"}

    except Exception as e:
        logger.error(f"Delete failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/settings")
async def get_settings():
    """Get voice cloning settings.

    Returns:
        Current settings
    """
    try:
        service = get_voice_service()
        device_info = service.engine.get_device_info()

        return {
            "device": device_info["device"],
            "model": device_info["model_name"],
            "quality": device_info["quality"],
            "nfe": device_info["nfe"],
            "cuda_available": device_info["cuda_available"],
            "storage_path": str(service.storage_path)
        }

    except Exception as e:
        logger.error(f"Failed to get settings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/parameter-presets")
async def get_parameter_presets():
    """Get predefined parameter presets for different voice styles.

    Returns:
        Dictionary of preset configurations
    """
    presets = {
        "neutral": {
            "speed": 1.0,
            "pitch": 0,
            "exaggeration": 0.5,
            "cfg_weight": 0.5,
            "temperature": 0.9,
            "emotion": "neutral",
            "description": "Natural, balanced speech"
        },
        "happy": {
            "speed": 1.1,
            "pitch": 2,
            "exaggeration": 0.7,
            "cfg_weight": 0.5,
            "temperature": 1.0,
            "emotion": "happy",
            "description": "Upbeat, cheerful speech"
        },
        "sad": {
            "speed": 0.8,
            "pitch": -3,
            "exaggeration": 0.6,
            "cfg_weight": 0.4,
            "temperature": 0.8,
            "emotion": "sad",
            "description": "Slow, melancholic speech"
        },
        "angry": {
            "speed": 1.2,
            "pitch": 3,
            "exaggeration": 0.8,
            "cfg_weight": 0.6,
            "temperature": 1.1,
            "emotion": "angry",
            "description": "Fast, intense speech"
        },
        "excited": {
            "speed": 1.3,
            "pitch": 4,
            "exaggeration": 0.9,
            "cfg_weight": 0.6,
            "temperature": 1.2,
            "emotion": "excited",
            "description": "Very energetic, enthusiastic speech"
        },
        "calm": {
            "speed": 0.9,
            "pitch": -1,
            "exaggeration": 0.4,
            "cfg_weight": 0.4,
            "temperature": 0.7,
            "emotion": "neutral",
            "description": "Slow, relaxed speech"
        },
        "professional": {
            "speed": 1.0,
            "pitch": 1,
            "exaggeration": 0.5,
            "cfg_weight": 0.5,
            "temperature": 0.8,
            "emotion": "confident",
            "description": "Clear, professional speech"
        },
        "dramatic": {
            "speed": 0.95,
            "pitch": 2,
            "exaggeration": 1.2,
            "cfg_weight": 0.5,
            "temperature": 1.0,
            "emotion": "joyful",
            "description": "Theatrical, expressive speech"
        }
    }

    return {
        "presets": presets,
        "total": len(presets),
        "description": "Use these presets as starting points for voice generation"
    }


@router.post("/validate-audio")
async def validate_audio(file: UploadFile = File(...)):
    """Validate reference audio file.

    Args:
        file: Audio file to validate

    Returns:
        Validation results
    """
    try:
        service = get_voice_service()

        # Save temporarily
        temp_path = f"/tmp/validate_{file.filename}"
        os.makedirs("/tmp", exist_ok=True)

        async with aiofiles.open(temp_path, 'wb') as f:
            content = await file.read()
            await f.write(content)

        # Validate
        validation = service.validate_reference_audio(temp_path)

        # Clean up
        if os.path.exists(temp_path):
            os.remove(temp_path)

        return validation

    except Exception as e:
        logger.error(f"Validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def cleanup_file(file_path: str):
    """Clean up temporary file."""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.debug(f"Cleaned up: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to clean up {file_path}: {e}")


__all__ = ["router"]

