"""
MCP Server entry point for Semantic Memory.

This module initializes and runs the Model Context Protocol server,
exposing semantic memory tools to AI agents.
"""

import asyncio
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent

from semantic_memory.config import config
from semantic_memory.logging_config import get_logger
from semantic_memory.prompts import PROMPTS, get_prompt

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
        from semantic_memory.knowledge.persistence import get_persistence_backend

        self.graph = ProvenanceGraph()
        logger.info("Provenance graph initialized")

        # Load persisted knowledge graph if it exists
        self.persistence = get_persistence_backend()
        try:
            self.persistence.load(self.graph)
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

        logger.debug("DEBUG: About to create OntologyLoader")
        self.ontology_loader = OntologyLoader()
        logger.debug("DEBUG: OntologyLoader created")
        
        try:
            logger.debug("DEBUG: About to load standard ontologies")
            await self.ontology_loader.load_standard_ontologies(self.graph)
            logger.debug("DEBUG: load_standard_ontologies returned")
            logger.info("Standard ontologies loaded")
        except Exception as e:
            logger.error(f"Failed to load ontologies: {e}", exc_info=True)
            logger.warning("Continuing without ontologies...")

        # Initialize reasoner
        logger.debug("DEBUG: About to import Reasoner")
        from semantic_memory.inference.reasoner import Reasoner

        logger.debug("DEBUG: About to create Reasoner instance")
        self.reasoner = Reasoner()
        logger.info("Reasoner initialized")

        # Apply automatic reasoning
        logger.debug("DEBUG: Checking if OWL reasoning is enabled")
        if config.enable_owl_reasoning:
            logger.info("Applying OWL-RL reasoning...")
            try:
                inferred = self.reasoner.apply_closure(self.graph)
                logger.info(f"Inferred {inferred} additional triples via OWL-RL")
            except Exception as e:
                logger.error(f"Error during OWL-RL reasoning: {e}")
        else:
            logger.info("OWL-RL reasoning disabled (SEMMEM_ENABLE_OWL_REASONING=false)")

        # Load and execute inference rules
        logger.debug("DEBUG: About to import RuleEngine")
        from semantic_memory.inference.rule_engine import RuleEngine, load_rules
        logger.debug("DEBUG: About to load rules")
        rules = load_rules([config.default_rules_dir, config.user_rules_dir])
        logger.debug(f"DEBUG: Loaded {len(rules)} rules")
        self.rule_engine = RuleEngine(rules)
        # Note: Don't execute rules on the full ontology graph at startup!
        # Rules will be executed when user adds new triples via add_memory
        logger.info(f"Loaded {len(rules)} inference rules (will execute on user data).")

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
        if self.graph and self.persistence:
            try:
                self.persistence.save(self.graph)
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
        - verify_inference: Confirm/reject uncertain inferences
        - load_custom_rule: Load user-defined SPARQL rules
        - list_rules: List all active rules
        - get_graph_stats: Get knowledge graph statistics
        """
        logger.info("Registering MCP tools...")

        # Import tools
        from semantic_memory.tools.add_memory import ADD_MEMORY_TOOL, add_memory
        from semantic_memory.tools.query_memory import QUERY_MEMORY_TOOL, query_memory
        from semantic_memory.tools.search_entity import SEARCH_ENTITY_TOOL, search_entity
        from semantic_memory.tools.list_rules import LIST_RULES_TOOL, list_rules
        from semantic_memory.tools.load_custom_rule import LOAD_CUSTOM_RULE_TOOL, load_custom_rule
        from semantic_memory.tools.verify_inference import VERIFY_INFERENCE_TOOL, verify_inference
        from semantic_memory.tools.get_pending_verifications import GET_PENDING_VERIFICATIONS_TOOL, get_pending_verifications
        from semantic_memory.tools.get_graph_stats import GET_GRAPH_STATS_TOOL, get_graph_stats

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
                    self.rule_engine,
                )
            elif name == "query_memory":
                return await query_memory(arguments, self.graph)
            elif name == "search_entity":
                return await search_entity(arguments, self.graph)
            elif name == "list_rules":
                return await list_rules(arguments, self.rule_engine)
            elif name == "load_custom_rule":
                return await load_custom_rule(arguments, self.rule_engine, self.graph)
            elif name == "verify_inference":
                return await verify_inference(arguments, self.graph)
            elif name == "get_pending_verifications":
                return await get_pending_verifications(arguments, self.graph)
            elif name == "get_graph_stats":
                return await get_graph_stats(arguments, self.graph, self.rule_engine)
            else:
                raise ValueError(f"Unknown tool: {name}")

        @self.server.list_tools()
        async def handle_list_tools() -> list:
            """List available tools."""
            return [
                ADD_MEMORY_TOOL,
                QUERY_MEMORY_TOOL,
                SEARCH_ENTITY_TOOL,
                LIST_RULES_TOOL,
                LOAD_CUSTOM_RULE_TOOL,
                VERIFY_INFERENCE_TOOL,
                GET_PENDING_VERIFICATIONS_TOOL,
                GET_GRAPH_STATS_TOOL,
            ]

        logger.info("MCP tools registered.")

        # Register prompts
        @self.server.list_prompts()
        async def handle_list_prompts() -> list:
            """List available prompts."""
            return PROMPTS

        @self.server.get_prompt()
        async def handle_get_prompt(name: str, arguments: dict[str, str] | None) -> Any:
            """Get a specific prompt."""
            return await get_prompt(name, arguments)

        logger.info("MCP prompts registered.")

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
    import signal
    
    server = SemanticMemoryServer()
    shutdown_event = asyncio.Event()
    
    def signal_handler(signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        shutdown_event.set()
    
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await server.startup()
        
        # Run server in a task so we can cancel it
        run_task = asyncio.create_task(server.run())
        
        # Wait for either server completion or shutdown signal
        done, pending = await asyncio.wait(
            [run_task, asyncio.create_task(shutdown_event.wait())],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Cancel any remaining tasks
        for task in pending:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
                
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
    finally:
        # Always shutdown cleanly
        try:
            await server.shutdown()
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
        logger.info("Server shutdown complete")


def cli_main() -> None:
    """CLI entry point (for setuptools entry_points)."""
    asyncio.run(main())


if __name__ == "__main__":
    cli_main()
