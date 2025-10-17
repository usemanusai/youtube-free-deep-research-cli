#!/usr/bin/env python3
"""Test script to verify the warning fix for OpenRouter API keys."""

import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv('youtube_chat_cli_main/.env', override=True)

print("=" * 80)
print("Testing OpenRouter API Key Configuration Warning Fix")
print("=" * 80)

# Test the config class
from youtube_chat_cli_main.core.config import get_config

print("\n--- Loading Configuration ---")
cfg = get_config()

print(f"\n✅ Configuration loaded successfully!")
print(f"   - has_llm_api_key: {cfg.has_llm_api_key}")
print(f"   - openrouter_api_keys count: {len(cfg.openrouter_api_keys)}")
print(f"   - First key: {cfg.openrouter_api_keys[0][:30]}..." if cfg.openrouter_api_keys else "   - No keys found")

print("\n--- Validation Results ---")
try:
    cfg.validate()
    print("✅ Configuration validation passed (no warnings expected)")
except Exception as e:
    print(f"❌ Configuration validation failed: {e}")

print("\n" + "=" * 80)
print("Test Complete")
print("=" * 80)

