"""
Rule extractor for documents using LLM.
"""

import json
from typing import List, Dict, Any, Optional
from mcp.types import TextContent
from smart_memory.logging_config import get_logger
from smart_memory.document.document_prompts import EXTRACT_RULES_PROMPT

logger = get_logger(__name__)

class RuleExtractor:
    """
    Extracts semantic rules from document content using an LLM.
    """
    
    def __init__(self, llm_client=None):
        # We might need to inject an LLM client or use the one from config/server
        # For MCP server, we usually don't have direct access to the LLM that is calling us!
        # This is a tricky part of key architecture. 
        # SmartMemory acts as a tool FOR an LLM. 
        # But here we want to "Process" a document.
        # IF we want to use an LLM *inside* SmartMemory to process the doc, 
        # we need an LLM client (e.g. via litellm or heavy dependency).
        # OR: We expose the content to the User/Assistant via MCP and ask IT to extract rules?
        # The prompt says: "I'd like for example to make an LLM read the rules... and automatically extract rules".
        # If we are the Server, we can provide a tool "extract_rules(text)" which the Assistant calls.
        # But the User wants "CLI loading". CLI runs python. Python needs an LLM client to do extraction.
        #
        # OPTION A: The CLI tool calls an external LLM API (OpenAI/Anthropic).
        # OPTION B: The CLI tool asks the USER to provide the analysis? No.
        #
        # Let's assume we need a configured LLM client in SmartMemory for this autonomous feature.
        # For now, I'll create the structure. If no LLM client is available, maybe we fallback or mock?
        # A common pattern for "Agentic" tools is to have their own simple LLM client.
        pass

    async def extract_rules(self, content: str, title: str, page: Optional[str] = "Unknown") -> List[Dict[str, Any]]:
        """
        Extract rules from content using LLM.
        
        Args:
            content: Text content
            title: Document title
            page: Page number or context
            
        Returns:
            List of rule dictionaries
        """
        try:
            from litellm import completion
            import os
        except ImportError:
            logger.error("litellm not installed. Please install with: pip install litellm")
            return []

        model = os.getenv("SMART_MEMORY_LLM_MODEL", "gpt-3.5-turbo")
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("ANTHROPIC_API_KEY") 
        ollama_host = os.getenv("OLLAMA_HOST")
        
        # Simple check for Ollama or other local models which might not need key
        if not api_key and "ollama" not in model and "localhost" not in model:
             logger.warning("No API key found for LLM (OPENAI_API_KEY, etc.). Rule extraction might fail.")

        logger.info(f"Extracting rules from '{title}' (page {page}) using model: {model}")
        if ollama_host:
             logger.info(f"Using custom Ollama Host: {ollama_host}")

        # Construct the prompt
        prompt = EXTRACT_RULES_PROMPT.format(
            document_title=title,
            page_number=page,
            document_content=content[:8000] # Truncate to avoid context limit issues for now
        )

        try:
            # Prepare args
            kwargs = {
                "model": model,
                "messages": [{"role": "user", "content": prompt}],
                "temperature": 0.1,
            }
            
            # Explicitly pass api_base if OLLAMA_HOST is set and we are using ollama
            if ollama_host and "ollama" in model:
                kwargs["api_base"] = ollama_host

            response = completion(**kwargs)
            
            response_content = response.choices[0].message.content
            logger.debug(f"LLM Response: {response_content[:200]}...")

            # Parse JSON from response
            # The prompt asks for a JSON array. We need to find it in the text.
            initial_json = self._extract_json(response_content)
            
            if initial_json:
                logger.info(f"Extracted {len(initial_json)} candidates from LLM response")
                return initial_json
            else:
                logger.warning("Could not parse JSON from LLM response")
                return []

        except Exception as e:
            logger.error(f"Error calling LLM for rule extraction: {e}")
            return []

    def _extract_json(self, text: str) -> List[Dict[str, Any]]:
        """Helper to find and parse JSON list in text."""
        try:
            # Try full parse first
            return json.loads(text)
        except json.JSONDecodeError:
            pass
            
        # Try to find [ ... ]
        import re
        match = re.search(r"\[.*\]", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError:
                pass
        
        return []

    def chunk_content(self, content: str, chunk_size: int = 4000) -> List[str]:
        """Split content into chunks."""
        # Simple character-based chunking for now
        # TODO: Improve with token-based chunking
        return [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
