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
            from pathlib import Path
        except ImportError:
            logger.error("litellm not installed. Please install with: pip install litellm")
            return []

        # Read LLM config from saved file or environment variables
        from smart_memory.config import config
        import os
        
        config_file = config.project_root / "llm_config.json"
        
        # Try to read from file first (for local development)
        if config_file.exists():
            try:
                with open(config_file, 'r') as f:
                    llm_config = json.load(f)
                provider = llm_config.get("provider", "openai")
                model = llm_config.get("model", "gpt-3.5-turbo")
                api_key = llm_config.get("api_key")
                base_url = llm_config.get("base_url")
                temperature = llm_config.get("temperature", 0.7)
                logger.info(f"Using LLM config from file: {provider}/{model}")
            except Exception as e:
                logger.error(f"Error reading LLM config file: {e}")
                return []
        else:
            # Fallback to environment variables (for Docker)
            provider = os.getenv("LLM_PROVIDER", "ollama")
            model = os.getenv("LLM_MODEL", "llama3")
            api_key = os.getenv("LLM_API_KEY")
            base_url = os.getenv("LLM_BASE_URL", "http://localhost:11434")
            temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
            
            if provider != "ollama" and not api_key:
                logger.error(f"LLM configuration not found. Either configure via dashboard or set environment variables (LLM_PROVIDER, LLM_MODEL, LLM_API_KEY, etc.)")
                return []
            
            logger.info(f"Using LLM config from environment: {provider}/{model}")

        logger.info(f"Extracting rules from '{title}' (page {page}) using {provider}/{model}")

        # Construct the prompt
        prompt = EXTRACT_RULES_PROMPT.format(
            document_title=title,
            page_number=page,
            document_content=content[:8000] # Truncate to avoid context limit issues for now
        )

        try:
            # Prepare args based on provider
            kwargs = {
                "messages": [{"role": "user", "content": prompt}],
                "temperature": temperature,
            }
            
            if provider == "ollama":
                kwargs["model"] = f"ollama/{model}"
                if base_url:
                    kwargs["api_base"] = base_url
            else:
                kwargs["model"] = model
                if api_key:
                    kwargs["api_key"] = api_key

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
