import json
mods = ['melo', 'melo.api', 'chatterbox', 'chatterbox.tts', 'torchaudio']
result = {}
for m in mods:
    try:
        __import__(m)
        result[m] = True
    except Exception:
        result[m] = False
with open('py311_tts_pkgs.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print('WROTE py311_tts_pkgs.json:', result)

