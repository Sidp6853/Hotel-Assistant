"""
Utility for parsing JSON from LLM outputs
"""
import json
import logging

logger = logging.getLogger(__name__)


def safe_json_load(content: str) -> dict:
    """
    Safely parse JSON from LLM output.
    Handles ```json blocks and trailing text.
    
    Args:
        content: Raw LLM output string
        
    Returns:
        Parsed dictionary
        
    Raises:
        ValueError: If JSON parsing fails
    """
    try:
        content = content.strip()
        
        # Handle markdown code blocks
        if content.startswith("```json"):
            parts = content.split("```")
            if len(parts) >= 3:
                content = parts[1].replace("json", "").strip()
        elif content.startswith("```"):
            content = content.split("```")[1].strip()
        
        return json.loads(content)
        
    except Exception as e:
        logger.error(f"JSON parse error: {e}")
        logger.error(f"Content: {content[:200]}")
        raise ValueError(f"Invalid JSON from model: {e}")