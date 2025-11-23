import pytest
from unittest.mock import MagicMock, patch
from src.services.persistence_service import PersistenceService
from src.models.knowledge_graph import KnowledgeGraph

def test_save_calls_serialize():
    service = PersistenceService("test.ttl")
    mock_kg = MagicMock(spec=KnowledgeGraph)
    mock_kg.explicit_graph = MagicMock()
    
    service.save(mock_kg)
    
    mock_kg.explicit_graph.serialize.assert_called_once_with(destination="test.ttl", format='turtle')

def test_load_calls_parse():
    service = PersistenceService("test.ttl")
    
    with patch('src.services.persistence_service.KnowledgeGraph') as MockKG:
        mock_kg_instance = MockKG.return_value
        mock_kg_instance.explicit_graph = MagicMock()
        
        result = service.load()
        
        mock_kg_instance.explicit_graph.parse.assert_called_once_with("test.ttl", format='turtle')
        assert result == mock_kg_instance

def test_load_file_not_found():
    service = PersistenceService("non_existent.ttl")
    
    with patch('src.services.persistence_service.KnowledgeGraph') as MockKG:
        mock_kg_instance = MockKG.return_value
        mock_kg_instance.explicit_graph = MagicMock()
        mock_kg_instance.explicit_graph.parse.side_effect = FileNotFoundError
        
        result = service.load()
        
        # Should return empty graph and log warning (not crash)
        assert result == mock_kg_instance
