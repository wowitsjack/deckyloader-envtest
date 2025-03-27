"""
Decky Plugin Interface
Defines constants and helper functions for Decky plugins. 
"""

version = "1.0.0"

import logging
from typing import Any

HOME: str
USER: str
DECKY_VERSION: str
DECKY_USER: str
DECKY_USER_HOME: str
DECKY_HOME: str
DECKY_PLUGIN_SETTINGS_DIR: str
DECKY_PLUGIN_RUNTIME_DIR: str
DECKY_PLUGIN_LOG_DIR: str
DECKY_PLUGIN_DIR: str
DECKY_PLUGIN_NAME: str
DECKY_PLUGIN_VERSION: str
DECKY_PLUGIN_AUTHOR: str
DECKY_PLUGIN_LOG: str

def migrate_any(target_dir: str, *files_or_directories: str) -> dict[str, str]:
    return {}

def migrate_settings(*files_or_directories: str) -> dict[str, str]:
    return {}

def migrate_runtime(*files_or_directories: str) -> dict[str, str]:
    return {}

def migrate_logs(*files_or_directories: str) -> dict[str, str]:
    return {}

logger: logging.Logger

async def emit(event: str, *args: Any) -> None:
    pass
