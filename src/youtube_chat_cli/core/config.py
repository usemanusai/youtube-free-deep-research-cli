"""
Configuration management for YouTube Chat CLI.
"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class Config:
    """Configuration manager for the application."""
    
    def __init__(self):
        """Initialize configuration."""
        # Load environment variables
        load_dotenv()
        
        # User data directory
        self.user_data_dir = Path.home() / ".youtube-chat-cli"
        self.user_data_dir.mkdir(exist_ok=True)
        
        # API Keys
        self.youtube_api_key = os.getenv('YOUTUBE_API_KEY')
        self.openrouter_api_key = os.getenv('OPENROUTER_API_KEY')
        
        # Service URLs
        self.marytts_server_url = os.getenv('MARYTTS_SERVER_URL', 'http://localhost:59125')
        self.n8n_webhook_url = os.getenv('N8N_WEBHOOK_URL')
        
        # Rate limiting settings
        self.max_videos_per_day = int(os.getenv('MAX_VIDEOS_PER_DAY', '5'))
        self.min_delay_hours = int(os.getenv('MIN_DELAY_HOURS', '1'))
        self.max_delay_hours = int(os.getenv('MAX_DELAY_HOURS', '2'))
        self.backoff_hours = int(os.getenv('BACKOFF_HOURS', '2'))
    
    @property
    def database_path(self) -> str:
        """Get database file path."""
        return str(self.user_data_dir / "videos.db")
    
    @property
    def config_dir(self) -> Path:
        """Get configuration directory."""
        return self.user_data_dir
    
    def get_api_key(self, service: str) -> Optional[str]:
        """Get API key for a specific service."""
        keys = {
            'youtube': self.youtube_api_key,
            'openrouter': self.openrouter_api_key
        }
        return keys.get(service.lower())
    
    def is_configured(self, service: str) -> bool:
        """Check if a service is properly configured."""
        if service.lower() == 'youtube':
            return bool(self.youtube_api_key)
        elif service.lower() == 'openrouter':
            return bool(self.openrouter_api_key)
        elif service.lower() == 'n8n':
            return bool(self.n8n_webhook_url)
        return False


# Global config instance
_config = None

def get_config() -> Config:
    """Get or create the global config instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config
