"""
Configuration management for Semantic Memory MCP Server.

Uses Pydantic settings for environment-based configuration with sensible defaults.
"""

from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class SemanticMemoryConfig(BaseSettings):
    """
    Configuration for the Semantic Memory server.

    Environment variables can override defaults by prefixing with SEMMEM_
    (e.g., SEMMEM_CACHE_DIR=/custom/cache)
    """

    model_config = SettingsConfigDict(
        env_prefix="SEMMEM_",
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Cache configuration
    cache_dir: Path = Field(
        default=Path.home() / ".cache" / "semantic-memory",
        description="Directory for caching downloaded ontologies (FOAF, Schema.org, etc.)",
    )

    cache_ttl_hours: int = Field(
        default=24,
        description="Time-to-live for cached ontologies in hours",
        ge=1,
    )

    # Persistence configuration
    persistence_backend: Literal["turtle", "sqlite", "oxigraph"] = Field(
        default="turtle",
        description="Storage backend for the knowledge graph",
    )

    persistence_path: Path = Field(
        default=Path(__file__).parent.parent.parent / "knowledge_graph.ttl",
        description="Path to persistence file (format depends on backend)",
    )

    # Reasoning configuration
    enable_owl_reasoning: bool = Field(
        default=True,
        description="Enable OWL-RL reasoning (can be slow on large ontologies, set to false for faster startup)",
    )
    
    load_ontologies: bool = Field(
        default=True,
        description="Load full ontologies (Schema.org, FOAF, SKOS). Required for core_* rules in _optional/. Adds ~17k triples and 5-10s startup time.",
    )

    # Inference depth and confidence configuration
    max_inference_depth: int = Field(
        default=10,
        description="Maximum depth for recursive inference to prevent infinite loops",
        ge=1,
        le=100,
    )

    auto_accept_threshold: float = Field(
        default=0.80,
        description="Confidence threshold for automatically accepting inferences",
        ge=0.0,
        le=1.0,
    )

    default_rule_confidence: float = Field(
        default=0.85,
        description="Default confidence for built-in SPARQL rules",
        ge=0.0,
        le=1.0,
    )

    debounce_seconds: float = Field(
        default=2.0,
        description="Time to wait after last trigger before running background inference pass",
        ge=0.0,
    )


    # Rule loading configuration
    default_rules_dir: Path = Field(
        default=Path(__file__).parent.parent / "rules" / "defaults",
        description="Directory containing default SPARQL inference rules",
    )

    user_rules_dir: Path = Field(
        default=Path(__file__).parent.parent.parent / "user_rules",
        description="Directory for user-defined SPARQL rules",
    )

    rejected_rules_dir: Path = Field(
        default=Path(__file__).parent.parent.parent / "rejected_rules",
        description="Directory for rejected rules (archived)",
    )

    # Ontology URLs with fallbacks (for when primary URLs timeout)
    ontology_urls: dict[str, list[str]] | dict[str, str] = Field(
        default={
            "foaf": [
                # Local bundled copy (fastest, most reliable)
                "file://" + str(Path(__file__).parent / "ontologies" / "foaf.rdf"),
                # GitHub mirror (more reliable than xmlns.com)
                "https://raw.githubusercontent.com/vocab/foaf/master/foaf.rdf",
                # Original (often times out)
                "http://xmlns.com/foaf/0.1/",
            ],
            "schema": [
                "https://schema.org/version/latest/schemaorg-current-https.rdf",
                # Fallback to specific version if latest is unavailable
                "https://schema.org/version/23.0/schemaorg-current-https.rdf",
            ],
            "skos": [
                "http://www.w3.org/2009/08/skos-reference/skos.rdf",
                "https://www.w3.org/TR/skos-reference/skos.rdf",
            ],
            "rdfs": [
                "http://www.w3.org/2000/01/rdf-schema#",
                "https://www.w3.org/2000/01/rdf-schema",
            ],
        },
        description="URLs for external ontologies to load (with fallbacks)",
    )

    # Server configuration
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO",
        description="Logging level for the server",
    )

    enable_provenance_tracking: bool = Field(
        default=True,
        description="Track provenance metadata for all triples",
    )

    force_offline: bool = Field(
        default=False,
        description="Force offline mode (no network requests) for testing",
    )

    user_namespace: str = Field(
        default="http://semanticmemory.org/user#",
        description="Namespace for user-created entities (referenced with ':' prefix)",
    )

    @property
    def project_root(self) -> Path:
        """Root directory of the project."""
        # Calculate relative to this file: src/smart_memory/config.py -> ../..
        return Path(__file__).parent.parent.parent

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Ensure directories exist
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.user_rules_dir.mkdir(parents=True, exist_ok=True)

        # Ensure persistence directory exists
        self.persistence_path.parent.mkdir(parents=True, exist_ok=True)


# Global config instance
config = SemanticMemoryConfig()
