from dataclasses import dataclass, field
from pathlib import Path
import glob
from typing import List
from rdflib.plugins.sparql.parser import parseQuery
from rdflib import Graph
from semantic_memory.knowledge.graph import ProvenanceGraph
from semantic_memory.knowledge.verification import VerificationRequest
from semantic_memory.vocabulary import SEM, UNCERTAIN_PREDICATE

@dataclass
class InferenceRule:
    id: str
    file_path: Path
    sparql_query: str
    source: str
    description: str | None = None
    is_active: bool = True
    validation_error: str | None = None
    execution_count: int = 0
    triples_generated: int = 0

def load_rules(rules_dirs: List[Path]) -> List[InferenceRule]:
    rules = []
    for rules_dir in rules_dirs:
        for rule_path in glob.glob(str(rules_dir / "*.rq")):
            path = Path(rule_path)
            with open(path, "r") as f:
                content = f.read()
                description = None
                if content.strip().startswith("#"):
                    description = content.strip().split("\n")[0].lstrip("#").strip()
                
                rule = InferenceRule(
                    id=path.stem,
                    file_path=path,
                    sparql_query=content,
                    source="default" if "defaults" in str(path) else "custom",
                    description=description,
                )
                validate_rule(rule)
                rules.append(rule)
    return rules

def validate_rule(rule: InferenceRule):
    try:
        # parsed_query = parseQuery(rule.sparql_query) # Keep for syntax checking
        # Heuristic check for CONSTRUCT query
        if "CONSTRUCT" not in rule.sparql_query.upper():
            rule.is_active = False
            rule.validation_error = "SPARQL query is not a CONSTRUCT query (heuristic check failed)."
    except Exception as e:
        rule.is_active = False
        rule.validation_error = f"SPARQL syntax error: {e}"

class RuleEngine:
    def __init__(self, rules: List[InferenceRule]):
        self.rules = rules

    def execute_rules(self, p_graph: ProvenanceGraph, max_depth: int = 10) -> int:
        """
        Execute SPARQL inference rules on the knowledge graph.
        
        Args:
            p_graph: ProvenanceGraph to run rules on
            max_depth: Maximum iterations to prevent infinite loops
            
        Returns:
            Number of triples inferred
        """
        from semantic_memory.logging_config import get_logger
        logger = get_logger(__name__)
        
        inferred_graph = Graph()
        for iteration in range(max_depth):
            newly_inferred_triples = 0
            for rule in self.rules:
                if not rule.is_active:
                    continue

                rule.execution_count += 1
                
                try:
                    # CONSTRUCT queries return a Graph, not a ResultSet
                    result = p_graph.graph.query(rule.sparql_query)
                    
                    # For CONSTRUCT queries, result is a Graph
                    # We need to iterate over it to get triples
                    if hasattr(result, 'graph'):
                        inferred_triples_result = result.graph
                    else:
                        # If it's already a graph (some versions of rdflib)
                        inferred_triples_result = result
                    
                    # Separate uncertain predicates from actual triples
                    uncertain_preds = {p for s, p, o in inferred_triples_result if p == UNCERTAIN_PREDICATE}
                    actual_triples = [t for t in inferred_triples_result if t[1] != UNCERTAIN_PREDICATE]

                    logger.debug(f"Rule '{rule.id}' found {len(actual_triples)} candidate triples")

                    for triple in actual_triples:
                        if triple not in p_graph.graph and triple not in inferred_graph:
                            
                            # Check for uncertainty
                            is_uncertain = (triple[0], UNCERTAIN_PREDICATE, triple[1]) in inferred_triples_result

                            if is_uncertain:
                                verification_request = VerificationRequest(
                                    triple=triple,
                                    confidence=0.5, # Or extract from rule
                                    source_rule=rule.id,
                                    context={}, # Add context from the WHERE clause
                                )
                                p_graph.add_pending_verification(verification_request)
                                logger.debug(f"Added uncertain triple for verification: {triple}")
                            else:
                                inferred_graph.add(triple)
                                newly_inferred_triples += 1
                                rule.triples_generated += 1
                                logger.debug(f"Inferred new triple: {triple}")
                
                except Exception as e:
                    logger.error(f"Error executing rule '{rule.id}': {e}", exc_info=True)

            logger.info(f"Iteration {iteration + 1}: Inferred {newly_inferred_triples} new triples")
            if newly_inferred_triples == 0:
                break
        
        # Add all inferred triples to the provenance graph
        total_inferred = len(inferred_graph)
        for triple in inferred_graph:
            # Note: rule.id might refer to the last rule, we should track this better
            p_graph.add_triple_with_provenance(triple[0], triple[1], triple[2], source="sparql-rule")
        
        logger.info(f"Rule engine finished: {total_inferred} total triples inferred")
        return total_inferred


