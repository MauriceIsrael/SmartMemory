"""
Natural language to RDF triple extractor.

Converts natural language statements into RDF triples using pattern matching
and simple heuristics.
"""

import re
from dataclasses import dataclass
from typing import Optional

from rdflib import URIRef, Literal as RDFLiteral, Namespace, BNode
from rdflib.namespace import RDF, RDFS

from semantic_memory.logging_config import get_logger
from semantic_memory.vocabulary import FOAF, SCHEMA

logger = get_logger(__name__)

# Default namespace for user entities
USER_NS = Namespace("http://semanticmemory.org/user#")


@dataclass
class ExtractedTriple:
    """Represents a single extracted RDF triple."""

    subject: URIRef | BNode
    predicate: URIRef
    object: URIRef | RDFLiteral | BNode
    confidence: float = 0.8


class TripleExtractor:
    """
    Extracts RDF triples from natural language text.

    Uses pattern matching and heuristics to identify subject-predicate-object
    patterns in natural language.
    """

    def __init__(self):
        """Initialize the triple extractor with common patterns."""
        self.patterns = self._init_patterns()

    def _init_patterns(self) -> list[dict]:
        """
        Initialize extraction patterns.

        Each pattern has:
        - regex: Regular expression to match
        - handler: Function to convert match to ExtractedTriple
        """
        return [
            {
                "name": "works_at",
                "regex": r"(\w+)\s+(?:works at|works for|is employed by)\s+(.+)",
                "handler": self._handle_works_at,
            },
            {
                "name": "knows",
                "regex": r"(\w+)\s+(?:knows|is friends with|is a friend of)\s+(\w+)",
                "handler": self._handle_knows,
            },
            {
                "name": "is_a",
                "regex": r"(\w+)\s+(?:is a|is an)\s+(\w+)",
                "handler": self._handle_is_a,
            },
            {
                "name": "located_in",
                "regex": r"(\w+)\s+(?:is in|is located in|is contained in)\s+(.+)",
                "handler": self._handle_located_in,
            },
            {
                "name": "attended_event",
                "regex": r"(\w+)\s+(?:attended|went to|participated in)\s+(.+)",
                "handler": self._handle_attended,
            },
            {
                "name": "created",
                "regex": r"(\w+)\s+(?:created|wrote|made|authored)\s+(.+)",
                "handler": self._handle_created,
            },
            {
                "name": "about_topic",
                "regex": r"(.+?)\s+(?:is about|covers|discusses)\s+(.+)",
                "handler": self._handle_about,
            },
        ]

    def _make_uri(self, name: str) -> URIRef:
        """
        Convert a name to a URI.

        Args:
            name: Name to convert (e.g., "Alice", "Google")

        Returns:
            URIRef in the user namespace
        """
        # Clean the name
        clean_name = name.strip().replace(" ", "_")
        return USER_NS[clean_name]

    def _handle_works_at(self, match: re.Match) -> list[ExtractedTriple]:
        """Handle 'X works at Y' pattern."""
        person = match.group(1)
        org = match.group(2)

        person_uri = self._make_uri(person)
        org_uri = self._make_uri(org)

        return [
            ExtractedTriple(
                subject=person_uri,
                predicate=SCHEMA.worksFor,
                object=org_uri,
                confidence=0.9,
            ),
            # Also add type information
            ExtractedTriple(
                subject=person_uri,
                predicate=RDF.type,
                object=SCHEMA.Person,
                confidence=0.85,
            ),
            ExtractedTriple(
                subject=org_uri,
                predicate=RDF.type,
                object=SCHEMA.Organization,
                confidence=0.85,
            ),
        ]

    def _handle_knows(self, match: re.Match) -> list[ExtractedTriple]:
        """Handle 'X knows Y' pattern."""
        person1 = match.group(1)
        person2 = match.group(2)

        person1_uri = self._make_uri(person1)
        person2_uri = self._make_uri(person2)

        return [
            ExtractedTriple(
                subject=person1_uri,
                predicate=FOAF.knows,
                object=person2_uri,
                confidence=0.9,
            ),
            ExtractedTriple(
                subject=person1_uri,
                predicate=RDF.type,
                object=FOAF.Person,
                confidence=0.85,
            ),
            ExtractedTriple(
                subject=person2_uri,
                predicate=RDF.type,
                object=FOAF.Person,
                confidence=0.85,
            ),
        ]

    def _handle_is_a(self, match: re.Match) -> list[ExtractedTriple]:
        """Handle 'X is a Y' pattern."""
        entity = match.group(1)
        type_name = match.group(2)

        entity_uri = self._make_uri(entity)
        type_uri = self._make_uri(type_name)

        return [
            ExtractedTriple(
                subject=entity_uri,
                predicate=RDF.type,
                object=type_uri,
                confidence=0.85,
            )
        ]

    def _handle_located_in(self, match: re.Match) -> list[ExtractedTriple]:
        """Handle 'X is in Y' pattern."""
        thing = match.group(1)
        place = match.group(2)

        thing_uri = self._make_uri(thing)
        place_uri = self._make_uri(place)

        return [
            ExtractedTriple(
                subject=thing_uri,
                predicate=SCHEMA.containedInPlace,
                object=place_uri,
                confidence=0.85,
            ),
            ExtractedTriple(
                subject=place_uri,
                predicate=RDF.type,
                object=SCHEMA.Place,
                confidence=0.8,
            ),
        ]

    def _handle_attended(self, match: re.Match) -> list[ExtractedTriple]:
        """Handle 'X attended Y' pattern."""
        person = match.group(1)
        event = match.group(2)

        person_uri = self._make_uri(person)
        event_uri = self._make_uri(event)

        return [
            ExtractedTriple(
                subject=event_uri,
                predicate=SCHEMA.attendee,
                object=person_uri,
                confidence=0.9,
            ),
            ExtractedTriple(
                subject=person_uri,
                predicate=RDF.type,
                object=SCHEMA.Person,
                confidence=0.85,
            ),
            ExtractedTriple(
                subject=event_uri,
                predicate=RDF.type,
                object=SCHEMA.Event,
                confidence=0.85,
            ),
        ]

    def _handle_created(self, match: re.Match) -> list[ExtractedTriple]:
        """Handle 'X created Y' pattern."""
        creator = match.group(1)
        thing = match.group(2)

        creator_uri = self._make_uri(creator)
        thing_uri = self._make_uri(thing)

        return [
            ExtractedTriple(
                subject=thing_uri,
                predicate=SCHEMA.creator,
                object=creator_uri,
                confidence=0.9,
            ),
            ExtractedTriple(
                subject=creator_uri,
                predicate=RDF.type,
                object=SCHEMA.Person,
                confidence=0.85,
            ),
        ]

    def _handle_about(self, match: re.Match) -> list[ExtractedTriple]:
        """Handle 'X is about Y' pattern."""
        thing = match.group(1)
        topic = match.group(2)

        thing_uri = self._make_uri(thing)
        topic_uri = self._make_uri(topic)

        return [
            ExtractedTriple(
                subject=thing_uri,
                predicate=SCHEMA.about,
                object=topic_uri,
                confidence=0.85,
            )
        ]

    def extract(self, text: str) -> list[ExtractedTriple]:
        """
        Extract RDF triples from natural language text.

        Args:
            text: Natural language text to process

        Returns:
            List of extracted triples with confidence scores
        """
        logger.debug(f"Extracting triples from: {text}")

        triples = []

        # Try each pattern
        for pattern_info in self.patterns:
            pattern = pattern_info["regex"]
            handler = pattern_info["handler"]

            # Case-insensitive matching
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                try:
                    extracted = handler(match)
                    triples.extend(extracted)
                    logger.debug(
                        f"Pattern '{pattern_info['name']}' matched, "
                        f"extracted {len(extracted)} triples"
                    )
                except Exception as e:
                    logger.warning(f"Failed to handle match for pattern {pattern}: {e}")

        # If no patterns matched, try to extract a simple triple
        if not triples:
            logger.debug("No patterns matched, attempting fallback extraction")
            triples = self._fallback_extraction(text)

        logger.info(f"Extracted {len(triples)} triples from text")
        return triples

    def _fallback_extraction(self, text: str) -> list[ExtractedTriple]:
        """
        Fallback extraction when no patterns match.

        Creates a simple triple with the text as a literal.
        """
        # Create a statement node
        statement_uri = BNode()

        return [
            ExtractedTriple(
                subject=statement_uri,
                predicate=RDFS.comment,
                object=RDFLiteral(text),
                confidence=0.5,  # Low confidence for fallback
            )
        ]

    def parse_triple_notation(self, notation: str) -> Optional[ExtractedTriple]:
        """
        Parse explicit triple notation like "subject predicate object".

        Args:
            notation: Triple in string format (e.g., ":Alice foaf:knows :Bob")

        Returns:
            ExtractedTriple or None if parsing fails
        """
        # Simple parser for Turtle-like notation
        parts = notation.strip().split()

        if len(parts) != 3:
            logger.warning(f"Invalid triple notation: {notation}")
            return None

        try:
            # Parse subject
            if parts[0].startswith(":"):
                subject = self._make_uri(parts[0][1:])
            else:
                subject = URIRef(parts[0])

            # Parse predicate
            if parts[1].startswith(":"):
                predicate = self._make_uri(parts[1][1:])
            elif ":" in parts[1]:
                prefix, local = parts[1].split(":", 1)
                if prefix == "foaf":
                    predicate = FOAF[local]
                elif prefix == "schema":
                    predicate = SCHEMA[local]
                elif prefix == "rdf":
                    predicate = RDF[local]
                else:
                    predicate = URIRef(parts[1])
            else:
                predicate = self._make_uri(parts[1])

            # Parse object
            if parts[2].startswith('"'):
                # Literal
                obj = RDFLiteral(parts[2].strip('"'))
            elif parts[2].startswith(":"):
                obj = self._make_uri(parts[2][1:])
            else:
                obj = URIRef(parts[2])

            return ExtractedTriple(
                subject=subject,
                predicate=predicate,
                object=obj,
                confidence=1.0,  # Explicit notation is high confidence
            )

        except Exception as e:
            logger.error(f"Failed to parse triple notation '{notation}': {e}")
            return None


__all__ = ["ExtractedTriple", "TripleExtractor"]
