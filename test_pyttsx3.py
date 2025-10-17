"""Test pyttsx3 TTS installation and functionality."""
import pyttsx3
import os

print("=" * 60)
print("Testing pyttsx3 TTS")
print("=" * 60)

# Initialize pyttsx3
print("\n1. Initializing pyttsx3...")
try:
    engine = pyttsx3.init()
    print("✅ pyttsx3 initialized successfully")
except Exception as e:
    print(f"❌ Failed to initialize pyttsx3: {e}")
    exit(1)

# Get available voices
print("\n2. Getting available voices...")
voices = engine.getProperty('voices')
print(f"✅ Found {len(voices)} voices:")
for i, voice in enumerate(voices[:5]):  # Show first 5 voices
    print(f"   {i+1}. {voice.name} ({voice.id})")

# Get current properties
print("\n3. Current engine properties:")
rate = engine.getProperty('rate')
volume = engine.getProperty('volume')
print(f"   Rate: {rate}")
print(f"   Volume: {volume}")

# Test audio generation
print("\n4. Generating test audio...")
test_text_host = "Welcome to today's podcast! We're diving into an exciting topic about artificial intelligence."
test_text_expert = "Thanks for having me! I'm thrilled to share my insights on this fascinating subject."

# Generate Host audio (first voice)
print("\n   Generating Host audio...")
engine.setProperty('voice', voices[0].id)
engine.setProperty('rate', 150)
engine.setProperty('volume', 0.9)
output_host = "test_pyttsx3_host.wav"
engine.save_to_file(test_text_host, output_host)
engine.runAndWait()

if os.path.exists(output_host):
    size = os.path.getsize(output_host)
    print(f"   ✅ Host audio generated: {output_host} ({size:,} bytes)")
else:
    print(f"   ❌ Failed to generate host audio")

# Generate Expert audio (second voice if available)
if len(voices) > 1:
    print("\n   Generating Expert audio...")
    engine.setProperty('voice', voices[1].id)
    engine.setProperty('rate', 150)
    engine.setProperty('volume', 0.9)
    output_expert = "test_pyttsx3_expert.wav"
    engine.save_to_file(test_text_expert, output_expert)
    engine.runAndWait()
    
    if os.path.exists(output_expert):
        size = os.path.getsize(output_expert)
        print(f"   ✅ Expert audio generated: {output_expert} ({size:,} bytes)")
    else:
        print(f"   ❌ Failed to generate expert audio")

print("\n" + "=" * 60)
print("✅ pyttsx3 test complete!")
print("=" * 60)
print("\nNOTE: pyttsx3 produces robotic-sounding audio.")
print("It should only be used as an emergency fallback.")
print("=" * 60)

