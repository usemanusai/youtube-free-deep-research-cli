import subprocess, json
from pathlib import Path
py311 = Path('.python311_path').read_text(encoding='utf-8').strip()
cmd = [py311, 'tts_bridge.py', '--engine', 'chatterbox', '--text', 'Hello from Chatterbox bridge', '--output', 'bridge_chatterbox_test.wav']
print('RUN', ' '.join(cmd))
res = subprocess.run(cmd, text=True, capture_output=True)
print('RC', res.returncode)
print('STDOUT', res.stdout[-4000:])
print('STDERR', res.stderr[-4000:])

