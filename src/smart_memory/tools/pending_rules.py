"""
Pending rule approvals management.

Stores rules proposed by the LLM that require user approval before activation.
"""

from typing import Any
from mcp.types import Tool, TextContent
from smart_memory.logging_config import get_logger

logger = get_logger(__name__)

# In-memory storage for pending rules, backed by JSON file
import json
from pathlib import Path
from smart_memory.config import config

PENDING_RULES_FILE = Path("pending_rules.json")

def _load_pending_rules():
    global _pending_rules
    if PENDING_RULES_FILE.exists():
        try:
            with open(PENDING_RULES_FILE, 'r') as f:
                _pending_rules = json.load(f)
        except Exception as e:
            logger.error(f"Failed to load pending rules from {PENDING_RULES_FILE}: {e}")
            _pending_rules = {}

def _save_pending_rules():
    try:
        with open(PENDING_RULES_FILE, 'w') as f:
            json.dump(_pending_rules, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save pending rules to {PENDING_RULES_FILE}: {e}")

_pending_rules: dict[str, dict] = {}
_load_pending_rules()  # Load on import

# Tool definition
GET_PENDING_RULES_TOOL = Tool(
    name="get_pending_rules",
    description=(
        "Get list of rules proposed by the LLM that are awaiting user approval. "
        "Use this after suggesting a rule to show the user what needs approval."
    ),
    inputSchema={
        "type": "object",
        "properties": {},
    },
)

APPROVE_RULE_TOOL = Tool(
    name="approve_rule",
    description=(
        "Approve a pending rule and activate it in the inference engine. "
        "The rule will start inferring facts immediately.\n\n"
        "**SYSTEM: DO NOT CALL THIS AUTOMATICALLY. WAIT FOR USER INPUT.**\n"
        "You CANNOT verify/approve your own rules. You must display the rule using `suggest_rule`, "
        "wait for the user to read it, and only call this if they strictly say 'Approved' or 'Yes'."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "rule_id": {
                "type": "string",
                "description": "ID of the rule to approve",
            },
        },
        "required": ["rule_id"],
    },
)

REJECT_RULE_TOOL = Tool(
    name="reject_rule",
    description=(
        "Reject a pending rule. It will not be activated and will be removed from pending list."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "rule_id": {
                "type": "string",
                "description": "ID of the rule to reject",
            },
        },
        "required": ["rule_id"],
    },
)


async def get_pending_rules(arguments: dict[str, Any]) -> list[TextContent]:
    """Get list of pending rules awaiting approval."""
    _load_pending_rules()  # Reload to get latest changes from other processes
    if not _pending_rules:
        return [
            TextContent(
                type="text",
                text="✓ No pending rules. All proposed rules have been approved or rejected."
            )
        ]
    
    # Format pending rules list
    response = f"📋 **Pending Rules ({len(_pending_rules)}):**\n\n"
    
    for rule_id, rule_data in _pending_rules.items():
        response += f"**{rule_id}**\n"
        response += f"  Description: {rule_data['description']}\n"
        response += f"  Confidence: {rule_data.get('confidence', 1.0)}\n"
        response += f"  Potential inferences: {rule_data.get('num_inferences', 'unknown')}\n"
        if 'preview' in rule_data:
            response += f"  Preview: {rule_data['preview'][:100]}...\n"
        response += "\n"
    
    response += "Use approve_rule(rule_id) or reject_rule(rule_id) to process these rules."
    
    return [TextContent(type="text", text=response)]


async def approve_rule(
    arguments: dict[str, Any],
    rule_engine,
    graph,
) -> list[TextContent]:
    """Approve and activate a pending rule."""
    rule_id = arguments["rule_id"]
    
    if rule_id not in _pending_rules:
        return [
            TextContent(
                type="text",
                text=f"❌ Rule '{rule_id}' not found in pending rules."
            )
        ]
    
    rule_data = _pending_rules[rule_id]
    
    try:
        # Load the rule using load_custom_rule
        from smart_memory.tools.load_custom_rule import load_custom_rule
        
        result = await load_custom_rule(
            {
                "rule_content": rule_data["sparql_pattern"],
                "rule_id": rule_id,
                "description": rule_data["description"],
            },
            rule_engine,
            graph,
        )
        
        # Remove from pending
        del _pending_rules[rule_id]
        _save_pending_rules()
        
        logger.info(f"Rule '{rule_id}' approved and activated")
        
        return [
            TextContent(
                type="text",
                text=f"✅ Rule '{rule_id}' approved and activated.\n"
                     f"The rule is now running and will infer new facts automatically."
            )
        ]
        
    except Exception as e:
        logger.error(f"Failed to approve rule '{rule_id}': {e}", exc_info=True)
        return [
            TextContent(
                type="text",
                text=f"❌ Failed to activate rule '{rule_id}': {str(e)}"
            )
        ]


async def reject_rule(arguments: dict[str, Any]) -> list[TextContent]:
    """Reject a pending rule."""
    rule_id = arguments["rule_id"]
    
    if rule_id not in _pending_rules:
        return [
            TextContent(
                type="text",
                text=f"❌ Rule '{rule_id}' not found in pending rules."
            )
        ]
    
    # Remove from pending
    del _pending_rules[rule_id]
    _save_pending_rules()
    
    logger.info(f"Rule '{rule_id}' rejected")
    
    return [
        TextContent(
            type="text",
            text=f"✓ Rule '{rule_id}' rejected and removed from pending list."
        )
    ]


def add_pending_rule(rule_id: str, rule_data: dict) -> None:
    """Add a rule to pending approvals."""
    _pending_rules[rule_id] = rule_data
    _save_pending_rules()
    logger.info(f"Added rule '{rule_id}' to pending approvals")


def clear_pending_rules() -> None:
    """Clear all pending rules (for testing)."""
    global _pending_rules
    _pending_rules = {}


__all__ = [
    "GET_PENDING_RULES_TOOL",
    "APPROVE_RULE_TOOL",
    "REJECT_RULE_TOOL",
    "get_pending_rules",
    "approve_rule",
    "reject_rule",
    "add_pending_rule",
    "clear_pending_rules",
]
