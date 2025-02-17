from jinja2 import Environment, FileSystemLoader
import os

class StrategyGenerator:
    """Generates FreqTrade strategy files from templates"""
    def __init__(self, template_dir: str = "templates"):
        pass

# src/state_manager.py
import sqlite3
from dataclasses import asdict
import json

class StateManager:
    """Manages persistent state storage"""
    def __init__(self, db_path: str = "freqtrade_ai.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS strategies (
                    name TEXT PRIMARY KEY,
                    code TEXT,
                    description TEXT,
                    performance JSON,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

    def save_state(self, state: SystemState):
        with sqlite3.connect(self.db_path) as conn:
            state_dict = asdict(state)
            for key, value in state_dict.items():
                if isinstance(value, (dict, list)):
                    value = json.dumps(value)
                conn.execute(
                    "INSERT OR REPLACE INTO state (key, value) VALUES (?, ?)",
                    (key, str(value))
                )

    def load_state(self) -> Dict[str, Any]:
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("SELECT key, value FROM state")
            return {key: json.loads(value) if value.startswith('{') or value.startswith('[') else value 
                    for key, value in cursor.fetchall()}

