"""
load_document MCP tool implementation.
"""

from typing import Any, List
from pathlib import Path
import uuid
from mcp.types import Tool, TextContent

from smart_memory.logging_config import get_logger
from smart_memory.document.document_loader import DocumentLoader
from smart_memory.document.rule_extractor import RuleExtractor

logger = get_logger(__name__)

LOAD_DOCUMENT_TOOL = Tool(
    name="load_document",
    description=(
        "Load a document (PDF, Text, Markdown) into the knowledge graph and automatically extract business rules."
        "\n\n**Usage:**"
        "\n- Load a file: load_document(file_path='/path/to/rules.pdf')"
        "\n- Upload content: load_document(content='Rule 1:...', title='My Rules')"
        "\n\n**What it does:**"
        "\n1. Parses the document"
        "\n2. Stores metadata in the graph"
        "\n3. Analyzes content with LLM to extract business rules"
        "\n4. Saves extracted rules as 'PENDING' for validation"
        "\n\n**Options:**"
        "\n- store_content: Set to True to save full text in graph"
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Absolute path to the document file (PDF, TXT, MD)",
            },
            "url": {
                "type": "string",
                "description": "URL of the document (not yet implemented)",
            },
            "content": {
                "type": "string",
                "description": "Direct text content to load",
            },
            "title": {
                "type": "string",
                "description": "Title of the document (optional, auto-detected if file)",
            },
            "store_content": {
                "type": "boolean",
                "description": "Whether to store the full text content in the knowledge graph",
                "default": False,
            },
            "extract_rules": {
                "type": "boolean",
                "description": "Whether to automatically extract rules using LLM",
                "default": True,
            },
        },
        "oneOf": [
            {"required": ["file_path"]},
            {"required": ["content"]},
        ],
    },
)

async def load_document(
    arguments: dict[str, Any],
    graph,
    rule_engine,
) -> List[TextContent]:
    """
    Load a document and extract rules.
    
    Args:
        arguments: Tool args
        graph: ProvenanceGraph
        rule_engine: RuleEngine
        
    Returns:
        List of TextContent
    """
    file_path = arguments.get("file_path")
    content = arguments.get("content")
    title = arguments.get("title")
    store_content = arguments.get("store_content", False)
    do_extract_rules = arguments.get("extract_rules", True)

    loader = DocumentLoader(graph)
    
    try:
        # 1. Load Document
        if file_path:
            logger.info(f"Loading document from file: {file_path}")
            doc_uri = loader.load_file(Path(file_path), title=title, store_content=store_content)
            # Fetch content for extraction if not stored? 
            # DocumentLoader extracts content but returns URI.
            # We need the content for extraction.
            # We can re-read or modify DocumentLoader to return content/metadata too.
            # For now, let's re-parse simply or assume we need to adjust DocumentLoader.
            # Rereading is safer/easier for now.
            pars_res = loader.parsers[Path(file_path).suffix.lower()].parse(Path(file_path))
            doc_content = pars_res["content"]
            doc_title = title or pars_res["metadata"].get("title") or Path(file_path).stem
            
        elif content:
            # TODO: Implement load_content in DocumentLoader (direct string)
            # For now, let's skip direct content or treat it as text
            return [TextContent(type="text", text="❌ Direct content loading not yet implemented in DocumentLoader.")]
        else:
            return [TextContent(type="text", text="❌ Must provide file_path or content.")]

        response_text = f"✅ Document loaded successfully.\n"
        response_text += f"**URI:** {doc_uri}\n"
        response_text += f"**Title:** {doc_title}\n"

        # 2. Extract Rules
        num_rules = 0
        if do_extract_rules:
            extractor = RuleExtractor()
            rules = await extractor.extract_rules(doc_content, doc_title)
            
            num_rules = len(rules)
            if num_rules > 0:
                from smart_memory.tools.pending_rules import add_pending_rule
                
                response_text += f"\n✨ **Extracted {num_rules} rules:**\n"
                for rule in rules:
                    rule_id = rule.get('rule_id', f"rule_{uuid.uuid4().hex[:8]}")
                    # Ensure rule_data has everything needed
                    rule_data = rule.copy()
                    rule_data['source_doc_uri'] = str(doc_uri)
                    
                    add_pending_rule(rule_id, rule_data)
                    response_text += f"- {rule_id} (Conf: {rule.get('confidence')})\n"
                response_text += f"\nUse `get_pending_rules` to review and approve them."
            else:
                response_text += f"\n⚠️ No rules extracted (or framework extraction stub used).\n"
                if len(doc_content) > 100000:
                    response_text += f"(Document size {len(doc_content)} chars might be too large for full scan)\n"

        return [TextContent(type="text", text=response_text)]

    except Exception as e:
        logger.error(f"Error loading document: {e}", exc_info=True)
        return [TextContent(type="text", text=f"❌ Error loading document: {str(e)}")]
