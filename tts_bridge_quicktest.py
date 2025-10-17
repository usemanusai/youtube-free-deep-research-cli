from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient
from pathlib import Path
import json

out = {"melotts": None, "chatterbox": None}
client = TTSBridgeClient()

# MeloTTS test
try:
    p = client.generate_melotts("Hello from Melo bridge", "bridge_melo_test.wav")
    out["melotts"] = {"ok": True, "path": p, "size": Path(p).stat().st_size}
except Exception as e:
    out["melotts"] = {"ok": False, "error": str(e)}

# Chatterbox test
try:
    p = client.generate_chatterbox("Hello from Chatterbox bridge", "bridge_chatterbox_test.wav")
    out["chatterbox"] = {"ok": True, "path": p, "size": Path(p).stat().st_size}
except Exception as e:
    out["chatterbox"] = {"ok": False, "error": str(e)}

Path('tts_bridge_quicktest.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
print("WROTE tts_bridge_quicktest.json")

