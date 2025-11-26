"""Configuration management for GoodBoy.AI."""
import json
from pathlib import Path
from typing import Any, Optional
from datetime import datetime

DEFAULT_CONFIG = {
    "engine": "local",
    "model_path": "models/qwen2.5-7b-instruct-q5_k_m-00001-of-00002.gguf",
    "cloud_api_base": "http://127.0.0.1:8000",
    "max_tokens": 512,
    "temperature": 0.6,
    "user_name": "Mayor",
    "theme": "dark",
    "auto_save": True,
    "memory_retention_days": 30,
    "enable_mini_bots": True,
    "enable_evolution": True,
    "log_level": "INFO",
    "api_port": 8000,
    "dashboard_port": 7860
}


class ConfigManager:
    """Manages application configuration."""
    
    def __init__(self, config_path: Path = None):
        self.config_path = config_path or Path("data/GoodBoy_config.json")
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load config from file or create default."""
        if self.config_path.exists():
            try:
                with open(self.config_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults for any missing keys
                    return {**DEFAULT_CONFIG, **loaded}
            except Exception:
                pass
        
        # Save default config
        self._save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()
    
    def _save_config(self, config: dict):
        """Save config to file."""
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a config value."""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set a config value."""
        self.config[key] = value
        self._save_config(self.config)
    
    def update(self, updates: dict):
        """Update multiple config values."""
        self.config.update(updates)
        self._save_config(self.config)
    
    def reset_to_defaults(self):
        """Reset config to defaults."""
        self.config = DEFAULT_CONFIG.copy()
        self._save_config(self.config)
    
    def get_all(self) -> dict:
        """Get all config values."""
        return self.config.copy()
    
    def export_config(self, export_path: Path) -> bool:
        """Export config to a file."""
        try:
            with open(export_path, 'w') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception:
            return False
    
    def import_config(self, import_path: Path) -> bool:
        """Import config from a file."""
        try:
            with open(import_path, 'r') as f:
                imported = json.load(f)
            self.config = {**DEFAULT_CONFIG, **imported}
            self._save_config(self.config)
            return True
        except Exception:
            return False
