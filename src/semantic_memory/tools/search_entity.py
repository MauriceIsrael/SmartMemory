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
    import time
    from collections import defaultdict
    
    search_term = arguments["search_term"].lower()
    entity_type = arguments.get("entity_type")
    limit = arguments.get("limit", 10)

    start_time = time.time()
    logger.info(f"search_entity called with term: {search_term}")

    # OPTIMIZED: Main query to find matching entities
    query = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX foaf: <http://xmlns.com/foaf/0.1/>
    PREFIX schema: <https://schema.org/>
    
    SELECT DISTINCT ?entity ?name ?type
    WHERE {{
        # Find entities by name
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
                elapsed = time.time() - start_time
                logger.info(f"search_entity completed in {elapsed:.3f}s - no results")
                response_text = f"No entities found matching '{search_term}'."
            else:
                # OPTIMIZED: Batch query for all entity properties at once
                entity_uris = [str(row["entity"] if isinstance(row, dict) else row[0]) for row in result_list]
                values_clause = " ".join([f"<{uri}>" for uri in entity_uris])
                
                batch_props_query = f"""
                PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
                
                SELECT ?entity ?p ?o
                WHERE {{
                    VALUES ?entity {{ {values_clause} }}
                    ?entity ?p ?o .
                }}
                """
                
                props_results = graph.query(batch_props_query)
                
                # Group properties by entity
                entity_props = defaultdict(list)
                for prop_row in props_results:
                    e = prop_row["entity"] if isinstance(prop_row, dict) else prop_row[0]
                    p = prop_row["p"] if isinstance(prop_row, dict) else prop_row[1]
                    o = prop_row["o"] if isinstance(prop_row, dict) else prop_row[2]
                    entity_props[str(e)].append((p, o))
                
                response_lines = [f"Found {len(result_list)} entity URI(s) matching '{search_term}':\n"]

                for row in result_list:
                    entity = row["entity"] if isinstance(row, dict) else row[0]
                    entity_str = str(entity)
                    
                    response_lines.append(f"  • {entity_str}")

                    # Display first 5 properties
                    for p, o in entity_props[entity_str][:5]:
                        prop_name = str(p).split("#")[-1].split("/")[-1]
                        response_lines.append(f"      {prop_name}: {o}")

                response_text = "\n".join(response_lines)
                elapsed = time.time() - start_time
                logger.info(f"search_entity completed in {elapsed:.3f}s - {len(result_list)} fallback results")

        else:
            # OPTIMIZED: Batch query for all entity properties at once
            entity_uris = []
            entity_map = {}  # Store entity details
            
            for row in result_list:
                if isinstance(row, dict):
                    entity = row.get("entity")
                    name = row.get("name")
                    entity_type_uri = row.get("type")
                else:
                    entity = row[0]
                    name = row[1] if len(row) > 1 else None
                    entity_type_uri = row[2] if len(row) > 2 else None
                
                entity_str = str(entity)
                entity_uris.append(entity_str)
                entity_map[entity_str] = {
                    "name": name,
                    "type": entity_type_uri,
                    "entity": entity
                }
            
            # Fetch all properties in one batch query
            values_clause = " ".join([f"<{uri}>" for uri in entity_uris])
            
            batch_detail_query = f"""
            PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
            PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            PREFIX schema: <https://schema.org/>
            
            SELECT ?entity ?p ?o
            WHERE {{
                VALUES ?entity {{ {values_clause} }}
                ?entity ?p ?o .
                FILTER(?p != rdf:type)
                FILTER(?p != rdfs:label)
                FILTER(?p != foaf:name)
                FILTER(?p != schema:name)
            }}
            """
            
            detail_results = graph.query(batch_detail_query)
            
            # Group properties by entity
            entity_props = defaultdict(list)
            for detail_row in detail_results:
                e = detail_row["entity"] if isinstance(detail_row, dict) else detail_row[0]
                p = detail_row["p"] if isinstance(detail_row, dict) else detail_row[1]
                o = detail_row["o"] if isinstance(detail_row, dict) else detail_row[2]
                entity_props[str(e)].append((p, o))
            
            # Format results
            response_lines = [f"Found {len(result_list)} matching entities:\n"]

            for entity_str in entity_uris:
                entity_data = entity_map[entity_str]
                name = entity_data["name"]
                entity_type_uri = entity_data["type"]
                entity = entity_data["entity"]

                # Format type
                if entity_type_uri:
                    type_str = str(entity_type_uri).split("#")[-1].split("/")[-1]
                    response_lines.append(f"  • {name} ({type_str})")
                else:
                    response_lines.append(f"  • {name}")

                response_lines.append(f"    URI: {entity}")

                # Display first 5 additional properties
                for p, o in entity_props[entity_str][:5]:
                    prop_name = str(p).split("#")[-1].split("/")[-1]
                    response_lines.append(f"    {prop_name}: {o}")

                response_lines.append("")  # Blank line between results

            response_text = "\n".join(response_lines)
            elapsed = time.time() - start_time
            logger.info(f"search_entity completed in {elapsed:.3f}s - {len(result_list)} results")

    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"Search failed after {elapsed:.3f}s: {e}", exc_info=True)
        response_text = f"Search failed: {str(e)}"

    return [TextContent(type="text", text=response_text)]


__all__ = ["SEARCH_ENTITY_TOOL", "search_entity"]
