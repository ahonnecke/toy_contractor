#!/usr/bin/env python3

import requests
import sys
import time


def list_contracts(base_url="http://api:8000", max_retries=5, retry_delay=2):
    """
    List all contracts

    Args:
        base_url: Base URL of the API service
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
    """
    print(f"Listing all contracts from {base_url}/contracts/")

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            response = requests.get(
                f"{base_url}/contracts/", timeout=60
            )  # 1 minute timeout
            response.raise_for_status()
            contracts = response.json()

            print("\nAvailable contracts:")
            if not contracts:
                print("No contracts found.")
                return []

            for contract in contracts:
                print(f"ID: {contract.get('id')}, Title: {contract.get('title')}")

            return contracts
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed after {max_retries} attempts")
                return None


if __name__ == "__main__":
    # Use command line argument as base URL if provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://api:8000"
    list_contracts(base_url)
