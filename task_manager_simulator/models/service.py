"""
Modelo de datos para servicios del sistema (Windows).
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ServiceStatus(Enum):
    """Estados posibles de un servicio."""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    STARTING = "starting"
    STOPPING = "stopping"
    PAUSING = "pausing"
    RESUMING = "resuming"
    UNKNOWN = "unknown"


class ServiceStartType(Enum):
    """Tipos de inicio de servicio."""
    AUTOMATIC = "automatic"
    AUTOMATIC_DELAYED = "automatic_delayed"
    MANUAL = "manual"
    DISABLED = "disabled"
    BOOT = "boot"
    SYSTEM = "system"


@dataclass
class Service:
    """
    Modelo de datos de un servicio del sistema.

    Attributes:
        name: Nombre del servicio
        display_name: Nombre para mostrar
        description: Descripción del servicio
        status: Estado actual del servicio
        start_type: Tipo de inicio del servicio
        pid: Process ID (si está en ejecución)
        username: Usuario que ejecuta el servicio
        binary_path: Ruta al ejecutable del servicio
        dependencies: Lista de servicios de los que depende
        dependent_services: Lista de servicios que dependen de este
    """

    name: str
    display_name: str
    description: Optional[str] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    start_type: ServiceStartType = ServiceStartType.MANUAL
    pid: Optional[int] = None
    username: Optional[str] = None
    binary_path: Optional[str] = None
    dependencies: list = None
    dependent_services: list = None

    def __post_init__(self):
        """Inicializa listas vacías si son None."""
        if self.dependencies is None:
            self.dependencies = []
        if self.dependent_services is None:
            self.dependent_services = []

    @property
    def is_running(self) -> bool:
        """Retorna True si el servicio está en ejecución."""
        return self.status == ServiceStatus.RUNNING

    @property
    def is_automatic(self) -> bool:
        """Retorna True si el servicio inicia automáticamente."""
        return self.start_type in [
            ServiceStartType.AUTOMATIC,
            ServiceStartType.AUTOMATIC_DELAYED,
            ServiceStartType.BOOT,
            ServiceStartType.SYSTEM
        ]

    def to_dict(self) -> dict:
        """Convierte el servicio a un diccionario."""
        return {
            "name": self.name,
            "display_name": self.display_name,
            "description": self.description,
            "status": self.status.value,
            "start_type": self.start_type.value,
            "pid": self.pid,
            "username": self.username,
            "binary_path": self.binary_path,
            "dependencies": self.dependencies,
            "dependent_services": self.dependent_services,
        }

    def __repr__(self) -> str:
        return f"Service(name='{self.name}', status={self.status.value}, start_type={self.start_type.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, Service):
            return False
        return self.name == other.name

    def __hash__(self) -> int:
        return hash(self.name)
