"""
Service layer for accessing the SmartMemory knowledge graph and inference engine.

This service provides methods to query the knowledge graph, access inference rules,
and retrieve system statistics for the supervision dashboard.
"""

from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from rdflib import URIRef, Literal, BNode
from rdflib.namespace import RDF

from smart_memory.knowledge.graph import ProvenanceGraph
from smart_memory.inference.rule_engine import RuleEngine, InferenceRule, load_rules
from smart_memory.vocabulary import SEM
from smart_memory.config import config
import json
import logging

logger = logging.getLogger(__name__)


class MemoryService:
    """Service for accessing SmartMemory data and operations."""
    
    def __init__(
        self,
        graph_file: Path | str = "knowledge_graph.ttl",
        rules_dirs: List[Path] | None = None
    ):
        """
        Initialize the MemoryService.
        
        Args:
            graph_file: Path to the knowledge graph file
            rules_dirs: List of directories containing inference rules
        """
        self.graph_file = Path(graph_file)
        
        # Initialize provenance graph
        self.p_graph = ProvenanceGraph()
        
        # Load knowledge graph if it exists
        if self.graph_file.exists():
            self.p_graph.graph.parse(self.graph_file, format="turtle")
        
        # Load inference rules
        if rules_dirs is None:
            # Default rules directories
            rules_dirs = [
                config.default_rules_dir,
                config.user_rules_dir,
            ]
        
        self.rules = load_rules(rules_dirs)
        self.rule_engine = RuleEngine(self.rules)
    
    def get_system_stats(self) -> Dict[str, int]:
        """
        Get system statistics.
        
        Returns:
            Dictionary with stats: total_triplets, inferred_triplet_count,
            asserted_triplet_count, active_rule_count, inactive_rule_count
        """
        # Count total triplets (excluding provenance metadata)
        total_triplets = len([
            (s, p, o) for s, p, o in self.p_graph.graph
            if p not in {RDF.type, RDF.subject, RDF.predicate, RDF.object, 
                        SEM.source, SEM.timestamp, SEM.confidence, SEM.sourceRule, SEM.uncertain}
        ])
        
        # Count inferred vs asserted triplets
        inferred_count = 0
        asserted_count = 0
        
        for s, p, o in self.p_graph.graph:
            if p == SEM.source:
                source_value = str(o)
                if source_value in {"sparql-rule", "owlrl"}:
                    inferred_count += 1
                elif source_value in {"user", "user-verified"}:
                    asserted_count += 1
        
        # Count active and inactive rules
        active_rules = sum(1 for rule in self.rules if rule.is_active)
        inactive_rules = len(self.rules) - active_rules
        
        return {
            "total_triplets": total_triplets,
            "inferred_triplet_count": inferred_count,
            "asserted_triplet_count": asserted_count,
            "active_rule_count": active_rules,
            "inactive_rule_count": inactive_rules,
        }
    
    def get_facts(
        self,
        page: int = 1,
        page_size: int = 50,
        search: Optional[str] = None,
        origin: Optional[str] = None
    ) -> Tuple[List[Dict[str, Any]], int]:
        """
        Get paginated list of facts from the knowledge graph.
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of items per page
            search: Optional search term to filter facts
            origin: Optional filter for fact origin ('explicit' for user-stated facts, 'inferred' for derived facts)
        
        Returns:
            Tuple of (list of facts, total count)
        """
        # Collect all non-provenance triples
        facts = []
        provenance_predicates = {
            RDF.type, RDF.subject, RDF.predicate, RDF.object,
            SEM.source, SEM.timestamp, SEM.confidence, SEM.sourceRule, SEM.uncertain
        }
        
        # Build a map of triples to their provenance
        triple_provenance = {}
        for s, p, o in self.p_graph.graph:
            if p == RDF.subject:
                # This is a reification node
                stmt_node = s
                # Find the triple components
                triple_s = next((obj for subj, pred, obj in self.p_graph.graph 
                               if pred == RDF.subject and subj == stmt_node), None)
                triple_p = next((obj for subj, pred, obj in self.p_graph.graph 
                               if pred == RDF.predicate and subj == stmt_node), None)
                triple_o = next((obj for subj, pred, obj in self.p_graph.graph 
                               if pred == RDF.object and subj == stmt_node), None)
                
                if triple_s and triple_p and triple_o:
                    source = next((str(obj) for subj, pred, obj in self.p_graph.graph 
                                 if pred == SEM.source and subj == stmt_node), "unknown")
                    triple_provenance[(triple_s, triple_p, triple_o)] = source
        
        # Collect facts with timestamps
        for s, p, o in self.p_graph.graph:
            if p in provenance_predicates:
                continue
            
            subject_str = self._format_term(s)
            predicate_str = self._format_term(p)
            object_str = self._format_term(o)
            
            # Apply search filter if provided
            if search:
                search_lower = search.lower()
                if not any(search_lower in term.lower() 
                          for term in [subject_str, predicate_str, object_str]):
                    continue
            
            # Get provenance and timestamp for this triple
            provenance = triple_provenance.get((s, p, o), "user")
            
            # Find timestamp from provenance metadata
            timestamp_str = "1970-01-01T00:00:00+00:00"  # Default old timestamp
            for stmt_s, stmt_p, stmt_o in self.p_graph.graph:
                if stmt_p == RDF.subject and stmt_o == s:
                    # Found the provenance node
                    for _, ts_p, ts_o in self.p_graph.graph:
                        if ts_p == SEM.timestamp:
                            timestamp_str = str(ts_o)
                            break
                    break
            
            # Apply origin filter if provided
            if origin:
                if origin == "explicit":
                    # Filter for user-stated facts
                    if provenance not in {"user", "user-verified"}:
                        continue
                elif origin == "inferred":
                    # Filter for inferred facts
                    if provenance not in {"sparql-rule", "owlrl"}:
                        continue
            
            facts.append({
                "Subject": subject_str,
                "Predicate": predicate_str,
                "Object": object_str,
                "Provenance": provenance,
                "_timestamp": timestamp_str,  # Internal for sorting
            })
        
        # Sort by timestamp descending (newest first)
        facts.sort(key=lambda f: f.get("_timestamp", ""), reverse=True)
        
        # Remove internal timestamp field before returning
        for fact in facts:
            fact.pop("_timestamp", None)
        
        total_count = len(facts)
        
        # Apply pagination
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        paginated_facts = facts[start_idx:end_idx]
        
        return paginated_facts, total_count
    
    def get_rules(self, source: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all inference rules with their metadata.
        
        Args:
            source: Optional filter for rule source ('default' for built-in, 'custom' for user-approved)
        
        Returns:
            List of rule dictionaries, optionally filtered
        """
        rules_list = []
        for rule in self.rules:
            # Determine rule source based on where it was loaded from
            # Rules loaded from src/rules/defaults/ are 'default'
            # Rules loaded from user_rules/ are 'custom' (dynamically approved by users)
            rule_source = getattr(rule, 'source', 'default')  # Use metadata if available
            
            # Fallback: infer from common custom rule patterns
            # If the rule has a source attribute, use it. Otherwise default to 'default'
            if rule_source == 'default':
                # Check if this is a commonly known custom rule pattern
                custom_patterns = [
                    'commute_by_car', 'driving_license_implies', 'age_18_implies',
                    'friendship_rule', 'acquaintance_rule', 'security_tls',
                    'colleagues_know', 'employed_from', 'friends_know',
                    'shared_company', 'spouses_know', 'mentorship', 
                    'potential_collaboration', 'test_rule', 'test_uncertain',
                    'uncertain_rule', 'driving_requires'
                ]
                if any(pattern in rule.id for pattern in custom_patterns):
                    rule_source = 'custom'
            
            # Apply source filter if provided
            if source:
                if source == 'dynamic' and rule_source == 'default':
                    continue
                elif source == 'custom' and rule_source == 'default':
                    continue
                elif source == 'default' and rule_source in ['custom', 'dynamic']:
                    continue
            
            rules_list.append({
                "id": rule.id,
                "description": rule.description or f"Rule: {rule.id}",
                "sparql_query": rule.sparql_query,
                "is_active": rule.is_active,
                "execution_count": rule.execution_count,
                "triples_generated": rule.triples_generated,
                "validation_error": rule.validation_error,
                "source": rule_source,  # Include source in response
            })
        
        # Sort rules by activity (execution_count + triples_generated) descending
        # This puts most recently active/productive rules first
        rules_list.sort(key=lambda r: (r["execution_count"], r["triples_generated"]), reverse=True)
        
        return rules_list
    
    def toggle_rule(self, rule_id: str) -> Optional[Dict[str, Any]]:
        """
        Toggle a rule's active state.
        
        Args:
            rule_id: ID of the rule to toggle
        
        Returns:
            Updated rule dictionary, or None if rule not found
        """
        for rule in self.rules:
            if rule.id == rule_id:
                rule.is_active = not rule.is_active
                return {
                    "id": rule.id,
                    "description": rule.description or f"Rule: {rule.id}",
                    "sparql_query": rule.sparql_query,
                    "is_active": rule.is_active,
                    "execution_count": rule.execution_count,
                    "triples_generated": rule.triples_generated,
                    "validation_error": rule.validation_error,
                }
        return None
    
    def run_inference(self) -> Dict[str, Any]:
        """
        Manually trigger a full inference run.
        
        Returns:
            Dictionary with inference run results
        """
        try:
            # Check enabled engines
            from services.engine_service import get_engine_service
            engine_service = get_engine_service()
            engines = engine_service.get_all_engines()
            
            triples_inferred = 0
            messages = []
            
            # 1. Run SPARQL Rules if enabled
            if engines.sparql_rules.enabled:
                count = self.rule_engine.execute_rules(self.p_graph, max_depth=10)
                triples_inferred += count
                messages.append(f"SPARQL: {count}")
            else:
                messages.append("SPARQL: Disabled")

            # 2. Run OWL Reasoning if enabled
            # (Note: OWL reasoning is often done on load, but we could trigger a re-run here if we had a dedicated OWL engine class)
            if engines.owl_reasoning.enabled:
                # Placeholder for actual OWL reasoning trigger
                # For now, we rely on the fact that if it's enabled in config, it runs.
                # But here we want manual trigger.
                # If we had an OWL reasoner wrapper, we'd call it here.
                # For now, just log that we skipped it or it's not fully implemented for manual trigger.
                messages.append("OWL: Not implemented for manual trigger")
            else:
                messages.append("OWL: Disabled")
            
            # Save the updated graph
            self.p_graph.graph.serialize(destination=str(self.graph_file), format="turtle")
            
            status = "success" if triples_inferred > 0 else "warning"
            message = f"Inference run completed. Inferred: {triples_inferred}. Details: {', '.join(messages)}"
            
            return {
                "status": status,
                "triples_inferred": triples_inferred,
                "message": message
            }
        except Exception as e:
            logger.error(f"Inference run failed: {e}", exc_info=True)
            return {
                "status": "error",
                "message": f"Inference run failed: {str(e)}"
            }
    
    @staticmethod
    def _format_term(term) -> str:
        """Format an RDF term for display."""
        if isinstance(term, URIRef):
            # Try to use the local name or full URI
            uri_str = str(term)
            if "#" in uri_str:
                return uri_str.split("#")[-1]
            elif "/" in uri_str:
                parts = uri_str.split("/")
                return parts[-1] if parts[-1] else uri_str
            return uri_str
        elif isinstance(term, Literal):
            return str(term)
        elif isinstance(term, BNode):
            return f"_:{term}"
        else:
            return str(term)
    
    def reload_graph(self) -> Dict[str, Any]:
        """
        Reload the knowledge graph from disk.
        
        This is useful when the graph has been modified by the MCP server
        and the supervision backend needs to see the latest changes.
        
        Returns:
            Dictionary with reload status and triple count
        """
        try:
            # Clear existing graph
            self.p_graph = ProvenanceGraph()
            
            # Reload from file if it exists
            if self.graph_file.exists():
                self.p_graph.graph.parse(self.graph_file, format="turtle")
                triple_count = len(list(self.p_graph.graph))
                
                return {
                    "status": "success",
                    "message": f"Graph reloaded successfully. {triple_count} triples loaded.",
                    "triple_count": triple_count
                }
            else:
                return {
                    "status": "warning",
                    "message": "Graph file does not exist yet.",
                    "triple_count": 0
                }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Failed to reload graph: {str(e)}",
                "triple_count": 0
            }

    # Pending Rules Management
    
    def get_pending_rules(self, doc_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get list of pending rules from the shared JSON file."""
        pending_file = config.project_root / "pending_rules.json"
        if not pending_file.exists():
            return []
            
        try:
            with open(pending_file, "r") as f:
                rules_dict = json.load(f)
                
            # Convert dict to list
            rules_list = []
            for k, v in rules_dict.items():
                # Filter by doc_id if provided
                if doc_id:
                     source_uri = v.get("source_doc_uri", "")
                     # Allow filtering by exact match or substring (e.g. if doc_id is UUID)
                     if doc_id not in source_uri:
                         continue
                
                rules_list.append({"id": k, **v})
                
            return rules_list
        except Exception as e:
            logger.error(f"Error reading pending rules: {e}")
            return []

    def approve_pending_rule(self, rule_id: str) -> bool:
        """Approve a pending rule via the backend."""
        # We need to reuse the logic from the tool
        # For simplicity, we'll manually move it here
        pending_file = config.project_root / "pending_rules.json"
        
        try:
            with open(pending_file, "r") as f:
                rules_dict = json.load(f)
                
            if rule_id not in rules_dict:
                return False
                
            rule_data = rules_dict[rule_id]
            
            # Load into engine
            from smart_memory.tools.load_custom_rule import load_custom_rule
            import asyncio
            
            # We need to run the async function synchronously here or change architecture
            # Since FastAPI handles async, we should actually propagate async up.
            # But this service method is synchronous currently? 
            # Looking at codebase, methods are synchronous.
            # We can use new event loop or standard loop if available.
            # Ideally, `load_custom_rule` should be split into sync/async parts.
            
            # Hack: execute "load_custom_rule" logic manually for now to avoid async complications in sync method
            # OR: make this method async. But `MemoryService` is used by sync endpoints?
            # Creating a new loop is risky inside uvicorn.
            
            # Let's rely on standard rule loading logic:
            # 1. Write to user_rules file
            # 2. Reload rules
            
            # Write sparql file
            rule_filename = f"{rule_id}.sparql"
            rules_dir = config.user_rules_dir
            rules_dir.mkdir(exist_ok=True)
            
            try:
                with open(rules_dir / rule_filename, 'w') as f:
                    # Construct SPARQL content
                    content = rule_data["sparql_pattern"]
                    # If description not in comment, maybe add it
                    f.write(f"# Description: {rule_data['description']}\n")
                    # Add source doc metadata
                    if 'source_doc_uri' in rule_data:
                        f.write(f"# Source Doc: {rule_data['source_doc_uri']}\n")
                    f.write(content)
            except Exception as e:
                logger.error(f"Failed to write rule file: {e}")
                return False

            # Reload rules in the engine
            self.rules = load_rules([config.default_rules_dir, config.user_rules_dir])
            self.rule_engine = RuleEngine(self.rules)
            
            # Remove from pending
            del rules_dict[rule_id]
            with open(pending_file, "w") as f:
                json.dump(rules_dict, f, indent=2)
                
            return True

        except Exception as e:
            logger.error(f"Error approving pending rule: {e}")
            return False

    def reject_pending_rule(self, rule_id: str) -> bool:
        """Reject a pending rule."""
        pending_file = config.project_root / "pending_rules.json"
        try:
            if not pending_file.exists():
                return False
                
            with open(pending_file, "r") as f:
                rules_dict = json.load(f)
                
            if rule_id in rules_dict:
                # Archive the rule before deleting
                try:
                    rule_data = rules_dict[rule_id]
                    config.rejected_rules_dir.mkdir(parents=True, exist_ok=True)
                    
                    archive_path = config.rejected_rules_dir / f"{rule_id}.sparql"
                    with open(archive_path, "w") as af:
                        af.write(f"# REJECTED RULE\n")
                        af.write(f"# ID: {rule_id}\n")
                        af.write(f"# Description: {rule_data.get('description', 'No description')}\n")
                        af.write(f"# Source Doc: {rule_data.get('source_doc_uri', 'Unknown')}\n\n")
                        af.write(rule_data.get('sparql_pattern', ''))
                        
                    logger.info(f"Archived rejected rule to {archive_path}")
                except Exception as archive_error:
                    logger.error(f"Failed to archive rejected rule: {archive_error}")
                    # Proceed with deletion anyway? Yes, user wanted rejection.

                del rules_dict[rule_id]
                with open(pending_file, "w") as f:
                    json.dump(rules_dict, f, indent=2)
                return True
            return False
        except Exception as e:
            logger.error(f"Error rejecting rule: {e}")
            return False

    def delete_document(self, doc_uri: str) -> bool:
        """Delete all triples associated with a document."""
        # Assuming documents are stored in named graphs or linked via provenance?
        # SmartMemory usually stores triples in default graph but with SEM.source?
        # Or uses Named Graphs?
        # Looking at `load_document.py`: 
        # `graph.add(triple, provenance=doc_uri)`
        # `ProvenanceGraph` stores it as a Quad or reified statement with `sem:source <doc_uri>`.
        
        # We need to find all statements where sem:source is the doc URI.
        # doc_uri usually looks like http://semanticmemory.org/document#doc_UUID
        
        try:
            # Strategies for ProvenanceGraph deletion:
            # 1. Find all reified statements where :source associated is doc_uri
            # 2. Delete them and their associated triples
            
            # Since ProvenanceGraph abstraction is a bit opaque here, let's look at implementation?
            # It uses `graph.remove(...)`.
            
            # Find associated statements
            stmts_to_remove = []
            
            # Iterate all triples to find provenance metadata
            for s, p, o in self.p_graph.graph:
                if p == SEM.source and str(o) == doc_uri:
                    # 's' is the reified statement node (or the triple ID)
                    stmts_to_remove.append(s)
            
            count = 0
            for stmt_node in stmts_to_remove:
                # Remove metadata triples for this statement
                self.p_graph.graph.remove((stmt_node, None, None))
                
                # Check if this node was a reification of a triple?
                # In standard reification: [ rdf:subject S; rdf:predicate P; rdf:object O ]
                # We need to find S, P, O and remove the actual asserted triple?
                # SmartMemory `ProvenanceGraph` might keep the asserted triple AND the reification.
                # If we remove the provenance, do we remove the triple? YES, if the user wants to "delete the document".
                
                # However, if other sources also assert the same triple, we should technically keep it?
                # For now, let's assume strict deletion: if this doc asserted it, we remove the assertion instance.
                # The actual (S,P,O) triple in the default graph might be distinct.
                
                # Let's perform a generic cleanup:
                # If we used `ProvenanceGraph.add`, it adds:
                # 1. (s, p, o) to graph
                # 2. (stmt_id, rdf:type, rdf:Statement)
                # 3. (stmt_id, rdf:subject, s) ...
                # 4. (stmt_id, sem:source, source)
                
                # We found stmt_id via (4).
                
                # We should find s, p, o from (3)
                subjects = list(self.p_graph.graph.objects(stmt_node, RDF.subject))
                predicates = list(self.p_graph.graph.objects(stmt_node, RDF.predicate))
                objects = list(self.p_graph.graph.objects(stmt_node, RDF.object))
                
                if subjects and predicates and objects:
                    s, p, o = subjects[0], predicates[0], objects[0]
                    # Remove the main triple
                    self.p_graph.graph.remove((s, p, o))
                    count += 1
            
            logger.info(f"Deleted {count} triples for document {doc_uri}")
            
            # Save changes
            self.p_graph.graph.serialize(destination=str(self.graph_file), format="turtle")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting document {doc_uri}: {e}")
            return False


# Global instance for the supervision backend
# This will be initialized when the backend starts
_memory_service_instance: Optional[MemoryService] = None


def get_memory_service() -> MemoryService:
    """Get or create the global MemoryService instance."""
    global _memory_service_instance
    if _memory_service_instance is None:
        # Use the default knowledge graph file from the project root
        project_root = Path(__file__).parent.parent.parent.parent.parent
        graph_file = project_root / "knowledge_graph.ttl"
        _memory_service_instance = MemoryService(graph_file=graph_file)
    return _memory_service_instance

