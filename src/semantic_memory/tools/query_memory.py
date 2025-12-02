"""
query_memory MCP tool implementation.

Executes SPARQL queries against the knowledge graph.
"""

from typing import Any

from mcp.types import Tool, TextContent

from semantic_memory.logging_config import get_logger

logger = get_logger(__name__)


# Tool definition
QUERY_MEMORY_TOOL = Tool(
    name="query_memory",
    description=(
        "Query the semantic memory graph using SPARQL. Returns ONLY facts that are formally proven "
        "(either explicitly added by user or inferred by SPARQL rules)."
        "\n\n**CRITICAL - Your Role as Assistant:**"
        "\n- You can make SOFT deductions based on language understanding (e.g., 'knows → probably acquaintances')"
        "\n- BUT you MUST distinguish between YOUR deductions and FORMALLY PROVEN facts"
        "\n- Use this tool to CHECK if your soft reasoning is formally proven"
        "\n- If not proven, use verify_inference() to confirm, then suggest_rule() to formalize"
        "\n\n**When to use:**"
        "\n- To verify if a fact exists in the graph"
        "\n- To check what the system KNOWS FOR CERTAIN (not what you deduce)"
        "\n- To explore relationships and connections"
        "\n\n**Query Guidelines:**"
        "\n- ALWAYS scope queries to user namespace with ':' prefix (e.g., ':User', ':Alice')"
        "\n- Use LIMIT to avoid overwhelming results (max 1000 auto-injected)"
        "\n- Common predicates: foaf:knows, schema:worksFor, schema:colleague, rdf:type"
        "\n\n**Example workflow:**"
        "\n1. User: 'Is Alice my friend?'"
        "\n2. You think: 'Hmm, I see :User foaf:knows :Alice, so maybe friends?'"
        "\n3. You call: verify_inference(':User', 'foaf:friend', ':Alice')"
        "\n4. Result: 'Not formally proven'"
        "\n5. You tell user: 'You know Alice, but friendship is not formally established. Should I create a rule?'"
        "\n\n**Output format:**"
        "\n- SELECT: Returns table of results as list of dicts"
        "\n- ASK: Returns boolean (True/False)"
        "\n- CONSTRUCT/DESCRIBE: Returns graph triples"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SPARQL query to execute. Common prefixes (rdf, rdfs, foaf, schema, owl, sem) are auto-added.",
            },
            "output_format": {
                "type": "string",
                "enum": ["table", "json", "turtle"],
                "description": "Output format (default: table for SELECT, turtle for CONSTRUCT)",
            },
        },
        "required": ["query"],
    },
)


import time

async def query_memory(
    arguments: dict[str, Any],
    graph,
) -> list[TextContent]:
    """
    Execute a SPARQL query against the knowledge graph.

    Args:
        arguments: Tool arguments containing 'query' and optional 'format'
        graph: ProvenanceGraph instance

    Returns:
        List of TextContent with query results
    """
    query_str = arguments["query"]
    output_format = arguments.get("format", "table")

    logger.info(f"query_memory called with {len(query_str)} char query")
    logger.debug(f"Query: {query_str}")

    # Auto-prepend common PREFIX declarations if not already present
    # This helps when Gemini forgets to include them
    # Define common prefixes
    common_prefixes = {
        ":": "<http://semanticmemory.org/user#>",
        "rdf:": "<http://www.w3.org/1999/02/22-rdf-syntax-ns#>",
        "rdfs:": "<http://www.w3.org/2000/01/rdf-schema#>",
        "owl:": "<http://www.w3.org/2002/07/owl#>",
        "foaf:": "<http://xmlns.com/foaf/0.1/>",
        "schema:": "<https://schema.org/>",
        "sem:": "<http://example.org/semanticmemory/>"
    }

    # Prepend prefixes if they are missing from the query
    prefixes_to_add = []
    query_upper = query_str.upper()
    
    for prefix, uri in common_prefixes.items():
        # Check if prefix is used but not defined
        # Simple heuristic: if "PREFIX foo:" is not in query, add it
        # We check for "PREFIX foo:" to see if user defined it manually
        if f"PREFIX {prefix}" not in query_upper:
            prefixes_to_add.append(f"PREFIX {prefix} {uri}")
            
    if prefixes_to_add:
        query_str = "\n".join(prefixes_to_add) + "\n" + query_str
        logger.debug(f"Auto-prepended {len(prefixes_to_add)} PREFIX declarations")

    try:
        # Auto-inject LIMIT for SELECT queries without explicit LIMIT to prevent token overflow
        # This protects against queries like "SELECT ?s ?p ?o WHERE { ?s ?p ?o }" which can return 17k+ results
        is_select_query = "SELECT" in query_upper
        has_limit = "LIMIT" in query_upper
        
        if is_select_query and not has_limit:
            # Inject LIMIT 1000 at the end of the query to prevent overwhelming the LLM
            # This is conservative but protects against accidental full ontology dumps
            query_str = query_str.rstrip()  # Remove trailing whitespace
            
            # Check if query ends with } (most common)
            if query_str.rstrip().endswith("}"):
                query_str += "\nLIMIT 1000"
                logger.warning(
                    "Auto-injected LIMIT 1000 to unbounded SELECT query to prevent token overflow. "
                    "For larger result sets, explicitly add LIMIT clause."
                )
            else:
                # Query has other structure, safer to not modify
                logger.warning(
                    "SELECT query without LIMIT detected but query structure unclear. "
                    "Results may be very large. Consider adding explicit LIMIT."
                )
        
        # Execute the SPARQL query
        start_time = time.time()
        results = graph.query(query_str)
        execution_time_ms = (time.time() - start_time) * 1000
        logger.info(f"Query executed in {execution_time_ms:.2f} ms")

        # Check if this is an ASK query FIRST (returns boolean)
        if isinstance(results, bool):
            response_text = f"Query result: {results}\n\nExecution time: {execution_time_ms:.2f} ms"
            logger.info(f"Query returned boolean: {results}")
        
        # Format results based on output format
        elif output_format == "json":
            # Return as JSON
            import json

            result_list = list(results)
            response_text = json.dumps(result_list, indent=2, default=str)
            logger.info(f"Query returned {len(result_list)} results")

        elif output_format == "turtle":
            # For CONSTRUCT/DESCRIBE queries, serialize as Turtle
            from rdflib import Graph
            if isinstance(results, Graph):
                response_text = results.serialize(format="turtle")
                logger.info("Query returned a graph (CONSTRUCT/DESCRIBE)")
            elif hasattr(results, "graph"):
                response_text = results.graph.serialize(format="turtle")
                logger.info("Query returned a graph (CONSTRUCT/DESCRIBE)")
            else:
                response_text = "Query did not return a graph (use CONSTRUCT or DESCRIBE for Turtle output)"
                logger.warning("Turtle format requested but query did not return a graph")

        else:  # table format (default)
            result_list = list(results)

            if not result_list:
                response_text = "No results found."
                logger.info("Query returned 0 results")
            else:
                # Format as a readable table
                response_lines = [f"Found {len(result_list)} result(s) in {execution_time_ms:.2f} ms:\n"]

                for i, row in enumerate(result_list, 1):
                    response_lines.append(f"\n--- Result {i} ---")

                    if isinstance(row, dict):
                        for key, value in row.items():
                            response_lines.append(f"  {key}: {value}")
                    else:
                        # Handle tuple results
                        for j, value in enumerate(row):
                            response_lines.append(f"  {j}: {value}")

                response_text = "\n".join(response_lines)
                logger.info(f"Query returned {len(result_list)} results")

    except Exception as e:
        logger.error(f"Query execution failed: {e}", exc_info=True)
        response_text = f"Query failed: {str(e)}\n\nPlease check your SPARQL syntax."

    return [TextContent(type="text", text=response_text)]


__all__ = ["QUERY_MEMORY_TOOL", "query_memory"]
