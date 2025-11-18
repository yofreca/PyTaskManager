"""
Modelo de datos para métricas de rendimiento del sistema.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class CPUMetrics:
    """Métricas de CPU del sistema."""

    total_percent: float = 0.0
    per_cpu_percent: List[float] = field(default_factory=list)
    frequency_current: float = 0.0
    frequency_min: float = 0.0
    frequency_max: float = 0.0
    count_physical: int = 0
    count_logical: int = 0
    process_count: int = 0
    thread_count: int = 0
    ctx_switches: int = 0
    interrupts: int = 0

    @property
    def average_percent(self) -> float:
        """Promedio de uso de todos los núcleos."""
        if self.per_cpu_percent:
            return sum(self.per_cpu_percent) / len(self.per_cpu_percent)
        return self.total_percent


@dataclass
class MemoryMetrics:
    """Métricas de memoria del sistema."""

    # Memoria física
    total_mb: float = 0.0
    available_mb: float = 0.0
    used_mb: float = 0.0
    percent: float = 0.0

    # Memoria virtual/swap
    swap_total_mb: float = 0.0
    swap_used_mb: float = 0.0
    swap_free_mb: float = 0.0
    swap_percent: float = 0.0

    # Memoria en caché (Linux/Windows específico)
    cached_mb: Optional[float] = None
    buffers_mb: Optional[float] = None
    shared_mb: Optional[float] = None

    @property
    def free_mb(self) -> float:
        """Memoria libre."""
        return self.total_mb - self.used_mb


@dataclass
class DiskMetrics:
    """Métricas de disco del sistema."""

    device: str
    mountpoint: str
    fstype: str
    total_gb: float = 0.0
    used_gb: float = 0.0
    free_gb: float = 0.0
    percent: float = 0.0

    # I/O stats
    read_count: int = 0
    write_count: int = 0
    read_bytes: int = 0
    write_bytes: int = 0
    read_time_ms: int = 0
    write_time_ms: int = 0

    @property
    def read_mb_per_sec(self) -> float:
        """MB leídos por segundo (requiere cálculo temporal)."""
        return 0.0  # Calculado externamente

    @property
    def write_mb_per_sec(self) -> float:
        """MB escritos por segundo (requiere cálculo temporal)."""
        return 0.0  # Calculado externamente


@dataclass
class NetworkMetrics:
    """Métricas de red del sistema."""

    interface: str
    bytes_sent: int = 0
    bytes_recv: int = 0
    packets_sent: int = 0
    packets_recv: int = 0
    errin: int = 0
    errout: int = 0
    dropin: int = 0
    dropout: int = 0

    # Velocidades (calculadas)
    send_mbps: float = 0.0
    recv_mbps: float = 0.0

    @property
    def total_mb_sent(self) -> float:
        """Total de MB enviados."""
        return self.bytes_sent / (1024 * 1024)

    @property
    def total_mb_recv(self) -> float:
        """Total de MB recibidos."""
        return self.bytes_recv / (1024 * 1024)


@dataclass
class SystemPerformance:
    """Métricas completas de rendimiento del sistema."""

    timestamp: datetime = field(default_factory=datetime.now)
    cpu: CPUMetrics = field(default_factory=CPUMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    disks: Dict[str, DiskMetrics] = field(default_factory=dict)
    network: Dict[str, NetworkMetrics] = field(default_factory=dict)
    uptime_seconds: float = 0.0

    def to_dict(self) -> dict:
        """Convierte las métricas a diccionario."""
        return {
            'timestamp': self.timestamp.isoformat(),
            'cpu': {
                'total_percent': self.cpu.total_percent,
                'per_cpu_percent': self.cpu.per_cpu_percent,
                'frequency_current': self.cpu.frequency_current,
                'count_physical': self.cpu.count_physical,
                'count_logical': self.cpu.count_logical,
                'process_count': self.cpu.process_count,
                'thread_count': self.cpu.thread_count,
            },
            'memory': {
                'total_mb': self.memory.total_mb,
                'used_mb': self.memory.used_mb,
                'available_mb': self.memory.available_mb,
                'percent': self.memory.percent,
                'swap_total_mb': self.memory.swap_total_mb,
                'swap_used_mb': self.memory.swap_used_mb,
                'swap_percent': self.memory.swap_percent,
            },
            'disks': {k: {'device': v.device, 'total_gb': v.total_gb, 'used_gb': v.used_gb,
                          'free_gb': v.free_gb, 'percent': v.percent}
                     for k, v in self.disks.items()},
            'network': {k: {'bytes_sent': v.bytes_sent, 'bytes_recv': v.bytes_recv,
                           'send_mbps': v.send_mbps, 'recv_mbps': v.recv_mbps}
                       for k, v in self.network.items()},
            'uptime_seconds': self.uptime_seconds,
        }
