"""
Pestaña de Procesos del Task Manager.
"""
import logging
from typing import List, Optional

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QLabel,
    QMenu,
    QMessageBox,
    QHeaderView,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from ...models.process import Process
from ...utils.formatters import format_bytes, format_percentage
from ...config.settings import settings


logger = logging.getLogger(__name__)


class ProcessesTab(QWidget):
    """
    Pestaña que muestra los procesos del sistema.

    Signals:
        process_killed: Emitido cuando se termina un proceso
        refresh_requested: Emitido cuando se solicita actualizar
    """

    process_killed = pyqtSignal(int)  # PID
    refresh_requested = pyqtSignal()

    def __init__(self, parent=None):
        """Inicializa la pestaña de procesos."""
        super().__init__(parent)

        self.processes: List[Process] = []
        self.selected_pid: Optional[int] = None

        self._init_ui()
        logger.debug("ProcessesTab inicializada")

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Encabezado con información
        header_layout = QHBoxLayout()
        self.info_label = QLabel("Processes: 0")
        header_layout.addWidget(self.info_label)
        header_layout.addStretch()

        # Botón de actualizar
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        header_layout.addWidget(refresh_btn)

        layout.addLayout(header_layout)

        # Tabla de procesos
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels([
            "Name",
            "PID",
            "Status",
            "CPU %",
            "Memory"
        ])

        # Configurar tabla
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)  # Name
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)  # PID
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)  # Status
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)  # CPU
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)  # Memory

        # Menú contextual
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # Señal de selección
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        layout.addWidget(self.table)

        # Botones de acción
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()

        self.end_task_btn = QPushButton("End Task")
        self.end_task_btn.setEnabled(False)
        self.end_task_btn.clicked.connect(self._end_selected_process)
        buttons_layout.addWidget(self.end_task_btn)

        layout.addLayout(buttons_layout)

    def update_processes(self, processes: List[Process]):
        """
        Actualiza la lista de procesos en la tabla.

        Args:
            processes: Lista de objetos Process
        """
        self.processes = processes

        # Deshabilitar ordenamiento temporalmente para mejor rendimiento
        self.table.setSortingEnabled(False)

        # Limpiar tabla
        self.table.setRowCount(0)

        # Agregar procesos
        for process in processes:
            self._add_process_row(process)

        # Reactivar ordenamiento
        self.table.setSortingEnabled(True)

        # Actualizar contador
        self.info_label.setText(f"Processes: {len(processes)}")

        logger.debug(f"Tabla de procesos actualizada: {len(processes)} procesos")

    def _add_process_row(self, process: Process):
        """
        Agrega una fila a la tabla con información del proceso.

        Args:
            process: Objeto Process
        """
        row = self.table.rowCount()
        self.table.insertRow(row)

        # Name
        name_item = QTableWidgetItem(process.name)
        name_item.setData(Qt.ItemDataRole.UserRole, process.pid)  # Guardar PID
        self.table.setItem(row, 0, name_item)

        # PID
        pid_item = QTableWidgetItem(str(process.pid))
        pid_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 1, pid_item)

        # Status
        status_item = QTableWidgetItem(process.status.value.title())
        self.table.setItem(row, 2, status_item)

        # CPU %
        cpu_item = QTableWidgetItem(format_percentage(process.cpu_percent))
        cpu_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 3, cpu_item)

        # Memory
        memory_item = QTableWidgetItem(format_bytes(process.memory_info.rss))
        memory_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.table.setItem(row, 4, memory_item)

    def _on_selection_changed(self):
        """Maneja el cambio de selección en la tabla."""
        selected_items = self.table.selectedItems()

        if selected_items:
            # Obtener PID de la fila seleccionada
            row = selected_items[0].row()
            name_item = self.table.item(row, 0)
            self.selected_pid = name_item.data(Qt.ItemDataRole.UserRole)
            self.end_task_btn.setEnabled(True)
        else:
            self.selected_pid = None
            self.end_task_btn.setEnabled(False)

    def _show_context_menu(self, position):
        """
        Muestra el menú contextual.

        Args:
            position: Posición del mouse
        """
        if self.selected_pid is None:
            return

        menu = QMenu(self)

        # Acción: End Task
        end_task_action = QAction("End Task", self)
        end_task_action.triggered.connect(self._end_selected_process)
        menu.addAction(end_task_action)

        # Acción: End Task Tree (futuro)
        end_tree_action = QAction("End Process Tree", self)
        end_tree_action.setEnabled(False)
        menu.addAction(end_tree_action)

        menu.addSeparator()

        # Acción: Properties (futuro)
        properties_action = QAction("Properties", self)
        properties_action.setEnabled(False)
        menu.addAction(properties_action)

        # Mostrar menú
        menu.exec(self.table.viewport().mapToGlobal(position))

    def _end_selected_process(self):
        """Termina el proceso seleccionado."""
        if self.selected_pid is None:
            return

        # Buscar el proceso
        process = next((p for p in self.processes if p.pid == self.selected_pid), None)

        if process is None:
            QMessageBox.warning(
                self,
                "Process Not Found",
                "The selected process no longer exists."
            )
            return

        # Confirmar
        reply = QMessageBox.question(
            self,
            "Confirm End Task",
            f"Are you sure you want to end the process '{process.name}' (PID: {process.pid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            # Emitir señal
            self.process_killed.emit(self.selected_pid)
            logger.info(f"Solicitud de terminar proceso: {process.name} (PID: {process.pid})")

    def get_selected_process(self) -> Optional[Process]:
        """
        Obtiene el proceso seleccionado.

        Returns:
            Objeto Process o None
        """
        if self.selected_pid is None:
            return None

        return next((p for p in self.processes if p.pid == self.selected_pid), None)

    def clear(self):
        """Limpia la tabla de procesos."""
        self.table.setRowCount(0)
        self.processes.clear()
        self.selected_pid = None
        self.info_label.setText("Processes: 0")
