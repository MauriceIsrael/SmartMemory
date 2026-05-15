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

from smart_memory.config import config
from smart_memory.logging_config import get_logger
from smart_memory.prompts import PROMPTS, get_prompt

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
        from smart_memory import __version__
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
        from smart_memory.knowledge import ProvenanceGraph
        from smart_memory.knowledge.persistence import get_persistence_backend

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
        from smart_memory.nlp import TripleExtractor

        self.triple_extractor = TripleExtractor()
        logger.info("Triple extractor initialized")

        # Load standard ontologies (ONLY if enabled - adds ~17k triples and 5-10s startup)
        # Set load_ontologies=True in config to enable (required for core_* rules in _optional/)
        if config.load_ontologies:
            from smart_memory.inference.ontology_loader import OntologyLoader

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
        else:
            logger.info("Ontology loading disabled by config (load_ontologies=False).")
            logger.info("To enable: set load_ontologies=True in config and copy core_*.rq rules from _optional/ to defaults/")
            self.ontology_loader = None

        # Initialize reasoner
        logger.debug("DEBUG: About to import Reasoner")
        from smart_memory.inference.reasoner import Reasoner

        logger.debug("DEBUG: About to create Reasoner instance")
        self.reasoner = Reasoner()
        logger.info("Reasoner initialized")

        # Apply automatic reasoning
        # Apply OWL-RL reasoning (if enabled)
        # MOVED TO BACKGROUND: Don't block startup with heavy reasoning!
        if config.enable_owl_reasoning:
            logger.info("Triggering background OWL-RL reasoning...")
            # We don't call apply_closure directly here.
            # Instead, we rely on the InferenceManager to pick it up.
            # We'll trigger it after the manager is started.
        else:
            logger.info("OWL-RL reasoning disabled by config.")

        # Load and execute inference rules
        logger.debug("DEBUG: About to import RuleEngine")
        from smart_memory.inference.rule_engine import RuleEngine, load_rules
        logger.debug("DEBUG: About to load rules")
        rules = load_rules([config.default_rules_dir, config.user_rules_dir])
        logger.debug(f"DEBUG: Loaded {len(rules)} rules")
        self.rule_engine = RuleEngine(rules)
        logger.info(f"Loaded {len(rules)} inference rules.")

        # Initialize Inference Manager for async background reasoning
        from smart_memory.inference.inference_manager import InferenceManager
        self.inference_manager = InferenceManager(debounce_seconds=config.debounce_seconds)

        
        # Register reasoning callbacks
        # 1. OWL-RL (if enabled)
        if config.enable_owl_reasoning:
            async def run_owl_reasoning():
                logger.info("Running background OWL-RL reasoning...")
                # Run CPU-bound reasoning in a separate thread to avoid blocking the event loop
                loop = asyncio.get_running_loop()
                count = await loop.run_in_executor(None, self.reasoner.apply_closure, self.graph)
                logger.info(f"OWL-RL inferred {count} new triples")
            self.inference_manager.register_callback(run_owl_reasoning)
            
        # 2. SPARQL Rules
        async def run_sparql_rules():
            logger.info("Running background SPARQL rules...")
            # Run CPU-bound rules in a separate thread
            loop = asyncio.get_running_loop()
            count = await loop.run_in_executor(None, self.rule_engine.execute_rules, self.graph)
            logger.info(f"SPARQL rules inferred {count} new triples")
        self.inference_manager.register_callback(run_sparql_rules)
        
        # Start background worker
        await self.inference_manager.start()
        
        # Trigger initial inference pass to catch up on any missing deductions
        if config.enable_owl_reasoning:
            self.inference_manager.trigger_inference()

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

        # Stop inference manager
        if hasattr(self, 'inference_manager') and self.inference_manager:
            await self.inference_manager.stop()

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

        Uses a registry pattern: each tool maps to its handler with pre-injected
        dependencies via functools.partial. Adding a new tool requires only 2 lines
        in the registry — no modification to the dispatcher.
        """
        logger.info("Registering MCP tools...")
        import functools

        # Import tool definitions and handlers
        from smart_memory.tools.add_memory import ADD_MEMORY_TOOL, add_memory
        from smart_memory.tools.query_memory import QUERY_MEMORY_TOOL, query_memory
        from smart_memory.tools.search_entity import SEARCH_ENTITY_TOOL, search_entity
        from smart_memory.tools.list_rules import LIST_RULES_TOOL, list_rules
        from smart_memory.tools.load_custom_rule import LOAD_CUSTOM_RULE_TOOL, load_custom_rule
        from smart_memory.tools.verify_inference import VERIFY_INFERENCE_TOOL, verify_inference
        from smart_memory.tools.suggest_rule import SUGGEST_RULE_TOOL, suggest_rule
        from smart_memory.tools.get_pending_verifications import GET_PENDING_VERIFICATIONS_TOOL, get_pending_verifications
        from smart_memory.tools.pending_rules import (
            GET_PENDING_RULES_TOOL, APPROVE_RULE_TOOL, REJECT_RULE_TOOL,
            get_pending_rules, approve_rule, reject_rule
        )
        from smart_memory.tools.get_graph_stats import GET_GRAPH_STATS_TOOL, get_graph_stats
        from smart_memory.tools.load_document import LOAD_DOCUMENT_TOOL, load_document
        from smart_memory.tools.forget_memory import FORGET_MEMORY_TOOL, forget_memory

        # Registry: tool_name -> (definition, async_handler_with_injected_deps)
        # Each handler is a coroutine function accepting (arguments: dict) as sole arg.
        registry = {
            "add_memory": (ADD_MEMORY_TOOL, functools.partial(
                add_memory,
                graph=self.graph,
                reasoner=self.reasoner,
                triple_extractor=self.triple_extractor,
                rule_engine=self.rule_engine,
                inference_manager=self.inference_manager,
            )),
            "query_memory": (QUERY_MEMORY_TOOL, functools.partial(query_memory, graph=self.graph)),
            "search_entity": (SEARCH_ENTITY_TOOL, functools.partial(search_entity, graph=self.graph)),
            "list_rules": (LIST_RULES_TOOL, functools.partial(list_rules, rule_engine=self.rule_engine)),
            "load_custom_rule": (LOAD_CUSTOM_RULE_TOOL, functools.partial(load_custom_rule, rule_engine=self.rule_engine, graph=self.graph)),
            "verify_inference": (VERIFY_INFERENCE_TOOL, functools.partial(verify_inference, graph=self.graph)),
            "suggest_rule": (SUGGEST_RULE_TOOL, functools.partial(suggest_rule, graph=self.graph, rule_engine=self.rule_engine)),
            "get_pending_verifications": (GET_PENDING_VERIFICATIONS_TOOL, functools.partial(get_pending_verifications, graph=self.graph)),
            "get_pending_rules": (GET_PENDING_RULES_TOOL, get_pending_rules),
            "approve_rule": (APPROVE_RULE_TOOL, functools.partial(approve_rule, rule_engine=self.rule_engine, graph=self.graph)),
            "reject_rule": (REJECT_RULE_TOOL, reject_rule),
            "get_graph_stats": (GET_GRAPH_STATS_TOOL, functools.partial(get_graph_stats, graph=self.graph, rule_engine=self.rule_engine)),
            "load_document": (LOAD_DOCUMENT_TOOL, functools.partial(load_document, graph=self.graph, rule_engine=self.rule_engine)),
            "forget_memory": (FORGET_MEMORY_TOOL, functools.partial(forget_memory, graph=self.graph, triple_extractor=self.triple_extractor)),
        }

        @self.server.call_tool()
        async def handle_call_tool(name: str, arguments: dict) -> list:
            """Dispatch tool calls via registry."""
            logger.info(f"Tool called: {name}")
            entry = registry.get(name)
            if entry is None:
                raise ValueError(f"Unknown tool: {name}")
            _, handler = entry
            return await handler(arguments)

        @self.server.list_tools()
        async def handle_list_tools() -> list:
            """List available tools from the registry."""
            return [definition for definition, _ in registry.values()]

        self._handle_call_tool = handle_call_tool
        logger.info(f"MCP tools registered ({len(registry)} tools).")



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
