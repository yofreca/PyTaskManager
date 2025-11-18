"""
Modelo de datos para procesos del sistema.
"""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum


class ProcessStatus(Enum):
    """Estados posibles de un proceso."""
    RUNNING = "running"
    SLEEPING = "sleeping"
    DISK_SLEEP = "disk-sleep"
    STOPPED = "stopped"
    ZOMBIE = "zombie"
    DEAD = "dead"
    WAKING = "waking"
    IDLE = "idle"
    LOCKED = "locked"
    WAITING = "waiting"


class ProcessPriority(Enum):
    """Prioridades de procesos."""
    REALTIME = 256
    HIGH = 128
    ABOVE_NORMAL = 32768
    NORMAL = 32
    BELOW_NORMAL = 16384
    IDLE = 64


@dataclass
class ProcessMemoryInfo:
    """Información de memoria de un proceso."""
    rss: int = 0  # Resident Set Size (memoria física)
    vms: int = 0  # Virtual Memory Size
    percent: float = 0.0  # Porcentaje de uso de memoria
    shared: int = 0  # Memoria compartida
    text: int = 0  # Memoria de texto
    data: int = 0  # Memoria de datos
    lib: int = 0  # Memoria de librerías


@dataclass
class ProcessCPUInfo:
    """Información de CPU de un proceso."""
    percent: float = 0.0  # Porcentaje de uso de CPU
    user_time: float = 0.0  # Tiempo de CPU en modo usuario
    system_time: float = 0.0  # Tiempo de CPU en modo kernel
    num_threads: int = 0  # Número de threads


@dataclass
class ProcessIOInfo:
    """Información de I/O de un proceso."""
    read_count: int = 0  # Número de operaciones de lectura
    write_count: int = 0  # Número de operaciones de escritura
    read_bytes: int = 0  # Bytes leídos
    write_bytes: int = 0  # Bytes escritos


@dataclass
class ProcessNetworkInfo:
    """Información de red de un proceso."""
    connections: int = 0  # Número de conexiones activas
    bytes_sent: int = 0  # Bytes enviados
    bytes_recv: int = 0  # Bytes recibidos


@dataclass
class Process:
    """
    Modelo de datos de un proceso del sistema.

    Attributes:
        pid: Process ID
        name: Nombre del proceso
        status: Estado del proceso
        username: Usuario que ejecuta el proceso
        create_time: Timestamp de creación del proceso
        cpu_info: Información de uso de CPU
        memory_info: Información de uso de memoria
        io_info: Información de I/O
        network_info: Información de red
        exe: Ruta al ejecutable
        cmdline: Línea de comandos
        cwd: Directorio de trabajo actual
        num_handles: Número de handles (Windows)
        parent_pid: PID del proceso padre
        priority: Prioridad del proceso
    """

    pid: int
    name: str
    status: ProcessStatus = ProcessStatus.RUNNING
    username: Optional[str] = None
    create_time: Optional[datetime] = None

    # Información de recursos
    cpu_info: ProcessCPUInfo = field(default_factory=ProcessCPUInfo)
    memory_info: ProcessMemoryInfo = field(default_factory=ProcessMemoryInfo)
    io_info: ProcessIOInfo = field(default_factory=ProcessIOInfo)
    network_info: ProcessNetworkInfo = field(default_factory=ProcessNetworkInfo)

    # Detalles del proceso
    exe: Optional[str] = None
    cmdline: List[str] = field(default_factory=list)
    cwd: Optional[str] = None
    num_handles: int = 0
    parent_pid: Optional[int] = None
    priority: Optional[ProcessPriority] = None

    # Metadatos
    description: Optional[str] = None
    icon_path: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el proceso a un diccionario."""
        return {
            "pid": self.pid,
            "name": self.name,
            "status": self.status.value if isinstance(self.status, ProcessStatus) else self.status,
            "username": self.username,
            "create_time": self.create_time.isoformat() if self.create_time else None,
            "cpu_percent": self.cpu_info.percent,
            "cpu_user_time": self.cpu_info.user_time,
            "cpu_system_time": self.cpu_info.system_time,
            "num_threads": self.cpu_info.num_threads,
            "memory_rss": self.memory_info.rss,
            "memory_vms": self.memory_info.vms,
            "memory_percent": self.memory_info.percent,
            "io_read_bytes": self.io_info.read_bytes,
            "io_write_bytes": self.io_info.write_bytes,
            "network_connections": self.network_info.connections,
            "exe": self.exe,
            "cmdline": " ".join(self.cmdline) if self.cmdline else "",
            "cwd": self.cwd,
            "num_handles": self.num_handles,
            "parent_pid": self.parent_pid,
            "priority": self.priority.value if self.priority else None,
            "description": self.description,
        }

    @property
    def cpu_percent(self) -> float:
        """Retorna el porcentaje de uso de CPU."""
        return self.cpu_info.percent

    @property
    def memory_percent(self) -> float:
        """Retorna el porcentaje de uso de memoria."""
        return self.memory_info.percent

    @property
    def memory_mb(self) -> float:
        """Retorna el uso de memoria en MB."""
        return self.memory_info.rss / (1024 * 1024)

    def __repr__(self) -> str:
        return f"Process(pid={self.pid}, name='{self.name}', status={self.status.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Process):
            return False
        return self.pid == other.pid

    def __hash__(self) -> int:
        return hash(self.pid)
