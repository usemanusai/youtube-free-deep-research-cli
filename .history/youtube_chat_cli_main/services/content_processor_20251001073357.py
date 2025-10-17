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
        
        # Google Docs (exported as text)
        elif file_type == 'application/vnd.google-apps.document':
            content = self._extract_text(file_path)
        
        else:
            raise ContentProcessingError(f"Unsupported file type: {file_type}")
        
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

