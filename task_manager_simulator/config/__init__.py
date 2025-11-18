"""
Configuración de la aplicación.
"""

from .settings import settings, setup_logging, get_resource_path
from .constants import (
    APP_NAME,
    APP_VERSION,
    UPDATE_INTERVAL_PROCESSES,
    UPDATE_INTERVAL_CPU,
    UPDATE_INTERVAL_MEMORY,
)

__all__ = [
    "settings",
    "setup_logging",
    "get_resource_path",
    "APP_NAME",
    "APP_VERSION",
    "UPDATE_INTERVAL_PROCESSES",
    "UPDATE_INTERVAL_CPU",
    "UPDATE_INTERVAL_MEMORY",
]
