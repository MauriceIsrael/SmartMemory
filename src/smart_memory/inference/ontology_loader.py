"""
Ontology loader with smart HTTP caching.

Loads standard ontologies (FOAF, Schema.org, SKOS, RDFS) with support for
HTTP conditional GET using ETag and Last-Modified headers.
"""

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Optional

import requests
from rdflib import Graph

from smart_memory.config import config
from smart_memory.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class OntologyCacheMetadata:
    """
    Metadata for cached ontology files.

    Tracks HTTP caching information to enable conditional GET requests.
    """

    url: str
    cached_at: str  # ISO 8601 timestamp
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    file_path: str = ""

    def is_expired(self) -> bool:
        """Check if the cache is expired based on TTL."""
        cached_time = datetime.fromisoformat(self.cached_at)
        ttl = timedelta(hours=config.cache_ttl_hours)
        return datetime.now(timezone.utc) - cached_time > ttl

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "OntologyCacheMetadata":
        """Create from dictionary."""
        return cls(**data)


def fetch_with_cache(
    url: str,
    cache_dir: Path,
    metadata: Optional[OntologyCacheMetadata] = None,
) -> tuple[Optional[str], OntologyCacheMetadata]:
    """
    Fetch ontology with HTTP conditional GET support.

    Uses ETag and Last-Modified headers to avoid redundant downloads.

    Args:
        url: URL of the ontology to fetch
        cache_dir: Directory to store cached files
        metadata: Existing cache metadata (if available)

    Returns:
        Tuple of (content, updated_metadata). Content is None if cache is valid.

    Raises:
        requests.RequestException: If HTTP request fails and no cache available
    """
    logger.info(f"Fetching ontology from {url}")

    if config.force_offline:
        logger.info("FORCE_OFFLINE is True, skipping network request.")
        if metadata and metadata.file_path and Path(metadata.file_path).exists():
            logger.info(f"Using cached fallback for {url}")
            with open(metadata.file_path, "r", encoding="utf-8") as f:
                return f.read(), metadata
        else:
            raise requests.RequestException(f"Offline mode: No cache available for {url}")

    # Prepare conditional GET headers
    headers = {}
    if metadata:
        if metadata.etag:
            headers["If-None-Match"] = metadata.etag
        if metadata.last_modified:
            headers["If-Modified-Since"] = metadata.last_modified

    try:
        response = requests.get(url, headers=headers, timeout=30)

        # HTTP 304 Not Modified - cache is still valid
        if response.status_code == 304:
            logger.info(f"Cache valid (304 Not Modified) for {url}")
            if metadata:
                # Update cached_at timestamp
                metadata.cached_at = datetime.now(timezone.utc).isoformat()
                return None, metadata
            else:
                raise ValueError("Received 304 but no metadata provided")

        # HTTP 200 OK - new content
        if response.status_code == 200:
            logger.info(f"Downloaded new content from {url} ({len(response.content)} bytes)")

            # Create cache filename from URL
            filename = url.split("/")[-1] or "ontology.rdf"
            if not any(filename.endswith(ext) for ext in [".rdf", ".ttl", ".xml", ".owl"]):
                filename += ".rdf"

            file_path = cache_dir / filename

            # Save to cache
            with open(file_path, "wb") as f:
                f.write(response.content)

            # Create new metadata
            new_metadata = OntologyCacheMetadata(
                url=url,
                cached_at=datetime.now(timezone.utc).isoformat(),
                etag=response.headers.get("ETag"),
                last_modified=response.headers.get("Last-Modified"),
                file_path=str(file_path),
            )

            return response.text, new_metadata

        # Other status codes
        response.raise_for_status()

    except requests.RequestException as e:
        logger.warning(f"Failed to fetch {url}: {e}")

        # If we have cached data, use it as fallback
        if metadata and metadata.file_path and Path(metadata.file_path).exists():
            logger.info(f"Using cached fallback for {url}")
            with open(metadata.file_path, "r", encoding="utf-8") as f:
                return f.read(), metadata

        # No cache available, re-raise the error
        raise

    return None, metadata  # Should never reach here


class OntologyLoader:
    """
    Loads and caches standard ontologies.

    Implements smart caching with HTTP conditional GET to minimize
    network requests and support offline operation.
    """

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the ontology loader.

        Args:
            cache_dir: Directory for caching ontologies (defaults to config.cache_dir)
        """
        self.cache_dir = cache_dir or config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.metadata_file = self.cache_dir / "metadata.json"
        self.metadata: dict[str, OntologyCacheMetadata] = self._load_metadata()

    def _load_metadata(self) -> dict[str, OntologyCacheMetadata]:
        """Load cache metadata from disk."""
        if not self.metadata_file.exists():
            return {}

        try:
            with open(self.metadata_file, "r") as f:
                data = json.load(f)
                return {
                    url: OntologyCacheMetadata.from_dict(meta) for url, meta in data.items()
                }
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load cache metadata: {e}")
            return {}

    def _save_metadata(self) -> None:
        """Save cache metadata to disk."""
        data = {url: meta.to_dict() for url, meta in self.metadata.items()}
        with open(self.metadata_file, "w") as f:
            json.dump(data, f, indent=2)

    def load_ontology(self, url: str, graph: Graph) -> None:
        """
        Load an ontology into the given graph.

        Uses cached version if available and valid, otherwise downloads.

        Args:
            url: URL of the ontology (http://, https://, or file://)
            graph: RDFLib graph to load into

        Raises:
            Exception: If loading fails and no cache is available
        """
        # Handle local file:// URLs directly
        if url.startswith("file://"):
            local_path = url.replace("file://", "")
            logger.info(f"Loading local ontology from {local_path}")
            try:
                graph.parse(local_path, format="xml")
                logger.info(f"Successfully loaded local ontology from {local_path}")
                return
            except Exception as e:
                logger.error(f"Failed to load local ontology from {local_path}: {e}")
                raise
        
        # For http/https URLs, use caching
        metadata = self.metadata.get(url)

        # Check if cache exists and is not expired
        use_cache = False
        if metadata and not metadata.is_expired() and Path(metadata.file_path).exists():
            use_cache = True
            logger.info(f"Using cached ontology for {url}")

        try:
            if use_cache:
                # Load from cache
                graph.parse(metadata.file_path)
            else:
                # Fetch from network (with conditional GET if we have metadata)
                content, new_metadata = fetch_with_cache(url, self.cache_dir, metadata)

                if content:
                    # New content downloaded
                    graph.parse(data=content, format="xml") # Explicitly specify format
                    self.metadata[url] = new_metadata
                    self._save_metadata()
                elif metadata:
                    # Cache still valid (304), load from file
                    graph.parse(metadata.file_path, format="xml") # Explicitly specify format
                    self.metadata[url] = new_metadata
                    self._save_metadata()

            logger.info(f"Successfully loaded ontology from {url}")

        except Exception as e:
            logger.error(f"Failed to load ontology from {url}: {e}")
            raise

    async def load_standard_ontologies(self, provenance_graph) -> None:
        """
        Load all standard ontologies into the knowledge graph.

        Args:
            provenance_graph: ProvenanceGraph instance to load into

        Note: This is async to allow for concurrent downloads in the future
        """
        logger.info("Loading standard ontologies...")

        for name, urls in config.ontology_urls.items():
            # Support both single URL (string) and multiple fallback URLs (list)
            url_list = urls if isinstance(urls, list) else [urls]
            
            loaded = False
            last_error = None
            
            for url in url_list:
                try:
                    logger.info(f"Loading {name} ontology from {url}")
                    self.load_ontology(url, provenance_graph.graph)
                    loaded = True
                    break  # Success! No need to try other URLs
                except Exception as e:
                    last_error = e
                    logger.warning(f"Failed to load {name} from {url}: {e}")
                    # Try next fallback URL
                    continue
            
            if not loaded:
                logger.error(f"Failed to load {name} ontology from all sources: {last_error}")
                # Continue loading other ontologies even if one fails completely

        logger.info(
            f"Finished loading ontologies. Graph now has {len(provenance_graph.graph)} triples"
        )



__all__ = ["OntologyCacheMetadata", "fetch_with_cache", "OntologyLoader"]
