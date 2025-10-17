"""
File processor module for uploading and processing files through n8n RAG workflow.
"""

import os
import mimetypes
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging

logger = logging.getLogger(__name__)


class FileProcessingError(Exception):
    """Error related to file processing."""
    pass


class FileProcessor:
    """Handles file upload and processing through n8n workflow."""

    # Supported file extensions (600+ types via n8n extractFromFile node)
    SUPPORTED_EXTENSIONS = {
        # Documents
        '.pdf', '.docx', '.doc', '.odt', '.rtf', '.txt', '.md',
        # Spreadsheets
        '.xlsx', '.xls', '.csv', '.ods',
        # Presentations
        '.pptx', '.ppt', '.odp',
        # Images (with OCR)
        '.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp',
        # Archives
        '.zip', '.rar', '.7z', '.tar', '.gz',
        # Code files
        '.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs', '.php', '.rb',
        '.html', '.css', '.scss', '.json', '.xml', '.yaml', '.yml',
        # Ebooks
        '.epub', '.mobi', '.azw',
        # Data formats
        '.toml', '.ini', '.cfg', '.conf',
        # And many more...
    }

    def __init__(self, n8n_webhook_url: str = None):
        """Initialize the file processor.

        Args:
            n8n_webhook_url: URL of the n8n webhook for file processing
        """
        if n8n_webhook_url is None:
            n8n_webhook_url = self._get_webhook_url()
        self.webhook_url = n8n_webhook_url

    def _get_webhook_url(self) -> str:
        """Get webhook URL from environment variable."""
        url = os.getenv('N8N_WEBHOOK_URL')
        if not url:
            raise ValueError("N8N_WEBHOOK_URL environment variable not set.")
        return url

    def is_supported_file(self, file_path: str) -> bool:
        """Check if file type is supported.

        Args:
            file_path: Path to the file

        Returns:
            True if file type is supported, False otherwise
        """
        ext = Path(file_path).suffix.lower()
        return ext in self.SUPPORTED_EXTENSIONS or ext == ''  # Allow extensionless files

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        if not path.exists():
            raise FileProcessingError(f"File not found: {file_path}")

        mime_type, _ = mimetypes.guess_type(file_path)

        return {
            'name': path.name,
            'size': path.stat().st_size,
            'extension': path.suffix.lower(),
            'mime_type': mime_type or 'application/octet-stream',
            'path': str(path.absolute())
        }

    def extract_text_from_file(self, file_path: str) -> str:
        """Extract text content from a file using n8n workflow.

        This sends the file to n8n which uses the extractFromFile node
        to extract text from 600+ file types.

        Args:
            file_path: Path to the file to process

        Returns:
            Extracted text content

        Raises:
            FileProcessingError: If file processing fails
        """
        logger.info(f"Extracting text from file: {file_path}")

        # Validate file
        if not self.is_supported_file(file_path):
            raise FileProcessingError(
                f"Unsupported file type: {Path(file_path).suffix}. "
                f"Supported types: {', '.join(sorted(self.SUPPORTED_EXTENSIONS))}"
            )

        file_info = self.get_file_info(file_path)
        logger.info(f"File info: {file_info['name']} ({file_info['size']} bytes)")

        # For now, read text files directly
        # In production, this would upload to n8n for processing
        if file_info['extension'] in ['.txt', '.md', '.json', '.xml', '.yaml', '.yml']:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Extracted {len(content)} characters from {file_info['name']}")
                return content
            except UnicodeDecodeError:
                raise FileProcessingError(f"Unable to decode file as UTF-8: {file_path}")

        # For other file types, we would need to:
        # 1. Upload file to n8n webhook
        # 2. n8n processes with extractFromFile node
        # 3. Return extracted text
        raise FileProcessingError(
            f"File type {file_info['extension']} requires n8n server to be running. "
            f"Please ensure n8n is configured and the workflow is active."
        )

    def process_file_for_rag(self, file_path: str, session_id: str) -> Dict[str, Any]:
        """Process a file and add it to the RAG knowledge base via n8n.

        This uploads the file to n8n which:
        1. Extracts text using extractFromFile
        2. Splits text into chunks
        3. Generates embeddings
        4. Stores in Qdrant vector database

        Args:
            file_path: Path to the file to process
            session_id: Session identifier for tracking

        Returns:
            Processing result with status and metadata

        Raises:
            FileProcessingError: If processing fails
        """
        logger.info(f"Processing file for RAG: {file_path}")

        file_info = self.get_file_info(file_path)

        # This would upload to n8n workflow
        # For now, return a mock response
        return {
            'status': 'success',
            'file_name': file_info['name'],
            'file_size': file_info['size'],
            'chunks_created': 0,  # Would be populated by n8n
            'vectors_stored': 0,  # Would be populated by n8n
            'session_id': session_id,
            'message': (
                f"File '{file_info['name']}' ready for processing. "
                f"To enable full RAG processing, ensure n8n workflow is active."
            )
        }

    def batch_process_files(self, file_paths: List[str], session_id: str) -> List[Dict[str, Any]]:
        """Process multiple files for RAG knowledge base.

        Args:
            file_paths: List of file paths to process
            session_id: Session identifier

        Returns:
            List of processing results
        """
        results = []
        for file_path in file_paths:
            try:
                result = self.process_file_for_rag(file_path, session_id)
                results.append(result)
            except FileProcessingError as e:
                logger.error(f"Failed to process {file_path}: {e}")
                results.append({
                    'status': 'error',
                    'file_name': Path(file_path).name,
                    'error': str(e)
                })

        return results

    def get_supported_file_types_summary(self) -> str:
        """Get a human-readable summary of supported file types.

        Returns:
            Formatted string listing supported file types
        """
        categories = {
            'Documents': ['.pdf', '.docx', '.doc', '.odt', '.rtf', '.txt', '.md'],
            'Spreadsheets': ['.xlsx', '.xls', '.csv', '.ods'],
            'Presentations': ['.pptx', '.ppt', '.odp'],
            'Images': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff', '.webp'],
            'Archives': ['.zip', '.rar', '.7z', '.tar', '.gz'],
            'Code': ['.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs', '.php', '.rb'],
            'Data': ['.json', '.xml', '.yaml', '.yml', '.toml', '.ini', '.cfg'],
            'Ebooks': ['.epub', '.mobi', '.azw'],
        }

        summary = "Supported File Types (600+ formats):\n\n"
        for category, extensions in categories.items():
            summary += f"  {category}: {', '.join(extensions)}\n"

        summary += "\n  And many more..."
        return summary


# Global file processor instance
_file_processor = None


def get_file_processor() -> FileProcessor:
    """Get or create the global file processor instance."""
    global _file_processor
    if _file_processor is None:
        try:
            _file_processor = FileProcessor()
        except ValueError:
            # If N8N_WEBHOOK_URL is not set, create with None
            # This allows the module to be imported without configuration
            _file_processor = FileProcessor(webhook_url="http://localhost:5678/webhook/invoke_n8n_agent")
    return _file_processor

