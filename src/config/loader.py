import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict

class ConfigLoader:
    _instance = None
    _config: Dict[str, Any] = {}
    _user_dir: Path = Path.home() / ".GenWKT"
    _config_path: Path = _user_dir / "settings.json"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigLoader, cls).__new__(cls)
            cls._instance._init_user_dir()
            cls._instance._load_config()
        return cls._instance

    def _init_user_dir(self):
        """Initialize user directory and default config if needed."""
        try:
            if not self._user_dir.exists():
                self._user_dir.mkdir(parents=True, exist_ok=True)
                # print(f"Created user directory at {self._user_dir}", file=sys.stderr)

            if not self._config_path.exists():
                # Try to copy from app dir if exists, else create default
                default_config_path = Path("config/settings.json")
                if default_config_path.exists():
                    shutil.copy(default_config_path, self._config_path)
                    # print(f"Copied default config to {self._config_path}", file=sys.stderr)
                else:
                    # Create minimal default config
                    default_config = {
                        "app": {"name": "GenWKT", "version": "2.0.0", "theme": "dark_theme.qss"},
                        "logging": {"level": "DEBUG", "file": "logs/app.log", "rotation": "10 MB"}
                    }
                    with open(self._config_path, "w", encoding="utf-8") as f:
                        json.dump(default_config, f, indent=4)
                    # print(f"Created new default config at {self._config_path}", file=sys.stderr)
        except Exception as e:
            # Fallback to local dir if permission denied etc.
            print(f"Failed to init user dir: {e}", file=sys.stderr)
            self._config_path = Path("config/settings.json")

    def _load_config(self):
        """Load configuration from JSON file."""
        if not self._config_path.exists():
             # Fallback
             self._config_path = Path("config/settings.json")

        if not self._config_path.exists():
            print("Configuration file not found.", file=sys.stderr)
            return
        
        try:
            with open(self._config_path, "r", encoding="utf-8") as f:
                self._config = json.load(f)
            # print(f"Loaded configuration from {self._config_path}", file=sys.stderr)
        except Exception as e:
            print(f"Failed to load configuration: {e}", file=sys.stderr)

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value by key (dot notation supported)."""
        keys = key.split(".")
        value = self._config
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            return default
    
    @property
    def user_dir(self) -> Path:
        return self._user_dir

# Global instance
config = ConfigLoader()
