from jinja2 import Environment, FileSystemLoader
import os

class StrategyGenerator:
    """Generates FreqTrade strategy files from templates"""
    def __init__(self, template_dir: str = "templates"):
        self.env = Environment(loader=FileSystemLoader(template_dir))
        self.template = self.env.get_template("strategy.j2")

    def generate_strategy(self, params: Dict[str, Any]) -> str:
        """Generate strategy code from template and parameters"""
        return self.template.render(**params)

    async def create_strategy_from_description(self, description: str, claude) -> str:
        """Use Claude to create strategy parameters from description"""
        prompt = f"""
        Create a FreqTrade strategy based on this description: {description}
        Return only a JSON object with these parameters:
        {{
            "strategy_name": "string",
            "buy_indicators": ["list of indicators"],
            "sell_indicators": ["list of indicators"],
            "timeframe": "string",
            "minimal_roi": {{"time_in_minutes": percentage}},
            "stoploss": -float
        }}
        """
        
        response = await claude.messages.create(
            model="claude-3-opus-20240229",
            messages=[{"role": "user", "content": prompt}]
        )
        
        try:
            params = json.loads(response.content[0].text)
            return self.generate_strategy(params)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON from Claude: {e}")

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

