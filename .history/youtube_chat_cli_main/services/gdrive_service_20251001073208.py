"""
JAEGIS NexusSync - Google Drive Service

This module provides Google Drive API integration with OAuth 2.0 authentication,
file monitoring, and automated document ingestion.
"""

import os
import pickle
import logging
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io

from ..core.config import get_config
from ..core.database import get_database

logger = logging.getLogger(__name__)

# Google Drive API scopes
# Using narrowly-focused scopes for security
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',  # Read-only access
    'https://www.googleapis.com/auth/drive.metadata.readonly'  # Metadata access
]


class GoogleDriveError(Exception):
    """Raised when Google Drive operations fail."""
    pass


class GoogleDriveService:
    """
    Google Drive API client with OAuth 2.0 authentication.
    
    Features:
    - OAuth 2.0 flow with refresh token storage
    - File monitoring and change detection
    - File download and metadata retrieval
    - Automatic token refresh
    """
    
    def __init__(self):
        """Initialize Google Drive service."""
        self.config = get_config()
        self.db = get_database()
        self.creds: Optional[Credentials] = None
        self.service = None
        self.token_file = Path('token.pickle')
        
        # Initialize authentication
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with Google Drive API using OAuth 2.0.
        
        This method:
        1. Checks for existing refresh token
        2. Refreshes token if expired
        3. Initiates OAuth flow if no valid token exists
        4. Stores refresh token for offline access
        """
        # Check if we have stored credentials
        if self.token_file.exists():
            logger.info("Loading stored Google Drive credentials...")
            with open(self.token_file, 'rb') as token:
                self.creds = pickle.load(token)
        
        # If credentials don't exist or are invalid, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Refreshing expired Google Drive token...")
                try:
                    self.creds.refresh(Request())
                    logger.info("✅ Google Drive token refreshed successfully")
                except Exception as e:
                    logger.error(f"Failed to refresh token: {e}")
                    # Token refresh failed, need to re-authenticate
                    self.creds = None
            
            if not self.creds:
                # No valid credentials, initiate OAuth flow
                logger.info("Initiating Google Drive OAuth 2.0 flow...")
                
                if not os.path.exists(self.config.google_client_secrets_file):
                    raise GoogleDriveError(
                        f"Google OAuth credentials file not found: "
                        f"{self.config.google_client_secrets_file}\n"
                        f"Please download it from Google Cloud Console and save it as "
                        f"'{self.config.google_client_secrets_file}'"
                    )
                
                try:
                    flow = InstalledAppFlow.from_client_secrets_file(
                        self.config.google_client_secrets_file,
                        SCOPES
                    )
                    
                    # Run local server for OAuth callback
                    self.creds = flow.run_local_server(
                        port=0,
                        authorization_prompt_message='Please visit this URL to authorize: {url}',
                        success_message='Authorization successful! You can close this window.',
                        open_browser=True
                    )
                    
                    logger.info("✅ Google Drive OAuth 2.0 authorization successful")
                    
                except Exception as e:
                    raise GoogleDriveError(f"OAuth 2.0 flow failed: {e}")
            
            # Save credentials for future use
            with open(self.token_file, 'wb') as token:
                pickle.dump(self.creds, token)
            logger.info(f"Credentials saved to {self.token_file}")
        
        # Build the Drive API service
        try:
            self.service = build('drive', 'v3', credentials=self.creds)
            logger.info("✅ Google Drive service initialized successfully")
        except Exception as e:
            raise GoogleDriveError(f"Failed to build Drive service: {e}")
    
    def list_files(
        self,
        folder_id: Optional[str] = None,
        page_size: int = 100,
        order_by: str = 'modifiedTime desc'
    ) -> List[Dict[str, Any]]:
        """
        List files in Google Drive.
        
        Args:
            folder_id: Folder ID to list files from (None = all files)
            page_size: Number of files per page
            order_by: Sort order (default: most recently modified first)
        
        Returns:
            List of file metadata dictionaries
        """
        try:
            # Build query
            query_parts = []
            if folder_id:
                query_parts.append(f"'{folder_id}' in parents")
            query_parts.append("trashed = false")
            
            query = " and ".join(query_parts)
            
            # Execute query
            results = self.service.files().list(
                q=query,
                pageSize=page_size,
                orderBy=order_by,
                fields="files(id, name, mimeType, modifiedTime, size, md5Checksum, parents)"
            ).execute()
            
            files = results.get('files', [])
            logger.info(f"Found {len(files)} files in Google Drive")
            
            return files
            
        except Exception as e:
            logger.error(f"Failed to list files: {e}")
            raise GoogleDriveError(f"Failed to list files: {e}")
    
    def get_file_metadata(self, file_id: str) -> Dict[str, Any]:
        """
        Get metadata for a specific file.
        
        Args:
            file_id: Google Drive file ID
        
        Returns:
            File metadata dictionary
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, modifiedTime, size, md5Checksum, parents, webViewLink"
            ).execute()
            
            return file
            
        except Exception as e:
            logger.error(f"Failed to get file metadata for {file_id}: {e}")
            raise GoogleDriveError(f"Failed to get file metadata: {e}")
    
    def download_file(self, file_id: str, output_path: str) -> str:
        """
        Download a file from Google Drive.
        
        Args:
            file_id: Google Drive file ID
            output_path: Local path to save the file
        
        Returns:
            Path to downloaded file
        """
        try:
            # Get file metadata
            file_metadata = self.get_file_metadata(file_id)
            mime_type = file_metadata.get('mimeType', '')
            
            # Handle Google Workspace files (Docs, Sheets, Slides)
            if mime_type.startswith('application/vnd.google-apps'):
                return self._export_google_file(file_id, mime_type, output_path)
            
            # Download regular files
            request = self.service.files().get_media(fileId=file_id)
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download file
            with io.FileIO(output_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                    if status:
                        logger.debug(f"Download progress: {int(status.progress() * 100)}%")
            
            logger.info(f"✅ Downloaded file: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to download file {file_id}: {e}")
            raise GoogleDriveError(f"Failed to download file: {e}")
    
    def _export_google_file(
        self,
        file_id: str,
        mime_type: str,
        output_path: str
    ) -> str:
        """
        Export Google Workspace files to downloadable formats.
        
        Args:
            file_id: Google Drive file ID
            mime_type: Google Workspace MIME type
            output_path: Local path to save the file
        
        Returns:
            Path to exported file
        """
        # Map Google Workspace types to export formats
        export_formats = {
            'application/vnd.google-apps.document': 'text/plain',  # Google Docs -> Text
            'application/vnd.google-apps.spreadsheet': 'text/csv',  # Sheets -> CSV
            'application/vnd.google-apps.presentation': 'application/pdf',  # Slides -> PDF
        }
        
        export_mime = export_formats.get(mime_type)
        if not export_mime:
            raise GoogleDriveError(f"Unsupported Google Workspace type: {mime_type}")
        
        try:
            request = self.service.files().export_media(
                fileId=file_id,
                mimeType=export_mime
            )
            
            # Ensure output directory exists
            Path(output_path).parent.mkdir(parents=True, exist_ok=True)
            
            # Download exported file
            with io.FileIO(output_path, 'wb') as fh:
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
            
            logger.info(f"✅ Exported Google Workspace file: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to export file {file_id}: {e}")
            raise GoogleDriveError(f"Failed to export file: {e}")

