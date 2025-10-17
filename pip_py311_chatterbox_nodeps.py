import subprocess
from pathlib import Path
py311 = Path('.python311_path').read_text(encoding='utf-8').strip()
print('USING', py311)
res = subprocess.run([py311, '-m', 'pip', 'install', 'chatterbox-tts==0.1.4', '--no-deps'], text=True, capture_output=True)
print('RC', res.returncode)
print('STDOUT_TAIL\n', res.stdout[-4000:])
print('STDERR_TAIL\n', res.stderr[-4000:])

