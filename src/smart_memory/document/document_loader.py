"""
Document loading and storage management.
"""

import datetime
from pathlib import Path
from typing import Optional, Dict, List
import uuid

from rdflib import URIRef, Literal, XSD
from smart_memory.logging_config import get_logger
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.document.vocabulary import DOC
from smart_memory.document.document_parser import PDFParser, TextParser, MarkdownParser

logger = get_logger(__name__)

class DocumentLoader:
    """
    Handles loading documents from files/URLs and storing them in the Knowledge Graph.
    """

    def __init__(self, graph: ProvenanceGraph):
        self.graph = graph
        self._init_parsers()
        self._bind_namespaces()

    def _init_parsers(self):
        self.parsers = {
            ".pdf": PDFParser(),
            ".txt": TextParser(),
            ".md": MarkdownParser(),
            ".markdown": MarkdownParser()
        }

    def _bind_namespaces(self):
        """Bind document namespace to the graph."""
        self.graph.graph.bind("doc", DOC)

    def load_file(self, file_path: Path, title: Optional[str] = None, store_content: bool = False) -> URIRef:
        """
        Load a file into the knowledge graph.
        
        Args:
            file_path: Path to the file
            title: Optional title override
            store_content: Whether to store full content in the graph
            
        Returns:
            URIRef of the created document
        """
        file_path = Path(file_path)
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        extension = file_path.suffix.lower()
        parser = self.parsers.get(extension)
        
        if not parser:
            # Fallback to text parser if unknown
            logger.warning(f"No parser for {extension}, trying TextParser")
            parser = TextParser()

        # Parse document
        result = parser.parse(file_path)
        content = result["content"]
        metadata = result["metadata"]
        
        # Calculate hash
        content_hash = parser.calculate_hash(file_path)
        
        # Check for duplicates or generate ID
        # For now, we generate a new ID based on hash to allow updates or separate instances?
        # Let's use a UUID based on hash for deduplication logic if needed, 
        # or just a random UUID for the document entity.
        doc_uuid = uuid.uuid4()
        doc_uri = DOC[f"doc_{doc_uuid}"]
        
        # Metadata
        final_title = title or metadata.get("title") or file_path.name
        
        # Add triples
        self.graph.add_triple_with_provenance(
            doc_uri, DOC.title, Literal(final_title), source="document_loader"
        )
        self.graph.add_triple_with_provenance(
            doc_uri, DOC.fileFormat, Literal(metadata.get("format", "unknown")), source="document_loader"
        )
        self.graph.add_triple_with_provenance(
            doc_uri, DOC.uploadDate, Literal(datetime.datetime.now(), datatype=XSD.dateTime), source="document_loader"
        )
        self.graph.add_triple_with_provenance(
            doc_uri, DOC.contentHash, Literal(content_hash), source="document_loader"
        )
        
        if "page_count" in metadata:
            self.graph.add_triple_with_provenance(
                doc_uri, DOC.pageCount, Literal(metadata["page_count"], datatype=XSD.integer), source="document_loader"
            )
            
        if store_content:
            self.graph.add_triple_with_provenance(
                doc_uri, DOC.content, Literal(content), source="document_loader"
            )
            
        logger.info(f"Loaded document {final_title} ({doc_uri})")
        return doc_uri

    def get_document_content(self, doc_uri: URIRef) -> Optional[str]:
        """Retrieve content if stored."""
        # Query for DOC.content
        # Implementation depends on how we query.
        pass
