"""
Punto de entrada principal de la aplicación Task Manager Simulator.
"""
import sys
import logging

from .config.settings import setup_logging, settings
from .config.constants import APP_NAME, APP_VERSION


def main():
    """Función principal de la aplicación."""
    # Configurar logging
    setup_logging(debug=settings.debug_mode)

    logger = logging.getLogger(__name__)
    logger.info(f"=== Iniciando {APP_NAME} v{APP_VERSION} ===")
    logger.info(f"Ejecutando con privilegios de administrador: {settings.is_admin}")

    # Importar y ejecutar la aplicación
    from .ui.main_window import run_application

    try:
        run_application()
    except Exception as e:
        logger.critical(f"Error fatal en la aplicación: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
