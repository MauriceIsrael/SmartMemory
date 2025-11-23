"""
Ontology loader - orchestrates the boot sequence.

Coordinates cache validation, fetching, and loading of ontologies
into the RDF graph.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from rdflib import Graph

from .cache import CacheManager, CacheEntry
from .fetcher import OntologyFetcher, FetchError, ValidationError
from .registry import OntologyRegistry, OntologySource

logger = logging.getLogger(__name__)


class OntologyLoader:
    """
    Orchestrates ontology loading with intelligent caching.
    
    Implements the boot sequence:
    1. Check local cache
    2. Validate with remote (HEAD request)
    3. Download if needed
    4. Load into RDF graph
    """
    
    def __init__(
        self,
        graph: Graph,
        cache_dir: Path = Path("./cache"),
        offline_mode: bool = False
    ):
        """
        Initialize ontology loader.
        
        Args:
            graph: RDFLib graph to load ontologies into
            cache_dir: Cache directory path
            offline_mode: If True, skip remote validation (use cache only)
        """
        self.graph = graph
        self.cache_manager = CacheManager(cache_dir)
        self.fetcher = OntologyFetcher()
        self.offline_mode = offline_mode
        self.loaded_ontologies: set[str] = set()
    
    def load_all(self) -> dict[str, bool]:
        """
        Load all registered ontologies.
        
        Returns:
            Dictionary mapping ontology name to success status
        """
        results = {}
        ontologies = OntologyRegistry.get_all()
        
        logger.info(f"Loading {len(ontologies)} ontologies...")
        
        for ontology in ontologies:
            try:
                success = self.load_ontology(ontology)
                results[ontology.name] = success
                if success:
                    self.loaded_ontologies.add(ontology.name)
            except Exception as e:
                logger.error(f"Failed to load {ontology.name}: {e}")
                results[ontology.name] = False
        
        loaded_count = sum(1 for v in results.values() if v)
        logger.info(f"Loaded {loaded_count}/{len(ontologies)} ontologies successfully")
        
        return results
    
    def load_ontology(self, ontology: OntologySource) -> bool:
        """
        Load a single ontology following the boot sequence.
        
        Args:
            ontology: OntologySource to load
            
        Returns:
            True if loaded successfully, False otherwise
        """
        logger.info(f"Loading ontology: {ontology.name} ({ontology.description})")
        
        cache_entry = self.cache_manager.get_entry(ontology.name)
        
        # Step 1: Check if local file exists
        if cache_entry and Path(cache_entry.local_path).exists():
            logger.debug(f"{ontology.name}: Found cached version")
            
            # Validate file integrity
            if not self.cache_manager.validate_file_integrity(ontology.name):
                logger.warning(f"{ontology.name}: Cache integrity check failed, re-downloading")
                return self._download_and_cache(ontology)
            
            # Step 2: Validate with remote (unless offline mode)
            if not self.offline_mode:
                try:
                    remote_headers = self.fetcher.get_headers(ontology.url)
                    
                    # Step 3: Compare metadata
                    if self.fetcher.needs_update(
                        remote_headers,
                        cache_entry.etag,
                        cache_entry.last_modified
                    ):
                        logger.info(f"{ontology.name}: Remote version is newer, downloading")
                        return self._download_and_cache(ontology)
                    else:
                        logger.info(f"{ontology.name}: Cache is up-to-date")
                
                except FetchError as e:
                    # Step 4: Fail-safe - use cached version
                    logger.warning(f"{ontology.name}: Network error, using cached version: {e}")
            
            # Step 5: Load from cache
            return self._load_from_cache(cache_entry)
        
        else:
            # No local file, must download
            logger.info(f"{ontology.name}: No cache found, downloading")
            return self._download_and_cache(ontology)
    
    def _download_and_cache(self, ontology: OntologySource) -> bool:
        """
        Download ontology and update cache.
        
        Args:
            ontology: OntologySource to download
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Download to temp file
            temp_file, headers = self.fetcher.download(
                ontology.url,
                ontology.format,
                validate=True
            )
            
            # Calculate hash
            file_hash = self.cache_manager.calculate_file_hash(temp_file)
            
            # Determine final cache path
            extension = ontology.format.value
            if extension == "xml":
                extension = "rdf"
            final_path = self.cache_manager.get_cache_path(ontology.name, extension)
            
            # Atomic move to cache
            temp_file.rename(final_path)
            logger.info(f"{ontology.name}: Cached to {final_path}")
            
            # Update manifest
            cache_entry = CacheEntry(
                url=ontology.url,
                local_path=str(final_path),
                etag=headers.get("ETag") or headers.get("etag"),
                last_modified=headers.get("Last-Modified") or headers.get("last-modified"),
                downloaded_at=datetime.utcnow().isoformat(),
                file_hash=file_hash
            )
            self.cache_manager.update_entry(ontology.name, cache_entry)
            
            # Load into graph
            return self._load_from_cache(cache_entry)
            
        except (FetchError, ValidationError) as e:
            logger.error(f"{ontology.name}: Download failed: {e}")
            return False
        except Exception as e:
            logger.error(f"{ontology.name}: Unexpected error during download: {e}")
            return False
    
    def _load_from_cache(self, cache_entry: CacheEntry) -> bool:
        """
        Load ontology from cached file into graph.
        
        Args:
            cache_entry: CacheEntry with file path
            
        Returns:
            True if loaded successfully, False otherwise
        """
        try:
            file_path = Path(cache_entry.local_path)
            
            # Determine format from file extension
            extension = file_path.suffix.lstrip('.')
            if extension == 'rdf':
                format = 'xml'
            else:
                format = extension
            
            # Parse into graph
            initial_size = len(self.graph)
            self.graph.parse(str(file_path), format=format)
            final_size = len(self.graph)
            added_triples = final_size - initial_size
            
            logger.info(f"Loaded {added_triples} triples from {file_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load from cache {cache_entry.local_path}: {e}")
            return False
    
    def refresh_ontology(self, name: str) -> bool:
        """
        Force refresh of a specific ontology.
        
        Args:
            name: Ontology name to refresh
            
        Returns:
            True if refreshed successfully, False otherwise
        """
        ontology = OntologyRegistry.get_by_name(name)
        if not ontology:
            logger.error(f"Unknown ontology: {name}")
            return False
        
        # Delete cache entry to force re-download
        self.cache_manager.delete_entry(name)
        
        return self.load_ontology(ontology)
    
    def get_loaded_ontologies(self) -> set[str]:
        """
        Get set of successfully loaded ontology names.
        
        Returns:
            Set of ontology names
        """
        return self.loaded_ontologies.copy()
    
    def get_cache_status(self) -> dict[str, dict]:
        """
        Get cache status for all ontologies.
        
        Returns:
            Dictionary with cache metadata for each ontology
        """
        status = {}
        for ontology in OntologyRegistry.get_all():
            entry = self.cache_manager.get_entry(ontology.name)
            if entry:
                status[ontology.name] = {
                    "url": entry.url,
                    "cached": True,
                    "local_path": entry.local_path,
                    "downloaded_at": entry.downloaded_at,
                    "etag": entry.etag,
                    "last_modified": entry.last_modified,
                    "file_hash": entry.file_hash,
                }
            else:
                status[ontology.name] = {
                    "url": ontology.url,
                    "cached": False,
                }
        return status
