"""Configuration loading for the Ollama pipeline."""

import os
import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    'models': {'default': 'llama3.2:1b', 'classifier': 'llama3.2:1b'},
    'model_assignments': {},
    'prompts': {},
    'thresholds': {'max_response_time': 60, 'min_response_length': 50},
    'cache': {'enabled': True},
}


def load_config(path='config.yaml'):
    """Load configuration from YAML file with defaults."""
    config = dict(DEFAULT_CONFIG)

    config_path = Path(path)
    if config_path.exists():
        with open(config_path) as f:
            file_config = yaml.safe_load(f) or {}
        for key, value in file_config.items():
            config[key] = value
    else:
        print(f"Config file not found at {path}, using defaults")

    if os.getenv('OLLAMA_MODEL'):
        config['models']['default'] = os.getenv('OLLAMA_MODEL')

    if os.getenv('OLLAMA_TIMEOUT'):
        config['thresholds']['max_response_time'] = int(os.getenv('OLLAMA_TIMEOUT'))

    required = ['models', 'model_assignments', 'thresholds']
    for field in required:
        if field not in config:
            raise ValueError(f"Missing required config field: {field}")

    return config
