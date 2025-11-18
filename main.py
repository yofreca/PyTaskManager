#!/usr/bin/env python3
"""
Task Manager Simulator - Punto de entrada principal
Simulador del Administrador de Tareas de Windows en Python
"""
import sys
import logging
from PyQt6.QtWidgets import QApplication

from task_manager_simulator.ui.main_window import MainWindow
from task_manager_simulator.config.settings import settings


def setup_logging():
    """Configura el sistema de logging."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL),
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Función principal."""
    # Configurar logging
    setup_logging()
    logger = logging.getLogger(__name__)

    logger.info(f"Iniciando {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Sistema operativo: {sys.platform}")
    logger.info(f"Privilegios de administrador: {settings.IS_ADMIN}")

    # Advertencia si no se ejecuta como administrador
    if not settings.IS_ADMIN:
        logger.warning(
            "La aplicación no se está ejecutando con privilegios de administrador. "
            "Algunas funcionalidades pueden estar limitadas."
        )

    # Crear aplicación Qt
    app = QApplication(sys.argv)
    app.setApplicationName(settings.APP_NAME)
    app.setApplicationVersion(settings.APP_VERSION)

    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()

    logger.info("Aplicación iniciada correctamente")

    # Ejecutar aplicación
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
