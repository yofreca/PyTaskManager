"""
Modelo de datos para programas de inicio automático.
"""
from dataclasses import dataclass
from typing import Optional
from enum import Enum
from datetime import datetime


class StartupLocation(Enum):
    """Ubicación del programa de inicio."""
    REGISTRY_RUN = "Registry: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    REGISTRY_RUN_ONCE = "Registry: HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"
    REGISTRY_MACHINE_RUN = "Registry: HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Run"
    REGISTRY_MACHINE_RUN_ONCE = "Registry: HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\RunOnce"
    STARTUP_FOLDER_USER = "Startup Folder (User)"
    STARTUP_FOLDER_COMMON = "Startup Folder (Common)"
    TASK_SCHEDULER = "Task Scheduler"
    SERVICES = "Services"
    UNKNOWN = "Unknown"


class StartupImpact(Enum):
    """Impacto del programa en el inicio del sistema."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NOT_MEASURED = "not_measured"


@dataclass
class StartupItem:
    """
    Modelo de datos de un programa de inicio automático.

    Attributes:
        name: Nombre del programa
        publisher: Editor/Fabricante
        status: Estado (habilitado/deshabilitado)
        impact: Impacto en el inicio del sistema
        location: Ubicación del registro o carpeta
        command_line: Línea de comandos completa
        file_path: Ruta al archivo ejecutable
        disabled_date: Fecha en que fue deshabilitado
        cpu_time: Tiempo de CPU durante el inicio (ms)
        disk_io: I/O de disco durante el inicio (bytes)
    """

    name: str
    publisher: Optional[str] = None
    enabled: bool = True
    impact: StartupImpact = StartupImpact.NOT_MEASURED
    location: StartupLocation = StartupLocation.UNKNOWN
    command_line: Optional[str] = None
    file_path: Optional[str] = None
    disabled_date: Optional[datetime] = None
    cpu_time: float = 0.0  # milisegundos
    disk_io: int = 0  # bytes

    @property
    def status(self) -> str:
        """Retorna el estado como string."""
        return "Enabled" if self.enabled else "Disabled"

    @property
    def location_str(self) -> str:
        """Retorna la ubicación como string."""
        return self.location.value

    @property
    def impact_str(self) -> str:
        """Retorna el impacto como string."""
        return self.impact.value.replace("_", " ").title()

    def to_dict(self) -> dict:
        """Convierte el item a un diccionario."""
        return {
            "name": self.name,
            "publisher": self.publisher,
            "enabled": self.enabled,
            "status": self.status,
            "impact": self.impact.value,
            "location": self.location.value,
            "command_line": self.command_line,
            "file_path": self.file_path,
            "disabled_date": self.disabled_date.isoformat() if self.disabled_date else None,
            "cpu_time": self.cpu_time,
            "disk_io": self.disk_io,
        }

    def __repr__(self) -> str:
        return f"StartupItem(name='{self.name}', enabled={self.enabled}, impact={self.impact.value})"

    def __eq__(self, other) -> bool:
        if not isinstance(other, StartupItem):
            return False
        return self.name == other.name and self.location == other.location

    def __hash__(self) -> int:
        return hash((self.name, self.location))
