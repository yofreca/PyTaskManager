"""
Constantes globales de la aplicación.
"""

# Frecuencias de actualización (en milisegundos)
REFRESH_RATE_PROCESSES = 1000  # 1 segundo
REFRESH_RATE_CPU = 1000  # 1 segundo
REFRESH_RATE_MEMORY = 2000  # 2 segundos
REFRESH_RATE_DISK = 2000  # 2 segundos
REFRESH_RATE_NETWORK = 1000  # 1 segundo
REFRESH_RATE_GPU = 3000  # 3 segundos

# Límites de rendimiento
MAX_PROCESS_COUNT = 10000
MAX_HISTORY_POINTS = 60  # 60 puntos para gráficos

# Umbrales de alerta
CPU_WARNING_THRESHOLD = 80.0  # %
CPU_CRITICAL_THRESHOLD = 95.0  # %
MEMORY_WARNING_THRESHOLD = 80.0  # %
MEMORY_CRITICAL_THRESHOLD = 90.0  # %
DISK_WARNING_THRESHOLD = 85.0  # %
DISK_CRITICAL_THRESHOLD = 95.0  # %

# Prioridades de proceso
PROCESS_PRIORITIES = {
    'idle': 0,
    'below_normal': 1,
    'normal': 2,
    'above_normal': 3,
    'high': 4,
    'realtime': 5,
}

# Tamaños de columnas por defecto (en píxeles)
DEFAULT_COLUMN_WIDTHS = {
    'name': 200,
    'pid': 80,
    'cpu_percent': 80,
    'memory_mb': 100,
    'status': 100,
    'username': 120,
}

# Colores de la UI
COLOR_CPU_LOW = '#00FF00'  # Verde
COLOR_CPU_MEDIUM = '#FFFF00'  # Amarillo
COLOR_CPU_HIGH = '#FFA500'  # Naranja
COLOR_CPU_CRITICAL = '#FF0000'  # Rojo

COLOR_MEMORY_LOW = '#00BFFF'  # Azul claro
COLOR_MEMORY_MEDIUM = '#1E90FF'  # Azul
COLOR_MEMORY_HIGH = '#0000CD'  # Azul oscuro
COLOR_MEMORY_CRITICAL = '#FF0000'  # Rojo

# Formatos de exportación
EXPORT_FORMATS = ['CSV', 'JSON', 'TXT', 'HTML']

# Sistema
SYSTEM_UPTIME_CHECK_INTERVAL = 60000  # 60 segundos

# Ventana principal
WINDOW_MIN_WIDTH = 800
WINDOW_MIN_HEIGHT = 600
WINDOW_DEFAULT_WIDTH = 1200
WINDOW_DEFAULT_HEIGHT = 800

# Gráficos
CHART_UPDATE_INTERVAL = 1000  # 1 segundo
CHART_ANIMATION_DURATION = 200  # milisegundos
