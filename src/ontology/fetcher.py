"""
HTTP fetcher for ontology files with cache validation.

Handles HTTP HEAD/GET requests, conditional requests (ETag, Last-Modified),
and RDF validation.
"""

import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Tuple

import requests
from rdflib import Graph
from rdflib.exceptions import ParserError

from .registry import OntologyFormat

logger = logging.getLogger(__name__)


class FetchError(Exception):
    """Raised when fetching an ontology fails."""
    pass


class ValidationError(Exception):
    """Raised when RDF validation fails."""
    pass


class OntologyFetcher:
    """
    Fetches ontologies from remote URLs with HTTP caching support.
    
    Supports conditional requests using ETag and Last-Modified headers
    to minimize unnecessary downloads.
    """
    
    def __init__(self, timeout: int = 30, max_redirects: int = 5):
        """
        Initialize fetcher.
        
        Args:
            timeout: HTTP request timeout in seconds
            max_redirects: Maximum number of redirects to follow
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.max_redirects = max_redirects
        self.session.headers.update({
            'User-Agent': 'SmartMemory-MCP/1.0 (Ontology Loader)'
        })
    
    def get_headers(self, url: str) -> Dict[str, str]:
        """
        Fetch HTTP headers using HEAD request.
        
        Args:
            url: Remote ontology URL
            
        Returns:
            Dictionary of HTTP headers
            
        Raises:
            FetchError: If request fails
        """
        try:
            response = self.session.head(url, timeout=self.timeout, allow_redirects=True)
            response.raise_for_status()
            logger.debug(f"HEAD {url} -> {response.status_code}")
            return dict(response.headers)
        except requests.RequestException as e:
            raise FetchError(f"Failed to fetch headers from {url}: {e}")
    
    def needs_update(
        self,
        remote_headers: Dict[str, str],
        cached_etag: Optional[str] = None,
        cached_last_modified: Optional[str] = None
    ) -> bool:
        """
        Check if remote ontology is newer than cached version.
        
        Args:
            remote_headers: HTTP headers from remote server
            cached_etag: Cached ETag value
            cached_last_modified: Cached Last-Modified value
            
        Returns:
            True if remote is newer or cache is missing, False otherwise
        """
        # If no cache metadata, always update
        if not cached_etag and not cached_last_modified:
            return True
        
        # Check ETag first (more reliable)
        remote_etag = remote_headers.get('ETag') or remote_headers.get('etag')
        if remote_etag and cached_etag:
            return remote_etag != cached_etag
        
        # Fall back to Last-Modified
        remote_last_modified = remote_headers.get('Last-Modified') or remote_headers.get('last-modified')
        if remote_last_modified and cached_last_modified:
            return remote_last_modified != cached_last_modified
        
        # If we can't compare, assume update needed
        return True
    
    def download(
        self,
        url: str,
        format: OntologyFormat,
        validate: bool = True
    ) -> Tuple[Path, Dict[str, str]]:
        """
        Download ontology to a temporary file.
        
        Args:
            url: Remote ontology URL
            format: Expected RDF format
            validate: Whether to validate RDF syntax (default: True)
            
        Returns:
            Tuple of (temp_file_path, response_headers)
            
        Raises:
            FetchError: If download fails
            ValidationError: If RDF validation fails
        """
        try:
            logger.info(f"Downloading ontology from {url}")
            response = self.session.get(url, timeout=self.timeout, stream=True)
            response.raise_for_status()
            
            # Create temporary file
            temp_file = tempfile.NamedTemporaryFile(
                mode='wb',
                delete=False,
                suffix=f'.{format.value}'
            )
            
            # Download with progress logging
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
                        downloaded += len(chunk)
            
            temp_path = Path(temp_file.name)
            logger.info(f"Downloaded {downloaded} bytes to {temp_path}")
            
            # Validate RDF if requested
            if validate:
                self._validate_rdf(temp_path, format)
            
            return temp_path, dict(response.headers)
            
        except requests.RequestException as e:
            raise FetchError(f"Failed to download from {url}: {e}")
    
    def _validate_rdf(self, file_path: Path, format: OntologyFormat) -> None:
        """
        Validate RDF file syntax.
        
        Args:
            file_path: Path to RDF file
            format: Expected RDF format
            
        Raises:
            ValidationError: If parsing fails
        """
        try:
            logger.debug(f"Validating RDF file: {file_path}")
            graph = Graph()
            graph.parse(str(file_path), format=format.value)
            triple_count = len(graph)
            logger.info(f"RDF validation successful: {triple_count} triples")
        except ParserError as e:
            raise ValidationError(f"Invalid RDF syntax: {e}")
        except Exception as e:
            raise ValidationError(f"RDF validation failed: {e}")
    
    def download_with_conditional_request(
        self,
        url: str,
        format: OntologyFormat,
        cached_etag: Optional[str] = None,
        cached_last_modified: Optional[str] = None
    ) -> Tuple[Optional[Path], Dict[str, str], bool]:
        """
        Download with conditional request (If-None-Match, If-Modified-Since).
        
        Args:
            url: Remote ontology URL
            format: Expected RDF format
            cached_etag: Cached ETag for conditional request
            cached_last_modified: Cached Last-Modified for conditional request
            
        Returns:
            Tuple of (temp_file_path or None, headers, was_modified)
            If was_modified is False (304 Not Modified), temp_file_path is None
            
        Raises:
            FetchError: If request fails
        """
        headers = {}
        if cached_etag:
            headers['If-None-Match'] = cached_etag
        if cached_last_modified:
            headers['If-Modified-Since'] = cached_last_modified
        
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            
            # 304 Not Modified - use cached version
            if response.status_code == 304:
                logger.info(f"Ontology not modified (304): {url}")
                return None, dict(response.headers), False
            
            # 200 OK - download new version
            response.raise_for_status()
            
            temp_file = tempfile.NamedTemporaryFile(
                mode='wb',
                delete=False,
                suffix=f'.{format.value}'
            )
            
            with temp_file:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        temp_file.write(chunk)
            
            temp_path = Path(temp_file.name)
            self._validate_rdf(temp_path, format)
            
            return temp_path, dict(response.headers), True
            
        except requests.RequestException as e:
            raise FetchError(f"Failed conditional request to {url}: {e}")
