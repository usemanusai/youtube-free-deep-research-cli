from pathlib import Path
import json
files = ['zRZLBiO4DYA_podcast.wav','hybrid_podcast.wav','bridge_melo_test.wav','bridge_chatterbox_test.wav','outputs/summary.txt','outputs/faq.txt','outputs/toc.txt']
info = {}
for f in files:
    p = Path(f)
    info[f] = {'exists': p.exists()}
    if p.exists():
        info[f]['size'] = p.stat().st_size
    if p.exists() and p.is_file() and p.suffix.lower() in ['.txt','.json']:
        try:
            with p.open('r', encoding='utf-8') as fh:
                head = ''.join([next(fh) for _ in range(3)])
            info[f]['head'] = head
        except Exception:
            pass
print(json.dumps(info, indent=2))

