import sqlite3
import os
import aiosqlite
from typing import List, Dict, Optional, Any

# Get database path from environment variable or use default
DB_PATH = os.environ.get("DB_PATH", "contracts.db")


async def init_db():
    """Initialize the database with required tables"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS contracts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        await db.commit()


async def save_contract(title: str, content: str) -> int:
    """Save a contract to the database and return its ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        cursor = await db.execute(
            "INSERT INTO contracts (title, content) VALUES (?, ?)",
            (title, content)
        )
        await db.commit()
        return cursor.lastrowid


async def get_contract(contract_id: int) -> Optional[Dict[str, Any]]:
    """Get a contract by ID"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT id, title, content FROM contracts WHERE id = ?",
            (contract_id,)
        )
        row = await cursor.fetchone()
        if row:
            return {"id": row["id"], "title": row["title"], "content": row["content"]}
        return None


async def get_all_contracts() -> List[Dict[str, Any]]:
    """Get all contracts"""
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute("SELECT id, title, content FROM contracts")
        rows = await cursor.fetchall()
        return [{"id": row["id"], "title": row["title"], "content": row["content"]} for row in rows]
