from youtube_chat_cli_main.tts_bridge_client import TTSBridgeClient

client = TTSBridgeClient()
print('py311', client.python311_path)
out = client.generate_chatterbox(text='Hello from client', output_file='bridge_client_test.wav')
print('OUT', out)

