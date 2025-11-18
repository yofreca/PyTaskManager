"""
Pestaña de Servicios del Task Manager (Windows).
"""
import logging
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QMenu, QMessageBox, QHeaderView
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from ...models.service import ServiceInfo, ServiceStatus
from ...core.service_manager import ServiceManager
from ...config.settings import settings


logger = logging.getLogger(__name__)


class ServicesTab(QWidget):
    """
    Pestaña que muestra los servicios del sistema Windows.

    Signals:
        refresh_requested: Emitido cuando se solicita actualizar
    """

    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Inicializa la pestaña de servicios."""
        super().__init__(parent)

        self.services: List[ServiceInfo] = []
        self.selected_service: Optional[ServiceInfo] = None
        self.service_manager = ServiceManager()

        self._init_ui()
        logger.debug("ServicesTab inicializada")

        # Mostrar advertencia si no está disponible
        if not self.service_manager.is_available:
            self._show_unavailable_message()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Barra de información
        header = self._create_header()
        layout.addWidget(header)

        # Tabla de servicios
        self.table = QTableWidget()
        self._setup_table()
        layout.addWidget(self.table)

        # Botones de acción
        button_bar = self._create_button_bar()
        layout.addLayout(button_bar)

    def _create_header(self) -> QWidget:
        """Crea el header con información."""
        header = QWidget()
        layout = QHBoxLayout(header)

        self.info_label = QLabel("Services: 0")
        layout.addWidget(self.info_label)

        layout.addStretch()

        # Botón de actualizar
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)

        return header

    def _setup_table(self):
        """Configura la tabla de servicios."""
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name",
            "Display Name",
            "Status",
            "Startup Type",
            "PID"
        ])

        # Configurar tabla
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)

        # Menú contextual
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # Señal de selección
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

    def _create_button_bar(self) -> QHBoxLayout:
        """Crea la barra de botones."""
        button_layout = QHBoxLayout()

        button_layout.addStretch()

        # Botones de acción
        self.start_btn = QPushButton("Start")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self._start_service)
        button_layout.addWidget(self.start_btn)

        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._stop_service)
        button_layout.addWidget(self.stop_btn)

        self.restart_btn = QPushButton("Restart")
        self.restart_btn.setEnabled(False)
        self.restart_btn.clicked.connect(self._restart_service)
        button_layout.addWidget(self.restart_btn)

        return button_layout

    def _show_unavailable_message(self):
        """Muestra mensaje de funcionalidad no disponible."""
        msg = QLabel()

        if not settings.is_windows:
            msg.setText(
                "Services management is only available on Windows.\n\n"
                "This tab will display mock data for demonstration purposes."
            )
        else:
            msg.setText(
                "Services management requires pywin32.\n\n"
                "Install with: pip install pywin32\n\n"
                "Displaying mock data for demonstration."
            )

        msg.setAlignment(Qt.AlignmentFlag.AlignCenter)
        msg.setStyleSheet("""
            QLabel {
                color: #666;
                font-size: 14px;
                padding: 20px;
                background-color: #FFF4CE;
                border: 1px solid #FFD700;
                border-radius: 5px;
            }
        """)

        self.layout().insertWidget(1, msg)

    def update_services(self, services: List[ServiceInfo]):
        """
        Actualiza la lista de servicios.

        Args:
            services: Lista de objetos ServiceInfo
        """
        self.services = services

        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        for service in services:
            self._add_service_row(service)

        self.table.setSortingEnabled(True)

        self.info_label.setText(f"Services: {len(services)}")
        logger.debug(f"Tabla de servicios actualizada: {len(services)} servicios")

    def _add_service_row(self, service: ServiceInfo):
        """Agrega una fila de servicio a la tabla."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Name
        name_item = QTableWidgetItem(service.name)
        name_item.setData(Qt.ItemDataRole.UserRole, service.name)
        self.table.setItem(row, 0, name_item)

        # Display Name
        display_item = QTableWidgetItem(service.display_name)
        self.table.setItem(row, 1, display_item)

        # Status
        status_item = QTableWidgetItem(service.status.value.title())
        status_item.setForeground(self._get_status_color(service.status))
        self.table.setItem(row, 2, status_item)

        # Startup Type
        startup_item = QTableWidgetItem(service.start_type.value.title())
        self.table.setItem(row, 3, startup_item)

        # PID
        pid_item = QTableWidgetItem(str(service.pid) if service.pid else "")
        pid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 4, pid_item)

    def _get_status_color(self, status: ServiceStatus):
        """Retorna el color según el estado del servicio."""
        from PyQt6.QtGui import QColor

        if status == ServiceStatus.RUNNING:
            return QColor("#107C10")  # Verde
        elif status == ServiceStatus.STOPPED:
            return QColor("#D13438")  # Rojo
        elif status == ServiceStatus.PAUSED:
            return QColor("#FFB900")  # Amarillo
        else:
            return QColor("#666666")  # Gris

    def _on_selection_changed(self):
        """Maneja el cambio de selección."""
        selected_items = self.table.selectedItems()

        if selected_items:
            row = selected_items[0].row()
            name_item = self.table.item(row, 0)
            service_name = name_item.data(Qt.ItemDataRole.UserRole)

            # Buscar el servicio
            self.selected_service = next(
                (s for s in self.services if s.name == service_name),
                None
            )

            if self.selected_service:
                self._update_button_states()
        else:
            self.selected_service = None
            self._disable_all_buttons()

    def _update_button_states(self):
        """Actualiza el estado de los botones según el servicio seleccionado."""
        if not self.selected_service or not self.service_manager.is_available:
            self._disable_all_buttons()
            return

        status = self.selected_service.status

        # Start: habilitado si está detenido
        self.start_btn.setEnabled(status == ServiceStatus.STOPPED)

        # Stop: habilitado si está en ejecución o pausado
        self.stop_btn.setEnabled(
            status in [ServiceStatus.RUNNING, ServiceStatus.PAUSED]
        )

        # Restart: habilitado si está en ejecución
        self.restart_btn.setEnabled(status == ServiceStatus.RUNNING)

    def _disable_all_buttons(self):
        """Deshabilita todos los botones."""
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(False)
        self.restart_btn.setEnabled(False)

    def _show_context_menu(self, position):
        """Muestra el menú contextual."""
        if not self.selected_service:
            return

        menu = QMenu(self)

        # Acciones según el estado
        if self.selected_service.status == ServiceStatus.STOPPED:
            start_action = QAction("Start", self)
            start_action.triggered.connect(self._start_service)
            menu.addAction(start_action)

        if self.selected_service.status in [ServiceStatus.RUNNING, ServiceStatus.PAUSED]:
            stop_action = QAction("Stop", self)
            stop_action.triggered.connect(self._stop_service)
            menu.addAction(stop_action)

        if self.selected_service.status == ServiceStatus.RUNNING:
            restart_action = QAction("Restart", self)
            restart_action.triggered.connect(self._restart_service)
            menu.addAction(restart_action)

        menu.addSeparator()

        # Propiedades (deshabilitado por ahora)
        properties_action = QAction("Properties", self)
        properties_action.setEnabled(False)
        menu.addAction(properties_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _start_service(self):
        """Inicia el servicio seleccionado."""
        if not self.selected_service:
            return

        reply = QMessageBox.question(
            self,
            "Start Service",
            f"Do you want to start the service '{self.selected_service.display_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.service_manager.start_service(self.selected_service.name)

            if success:
                QMessageBox.information(self, "Success",
                                      f"Service '{self.selected_service.display_name}' started successfully.")
                self.refresh_requested.emit()
            else:
                QMessageBox.critical(self, "Error",
                                   f"Failed to start service '{self.selected_service.display_name}'.\n"
                                   "Make sure you have administrator privileges.")

    def _stop_service(self):
        """Detiene el servicio seleccionado."""
        if not self.selected_service:
            return

        reply = QMessageBox.warning(
            self,
            "Stop Service",
            f"Do you want to stop the service '{self.selected_service.display_name}'?\n\n"
            "Stopping a service may affect system functionality.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.service_manager.stop_service(self.selected_service.name)

            if success:
                QMessageBox.information(self, "Success",
                                      f"Service '{self.selected_service.display_name}' stopped successfully.")
                self.refresh_requested.emit()
            else:
                QMessageBox.critical(self, "Error",
                                   f"Failed to stop service '{self.selected_service.display_name}'.\n"
                                   "Make sure you have administrator privileges.")

    def _restart_service(self):
        """Reinicia el servicio seleccionado."""
        if not self.selected_service:
            return

        reply = QMessageBox.question(
            self,
            "Restart Service",
            f"Do you want to restart the service '{self.selected_service.display_name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            success = self.service_manager.restart_service(self.selected_service.name)

            if success:
                QMessageBox.information(self, "Success",
                                      f"Service '{self.selected_service.display_name}' restarted successfully.")
                self.refresh_requested.emit()
            else:
                QMessageBox.critical(self, "Error",
                                   f"Failed to restart service '{self.selected_service.display_name}'.\n"
                                   "Make sure you have administrator privileges.")

    def clear(self):
        """Limpia la tabla."""
        self.table.setRowCount(0)
        self.services.clear()
        self.selected_service = None
        self.info_label.setText("Services: 0")
