#!/usr/bin/env python3
"""Test script to verify OpenRouter API key rotation configuration."""

import os
from dotenv import load_dotenv

# Load the .env file
load_dotenv('youtube_chat_cli_main/.env', override=True)

# Test raw environment variable
keys_csv = os.getenv('OPENROUTER_API_KEYS', '')
print(f"Raw OPENROUTER_API_KEYS length: {len(keys_csv)} characters")

# Parse keys
if keys_csv:
    keys = [k.strip() for k in keys_csv.split(',') if k.strip()]
    print(f"Number of keys parsed: {len(keys)}")
    print(f"First key: {keys[0][:30]}...")
    print(f"Last key: {keys[-1][:30]}...")
else:
    print("No OPENROUTER_API_KEYS found!")

# Test the config class
print("\n--- Testing Config Class ---")
from youtube_chat_cli_main.core.config import get_config

cfg = get_config()
api_keys = cfg.openrouter_api_keys
print(f"Config loaded {len(api_keys)} API keys")
if api_keys:
    print(f"First key from config: {api_keys[0][:30]}...")
    print(f"Last key from config: {api_keys[-1][:30]}...")

