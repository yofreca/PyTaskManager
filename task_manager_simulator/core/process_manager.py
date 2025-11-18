"""
Gestor de procesos del sistema usando psutil.
"""
import psutil
import logging
from typing import List, Optional, Dict
from datetime import datetime

from ..models.process import ProcessInfo


logger = logging.getLogger(__name__)


class ProcessManager:
    """Gestor de procesos del sistema."""

    def __init__(self):
        """Inicializa el gestor de procesos."""
        self._process_cache: Dict[int, ProcessInfo] = {}
        self._last_cpu_times: Dict[int, float] = {}

    def get_all_processes(self) -> List[ProcessInfo]:
        """
        Obtiene la lista de todos los procesos activos.

        Returns:
            Lista de ProcessInfo con información de cada proceso.
        """
        processes = []

        for proc in psutil.process_iter(['pid', 'name', 'username', 'status',
                                         'cpu_percent', 'memory_info', 'num_threads',
                                         'create_time', 'exe', 'cmdline']):
            try:
                proc_info = self._create_process_info(proc)
                if proc_info:
                    processes.append(proc_info)
                    self._process_cache[proc_info.pid] = proc_info
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                logger.debug(f"Error al obtener proceso: {e}")
                continue

        return processes

    def get_process_by_pid(self, pid: int) -> Optional[ProcessInfo]:
        """
        Obtiene información de un proceso específico por PID.

        Args:
            pid: Process ID

        Returns:
            ProcessInfo o None si no se encuentra.
        """
        try:
            proc = psutil.Process(pid)
            return self._create_process_info(proc)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            logger.error(f"Error al obtener proceso {pid}: {e}")
            return None

    def _create_process_info(self, proc: psutil.Process) -> Optional[ProcessInfo]:
        """
        Crea un objeto ProcessInfo desde un proceso psutil.

        Args:
            proc: Proceso de psutil

        Returns:
            ProcessInfo o None si hay error.
        """
        try:
            # Obtener información básica
            info = proc.info

            # Obtener información de memoria
            mem_info = proc.memory_info()
            memory_mb = mem_info.rss / (1024 * 1024)  # Convertir bytes a MB

            # Obtener porcentaje de memoria
            try:
                memory_percent = proc.memory_percent()
            except (psutil.AccessDenied, AttributeError):
                memory_percent = 0.0

            # Obtener CPU percent
            cpu_percent = info.get('cpu_percent', 0.0) or 0.0

            # Obtener información de I/O si está disponible
            disk_read_mb = 0.0
            disk_write_mb = 0.0
            try:
                io_counters = proc.io_counters()
                disk_read_mb = io_counters.read_bytes / (1024 * 1024)
                disk_write_mb = io_counters.write_bytes / (1024 * 1024)
            except (psutil.AccessDenied, AttributeError, OSError):
                pass

            # Crear ProcessInfo
            process_info = ProcessInfo(
                pid=info['pid'],
                name=info.get('name', 'Unknown'),
                username=info.get('username'),
                cpu_percent=cpu_percent,
                memory_mb=memory_mb,
                memory_percent=memory_percent,
                disk_read_mb=disk_read_mb,
                disk_write_mb=disk_write_mb,
                status=info.get('status', 'unknown'),
                num_threads=info.get('num_threads', 0),
                exe_path=info.get('exe'),
                cmdline=' '.join(info.get('cmdline', [])) if info.get('cmdline') else None,
                create_time=datetime.fromtimestamp(info['create_time']) if info.get('create_time') else None,
            )

            # Obtener prioridad si está disponible
            try:
                nice = proc.nice()
                process_info.nice = nice
                process_info.priority = self._get_priority_name(nice)
            except (psutil.AccessDenied, AttributeError):
                pass

            # Obtener proceso padre
            try:
                parent = proc.parent()
                if parent:
                    process_info.parent_pid = parent.pid
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                pass

            return process_info

        except Exception as e:
            logger.debug(f"Error al crear ProcessInfo: {e}")
            return None

    def _get_priority_name(self, nice: int) -> str:
        """Convierte el valor nice a nombre de prioridad."""
        if nice < -10:
            return "realtime"
        elif nice < -5:
            return "high"
        elif nice < 0:
            return "above_normal"
        elif nice == 0:
            return "normal"
        elif nice < 10:
            return "below_normal"
        else:
            return "idle"

    def kill_process(self, pid: int, force: bool = False) -> bool:
        """
        Termina un proceso.

        Args:
            pid: Process ID
            force: Si True, usa SIGKILL en lugar de SIGTERM

        Returns:
            True si el proceso fue terminado exitosamente.
        """
        try:
            proc = psutil.Process(pid)
            if force:
                proc.kill()
            else:
                proc.terminate()

            # Esperar a que el proceso termine
            proc.wait(timeout=3)
            logger.info(f"Proceso {pid} terminado exitosamente")
            return True

        except psutil.NoSuchProcess:
            logger.warning(f"Proceso {pid} no encontrado")
            return False
        except psutil.AccessDenied:
            logger.error(f"Acceso denegado al terminar proceso {pid}")
            return False
        except psutil.TimeoutExpired:
            logger.warning(f"Timeout al terminar proceso {pid}")
            return False
        except Exception as e:
            logger.error(f"Error al terminar proceso {pid}: {e}")
            return False

    def suspend_process(self, pid: int) -> bool:
        """
        Suspende un proceso.

        Args:
            pid: Process ID

        Returns:
            True si el proceso fue suspendido exitosamente.
        """
        try:
            proc = psutil.Process(pid)
            proc.suspend()
            logger.info(f"Proceso {pid} suspendido")
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error al suspender proceso {pid}: {e}")
            return False

    def resume_process(self, pid: int) -> bool:
        """
        Reanuda un proceso suspendido.

        Args:
            pid: Process ID

        Returns:
            True si el proceso fue reanudado exitosamente.
        """
        try:
            proc = psutil.Process(pid)
            proc.resume()
            logger.info(f"Proceso {pid} reanudado")
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error al reanudar proceso {pid}: {e}")
            return False

    def set_priority(self, pid: int, priority: str) -> bool:
        """
        Establece la prioridad de un proceso.

        Args:
            pid: Process ID
            priority: Nombre de la prioridad (idle, below_normal, normal, above_normal, high, realtime)

        Returns:
            True si la prioridad fue establecida exitosamente.
        """
        priority_map = {
            'idle': psutil.IDLE_PRIORITY_CLASS if hasattr(psutil, 'IDLE_PRIORITY_CLASS') else 19,
            'below_normal': psutil.BELOW_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'BELOW_NORMAL_PRIORITY_CLASS') else 10,
            'normal': psutil.NORMAL_PRIORITY_CLASS if hasattr(psutil, 'NORMAL_PRIORITY_CLASS') else 0,
            'above_normal': psutil.ABOVE_NORMAL_PRIORITY_CLASS if hasattr(psutil, 'ABOVE_NORMAL_PRIORITY_CLASS') else -5,
            'high': psutil.HIGH_PRIORITY_CLASS if hasattr(psutil, 'HIGH_PRIORITY_CLASS') else -10,
            'realtime': psutil.REALTIME_PRIORITY_CLASS if hasattr(psutil, 'REALTIME_PRIORITY_CLASS') else -20,
        }

        try:
            proc = psutil.Process(pid)
            nice_value = priority_map.get(priority, 0)
            proc.nice(nice_value)
            logger.info(f"Prioridad de proceso {pid} establecida a {priority}")
            return True
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            logger.error(f"Error al establecer prioridad de proceso {pid}: {e}")
            return False

    def get_process_count(self) -> int:
        """Retorna el número total de procesos activos."""
        return len(psutil.pids())

    def get_thread_count(self) -> int:
        """Retorna el número total de threads en el sistema."""
        total_threads = 0
        for proc in psutil.process_iter(['num_threads']):
            try:
                total_threads += proc.info.get('num_threads', 0)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return total_threads
