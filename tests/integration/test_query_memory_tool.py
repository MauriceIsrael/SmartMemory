"""
Integration tests for query_memory tool.

Tests the complete LLM interaction flow including auto-prefixing.
These tests reflect how the LLM will actually use the query_memory tool.
"""

import pytest
from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.tools.query_memory import query_memory
from smart_memory.vocabulary import FOAF, SCHEMA
from rdflib import Namespace, Literal as RDFLiteral

USER_NS = Namespace("http://semanticmemory.org/user#")


@pytest.fixture
def populated_graph():
    """Graph with test data for query_memory tests."""
    graph = ProvenanceGraph()
    
    # Add Thales employees
    employees = ["Gilles", "Jérémie", "Coralie", "Daniel"]
    for emp in employees:
        graph.add_triple_with_provenance(
            USER_NS[emp],
            FOAF.name,
            RDFLiteral(emp),
            source="user"
        )
        graph.add_triple_with_provenance(
            USER_NS[emp],
            SCHEMA.worksFor,
            USER_NS.Thales,
            source="user"
        )
    
    # Add some relationships
    graph.add_triple_with_provenance(
        USER_NS.User,
        FOAF.knows,
        USER_NS.Gilles,
        source="user"
    )
    
    # Add ages
    graph.add_triple_with_provenance(
        USER_NS.Gilles,
        FOAF.age,
        RDFLiteral(35),
        source="user"
    )
    graph.add_triple_with_provenance(
        USER_NS.Daniel,
        FOAF.age,
        RDFLiteral(28),
        source="user"
    )
    
    return graph


class TestAutoPrefixing:
    """Test that query_memory auto-adds PREFIX declarations like the LLM expects."""
    
    @pytest.mark.asyncio
    async def test_query_without_prefix_declarations(self, populated_graph):
        """LLM might forget PREFIX declarations - tool should add them automatically."""
        # Query WITHOUT any PREFIX declarations (LLM forgot them)
        query = """
        SELECT ?employee WHERE {
            ?employee schema:worksFor :Thales .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        assert "Gilles" in result[0].text
        assert "Jérémie" in result[0].text or "Jeremie" in result[0].text
        assert "Coralie" in result[0].text
        assert "Daniel" in result[0].text
    
    @pytest.mark.asyncio
    async def test_query_with_colon_prefix(self, populated_graph):
        """Test that ':Entity' syntax works (default namespace)."""
        query = """
        SELECT ?name WHERE {
            :Gilles foaf:name ?name .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        assert "Gilles" in result[0].text
    
    @pytest.mark.asyncio
    async def test_manual_prefix_preserved(self, populated_graph):
        """If LLM provides PREFIX, it should be preserved."""
        query = """
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX schema: <https://schema.org/>
        SELECT ?employee WHERE {
            ?employee schema:worksFor :Thales .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        assert "4 result" in result[0].text  # 4 employees
    
    @pytest.mark.asyncio
    async def test_all_common_prefixes_available(self, populated_graph):
        """All common prefixes should be auto-added."""
        # Query using multiple prefixes without declaring them
        query = """
        SELECT ?person ?name ?company WHERE {
            ?person foaf:name ?name .
            ?person schema:worksFor ?company .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        assert "result" in result[0].text.lower()


class TestOutputFormats:
    """Test different output formats as LLM would request them."""
    
    @pytest.mark.asyncio
    async def test_default_table_format(self, populated_graph):
        """Default format should be table (readable for LLM)."""
        query = """
        SELECT ?name WHERE {
            :Gilles foaf:name ?name .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        assert "Result 1" in text or "result" in text.lower()
        assert "Gilles" in text
    
    @pytest.mark.asyncio
    async def test_json_format(self, populated_graph):
        """JSON format for structured data."""
        query = """
        SELECT ?name WHERE {
            :Gilles foaf:name ?name .
        }
        """
        
        result = await query_memory(
            {"query": query, "format": "json"},
            populated_graph
        )
        
        assert len(result) == 1
        text = result[0].text
        # Should be valid JSON
        import json
        data = json.loads(text)
        assert isinstance(data, list)
    
    @pytest.mark.asyncio
    async def test_turtle_format_for_construct(self, populated_graph):
        """Turtle format for CONSTRUCT queries."""
        query = """
        CONSTRUCT {
            ?person a foaf:Person .
        }
        WHERE {
            ?person foaf:name ?name .
        }
        """
        
        result = await query_memory(
            {"query": query, "format": "turtle"},
            populated_graph
        )
        
        assert len(result) == 1
        text = result[0].text
        # Should contain Turtle syntax
        assert "@prefix" in text or "foaf:Person" in text


class TestRealWorldQueries:
    """Test queries that LLM would actually generate based on user requests."""
    
    @pytest.mark.asyncio
    async def test_find_colleagues_natural_query(self, populated_graph):
        """LLM query: 'Who are Daniel's colleagues?'"""
        # This is how the LLM might formulate it
        query = """
        SELECT ?colleague WHERE {
            :Daniel schema:worksFor ?company .
            ?colleague schema:worksFor ?company .
            FILTER(?colleague != :Daniel)
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        assert "Gilles" in text
        assert "Jérémie" in text or "Jeremie" in text
        assert "Coralie" in text
        # Daniel should NOT be in results
        assert text.count("Daniel") <= 1  # Might appear in header but not in results
    
    @pytest.mark.asyncio
    async def test_check_relationship_ask_query(self, populated_graph):
        """LLM query: 'Does User know Gilles?'"""
        query = """
        ASK {
            :User foaf:knows :Gilles
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        assert "True" in result[0].text or "true" in result[0].text
    
    @pytest.mark.asyncio
    async def test_find_people_by_age_range(self, populated_graph):
        """LLM query: 'Who is older than 30?'"""
        query = """
        SELECT ?person ?age WHERE {
            ?person foaf:age ?age .
            FILTER(?age > 30)
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        assert "Gilles" in text  # Age 35
        assert "Daniel" not in text  # Age 28
    
    @pytest.mark.asyncio
    async def test_count_employees(self, populated_graph):
        """LLM query: 'How many people work at Thales?'"""
        query = """
        SELECT (COUNT(?employee) AS ?count) WHERE {
            ?employee schema:worksFor :Thales .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        assert "4" in result[0].text  # 4 employees


class TestErrorHandling:
    """Test error handling as LLM would encounter it."""
    
    @pytest.mark.asyncio
    async def test_syntax_error_helpful_message(self, populated_graph):
        """Syntax errors should give helpful feedback to LLM."""
        # Invalid SPARQL syntax
        query = """
        SELECT ?person WHERE
            ?person foaf:name ?name
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        assert "failed" in text.lower() or "error" in text.lower()
        assert "syntax" in text.lower()
    
    @pytest.mark.asyncio
    async def test_no_results_clear_message(self, populated_graph):
        """No results should be clearly communicated."""
        query = """
        SELECT ?person WHERE {
            ?person foaf:name "NonExistent" .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        assert "No results" in text or "0 result" in text


class TestPerformanceMetrics:
    """Test that performance metrics are reported to LLM."""
    
    @pytest.mark.asyncio
    async def test_execution_time_reported(self, populated_graph):
        """Execution time should be reported in results."""
        query = """
        SELECT ?person WHERE {
            ?person foaf:name ?name .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        # Should contain timing information
        assert "ms" in text.lower() or "time" in text.lower()
    
    @pytest.mark.asyncio
    async def test_result_count_reported(self, populated_graph):
        """Number of results should be clearly stated."""
        query = """
        SELECT ?employee WHERE {
            ?employee schema:worksFor :Thales .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        # Should state number of results
        assert "4" in text and "result" in text.lower()


class TestLLMPromptCompatibility:
    """Test that queries work as LLM would generate them from prompts."""
    
    @pytest.mark.asyncio
    async def test_french_user_prompt_query(self, populated_graph):
        """Test query generated from French prompt: 'Qui travaille chez Thales?'"""
        # LLM generates this query
        query = """
        SELECT ?person ?name WHERE {
            ?person schema:worksFor :Thales .
            ?person foaf:name ?name .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        assert "Gilles" in text
        assert "Daniel" in text
    
    @pytest.mark.asyncio
    async def test_verify_inference_prompt(self, populated_graph):
        """Test query for verifying inferences: 'Show me inferred facts'"""
        # LLM might generate this to check for inferred triples
        query = """
        SELECT ?s ?p ?o WHERE {
            ?stmt a rdf:Statement ;
                  rdf:subject ?s ;
                  rdf:predicate ?p ;
                  rdf:object ?o ;
                  sem:source ?source .
            FILTER(?source = "sparql-rule")
        }
        LIMIT 10
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        # Should execute without error (even if no inferred facts yet)
        assert len(result) == 1
    
    @pytest.mark.asyncio
    async def test_property_path_from_natural_language(self, populated_graph):
        """Test property path query from: 'What are the names of people User knows?'"""
        query = """
        SELECT ?friendName WHERE {
            :User foaf:knows/foaf:name ?friendName .
        }
        """
        
        result = await query_memory({"query": query}, populated_graph)
        
        assert len(result) == 1
        text = result[0].text
        assert "Gilles" in text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
