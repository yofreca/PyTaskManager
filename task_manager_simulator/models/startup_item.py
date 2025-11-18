"""
Modelo de datos para elementos de inicio automático.
"""
from dataclasses import dataclass
from typing import Optional
from datetime import datetime
from enum import Enum


class StartupImpact(Enum):
    """Impacto de un elemento en el inicio del sistema."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOT_MEASURED = "not_measured"


class StartupLocation(Enum):
    """Ubicación de registro del elemento de inicio."""
    REGISTRY_RUN = "registry_run"
    REGISTRY_RUNONCE = "registry_runonce"
    STARTUP_FOLDER = "startup_folder"
    TASK_SCHEDULER = "task_scheduler"
    SERVICE = "service"
    UNKNOWN = "unknown"


@dataclass
class StartupItem:
    """Elemento de inicio automático del sistema."""

    name: str
    command: str
    location: StartupLocation = StartupLocation.UNKNOWN
    enabled: bool = True

    # Información adicional
    publisher: Optional[str] = None
    impact: StartupImpact = StartupImpact.NOT_MEASURED
    file_path: Optional[str] = None

    # Fechas
    disabled_date: Optional[datetime] = None

    def to_dict(self) -> dict:
        """Convierte el elemento a diccionario."""
        return {
            'name': self.name,
            'command': self.command,
            'location': self.location.value if isinstance(self.location, StartupLocation) else self.location,
            'enabled': self.enabled,
            'publisher': self.publisher,
            'impact': self.impact.value if isinstance(self.impact, StartupImpact) else self.impact,
            'file_path': self.file_path,
            'disabled_date': self.disabled_date.isoformat() if self.disabled_date else None,
        }
