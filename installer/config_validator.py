"""
Config & Environment Validation Helpers for the Installer
- Port availability checks
- Minimal API key format checks (no live network calls by default)
- .env writing helpers
"""
from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Dict, Optional


def is_port_open(host: str, port: int, timeout: float = 0.5) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        return s.connect_ex((host, port)) == 0
    finally:
        s.close()


def next_available_port(start: int, host: str = '127.0.0.1') -> int:
    p = start
    while is_port_open(host, p):
        p += 1
    return p


def looks_like_api_key(value: Optional[str]) -> bool:
    if not value:
        return False
    # Heuristic: length and allowed charset
    v = value.strip()
    return 20 <= len(v) <= 128 and all(32 < ord(c) < 127 for c in v)


def write_env(path: Path, data: Dict[str, str]) -> None:
    lines = []
    for k, v in data.items():
        if v is None:
            continue
        safe = str(v).replace("\n", "\\n")
        lines.append(f"{k}={safe}")
    path.write_text("\n".join(lines) + "\n", encoding='utf-8')


def write_state(path: Path, state: Dict) -> None:
    path.write_text(json.dumps(state, indent=2), encoding='utf-8')

