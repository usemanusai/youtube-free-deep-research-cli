import subprocess
from pathlib import Path
py311 = Path('.python311_path').read_text(encoding='utf-8').strip()

def install(pkg):
    print('INSTALL', pkg, flush=True)
    r = subprocess.run([py311,'-m','pip','install',pkg], text=True, capture_output=True)
    print('RC', r.returncode)
    print(r.stdout[-2000:])
    print(r.stderr[-2000:])

for pkg in [
    's3tokenizer==0.2.0',
    'pykakasi==2.3.0',
    'gradio==5.44.1'
]:
    install(pkg)
print('DONE')

