import os
import json
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()


class Config:
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.getenv("CONFIG_FILE", "config.json")
        self._config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        default_config = {
            "voyageai": {
                "api_key": os.getenv("VOYAGE_API_KEY"),
                "model": "voyage-code-2",
                "batch_size": 128
            },
            "mongodb": {
                "uri": os.getenv("MONGODB_URI", "mongodb://localhost:27017"),
                "database": "speckit",
                "collection": "specifications",
                "vector_index": "spec_vector_index"
            }
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    file_config = json.load(f)
                    # Merge file config with default config
                    self._merge_configs(default_config, file_config)
            except (json.JSONDecodeError, FileNotFoundError) as e:
                print(f"Warning: Could not load config file {self.config_file}: {e}")
        
        return default_config
    
    def _merge_configs(self, default: Dict[str, Any], override: Dict[str, Any]):
        for key, value in override.items():
            if key in default and isinstance(default[key], dict) and isinstance(value, dict):
                self._merge_configs(default[key], value)
            else:
                default[key] = value
    
    def get_voyageai_config(self) -> Dict[str, Any]:
        return self._config.get("voyageai", {})
    
    def get_mongodb_config(self) -> Dict[str, Any]:
        return self._config.get("mongodb", {})
    
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any):
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def save_config(self) -> bool:
        try:
            # Don't save API keys to file
            config_to_save = self._sanitize_config(self._config)
            with open(self.config_file, 'w') as f:
                json.dump(config_to_save, f, indent=2)
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def _sanitize_config(self, config: Dict[str, Any]) -> Dict[str, Any]:
        sanitized = {}
        for key, value in config.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_config(value)
            elif key == "api_key":
                # Don't save API keys to file
                continue
            else:
                sanitized[key] = value
        return sanitized
    
    def validate_config(self) -> Dict[str, Any]:
        issues = []
        warnings = []
        
        # Validate VoyageAI config
        voyage_config = self.get_voyageai_config()
        if not voyage_config.get("api_key"):
            issues.append("VoyageAI API key not configured. Set VOYAGE_API_KEY environment variable.")
        
        model = voyage_config.get("model", "")
        if not model.startswith("voyage-"):
            warnings.append(f"VoyageAI model '{model}' may not be valid. Consider using 'voyage-code-2'.")
        
        # Validate MongoDB config
        mongodb_config = self.get_mongodb_config()
        uri = mongodb_config.get("uri", "")
        if not uri:
            issues.append("MongoDB URI not configured. Set MONGODB_URI environment variable.")
        
        if not mongodb_config.get("database"):
            issues.append("MongoDB database name not configured.")
        
        if not mongodb_config.get("collection"):
            issues.append("MongoDB collection name not configured.")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def get_all_config(self) -> Dict[str, Any]:
        return self._config.copy()


# Global config instance
config = Config()