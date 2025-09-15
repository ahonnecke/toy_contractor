#!/usr/bin/env python3

import requests
import sys
import time
from urllib.parse import urljoin


def test_api_connectivity(base_url, max_retries=5, retry_delay=2):
    """
    Test connectivity to the API service

    Args:
        base_url: Base URL of the API service
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
    """
    print(f"Testing connectivity to API at {base_url}")

    # Test endpoints
    endpoints = ["/health", "/", "/contracts/"]

    for endpoint in endpoints:
        url = urljoin(base_url, endpoint)
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries} - Testing endpoint: {url}")
                response = requests.get(url, timeout=5)
                print(f"  Status code: {response.status_code}")
                print(f"  Response: {response.text[:100]}...")
                # If we get here, the request succeeded
                break
            except requests.exceptions.RequestException as e:
                print(f"  Error: {e}")
                if attempt < max_retries - 1:
                    print(f"  Retrying in {retry_delay} seconds...")
                    time.sleep(retry_delay)
                else:
                    print(f"  Failed after {max_retries} attempts")
        print()  # Add a blank line between endpoints

    # Try to create a simple contract
    try:
        print("Attempting to create a test contract...")
        contract_data = {
            "title": "Test Contract",
            "description": "This is a test contract to verify API connectivity",
        }
        response = requests.post(
            urljoin(base_url, "/contracts/"), json=contract_data, timeout=10
        )
        print(f"  Status code: {response.status_code}")
        print(f"  Response: {response.text[:100]}...")
    except requests.exceptions.RequestException as e:
        print(f"  Error creating contract: {e}")

    print("\nConnectivity test complete")


if __name__ == "__main__":
    # Default to http://api:8000 if no argument is provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://api:8000"
    test_api_connectivity(base_url)
