import sys
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

# Add the project root to sys.path to allow imports from 'src'
# This is needed because the backend code imports from 'smart_memory' which is in 'src'
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent))

from main import app

client = TestClient(app)

def test_read_stats():
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_triplets" in data
    assert "inferred_triplet_count" in data
    assert "asserted_triplet_count" in data
    assert "active_rule_count" in data
    assert "inactive_rule_count" in data

def test_read_facts():
    response = client.get("/api/facts")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total_items" in data
    assert isinstance(data["items"], list)

def test_read_facts_pagination():
    response = client.get("/api/facts?page=1&page_size=5")
    assert response.status_code == 200
    data = response.json()
    assert len(data["items"]) <= 5

def test_read_rules():
    response = client.get("/api/rules")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    if len(data) > 0:
        rule = data[0]
        assert "id" in rule
        assert "is_active" in rule

def test_toggle_rule():
    # First get a rule to toggle
    response = client.get("/api/rules")
    data = response.json()
    if len(data) > 0:
        rule_id = data[0]["id"]
        initial_state = data[0]["is_active"]
        
        # Toggle it
        response = client.post(f"/api/rules/{rule_id}/toggle")
        assert response.status_code == 200
        new_state = response.json()["is_active"]
        assert new_state != initial_state
        
        # Toggle it back to restore state
        client.post(f"/api/rules/{rule_id}/toggle")

def test_run_inference():
    # This might take time, so we just check if it accepts the request
    # or mocks the actual inference if it's too heavy.
    # For now, let's assume it runs quickly enough or we accept it might be slow.
    response = client.post("/api/inference/run")
    assert response.status_code == 202
    data = response.json()
    assert "status" in data
    assert "triples_inferred" in data
