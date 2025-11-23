"""
MCP Server entry point for Semantic Memory.

This module initializes and runs the Model Context Protocol server,
exposing semantic memory tools to AI agents.
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server

from semantic_memory.config import config
from semantic_memory.logging_config import get_logger

logger = get_logger(__name__)


class SemanticMemoryServer:
    """
    MCP server for semantic memory operations.

    Provides tools for storing, querying, and reasoning over RDF knowledge graphs.
    """

    def __init__(self):
        """Initialize the Semantic Memory server."""
        self.server = Server("semantic-memory")
        self.graph = None  # Will be initialized in startup
        self.ontology_loader = None
        self.reasoner = None
        self.rule_engine = None
        self.triple_extractor = None

        logger.info(f"Initializing Semantic Memory Server v{self._get_version()}")
        logger.debug(f"Cache directory: {config.cache_dir}")
        logger.debug(f"Persistence path: {config.persistence_path}")
        logger.debug(f"Persistence backend: {config.persistence_backend}")

    def _get_version(self) -> str:
        """Get the server version."""
        from semantic_memory import __version__
        return __version__

    async def startup(self) -> None:
        """
        Initialize server components.

        This method is called when the server starts up and handles:
        1. Loading the persisted knowledge graph
        2. Loading standard ontologies (FOAF, Schema.org, etc.)
        3. Applying OWL-RL reasoning
        4. Loading default SPARQL rules
        5. Loading user-defined rules
        """
        logger.info("Starting up Semantic Memory server...")

        # Initialize ProvenanceGraph
        from semantic_memory.knowledge import ProvenanceGraph

        self.graph = ProvenanceGraph()
        logger.info("Provenance graph initialized")

        # Load persisted knowledge graph if it exists
        if config.persistence_path.exists():
            try:
                self.graph.load_from_file(config.persistence_path)
                logger.info(
                    f"Loaded {self.graph.get_triple_count()} triples from {config.persistence_path}"
                )
            except Exception as e:
                logger.warning(f"Failed to load persisted graph: {e}")

        # Initialize triple extractor
        from semantic_memory.nlp import TripleExtractor

        self.triple_extractor = TripleExtractor()
        logger.info("Triple extractor initialized")

        # Load standard ontologies
        from semantic_memory.inference.ontology_loader import OntologyLoader

        self.ontology_loader = OntologyLoader()
        try:
            await self.ontology_loader.load_standard_ontologies(self.graph)
            logger.info("Standard ontologies loaded")
        except Exception as e:
            logger.error(f"Failed to load ontologies: {e}", exc_info=True)
            logger.warning("Continuing without ontologies...")

        # Initialize reasoner
        from semantic_memory.inference.reasoner import Reasoner

        self.reasoner = Reasoner()
        logger.info("Reasoner initialized")

        # Apply initial OWL-RL reasoning
        try:
            inferred = self.reasoner.apply_closure(self.graph)
            logger.info(f"Initial OWL-RL reasoning inferred {inferred} triples")
        except Exception as e:
            logger.error(f"Initial reasoning failed: {e}", exc_info=True)

        # TODO: Load inference rules (Phase 4 - User Story 2)
        # from semantic_memory.inference.rule_engine import RuleEngine
        # self.rule_engine = RuleEngine()
        # await self.rule_engine.load_default_rules()

        logger.info(
            f"Semantic Memory server startup complete. "
            f"Knowledge graph has {self.graph.get_triple_count()} triples."
        )

    async def shutdown(self) -> None:
        """
        Cleanup server resources.

        Saves the knowledge graph to persistence before shutting down.
        """
        logger.info("Shutting down Semantic Memory server...")

        # Save graph to persistence
        if self.graph:
            try:
                self.graph.save_to_file(config.persistence_path)
                logger.info(
                    f"Knowledge graph saved to {config.persistence_path} "
                    f"({self.graph.get_triple_count()} triples)"
                )
            except Exception as e:
                logger.error(f"Failed to save graph: {e}", exc_info=True)

        logger.info("Shutdown complete")

    def register_tools(self) -> None:
        """
        Register MCP tools with the server.

        Tools to register:
        - add_memory: Add natural language or RDF triples
        - query_memory: Execute SPARQL queries
        - search_entity: Full-text search for entities
        - verify_inference: Confirm/reject uncertain inferences (TODO: Phase 3)
        - load_custom_rule: Load user-defined SPARQL rules (TODO: Phase 4)
        - list_rules: List all active rules (TODO: Phase 4)
        - get_graph_stats: Get knowledge graph statistics (TODO: Phase 5)
        """
        logger.info("Registering MCP tools...")

        # Import tools
        from semantic_memory.tools.add_memory import ADD_MEMORY_TOOL, add_memory
        from semantic_memory.tools.query_memory import QUERY_MEMORY_TOOL, query_memory
        from semantic_memory.tools.search_entity import SEARCH_ENTITY_TOOL, search_entity

        # Register add_memory
        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list:
            """Handle tool calls."""
            logger.info(f"Tool called: {name}")

            if name == "add_memory":
                return await add_memory(
                    arguments,
                    self.graph,
                    self.reasoner,
                    self.triple_extractor,
                )
            elif name == "query_memory":
                return await query_memory(arguments, self.graph)
            elif name == "search_entity":
                return await search_entity(arguments, self.graph)
            else:
                raise ValueError(f"Unknown tool: {name}")

        # Register tool schemas
        @self.server.list_tools()
        async def handle_list_tools() -> list:
            """List available tools."""
            return [
                ADD_MEMORY_TOOL,
                QUERY_MEMORY_TOOL,
                SEARCH_ENTITY_TOOL,
            ]

        logger.info("MCP tools registered: add_memory, query_memory, search_entity")

    async def run(self) -> None:
        """Run the MCP server with stdio transport."""
        logger.info("Starting MCP server with stdio transport...")

        # Register tools before starting
        self.register_tools()

        # Run the server with stdio transport
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options(),
            )


async def main() -> None:
    """Main entry point for the server."""
    server = SemanticMemoryServer()

    try:
        await server.startup()
        await server.run()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
        raise
    finally:
        await server.shutdown()


def cli_main() -> None:
    """CLI entry point (for setuptools entry_points)."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
