import subprocess
from pathlib import Path

py311 = Path('.python311_path').read_text(encoding='utf-8').strip()
code = (
    'ok1=ok2=False\n'
    'try:\n    import chatterbox\n    ok1=True\nexcept Exception as e:\n    print("E1", e)\n'
    'try:\n    from chatterbox import tts as _t\n    ok2=True\nexcept Exception as e:\n    print("E2", e)\n'
    'print("HAS_CHATTERBOX", ok1)\nprint("HAS_CHATTERBOX_TTS", ok2)\n'
)
res = subprocess.run([py311, '-c', code], text=True, capture_output=True)
print('RC', res.returncode)
print(res.stdout)
print(res.stderr)
