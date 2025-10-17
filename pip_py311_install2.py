import subprocess, sys
from pathlib import Path

py311 = Path('.python311_path').read_text(encoding='utf-8').strip()

def run(cmd, timeout=2400):
    print('RUN:', ' '.join(cmd), flush=True)
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)

logs = []
steps = [
    [py311, '-m', 'pip', 'install', '--upgrade', 'pip'],
    [py311, '-m', 'pip', 'install', 'numpy==1.25.2'],
    [py311, '-m', 'pip', 'install', '--index-url', 'https://download.pytorch.org/whl/cpu', 'torch==2.6.0+cpu', 'torchaudio==2.6.0+cpu'],
    [py311, '-m', 'pip', 'install', 'chatterbox-tts==0.1.4'],
    [py311, 'check_py311_pkgs2.py'],
]

rc = 0
out_lines = []
for i, cmd in enumerate(steps, 1):
    try:
        res = run(cmd)
        out_lines.append(f'== Step {i} ==\nCMD: {" ".join(cmd)}\nRC: {res.returncode}\nSTDOUT_TAIL:\n{res.stdout[-4000:]}\nSTDERR_TAIL:\n{res.stderr[-4000:]}\n')
        if res.returncode != 0 and rc == 0:
            rc = res.returncode
    except Exception as e:
        out_lines.append(f'== Step {i} ==\nCMD: {" ".join(cmd)}\nRC: -1\nEXC: {e}\n')
        if rc == 0:
            rc = -1

Path('pip_py311_install2_log.txt').write_text('\n'.join(out_lines), encoding='utf-8')
print('DONE pip_py311_install2.py rc=', rc)

