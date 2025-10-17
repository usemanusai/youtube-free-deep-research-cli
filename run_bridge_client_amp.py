from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient

c = TTSBridgeClient()
try:
    out = c.generate_chatterbox(text='Code & Conversation', output_file='bridge_client_amp.wav')
    print('OK', out)
except Exception as e:
    print('ERR', e)

