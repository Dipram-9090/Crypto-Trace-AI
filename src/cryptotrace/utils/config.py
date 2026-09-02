"""
Configuration Loader & Property Manager.
"""

import os
from typing import Dict, Any
from src.cryptotrace.utils.io import load_yaml
from src.cryptotrace.utils.paths import CONFIGS_DIR


class ConfigManager:
    """Loads and exposes application configs (config.yaml, data.yaml, models.yaml, features.yaml)."""

    def __init__(self, configs_path: str = CONFIGS_DIR):
        self.configs_path = configs_path
        self.main_config = load_yaml(os.path.join(configs_path, "config.yaml"))
        self.data_config = load_yaml(os.path.join(configs_path, "data.yaml"))
        self.models_config = load_yaml(os.path.join(configs_path, "models.yaml"))
        self.features_config = load_yaml(os.path.join(configs_path, "features.yaml"))
