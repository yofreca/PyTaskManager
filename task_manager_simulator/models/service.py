"""
Modelo de datos para servicios del sistema (Windows).
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class ServiceStatus(Enum):
    """Estado de un servicio."""
    RUNNING = "running"
    STOPPED = "stopped"
    PAUSED = "paused"
    START_PENDING = "start_pending"
    STOP_PENDING = "stop_pending"
    PAUSE_PENDING = "pause_pending"
    CONTINUE_PENDING = "continue_pending"
    UNKNOWN = "unknown"


class ServiceStartType(Enum):
    """Tipo de inicio de un servicio."""
    AUTO = "automatic"
    MANUAL = "manual"
    DISABLED = "disabled"
    AUTO_DELAYED = "automatic_delayed"
    UNKNOWN = "unknown"


@dataclass
class ServiceInfo:
    """Información de un servicio del sistema."""

    name: str
    display_name: str
    description: Optional[str] = None
    status: ServiceStatus = ServiceStatus.UNKNOWN
    start_type: ServiceStartType = ServiceStartType.UNKNOWN

    # Detalles adicionales
    pid: Optional[int] = None
    username: Optional[str] = None
    path: Optional[str] = None

    # Estado
    can_stop: bool = False
    can_pause: bool = False

    def to_dict(self) -> dict:
        """Convierte el servicio a diccionario."""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'description': self.description,
            'status': self.status.value if isinstance(self.status, ServiceStatus) else self.status,
            'start_type': self.start_type.value if isinstance(self.start_type, ServiceStartType) else self.start_type,
            'pid': self.pid,
            'username': self.username,
            'path': self.path,
            'can_stop': self.can_stop,
            'can_pause': self.can_pause,
        }
