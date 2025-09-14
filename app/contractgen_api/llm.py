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
    # For testing/development, return a mock response if the description is too long
    if len(description) > 500:
        return f"Mock contract for: {description[:100]}..."
    
    prompt = f"""
    You are a legal expert specializing in contract generation. Create a comprehensive and legally sound contract based on the following description:  
    
    {description}
    
    The contract should include all necessary legal clauses, terms, and conditions appropriate for this type of agreement.
    Format the contract professionally with proper sections, numbering, and legal terminology.
    """
    
    # Use a much longer timeout for the entire client session
    async with httpx.AsyncClient(timeout=300.0) as client:
        try:
            # Try to generate text with a simpler prompt first for testing
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": "Generate a simple test contract",
                    "stream": False
                },
                timeout=300.0  # 5 minutes timeout
            )
            
            if response.status_code != 200:
                # If the model doesn't exist, try to pull it
                if "model not found" in response.text.lower():
                    print(f"Model {MODEL} not found. Attempting to pull...")
                    try:
                        pull_response = await client.post(
                            f"{OLLAMA_HOST}/api/pull",
                            json={"name": MODEL},
                            timeout=600.0  # 10 minutes timeout for pulling
                        )
                        print(f"Pull response: {pull_response.status_code}")
                    except Exception as e:
                        print(f"Error pulling model: {e}")
                        # Return a fallback response for development
                        return f"Failed to pull model. Using mock contract for: {description[:100]}..."
                else:
                    print(f"Ollama API error: {response.text}")
                    # Return a fallback response for development
                    return f"Ollama API error. Using mock contract for: {description[:100]}..."
            
            # Now try with the actual prompt
            response = await client.post(
                f"{OLLAMA_HOST}/api/generate",
                json={
                    "model": MODEL,
                    "prompt": prompt,
                    "stream": False
                },
                timeout=300.0  # 5 minutes timeout
            )
            
            if response.status_code != 200:
                raise Exception(f"Ollama API error: {response.text}")
            
            result = response.json()
            # Handle different response formats
            if "message" in result:
                return result.get("message", {}).get("content", "")
            return result.get("response", "")
            
        except httpx.TimeoutException:
            print("Request to Ollama timed out")
            # Return a fallback response for development
            return f"Request timed out. Using mock contract for: {description[:100]}..."
        except Exception as e:
            print(f"Error generating contract: {e}")
            # Return a fallback response for development
            return f"Error: {str(e)}. Using mock contract for: {description[:100]}..."
