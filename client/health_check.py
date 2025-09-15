#!/usr/bin/env python3

import requests
import sys
import time


def check_health(base_url="http://api:8000", max_retries=10, retry_delay=2):
    """
    Check the health of the API service

    Args:
        base_url: Base URL of the API service
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
    """
    print(f"Checking API health at {base_url}/health")

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            response = requests.get(f"{base_url}/health", timeout=5)
            print(f"Status code: {response.status_code}")
            print(f"Response: {response.text}")
            print("\nAPI is healthy!")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed after {max_retries} attempts")
                return False


if __name__ == "__main__":
    # Use command line argument as base URL if provided
    base_url = sys.argv[1] if len(sys.argv) > 1 else "http://api:8000"
    check_health(base_url)
