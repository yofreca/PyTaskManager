"""
Constantes globales de la aplicación Task Manager Simulator.
"""

# Versión de la aplicación
APP_VERSION = "0.1.0"
APP_NAME = "Task Manager Simulator"

# Frecuencias de actualización (en milisegundos)
UPDATE_INTERVAL_PROCESSES = 1000      # 1 segundo
UPDATE_INTERVAL_CPU = 1000             # 1 segundo
UPDATE_INTERVAL_MEMORY = 2000          # 2 segundos
UPDATE_INTERVAL_DISK = 2000            # 2 segundos
UPDATE_INTERVAL_NETWORK = 1000         # 1 segundo
UPDATE_INTERVAL_GPU = 3000             # 3 segundos

# Límites de rendimiento
MAX_HISTORY_POINTS = 60                # Puntos en gráficos (60 segundos)
MAX_PROCESSES_DISPLAY = 500            # Máximo de procesos a mostrar

# Prioridades de procesos (Windows)
PRIORITY_CLASSES = {
    "REALTIME": 256,
    "HIGH": 128,
    "ABOVE_NORMAL": 32768,
    "NORMAL": 32,
    "BELOW_NORMAL": 16384,
    "IDLE": 64
}

# Estados de procesos
PROCESS_STATUS = {
    "RUNNING": "running",
    "SLEEPING": "sleeping",
    "DISK_SLEEP": "disk-sleep",
    "STOPPED": "stopped",
    "ZOMBIE": "zombie",
    "DEAD": "dead",
    "WAKING": "waking",
    "IDLE": "idle",
    "LOCKED": "locked",
    "WAITING": "waiting"
}

# Estados de servicios
SERVICE_STATUS = {
    "RUNNING": "running",
    "STOPPED": "stopped",
    "PAUSED": "paused",
    "PENDING": "pending"
}

# Tipos de inicio de servicios
SERVICE_START_TYPES = {
    "AUTO": "automatic",
    "MANUAL": "manual",
    "DISABLED": "disabled"
}

# Columnas disponibles para la tabla de procesos
PROCESS_COLUMNS = [
    "name",
    "pid",
    "status",
    "username",
    "cpu_percent",
    "memory_percent",
    "memory_info",
    "num_threads",
    "create_time"
]

# Columnas para la tabla de detalles (extendida)
DETAIL_COLUMNS = [
    "name",
    "pid",
    "status",
    "username",
    "cpu_percent",
    "cpu_times",
    "memory_percent",
    "memory_info",
    "memory_maps",
    "num_threads",
    "num_handles",
    "io_counters",
    "connections",
    "create_time",
    "exe",
    "cmdline"
]

# Formato de datos
SIZE_UNITS = ["B", "KB", "MB", "GB", "TB"]

# Colores para gráficos
CHART_COLORS = {
    "cpu": "#0078D4",      # Azul
    "memory": "#00A300",   # Verde
    "disk": "#E81123",     # Rojo
    "network": "#FFB900",  # Amarillo/Dorado
    "gpu": "#8E8CD8"       # Púrpura
}

# Umbrales de advertencia (porcentajes)
WARNING_THRESHOLDS = {
    "cpu": 80,
    "memory": 85,
    "disk": 90
}

# Configuración de UI
UI_CONFIG = {
    "window_min_width": 800,
    "window_min_height": 600,
    "table_row_height": 25,
    "icon_size": 16
}

# Mensajes de error comunes
ERROR_MESSAGES = {
    "access_denied": "Acceso denegado. Se requieren privilegios de administrador.",
    "process_not_found": "El proceso ya no existe.",
    "operation_failed": "La operación no se pudo completar.",
    "permission_required": "Esta operación requiere permisos elevados."
}
