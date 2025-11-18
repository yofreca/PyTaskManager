"""
Utilidades para formatear datos de forma amigable.
"""
from datetime import datetime, timedelta
from typing import Optional


def format_bytes(bytes_value: float, precision: int = 2) -> str:
    """
    Formatea bytes a una representación legible (KB, MB, GB, etc.).

    Args:
        bytes_value: Valor en bytes
        precision: Número de decimales

    Returns:
        String formateado (ej: "1.50 GB")
    """
    if bytes_value < 1024:
        return f"{bytes_value:.{precision}f} B"
    elif bytes_value < 1024 ** 2:
        return f"{bytes_value / 1024:.{precision}f} KB"
    elif bytes_value < 1024 ** 3:
        return f"{bytes_value / (1024 ** 2):.{precision}f} MB"
    elif bytes_value < 1024 ** 4:
        return f"{bytes_value / (1024 ** 3):.{precision}f} GB"
    else:
        return f"{bytes_value / (1024 ** 4):.{precision}f} TB"


def format_mb(mb_value: float, precision: int = 2) -> str:
    """
    Formatea megabytes a una representación legible.

    Args:
        mb_value: Valor en MB
        precision: Número de decimales

    Returns:
        String formateado (ej: "1,234.56 MB")
    """
    if mb_value < 1024:
        return f"{mb_value:,.{precision}f} MB"
    else:
        gb_value = mb_value / 1024
        return f"{gb_value:,.{precision}f} GB"


def format_percent(percent_value: float, precision: int = 1) -> str:
    """
    Formatea un porcentaje.

    Args:
        percent_value: Valor del porcentaje
        precision: Número de decimales

    Returns:
        String formateado (ej: "45.5%")
    """
    return f"{percent_value:.{precision}f}%"


def format_number(number: int) -> str:
    """
    Formatea un número con separadores de miles.

    Args:
        number: Número a formatear

    Returns:
        String formateado (ej: "1,234,567")
    """
    return f"{number:,}"


def format_uptime(seconds: float) -> str:
    """
    Formatea el tiempo de actividad (uptime).

    Args:
        seconds: Tiempo en segundos

    Returns:
        String formateado (ej: "2d 5h 30m")
    """
    td = timedelta(seconds=int(seconds))
    days = td.days
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    if not parts:  # Si es menos de un minuto
        parts.append(f"{seconds}s")

    return " ".join(parts)


def format_datetime(dt: Optional[datetime], fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formatea un objeto datetime.

    Args:
        dt: Objeto datetime
        fmt: Formato de salida

    Returns:
        String formateado
    """
    if dt is None:
        return "N/A"
    return dt.strftime(fmt)


def format_speed(bytes_per_sec: float) -> str:
    """
    Formatea velocidad de transferencia.

    Args:
        bytes_per_sec: Bytes por segundo

    Returns:
        String formateado (ej: "5.5 MB/s")
    """
    if bytes_per_sec < 1024:
        return f"{bytes_per_sec:.1f} B/s"
    elif bytes_per_sec < 1024 ** 2:
        return f"{bytes_per_sec / 1024:.1f} KB/s"
    elif bytes_per_sec < 1024 ** 3:
        return f"{bytes_per_sec / (1024 ** 2):.1f} MB/s"
    else:
        return f"{bytes_per_sec / (1024 ** 3):.1f} GB/s"


def format_frequency(mhz: float) -> str:
    """
    Formatea frecuencia de CPU.

    Args:
        mhz: Frecuencia en MHz

    Returns:
        String formateado (ej: "3.5 GHz")
    """
    if mhz >= 1000:
        return f"{mhz / 1000:.2f} GHz"
    else:
        return f"{mhz:.0f} MHz"


def truncate_string(text: str, max_length: int = 50, suffix: str = "...") -> str:
    """
    Trunca una cadena si excede la longitud máxima.

    Args:
        text: Texto a truncar
        max_length: Longitud máxima
        suffix: Sufijo para indicar truncamiento

    Returns:
        String truncado
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
