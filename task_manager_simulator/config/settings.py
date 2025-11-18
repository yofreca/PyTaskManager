"""
Configuraciones globales de la aplicación Task Manager Simulator.
"""
import os
import sys
import logging
from pathlib import Path
from typing import Dict, Any

# Rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent
APP_ROOT = Path(__file__).parent.parent
RESOURCES_DIR = APP_ROOT / "resources"
ICONS_DIR = RESOURCES_DIR / "icons"
STYLES_DIR = RESOURCES_DIR / "styles"
IMAGES_DIR = RESOURCES_DIR / "images"

# Configuración de logging
LOG_LEVEL = logging.INFO
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = PROJECT_ROOT / "task_manager.log"

# Configuración de la aplicación
class AppSettings:
    """Configuraciones de la aplicación."""

    def __init__(self):
        self.debug_mode: bool = False
        self.auto_refresh: bool = True
        self.show_system_processes: bool = True
        self.show_user_processes: bool = True
        self.update_interval: int = 1000  # ms
        self.theme: str = "light"  # "light" o "dark"
        self.language: str = "es"  # "es" o "en"

        # Preferencias de visualización
        self.graph_history_length: int = 60  # segundos
        self.cpu_graph_visible: bool = True
        self.memory_graph_visible: bool = True
        self.disk_graph_visible: bool = False
        self.network_graph_visible: bool = False

        # Columnas visibles por defecto en tabla de procesos
        self.visible_columns: list = [
            "name",
            "pid",
            "status",
            "cpu_percent",
            "memory_percent"
        ]

        # Ordenamiento por defecto
        self.default_sort_column: str = "cpu_percent"
        self.default_sort_order: str = "desc"  # "asc" o "desc"

        # Privilegios
        self.is_admin: bool = self._check_admin_privileges()

    def _check_admin_privileges(self) -> bool:
        """Verifica si la aplicación se está ejecutando con privilegios de administrador."""
        try:
            if sys.platform == 'win32':
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    def to_dict(self) -> Dict[str, Any]:
        """Convierte la configuración a diccionario."""
        return {
            "debug_mode": self.debug_mode,
            "auto_refresh": self.auto_refresh,
            "show_system_processes": self.show_system_processes,
            "show_user_processes": self.show_user_processes,
            "update_interval": self.update_interval,
            "theme": self.theme,
            "language": self.language,
            "graph_history_length": self.graph_history_length,
            "cpu_graph_visible": self.cpu_graph_visible,
            "memory_graph_visible": self.memory_graph_visible,
            "disk_graph_visible": self.disk_graph_visible,
            "network_graph_visible": self.network_graph_visible,
            "visible_columns": self.visible_columns,
            "default_sort_column": self.default_sort_column,
            "default_sort_order": self.default_sort_order,
        }

    def from_dict(self, config: Dict[str, Any]) -> None:
        """Carga la configuración desde un diccionario."""
        for key, value in config.items():
            if hasattr(self, key):
                setattr(self, key, value)


# Instancia global de configuración
settings = AppSettings()


def setup_logging(debug: bool = False) -> None:
    """
    Configura el sistema de logging.

    Args:
        debug: Si True, establece nivel DEBUG, sino INFO
    """
    level = logging.DEBUG if debug else LOG_LEVEL

    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.FileHandler(LOG_FILE, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

    # Ajustar nivel de loggers de librerías externas
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)


def get_resource_path(resource_type: str, filename: str) -> Path:
    """
    Obtiene la ruta completa a un archivo de recursos.

    Args:
        resource_type: Tipo de recurso ("icons", "styles", "images")
        filename: Nombre del archivo

    Returns:
        Path al archivo de recurso
    """
    resource_dirs = {
        "icons": ICONS_DIR,
        "styles": STYLES_DIR,
        "images": IMAGES_DIR
    }

    base_dir = resource_dirs.get(resource_type, RESOURCES_DIR)
    return base_dir / filename
