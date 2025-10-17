#!/usr/bin/env python3
"""Test script to verify OpenRouter API key rotation logic."""

import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv('youtube_chat_cli_main/.env', override=True)

from youtube_chat_cli_main.services.llm_service import get_llm_service

print("Initializing LLM service...")
llm = get_llm_service()

print(f"\nLLM Backend: {type(llm.backend).__name__}")

if hasattr(llm.backend, 'api_keys'):
    print(f"Total API keys available: {len(llm.backend.api_keys)}")
    print(f"Current key index: {llm.backend.current_key_index}")
    print(f"Current key (first 30 chars): {llm.backend.api_keys[llm.backend.current_key_index][:30]}...")
    
    # Test a simple generation
    print("\n--- Testing Simple Generation ---")
    try:
        result = llm.generate(
            prompt="Say 'Hello, world!' and nothing else.",
            temperature=0.7,
            max_tokens=50
        )
        print(f"✅ Generation successful!")
        print(f"Response: {result[:100]}...")
    except Exception as e:
        print(f"❌ Generation failed: {e}")
else:
    print("Backend does not support key rotation (not OpenRouter)")

