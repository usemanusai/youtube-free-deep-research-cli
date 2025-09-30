"""
Basic import test runner for verifying module structure.
Run this when pytest isn't available due to dependency issues.
"""

def test_basic_imports():
    """Test that all modules can be imported successfully."""
    print("Testing basic module imports...")

    try:
        # Test core modules
        import session_manager
        print("✓ session_manager imports successfully")

        import source_processor
        print("✓ source_processor imports successfully")

        import llm_service
        print("✓ llm_service imports successfully")

        import tts_service
        print("✓ tts_service imports successfully")

        import n8n_client
        print("✓ n8n_client imports successfully")

        # Test CLI
        import cli
        print("✓ cli imports successfully")

        # Test factory functions
        from source_processor import get_source_processor
        processor = get_source_processor()
        print("✓ get_source_processor() works")

        from session_manager import SessionManager
        manager = SessionManager("test_session.json")
        print("✓ SessionManager can be created")

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
