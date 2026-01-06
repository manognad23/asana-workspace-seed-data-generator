"""
Database connection and utilities for SQLite database.
"""
import sqlite3
import os
from pathlib import Path
from typing import Optional


class Database:
    """Manages SQLite database connection and schema initialization."""
    
    def __init__(self, db_path: str = "output/asana_simulation.sqlite"):
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
        
    def connect(self, recreate: bool = False) -> sqlite3.Connection:
        """Create database connection."""
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        # Remove existing database if recreate is True
        if recreate and os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # Enable column access by name
        return self.conn
    
    def initialize_schema(self):
        """Initialize database schema from schema.sql file."""
        if not self.conn:
            self.connect()
        
        schema_path = Path(__file__).parent.parent.parent / "schema.sql"
        with open(schema_path, 'r', encoding='utf-8') as f:
            schema_sql = f.read()
        
        self.conn.executescript(schema_sql)
        self.conn.commit()
        print("[OK] Database schema initialized")
    
    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query with parameters."""
        if not self.conn:
            self.connect()
        return self.conn.execute(query, params)
    
    def executemany(self, query: str, params_list: list) -> sqlite3.Cursor:
        """Execute a query multiple times with different parameters."""
        if not self.conn:
            self.connect()
        return self.conn.executemany(query, params_list)
    
    def commit(self):
        """Commit current transaction."""
        if self.conn:
            self.conn.commit()
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
