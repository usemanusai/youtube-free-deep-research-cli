import subprocess, sys
from pathlib import Path

py311 = Path('.python311_path').read_text(encoding='utf-8').strip()

def run(cmd, timeout=1800):
    print('RUN:', ' '.join(cmd), flush=True)
    return subprocess.run(cmd, text=True, capture_output=True, timeout=timeout)

logs = []
steps = [
    [py311, '-m', 'pip', 'install', '--upgrade', 'pip', 'wheel', 'setuptools'],
    [py311, '-m', 'pip', 'install', 'MeloTTS'],
    [py311, '-m', 'pip', 'install', 'chatterbox-tts'],
    # CPU-only torch/torchaudio; may fail but we'll continue
    [py311, '-m', 'pip', 'install', '--index-url', 'https://download.pytorch.org/whl/cpu', 'torch', 'torchaudio'],
    [py311, 'check_py311_pkgs2.py'],
]

rc = 0
for i, cmd in enumerate(steps, 1):
    try:
        res = run(cmd)
        logs.append((i, cmd, res.returncode, res.stdout[-4000:], res.stderr[-4000:]))
        if res.returncode != 0 and rc == 0:
            rc = res.returncode
    except Exception as e:
        logs.append((i, cmd, -1, '', str(e)))
        if rc == 0:
            rc = -1

# Write log file
out = []
for i, cmd, code, out_last, err_last in logs:
    out.append(f'== Step {i} ==\nCMD: {" ".join(cmd)}\nRC: {code}\nSTDOUT_TAIL:\n{out_last}\nSTDERR_TAIL:\n{err_last}\n')
Path('pip_py311_install_log.txt').write_text('\n'.join(out), encoding='utf-8')
print('DONE pip_py311_install.py rc=', rc)

