import importlib.util, json, sys
mods = ['melo', 'melo.api', 'chatterbox', 'chatterbox.tts', 'torchaudio']
result = {m: (importlib.util.find_spec(m) is not None) for m in mods}
with open('py311_tts_pkgs.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2)
print('WROTE py311_tts_pkgs.json:', result)

