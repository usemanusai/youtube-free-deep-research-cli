import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env explicitly
load_dotenv(dotenv_path=str(Path('.env').resolve()), override=True)

from youtube_chat_cli_main.session_manager import SessionManager
from youtube_chat_cli_main.source_processor import get_source_processor
from youtube_chat_cli_main.llm_service import get_llm_service
from youtube_chat_cli_main.tts_service import get_tts_service

URL = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

sm = SessionManager()
sp = get_source_processor()
llm = get_llm_service()

active = sm.get_active_source() or ""
if not active:
    # Process and set source
    processed = sp.process_content(URL)
    sm.set_active_source(URL)
    sm.clear_chat_history()

# Always work from the active source
active = sm.get_active_source()
ctx = sp.process_content(active)

print("=== SUMMARY ===")
print(llm.summarize_content(ctx))
print()

print("=== FAQ ===")
print(llm.generate_faq(ctx))
print()

print("=== TOC ===")
print(llm.generate_toc(ctx))
print()

# Confirm existing podcast artifact if present
podcast_path = Path("hybrid_podcast.wav")
if podcast_path.exists():
    print(f"=== PODCAST ===\nFile: {podcast_path} | Size: {podcast_path.stat().st_size} bytes\n")
else:
    print("=== PODCAST ===\nNo existing podcast file found (hybrid_podcast.wav).\n")

