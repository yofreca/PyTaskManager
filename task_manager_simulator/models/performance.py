"""
Modelo de datos para métricas de rendimiento del sistema.
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime


@dataclass
class CPUMetrics:
    """Métricas de uso de CPU."""
    percent: float = 0.0  # Uso total de CPU (%)
    per_cpu_percent: List[float] = field(default_factory=list)  # Uso por núcleo
    frequency_current: float = 0.0  # Frecuencia actual (MHz)
    frequency_min: float = 0.0  # Frecuencia mínima (MHz)
    frequency_max: float = 0.0  # Frecuencia máxima (MHz)
    num_cores_physical: int = 0  # Número de núcleos físicos
    num_cores_logical: int = 0  # Número de núcleos lógicos
    user_time: float = 0.0  # Tiempo en modo usuario
    system_time: float = 0.0  # Tiempo en modo sistema
    idle_time: float = 0.0  # Tiempo en idle
    interrupt_time: float = 0.0  # Tiempo en interrupciones
    ctx_switches: int = 0  # Cambios de contexto
    interrupts: int = 0  # Interrupciones
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte las métricas a diccionario."""
        return {
            "percent": round(self.percent, 2),
            "per_cpu_percent": [round(p, 2) for p in self.per_cpu_percent],
            "frequency_current": round(self.frequency_current, 2),
            "frequency_min": self.frequency_min,
            "frequency_max": self.frequency_max,
            "num_cores_physical": self.num_cores_physical,
            "num_cores_logical": self.num_cores_logical,
            "user_time": round(self.user_time, 2),
            "system_time": round(self.system_time, 2),
            "idle_time": round(self.idle_time, 2),
            "ctx_switches": self.ctx_switches,
            "interrupts": self.interrupts,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class MemoryMetrics:
    """Métricas de uso de memoria."""
    total: int = 0  # Memoria total (bytes)
    available: int = 0  # Memoria disponible (bytes)
    used: int = 0  # Memoria usada (bytes)
    free: int = 0  # Memoria libre (bytes)
    percent: float = 0.0  # Porcentaje de uso
    active: int = 0  # Memoria activa
    inactive: int = 0  # Memoria inactiva
    buffers: int = 0  # Buffers
    cached: int = 0  # Caché
    shared: int = 0  # Memoria compartida
    slab: int = 0  # Slab (kernel)
    timestamp: datetime = field(default_factory=datetime.now)

    # Swap
    swap_total: int = 0
    swap_used: int = 0
    swap_free: int = 0
    swap_percent: float = 0.0

    @property
    def total_mb(self) -> float:
        """Retorna memoria total en MB."""
        return self.total / (1024 * 1024)

    @property
    def used_mb(self) -> float:
        """Retorna memoria usada en MB."""
        return self.used / (1024 * 1024)

    @property
    def available_mb(self) -> float:
        """Retorna memoria disponible en MB."""
        return self.available / (1024 * 1024)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte las métricas a diccionario."""
        return {
            "total": self.total,
            "available": self.available,
            "used": self.used,
            "free": self.free,
            "percent": round(self.percent, 2),
            "active": self.active,
            "inactive": self.inactive,
            "buffers": self.buffers,
            "cached": self.cached,
            "shared": self.shared,
            "swap_total": self.swap_total,
            "swap_used": self.swap_used,
            "swap_free": self.swap_free,
            "swap_percent": round(self.swap_percent, 2),
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class DiskMetrics:
    """Métricas de uso de disco."""
    device: str = ""  # Nombre del dispositivo
    mountpoint: str = ""  # Punto de montaje
    fstype: str = ""  # Tipo de sistema de archivos
    total: int = 0  # Espacio total (bytes)
    used: int = 0  # Espacio usado (bytes)
    free: int = 0  # Espacio libre (bytes)
    percent: float = 0.0  # Porcentaje de uso
    read_count: int = 0  # Número de lecturas
    write_count: int = 0  # Número de escrituras
    read_bytes: int = 0  # Bytes leídos
    write_bytes: int = 0  # Bytes escritos
    read_time: int = 0  # Tiempo de lectura (ms)
    write_time: int = 0  # Tiempo de escritura (ms)
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def total_gb(self) -> float:
        """Retorna espacio total en GB."""
        return self.total / (1024 ** 3)

    @property
    def used_gb(self) -> float:
        """Retorna espacio usado en GB."""
        return self.used / (1024 ** 3)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte las métricas a diccionario."""
        return {
            "device": self.device,
            "mountpoint": self.mountpoint,
            "fstype": self.fstype,
            "total": self.total,
            "used": self.used,
            "free": self.free,
            "percent": round(self.percent, 2),
            "read_count": self.read_count,
            "write_count": self.write_count,
            "read_bytes": self.read_bytes,
            "write_bytes": self.write_bytes,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class NetworkMetrics:
    """Métricas de uso de red."""
    interface: str = ""  # Nombre de la interfaz
    bytes_sent: int = 0  # Bytes enviados
    bytes_recv: int = 0  # Bytes recibidos
    packets_sent: int = 0  # Paquetes enviados
    packets_recv: int = 0  # Paquetes recibidos
    errin: int = 0  # Errores de entrada
    errout: int = 0  # Errores de salida
    dropin: int = 0  # Paquetes descartados (entrada)
    dropout: int = 0  # Paquetes descartados (salida)
    speed: int = 0  # Velocidad de la interfaz (Mbps)
    is_up: bool = True  # Estado de la interfaz
    timestamp: datetime = field(default_factory=datetime.now)

    @property
    def bytes_sent_mb(self) -> float:
        """Retorna bytes enviados en MB."""
        return self.bytes_sent / (1024 * 1024)

    @property
    def bytes_recv_mb(self) -> float:
        """Retorna bytes recibidos en MB."""
        return self.bytes_recv / (1024 * 1024)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte las métricas a diccionario."""
        return {
            "interface": self.interface,
            "bytes_sent": self.bytes_sent,
            "bytes_recv": self.bytes_recv,
            "packets_sent": self.packets_sent,
            "packets_recv": self.packets_recv,
            "errin": self.errin,
            "errout": self.errout,
            "dropin": self.dropin,
            "dropout": self.dropout,
            "speed": self.speed,
            "is_up": self.is_up,
            "timestamp": self.timestamp.isoformat()
        }


@dataclass
class SystemPerformance:
    """
    Métricas de rendimiento del sistema completo.

    Agrupa todas las métricas de CPU, memoria, disco y red.
    """
    cpu: CPUMetrics = field(default_factory=CPUMetrics)
    memory: MemoryMetrics = field(default_factory=MemoryMetrics)
    disks: List[DiskMetrics] = field(default_factory=list)
    networks: List[NetworkMetrics] = field(default_factory=list)
    boot_time: datetime = field(default_factory=datetime.now)
    num_processes: int = 0
    num_threads: int = 0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convierte todas las métricas a diccionario."""
        return {
            "cpu": self.cpu.to_dict(),
            "memory": self.memory.to_dict(),
            "disks": [disk.to_dict() for disk in self.disks],
            "networks": [net.to_dict() for net in self.networks],
            "boot_time": self.boot_time.isoformat(),
            "num_processes": self.num_processes,
            "num_threads": self.num_threads,
            "timestamp": self.timestamp.isoformat()
        }
