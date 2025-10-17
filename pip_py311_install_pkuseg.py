import subprocess
from pathlib import Path
py311 = Path('.python311_path').read_text(encoding='utf-8').strip()
print('PY311', py311)
res = subprocess.run([py311,'-m','pip','install','pkuseg==0.0.25'], text=True, capture_output=True)
print('RC', res.returncode)
print(res.stdout[-4000:])
print(res.stderr[-4000:])

