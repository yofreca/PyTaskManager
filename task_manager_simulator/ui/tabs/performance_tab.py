"""
Pestaña de Rendimiento del Task Manager.
"""
import logging
from typing import List

from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QFrame,
    QGridLayout,
)
from PyQt6.QtCore import Qt

from ...models.performance import SystemPerformance
from ...utils.formatters import (
    format_percentage,
    format_bytes,
    format_frequency,
    format_duration,
)
from ..widgets.performance_chart import PerformanceChart


logger = logging.getLogger(__name__)


class PerformanceTab(QWidget):
    """
    Pestaña que muestra el rendimiento del sistema.

    Muestra métricas de CPU, memoria, disco y red.
    """

    def __init__(self, parent=None):
        """Inicializa la pestaña de rendimiento."""
        super().__init__(parent)

        self.cpu_history: List[float] = []
        self.memory_history: List[float] = []

        self._init_ui()
        logger.debug("PerformanceTab inicializada")

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        main_layout = QVBoxLayout(self)

        # Crear grid para organizar las métricas
        grid = QGridLayout()

        # Panel de CPU
        self.cpu_panel = self._create_metric_panel("CPU")
        grid.addWidget(self.cpu_panel, 0, 0)

        # Panel de Memoria
        self.memory_panel = self._create_metric_panel("Memory")
        grid.addWidget(self.memory_panel, 0, 1)

        # Panel de Disco (placeholder)
        self.disk_panel = self._create_metric_panel("Disk")
        grid.addWidget(self.disk_panel, 1, 0)

        # Panel de Red (placeholder)
        self.network_panel = self._create_metric_panel("Network")
        grid.addWidget(self.network_panel, 1, 1)

        main_layout.addLayout(grid)

    def _create_metric_panel(self, title: str) -> QFrame:
        """
        Crea un panel de métricas.

        Args:
            title: Título del panel

        Returns:
            QFrame configurado
        """
        frame = QFrame()
        frame.setFrameShape(QFrame.Shape.StyledPanel)
        frame.setFrameShadow(QFrame.Shadow.Raised)

        layout = QVBoxLayout(frame)

        # Título
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)

        # Porcentaje grande
        percent_label = QLabel("0.0%")
        percent_label.setStyleSheet("font-size: 32px; color: #0078D4;")
        percent_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(percent_label)

        # Guardar referencia
        if title == "CPU":
            self.cpu_percent_label = percent_label
        elif title == "Memory":
            self.memory_percent_label = percent_label

        # Área para gráfico (placeholder)
        graph_placeholder = QLabel("[ Graph Area ]")
        graph_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        graph_placeholder.setStyleSheet("color: gray; font-size: 12px;")
        graph_placeholder.setMinimumHeight(150)
        layout.addWidget(graph_placeholder)

        # Reemplazar placeholder con gráfico real
        if title == "CPU":
            # Crear gráfico de CPU
            self.cpu_chart = PerformanceChart(
                title="CPU Usage History",
                max_points=60,
                y_range=(0, 100)
            )
            layout.removeWidget(graph_placeholder)
            graph_placeholder.deleteLater()
            layout.insertWidget(2, self.cpu_chart)
        elif title == "Memory":
            # Crear gráfico de Memoria
            self.memory_chart = PerformanceChart(
                title="Memory Usage History",
                max_points=60,
                y_range=(0, 100)
            )
            layout.removeWidget(graph_placeholder)
            graph_placeholder.deleteLater()
            layout.insertWidget(2, self.memory_chart)

        # Detalles
        details_layout = QVBoxLayout()

        if title == "CPU":
            self.cpu_details = self._create_details_widget()
            details_layout.addWidget(self.cpu_details)
        elif title == "Memory":
            self.memory_details = self._create_details_widget()
            details_layout.addWidget(self.memory_details)
        else:
            # Placeholder para Disk y Network
            placeholder = QLabel("Details coming soon...")
            placeholder.setStyleSheet("color: gray; font-style: italic;")
            details_layout.addWidget(placeholder)

        layout.addLayout(details_layout)
        layout.addStretch()

        return frame

    def _create_details_widget(self) -> QWidget:
        """
        Crea un widget de detalles.

        Returns:
            QWidget con labels de detalles
        """
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(5)

        return widget

    def update_performance(self, performance: SystemPerformance):
        """
        Actualiza las métricas de rendimiento.

        Args:
            performance: Objeto SystemPerformance
        """
        # Actualizar CPU
        self._update_cpu_metrics(performance)

        # Actualizar Memoria
        self._update_memory_metrics(performance)

        logger.debug("Métricas de rendimiento actualizadas")

    def _update_cpu_metrics(self, performance: SystemPerformance):
        """
        Actualiza las métricas de CPU.

        Args:
            performance: Objeto SystemPerformance
        """
        cpu = performance.cpu

        # Actualizar porcentaje
        self.cpu_percent_label.setText(format_percentage(cpu.percent, precision=1))

        # Actualizar historial
        self.cpu_history.append(cpu.percent)
        if len(self.cpu_history) > 60:
            self.cpu_history.pop(0)

        # Actualizar gráfico
        if hasattr(self, 'cpu_chart'):
            self.cpu_chart.update_data(cpu.percent)

        # Actualizar detalles
        self._update_cpu_details(cpu)

    def _update_cpu_details(self, cpu):
        """
        Actualiza los detalles de CPU.

        Args:
            cpu: Objeto CPUMetrics
        """
        # Limpiar detalles anteriores
        layout = self.cpu_details.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Crear nuevos detalles
        details = [
            ("Cores (Logical):", f"{cpu.num_cores_logical}"),
            ("Cores (Physical):", f"{cpu.num_cores_physical}"),
            ("Frequency:", format_frequency(cpu.frequency_current)),
            ("Max Frequency:", format_frequency(cpu.frequency_max)),
        ]

        for label_text, value_text in details:
            detail_layout = QHBoxLayout()

            label = QLabel(label_text)
            label.setStyleSheet("color: gray;")
            detail_layout.addWidget(label)

            value = QLabel(value_text)
            value.setStyleSheet("font-weight: bold;")
            detail_layout.addWidget(value)

            detail_layout.addStretch()

            layout.addLayout(detail_layout)

    def _update_memory_metrics(self, performance: SystemPerformance):
        """
        Actualiza las métricas de memoria.

        Args:
            performance: Objeto SystemPerformance
        """
        memory = performance.memory

        # Actualizar porcentaje
        self.memory_percent_label.setText(format_percentage(memory.percent, precision=1))

        # Actualizar historial
        self.memory_history.append(memory.percent)
        if len(self.memory_history) > 60:
            self.memory_history.pop(0)

        # Actualizar gráfico
        if hasattr(self, 'memory_chart'):
            self.memory_chart.update_data(memory.percent)

        # Actualizar detalles
        self._update_memory_details(memory)

    def _update_memory_details(self, memory):
        """
        Actualiza los detalles de memoria.

        Args:
            memory: Objeto MemoryMetrics
        """
        # Limpiar detalles anteriores
        layout = self.memory_details.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        # Crear nuevos detalles
        used_gb = memory.used / (1024 ** 3)
        total_gb = memory.total / (1024 ** 3)

        details = [
            ("In Use:", f"{used_gb:.1f} GB / {total_gb:.1f} GB"),
            ("Available:", format_bytes(memory.available)),
            ("Cached:", format_bytes(memory.cached)),
            ("Swap Used:", format_bytes(memory.swap_used)),
        ]

        for label_text, value_text in details:
            detail_layout = QHBoxLayout()

            label = QLabel(label_text)
            label.setStyleSheet("color: gray;")
            detail_layout.addWidget(label)

            value = QLabel(value_text)
            value.setStyleSheet("font-weight: bold;")
            detail_layout.addWidget(value)

            detail_layout.addStretch()

            layout.addLayout(detail_layout)

    def clear(self):
        """Limpia todas las métricas."""
        self.cpu_history.clear()
        self.memory_history.clear()
        self.cpu_percent_label.setText("0.0%")
        self.memory_percent_label.setText("0.0%")

        # Limpiar gráficos
        if hasattr(self, 'cpu_chart'):
            self.cpu_chart.clear()
        if hasattr(self, 'memory_chart'):
            self.memory_chart.clear()
