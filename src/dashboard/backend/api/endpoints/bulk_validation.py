"""
Bulk rule validation endpoints.
"""

from typing import List, Dict, Any, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

# Import persistence logic directly or via service wrapper
# We reuse the tool logic which handles persistence
from smart_memory.tools import pending_rules
from smart_memory.inference.rule_engine import RuleEngine, load_rules
from smart_memory.knowledge.graph import ProvenanceGraph
from services.memory_service import get_memory_service

router = APIRouter()

class BulkActionRequest(BaseModel):
    rule_ids: List[str]

@router.get("/rules/pending")
async def get_pending_rules_api(doc_id: Optional[str] = None):
    """Get pending rules."""
    pending_rules._load_pending_rules()
    
    # Convert dict to list
    rules_list = []
    for rule_id, data in pending_rules._pending_rules.items():
        # Filter by document if requested
        if doc_id:
            source_uri = data.get("source_doc_uri", "")
            if doc_id not in source_uri: # Simple substring match for ID in URI
                continue
                
        rule_item = data.copy()
        rule_item["rule_id"] = rule_id
        rules_list.append(rule_item)
        
    return rules_list

@router.post("/rules/bulk-approve")
async def bulk_approve(request: BulkActionRequest):
    """Approve multiple rules."""
    pending_rules._load_pending_rules()
    memory = get_memory_service()
    
    results = {
        "approved": [],
        "failed": []
    }
    
    for rule_id in request.rule_ids:
        # We reuse the tool function logic but need to adapt args
        # tool needs arguments dict
        
        # Or simpler: replicate logic here using memory service
        if rule_id not in pending_rules._pending_rules:
            results["failed"].append({"rule_id": rule_id, "reason": "Not found"})
            continue
            
        try:
             # Call approve tool implementation directly? 
             # It returns [TextContent].
             # Better to use Tool implementation logic:
             rule_data = pending_rules._pending_rules[rule_id]
             from smart_memory.tools.load_custom_rule import load_custom_rule
             
             await load_custom_rule(
                {
                    "rule_content": rule_data["sparql_pattern"],
                    "rule_id": rule_id,
                    "description": rule_data["description"],
                },
                memory.rule_engine,
                memory.p_graph,
            )
             
             del pending_rules._pending_rules[rule_id]
             results["approved"].append(rule_id)
        except Exception as e:
            results["failed"].append({"rule_id": rule_id, "reason": str(e)})
            
    pending_rules._save_pending_rules()
    return results

@router.post("/rules/bulk-reject")
async def bulk_reject(request: BulkActionRequest):
    """Reject multiple rules."""
    pending_rules._load_pending_rules()
    
    results = {
        "rejected": [],
        "failed": []
    }
    
    for rule_id in request.rule_ids:
        if rule_id in pending_rules._pending_rules:
            del pending_rules._pending_rules[rule_id]
            results["rejected"].append(rule_id)
        else:
            results["failed"].append({"rule_id": rule_id, "reason": "Not found"})
            
    pending_rules._save_pending_rules()
    return results
