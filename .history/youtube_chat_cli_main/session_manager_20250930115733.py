"""
Session manager module for handling session state persistence.
"""

import json
import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional


class SessionManager:
    """Manages persistent session state for the CLI tool."""

    def __init__(self, session_file: str = "session.json"):
        """Initialize session manager with session file path.

        Args:
            session_file: Name of the session file (stored in user data directory)
        """
        self.session_file = self._get_session_file_path(session_file)

    def _get_session_file_path(self, session_file: str) -> Path:
        """Get the full path for the session file in user data directory."""
        # Use user data directory to persist sessions across runs
        user_data_dir = Path.home() / ".youtube-chat-cli"
        user_data_dir.mkdir(exist_ok=True)
        return user_data_dir / session_file

    def load_session(self) -> Dict:
        """Load session data from the session file.

        Returns:
            Dict containing session_id, active_source_url, and chat_history
        """
        if not self.session_file.exists():
            # Create default session
            default_session = {
                "session_id": str(uuid.uuid4()),
                "active_source_url": "",
                "chat_history": []
            }
            self._save_session_file(default_session)
            return default_session

        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
                # Ensure all required keys exist
                if 'session_id' not in session_data:
                    session_data['session_id'] = str(uuid.uuid4())
                if 'active_source_url' not in session_data:
                    session_data['active_source_url'] = ""
                if 'chat_history' not in session_data:
                    session_data['chat_history'] = []
                return session_data
        except (json.JSONDecodeError, IOError) as e:
            # If file is corrupted, create new session
            print(f"Warning: Session file corrupted ({e}), creating new session.")
            default_session = {
                "session_id": str(uuid.uuid4()),
                "active_source_url": "",
                "chat_history": []
            }
            self._save_session_file(default_session)
            return default_session

    def _save_session_file(self, session_data: Dict) -> None:
        """Save session data to the session file."""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            raise IOError(f"Failed to save session file: {e}")

    def save_session(self, session_data: Dict) -> None:
        """Save the session data and ensure file is written to disk."""
        self._save_session_file(session_data)

    def get_session_id(self) -> str:
        """Get the current session ID, generating one if it doesn't exist."""
        session = self.load_session()
        if not session.get('session_id'):
            session['session_id'] = str(uuid.uuid4())
            self.save_session(session)
        return session['session_id']

    def set_session_id(self, new_session_id: str) -> None:
        """Set a new session ID."""
        session = self.load_session()
        session['session_id'] = new_session_id
        self.save_session(session)

    def get_active_source(self) -> str:
        """Get the currently active source URL."""
        session = self.load_session()
        return session.get('active_source_url', "")

    def set_active_source(self, url: str) -> None:
        """Set the active source URL."""
        session = self.load_session()
        session['active_source_url'] = url
        self.save_session(session)

    def get_chat_history(self) -> List[Dict]:
        """Get the chat history for the current session."""
        session = self.load_session()
        return session.get('chat_history', [])

    def add_to_chat_history(self, role: str, content: str) -> None:
        """Add a message to the chat history."""
        session = self.load_session()
        if 'chat_history' not in session:
            session['chat_history'] = []

        session['chat_history'].append({
            'role': role,
            'content': content
        })

        self.save_session(session)

    def clear_chat_history(self) -> None:
        """Clear the chat history while keeping other session data."""
        session = self.load_session()
        session['chat_history'] = []
        self.save_session(session)


# Global session manager instance
_session_manager = None

def get_session_manager():
    """Get or create the global session manager instance."""
    global _session_manager
    if _session_manager is None:
        _session_manager = SessionManager()
    return _session_manager
