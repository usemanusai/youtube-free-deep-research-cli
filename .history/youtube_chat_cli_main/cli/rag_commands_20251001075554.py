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
        
        # Filter for supported file types
        supported_extensions = {'.pdf', '.docx', '.txt', '.md', '.html', '.png', '.jpg', '.jpeg'}
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
        click.echo(Fore.YELLOW + "Run 'jaegis queue process' to process them")
        
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

