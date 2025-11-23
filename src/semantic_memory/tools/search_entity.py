"""
search_entity MCP tool implementation.

Performs full-text search for entities in the knowledge graph.
"""

from typing import Any

from mcp.types import Tool, TextContent
from rdflib.namespace import RDFS

from semantic_memory.logging_config import get_logger
from semantic_memory.vocabulary import FOAF, SCHEMA

logger = get_logger(__name__)


# Tool definition
SEARCH_ENTITY_TOOL = Tool(
    name="search_entity",
    description=(
        "Search for entities in the knowledge graph by name or label. "
        "Returns matching entities with their types and key properties."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "search_term": {
                "type": "string",
                "description": "Text to search for in entity names/labels",
            },
            "entity_type": {
                "type": "string",
                "description": "Optional filter by entity type (e.g., 'Person', 'Organization')",
            },
            "limit": {
                "type": "integer",
                "default": 10,
                "description": "Maximum number of results to return",
            },
        },
        "required": ["search_term"],
    },
)


async def search_entity(
    arguments: dict[str, Any],
    graph,
) -> list[TextContent]:
    """
    Search for entities in the knowledge graph.

    Args:
        arguments: Tool arguments containing 'search_term', optional 'entity_type' and 'limit'
        graph: ProvenanceGraph instance

    Returns:
        List of TextContent with search results
    """
    search_term = arguments["search_term"].lower()
    entity_type = arguments.get("entity_type")
    limit = arguments.get("limit", 10)

    logger.info(f"search_entity called with term: {search_term}")

    # Build SPARQL query
    # Search in foaf:name, rdfs:label, and schema:name
    query = f"""
    SELECT DISTINCT ?entity ?name ?type
    WHERE {{
        ?entity ?nameProp ?name .

        # Search in common name properties
        FILTER(
            ?nameProp = foaf:name ||
            ?nameProp = rdfs:label ||
            ?nameProp = schema:name
        )

        # Case-insensitive substring match
        FILTER(CONTAINS(LCASE(STR(?name)), "{search_term}"))

        # Get entity type if available
        OPTIONAL {{ ?entity a ?type }}

        {f'FILTER(?type = {entity_type})' if entity_type else ''}
    }}
    LIMIT {limit}
    """

    try:
        results = graph.query(query)
        result_list = list(results)

        if not result_list:
            # Fallback: search in all URIs that contain the term
            fallback_query = f"""
            SELECT DISTINCT ?entity
            WHERE {{
                ?entity ?p ?o .
                FILTER(CONTAINS(LCASE(STR(?entity)), "{search_term}"))
            }}
            LIMIT {limit}
            """

            results = graph.query(fallback_query)
            result_list = list(results)

            if not result_list:
                response_text = f"No entities found matching '{search_term}'."
            else:
                response_lines = [f"Found {len(result_list)} entity URI(s) matching '{search_term}':\n"]

                for row in result_list:
                    entity = row["entity"] if isinstance(row, dict) else row[0]
                    response_lines.append(f"  • {entity}")

                    # Get some properties of this entity
                    props_query = f"""
                    SELECT ?p ?o
                    WHERE {{
                        <{entity}> ?p ?o .
                    }}
                    LIMIT 3
                    """

                    props_results = graph.query(props_query)
                    for prop_row in props_results:
                        p = prop_row["p"] if isinstance(prop_row, dict) else prop_row[0]
                        o = prop_row["o"] if isinstance(prop_row, dict) else prop_row[1]
                        response_lines.append(f"      {p.split('#')[-1]}: {o}")

                response_text = "\n".join(response_lines)

        else:
            # Format results with names and types
            response_lines = [f"Found {len(result_list)} matching entities:\n"]

            for row in result_list:
                if isinstance(row, dict):
                    entity = row.get("entity")
                    name = row.get("name")
                    entity_type_uri = row.get("type")
                else:
                    entity = row[0]
                    name = row[1] if len(row) > 1 else None
                    entity_type_uri = row[2] if len(row) > 2 else None

                # Format type
                if entity_type_uri:
                    type_str = str(entity_type_uri).split("#")[-1].split("/")[-1]
                    response_lines.append(f"  • {name} ({type_str})")
                else:
                    response_lines.append(f"  • {name}")

                response_lines.append(f"    URI: {entity}")

                # Get additional key properties
                detail_query = f"""
                SELECT ?p ?o
                WHERE {{
                    <{entity}> ?p ?o .
                    FILTER(?p != rdf:type)
                    FILTER(?p != rdfs:label)
                    FILTER(?p != foaf:name)
                    FILTER(?p != schema:name)
                }}
                LIMIT 5
                """

                detail_results = graph.query(detail_query)
                for detail_row in detail_results:
                    if isinstance(detail_row, dict):
                        p = detail_row["p"]
                        o = detail_row["o"]
                    else:
                        p = detail_row[0]
                        o = detail_row[1]

                    prop_name = str(p).split("#")[-1].split("/")[-1]
                    response_lines.append(f"    {prop_name}: {o}")

                response_lines.append("")  # Blank line between results

            response_text = "\n".join(response_lines)

    except Exception as e:
        logger.error(f"Search failed: {e}", exc_info=True)
        response_text = f"Search failed: {str(e)}"

    return [TextContent(type="text", text=response_text)]


__all__ = ["SEARCH_ENTITY_TOOL", "search_entity"]
