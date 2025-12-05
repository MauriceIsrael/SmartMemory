"""
RDF Vocabulary for SmartMemory Documents.
"""

from rdflib import Namespace

# Document Namespace
DOC = Namespace("http://semanticmemory.org/document#")

# Predicates
DOC.title
DOC.uploadDate
DOC.fileFormat     # Renamed from format to avoid collision
DOC.sourceUrl      # Original URL if loaded from web
DOC.contentHash    # SHA-256 hash for deduplication
DOC.pageCount      # Number of pages (for PDF)
DOC.extractedRule  # Link to an extracted rule
DOC.content        # Full content (optional)
DOC.chunkOf        # For linking chunks to parent document
