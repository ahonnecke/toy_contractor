#!/bin/bash

# Demo script for contract generation and refinement

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to handle errors
handle_error() {
    echo -e "${RED}Error: $1${NC}"
    echo -e "${YELLOW}Continuing with demo...${NC}"
    echo
}

echo -e "${BLUE}=== Contract Generation Demo ===${NC}"
echo

# Make sure the client service is running
if ! docker compose ps | grep -q "contractgen-client-1.*Up"; then
    echo -e "${YELLOW}Starting client service...${NC}"
    docker compose up -d client
    # Give it a moment to start
    sleep 5
    echo -e "${GREEN}Client service started.${NC}"
fi

# Check if the API is healthy
echo -e "${YELLOW}Checking API health...${NC}"
if ! docker compose exec -T client python api_client.py --api-url http://api:8000 health; then
    handle_error "API health check failed. The API service might not be ready yet."
else
    echo -e "${GREEN}API is healthy!${NC}"
    echo
fi

# Sample contract details - using a shorter description for faster processing
CONTRACT_TITLE="Software Development Agreement"
CONTRACT_DESCRIPTION="Create a simple software development agreement between a client and a developer."

# Create a new contract
echo -e "${YELLOW}Creating a new contract: ${GREEN}$CONTRACT_TITLE${NC}"
echo -e "${YELLOW}This may take some time as the LLM generates the contract...${NC}"
if ! docker compose exec -T client python api_client.py --api-url http://api:8000 create --title "$CONTRACT_TITLE" --description "$CONTRACT_DESCRIPTION"; then
    handle_error "Failed to create contract. This could be due to Ollama taking too long to respond."
    # Create a mock contract directly in the database for demo purposes
    echo -e "${YELLOW}Creating a mock contract for demo purposes...${NC}"
    docker compose exec -T api python -c "import asyncio, sqlite3; conn = sqlite3.connect('/data/contracts.db'); conn.execute('CREATE TABLE IF NOT EXISTS contracts (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, content TEXT NOT NULL, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)'); conn.execute('INSERT INTO contracts (title, content) VALUES (?, ?)', ('Demo Contract', 'This is a mock contract for demonstration purposes.\n\nIt contains basic terms and conditions.\n\nSigned by both parties.')); conn.commit(); conn.close(); print('Mock contract created successfully!');"
    echo -e "${GREEN}Mock contract created for demo purposes.${NC}"
fi
echo

# List all contracts
echo -e "${YELLOW}Listing all contracts...${NC}"
if ! docker compose exec -T client python api_client.py --api-url http://api:8000 list; then
    handle_error "Failed to list contracts."
    # List contracts directly from the database
    echo -e "${YELLOW}Listing contracts directly from database...${NC}"
    docker compose exec -T api python -c "import sqlite3; conn = sqlite3.connect('/data/contracts.db'); cursor = conn.execute('SELECT id, title FROM contracts'); print('\nAvailable contracts:'); [print(f'ID: {row[0]}, Title: {row[1]}') for row in cursor]; conn.close();"
fi
echo

# Get the first contract ID
CONTRACT_ID=$(docker compose exec -T api python -c "import sqlite3; conn = sqlite3.connect('/data/contracts.db'); cursor = conn.execute('SELECT id FROM contracts LIMIT 1'); row = cursor.fetchone(); print(row[0] if row else 1); conn.close();")

# Check if we got a valid contract ID
if [ -z "$CONTRACT_ID" ] || ! [[ "$CONTRACT_ID" =~ ^[0-9]+$ ]]; then
    echo -e "${YELLOW}No valid contract ID found. Using ID 1 as fallback.${NC}"
    CONTRACT_ID=1
fi

# Refine the contract
echo -e "${YELLOW}Refining contract ID ${GREEN}$CONTRACT_ID${NC}"
echo -e "${YELLOW}This may take some time as the LLM refines the contract...${NC}"
REFINEMENT_PROMPT="Please add a termination clause."
if ! docker compose exec -T client python api_client.py --api-url http://api:8000 refine --id "$CONTRACT_ID" --prompt "$REFINEMENT_PROMPT"; then
    handle_error "Failed to refine contract. This could be due to Ollama taking too long to respond."
    # Create a mock refined contract
    echo -e "${YELLOW}Creating a mock refined contract for demo purposes...${NC}"
    docker compose exec -T api python -c "import sqlite3; conn = sqlite3.connect('/data/contracts.db'); cursor = conn.execute('SELECT title, content FROM contracts WHERE id = ?', (1,)); row = cursor.fetchone(); title, content = row if row else ('Demo Contract', 'Sample content'); refined_title = title + ' (Refined)'; refined_content = content + '\n\nTERMINATION CLAUSE:\nEither party may terminate this agreement with 30 days written notice.'; conn.execute('INSERT INTO contracts (title, content) VALUES (?, ?)', (refined_title, refined_content)); conn.commit(); cursor = conn.execute('SELECT id, title FROM contracts ORDER BY id DESC LIMIT 1'); row = cursor.fetchone(); print(f'\nContract refined successfully:\nNew ID: {row[0]}\nNew Title: {row[1]}\n\nRefined Content:\n{refined_content}'); conn.close()"

fi
echo

echo -e "${BLUE}=== Demo Complete ===${NC}"
