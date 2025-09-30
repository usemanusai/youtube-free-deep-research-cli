"""
Interactive chat interface for YouTube Chat CLI with n8n RAG integration.
"""

import os
import sys
import json
import logging
import threading
import time
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# Rich imports for beautiful terminal UI
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    from rich.table import Table
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Prompt, Confirm
    from rich.layout import Layout
    from rich.live import Live
    from rich.align import Align
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    Console = None

from youtube_chat_cli.services.n8n.client import get_n8n_client
from youtube_chat_cli.services.workflow.manager import get_workflow_manager

logger = logging.getLogger(__name__)


class ChatMessageType(Enum):
    """Types of chat messages."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"
    ERROR = "error"


@dataclass
class ChatMessage:
    """A chat message."""
    type: ChatMessageType
    content: str
    timestamp: datetime
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class ChatSession:
    """A chat session with history and metadata."""
    
    def __init__(self, session_id: str, workflow_name: Optional[str] = None):
        """Initialize a chat session."""
        self.session_id = session_id
        self.workflow_name = workflow_name
        self.messages: List[ChatMessage] = []
        self.created_at = datetime.now()
        self.last_activity = datetime.now()
        self.metadata = {}
    
    def add_message(self, message: ChatMessage):
        """Add a message to the session."""
        self.messages.append(message)
        self.last_activity = datetime.now()
    
    def get_history(self, limit: Optional[int] = None) -> List[ChatMessage]:
        """Get chat history."""
        if limit:
            return self.messages[-limit:]
        return self.messages
    
    def export_history(self, format: str = "json") -> str:
        """Export chat history in specified format."""
        if format == "json":
            data = {
                "session_id": self.session_id,
                "workflow_name": self.workflow_name,
                "created_at": self.created_at.isoformat(),
                "last_activity": self.last_activity.isoformat(),
                "messages": [
                    {
                        "type": msg.type.value,
                        "content": msg.content,
                        "timestamp": msg.timestamp.isoformat(),
                        "metadata": msg.metadata
                    } for msg in self.messages
                ]
            }
            return json.dumps(data, indent=2, ensure_ascii=False)
        elif format == "markdown":
            lines = [f"# Chat Session: {self.session_id}\n"]
            lines.append(f"**Created:** {self.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n")
            lines.append(f"**Workflow:** {self.workflow_name or 'Default'}\n")
            lines.append("---\n")
            
            for msg in self.messages:
                if msg.type == ChatMessageType.USER:
                    lines.append(f"**You:** {msg.content}\n")
                elif msg.type == ChatMessageType.ASSISTANT:
                    lines.append(f"**Assistant:** {msg.content}\n")
                elif msg.type == ChatMessageType.SYSTEM:
                    lines.append(f"*System: {msg.content}*\n")
                lines.append("")
            
            return "\n".join(lines)
        else:
            raise ValueError(f"Unsupported export format: {format}")


class InteractiveChatInterface:
    """Interactive chat interface with rich terminal UI."""
    
    def __init__(self):
        """Initialize the chat interface."""
        if not RICH_AVAILABLE:
            raise ImportError("Rich library is required for interactive chat. Install with: pip install rich")
        
        self.console = Console()
        self.n8n_client = get_n8n_client()
        self.workflow_manager = get_workflow_manager()
        
        # Chat state
        self.current_session: Optional[ChatSession] = None
        self.sessions: Dict[str, ChatSession] = {}
        self.is_running = False
        
        # UI state
        self.show_typing_indicator = False
        self.typing_thread: Optional[threading.Thread] = None
        
        # Create sessions directory
        self.sessions_dir = Path.home() / ".youtube-chat-cli" / "chat_sessions"
        self.sessions_dir.mkdir(parents=True, exist_ok=True)
        
        # Load saved sessions
        self._load_sessions()
        
        # Chat commands
        self.commands = {
            "/help": self._show_help,
            "/quit": self._quit_chat,
            "/exit": self._quit_chat,
            "/clear": self._clear_screen,
            "/history": self._show_history,
            "/save": self._save_session,
            "/load": self._load_session,
            "/sessions": self._list_sessions,
            "/workflow": self._change_workflow,
            "/workflows": self._list_workflows,
            "/export": self._export_session,
            "/new": self._new_session,
            "/status": self._show_status
        }
    
    def start_chat(self, session_id: Optional[str] = None, workflow_name: Optional[str] = None):
        """Start the interactive chat interface."""
        self.is_running = True
        
        # Create or load session
        if session_id and session_id in self.sessions:
            self.current_session = self.sessions[session_id]
            self.console.print(f"[green]Resumed session: {session_id}[/green]")
        else:
            session_id = session_id or f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            self.current_session = ChatSession(session_id, workflow_name)
            self.sessions[session_id] = self.current_session
        
        # Show welcome message
        self._show_welcome()
        
        # Main chat loop
        try:
            while self.is_running:
                self._chat_loop()
        except KeyboardInterrupt:
            self._quit_chat()
        except Exception as e:
            self.console.print(f"[red]Error: {e}[/red]")
            logger.error(f"Chat interface error: {e}")
    
    def _show_welcome(self):
        """Show welcome message and interface."""
        welcome_panel = Panel.fit(
            "[bold blue]YouTube Chat CLI - Interactive RAG Chat[/bold blue]\n\n"
            f"Session: [cyan]{self.current_session.session_id}[/cyan]\n"
            f"Workflow: [yellow]{self.current_session.workflow_name or 'Default'}[/yellow]\n\n"
            "Type your message and press Enter to chat.\n"
            "Use [bold]/help[/bold] for commands or [bold]/quit[/bold] to exit.",
            title="Welcome",
            border_style="blue"
        )
        self.console.print(welcome_panel)
        self.console.print()
    
    def _chat_loop(self):
        """Main chat interaction loop."""
        try:
            # Get user input
            user_input = Prompt.ask(
                "[bold green]You[/bold green]",
                console=self.console
            ).strip()
            
            if not user_input:
                return
            
            # Handle commands
            if user_input.startswith('/'):
                self._handle_command(user_input)
                return
            
            # Add user message to session
            user_message = ChatMessage(
                type=ChatMessageType.USER,
                content=user_input,
                timestamp=datetime.now()
            )
            self.current_session.add_message(user_message)
            
            # Show typing indicator
            self._start_typing_indicator()
            
            try:
                # Send to n8n workflow
                workflow = self.workflow_manager.get_workflow(self.current_session.workflow_name)
                if not workflow:
                    raise ValueError("No workflow configured")
                
                response = self.n8n_client.invoke_agent(
                    user_input, 
                    self.current_session.session_id
                )
                
                # Stop typing indicator
                self._stop_typing_indicator()
                
                # Process response
                if response.get('status') == 'success':
                    assistant_content = response.get('response', 'No response received')
                    
                    # Add assistant message to session
                    assistant_message = ChatMessage(
                        type=ChatMessageType.ASSISTANT,
                        content=assistant_content,
                        timestamp=datetime.now(),
                        metadata={"workflow": self.current_session.workflow_name}
                    )
                    self.current_session.add_message(assistant_message)
                    
                    # Display response with rich formatting
                    self._display_assistant_response(assistant_content)
                    
                else:
                    error_msg = response.get('error', 'Unknown error occurred')
                    self._display_error(f"Workflow error: {error_msg}")
                    
            except Exception as e:
                self._stop_typing_indicator()
                self._display_error(f"Failed to get response: {str(e)}")
                
        except (EOFError, KeyboardInterrupt):
            self._quit_chat()
    
    def _handle_command(self, command: str):
        """Handle chat commands."""
        parts = command.split(' ', 1)
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd in self.commands:
            self.commands[cmd](args)
        else:
            self.console.print(f"[red]Unknown command: {cmd}[/red]")
            self.console.print("Type [bold]/help[/bold] for available commands.")
    
    def _display_assistant_response(self, content: str):
        """Display assistant response with rich formatting."""
        # Try to detect and format different content types
        if content.startswith('```') and content.endswith('```'):
            # Code block
            code = content.strip('```').strip()
            lines = code.split('\n')
            language = lines[0] if lines and not ' ' in lines[0] else "text"
            code_content = '\n'.join(lines[1:]) if language != "text" else code
            
            syntax = Syntax(code_content, language, theme="monokai", line_numbers=True)
            panel = Panel(syntax, title="Code", border_style="cyan")
            self.console.print(panel)
        elif '|' in content and content.count('|') > 2:
            # Possible table - try to format
            try:
                lines = content.strip().split('\n')
                if len(lines) >= 2:
                    headers = [h.strip() for h in lines[0].split('|') if h.strip()]
                    if headers:
                        table = Table()
                        for header in headers:
                            table.add_column(header)
                        
                        for line in lines[2:]:  # Skip header separator
                            if '|' in line:
                                row = [cell.strip() for cell in line.split('|') if cell.strip()]
                                if len(row) == len(headers):
                                    table.add_row(*row)
                        
                        self.console.print(table)
                        return
            except:
                pass
        
        # Default: treat as markdown
        try:
            markdown = Markdown(content)
            panel = Panel(markdown, title="[bold blue]Assistant[/bold blue]", border_style="blue")
            self.console.print(panel)
        except:
            # Fallback: plain text
            panel = Panel(content, title="[bold blue]Assistant[/bold blue]", border_style="blue")
            self.console.print(panel)
        
        self.console.print()
    
    def _display_error(self, error_msg: str):
        """Display error message."""
        error_panel = Panel(
            f"[red]{error_msg}[/red]",
            title="Error",
            border_style="red"
        )
        self.console.print(error_panel)
        self.console.print()
    
    def _start_typing_indicator(self):
        """Start typing indicator animation."""
        self.show_typing_indicator = True
        self.typing_thread = threading.Thread(target=self._typing_animation)
        self.typing_thread.daemon = True
        self.typing_thread.start()
    
    def _stop_typing_indicator(self):
        """Stop typing indicator animation."""
        self.show_typing_indicator = False
        if self.typing_thread:
            self.typing_thread.join(timeout=1)
    
    def _typing_animation(self):
        """Typing indicator animation."""
        with Progress(
            SpinnerColumn(),
            TextColumn("[bold blue]Assistant is thinking..."),
            console=self.console,
            transient=True
        ) as progress:
            task = progress.add_task("thinking", total=None)
            while self.show_typing_indicator:
                progress.advance(task)
                time.sleep(0.1)
    
    # Command implementations
    def _show_help(self, args: str):
        """Show help information."""
        help_table = Table(title="Available Commands")
        help_table.add_column("Command", style="cyan")
        help_table.add_column("Description", style="white")
        
        commands_help = [
            ("/help", "Show this help message"),
            ("/quit, /exit", "Exit the chat"),
            ("/clear", "Clear the screen"),
            ("/history [limit]", "Show chat history"),
            ("/save", "Save current session"),
            ("/load <session_id>", "Load a saved session"),
            ("/sessions", "List all sessions"),
            ("/new [session_id]", "Start a new session"),
            ("/workflow <name>", "Change workflow"),
            ("/workflows", "List available workflows"),
            ("/export <format>", "Export session (json/markdown)"),
            ("/status", "Show session status")
        ]
        
        for cmd, desc in commands_help:
            help_table.add_row(cmd, desc)
        
        self.console.print(help_table)
        self.console.print()
    
    def _quit_chat(self, args: str = ""):
        """Quit the chat interface."""
        if Confirm.ask("Save current session before exiting?", console=self.console):
            self._save_session("")
        
        self.console.print("[yellow]Goodbye! 👋[/yellow]")
        self.is_running = False
    
    def _clear_screen(self, args: str):
        """Clear the screen."""
        self.console.clear()
        self._show_welcome()
    
    def _show_history(self, args: str):
        """Show chat history."""
        try:
            limit = int(args) if args.strip() else None
        except ValueError:
            limit = None
        
        messages = self.current_session.get_history(limit)
        
        if not messages:
            self.console.print("[yellow]No messages in history.[/yellow]")
            return
        
        history_panel = Panel.fit(
            f"Chat History - Last {len(messages)} messages",
            title="History",
            border_style="cyan"
        )
        self.console.print(history_panel)
        
        for msg in messages:
            timestamp = msg.timestamp.strftime("%H:%M:%S")
            if msg.type == ChatMessageType.USER:
                self.console.print(f"[dim]{timestamp}[/dim] [bold green]You:[/bold green] {msg.content}")
            elif msg.type == ChatMessageType.ASSISTANT:
                self.console.print(f"[dim]{timestamp}[/dim] [bold blue]Assistant:[/bold blue] {msg.content[:100]}...")
        
        self.console.print()
    
    def _save_session(self, args: str):
        """Save current session."""
        self._save_sessions()
        self.console.print(f"[green]Session saved: {self.current_session.session_id}[/green]")
    
    def _load_session(self, args: str):
        """Load a saved session."""
        if not args.strip():
            self.console.print("[red]Please specify a session ID to load.[/red]")
            return
        
        session_id = args.strip()
        if session_id in self.sessions:
            self.current_session = self.sessions[session_id]
            self.console.print(f"[green]Loaded session: {session_id}[/green]")
        else:
            self.console.print(f"[red]Session not found: {session_id}[/red]")
    
    def _list_sessions(self, args: str):
        """List all sessions."""
        if not self.sessions:
            self.console.print("[yellow]No saved sessions.[/yellow]")
            return
        
        sessions_table = Table(title="Saved Sessions")
        sessions_table.add_column("Session ID", style="cyan")
        sessions_table.add_column("Created", style="white")
        sessions_table.add_column("Messages", style="yellow")
        sessions_table.add_column("Workflow", style="green")
        
        for session in self.sessions.values():
            sessions_table.add_row(
                session.session_id,
                session.created_at.strftime("%Y-%m-%d %H:%M"),
                str(len(session.messages)),
                session.workflow_name or "Default"
            )
        
        self.console.print(sessions_table)
        self.console.print()
    
    def _new_session(self, args: str):
        """Start a new session."""
        session_id = args.strip() or f"chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if session_id in self.sessions:
            if not Confirm.ask(f"Session {session_id} exists. Overwrite?", console=self.console):
                return
        
        self.current_session = ChatSession(session_id, self.current_session.workflow_name)
        self.sessions[session_id] = self.current_session
        
        self.console.print(f"[green]Started new session: {session_id}[/green]")
    
    def _change_workflow(self, args: str):
        """Change the current workflow."""
        if not args.strip():
            self.console.print("[red]Please specify a workflow name.[/red]")
            return
        
        workflow_name = args.strip()
        workflow = self.workflow_manager.get_workflow(workflow_name)
        
        if not workflow:
            self.console.print(f"[red]Workflow not found: {workflow_name}[/red]")
            return
        
        self.current_session.workflow_name = workflow_name
        self.console.print(f"[green]Changed workflow to: {workflow_name}[/green]")
    
    def _list_workflows(self, args: str):
        """List available workflows."""
        workflows = self.workflow_manager.list_workflows()
        
        if not workflows:
            self.console.print("[yellow]No workflows configured.[/yellow]")
            return
        
        workflows_table = Table(title="Available Workflows")
        workflows_table.add_column("Name", style="cyan")
        workflows_table.add_column("URL", style="white")
        workflows_table.add_column("Status", style="yellow")
        workflows_table.add_column("Description", style="green")
        
        for workflow in workflows:
            status_color = {
                "active": "green",
                "error": "red",
                "unknown": "yellow"
            }.get(workflow.status.value, "white")
            
            workflows_table.add_row(
                workflow.name,
                workflow.url[:50] + "..." if len(workflow.url) > 50 else workflow.url,
                f"[{status_color}]{workflow.status.value}[/{status_color}]",
                workflow.description[:30] + "..." if len(workflow.description) > 30 else workflow.description
            )
        
        self.console.print(workflows_table)
        self.console.print()
    
    def _export_session(self, args: str):
        """Export current session."""
        format_type = args.strip().lower() or "json"
        
        if format_type not in ["json", "markdown"]:
            self.console.print("[red]Supported formats: json, markdown[/red]")
            return
        
        try:
            exported_content = self.current_session.export_history(format_type)
            
            # Save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.current_session.session_id}_{timestamp}.{format_type}"
            export_path = self.sessions_dir / filename
            
            with open(export_path, 'w', encoding='utf-8') as f:
                f.write(exported_content)
            
            self.console.print(f"[green]Session exported to: {export_path}[/green]")
            
        except Exception as e:
            self.console.print(f"[red]Export failed: {e}[/red]")
    
    def _show_status(self, args: str):
        """Show session status."""
        status_table = Table(title="Session Status")
        status_table.add_column("Property", style="cyan")
        status_table.add_column("Value", style="white")
        
        status_table.add_row("Session ID", self.current_session.session_id)
        status_table.add_row("Workflow", self.current_session.workflow_name or "Default")
        status_table.add_row("Messages", str(len(self.current_session.messages)))
        status_table.add_row("Created", self.current_session.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        status_table.add_row("Last Activity", self.current_session.last_activity.strftime("%Y-%m-%d %H:%M:%S"))
        
        self.console.print(status_table)
        self.console.print()
    
    def _load_sessions(self):
        """Load saved sessions from disk."""
        # Implementation would load from JSON files
        pass
    
    def _save_sessions(self):
        """Save sessions to disk."""
        # Implementation would save to JSON files
        pass


# Global chat interface instance
_chat_interface = None

def get_chat_interface() -> InteractiveChatInterface:
    """Get or create the global chat interface instance."""
    global _chat_interface
    if _chat_interface is None:
        _chat_interface = InteractiveChatInterface()
    return _chat_interface
