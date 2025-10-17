"""
Unit tests for session_manager module.
"""

import json
import pytest
import tempfile
import uuid
from pathlib import Path
from session_manager import SessionManager


class TestSessionManager:
    """Test cases for SessionManager class."""

    @pytest.fixture
    def temp_session_file(self):
        """Create a temporary session file for testing."""
        with tempfile.NamedTemporaryFile(mode='w+', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
            yield temp_path
        temp_path.unlink(missing_ok=True)

    @pytest.fixture
    def session_manager(self, temp_session_file):
        """Create a SessionManager instance with a temporary file."""
        return SessionManager(temp_session_file.name)

    def test_initial_session_creation(self, session_manager, temp_session_file):
        """Test that a new session is created when file doesn't exist."""
        # Load session - should create default session
        session = session_manager.load_session()

        # Check that required fields exist
        assert 'session_id' in session
        assert 'active_source_url' in session
        assert 'chat_history' in session

        # Check that session_id is a valid UUID
        session_id = session['session_id']
        assert isinstance(session_id, str)
        uuid.UUID(session_id)  # Should not raise exception

        # Check that active_source_url is empty string
        assert session['active_source_url'] == ""

        # Check that chat_history is empty list
        assert session['chat_history'] == []

        # Check that file was created
        assert temp_session_file.exists()

    def test_load_existing_session(self, session_manager, temp_session_file):
        """Test loading an existing session from file."""
        # Create a session manually
        test_session = {
            "session_id": "test-session-123",
            "active_source_url": "https://example.com/video",
            "chat_history": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi there!"}
            ]
        }

        # Write to file
        with open(temp_session_file, 'w') as f:
            json.dump(test_session, f)

        # Load session
        loaded_session = session_manager.load_session()

        # Verify contents
        assert loaded_session['session_id'] == "test-session-123"
        assert loaded_session['active_source_url'] == "https://example.com/video"
        assert len(loaded_session['chat_history']) == 2
        assert loaded_session['chat_history'][0]['role'] == "user"
        assert loaded_session['chat_history'][0]['content'] == "Hello"

    def test_corrupted_session_file(self, session_manager, temp_session_file):
        """Test handling of corrupted session files."""
        # Write corrupted JSON
        temp_session_file.write_text("{ invalid json")

        # Loading should create new session and work
        session = session_manager.load_session()

        # Should have created valid session
        assert 'session_id' in session
        assert 'active_source_url' in session
        assert 'chat_history' in session

    def test_get_session_id_creates_if_missing(self, session_manager, temp_session_file):
        """Test get_session_id creates ID if missing."""
        # Create session without ID
        incomplete_session = {"active_source_url": "", "chat_history": []}
        with open(temp_session_file, 'w') as f:
            json.dump(incomplete_session, f)

        # Get session ID - should create one
        session_id = session_manager.get_session_id()
        assert session_id is not None
        assert isinstance(session_id, str)

        # Should be saved in session
        loaded_session = session_manager.load_session()
        assert loaded_session['session_id'] == session_id

    def test_set_and_get_active_source(self, session_manager):
        """Test setting and getting active source URL."""
        test_url = "https://youtu.be/test123"

        session_manager.set_active_source(test_url)
        retrieved_url = session_manager.get_active_source()

        assert retrieved_url == test_url

    def test_chat_history_operations(self, session_manager):
        """Test adding and clearing chat history."""
        # Add messages
        session_manager.add_to_chat_history("user", "What is this?")
        session_manager.add_to_chat_history("assistant", "This is a test.")

        chat_history = session_manager.get_chat_history()
        assert len(chat_history) == 2
        assert chat_history[0]['role'] == "user"
        assert chat_history[0]['content'] == "What is this?"
        assert chat_history[1]['role'] == "assistant"
        assert chat_history[1]['content'] == "This is a test."

        # Clear history
        session_manager.clear_chat_history()
        chat_history = session_manager.get_chat_history()
        assert len(chat_history) == 0

    def test_session_file_path(self, temp_session_file):
        """Test that session file path is constructed correctly."""
        session_manager = SessionManager(temp_session_file.name)
        expected_path = Path(temp_session_file.name)

        assert session_manager.session_file == expected_path

    def test_session_persistence_across_instances(self, temp_session_file):
        """Test that session data persists across manager instances."""
        # First manager instance
        manager1 = SessionManager(temp_session_file.name)
        manager1.set_active_source("https://test.com")

        # Second manager instance
        manager2 = SessionManager(temp_session_file.name)
        retrieved_url = manager2.get_active_source()

        assert retrieved_url == "https://test.com"

    def test_set_session_id(self, session_manager):
        """Test setting a custom session ID."""
        custom_id = "my-custom-session-id-12345"
        session_manager.set_session_id(custom_id)

        retrieved_id = session_manager.get_session_id()
        assert retrieved_id == custom_id
