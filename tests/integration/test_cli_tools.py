import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from src.cli.add_fact import main as add_fact_main
from src.cli.get_pending_verifications import main as get_pending_main
from src.models.knowledge_graph import KnowledgeGraph
from src.services.persistence_service import PersistenceService

def test_add_fact_integration(tmp_path):
    # Use a temporary file for the knowledge graph
    ttl_file = tmp_path / "knowledge_graph.ttl"
    
    # Patch PersistenceService to use the temp file
    # We need to patch where it is instantiated in add_fact.py
    # Actually add_fact.py instantiates PersistenceService('knowledge_graph.ttl') directly.
    # We can patch PersistenceService class to return an instance with our path.
    
    with patch('src.cli.add_fact.PersistenceService') as MockPersistenceService:
        # Setup the mock to behave like real service but with our file
        real_service = PersistenceService(str(ttl_file))
        MockPersistenceService.return_value = real_service
        
        # Mock sys.argv
        with patch.object(sys, 'argv', ['add_fact.py', 'Subject', 'Predicate', 'Object']):
            add_fact_main()
            
    # Verify file was created/updated
    assert os.path.exists(ttl_file)
    
    # Verify content
    kg = PersistenceService(str(ttl_file)).load()
    assert len(kg.explicit_graph) == 1
    # Check if triple exists (Subject, Predicate, Object)
    # Note: add_fact.py uses Triple(subject=..., ...) which treats strings as literals unless they look like URIs.
    # The arguments passed are "Subject", "Predicate", "Object".
    # KnowledgeGraph._to_node converts them to Literal unless they start with http or :
    # So they should be Literals.
    # Wait, add_fact.py: Triple(subject=args.subject, ...)
    # KnowledgeGraph.add_explicit: s = URIRef(triple.subject) -> This assumes subject is URI.
    # If I pass "Subject", URIRef("Subject") might be invalid or relative.
    # Let's pass ":Subject", ":Predicate", ":Object" to be safe and consistent with logic.
    
def test_add_fact_integration_with_uris(tmp_path):
    ttl_file = tmp_path / "knowledge_graph.ttl"
    
    with patch('src.cli.add_fact.PersistenceService') as MockPersistenceService:
        real_service = PersistenceService(str(ttl_file))
        MockPersistenceService.return_value = real_service
        
        with patch.object(sys, 'argv', ['add_fact.py', ':Subject', ':Predicate', ':Object']):
            add_fact_main()
            
    kg = PersistenceService(str(ttl_file)).load()
    assert len(kg.explicit_graph) == 1
    
def test_get_pending_verifications_integration(capsys):
    # Since VerificationService is in-memory and not shared, this will just print nothing or empty.
    # We can patch VerificationService to return some mock data to verify the printing logic.
    
    with patch('src.cli.get_pending_verifications.VerificationService') as MockVerificationService:
        mock_service = MockVerificationService.return_value
        mock_request = MagicMock()
        mock_request.json.return_value = '{"id": "1", "triple": "test"}'
        mock_service.get_pending.return_value = [mock_request]
        
        with patch.object(sys, 'argv', ['get_pending_verifications.py']):
            get_pending_main()
            
    captured = capsys.readouterr()
    assert '{"id": "1", "triple": "test"}' in captured.out
