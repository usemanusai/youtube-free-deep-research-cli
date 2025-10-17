import os, json
from pathlib import Path
from dotenv import load_dotenv
from youtube_chat_cli_main.llm_service import LLMService

# Load .env from repo root
load_dotenv(dotenv_path=str(Path('.env').resolve()), override=True)

res = {
    'agents_config_len': len(os.getenv('AGENTS_CONFIG_JSON') or ''),
    'roles': {}
}
roles = ['planner','orchestrator','cortex','executor','hopper','outputter']
for r in roles:
    svc = LLMService(role=r)
    res['roles'][r] = svc.model

Path('verify_roles_results.json').write_text(json.dumps(res, indent=2))
print('WROTE verify_roles_results.json')

