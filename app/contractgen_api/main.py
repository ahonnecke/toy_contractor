from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import asyncio
from typing import List, Optional

# Import local modules
from . import db
from . import llm

app = FastAPI(title="Contract Generation API")


@app.on_event("startup")
async def startup_event():
    """Initialize the database on startup"""
    print("Initializing database...")
    await db.init_db()
    print("Database initialized successfully.")

    # Just check if Ollama is reachable without generating text
    print("Checking if Ollama service is reachable...")
    try:
        # This will just ping Ollama without generating text
        await llm.check_ollama_connection()
        print("Ollama service is reachable.")
    except Exception as e:
        print(f"Warning: Ollama connection check failed: {e}")
        print(
            "API will continue to run, but contract generation may not work properly."
        )

    # Start a background task to warm up the model
    asyncio.create_task(warm_up_model())


async def warm_up_model():
    """Warm up the LLM model in the background"""
    print("Warming up LLM model in the background...")
    try:
        # Use a very simple prompt to warm up the model
        await llm.generate_contract("Test")
        print("Model warm-up complete.")
    except Exception as e:
        print(f"Model warm-up failed: {e}")


class Contract(BaseModel):
    id: Optional[int] = None
    title: str
    content: str


class ContractRequest(BaseModel):
    title: str
    description: str


class RefinementRequest(BaseModel):
    contract_id: int
    refinement_instructions: str


@app.get("/")
async def root():
    return {"message": "Contract Generation API is running"}


@app.post("/contracts/", response_model=Contract)
async def create_contract(request: ContractRequest):
    """Generate a contract based on the provided description"""
    try:
        # Use LLM to generate contract content
        content = await llm.generate_contract(request.description)

        # Save to database
        contract_id = await db.save_contract(request.title, content)

        return Contract(id=contract_id, title=request.title, content=content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contracts/", response_model=List[Contract])
async def list_contracts():
    """List all contracts"""
    try:
        contracts = await db.get_all_contracts()
        return contracts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/contracts/{contract_id}", response_model=Contract)
async def get_contract(contract_id: int):
    """Get a specific contract by ID"""
    try:
        contract = await db.get_contract(contract_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return contract
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


@app.post("/contracts/refine/", response_model=Contract)
async def refine_contract(request: RefinementRequest):
    """Refine an existing contract based on the provided instructions"""
    try:
        # Get the existing contract
        existing_contract = await db.get_contract(request.contract_id)
        if not existing_contract:
            raise HTTPException(status_code=404, detail="Contract not found")

        # Create refinement prompt
        refinement_prompt = f"""Original Contract:
{existing_contract["content"]}

Refinement Instructions:
{request.refinement_instructions}

Please provide a complete, refined version of this contract that incorporates the refinement instructions.
"""

        # Generate refined content
        refined_content = await llm.generate_contract(refinement_prompt)

        # Save refined contract
        refined_title = f"{existing_contract['title']} (Refined)"
        contract_id = await db.save_contract(refined_title, refined_content)

        return Contract(id=contract_id, title=refined_title, content=refined_content)
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=500, detail=str(e))
