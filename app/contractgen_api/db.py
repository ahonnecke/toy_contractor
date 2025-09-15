import os
import json
from typing import List, Dict, Optional, Any
from redis import asyncio as aioredis

# Get Redis connection details from environment variables
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))

# Redis key prefixes
CONTRACT_KEY_PREFIX = "contract:"
CONTRACT_ID_COUNTER = "contract:id:counter"


# Redis client instance
_redis_client = None

async def get_redis():
    """Get or create Redis client"""
    global _redis_client
    if _redis_client is None:
        _redis_client = await aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    return _redis_client

async def init_db():
    """Initialize the Redis database"""
    # Redis doesn't need schema initialization like SQLite
    # Just ensure we can connect
    redis = await get_redis()
    # Check if the ID counter exists, if not initialize it
    if not await redis.exists(CONTRACT_ID_COUNTER):
        await redis.set(CONTRACT_ID_COUNTER, 0)


async def save_contract(title: str, content: str) -> int:
    """Save a contract to Redis and return its ID"""
    redis = await get_redis()
    
    # Increment the ID counter to get a new ID
    contract_id = await redis.incr(CONTRACT_ID_COUNTER)
    
    # Create contract data with timestamp
    contract_data = {
        "id": contract_id,
        "title": title,
        "content": content,
        "created_at": import_time().isoformat()
    }
    
    # Save to Redis
    await redis.set(
        f"{CONTRACT_KEY_PREFIX}{contract_id}", 
        json.dumps(contract_data)
    )
    
    return contract_id

def import_time():
    """Import time module and return current time"""
    from datetime import datetime
    return datetime.now()


async def get_contract(contract_id: int) -> Optional[Dict[str, Any]]:
    """Get a contract by ID from Redis"""
    redis = await get_redis()
    
    # Get contract data from Redis
    contract_data = await redis.get(f"{CONTRACT_KEY_PREFIX}{contract_id}")
    
    if contract_data:
        contract = json.loads(contract_data)
        return {"id": contract["id"], "title": contract["title"], "content": contract["content"]}
    
    return None


async def get_all_contracts() -> List[Dict[str, Any]]:
    """Get all contracts from Redis"""
    redis = await get_redis()
    
    # Get the current max ID
    max_id = await redis.get(CONTRACT_ID_COUNTER)
    if not max_id:
        return []
    
    max_id = int(max_id)
    contracts = []
    
    # Get all contracts by their IDs
    for contract_id in range(1, max_id + 1):
        contract_data = await redis.get(f"{CONTRACT_KEY_PREFIX}{contract_id}")
        if contract_data:
            contract = json.loads(contract_data)
            contracts.append({
                "id": contract["id"], 
                "title": contract["title"], 
                "content": contract["content"]
            })
    
    return contracts
