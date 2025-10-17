import json
from pathlib import Path
base = Path('outputs')
seg_dirs = [p for p in base.glob('podcast_segments_*') if p.is_dir()]
info = {}
for d in seg_dirs:
    wavs = sorted(d.glob('*.wav'))
    info[str(d)] = [{'name': str(w), 'size': w.stat().st_size} for w in wavs]
print(json.dumps(info, indent=2))

