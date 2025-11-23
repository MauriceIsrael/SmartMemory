from typing import List
from rdflib import URIRef
from src.models.knowledge_graph import KnowledgeGraph
from src.models.inference_rule import InferenceRule
from src.models.triple import Triple
from src.models.verification_request import VerificationRequest
from src.services.verification_service import VerificationService
import uuid
import logging

logger = logging.getLogger(__name__)

class InferenceEngine:
    def __init__(self, rules: List[InferenceRule], verification_service: VerificationService, certainty_threshold: float = 0.9):
        self.rules = rules
        self.verification_service = verification_service
        self.certainty_threshold = certainty_threshold
        logger.info(f"Inference engine initialized with {len(rules)} rule(s), threshold={certainty_threshold}")

    def infer(self, knowledge_graph: KnowledgeGraph) -> List[Triple]:
        newly_inferred_triples = []
        total_inferences = 0
        total_verifications = 0
        
        try:
            logger.debug(f"Starting inference process with {len(self.rules)} rule(s)")
            
            for rule in self.rules:
                rule_triggered = False
                rule_inferences = 0
                
                if len(rule.conditions) == 1:
                    condition = rule.conditions[0]
                    
                    # Find matching triples in the graph
                    matches = list(knowledge_graph.explicit_graph.triples((None, URIRef(condition.predicate), None)))
                    
                    if matches:
                        logger.info(f"🔍 Rule '{rule.name}' triggered by {len(matches)} fact(s)")
                        rule_triggered = True
                    
                    for s, p, o in matches:
                        # Log the triggering fact
                        logger.debug(f"   Fact: {s} {p} {o}")
                        
                        # This is a mock certainty score
                        certainty_score = 0.7 

                        inferred_triple = Triple(
                            subject=str(s),
                            predicate=rule.conclusion.predicate,
                            object=str(o)
                        )

                        if certainty_score < self.certainty_threshold:
                            logger.info(f"   ⚠️  Inferred (low confidence {certainty_score:.2f}): {inferred_triple.subject} {inferred_triple.predicate} {inferred_triple.object}")
                            logger.info(f"   → Requesting user verification")
                            
                            verification_request = VerificationRequest(
                                id=str(uuid.uuid4()),
                                triple=inferred_triple,
                                certainty_score=certainty_score
                            )
                            self.verification_service.add(verification_request)
                            total_verifications += 1
                        else:
                            logger.info(f"   ✓ Inferred (high confidence {certainty_score:.2f}): {inferred_triple.subject} {inferred_triple.predicate} {inferred_triple.object}")
                            logger.info(f"   → Added automatically to knowledge graph")
                            newly_inferred_triples.append(inferred_triple)
                            rule_inferences += 1
                
                if rule_triggered:
                    total_inferences += rule_inferences
                    logger.info(f"   Rule '{rule.name}' produced {rule_inferences} automatic inference(s)")
            
            # Summary logging
            if total_inferences > 0 or total_verifications > 0:
                logger.info(f"📊 Inference summary: {total_inferences} fact(s) added automatically, {total_verifications} pending verification(s)")
            else:
                logger.debug("No inferences triggered")
                
        except Exception as e:
            logger.error(f"Error during inference: {e}", exc_info=True)
            
        return newly_inferred_triples