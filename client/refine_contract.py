#!/usr/bin/env python3

import requests
import sys
import time


def refine_contract(
    contract_id,
    refinement_prompt,
    base_url="http://api:8000",
    max_retries=5,
    retry_delay=2,
):
    """
    Refine an existing contract

    Args:
        contract_id: ID of the contract to refine
        refinement_prompt: Instructions for refinement
        base_url: Base URL of the API service
        max_retries: Maximum number of retries
        retry_delay: Delay between retries in seconds
    """
    print(f"Refining contract ID: {contract_id}")
    print(f"Refinement instructions: {refinement_prompt}")

    data = {"contract_id": contract_id, "refinement_instructions": refinement_prompt}

    for attempt in range(max_retries):
        try:
            print(f"Attempt {attempt + 1}/{max_retries}")
            response = requests.post(
                f"{base_url}/contracts/refine/",
                json=data,
                timeout=300,  # 5 minute timeout for contract refinement
            )
            response.raise_for_status()
            result = response.json()

            print("\nContract refined successfully:")
            print(f"New ID: {result.get('id')}")
            print(f"New Title: {result.get('title')}")
            print("\nRefined Content:")
            print(result.get("content"))
            return result
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            if attempt < max_retries - 1:
                print(f"Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print(f"Failed after {max_retries} attempts")

                # Try to get the original contract to show what we were trying to refine
                try:
                    get_response = requests.get(
                        f"{base_url}/contracts/{contract_id}", timeout=10
                    )
                    if get_response.status_code == 200:
                        original = get_response.json()
                        print("\nOriginal contract that was being refined:")
                        print(f"ID: {original.get('id')}")
                        print(f"Title: {original.get('title')}")
                        print(f"Content: {original.get('content')[:100]}...")
                except:
                    pass

                return None


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage: python refine_contract.py <contract_id> <refinement_prompt> [base_url]"
        )
        sys.exit(1)

    contract_id = int(sys.argv[1])
    refinement_prompt = sys.argv[2]
    base_url = sys.argv[3] if len(sys.argv) > 3 else "http://api:8000"

    refine_contract(contract_id, refinement_prompt, base_url)
