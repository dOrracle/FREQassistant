import logging
from anthropic import Anthropic
import json
import os
import re
from typing import Dict, Any, Optional, Union

logger = logging.getLogger(__name__)

class FreqtradeConfigManager:
    def __init__(self, api_key: str, config_path: str = "config.json"):
        self.claude = Anthropic(api_key=api_key)
        self.config_path = os.path.abspath(config_path)
        self.config = None
        
        # Ensure config directory exists
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)

    def read_config(self) -> Optional[Dict[str, Any]]:
        """Reads the configuration file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = json.load(f)
                return self.config
        except FileNotFoundError:
            logger.error(f"Config file not found at {self.config_path}")
            return None
        except json.JSONDecodeError:
            logger.error(f"Invalid JSON in config file at {self.config_path}")
            return None
        except Exception as e:
            logger.error(f"Error reading config file: {e}")
            return None

    def write_config(self, config: Dict[str, Any]) -> bool:
        """Writes the configuration file, creating a backup."""
        if config is None:
            logger.error("Cannot write None to config file.")
            return False

        backup_path = f"{self.config_path}.backup"
        try:
            if os.path.exists(self.config_path):
                os.replace(self.config_path, backup_path)

            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=4)
            os.chmod(self.config_path, 0o600)  # Secure file permissions
            return True
        except Exception as e:
            logger.error(f"Error writing config file: {e}")
            if os.path.exists(backup_path):
                os.replace(backup_path, self.config_path)
            return False

    def validate_config(self, config: Dict[str, Any]) -> bool:
        required_fields = ['exchange', 'stake_currency', 'max_open_trades']
        return all(field in config for field in required_fields)

    def validate_claude_config(self, config: Dict[str, Any]) -> bool:
        required_fields = {
            'anthropic': ['api_key'],
            'claude_integration': ['model_version', 'max_tokens', 'temperature']
        }
        
        try:
            for section, fields in required_fields.items():
                if section not in config:
                    logger.error(f"Missing config section: {section}")
                    return False
                for field in fields:
                    if field not in config[section]:
                        logger.error(f"Missing field in {section}: {field}")
                        return False
            return True
        except Exception as e:
            logger.error(f"Config validation error: {str(e)}")
            return False

    def _validate_and_normalize_config(self, config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Validates and normalizes configuration."""
        try:
            if not self.validate_config(config):
                logger.error("Invalid FreqTrade configuration")
                return None
                
            if not self.validate_claude_config(config):
                logger.error("Invalid Claude configuration")
                return None
                
            return config
        except Exception as e:
            logger.error(f"Config validation error: {e}")
            return None

    async def update_config(self, request: str) -> Union[str, Dict[str, Any]]:
        """Updates the configuration based on a user request."""
        current_config = self.read_config()
        if current_config is None:
            return "Error: Could not read current configuration."

        claude_config = current_config.get('claude_integration', {})
        
        prompt = f"""
        Update the configuration based on the user's request.
        Provide ONLY the modified JSON configuration.

        Current config:
        ```json
        {json.dumps(current_config, indent=4)}
        ```

        User request: {request}
        """
        try:
            response = await self.claude.messages.create(
                model=claude_config.get('model_version', 'claude-3-5-sonnet-20241022'),
                max_tokens=claude_config.get('max_tokens', 4096),
                temperature=claude_config.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )

            response_text = response.content[0].text
            match = re.search(r"``[json\n(.*)\n](http://_vscodecontentref_/1)``", response_text, re.DOTALL)
            if match:
                json_string = match.group(1)
            else:
                json_string = response_text

            try:
                new_config = json.loads(json_string)
                if not isinstance(new_config, dict):
                    logger.error("Invalid configuration format received")
                    return "Error: Invalid configuration format."

                if self.write_config(new_config):
                    logger.info("Configuration updated successfully")
                    return "Config updated successfully."
                else:
                    logger.error("Failed to write updated configuration")
                    return "Error: Failed to write updated configuration."

            except json.JSONDecodeError as e:
                logger.error(f"Error parsing configuration: {e}")
                return f"Error parsing configuration: {e}"

        except Exception as e:
            logger.error(f"Error updating config: {e}")
            return f"Error updating config: {e}"

    async def update_freqai_config(self, params: Dict[str, Any]) -> str:
        """Updates the FreqAI section of the configuration file."""
        config = self.read_config()
        if config:
            try:
                config['freqai'] = params
                if self.write_config(config):
                    return "FreqAI configuration updated successfully."
                return "Error writing configuration."
            except Exception as e:
                return f"Error updating config: {e}"
        return "Configuration not loaded."