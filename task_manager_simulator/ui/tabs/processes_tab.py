"""
Pestaña de Procesos - Muestra la lista de procesos activos.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTableWidget,
                              QTableWidgetItem, QPushButton, QLabel, QHeaderView,
                              QMenu, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction
import logging
from typing import List

from ...core.process_manager import ProcessManager
from ...models.process import ProcessInfo
from ...utils.formatters import format_mb, format_percent
from ...config.constants import REFRESH_RATE_PROCESSES


logger = logging.getLogger(__name__)


class ProcessesTab(QWidget):
    """Pestaña que muestra la lista de procesos activos."""

    def __init__(self, process_manager: ProcessManager):
        super().__init__()
        self.process_manager = process_manager
        self.processes: List[ProcessInfo] = []

        self._init_ui()
        self._setup_timer()
        self.refresh_processes()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Etiqueta de información
        self.info_label = QLabel("Procesos: 0")
        layout.addWidget(self.info_label)

        # Tabla de procesos
        self.table = QTableWidget()
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels([
            "Nombre", "PID", "CPU %", "Memoria", "Estado", "Usuario", "Threads"
        ])

        # Configurar tabla
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setSortingEnabled(True)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        # Ajustar columnas
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(6, QHeaderView.ResizeMode.ResizeToContents)

        # Menú contextual
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        layout.addWidget(self.table)

        # Botones
        button_layout = QHBoxLayout()
        self.refresh_button = QPushButton("Actualizar")
        self.refresh_button.clicked.connect(self.refresh_processes)
        self.end_task_button = QPushButton("Finalizar Proceso")
        self.end_task_button.clicked.connect(self._end_process)

        button_layout.addWidget(self.refresh_button)
        button_layout.addWidget(self.end_task_button)
        button_layout.addStretch()

        layout.addLayout(button_layout)

    def _setup_timer(self):
        """Configura el temporizador de actualización automática."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_processes)
        self.timer.start(REFRESH_RATE_PROCESSES)

    def refresh_processes(self):
        """Actualiza la lista de procesos."""
        try:
            self.processes = self.process_manager.get_all_processes()
            self._update_table()
            self.info_label.setText(f"Procesos: {len(self.processes)}")
        except Exception as e:
            logger.error(f"Error al actualizar procesos: {e}")

    def _update_table(self):
        """Actualiza la tabla con la lista de procesos."""
        # Desactivar ordenamiento temporalmente
        self.table.setSortingEnabled(False)

        # Limpiar tabla
        self.table.setRowCount(0)

        # Añadir procesos
        for row, process in enumerate(self.processes):
            self.table.insertRow(row)

            # Nombre
            name_item = QTableWidgetItem(process.name)
            name_item.setData(Qt.ItemDataRole.UserRole, process.pid)
            self.table.setItem(row, 0, name_item)

            # PID
            self.table.setItem(row, 1, QTableWidgetItem(str(process.pid)))

            # CPU %
            cpu_item = QTableWidgetItem(format_percent(process.cpu_percent))
            cpu_item.setData(Qt.ItemDataRole.UserRole, process.cpu_percent)
            self.table.setItem(row, 2, cpu_item)

            # Memoria
            mem_item = QTableWidgetItem(format_mb(process.memory_mb))
            mem_item.setData(Qt.ItemDataRole.UserRole, process.memory_mb)
            self.table.setItem(row, 3, mem_item)

            # Estado
            self.table.setItem(row, 4, QTableWidgetItem(process.status))

            # Usuario
            self.table.setItem(row, 5, QTableWidgetItem(process.username or "N/A"))

            # Threads
            self.table.setItem(row, 6, QTableWidgetItem(str(process.num_threads)))

        # Reactivar ordenamiento
        self.table.setSortingEnabled(True)

    def _show_context_menu(self, position):
        """Muestra el menú contextual."""
        menu = QMenu()

        end_action = QAction("Finalizar proceso", self)
        end_action.triggered.connect(self._end_process)
        menu.addAction(end_action)

        suspend_action = QAction("Suspender proceso", self)
        suspend_action.triggered.connect(self._suspend_process)
        menu.addAction(suspend_action)

        resume_action = QAction("Reanudar proceso", self)
        resume_action.triggered.connect(self._resume_process)
        menu.addAction(resume_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _get_selected_pid(self) -> int:
        """Obtiene el PID del proceso seleccionado."""
        selected_items = self.table.selectedItems()
        if selected_items:
            row = selected_items[0].row()
            pid_item = self.table.item(row, 1)
            return int(pid_item.text())
        return -1

    def _end_process(self):
        """Finaliza el proceso seleccionado."""
        pid = self._get_selected_pid()
        if pid == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un proceso primero.")
            return

        reply = QMessageBox.question(
            self, 'Confirmar',
            f'¿Está seguro de finalizar el proceso {pid}?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            if self.process_manager.kill_process(pid):
                QMessageBox.information(self, "Éxito", f"Proceso {pid} finalizado.")
                self.refresh_processes()
            else:
                QMessageBox.critical(self, "Error", f"No se pudo finalizar el proceso {pid}.")

    def _suspend_process(self):
        """Suspende el proceso seleccionado."""
        pid = self._get_selected_pid()
        if pid == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un proceso primero.")
            return

        if self.process_manager.suspend_process(pid):
            QMessageBox.information(self, "Éxito", f"Proceso {pid} suspendido.")
            self.refresh_processes()
        else:
            QMessageBox.critical(self, "Error", f"No se pudo suspender el proceso {pid}.")

    def _resume_process(self):
        """Reanuda el proceso seleccionado."""
        pid = self._get_selected_pid()
        if pid == -1:
            QMessageBox.warning(self, "Advertencia", "Seleccione un proceso primero.")
            return

        if self.process_manager.resume_process(pid):
            QMessageBox.information(self, "Éxito", f"Proceso {pid} reanudado.")
            self.refresh_processes()
        else:
            QMessageBox.critical(self, "Error", f"No se pudo reanudar el proceso {pid}.")

    def cleanup(self):
        """Limpia recursos al cerrar la pestaña."""
        if hasattr(self, 'timer'):
            self.timer.stop()
