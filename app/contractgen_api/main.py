from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os
from typing import List, Optional

# Import local modules
from . import db
from . import llm

app = FastAPI(title="Contract Generation API")


class Contract(BaseModel):
    id: Optional[int] = None
    title: str
    content: str


class ContractRequest(BaseModel):
    title: str
    description: str


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
