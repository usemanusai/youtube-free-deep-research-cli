import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load .env explicitly from repo root
load_dotenv(dotenv_path=str(Path('.env').resolve()), override=True)

# Late imports after env
from youtube_chat_cli_main.session_manager import SessionManager
from youtube_chat_cli_main.source_processor import get_source_processor
from youtube_chat_cli_main.llm_service import get_llm_service

URL = sys.argv[1] if len(sys.argv) > 1 else "https://www.youtube.com/watch?v=dQw4w9WgXcQ"

out_dir = Path('outputs'); out_dir.mkdir(exist_ok=True)

sm = SessionManager()
sp = get_source_processor()
llm = get_llm_service()

# Set/ensure source
active = sm.get_active_source() or ""
if active != URL:
    sp.process_content(URL)
    sm.set_active_source(URL)
    sm.clear_chat_history()

# Always work from active
active = sm.get_active_source()
ctx = sp.process_content(active)

# Generate outputs
summary = llm.summarize_content(ctx)
faq = llm.generate_faq(ctx)
toc = llm.generate_toc(ctx)

(Path(out_dir/ 'summary.txt')).write_text(summary, encoding='utf-8')
(Path(out_dir/ 'faq.txt')).write_text(faq, encoding='utf-8')
(Path(out_dir/ 'toc.txt')).write_text(toc, encoding='utf-8')

print('WROTE outputs/summary.txt, outputs/faq.txt, outputs/toc.txt')

