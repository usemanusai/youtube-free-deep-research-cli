import os
import math
import time
from pathlib import Path

from youtube_chat_cli_main.session_manager import get_session_manager
from youtube_chat_cli_main.source_processor import get_source_processor
from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient

# Optional pydub combine if available
try:
    from pydub import AudioSegment
    HAVE_PYDUB = True
except Exception:
    HAVE_PYDUB = False


def chunk_text(text: str, max_len: int = 300):
    # Simple sentence-aware splitting
    sentences = []
    buff = []
    l = 0
    for part in text.split('. '):
        piece = (part + '. ').strip()
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
    out_file = Path('zRZLBiO4DYA_podcast_hq_chatterbox.wav')
    sm = get_session_manager()
    sp = get_source_processor()

    active = sm.get_active_source()
    if not active:
        print('No active source. Set with: youtube_chat_cli_main\\cli.py set-source <URL>')
        raise SystemExit(1)

    print('Fetching transcript + punctuation...')
    text = sp.process_content(active)
    if not text:
        print('No content text found')
        raise SystemExit(1)

    chunks = chunk_text(text, max_len=280)
    print(f'Chunks: {len(chunks)}')

    seg_dir = Path('outputs') / f'transcript_segments_{int(time.time())}'
    seg_dir.mkdir(parents=True, exist_ok=True)

    client = TTSBridgeClient()

    wavs = []
    for i, ch in enumerate(chunks, start=1):
        fp = seg_dir / f'seg_{i:03d}.wav'
        print(f'[{i}/{len(chunks)}] synthesize -> {fp.name}')
        client.generate_chatterbox(text=ch, output_file=str(fp))
        wavs.append(fp)

    print('Combining segments...')
    combine_segments_wav(wavs, str(out_file))
    print('Done:', out_file, out_file.stat().st_size, 'bytes')


if __name__ == '__main__':
    main()

