#!/bin/bash

# Demo script for contract generation and refinement

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Contract Generation Demo ===${NC}"
echo

# Make sure the client service is running
if ! docker compose ps | grep -q "contractgen-client-1.*Up"; then
    echo -e "${YELLOW}Starting client service...${NC}"
    docker compose up -d client
    # Give it a moment to start
    sleep 2
fi

# Check if the API is healthy
echo -e "${YELLOW}Checking API health...${NC}"
docker compose exec -T client python api_client.py --api-url http://api:8000 health
echo

# Sample contract details
CONTRACT_TITLE="Software Development Agreement"
CONTRACT_DESCRIPTION="Create a software development agreement between a client and a development company for a mobile application project. The project will take 6 months to complete with a budget of $50,000. Include payment milestones, intellectual property rights, and confidentiality clauses."

# Create a new contract
echo -e "${YELLOW}Creating a new contract: ${GREEN}$CONTRACT_TITLE${NC}"
docker compose exec -T client python api_client.py --api-url http://api:8000 create --title "$CONTRACT_TITLE" --description "$CONTRACT_DESCRIPTION"
echo

# List all contracts
echo -e "${YELLOW}Listing all contracts...${NC}"
docker compose exec -T client python api_client.py --api-url http://api:8000 list
echo

# Get the first contract ID
CONTRACT_ID=$(docker compose exec -T client python api_client.py --api-url http://api:8000 list | grep "ID:" | head -n 1 | awk '{print $2}' | tr -d ',')

# Check if we got a valid contract ID
if [ -z "$CONTRACT_ID" ] || ! [[ "$CONTRACT_ID" =~ ^[0-9]+$ ]]; then
    echo -e "${YELLOW}No valid contract ID found. Using ID 1 as fallback.${NC}"
    CONTRACT_ID=1
fi

# Refine the contract
echo -e "${YELLOW}Refining contract ID ${GREEN}$CONTRACT_ID${NC}"
REFINEMENT_PROMPT="Please add a termination clause that allows either party to terminate with 30 days written notice. Also, add a force majeure clause to cover unforeseen circumstances."
docker compose exec -T client python api_client.py --api-url http://api:8000 refine --id "$CONTRACT_ID" --prompt "$REFINEMENT_PROMPT"
echo

echo -e "${BLUE}=== Demo Complete ===${NC}"
