import sys
import os
import logging
from pathlib import Path

# Add the project root to sys.path to allow imports from 'src'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp.server.fastmcp import FastMCP
from rdflib import Graph
from src.models.knowledge_graph import KnowledgeGraph
from src.services.persistence_service import PersistenceService
from src.services.inference_engine import InferenceEngine
from src.services.verification_service import VerificationService
from src.models.triple import Triple
from src.models.inference_rule import InferenceRule
from src.ontology import OntologyLoader

# Configure logging
# Write to stderr to avoid interfering with MCP protocol on stdout
# Optionally write to file if LOG_FILE env var is set
log_handlers = [logging.StreamHandler(sys.stderr)]

log_file = os.environ.get('LOG_FILE')
if log_file:
    # Ensure log directory exists
    log_path = Path(log_file)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_handlers.append(logging.FileHandler(log_file))

logging.basicConfig(
    level=logging.INFO,
    handlers=log_handlers,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

if log_file:
    logger.info(f"📝 Logging to file: {log_file}")

# Initialize services
# In a real app, we might want to wrap this in a class or context manager
try:
    logger.info("🚀 Starting Semantic Memory MCP Server...")
    
    # Step 1: Load ontologies
    logger.info("📚 Loading standard ontologies (FOAF, SKOS, Schema.org)...")
    ontology_graph = Graph()
    ontology_loader = OntologyLoader(
        graph=ontology_graph,
        cache_dir=Path("./cache"),
        offline_mode=False
    )
    ontology_results = ontology_loader.load_all()
    
    loaded_count = sum(1 for success in ontology_results.values() if success)
    logger.info(f"✓ Loaded {loaded_count}/{len(ontology_results)} ontologies")
    
    # Step 2: Create inference rules based on ontologies
    logger.info("🧠 Creating inference rules...")
    
    # Rule 1: Symmetric property inference (from FOAF :knows)
    rule_symmetric_knows = InferenceRule(
        name="symmetric_knows",
        conditions=[
            Triple(subject="?x", predicate="http://xmlns.com/foaf/0.1/knows", object="?y")
        ],
        conclusion=Triple(subject="?y", predicate="http://xmlns.com/foaf/0.1/knows", object="?x")
    )
    
    # Rule 2: If someone likes programming, they might be a developer
    rule_developer = InferenceRule(
        name="programming_enthusiast",
        conditions=[
            Triple(subject="?x", predicate=":likes", object=":Programming")
        ],
        conclusion=Triple(subject="?x", predicate=":isA", object=":Developer")
    )
    
    # Rule 3: If someone works at a company, they are an employee
    rule_employee = InferenceRule(
        name="company_employee",
        conditions=[
            Triple(subject="?x", predicate=":worksAt", object="?company")
        ],
        conclusion=Triple(subject="?x", predicate=":isA", object=":Employee")
    )
    
    inference_rules = [rule_symmetric_knows, rule_developer, rule_employee]
    logger.info(f"✓ Created {len(inference_rules)} inference rule(s)")
    
    # Step 3: Initialize services
    persistence_service = PersistenceService('knowledge_graph.ttl')
    verification_service = VerificationService()
    inference_engine = InferenceEngine(
        rules=inference_rules, 
        verification_service=verification_service,
        certainty_threshold=0.8  # Lower threshold to trigger more verifications
    )
    
    knowledge_graph = persistence_service.load()
    knowledge_graph.inference_engine = inference_engine
    
    # Merge ontologies into knowledge graph (optional - for querying)
    # knowledge_graph.explicit_graph += ontology_graph
    
    logger.info("✅ Services initialized successfully")
    logger.info(f"   - Knowledge graph: {len(knowledge_graph.explicit_graph)} fact(s)")
    logger.info(f"   - Ontologies: {len(ontology_graph)} triple(s)")
    logger.info(f"   - Inference rules: {len(inference_rules)}")
    
except Exception as e:
    logger.critical(f"❌ Failed to initialize services: {e}", exc_info=True)
    sys.exit(1)

# Create MCP server
mcp = FastMCP("Semantic Memory")

@mcp.tool()
def add_fact(subject: str, predicate: str, object: str) -> str:
    """Add a fact to the knowledge graph.
    
    Args:
        subject: The subject of the fact (e.g. ":User")
        predicate: The predicate of the fact (e.g. ":likes")
        object: The object of the fact (e.g. ":Python")
    """
    try:
        logging.info(f"Adding fact: {subject} {predicate} {object}")
        triple = Triple(subject=subject, predicate=predicate, object=object)
        knowledge_graph.add_explicit(triple)
        persistence_service.save(knowledge_graph)
        return f"Fact added: {triple}"
    except Exception as e:
        logging.error(f"Error adding fact: {e}")
        return f"Error adding fact: {e}"

@mcp.tool()
def get_pending_verifications() -> str:
    """Get a list of pending verifications."""
    try:
        verifications = verification_service.get_pending()
        return str([v.model_dump() for v in verifications])
    except Exception as e:
        logging.error(f"Error getting verifications: {e}")
        return f"Error getting verifications: {e}"

@mcp.prompt()
def semantic_memory_guide() -> str:
    """Returns a guide on how to use the Semantic Memory MCP server."""
    return """
You are interacting with a Semantic Memory system based on a Knowledge Graph.
Your goal is to store important facts about the user and the world, and to verify inferred information.

### Tools Usage:

1.  **`add_fact(subject, predicate, object)`**:
    *   Use this to store a NEW fact.
    *   Format the arguments as RDF-like strings, preferably with a colon prefix for entities (e.g., `:User`, `:Python`) and predicates (e.g., `:likes`, `:isA`).
    *   Example: User says "I like Python" -> `add_fact(":User", ":likes", ":Python")`

2.  **`get_pending_verifications()`**:
    *   Use this to check if the system has made any inferences that need user confirmation.
    *   If this returns a list of requests, present them to the user naturally.
    *   Example: "The system inferred that you might be a Developer. Is this correct?"

### Workflow:

*   **Listen**: When the user states a fact, add it immediately.
*   **Check**: Periodically (or after adding facts), check for pending verifications.
*   **Verify**: If there are pending verifications, ask the user. (Note: Currently there is no tool to 'confirm' the verification programmatically, just acknowledge it to the user).

Do NOT call `get_pending_verifications` immediately after `add_fact` unless you have reason to believe an inference rule was triggered.
"""

if __name__ == "__main__":
    mcp.run()