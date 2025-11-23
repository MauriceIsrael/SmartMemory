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
        "Execute a SPARQL query against the knowledge graph. "
        "Supports SELECT, CONSTRUCT, ASK, and DESCRIBE queries. "
        "Returns results in a readable format."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "SPARQL query to execute",
            },
            "format": {
                "type": "string",
                "enum": ["table", "json", "turtle"],
                "default": "table",
                "description": "Output format for results",
            },
        },
        "required": ["query"],
    },
)


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

    try:
        # Execute the query
        results = graph.query(query_str)

        # Format results based on output format
        if output_format == "json":
            # Return as JSON
            import json

            result_list = list(results)
            response_text = json.dumps(result_list, indent=2, default=str)

        elif output_format == "turtle":
            # For CONSTRUCT queries, serialize as Turtle
            if hasattr(results, "graph"):
                response_text = results.graph.serialize(format="turtle")
            else:
                response_text = "Query did not return a graph (use CONSTRUCT for Turtle output)"

        else:  # table format (default)
            result_list = list(results)

            if not result_list:
                response_text = "No results found."
            else:
                # Format as a readable table
                response_lines = [f"Found {len(result_list)} result(s):\n"]

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

        logger.info(f"Query returned {len(list(results)) if hasattr(results, '__iter__') else 0} results")

    except Exception as e:
        logger.error(f"Query execution failed: {e}", exc_info=True)
        response_text = f"Query failed: {str(e)}\n\nPlease check your SPARQL syntax."

    return [TextContent(type="text", text=response_text)]


__all__ = ["QUERY_MEMORY_TOOL", "query_memory"]
