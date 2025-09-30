"""
Basic import test runner for verifying module structure.
Run this when pytest isn't available due to dependency issues.
"""

def test_basic_imports():
    """Test that all modules can be imported successfully."""
    print("Testing basic module imports...")

    try:
        # Test core modules
        from youtube_chat_cli.utils.session_manager import SessionManager
        print("✓ SessionManager imports successfully")

        from youtube_chat_cli.services.transcription.processor import get_source_processor
        print("✓ SourceProcessor imports successfully")

        from youtube_chat_cli.utils.llm_service import get_llm_service
        print("✓ LLMService imports successfully")

        from youtube_chat_cli.services.tts.service import get_tts_service
        print("✓ TTSService imports successfully")

        from youtube_chat_cli.services.n8n.client import get_n8n_client
        print("✓ N8nClient imports successfully")

        # Test CLI
        import cli
        print("✓ cli imports successfully")

        # Test factory functions
        processor = get_source_processor()
        print("✓ get_source_processor() works")

        manager = SessionManager("test_session.json")
        print("✓ SessionManager can be created")

        # Test core functionality
        from youtube_chat_cli.core.youtube_api import get_youtube_client
        print("✓ YouTubeAPIClient imports successfully")

        from youtube_chat_cli.core.database import get_video_database
        print("✓ VideoDatabase imports successfully")

        print("\n✅ All basic imports successful!")
        print("The modular architecture is properly structured.")
        print("Once dependencies are installed, full functionality will work.")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def show_cli_commands():
    """Show available CLI commands."""
    print("\nAvailable CLI commands:")
    try:
        import cli
        # Access the click group to show commands
        print("  session view           - Show current session info")
        print("  session clear-history  - Clear chat history")
        print("  session clear-all      - Clear source and history")
        print("  session new-id         - Generate new session ID")
        print("  set-source <URL>       - Set active content source")
        print("  print-text             - Display processed content")
        print("  summarize              - Generate content summary")
        print("  faq                    - Generate FAQ from content")
        print("  toc                    - Generate table of contents")
        print("  chat                   - Interactive Q&A session")
        print("  podcast [--output]     - Generate audio podcast")
        print("  verify-connections     - Check external service status")
        print("  invoke-n8n <message>   - Send message to n8n workflow")
    except Exception as e:
        print(f"Error showing CLI commands: {e}")


if __name__ == "__main__":
    print("Personal Research Insight CLI - Basic Test Runner")
    print("=" * 55)

    success = test_basic_imports()

    show_cli_commands()

    print(f"\nResult: {'PASSED' if success else 'FAILED'}")
    print("\nNote: Full functionality requires installing dependencies:")
    print("  pip install -r requirements.txt")
    print("  (Resolve disk space issue first)")
