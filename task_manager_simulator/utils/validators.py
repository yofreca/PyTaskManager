"""
Utilidades para validación de datos.
"""
import os
import psutil
from typing import Optional


def is_valid_pid(pid: int) -> bool:
    """
    Verifica si un PID es válido y existe en el sistema.

    Args:
        pid: Process ID a validar

    Returns:
        True si el PID es válido y existe

    Examples:
        >>> is_valid_pid(1)  # init/systemd siempre existe
        True
        >>> is_valid_pid(-1)
        False
    """
    if not isinstance(pid, int) or pid < 0:
        return False

    return psutil.pid_exists(pid)


def is_system_process(pid: int) -> bool:
    """
    Determina si un proceso es del sistema.

    Args:
        pid: Process ID

    Returns:
        True si es un proceso del sistema
    """
    if pid < 10:
        return True

    try:
        proc = psutil.Process(pid)
        username = proc.username()

        if username in ['SYSTEM', 'NT AUTHORITY\\SYSTEM', 'root']:
            return True

    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    return False


def is_valid_priority(priority: int) -> bool:
    """
    Verifica si un valor de prioridad es válido.

    Args:
        priority: Valor de prioridad

    Returns:
        True si la prioridad es válida
    """
    valid_priorities = {256, 128, 32768, 32, 16384, 64}
    return priority in valid_priorities


def is_valid_percentage(value: float) -> bool:
    """
    Verifica si un valor es un porcentaje válido (0-100).

    Args:
        value: Valor a validar

    Returns:
        True si está entre 0 y 100

    Examples:
        >>> is_valid_percentage(50.5)
        True
        >>> is_valid_percentage(150)
        False
    """
    return 0 <= value <= 100


def is_file_executable(file_path: str) -> bool:
    """
    Verifica si un archivo es ejecutable.

    Args:
        file_path: Ruta al archivo

    Returns:
        True si el archivo existe y es ejecutable
    """
    if not os.path.exists(file_path):
        return False

    if not os.path.isfile(file_path):
        return False

    return os.access(file_path, os.X_OK)


def sanitize_process_name(name: str) -> str:
    """
    Sanitiza el nombre de un proceso para mostrar.

    Args:
        name: Nombre del proceso

    Returns:
        Nombre sanitizado
    """
    if not name:
        return "Unknown"

    # Remover caracteres especiales problemáticos
    sanitized = name.strip()

    # Limitar longitud
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."

    return sanitized


def validate_update_interval(interval: int) -> Optional[int]:
    """
    Valida y ajusta un intervalo de actualización.

    Args:
        interval: Intervalo en milisegundos

    Returns:
        Intervalo validado o None si es inválido

    Examples:
        >>> validate_update_interval(1000)
        1000
        >>> validate_update_interval(50)
        100
        >>> validate_update_interval(100000)
        60000
    """
    # Mínimo 100ms, máximo 60s
    MIN_INTERVAL = 100
    MAX_INTERVAL = 60000

    if not isinstance(interval, int):
        return None

    if interval < MIN_INTERVAL:
        return MIN_INTERVAL

    if interval > MAX_INTERVAL:
        return MAX_INTERVAL

    return interval
