from youtube_chat_cli_main.core.database import get_database


def test_session_crud():
    db = get_database()
    sid = 'test-session-1'
    # Create
    db.create_chat_session(session_id=sid, name='unit', metadata={'k': 'v'})
    db.add_chat_message(session_id=sid, role='assistant', content='hello', metadata={})
    # Retrieve
    sess = db.get_session(sid)
    assert sess and sess['id'] == sid
    msgs = db.get_session_messages(sid)
    assert len(msgs) >= 1
    # List
    res = db.list_sessions(limit=10, offset=0, workflow_type=None)
    assert isinstance(res, dict) and 'sessions' in res

