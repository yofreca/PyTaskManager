"""
Ventana principal de la aplicación.
"""
from PyQt6.QtWidgets import (QMainWindow, QTabWidget, QStatusBar, QMessageBox,
                              QWidget, QVBoxLayout, QLabel)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction
import logging

from ..core.process_manager import ProcessManager
from ..core.performance_monitor import PerformanceMonitor
from ..config.settings import settings
from ..config.constants import (WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT,
                                WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)
from .tabs.processes_tab import ProcessesTab
from .tabs.performance_tab import PerformanceTab


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """Ventana principal del Administrador de Tareas."""

    def __init__(self):
        super().__init__()

        # Inicializar gestores
        self.process_manager = ProcessManager()
        self.performance_monitor = PerformanceMonitor()

        self._init_ui()
        self._create_menu_bar()
        self._create_status_bar()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle(f"{settings.APP_NAME} v{settings.APP_VERSION}")
        self.setGeometry(100, 100, WINDOW_DEFAULT_WIDTH, WINDOW_DEFAULT_HEIGHT)
        self.setMinimumSize(WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT)

        # Widget central con pestañas
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Crear pestañas
        self._create_tabs()

    def _create_tabs(self):
        """Crea las pestañas de la aplicación."""
        # Pestaña de Procesos
        self.processes_tab = ProcessesTab(self.process_manager)
        self.tabs.addTab(self.processes_tab, "Procesos")

        # Pestaña de Rendimiento
        self.performance_tab = PerformanceTab(self.performance_monitor)
        self.tabs.addTab(self.performance_tab, "Rendimiento")

        # Pestaña de Detalles (placeholder)
        details_placeholder = self._create_placeholder("Detalles")
        self.tabs.addTab(details_placeholder, "Detalles")

        # Pestaña de Servicios (placeholder)
        if settings.IS_WINDOWS:
            services_placeholder = self._create_placeholder("Servicios")
            self.tabs.addTab(services_placeholder, "Servicios")

        # Pestaña de Inicio (placeholder)
        if settings.IS_WINDOWS:
            startup_placeholder = self._create_placeholder("Inicio")
            self.tabs.addTab(startup_placeholder, "Inicio")

    def _create_placeholder(self, text: str) -> QWidget:
        """Crea un widget placeholder para pestañas no implementadas."""
        widget = QWidget()
        layout = QVBoxLayout()
        label = QLabel(f"Pestaña '{text}' - En desarrollo")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 18px; color: gray;")
        layout.addWidget(label)
        widget.setLayout(layout)
        return widget

    def _create_menu_bar(self):
        """Crea la barra de menú."""
        menubar = self.menuBar()

        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")

        refresh_action = QAction("&Actualizar", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self._refresh_all)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        exit_action = QAction("&Salir", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menú Ver
        view_menu = menubar.addMenu("&Ver")

        theme_action = QAction("Alternar &Tema", self)
        theme_action.triggered.connect(self._toggle_theme)
        view_menu.addAction(theme_action)

        # Menú Ayuda
        help_menu = menubar.addMenu("A&yuda")

        about_action = QAction("&Acerca de", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _create_status_bar(self):
        """Crea la barra de estado."""
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

        # Mostrar advertencia si no se ejecuta como administrador
        if not settings.IS_ADMIN:
            self.statusBar.showMessage(
                "⚠ Ejecutando sin privilegios de administrador - "
                "Algunas funciones pueden estar limitadas"
            )
        else:
            self.statusBar.showMessage("Listo")

    def _refresh_all(self):
        """Actualiza todas las pestañas."""
        try:
            current_tab = self.tabs.currentWidget()
            if hasattr(current_tab, 'refresh_processes'):
                current_tab.refresh_processes()
            elif hasattr(current_tab, 'refresh_performance'):
                current_tab.refresh_performance()

            self.statusBar.showMessage("Actualizado", 2000)
        except Exception as e:
            logger.error(f"Error al actualizar: {e}")
            self.statusBar.showMessage("Error al actualizar", 2000)

    def _toggle_theme(self):
        """Alterna entre tema claro y oscuro."""
        settings.toggle_theme()
        QMessageBox.information(
            self,
            "Cambio de tema",
            f"Tema cambiado a: {settings.THEME}\n"
            "Reinicie la aplicación para aplicar los cambios."
        )

    def _show_about(self):
        """Muestra el diálogo Acerca de."""
        QMessageBox.about(
            self,
            f"Acerca de {settings.APP_NAME}",
            f"<h2>{settings.APP_NAME}</h2>"
            f"<p>Versión: {settings.APP_VERSION}</p>"
            f"<p>Simulador del Administrador de Tareas de Windows</p>"
            f"<p>Desarrollado con Python y PyQt6</p>"
            f"<p>Sistema: {'Windows' if settings.IS_WINDOWS else 'Linux/Unix'}</p>"
            f"<p>Privilegios: {'Administrador' if settings.IS_ADMIN else 'Usuario'}</p>"
        )

    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        # Limpiar recursos de las pestañas
        if hasattr(self.processes_tab, 'cleanup'):
            self.processes_tab.cleanup()
        if hasattr(self.performance_tab, 'cleanup'):
            self.performance_tab.cleanup()

        event.accept()
