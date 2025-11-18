"""
Monitor de rendimiento del sistema usando psutil.
"""
import psutil
import logging
from typing import List, Dict
from datetime import datetime
from collections import deque

from ..models.performance import (
    SystemPerformance,
    CPUMetrics,
    MemoryMetrics,
    DiskMetrics,
    NetworkMetrics,
)


logger = logging.getLogger(__name__)


class PerformanceMonitor:
    """
    Monitor de rendimiento del sistema.

    Proporciona funcionalidades para:
    - Monitorear uso de CPU
    - Monitorear uso de memoria
    - Monitorear actividad de disco
    - Monitorear actividad de red
    - Mantener historial de métricas
    """

    def __init__(self, history_length: int = 60):
        """
        Inicializa el monitor de rendimiento.

        Args:
            history_length: Número de muestras a mantener en el historial
        """
        self.history_length = history_length

        # Historial de métricas
        self.cpu_history: deque = deque(maxlen=history_length)
        self.memory_history: deque = deque(maxlen=history_length)
        self.disk_history: Dict[str, deque] = {}
        self.network_history: Dict[str, deque] = {}

        # Cache para cálculos delta
        self._last_disk_io: Dict[str, tuple] = {}
        self._last_network_io: Dict[str, tuple] = {}
        self._last_sample_time: datetime = datetime.now()

        # Información del sistema
        self.boot_time = datetime.fromtimestamp(psutil.boot_time())
        self.cpu_count_physical = psutil.cpu_count(logical=False) or 1
        self.cpu_count_logical = psutil.cpu_count(logical=True) or 1

        logger.info("PerformanceMonitor inicializado")

    def get_current_performance(self) -> SystemPerformance:
        """
        Obtiene las métricas de rendimiento actuales del sistema.

        Returns:
            Objeto SystemPerformance con todas las métricas
        """
        perf = SystemPerformance()

        # Métricas de CPU
        perf.cpu = self.get_cpu_metrics()
        self.cpu_history.append(perf.cpu)

        # Métricas de memoria
        perf.memory = self.get_memory_metrics()
        self.memory_history.append(perf.memory)

        # Métricas de disco
        perf.disks = self.get_disk_metrics()

        # Métricas de red
        perf.networks = self.get_network_metrics()

        # Información general
        perf.boot_time = self.boot_time
        perf.num_processes = len(psutil.pids())
        perf.timestamp = datetime.now()

        return perf

    def get_cpu_metrics(self) -> CPUMetrics:
        """
        Obtiene métricas de CPU.

        Returns:
            Objeto CPUMetrics
        """
        metrics = CPUMetrics()

        try:
            # Porcentaje de uso
            metrics.percent = psutil.cpu_percent(interval=0.1)
            metrics.per_cpu_percent = psutil.cpu_percent(interval=0.1, percpu=True)

            # Frecuencia
            cpu_freq = psutil.cpu_freq()
            if cpu_freq:
                metrics.frequency_current = cpu_freq.current
                metrics.frequency_min = cpu_freq.min
                metrics.frequency_max = cpu_freq.max

            # Número de núcleos
            metrics.num_cores_physical = self.cpu_count_physical
            metrics.num_cores_logical = self.cpu_count_logical

            # Tiempos de CPU
            cpu_times = psutil.cpu_times()
            metrics.user_time = cpu_times.user
            metrics.system_time = cpu_times.system
            metrics.idle_time = cpu_times.idle

            # Estadísticas
            cpu_stats = psutil.cpu_stats()
            metrics.ctx_switches = cpu_stats.ctx_switches
            metrics.interrupts = cpu_stats.interrupts

            metrics.timestamp = datetime.now()

        except Exception as e:
            logger.error(f"Error obteniendo métricas de CPU: {e}")

        return metrics

    def get_memory_metrics(self) -> MemoryMetrics:
        """
        Obtiene métricas de memoria.

        Returns:
            Objeto MemoryMetrics
        """
        metrics = MemoryMetrics()

        try:
            # Memoria virtual
            vm = psutil.virtual_memory()
            metrics.total = vm.total
            metrics.available = vm.available
            metrics.used = vm.used
            metrics.free = vm.free
            metrics.percent = vm.percent

            # Atributos específicos de la plataforma
            if hasattr(vm, 'active'):
                metrics.active = vm.active
            if hasattr(vm, 'inactive'):
                metrics.inactive = vm.inactive
            if hasattr(vm, 'buffers'):
                metrics.buffers = vm.buffers
            if hasattr(vm, 'cached'):
                metrics.cached = vm.cached
            if hasattr(vm, 'shared'):
                metrics.shared = vm.shared
            if hasattr(vm, 'slab'):
                metrics.slab = vm.slab

            # Swap
            swap = psutil.swap_memory()
            metrics.swap_total = swap.total
            metrics.swap_used = swap.used
            metrics.swap_free = swap.free
            metrics.swap_percent = swap.percent

            metrics.timestamp = datetime.now()

        except Exception as e:
            logger.error(f"Error obteniendo métricas de memoria: {e}")

        return metrics

    def get_disk_metrics(self) -> List[DiskMetrics]:
        """
        Obtiene métricas de disco para todas las particiones.

        Returns:
            Lista de objetos DiskMetrics
        """
        disk_metrics = []

        try:
            # Particiones
            partitions = psutil.disk_partitions(all=False)

            for partition in partitions:
                try:
                    metrics = DiskMetrics()
                    metrics.device = partition.device
                    metrics.mountpoint = partition.mountpoint
                    metrics.fstype = partition.fstype

                    # Uso de espacio
                    usage = psutil.disk_usage(partition.mountpoint)
                    metrics.total = usage.total
                    metrics.used = usage.used
                    metrics.free = usage.free
                    metrics.percent = usage.percent

                    # I/O counters (si está disponible)
                    try:
                        io_counters = psutil.disk_io_counters(perdisk=True)
                        device_name = partition.device.replace('/dev/', '').replace('\\', '')

                        # Buscar el contador correspondiente
                        for disk_name, counters in io_counters.items():
                            if disk_name in device_name or device_name in disk_name:
                                metrics.read_count = counters.read_count
                                metrics.write_count = counters.write_count
                                metrics.read_bytes = counters.read_bytes
                                metrics.write_bytes = counters.write_bytes
                                metrics.read_time = counters.read_time
                                metrics.write_time = counters.write_time
                                break

                    except (AttributeError, KeyError):
                        pass  # I/O counters no disponibles

                    metrics.timestamp = datetime.now()
                    disk_metrics.append(metrics)

                    # Agregar al historial
                    if partition.device not in self.disk_history:
                        self.disk_history[partition.device] = deque(maxlen=self.history_length)
                    self.disk_history[partition.device].append(metrics)

                except (PermissionError, OSError):
                    continue  # Partición no accesible

        except Exception as e:
            logger.error(f"Error obteniendo métricas de disco: {e}")

        return disk_metrics

    def get_network_metrics(self) -> List[NetworkMetrics]:
        """
        Obtiene métricas de red para todas las interfaces.

        Returns:
            Lista de objetos NetworkMetrics
        """
        network_metrics = []

        try:
            # Estadísticas de red por interfaz
            net_io = psutil.net_io_counters(pernic=True)
            net_stats = psutil.net_if_stats()

            for interface, counters in net_io.items():
                metrics = NetworkMetrics()
                metrics.interface = interface
                metrics.bytes_sent = counters.bytes_sent
                metrics.bytes_recv = counters.bytes_recv
                metrics.packets_sent = counters.packets_sent
                metrics.packets_recv = counters.packets_recv
                metrics.errin = counters.errin
                metrics.errout = counters.errout
                metrics.dropin = counters.dropin
                metrics.dropout = counters.dropout

                # Estadísticas de la interfaz
                if interface in net_stats:
                    stats = net_stats[interface]
                    metrics.speed = stats.speed
                    metrics.is_up = stats.isup

                metrics.timestamp = datetime.now()
                network_metrics.append(metrics)

                # Agregar al historial
                if interface not in self.network_history:
                    self.network_history[interface] = deque(maxlen=self.history_length)
                self.network_history[interface].append(metrics)

        except Exception as e:
            logger.error(f"Error obteniendo métricas de red: {e}")

        return network_metrics

    def get_cpu_history(self, samples: int = None) -> List[CPUMetrics]:
        """
        Obtiene el historial de métricas de CPU.

        Args:
            samples: Número de muestras a retornar (None = todas)

        Returns:
            Lista de objetos CPUMetrics
        """
        if samples is None:
            return list(self.cpu_history)
        return list(self.cpu_history)[-samples:]

    def get_memory_history(self, samples: int = None) -> List[MemoryMetrics]:
        """
        Obtiene el historial de métricas de memoria.

        Args:
            samples: Número de muestras a retornar (None = todas)

        Returns:
            Lista de objetos MemoryMetrics
        """
        if samples is None:
            return list(self.memory_history)
        return list(self.memory_history)[-samples:]

    def get_cpu_percent_series(self) -> List[float]:
        """
        Obtiene una serie temporal de porcentajes de CPU.

        Returns:
            Lista de porcentajes de CPU
        """
        return [metric.percent for metric in self.cpu_history]

    def get_memory_percent_series(self) -> List[float]:
        """
        Obtiene una serie temporal de porcentajes de memoria.

        Returns:
            Lista de porcentajes de memoria
        """
        return [metric.percent for metric in self.memory_history]

    def get_uptime(self) -> float:
        """
        Obtiene el tiempo de actividad del sistema en segundos.

        Returns:
            Segundos desde el arranque
        """
        return (datetime.now() - self.boot_time).total_seconds()

    def get_uptime_formatted(self) -> str:
        """
        Obtiene el tiempo de actividad formateado.

        Returns:
            String formateado (ej: "2 days, 3:45:12")
        """
        uptime_seconds = self.get_uptime()
        days = int(uptime_seconds // 86400)
        hours = int((uptime_seconds % 86400) // 3600)
        minutes = int((uptime_seconds % 3600) // 60)
        seconds = int(uptime_seconds % 60)

        if days > 0:
            return f"{days} days, {hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def clear_history(self):
        """Limpia todo el historial de métricas."""
        self.cpu_history.clear()
        self.memory_history.clear()
        for history in self.disk_history.values():
            history.clear()
        for history in self.network_history.values():
            history.clear()
        logger.debug("Historial de métricas limpiado")
