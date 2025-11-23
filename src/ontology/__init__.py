"""
Ontology management module for SmartMemory MCP server.

This module provides intelligent loading and caching of standard ontologies
(FOAF, SKOS, Schema.org) with HTTP-based cache validation.
"""

from .loader import OntologyLoader
from .registry import OntologyRegistry, OntologySource
from .cache import CacheManager, CacheEntry
from .fetcher import OntologyFetcher

__all__ = [
    "OntologyLoader",
    "OntologyRegistry",
    "OntologySource",
    "CacheManager",
    "CacheEntry",
    "OntologyFetcher",
]
