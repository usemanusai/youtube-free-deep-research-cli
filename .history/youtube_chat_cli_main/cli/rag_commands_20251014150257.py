"""
JAEGIS NexusSync - RAG CLI Commands

Enhanced CLI commands for Adaptive RAG functionality including:
- Interactive chat with RAG
- File processing
- Queue management
- Google Drive sync
- Vector store search
- Background service control
"""

import click
import logging
from pathlib import Path
from typing import Optional
from colorama import Fore, Style

from ..core.config import get_config
from ..core.database import get_database
from ..services.rag_engine import get_rag_engine
from ..services.content_processor import get_content_processor
from ..services.gdrive_service import get_gdrive_watcher
from ..services.background_service import get_background_service
from ..services.vector_store import get_vector_store

logger = logging.getLogger(__name__)


@click.group()
def rag():
    """JAEGIS NexusSync - Adaptive RAG commands."""
    pass


@rag.command()
@click.option('--stream', is_flag=True, help='Stream the response')
def chat(stream: bool):
    """
    Interactive RAG chat session.

    Ask questions and get answers from your knowledge base with web search fallback.
    """
    click.echo(Fore.CYAN + "╔═══════════════════════════════════════════════════════════╗")
    click.echo(Fore.CYAN + "║   JAEGIS NexusSync - Adaptive RAG Chat                   ║")
    click.echo(Fore.CYAN + "╚═══════════════════════════════════════════════════════════╝")
    click.echo()
    click.echo(Fore.YELLOW + "Type your questions. Type 'exit' or 'quit' to end the session.")
    click.echo(Fore.YELLOW + "Type 'help' for available commands.")
    click.echo()

    # Initialize RAG engine
    try:
        rag_engine = get_rag_engine()
        click.echo(Fore.GREEN + "✅ RAG engine initialized")
        click.echo()
    except Exception as e:
        click.echo(Fore.RED + f"❌ Failed to initialize RAG engine: {e}")
        return

    # Chat loop
    while True:
        try:
            # Get user input
            question = click.prompt(Fore.CYAN + "You", type=str)

            # Handle special commands
            if question.lower() in ['exit', 'quit']:
                click.echo(Fore.YELLOW + "Goodbye!")
                break

            if question.lower() == 'help':
                click.echo(Fore.YELLOW + "\nAvailable commands:")
                click.echo("  exit, quit - End the chat session")
                click.echo("  help - Show this help message")
                click.echo()
                continue

            # Query RAG engine
            click.echo(Fore.YELLOW + "🤔 Thinking...")

            result = rag_engine.query(question)

            # Display answer
            click.echo()
            click.echo(Fore.GREEN + "Assistant: " + Style.RESET_ALL + result['answer'])
            click.echo()

            # Display metadata
            if result.get('web_search_used'):
                click.echo(Fore.YELLOW + "ℹ️  Used web search")
            if result.get('transform_count', 0) > 0:
                click.echo(Fore.YELLOW + f"ℹ️  Query transformed {result['transform_count']} times")

            num_docs = len(result.get('documents', []))
            if num_docs > 0:
                click.echo(Fore.YELLOW + f"ℹ️  Retrieved {num_docs} documents")

            click.echo()

        except KeyboardInterrupt:
            click.echo()
            click.echo(Fore.YELLOW + "Goodbye!")
            break
        except Exception as e:
            click.echo(Fore.RED + f"❌ Error: {e}")
            click.echo()


@rag.command()
@click.argument('file_path', type=click.Path(exists=True))
@click.option('--priority', default=0, help='Processing priority (higher = sooner)')
def process_file(file_path: str, priority: int):
    """
    Process a file and add it to the vector store.

    Supports: PDF, DOCX, TXT, Markdown, HTML, Images (with OCR)
    """
    click.echo(Fore.CYAN + f"Processing file: {file_path}")

    try:
        # Initialize services
        processor = get_content_processor()
        db = get_database()

        # Add to queue
        queue_id = db.add_to_queue(
            file_id=file_path,
            file_name=Path(file_path).name,
            source='local',
            priority=priority
        )

        click.echo(Fore.YELLOW + f"Added to queue (ID: {queue_id})")

        # Process immediately
        click.echo(Fore.YELLOW + "Processing...")
        success = processor.process_queue_item(queue_id)

        if success:
            click.echo(Fore.GREEN + "✅ File processed successfully")
        else:
            click.echo(Fore.RED + "❌ Processing failed")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@rag.command()
@click.argument('folder_path', type=click.Path(exists=True))
@click.option('--priority', default=0, help='Processing priority')
@click.option('--recursive', is_flag=True, help='Process subdirectories')
def process_folder(folder_path: str, priority: int, recursive: bool):
    """
    Process all files in a folder.
    """
    click.echo(Fore.CYAN + f"Processing folder: {folder_path}")

    try:
        db = get_database()
        folder = Path(folder_path)

        # Get all files
        if recursive:
            files = list(folder.rglob('*'))
        else:
            files = list(folder.glob('*'))

        # Filter for supported file types (expanded)
        supported_extensions = {
            '.pdf', '.docx', '.txt', '.md', '.html', '.png', '.jpg', '.jpeg',
            '.mp3', '.wav', '.m4a', '.flac', '.ogg',
            '.mp4', '.avi', '.mov', '.mkv',
            '.json'
        }
        files = [f for f in files if f.is_file() and f.suffix.lower() in supported_extensions]

        click.echo(Fore.YELLOW + f"Found {len(files)} files to process")

        # Add to queue
        for file in files:
            db.add_to_queue(
                file_id=str(file),
                file_name=file.name,
                source='local',
                priority=priority
            )

        click.echo(Fore.GREEN + f"✅ Added {len(files)} files to processing queue")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")



@rag.command(name='import-batch')
@click.option('--directory', '-d', type=click.Path(exists=True, file_okay=False), required=True, help='Directory to import from')
@click.option('--recursive', '-r', is_flag=True, help='Recurse into subdirectories')
@click.option('--formats', '-f', type=str, default='', help='Comma-separated list of file extensions (e.g., .pdf,.md,.mp3). Empty = all supported')
@click.option('--tags', '-t', type=str, default='', help='Comma-separated tags to attach to imported items')
@click.option('--queue', is_flag=True, help='Add to processing queue instead of processing immediately')
@click.option('--max-files', type=int, default=0, help='Limit number of files (0 = no limit)')
def import_batch(directory: str, recursive: bool, formats: str, tags: str, queue: bool, max_files: int):
    """
    Batch import multi-format documents (text, audio with transcription, video with transcription, PDFs, HTML, JSON).

    Examples:
      jaegis rag import-batch -d ./docs -r
      jaegis rag import-batch -d ./media --formats .mp3,.wav --tags podcast,meeting
    """
    click.echo(Fore.CYAN + f"Importing from: {directory}")

    # Build supported extensions set
    supported = {
        '.pdf', '.docx', '.txt', '.md', '.html', '.png', '.jpg', '.jpeg',
        '.mp3', '.wav', '.m4a', '.flac', '.ogg',
        '.mp4', '.avi', '.mov', '.mkv',
        '.json'
    }
    selected_exts = set(e.strip().lower() for e in formats.split(',') if e.strip())
    if selected_exts:
        unknown = selected_exts - supported
        if unknown:
            click.echo(Fore.RED + f"Unsupported extensions requested: {', '.join(sorted(unknown))}")
            return
        use_exts = selected_exts
    else:
        use_exts = supported

    # Enumerate files
    base = Path(directory)
    files = list(base.rglob('*') if recursive else base.glob('*'))
    files = [f for f in files if f.is_file() and f.suffix.lower() in use_exts]
    if max_files and max_files > 0:
        files = files[:max_files]

    if not files:
        click.echo(Fore.YELLOW + "No matching files found")
        return

    click.echo(Fore.YELLOW + f"Found {len(files)} files")

    tag_list = [t.strip() for t in tags.split(',') if t.strip()]

    try:
        processor = get_content_processor()
        vector_store = get_vector_store()
        db = get_database()

        success_count = 0
        fail_count = 0

        with click.progressbar(files, label='Importing', show_pos=True) as bar:
            for f in bar:
                try:
                    if queue:
                        db.add_to_queue(
                            file_id=str(f),
                            file_name=f.name,
                            source='local',
                            priority=0
                        )
                        success_count += 1
                    else:
                        result = processor.process_file(str(f))
                        # Attach tags and additional metadata
                        metadata = {
                            'file_id': str(f),
                            'file_name': f.name,
                            'source': 'local',
                            'tags': tag_list,
                            **result['metadata']
                        }
                        vector_store.add_documents(result['chunks'], metadata=metadata)
                        success_count += 1
                except Exception as e:
                    logger.exception(f"Failed to import {f}: {e}")
                    fail_count += 1

        click.echo(Fore.GREEN + f"\n✅ Import complete: {success_count} succeeded, {fail_count} failed")
        if queue:
            click.echo(Fore.YELLOW + "Items were enqueued. Run 'jaegis rag queue_process' to process.")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@rag.command()
@click.option('--query', '-q', help='Search query')
@click.option('--top-k', default=5, help='Number of results')
def search(query: Optional[str], top_k: int):
    """
    Search the vector store.
    """
    if not query:
        query = click.prompt(Fore.CYAN + "Enter search query", type=str)

    click.echo(Fore.YELLOW + f"Searching for: {query}")

    try:
        vector_store = get_vector_store()
        results = vector_store.search(query, top_k=top_k)

        click.echo()
        click.echo(Fore.GREEN + f"Found {len(results)} results:")
        click.echo()

        for i, result in enumerate(results, 1):
            click.echo(Fore.CYAN + f"[{i}] Score: {result['score']:.3f}")
            click.echo(Fore.WHITE + result['content'][:200] + "...")

            # Show metadata
            metadata = result.get('metadata', {})
            if metadata.get('file_name'):
                click.echo(Fore.YELLOW + f"    Source: {metadata['file_name']}")

            click.echo()

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@rag.command()
def gdrive_sync():
    """
    Manually sync Google Drive folder.

    Checks for new or modified files and adds them to the processing queue.
    """
    click.echo(Fore.CYAN + "Syncing Google Drive...")

    try:
        watcher = get_gdrive_watcher()
        count = watcher.watch()

        if count > 0:
            click.echo(Fore.GREEN + f"✅ Added {count} files to processing queue")
        else:
            click.echo(Fore.YELLOW + "No new or modified files found")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@rag.command()
def queue_status():
    """
    Show processing queue status.
    """
    click.echo(Fore.CYAN + "Processing Queue Status")
    click.echo(Fore.CYAN + "=" * 50)

    try:
        db = get_database()
        stats = db.get_queue_statistics()

        click.echo()
        click.echo(Fore.WHITE + f"Total items: {stats['total']}")
        click.echo()

        # Show counts by status
        click.echo(Fore.YELLOW + "By Status:")
        for status, count in stats['by_status'].items():
            color = Fore.GREEN if status == 'completed' else Fore.YELLOW
            if status == 'failed':
                color = Fore.RED
            click.echo(f"  {color}{status}: {count}")

        click.echo()

        if stats['failed_high_retry'] > 0:
            click.echo(Fore.RED + f"⚠️  {stats['failed_high_retry']} items failed multiple times")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@rag.command()
@click.option('--limit', default=10, help='Number of items to process')
def queue_process(limit: int):
    """
    Process pending items in the queue.
    """
    click.echo(Fore.CYAN + f"Processing up to {limit} queue items...")

    try:
        db = get_database()
        processor = get_content_processor()

        # Get pending items
        items = db.get_pending_queue_items(limit=limit)

        if not items:
            click.echo(Fore.YELLOW + "No pending items in queue")
            return

        click.echo(Fore.YELLOW + f"Processing {len(items)} items...")

        success_count = 0
        fail_count = 0

        for item in items:
            click.echo(Fore.WHITE + f"Processing: {item['file_name']}...")

            success = processor.process_queue_item(item['id'])

            if success:
                click.echo(Fore.GREEN + "  ✅ Success")
                success_count += 1
            else:
                click.echo(Fore.RED + "  ❌ Failed")
                fail_count += 1

        click.echo()
        click.echo(Fore.GREEN + f"✅ Processed: {success_count} succeeded, {fail_count} failed")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@rag.group()
def background():
    """Background service management."""
    pass


@background.command()
def start():
    """
    Start the background service.

    This starts automated Google Drive monitoring and queue processing.
    """
    click.echo(Fore.CYAN + "Starting background service...")

    try:
        bg_service = get_background_service()
        bg_service.start()

        click.echo(Fore.GREEN + "✅ Background service started")
        click.echo(Fore.YELLOW + "Press Ctrl+C to stop")

        # Keep running
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            click.echo()
            click.echo(Fore.YELLOW + "Stopping background service...")
            bg_service.stop()
            click.echo(Fore.GREEN + "✅ Background service stopped")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@background.command()
def status():
    """
    Show background service status.
    """
    click.echo(Fore.CYAN + "Background Service Status")
    click.echo(Fore.CYAN + "=" * 50)

    try:
        bg_service = get_background_service()
        status_info = bg_service.get_status()

        click.echo()

        if status_info['is_running']:
            click.echo(Fore.GREEN + "Status: Running")
        else:
            click.echo(Fore.YELLOW + "Status: Stopped")

        click.echo()

        if status_info['jobs']:
            click.echo(Fore.YELLOW + "Scheduled Jobs:")
            for job in status_info['jobs']:
                click.echo(f"  • {job['name']}")
                if job['next_run']:
                    click.echo(f"    Next run: {job['next_run']}")

        click.echo()

        # Show queue stats
        queue_stats = status_info.get('queue_statistics', {})
        if queue_stats:
            click.echo(Fore.YELLOW + "Queue Statistics:")
            click.echo(f"  Total: {queue_stats.get('total', 0)}")
            for status, count in queue_stats.get('by_status', {}).items():
                click.echo(f"  {status}: {count}")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@background.command()
def run_once():
    """
    Run background tasks once (for testing).
    """
    click.echo(Fore.CYAN + "Running background tasks once...")

    try:
        bg_service = get_background_service()
        results = bg_service.run_once()

        click.echo()
        click.echo(Fore.GREEN + "✅ Tasks completed:")
        click.echo(f"  Google Drive: {results['gdrive_watcher']} files added")
        click.echo(f"  Queue: {results['queue_processor']} items processed")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")


@rag.command()
def verify_connections():
    """
    Verify all service connections.

    Tests connectivity to Ollama, Qdrant, Google Drive, etc.
    """
    click.echo(Fore.CYAN + "Verifying Service Connections")
    click.echo(Fore.CYAN + "=" * 50)
    click.echo()

    # Test configuration
    click.echo(Fore.YELLOW + "1. Configuration...")
    try:
        config = get_config()
        click.echo(Fore.GREEN + "   ✅ Configuration loaded")
    except Exception as e:
        click.echo(Fore.RED + f"   ❌ Configuration failed: {e}")
        return

    # Test database
    click.echo(Fore.YELLOW + "2. Database...")
    try:
        db = get_database()
        stats = db.get_queue_statistics()
        click.echo(Fore.GREEN + f"   ✅ Database connected ({stats['total']} queue items)")
    except Exception as e:
        click.echo(Fore.RED + f"   ❌ Database failed: {e}")

    # Test LLM
    click.echo(Fore.YELLOW + "3. LLM Service...")
    try:
        from ..services.llm_service import get_llm_service
        llm = get_llm_service()
        response = llm.generate("Say 'OK' if you can hear me.", temperature=0.0, max_tokens=10)
        click.echo(Fore.GREEN + f"   ✅ LLM connected: {response[:50]}")
    except Exception as e:
        click.echo(Fore.RED + f"   ❌ LLM failed: {e}")

    # Test embeddings
    click.echo(Fore.YELLOW + "4. Embedding Service...")
    try:
        from ..services.embedding_service import get_embedding_service
        emb = get_embedding_service()
        embedding = emb.embed_query("test")
        click.echo(Fore.GREEN + f"   ✅ Embeddings connected (dim: {len(embedding)})")
    except Exception as e:
        click.echo(Fore.RED + f"   ❌ Embeddings failed: {e}")

    # Test vector store
    click.echo(Fore.YELLOW + "5. Vector Store...")
    try:
        vs = get_vector_store()
        info = vs.get_collection_info()
        click.echo(Fore.GREEN + f"   ✅ Vector store connected ({info.get('points_count', 0)} vectors)")
    except Exception as e:
        click.echo(Fore.RED + f"   ❌ Vector store failed: {e}")

    # Test web search
    click.echo(Fore.YELLOW + "6. Web Search...")
    try:
        from ..services.web_search_service import get_web_search_service
        ws = get_web_search_service()
        click.echo(Fore.GREEN + "   ✅ Web search configured")
    except Exception as e:
        click.echo(Fore.RED + f"   ❌ Web search failed: {e}")

    # Test Google Drive
    click.echo(Fore.YELLOW + "7. Google Drive...")
    try:
        from ..services.gdrive_service import get_gdrive_service
        gdrive = get_gdrive_service()
        click.echo(Fore.GREEN + "   ✅ Google Drive connected")
    except Exception as e:
        click.echo(Fore.RED + f"   ❌ Google Drive failed: {e}")

    click.echo()
    click.echo(Fore.GREEN + "✅ Connection verification complete")


@rag.command()
def info():
    """
    Show system information and statistics.
    """
    click.echo(Fore.CYAN + "╔═══════════════════════════════════════════════════════════╗")
    click.echo(Fore.CYAN + "║   JAEGIS NexusSync - System Information                  ║")
    click.echo(Fore.CYAN + "╚═══════════════════════════════════════════════════════════╝")
    click.echo()

    try:
        config = get_config()
        db = get_database()
        vs = get_vector_store()

        # Configuration
        click.echo(Fore.YELLOW + "Configuration:")
        click.echo(f"  LLM Model: {config.llm_model}")
        click.echo(f"  Embedding Provider: {config.embedding_provider}")
        click.echo(f"  Vector Store: {config.vector_store_type}")
        click.echo(f"  OCR Provider: {config.ocr_provider}")
        click.echo()

        # Database stats
        queue_stats = db.get_queue_statistics()
        click.echo(Fore.YELLOW + "Database:")
        click.echo(f"  Queue Items: {queue_stats['total']}")
        click.echo(f"  Pending: {queue_stats['by_status'].get('pending', 0)}")
        click.echo(f"  Completed: {queue_stats['by_status'].get('completed', 0)}")
        click.echo(f"  Failed: {queue_stats['by_status'].get('failed', 0)}")
        click.echo()

        # Vector store stats
        vs_info = vs.get_collection_info()
        click.echo(Fore.YELLOW + "Vector Store:")
        click.echo(f"  Collection: {vs_info.get('name', 'N/A')}")
        click.echo(f"  Vectors: {vs_info.get('vectors_count', 0)}")
        click.echo()

        # RAG config
        click.echo(Fore.YELLOW + "RAG Configuration:")
        click.echo(f"  Top K: {config.rag_top_k}")
        click.echo(f"  Min Relevance: {config.rag_min_relevance_score}")
        click.echo(f"  Max Transforms: {config.rag_max_transform_attempts}")
        click.echo(f"  Hallucination Check: {config.rag_hallucination_check}")
        click.echo(f"  Answer Check: {config.rag_answer_check}")

    except Exception as e:
        click.echo(Fore.RED + f"❌ Error: {e}")
