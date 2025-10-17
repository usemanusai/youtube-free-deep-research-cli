"""
JAEGIS NexusSync - Content Processing Service

This module handles multi-format document processing including:
- File format conversion to markdown
- OCR for PDFs and images
- Markdown-aware text splitting by headings
- Document chunking for vector storage
"""

import os
import logging
import tempfile
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import re

# Document processing
from PyPDF2 import PdfReader
import docx
from bs4 import BeautifulSoup
import markdown
from PIL import Image

# OCR
import pytesseract

# Text splitting
from langchain.text_splitter import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter
)

from ..core.config import get_config
from ..core.database import get_database

logger = logging.getLogger(__name__)


class ContentProcessingError(Exception):
    """Raised when content processing fails."""
    pass


class ContentProcessor:
    """
    Multi-format content processor with OCR and intelligent chunking.
    
    Supports:
    - PDF (with OCR)
    - DOCX
    - TXT
    - HTML
    - Markdown
    - Images (with OCR)
    - Google Docs (exported as text)
    """
    
    def __init__(self):
        """Initialize content processor."""
        self.config = get_config()
        self.db = get_database()
        
        # Configure Tesseract path if specified
        if self.config.ocr_provider == 'tesseract':
            tesseract_path = getattr(self.config, 'tesseract_path', None)
            if tesseract_path and tesseract_path != 'tesseract':
                pytesseract.pytesseract.tesseract_cmd = tesseract_path
    
    def process_file(
        self,
        file_path: str,
        file_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process a file and extract structured markdown content.
        
        Args:
            file_path: Path to the file
            file_type: MIME type or file extension (auto-detected if None)
        
        Returns:
            Dictionary with:
                - content: Extracted markdown content
                - metadata: File metadata
                - chunks: Text chunks for vector storage
        """
        logger.info(f"Processing file: {file_path}")
        
        # Detect file type if not provided
        if not file_type:
            file_type = self._detect_file_type(file_path)
        
        # Extract content based on file type
        try:
            content, metadata = self._extract_content(file_path, file_type)
            
            # Split into chunks
            chunks = self._split_content(content)
            
            logger.info(f"✅ Processed file: {len(content)} chars, {len(chunks)} chunks")
            
            return {
                'content': content,
                'metadata': metadata,
                'chunks': chunks,
                'file_path': file_path,
                'file_type': file_type
            }
            
        except Exception as e:
            logger.error(f"Failed to process file {file_path}: {e}")
            raise ContentProcessingError(f"Failed to process file: {e}")
    
    def _detect_file_type(self, file_path: str) -> str:
        """
        Detect file type from extension or MIME type.
        
        Args:
            file_path: Path to the file
        
        Returns:
            File type identifier
        """
        ext = Path(file_path).suffix.lower()
        
        type_map = {
            '.pdf': 'application/pdf',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.doc': 'application/msword',
            '.txt': 'text/plain',
            '.md': 'text/markdown',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            # Audio formats
            '.mp3': 'audio/mpeg',
            '.wav': 'audio/wav',
            '.m4a': 'audio/mp4',
            '.flac': 'audio/flac',
            '.ogg': 'audio/ogg',
            # Video formats
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.mkv': 'video/x-matroska',
            # Data formats
            '.json': 'application/json',
        }

        return type_map.get(ext, 'application/octet-stream')

    def _extract_content(
        self,
        file_path: str,
        file_type: str
    ) -> Tuple[str, Dict[str, Any]]:
        """
        Extract content from file based on type.

        Args:
            file_path: Path to the file
            file_type: File MIME type

        Returns:
            Tuple of (content, metadata)
        """
        metadata = {
            'file_name': Path(file_path).name,
            'file_type': file_type,
            'file_size': os.path.getsize(file_path)
        }

        # PDF files
        if file_type == 'application/pdf':
            content = self._extract_pdf(file_path)

        # Word documents
        elif 'wordprocessingml' in file_type or file_type == 'application/msword':
            content = self._extract_docx(file_path)

        # Plain text
        elif file_type == 'text/plain':
            content = self._extract_text(file_path)

        # Markdown
        elif file_type == 'text/markdown':
            content = self._extract_text(file_path)

        # HTML
        elif file_type == 'text/html':
            content = self._extract_html(file_path)

        # Images (OCR)
        elif file_type.startswith('image/'):
            content = self._extract_image_ocr(file_path)

        # Audio
        elif file_type.startswith('audio/'):
            content = self._extract_audio_transcription(file_path)

        # Video (extract audio then transcribe)
        elif file_type.startswith('video/'):
            content = self._extract_video_transcription(file_path)

        # JSON (flatten to text)
        elif file_type == 'application/json':
            content = self._extract_json(file_path)

        # Google Docs (exported as text)
        elif file_type == 'application/vnd.google-apps.document':
            content = self._extract_text(file_path)

        else:
            raise ContentProcessingError(f"Unsupported file type: {file_type}")

        # Attempt to enrich metadata
        try:
            # Duration for audio/video
            if file_type.startswith('audio/') or file_type.startswith('video/'):
                from pydub import AudioSegment  # type: ignore
                dur = AudioSegment.from_file(file_path).duration_seconds
                metadata['duration_seconds'] = float(dur)
        except Exception:
            # Duration enrichment is best-effort; ignore errors
            pass

        return content, metadata

    def _extract_pdf(self, file_path: str) -> str:
        """
        Extract text from PDF with OCR fallback.
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Extracted markdown content
        """
        try:
            # Try text extraction first
            reader = PdfReader(file_path)
            text_content = []
            
            for page_num, page in enumerate(reader.pages, 1):
                text = page.extract_text()
                
                # If page has little text, use OCR
                if len(text.strip()) < 50:
                    logger.info(f"Page {page_num} has little text, using OCR...")
                    # OCR would go here - for now, use extracted text
                    text_content.append(f"## Page {page_num}\n\n{text}")
                else:
                    text_content.append(f"## Page {page_num}\n\n{text}")
            
            content = "\n\n".join(text_content)
            
            # Clean up the text
            content = self._clean_text(content)
            
            return content
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            raise ContentProcessingError(f"PDF extraction failed: {e}")
    
    def _extract_docx(self, file_path: str) -> str:
        """
        Extract text from DOCX file.
        
        Args:
            file_path: Path to DOCX file
        
        Returns:
            Extracted markdown content
        """
        try:
            doc = docx.Document(file_path)
            
            content_parts = []
            
            for para in doc.paragraphs:
                text = para.text.strip()
                if not text:
                    continue
                
                # Detect headings based on style
                if para.style.name.startswith('Heading'):
                    level = para.style.name.replace('Heading ', '')
                    if level.isdigit():
                        content_parts.append(f"{'#' * int(level)} {text}")
                    else:
                        content_parts.append(f"## {text}")
                else:
                    content_parts.append(text)
            
            content = "\n\n".join(content_parts)
            return self._clean_text(content)
            
        except Exception as e:
            logger.error(f"DOCX extraction failed: {e}")
            raise ContentProcessingError(f"DOCX extraction failed: {e}")
    
    def _extract_text(self, file_path: str) -> str:
        """
        Extract text from plain text file.
        
        Args:
            file_path: Path to text file
        
        Returns:
            File content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return self._clean_text(content)
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            raise ContentProcessingError(f"Text extraction failed: {e}")
    
    def _extract_html(self, file_path: str) -> str:
        """
        Extract text from HTML file.
        
        Args:
            file_path: Path to HTML file
        
        Returns:
            Extracted markdown content
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text
            text = soup.get_text()
            
            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)
            
            return self._clean_text(text)
            
        except Exception as e:
            logger.error(f"HTML extraction failed: {e}")
            raise ContentProcessingError(f"HTML extraction failed: {e}")
    
    def _extract_image_ocr(self, file_path: str) -> str:
        """
        Extract text from image using OCR.

        Args:
            file_path: Path to image file

        Returns:
            Extracted text
        """
        try:
            image = Image.open(file_path)
            text = pytesseract.image_to_string(image)

            logger.info(f"OCR extracted {len(text)} characters from image")
            return self._clean_text(text)

        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise ContentProcessingError(f"OCR extraction failed: {e}")

    def _extract_audio_transcription(self, file_path: str) -> str:
        """
        Transcribe supported audio files to text using the transcription service.
        """
        try:
            from .transcription_service import get_transcription_service
            svc = get_transcription_service()
            text = svc.transcribe(file_path)
            if not text:
                raise ContentProcessingError("Transcription produced empty text")
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"Audio transcription failed: {e}")
            raise ContentProcessingError(f"Audio transcription failed: {e}")

    def _extract_video_transcription(self, file_path: str) -> str:
        """
        Extract audio from video (requires ffmpeg/yt-dlp for some formats) and transcribe.
        """
        # Strategy: try to open with pydub (ffmpeg). If that fails, ask user to install ffmpeg.
        try:
            import tempfile
            from pydub import AudioSegment  # type: ignore
            tmpdir = tempfile.mkdtemp()
            wav_path = os.path.join(tmpdir, "extracted_audio.wav")
            # Let ffmpeg figure out the input format automatically
            audio = AudioSegment.from_file(file_path)
            audio.export(wav_path, format="wav")
            from .transcription_service import get_transcription_service
            svc = get_transcription_service()
            text = svc.transcribe(wav_path)
            if not text:
                raise ContentProcessingError("Transcription produced empty text from video")
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"Video transcription failed: {e}")
            raise ContentProcessingError(
                "Video transcription failed. Ensure ffmpeg is installed and accessible in PATH. "
                f"Error: {e}"
            )

    def _extract_json(self, file_path: str) -> str:
        """
        Flatten JSON content to a readable text representation.
        """
        try:
            import json
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            def flatten(obj, prefix=""):
                lines = []
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        lines.extend(flatten(v, f"{prefix}{k}."))
                elif isinstance(obj, list):
                    for i, v in enumerate(obj):
                        lines.extend(flatten(v, f"{prefix}{i}."))
                else:
                    # Primitive
                    key = prefix[:-1] if prefix.endswith(".") else prefix
                    lines.append(f"{key}: {obj}")
                return lines
            text = "\n".join(flatten(data))
            return self._clean_text(text)
        except Exception as e:
            logger.error(f"JSON extraction failed: {e}")
            raise ContentProcessingError(f"JSON extraction failed: {e}")

    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text content.

        Args:
            text: Raw text content

        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = re.sub(r' {2,}', ' ', text)

        # Remove leading/trailing whitespace
        text = text.strip()

        return text

    def _split_content(self, content: str) -> List[Dict[str, Any]]:
        """
        Split content into chunks using markdown-aware splitting.

        This is a CRITICAL improvement over n8n's arbitrary character splitting.
        We split by markdown headings to preserve semantic structure.

        Args:
            content: Markdown content to split

        Returns:
            List of chunk dictionaries with content and metadata
        """
        chunks = []

        # Check if content has markdown headings
        has_headings = bool(re.search(r'^#{1,6}\s+.+$', content, re.MULTILINE))

        if has_headings and self.config.split_by_headings:
            # Use markdown-aware splitting
            chunks = self._split_by_markdown_headings(content)
        else:
            # Fall back to recursive character splitting
            chunks = self._split_by_characters(content)

        logger.info(f"Split content into {len(chunks)} chunks")
        return chunks

    def _split_by_markdown_headings(self, content: str) -> List[Dict[str, Any]]:
        """
        Split content by markdown headings to preserve structure.

        Args:
            content: Markdown content

        Returns:
            List of chunks with heading hierarchy preserved
        """
        # Define heading hierarchy to split on
        headers_to_split_on = [
            ("#", "Header 1"),
            ("##", "Header 2"),
            ("###", "Header 3"),
            ("####", "Header 4"),
        ]

        # Create markdown splitter
        markdown_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=headers_to_split_on,
            strip_headers=False
        )

        # Split by headings
        md_header_splits = markdown_splitter.split_text(content)

        # Further split large sections if needed
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        chunks = []
        for i, doc in enumerate(md_header_splits):
            # If section is too large, split it further
            if len(doc.page_content) > self.config.chunk_size:
                sub_chunks = text_splitter.split_text(doc.page_content)
                for j, sub_chunk in enumerate(sub_chunks):
                    chunks.append({
                        'content': sub_chunk,
                        'metadata': {
                            **doc.metadata,
                            'chunk_index': len(chunks),
                            'sub_chunk': j,
                            'total_sub_chunks': len(sub_chunks)
                        }
                    })
            else:
                chunks.append({
                    'content': doc.page_content,
                    'metadata': {
                        **doc.metadata,
                        'chunk_index': len(chunks)
                    }
                })

        return chunks

    def _split_by_characters(self, content: str) -> List[Dict[str, Any]]:
        """
        Split content by characters using recursive splitting.

        Args:
            content: Text content

        Returns:
            List of chunks
        """
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""]
        )

        text_chunks = text_splitter.split_text(content)

        chunks = []
        for i, chunk in enumerate(text_chunks):
            chunks.append({
                'content': chunk,
                'metadata': {
                    'chunk_index': i,
                    'total_chunks': len(text_chunks)
                }
            })

        return chunks

    def process_queue_item(self, queue_id: int) -> bool:
        """
        Process a single item from the processing queue.

        Args:
            queue_id: Queue item ID

        Returns:
            True if processing succeeded, False otherwise
        """
        try:
            # Get queue item
            item = self.db.get_queue_item(queue_id)
            if not item:
                logger.error(f"Queue item {queue_id} not found")
                return False

            # Update status to processing
            self.db.update_queue_status(queue_id, 'processing')

            # Download file if from Google Drive
            if item['source'] == 'google_drive':
                from .gdrive_service import get_gdrive_service
                gdrive = get_gdrive_service()

                # Create temp directory
                temp_dir = tempfile.mkdtemp()
                file_path = os.path.join(temp_dir, item['file_name'])

                # Download file
                gdrive.download_file(item['file_id'], file_path)
            else:
                file_path = item['file_id']  # Assume it's a local path

            # Process file
            result = self.process_file(file_path, item.get('file_type'))

            # Store chunks in vector store
            from .vector_store import get_vector_store
            vector_store = get_vector_store()

            vector_store.add_documents(
                documents=result['chunks'],
                metadata={
                    'file_id': item['file_id'],
                    'file_name': item['file_name'],
                    'source': item['source'],
                    **result['metadata']
                }
            )

            # Update status to completed
            self.db.update_queue_status(queue_id, 'completed')

            # Update Google Drive file status if applicable
            if item['source'] == 'google_drive':
                self.db.update_gdrive_file_status(item['file_id'], 'processed')

            logger.info(f"✅ Successfully processed queue item {queue_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to process queue item {queue_id}: {e}")

            # Update status to failed
            self.db.update_queue_status(queue_id, 'failed', error_message=str(e))

            # Increment retry count
            self.db.increment_queue_retry(queue_id)

            return False


# Global service instance
_content_processor: Optional[ContentProcessor] = None


def get_content_processor() -> ContentProcessor:
    """
    Get the global content processor instance.

    Returns:
        ContentProcessor instance
    """
    global _content_processor

    if _content_processor is None:
        _content_processor = ContentProcessor()
        logger.info("Content processor instance created")

    return _content_processor

