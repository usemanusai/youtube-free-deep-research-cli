import os
import sys
import time
import traceback
import shutil
import logging
from pathlib import Path

from youtube_chat_cli_main.session_manager import get_session_manager
from youtube_chat_cli_main.source_processor import get_source_processor
from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient

# Logging setup
logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s')
log = logging.getLogger("podcast_gen")

# pydub detection with ffmpeg availability
HAVE_PYDUB = False
try:
    from pydub import AudioSegment
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        HAVE_PYDUB = True
        log.info(f"pydub available (ffmpeg at {ffmpeg})")
    else:
        log.info("pydub present but ffmpeg not found; using wave fallback")
except Exception:
    log.info("pydub not available; using wave fallback")


def chunk_text(text: str, max_len: int = 300):
    # Simple sentence-aware splitting
    sentences = []
    buff = []
    l = 0
    for part in text.split('. '):
        piece = (part + '. ').strip()
        if not piece:
            continue
        if l + len(piece) > max_len and buff:
            sentences.append(' '.join(buff).strip())
            buff = [piece]
            l = len(piece)
        else:
            buff.append(piece)
            l += len(piece)
    if buff:
        sentences.append(' '.join(buff).strip())
    return [s for s in sentences if s]


def combine_segments_wav(files, out_path):
    if HAVE_PYDUB:
        segs = [AudioSegment.from_wav(str(f)) for f in files]
        silence = AudioSegment.silent(duration=300)
        acc = None
        for i, s in enumerate(segs):
            acc = s if acc is None else acc + silence + s
        acc.export(out_path, format='wav')
        return
    # wave fallback
    import wave
    with wave.open(out_path, 'wb') as out_wav:
        first_params = None
        for i, fp in enumerate(files):
            with wave.open(str(fp), 'rb') as w:
                params = w.getparams()
                if first_params is None:
                    first_params = params
                    out_wav.setparams(params)
                out_wav.writeframes(w.readframes(w.getnframes()))
                if i < len(files) - 1:
                    n_channels = first_params.nchannels
                    sampwidth = first_params.sampwidth
                    framerate = first_params.framerate
                    n_samples = int(framerate * 0.3)
                    out_wav.writeframes(b"\x00" * n_samples * n_channels * sampwidth)


def main():
    os.environ.setdefault('PYTHONUTF8', '1')

    # Allow overriding source via env for quick tests
    test_source = os.getenv('TEST_SOURCE')

    out_file = Path('zRZLBiO4DYA_podcast_hq_chatterbox.wav')
    sm = get_session_manager()
    sp = get_source_processor()

    active = test_source or sm.get_active_source()
    if not active:
        log.error('No active source. Set with: youtube_chat_cli_main\\cli.py set-source <URL>')
        sys.exit(1)

    log.info(f'Active source: {active}')

    # Fast path to avoid heavy punctuation model during debug
    if os.getenv('FAST_TRANSCRIPT', '1') == '1':
        log.info('FAST_TRANSCRIPT=1 -> fetching raw YouTube transcript (skip punctuation)')
        try:
            text = sp.get_youtube_transcript(active)
            log.info('Fetched raw transcript successfully')
        except Exception:
            log.info('Raw transcript fetch failed, falling back to full processing')
            text = sp.process_content(active)
    else:
        log.info('Fetching transcript + punctuation...')
        text = sp.process_content(active)

    if not text:
        log.error('No content text found')
        sys.exit(1)

    log.info(f'Text length: {len(text)} chars')
    chunks = chunk_text(text, max_len=280)
    # During debug, cap chunks to speed up
    max_chunks = int(os.getenv('MAX_CHUNKS', '8'))
    if len(chunks) > max_chunks:
        log.info(f"Capping chunks from {len(chunks)} to {max_chunks} for faster iteration")
        chunks = chunks[:max_chunks]
    log.info(f'Chunks: {len(chunks)}')

    seg_dir = Path('outputs') / f'transcript_segments_{int(time.time())}'
    seg_dir.mkdir(parents=True, exist_ok=True)

    client = TTSBridgeClient()

    wavs = []
    errors = 0
    for i, ch in enumerate(chunks, start=1):
        fp = seg_dir / f'seg_{i:03d}.wav'
        log.info(f'[{i}/{len(chunks)}] synthesize -> {fp.name} ({len(ch)} chars)')
        try:
            client.generate_chatterbox(text=ch, output_file=str(fp))
            if fp.exists() and fp.stat().st_size > 0:
                wavs.append(fp)
                log.info(f'  ✓ wrote {fp.stat().st_size} bytes')
            else:
                raise RuntimeError('empty or missing output')
        except Exception:
            errors += 1
            log.error(f'  ✗ segment {i} failed')
            traceback.print_exc()

    if not wavs:
        log.error('No segments synthesized; aborting')
        sys.exit(2)

    log.info('Combining segments...')
    combine_segments_wav(wavs, str(out_file))
    log.info(f'Done: {out_file} {out_file.stat().st_size} bytes (segments: {len(wavs)}, errors: {errors})')


if __name__ == '__main__':
    try:
        main()
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        sys.exit(3)
