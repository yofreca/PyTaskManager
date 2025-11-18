"""
Monitor de rendimiento del sistema usando psutil.
"""
import psutil
import logging
from typing import Dict, List
from datetime import datetime
from collections import deque

from ..models.performance import (
    SystemPerformance, CPUMetrics, MemoryMetrics,
    DiskMetrics, NetworkMetrics
)
from ..config.constants import MAX_HISTORY_POINTS


logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """Monitor de rendimiento del sistema."""

    def __init__(self):
        """Inicializa el monitor de rendimiento."""
        self._cpu_history: deque = deque(maxlen=MAX_HISTORY_POINTS)
        self._memory_history: deque = deque(maxlen=MAX_HISTORY_POINTS)
        self._disk_io_prev: Dict[str, tuple] = {}
        self._net_io_prev: Dict[str, tuple] = {}
        self._last_update = datetime.now()

        # Inicializar psutil CPU para el primer cálculo
        psutil.cpu_percent(interval=None)

    def get_system_performance(self) -> SystemPerformance:
        """
        Obtiene las métricas completas de rendimiento del sistema.

        Returns:
            Objeto SystemPerformance con todas las métricas.
        """
        performance = SystemPerformance(
            timestamp=datetime.now(),
            cpu=self._get_cpu_metrics(),
            memory=self._get_memory_metrics(),
            disks=self._get_disk_metrics(),
            network=self._get_network_metrics(),
            uptime_seconds=self._get_uptime()
        )

        # Guardar en historial
        self._cpu_history.append(performance.cpu.total_percent)
        self._memory_history.append(performance.memory.percent)
        self._last_update = datetime.now()

        return performance

    def _get_cpu_metrics(self) -> CPUMetrics:
        """Obtiene métricas de CPU."""
        try:
            # CPU percent total y por núcleo
            cpu_percent = psutil.cpu_percent(interval=None)
            per_cpu_percent = psutil.cpu_percent(interval=None, percpu=True)

            # Frecuencias
            freq = psutil.cpu_freq()
            freq_current = freq.current if freq else 0.0
            freq_min = freq.min if freq else 0.0
            freq_max = freq.max if freq else 0.0

            # Contadores
            cpu_count_physical = psutil.cpu_count(logical=False) or 0
            cpu_count_logical = psutil.cpu_count(logical=True) or 0

            # Estadísticas
            stats = psutil.cpu_stats()
            ctx_switches = stats.ctx_switches if stats else 0
            interrupts = stats.interrupts if stats else 0

            return CPUMetrics(
                total_percent=cpu_percent,
                per_cpu_percent=per_cpu_percent,
                frequency_current=freq_current,
                frequency_min=freq_min,
                frequency_max=freq_max,
                count_physical=cpu_count_physical,
                count_logical=cpu_count_logical,
                ctx_switches=ctx_switches,
                interrupts=interrupts,
            )

        except Exception as e:
            logger.error(f"Error al obtener métricas de CPU: {e}")
            return CPUMetrics()

    def _get_memory_metrics(self) -> MemoryMetrics:
        """Obtiene métricas de memoria."""
        try:
            # Memoria virtual
            mem = psutil.virtual_memory()

            # Swap
            swap = psutil.swap_memory()

            return MemoryMetrics(
                total_mb=mem.total / (1024 * 1024),
                available_mb=mem.available / (1024 * 1024),
                used_mb=mem.used / (1024 * 1024),
                percent=mem.percent,
                swap_total_mb=swap.total / (1024 * 1024),
                swap_used_mb=swap.used / (1024 * 1024),
                swap_free_mb=swap.free / (1024 * 1024),
                swap_percent=swap.percent,
                cached_mb=getattr(mem, 'cached', 0) / (1024 * 1024),
                buffers_mb=getattr(mem, 'buffers', 0) / (1024 * 1024),
                shared_mb=getattr(mem, 'shared', 0) / (1024 * 1024),
            )

        except Exception as e:
            logger.error(f"Error al obtener métricas de memoria: {e}")
            return MemoryMetrics()

    def _get_disk_metrics(self) -> Dict[str, DiskMetrics]:
        """Obtiene métricas de disco."""
        disks = {}

        try:
            # Obtener particiones
            partitions = psutil.disk_partitions(all=False)

            for partition in partitions:
                try:
                    # Uso de disco
                    usage = psutil.disk_usage(partition.mountpoint)

                    disk_metric = DiskMetrics(
                        device=partition.device,
                        mountpoint=partition.mountpoint,
                        fstype=partition.fstype,
                        total_gb=usage.total / (1024 ** 3),
                        used_gb=usage.used / (1024 ** 3),
                        free_gb=usage.free / (1024 ** 3),
                        percent=usage.percent,
                    )

                    disks[partition.device] = disk_metric

                except (PermissionError, OSError) as e:
                    logger.debug(f"Error al acceder a partición {partition.device}: {e}")
                    continue

            # I/O counters
            try:
                io_counters = psutil.disk_io_counters(perdisk=True)
                for disk_name, io in io_counters.items():
                    if disk_name in disks:
                        disks[disk_name].read_count = io.read_count
                        disks[disk_name].write_count = io.write_count
                        disks[disk_name].read_bytes = io.read_bytes
                        disks[disk_name].write_bytes = io.write_bytes
                        disks[disk_name].read_time_ms = io.read_time
                        disks[disk_name].write_time_ms = io.write_time
            except Exception as e:
                logger.debug(f"Error al obtener I/O counters de disco: {e}")

        except Exception as e:
            logger.error(f"Error al obtener métricas de disco: {e}")

        return disks

    def _get_network_metrics(self) -> Dict[str, NetworkMetrics]:
        """Obtiene métricas de red."""
        networks = {}

        try:
            # I/O counters por interfaz
            net_io = psutil.net_io_counters(pernic=True)

            for interface, io in net_io.items():
                network_metric = NetworkMetrics(
                    interface=interface,
                    bytes_sent=io.bytes_sent,
                    bytes_recv=io.bytes_recv,
                    packets_sent=io.packets_sent,
                    packets_recv=io.packets_recv,
                    errin=io.errin,
                    errout=io.errout,
                    dropin=io.dropin,
                    dropout=io.dropout,
                )

                # Calcular velocidad si tenemos datos previos
                if interface in self._net_io_prev:
                    prev_sent, prev_recv, prev_time = self._net_io_prev[interface]
                    time_delta = (datetime.now() - prev_time).total_seconds()

                    if time_delta > 0:
                        bytes_sent_diff = io.bytes_sent - prev_sent
                        bytes_recv_diff = io.bytes_recv - prev_recv

                        # Convertir a Mbps
                        network_metric.send_mbps = (bytes_sent_diff / time_delta) * 8 / (1024 * 1024)
                        network_metric.recv_mbps = (bytes_recv_diff / time_delta) * 8 / (1024 * 1024)

                # Guardar estado actual
                self._net_io_prev[interface] = (io.bytes_sent, io.bytes_recv, datetime.now())

                networks[interface] = network_metric

        except Exception as e:
            logger.error(f"Error al obtener métricas de red: {e}")

        return networks

    def _get_uptime(self) -> float:
        """Obtiene el tiempo de actividad del sistema en segundos."""
        try:
            boot_time = psutil.boot_time()
            return (datetime.now().timestamp() - boot_time)
        except Exception as e:
            logger.error(f"Error al obtener uptime: {e}")
            return 0.0

    def get_cpu_history(self) -> List[float]:
        """Retorna el historial de uso de CPU."""
        return list(self._cpu_history)

    def get_memory_history(self) -> List[float]:
        """Retorna el historial de uso de memoria."""
        return list(self._memory_history)

    def clear_history(self):
        """Limpia el historial de métricas."""
        self._cpu_history.clear()
        self._memory_history.clear()

    def get_cpu_count(self) -> tuple:
        """Retorna (núcleos físicos, núcleos lógicos)."""
        return (psutil.cpu_count(logical=False) or 0,
                psutil.cpu_count(logical=True) or 0)

    def get_total_memory(self) -> float:
        """Retorna la memoria total del sistema en GB."""
        try:
            mem = psutil.virtual_memory()
            return mem.total / (1024 ** 3)
        except Exception as e:
            logger.error(f"Error al obtener memoria total: {e}")
            return 0.0
