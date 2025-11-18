"""
Pestaña de Detalles avanzada del Task Manager.
"""
import logging
from typing import List, Optional, Set
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QLineEdit, QComboBox, QMenu, QDialog,
    QListWidget, QDialogButtonBox, QCheckBox, QHeaderView, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from ...models.process import Process
from ...utils.formatters import (
    format_bytes, format_percentage, format_duration,
    format_timestamp, format_number
)
from ...config.settings import settings


logger = logging.getLogger(__name__)


class DetailsTab(QWidget):
    """
    Pestaña de Detalles con información completa y configurable de procesos.

    Signals:
        process_killed: Emitido cuando se termina un proceso
        refresh_requested: Emitido cuando se solicita actualizar
    """

    process_killed = pyqtSignal(int)  # PID
    refresh_requested = pyqtSignal()

    # Definición de todas las columnas disponibles
    ALL_COLUMNS = {
        'name': {'label': 'Name', 'width': 200, 'default': True},
        'pid': {'label': 'PID', 'width': 80, 'default': True},
        'status': {'label': 'Status', 'width': 100, 'default': True},
        'username': {'label': 'User name', 'width': 120, 'default': True},
        'cpu_percent': {'label': 'CPU', 'width': 80, 'default': True},
        'memory': {'label': 'Memory', 'width': 100, 'default': True},
        'memory_percent': {'label': 'Memory %', 'width': 90, 'default': False},
        'threads': {'label': 'Threads', 'width': 80, 'default': False},
        'handles': {'label': 'Handles', 'width': 80, 'default': False},
        'create_time': {'label': 'Start time', 'width': 150, 'default': False},
        'cpu_time': {'label': 'CPU time', 'width': 100, 'default': False},
        'exe': {'label': 'Executable path', 'width': 300, 'default': False},
        'cmdline': {'label': 'Command line', 'width': 300, 'default': False},
        'parent_pid': {'label': 'Parent PID', 'width': 90, 'default': False},
        'io_read': {'label': 'I/O Read', 'width': 100, 'default': False},
        'io_write': {'label': 'I/O Write', 'width': 100, 'default': False},
        'network_connections': {'label': 'Connections', 'width': 90, 'default': False},
    }

    def __init__(self, parent=None):
        """Inicializa la pestaña de detalles."""
        super().__init__(parent)

        self.processes: List[Process] = []
        self.selected_pid: Optional[int] = None
        self.visible_columns: Set[str] = self._get_default_columns()
        self.filter_text: str = ""
        self.filter_column: str = "all"

        self._init_ui()
        logger.debug("DetailsTab inicializada")

    def _get_default_columns(self) -> Set[str]:
        """Retorna el conjunto de columnas visibles por defecto."""
        return {col for col, info in self.ALL_COLUMNS.items() if info['default']}

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Barra de herramientas superior
        toolbar = self._create_toolbar()
        layout.addLayout(toolbar)

        # Barra de búsqueda y filtros
        search_bar = self._create_search_bar()
        layout.addLayout(search_bar)

        # Tabla de procesos
        self.table = QTableWidget()
        self._setup_table()
        layout.addWidget(self.table)

        # Barra de información inferior
        info_bar = self._create_info_bar()
        layout.addLayout(info_bar)

    def _create_toolbar(self) -> QHBoxLayout:
        """Crea la barra de herramientas."""
        toolbar = QHBoxLayout()

        self.info_label = QLabel("Processes: 0 | Filtered: 0")
        toolbar.addWidget(self.info_label)

        toolbar.addStretch()

        # Botón para seleccionar columnas
        columns_btn = QPushButton("Select columns...")
        columns_btn.clicked.connect(self._show_column_selector)
        toolbar.addWidget(columns_btn)

        # Botón para exportar
        export_btn = QPushButton("Export...")
        export_btn.clicked.connect(self._export_data)
        toolbar.addWidget(export_btn)

        # Botón de actualizar
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        toolbar.addWidget(refresh_btn)

        return toolbar

    def _create_search_bar(self) -> QHBoxLayout:
        """Crea la barra de búsqueda."""
        search_bar = QHBoxLayout()

        search_bar.addWidget(QLabel("Search:"))

        # Campo de búsqueda
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Type to filter processes...")
        self.search_input.textChanged.connect(self._on_search_changed)
        search_bar.addWidget(self.search_input)

        search_bar.addWidget(QLabel("in"))

        # Selector de columna para buscar
        self.search_column = QComboBox()
        self.search_column.addItem("All columns", "all")
        self.search_column.addItem("Name", "name")
        self.search_column.addItem("PID", "pid")
        self.search_column.addItem("User", "username")
        self.search_column.addItem("Path", "exe")
        self.search_column.currentIndexChanged.connect(self._on_search_changed)
        search_bar.addWidget(self.search_column)

        # Botón para limpiar búsqueda
        clear_btn = QPushButton("Clear")
        clear_btn.clicked.connect(self._clear_search)
        search_bar.addWidget(clear_btn)

        return search_bar

    def _create_info_bar(self) -> QHBoxLayout:
        """Crea la barra de información."""
        info_bar = QHBoxLayout()

        self.selection_label = QLabel("No selection")
        info_bar.addWidget(self.selection_label)

        info_bar.addStretch()

        # Botón para terminar proceso
        self.end_task_btn = QPushButton("End Task")
        self.end_task_btn.setEnabled(False)
        self.end_task_btn.clicked.connect(self._end_selected_process)
        info_bar.addWidget(self.end_task_btn)

        return info_bar

    def _setup_table(self):
        """Configura la tabla de procesos."""
        # Configurar tabla
        self.table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.table.setAlternatingRowColors(True)
        self.table.setSortingEnabled(True)

        # Menú contextual
        self.table.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self._show_context_menu)

        # Señal de selección
        self.table.itemSelectionChanged.connect(self._on_selection_changed)

        # Actualizar columnas
        self._update_table_columns()

    def _update_table_columns(self):
        """Actualiza las columnas visibles en la tabla."""
        # Obtener lista ordenada de columnas visibles
        visible_cols = [col for col in self.ALL_COLUMNS.keys()
                       if col in self.visible_columns]

        self.table.setColumnCount(len(visible_cols))

        # Configurar headers
        headers = [self.ALL_COLUMNS[col]['label'] for col in visible_cols]
        self.table.setHorizontalHeaderLabels(headers)

        # Ajustar anchos
        header = self.table.horizontalHeader()
        for i, col in enumerate(visible_cols):
            width = self.ALL_COLUMNS[col]['width']
            if col in ['name', 'exe', 'cmdline']:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.Stretch)
            else:
                header.setSectionResizeMode(i, QHeaderView.ResizeMode.ResizeToContents)

    def update_processes(self, processes: List[Process]):
        """
        Actualiza la lista de procesos en la tabla.

        Args:
            processes: Lista de objetos Process
        """
        self.processes = processes

        # Aplicar filtros
        filtered_processes = self._filter_processes(processes)

        # Actualizar tabla
        self._populate_table(filtered_processes)

        # Actualizar contador
        self.info_label.setText(
            f"Processes: {len(processes)} | Filtered: {len(filtered_processes)}"
        )

        logger.debug(f"Tabla de detalles actualizada: {len(filtered_processes)} procesos")

    def _filter_processes(self, processes: List[Process]) -> List[Process]:
        """Filtra procesos según los criterios de búsqueda."""
        if not self.filter_text:
            return processes

        filtered = []
        search_text = self.filter_text.lower()
        search_col = self.search_column.currentData()

        for proc in processes:
            if self._matches_filter(proc, search_text, search_col):
                filtered.append(proc)

        return filtered

    def _matches_filter(self, process: Process, search_text: str, search_column: str) -> bool:
        """Verifica si un proceso coincide con el filtro."""
        if search_column == "all":
            # Buscar en todas las columnas
            fields = [
                process.name,
                str(process.pid),
                process.username or "",
                process.exe or "",
            ]
            return any(search_text in str(field).lower() for field in fields)

        # Buscar en columna específica
        field_map = {
            'name': process.name,
            'pid': str(process.pid),
            'username': process.username or "",
            'exe': process.exe or "",
        }

        field_value = field_map.get(search_column, "")
        return search_text in str(field_value).lower()

    def _populate_table(self, processes: List[Process]):
        """Pobla la tabla con los procesos."""
        self.table.setSortingEnabled(False)
        self.table.setRowCount(0)

        visible_cols = [col for col in self.ALL_COLUMNS.keys()
                       if col in self.visible_columns]

        for process in processes:
            self._add_process_row(process, visible_cols)

        self.table.setSortingEnabled(True)

    def _add_process_row(self, process: Process, columns: List[str]):
        """Agrega una fila de proceso a la tabla."""
        row = self.table.rowCount()
        self.table.insertRow(row)

        for col_index, col_name in enumerate(columns):
            item = self._create_table_item(process, col_name)
            if item:
                self.table.setItem(row, col_index, item)

    def _create_table_item(self, process: Process, column: str) -> Optional[QTableWidgetItem]:
        """Crea un item de tabla para una columna específica."""
        value = ""

        if column == 'name':
            value = process.name
        elif column == 'pid':
            value = str(process.pid)
        elif column == 'status':
            value = process.status.value.title()
        elif column == 'username':
            value = process.username or "N/A"
        elif column == 'cpu_percent':
            value = format_percentage(process.cpu_percent)
        elif column == 'memory':
            value = format_bytes(process.memory_info.rss) if process.memory_info else "N/A"
        elif column == 'memory_percent':
            value = format_percentage(process.memory_info.percent) if process.memory_info else "N/A"
        elif column == 'threads':
            value = str(process.cpu_info.num_threads) if process.cpu_info else "0"
        elif column == 'handles':
            value = str(process.num_handles) if process.num_handles else "N/A"
        elif column == 'create_time':
            value = format_timestamp(process.create_time) if process.create_time else "N/A"
        elif column == 'cpu_time':
            cpu_time = (process.cpu_info.user_time or 0) + (process.cpu_info.system_time or 0) if process.cpu_info else 0
            value = format_duration(cpu_time)
        elif column == 'exe':
            value = process.exe or "N/A"
        elif column == 'cmdline':
            value = ' '.join(process.cmdline) if process.cmdline else "N/A"
        elif column == 'parent_pid':
            value = str(process.parent_pid) if process.parent_pid else "N/A"
        elif column == 'io_read':
            value = format_bytes(process.io_info.read_bytes) if process.io_info else "N/A"
        elif column == 'io_write':
            value = format_bytes(process.io_info.write_bytes) if process.io_info else "N/A"
        elif column == 'network_connections':
            value = str(process.network_info.connections) if process.network_info else "0"

        item = QTableWidgetItem(value)

        # Guardar PID en la primera columna
        if column == 'name':
            item.setData(Qt.ItemDataRole.UserRole, process.pid)

        # Alinear números a la derecha
        if column in ['pid', 'cpu_percent', 'memory', 'memory_percent', 'threads',
                     'handles', 'parent_pid', 'io_read', 'io_write', 'network_connections']:
            item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)

        return item

    def _on_search_changed(self):
        """Maneja el cambio en el campo de búsqueda."""
        self.filter_text = self.search_input.text()
        self.filter_column = self.search_column.currentData()
        self.update_processes(self.processes)

    def _clear_search(self):
        """Limpia el campo de búsqueda."""
        self.search_input.clear()

    def _show_column_selector(self):
        """Muestra el diálogo de selección de columnas."""
        dialog = ColumnSelectorDialog(self.ALL_COLUMNS, self.visible_columns, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.visible_columns = dialog.get_selected_columns()
            self._update_table_columns()
            self.update_processes(self.processes)

    def _export_data(self):
        """Exporta los datos de la tabla."""
        # TODO: Implementar exportación
        QMessageBox.information(self, "Export", "Export functionality coming soon!")

    def _on_selection_changed(self):
        """Maneja el cambio de selección."""
        selected_items = self.table.selectedItems()

        if selected_items:
            row = selected_items[0].row()
            # Buscar el PID en la primera columna visible
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                pid = item.data(Qt.ItemDataRole.UserRole)
                if pid:
                    self.selected_pid = pid
                    break

            # Buscar el proceso
            process = next((p for p in self.processes if p.pid == self.selected_pid), None)
            if process:
                self.selection_label.setText(
                    f"Selected: {process.name} (PID: {process.pid})"
                )
                self.end_task_btn.setEnabled(True)
        else:
            self.selected_pid = None
            self.selection_label.setText("No selection")
            self.end_task_btn.setEnabled(False)

    def _show_context_menu(self, position):
        """Muestra el menú contextual."""
        if self.selected_pid is None:
            return

        menu = QMenu(self)

        end_task_action = QAction("End Task", self)
        end_task_action.triggered.connect(self._end_selected_process)
        menu.addAction(end_task_action)

        menu.addSeparator()

        properties_action = QAction("Properties", self)
        properties_action.setEnabled(False)
        menu.addAction(properties_action)

        menu.exec(self.table.viewport().mapToGlobal(position))

    def _end_selected_process(self):
        """Termina el proceso seleccionado."""
        if self.selected_pid is None:
            return

        process = next((p for p in self.processes if p.pid == self.selected_pid), None)
        if process is None:
            QMessageBox.warning(self, "Process Not Found",
                              "The selected process no longer exists.")
            return

        reply = QMessageBox.question(
            self, "Confirm End Task",
            f"Are you sure you want to end '{process.name}' (PID: {process.pid})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if reply == QMessageBox.StandardButton.Yes:
            self.process_killed.emit(self.selected_pid)
            logger.info(f"Solicitud de terminar proceso: {process.name} (PID: {process.pid})")

    def clear(self):
        """Limpia la tabla."""
        self.table.setRowCount(0)
        self.processes.clear()
        self.selected_pid = None
        self.info_label.setText("Processes: 0 | Filtered: 0")


class ColumnSelectorDialog(QDialog):
    """Diálogo para seleccionar columnas visibles."""

    def __init__(self, all_columns: dict, visible_columns: Set[str], parent=None):
        super().__init__(parent)
        self.all_columns = all_columns
        self.selected_columns = set(visible_columns)

        self.setWindowTitle("Select Columns")
        self.setMinimumWidth(400)
        self.setMinimumHeight(500)

        self._init_ui()

    def _init_ui(self):
        """Inicializa la interfaz."""
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Select columns to display:"))

        # Lista de columnas
        self.column_list = QListWidget()

        for col_name, col_info in self.ALL_COLUMNS.items():
            checkbox = QCheckBox(col_info['label'])
            checkbox.setChecked(col_name in self.selected_columns)
            checkbox.setProperty('column_name', col_name)
            checkbox.stateChanged.connect(self._on_checkbox_changed)

            item = QTableWidgetItem()
            self.column_list.addItem(item)
            self.column_list.setItemWidget(item, checkbox)

        layout.addWidget(self.column_list)

        # Botones
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok |
            QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def _on_checkbox_changed(self, state):
        """Maneja el cambio de estado de un checkbox."""
        checkbox = self.sender()
        col_name = checkbox.property('column_name')

        if state == Qt.CheckState.Checked.value:
            self.selected_columns.add(col_name)
        else:
            self.selected_columns.discard(col_name)

    def get_selected_columns(self) -> Set[str]:
        """Retorna las columnas seleccionadas."""
        return self.selected_columns
