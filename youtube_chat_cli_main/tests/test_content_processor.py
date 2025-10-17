"""
Unit tests for the Content Processor Service.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from pathlib import Path

from youtube_chat_cli_main.services.content_processor import (
    ContentProcessor,
    ContentProcessingError
)


class TestContentProcessor:
    """Test suite for ContentProcessor."""
    
    @pytest.fixture
    def mock_config(self):
        """Mock configuration."""
        config = Mock()
        config.ocr_provider = "tesseract"
        config.tesseract_path = None
        config.chunk_size = 1000
        config.chunk_overlap = 200
        return config
    
    @pytest.fixture
    def mock_database(self):
        """Mock database."""
        db = Mock()
        db.get_queue_item.return_value = {
            "id": 1,
            "file_id": "test.pdf",
            "file_name": "test.pdf",
            "source": "local",
            "status": "pending"
        }
        return db
    
    @pytest.fixture
    def mock_vector_store(self):
        """Mock vector store."""
        vs = Mock()
        vs.add_documents.return_value = ["doc1", "doc2"]
        return vs
    
    @pytest.fixture
    def processor(self, mock_config, mock_database, mock_vector_store):
        """Create content processor with mocked dependencies."""
        with patch('youtube_chat_cli_main.services.content_processor.get_config', return_value=mock_config), \
             patch('youtube_chat_cli_main.services.content_processor.get_database', return_value=mock_database), \
             patch('youtube_chat_cli_main.services.content_processor.get_vector_store', return_value=mock_vector_store):
            processor = ContentProcessor()
            return processor
    
    def test_initialization(self, processor):
        """Test content processor initialization."""
        assert processor is not None
        assert processor.config is not None
        assert processor.db is not None
        assert processor.vector_store is not None
    
    def test_detect_file_type_pdf(self, processor):
        """Test PDF file type detection."""
        file_type = processor._detect_file_type("document.pdf")
        assert file_type == "pdf"
    
    def test_detect_file_type_docx(self, processor):
        """Test DOCX file type detection."""
        file_type = processor._detect_file_type("document.docx")
        assert file_type == "docx"
    
    def test_detect_file_type_markdown(self, processor):
        """Test Markdown file type detection."""
        file_type = processor._detect_file_type("README.md")
        assert file_type == "markdown"
    
    def test_detect_file_type_image(self, processor):
        """Test image file type detection."""
        assert processor._detect_file_type("image.png") == "image"
        assert processor._detect_file_type("photo.jpg") == "image"
        assert processor._detect_file_type("picture.jpeg") == "image"
    
    def test_detect_file_type_unsupported(self, processor):
        """Test unsupported file type detection."""
        with pytest.raises(ContentProcessingError, match="Unsupported file type"):
            processor._detect_file_type("file.xyz")
    
    @patch('builtins.open', new_callable=mock_open, read_data="Test text content")
    def test_process_text_file(self, mock_file, processor):
        """Test processing text file."""
        content = processor._process_text_file("test.txt")
        
        assert content == "Test text content"
        mock_file.assert_called_once()
    
    @patch('builtins.open', new_callable=mock_open, read_data="# Heading\n\nTest markdown content")
    def test_process_markdown_file(self, mock_file, processor):
        """Test processing markdown file."""
        content = processor._process_markdown_file("test.md")
        
        assert "Heading" in content
        assert "Test markdown content" in content
    
    @patch('youtube_chat_cli_main.services.content_processor.html2text.HTML2Text')
    @patch('builtins.open', new_callable=mock_open, read_data="<html><body><h1>Test</h1></body></html>")
    def test_process_html_file(self, mock_file, mock_html2text, processor):
        """Test processing HTML file."""
        mock_converter = Mock()
        mock_converter.handle.return_value = "# Test\n"
        mock_html2text.return_value = mock_converter
        
        content = processor._process_html_file("test.html")
        
        assert content == "# Test\n"
        mock_converter.handle.assert_called_once()
    
    @patch('youtube_chat_cli_main.services.content_processor.PyPDF2.PdfReader')
    @patch('builtins.open', new_callable=mock_open)
    def test_process_pdf_file(self, mock_file, mock_pdf_reader, processor):
        """Test processing PDF file."""
        mock_page = Mock()
        mock_page.extract_text.return_value = "PDF page content"
        
        mock_reader = Mock()
        mock_reader.pages = [mock_page, mock_page]
        mock_pdf_reader.return_value = mock_reader
        
        content = processor._process_pdf_file("test.pdf")
        
        assert "PDF page content" in content
        assert mock_page.extract_text.call_count == 2
    
    @patch('youtube_chat_cli_main.services.content_processor.docx.Document')
    def test_process_docx_file(self, mock_docx, processor):
        """Test processing DOCX file."""
        mock_para1 = Mock()
        mock_para1.text = "Paragraph 1"
        mock_para2 = Mock()
        mock_para2.text = "Paragraph 2"
        
        mock_doc = Mock()
        mock_doc.paragraphs = [mock_para1, mock_para2]
        mock_docx.return_value = mock_doc
        
        content = processor._process_docx_file("test.docx")
        
        assert "Paragraph 1" in content
        assert "Paragraph 2" in content
    
    def test_split_by_markdown_headings(self, processor):
        """Test markdown-aware text splitting."""
        content = """# Main Heading

This is the introduction.

## Section 1

Content for section 1.

## Section 2

Content for section 2.

### Subsection 2.1

Detailed content.
"""
        
        chunks = processor._split_by_markdown_headings(content)
        
        assert len(chunks) > 0
        # Verify chunks preserve heading structure
        assert any("Main Heading" in chunk.get("content", "") for chunk in chunks)
    
    def test_split_text_fallback(self, processor):
        """Test fallback text splitting for non-markdown content."""
        content = "A" * 5000  # Long text without markdown
        
        chunks = processor._split_text_fallback(content)
        
        assert len(chunks) > 1
        # Verify chunks are within size limits
        for chunk in chunks:
            assert len(chunk["content"]) <= processor.config.chunk_size + processor.config.chunk_overlap
    
    def test_process_queue_item_success(self, processor, mock_database, mock_vector_store):
        """Test successful queue item processing."""
        with patch.object(processor, '_process_file', return_value="Test content"), \
             patch.object(processor, '_split_by_markdown_headings', return_value=[
                 {"content": "Chunk 1", "metadata": {}},
                 {"content": "Chunk 2", "metadata": {}}
             ]):
            
            success = processor.process_queue_item(1)
            
            assert success is True
            mock_database.update_queue_status.assert_called_with(1, "completed")
            mock_vector_store.add_documents.assert_called_once()
    
    def test_process_queue_item_failure(self, processor, mock_database):
        """Test queue item processing failure."""
        with patch.object(processor, '_process_file', side_effect=Exception("Processing error")):
            
            success = processor.process_queue_item(1)
            
            assert success is False
            mock_database.update_queue_status.assert_called_with(1, "failed")
            mock_database.increment_queue_retry.assert_called_with(1)
    
    def test_process_queue_item_not_found(self, processor, mock_database):
        """Test processing non-existent queue item."""
        mock_database.get_queue_item.return_value = None
        
        success = processor.process_queue_item(999)
        
        assert success is False
    
    @patch('youtube_chat_cli_main.services.content_processor.pytesseract.image_to_string')
    @patch('youtube_chat_cli_main.services.content_processor.Image.open')
    def test_process_image_file_with_ocr(self, mock_image_open, mock_ocr, processor):
        """Test processing image file with OCR."""
        mock_image = Mock()
        mock_image_open.return_value = mock_image
        mock_ocr.return_value = "OCR extracted text"
        
        content = processor._process_image_file("test.png")
        
        assert content == "OCR extracted text"
        mock_ocr.assert_called_once_with(mock_image)
    
    def test_process_file_routes_to_correct_handler(self, processor):
        """Test that _process_file routes to correct handler based on file type."""
        with patch.object(processor, '_process_text_file', return_value="Text content") as mock_text:
            processor._process_file("test.txt")
            mock_text.assert_called_once()
        
        with patch.object(processor, '_process_pdf_file', return_value="PDF content") as mock_pdf:
            processor._process_file("test.pdf")
            mock_pdf.assert_called_once()
        
        with patch.object(processor, '_process_markdown_file', return_value="MD content") as mock_md:
            processor._process_file("test.md")
            mock_md.assert_called_once()
    
    def test_extract_metadata_from_file(self, processor):
        """Test metadata extraction from file."""
        with patch('youtube_chat_cli_main.services.content_processor.Path') as mock_path:
            mock_file = Mock()
            mock_file.name = "test.pdf"
            mock_file.suffix = ".pdf"
            mock_file.stat.return_value.st_size = 1024
            mock_path.return_value = mock_file
            
            metadata = processor._extract_metadata("test.pdf")
            
            assert metadata["file_name"] == "test.pdf"
            assert metadata["file_type"] == ".pdf"
            assert metadata["file_size"] == 1024

