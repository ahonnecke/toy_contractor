import os
import httpx
from typing import Dict, Any

# Get configuration from environment variables
PROVIDER = os.environ.get("PROVIDER", "ollama")
MODEL = os.environ.get("MODEL", "mistral:7b")
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


async def generate_contract(description: str) -> str:
    """Generate a contract based on the provided description"""
    if PROVIDER.lower() == "ollama":
        return await _generate_with_ollama(description)
    else:
        raise ValueError(f"Unsupported provider: {PROVIDER}")


async def _generate_with_ollama(description: str) -> str:
    """Generate text using Ollama API"""
    prompt = f"""
    You are a legal expert specializing in contract generation. Create a comprehensive and legally sound contract based on the following description:  
    
    {description}
    
    The contract should include all necessary legal clauses, terms, and conditions appropriate for this type of agreement.
    Format the contract professionally with proper sections, numbering, and legal terminology.
    """
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model": MODEL,
                "prompt": prompt,
                "stream": False
            },
            timeout=60.0
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama API error: {response.text}")
        
        result = response.json()
        return result.get("response", "")
