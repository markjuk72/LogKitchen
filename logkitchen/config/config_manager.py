"""
Configuration management for LogKitchen
"""

import os
import yaml
from pathlib import Path
from typing import Any, Dict, Optional


class ConfigManager:
    """Manage configuration loading and access"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration manager

        Args:
            config_path: Path to configuration file. If None, uses default config.
        """
        self.config_path = config_path
        self.config = self._load_config()

    def _get_default_config_path(self) -> str:
        """Get the path to the default configuration file"""
        # Get the package root directory
        package_root = Path(__file__).parent.parent.parent
        config_file = package_root / "config" / "default_config.yaml"

        if not config_file.exists():
            raise FileNotFoundError(f"Default configuration file not found: {config_file}")

        return str(config_file)

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if self.config_path is None:
            self.config_path = self._get_default_config_path()

        try:
            with open(self.config_path, 'r') as f:
                config = yaml.safe_load(f)
                return config if config else {}
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {self.config_path}")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")

    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a configuration value using dot notation

        Args:
            key_path: Dot-separated path to config value (e.g., 'global.seed')
            default: Default value if key not found

        Returns:
            Configuration value or default
        """
        keys = key_path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    def get_section(self, section: str) -> Dict[str, Any]:
        """
        Get an entire configuration section

        Args:
            section: Section name (e.g., 'syslog', 'network')

        Returns:
            Configuration section as dictionary
        """
        return self.get(section, {})

    def reload(self):
        """Reload configuration from file"""
        self.config = self._load_config()

    def save(self, path: Optional[str] = None):
        """
        Save current configuration to file

        Args:
            path: Path to save to. If None, uses current config_path
        """
        save_path = path or self.config_path

        with open(save_path, 'w') as f:
            yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)

    def update(self, key_path: str, value: Any):
        """
        Update a configuration value using dot notation

        Args:
            key_path: Dot-separated path to config value
            value: New value to set
        """
        keys = key_path.split('.')
        config = self.config

        # Navigate to the parent of the target key
        for key in keys[:-1]:
            if key not in config:
                config[key] = {}
            config = config[key]

        # Set the value
        config[keys[-1]] = value

    def __repr__(self) -> str:
        return f"ConfigManager(config_path='{self.config_path}')"


# Global configuration instance
_global_config: Optional[ConfigManager] = None


def get_config(config_path: Optional[str] = None) -> ConfigManager:
    """
    Get the global configuration instance

    Args:
        config_path: Path to configuration file (only used on first call)

    Returns:
        ConfigManager instance
    """
    global _global_config

    if _global_config is None:
        _global_config = ConfigManager(config_path)

    return _global_config


def reload_config():
    """Reload the global configuration"""
    global _global_config

    if _global_config is not None:
        _global_config.reload()
