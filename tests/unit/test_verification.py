import pytest
from rdflib import Namespace, Literal, OWL, RDF
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.knowledge.verification import VerificationRequest
from smart_memory.tools.verify_inference import verify_inference

# Use the same namespace as TripleExtractor
USER_NS = Namespace("http://semanticmemory.org/user#")

@pytest.fixture
def provenance_graph():
    return ProvenanceGraph()

@pytest.fixture
def verification_request():
    return VerificationRequest(
        triple=(USER_NS.subject, USER_NS.predicate, USER_NS.object),
        confidence=0.6,
        source_rule="test_rule",
        context={},
    )

@pytest.mark.asyncio
async def test_accept_verification_request(provenance_graph, verification_request):
    provenance_graph.add_pending_verification(verification_request)
    
    assert len(provenance_graph.pending_verifications_graph) > 0
    
    # Use prefix notation as the TripleExtractor expects
    args = {
        "triple": ":subject :predicate :object",
        "action": "accept",
    }
    
    result = await verify_inference(args, provenance_graph)
    
    assert "Inference accepted" in result[0].text
    assert len(provenance_graph.pending_verifications_graph) == 0
    assert (USER_NS.subject, USER_NS.predicate, USER_NS.object) in provenance_graph.graph

@pytest.mark.asyncio
async def test_reject_verification_request(provenance_graph, verification_request):
    provenance_graph.add_pending_verification(verification_request)
    
    assert len(provenance_graph.pending_verifications_graph) > 0
    
    # Use prefix notation as the TripleExtractor expects
    args = {
        "triple": ":subject :predicate :object",
        "action": "reject",
    }
    
    result = await verify_inference(args, provenance_graph)
    
    assert "Inference rejected" in result[0].text
    assert len(provenance_graph.pending_verifications_graph) == 0
    assert (USER_NS.subject, USER_NS.predicate, USER_NS.object) not in provenance_graph.graph
    assert (USER_NS.subject, USER_NS.predicate, USER_NS.object) in provenance_graph.rejected_verifications_graph
