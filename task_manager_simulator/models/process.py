"""
Modelo de datos para representar un proceso del sistema.
"""
from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime


@dataclass
class ProcessInfo:
    """Información completa de un proceso del sistema."""

    # Identificación
    pid: int
    name: str
    description: Optional[str] = None
    username: Optional[str] = None

    # Recursos
    cpu_percent: float = 0.0
    memory_mb: float = 0.0
    memory_percent: float = 0.0
    disk_read_mb: float = 0.0
    disk_write_mb: float = 0.0
    net_sent_kb: float = 0.0
    net_recv_kb: float = 0.0

    # Estado
    status: str = "running"  # running, sleeping, disk-sleep, stopped, zombie
    num_threads: int = 0
    num_handles: Optional[int] = None

    # Detalles
    exe_path: Optional[str] = None
    cmdline: Optional[str] = None
    create_time: Optional[datetime] = None
    parent_pid: Optional[int] = None

    # Prioridad
    priority: Optional[str] = None  # realtime, high, above_normal, normal, below_normal, idle
    nice: Optional[int] = None

    # CPU Affinity
    cpu_affinity: Optional[List[int]] = None

    def __post_init__(self):
        """Validación y conversión de tipos después de inicialización."""
        if self.create_time and isinstance(self.create_time, (int, float)):
            self.create_time = datetime.fromtimestamp(self.create_time)

    @property
    def uptime_seconds(self) -> Optional[float]:
        """Retorna el tiempo de actividad del proceso en segundos."""
        if self.create_time:
            return (datetime.now() - self.create_time).total_seconds()
        return None

    def to_dict(self) -> dict:
        """Convierte el proceso a diccionario."""
        return {
            'pid': self.pid,
            'name': self.name,
            'description': self.description,
            'username': self.username,
            'cpu_percent': self.cpu_percent,
            'memory_mb': self.memory_mb,
            'memory_percent': self.memory_percent,
            'disk_read_mb': self.disk_read_mb,
            'disk_write_mb': self.disk_write_mb,
            'net_sent_kb': self.net_sent_kb,
            'net_recv_kb': self.net_recv_kb,
            'status': self.status,
            'num_threads': self.num_threads,
            'num_handles': self.num_handles,
            'exe_path': self.exe_path,
            'cmdline': self.cmdline,
            'create_time': self.create_time.isoformat() if self.create_time else None,
            'parent_pid': self.parent_pid,
            'priority': self.priority,
            'nice': self.nice,
            'cpu_affinity': self.cpu_affinity,
        }
