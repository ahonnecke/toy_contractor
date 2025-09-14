# Contract Generation Demo Scripts

This folder contains Python scripts for interacting with the Contract Generation API.

## Available Scripts

### 1. Health Check
Check if the API is healthy and ready to accept requests.

```bash
python health_check.py [base_url]
```

### 2. Create Contract
Create a new contract based on a title and description.

```bash
python create_contract.py <title> <description> [base_url]
```

Example:
```bash
python create_contract.py "Software Agreement" "Create a software development agreement between a client and a developer."
```

### 3. List Contracts
List all available contracts.

```bash
python list_contracts.py [base_url]
```

### 4. Refine Contract
Refine an existing contract with additional instructions.

```bash
python refine_contract.py <contract_id> <refinement_prompt> [base_url]
```

Example:
```bash
python refine_contract.py 1 "Add a termination clause that allows either party to terminate with 30 days written notice."
```

## Notes

- All scripts default to using `http://api:8000` as the base URL if not specified.
- The scripts include retry logic to handle cases where the API service is still starting up.
- Each script can be run independently as needed.
