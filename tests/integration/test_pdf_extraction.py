
import pytest
from pathlib import Path
import fitz
import os
from smart_memory.document.document_loader import DocumentLoader
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.document.vocabulary import DOC

@pytest.fixture
def graph():
    return ProvenanceGraph()

@pytest.fixture
def loader(graph):
    return DocumentLoader(graph)

@pytest.fixture
def sample_pdf(tmp_path):
    pdf_path = tmp_path / "test_doc.pdf"
    doc = fitz.open()
    page = doc.new_page()
    page.insert_text((50, 72), "This is a test PDF document.\nIt has multiple lines.")
    doc.set_metadata({
        "title": "Test Document",
        "author": "Test Author"
    })
    doc.save(pdf_path)
    return pdf_path

def test_pdf_parsing_and_loading(loader, sample_pdf, graph):
    # Load document
    doc_uri = loader.load_file(sample_pdf, store_content=True)
    
    # Query graph
    query = """
    PREFIX doc: <http://semanticmemory.org/document#>
    SELECT ?title ?format ?pageCount ?content
    WHERE {
        ?doc doc:title ?title ;
              doc:fileFormat ?format ;
              doc:pageCount ?pageCount ;
              doc:content ?content .
    }
    """
    
    results = list(graph.query(query))
    assert len(results) == 1
    
    row = results[0]
    assert str(row["title"]) == "Test Document"
    assert str(row["format"]) == "pdf"
    assert int(row["pageCount"]) == 1
    assert "This is a test PDF document" in str(row["content"])

def test_metadata_only_loading(loader, sample_pdf, graph):
    doc_uri = loader.load_file(sample_pdf, store_content=False)
    
    # Verify content IS NOT stored
    content_query = """
    PREFIX doc: <http://semanticmemory.org/document#>
    ASK { ?doc doc:content ?content }
    """
    assert not graph.query(content_query)
    
    # Verify metadata IS stored
    meta_query = """
    PREFIX doc: <http://semanticmemory.org/document#>
    ASK { ?doc doc:title "Test Document" }
    """
    assert graph.query(meta_query)
