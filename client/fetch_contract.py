#!/usr/bin/env python3

import requests
import sys
import json
import time
import os

def fetch_contract(contract_id, base_url="http://api:8000", output_format="full", max_retries=5, retry_delay=2):
    """
    Fetch a specific contract by ID
    
    Args:
        contract_id: ID of the contract to fetch
        base_url: Base URL of the API service
        output_format: Output format (full, content, or json)
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
    """
    print(f"Fetching contract ID {contract_id} from {base_url}/contracts/{contract_id}")
    
    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt+1}/{max_retries}")
            response = requests.get(f"{base_url}/contracts/{contract_id}", timeout=60)  # 1 minute timeout
            response.raise_for_status()
            contract = response.json()
            
            if output_format == "json":
                print(json.dumps(contract, indent=2))
            elif output_format == "content":
                print(contract["content"])
            else:  # full
                print(f"\nContract ID: {contract['id']}")
                print(f"Title: {contract['title']}")
                print("\nContent:")
                print(contract["content"])
                
            return contract
        except requests.exceptions.RequestException as e:
            if e.response and e.response.status_code == 404:
                print(f"Error: Contract with ID {contract_id} not found")
                return None
            print(f"Error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed after {max_retries} attempts")
                return None
    
if __name__ == "__main__":
    # Parse command line arguments
    import argparse
    
    parser = argparse.ArgumentParser(description="Fetch a contract by ID")
    parser.add_argument("id", type=int, help="Contract ID to fetch")
    parser.add_argument("--api-url", default="http://api:8000", help="API URL (default: http://api:8000)")
    parser.add_argument("--output", "-o", choices=["full", "content", "json"], default="full", 
                        help="Output format: full (default), content (only content), or json (raw JSON)")
    
    args = parser.parse_args()
    
    fetch_contract(args.id, base_url=args.api_url, output_format=args.output)
