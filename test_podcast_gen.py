#!/usr/bin/env python
"""Test podcast generation from imports."""
import sys
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from youtube_chat_cli_main.services.vector_store import get_vector_store
from youtube_chat_cli_main.llm_service import get_llm_service
from youtube_chat_cli_main.tts_service import get_tts_service

def _build_filter_dict(tags: str):
    conditions = []
    tag_list = [t.strip().lower() for t in (tags or '').split(',') if t.strip()]
    for t in tag_list:
        conditions.append({f'tag_{t}': 1})
    return {'$and': conditions} if conditions else None

def _aggregate_results_text(results, max_chars: int = 8000) -> str:
    parts = []
    seen_files = set()
    total = 0
    for r in results:
        meta = r.get('metadata') or {}
        fname = meta.get('file_name') or ''
        if fname and fname not in seen_files:
            seen_files.add(fname)
        chunk = r.get('content') or ''
        if not chunk:
            continue
        if total + len(chunk) > max_chars:
            chunk = chunk[: max(0, max_chars - total)]
        if chunk:
            parts.append(f"\n\n# Source: {fname}\n\n{chunk}")
            total += len(chunk)
        if total >= max_chars:
            break
    return ("\n".join(parts)).strip()

def main():
    print("Starting podcast generation test...")
    
    # Get vector store
    print("1. Getting vector store...")
    vs = get_vector_store()
    
    # Build filter
    print("2. Building filter...")
    filt = _build_filter_dict('podcast,important')
    print(f"   Filter: {filt}")
    
    # Search
    print("3. Searching vector store...")
    results = vs.search(query='content', top_k=20, filter_dict=filt)
    print(f"   Found {len(results)} results")
    
    # Aggregate
    print("4. Aggregating context...")
    context = _aggregate_results_text(results, max_chars=8000)
    print(f"   Context length: {len(context)} characters")
    if not context:
        print("ERROR: No content matched the given filters.")
        return 1
    
    # Generate script
    print("5. Generating podcast script...")
    llm = get_llm_service()
    script = llm.generate_podcast_script(context)
    print(f"   Script length: {len(script)} characters")
    print(f"   Script preview: {script[:200]}...")
    
    # Generate audio
    print("6. Generating audio...")
    tts = get_tts_service()
    audio_path = tts.generate_podcast_audio(script, 'podcast_test.wav')
    print(f"   ✅ Podcast generated: {audio_path}")
    
    return 0

if __name__ == '__main__':
    sys.exit(main())

