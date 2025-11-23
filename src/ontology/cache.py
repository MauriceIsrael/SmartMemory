"""
Cache management for ontology files.

Handles local cache directory, manifest file (cache_manifest.json),
and cache entry validation.
"""

import hashlib
import json
import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


@dataclass
class CacheEntry:
    """
    Represents a cached ontology file with metadata.
    
    Attributes:
        url: Original remote URL
        local_path: Path to cached file
        etag: HTTP ETag header value (if available)
        last_modified: HTTP Last-Modified header value (if available)
        downloaded_at: ISO timestamp of download
        file_hash: SHA-256 hash of file contents
    """
    url: str
    local_path: str
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    downloaded_at: Optional[str] = None
    file_hash: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict) -> "CacheEntry":
        """Create CacheEntry from dictionary."""
        return cls(**data)


class CacheManager:
    """
    Manages the local ontology cache directory and manifest.
    
    The cache structure:
        ./cache/ontologies/       - Cached .ttl/.rdf files
        ./cache/cache_manifest.json - Metadata for all cached files
    """
    
    def __init__(self, cache_dir: Path = Path("./cache")):
        """
        Initialize cache manager.
        
        Args:
            cache_dir: Root cache directory (default: ./cache)
        """
        self.cache_dir = cache_dir
        self.ontologies_dir = cache_dir / "ontologies"
        self.manifest_file = cache_dir / "cache_manifest.json"
        self._manifest: Dict[str, CacheEntry] = {}
        
        # Create directories if they don't exist
        self._initialize_cache()
    
    def _initialize_cache(self) -> None:
        """Create cache directories and load manifest."""
        self.ontologies_dir.mkdir(parents=True, exist_ok=True)
        
        if self.manifest_file.exists():
            self._load_manifest()
        else:
            logger.info("No existing cache manifest found, starting fresh")
            self._manifest = {}
    
    def _load_manifest(self) -> None:
        """Load manifest from JSON file."""
        try:
            with open(self.manifest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                ontologies = data.get("ontologies", {})
                self._manifest = {
                    name: CacheEntry.from_dict(entry)
                    for name, entry in ontologies.items()
                }
            logger.info(f"Loaded cache manifest with {len(self._manifest)} entries")
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to load cache manifest: {e}")
            self._manifest = {}
    
    def _save_manifest(self) -> None:
        """Save manifest to JSON file."""
        try:
            data = {
                "ontologies": {
                    name: entry.to_dict()
                    for name, entry in self._manifest.items()
                }
            }
            with open(self.manifest_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug("Saved cache manifest")
        except IOError as e:
            logger.error(f"Failed to save cache manifest: {e}")
    
    def get_entry(self, name: str) -> Optional[CacheEntry]:
        """
        Get cache entry for an ontology.
        
        Args:
            name: Ontology name (e.g., 'foaf', 'skos')
            
        Returns:
            CacheEntry if found and file exists, None otherwise
        """
        entry = self._manifest.get(name)
        if entry and Path(entry.local_path).exists():
            return entry
        return None
    
    def update_entry(self, name: str, entry: CacheEntry) -> None:
        """
        Update or create a cache entry.
        
        Args:
            name: Ontology name
            entry: CacheEntry with updated metadata
        """
        self._manifest[name] = entry
        self._save_manifest()
        logger.info(f"Updated cache entry for '{name}'")
    
    def delete_entry(self, name: str) -> None:
        """
        Delete a cache entry and its file.
        
        Args:
            name: Ontology name to delete
        """
        entry = self._manifest.get(name)
        if entry:
            # Delete file if it exists
            file_path = Path(entry.local_path)
            if file_path.exists():
                file_path.unlink()
                logger.info(f"Deleted cached file: {file_path}")
            
            # Remove from manifest
            del self._manifest[name]
            self._save_manifest()
            logger.info(f"Deleted cache entry for '{name}'")
    
    def clear_all(self) -> None:
        """Clear all cache entries and files."""
        for name in list(self._manifest.keys()):
            self.delete_entry(name)
        logger.info("Cleared all cache entries")
    
    def get_cache_path(self, name: str, extension: str = "ttl") -> Path:
        """
        Get the cache file path for an ontology.
        
        Args:
            name: Ontology name
            extension: File extension (default: 'ttl')
            
        Returns:
            Path to cache file
        """
        return self.ontologies_dir / f"{name}.{extension}"
    
    @staticmethod
    def calculate_file_hash(file_path: Path) -> str:
        """
        Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex string of SHA-256 hash
        """
        sha256 = hashlib.sha256()
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        return f"sha256:{sha256.hexdigest()}"
    
    def validate_file_integrity(self, name: str) -> bool:
        """
        Validate cached file integrity using stored hash.
        
        Args:
            name: Ontology name
            
        Returns:
            True if file hash matches stored hash, False otherwise
        """
        entry = self.get_entry(name)
        if not entry or not entry.file_hash:
            return False
        
        file_path = Path(entry.local_path)
        if not file_path.exists():
            return False
        
        current_hash = self.calculate_file_hash(file_path)
        return current_hash == entry.file_hash
