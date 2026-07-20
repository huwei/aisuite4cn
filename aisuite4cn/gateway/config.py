"""Config file loader for aisuite4cn Gateway."""

import json
from pathlib import Path
from typing import Any, Dict, Optional

# 默认配置文件路径
DEFAULT_CONFIG_PATH = Path.home() / ".aisuite4cn" / "config.yaml"


def load_config(config_path: str) -> Dict[str, Any]:
    """Load gateway configuration from a YAML or JSON file.

    Expected format:
        providers:
          deepseek:
            api_key: "sk-xxx"
          qwen:
            api_key: "sk-yyy"

    Args:
        config_path: Path to the configuration file (.yaml, .yml, or .json).

    Returns:
        Dict with provider configurations.

    Raises:
        FileNotFoundError: If the config file does not exist.
        ValueError: If the file format is unsupported or invalid.
    """
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    content = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()

    if suffix in (".yaml", ".yml"):
        try:
            import yaml
            config = yaml.safe_load(content)
        except ImportError:
            raise ValueError(
                "PyYAML is required for YAML config files. "
                "Install it with: pip install pyyaml"
            )
    elif suffix == ".json":
        config = json.loads(content)
    else:
        raise ValueError(
            f"Unsupported config file format: {suffix}. "
            "Use .yaml, .yml, or .json"
        )

    if not isinstance(config, dict):
        raise ValueError("Config file must contain a top-level mapping.")

    return config


def get_provider_configs(config_path: Optional[str] = None) -> Dict[str, Any]:
    """Get provider configs from a file, or from default location, or empty dict.

    Resolution order:
    1. Explicit config_path argument if provided
    2. DEFAULT_CONFIG_PATH (~/.aisuite4cn/config.yaml) if it exists
    3. Empty dict

    Args:
        config_path: Optional explicit path to a config file.

    Returns:
        Provider configurations dict suitable for AsyncClient.
    """
    # 1. Use explicit path if given
    if config_path:
        config = load_config(config_path)
        providers = config.get("providers") or {}
        if not isinstance(providers, dict):
            raise ValueError("'providers' must be a mapping of provider configs.")
        return providers

    # 2. Fall back to default location
    if DEFAULT_CONFIG_PATH.exists():
        config = load_config(str(DEFAULT_CONFIG_PATH))
        providers = config.get("providers") or {}
        if not isinstance(providers, dict):
            raise ValueError("'providers' must be a mapping of provider configs.")
        return providers

    # 3. No config available
    return {}
