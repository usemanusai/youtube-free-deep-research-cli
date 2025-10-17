import subprocess
from pathlib import Path
py311 = Path('.python311_path').read_text(encoding='utf-8').strip()

def run(args):
    print('RUN', ' '.join(args), flush=True)
    return subprocess.run([py311, '-m', 'pip'] + args, text=True, capture_output=True)

pkgs = [
    ['install', 'numpy==1.25.2'],
    ['install', 'librosa==0.11.0'],
    ['install', 'transformers==4.46.3'],
    ['install', 'diffusers==0.29.0'],
    ['install', 'safetensors==0.5.3'],
    ['install', 'soundfile==0.13.1'],
    ['install', 'soxr==1.0.0'],
    ['install', 'cffi==2.0.0'],
    ['install', 'resemble-perth==1.0.1'],
    ['install', 'conformer==0.3.2'],
]

codes = []
for args in pkgs:
    res = run(args)
    print('RC', res.returncode)
    print(res.stdout[-2000:])
    print(res.stderr[-2000:])
    codes.append(res.returncode)

print('EXIT_SUMMARY', codes)

