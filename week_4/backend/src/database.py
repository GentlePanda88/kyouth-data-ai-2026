import json
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "sentinel.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create tables if they don't exist."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS consensus_cache (
                ticker TEXT PRIMARY KEY,
                company_name TEXT NOT NULL,
                result_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


def save_consensus(ticker: str, company_name: str, result: dict) -> None:
    """Save a consensus result to the cache."""
    with get_connection() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO consensus_cache
                (ticker, company_name, result_json)
            VALUES (?, ?, ?)
            """,
            (ticker, company_name, json.dumps(result)),
        )
        conn.commit()


def get_consensus(ticker: str) -> dict | None:
    """Retrieve a cached consensus result for a ticker."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT result_json FROM consensus_cache WHERE ticker = ?",
            (ticker,),
        ).fetchone()

    if row:
        return json.loads(row["result_json"])
    return None


def clear_consensus(ticker: str) -> None:
    """Delete cached result for a ticker to force a fresh analysis."""
    with get_connection() as conn:
        conn.execute(
            "DELETE FROM consensus_cache WHERE ticker = ?",
            (ticker,),
        )
        conn.commit()