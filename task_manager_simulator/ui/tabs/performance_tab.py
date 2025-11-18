"""
Pestaña de Rendimiento - Muestra métricas de rendimiento del sistema.
"""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QProgressBar, QGroupBox)
from PyQt6.QtCore import QTimer
import logging

from ...core.performance_monitor import PerformanceMonitor
from ...utils.formatters import (format_mb, format_percent, format_uptime,
                                 format_frequency, format_number)
from ...config.constants import REFRESH_RATE_CPU


logger = logging.getLogger(__name__)


class PerformanceTab(QWidget):
    """Pestaña que muestra métricas de rendimiento del sistema."""

    def __init__(self, performance_monitor: PerformanceMonitor):
        super().__init__()
        self.performance_monitor = performance_monitor

        self._init_ui()
        self._setup_timer()
        self.refresh_performance()

    def _init_ui(self):
        """Inicializa la interfaz de usuario."""
        layout = QVBoxLayout(self)

        # Layout principal con dos columnas
        main_layout = QHBoxLayout()

        # Columna izquierda: CPU
        cpu_group = self._create_cpu_group()
        main_layout.addWidget(cpu_group)

        # Columna derecha: Memoria
        memory_group = self._create_memory_group()
        main_layout.addWidget(memory_group)

        layout.addLayout(main_layout)

        # Información del sistema en la parte inferior
        system_group = self._create_system_group()
        layout.addWidget(system_group)

        layout.addStretch()

    def _create_cpu_group(self) -> QGroupBox:
        """Crea el grupo de información de CPU."""
        group = QGroupBox("CPU")
        layout = QVBoxLayout()

        # Porcentaje de uso
        self.cpu_percent_label = QLabel("0.0%")
        self.cpu_percent_label.setStyleSheet("font-size: 32px; font-weight: bold;")
        layout.addWidget(self.cpu_percent_label)

        # Barra de progreso
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setMaximum(100)
        self.cpu_progress.setTextVisible(False)
        layout.addWidget(self.cpu_progress)

        # Detalles
        details_layout = QGridLayout()

        details_layout.addWidget(QLabel("Utilización:"), 0, 0)
        self.cpu_utilization_label = QLabel("0.0%")
        details_layout.addWidget(self.cpu_utilization_label, 0, 1)

        details_layout.addWidget(QLabel("Velocidad:"), 1, 0)
        self.cpu_speed_label = QLabel("0.00 GHz")
        details_layout.addWidget(self.cpu_speed_label, 1, 1)

        details_layout.addWidget(QLabel("Procesos:"), 2, 0)
        self.cpu_processes_label = QLabel("0")
        details_layout.addWidget(self.cpu_processes_label, 2, 1)

        details_layout.addWidget(QLabel("Threads:"), 3, 0)
        self.cpu_threads_label = QLabel("0")
        details_layout.addWidget(self.cpu_threads_label, 3, 1)

        details_layout.addWidget(QLabel("Núcleos:"), 4, 0)
        self.cpu_cores_label = QLabel("0")
        details_layout.addWidget(self.cpu_cores_label, 4, 1)

        layout.addLayout(details_layout)

        group.setLayout(layout)
        return group

    def _create_memory_group(self) -> QGroupBox:
        """Crea el grupo de información de memoria."""
        group = QGroupBox("Memoria")
        layout = QVBoxLayout()

        # Memoria en uso
        self.memory_used_label = QLabel("0 MB / 0 MB")
        self.memory_used_label.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(self.memory_used_label)

        # Barra de progreso
        self.memory_progress = QProgressBar()
        self.memory_progress.setMaximum(100)
        self.memory_progress.setTextVisible(True)
        layout.addWidget(self.memory_progress)

        # Detalles
        details_layout = QGridLayout()

        details_layout.addWidget(QLabel("En uso:"), 0, 0)
        self.memory_percent_label = QLabel("0.0%")
        details_layout.addWidget(self.memory_percent_label, 0, 1)

        details_layout.addWidget(QLabel("Disponible:"), 1, 0)
        self.memory_available_label = QLabel("0 MB")
        details_layout.addWidget(self.memory_available_label, 1, 1)

        details_layout.addWidget(QLabel("Caché:"), 2, 0)
        self.memory_cached_label = QLabel("0 MB")
        details_layout.addWidget(self.memory_cached_label, 2, 1)

        details_layout.addWidget(QLabel("Swap:"), 3, 0)
        self.memory_swap_label = QLabel("0 MB / 0 MB")
        details_layout.addWidget(self.memory_swap_label, 3, 1)

        layout.addLayout(details_layout)

        group.setLayout(layout)
        return group

    def _create_system_group(self) -> QGroupBox:
        """Crea el grupo de información del sistema."""
        group = QGroupBox("Sistema")
        layout = QGridLayout()

        layout.addWidget(QLabel("Tiempo activo:"), 0, 0)
        self.uptime_label = QLabel("0s")
        layout.addWidget(self.uptime_label, 0, 1)

        group.setLayout(layout)
        return group

    def _setup_timer(self):
        """Configura el temporizador de actualización automática."""
        self.timer = QTimer()
        self.timer.timeout.connect(self.refresh_performance)
        self.timer.start(REFRESH_RATE_CPU)

    def refresh_performance(self):
        """Actualiza las métricas de rendimiento."""
        try:
            performance = self.performance_monitor.get_system_performance()
            self._update_cpu_display(performance)
            self._update_memory_display(performance)
            self._update_system_display(performance)
        except Exception as e:
            logger.error(f"Error al actualizar rendimiento: {e}")

    def _update_cpu_display(self, performance):
        """Actualiza la visualización de CPU."""
        cpu = performance.cpu

        # Porcentaje principal
        self.cpu_percent_label.setText(format_percent(cpu.total_percent, 1))
        self.cpu_progress.setValue(int(cpu.total_percent))

        # Detalles
        self.cpu_utilization_label.setText(format_percent(cpu.total_percent, 1))
        self.cpu_speed_label.setText(format_frequency(cpu.frequency_current))
        self.cpu_processes_label.setText(format_number(cpu.process_count))
        self.cpu_threads_label.setText(format_number(cpu.thread_count))
        self.cpu_cores_label.setText(f"{cpu.count_physical} físicos, {cpu.count_logical} lógicos")

        # Color de la barra según uso
        if cpu.total_percent < 50:
            self.cpu_progress.setStyleSheet("QProgressBar::chunk { background-color: green; }")
        elif cpu.total_percent < 80:
            self.cpu_progress.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.cpu_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")

    def _update_memory_display(self, performance):
        """Actualiza la visualización de memoria."""
        memory = performance.memory

        # Memoria en uso
        self.memory_used_label.setText(
            f"{format_mb(memory.used_mb, 0)} / {format_mb(memory.total_mb, 0)}"
        )

        # Barra de progreso
        self.memory_progress.setValue(int(memory.percent))
        self.memory_progress.setFormat(format_percent(memory.percent, 1))

        # Detalles
        self.memory_percent_label.setText(format_percent(memory.percent, 1))
        self.memory_available_label.setText(format_mb(memory.available_mb, 0))
        self.memory_cached_label.setText(
            format_mb(memory.cached_mb, 0) if memory.cached_mb else "N/A"
        )
        self.memory_swap_label.setText(
            f"{format_mb(memory.swap_used_mb, 0)} / {format_mb(memory.swap_total_mb, 0)}"
        )

        # Color de la barra según uso
        if memory.percent < 50:
            self.memory_progress.setStyleSheet("QProgressBar::chunk { background-color: blue; }")
        elif memory.percent < 80:
            self.memory_progress.setStyleSheet("QProgressBar::chunk { background-color: orange; }")
        else:
            self.memory_progress.setStyleSheet("QProgressBar::chunk { background-color: red; }")

    def _update_system_display(self, performance):
        """Actualiza la visualización del sistema."""
        self.uptime_label.setText(format_uptime(performance.uptime_seconds))

    def cleanup(self):
        """Limpia recursos al cerrar la pestaña."""
        if hasattr(self, 'timer'):
            self.timer.stop()
