"""
Custom vocabulary namespace for Semantic Memory provenance tracking.

Defines the sem: namespace for tracking metadata about triples in the knowledge graph.
"""

from rdflib import Namespace, URIRef

# Custom namespace for semantic memory provenance
SEM = Namespace("http://semanticmemory.org/vocab#")

# Provenance properties
SOURCE = SEM.source  # Literal["user", "owlrl", "sparql-rule"]
SOURCE_RULE = SEM.sourceRule  # URI of the SPARQL rule file that generated this triple
TIMESTAMP = SEM.timestamp  # xsd:dateTime when the triple was added
CONFIDENCE = SEM.confidence  # xsd:decimal between 0.0 and 1.0
UNCERTAIN = SEM.uncertain  # xsd:boolean - true if verification is needed
UNCERTAIN_PREDICATE = SEM.uncertainPredicate # a predicate that is uncertain

# Verification properties
VERIFICATION_ID = SEM.verificationId  # Unique ID for pending verifications
VERIFICATION_QUESTION = SEM.verificationQuestion  # Natural language question text
VERIFICATION_STATUS = SEM.verificationStatus  # Literal["pending", "confirmed", "rejected"]
VERIFIED_AT = SEM.verifiedAt  # xsd:dateTime when verification was completed
VERIFICATION_FEEDBACK = SEM.verificationFeedback  # User's textual feedback

# Rule metadata properties
RULE_NAME = SEM.ruleName  # Name of the inference rule
RULE_DESCRIPTION = SEM.ruleDescription  # Human-readable description
RULE_CONFIDENCE = SEM.ruleConfidence  # Default confidence for the rule
RULE_ENABLED = SEM.ruleEnabled  # xsd:boolean - whether rule is active

# Standard ontology namespaces (re-exported for convenience)
from rdflib.namespace import FOAF, RDF, RDFS, SKOS, OWL, XSD

# Schema.org namespace
SCHEMA = Namespace("https://schema.org/")

# Common predicates
def get_provenance_predicates() -> list[URIRef]:
    """Return list of all provenance predicates for filtering."""
    return [
        SOURCE,
        SOURCE_RULE,
        TIMESTAMP,
        CONFIDENCE,
        UNCERTAIN,
        UNCERTAIN_PREDICATE,
        VERIFICATION_ID,
        VERIFICATION_QUESTION,
        VERIFICATION_STATUS,
        VERIFIED_AT,
        VERIFICATION_FEEDBACK,
        RULE_NAME,
        RULE_DESCRIPTION,
        RULE_CONFIDENCE,
        RULE_ENABLED,
    ]


__all__ = [
    # Custom namespace
    "SEM",
    # Provenance properties
    "SOURCE",
    "SOURCE_RULE",
    "TIMESTAMP",
    "CONFIDENCE",
    "UNCERTAIN",
    "UNCERTAIN_PREDICATE",
    # Verification properties
    "VERIFICATION_ID",
    "VERIFICATION_QUESTION",
    "VERIFICATION_STATUS",
    "VERIFIED_AT",
    "VERIFICATION_FEEDBACK",
    # Rule metadata
    "RULE_NAME",
    "RULE_DESCRIPTION",
    "RULE_CONFIDENCE",
    "RULE_ENABLED",
    # Standard namespaces
    "FOAF",
    "RDF",
    "RDFS",
    "SKOS",
    "OWL",
    "XSD",
    "SCHEMA",
    # Utility
    "get_provenance_predicates",
]
