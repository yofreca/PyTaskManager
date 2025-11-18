"""
Configuración global de la aplicación.
"""
import os
import sys
from pathlib import Path
from typing import Optional


class Settings:
    """Configuración de la aplicación."""

    def __init__(self):
        # Rutas
        self.BASE_DIR = Path(__file__).parent.parent
        self.RESOURCES_DIR = self.BASE_DIR / 'resources'
        self.ICONS_DIR = self.RESOURCES_DIR / 'icons'
        self.STYLES_DIR = self.RESOURCES_DIR / 'styles'
        self.IMAGES_DIR = self.RESOURCES_DIR / 'images'

        # Aplicación
        self.APP_NAME = "Task Manager Simulator"
        self.APP_VERSION = "0.1.0"
        self.APP_AUTHOR = "PyTaskManager"

        # Sistema
        self.IS_WINDOWS = sys.platform == 'win32'
        self.IS_LINUX = sys.platform.startswith('linux')
        self.IS_MAC = sys.platform == 'darwin'

        # Privilegios
        self.IS_ADMIN = self._check_admin_privileges()

        # Configuración de UI
        self.THEME = 'light'  # 'light' o 'dark'
        self.SHOW_SYSTEM_PROCESSES = True
        self.SHOW_BACKGROUND_PROCESSES = True
        self.AUTO_REFRESH = True

        # Logging
        self.LOG_LEVEL = 'INFO'
        self.LOG_FILE: Optional[Path] = None
        self.LOG_TO_CONSOLE = True

        # Rendimiento
        self.ENABLE_ANIMATIONS = True
        self.ENABLE_CHARTS = True
        self.LOW_PERFORMANCE_MODE = False

    def _check_admin_privileges(self) -> bool:
        """Verifica si la aplicación se ejecuta con privilegios de administrador."""
        try:
            if self.IS_WINDOWS:
                import ctypes
                return ctypes.windll.shell32.IsUserAnAdmin() != 0
            else:
                return os.geteuid() == 0
        except Exception:
            return False

    def enable_dark_theme(self):
        """Habilita el tema oscuro."""
        self.THEME = 'dark'

    def enable_light_theme(self):
        """Habilita el tema claro."""
        self.THEME = 'light'

    def toggle_theme(self):
        """Alterna entre tema claro y oscuro."""
        self.THEME = 'dark' if self.THEME == 'light' else 'light'


# Instancia global de configuración
settings = Settings()
