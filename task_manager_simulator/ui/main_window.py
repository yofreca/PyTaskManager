"""
Ventana principal de la aplicación Task Manager Simulator.
"""
import sys
import logging
from PyQt6.QtWidgets import (
    QMainWindow,
    QTabWidget,
    QWidget,
    QVBoxLayout,
    QStatusBar,
    QMenuBar,
    QMenu,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction

from ..config.settings import settings, APP_NAME, APP_VERSION
from ..config.constants import UPDATE_INTERVAL_PROCESSES
from ..core.process_manager import ProcessManager
from ..core.performance_monitor import PerformanceMonitor
from ..core.service_manager import ServiceManager
from .tabs.processes_tab import ProcessesTab
from .tabs.performance_tab import PerformanceTab
from .tabs.details_tab import DetailsTab
from .tabs.services_tab import ServicesTab


logger = logging.getLogger(__name__)


class MainWindow(QMainWindow):
    """
    Ventana principal de la aplicación.

    Contiene el sistema de pestañas y coordina todos los módulos.
    """

    def __init__(self):
        """Inicializa la ventana principal."""
        super().__init__()

        # Managers
        self.process_manager = ProcessManager()
        self.performance_monitor = PerformanceMonitor()
        self.service_manager = ServiceManager()

        # Timer para actualizaciones
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self._on_update_timer)

        self._init_ui()
        self._init_menu()
        self._init_status_bar()

        # Iniciar actualizaciones automáticas
        if settings.auto_refresh:
            self.start_auto_refresh()

        logger.info("MainWindow inicializada")

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        self.setWindowTitle(f"{APP_NAME} v{APP_VERSION}")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        # Widget central con tabs
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Layout principal
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)

        # Sistema de pestañas
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)

        # Crear pestañas
        self._create_tabs()

    def _create_tabs(self):
        """Crea las pestañas de la aplicación."""
        # Pestaña de Procesos
        self.processes_tab = ProcessesTab()
        self.processes_tab.process_killed.connect(self._on_process_killed)
        self.processes_tab.refresh_requested.connect(self.refresh_all)
        self.tab_widget.addTab(self.processes_tab, "Processes")

        # Pestaña de Rendimiento
        self.performance_tab = PerformanceTab()
        self.tab_widget.addTab(self.performance_tab, "Performance")

        # Pestaña de Detalles
        self.details_tab = DetailsTab()
        self.details_tab.process_killed.connect(self._on_process_killed)
        self.details_tab.refresh_requested.connect(self.refresh_all)
        self.tab_widget.addTab(self.details_tab, "Details")

        # Pestaña de Servicios (solo en Windows)
        if settings.is_windows or self.service_manager.is_available:
            self.services_tab = ServicesTab()
            self.services_tab.refresh_requested.connect(self.refresh_all)
            self.tab_widget.addTab(self.services_tab, "Services")

    def _init_menu(self):
        """Inicializa el menú de la aplicación."""
        menubar = self.menuBar()

        # Menú File
        file_menu = menubar.addMenu("&File")

        # Acción: Refresh
        refresh_action = QAction("&Refresh", self)
        refresh_action.setShortcut("F5")
        refresh_action.triggered.connect(self.refresh_all)
        file_menu.addAction(refresh_action)

        file_menu.addSeparator()

        # Acción: Exit
        exit_action = QAction("E&xit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Menú View
        view_menu = menubar.addMenu("&View")

        # Acción: Auto Refresh
        self.auto_refresh_action = QAction("Auto Refresh", self)
        self.auto_refresh_action.setCheckable(True)
        self.auto_refresh_action.setChecked(settings.auto_refresh)
        self.auto_refresh_action.triggered.connect(self._toggle_auto_refresh)
        view_menu.addAction(self.auto_refresh_action)

        view_menu.addSeparator()

        # Acción: System Processes
        self.show_system_action = QAction("Show System Processes", self)
        self.show_system_action.setCheckable(True)
        self.show_system_action.setChecked(settings.show_system_processes)
        self.show_system_action.triggered.connect(self._toggle_system_processes)
        view_menu.addAction(self.show_system_action)

        # Menú Help
        help_menu = menubar.addMenu("&Help")

        # Acción: About
        about_action = QAction("&About", self)
        about_action.triggered.connect(self._show_about_dialog)
        help_menu.addAction(about_action)

    def _init_status_bar(self):
        """Inicializa la barra de estado."""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Mensaje inicial
        if settings.is_admin:
            self.status_bar.showMessage("Running with administrator privileges")
        else:
            self.status_bar.showMessage("Running without administrator privileges - some features may be limited")

    def start_auto_refresh(self):
        """Inicia la actualización automática."""
        self.update_timer.start(UPDATE_INTERVAL_PROCESSES)
        settings.auto_refresh = True
        logger.info("Auto-refresh iniciado")

    def stop_auto_refresh(self):
        """Detiene la actualización automática."""
        self.update_timer.stop()
        settings.auto_refresh = False
        logger.info("Auto-refresh detenido")

    def refresh_all(self):
        """Refresca todos los datos de la aplicación."""
        logger.debug("Refrescando todos los datos...")

        # Actualizar procesos
        processes = self.process_manager.get_all_processes(
            include_system=settings.show_system_processes
        )
        self.processes_tab.update_processes(processes)

        # Actualizar detalles (usa información más detallada)
        self.details_tab.update_processes(processes)

        # Actualizar rendimiento
        performance = self.performance_monitor.get_current_performance()
        self.performance_tab.update_performance(performance)

        # Actualizar servicios (solo en Windows)
        if hasattr(self, 'services_tab') and self.service_manager.is_available:
            services = self.service_manager.get_all_services()
            self.services_tab.update_services(services)

        # Actualizar barra de estado
        current_tab = self.tab_widget.currentIndex()
        tab_name = self.tab_widget.tabText(current_tab)
        self.status_bar.showMessage(f"Refreshed {tab_name}", 2000)

    def _on_update_timer(self):
        """Callback del timer de actualización."""
        self.refresh_all()

    def _on_process_killed(self, pid: int):
        """
        Maneja la solicitud de terminar un proceso.

        Args:
            pid: Process ID a terminar
        """
        success = self.process_manager.kill_process(pid, force=False)

        if success:
            self.status_bar.showMessage(f"Process {pid} terminated successfully", 3000)
            # Refrescar inmediatamente
            self.refresh_all()
        else:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to terminate process {pid}. Access denied or process no longer exists."
            )

    def _toggle_auto_refresh(self, checked: bool):
        """Alterna el auto-refresh."""
        if checked:
            self.start_auto_refresh()
        else:
            self.stop_auto_refresh()

    def _toggle_system_processes(self, checked: bool):
        """Alterna la visualización de procesos del sistema."""
        settings.show_system_processes = checked
        self.refresh_all()
        logger.info(f"Show system processes: {checked}")

    def _show_about_dialog(self):
        """Muestra el diálogo About."""
        about_text = f"""
        <h2>{APP_NAME}</h2>
        <p><b>Version:</b> {APP_VERSION}</p>
        <p><b>Description:</b> Windows Task Manager Simulator built with Python and PyQt6</p>
        <br>
        <p>A Python implementation of the Windows Task Manager for educational purposes.</p>
        <p><b>Technologies:</b> Python, PyQt6, psutil</p>
        <br>
        <p><i>© 2024 PyTaskManager Team</i></p>
        """

        QMessageBox.about(self, f"About {APP_NAME}", about_text)

    def closeEvent(self, event):
        """Maneja el evento de cierre de la ventana."""
        # Detener timers
        self.stop_auto_refresh()

        # Limpiar recursos
        self.process_manager.clear_cache()
        self.performance_monitor.clear_history()

        logger.info("Aplicación cerrada")
        event.accept()


def run_application():
    """Punto de entrada para ejecutar la aplicación."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)

    # Configurar estilo de la aplicación
    app.setStyle("Fusion")

    # Crear y mostrar ventana principal
    window = MainWindow()
    window.show()

    sys.exit(app.exec())
