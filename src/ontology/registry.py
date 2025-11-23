"""
Ontology registry with hardcoded standard ontologies.

Maintains the list of ontologies to load at startup with their URLs,
preferred formats, and load order.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class OntologyFormat(Enum):
    """Supported RDF serialization formats."""
    TURTLE = "turtle"
    RDF_XML = "xml"
    N3 = "n3"
    NT = "nt"


@dataclass
class OntologySource:
    """
    Represents a remote ontology source.
    
    Attributes:
        name: Short identifier (e.g., 'foaf', 'skos')
        url: Remote URL to fetch the ontology from
        format: Preferred RDF serialization format
        priority: Load order (lower number = higher priority)
        description: Human-readable description
    """
    name: str
    url: str
    format: OntologyFormat
    priority: int
    description: str


class OntologyRegistry:
    """
    Registry of standard ontologies to load.
    
    This class maintains a hardcoded list of well-known ontologies
    that provide foundational vocabulary for the knowledge graph.
    """
    
    # Standard ontologies to load at startup
    _ONTOLOGIES: List[OntologySource] = [
        # OntologySource(
        #     name="foaf",
        #     url="http://xmlns.com/foaf/0.1/",
        #     format=OntologyFormat.RDF_XML,
        #     priority=1,
        #     description="Friend of a Friend (FOAF) - vocabulary for people and relationships"
        # ),
        OntologySource(
            name="skos",
            url="http://www.w3.org/2004/02/skos/core",
            format=OntologyFormat.RDF_XML,
            priority=2,
            description="Simple Knowledge Organization System (SKOS) - for concept schemes"
        ),
        OntologySource(
            name="schema",
            url="https://schema.org/version/latest/schemaorg-current-https.ttl",
            format=OntologyFormat.TURTLE,
            priority=3,
            description="Schema.org - structured data vocabulary (curated subset)"
        ),
    ]
    
    @classmethod
    def get_all(cls) -> List[OntologySource]:
        """
        Get all registered ontologies sorted by priority.
        
        Returns:
            List of OntologySource objects, ordered by priority (ascending)
        """
        return sorted(cls._ONTOLOGIES, key=lambda x: x.priority)
    
    @classmethod
    def get_by_name(cls, name: str) -> OntologySource | None:
        """
        Get a specific ontology by name.
        
        Args:
            name: Ontology identifier (e.g., 'foaf', 'skos')
            
        Returns:
            OntologySource if found, None otherwise
        """
        for ontology in cls._ONTOLOGIES:
            if ontology.name == name:
                return ontology
        return None
    
    @classmethod
    def add_custom(cls, ontology: OntologySource) -> None:
        """
        Add a custom ontology to the registry.
        
        This allows extending the registry with project-specific ontologies
        beyond the standard set.
        
        Args:
            ontology: Custom OntologySource to add
        """
        cls._ONTOLOGIES.append(ontology)
