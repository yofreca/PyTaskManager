"""
Utilidades para formatear datos y presentarlos en la UI.
"""
from typing import Union
from datetime import datetime, timedelta


def format_bytes(bytes_value: Union[int, float], precision: int = 2) -> str:
    """
    Formatea un valor en bytes a una unidad legible (KB, MB, GB, etc.).

    Args:
        bytes_value: Valor en bytes
        precision: Número de decimales

    Returns:
        String formateado (ej: "1.50 GB")

    Examples:
        >>> format_bytes(1024)
        '1.00 KB'
        >>> format_bytes(1536000)
        '1.46 MB'
    """
    if bytes_value < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB", "PB"]
    unit_index = 0

    value = float(bytes_value)

    while value >= 1024.0 and unit_index < len(units) - 1:
        value /= 1024.0
        unit_index += 1

    return f"{value:.{precision}f} {units[unit_index]}"


def format_bytes_per_second(bytes_value: Union[int, float], precision: int = 2) -> str:
    """
    Formatea una tasa de bytes por segundo.

    Args:
        bytes_value: Bytes por segundo
        precision: Número de decimales

    Returns:
        String formateado (ej: "1.50 MB/s")
    """
    return f"{format_bytes(bytes_value, precision)}/s"


def format_percentage(value: float, precision: int = 1) -> str:
    """
    Formatea un valor como porcentaje.

    Args:
        value: Valor entre 0 y 100
        precision: Número de decimales

    Returns:
        String formateado (ej: "45.5%")

    Examples:
        >>> format_percentage(75.5)
        '75.5%'
        >>> format_percentage(100)
        '100.0%'
    """
    return f"{value:.{precision}f}%"


def format_number(value: Union[int, float], precision: int = 0, thousands_sep: str = ",") -> str:
    """
    Formatea un número con separador de miles.

    Args:
        value: Número a formatear
        precision: Número de decimales
        thousands_sep: Separador de miles

    Returns:
        String formateado (ej: "1,234,567")

    Examples:
        >>> format_number(1234567)
        '1,234,567'
        >>> format_number(1234.5678, precision=2)
        '1,234.57'
    """
    if precision == 0:
        return f"{int(value):,}".replace(",", thousands_sep)
    else:
        formatted = f"{value:,.{precision}f}"
        return formatted.replace(",", thousands_sep)


def format_duration(seconds: Union[int, float]) -> str:
    """
    Formatea una duración en segundos a un formato legible.

    Args:
        seconds: Duración en segundos

    Returns:
        String formateado (ej: "2 days, 3:45:12")

    Examples:
        >>> format_duration(3661)
        '1:01:01'
        >>> format_duration(90061)
        '1 day, 1:01:01'
    """
    if seconds < 0:
        return "0:00:00"

    td = timedelta(seconds=int(seconds))
    days = td.days
    hours = td.seconds // 3600
    minutes = (td.seconds % 3600) // 60
    secs = td.seconds % 60

    if days > 0:
        if days == 1:
            return f"1 day, {hours:02d}:{minutes:02d}:{secs:02d}"
        else:
            return f"{days} days, {hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_timestamp(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formatea un objeto datetime a string.

    Args:
        dt: Objeto datetime
        format_str: Formato de salida

    Returns:
        String formateado

    Examples:
        >>> from datetime import datetime
        >>> format_timestamp(datetime(2024, 1, 15, 14, 30, 0))
        '2024-01-15 14:30:00'
    """
    if dt is None:
        return ""

    return dt.strftime(format_str)


def format_frequency(mhz: float) -> str:
    """
    Formatea una frecuencia en MHz a un formato legible.

    Args:
        mhz: Frecuencia en MHz

    Returns:
        String formateado (ej: "2.40 GHz" o "1500 MHz")

    Examples:
        >>> format_frequency(2400)
        '2.40 GHz'
        >>> format_frequency(800)
        '800 MHz'
    """
    if mhz >= 1000:
        ghz = mhz / 1000
        return f"{ghz:.2f} GHz"
    else:
        return f"{int(mhz)} MHz"


def format_process_status(status: str) -> str:
    """
    Formatea el estado de un proceso para mostrar.

    Args:
        status: Estado del proceso

    Returns:
        String formateado y traducido

    Examples:
        >>> format_process_status("running")
        'Running'
        >>> format_process_status("sleeping")
        'Sleeping'
    """
    status_translation = {
        "running": "Running",
        "sleeping": "Sleeping",
        "disk-sleep": "Disk Sleep",
        "stopped": "Stopped",
        "zombie": "Zombie",
        "dead": "Dead",
        "waking": "Waking",
        "idle": "Idle",
        "locked": "Locked",
        "waiting": "Waiting",
    }

    return status_translation.get(status.lower(), status.title())


def format_priority(priority: Union[int, str]) -> str:
    """
    Formatea la prioridad de un proceso.

    Args:
        priority: Valor o nombre de prioridad

    Returns:
        String formateado

    Examples:
        >>> format_priority(32)
        'Normal'
        >>> format_priority("high")
        'High'
    """
    if isinstance(priority, str):
        return priority.title()

    priority_map = {
        256: "Realtime",
        128: "High",
        32768: "Above Normal",
        32: "Normal",
        16384: "Below Normal",
        64: "Idle"
    }

    return priority_map.get(priority, f"Unknown ({priority})")


def format_cpu_time(seconds: float) -> str:
    """
    Formatea el tiempo de CPU en segundos a formato hh:mm:ss.

    Args:
        seconds: Tiempo en segundos

    Returns:
        String formateado

    Examples:
        >>> format_cpu_time(3661.5)
        '01:01:01'
    """
    return format_duration(seconds)


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Trunca un string si excede la longitud máxima.

    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo a agregar si se trunca

    Returns:
        String truncado

    Examples:
        >>> truncate_string("This is a very long text", 10)
        'This is...'
    """
    if len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def format_speed_mbps(bytes_per_second: float) -> str:
    """
    Formatea una velocidad en bytes/segundo a Mbps.

    Args:
        bytes_per_second: Bytes por segundo

    Returns:
        String formateado (ej: "12.5 Mbps")

    Examples:
        >>> format_speed_mbps(1572864)
        '12.6 Mbps'
    """
    mbps = (bytes_per_second * 8) / (1024 * 1024)
    return f"{mbps:.1f} Mbps"


def format_temperature(celsius: float) -> str:
    """
    Formatea una temperatura.

    Args:
        celsius: Temperatura en Celsius

    Returns:
        String formateado (ej: "45.0 °C")
    """
    return f"{celsius:.1f} °C"
