#!/usr/bin/env python3

import requests
import sys
import time


def create_contract(
    title, description, base_url="http://api:8000", max_retries=5, retry_delay=2
):
    """
    Create a new contract

    Args:
        title: Contract title
        description: Contract description
        base_url: Base URL of the API service
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
    """
    print(f"Creating contract: {title}")
    print(f"Description: {description[:50]}...")

    data = {"title": title, "description": description}

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            response = requests.post(
                f"{base_url}/contracts/",
                json=data,
                timeout=300,  # 5 minute timeout for contract generation
            )
            response.raise_for_status()
            result = response.json()

            print("\nContract created successfully:")
            print(f"ID: {result.get('id')}")
            print(f"Title: {result.get('title')}")
            print("\nContent:")
            print(result.get("content"))
            return result
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed after {max_retries} attempts")
                return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_contract.py <title> <description> [base_url]")
        sys.exit(1)

    title = sys.argv[1]
    description = sys.argv[2]
    base_url = sys.argv[3] if len(sys.argv) > 3 else "http://api:8000"

    create_contract(title, description, base_url)
