#!/usr/bin/env python3

import argparse
import asyncio
import json
import sys
from typing import Dict, Any, List, Optional

import httpx


class ContractGenClient:
    """Client for interacting with the Contract Generation API"""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=60.0)

    async def close(self):
        await self.client.aclose()

    async def health_check(self) -> Dict[str, Any]:
        """Check if the API is healthy"""
        response = await self.client.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()

    async def create_contract(self, title: str, description: str) -> Dict[str, Any]:
        """Create a new contract based on the description"""
        data = {"title": title, "description": description}
        response = await self.client.post(f"{self.base_url}/contracts/", json=data)
        response.raise_for_status()
        return response.json()

    async def get_contract(self, contract_id: int) -> Dict[str, Any]:
        """Get a specific contract by ID"""
        response = await self.client.get(f"{self.base_url}/contracts/{contract_id}")
        response.raise_for_status()
        return response.json()

    async def list_contracts(self) -> List[Dict[str, Any]]:
        """List all contracts"""
        response = await self.client.get(f"{self.base_url}/contracts/")
        response.raise_for_status()
        return response.json()

    async def refine_contract(self, contract_id: int, refinement_prompt: str) -> Dict[str, Any]:
        """Refine an existing contract with additional instructions"""
        # First, get the existing contract
        contract = await self.get_contract(contract_id)
        
        # Create a refinement description
        refinement_description = f"""Original Contract: 
{contract['content']}

Refinement Instructions: 
{refinement_prompt}
"""
        
        # Create a new refined contract
        refined_title = f"{contract['title']} (Refined)"
        return await self.create_contract(refined_title, refinement_description)


async def main():
    parser = argparse.ArgumentParser(description="Contract Generation Client")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API URL")
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Health check command
    subparsers.add_parser("health", help="Check API health")
    
    # Create contract command
    create_parser = subparsers.add_parser("create", help="Create a new contract")
    create_parser.add_argument("--title", required=True, help="Contract title")
    create_parser.add_argument("--description", required=True, help="Contract description")
    
    # Get contract command
    get_parser = subparsers.add_parser("get", help="Get a specific contract")
    get_parser.add_argument("--id", required=True, type=int, help="Contract ID")
    
    # List contracts command
    subparsers.add_parser("list", help="List all contracts")
    
    # Refine contract command
    refine_parser = subparsers.add_parser("refine", help="Refine an existing contract")
    refine_parser.add_argument("--id", required=True, type=int, help="Contract ID to refine")
    refine_parser.add_argument("--prompt", required=True, help="Refinement instructions")
    
    args = parser.parse_args()
    
    client = ContractGenClient(args.api_url)
    
    try:
        if args.command == "health":
            result = await client.health_check()
            print(json.dumps(result, indent=2))
        
        elif args.command == "create":
            result = await client.create_contract(args.title, args.description)
            print("\nContract created successfully:")
            print(f"ID: {result['id']}")
            print(f"Title: {result['title']}")
            print("\nContent:")
            print(result['content'])
        
        elif args.command == "get":
            result = await client.get_contract(args.id)
            print("\nContract details:")
            print(f"ID: {result['id']}")
            print(f"Title: {result['title']}")
            print("\nContent:")
            print(result['content'])
        
        elif args.command == "list":
            results = await client.list_contracts()
            print("\nAvailable contracts:")
            for contract in results:
                print(f"ID: {contract['id']}, Title: {contract['title']}")
        
        elif args.command == "refine":
            result = await client.refine_contract(args.id, args.prompt)
            print("\nContract refined successfully:")
            print(f"New ID: {result['id']}")
            print(f"New Title: {result['title']}")
            print("\nRefined Content:")
            print(result['content'])
        
        else:
            parser.print_help()
    
    finally:
        await client.close()


if __name__ == "__main__":
    asyncio.run(main())
