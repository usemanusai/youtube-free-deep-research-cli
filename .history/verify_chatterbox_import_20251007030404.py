import subprocess, sys
from pathlib import Path
py311 = Path('.python311_path').read_text(encoding='utf-8').strip()
cmd = [py311, '-c', 'import importlib;import sys;print("HAS_CHATTERBOX", importlib.util.find_spec("chatterbox") is not None);print("HAS_CHATTERBOX_TTS", importlib.util.find_spec("chatterbox.tts") is not None)']
res = subprocess.run(cmd, text=True, capture_output=True)
print('RC', res.returncode)
print(res.stdout)
print(res.stderr)

