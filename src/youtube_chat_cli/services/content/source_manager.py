"""
Multi-source content processing and management system.
"""

import os
import logging
import mimetypes
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import json

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """Supported source types."""
    # Documents
    PDF = "pdf"
    DOCX = "docx"
    TXT = "txt"
    MD = "md"
    RTF = "rtf"
    ODT = "odt"
    
    # Spreadsheets
    CSV = "csv"
    XLSX = "xlsx"
    XLS = "xls"
    ODS = "ods"
    
    # Audio
    MP3 = "mp3"
    WAV = "wav"
    M4A = "m4a"
    FLAC = "flac"
    OGG = "ogg"
    
    # Video
    MP4 = "mp4"
    AVI = "avi"
    MOV = "mov"
    MKV = "mkv"
    WEBM = "webm"
    
    # Web
    URL = "url"
    HTML = "html"
    
    # YouTube
    YOUTUBE_VIDEO = "youtube_video"
    YOUTUBE_PLAYLIST = "youtube_playlist"
    YOUTUBE_CHANNEL = "youtube_channel"
    
    # Presentations
    PPTX = "pptx"
    PPT = "ppt"
    ODP = "odp"
    
    # Code
    PY = "py"
    JS = "js"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"
    
    # Images
    PNG = "png"
    JPG = "jpg"
    JPEG = "jpeg"
    
    # Directories
    DIRECTORY = "directory"
    GOOGLE_DRIVE = "google_drive"


class SourceLocation(Enum):
    """Source location types."""
    LOCAL = "local"
    GOOGLE_DRIVE = "google_drive"
    WEB = "web"
    YOUTUBE = "youtube"
    DROPBOX = "dropbox"
    ONEDRIVE = "onedrive"


@dataclass
class SourceFilter:
    """Filter configuration for source selection."""
    date_range: Optional[tuple] = None  # (start_date, end_date)
    file_types: Optional[Set[SourceType]] = None
    locations: Optional[Set[SourceLocation]] = None
    tags: Optional[Set[str]] = None
    size_range: Optional[tuple] = None  # (min_bytes, max_bytes)
    exclude_patterns: Optional[Set[str]] = None
    include_patterns: Optional[Set[str]] = None
    modified_since: Optional[datetime] = None
    created_since: Optional[datetime] = None


@dataclass
class SourceMetadata:
    """Metadata for a content source."""
    source_id: str
    path: str
    source_type: SourceType
    location: SourceLocation
    size: int
    created_at: datetime
    modified_at: datetime
    checksum: str
    tags: Set[str] = field(default_factory=set)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processed_at: Optional[datetime] = None
    processing_status: str = "pending"  # pending, processing, completed, failed
    error_message: Optional[str] = None


@dataclass
class ProcessedContent:
    """Processed content from a source."""
    source_id: str
    content_type: str
    text_content: str
    summary: Optional[str] = None
    key_points: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0
    word_count: int = 0
    language: Optional[str] = None


class SourceManager:
    """Manager for multi-source content processing."""
    
    def __init__(self, cache_dir: Optional[Path] = None):
        """Initialize the source manager."""
        self.cache_dir = cache_dir or Path.home() / ".youtube-chat-cli" / "sources"
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        self.metadata_file = self.cache_dir / "source_metadata.json"
        self.sources: Dict[str, SourceMetadata] = {}
        self.processed_content: Dict[str, ProcessedContent] = {}
        
        self._load_metadata()
        self._initialize_processors()
    
    def _load_metadata(self):
        """Load source metadata from cache."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for source_id, metadata_dict in data.get('sources', {}).items():
                        # Convert datetime strings back to datetime objects
                        metadata_dict['created_at'] = datetime.fromisoformat(metadata_dict['created_at'])
                        metadata_dict['modified_at'] = datetime.fromisoformat(metadata_dict['modified_at'])
                        if metadata_dict.get('processed_at'):
                            metadata_dict['processed_at'] = datetime.fromisoformat(metadata_dict['processed_at'])
                        
                        # Convert enums
                        metadata_dict['source_type'] = SourceType(metadata_dict['source_type'])
                        metadata_dict['location'] = SourceLocation(metadata_dict['location'])
                        metadata_dict['tags'] = set(metadata_dict.get('tags', []))
                        
                        self.sources[source_id] = SourceMetadata(**metadata_dict)
            except Exception as e:
                logger.warning(f"Failed to load source metadata: {e}")
    
    def _save_metadata(self):
        """Save source metadata to cache."""
        try:
            data = {'sources': {}}
            for source_id, metadata in self.sources.items():
                metadata_dict = {
                    'source_id': metadata.source_id,
                    'path': metadata.path,
                    'source_type': metadata.source_type.value,
                    'location': metadata.location.value,
                    'size': metadata.size,
                    'created_at': metadata.created_at.isoformat(),
                    'modified_at': metadata.modified_at.isoformat(),
                    'checksum': metadata.checksum,
                    'tags': list(metadata.tags),
                    'metadata': metadata.metadata,
                    'processing_status': metadata.processing_status,
                    'error_message': metadata.error_message
                }
                if metadata.processed_at:
                    metadata_dict['processed_at'] = metadata.processed_at.isoformat()
                
                data['sources'][source_id] = metadata_dict
            
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save source metadata: {e}")
    
    def _initialize_processors(self):
        """Initialize content processors for different source types."""
        self.processors = {
            # Document processors
            SourceType.PDF: self._process_pdf,
            SourceType.DOCX: self._process_docx,
            SourceType.TXT: self._process_text,
            SourceType.MD: self._process_markdown,
            SourceType.RTF: self._process_rtf,
            
            # Spreadsheet processors
            SourceType.CSV: self._process_csv,
            SourceType.XLSX: self._process_excel,
            
            # Audio/Video processors
            SourceType.MP3: self._process_audio,
            SourceType.WAV: self._process_audio,
            SourceType.MP4: self._process_video,
            
            # Web processors
            SourceType.URL: self._process_url,
            SourceType.HTML: self._process_html,
            
            # YouTube processors
            SourceType.YOUTUBE_VIDEO: self._process_youtube_video,
            SourceType.YOUTUBE_PLAYLIST: self._process_youtube_playlist,
            SourceType.YOUTUBE_CHANNEL: self._process_youtube_channel,
            
            # Code processors
            SourceType.PY: self._process_code,
            SourceType.JS: self._process_code,
            SourceType.JSON: self._process_json,
            
            # Image processors
            SourceType.PNG: self._process_image,
            SourceType.JPG: self._process_image,
        }
    
    def add_source(self, path: str, location: SourceLocation = SourceLocation.LOCAL, 
                   tags: Optional[Set[str]] = None) -> str:
        """Add a new source for processing."""
        source_id = self._generate_source_id(path)
        
        # Determine source type
        source_type = self._detect_source_type(path)
        
        # Get file metadata
        if location == SourceLocation.LOCAL and os.path.exists(path):
            stat = os.stat(path)
            size = stat.st_size
            created_at = datetime.fromtimestamp(stat.st_ctime)
            modified_at = datetime.fromtimestamp(stat.st_mtime)
            checksum = self._calculate_checksum(path)
        else:
            # For remote sources, use current time and placeholder values
            size = 0
            created_at = datetime.now()
            modified_at = datetime.now()
            checksum = hashlib.md5(path.encode()).hexdigest()
        
        metadata = SourceMetadata(
            source_id=source_id,
            path=path,
            source_type=source_type,
            location=location,
            size=size,
            created_at=created_at,
            modified_at=modified_at,
            checksum=checksum,
            tags=tags or set()
        )
        
        self.sources[source_id] = metadata
        self._save_metadata()
        
        logger.info(f"Added source: {path} (ID: {source_id})")
        return source_id
    
    def _generate_source_id(self, path: str) -> str:
        """Generate a unique source ID."""
        return hashlib.md5(path.encode()).hexdigest()[:12]
    
    def _detect_source_type(self, path: str) -> SourceType:
        """Detect the source type from path/URL."""
        if path.startswith(('http://', 'https://')):
            if 'youtube.com' in path or 'youtu.be' in path:
                if 'playlist' in path:
                    return SourceType.YOUTUBE_PLAYLIST
                elif 'channel' in path or '/c/' in path or '/user/' in path:
                    return SourceType.YOUTUBE_CHANNEL
                else:
                    return SourceType.YOUTUBE_VIDEO
            else:
                return SourceType.URL
        
        # Local file - detect by extension
        ext = Path(path).suffix.lower().lstrip('.')
        
        type_mapping = {
            'pdf': SourceType.PDF,
            'docx': SourceType.DOCX,
            'doc': SourceType.DOCX,
            'txt': SourceType.TXT,
            'md': SourceType.MD,
            'rtf': SourceType.RTF,
            'odt': SourceType.ODT,
            'csv': SourceType.CSV,
            'xlsx': SourceType.XLSX,
            'xls': SourceType.XLS,
            'ods': SourceType.ODS,
            'mp3': SourceType.MP3,
            'wav': SourceType.WAV,
            'm4a': SourceType.M4A,
            'flac': SourceType.FLAC,
            'ogg': SourceType.OGG,
            'mp4': SourceType.MP4,
            'avi': SourceType.AVI,
            'mov': SourceType.MOV,
            'mkv': SourceType.MKV,
            'webm': SourceType.WEBM,
            'html': SourceType.HTML,
            'htm': SourceType.HTML,
            'pptx': SourceType.PPTX,
            'ppt': SourceType.PPT,
            'odp': SourceType.ODP,
            'py': SourceType.PY,
            'js': SourceType.JS,
            'json': SourceType.JSON,
            'yaml': SourceType.YAML,
            'yml': SourceType.YAML,
            'xml': SourceType.XML,
            'png': SourceType.PNG,
            'jpg': SourceType.JPG,
            'jpeg': SourceType.JPEG,
        }
        
        return type_mapping.get(ext, SourceType.TXT)  # Default to text
    
    def _calculate_checksum(self, path: str) -> str:
        """Calculate MD5 checksum of a file."""
        try:
            hash_md5 = hashlib.md5()
            with open(path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate checksum for {path}: {e}")
            return ""

    def process_source(self, source_id: str) -> Optional[ProcessedContent]:
        """Process a source and extract content."""
        if source_id not in self.sources:
            logger.error(f"Source not found: {source_id}")
            return None

        metadata = self.sources[source_id]
        metadata.processing_status = "processing"
        metadata.processed_at = datetime.now()

        try:
            processor = self.processors.get(metadata.source_type)
            if not processor:
                raise ValueError(f"No processor available for {metadata.source_type}")

            start_time = datetime.now()
            content = processor(metadata.path)
            processing_time = (datetime.now() - start_time).total_seconds()

            processed_content = ProcessedContent(
                source_id=source_id,
                content_type=metadata.source_type.value,
                text_content=content.get('text', ''),
                summary=content.get('summary'),
                key_points=content.get('key_points', []),
                metadata=content.get('metadata', {}),
                processing_time=processing_time,
                word_count=len(content.get('text', '').split()),
                language=content.get('language')
            )

            self.processed_content[source_id] = processed_content
            metadata.processing_status = "completed"

            logger.info(f"Successfully processed source: {metadata.path}")
            return processed_content

        except Exception as e:
            metadata.processing_status = "failed"
            metadata.error_message = str(e)
            logger.error(f"Failed to process source {metadata.path}: {e}")
            return None
        finally:
            self._save_metadata()

    def get_sources(self, filter_config: Optional[SourceFilter] = None) -> List[SourceMetadata]:
        """Get sources matching the filter criteria."""
        sources = list(self.sources.values())

        if not filter_config:
            return sources

        filtered_sources = []
        for source in sources:
            if self._matches_filter(source, filter_config):
                filtered_sources.append(source)

        return filtered_sources

    def _matches_filter(self, source: SourceMetadata, filter_config: SourceFilter) -> bool:
        """Check if a source matches the filter criteria."""
        # Date range filter
        if filter_config.date_range:
            start_date, end_date = filter_config.date_range
            if not (start_date <= source.modified_at <= end_date):
                return False

        # File type filter
        if filter_config.file_types and source.source_type not in filter_config.file_types:
            return False

        # Location filter
        if filter_config.locations and source.location not in filter_config.locations:
            return False

        # Tags filter
        if filter_config.tags and not filter_config.tags.intersection(source.tags):
            return False

        # Size range filter
        if filter_config.size_range:
            min_size, max_size = filter_config.size_range
            if not (min_size <= source.size <= max_size):
                return False

        # Modified since filter
        if filter_config.modified_since and source.modified_at < filter_config.modified_since:
            return False

        # Created since filter
        if filter_config.created_since and source.created_at < filter_config.created_since:
            return False

        # Exclude patterns
        if filter_config.exclude_patterns:
            for pattern in filter_config.exclude_patterns:
                if pattern in source.path:
                    return False

        # Include patterns
        if filter_config.include_patterns:
            matches_include = False
            for pattern in filter_config.include_patterns:
                if pattern in source.path:
                    matches_include = True
                    break
            if not matches_include:
                return False

        return True

    # Content processor methods (placeholder implementations)
    def _process_text(self, path: str) -> Dict[str, Any]:
        """Process text file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            return {
                'text': text,
                'summary': text[:500] + "..." if len(text) > 500 else text,
                'metadata': {'file_type': 'text'}
            }
        except Exception as e:
            logger.error(f"Failed to process text file {path}: {e}")
            return {'text': '', 'metadata': {'error': str(e)}}

    def _process_pdf(self, path: str) -> Dict[str, Any]:
        """Process PDF file."""
        # Placeholder - would use PyPDF2 or similar
        return {'text': f'PDF content from {path}', 'metadata': {'file_type': 'pdf'}}

    def _process_docx(self, path: str) -> Dict[str, Any]:
        """Process DOCX file."""
        # Placeholder - would use python-docx
        return {'text': f'DOCX content from {path}', 'metadata': {'file_type': 'docx'}}

    def _process_markdown(self, path: str) -> Dict[str, Any]:
        """Process Markdown file."""
        return self._process_text(path)  # Similar to text for now

    def _process_rtf(self, path: str) -> Dict[str, Any]:
        """Process RTF file."""
        return {'text': f'RTF content from {path}', 'metadata': {'file_type': 'rtf'}}

    def _process_csv(self, path: str) -> Dict[str, Any]:
        """Process CSV file."""
        # Placeholder - would use pandas
        return {'text': f'CSV data from {path}', 'metadata': {'file_type': 'csv'}}

    def _process_excel(self, path: str) -> Dict[str, Any]:
        """Process Excel file."""
        # Placeholder - would use pandas
        return {'text': f'Excel data from {path}', 'metadata': {'file_type': 'excel'}}

    def _process_audio(self, path: str) -> Dict[str, Any]:
        """Process audio file with transcription."""
        # Placeholder - would use speech recognition
        return {'text': f'Transcribed audio from {path}', 'metadata': {'file_type': 'audio'}}

    def _process_video(self, path: str) -> Dict[str, Any]:
        """Process video file with transcription."""
        # Placeholder - would extract audio and transcribe
        return {'text': f'Transcribed video from {path}', 'metadata': {'file_type': 'video'}}

    def _process_url(self, url: str) -> Dict[str, Any]:
        """Process web URL."""
        # Placeholder - would use requests and BeautifulSoup
        return {'text': f'Web content from {url}', 'metadata': {'file_type': 'url'}}

    def _process_html(self, path: str) -> Dict[str, Any]:
        """Process HTML file."""
        # Placeholder - would use BeautifulSoup
        return {'text': f'HTML content from {path}', 'metadata': {'file_type': 'html'}}

    def _process_youtube_video(self, url: str) -> Dict[str, Any]:
        """Process YouTube video."""
        # Would integrate with existing YouTube processing
        return {'text': f'YouTube video content from {url}', 'metadata': {'file_type': 'youtube_video'}}

    def _process_youtube_playlist(self, url: str) -> Dict[str, Any]:
        """Process YouTube playlist."""
        return {'text': f'YouTube playlist content from {url}', 'metadata': {'file_type': 'youtube_playlist'}}

    def _process_youtube_channel(self, url: str) -> Dict[str, Any]:
        """Process YouTube channel."""
        return {'text': f'YouTube channel content from {url}', 'metadata': {'file_type': 'youtube_channel'}}

    def _process_code(self, path: str) -> Dict[str, Any]:
        """Process code file."""
        return self._process_text(path)  # Similar to text for now

    def _process_json(self, path: str) -> Dict[str, Any]:
        """Process JSON file."""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            text = json.dumps(data, indent=2)
            return {
                'text': text,
                'metadata': {'file_type': 'json', 'structure': type(data).__name__}
            }
        except Exception as e:
            return {'text': '', 'metadata': {'error': str(e)}}

    def _process_image(self, path: str) -> Dict[str, Any]:
        """Process image file with OCR."""
        # Placeholder - would use OCR library like pytesseract
        return {'text': f'OCR text from image {path}', 'metadata': {'file_type': 'image'}}


# Global source manager instance
_source_manager = None

def get_source_manager() -> SourceManager:
    """Get or create the global source manager instance."""
    global _source_manager
    if _source_manager is None:
        _source_manager = SourceManager()
    return _source_manager
