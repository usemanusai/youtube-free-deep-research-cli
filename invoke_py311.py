import subprocess, sys
from pathlib import Path
py311_path = Path('.python311_path').read_text(encoding='utf-8').strip()
cmd = [py311_path, 'check_py311_pkgs2.py']
res = subprocess.run(cmd, capture_output=True, text=True)
Path('py311_invoke_log.txt').write_text(f'cmd: {cmd}\nreturncode: {res.returncode}\nstdout:\n{res.stdout}\nstderr:\n{res.stderr}', encoding='utf-8')
print('DONE invoke_py311: returncode', res.returncode)

