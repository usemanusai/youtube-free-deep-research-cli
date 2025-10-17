import os
from pathlib import Path
from dotenv import load_dotenv
from youtube_chat_cli_main.llm_service import LLMService

# Load .env from repo root
load_dotenv(dotenv_path=str(Path(__file__).resolve().parent / '.env'), override=True)

print('AGENTS_CONFIG_JSON length:', len(os.getenv('AGENTS_CONFIG_JSON') or ''))
roles = ['planner','orchestrator','cortex','executor','hopper','outputter']
for r in roles:
    svc = LLMService(role=r)
    print(f"{r}: {svc.model}")

